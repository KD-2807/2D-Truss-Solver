"""English / Vietnamese texts shared by the web and desktop front ends.

Missing Vietnamese keys fall back to English.
"""
from __future__ import annotations

LANGUAGES = {"en": "English", "vi": "Tiếng Việt"}

EN = {
    "app.title": "2D PLANAR TRUSS ANALYSIS",
    "app.caption": "Units: m · N · E in 10⁹ Pa · A in m² · density in kg/m³",
    "ui.language": "Language",
    "ui.template": "Example",
    "ui.load_template": "Load example",
    "ui.back": "← Back to the truss",
    "ui.hint_overview": "Click a joint or a member to isolate it.",
    "ui.hint_joint": "Joint {name} isolated. Go back to the truss to choose another.",
    "ui.hint_member": "Member {name} isolated. Go back to the truss to choose another.",
    "ui.add_row": "+ Add row",
    "ui.delete": "Delete",
    "ui.open": "Open file",
    "ui.save": "Save file",
    "ui.status": "Status",
    "ui.legend": "Legend",
    "ui.legend_tension": "Tension",
    "ui.legend_compression": "Compression",
    "ui.legend_zero": "Zero force",
    "ui.error": "Error",
    "template.warren_example": "Warren truss (reference sketch)",
    "template.triangle": "Simple triangle",
    "template.warren_blank": "Warren truss, no loads",
    "template.cantilever_bracket": "Cantilever wall bracket",
    "template.pratt_example": "Pratt truss, 4 panels",
    "template.king_post_with_wind": "King-post roof truss with wind",
    "tab.points": "Points",
    "tab.members": "Members",
    "tab.materials": "Materials",
    "tab.loads": "Loads",
    "tab.supports": "Supports",
    "col.id": "ID", "col.name": "Name", "col.x": "x (m)", "col.y": "y (m)",
    "col.start_point": "Start", "col.end_point": "End", "col.material": "Material",
    "col.A": "A (m²)", "col.E": "E (10⁹ Pa)", "col.density": "Density (kg/m³)",
    "col.point": "Point", "col.Fx": "Fx (N)", "col.Fy": "Fy (N)", "col.type": "Support type",
    "support.pin": "Pin support (Rx, Ry)",
    "support.roller_y": "Roller support (Ry)",
    "support.roller_x": "Roller support (Rx)",
    "status.solved": "Solved: all reactions and member forces found.",
    "status.invalid_input": "Invalid input: fix the following errors.",
    "status.unstable_external": "Unstable: the supports cannot hold the truss.",
    "status.unstable_internal": "Unstable: the truss contains a mechanism.",
    "status.indeterminate": "Statically indeterminate: cannot be solved by statics alone.",
    "title.overview": "Truss",
    "title.joint": "Joint {name}",
    "title.member": "Member {name}",
    "table.reactions": "Support reactions",
    "table.members": "Member forces",
    "table.joint": "Forces acting on joint {name}",
    "table.member": "Forces acting on member {name}",
    "table.analysis": "Analysis",
    "c.name": "Name", "c.kind": "Type", "c.magnitude": "Magnitude", "c.unit": "Unit",
    "c.angle": "Angle (°)", "c.sense": "Direction", "c.fx": "Fx (N)", "c.fy": "Fy (N)",
    "c.support": "Support", "c.point": "Point", "c.state": "State", "c.force": "Force (N)",
    "c.length": "Length (m)", "c.start": "Start", "c.end": "End", "c.applied_by": "Applied by",
    "kind.member": "Member force", "kind.load": "Applied load", "kind.reaction": "Reaction",
    "state.tension": "Tension", "state.compression": "Compression", "state.zero": "Zero force",
    "sense.pull_toward": "pulls toward {other}",
    "sense.push_away": "pushes away from {other}",
    "sense.zero": "none",
    "dir.right": "right", "dir.left": "left", "dir.up": "up", "dir.down": "down",
    "balance.ok": "Equilibrium: ΣFx = {fx} N, ΣFy = {fy} N",
    "balance.bad": "NOT balanced: ΣFx = {fx} N, ΣFy = {fy} N",
    "an.points": "Joints (n)", "an.members": "Members (m)", "an.reactions": "Reaction components (r)",
    "an.equations": "Equations (2n)", "an.unknowns": "Unknowns (m + r)",
    "an.degree": "Degree of indeterminacy (m + r − 2n)", "an.mechanisms": "Mechanisms",
    "an.residual": "Max equilibrium residual (N)",
    "scene.member_force": "{name} = {value} N ({state})",
    "scene.at_end": "at {point}",
    "issue.no_points": "No points defined.",
    "issue.blank_id": "Row {row} of '{table}' has no id.",
    "issue.duplicate_id": "Duplicate id '{id}' in '{table}'.",
    "issue.point_missing_value": "Point '{id}': x and y are required.",
    "issue.no_members": "No members defined.",
    "issue.member_bad_point": "Member '{id}': point '{point}' not found.",
    "issue.member_same_point": "Member '{id}': start and end points are the same.",
    "issue.member_zero_length": "Member '{id}': length is zero.",
    "issue.member_bad_material": "Member '{id}': material '{material}' not found.",
    "issue.member_duplicate": "Two members connect the same joints {a} and {b}.",
    "issue.point_isolated": "Point '{id}' is not connected to any member.",
    "issue.material_bad_value": "Material '{id}': A and E must be positive, density cannot be negative.",
    "issue.load_bad_point": "Load '{id}': point '{point}' not found.",
    "issue.no_supports": "No supports defined.",
    "issue.support_bad_point": "Support '{id}': point '{point}' not found.",
    "issue.support_bad_type": "Support '{id}': unknown support type '{type}'.",
    "issue.support_duplicate_point": "More than one support at point '{point}'.",
    "issue.status_unstable_external": (
        "The supports cannot prevent rigid-body motion (reaction lines are parallel, concurrent "
        "or too few): {mechanisms} free motion(s)."),
    "issue.status_unstable_internal": (
        "The truss has {mechanisms} internal mechanism(s): a part is not triangulated or is "
        "disconnected."),
    "issue.status_indeterminate": (
        "Statically indeterminate (degree {degree}): the joint equations cannot give all "
        "member forces and {reactions} reaction components."),
}

