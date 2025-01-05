from rich.align import Align
from rich.text import Text
from rich.markdown import Markdown
from rich.console import RenderableType, Group
from textual.widgets import Static
from textual.reactive import reactive
import os


DEFAULT_TEXT = Text("Click on an article to display its contents.")


class ArticleView(Static, can_focus=True):
    """widget to display the whole article to read."""

    DEFAULT = reactive(True)
    article_main = reactive(Text("Click on an article to display its contents."))
    article_title = reactive(Text)
    article_date = reactive(Text)

    def on_mount(self) -> None:
        self.add_class("text-disabled")

    def update_article(
        self, article_main_: str, article_title_: str, article_date_: str
    ) -> None:
        self.article_main = article_main_
        self.article_title = article_title_
        self.article_date = article_date_

    def render(self) -> RenderableType:
        if self.article_main == DEFAULT_TEXT and self.DEFAULT:
            return Align.center(
                self.article_main,
                vertical="middle",
                height=os.get_terminal_size()[1] - 3,
            )
        else:
            if self.DEFAULT:
                self.DEFAULT = False
                self._remove_default()
            renderables: Group = self._prepare_view()
            return renderables

    def watch_article_main(self) -> None:
        self.update(self.render())

    def _remove_default(self) -> None:
        if "text-disabled" in self.classes:
            self.remove_class("text-disabled")

    def _prepare_view(self) -> RenderableType:
        right = Align.right(self.article_date, style="italic")
        center = Align.center(self.article_title, style="bold")
        left = Align.left(Markdown(self.article_main))
        return Group(right, "\n\n", center, "\n", left)
        
