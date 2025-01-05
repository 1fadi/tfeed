from __future__ import annotations
from typing import ClassVar

from textual import events
from textual.await_remove import AwaitRemove
from textual.binding import Binding, BindingType
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.widget import AwaitMount, Widget

from .article_item import Article


class VerticalPage(Widget):
    """A container widget which aligns children virtically."""

    BINDINGS: ClassVar[list[BindingType]] = [
        # normal-keybindings
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("up", "scroll_up", "Scroll Up", show=False),
        Binding("down", "scroll_down", "Scroll Down", show=False),
        Binding("right,left", "move_focus", "Move Focus", show=False),
        # vim-keybindings
        Binding("o,O", "select_cursor", "Select", show=False),
        Binding("k", "scroll_up", "Scroll Up", show=False),
        Binding("j", "scroll_down", "Scroll Down", show=False),
        Binding("h", "move_focus", "Move Focus", show=False),
        Binding("l", "move_focus", "Move Focus", show=False),
        Binding("g", "scroll_home", "Scroll Home", show=False),
        Binding("G", "scroll_end", "Scroll End", show=False),
    ]

    class MoveFocus(Message, bubble=True):
        """
        Event to move focus to other child in a container.
        e.g. when you press right/left arrow keys, h or l.
        """

        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.styles.layout = "vertical"
        self.styles.overflow_y = "auto"
        self.styles.border = ("round", "white")
        self.styles.scrollbar_size_vertical = 1

    def action_move_focus(self) -> None:
        self.emit_no_wait(self.MoveFocus(self))

    def action_scroll_home(self) -> None:
        super().scroll_home(animate=False)

    def action_scroll_end(self) -> None:
        super().scroll_end(animate=False)


class ArticleList(VerticalPage, can_focus=True, can_focus_children=False):
    """Displays a vertical list of `Article`s which can be highlighted
    and selected using the mouse or keyboard.

    Attributes:
        index: The index in the list that's currently highlighted.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        # normal-keybindings
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
        Binding("h", "move_focus", "Move Focus", show=False),
        Binding("l", "move_focus", "Move Focus", show=False),
        # vim-keybindings
        Binding("o,O", "select_cursor", "Select", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("j", "cursor_down", "Cursor Down", show=False),
    ]

    index = reactive(0, always_update=True)

    class Highlighted(Message, bubble=True):
        """Emitted when the highlighted item changes.

        Highlighted item is controlled using up/down or j/k keys.

        Attributes:
            item: The highlighted item, if there is one highlighted.
        """

        def __init__(self, sender: ArticleList, item: Article | None) -> None:
            super().__init__(sender)
            self.item: Article | None = item

    class Selected(Message, bubble=True):
        """Emitted when a list item is selected, e.g. when you press the enter key on it.

        Attributes:
            item: The selected item.
        """

        def __init__(self, sender: ArticleList, item: Article) -> None:
            super().__init__(sender)
            self.item: Article = item

    def __init__(
        self,
        *children: Article,
        initial_index: int | None = 0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Args:
            *children: The Articles to display in the list.
            initial_index: The index that should be highlighted when the list is first mounted.
            name: The name of the widget.
            id: The unique ID of the widget used in CSS/query selection.
            classes: The CSS classes of the widget.
        """
        super().__init__(*children, name=name, id=id, classes=classes)
        self._index = initial_index

    def on_mount(self) -> None:
        """Ensure the ArticleList is fully-settled after mounting."""
        self.index = self._index

    @property
    def highlighted_child(self) -> Article | None:
        """Article | None: The currently highlighted Article,
        or None if nothing is highlighted.
        """
        if self.index is None:
            return None
        elif 0 <= self.index < len(self.children):
            return self.children[self.index]

    def validate_index(self, index: int | None) -> int | None:
        """Clamp the index to the valid range, or set to None if there's nothing to highlight."""
        if not self.children or index is None:
            return None
        return self._clamp_index(index)

    def _clamp_index(self, index: int) -> int:
        """Clamp the index to a valid value given the current list of children"""
        last_index = max(len(self.children) - 1, 0)
        if index < 0:
            return 0
        elif index > last_index:
            return last_index
        else:
            return index

    def _is_valid_index(self, index: int | None) -> bool:
        """Return True if the current index is valid given the current list of children"""
        if index is None:
            return False
        return 0 <= index < len(self.children)

    def watch_index(self, old_index: int, new_index: int) -> None:
        """Updates the highlighting when the index changes."""
        if self._is_valid_index(old_index):
            old_child = self.children[old_index]
            old_child.highlighted = False
        if self._is_valid_index(new_index):
            new_child = self.children[new_index]
            new_child.highlighted = True
        else:
            new_child = None

        self._scroll_highlighted_region()
        self.emit_no_wait(self.Highlighted(self, new_child))

    def append(self, item: Article) -> AwaitMount:
        """Append a new Article to the end of the ArticleList.

        Args:
            item: The Article to append.

        Returns:
            An awaitable that yields control to the event loop
                until the DOM has been updated with the new child item.
        """
        await_mount = self.mount(item)
        if len(self) == 1:
            self.index = 0
        return await_mount

    def clear(self) -> AwaitRemove:
        """Clear all items from the ArticleList.

        Returns:
            An awaitable that yields control to the event loop until
                the DOM has been updated to reflect all children being removed.
        """
        await_remove = self.query("ArticleList > Article").remove()
        self.index = None
        return await_remove

    def action_select_cursor(self) -> None:
        selected_child = self.highlighted_child
        self.emit_no_wait(self.Selected(self, selected_child))

    def action_cursor_down(self) -> None:
        self.index += 1

    def action_cursor_up(self) -> None:
        self.index -= 1

    def on_article__child_clicked(self, event: Article._ChildClicked) -> None:
        self.focus()
        self.index = self.children.index(event.sender)
        self.emit_no_wait(self.Selected(self, event.sender))

    def _scroll_highlighted_region(self) -> None:
        """Used to keep the highlighted index within vision"""
        if self.highlighted_child is not None:
            self.scroll_to_widget(self.highlighted_child, animate=False)

    def action_scroll_home(self) -> None:
        self.index = 0

    def action_scroll_end(self) -> None:
        self.index +=1

    def __len__(self):
        return len(self.children)


class MainScreen(Container, can_focus=False, can_focus_children=True):

    def __init__(
        self,
        *children,
        entries: list,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None
    ) -> None:

        super().__init__(*children, name=name, id=id, classes=classes)
        self.entries = entries
    
    def on_article_list_selected(self, event: ArticleList.Selected) -> None:
        event.stop()
        article_view = self.query_one("#ArticleView")
        self.screen.set_focus(article_view)
        index = int(event.item.id.split("-")[1])
        entry = self.select_entry(index)
        article_main = entry["summary"]
        article_title = entry["title"]
        article_date = entry["date"]
        article_view.update_article(article_main, article_title, article_date)

    def select_entry(self, index) -> str:
        return self.entries[index]

