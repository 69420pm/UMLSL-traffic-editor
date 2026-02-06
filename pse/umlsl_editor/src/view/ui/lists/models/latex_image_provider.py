"""
LaTeX image provider for QML views.

Provides a QQuickImageProvider that renders LaTeX strings to images
for display in QML list views.
"""

from urllib.parse import unquote

from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap
from PySide6.QtQuick import QQuickImageProvider

from pse.umlsl_editor.src.view.ui.lists.latex_renderer import latex_to_pixmap


class LatexImageProvider(QQuickImageProvider):
    """
    Image provider that renders LaTeX strings to QML-compatible images.

    This provider is registered with the QML engine and can be accessed
    via image URLs in the format: "image://latex/<latex_string>"

    The LaTeX string in the URL should be URL-encoded if it contains
    special characters.
    """

    def __init__(self) -> None:
        """Initialize the LaTeX image provider."""
        super().__init__(QQuickImageProvider.ImageType.Pixmap)
        self._cache: dict[str, QPixmap] = {}

    def requestPixmap(
            self, id: str, size: QSize, requestedSize: QSize
    ) -> QPixmap:
        """
        Provide a pixmap for the given LaTeX string.

        Args:
            id: The LaTeX string to render (URL-decoded by Qt).
            size: Output parameter for the actual image size.
            requestedSize: The requested size (width used as max_width if valid).

        Returns:
            The rendered pixmap.
        """
        # URL-decode the LaTeX string (Qt does not auto-decode image provider IDs)
        latex_string = unquote(id)

        # Use requested size as max dimensions, or default to 150x36
        max_width = requestedSize.width() if requestedSize.width() > 0 else 200
        max_height = requestedSize.height() if requestedSize.height() > 0 else 36

        # Create a cache key based on the LaTeX and max dimensions
        cache_key = f"{latex_string}_{max_width}_{max_height}"

        if cache_key not in self._cache:
            # Render the LaTeX to a pixmap
            try:
                pixmap = latex_to_pixmap(
                    latex_string,
                    font_size=10,
                    color="#FFFFFF",
                    max_width=max_width,
                    max_height=max_height,
                )
            except Exception:
                pixmap = QPixmap()
            self._cache[cache_key] = pixmap

        pixmap = self._cache[cache_key]

        if pixmap.isNull():
            return QPixmap()

        return pixmap

    def clear_cache(self) -> None:
        """Clear the image cache."""
        self._cache.clear()

    def invalidate_latex(self, latex: str) -> None:
        """
        Invalidate cached images for a specific LaTeX string.

        Args:
            latex: The LaTeX string whose cached images should be cleared.
        """
        keys_to_remove = [key for key in self._cache if key.startswith(f"{latex}_")]
        for key in keys_to_remove:
            del self._cache[key]
