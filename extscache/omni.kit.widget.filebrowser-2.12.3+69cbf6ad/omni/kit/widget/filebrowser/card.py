# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""
Base Model classes for the filebrowser entity.
"""
__all__ = ["FileBrowserItemCard"]
import os
import carb
import omni.client

from typing import Optional
from functools import partial
from omni import ui
from .clipboard import is_path_cut
from .model import FileBrowserItem
from .style import UI_STYLES, THUMBNAIL_PATH, ICON_PATH
from . import ALERT_WARNING, ALERT_ERROR


class FileBrowserItemCard(ui.Widget):
    """
    Widget used by FileBrowserGridView to build the browser item.

    Args:
        item (:obj:`FileBrowserItem`): Item to build the widget with.

    Keyword Args:
        width (int): width of the widget, defaults to 60.
        height (int): height of the widget, defaults to 60.
        mouse_pressed_fn (Callable): Function called on mouse press. Function signature:
            void mouse_pressed_fn(pane: int, button: int, key_mode: int, item: :obj:`FileBrowserItem`)
        mouse_double_clicked_fn (Callable): Function called on mouse double click. Function signature:
            void mouse_double_clicked_fn(pane: int, button: int, key_mode: int, item: :obj:`FileBrowserItem`)
        mouse_released_fn (Callable): Function called on mouse release. Function signature:
            void mouse_pressed_fn(pane: int, button: int, key_mode: int, item: :obj:`FileBrowserItem`)
        drop_fn (Callable): Function called to handle drag-n-drops. Function signature:
            void drop_fn(dst_item: :obj:`FileBrowserItem`, event: :obj:`ui.WidgetMouseDropEvent`)
        get_thumbnail_fn (Callable): Function called to get the thumbnail from the item. Function signature:
            str badges_provider(item: :obj:`FileBrowserItem`)
        get_badges_fn (Callable): Function called to get badges from the item. Function signature:
            List[str] badges_provider(item: :obj:`FileBrowserItem`)
        custom_thumbnail (str): Thumbnail to override the default one.
        drag_fn (Callable): Function called to handle dragging thumbnails. Function signature:
            void drag_fn(thumbnail: str)

    """
    def __init__(self, item: FileBrowserItem, **kwargs):
        import carb.settings

        self._item = item
        self._widget = None
        self._rectangle = None
        self._image_frame = None
        self._image_buffer = None
        self._image_buffer_thumbnail = None
        self._overlay_frame = None
        self._back_buffer = None
        self._back_buffer_thumbnail = None
        self._label = None
        self._selected = False

        self._theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"
        use_default_style = carb.settings.get_settings().get_as_string("/persistent/app/window/useDefaultStyle") or False
        if use_default_style:
            self._style = {}
        else:
            self._style = kwargs.get("style", UI_STYLES[self._theme])
        self._width = kwargs.get("width", 60)
        self._height = kwargs.get("height", 60)
        self._mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self._mouse_released_fn = kwargs.get("mouse_released_fn", None)
        self._mouse_double_clicked_fn = kwargs.get("mouse_double_clicked_fn", None)
        self._drop_fn = kwargs.get("drop_fn", None)
        self._get_thumbnail_fn = kwargs.get("get_thumbnail_fn", None)
        self._get_badges_fn = kwargs.get("get_badges_fn", None)
        self._custom_thumbnail = kwargs.get("custom_thumbnail", None)

        super().__init__()

        self._drag_fn = kwargs.get("drag_fn", None)
        if self._drag_fn:
            self._drag_fn = partial(self._drag_fn, self)
        else:
            # If nothing is set, use the default one
            self._drag_fn = self.on_drag

        self._tooltip = f"Path:  {item.path}\n"
        self._tooltip += f"Size:  {FileBrowserItem.size_as_string(item.fields.size)}\n"
        self._tooltip += f"Modified:  {FileBrowserItem.datetime_as_string(item.fields.date)}"

        self._cached_thumbnail: Optional[str] = None

        self._build_ui()

    @property
    def item(self) -> FileBrowserItem:
        """ Return the item associated with the widget. """
        return self._item

    @property
    def selected(self) -> bool:
        """ Return True when selected. """
        return self._selected

    @selected.setter
    def selected(self, value: bool):
        """ Set selected or not. """
        self._rectangle.selected = value
        self._label.checked = value
        self._selected = value

    def apply_cut_style(self):
        """ Apply cut style to the widget. """
        for widget in (self._back_buffer_thumbnail, self._image_buffer_thumbnail, self._label):
            if widget:
                widget.name = "Cut"

    def remove_cut_style(self):
        """ Remove cut style from the widget. """
        for widget in (self._back_buffer_thumbnail, self._image_buffer_thumbnail, self._label):
            if widget:
                widget.name = ""

    def _build_ui(self):
        if not self._item:
            return

        def on_mouse_pressed(card: "FileBrowserItemCard", *args):
            if self._mouse_pressed_fn:
                self._mouse_pressed_fn(card, *args)

        def on_mouse_released(card: "FileBrowserItemCard", *args):
            if self._mouse_released_fn:
                self._mouse_released_fn(card, *args)

        def on_mouse_double_clicked(card: "FileBrowserItemCard", *args):
            if self._mouse_double_clicked_fn:
                self._mouse_double_clicked_fn(card, *args)

        def mouse_hovered_fn(hovered: bool):
            self._label.selected = hovered

        self._widget = ui.ZStack(width=0, height=0, style=self._style)
        with self._widget:
            self._rectangle = ui.Rectangle(
                mouse_pressed_fn=partial(on_mouse_pressed, self),
                mouse_released_fn=partial(on_mouse_released, self),
                mouse_double_clicked_fn=partial(on_mouse_double_clicked, self),
                style_type_name_override="Card",
                identifier=self._item.name,
            )
            self._rectangle.set_mouse_hovered_fn(mouse_hovered_fn)
            with ui.VStack(spacing=0):
                with ui.ZStack():
                    def is_valid_url(source):
                        for url in source.splitlines():
                            # NOTE: "material::" prefix isn't supported currently as moving materials could
                            #       cause problems as material in new location could fail to compile
                            if url.startswith(("material::")):
                                return False

                            if not omni.client.is_local_url(url) and omni.client.is_valid_url(url):
                                continue

                            if url.startswith(("file:/")):
                                continue

                            # must be a local filepath, use lstat to verify as it will throw an error in not valid
                            try:
                                os.lstat(url)
                            except OSError as exc:
                                return False

                        return True

                    thumbnail = self._custom_thumbnail or self._get_thumbnail(self._item)
                    self._image_frame = ui.Frame(
                        width=self._width,
                        height=self._height,
                        drag_fn=lambda: self.on_drag(thumbnail),
                        accept_drop_fn=lambda url: self._item.is_folder and is_valid_url(url),
                        drop_fn=lambda event: self._on_drop(event),
                    )
                    self._overlay_frame = ui.Frame(
                        width=self._width,
                        height=self._height,
                    )
                    self.draw_thumbnail(self._custom_thumbnail)
                    self.draw_badges()

                with ui.HStack(height=40):
                    # Note: This Placer nudges the label closer to the image. The inherent
                    # margin would otherwise create a less pleasing separation.
                    with ui.Placer(stable_size=True, offset_x=0, offset_y=-8):
                        self._label = ui.Label(
                            self._item.name,
                            style_type_name_override="Card.Label",
                            word_wrap=True,
                            elided_text=True if self._theme == "NvidiaDark" else False,
                            tooltip=self._tooltip,
                        )
                ui.Spacer()
        # add cut style if path is in cut clipboard on build
        if is_path_cut(self._item.path):
            self.apply_cut_style()

    def _get_thumbnail(self, item: FileBrowserItem) -> str:
        thumbnail = None
        if self._get_thumbnail_fn:
            thumbnail = self._get_thumbnail_fn(item)

        if not thumbnail:
            # Set to default thumbnails
            if self._item.is_folder:
                thumbnail = f"{THUMBNAIL_PATH}/folder_256.png"
            else:
                thumbnail = f"{THUMBNAIL_PATH}/file_256.png"

        return thumbnail

    def on_drag(self, thumbnail: Optional[str] = None):
        """
        Default drag handler, create a thumbnail at the given path in the current widget container.

        Args:
            thumbnail (str): thumbnail path.

        Returns:
            The current item path.
        """
        with ui.VStack():
            if not thumbnail and self._cached_thumbnail:
                thumbnail = self._cached_thumbnail
            elif not thumbnail:
                if self._item.is_folder:
                    thumbnail = f"{THUMBNAIL_PATH}/folder_256.png"
                else:
                    thumbnail = f"{THUMBNAIL_PATH}/file_256.png"

            ui.Image(thumbnail, width=32, height=32)
            ui.Label(self._item.path)
        return self._item.path

    def _on_drop(self, event: ui.WidgetMouseDropEvent):
        if self._drop_fn:
            self._drop_fn(self._item, event.mime_data)

    async def _draw_thumbnail_async(self, thumbnail: str):
        self.draw_thumbnail(thumbnail)
        if is_path_cut(self._item.path):
            self.apply_cut_style()

    def draw_thumbnail(self, thumbnail: str):
        """
        Asynchronously redraw thumbnail with the given file.

        Args:
            thumbnail (str): thumbnail path.
        """
        def on_image_progress(frame: ui.Frame, thumbnail_image: ui.Image, progress: float):
            """Called when the image loading progress is changed."""
            if progress != 1.0:
                # We only need to catch the moment when the image is loaded.
                return

            # Hide the icon on the background.
            if frame:
                frame.visible = False

            # Remove the callback to avoid circular references.
            thumbnail_image.set_progress_changed_fn(None)

            if thumbnail:
                self._cached_thumbnail = thumbnail

        with self._image_frame:
            if not self._image_buffer:
                self._image_buffer = ui.ZStack()
                with self._image_buffer:
                    self._back_buffer = ui.Frame()
                    with self._back_buffer:
                        default_thumbnail = self._get_thumbnail(self._item)
                        self._back_buffer_thumbnail = ui.ImageWithProvider(
                            default_thumbnail,
                            fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT,
                            style_type_name_override="Card.Image",
                        )
                        self._image_frame.set_drag_fn(lambda: self._drag_fn(default_thumbnail))


            if not thumbnail:
                return

            with self._image_buffer:
                front_buffer = ui.Frame()
                with front_buffer:
                    # NOTE: Ideally, we could use ui.ImageProvider here for consistency. However, if that
                    # method doesn't allow loading images from "omniverse://".
                    thumbnail_image = ui.Image(
                        thumbnail,
                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                        style_type_name_override="Card.Image",
                    )
                    thumbnail_image.set_progress_changed_fn(partial(on_image_progress, self._back_buffer, thumbnail_image))
                    self._image_buffer_thumbnail = thumbnail_image
                    self._image_frame.set_drag_fn(lambda: self._drag_fn(thumbnail))
                    self._back_buffer = None

    def draw_badges(self):
        """
        Draw badges if get_badgets_fn is provided in the constructor.
        """
        if not self._item or not self._get_badges_fn:
            return

        badges = self._get_badges_fn(self._item)
        if self._item.alert:
            sev, msg = self._item.alert
            if sev == ALERT_WARNING:
                badges.append((f"{ICON_PATH}/{self._theme}/warn.svg", msg))
            elif sev == ALERT_ERROR:
                badges.append((f"{ICON_PATH}/{self._theme}/error.svg", msg))
            else:
                badges.append((f"{ICON_PATH}/{self._theme}/info.svg", msg))

        if not badges:
            return

        size = 14
        margin_width = 6
        margin_height = 8
        shadow_offset = 1

        with self._overlay_frame:
            # First, the shadows
            with ui.ZStack():
                with ui.VStack():
                    ui.Spacer()
                    with ui.HStack(height=size, spacing=2):
                        ui.Spacer()
                        for badge in badges:
                            icon, _ = badge
                            ui.ImageWithProvider(
                                icon,
                                width=size,
                                name="shadow",
                                fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT,
                                style_type_name_override="Card.Badge",
                            )
                        ui.Spacer(width=margin_width - shadow_offset)
                    ui.Spacer(height=margin_height - shadow_offset)
                # Then, the image itself
                with ui.VStack():
                    ui.Spacer()
                    with ui.HStack(height=size, spacing=2):
                        ui.Spacer()
                        for badge in badges:
                            icon, tooltip = badge
                            ui.ImageWithProvider(
                                icon,
                                tooltip=tooltip,
                                width=size,
                                fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT,
                                style_type_name_override="Card.Badge",
                            )
                        ui.Spacer(width=margin_width)
                    ui.Spacer(height=margin_height)

    async def refresh_thumbnail_async(self, thumbnail: str):
        """
        Asynchronously redraw thumbnail with the given file.

        Args:
            thumbnail (str): thumbnail path.
        """
        try:
            await self._draw_thumbnail_async(thumbnail)
        except Exception as exc:
            carb.log_error(f"Failed to redraw thumbnail {exc}")

    def destroy(self):
        """ Destructor """
        self._item = None
        self._label = None
        self._image_frame = None
        self._overlay_frame = None
        self._image_buffer = None
        self._image_buffer_thumbnail = None
        self._back_buffer = None
        self._back_buffer_thumbnail = None
        self._rectangle = None
        self._widget = None
