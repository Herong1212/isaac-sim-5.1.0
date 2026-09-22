# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.anim.navigation.core as nav
import omni.ui as ui
import omni.usd
import omni.kit.window.property
import math

NAVMESH_SESSION_PRIM = "/__omni_nav_mesh_viz_1F21D921"


def length3(v):
    """Calculate float3 vector's length"""
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def scale3(v, f):
    """Scale float3 vector with f"""
    return [v[0] * f, v[1] * f, v[2] * f]


def normalize3(v):
    """Normalize float3 vector"""
    l3 = length3(v)
    if l3 > 0.001:
        return scale3(v, 1 / l3)
    else:
        return [0, 0, 0]


def add3(a, b):
    """Add two float3 vector together"""
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def sub3(a, b):
    """Subtract two float3 vector together"""
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def create_float3_drag_with_labels(x: float, y: float, z: float, labels, comp_count, **kwargs) -> ui.MultiFloatDragField:
    RECT_WIDTH = 13
    SPACING = 4
    with ui.ZStack():
        with ui.HStack():
            if labels:
                ui.Spacer(width=RECT_WIDTH)
                widget_kwargs = {"name": "multivalue", "h_spacing": RECT_WIDTH + SPACING}
            else:
                widget_kwargs = {"name": "multivalue", "h_spacing": 3}

            widget_kwargs.update(kwargs)
            drag_field = ui.MultiFloatDragField(x, y, z, **widget_kwargs)
        with ui.HStack():
            if labels:
                for i in range(comp_count):
                    if i != 0:
                        ui.Spacer(width=SPACING)
                    label = labels[i]
                    with ui.ZStack(width=RECT_WIDTH + 1):
                        ui.Rectangle(name="vector_label", style={"background_color": label[1]})
                        ui.Label(label[0], name="vector_label", alignment=ui.Alignment.CENTER)
                    ui.Spacer()
    return drag_field


def is_supported_navmesh_prim(prim, skip_hidden_prims=True):
    if skip_hidden_prims and prim.GetMetadata('hide_in_stage_window') or prim.GetPath().pathString.startswith(NAVMESH_SESSION_PRIM):
        return False
    iface = nav.acquire_interface()
    return iface.is_supported_navmesh_prim(prim.GetPath().pathString)


def clear_cache():
    inav = nav.acquire_interface()
    inav.clear_cache_dir()


def open_cache_dir():
    inav = nav.acquire_interface()
    cache_dir_path = inav.get_cache_dir()
    import os
    import webbrowser

    if not os.path.exists(cache_dir_path):
        os.makedirs(cache_dir_path, exist_ok=True)

    webbrowser.open(cache_dir_path)


def refresh_property_window():
    selected_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
    omni.usd.get_context().get_selection().clear_selected_prim_paths()
    omni.kit.window.property.get_window()._window.frame.rebuild()
    omni.usd.get_context().get_selection().set_selected_prim_paths(selected_paths, True)


class Prompt:
    def __init__(
        self,
        title,
        text,
        ok_button_text="OK",
        cancel_button_text=None,
        middle_button_text=None,
        ok_button_fn=None,
        cancel_button_fn=None,
        middle_button_fn=None,
        modal=False,
    ):
        self._title = title
        self._text = text
        self._cancel_button_text = cancel_button_text
        self._cancel_button_fn = cancel_button_fn
        self._ok_button_fn = ok_button_fn
        self._ok_button_text = ok_button_text
        self._middle_button_text = middle_button_text
        self._middle_button_fn = middle_button_fn
        self._modal = modal
        self._build_ui()

    def __del__(self):
        self._cancel_button_fn = None
        self._ok_button_fn = None

    def __enter__(self):
        self._window.show()
        return self

    def __exit__(self, type, value, trace):
        self._window.hide()

    def show(self):
        self._window.visible = True

    def hide(self):
        self._window.visible = False

    def is_visible(self):
        return self._window.visible

    def set_text(self, text):
        self._text_label.text = text

    def set_confirm_fn(self, on_ok_button_clicked):
        self._ok_button_fn = on_ok_button_clicked

    def set_cancel_fn(self, on_cancel_button_clicked):
        self._cancel_button_fn = on_cancel_button_clicked

    def set_middle_button_fn(self, on_middle_button_clicked):
        self._middle_button_fn = on_middle_button_clicked

    def _on_ok_button_fn(self):
        self.hide()
        if self._ok_button_fn:
            self._ok_button_fn()

    def _on_cancel_button_fn(self):
        self.hide()
        if self._cancel_button_fn:
            self._cancel_button_fn()

    def _on_middle_button_fn(self):
        self.hide()
        if self._middle_button_fn:
            self._middle_button_fn()

    def _build_ui(self):
        self._window = ui.Window(
            self._title, visible=False, height=0, dockPreference=ui.DockPreference.DISABLED
        )
        self._window.flags = (
            ui.WINDOW_FLAGS_NO_COLLAPSE
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_MOVE
        )

        if self._modal:
            self._window.flags = self._window.flags | ui.WINDOW_FLAGS_MODAL

        with self._window.frame:
            with ui.VStack(height=0):
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer()
                    self._text_label = ui.Label(self._text, word_wrap=True, width=self._window.width - 80, height=0)
                    ui.Spacer()
                ui.Spacer(width=0, height=10)
                with ui.HStack(height=0):
                    ui.Spacer(height=0)
                    if self._ok_button_text:
                        ok_button = ui.Button(self._ok_button_text, width=60, height=0)
                        ok_button.set_clicked_fn(self._on_ok_button_fn)
                    if self._middle_button_text:
                        middle_button = ui.Button(self._middle_button_text, width=60, height=0)
                        middle_button.set_clicked_fn(self._on_middle_button_fn)
                    if self._cancel_button_text:
                        cancel_button = ui.Button(self._cancel_button_text, width=60, height=0)
                        cancel_button.set_clicked_fn(self._on_cancel_button_fn)
                    ui.Spacer(height=0)
                ui.Spacer(width=0, height=10)