VI = {
    "app.title": "PHÂN TÍCH HỆ GIÀN PHẲNG 2D",
    "app.caption": "Đơn vị: m · N · E tính bằng 10⁹ Pa · A tính bằng m² · khối lượng riêng kg/m³",
    "ui.language": "Ngôn ngữ",
    "ui.template": "Ví dụ mẫu",
    "ui.load_template": "Tải ví dụ",
    "ui.back": "← Quay lại toàn hệ",
    "ui.hint_overview": "Bấm vào một nút hoặc một thanh để tách ra xem.",
    "ui.hint_joint": "Đang xem nút {name}. Hãy quay lại toàn hệ để chọn nút/thanh khác.",
    "ui.hint_member": "Đang xem thanh {name}. Hãy quay lại toàn hệ để chọn nút/thanh khác.",
    "ui.add_row": "+ Thêm hàng",
    "ui.delete": "Xóa",
    "ui.open": "Mở file",
    "ui.save": "Lưu file",
    "ui.status": "Trạng thái",
    "ui.legend": "Chú giải",
    "ui.legend_tension": "Kéo",
    "ui.legend_compression": "Nén",
    "ui.legend_zero": "Thanh không chịu lực",
    "ui.error": "Lỗi",
    "template.warren_example": "Giàn Warren (hình minh họa)",
    "template.triangle": "Giàn tam giác đơn giản",
    "template.warren_blank": "Giàn Warren, không tải",
    "template.cantilever_bracket": "Giá đỡ công-xôn gắn tường",
    "template.pratt_example": "Giàn Pratt 4 khoang",
    "template.king_post_with_wind": "Giàn mái cột đứng chịu gió",
    "tab.points": "Điểm", "tab.members": "Thanh", "tab.materials": "Vật liệu",
    "tab.loads": "Tải trọng", "tab.supports": "Gối đỡ",
    "col.id": "Mã", "col.name": "Tên", "col.start_point": "Điểm đầu", "col.end_point": "Điểm cuối",
    "col.material": "Vật liệu", "col.density": "Khối lượng riêng (kg/m³)", "col.point": "Điểm",
    "col.type": "Loại gối",
    "support.pin": "Gối cố định (Rx, Ry)",
    "support.roller_y": "Gối di động (Ry)",
    "support.roller_x": "Gối di động (Rx)",
    "status.solved": "Đã giải: tìm được toàn bộ phản lực và nội lực thanh.",
    "status.invalid_input": "Dữ liệu không hợp lệ: hãy sửa các lỗi sau.",
    "status.unstable_external": "Hệ không ổn định: các gối không giữ được giàn.",
    "status.unstable_internal": "Hệ không ổn định: giàn có cơ cấu biến hình.",
    "status.indeterminate": "Hệ siêu tĩnh: không giải được chỉ bằng phương trình cân bằng.",
    "title.overview": "Toàn hệ giàn",
    "title.joint": "Nút {name}",
    "title.member": "Thanh {name}",
    "table.reactions": "Phản lực liên kết",
    "table.members": "Ứng lực trong các thanh",
    "table.joint": "Các lực tác dụng lên nút {name}",
    "table.member": "Các lực tác dụng lên thanh {name}",
    "table.analysis": "Phân tích",
    "c.name": "Tên", "c.kind": "Loại", "c.magnitude": "Độ lớn", "c.unit": "Đơn vị",
    "c.angle": "Góc (°)", "c.sense": "Phương chiều", "c.support": "Gối", "c.point": "Điểm",
    "c.state": "Trạng thái", "c.force": "Lực (N)", "c.length": "Chiều dài (m)",
    "c.start": "Đầu", "c.end": "Cuối", "c.applied_by": "Do nút tác dụng",
    "kind.member": "Nội lực thanh", "kind.load": "Tải trọng", "kind.reaction": "Phản lực",
    "state.tension": "Kéo", "state.compression": "Nén", "state.zero": "Không chịu lực",
    "sense.pull_toward": "kéo về phía {other}",
    "sense.push_away": "đẩy ra xa {other}",
    "sense.zero": "không",
    "dir.right": "sang phải", "dir.left": "sang trái", "dir.up": "lên trên", "dir.down": "xuống dưới",
    "balance.ok": "Cân bằng: ΣFx = {fx} N, ΣFy = {fy} N",
    "balance.bad": "KHÔNG cân bằng: ΣFx = {fx} N, ΣFy = {fy} N",
    "an.points": "Số nút (n)", "an.members": "Số thanh (m)", "an.reactions": "Số thành phần phản lực (r)",
    "an.equations": "Số phương trình (2n)", "an.unknowns": "Số ẩn (m + r)",
    "an.degree": "Bậc siêu tĩnh (m + r − 2n)", "an.mechanisms": "Số cơ cấu biến hình",
    "an.residual": "Sai số cân bằng lớn nhất (N)",
    "scene.member_force": "{name} = {value} N ({state})",
    "scene.at_end": "tại {point}",
    "issue.no_points": "Chưa có điểm nào.",
    "issue.blank_id": "Hàng {row} của bảng '{table}' chưa có mã.",
    "issue.duplicate_id": "Mã '{id}' bị trùng trong bảng '{table}'.",
    "issue.point_missing_value": "Điểm '{id}': thiếu x hoặc y.",
    "issue.no_members": "Chưa có thanh nào.",
    "issue.member_bad_point": "Thanh '{id}': không tìm thấy điểm '{point}'.",
    "issue.member_same_point": "Thanh '{id}': điểm đầu và điểm cuối trùng nhau.",
    "issue.member_zero_length": "Thanh '{id}': chiều dài bằng 0.",
    "issue.member_bad_material": "Thanh '{id}': không tìm thấy vật liệu '{material}'.",
    "issue.member_duplicate": "Có hai thanh cùng nối hai nút {a} và {b}.",
    "issue.point_isolated": "Điểm '{id}' chưa nối với thanh nào.",
    "issue.material_bad_value": "Vật liệu '{id}': A và E phải dương, khối lượng riêng không được âm.",
    "issue.load_bad_point": "Tải '{id}': không tìm thấy điểm '{point}'.",
    "issue.no_supports": "Chưa có gối đỡ nào.",
    "issue.support_bad_point": "Gối '{id}': không tìm thấy điểm '{point}'.",
    "issue.support_bad_type": "Gối '{id}': loại gối '{type}' không hợp lệ.",
    "issue.support_duplicate_point": "Có nhiều hơn một gối tại điểm '{point}'.",
    "issue.status_unstable_external": (
        "Các gối không ngăn được chuyển động của cả giàn (phản lực song song, đồng quy hoặc quá ít): "
        "{mechanisms} chuyển động tự do."),
    "issue.status_unstable_internal": (
        "Giàn có {mechanisms} cơ cấu biến hình bên trong: có phần chưa tạo tam giác hoặc bị tách rời."),
    "issue.status_indeterminate": (
        "Hệ siêu tĩnh bậc {degree}: các phương trình cân bằng nút không đủ để tìm hết nội lực "
        "và {reactions} thành phần phản lực."),
}

TABLES = {"en": EN, "vi": VI}


class Translator:
    """t(key, **params) with English fallback."""

    def __init__(self, lang: str = "en"):
        self.lang = lang if lang in TABLES else "en"
        self._table = TABLES[self.lang]

    def __call__(self, key: str, **params) -> str:
        text = self._table.get(key) or EN.get(key) or key
        try:
            return text.format(**params) if params else text
        except (KeyError, IndexError):
            return text

    def has(self, key: str) -> bool:
        return key in EN

    def bundle(self) -> dict:
        """All strings of this language (for the web front end)."""
        return {**EN, **self._table}

    def issue(self, issue) -> str:
        params = dict(issue.params)
        if "table" in params:
            params["table"] = params["table"]
        return self(f"issue.{issue.code}", **params)