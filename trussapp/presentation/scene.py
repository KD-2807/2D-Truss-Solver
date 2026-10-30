"""Renderer-independent drawing of the truss ("scene description").

A Scene is a flat list of simple primitives in world coordinates (y up). The
web page and the desktop app are thin renderers of the same scene, so both
front ends always show exactly the same drawing and the same texts.

Primitives (field `type`): line, polygon, arrow, dot, label.
Sizes in pixels (line width, dot radius, label offset) are independent of zoom.
Primitives with a `ref` are clickable (only present in the overview scene).
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field

from ..core.domain import Axis, Truss
from ..core.errors import InvalidSelectionError, UnknownEntityError
from ..core.results import AnalysisResult, ArrowStyle, ForceKind, ForceVector, MemberState
from .i18n import Translator
from .selection import Selection, ViewMode

# ---- primitives --------------------------------------------------------------


@dataclass
class Ref:
    kind: str  # "joint" | "member"
    id: str


@dataclass
class Line:
    x1: float
    y1: float
    x2: float
    y2: float
    role: str
    width: float = 2.0
    dash: bool = False
    ref: Ref | None = None
    type: str = "line"


@dataclass
class Polygon:
    points: list
    role: str
    fill: bool = False
    width: float = 2.0
    type: str = "polygon"


@dataclass
class Arrow:
    x1: float  # tail
    y1: float
    x2: float  # head
    y2: float
    role: str
    width: float = 3.0
    type: str = "arrow"


@dataclass
class Dot:
    x: float
    y: float
    radius: float
    role: str
    ref: Ref | None = None
    type: str = "dot"


@dataclass
class Label:
    x: float
    y: float
    text: str
    role: str = "label"
    dx: float = 0.0  # pixel offset (screen, +y down)
    dy: float = 0.0
    anchor: str = "middle"  # start | middle | end
    size: int = 13
    bold: bool = False
    type: str = "label"


@dataclass
class Scene:
    mode: str
    title: str
    items: list = field(default_factory=list)
    bounds: tuple = (-1.0, -1.0, 1.0, 1.0)  # xmin, ymin, xmax, ymax (world)

    def to_dict(self) -> dict:
        return asdict(self)


# ---- helpers -----------------------------------------------------------------

_STATE_ROLE = {MemberState.TENSION: "tension", MemberState.COMPRESSION: "compression",
               MemberState.ZERO: "zero"}


def fmt_number(value: float) -> str:
    """Compact number: 5000, 6009.2, -0.35 (no trailing zeros, no '-0')."""
    text = f"{value:.1f}" if abs(value) >= 10 else f"{value:.2f}"
    text = text.rstrip("0").rstrip(".") if "." in text else text
    return "0" if text in ("-0", "") else text


def force_role(force: ForceVector) -> str:
    if force.kind is ForceKind.MEMBER:
        return f"force_{_STATE_ROLE[force.state]}"
    return f"force_{force.kind.value}"


def nice_step(raw: float) -> float:
    exponent = math.floor(math.log10(raw))
    fraction = raw / 10 ** exponent
    nice = 1 if fraction < 1.5 else 2 if fraction < 3.5 else 5 if fraction < 7.5 else 10
    return nice * 10 ** exponent


def outward_label(ux: float, uy: float) -> tuple:
    """Pixel offset and anchor that push a label away from the origin along (ux, uy)."""
    dx, dy = 10 * ux, -12 * uy
    anchor = "start" if ux > 0.3 else "end" if ux < -0.3 else "middle"
    if abs(uy) <= 0.3:
        dy -= 4
    return dx, dy, anchor


def _arrow_with_label(items: list, tx: float, ty: float, hx: float, hy: float, role: str,
                      text: str, label_at_tail: bool) -> None:
    items.append(Arrow(tx, ty, hx, hy, role))
    lx, ly, (ox, oy) = (tx, ty, (tx - hx, ty - hy)) if label_at_tail else (hx, hy, (hx - tx, hy - ty))
    norm = math.hypot(ox, oy) or 1.0
    dx, dy, anchor = outward_label(ox / norm, oy / norm)
    items.append(Label(lx, ly, text, role.replace("force_", "label_"), dx, dy, anchor, bold=True))


def _bounds(items: list, pad_fraction: float = 0.08) -> tuple:
    xs, ys = [], []
    for it in items:
        if it.type == "line" or it.type == "arrow":
            xs += [it.x1, it.x2]
            ys += [it.y1, it.y2]
        elif it.type == "polygon":
            xs += [p[0] for p in it.points]
            ys += [p[1] for p in it.points]
        elif it.type == "dot":
            xs.append(it.x)
            ys.append(it.y)
    if not xs:
        return (-1.0, -1.0, 1.0, 1.0)
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    pad = pad_fraction * max(xmax - xmin, ymax - ymin, 1.0)
    return (xmin - pad, ymin - pad, xmax + pad, ymax + pad)


# ---- overview ----------------------------------------------------------------


class SupportSymbolFactory:
    """Textbook support symbols: pin = triangle, roller = triangle on rollers, hatched ground."""

    def build(self, kind: str, x: float, y: float, size: float, wall: float) -> list:
        horizontal = kind == "roller_x"
        n = (wall, 0.0) if horizontal else (0.0, -1.0)  # node -> ground
        t = (-n[1], n[0])

        def w(a: float, b: float) -> tuple:
            return (x + a * t[0] + b * n[0], y + a * t[1] + b * n[1])

        s, items = size, []
        height = 1.0 * s if kind == "pin" else 0.8 * s
        half = 0.6 * s
        items.append(Polygon([w(0, 0), w(-half, height), w(half, height)], "support", fill=False))
        base = height
        if kind != "pin":
            r = 0.14 * s
            for a in (-0.32 * s, 0.32 * s):
                cx, cy = w(a, height + r)
                items.append(Polygon([(cx + r * math.cos(k * math.pi / 6),
                                       cy + r * math.sin(k * math.pi / 6)) for k in range(12)],
                                     "support"))
            base = height + 2 * r
        ground = 0.95 * s
        p, q = w(-ground, base), w(ground, base)
        items.append(Line(p[0], p[1], q[0], q[1], "support", 3))
        for k in range(7):
            a = -ground + k * (2 * ground / 6)
            h1, h2 = w(a, base), w(a - 0.3 * s, base + 0.3 * s)
            items.append(Line(h1[0], h1[1], h2[0], h2[1], "support", 1.5))
        return items


class OverviewSceneBuilder:
    def __init__(self, symbols: SupportSymbolFactory | None = None):
        self._symbols = symbols or SupportSymbolFactory()

    def build(self, truss: Truss, analysis: AnalysisResult, t: Translator) -> Scene:
        coords = {p.id: (p.x, p.y) for p in truss.points if p.x is not None and p.y is not None}
        xs = [c[0] for c in coords.values()] or [0.0]
        ys = [c[1] for c in coords.values()] or [0.0]
        span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
        cx = sum(xs) / len(xs)
        states = {m.id: m.state for m in analysis.members}
        forces = {m.id: m.force for m in analysis.members}

        geometry, symbols, arrows, nodes, labels = [], [], [], [], []

        for m in truss.members:
            if m.start_point in coords and m.end_point in coords:
                (x1, y1), (x2, y2) = coords[m.start_point], coords[m.end_point]
                role = f"member_{_STATE_ROLE[states[m.id]]}" if m.id in states else "member"
                geometry.append(Line(x1, y1, x2, y2, role, 4, ref=Ref("member", m.id)))
                text = m.name or m.id
                labels.append(Label((x1 + x2) / 2, (y1 + y2) / 2, text, "label_member", 0, -9,
                                    size=12))

        for s in truss.supports:
            if s.point in coords and s.kind in ("pin", "roller_y", "roller_x"):
                px, py = coords[s.point]
                symbols += self._symbols.build(s.kind, px, py, 0.05 * span,
                                               -1.0 if px <= cx else 1.0)

        fmax = max([abs(v) for v in (l.fx for l in truss.loads)] +
                   [abs(l.fy) for l in truss.loads] +
                   [abs(r.value) for r in analysis.reactions] + [1e-9])

        def length(value: float) -> float:
            return max(0.05, 0.17 * abs(value) / fmax) * span

        for load in truss.loads:
            if load.point in coords and (load.fx or load.fy):
                px, py = coords[load.point]
                mag = math.hypot(load.fx, load.fy)
                ux, uy = load.fx / mag, load.fy / mag
                size = max(0.05, 0.17 * mag / fmax) * span
                _arrow_with_label(arrows, px - ux * size, py - uy * size, px, py, "force_load",
                                  f"{load.name or load.id} ({fmt_number(load.fx)}, "
                                  f"{fmt_number(load.fy)}) N", label_at_tail=True)
        for r in analysis.reactions:
            if r.value != 0 and r.point in coords:
                px, py = coords[r.point]
                ux, uy = (math.copysign(1, r.value), 0.0) if r.axis == "x" else (0.0, math.copysign(1, r.value))
                size = length(r.value)
                _arrow_with_label(arrows, px, py, px + ux * size, py + uy * size, "force_reaction",
                                  f"{r.name} = {fmt_number(r.value)} N", label_at_tail=False)

        for p in truss.points:
            if p.id in coords:
                x, y = coords[p.id]
                nodes.append(Dot(x, y, 6, "node", Ref("joint", p.id)))
                labels.append(Label(x, y, p.name or p.id, "label_node", 8, -10, "start", 14,
                                    bold=True))

        content = geometry + symbols + arrows + nodes
        bounds = _bounds(content)
        items = self._grid(bounds) + content + labels
        return Scene("overview", t("title.overview"), items, bounds)

    @staticmethod
    def _grid(bounds: tuple) -> list:
        xmin, ymin, xmax, ymax = bounds
        step = nice_step(max(xmax - xmin, ymax - ymin) / 8)
        items = []
        k = math.ceil(xmin / step)
        while k * step <= xmax:
            x = k * step
            items.append(Line(x, ymin, x, ymax, "grid", 1))
            items.append(Label(x, ymin, fmt_number(x), "tick", 0, -4, "middle", 10))
            k += 1
        k = math.ceil(ymin / step)
        while k * step <= ymax:
            y = k * step
            items.append(Line(xmin, y, xmax, y, "grid", 1))
            items.append(Label(xmin, y, fmt_number(y), "tick", 4, -3, "start", 10))
            k += 1
        if xmin <= 0 <= xmax:
            items.append(Line(0, ymin, 0, ymax, "axis", 1.5))
        if ymin <= 0 <= ymax:
            items.append(Line(xmin, 0, xmax, 0, "axis", 1.5))
            items.append(Label(xmax, 0, "x", "tick", -4, 14, "end", 12, True))
        if xmin <= 0 <= xmax:
            items.append(Label(0, ymax, "y", "tick", 8, 12, "start", 12, True))
        return items


# ---- isolated joint ------------------------------------------------------------


class JointSceneBuilder:
    L_MIN, L_MAX = 0.4, 1.0

    def build(self, analysis: AnalysisResult, joint_id: str, t: Translator) -> Scene:
        view = analysis.joint_views[joint_id]
        fmax = max([f.magnitude for f in view.forces] + [1e-9])
        items = []
        for f in view.forces:
            if f.magnitude <= 1e-12:
                self._zero_member(items, f, t)
                continue
            ux, uy = f.fx / f.magnitude, f.fy / f.magnitude
            size = self.L_MIN + (self.L_MAX - self.L_MIN) * f.magnitude / fmax
            text = self._text(f, t)
            if f.arrow is ArrowStyle.OUT:  # tension pulls away: tail on the joint
                _arrow_with_label(items, 0, 0, ux * size, uy * size, force_role(f), text, False)
            else:  # compression, loads, reactions: head on the joint
                _arrow_with_label(items, -ux * size, -uy * size, 0, 0, force_role(f), text, True)
        items.append(Dot(0, 0, 8, "node"))
        items.append(Label(0, 0, view.point_name, "label_node", 12, 20, "start", 18, True))
        bound = self.L_MAX + 0.15
        return Scene("joint", t("title.joint", name=view.point_name), items,
                     (-bound, -bound, bound, bound))

    @staticmethod
    def _text(f: ForceVector, t: Translator) -> str:
        if f.kind is ForceKind.MEMBER:
            return t("scene.member_force", name=f.name, value=fmt_number(f.magnitude),
                     state=t(f"state.{f.state.value}"))
        return f"{f.name} = {fmt_number(f.magnitude)} N"

    def _zero_member(self, items: list, f: ForceVector, t: Translator) -> None:
        size = 0.55
        hx, hy = f.toward_x * size, f.toward_y * size
        items.append(Line(0, 0, hx, hy, "force_zero", 2, dash=True))
        dx, dy, anchor = outward_label(f.toward_x, f.toward_y)
        items.append(Label(hx, hy, f"{f.name} = 0", "label_zero", dx, dy, anchor, bold=True))


# ---- isolated member -----------------------------------------------------------


class MemberSceneBuilder:
    HALF = 1.0
    ARROW = 0.75

    def build(self, analysis: AnalysisResult, member_id: str, t: Translator) -> Scene:
        view = analysis.member_views[member_id]
        m = view.member
        ux, uy = math.cos(math.radians(m.angle_deg)), math.sin(math.radians(m.angle_deg))
        start = (-ux * self.HALF, -uy * self.HALF)
        end = (ux * self.HALF, uy * self.HALF)
        role = f"member_{_STATE_ROLE[m.state]}"
        items = [Line(start[0], start[1], end[0], end[1], role, 6)]
        for (px, py), force in zip((start, end), view.end_forces):
            if force.magnitude > 1e-12:
                fx, fy = force.fx / force.magnitude, force.fy / force.magnitude
                size = self.ARROW
                text = JointSceneBuilder._text(force, t)
                if force.arrow is ArrowStyle.OUT:
                    _arrow_with_label(items, px, py, px + fx * size, py + fy * size,
                                      force_role(force), text, False)
                else:
                    _arrow_with_label(items, px - fx * size, py - fy * size, px, py,
                                      force_role(force), text, True)
        items.append(Dot(*start, 7, "node"))
        items.append(Dot(*end, 7, "node"))
        items.append(Label(*start, view.start_name, "label_node", -10, 22, "middle", 16, True))
        items.append(Label(*end, view.end_name, "label_node", 10, 22, "middle", 16, True))
        label = t("scene.member_force", name=f"N_{m.name}", value=fmt_number(abs(m.force)),
                  state=t(f"state.{m.state.value}"))
        items.append(Label(0, 0, label, f"label_{_STATE_ROLE[m.state]}", 18, 0, "start", 15, True))
        bound = self.HALF + self.ARROW + 0.2
        return Scene("member", t("title.member", name=m.name), items, (-bound, -bound, bound, bound))


# ---- facade --------------------------------------------------------------------


class SceneBuilder:
    """Picks the builder that matches the selection (strategy per view mode)."""

    def __init__(self, overview=None, joint=None, member=None):
        self._overview = overview or OverviewSceneBuilder()
        self._joint = joint or JointSceneBuilder()
        self._member = member or MemberSceneBuilder()

    def build(self, truss: Truss, analysis: AnalysisResult, selection: Selection,
              t: Translator) -> Scene:
        if selection.mode is ViewMode.OVERVIEW:
            return self._overview.build(truss, analysis, t)
        if not analysis.solved:
            raise InvalidSelectionError("the truss has to be solved before isolating a joint or member")
        if selection.mode is ViewMode.JOINT:
            if selection.target_id not in analysis.joint_views:
                raise UnknownEntityError(f"joint '{selection.target_id}' not found")
            return self._joint.build(analysis, selection.target_id, t)
        if selection.target_id not in analysis.member_views:
            raise UnknownEntityError(f"member '{selection.target_id}' not found")
        return self._member.build(analysis, selection.target_id, t)
