from PySide6.QtWidgets import (QPushButton, QLabel, QWidget, QVBoxLayout, 
                               QHBoxLayout, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, Signal
from config import COLORS


class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_animation()
        self.setCursor(Qt.PointingHandCursor)

    def _setup_animation(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def mousePressEvent(self, event):
        if self.isEnabled():
            self._start_zoom(True)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.isEnabled():
            self._start_zoom(False)
        super().mouseReleaseEvent(event)

    def _start_zoom(self, pressed):
        geom = self.geometry()
        if pressed:
            new_geom = geom.adjusted(2, 2, -2, -2)
        else:
            new_geom = geom.adjusted(-2, -2, 2, 2)
        self.animation.stop()
        self.animation.setStartValue(geom)
        self.animation.setEndValue(new_geom)
        self.animation.start()


class BreathingLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._opacity = 1.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._breathe)
        self._breathing_up = False

    def start_breathing(self):
        self._timer.start(80)

    def stop_breathing(self):
        self._timer.stop()
        self._opacity = 1.0
        self.update()

    def _breathe(self):
        if self._breathing_up:
            self._opacity += 0.02
            if self._opacity >= 1.0:
                self._breathing_up = False
        else:
            self._opacity -= 0.02
            if self._opacity <= 0.5:
                self._breathing_up = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self._opacity)
        super().paintEvent(event)


class RobotFaceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.emotion = "happy"
        self.setMinimumSize(200, 200)
        self.bounce_offset = 0
        self.blink = False
        
        self.bounce_timer = QTimer(self)
        self.bounce_timer.timeout.connect(self._bounce_tick)
        self.bounce_timer.start(50)
        
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self._blink_tick)
        self.blink_timer.start(3000)

    def set_emotion(self, emotion):
        self.emotion = emotion
        self.update()

    def _bounce_tick(self):
        import math
        import time
        self.bounce_offset = math.sin(time.time() * 3) * 3
        self.update()

    def _blink_tick(self):
        self.blink = True
        self.update()
        QTimer.singleShot(150, self._unblink)

    def _unblink(self):
        self.blink = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        center_x, center_y = w // 2, h // 2 + self.bounce_offset
        
        face_color = QColor(COLORS["primary"])
        eye_color = QColor(COLORS["text"])
        cheek_color = QColor(COLORS["accent"])
        
        painter.setBrush(QBrush(face_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - 80, center_y - 80, 160, 160)
        
        left_eye_x = center_x - 35
        right_eye_x = center_x + 35
        eye_y = center_y - 15
        
        if self.blink:
            painter.setBrush(QBrush(eye_color))
            painter.drawRoundedRect(left_eye_x - 15, eye_y, 30, 4, 2, 2)
            painter.drawRoundedRect(right_eye_x - 15, eye_y, 30, 4, 2, 2)
        else:
            painter.setBrush(QBrush(eye_color))
            if self.emotion == "happy":
                painter.drawChord(left_eye_x - 18, eye_y - 18, 36, 36, 0, 180 * 16)
                painter.drawChord(right_eye_x - 18, eye_y - 18, 36, 36, 0, 180 * 16)
            elif self.emotion == "sleepy":
                painter.drawChord(left_eye_x - 18, eye_y, 36, 36, 180 * 16, 180 * 16)
                painter.drawChord(right_eye_x - 18, eye_y, 36, 36, 180 * 16, 180 * 16)
            elif self.emotion == "thinking":
                painter.drawEllipse(left_eye_x - 8, eye_y - 8, 16, 16)
                painter.drawEllipse(right_eye_x - 8, eye_y - 8, 16, 16)
                painter.setBrush(QBrush(QColor("white")))
                painter.drawEllipse(left_eye_x - 3, eye_y - 5, 5, 5)
                painter.drawEllipse(right_eye_x - 3, eye_y - 5, 5, 5)
            elif self.emotion == "curious":
                painter.drawEllipse(left_eye_x - 10, eye_y - 10, 20, 20)
                painter.drawEllipse(right_eye_x - 6, eye_y - 6, 12, 12)
                painter.setBrush(QBrush(QColor("white")))
                painter.drawEllipse(left_eye_x - 4, eye_y - 4, 4, 4)
            else:
                painter.drawEllipse(left_eye_x - 10, eye_y - 10, 20, 20)
                painter.drawEllipse(right_eye_x - 10, eye_y - 10, 20, 20)
                painter.setBrush(QBrush(QColor("white")))
                painter.drawEllipse(left_eye_x - 4, eye_y - 4, 4, 4)
                painter.drawEllipse(right_eye_x - 4, eye_y - 4, 4, 4)
        
        painter.setBrush(QBrush(cheek_color))
        painter.setOpacity(0.3)
        painter.drawEllipse(left_eye_x - 25, eye_y + 20, 20, 10)
        painter.drawEllipse(right_eye_x + 5, eye_y + 20, 20, 10)
        painter.setOpacity(1.0)
        
        painter.setBrush(QBrush(eye_color))
        painter.setPen(Qt.NoPen)
        mouth_y = center_y + 30
        
        if self.emotion == "happy" or self.emotion == "excited":
            painter.drawChord(center_x - 20, mouth_y - 10, 40, 30, 0, -180 * 16)
        elif self.emotion == "sleepy":
            painter.drawRoundedRect(center_x - 10, mouth_y, 20, 6, 3, 3)
        elif self.emotion == "thinking":
            painter.drawRoundedRect(center_x - 15, mouth_y + 2, 30, 4, 2, 2)
        elif self.emotion == "curious":
            painter.drawEllipse(center_x - 5, mouth_y, 10, 12)
        else:
            painter.drawRoundedRect(center_x - 15, mouth_y, 30, 4, 2, 2)


class CardWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 16px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 10))
        self.setGraphicsEffect(shadow)


class SwitchButton(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(52, 28)
        self._checked = False
        self.setCursor(Qt.PointingHandCursor)

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        self._checked = checked
        self.update()

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self.toggled.emit(self._checked)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self._checked:
            bg_color = QColor(COLORS["primary"])
            circle_x = self.width() - 24
        else:
            bg_color = QColor(COLORS["border"])
            circle_x = 4
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        
        painter.setBrush(QBrush(QColor("white")))
        painter.drawEllipse(circle_x, 4, 20, 20)


class PageTransitionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_widget = None
        self._next_widget = None
        self._animation = QPropertyAnimation(self, b"windowOpacity")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def set_widget(self, widget):
        if self._current_widget:
            self._current_widget.deleteLater()
        self._current_widget = widget
        self._layout.addWidget(widget)
        widget.show()

    def transition_to(self, widget):
        self._next_widget = widget
        self._next_widget.setParent(self)
        self._next_widget.setGeometry(self.rect())
        self._next_widget.hide()
        
        self._animation.finished.connect(self._on_fade_out_done)
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.start()

    def _on_fade_out_done(self):
        self._animation.finished.disconnect(self._on_fade_out_done)
        if self._current_widget:
            self._current_widget.hide()
        
        self._next_widget.show()
        self._current_widget = self._next_widget
        self._next_widget = None
        
        self._animation.finished.connect(self._on_fade_in_done)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.start()

    def _on_fade_in_done(self):
        self._animation.finished.disconnect(self._on_fade_in_done)

    def resizeEvent(self, event):
        if self._current_widget:
            self._current_widget.setGeometry(self.rect())
        if self._next_widget:
            self._next_widget.setGeometry(self.rect())
        super().resizeEvent(event)
