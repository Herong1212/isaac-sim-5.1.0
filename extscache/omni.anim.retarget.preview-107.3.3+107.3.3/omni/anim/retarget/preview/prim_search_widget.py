import asyncio
import re
from functools import partial
from typing import *

import carb
import omni.kit.app
import omni.ui as ui
from omni.ui import color as cl
from pxr import Usd, UsdGeom, UsdSkel

from omni.kit.helper.file_utils.asset_types import get_icon


__all__ = ["PrimSearchWidget"]


WIDGET_HEIGHT = 36
SEARCH_WIDGET_HEIGHT = WIDGET_HEIGHT * 5
SEARCH_ITEM_HEIGHT = 24
SEARCH_FIELD_HEIGHT = 16


def icon(name:str) -> str:
    icon_path = f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/icons"
    return f"{icon_path}/{name}.svg"


SKELANIM_ICON = get_icon("a.skelanim.usd")
SKEL_ICON = get_icon("a.skel.usd")
FILE_ICON = get_icon("a.usd")



# Function to find all mesh prim paths in the scene
def find_skel_prims(stage):
    all_roots = [prim.GetPath().pathString for prim in stage.Traverse() if prim.IsA(UsdSkel.Root) and not prim.GetTypeName() == "BehaviorMotionLibrary"]
    return all_roots

def find_anim_prims(stage):
    all_roots = [prim.GetPath().pathString for prim in stage.Traverse() if prim.IsA(UsdSkel.Animation)]
    return all_roots


class PrimSearchItem:
    background_style = {
        "background_color": 0xFF118811,
    }

    brightfont_style = {
        "color": cl.white,
        # "background_color": 0xFF77FF77,
    }

    dimfont_style = {
        "color": cl.grey,
    }

    def __init__(self, name:str, index:int):
        self._name  = name
        self._index = index
        self._frame = ui.Frame(margin=0, padding=0)
        self._frame.set_build_fn(self.build_fn)
        self._hovered = False

    def build_fn(self):
        with ui.HStack(margin=0, padding=0, height=SEARCH_ITEM_HEIGHT):
            ui.Spacer(width=6)
            with ui.ZStack():
                self._rect = ui.Rectangle(style=PrimSearchItem.background_style if self._hovered else {},
                                        mouse_hovered_fn=self._item_mouse_hover)
                self._label = ui.Label(self._name,
                                        style=PrimSearchItem.brightfont_style if self._hovered else {})
            ui.Spacer(width=6)

    def _item_mouse_hover(self, hovered:bool):
        if hovered == self._hovered:
            return
        self._hovered = hovered
        self._rect.style = PrimSearchItem.background_style if self._hovered else {}
        self._label = PrimSearchItem.brightfont_style if self._hovered else {}


