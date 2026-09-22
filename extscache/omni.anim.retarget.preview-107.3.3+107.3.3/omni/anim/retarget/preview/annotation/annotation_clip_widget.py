# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import carb
import enum
import omni.kit.context_menu
import omni.ui as ui
from typing import Optional
from .annotation_model import Annotation, AnnotationSet
from .annotation_context_menu import annotation_menu_list


BORDER_RADIUS = 15
DRAG_HANDLER_WIDTH = 5

STYLE_WRITEABLE = {
    "ClipRectangle:hovered": {
        "background_color": 0xFFAA5500,
        "border_color": 0xFFFFFFFF,
        "border_radius": BORDER_RADIUS
    },
    "ClipRectangle:selected": {
        "background_color": 0xFFAA5500,
        "border_color": 0xFFFFFFFF,
        "border_radius": BORDER_RADIUS,
        "border_width": 3
    },
    "ClipRectangle:pressed": {
        "background_color": 0xFFAA5500,
        "border_color": 0xFFFFFFFF,
        "border_radius": BORDER_RADIUS,
    },
    "DragRectangle": {
        "background_color": 0x00AA5500,
        "border_color": 0xFFFFFFFF,
        "border_radius": 0,
        "border_width": 0,
    },
    "DragRectangle:hovered": {
        "background_color": 0xFFFFFFFF,
        "border_color": 0xFFFFFFFF,
        "border_radius": 0,
        "border_width": 0,
    },
}

STYLE_READONLY = {
    "ClipRectangle:hovered": {
        "background_color": 0xFF656565,
        "border_color": 0xFFFFFFFF,
        "border_radius": BORDER_RADIUS
    },
    "ClipRectangle:selected": {
        "background_color": 0xFF656565,
        "border_color": 0xFFFFFFFF,
        "border_radius": BORDER_RADIUS,
        "border_width": 3
    },
    "ClipRectangle:pressed": {
        "background_color": 0xFF656565,
        "border_color": 0xFFFFFFFF,
        "border_radius": BORDER_RADIUS,
    },
    "DragRectangle": {
        "background_color": 0xFF656565,
        "border_color": 0xFFFFFFFF,
        "border_radius": 0,
        "border_width": 0,
    },
    "DragRectangle:hovered": {
        "background_color": 0xFF656565,
        "border_color": 0xFFFFFFFF,
        "border_radius": 0,
        "border_width": 0,
    },
}

BG_STYLE_WRITEABLE = {
    "background_color": 0xFFAA5500, "border_color": 0xFFEE9900, "border_radius": BORDER_RADIUS, "border_width": 1
}

BG_STYLE_READONLY = {
    "background_color": 0xFF656565, "border_color": 0xFFFFFFFF, "border_radius": BORDER_RADIUS, "border_width": 1
}


class WidgetSide(enum.Enum):
    Left = 1
    Center = 2
    Right = 3
    Outside = 4


