"""
Binder for the main window .ui structure.

Responsibilities:
- Bind key sub-widgets from a loaded QMainWindow root using objectName lookups.
- Provide typed attributes for controllers to wire behavior.
- Avoid implementing application logic; this class is strictly structural.

Designer expectations (suggested objectName values):
- mainWindow: QMainWindow (root)
- mainSplitter: QSplitter (set as central widget)
- sidebarContainer: QWidget (left pane container)
- canvasContainer: QWidget (right pane container) OR direct promoted QGraphicsView
- trafficView: QGraphicsView (promoted to TrafficCanvasView), optional if using canvasContainer

Promoted widget setup in Designer:
- Add a QGraphicsView in the canvas area.
- Promote it:
  - Promoted class name: TrafficCanvasView
  - Header: pse.umlsl_editor.src.view.canvas.traffic_view

Notes:
- This binder assumes objectNames are set consistently in Designer.
- The actual loading of the .ui and creation of the widget tree is done elsewhere.
- Controllers should call bind(root) after the .ui is loaded to map sub-widgets.
"""

from typing import Generic, Optional, TypeVar

from PySide6.QtWidgets import QGraphicsView, QMainWindow, QSplitter, QWidget

TMainWindow = TypeVar("TMainWindow", bound=QMainWindow)


class MainWindowUiBinder(Generic[TMainWindow]):
    """
    Maps a loaded main window .ui (QMainWindow) to structured attributes.

    Attributes:
        root: The bound QMainWindow instance.
        main_splitter: The central QSplitter dividing sidebar and canvas.
        sidebar_container: The left pane container (may host tabs/lists).
        canvas_container: The right pane container (may host the graphics view).
        traffic_view: The graphics view (promoted to TrafficCanvasView), if present.
    """

    def __init__(self) -> None:
        self.root: Optional[TMainWindow] = None
        self.main_splitter: Optional[QSplitter] = None
        self.sidebar_container: Optional[QWidget] = None
        self.canvas_container: Optional[QWidget] = None
        self.traffic_view: Optional[QGraphicsView] = None

    def bind(self, root: TMainWindow) -> None:
        """
        Bind the already-loaded .ui root to this binder.

        Expected usage:
            1) Load the .ui into a QMainWindow instance (root)
            2) Call binder.bind(root)
            3) Controllers use binder.* attributes to wire behaviors

        This method should:
        - Store the root
        - Find children by objectName via root.findChild(...)
        - Assign them to the corresponding attributes

        Raises:
            NotImplementedError: Binding logic is not implemented yet (structure only).
        """
        raise NotImplementedError
