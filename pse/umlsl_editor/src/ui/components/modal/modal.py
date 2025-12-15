from typing import Optional

from pse.umlsl_editor.src.core.car import Car
from pse.umlsl_editor.src.core.road import Road
from pse.umlsl_editor.src.ui.scene_element import LaTeXPreviewWidget


class BaseDialog:
    """Abstract base for Modal Dialogs."""

    def open(self): pass

    def validate(self) -> bool: pass


class RoadEditorDialog(BaseDialog):
    def __init__(self, road: Optional[Road]): pass


class CarEditorDialog(BaseDialog):
    def __init__(self, car: Optional[Car]): pass

    class QueryEditorDialog(BaseDialog):
        """Dialog with LaTeX input and Preview."""

        def __init__(self):
            self.preview_widget = LaTeXPreviewWidget()

        def on_text_changed(self, text):
            # Triggers live preview
            pass
