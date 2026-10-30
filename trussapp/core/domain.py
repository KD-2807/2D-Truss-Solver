"""Domain model of a 2D planar pin-jointed truss.

Units: length = m, force = N, E = 1e9 Pa, A = m^2, density = kg/m^3.
Axes: +x to the right, +y up.

While a truss is being edited, numeric fields may be ``None`` (an unfinished
table row). ``TrussValidator`` guards the solver against such drafts.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

from .errors import DuplicateIdError, UnknownEntityError


class Axis(str, Enum):
    X = "x"
    Y = "y"


@dataclass(frozen=True)
class SupportKind:
    """A support type: which displacement components it restrains.

    Every restrained component produces one reaction force along that axis.
    New support types are added by registering a new instance (open/closed).
    """

    key: str
    reaction_axes: tuple

    @property
    def reaction_count(self) -> int:
        return len(self.reaction_axes)


class SupportRegistry:
    """Lookup of the known support kinds."""

    def __init__(self, kinds=()):
        self._kinds = {}
        for kind in kinds:
            self.register(kind)

    def register(self, kind: SupportKind) -> None:
        self._kinds[kind.key] = kind

    def get(self, key: str) -> SupportKind:
        try:
            return self._kinds[key]
        except KeyError:
            raise UnknownEntityError(f"unknown support kind '{key}'") from None

    def __contains__(self, key) -> bool:
        return key in self._kinds

    def keys(self) -> list:
        return list(self._kinds)


# Pin: Ux = Uy = 0 -> Rx, Ry.   Roller: only one displacement restrained.
SUPPORTS = SupportRegistry([
    SupportKind("pin", (Axis.X, Axis.Y)),
    SupportKind("roller_y", (Axis.Y,)),
    SupportKind("roller_x", (Axis.X,)),
])


@dataclass(frozen=True)
class Point:
    id: str
    name: str
    x: float | None
    y: float | None


@dataclass(frozen=True)
class Material:
    id: str
    name: str
    area: float | None  # A, m^2
    modulus: float | None  # E, 1e9 Pa
    density: float | None = 0.0  # kg/m^3


@dataclass(frozen=True)
class Member:
    id: str
    name: str
    start_point: str
    end_point: str
    material: str


@dataclass(frozen=True)
class Load:
    """Point load applied on a joint (+fx right, +fy up)."""

    id: str
    name: str
    point: str
    fx: float = 0.0
    fy: float = 0.0


@dataclass(frozen=True)
class Support:
    id: str
    name: str
    point: str
    kind: str  # key of a SupportKind


@dataclass(frozen=True)
class MemberGeometry:
    """Length and orientation of a member (start -> end)."""

    length: float
    ux: float  # unit vector start -> end
    uy: float
    angle_deg: float  # from +x, counterclockwise

    @classmethod
    def between(cls, start: Point, end: Point) -> "MemberGeometry":
        dx, dy = end.x - start.x, end.y - start.y
        length = math.hypot(dx, dy)
        return cls(length, dx / length, dy / length, math.degrees(math.atan2(dy, dx)))


@dataclass
class Truss:
    """Aggregate root: the five input tables of the program."""

    points: list = field(default_factory=list)
    members: list = field(default_factory=list)
    materials: list = field(default_factory=list)
    loads: list = field(default_factory=list)
    supports: list = field(default_factory=list)

    # ---- building ---------------------------------------------------------
    def _add(self, table: list, entity):
        if any(e.id == entity.id for e in table):
            raise DuplicateIdError(f"duplicate id '{entity.id}'")
        table.append(entity)
        return entity

    def add_point(self, point: Point) -> Point:
        return self._add(self.points, point)

    def add_member(self, member: Member) -> Member:
        return self._add(self.members, member)

    def add_material(self, material: Material) -> Material:
        return self._add(self.materials, material)

    def add_load(self, load: Load) -> Load:
        return self._add(self.loads, load)

    def add_support(self, support: Support) -> Support:
        return self._add(self.supports, support)

    # ---- queries ----------------------------------------------------------
    @staticmethod
    def _find(table: list, entity_id: str, what: str):
        for entity in table:
            if entity.id == entity_id:
                return entity
        raise UnknownEntityError(f"{what} '{entity_id}' not found")

    def point(self, point_id: str) -> Point:
        return self._find(self.points, point_id, "point")

    def member(self, member_id: str) -> Member:
        return self._find(self.members, member_id, "member")

    def material(self, material_id: str) -> Material:
        return self._find(self.materials, material_id, "material")

    def geometry_of(self, member: Member) -> MemberGeometry:
        return MemberGeometry.between(self.point(member.start_point), self.point(member.end_point))

    def members_at(self, point_id: str) -> list:
        return [m for m in self.members if point_id in (m.start_point, m.end_point)]

    def loads_at(self, point_id: str) -> list:
        return [l for l in self.loads if l.point == point_id]

    def supports_at(self, point_id: str) -> list:
        return [s for s in self.supports if s.point == point_id]

    @property
    def centroid(self) -> tuple:
        pts = [p for p in self.points if p.x is not None and p.y is not None]
        if not pts:
            return 0.0, 0.0
        return sum(p.x for p in pts) / len(pts), sum(p.y for p in pts) / len(pts)
