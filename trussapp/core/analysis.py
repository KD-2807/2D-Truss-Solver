"""TrussAnalysisService: the single entry point of the core.

validate -> assemble -> stability check -> solve -> result + free-body views.
Every collaborator is injected, so each step can be replaced or tested alone.
"""
from __future__ import annotations

from .domain import Truss
from .results import AnalysisResult, AnalysisStatus, Issue
from .statics import EquilibriumAssembler, EquilibriumSolver, StabilityAnalyzer
from .validation import TrussValidator
from .views import JointViewBuilder, MemberViewBuilder, ResultAssembler


class TrussAnalysisService:
    def __init__(self, validator: TrussValidator | None = None,
                 assembler: EquilibriumAssembler | None = None,
                 stability: StabilityAnalyzer | None = None,
                 solver: EquilibriumSolver | None = None):
        self._validator = validator or TrussValidator()
        self._assembler = assembler or EquilibriumAssembler()
        self._stability = stability or StabilityAnalyzer()
        self._solver = solver or EquilibriumSolver()

    def analyze(self, truss: Truss) -> AnalysisResult:
        issues = self._validator.validate(truss)
        if issues:
            return AnalysisResult(AnalysisStatus.INVALID_INPUT, issues=issues)

        system = self._assembler.assemble(truss)
        report = self._stability.analyze(system)
        counts = {"points": system.n_joints, "members": system.n_members,
                  "reactions": system.n_reactions, "equations": report.equations,
                  "unknowns": report.unknowns, "degree": report.degree,
                  "mechanisms": report.mechanisms}
        result = AnalysisResult(report.status, counts=counts)

        if report.status is not AnalysisStatus.SOLVED:
            result.issues.append(Issue(f"status_{report.status.value}", report.params))
            return result

        solution = self._solver.solve(system)
        assembler = ResultAssembler(truss, system.unknowns, solution.values, system.geometries)
        result.members = assembler.members()
        result.reactions = assembler.reactions()
        result.residual = solution.residual

        joints = JointViewBuilder(truss, result.members, result.reactions, system.geometries)
        members = MemberViewBuilder(truss, result.members, system.geometries)
        result.joint_views = {p.id: joints.build(p.id) for p in truss.points}
        result.member_views = {m.id: members.build(m.id) for m in truss.members}
        return result
