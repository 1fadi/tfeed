from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Header
from . import *


class Reader(Screen):
    BINDINGS = [
        Binding(
            "question_mark", "push_screen('help')", "Help", key_display="?"
        ),
    ]

    def __init__(self, *, entries: list):
        super().__init__()
        self.entries: list = entries
        self.article_list: ArticleList = ArticleList(id="leftpane")
        self.article_view: ArticleView = ArticleView(id="ArticleView")

    def on_mount(self) -> None:
        self.article_list.focus()

    def compose(self) -> ComposeResult:
        yield Header()
        yield MainScreen(
            self.article_list,
            VerticalPage(self.article_view, id="rightpane"),
            id="app-grid",
            entries=self.entries
        )
        self.append_articles(self.article_list)

    def on_vertical_page_move_focus(self, event: VerticalPage.MoveFocus) -> None:
        if self.article_view.DEFAULT:
            return
        if self.article_view.has_focus:
            self.set_focus(self.article_list)
        else:
            self.set_focus(self.article_view)

    def append_articles(self, container: ArticleList) -> None:
        for i in range(len(self.entries)):
            article: Article = Article(id=f"Article-{i}")
            article.article_title = self.entries[i]["title"]
            container.append(article)


class RssReader(App[None]):
    """The main class to start the App."""

    SCREENS = {"help": Help}

    def __init__(
        self,
        *,
        css_path: str,
        title: str,
        help_file: str,
        entries: list
    ):
        self.CSS_PATH = css_path
        self.TITLE = title
        super().__init__()
        self.entries = entries

    def on_mount(self) -> None:
        self.push_screen(Reader(entries=self.entries))

