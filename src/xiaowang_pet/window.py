from __future__ import annotations

import random
import time

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QPainter, QPen, QPixmap, QTransform
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QWidget

from .animations import SequencePlayer
from .assets import find_asset
from .config import AppConfig, load_config
from .emotes import choose_emote, emote_text
from .state_machine import PetStateMachine, Transition
from .states import PetState


def now_ms() -> int:
    return int(time.monotonic() * 1000)


class QtAssetStore:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._cache: dict[tuple[str, bool], QPixmap] = {}

    def pixmap(self, frame_name: str, mirrored: bool = False) -> QPixmap:
        key = (frame_name, mirrored)
        if key in self._cache:
            return self._cache[key]

        path = find_asset(self.config.asset_dir, frame_name)
        if path is None:
            pixmap = self._placeholder(frame_name)
        else:
            pixmap = QPixmap(str(path))
            if pixmap.isNull():
                pixmap = self._placeholder(frame_name)

        pixmap = pixmap.scaled(
            self.config.pet_size,
            self.config.pet_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        if mirrored:
            pixmap = pixmap.transformed(QTransform().scale(-1, 1))

        self._cache[key] = pixmap
        return pixmap

    def _placeholder(self, frame_name: str) -> QPixmap:
        size = self.config.pet_size
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#2F6FAE"), 4))
        painter.setBrush(QColor("#EAF6FF"))
        painter.drawEllipse(34, 36, size - 68, size - 72)
        painter.drawEllipse(48, 18, 30, 36)
        painter.drawEllipse(size - 78, 18, 30, 36)

        painter.setPen(QPen(QColor("#1C2B39"), 5))
        eye_y = int(size * 0.45)
        painter.drawPoint(int(size * 0.43), eye_y)
        painter.drawPoint(int(size * 0.57), eye_y)
        painter.setPen(QPen(QColor("#1C2B39"), 2))
        painter.drawArc(int(size * 0.45), eye_y + 12, 24, 16, 200 * 16, 140 * 16)

        painter.setFont(QFont("Consolas", 10))
        painter.setPen(QColor("#2F6FAE"))
        painter.drawText(
            pixmap.rect().adjusted(12, size - 42, -12, -12),
            Qt.AlignmentFlag.AlignCenter,
            frame_name,
        )
        painter.end()
        return pixmap


class PetWindow(QWidget):
    def __init__(self, config: AppConfig | None = None) -> None:
        super().__init__()
        self.config = config or load_config()
        self.brain = PetStateMachine(self.config)
        self.player = SequencePlayer()
        self.assets = QtAssetStore(self.config)
        self.rng = random.Random()

        self._direction = 1
        self._press_global: QPoint | None = None
        self._drag_offset = QPoint()
        self._dragging = False

        self._init_window()
        self._init_timers()
        self._place_initial()
        self._render_next_frame()

    def _init_window(self) -> None:
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowTitle("Xiaowang")

        self.bubble_height = 48
        self.setFixedSize(self.config.pet_size, self.config.pet_size + self.bubble_height)

        self.pet_label = QLabel(self)
        self.pet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_label.setGeometry(0, self.bubble_height, self.config.pet_size, self.config.pet_size)

        self.emote_label = QLabel(self)
        self.emote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emote_label.setGeometry(self.config.pet_size // 2 - 34, 4, 68, 40)
        self.emote_label.setStyleSheet(
            "background: rgba(255, 255, 255, 225);"
            "border: 1px solid rgba(47, 111, 174, 180);"
            "border-radius: 14px;"
            "font-size: 22px;"
        )
        self.emote_label.hide()

    def _init_timers(self) -> None:
        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self._on_frame)
        self.frame_timer.start(self.config.timing.frame_ms)

        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self._on_behavior_check)
        self.behavior_timer.start(self.config.timing.behavior_check_ms)

        self.single_click_timer = QTimer(self)
        self.single_click_timer.setSingleShot(True)
        self.single_click_timer.timeout.connect(self._on_single_click_confirmed)

        self.emote_timer = QTimer(self)
        self.emote_timer.setSingleShot(True)
        self.emote_timer.timeout.connect(self.emote_label.hide)

    def _place_initial(self) -> None:
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry() if screen else self.frameGeometry()
        margin = 36
        if self.config.initial_anchor == "center":
            x = rect.center().x() - self.width() // 2
            y = rect.center().y() - self.height() // 2
        else:
            x = rect.right() - self.width() - margin
            y = rect.bottom() - self.height() - margin
        self.move(x, y)

    def _on_frame(self) -> None:
        transition = self.brain.tick(now_ms())
        if transition:
            self._apply_transition(transition)

        if self.brain.state == PetState.WALK:
            self._move_walk_step()

        self._render_next_frame()

    def _on_behavior_check(self) -> None:
        transition = self.brain.maybe_start_walk(now_ms(), self.rng)
        if transition:
            self._direction = self.rng.choice((-1, 1))
            self._apply_transition(transition)

    def _on_single_click_confirmed(self) -> None:
        self.brain.handle_single_click(now_ms())
        name = choose_emote(self.brain.state, self.config, self.rng)
        self.emote_label.setText(emote_text(name))
        self.emote_label.show()
        self.emote_timer.start(self.config.timing.emote_ms)

    def _apply_transition(self, transition: Transition) -> None:
        self.player.play_transition(transition.from_state, transition.to_state)
        self._render_next_frame()

    def _render_next_frame(self) -> None:
        mirrored = self.brain.state == PetState.WALK and self._direction < 0
        frame_name = self.player.next_frame()
        self.pet_label.setPixmap(self.assets.pixmap(frame_name, mirrored=mirrored))

    def _move_walk_step(self) -> None:
        screen = self.screen() or QApplication.primaryScreen()
        rect = screen.availableGeometry() if screen else self.frameGeometry()
        next_x = self.x() + self._direction * self.config.movement.walk_speed_px

        if next_x <= rect.left():
            next_x = rect.left()
            self._direction = 1
        elif next_x + self.width() >= rect.right():
            next_x = rect.right() - self.width()
            self._direction = -1

        self.move(next_x, self.y())

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.RightButton:
            self._show_menu(event.globalPosition().toPoint())
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self._press_global = event.globalPosition().toPoint()
            self._drag_offset = self._press_global - self.frameGeometry().topLeft()
            self._dragging = False
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self._press_global is None:
            super().mouseMoveEvent(event)
            return

        global_pos = event.globalPosition().toPoint()
        moved = (global_pos - self._press_global).manhattanLength()
        if moved < 4 and not self._dragging:
            return

        if not self._dragging:
            self.single_click_timer.stop()
            transition = self.brain.begin_drag(now_ms())
            if transition:
                self._apply_transition(transition)
            self._dragging = True

        self.move(global_pos - self._drag_offset)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return

        if self._dragging:
            transition = self.brain.end_drag(now_ms())
            if transition:
                self._apply_transition(transition)
        else:
            self.single_click_timer.start(self.config.timing.click_window_ms)

        self._press_global = None
        self._dragging = False
        event.accept()

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.single_click_timer.stop()
            transition = self.brain.handle_double_click(now_ms(), self.rng)
            if transition:
                self._apply_transition(transition)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if self.config.temp_quit_key.lower() == "esc" and event.key() == Qt.Key.Key_Escape:
            QApplication.quit()
            event.accept()
            return
        super().keyPressEvent(event)

    def _show_menu(self, global_pos: QPoint) -> None:
        menu = QMenu(self)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        menu.exec(global_pos)


def run_app() -> int:
    app = QApplication([])
    window = PetWindow(load_config())
    window.show()
    return app.exec()
