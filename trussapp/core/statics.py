"""Statics of a pin-jointed truss (method of joints, written as one linear system).

Unknowns:  member axial forces N_k (+ = tension) and support reactions r.
Equations: for every joint, sum Fx = 0 and sum Fy = 0:

    G x = -P          x = [N_1 .. N_m, r_1 .. r_q]

A tension member pulls each of its joints toward the other end. Deformations
are ignored, so only statically determinate trusses (m + q = 2n) are solved.

Three small collaborators:
    EquilibriumAssembler  builds G and P from a Truss
    StabilityAnalyzer     decides stable / mechanism / indeterminate from G
    EquilibriumSolver     solves G x = -P
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .domain import SUPPORTS, Axis, SupportRegistry, Truss
from .results import AnalysisStatus

RANK_TOL = 1e-9  # relative singular value threshold used for rank decisions


@dataclass(frozen=True)
class Unknown:
    kind: str  # "member" | "reaction"
    owner_id: str  # member id or support id
    axis: Axis | None = None  # reactions only


@dataclass
class EquilibriumSystem:
    matrix: np.ndarray  # G, shape (2n, m + q)
    rhs: np.ndarray  # -P, shape (2n,)
    unknowns: list
    joint_ids: list  # row order: (x, y) of each joint
    geometries: dict  # member id -> MemberGeometry
    global_matrix: np.ndarray  # 3 x q rigid-body equilibrium of the reactions

    @property
    def n_joints(self) -> int:
        return len(self.joint_ids)

    @property
    def n_members(self) -> int:
        return sum(1 for u in self.unknowns if u.kind == "member")

    @property
    def n_reactions(self) -> int:
        return sum(1 for u in self.unknowns if u.kind == "reaction")


class EquilibriumAssembler:
    def __init__(self, registry: SupportRegistry = SUPPORTS):
        self._registry = registry

    def assemble(self, truss: Truss) -> EquilibriumSystem:
        joint_ids = [p.id for p in truss.points]
        row = {pid: 2 * i for i, pid in enumerate(joint_ids)}
        xc, yc = truss.centroid
        geometries = {m.id: truss.geometry_of(m) for m in truss.members}

        columns, unknowns, global_cols = [], [], []
        for member in truss.members:
            g = geometries[member.id]
            col = np.zeros(2 * len(joint_ids))
            a, b = row[member.start_point], row[member.end_point]
            col[a], col[a + 1] = g.ux, g.uy  # tension pulls the start joint toward the end
            col[b], col[b + 1] = -g.ux, -g.uy
            columns.append(col)
            unknowns.append(Unknown("member", member.id))

        for support in truss.supports:
            point = truss.point(support.point)
            for axis in self._registry.get(support.kind).reaction_axes:
                col = np.zeros(2 * len(joint_ids))
                if axis is Axis.X:
                    col[row[support.point]] = 1.0
                    global_cols.append([1.0, 0.0, -(point.y - yc)])
                else:
                    col[row[support.point] + 1] = 1.0
                    global_cols.append([0.0, 1.0, point.x - xc])
                columns.append(col)
                unknowns.append(Unknown("reaction", support.id, axis))

        load_vector = np.zeros(2 * len(joint_ids))
        for load in truss.loads:
            load_vector[row[load.point]] += load.fx
            load_vector[row[load.point] + 1] += load.fy

        matrix = np.array(columns).T if columns else np.zeros((2 * len(joint_ids), 0))
        global_matrix = np.array(global_cols).T if global_cols else np.zeros((3, 0))
        return EquilibriumSystem(matrix, -load_vector, unknowns, joint_ids, geometries, global_matrix)


@dataclass
class StabilityReport:
    status: AnalysisStatus
    equations: int
    unknowns: int
    rank: int
    external_rank: int
    mechanisms: int  # equations - rank
    degree: int  # unknowns - equations (> 0: statically indeterminate)
    params: dict = field(default_factory=dict)


def matrix_rank(matrix: np.ndarray) -> int:
    if matrix.size == 0:
        return 0
    s = np.linalg.svd(matrix, compute_uv=False)
    return int((s > RANK_TOL * s[0]).sum()) if s[0] > 0 else 0


class StabilityAnalyzer:
    """Classifies the system from the rank of the joint-equilibrium matrix."""

    def analyze(self, system: EquilibriumSystem) -> StabilityReport:
        equations = system.matrix.shape[0]
        unknowns = system.matrix.shape[1]
        rank = matrix_rank(system.matrix)
        external_rank = matrix_rank(system.global_matrix)
        mechanisms = equations - rank
        degree = unknowns - equations
        if mechanisms > 0:
            status = (AnalysisStatus.UNSTABLE_EXTERNAL if external_rank < 3
                      else AnalysisStatus.UNSTABLE_INTERNAL)
        elif degree > 0:
            status = AnalysisStatus.INDETERMINATE
        else:
            status = AnalysisStatus.SOLVED
        return StabilityReport(status, equations, unknowns, rank, external_rank,
                               mechanisms, degree,
                               {"mechanisms": mechanisms, "degree": degree,
                                "reactions": system.n_reactions})


@dataclass
class Solution:
    values: np.ndarray
    residual: float  # largest |G x + P|


class EquilibriumSolver:
    def solve(self, system: EquilibriumSystem) -> Solution:
        values = np.linalg.solve(system.matrix, system.rhs)
        residual = float(np.abs(system.matrix @ values - system.rhs).max(initial=0.0))
        tolerance = 1e-9 * max(1.0, float(np.abs(values).max(initial=0.0)))
        values = np.where(np.abs(values) < tolerance, 0.0, values)
        return Solution(values, residual)
