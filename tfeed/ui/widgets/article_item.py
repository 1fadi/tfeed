from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.console import RenderableType


class Article(Widget, can_focus=False):

    highlighted: bool = reactive(False)
    article_title: str = reactive("")
    article_id: int = reactive(int)

    class _ChildClicked(Message):
        """inform the parent when an a child is clicked."""

        pass

    def render(self) -> RenderableType:
        return Text(self.article_title)

    def on_click(self) -> None:
        self.emit_no_wait(self._ChildClicked(self))

    def watch_highlighted(self, value: bool) -> None:
        self.set_class(value, "--highlight")
