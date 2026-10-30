"""Ready-made trusses (factory functions) used as starting points."""
from __future__ import annotations

from .domain import Load, Material, Member, Point, Support, Truss
from .serialization import truss_to_dict

STEEL = Material("M1", "Steel", 0.001, 200.0, 7850.0)


def triangle() -> Truss:
    t = Truss()
    t.add_material(STEEL)
    for pid, x, y in (("A", 0.0, 0.0), ("B", 4.0, 0.0), ("C", 2.0, 3.0)):
        t.add_point(Point(pid, pid, x, y))
    for a, b in (("A", "B"), ("B", "C"), ("A", "C")):
        t.add_member(Member(a + b, a + b, a, b, "M1"))
    t.add_load(Load("P1", "P1", "C", 0.0, -10000.0))
    t.add_support(Support("S1", "Pin at A", "A", "pin"))
    t.add_support(Support("S2", "Roller at B", "B", "roller_y"))
    return t


def warren(bays: int = 5, bay_width: float = 2.0, height: float = 3.0) -> Truss:
    """Warren truss with a flat top and bottom chord (the shape of the reference sketch).

    Bottom joints: A, K, J, I, H, G ... (bays + 1 joints); top joints: B, C, D, E, F ...
    (bays joints, above the middle of each bay).
    """
    bottom_names = ["A", "K", "J", "I", "H", "G", "L", "M", "N", "O", "P", "Q"]
    top_names = ["B", "C", "D", "E", "F", "R", "S", "T", "U", "V", "W", "X"]
    if not 1 <= bays <= len(top_names):
        raise ValueError(f"bays must be between 1 and {len(top_names)}")
    t = Truss()
    t.add_material(STEEL)
    bottom = [bottom_names[i] for i in range(bays + 1)]
    top = [top_names[i] for i in range(bays)]
    for i, name in enumerate(bottom):
        t.add_point(Point(name, name, i * bay_width, 0.0))
    for i, name in enumerate(top):
        t.add_point(Point(name, name, (i + 0.5) * bay_width, height))

    def link(a: str, b: str) -> None:
        t.add_member(Member(a + b, a + b, a, b, "M1"))

    for i in range(bays):
        link(bottom[i], bottom[i + 1])  # bottom chord
        link(bottom[i], top[i])  # diagonals
        link(top[i], bottom[i + 1])
        if i + 1 < bays:
            link(top[i], top[i + 1])  # top chord
    t.add_support(Support("S1", f"Pin at {bottom[0]}", bottom[0], "pin"))
    t.add_support(Support("S2", f"Roller at {bottom[-1]}", bottom[-1], "roller_y"))
    return t


def warren_example() -> Truss:
    """The 11-joint Warren truss of the reference sketch, with its four loads."""
    t = warren(5, 2.0, 3.0)
    t.add_load(Load("P1", "P1", "B", 5000.0, 0.0))  # horizontal load on B
    t.add_load(Load("P2", "P2", "F", -3000.0, -4000.0))  # inclined load on F
    t.add_load(Load("P3", "P3", "J", 0.0, -6000.0))
    t.add_load(Load("P4", "P4", "H", 0.0, -6000.0))
    return t


def cantilever_bracket() -> Truss:
    """Wall bracket: pin at A, horizontal roller at B, 6 kN hanging from C.

    3 joints, 3 members, 3 reactions. Clean 3-4-5 numbers, easy to check by hand.
    """
    t = Truss()
    t.add_material(STEEL)
    for pid, x, y in (("A", 0.0, 0.0), ("B", 0.0, 3.0), ("C", 4.0, 0.0)):
        t.add_point(Point(pid, pid, x, y))
    for a, b in (("A", "B"), ("A", "C"), ("B", "C")):
        t.add_member(Member(a + b, a + b, a, b, "M1"))
    t.add_load(Load("P1", "P1", "C", 0.0, -6000.0))
    t.add_support(Support("S1", "Pin at A", "A", "pin"))
    t.add_support(Support("S2", "Roller at B", "B", "roller_x"))
    return t


def pratt_example() -> Truss:
    """4-panel Pratt truss (span 12, height 3) with 10 kN on each interior bottom joint.

    8 joints, 13 members, 3 reactions. The middle vertical CG is a zero-force member.
    """
    t = Truss()
    t.add_material(STEEL)
    for pid, x, y in (("A", 0.0, 0.0), ("B", 3.0, 0.0), ("C", 6.0, 0.0),
                      ("D", 9.0, 0.0), ("E", 12.0, 0.0),
                      ("F", 3.0, 3.0), ("G", 6.0, 3.0), ("H", 9.0, 3.0)):
        t.add_point(Point(pid, pid, x, y))

    def link(a: str, b: str) -> None:
        t.add_member(Member(a + b, a + b, a, b, "M1"))

    for a, b in (("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")):  # bottom chord
        link(a, b)
    for a, b in (("F", "G"), ("G", "H")):  # top chord
        link(a, b)
    for a, b in (("B", "F"), ("C", "G"), ("D", "H")):  # verticals
        link(a, b)
    for a, b in (("A", "F"), ("F", "C"), ("C", "H"), ("H", "E")):  # diagonals
        link(a, b)
    t.add_load(Load("P1", "P1", "B", 0.0, -10000.0))
    t.add_load(Load("P2", "P2", "C", 0.0, -10000.0))
    t.add_load(Load("P3", "P3", "D", 0.0, -10000.0))
    t.add_support(Support("S1", "Pin at A", "A", "pin"))
    t.add_support(Support("S2", "Roller at E", "E", "roller_y"))
    return t


def king_post_with_wind() -> Truss:
    """King-post roof truss: 12 kN gravity load plus 3 kN horizontal wind at the apex C.

    4 joints, 5 members, 3 reactions. Reactions are not symmetric, and the king post CM
    is a zero-force member (joint M has no load and AM, MB are collinear).
    """
    t = Truss()
    t.add_material(STEEL)
    for pid, x, y in (("A", 0.0, 0.0), ("M", 4.0, 0.0), ("B", 8.0, 0.0), ("C", 4.0, 3.0)):
        t.add_point(Point(pid, pid, x, y))
    for a, b in (("A", "M"), ("M", "B"), ("A", "C"), ("B", "C"), ("C", "M")):
        t.add_member(Member(a + b, a + b, a, b, "M1"))
    t.add_load(Load("P1", "P1", "C", 3000.0, -12000.0))
    t.add_support(Support("S1", "Pin at A", "A", "pin"))
    t.add_support(Support("S2", "Roller at B", "B", "roller_y"))
    return t


TEMPLATES = {
    "warren_example": ("Warren truss (reference sketch)", warren_example),
    "triangle": ("Simple triangle", triangle),
    "warren_blank": ("Warren truss, no loads", warren),
    "cantilever_bracket": ("Cantilever wall bracket", cantilever_bracket),
    "pratt_example": ("Pratt truss, 4 panels", pratt_example),
    "king_post_with_wind": ("King-post roof truss with wind", king_post_with_wind),
}


def list_templates() -> list:
    return [{"key": key, "name": name} for key, (name, _) in TEMPLATES.items()]


def template_dict(key: str) -> dict:
    if key not in TEMPLATES:
        raise KeyError(key)
    return truss_to_dict(TEMPLATES[key][1]())