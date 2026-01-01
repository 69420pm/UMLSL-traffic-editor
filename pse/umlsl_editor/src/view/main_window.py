from PySide6.QtWidgets import QMainWindow, QGraphicsView
from pse.umlsl_editor.src.view.canvas.traffic_scene import TrafficScene

class MainWindow(QMainWindow):
    """
    The main application window.
    """
    def __init__(self):
        super().__init__()
        self.scene = TrafficScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

    def get_scene(self) -> TrafficScene:
        """
        Returns the TrafficScene instance used by the main window.
        """
        return self.scene