class PrimSearchWidget:
    remove_button_style = {
        "Button": {
            "background_color": ui.color.transparent,
        },
        "Button.Image": {
            "image_url": icon("remove"),
        },
        "Button.Image:disabled": {
            "image_url": "",
        },
        "Button.Image:hovered": {
            "image_url": icon("remove-hovered")
        },
        "Button:hovered": {
            "background_color": ui.color.transparent,
        },
        "Button:pressed": {
            "background_color": ui.color.transparent,
            "border_color": cl("#005499"),
            "border_width": 1.0
        }
    }

    def __init__(self, data:List[str]=[], value:str="", opens_up:bool=False, full_prim_name:bool=False, enabled=True, icon:str=SKEL_ICON):
        self._frame = ui.Frame(height=WIDGET_HEIGHT)
        self._frame.set_build_fn(self.build_fn)
        self._search_window = None
        self._opens_up = opens_up
        self._data:List[Usd.Prim] = []
        self.set_data(data)
        self._enabled = enabled
        self._full_prim_name = full_prim_name
        self._icon_path = icon

        self._value = None
        self.set_value(value, run_callbacks=False)
        self._index = self._data.index(value) if value in self._data else -1
        self._main_label = None
        self._search_filter_text = ""

        self._prim_search_items = None

        self._changed_callbacks = []

    def __del__(self):
        self.destroy()

    def destroy(self):
        self._changed_callbacks = []
        self._prim_search_items = None
        if self._search_window:
            self._search_window.destroy()
        self._search_window = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value:bool):
        self._enabled = value
        self._frame.enabled = value
        self._main_label.style = PrimSearchItem.brightfont_style if value else PrimSearchItem.dimfont_style

    def add_changed_callback(self, callback):
        if not callback in self._changed_callbacks:
            self._changed_callbacks.append(callback)

    def remove_changed_callback(self, callback):
        self._changed_callbacks = [x for x in self._changed_callbacks if not x is callback]

    def set_data(self, data:List[Usd.Prim]):
        self._data = data

    def _close_search_window(self):
        async def close_window():
            await omni.kit.app.get_app().next_update_async()
            if self._search_window:
                self._search_window.visible = False

        asyncio.ensure_future(close_window())

    def get_value(self) -> str:
        return self._value

    def set_value(self, text:str, run_callbacks:bool=True):
        value = text.strip()
        item = None
        if value == "":
            self._value = ""
        else:
            for index, prim in enumerate(self._data):
                if not prim:
                    continue
                if value == prim.GetName() or value == prim.GetPath():
                    self._value = str(prim.GetPath()) if self._full_prim_name else str(prim.GetName())
                    item = prim
                    break

        if run_callbacks:
            for callback in self._changed_callbacks:
                path = item.GetPrimPath() if item else ""
                callback(path)

        if not self._full_prim_name and self._value.count("/"):
            self._value = self._value.rpartition("/")[-1]

        self._close_search_window()
        self._frame.rebuild()

    def set_search_filter_text(self, text:str):
        self._search_filter_text = text.strip().lower()
        self._search_window_scrolling_frame.rebuild()

    def show_search_window(self, *args):
        if self._search_window:
            self._search_window.visible = False
            self._search_window.destroy()
            self._search_window = None

        if not self._enabled:
            return

        self._search_window = ui.Window(title="PrimSearchWidget_SearchWWindow",
                                        flags=ui.WINDOW_FLAGS_POPUP
                                            | ui.WINDOW_FLAGS_NO_TITLE_BAR
                                            | ui.WINDOW_FLAGS_NO_RESIZE
                                            | ui.WINDOW_FLAGS_NO_MOVE,
                                        padding_x=0,
                                        padding_y=0,
                                        width=self._frame.computed_width - 40 + 1,
                                        height=SEARCH_WIDGET_HEIGHT,
                                        visible=False)

        self._search_window.frame.set_build_fn(self._search_window_build_fn)
        self._search_window.visible = True

    def _search_item_mouse_pressed(self, index:int, *args):
        self.set_value(str(self._data[index].GetPath()))

    def _search_window_scroller_hovered_fn(self, index:int, *args):
        self._search_window_scrolling_frame.rebuild()

    def _search_window_scroller_build_fn(self):
        self._prim_search_items = []
        # remember: the scrolling frame needs a single child layout
        self._search_window_scroller_main_vstack = ui.VStack(margin=0, padding=0)
        self._search_window_scroller_main_vstack.set_mouse_hovered_fn(self._search_window_scroller_hovered_fn)
        with self._search_window_scroller_main_vstack:
            for index, item in enumerate(self._data):
                item_name = str(item.GetPath()) if self._full_prim_name else str(item.GetName())
                if len(self._search_filter_text):
                    if not self._search_filter_text in item_name.lower():
                        continue
                prim_item = PrimSearchItem(item_name, index)
                prim_item._frame.set_mouse_pressed_fn(partial(self._search_item_mouse_pressed, index))
                self._prim_search_items.append(prim_item)

        scroller_internal_size = SEARCH_ITEM_HEIGHT * len(self._prim_search_items)
        self._search_window_scroller_main_vstack.height = ui.Length(scroller_internal_size)

    def _search_edit_value_changed_fn(self, model:ui.SimpleStringModel):
        carb.log_warn(f"Search Edit Value Changed: '{model.get_value_as_string()}'")
        self.set_search_filter_text(model.get_value_as_string());

    def _search_edit_end_fn(self, model:ui.SimpleStringModel):
        carb.log_warn(f"Search Edit End: {model}")
        self.set_search_filter_text(model.get_value_as_string());

    def _search_window_build_fn(self):
        with ui.VStack(margin=0, padding=0, name="vs_search_window", height=SEARCH_FIELD_HEIGHT, style={"background_color": 0xFF000000}):
            with ui.HStack(margin=0, padding=0):
                with ui.ZStack(margin=0, padding=0, width=SEARCH_FIELD_HEIGHT, height=SEARCH_FIELD_HEIGHT):
                    ui.Rectangle(margin=0, padding=0, style={"background_color": 0xFF000000})
                    ui.Image(icon("search"), width=SEARCH_FIELD_HEIGHT, height=SEARCH_FIELD_HEIGHT)

                with ui.ZStack(margin=0, padding=0, height=SEARCH_FIELD_HEIGHT):
                    ui.Rectangle(margin=0, padding=0, style={"background_color": 0xFF000000})
                    with ui.HStack(margin=0, padding=0):
                        ui.Spacer(width=6)
                        self._search_field = ui.StringField(focused=True, style={"font_size": SEARCH_FIELD_HEIGHT})
                        self._search_field.model.set_value(self._search_filter_text)
                        self._search_field.model.add_value_changed_fn(self._search_edit_value_changed_fn)
                        self._search_field.model.add_end_edit_fn(self._search_edit_end_fn)
                        ui.Spacer(width=6)

            self._search_window_scrolling_frame = ui.ScrollingFrame(
                height=SEARCH_WIDGET_HEIGHT - WIDGET_HEIGHT,
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            )

            self._search_window_scrolling_frame.set_build_fn(self._search_window_scroller_build_fn)

            if self._opens_up:
                screen_position_y = self._frame.screen_position_y - SEARCH_WIDGET_HEIGHT - 2
            else:
                screen_position_y = self._frame.screen_position_y + self._frame.computed_height + 2

        self._search_window.setPosition(self._frame.screen_position_x + 40 - 1, screen_position_y)
        self._search_window.set_top_modal()

    def _remove_clicked_fn(self, *args):
        self.set_value("")

    def build_fn(self):
        with self._frame:
            black_style = {"background_color": 0xFF000000}

            with ui.ZStack(margin=0, height=WIDGET_HEIGHT, padding=0, name="main_zstack"):
                ui.Rectangle(margin=0, padding=0, style=black_style, name="main_color")

                with ui.HStack(margin=0, padding=0):
                    with ui.ZStack(margin=0, padding=0, width=36, height=WIDGET_HEIGHT):
                        ui.Rectangle(margin=0, padding=0, style=black_style)
                        ui.Image(self._icon_path, style={"alignment": ui.Alignment.H_CENTER}, width=36, height=WIDGET_HEIGHT)

                    ui.Spacer(width=4)

                    with ui.ZStack(margin=0, padding=0, height=WIDGET_HEIGHT):
                        ui.Rectangle(margin=0, padding=0, style=black_style)
                        with ui.HStack(margin=0, padding=0):
                            ui.Spacer(width=6)
                            self._main_label = ui.Label(self._value if self.enabled else "",
                                                        style={"background_color": 0xFFcccccc},
                                                        mouse_pressed_fn=self.show_search_window,
                                                        word_wrap=True)
                            ui.Spacer(width=6)

                    with ui.ZStack(margin=0, padding=0, width=WIDGET_HEIGHT, height=WIDGET_HEIGHT):
                        ui.Rectangle(margin=0, padding=0, style=black_style)
                        if not self._main_label.text == "":
                            with ui.VStack(margin=0, padding=0):
                                ui.Spacer(height=6)
                                with ui.HStack(margin=0, padding=0):
                                    # ui.Spacer(width=2)
                                    ui.Button(width=24, height=24, style=PrimSearchWidget.remove_button_style,
                                              clicked_fn=self._remove_clicked_fn)
