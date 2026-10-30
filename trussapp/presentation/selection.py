"""Selection state machine: one joint OR one member at a time.

    OVERVIEW --select_joint/select_member--> JOINT / MEMBER --back--> OVERVIEW

While a target is isolated no other target can be chosen; the user must go
back to the whole truss first.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..core.errors import InvalidSelectionError, UnknownEntityError


class ViewMode(str, Enum):
    OVERVIEW = "overview"
    JOINT = "joint"
    MEMBER = "member"


@dataclass(frozen=True)
class Selection:
    mode: ViewMode = ViewMode.OVERVIEW
    target_id: str | None = None

    @classmethod
    def parse(cls, mode: str | None, target: str | None) -> "Selection":
        try:
            view_mode = ViewMode(mode or "overview")
        except ValueError:
            raise InvalidSelectionError(f"unknown view mode '{mode}'") from None
        if view_mode is not ViewMode.OVERVIEW and not target:
            raise InvalidSelectionError("a joint/member view needs a target id")
        return cls(view_mode, target if view_mode is not ViewMode.OVERVIEW else None)


class SelectionController:
    def __init__(self, joint_ids=lambda: (), member_ids=lambda: (), on_change=None):
        self._joint_ids, self._member_ids = joint_ids, member_ids
        self._on_change = on_change
        self._selection = Selection()

    @property
    def selection(self) -> Selection:
        return self._selection

    def _require_overview(self) -> None:
        if self._selection.mode is not ViewMode.OVERVIEW:
            raise InvalidSelectionError("go back to the truss before selecting another target")

    def _set(self, selection: Selection) -> None:
        self._selection = selection
        if self._on_change:
            self._on_change(selection)

    def select_joint(self, point_id: str) -> None:
        self._require_overview()
        if point_id not in set(self._joint_ids()):
            raise UnknownEntityError(f"joint '{point_id}' not found")
        self._set(Selection(ViewMode.JOINT, point_id))

    def select_member(self, member_id: str) -> None:
        self._require_overview()
        if member_id not in set(self._member_ids()):
            raise UnknownEntityError(f"member '{member_id}' not found")
        self._set(Selection(ViewMode.MEMBER, member_id))

    def back(self) -> None:
        self._set(Selection())

    def reset(self) -> None:
        """Silently drop the selection (e.g. the model changed)."""
        self._selection = Selection()
