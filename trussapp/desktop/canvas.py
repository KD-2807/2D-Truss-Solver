"""SceneCanvas: draws a Scene with Qt (same scene description as the web page)."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import (QBrush, QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen,
                           QPolygonF)
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsScene, QGraphicsView

THEME = {
    "grid": "#e6e9ef", "axis": "#b9c0cd", "member": "#3b4252", "member_tension": "#d1431b",
    "member_compression": "#1d5fd1", "member_zero": "#8a93a3", "force_tension": "#d1431b",
    "force_compression": "#1d5fd1", "force_zero": "#8a93a3", "force_load": "#b4208a",
    "force_reaction": "#148a4a", "support": "#a26a00", "node": "#111827",
    "label": "#1c2230", "label_node": "#1c2230", "label_member": "#667085", "tick": "#8a93a3",
    "label_tension": "#d1431b", "label_compression": "#1d5fd1", "label_zero": "#8a93a3",
    "label_load": "#b4208a", "label_reaction": "#148a4a",
}
BACKGROUND = "#ffffff"


def color(role: str) -> QColor:
    return QColor(THEME.get(role, "#222222"))


class SceneCanvas(QGraphicsView):
    """Renders scene primitives; emits `selected(kind, id)` when a clickable item is clicked."""

    selected = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene_model = None
        self._qscene = QGraphicsScene(self)
        self.setScene(self._qscene)
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        self.setBackgroundBrush(QBrush(QColor(BACKGROUND)))
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # ---- public ------------------------------------------------------------------
    def show_scene(self, scene) -> None:
        self._scene_model = scene
        self.redraw()

    def redraw(self) -> None:
        self._qscene.clear()
        scene = self._scene_model
        W, H = max(self.viewport().width(), 200), max(self.viewport().height(), 200)
        self._qscene.setSceneRect(0, 0, W, H)
        if scene is None:
            return
        xmin, ymin, xmax, ymax = scene.bounds
        overview = scene.mode == "overview"
        pad_x, pad_y = (95, 70) if overview else (150, 80)
        scale = max(1e-9, min((W - 2 * pad_x) / (xmax - xmin), (H - 2 * pad_y) / (ymax - ymin)))
        ox, oy = (W - (xmax - xmin) * scale) / 2, (H - (ymax - ymin) * scale) / 2
        sx = lambda x: ox + (x - xmin) * scale  # noqa: E731
        sy = lambda y: H - (oy + (y - ymin) * scale)  # noqa: E731
        for item in scene.items:
            getattr(self, f"_draw_{item.type}")(item, sx, sy)

    # ---- events --------------------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.redraw()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            for item in self.items(event.position().toPoint()):
                ref = item.data(0)
                if ref:
                    self.selected.emit(ref[0], ref[1])
                    break
        super().mousePressEvent(event)

    # ---- primitives ----------------------------------------------------------------
    def _pen(self, role: str, width: float, dash: bool = False) -> QPen:
        pen = QPen(color(role), width)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        if dash:
            pen.setStyle(Qt.DashLine)
        return pen

    def _draw_line(self, l, sx, sy) -> None:
        a, b = QPointF(sx(l.x1), sy(l.y1)), QPointF(sx(l.x2), sy(l.y2))
        line = self._qscene.addLine(a.x(), a.y(), b.x(), b.y(), self._pen(l.role, l.width, l.dash))
        line.setZValue(1)
        if l.ref:  # wide invisible line: easy to click on a thin member
            hit = QGraphicsLineItem(a.x(), a.y(), b.x(), b.y())
            hit.setPen(QPen(QColor(0, 0, 0, 0), l.width + 14))
            hit.setData(0, (l.ref.kind, l.ref.id))
            hit.setCursor(Qt.PointingHandCursor)
            hit.setZValue(1.5)
            self._qscene.addItem(hit)

    def _draw_polygon(self, p, sx, sy) -> None:
        poly = QPolygonF([QPointF(sx(x), sy(y)) for x, y in p.points])
        brush = QBrush(color(p.role)) if p.fill else QBrush(QColor(BACKGROUND))
        self._qscene.addPolygon(poly, self._pen(p.role, p.width), brush).setZValue(1)

    def _draw_arrow(self, a, sx, sy) -> None:
        x1, y1, x2, y2 = sx(a.x1), sy(a.y1), sx(a.x2), sy(a.y2)
        length = math.hypot(x2 - x1, y2 - y1) or 1.0
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        head = min(13.0, length * 0.5)
        half = head * 0.42
        bx, by = x2 - ux * head, y2 - uy * head
        self._qscene.addLine(x1, y1, bx, by, self._pen(a.role, a.width)).setZValue(3)
        tip = QPolygonF([QPointF(x2, y2), QPointF(bx - uy * half, by + ux * half),
                         QPointF(bx + uy * half, by - ux * half)])
        self._qscene.addPolygon(tip, QPen(Qt.NoPen), QBrush(color(a.role))).setZValue(3)

    def _draw_dot(self, d, sx, sy) -> None:
        item = QGraphicsEllipseItem(sx(d.x) - d.radius, sy(d.y) - d.radius, 2 * d.radius, 2 * d.radius)
        item.setBrush(QBrush(color(d.role)))
        item.setPen(QPen(Qt.NoPen))
        item.setZValue(4)
        if d.ref:
            item.setData(0, (d.ref.kind, d.ref.id))
            item.setCursor(Qt.PointingHandCursor)
        self._qscene.addItem(item)

    def _draw_label(self, l, sx, sy) -> None:
        font = QFont(self.font())
        font.setPixelSize(l.size)
        font.setBold(l.bold)
        metrics = QFontMetrics(font)
        width = metrics.horizontalAdvance(l.text)
        x = sx(l.x) + l.dx - {"start": 0, "middle": width / 2, "end": width}[l.anchor]
        top = sy(l.y) + l.dy - metrics.ascent()  # dy is relative to the text baseline
        path = QPainterPath()
        path.addText(x, top + metrics.ascent(), font, l.text)
        halo = self._qscene.addPath(path, QPen(QColor(BACKGROUND), 4), QBrush(QColor(BACKGROUND)))
        text = self._qscene.addPath(path, QPen(Qt.NoPen), QBrush(color(l.role)))
        halo.setZValue(5)
        text.setZValue(6)
