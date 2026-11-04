"""
GUI Application Module for Griductive.
Provides programmatic interface and standalone launcher for the modern Griductive GUI.
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gui.web_server import start_server


def launch_gui(port: int = 8000, open_browser: bool = True) -> None:
    """Launches the Griductive GUI application."""
    print(f"[*] Launching Griductive GUI on http://localhost:{port} ...")
    start_server(port=port, open_browser=open_browser)


class GriductiveApp:
    """Application wrapper class for Griductive GUI."""

    def __init__(self, port: int = 8000, open_browser: bool = True):
        self.port = port
        self.open_browser = open_browser

    def run(self) -> None:
        launch_gui(port=self.port, open_browser=self.open_browser)


if __name__ == "__main__":
    launch_gui()
