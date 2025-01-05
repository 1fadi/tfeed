from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Label

from rich.markdown import Markdown
from pathlib import Path
import os


class Help(Screen):
    """The help screen for the application."""

    BINDINGS = [("escape,space,q,question_mark", "pop_screen", "Close")]

    def compose(self) -> ComposeResult:
        """Compose the app's help.

        Returns:
            ComposeResult: The result of composing the help screen.
        """
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        HELP_PATH = os.path.join(ROOT_DIR, "ui/help.md")
        yield Label(Markdown(Path(HELP_PATH).with_suffix(".md").read_text()))
