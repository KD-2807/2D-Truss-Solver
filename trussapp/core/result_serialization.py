"""AnalysisResult <-> plain dict (the JSON contract between the services)."""
from __future__ import annotations

from dataclasses import asdict
from enum import Enum

from .results import (AnalysisResult, AnalysisStatus, ArrowStyle, ForceKind, ForceVector,
                      Issue, JointView, MemberResult, MemberState, MemberView, ReactionResult)


def _plain(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def analysis_to_dict(result: AnalysisResult) -> dict:
    data = _plain(asdict(result))
    data["solved"] = result.solved
    return data


def _force(d: dict) -> ForceVector:
    return ForceVector(**{**d, "kind": ForceKind(d["kind"]), "arrow": ArrowStyle(d["arrow"]),
                          "state": MemberState(d["state"]) if d.get("state") else None})


def _member(d: dict) -> MemberResult:
    return MemberResult(**{**d, "state": MemberState(d["state"])})


def analysis_from_dict(data: dict) -> AnalysisResult:
    return AnalysisResult(
        status=AnalysisStatus(data["status"]),
        issues=[Issue(i["code"], i.get("params", {})) for i in data.get("issues", [])],
        counts=data.get("counts", {}),
        members=[_member(m) for m in data.get("members", [])],
        reactions=[ReactionResult(**r) for r in data.get("reactions", [])],
        joint_views={k: JointView(**{**v, "forces": [_force(f) for f in v["forces"]]})
                     for k, v in data.get("joint_views", {}).items()},
        member_views={k: MemberView(_member(v["member"]), v["start_name"], v["end_name"],
                                    [_force(f) for f in v["end_forces"]])
                      for k, v in data.get("member_views", {}).items()},
        residual=data.get("residual"),
    )
