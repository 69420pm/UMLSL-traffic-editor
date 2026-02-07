from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect)


class GreenSnackbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. SETUP
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 2. INTERNAL LAYOUT
        # We don't use a QFrame container anymore; we draw directly on 'self'.
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 0, 16, 0)  # Bottom margin increased for shadow space
        self.layout.setSpacing(20)
        self.setMinimumWidth(150)
        self.setMinimumHeight(36)

        # Icon
        # self.icon_label = QLabel("✔")
        # self.icon_label.setStyleSheet("color: #011C27; font-size: 20px; font-weight: bold; background: transparent;")
        # self.layout.addWidget(self.icon_label)

        # Text
        self.text_label = QLabel("")
        self.text_label.setStyleSheet("color: #011C27; font-size: 13px; background: transparent;")
        self.layout.addWidget(self.text_label)

        # 3. OPACITY EFFECT (Only ONE effect used now)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Animation
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.finished.connect(self.hide)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)

        self.hide()

    def paintEvent(self, event):
        """
        Manually draw the pill shape and shadow to avoid QGraphicsEffect conflicts.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # The drawing area (leave space for shadow)
        rect = self.rect().adjusted(2, 2, -2, -2)

        # 2. DRAW GREEN PILL
        painter.setBrush(QColor("#799582"))  # Sage Green
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 18, 18)

    def show_message(self, message="", duration=3000):
        self.text_label.setText(message)
        self.adjustSize()

        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            y = parent_rect.height() - self.height() - 8
            self.move(x, y)

        self.anim.stop()
        self.opacity_effect.setOpacity(1.0)
        self.raise_()
        self.show()
        self.timer.start(duration)

    def fade_out(self):
        self.anim.setDuration(500)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.start()
