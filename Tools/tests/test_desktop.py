"""Project discovery and launcher tests, including frozen/external executable paths."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_pipeline import ProjectCase
from config_desktop import executable_directory, find_project, is_project, main


class DesktopTests(ProjectCase):
    def test_find_project_from_build_output_or_root(self):
        self.assertEqual(find_project(self.root / "Builds" / "ConfigTool"), self.root)
        self.assertEqual(find_project(self.root), self.root)
        self.assertFalse(is_project(self.root / "ConfigSource"))

    def test_unrelated_executable_does_not_use_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(find_project(directory))

    def test_frozen_executable_path_ignores_extraction_directory(self):
        location = self.root / "Builds" / "ConfigTool" / "TDConfigTool.exe"
        with patch("sys.frozen", True, create=True), patch("sys.executable", str(location)):
            self.assertEqual(executable_directory(), location.parent)

    def test_explicit_project_and_cancelled_picker(self):
        with patch("config_desktop.tk.Tk"), patch("config_desktop.ConfigApp") as app:
            self.assertEqual(main(["--root", str(self.root)]), 0)
            self.assertEqual(app.call_args.args[1].root, self.root)
        with patch("config_desktop.tk.Tk"), patch("config_desktop.find_project", return_value=None), \
                patch("config_desktop.filedialog.askdirectory", return_value=""), \
                patch("config_desktop.ConfigApp") as app:
            self.assertEqual(main([]), 0)
            app.assert_not_called()

    def test_invalid_selection_then_valid_project(self):
        with patch("config_desktop.tk.Tk"), patch("config_desktop.find_project", return_value=None), \
                patch("config_desktop.filedialog.askdirectory", side_effect=[str(self.root / "bad"), str(self.root)]), \
                patch("config_desktop.messagebox.showerror") as error, patch("config_desktop.ConfigApp") as app:
            self.assertEqual(main([]), 0)
            error.assert_called_once()
            self.assertEqual(app.call_args.args[1].root, self.root)

    def test_startup_failure_is_visible_in_windowed_mode(self):
        with patch("config_desktop.tk.Tk"), patch("config_desktop.messagebox.showerror") as error:
            self.assertEqual(main(["--root", str(self.root / "missing")]), 1)
            error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
