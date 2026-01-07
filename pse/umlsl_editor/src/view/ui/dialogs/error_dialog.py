from PySide6.QtWidgets import QVBoxLayout


class ErrorDialog:
    def __init__(self, error_title, error_message):
        self.error_title = error_title
        self.error_message = error_message

    def setup_ui(self):
        pass

    def on_close(self):
        pass