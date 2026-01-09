from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

def load_ui(path, parent=None):
    loader = QUiLoader()
    file = QFile(path)
    if not file.open(QFile.ReadOnly):
        print(f"CRITICAL ERROR: Could not open {path}")
        return None
    widget = loader.load(file, parent)
    file.close()
    return widget