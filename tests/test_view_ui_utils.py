import unittest
import tempfile
import os
from unittest.mock import patch

from pse.umlsl_editor.src.view.ui_utils import load_ui


class TestUIUtils(unittest.TestCase):

    def test_load_ui_nonexistent_file(self):
        result = load_ui("nonexistent.ui")
        self.assertIsNone(result)

    @patch('pse.umlsl_editor.src.view.ui_utils.QFile.open')
    @patch('pse.umlsl_editor.src.view.ui_utils.QUiLoader.load')
    def test_load_ui_file_open_fails(self, mock_load, mock_open):
        mock_open.return_value = False

        result = load_ui("some.ui")

        self.assertIsNone(result)
        mock_open.assert_called_once()
        mock_load.assert_not_called()

    @patch('pse.umlsl_editor.src.view.ui_utils.QFile')
    @patch('pse.umlsl_editor.src.view.ui_utils.QUiLoader.load')
    def test_load_ui_success(self, mock_load, mock_qfile):
        mock_file = mock_qfile.return_value
        mock_file.open.return_value = True
        mock_widget = mock_load.return_value

        result = load_ui("valid.ui")

        self.assertEqual(result, mock_widget)
        mock_file.open.assert_called_once()
        mock_file.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
