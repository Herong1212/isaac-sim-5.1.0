from typing import Dict, List, Optional

import carb
from carb.input import KEYBOARD_MODIFIER_FLAG_CONTROL, KEYBOARD_MODIFIER_FLAG_SHIFT
from omni import ui

from ..models import AbstractBrowserModel, DetailItem
from .detail_delegate import DetailDelegate


class ThumbnailView(ui.VGrid):
    """
    GridView to show thumbnails of details or categories.

    Keyword Args:
        delegate (DetailDelegate): delegate object to represent detail item
        thumbnail_size (int): width of thumbnail, in pixel. Default 128.
        thumbnail_aspect (float): Aspect ratio of thumbnail. Default 1.0 (width / height).
        extra_filter_fn (callable): Extra filter function called to filter items. Return True to show item otherwise hide.
            Default None. Function signure: bool extra_filter_fn(item: DetailItem)
        thumbnail_padding_width (int): padding width between thumbnails, default 1
        thumbnail_padding_height (int): padding height between thumbnails, default 1
        multiple_drag (bool): True to allow drag multiple items. Default False.

    Properties:
        selection (List[DetailItem]): selected detail items. Readonly.
        thumbnail_size (int): size of thumbnail, in pixel. Read and write.
    """

    def __init__(
        self,
        model,
        delegate: DetailDelegate = None,
        thumbnail_size: int = 128,
        thumbnail_aspect: float = 1,
        extra_filter_fn: callable = None,
        thumbnail_padding_width: int = 1,
        thumbnail_padding_height: int = 1,
        multiple_drag: bool = False,
    ):
        super().__init__(content_clipping=True)

        self._model_sub_ids: Dict[AbstractBrowserModel, callable] = {}
        self.model = model
        self._delegate = delegate or DetailDelegate(self._model)
        self._selections = []
        self._delegates = {}
        self._thumbnail_aspect = thumbnail_aspect
        self._thumbnail_padding_width = thumbnail_padding_width
        self._thumbnail_padding_height = thumbnail_padding_height
        self.thumbnail_size = thumbnail_size
        self._extra_filter_fn = extra_filter_fn
        self._multiple_drag = multiple_drag

        self._filter_words: Optional[str] = None
        self._on_selection_changed_fn = None
        self.__in_dragging = False

        if multiple_drag:
            # Multiple drag: keep selections when mouse pressed
            self.set_mouse_released_fn(lambda x, y, btn, flag: self._on_mouse_pressed(btn, flag, None))
            # Handle drag items in view for multiple items instead of delegate for single item
            self._delegate.set_drag_fn(self.on_drag)
        else:
            self.set_mouse_pressed_fn(lambda x, y, btn, flag: self._on_mouse_pressed(btn, flag, None))

        self._padding_left: Dict[DetailItem, ui.Spacer] = {}
        self._padding_right: Dict[DetailItem, ui.Spacer] = {}
        self._padding_top: Dict[DetailItem, ui.Spacer] = {}
        self._padding_bottom: Dict[DetailItem, ui.Spacer] = {}
        self._build_ui()

    def destroy(self):
        self._on_selection_changed_fn = None
        # Clear children widgets, otherwise it will crash when exiting if ui.ImageWithProvider loads remote image
        self.clear()
        self._delegate.destroy()

    @property
    def model(self) -> AbstractBrowserModel:
        return self._model

    @model.setter
    def model(self, new_model: AbstractBrowserModel) -> None:
        self._model = new_model
        if new_model not in self._model_sub_ids:
            self._model_sub_ids[new_model] = self._model.add_item_changed_fn(self._model_item_changed)

    @property
    def selection(self) -> List[DetailItem]:
        return self._selections

    @selection.setter
    def selection(self, items: List[DetailItem]) -> None:
        self._clear_selections()
        for item in items:
            self._add_selection(item)
        if self._on_selection_changed_fn is not None:
            self._on_selection_changed_fn(self._selections)

    @property
    def thumbnail_size(self) -> int:
        """Thumbnail size of detail item"""
        return self.column_width - 2 * self._thumbnail_padding_width

    @thumbnail_size.setter
    def thumbnail_size(self, value: int) -> None:
        """Thumbnail size of detail item"""
        self.column_width = value + 2 * self._thumbnail_padding_width

        # Update grid row height
        self.row_height = (
            value / self._thumbnail_aspect + 2 * self._thumbnail_padding_height + self._delegate.get_label_height()
        )
        self._delegate.thumbnail_size = value

    @property
    def thumbnail_padding_width(self) -> int:
        """Padding width between deaiil items"""
        return self._thumbnail_padding_width

    @thumbnail_padding_width.setter
    def thumbnail_padding_width(self, value: int) -> None:
        self._thumbnail_padding_width = value
        self.column_width = self.thumbnail_size + 2 * value
        for item in self._padding_left:
            self._padding_left[item].width = ui.Pixel(value)
            self._padding_right[item].width = ui.Pixel(value)

    @property
    def thumbnail_padding_height(self) -> int:
        """Padding width between deaiil items"""
        return self._thumbnail_padding_width

    @thumbnail_padding_height.setter
    def thumbnail_padding_height(self, value: int) -> None:
        self._thumbnail_padding_height = value
        self.row_height = (
            self.thumbnail_size / self._thumbnail_aspect
            + 2 * self._thumbnail_padding_height
            + self._delegate.get_label_height()
        )
        for item in self._padding_top:
            self._padding_top[item].height = ui.Pixel(value)
            self._padding_bottom[item].height = ui.Pixel(value)

    def filter(self, filter_words: Optional[List[str]]) -> None:
        """
        Filter detail items.
        Args:
            filter_words: A string list to filter detail items. None means filtering nothing.
        """
        self._filter_words = filter_words
        # Update item visibility, donot need to rebuild items.
        self.refresh()

    def set_selection_changed_fn(self, on_selection_changed_fn) -> None:
        """
        Set function called when selection changed.
        Args:
            on_selection_changed_fn (callable): Function called when selection changed. Function signure:
                void on_selection_changed_fn(selection: List[DetailItem])
        """
        self._on_selection_changed_fn = on_selection_changed_fn

    def set_extra_filter_fn(self, extra_filter_fn: Optional[callable]) -> None:
        self._extra_filter_fn = extra_filter_fn
        self.refresh()

    def refresh(self):
        """
        Refresh details items for visibility.
        """
        selection_changed = False
        for item in self._delegates:
            self._delegates[item].visible = self._is_item_visible(item)

            # Since item invisible, clear selection state
            if not self._delegates[item].visible:
                if self._remove_selection(item):
                    selection_changed = True

        if selection_changed and self._on_selection_changed_fn is not None:
            self._on_selection_changed_fn(self._selections)

    def clear(self) -> None:
        """Clear all items and selections"""
        super().clear()
        self._clear_selections()
        self._delegates.clear()
        self._padding_left.clear()

        if self._on_selection_changed_fn is not None:
            self._on_selection_changed_fn(self._selections)

    def on_drag(self, item: DetailItem) -> str:
        self.__in_dragging = True

        if item not in self._selections:
            return self._delegate.on_drag(item)

        # Combine item drag mime data into one
        drag_mime_datas: List[str] = []
        with ui.VStack():
            multiple = len(self._selections) > 1
            for item in self._selections:
                drag_mime_datas.append(self._delegate.on_multiple_drag(item) if multiple else self._delegate.on_drag(item))
        return "\n".join(drag_mime_datas)

    def _build_ui(self) -> None:
        self.clear()

        # Add detail items as grid children
        children = self._model.get_item_children()
        if children is None or len(children) == 0:
            return
        with self:
            for item in children:
                self._delegates[item] = ui.Frame(build_fn=lambda i=item: self._build_detail_frame(i))

    def _build_detail_frame(self, item: DetailItem) -> None:
        with self._delegates[item]:
            with ui.HStack(content_clipping=True):
                self._padding_left[item] = ui.Spacer(width=self._thumbnail_padding_width)
                with ui.VStack(content_clipping=True):
                    self._padding_top[item] = ui.Spacer(height=self._thumbnail_padding_height)
                    self._build_detail_item(item)
                    self._padding_bottom[item] = ui.Spacer(height=self._thumbnail_padding_height)
                self._padding_right[item] = ui.Spacer(width=self._thumbnail_padding_width)

        # To avoid re-creating items, always create first and change visibilty by filter words.
        self._delegates[item].visible = self._is_item_visible(item)

    def _build_detail_item(self, item: DetailItem) -> None:
        stack = ui.ZStack()
        with stack:
            self._delegate.build_widget(self._model, item)
        if self._multiple_drag:
            stack.set_mouse_released_fn(lambda x, y, btn, flag, item=item: self._on_mouse_pressed(btn, flag, item))
        else:
            stack.set_mouse_pressed_fn(lambda x, y, btn, flag, item=item: self._on_mouse_pressed(btn, flag, item))

    def _on_mouse_pressed(self, btn: int, flag: int, item: DetailItem) -> None:
        if btn == 0:
            self._on_click(flag, item)
        elif btn == 1:
            self._on_right_click(item)

    def _on_click(self, flag: int, item: DetailItem) -> None:
        if self.__in_dragging:
            if item:
                self.__in_dragging = False
            return

        if flag & KEYBOARD_MODIFIER_FLAG_CONTROL:
            if item in self._selections:
                self._remove_selection(item)
            else:
                self._add_selection(item)
        elif flag & KEYBOARD_MODIFIER_FLAG_SHIFT:
            if not self._selections:
                self._add_selection(item)
            elif item:
                last_selection = self._selections[-1]
                current_selection = item
                children = self._model.get_item_children(None)
                last_selection_index = children.index(last_selection)
                current_selection_index = children.index(current_selection)

                first_index = min(last_selection_index, current_selection_index)
                last_index = max(last_selection_index, current_selection_index)
                self._clear_selections()
                for i in reversed(range(first_index, last_index + 1)):
                    if self._delegates[children[i]].visible:
                        self._add_selection(children[i])
        else:
            self._clear_selections()
            self._add_selection(item)

        if self._on_selection_changed_fn is not None:
            self._on_selection_changed_fn(self._selections)

    def _on_right_click(self, item: DetailItem) -> None:
        if self._multiple_drag:
            # Do not change selection for right click in multiple drag mode
            return

        if item not in self._selections:
            self._clear_selections()
            self._add_selection(item)

            if self._on_selection_changed_fn is not None:
                self._on_selection_changed_fn(self._selections)

    def _clear_selections(self) -> None:
        for item in self._selections:
            self._delegates[item].selected = False
        self._selections.clear()

    def _add_selection(self, item: DetailItem) -> None:
        if item is not None:
            self._selections.append(item)
            self._delegates[item].selected = True

    def _remove_selection(self, item: DetailItem) -> bool:
        if item in self._selections:
            self._selections.remove(item)
            self._delegates[item].selected = False
            return True
        else:
            return False

    def _model_item_changed(self, model: ui.AbstractItemModel, item: DetailItem) -> None:
        self._build_ui()

    def _is_item_visible(self, item: DetailItem) -> bool:
        visible = item.filter(self._filter_words)
        if self._extra_filter_fn is not None:
            visible = visible and self._extra_filter_fn(item)

        return visible
