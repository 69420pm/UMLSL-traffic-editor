"""
Centralized locations of .ui files produced by Qt Designer.

Usage:
- Keep .ui files editable and load them at runtime via a UiLoader.
- Use these constants wherever a .ui needs to be loaded.
- Adjust the paths if you choose a different resource layout.

Convention:
- .ui files live under pse/umlsl_editor/resources/ui/
- Each file has a stable, descriptive name that matches its role.

Note:
This module only defines constants and lightweight helpers; it does not perform any I/O.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UiFiles:
    """
    Immutable container of .ui file paths.

    You can inject a customized instance of UiFiles into components if your
    environment uses different resource directories or filenames.
    """
    main_window: str = "pse/umlsl_editor/resources/ui/main_window.ui"
    car_modal: str = "pse/umlsl_editor/resources/ui/car_modal.ui"
    road_modal: str = "pse/umlsl_editor/resources/ui/road_modal.ui"
    query_modal: str = "pse/umlsl_editor/resources/ui/query_modal.ui"
    confirmation_dialog: str = "pse/umlsl_editor/resources/ui/confirmation_dialog.ui"


# Default singleton-style instance for convenience imports.
DEFAULT_UI_FILES = UiFiles()


def get_ui_files() -> UiFiles:
    """
    Return the default UiFiles instance.

    Prefer dependency injection in larger applications, but this helper makes it
    easy to fetch the default paths in smaller modules.
    """
    return DEFAULT_UI_FILES
