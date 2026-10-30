"""Result objects produced by the analysis (plain data, no behaviour)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

FORCE_UNIT = "N"


class AnalysisStatus(str, Enum):
    SOLVED = "solved"
    INVALID_INPUT = "invalid_input"
    UNSTABLE_EXTERNAL = "unstable_external"
    UNSTABLE_INTERNAL = "unstable_internal"
    INDETERMINATE = "indeterminate"


class MemberState(str, Enum):
    TENSION = "tension"
    COMPRESSION = "compression"
    ZERO = "zero"


class ForceKind(str, Enum):
    MEMBER = "member"
    LOAD = "load"
    REACTION = "reaction"


class ArrowStyle(str, Enum):
    """How a force arrow is drawn relative to the body it acts on.

    INTO: the arrow head touches the body (compression, loads, pushes).
    OUT:  the arrow tail is on the body and the head points away (tension, pulls).
    """

    INTO = "into"
    OUT = "out"


@dataclass(frozen=True)
class Issue:
    """A problem in the model; `code` selects a translatable message."""

    code: str
    params: dict = field(default_factory=dict)


@dataclass
class ForceVector:
    """A force acting on a body (a joint or a member end)."""

    name: str  # e.g. "N_BK", "P1", "A_x"
    kind: ForceKind
    fx: float
    fy: float
    magnitude: float
    angle_deg: float | None  # direction of the force vector, [0, 360); None for zero
    arrow: ArrowStyle
    unit: str = FORCE_UNIT
    state: MemberState | None = None  # members only
    source_id: str = ""  # member / load / support id
    other_point: str | None = None  # members: the joint at the other end
    other_point_name: str | None = None
    toward_x: float = 0.0  # members: unit vector from this body toward the other end
    toward_y: float = 0.0


@dataclass
class MemberResult:
    id: str
    name: str
    start_point: str
    end_point: str
    material: str
    length: float
    angle_deg: float
    force: float  # signed axial force, + tension / - compression (N)
    state: MemberState


@dataclass
class ReactionResult:
    support_id: str
    support_name: str
    support_kind: str
    point: str
    point_name: str
    name: str  # e.g. "A_x"
    axis: str  # "x" | "y"
    value: float  # signed: +x right / +y up
    angle_deg: float | None
    unit: str = FORCE_UNIT


@dataclass
class JointView:
    """Free-body diagram data of one isolated joint."""

    point_id: str
    point_name: str
    x: float
    y: float
    forces: list
    sum_fx: float
    sum_fy: float
    balanced: bool


@dataclass
class MemberView:
    """Free-body data of one isolated member (forces applied by its end joints)."""

    member: MemberResult
    start_name: str
    end_name: str
    end_forces: list  # [force on the member at the start end, at the end end]


@dataclass
class AnalysisResult:
    status: AnalysisStatus
    issues: list = field(default_factory=list)
    counts: dict = field(default_factory=dict)
    members: list = field(default_factory=list)
    reactions: list = field(default_factory=list)
    joint_views: dict = field(default_factory=dict)  # point id -> JointView
    member_views: dict = field(default_factory=dict)  # member id -> MemberView
    residual: float | None = None  # largest joint-equilibrium residual

    @property
    def solved(self) -> bool:
        return self.status is AnalysisStatus.SOLVED
