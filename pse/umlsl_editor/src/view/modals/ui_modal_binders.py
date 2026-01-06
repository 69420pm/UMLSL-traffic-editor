"""
Binder classes for modal .ui files (car, road, query, confirmation).

These classes are responsible for mapping objectNames from Qt Designer .ui files
to typed Python attributes for later use by controllers and modal logic.

Structure-only:
- No I/O or loading implemented here.
- bind(root) methods are declared but not implemented.
- Controllers or modal classes should call bind(root) after loading the .ui
  via a runtime loader.

Designer expectations (suggested objectName values per modal):

Car Modal:
- nameInput: QLineEdit
- roadCombo: QComboBox
- laneIndexSpin: QDoubleSpinBox (or QSpinBox)
- laneDirectionCombo: QComboBox
- colorInput: QLineEdit
- chooseColorButton: QPushButton
- positionSpin: QDoubleSpinBox
- transitionSpin: QDoubleSpinBox
- velocitySpin: QDoubleSpinBox
- lengthSpin: QDoubleSpinBox
- okButton: QPushButton
- cancelButton: QPushButton

Road Modal:
- nameInput: QLineEdit
- orientationCombo: QComboBox
- forwardLanesSpin: QDoubleSpinBox (or QSpinBox)
- backwardLanesSpin: QDoubleSpinBox (or QSpinBox)
- positionSpin: QDoubleSpinBox
- okButton: QPushButton
- cancelButton: QPushButton

Query Modal:
- queryText: QTextEdit
- carCombo: QComboBox
- okButton: QPushButton
- cancelButton: QPushButton

Confirmation Dialog:
- messageLabel: QLabel
- okButton: QPushButton
- cancelButton: QPushButton
"""

from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
)


class CarModalUiBinder:
    """
    Binder for car modal .ui widgets.

    Maps objectNames from the loaded car modal .ui to typed attributes for use
    by modal logic and controllers.
    """

    def __init__(self) -> None:
        self.root: Optional[QDialog] = None
        self.name_input: Optional[QLineEdit] = None
        self.road_combo: Optional[QComboBox] = None
        self.lane_index_spin: Optional[QDoubleSpinBox] = None
        self.lane_direction_combo: Optional[QComboBox] = None
        self.color_input: Optional[QLineEdit] = None
        self.choose_color_button: Optional[QPushButton] = None
        self.position_spin: Optional[QDoubleSpinBox] = None
        self.transition_spin: Optional[QDoubleSpinBox] = None
        self.velocity_spin: Optional[QDoubleSpinBox] = None
        self.length_spin: Optional[QDoubleSpinBox] = None
        self.ok_button: Optional[QPushButton] = None
        self.cancel_button: Optional[QPushButton] = None

    def bind(self, root: QDialog) -> None:
        """
        Bind the loaded dialog root to this binder.

        Expected to:
        - Store root
        - Find children by objectName and assign to attributes

        Structure-only: not implemented.
        """
        raise NotImplementedError


class RoadModalUiBinder:
    """
    Binder for road modal .ui widgets.

    Maps objectNames from the loaded road modal .ui to typed attributes for use
    by modal logic and controllers.
    """

    def __init__(self) -> None:
        self.root: Optional[QDialog] = None
        self.name_input: Optional[QLineEdit] = None
        self.orientation_combo: Optional[QComboBox] = None
        self.forward_lanes_spin: Optional[QDoubleSpinBox] = None
        self.backward_lanes_spin: Optional[QDoubleSpinBox] = None
        self.position_spin: Optional[QDoubleSpinBox] = None
        self.ok_button: Optional[QPushButton] = None
        self.cancel_button: Optional[QPushButton] = None

    def bind(self, root: QDialog) -> None:
        """
        Bind the loaded dialog root to this binder.

        Expected to:
        - Store root
        - Find children by objectName and assign to attributes

        Structure-only: not implemented.
        """
        raise NotImplementedError


class QueryModalUiBinder:
    """
    Binder for query modal .ui widgets.

    Maps objectNames from the loaded query modal .ui to typed attributes for use
    by modal logic and controllers.
    """

    def __init__(self) -> None:
        self.root: Optional[QDialog] = None
        self.query_text: Optional[QTextEdit] = None  # intended: QTextEdit
        self.car_combo: Optional[QComboBox] = None
        self.ok_button: Optional[QPushButton] = None
        self.cancel_button: Optional[QPushButton] = None

    def bind(self, root: QDialog) -> None:
        """
        Bind the loaded dialog root to this binder.

        Expected to:
        - Store root
        - Find children by objectName and assign to attributes

        Structure-only: not implemented.
        """
        raise NotImplementedError


class ConfirmationDialogUiBinder:
    """
    Binder for delete confirmation dialog .ui widgets.

    Maps objectNames from the loaded confirmation dialog .ui to typed attributes
    for use by modal logic and controllers.
    """

    def __init__(self) -> None:
        self.root: Optional[QDialog] = None
        self.message_label: Optional[QLabel] = None
        self.ok_button: Optional[QPushButton] = None
        self.cancel_button: Optional[QPushButton] = None

    def bind(self, root: QDialog) -> None:
        """
        Bind the loaded dialog root to this binder.

        Expected to:
        - Store root
        - Find children by objectName and assign to attributes

        Structure-only: not implemented.
        """
        raise NotImplementedError
