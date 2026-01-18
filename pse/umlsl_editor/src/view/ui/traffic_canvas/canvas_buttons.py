from PySide6.QtCore import QObject, QEvent
from PySide6.QtWidgets import QFrame, QToolButton, QScrollArea

from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_view import TrafficView
from pse.umlsl_editor.src.view.view_constants import DIMENSION


class CanvasButtons(QObject):
    """
    Controller for canvas-specific buttons.
    Manages buttons displayed on or around the traffic canvas.
    """

    PADDING = 16

    def __init__(self, main_ui, traffic_view: TrafficView):
        """
        Initialize canvas buttons.

        Args:
            main_ui: Reference to the root UI widget (loaded from .ui).
            traffic_view: Reference to the specific TrafficView widget.
        """
        super().__init__()
        self.main_ui = main_ui
        self.view = traffic_view
        self.zoom_buttons = None
        self.b_plus = None
        self.b_minus = None
        self.b_sidebar_toggle = None
        self.sidebar = None

    def setup_ui(self) -> None:
        """Set up UI connections and overlay logic."""
        if not self._find_widgets():
            return

        self._reparent_widgets()
        self._connect_signals()

        # Install event filter to update positions on resize
        self.view.installEventFilter(self)
        self._update_position()

    def _find_widgets(self) -> bool:
        """Find all required widgets from the UI. Returns True if all found."""
        widget_specs = [
            (QFrame, "zoom_buttons"),
            (QToolButton, "b_sidebar_toggle"),
            (QScrollArea, "sidebar"),
            (QToolButton, "b_plus"),
            (QToolButton, "b_minus"),
        ]

        for widget_type, name in widget_specs:
            widget = self.main_ui.findChild(widget_type, name)
            if not widget:
                print(f"Error: Could not find '{name}' in UI.")
                return False
            setattr(self, name, widget)
        return True

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
        """Toggle the visibility of the sidebar."""
        self.sidebar.setVisible(not self.sidebar.isVisible())


    def _update_position(self) -> None:
        """Update overlay button positions relative to the view."""
        if not self.zoom_buttons or not self.view or not self.b_sidebar_toggle:
            return

        # Position zoom buttons in top-right corner
        zoom_x = self.view.width() - self.zoom_buttons.width() - self.PADDING
        self.zoom_buttons.move(zoom_x, self.PADDING)

        # Position sidebar toggle in top-left corner
        self.b_sidebar_toggle.move(0, self.PADDING)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        """Intercept events from the TrafficView to update overlay positions."""
        if source == self.view and event.type() == QEvent.Type.Resize:
            self._update_position()
        return super().eventFilter(source, event)