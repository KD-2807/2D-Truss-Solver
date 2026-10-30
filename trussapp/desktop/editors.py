"""Editable tables for the five input tables (points, members, materials, loads, supports)."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from ..core.domain import SUPPORTS
from ..core.serialization import to_float

# (json key, kind) per table; kinds: text | number | points | materials | kinds
TABLE_SPECS = {
    "points": ("P", [("id", "text"), ("name", "text"), ("x", "number"), ("y", "number")]),
    "members": ("T", [("id", "text"), ("name", "text"), ("start_point", "points"),
                      ("end_point", "points"), ("material", "materials")]),
    "materials": ("M", [("id", "text"), ("name", "text"), ("A", "number"), ("E", "number"),
                        ("density", "number")]),
    "loads": ("L", [("id", "text"), ("name", "text"), ("point", "points"), ("Fx", "number"),
                    ("Fy", "number")]),
    "supports": ("S", [("id", "text"), ("name", "text"), ("point", "points"), ("type", "kinds")]),
}


class TableEditor(QWidget):
    """One editable table + add/delete buttons. Emits `edited` after every change."""

    edited = Signal()

    def __init__(self, name: str, options, translate, parent=None):
        super().__init__(parent)
        self.name = name
        self._prefix, self._columns = TABLE_SPECS[name]
        self._options = options  # callable(kind) -> [(value, label)]
        self._tr = translate  # callable(key) -> text
        self._loading = False

        self.table = QTableWidget(0, len(self._columns))
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.itemChanged.connect(self._item_changed)
        self.add_button, self.delete_button = QPushButton(), QPushButton()
        self.add_button.clicked.connect(self.add_row)
        self.delete_button.clicked.connect(self.delete_selected)
        buttons = QHBoxLayout()
        buttons.addWidget(self.add_button)
        buttons.addWidget(self.delete_button)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
        layout.addLayout(buttons)
        self.retranslate()

    def retranslate(self) -> None:
        self.table.setHorizontalHeaderLabels([self._tr(f"col.{key}") for key, _ in self._columns])
        self.add_button.setText(self._tr("ui.add_row"))
        self.delete_button.setText(self._tr("ui.delete"))

    # ---- data ---------------------------------------------------------------------
    def rows(self) -> list:
        out = []
        for r in range(self.table.rowCount()):
            row = {}
            for c, (key, kind) in enumerate(self._columns):
                if kind in ("text", "number"):
                    item = self.table.item(r, c)
                    text = item.text().strip() if item else ""
                    row[key] = to_float(text) if kind == "number" else text
                else:
                    combo = self.table.cellWidget(r, c)
                    row[key] = combo.currentData() if combo else ""
            out.append(row)
        return out

    def set_rows(self, rows: list) -> None:
        self._loading = True
        try:
            self.table.setRowCount(0)
            for row in rows:
                self._append(row)
        finally:
            self._loading = False
        self.table.resizeColumnsToContents()

    def refresh_choices(self) -> None:
        """Rebuild the drop-downs (other tables may have new/renamed ids)."""
        self._loading = True
        try:
            for r in range(self.table.rowCount()):
                for c, (key, kind) in enumerate(self._columns):
                    combo = self.table.cellWidget(r, c)
                    if combo is not None:
                        self._fill_combo(combo, kind, combo.currentData())
        finally:
            self._loading = False

    # ---- internals ------------------------------------------------------------------
    def _fill_combo(self, combo: QComboBox, kind: str, value) -> None:
        combo.blockSignals(True)
        combo.clear()
        options = list(self._options(kind))
        if value not in [v for v, _ in options]:
            options.insert(0, (value or "", value or "—"))
        for v, label in options:
            combo.addItem(label, v)
        combo.setCurrentIndex(max(0, combo.findData(value)))
        combo.blockSignals(False)

    def _append(self, row: dict) -> None:
        r = self.table.rowCount()
        self.table.insertRow(r)
        for c, (key, kind) in enumerate(self._columns):
            value = row.get(key)
            if kind in ("text", "number"):
                self.table.setItem(r, c, QTableWidgetItem("" if value is None else str(value)))
            else:
                combo = QComboBox()
                self._fill_combo(combo, kind, value)
                combo.currentIndexChanged.connect(self._combo_changed)
                self.table.setCellWidget(r, c, combo)

    def _item_changed(self, _item) -> None:
        if not self._loading:
            self.edited.emit()

    def _combo_changed(self, _index) -> None:
        if not self._loading:
            self.edited.emit()

    def add_row(self) -> None:
        n = self.table.rowCount() + 1
        existing = {row["id"] for row in self.rows()}
        while f"{self._prefix}{n}" in existing:
            n += 1
        rid = f"{self._prefix}{n}"
        first = (self._options("points") or [("", "")])[0][0]
        defaults = {"points": {"x": 0, "y": 0}, "members": {"start_point": first, "end_point": first},
                    "materials": {"A": 0.001, "E": 200, "density": 7850},
                    "loads": {"point": first, "Fx": 0, "Fy": 0},
                    "supports": {"point": first, "type": SUPPORTS.keys()[0]}}[self.name]
        if self.name == "members":
            mats = self._options("materials")
            defaults["material"] = mats[0][0] if mats else ""
        self._loading = True
        self._append({"id": rid, "name": rid, **defaults})
        self._loading = False
        self.edited.emit()

    def delete_selected(self) -> None:
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        if not rows and self.table.currentRow() >= 0:
            rows = [self.table.currentRow()]
        for r in rows:
            self.table.removeRow(r)
        if rows:
            self.edited.emit()
