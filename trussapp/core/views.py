"""Turns the raw solution vector into result objects and free-body views.

    ResultAssembler   members + reactions with names, states and angles
    JointViewBuilder  all forces acting on one isolated joint
    MemberViewBuilder the forces applied by the end joints on one member
"""
from __future__ import annotations

import math

import numpy as np

from .domain import Truss
from .results import (ArrowStyle, ForceKind, ForceVector, JointView, MemberResult,
                      MemberState, MemberView, ReactionResult)


def angle_of(fx: float, fy: float, tol: float = 0.0) -> float | None:
    """Direction angle in [0, 360) degrees, None for a zero vector."""
    if math.hypot(fx, fy) <= tol:
        return None
    angle = math.degrees(math.atan2(fy, fx)) % 360.0
    return 0.0 if abs(angle - 360.0) < 1e-9 else angle


def state_of(force: float, tol: float) -> MemberState:
    if abs(force) <= tol:
        return MemberState.ZERO
    return MemberState.TENSION if force > 0 else MemberState.COMPRESSION


class ResultAssembler:
    """Splits the solution vector into member results and reactions."""

    def __init__(self, truss: Truss, unknowns: list, values: np.ndarray, geometries: dict):
        self._truss, self._unknowns, self._values, self._geo = truss, unknowns, values, geometries
        self._tol = 1e-9 * max(1.0, float(np.abs(values).max(initial=0.0)))

    def members(self) -> list:
        forces = {u.owner_id: float(v) for u, v in zip(self._unknowns, self._values)
                  if u.kind == "member"}
        out = []
        for m in self._truss.members:
            g, n = self._geo[m.id], forces[m.id]
            out.append(MemberResult(m.id, m.name or m.id, m.start_point, m.end_point, m.material,
                                    g.length, g.angle_deg, n, state_of(n, self._tol)))
        return out

    def reactions(self) -> list:
        out = []
        for u, v in zip(self._unknowns, self._values):
            if u.kind != "reaction":
                continue
            support = next(s for s in self._truss.supports if s.id == u.owner_id)
            point = self._truss.point(support.point)
            label = point.name or point.id
            value = float(v)
            fx, fy = (value, 0.0) if u.axis.value == "x" else (0.0, value)
            out.append(ReactionResult(support.id, support.name or support.id, support.kind,
                                      point.id, label, f"{label}_{u.axis.value}", u.axis.value,
                                      value, angle_of(fx, fy), ))
        return out


def _member_force_on_joint(member: MemberResult, joint_id: str, truss: Truss,
                           geometries: dict) -> ForceVector:
    """Force the member exerts on `joint_id` (tension pulls toward the other end)."""
    g = geometries[member.id]
    at_start = joint_id == member.start_point
    ux, uy = (g.ux, g.uy) if at_start else (-g.ux, -g.uy)  # joint -> other end
    other_id = member.end_point if at_start else member.start_point
    other = truss.point(other_id)
    fx, fy = member.force * ux, member.force * uy
    arrow = ArrowStyle.OUT if member.state is MemberState.TENSION else ArrowStyle.INTO
    return ForceVector(f"N_{member.name}", ForceKind.MEMBER, fx, fy, abs(member.force),
                       angle_of(fx, fy, 1e-12), arrow, state=member.state, source_id=member.id,
                       other_point=other_id, other_point_name=other.name or other.id,
                       toward_x=ux, toward_y=uy)


class JointViewBuilder:
    def __init__(self, truss: Truss, members: list, reactions: list, geometries: dict):
        self._truss, self._geo = truss, geometries
        self._members = {m.id: m for m in members}
        self._reactions = reactions

    def build(self, point_id: str) -> JointView:
        truss = self._truss
        point = truss.point(point_id)
        forces = []
        for load in truss.loads_at(point_id):
            if load.fx or load.fy:
                forces.append(ForceVector(load.name or load.id, ForceKind.LOAD, load.fx, load.fy,
                                          math.hypot(load.fx, load.fy), angle_of(load.fx, load.fy),
                                          ArrowStyle.INTO, source_id=load.id))
        for r in self._reactions:
            if r.point == point_id:
                fx, fy = (r.value, 0.0) if r.axis == "x" else (0.0, r.value)
                forces.append(ForceVector(r.name, ForceKind.REACTION, fx, fy, abs(r.value),
                                          r.angle_deg, ArrowStyle.INTO, source_id=r.support_id))
        for member in truss.members_at(point_id):
            forces.append(_member_force_on_joint(self._members[member.id], point_id, truss,
                                                 self._geo))
        sum_fx, sum_fy = sum(f.fx for f in forces), sum(f.fy for f in forces)
        scale = max([1.0] + [f.magnitude for f in forces])
        balanced = math.hypot(sum_fx, sum_fy) <= 1e-6 * scale
        return JointView(point.id, point.name or point.id, point.x, point.y, forces,
                         sum_fx, sum_fy, balanced)


class MemberViewBuilder:
    def __init__(self, truss: Truss, members: list, geometries: dict):
        self._truss, self._geo = truss, geometries
        self._members = {m.id: m for m in members}

    def build(self, member_id: str) -> MemberView:
        m = self._members[member_id]
        g = self._geo[member_id]
        start, end = self._truss.point(m.start_point), self._truss.point(m.end_point)
        arrow = ArrowStyle.OUT if m.state is MemberState.TENSION else ArrowStyle.INTO
        # force applied ON the member by the joint: tension pulls the member outward
        out = []
        for joint, sign in ((start, -1.0), (end, 1.0)):
            fx, fy = sign * m.force * g.ux, sign * m.force * g.uy
            # `other_point` is the joint that applies the force: tension pulls the member
            # toward it, compression pushes the member away from it
            out.append(ForceVector(f"N_{m.name}@{joint.name or joint.id}", ForceKind.MEMBER, fx, fy,
                                   abs(m.force), angle_of(fx, fy, 1e-12), arrow, state=m.state,
                                   source_id=joint.id, other_point=joint.id,
                                   other_point_name=joint.name or joint.id,
                                   toward_x=sign * g.ux, toward_y=sign * g.uy))
        return MemberView(m, start.name or start.id, end.name or end.id, out)
