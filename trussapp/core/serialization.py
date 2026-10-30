"""Truss <-> plain dict (JSON) conversion.

JSON keys follow the input specification:
    points    : id, name, x, y
    members   : id, name, start_point, end_point, material
    materials : id, name, A, E, density
    loads     : id, name, point, Fx, Fy
    supports  : id, name, point, type

Parsing is tolerant (blank cells, None, NaN) so half-edited tables can be
round-tripped; the validator reports what is missing.
"""
from __future__ import annotations

import math

from .domain import Load, Material, Member, Point, Support, Truss

UNITS = {"length": "m", "force": "N", "E": "1e9 Pa", "A": "m2", "density": "kg/m3"}


def to_text(value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return str(value).strip()


def to_float(value, default=None):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _rows(data: dict, key: str) -> list:
    rows = data.get(key) or []
    return [row for row in rows if isinstance(row, dict)]


def truss_from_dict(data: dict) -> Truss:
    """Build a Truss from a dict; duplicate ids are kept (the validator reports them)."""
    truss = Truss()
    for r in _rows(data, "points"):
        truss.points.append(Point(to_text(r.get("id")), to_text(r.get("name")),
                                  to_float(r.get("x")), to_float(r.get("y"))))
    for r in _rows(data, "materials"):
        truss.materials.append(Material(to_text(r.get("id")), to_text(r.get("name")),
                                        to_float(r.get("A")), to_float(r.get("E")),
                                        to_float(r.get("density"), 0.0)))
    for r in _rows(data, "members"):
        truss.members.append(Member(to_text(r.get("id")), to_text(r.get("name")),
                                    to_text(r.get("start_point")), to_text(r.get("end_point")),
                                    to_text(r.get("material"))))
    for r in _rows(data, "loads"):
        truss.loads.append(Load(to_text(r.get("id")), to_text(r.get("name")),
                                to_text(r.get("point")),
                                to_float(r.get("Fx"), 0.0), to_float(r.get("Fy"), 0.0)))
    for r in _rows(data, "supports"):
        truss.supports.append(Support(to_text(r.get("id")), to_text(r.get("name")),
                                      to_text(r.get("point")), to_text(r.get("type"))))
    return truss


def truss_to_dict(truss: Truss) -> dict:
    return {
        "units": dict(UNITS),
        "points": [{"id": p.id, "name": p.name, "x": p.x, "y": p.y} for p in truss.points],
        "members": [{"id": m.id, "name": m.name, "start_point": m.start_point,
                     "end_point": m.end_point, "material": m.material} for m in truss.members],
        "materials": [{"id": m.id, "name": m.name, "A": m.area, "E": m.modulus,
                       "density": m.density} for m in truss.materials],
        "loads": [{"id": l.id, "name": l.name, "point": l.point, "Fx": l.fx, "Fy": l.fy}
                  for l in truss.loads],
        "supports": [{"id": s.id, "name": s.name, "point": s.point, "type": s.kind}
                     for s in truss.supports],
    }
