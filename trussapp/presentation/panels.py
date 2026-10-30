"""Translated data tables shown next to the drawing (same for web and desktop)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

from ..core.domain import Truss
from ..core.results import AnalysisResult, ForceKind, ForceVector, MemberState
from .i18n import Translator
from .scene import fmt_number
from .selection import Selection, ViewMode

AXIS_TOL = 1e-9


@dataclass
class Table:
    key: str
    title: str
    columns: list
    rows: list = field(default_factory=list)
    note: str | None = None
    note_ok: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


def angle_text(angle: float | None) -> str:
    return "—" if angle is None else fmt_number(angle)


class SenseFormatter:
    """Words for the direction/sense of a force."""

    def __init__(self, t: Translator):
        self._t = t

    def describe(self, f: ForceVector) -> str:
        t = self._t
        if f.magnitude <= 1e-12:
            return t("sense.zero")
        if f.kind is ForceKind.MEMBER:
            key = "sense.pull_toward" if f.state is MemberState.TENSION else "sense.push_away"
            return t(key, other=f.other_point_name)
        words = []
        if abs(f.fx) > AXIS_TOL:
            words.append(t("dir.right" if f.fx > 0 else "dir.left"))
        if abs(f.fy) > AXIS_TOL:
            words.append(t("dir.up" if f.fy > 0 else "dir.down"))
        return ", ".join(words)


class PanelPresenter:
    def present(self, truss: Truss, analysis: AnalysisResult, selection: Selection,
                t: Translator) -> list:
        if selection.mode is ViewMode.JOINT:
            return [self._joint_table(analysis, selection.target_id, t)]
        if selection.mode is ViewMode.MEMBER:
            return [self._member_table(analysis, selection.target_id, t)]
        return self._overview_tables(analysis, t)

    # ---- overview ---------------------------------------------------------
    def _overview_tables(self, a: AnalysisResult, t: Translator) -> list:
        tables = []
        if a.reactions:
            cols = [t("c.name"), t("c.support"), t("c.point"), t("c.magnitude"), t("c.unit"),
                    t("c.angle"), t("c.sense")]
            rows = []
            for r in a.reactions:
                words = t("dir.right" if r.value > 0 else "dir.left") if r.axis == "x" \
                    else t("dir.up" if r.value > 0 else "dir.down")
                rows.append([r.name, r.support_name, r.point_name, fmt_number(abs(r.value)),
                             r.unit, angle_text(r.angle_deg), words if r.value else t("sense.zero")])
            tables.append(Table("reactions", t("table.reactions"), cols, rows))
        if a.members:
            cols = [t("c.name"), t("c.start"), t("c.end"), t("c.force"), t("c.state"),
                    t("c.length")]
            rows = [[m.name, m.start_point, m.end_point, fmt_number(m.force),
                     t(f"state.{m.state.value}"), fmt_number(m.length)] for m in a.members]
            tables.append(Table("members", t("table.members"), cols, rows))
        if a.counts:
            c = a.counts
            rows = [[t("an.points"), c["points"]], [t("an.members"), c["members"]],
                    [t("an.reactions"), c["reactions"]], [t("an.equations"), c["equations"]],
                    [t("an.unknowns"), c["unknowns"]], [t("an.degree"), c["degree"]],
                    [t("an.mechanisms"), c["mechanisms"]]]
            if a.residual is not None:
                rows.append([t("an.residual"), f"{a.residual:.2e}"])
            tables.append(Table("analysis", t("table.analysis"), ["", ""],
                                [[str(x) for x in row] for row in rows]))
        return tables

    # ---- isolated joint ---------------------------------------------------
    def _joint_table(self, a: AnalysisResult, joint_id: str, t: Translator) -> Table:
        view = a.joint_views[joint_id]
        sense = SenseFormatter(t)
        cols = [t("c.name"), t("c.kind"), t("c.magnitude"), t("c.unit"), t("c.angle"),
                t("c.sense"), t("c.fx"), t("c.fy")]
        rows = [[f.name, self._kind_text(f, t), fmt_number(f.magnitude), f.unit,
                 angle_text(f.angle_deg), sense.describe(f), fmt_number(f.fx), fmt_number(f.fy)]
                for f in view.forces]
        key = "balance.ok" if view.balanced else "balance.bad"
        note = t(key, fx=fmt_number(view.sum_fx), fy=fmt_number(view.sum_fy))
        return Table("joint", t("table.joint", name=view.point_name), cols, rows, note,
                     view.balanced)

    # ---- isolated member --------------------------------------------------
    def _member_table(self, a: AnalysisResult, member_id: str, t: Translator) -> Table:
        view = a.member_views[member_id]
        m = view.member
        sense = SenseFormatter(t)
        cols = [t("c.name"), t("c.applied_by"), t("c.magnitude"), t("c.unit"), t("c.angle"),
                t("c.sense"), t("c.fx"), t("c.fy")]
        joint_names = (view.start_name, view.end_name)
        rows = [[f.name, joint_names[i], fmt_number(f.magnitude), f.unit, angle_text(f.angle_deg),
                 sense.describe(f), fmt_number(f.fx), fmt_number(f.fy)]
                for i, f in enumerate(view.end_forces)]
        note = (f"{t('c.state')}: {t('state.' + m.state.value)} · {t('c.force')}: "
                f"{fmt_number(m.force)} · {t('c.length')}: {fmt_number(m.length)} · "
                f"{t('c.angle')}: {fmt_number(m.angle_deg)}")
        return Table("member", t("table.member", name=m.name), cols, rows, note)

    @staticmethod
    def _kind_text(f: ForceVector, t: Translator) -> str:
        if f.kind is ForceKind.MEMBER:
            return t("state." + f.state.value)
        return t(f"kind.{f.kind.value}")
