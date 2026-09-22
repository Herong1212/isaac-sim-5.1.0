# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ui as ui
import omni.usd
import omni.kit.commands
from functools import partial
from ..model.source_model import SourceItemModel, SourceSetModel
from ..anim_preview_model import AnimPreviewModel
from omni.ui import color as cl

# TODO: Utility
BASE_BUTTON_STYLE = {
    "Button": {
        "margin": 2,
        "background_color": cl.shade(cl("#25282ACC"))
    },
    "Button:pressed": {
        "background_color": cl.shade(cl("#34C7FF3B"))
    },
    "Button:hovered": {
        "background_color": cl.shade(cl("#34C7FF3B")),
        "border_width": 1,
        "border_color": cl.shade(cl("#34C7FF"))
    },
    "Button:checked": {
        "background_color": cl.shade(cl("#6E6E6E"))
    },
}


class SourceWidgetSettings:
    def __init__(self):
        self.icon = None

        # TODO: this only works with text right now
        self.icon_width = 28

        self.menu_buffer = 8

        self.show_text = True
        self.length = 0

        self.height = ui.Percent(100)
        self.width = ui.Percent(100)

        self.compare_joint_fn = None
        self.clear_fn = None

        self.enabled = True


class SourceWidget:
    def __init__(
        self,
        name: str,
        preview_model: AnimPreviewModel = None,
        model: SourceSetModel = None,
        settings: SourceWidgetSettings = None,
        index:int = 1
    ):
        self._name = name
        self._preview_model = preview_model
        self._index = index

        if model is None:
            self.model = SourceSetModel()
        else:
            self.model = model

        if settings is None:
            self._settings = SourceWidgetSettings()
        else:
            self._settings = settings

        self._frame = ui.Frame(name=f"SourceWidgetFrame_{self._index:02d}", build_fn=self._build)
        self._changed_sub = self.model.add_item_changed_fn(self._on_item_changed)

        self._stack = None
        self._button = None
        self._image = None
        self._menu = None

        self._button_style = BASE_BUTTON_STYLE

    def _build(self):
        # Button isn't sized right if no text
        display_text = ""
        if self._settings.show_text and self.model:
            source = self.model.get_current_source()
            display_text = source.as_string if source else " "

        self._stack = ui.ZStack(name=f"zs_source_widget_main_{self._index:02d}", height=self._settings.height, width=self._settings.width)
        with self._stack:
            self._button = ui.Button(
                " ",
                name=f"button_source_widget_menu_{self._index:02d}",
                style=self._button_style,
                clicked_fn=self._show_menu,
                enabled=self._settings.enabled
            )
            if self._settings.show_text:
                with ui.VStack(name=f"zs_source_widget_text_main_{self._index:02d}", width=ui.Percent(90)):
                    ui.Spacer()
                    with ui.HStack(height=ui.Percent(90)):
                        ui.Spacer(width=5)
                        if self._settings.icon:
                            ui.Image(self._settings.icon, width=self._settings.icon_width, alignment=ui.Alignment.CENTER, pixel_aligned=False)
                            ui.Spacer(width=5)
                        display_text = " "
                        if self.model:
                            source = self.model.get_current_source()
                            display_text = source.as_string if source else " "
                        ui.Label(display_text, elided_text=True)
                        ui.Spacer(width=5)
                    ui.Spacer()
            else:
                ui.Image(self._settings.icon, name=f"SourceWidgetIcon_{self._index:02d}", alignment=ui.Alignment.CENTER, pixel_aligned=False, style={"padding": 2})

    def _on_item_changed(self, item_model: SourceSetModel, item: SourceItemModel):
        self._frame.rebuild()

    def _tooltip(self):
        with ui.VStack():
            source = self.model.get_current_source()
            if source is None or source.is_empty():
                ui.Label(
                    'No animation is loaded.',
                    style={"font_size": 16, "color": 0xFFFF0000},
                )
            else:
                if source.is_external:
                    ui.Label(
                        f'Source: "{source.source_url}"',
                        style={"font_size": 16, "color": 0xFFFF0000},
                    )
                ui.Label(
                    f'Path in stage: "{source.source_path_in_stage}"',
                    style={"font_size": 16, "color": 0xFFFF0000},
                )

    def _source_item_clicked(self, index):
        self.model.set_current(index)

    def _select_in_stage(self):
        source = self.model.get_current_source()
        if source is None or source.is_external:
            return
        context = omni.usd.get_context()
        stage = context.get_stage()
        if stage is None:
            return
        prim = stage.GetPrimAtPath(source.source_path_in_stage)
        if prim.IsValid():
            selection = [str(prim.GetPath())]
            context.get_selection().set_selected_prim_paths(selection, True)

    def _add_to_main_stage(self, as_payload: bool, prim_only: bool = True):
        source = self.model.get_current_source()
        target_context = omni.usd.get_context()
        target_stage = target_context.get_stage()
        self._preview_model.add_to_stage(target_context, target_stage, source, as_payload, prim_only)

    def _show_menu(self):
        if self._menu is None:
            self._menu = ui.Menu(
                self._name,
            )

        self._menu.clear()
        with self._menu:
            for i, source in enumerate(self.model._sources):
                current = i == self.model._current_index.as_int  # TODO: better access to index
                ui.MenuItem(
                    source[0].model.as_string,
                    triggered_fn=partial(self._source_item_clicked, i),
                    checkable=True,
                    enabled=not current,
                    checked=current
                )

            ui.Separator()

            current_source = self.model.get_current_source()
            can_select = current_source is not None and not current_source.is_external\
                and current_source.exists_in_source_stage
            ui.MenuItem(
                "Select in Stage",
                triggered_fn=self._select_in_stage,
                enabled=can_select
            )
            can_select = current_source is not None and (current_source.is_external or
                not current_source.exists_in_source_stage)
            if can_select:
                with ui.MenuItemCollection(text='Add to main stage', checkable=False):
                    ui.MenuItem(
                        "Copy",
                        triggered_fn=partial(self._add_to_main_stage, False),
                        enabled=can_select
                    )
                    ui.MenuItem(
                        "Add as Payload (Selection Only)",
                        triggered_fn=partial(self._add_to_main_stage, True, True),
                        enabled=can_select
                    )
                    ui.MenuItem(
                        "Add as Payload (Entire Stage)",
                        triggered_fn=partial(self._add_to_main_stage, True, False),
                        enabled=can_select
                    )
            else:
                ui.MenuItem(
                    "Add to Main Stage",
                    enabled=False
                )

            # TODO: make this more flexible
            if self._settings.compare_joint_fn:
                ui.MenuItem(
                    "Compare Joints",
                    triggered_fn=self._settings.compare_joint_fn,
                    enabled=True
                )

            if self._settings.clear_fn:
                ui.Separator()

                ui.MenuItem(
                    "Clear All",
                    triggered_fn=self._settings.clear_fn,
                    enabled=True
                )

        self._menu.show_at(
            (int)(self._stack.screen_position_x),
            # (int)(self._stack.screen_position_y + self._stack.computed_content_height + self._settings.menu_buffer)
            (int)(self._stack.screen_position_y - self._menu.computed_content_height - self._settings.menu_buffer)
        )

    def update_icon(self, icon):
        self._settings.icon = icon
        if self._image:
            self._image

    def destroy(self):
        if self.model is not None and self._changed_sub is not None:
            self.model.remove_item_changed_fn(self._changed_sub)
        self.model = None
        if self._stack:
            self._stack.destroy()
            self._stack = None
        if self._button:
            self._button.destroy()
            self._button = None
        if self._image:
            self._image.destroy()
            self._image = None
