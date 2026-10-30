"""Application controller of the desktop app (no widgets here, so it is easy to test).

It owns the truss, runs the shared core services in-process and exposes a ViewModel
(scene + tables + texts) that the widgets simply display.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal

from ..core.analysis import TrussAnalysisService
from ..core.domain import Truss
from ..core.errors import InvalidSelectionError, UnknownEntityError
from ..core.results import AnalysisResult
from ..core.serialization import truss_from_dict, truss_to_dict
from ..core.templates import template_dict
from ..presentation.i18n import Translator
from ..presentation.panels import PanelPresenter, Table
from ..presentation.scene import Scene, SceneBuilder
from ..presentation.selection import Selection, SelectionController, ViewMode


@dataclass
class ViewModel:
    scene: Scene
    tables: list
    status: str
    status_text: str
    issues: list = field(default_factory=list)
    mode: str = "overview"
    target: str | None = None
    solved: bool = False


class AppController(QObject):
    changed = Signal()  # the view model has to be redrawn

    def __init__(self, analysis: TrussAnalysisService | None = None,
                 scenes: SceneBuilder | None = None, panels: PanelPresenter | None = None):
        super().__init__()
        self._service = analysis or TrussAnalysisService()
        self._scenes = scenes or SceneBuilder()
        self._panels = panels or PanelPresenter()
        self.lang = "en"
        self.t = Translator(self.lang)
        self.truss = Truss()
        self.analysis: AnalysisResult = self._service.analyze(self.truss)
        self.selection = SelectionController(
            joint_ids=lambda: [p.id for p in self.truss.points],
            member_ids=lambda: [m.id for m in self.truss.members],
            on_change=lambda _selection: self._publish())
        self.view: ViewModel | None = None

    # ---- model ---------------------------------------------------------------
    def load_dict(self, data: dict) -> None:
        self.truss = truss_from_dict(data)
        self.selection.reset()
        self._recompute()

    def load_template(self, key: str) -> None:
        self.load_dict(template_dict(key))

    def to_dict(self) -> dict:
        return truss_to_dict(self.truss)

    # ---- selection (one joint OR one member at a time) ------------------------------
    def select_joint(self, point_id: str) -> None:
        self._guard(lambda: self.selection.select_joint(point_id))

    def select_member(self, member_id: str) -> None:
        self._guard(lambda: self.selection.select_member(member_id))

    def select(self, kind: str, target_id: str) -> None:
        (self.select_joint if kind == "joint" else self.select_member)(target_id)

    def back(self) -> None:
        self.selection.back()

    def set_language(self, lang: str) -> None:
        self.lang, self.t = lang, Translator(lang)
        self._publish()

    # ---- internals -------------------------------------------------------------------
    def _guard(self, action) -> None:
        try:
            action()
        except (InvalidSelectionError, UnknownEntityError):
            pass  # ignored: e.g. clicking while another target is isolated

    def _recompute(self) -> None:
        self.analysis = self._service.analyze(self.truss)
        self._publish()

    def _publish(self) -> None:
        selection = self.selection.selection
        if selection.mode is not ViewMode.OVERVIEW and not self.analysis.solved:
            self.selection.reset()
            selection = Selection()
        t, a = self.t, self.analysis
        status = a.status.value
        self.view = ViewModel(
            scene=self._scenes.build(self.truss, a, selection, t),
            tables=self._panels.present(self.truss, a, selection, t),
            status=status, status_text=t(f"status.{status}"),
            issues=[t.issue(i) for i in a.issues], mode=selection.mode.value,
            target=selection.target_id, solved=a.solved)
        self.changed.emit()
