import io

import matplotlib.pyplot as plt
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap


def latex_to_pixmap(
        latex_str: str,
        font_size: int = 12,
        color: str = "black",
        max_width: int | None = 270,
        max_height: int | None = None,
        device_pixel_ratio: float = 1.0,
) -> QPixmap:
    """
    Converts a LaTeX string into a QPixmap using Matplotlib.

    Args:
        latex_str: The LaTeX string to render.
        font_size: Font size for the rendered text.
        color: Text color.
        max_width: Maximum width of the output pixmap in logical pixels. If None, no width limit.
        max_height: Maximum height of the output pixmap in logical pixels. If None, no height limit.
        device_pixel_ratio: The device pixel ratio for high-DPI displays (e.g., 2.0 for Retina).

    Returns:
        A QPixmap containing the rendered LaTeX, scaled to fit within
        max_width and max_height while preserving aspect ratio.
        The pixmap's devicePixelRatio is set appropriately for sharp display on high-DPI screens.
    """
    if not latex_str:
        return QPixmap()

    try:
        # 1. Create a Matplotlib Figure
        # figsize is small because bbox_inches='tight' will resize it anyway
        fig = plt.figure(figsize=(0.1, 0.1), dpi=300)

        # 2. Add the text (wrap in $ for math mode)
        text_content = f"${latex_str}$" if not latex_str.startswith("$") else latex_str

        # Add text to figure
        fig.text(0, 0, text_content, fontsize=font_size, color=color)

        # 3. Save to a memory buffer
        buf = io.BytesIO()

        # transparent=True makes the background see-through
        # bbox_inches='tight' crops it to the text size
        plt.savefig(
            buf, format="png", bbox_inches="tight", pad_inches=0.05, transparent=True
        )
        plt.close(fig)  # Close figure to free memory

        # 4. Convert Buffer to QImage, then QPixmap
        buf.seek(0)
        qimg = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(qimg)

        # 5. Scale the image to fit within max_width and max_height (in physical pixels)
        # Multiply by device_pixel_ratio to render at full resolution for high-DPI displays
        physical_max_width = int(max_width * device_pixel_ratio) if max_width is not None else None
        physical_max_height = int(max_height * device_pixel_ratio) if max_height is not None else None
        pixmap = _scale_pixmap_to_fit(pixmap, physical_max_width, physical_max_height)

        # 6. Set the device pixel ratio so Qt displays it at the correct logical size
        if device_pixel_ratio != 1.0:
            pixmap.setDevicePixelRatio(device_pixel_ratio)

        return pixmap

    except Exception as e:
        print(f"Error rendering LaTeX: {e}")
        return QPixmap()


def _scale_pixmap_to_fit(
        pixmap: QPixmap,
        max_width: int | None,
        max_height: int | None,
) -> QPixmap:
    """
    Scale a pixmap to fit within the given max dimensions while preserving aspect ratio.

    Only scales down if the pixmap exceeds the max dimensions. Does not scale up.

    Args:
        pixmap: The pixmap to scale.
        max_width: Maximum width. If None, no width limit.
        max_height: Maximum height. If None, no height limit.

    Returns:
        The scaled pixmap.
    """
    if pixmap.isNull():
        return pixmap

    current_width = pixmap.width()
    current_height = pixmap.height()

    # Calculate scale factors for each dimension
    width_scale = 1.0
    height_scale = 1.0

    if max_width is not None and current_width > max_width:
        width_scale = max_width / current_width

    if max_height is not None and current_height > max_height:
        height_scale = max_height / current_height

    # Use the smaller scale factor to ensure we fit within both constraints
    scale = min(width_scale, height_scale)

    if scale < 1.0:
        new_width = int(current_width * scale)
        new_height = int(current_height * scale)
        pixmap = pixmap.scaled(
            new_width,
            new_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    return pixmap
