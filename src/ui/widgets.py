from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QPushButton


class AnimatedButton(QPushButton):

    def __init__(self, text, parent=None, shadow_color="#FF4D6D"):
        super().__init__(text, parent)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(shadow_color))
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)

    def enterEvent(self, event):
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(200)
        self.anim.setStartValue(15)
        self.anim.setEndValue(30)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(200)
        self.anim.setStartValue(30)
        self.anim.setEndValue(15)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
        super().leaveEvent(event)
