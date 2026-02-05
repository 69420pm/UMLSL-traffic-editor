import io

from PySide6.QtGui import QPixmap

import matplotlib.pyplot as plt

from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QPixmap, QImage

def latex_to_pixmap(latex_str, font_size=12, color="black"):
    """
    Converts a LaTeX string into a QPixmap using Matplotlib.
    """
    if not latex_str:
        return QPixmap()

    try:
        # 1. Create a Matplotlib Figure
        # figsize is small because bbox_inches='tight' will resize it anyway
        fig = plt.figure(figsize=(0.1, 0.1), dpi=100)

        # 2. Add the text (wrap in $ for math mode)
        text_content = f"${latex_str}$" if not latex_str.startswith("$") else latex_str

        # Add text to figure
        fig.text(0, 0, text_content, fontsize=font_size, color=color)

        # 3. Save to a memory buffer
        buf = io.BytesIO()

        # transparent=True makes the background see-through
        # bbox_inches='tight' crops it to the text size
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.05, transparent=True)
        plt.close(fig)  # Close figure to free memory

        # 4. Convert Buffer to QImage, then QPixmap
        buf.seek(0)
        qimg = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(qimg)

        return pixmap

    except Exception as e:
        print(f"Error rendering LaTeX: {e}")
        return QPixmap()