class AnnotationClipWidget(ui.Widget):
    def __init__(
        self,
        model: Annotation,
        all_models: AnnotationSet,
        timeline_name: Optional[str] = None,
        track_name: str = '',
        on_clip_double_clicked: callable = None
    ):
        super().__init__()
        self._model = model
        self._all_models = all_models

        self._background_rect = None
        self._tag_stringfield = None
        self._tag_label = None
        self._is_selected = False
        self._left_hovered = False
        self._right_hovered = False
        self._body_hovered = False
        self._string_frame = None
        if timeline_name is None:
            self._timeline_name = ''
        else:
            self._timeline_name = timeline_name
        self._track_name = track_name
        self._is_editing = False
        self._on_clip_double_clicked_fn = on_clip_double_clicked

        self._build_ui()

    @property
    def model(self) -> Annotation:
        return self._model

    def contain_type(self) -> WidgetSide:
        if self._left_hovered:
            return WidgetSide.Left
        elif self._right_hovered:
            return WidgetSide.Right
        elif self._body_hovered:
            return WidgetSide.Center
        return WidgetSide.Outside

    def rebuild(self):
        self._build_ui()

    def set_track(self, track_name: str):
        self._track_name = track_name

    def update_color(self):
        clip_data = self._model
        if self._can_edit_source():
            style = STYLE_WRITEABLE
            bg_style = BG_STYLE_WRITEABLE
            border_color = 0xFFEE9900
        else:
            style = STYLE_READONLY
            bg_style = BG_STYLE_READONLY
            border_color = 0xFF000000
        if clip_data.color is not None:
            style["ClipRectangle"] = {
                "background_color": clip_data.color, "border_color": border_color,
                "border_radius": BORDER_RADIUS, "border_width": 1
            }
        else:
            style["ClipRectangle"] = bg_style
        if self._background_rect is not None:
            self._background_rect.style = style

    @property
    def selected(self) -> bool:
        return self._is_selected

    @property
    def is_editing(self) -> bool:
        return self._is_editing

    @selected.setter
    def selected(self, value: bool):
        self._is_selected = value
        if self._background_rect:
            self._background_rect.selected = self._is_selected

    def _get_tooltip(self) -> str:
        scale = omni.usd.get_context().get_stage().GetTimeCodesPerSecond() / self._all_models.time_codes_per_second
        return f'{self._model.tag}\n' + \
            f'Frame range: {int(self._model.start * scale)} - {int(self._model.end * scale)} ({int(self._model.length * scale)} frames)'

    def _build_ui(self):
        container = ui.ZStack()
        container.set_mouse_pressed_fn(self._on_mouse_pressed)
        container.set_mouse_released_fn(self._on_mouse_released)
        container.set_mouse_double_clicked_fn(self._on_clip_double_clicked)

        with container:
            self._background_rect = ui.Rectangle(
                style_type_name_override="ClipRectangle",
                style=STYLE_WRITEABLE,
                selected=self._is_selected,
                tooltip=self._get_tooltip(),
                mouse_hovered_fn=self._on_body_hovered
            )
            self.update_color()
            with ui.HStack():
                if self._can_edit_source():
                    ui.Rectangle(
                        width=DRAG_HANDLER_WIDTH,
                        style_type_name_override="DragRectangle",
                        style=STYLE_WRITEABLE,
                        mouse_hovered_fn=self._on_left_hovered
                    )
                    self._string_frame = ui.Frame(
                            build_fn=self._build_string_frame,
                            horizontal_clipping=True,  # For clipping ui.Label
                        )
                    ui.Rectangle(
                            width=DRAG_HANDLER_WIDTH,
                            style_type_name_override="DragRectangle",
                            style=STYLE_WRITEABLE,
                            mouse_hovered_fn=self._on_right_hovered
                    )
                else:
                    ui.Frame(
                        build_fn=self._build_string_frame,
                        horizontal_clipping=True,  # For clipping ui.Label
                    )

    def _can_edit_source(self) -> bool:
        return self._model is not None and self._model.source is not None and not self._model.source.is_read_only()

    def _on_mouse_pressed(self, x: float, y: float, button: int, modifier: int):
        if button == 1:
            self.show_context_menu()
        self._background_rect.tooltip = ''

    def _on_mouse_released(self, x: float, y: float, button: int, modifier: int):
        self._background_rect.tooltip = self._get_tooltip()

    def _on_clip_double_clicked(self, x: float, y: float, button: int, modifier: int):
        self.selected = True
        self.start_edit()
        if self._on_clip_double_clicked_fn:
            self._on_clip_double_clicked_fn(self._model, x, y, button, modifier)

    def _on_left_hovered(self, hovered:bool):
        self._left_hovered = hovered

    def _on_right_hovered(self, hovered:bool):
        self._right_hovered = hovered

    def _on_body_hovered(self, hovered:bool):
        self._body_hovered = hovered

    def start_edit(self):
        if not self._can_edit_source():
            return
        if self._tag_label is not None:
            self._is_editing = True
            self._tag_label.visible = False
            self._tag_stringfield.visible = True

    def end_edit(self):
        if not self._can_edit_source() or not self._is_editing:
            return
        self._is_editing = False
        self._tag_label.visible = True
        length_changed = len(self._tag_label.text) != len(self._tag_stringfield.model.as_string)
        self._tag_label.text = self._tag_stringfield.model.as_string
        self._tag_stringfield.visible = False
        self._background_rect.tooltip = self._get_tooltip()
        # Need to rebuild the frame to make sure that the new string is also centered
        if length_changed and self._string_frame:
            self._string_frame.rebuild()

    def show_context_menu(self):
        context_menu: omni.kit.context_menu.ContextMenuExtension = omni.kit.context_menu.get_instance()
        if context_menu is None:
            carb.log_warn("Context menu is disabled.")
            return

        is_external = self._model.source is not None and self._model.source.is_external
        objects = {
            'annotation': self._model,
            'all_annotations': self._all_models,
            'external': is_external,
            'source': self._model.source,
            'timeline_name': self._timeline_name
        }
        menu_name = 'clip_context_menu_' + self._model.name
        context_menu.show_context_menu(menu_name, objects, annotation_menu_list)

    def _build_string_frame(self):
        stringfield_style = {}
        stringfield_style['background_color'] = 0x00000000
        stringfield_style['border_radius'] = 0
        stringfield_style['margin'] = 0
        with ui.ZStack():
            self._tag_stringfield = ui.StringField(
                model=self._model.tag_model,
                style=stringfield_style,
            )
            self._tag_label = ui.Label(
                self._model.tag_model.as_string,
                alignment=ui.Alignment.CENTER,
            )
            self._tag_label.visible = not self._is_editing
            self._tag_stringfield.visible = self._is_editing

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self._tag_stringfield:
            self._tag_stringfield.destroy()
            self._tag_stringfield = None
        if self._tag_label:
            self._tag_label.destroy()
            self._tag_label = None
        if self._string_frame:
            self._string_frame.destroy()
            self._string_frame = None
        if self._background_rect:
            self._background_rect.destroy()
            self._background_rect = None
        self._model = None
        self._all_models = None
        self._is_selected = False
        self._is_editing = False
