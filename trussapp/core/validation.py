"""Input validation: a list of small independent rules (open/closed).

Each rule inspects the truss and yields `Issue`s. Add a rule class and append
it to DEFAULT_RULES to extend the validation without touching the others.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter

from .domain import SUPPORTS, SupportRegistry, Truss
from .results import Issue


class ValidationRule(ABC):
    @abstractmethod
    def check(self, truss: Truss):
        """Yield Issue objects."""


class UniqueIdsRule(ValidationRule):
    def check(self, truss: Truss):
        tables = {"points": truss.points, "members": truss.members, "materials": truss.materials,
                  "loads": truss.loads, "supports": truss.supports}
        for table, rows in tables.items():
            counts = Counter(r.id for r in rows if r.id)
            for index, row in enumerate(rows, start=1):
                if not row.id:
                    yield Issue("blank_id", {"table": table, "row": index})
            for rid, n in counts.items():
                if n > 1:
                    yield Issue("duplicate_id", {"table": table, "id": rid})


class PointsRule(ValidationRule):
    def check(self, truss: Truss):
        if not truss.points:
            yield Issue("no_points")
        for p in truss.points:
            if p.id and (p.x is None or p.y is None):
                yield Issue("point_missing_value", {"id": p.id})


class MaterialsRule(ValidationRule):
    def check(self, truss: Truss):
        for m in truss.materials:
            if m.id and (m.area is None or m.modulus is None or m.area <= 0
                         or m.modulus <= 0 or (m.density or 0) < 0):
                yield Issue("material_bad_value", {"id": m.id})


class MembersRule(ValidationRule):
    def check(self, truss: Truss):
        if not truss.members:
            yield Issue("no_members")
        point_ids = {p.id for p in truss.points}
        material_ids = {m.id for m in truss.materials}
        coords = {p.id: (p.x, p.y) for p in truss.points if p.x is not None and p.y is not None}
        for m in truss.members:
            ends_ok = True
            for pid in (m.start_point, m.end_point):
                if pid not in point_ids:
                    ends_ok = False
                    yield Issue("member_bad_point", {"id": m.id, "point": pid})
            if ends_ok:
                if m.start_point == m.end_point:
                    yield Issue("member_same_point", {"id": m.id})
                elif (m.start_point in coords and m.end_point in coords
                      and coords[m.start_point] == coords[m.end_point]):
                    yield Issue("member_zero_length", {"id": m.id})
            if m.material not in material_ids:
                yield Issue("member_bad_material", {"id": m.id, "material": m.material})
        seen = Counter(frozenset((m.start_point, m.end_point)) for m in truss.members)
        for ends, n in seen.items():
            if n > 1 and len(ends) == 2:
                yield Issue("member_duplicate", {"a": sorted(ends)[0], "b": sorted(ends)[1]})
        connected = {pid for m in truss.members for pid in (m.start_point, m.end_point)}
        for p in truss.points:
            if p.id and truss.members and p.id not in connected:
                yield Issue("point_isolated", {"id": p.id})


class LoadsRule(ValidationRule):
    def check(self, truss: Truss):
        point_ids = {p.id for p in truss.points}
        for load in truss.loads:
            if load.point not in point_ids:
                yield Issue("load_bad_point", {"id": load.id, "point": load.point})


class SupportsRule(ValidationRule):
    def __init__(self, registry: SupportRegistry = SUPPORTS):
        self._registry = registry

    def check(self, truss: Truss):
        if not truss.supports:
            yield Issue("no_supports")
        point_ids = {p.id for p in truss.points}
        used = set()
        for s in truss.supports:
            if s.point not in point_ids:
                yield Issue("support_bad_point", {"id": s.id, "point": s.point})
            elif s.point in used:
                yield Issue("support_duplicate_point", {"point": s.point})
            used.add(s.point)
            if s.kind not in self._registry:
                yield Issue("support_bad_type", {"id": s.id, "type": s.kind})


DEFAULT_RULES = (UniqueIdsRule(), PointsRule(), MaterialsRule(), MembersRule(),
                 LoadsRule(), SupportsRule())


class TrussValidator:
    def __init__(self, rules=DEFAULT_RULES):
        self._rules = tuple(rules)

    def validate(self, truss: Truss) -> list:
        return [issue for rule in self._rules for issue in rule.check(truss)]
