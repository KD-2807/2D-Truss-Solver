"""Main window of the desktop app: input tables | drawing | results."""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QComboBox, QFileDialog, QFrame, QHBoxLayout, QHeaderView, QLabel,
                               QMainWindow, QMessageBox, QPushButton, QScrollArea, QSplitter,
                               QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget)

from ..core.domain import SUPPORTS
from ..core.templates import TEMPLATES
from ..presentation.i18n import LANGUAGES
from .canvas import SceneCanvas
from .controller import AppController
from .editors import TABLE_SPECS, TableEditor

STATUS_STYLE = {
    "solved": "background:#e6f6ec;color:#0f6b36;",
    "indeterminate": "background:#fff4dc;color:#8a5a00;",
}
STATUS_BAD = "background:#fde8e6;color:#a3241a;"


class MainWindow(QMainWindow):
    def __init__(self, controller: AppController | None = None):
        super().__init__()
        self.controller = controller or AppController()
        self.resize(1480, 860)
        self._build_ui()
        self._debounce = QTimer(self, singleShot=True, interval=300)
        self._debounce.timeout.connect(self._apply_edits)
        self.controller.changed.connect(self._render)
        QShortcut(QKeySequence(Qt.Key_Escape), self, activated=self._escape)
        self.controller.load_template("warren_example")
        self._fill_editors()
        self.retranslate()

    # ---- construction ---------------------------------------------------------------
    def _build_ui(self) -> None:
        t = self.controller
        root = QWidget()
        outer = QVBoxLayout(root)

        bar = QHBoxLayout()
        self.title = QLabel()
        self.title.setStyleSheet("font-weight:700;font-size:15px;")
        self.language = QComboBox()
        for code, name in LANGUAGES.items():
            self.language.addItem(name, code)
        self.language.currentIndexChanged.connect(self._language_changed)
        self.template = QComboBox()
        self.template.activated.connect(self._load_template)
        self.load_button, self.open_button, self.save_button = QPushButton(), QPushButton(), QPushButton()
        self.load_button.clicked.connect(self._load_template)
        self.open_button.clicked.connect(self._open_file)
        self.save_button.clicked.connect(self._save_file)
        bar.addWidget(self.title, 1)
        for w in (self.language, self.template, self.load_button, self.open_button, self.save_button):
            bar.addWidget(w)
        outer.addLayout(bar)

        split = QSplitter(Qt.Horizontal)
        outer.addWidget(split, 1)

        # left: input tables
        self.tabs = QTabWidget()
        self.editors = {}
        for name in TABLE_SPECS:
            editor = TableEditor(name, self._options, lambda key: self.controller.t(key))
            editor.edited.connect(self._edited)
            self.editors[name] = editor
            self.tabs.addTab(editor, "")
        split.addWidget(self.tabs)

        # centre: drawing
        centre = QWidget()
        cl = QVBoxLayout(centre)
        head = QHBoxLayout()
        self.back_button = QPushButton()
        self.back_button.setStyleSheet("background:#1d4ed8;color:white;padding:6px 12px;border-radius:6px;")
        self.back_button.clicked.connect(self.controller.back)
        self.stage_title = QLabel()
        self.stage_title.setStyleSheet("font-weight:700;")
        self.stage_hint = QLabel()
        self.stage_hint.setStyleSheet("color:#667085;")
        self.legend = QLabel()
        self.legend.setTextFormat(Qt.RichText)
        head.addWidget(self.back_button)
        head.addWidget(self.stage_title)
        head.addWidget(self.stage_hint, 1)
        head.addWidget(self.legend)
        cl.addLayout(head)
        self.canvas = SceneCanvas()
        self.canvas.selected.connect(self.controller.select)
        cl.addWidget(self.canvas, 1)
        split.addWidget(centre)

        # right: results
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.issues = QLabel()
        self.issues.setWordWrap(True)
        self.issues.setStyleSheet("color:#a3241a;")
        self.tables_box = QVBoxLayout()
        holder = QWidget()
        hl = QVBoxLayout(holder)
        hl.addWidget(self.status)
        hl.addWidget(self.issues)
        hl.addLayout(self.tables_box)
        hl.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(holder)
        scroll.setFrameShape(QFrame.NoFrame)
        split.addWidget(scroll)
        split.setSizes([330, 650, 560])
        self.setCentralWidget(root)

    def _options(self, kind: str) -> list:
        if kind == "points":
            return [(p["id"], p["id"]) for p in self.editors["points"].rows() if p["id"]] \
                if "points" in self.editors else []
        if kind == "materials":
            return [(m["id"], m["id"]) for m in self.editors["materials"].rows() if m["id"]] \
                if "materials" in self.editors else []
        return [(k, self.controller.t(f"support.{k}")) for k in SUPPORTS.keys()]

    # ---- texts ----------------------------------------------------------------------
    def retranslate(self) -> None:
        t = self.controller.t
        self.setWindowTitle(t("app.title"))
        self.title.setText(f"{t('app.title')}   —   {t('app.caption')}")
        self.load_button.setText(t("ui.load_template"))
        self.open_button.setText(t("ui.open"))
        self.save_button.setText(t("ui.save"))
        self.back_button.setText(t("ui.back"))
        current = self.template.currentData()
        self.template.blockSignals(True)
        self.template.clear()
        for key in TEMPLATES:
            self.template.addItem(t(f"template.{key}"), key)
        self.template.setCurrentIndex(max(0, self.template.findData(current)))
        self.template.blockSignals(False)
        for i, name in enumerate(TABLE_SPECS):
            self.tabs.setTabText(i, t(f"tab.{name}"))
            self.editors[name].retranslate()
            self.editors[name].refresh_choices()
        self.legend.setText(
            "  ".join(f'<span style="color:{c}">■</span> {t("ui.legend_" + s)}'
                      for s, c in (("tension", "#d1431b"), ("compression", "#1d5fd1"), ("zero", "#8a93a3"))))

    # ---- model edits -----------------------------------------------------------------
    def _fill_editors(self) -> None:
        data = self.controller.to_dict()
        for name in ("points", "materials", "members", "loads", "supports"):
            self.editors[name].set_rows(data[name])
        for editor in self.editors.values():
            editor.refresh_choices()

    def _edited(self) -> None:
        for editor in self.editors.values():
            editor.refresh_choices()
        self._debounce.start()

    def _apply_edits(self) -> None:
        self.controller.load_dict({name: editor.rows() for name, editor in self.editors.items()})

    def _load_template(self) -> None:
        self.controller.load_template(self.template.currentData())
        self._fill_editors()

    def _language_changed(self) -> None:
        self.controller.set_language(self.language.currentData())
        self.retranslate()

    def _escape(self) -> None:
        if self.controller.view and self.controller.view.mode != "overview":
            self.controller.back()

    # ---- files -----------------------------------------------------------------------
    def _open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self.controller.t("ui.open"), "", "JSON (*.json)")
        if path:
            try:
                self.controller.load_dict(json.loads(Path(path).read_text("utf-8")))
            except (OSError, ValueError) as exc:
                QMessageBox.warning(self, self.controller.t("ui.error"), str(exc))
                return
            self._fill_editors()

    def _save_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, self.controller.t("ui.save"), "truss.json", "JSON (*.json)")
        if path:
            Path(path).write_text(json.dumps(self.controller.to_dict(), indent=2, ensure_ascii=False), "utf-8")

    # ---- rendering ---------------------------------------------------------------------
    def _render(self) -> None:
        v, t = self.controller.view, self.controller.t
        self.canvas.show_scene(v.scene)
        self.stage_title.setText(v.scene.title)
        name = v.scene.title.split(" ", 1)[-1]
        self.stage_hint.setText(t("ui.hint_overview") if v.mode == "overview"
                                else t("ui.hint_joint" if v.mode == "joint" else "ui.hint_member",
                                       name=name))
        self.back_button.setVisible(v.mode != "overview")
        self.legend.setVisible(v.solved)
        self.status.setText(v.status_text)
        self.status.setStyleSheet("padding:8px;border-radius:6px;font-weight:600;"
                                  + STATUS_STYLE.get(v.status, STATUS_BAD))
        self.issues.setText("\n".join(f"• {i}" for i in v.issues))
        self._render_tables(v.tables)

    def _render_tables(self, tables: list) -> None:
        while self.tables_box.count():
            item = self.tables_box.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()  # deleteLater alone leaves it painted until the next event loop turn
                widget.setParent(None)
                widget.deleteLater()
        for table in tables:
            heading = QLabel(f"<b>{table.title}</b>")
            self.tables_box.addWidget(heading)
            widget = QTableWidget(len(table.rows), len(table.columns))
            widget.setEditTriggers(QTableWidget.NoEditTriggers)
            if any(table.columns):
                widget.setHorizontalHeaderLabels(table.columns)
            else:
                widget.horizontalHeader().setVisible(False)
            widget.verticalHeader().setVisible(False)
            widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # the page scrolls, not the table
            for r, row in enumerate(table.rows):
                for c, cell in enumerate(row):
                    widget.setItem(r, c, QTableWidgetItem(str(cell)))
            widget.resizeColumnsToContents()
            widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            widget.setFixedHeight(widget.horizontalHeader().height() * (1 if any(table.columns) else 0)
                                  + sum(widget.rowHeight(r) for r in range(widget.rowCount())) + 24)
            self.tables_box.addWidget(widget)
            if table.note:
                note = QLabel(table.note)
                note.setWordWrap(True)
                note.setStyleSheet("font-weight:600;color:" + ("#0f6b36" if table.note_ok else "#a3241a"))
                self.tables_box.addWidget(note)
