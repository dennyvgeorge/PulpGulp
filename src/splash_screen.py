import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap


def resource_path(filename):
    import sys
    if getattr(sys, '_MEIPASS', None):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets", filename)


class SplashScreen(QWidget):
    def __init__(self, on_finished):
        super().__init__()
        self.on_finished = on_finished
        self.setStyleSheet("background-color: #151419;")
        self.setup_ui()

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

        QTimer.singleShot(2500, self.fade_out)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.splash_image = QLabel()
        self.splash_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.splash_image.setStyleSheet("background: transparent;")

        splash_path = resource_path("splash.png")
        if os.path.isfile(splash_path):
            pixmap = QPixmap(splash_path)
            self.splash_image.setPixmap(pixmap.scaled(
                750, 960,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))

        layout.addWidget(self.splash_image)

    def fade_out(self):
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.finished.connect(self.on_finished)
        self.animation.start()

