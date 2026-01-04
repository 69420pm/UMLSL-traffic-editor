"""
Simple confirmation dialog for destructive operations.
"""
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PySide6.QtCore import Qt


class ConfirmationDialog(QDialog):
    """
    Simple yes/no confirmation dialog.

    Used for confirming destructive operations like deletions.
    """

    def __init__(
        self,
        title: str,
        message: str,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize the confirmation dialog.

        Args:
            title: Window title.
            message: Confirmation message to display.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self._setup_ui(message)

    def _setup_ui(self, message: str) -> None:
        """Initialize the UI components."""
        # layout = QVBoxLayout(self)
        #
        # # Message label
        # message_label = QLabel(message)
        # message_label.setWordWrap(True)
        # layout.addWidget(message_label)
        #
        # # Button box
        # button_layout = QHBoxLayout()
        # button_layout.addStretch()
        #
        # yes_button = QPushButton("Yes")
        # yes_button.clicked.connect(self.accept)
        # button_layout.addWidget(yes_button)
        #
        # no_button = QPushButton("No")
        # no_button.clicked.connect(self.reject)
        # no_button.setDefault(True)
        # button_layout.addWidget(no_button)
        #
        # layout.addLayout(button_layout)
        #
        # # Set reasonable size
        # self.resize(300, 120)

    @staticmethod
    def confirm(
        title: str,
        message: str,
        parent: Optional[QWidget] = None
    ) -> bool:
        """
        Show confirmation dialog and return user's choice.

        Args:
            title: Window title.
            message: Confirmation message.
            parent: Parent widget.

        Returns:
            True if user clicked Yes, False otherwise.
        """
        # dialog = ConfirmationDialog(title, message, parent)
        # return dialog.exec() == QDialog.DialogCode.Accepted

