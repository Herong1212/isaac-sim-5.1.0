import asyncio
from functools import partial

import omni.ui as ui
from omni.kit.widget.filebrowser import find_thumbnails_for_files_async
from omni.kit.widget.filebrowser.thumbnails import _find_thumbnail_async


class WarehouseTileCardWidget:
    def __init__(self, **kwargs):
        size = kwargs.get("size", 64)
        self.size = size
        self.thumb = None
        self._frame = ui.Frame(**kwargs, width=size, height=size)
        self.name = kwargs.get("name", "")
        self._checked = kwargs.get("selected", False)
        self._selected = kwargs.get("selected", False)
        self.usd_asset = kwargs.get("usd_asset", "")
        self.mouse_pressed_fn = kwargs.get("mouse_pressed_fn", None)
        self.thumb_task = asyncio.ensure_future(self.get_thumb_async())
        self.thumb_task.add_done_callback(self.thumb_callback)

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        self._checked = value
        self.build_widget()

    @property
    def selected(self) -> bool:
        # print(self._selected)
        return self._selected

    @selected.setter
    def selected(self, value: bool):
        if self._frame:
            self._frame.selected = value
            self._selected = value
            self.build_widget()

    def thumb_callback(self, task):
        self.build_widget()

    async def get_thumb_async(self):
        url, thumb = await _find_thumbnail_async(self.usd_asset)
        if self.usd_asset == url:
            self.thumb = thumb
        return None

    def get_thumb(self):
        if self.thumb:
            return self.thumb
        return ""

    def _on_mouse_pressed(self, *args):
        self.selected = True
        if self.mouse_pressed_fn:
            self.mouse_pressed_fn(self, args)

    def make_tooltip(self):
        ui.ImageWithProvider(self.get_thumb(), height=256, width=256, style={"border_radius": 10, "margin": 6})

    def build_widget(self):
        with self._frame:
            with ui.ZStack():
                self._rect = ui.Rectangle(
                    mouse_pressed_fn=partial(self._on_mouse_pressed),
                    style={
                        "margin_width": 3,
                        "margin_height": 3,
                        "background_color": 0x99AAAAAA,
                        "border_radius": 10,
                        "border_color": 0x00222222,
                        "border_width": 2,
                        ":hovered": {"background_color": 0x6600B976},
                        ":selected": {"background_color": 0xFF00B976},
                    },
                    tooltip_fn=self.make_tooltip,
                )
                ui.ImageWithProvider(
                    self.get_thumb(), height=self.size, width=self.size, style={"border_radius": 10, "margin": 6}
                )
