# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
A generic GridView Widget for File Systems.
"""
__all__ = ["FileBrowserGridView", "FileBrowserGridViewDelegate"]
import asyncio
import carb
import omni.kit.app

from typing import Dict, List, Optional, Callable
from functools import partial
from omni import ui
from carb import eventdispatcher, log_warn
from carb.input import KEYBOARD_MODIFIER_FLAG_CONTROL, KEYBOARD_MODIFIER_FLAG_SHIFT

from .view import FileBrowserView
from .model import FileBrowserItem, FileBrowserModel, FileBrowserUdimItem
from .style import UI_STYLES
from .card import FileBrowserItemCard
from .thumbnails import find_thumbnails_for_files_async
from . import THUMBNAILS_GENERATED_GLOBAL_EVENT
from .clipboard import is_path_cut


class FileBrowserGridView(FileBrowserView):
    """
    UI Widget for display files or folders as icons in a directory in grid view.

    Keyword Args:
        allow_multi_selection (bool): Optional argument to enable multi selection, defaults to True.
        selection_changed_fn (Callable): Function called when selection changed. Function signature:
            void selection_changed_fn(selections: List[:obj:`FileBrowserItem`])
    """
    def __init__(self, model: FileBrowserModel, **kwargs):
        self._delegate = None
        super().__init__(model)

        theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        use_default_style = carb.settings.get_settings().get_as_string("/persistent/app/window/useDefaultStyle") or False
        if use_default_style:
            self._style = {}
        else:
            self._style = UI_STYLES[theme]
        self._allow_multi_selection = kwargs.get("allow_multi_selection", True)
        self._selection_changed_fn = kwargs.get("selection_changed_fn", None)
        name="GridViewFrame"
        self._widget = ui.ScrollingFrame(
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
            style_type_name_override="GridView.ScrollingFrame",
            name=name,
            identifier=name,
        )
        self._delegate = FileBrowserGridViewDelegate(self._widget, theme, **kwargs)
        self.build_ui()

    @property
    def selections(self):
        if self._delegate:
            return self._delegate.selections
        return []

    @selections.setter
    def selections(self, selections):
        if self._delegate:
            self._delegate.selections = selections or []

    def build_ui(self, restore_selections: Optional[List[FileBrowserItem]] = None):
        """
        Build the UI of the grid view.

        Keyword Args:
            restore_selections (List[:obj:`FileBrowserItem`]): List of file browser items to restore selection to.
        """
        if self._delegate:
            self._delegate.build_grid(self.model)
        self.refresh_ui(selections=restore_selections)

    def scale_view(self, scale: float):
        """
        Change the scale of items inside the grid view.
        Args:
            scale (float): the new scale to set.
        """
        if self._delegate:
            self._delegate.scale = scale

    def refresh_ui(self, item: Optional[FileBrowserItem] = None, selections: Optional[List[FileBrowserItem]] = None):
        """
        Throttle the refreshes so that the UI can keep up with multiple refresh directives in succession.

        Keyword Args:
            item (:obj:`FileBrowserItem`): Unused argument, kept for compatibility.
            selection (List[:obj:`FileBrowserItem`]): List of file browser items to set the new selection to.
        """
        if not self._delegate:
            return

        def apply_selections(selections):
            self.selections = selections

        def refresh_ui_callback(selections):
            self._delegate.update_grid(self.model)
            # OM-70157: Switching between List/different Grid View sizes shouldn't reset user selections
            if selections:
                self.select_and_center(selections[0], callback=lambda _: apply_selections(selections))

        self._throttled_refresh_ui(
            item=None,
            callback=lambda _: refresh_ui_callback(selections),
            throttle_frames=2)

    def select_and_center(self, item: FileBrowserItem, callback: Optional[Callable[[FileBrowserItem], None]] = None):
        """
        Select and center the view on the given item.

        Args:
            item (:obj:`FileBrowserItem`): the item to set the new selection to.
            callback (Callable): optional callback to call after setting the selection. Function signature:
                void(item: :obj:`FileBrowserItem`)
        """
        if not self._visible or not item:
            return
        self.selections = [item]

        # OM-70154: add the ability to center the selected item in file browser grid view
        # calculate the scroll ratio by item index
        items = self.model.get_item_children(None)
        # This should not happen, but add it here as a fail-safe
        if item not in items:
            carb.log_warn(f"Failed to select and center item [ {item.path} ] in file browser grid view.")
            return
        item_index = items.index(item)
        scroll_ratio = float((item_index + 1) / len(items))
        asyncio.ensure_future(
            self._delegate.center_selection_async(
                item, scroll_frame=self._widget, scroll_ratio=scroll_ratio, refresh_interval=3, callback=callback))

    def _on_selection_changed(self, selections: List[FileBrowserItem]):
        if not self._allow_multi_selection:
            if selections:
                selections = selections[-1:]
                self._widget.selection = selections
        if self._selection_changed_fn:
            self._selection_changed_fn(selections)

    def _on_item_changed(self, model, _):
        self.refresh_ui()

    def _on_model_changed(self, model):
        """Called by super when the model is changed"""
        self._throttled_refresh_ui(
            item=None,
            callback=lambda _: self.build_ui(),
            throttle_frames=2)

    def scroll_top(self):
        """Scroll the widget to top"""
        # Scroll to top upon refresh
        self._widget.scroll_y = 0.0

    def destroy(self):
        """Destructor."""
        super().destroy()
        if self._delegate:
            self._delegate.destroy()
            self._delegate = None
        if self._widget:
            self._widget.destroy()
            self._widget = None
        self._style = None
        self._selection_changed_fn = None


class FileBrowserGridViewDelegate:
    """
    The delegate that manages building browser items under the model as widgets inside the grid view.

    Args:
        widget (:obj: `ui.Frame`): The frame for the delegate to build widgets under.
        theme (str): The theme name to use.

    Keyword Args:
        mouse_pressed_fn (Callable): Function called on mouse press. Function signature:
            void mouse_pressed_fn(button: int, key_mode: int, item: :obj:`FileBrowserItem`, x: float=0, y: float=0)
        mouse_double_clicked_fn (Callable): Function called on mouse double click. Function signature:
            void mouse_double_clicked_fn(button: int, key_mode: int, item: :obj:`FileBrowserItem`, x: float=0, y: float=0)
        selection_changed_fn (Callable): Function called when selection changed. Function signature:
            void selection_changed_fn(selections: list[:obj:`FileBrowserItem`])
        drop_fn (Callable): Function called to handle drag-n-drops. Function signature:
            void drop_fn(dst_item: :obj:`FileBrowserItem`, src_path: str)
        thumbnail_provider (Callable): This callback returns the path to the item's thumbnail. If not specified,
            then a default thumbnail is used. Signature: str thumbnail_provider(item: :obj:`FileBrowserItem`).
        badges_provider (Callable): This callback provides the list of badges to layer atop the thumbnail
            in the grid view. Callback signature: List[str] badges_provider(item: :obj:`FileBrowserItem`)
        treeview_identifier (str): widget identifier for treeview, only used by tests.
        testing (bool): When enabled, forces items to immediately be built and made available.
    """
    def __init__(self, widget: ui.Frame, theme: str, **kwargs):
        self._widget: ui.Frame = widget
        self._grid: ui.VGrid = None
        self._cards: Dict[str, FileBrowserItemCard] = {}
        self._card_paths: List[str] = []
        self._custom_thumbnails: Dict[str, str] = {}
        self._selections = []
        self._pending_selections = []

        self._style = UI_STYLES[theme]
        self._tooltip = kwargs.get("tooltip", False)
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)
        self._selection_changed_fn = kwargs.get("selection_changed_fn", None)
        self._drop_fn = kwargs.get("drop_fn", None)
        self._thumbnail_provider = kwargs.get("thumbnail_provider", None)
        self._badges_provider = kwargs.get("badges_provider", None)
        self._treeview_identifier = kwargs.get("treeview_identifier", None)
        self._testing = kwargs.get("testing", False)
        self._card_width = 120
        self._card_height = 120
        self._scale = 1
        self._update_grid_future = None
        self._thumbnails_generated_subscription = None
        self._was_dragging = False

        # Monitor for new thumbnails being generated
        self._thumbnails_generated_subscription = eventdispatcher.get_eventdispatcher().observe_event(
            observer_name="omni.kit.widget.filebrowser.grid_view",
            event_name=THUMBNAILS_GENERATED_GLOBAL_EVENT,
            on_event=self.update_cards_on_thumbnails_generated
        )

    @property
    def scale(self) -> float:
        """
        Get the scale of items.
        """
        return self._scale

    @scale.setter
    def scale(self, scale: float):
        self._scale = scale

    @property
    def selections(self) -> List[FileBrowserItem]:
        """
        Get the current selection.
        """
        return [card.item for card in self._selections]

    @selections.setter
    def selections(self, selections: List[FileBrowserItem]):
        self._pending_selections = []
        if self._cards:
            # grid been build, set selection
            cards = [self._cards[item.path] for item in selections if item.path in self._cards]
            self.clear_selections()
            self.extend_selections(cards)
        else:
            # grid has not been build yet, set pending_selection
            self._pending_selections = selections

    def build_grid(self, model: FileBrowserModel):
        """
        Build browser items under the model.

        Args:
            model (:obj:`FileBrowserModel`): Model containing items to build.
        """
        self.clear_selections()
        for _, card in self._cards.items():
            card.destroy()
        self._cards.clear()
        self._card_paths.clear()

        with self._widget:
            with ui.ZStack():
                with ui.VStack():
                    if self._grid:
                        self._grid = None
                    self._grid = ui.VGrid(
                        column_width=self._scale * self._card_width,
                        row_height=self._scale * self._card_height + 20,
                        mouse_pressed_fn=partial(self._on_mouse_pressed, model, None),
                        mouse_double_clicked_fn=partial(self._on_mouse_double_clicked, None),
                        style_type_name_override="GridView.Grid",
                        content_clipping=True,
                    )
                    if self._treeview_identifier:
                        self._grid.identifier = self._treeview_identifier
                    ui.Spacer(height=30)

                # OM-70157: Since we cannot clip the mouse event for the button in Zoombar for the VGrid, we have to add a invisibleButton here, whose clicked_fn
                #  will not be triggered if the ZoomBar switch layout button is on top of it; this way it will not clear out the selections when the user click
                #  on the layout switch button when it is on top of the VGrid.
                def grid_clicked(*args, **kwargs):
                    self._on_mouse_released(model, None, None, None, 0, 0)
                ui.InvisibleButton(clicked_fn=grid_clicked)

    def update_grid(self, model: FileBrowserModel):
        """
        Generate a grid of cards and renders them with custom thumbnails.

        Args:
            model (:obj:`FileBrowserModel`): Model containing items to update.
        """
        if not self._grid:
            return

        if model:
            children = model.get_item_children(None)
        else:
            return

        # make sure the grid not rebuild more than once
        rebuilt_grid = False

        for path in self._cards:
            # If items got deleted then re-build the grid
            if path not in [c.path for c in children]:
                self.build_grid(model)
                rebuilt_grid = True
                break

            # update card style if path in cut clipboard
            if is_path_cut(path):
                self._cards[path].apply_cut_style()
            else:
                self._cards[path].remove_cut_style()

        for item in children:
            # Add cards for any new children
            if item.item_changed :
                item.item_changed  = False
                if not rebuilt_grid:
                    self.build_grid(model)
                    rebuilt_grid = True

        with self._grid:
            for item in children:
                # Add cards for any new children
                # OM-91073: check paths to prevent build card more than once in sometimes
                # not use the self._cards because it not create immediately in frame's build_fn
                # so we need store and check the card path directly
                if item.path in self._card_paths:
                    continue

                def __build_card(file_item):
                    self._cards[file_item.path] = self.build_card(model, file_item)

                self._card_paths.append(item.path)
                if self._testing:
                    # In testing mode, forces cards to immediately be built and made available
                    with ui.Frame():
                        self._cards[item.path] = self.build_card(model, item)
                else:
                    # OM-63433: Use content_clipping to speed up item display in file picker
                    ui.Frame(content_clipping=True, build_fn=lambda i=item: __build_card(i))

        async def refresh_thumbnails(model: FileBrowserModel):
            """
            Get custom thumbnails for parent folder and synchronously render them if they exist.

            Args:
                model (:obj:`FileBrowserModel`): Model to get thumbnails in the current directory.
            """
            if model and model.root:
                self._custom_thumbnails = await model.root.get_custom_thumbnails_for_folder_async()
            try:
                await self.refresh_thumbnails_async(list(self._cards))
            except asyncio.CancelledError:
                return

            # selections was set before cards created, update now
            if self._pending_selections:
                cards = [self._cards[item.path] for item in self._pending_selections if item.path in self._cards]
                self._pending_selections = []
                self.clear_selections()
                self.extend_selections(cards)

        # Store away future so that it can be cancelled, e.g. when switching directories
        if self._update_grid_future and not self._update_grid_future.done():
            self._update_grid_future.cancel()
        self._update_grid_future = asyncio.ensure_future(refresh_thumbnails(model))

    def update_cards_on_thumbnails_generated(self, event: eventdispatcher.Event):
        """
        When new thumbnails are generated, re-renders associated cards.

        Args:
            events ( :obj:`IEvent`): event containing the thumbnail URLs to update.
        """
        urls = event["paths"]

        async def refresh_thumbnails(urls: str):
            # Get custom thumbnails for given urls. Don't try to generate (again) if not found.
            self._custom_thumbnails.update(await find_thumbnails_for_files_async(urls, generate_missing=False))
            try:
                await self.refresh_thumbnails_async(urls)
            except asyncio.CancelledError:
                return

        refresh_urls = [url for url in urls if url in self._cards]
        if refresh_urls:
            # Execute and forget
            asyncio.ensure_future(refresh_thumbnails(refresh_urls))

    def build_card(self, model: FileBrowserModel, item: FileBrowserItem) -> FileBrowserItemCard:
        """
        Create a widget per item.

        Args:
            model (:obj:`FileBrowserModel`): model to build the item with.
            item (:obj:`FileBrowserItem`): the item to build the widget.
        """
        if not item:
            return

        if isinstance(item, FileBrowserUdimItem):
            custom_thumbnail = self._custom_thumbnails.get(item.repr_path)
        else:
            custom_thumbnail = self._custom_thumbnails.get(item.path)

        card = FileBrowserItemCard(
            item,
            width=self._scale * self._card_width,
            height=self._scale * self._card_height,
            mouse_pressed_fn=partial(self._on_mouse_pressed, model),
            mouse_released_fn=partial(self._on_mouse_released, model),
            mouse_double_clicked_fn=self._on_mouse_double_clicked,
            drag_fn=self._on_drag,
            drop_fn=self._drop_fn,
            get_thumbnail_fn=self._thumbnail_provider,
            get_badges_fn=self._badges_provider,
            custom_thumbnail=custom_thumbnail,
            timeout=model._timeout if model else 10.0,
        )

        return card

    async def refresh_thumbnails_async(self, urls: str):
        """
        Re-generate the thumbnails with given URLs.

        Args:
            urls (List[str]): thumbnail URLs to update.
        """
        if not self._custom_thumbnails:
            return
        tasks = []
        for url in urls:
            card = self._cards.get(url, None)
            item = card.item
            if isinstance(item, FileBrowserUdimItem):
                custom_thumbnail = self._custom_thumbnails.get(item.repr_path)
            else:
                custom_thumbnail = self._custom_thumbnails.get(item.path)

            if card and custom_thumbnail:
                tasks.append(card.refresh_thumbnail_async(custom_thumbnail))
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                carb.log_error(f"Failed to refresh thumbnails: {e}")
            except asyncio.CancelledError:
                return

    def _on_mouse_pressed(self, model: FileBrowserModel, card: FileBrowserItemCard, x, y, b, key_mod):
        if self._mouse_pressed_fn:
            self._mouse_pressed_fn(b, key_mod, card.item if card else None, x=x, y=y)

    def _on_mouse_released(self, model: FileBrowserModel, card: FileBrowserItemCard, x, y, b, key_mod):
        # Don't cancel selections
        # FIXME: mouse release event will be triggered for both card and grid. It
        # needs to check card to make sure mouse release event from grid will not influence selections.
        if self._was_dragging:
            if card:
                self._was_dragging = False

            return

        if b == 0:
            # Update selection list on left mouse clicks
            if key_mod & KEYBOARD_MODIFIER_FLAG_CONTROL:
                if card in self._selections:
                    self.remove_selection(card)
                else:
                    self.add_selection(card)
            elif key_mod & KEYBOARD_MODIFIER_FLAG_SHIFT:
                if not self._selections:
                    self.add_selection(card)
                elif card:
                    last_selection = self._selections[-1].item
                    current_selection = card.item
                    children = model.get_item_children(None)
                    # Note: Search items may re-generate frame to frame, so find by path rather than by object ref
                    last_selection_index = next((i for i, item in enumerate(children) if item.path == last_selection.path), -1)
                    current_selection_index = next((i for i, item in enumerate(children) if item.path == current_selection.path), -1)
                    if last_selection_index >= 0 and current_selection_index >=0:
                        first_index = min(last_selection_index, current_selection_index)
                        last_index = max(last_selection_index, current_selection_index)
                        self.clear_selections()
                        selection_indices = range(first_index, last_index+1)
                        # OM-72965: only add selection in reverse order if current selection is after last selection, so
                        #  that the last element in selection remains the oldest (similar to file explorer)
                        if current_selection_index > last_selection_index:
                            selection_indices = reversed(selection_indices)
                        for i in selection_indices:
                            card = self._cards.get(children[i].path)
                            self.add_selection(card)
            else:
                self.clear_selections()
                self.add_selection(card)

        if self._selection_changed_fn:
            self._selection_changed_fn(self.selections)

    def _on_mouse_double_clicked(self, card: FileBrowserItemCard, x, y, b, key_mod):
        if self._mouse_double_clicked_fn:
            self._mouse_double_clicked_fn(b, key_mod, card.item if card else None, x=x, y=y)

    def _on_drag(self, card: FileBrowserItemCard, thumbnail: str):
        self._was_dragging = True
        result: List[str] = []
        if card not in self._selections:
            return card.on_drag()

        with ui.VStack():
            for card in self._selections:
                result.append(card.on_drag())
        return "\n".join(result)

    def clear_selections(self):
        """ Clear current selection. """
        for selection in self._selections:
            selection.selected = False
        self._selections.clear()

    def extend_selections(self, cards: List[FileBrowserItemCard]):
        """
        Extend current selection.

        Args:
            cards (List[:obj:`FileBrowserItemCard`]): List of item widgets to extend.
        """
        for card in cards:
            self.add_selection(card)

    def add_selection(self, card: FileBrowserItemCard):
        """
        Add a new card to selection.

        Args:
            card (:obj:`FileBrowserItemCard`): Item widget to add.
        """
        if card and card not in self._selections:
            card.selected = True
            self._selections.append(card)

    def remove_selection(self, card: FileBrowserItemCard):
        """
        Remove a new card from the selection.

        Args:
            card (:obj:`FileBrowserItemCard`): Item widget to remove.
        """
        if card and card in self._selections:
            card.selected = False
            self._selections.remove(card)

    async def center_selection_async(
        self,
        selection : FileBrowserItem,
        scroll_frame: Optional[ui.Frame]=None, scroll_ratio=0.0,
        refresh_interval=2,
        callback: Optional[Callable[[FileBrowserItem], None]] = None
    ):
        """
        Center the given item and add it to the selection.

        Args:
            selection (:obj:`FileBrowserItem`): Item to center on.
            scroll_frame (:obj:`ui.Frame`): Optional argument frame to scroll to the item's new position.
            scroll_ratio (float): Optional argument ratio to scroll to the item's new position using item index ratio.
        """
        # OM-70154: add the ability to center the selected item in file browser grid view
        async def _wait_for_ui_build(refresh_interval=refresh_interval):
            for _ in range(refresh_interval):
                await omni.kit.app.get_app().next_update_async()

        await _wait_for_ui_build()
        cards = list(self._cards.values())
        if not cards:
            return
        card_height = cards[0]._widget.computed_content_height
        card = self._cards.get(selection.path)
        if not scroll_frame and not card:
            return

        # card is not built yet, need to scroll to the y position in the scrolling frame to trigger card build
        if not card:
            # scroll one line to trigger calculation for scroll_y_max
            scroll_frame.scroll_y = card_height
            await _wait_for_ui_build()

            # scroll to the card by using the item index ratio
            if scroll_ratio > 0:
                scroll_frame.scroll_y = scroll_ratio * scroll_frame.scroll_y_max - card_height * 0.5
                await _wait_for_ui_build()
                card = self._cards.get(selection.path)

        if card:
            card._widget.scroll_here()
            self.add_selection(card)

        if callback:
            callback(selection)

    def destroy(self):
        """ Destructor. """
        self._grid = None
        self._cards.clear()
        self._card_paths.clear()
        self._custom_thumbnails.clear()
        self._selections.clear()
        if self._update_grid_future and not self._update_grid_future.done():
            self._update_grid_future.cancel()
        self._update_grid_future = None
        self._thumbnails_generated_subscription = None

        self._style = None
        self._mouse_pressed_fn = None
        self._mouse_double_clicked_fn = None
        self._selection_changed_fn = None
        self._drop_fn = None
        self._thumbnail_provider = None
        self._badges_provider = None
