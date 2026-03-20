from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QWidget


class GreenSnackbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Draw directly on the widget instead of using a QFrame container.
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

        # Single opacity effect to avoid stacked QGraphicsEffects.
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
        Custom paint to keep the pill and shadow consistent with opacity animation.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Leave space for the shadow.
        rect = self.rect().adjusted(2, 2, -2, -2)

        # Draw the pill background.
        painter.setBrush(QColor("#799582"))  # Sage Green
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 18, 18)

    def show_message(self, message: str = "", duration: int | None = 3000):
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

        if duration is None or duration <= 0:
            self.timer.stop()
        else:
            self.timer.start(duration)

    def hide_message(self):
        self.fade_out()

    def fade_out(self):
        self.anim.setDuration(500)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.start()
