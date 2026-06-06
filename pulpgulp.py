import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from src.splash_screen import SplashScreen
from src.main_window import MainWindow


class PulpGulpApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")

        self.main_window = MainWindow()

        self.splash_window = QMainWindow()
        self.splash_window.setWindowTitle("PulpGulp")
        self.splash_window.setMinimumSize(750, 960)
        self.splash_window.resize(750, 960)
        self.splash_window.setStyleSheet("background-color: #151419;")

        self.splash = SplashScreen(on_finished=self.show_main)
        self.splash_window.setCentralWidget(self.splash)
        self.splash_window.show()

    def show_main(self):
        self.splash_window.close()
        self.main_window.show()

    def run(self):
        return self.app.exec()


def main():
    pulpgulp = PulpGulpApp()
    sys.exit(pulpgulp.run())


if __name__ == "__main__":
    main()
