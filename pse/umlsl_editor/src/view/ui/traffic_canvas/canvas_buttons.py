from PySide6.QtCore import QObject, QEvent
from PySide6.QtWidgets import QFrame, QToolButton, QScrollArea, QMainWindow

from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_view import TrafficView
from pse.umlsl_editor.src.view.view_constants import DIMENSION
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_main import Ui_MainWindow


# Ideally, import the generated UI class for type hinting (optional but recommended)
class CanvasButtons(QObject):
    """
    Controller for canvas-specific buttons.
    Manages logic for the overlay buttons defined in MainWindow.ui.
    """



    PADDING = 16

    def __init__(self, main_window: Ui_MainWindow):
        """
        Args:
            main_window: The MainWindow instance (which inherits Ui_MainWindow).
        """
        super().__init__()
        self.window = main_window

        # 1. Access Widgets Directly (No more findChild!)
        # Since main_window inherits the UI class, attributes are available directly.
        self.view: TrafficView = self.window.trafficView
        self.zoom_buttons: QFrame = self.window.zoom_buttons
        self.b_sidebar_toggle: QToolButton = self.window.b_sidebar_toggle
        self.sidebar: QScrollArea = self.window.sidebar
        self.b_plus: QToolButton = self.window.b_plus
        self.b_minus: QToolButton = self.window.b_minus

        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up UI connections and overlay logic."""
        self._reparent_widgets()
        self._connect_signals()

        # Install event filter to update positions on resize
        self.view.installEventFilter(self)
        self._update_position()

    def _reparent_widgets(self) -> None:
        """Reparent overlay widgets to the TrafficView so they float on top."""
        self.zoom_buttons.setParent(self.view)
        self.zoom_buttons.show()

        self.b_sidebar_toggle.setParent(self.view)
        self.b_sidebar_toggle.show()

    def _connect_signals(self) -> None:
        """Connect button click signals."""
        self.b_plus.clicked.connect(
            lambda: self.view.button_zoom(DIMENSION.BUTTON_ZOOM_AMOUNT)
        )
        self.b_minus.clicked.connect(
            lambda: self.view.button_zoom(1 / DIMENSION.BUTTON_ZOOM_AMOUNT)
        )
        self.b_sidebar_toggle.clicked.connect(self.toggle_sidebar)

    def toggle_sidebar(self) -> None:
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def _update_position(self) -> None:
        # (Same implementation as your original code)
        zoom_x = self.view.width() - self.zoom_buttons.width() - self.PADDING
        self.zoom_buttons.move(zoom_x, self.PADDING)
        self.b_sidebar_toggle.move(0, self.PADDING)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        # (Same implementation as your original code)
        if source == self.view and event.type() == QEvent.Type.Resize:
            self._update_position()
        return super().eventFilter(source, event)