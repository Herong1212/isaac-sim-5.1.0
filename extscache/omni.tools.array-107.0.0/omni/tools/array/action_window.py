# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import random
from typing import List

import carb
import omni.kit.menu.utils as menu_utils
import omni.ui as ui
import omni.usd
from omni.kit.menu.utils import MenuItemDescription
from pxr import Gf, Sdf, Tf, Usd

from . import array_const as a_c
from . import ui_const as ui_c
from .array_core import ArrayCore
from .array_params import ArrayParams


class ActionWindow:
    def __init__(self):
        super().__init__()
        self._window = None
        self._menu_entry = None
        self._create_menu_entry()

        # Get the array core instance
        self._array_core = ArrayCore.get_instance()

        # Setup stage/usd/omni references
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._stage = None
        self._selected_paths = []
        self._stage_listener = None

        # Async object updates
        self._pending_changed_paths = set()
        self._update_task = None

        # Subscribe to stage events
        self._stage_event_sub = self._usd_context.get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event
        )

        # If the stage is already open with this is initialized, call _on_stage_opened
        if self._usd_context.get_stage_state() == omni.usd.StageState.OPENED:
            self._on_stage_opened()

        self._reset_ui_object_refs()

        self._closed_via_tool_button = False
        self.skip_lock = False
        self.skip_ui_callbacks = False
        self.allow_drag_field_updates = False
        self.field_currently_drag_edited = False
        self.skip_vector_conversion = False

        self._array_params = ArrayParams()
        self._last_array_values = self._array_params.get_defaults()

    # Clean up references
    def clean(self):
        self.hide()
        self._window = None
        self._array_core.clean()
        self._array_core = None
        self._reset_ui_object_refs()
        # Unsubscribe from stage events
        self._stage_event_sub = None
        # Remove the Array Menu item from the "Tools" menu
        menu_utils.remove_menu_items([self._menu_entry], name="Tools")
        self._menu_entry = None
        # Cancel/clear async tasks
        if self._update_task is not None:
            self._update_task.cancel()
            self._update_task = None
            self._pending_changed_paths.clear()

    def _reset_ui_object_refs(self):
        self.preview_button = None
        self.count_1d_widget = None
        self.count_2d_widget = None
        self.count_3d_widget = None
        self.translate_1d_widget = None
        self.rotate_1d_widget = None
        self.scale_1d_widget = None
        self.linked_scale_button = None
        self.offset_2d_widget = None
        self.offset_3d_widget = None
        self.translate_1d_total_button = None
        self.rotate_1d_total_button = None
        self.scale_1d_total_button = None
        self.offset_3d_total_button = None
        self.offset_2d_total_button = None
        self.create_type_collection = None
        self.array_type_dropdown = None
        self.group_results_checkbox = None
        self.reorient_checkbox = None
        self.remember_values_checkbox = None
        self.autoselect_objects_checkbox = None
        self.cancel_button = None
        self.reset_all_button = None
        self.apply_button = None
        self.scale_label = None
        self.random_sequence_seed_field = None
        self.random_button = None

    # Fired when a stage is opened
    def _on_stage_opened(self):
        self._stage = self._usd_context.get_stage()
        self._update_selection()

    # Fired when a stage is closed
    def _on_stage_closed(self):
        self._stage = None
        self._selected_paths = []

    # Fired every time something happens in the stage
    def _on_stage_event(self, evt):
        if evt.type == int(omni.usd.StageEventType.OPENED):
            self._on_stage_opened()
        elif evt.type == int(omni.usd.StageEventType.CLOSING):
            self._on_stage_closed()
        # Every time a selection is changed update the selection variables
        if evt.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            # Update prims
            self._update_selection()

    # Update the selected prims and tell array core
    def _update_selection(self):
        # If the has not been created or is not visible, exit
        if self._window is None or not self._window.visible:
            return
        self._selected_paths = self._selection.get_selected_prim_paths()
        prims = self._get_prims_from_selected_paths()

        filtered_prims = self._check_instanceable_prims(prims)
        self._array_core.update_target_prims(filtered_prims)

        # If any selected objects are filtered and remain, listen for object changes for preview updates, otherwise revoke listener
        self._toggle_objects_changed_listener(len(filtered_prims) > 0)

    # Checks provided prims to see if they are valid for instancing
    def _check_instanceable_prims(self, prims: list):
        # Only instance Xforms
        allowed_types_for_instancing = a_c.ALLOWED_INSTANCE_TYPES
        unallowed_prims = []
        allowed_prims = []
        for prim in prims:
            if not prim or prim.GetTypeName() not in allowed_types_for_instancing:
                unallowed_prims.append(prim)
            else:
                allowed_prims.append(prim)

        # Toggle the instanceable warning based on conditions
        has_unallowed_prims = len(unallowed_prims) > 0
        has_mixed_prims = has_unallowed_prims and prims != unallowed_prims
        self._toggle_instanceable_warning(
            active=has_unallowed_prims, has_mixed_prims=has_mixed_prims, unallowed_prims=unallowed_prims
        )

        # If the creation type is set to Copies, return the original list
        if self._last_array_values[a_c.CREATE_TYPE] is a_c.CreateType.COPIES:
            return prims

        # If the current creation type is set to Instances...
        if self._last_array_values[a_c.CREATE_TYPE] is a_c.CreateType.INSTANCES:
            # If there is a mix of valid and invalid prims, only return the valid prims
            if has_mixed_prims:
                return allowed_prims
            else:
                # If all prims are invalid, force set the creation type to Copies
                if has_unallowed_prims:
                    self._update_create_type_setting(2, False)
                # Then return the original prim list (will either be empty - no selection - or a list of only unallowed prims - which would be used by copies)
                return prims

    def _toggle_instanceable_warning(
        self, active: bool, has_mixed_prims: bool, unallowed_prims: list = None, tooltip_limit=3
    ):
        # ==== Hide Warning ====
        if not active:
            # Hide warning icon
            self._warning_icon.visible = False
            # Re-enable create instances UI element
            self._create_instance_label.enabled = True
            self._create_instance_radio.enabled = True
            return

        # ==== Show Warning =====
        # Always make sure the options get un-collapsed
        self._options.collapsed = False
        # Show warning icon
        self._warning_icon.visible = True
        # Disable/Enable create instance UI element based on the has_mixed_prims value
        self._create_instance_label.enabled = has_mixed_prims
        self._create_instance_radio.enabled = has_mixed_prims

        # Generate dynamic tooltips
        tooltip = "Only Xforms are allowed to be instanced. The following prims are not allowed: \n"
        for index, prim in enumerate(unallowed_prims):
            if index < tooltip_limit:
                tooltip += f"{prim}"

                # Append a . or , on the end
                if index == len(unallowed_prims) - 1:
                    tooltip += "."
                else:
                    if index < tooltip_limit - 1:
                        tooltip += ", "
            else:
                tooltip += "... see the console for the full list of unallowed prims."
        # If there aren't any mixed prims, add this line to the tooltip about "Create Instances" being disabled
        if not has_mixed_prims:
            tooltip += "\n\n'Create Instances' is disabled until a valid instanceable prim is selected."
        self._warning_icon.set_tooltip_fn(lambda: self._create_tooltip(tooltip))

        # Log warnings
        if self._last_array_values[a_c.CREATE_TYPE] is a_c.CreateType.INSTANCES:
            message = (
                f"Only Xforms are allowed to be instanced. Failed to instance the following prims: {unallowed_prims}."
            )
            carb.log_warn(message)

    def _toggle_objects_changed_listener(self, toggle: bool):
        if toggle:
            if self._stage_listener is None:
                self._stage_listener = Tf.Notice.Register(
                    Usd.Notice.ObjectsChanged, self._on_objects_changed, self._stage
                )
        else:
            # Clear Stage listener
            if self._stage_listener is not None:
                self._stage_listener.Revoke()
                self._stage_listener = None
            # End async object change task if one exists
            if self._update_task is not None:
                self._update_task.cancel()
                self._update_task = None
                self._pending_changed_paths.clear()

    # Called when an object changes in the scene while the Array Tool is open
    def _on_objects_changed(self, notice, sender):
        # Collect all prim paths that changed into a set (filters uniques)
        self._pending_changed_paths.update(
            Sdf.Path.GetAbsoluteRootOrPrimPath(i) for i in notice.GetChangedInfoOnlyPaths()
        )

        # If there is no active task, start one on the next update
        if self._update_task is None or self._update_task.done():
            # Only start task if a change happened
            if self._pending_changed_paths:
                self._update_task = asyncio.ensure_future(self._handle_changed_paths_async())

    # Batch handle object changes
    async def _handle_changed_paths_async(self):
        # Isolate objects that moved which are also selected
        moved_selected = []
        for path in self._selected_paths:
            if Sdf.Path(path) in self._pending_changed_paths:
                moved_selected.append(path)

        # If there are moved & selected objects that changed, update core
        if moved_selected:
            moved_selected_prims = [self._stage.GetPrimAtPath(x) for x in moved_selected]
            self._array_core.update_target_prims(moved_selected_prims)

        # Clear pending paths and clear task
        self._pending_changed_paths.clear()
        self._update_task = None

    # Show the UI window. Create one if none exist
    def show(self):
        if self._window is None:
            self._create_window()
        self._window.visible = True
        self._update_selection()

        if self.remember_values_checkbox.model.as_bool:
            self._sync_ui_with_values(self._last_array_values, False)
        else:
            self._reset_ui_to_defaults_and_apply_to_core()
            self._last_array_values = self._array_core.get_all_array_values()

    # Hide the UI window
    def hide(self):
        if self._window is not None:
            self._window.visible = False

        self._array_core.cancel_array()
        self._toggle_objects_changed_listener(False)

    # Create the UI window for the first time
    def _create_window(self):
        self._window = ui.Window(ui_c.NAME_TOOL, visible=False)
        self._window.auto_resize = True

        # populate window with content
        with self._window.frame:
            self.window_content = ui.VStack(width=385, style={"margin": 7})
            with self.window_content:
                self._create_array_interface()
                # register ui element events
                self._set_up_ui_elements_functionality()
                # set everything to default
                self._reset_ui_to_defaults_and_apply_to_core()

        self._window.set_visibility_changed_fn(self._update_menu_entry_visibility)

    # Apply clicked on
    def _on_apply_clicked(self):
        # Apply settings
        omni.kit.commands.execute("ApplyArrayCommand")
        self._closed_via_tool_button = True
        # Close UI
        self.hide()

    # Close/Cancel clicked on
    def _on_close_clicked(self):
        self._closed_via_tool_button = True
        # Close the UI window
        self.hide()

    # Reset clicked on
    def _on_reset_clicked(self):
        # Reset array tool values to defaults
        self._reset_ui_to_defaults_and_apply_to_core()
        self._update_remember_last_values_checkbox(ui_c.REMEMBER_LAST_DEFAULT)

    # Create the Omniverse menu entry
    def _create_menu_entry(self):
        self._menu_entry = MenuItemDescription(
            name="Array",
            appear_after="Align",
            ticked=True,
            ticked_fn=self._is_visible,
            onclick_fn=self._menu_window_toggle,
        )

        menu_utils.add_menu_items([self._menu_entry], name="Tools")

    # Utility method to Query window visibility
    def _is_visible(self) -> bool:
        return False if self._window is None else self._window.visible

    # Toggle the UI window from the menu button
    def _menu_window_toggle(self):
        if self._is_visible():
            self.hide()
        else:
            self.show()

    # Called when the UI window's visibility changes
    def _update_menu_entry_visibility(self, visible):
        # If the window was closed
        if not visible:
            # Refresh the "Tools" menu so the tick gets updated
            menu_utils.refresh_menu_items("Tools")
            # If it wasn't closed because of cancel or apply
            # Must be closed by the 'x'
            if not self._closed_via_tool_button:
                self._array_core.cancel_array()
                self._toggle_objects_changed_listener(False)
            self._closed_via_tool_button = False

    # ========================== VALUES CHANGES =============================
    # The functions in this section are only called when any of the array core values are actually being updated

    def _on_count_changed(self, value):
        self._update_core_value(a_c.COUNT, value)

    def _on_two_d_count_changed(self, value):
        self._update_core_value(a_c.TWO_D_COUNT, value)

    def _on_three_d_count_changed(self, value):
        self._update_core_value(a_c.THREE_D_COUNT, value)

    def _on_preview_changed(self, value):
        self._update_core_value(a_c.PREVIEW, value)
        self._toggle_objects_changed_listener(value)

    def _on_incremental_translate_changed(self, value):
        self._update_core_value(a_c.INC_TRANSLATE, Gf.Vec3d(value))

    def _on_incremental_rotate_changed(self, value):
        self._update_core_value(a_c.INC_ROTATE, Gf.Vec3d(value))

    def _on_incremental_scale_changed(self, value):
        self._update_core_value(a_c.INC_SCALE, Gf.Vec3d(value))

    def _on_two_d_offset_changed(self, value):
        self._update_core_value(a_c.TWO_D_OFFSET, Gf.Vec3d(value))

    def _on_three_d_offset_changed(self, value):
        self._update_core_value(a_c.THREE_D_OFFSET, Gf.Vec3d(value))

    def _on_total_translate_toggle_changed(self, value):
        self._update_core_value(a_c.TOT_TRANSLATE_TOGGLE, value)
        self._update_row_total_or_incremental_mode(
            value, a_c.INC_TRANSLATE, self._array_core.get_array_value(a_c.COUNT), self.translate_1d_widget
        )

    def _on_total_rotate_toggle_changed(self, value):
        self._update_core_value(a_c.TOT_ROTATE_TOGGLE, value)
        self._update_row_total_or_incremental_mode(
            value, a_c.INC_ROTATE, self._array_core.get_array_value(a_c.COUNT), self.rotate_1d_widget
        )

    def _on_total_scale_toggle_changed(self, value):
        self._update_core_value(a_c.TOT_SCALE_TOGGLE, value)
        self._update_row_total_or_incremental_mode(
            value, a_c.INC_SCALE, self._array_core.get_array_value(a_c.COUNT), self.scale_1d_widget
        )

    def _on_total_offset_two_d_toggle_changed(self, value):
        self._update_core_value(a_c.TOT_TWO_D_OFFSET_TOGGLE, value)
        self._update_row_total_or_incremental_mode(
            value, a_c.TWO_D_OFFSET, self._array_core.get_array_value(a_c.TWO_D_COUNT), self.offset_2d_widget
        )

    def _on_total_offset_three_d_toggle_changed(self, value):
        self._update_core_value(a_c.TOT_THREE_D_OFFSET_TOGGLE, value)
        self._update_row_total_or_incremental_mode(
            value, a_c.THREE_D_OFFSET, self._array_core.get_array_value(a_c.THREE_D_COUNT), self.offset_3d_widget
        )

    def _on_create_type_changed(self, value):
        self._update_core_value(a_c.CREATE_TYPE, a_c.CreateType(value))

    def _on_array_type_changed(self, value):
        self._update_core_value(a_c.ARRAY_TYPE, a_c.ArrayType(value))

    def _on_random_seed_changed(self, value):
        self._update_core_value(a_c.RANDOM_ORDER_SEED, value)

    def _on_array_group_result_changed(self, value):
        self._update_core_value(a_c.ARRAY_GROUP_RESULT, value)

    def _on_reorient_changed(self, value):
        self._update_core_value(a_c.REORIENT_ROTATION, value)

    def _on_linked_scale_changed(self, value):
        self._update_core_value(a_c.LINKED_SCALE_TOGGLE, value)

    def _on_remember_last_changed(self, value):
        pass

    def _on_auto_select_created_changed(self, value):
        self._update_core_value(a_c.AUTO_SELECT_CREATED, value)

    # ========================== Full UI Updates =============================

    # Sets all UI elements back to the default values. Also propagates to array core.
    def _reset_ui_to_defaults_and_apply_to_core(self):
        # Force any drag fields to update core values even when not being mouse-dragged
        self._set_allow_drag_field_updates(True)

        self._update_preview_button(a_c.PREVIEW_DEFAULT)

        self._update_count_1d(a_c.COUNT_DEFAULT)
        self._update_count_2d(a_c.TWO_D_COUNT_DEFAULT)
        self._update_count_3d(a_c.THREE_D_COUNT_DEFAULT)

        self._set_multi_values(self.translate_1d_widget, a_c.INC_TRANSLATE_DEFAULT)
        self._set_multi_values(self.rotate_1d_widget, a_c.INC_ROTATE_DEFAULT)
        self._set_multi_values(self.scale_1d_widget, a_c.INC_SCALE_DEFAULT)
        self._set_multi_values(self.offset_2d_widget, a_c.TWO_D_OFFSET_DEFAULT)
        self._set_multi_values(self.offset_3d_widget, a_c.THREE_D_OFFSET_DEFAULT)

        self._update_linked_scale_button(self.linked_scale_button, a_c.LINKED_SCALE_TOGGLE_DEFAULT)
        self._update_linked_scale_reference(a_c.LINKED_SCALE_DEFAULT)

        self._update_translate_total_mode_button(a_c.TOT_TRANSLATE_TOGGLE_DEFAULT)
        self._update_rotate_total_mode_button(a_c.TOT_ROTATE_TOGGLE_DEFAULT)
        self._update_scale_total_mode_button(a_c.TOT_SCALE_TOGGLE_DEFAULT)
        self._update_offset_2d_total_mode_button(a_c.TOT_TWO_D_OFFSET_TOGGLE_DEFAULT)
        self._update_offset_3d_total_mode_button(a_c.TOT_THREE_D_OFFSET_TOGGLE_DEFAULT)

        self._update_create_type_setting(a_c.CREATE_TYPE_DEFAULT)
        self._update_array_type_setting(a_c.ARRAY_TYPE_DEFAULT)

        self._update_random_seed(a_c.RANDOM_ORDER_SEED_DEFAULT)
        self._update_random_sequence_seed_field()
        self._update_group_results_checkbox(a_c.ARRAY_GROUP_RESULT_DEFAULT)
        self._update_reorient_checkbox(a_c.REORIENT_ROTATION_DEFAULT)
        self._update_autoselect_checkbox(a_c.AUTO_SELECT_CREATED_DEFAULT)

        self._set_allow_drag_field_updates(False)

    # Updates all UI values to match the passed in values. Skip callbacks if core updates should not be updated.
    def _sync_ui_with_values(self, values: dict, skip_callbacks: bool = False):

        # Temporarily skip all UI elements callbacks, since we only want to update the UI and not change core values
        self._set_skip_ui_callbacks(skip_callbacks)
        self._set_allow_drag_field_updates(not skip_callbacks)
        self._set_skip_lock(True)
        self.skip_vector_conversion = True

        self._update_preview_button()

        self._update_count_1d(values[a_c.COUNT], True)
        self._update_count_2d(values[a_c.TWO_D_COUNT], True)
        # Fix to make sure count and offset values are applied correctly to array core if tool is opened
        # with 2d offset count at 1
        if values[a_c.TWO_D_COUNT] > 1:
            self._update_count_3d(values[a_c.THREE_D_COUNT], True)
        else:
            self._connect_2d_to_3d_count(values[a_c.TWO_D_COUNT])

        self._update_linked_scale_button(self.linked_scale_button, values[a_c.LINKED_SCALE_TOGGLE])

        self._set_multi_values(self.translate_1d_widget, values[a_c.INC_TRANSLATE])
        self._force_set_multi_values_changed(self.translate_1d_widget)
        self._set_multi_values(self.rotate_1d_widget, values[a_c.INC_ROTATE])
        self._force_set_multi_values_changed(self.rotate_1d_widget)
        self._set_multi_values(self.scale_1d_widget, values[a_c.INC_SCALE])
        self._force_set_multi_values_changed(self.scale_1d_widget)
        self._set_multi_values(self.offset_2d_widget, values[a_c.TWO_D_OFFSET])
        self._force_set_multi_values_changed(self.offset_2d_widget)
        self._set_multi_values(self.offset_3d_widget, values[a_c.THREE_D_OFFSET])
        self._force_set_multi_values_changed(self.offset_3d_widget)

        self._update_translate_total_mode_button(values[a_c.TOT_TRANSLATE_TOGGLE])
        self._update_rotate_total_mode_button(values[a_c.TOT_ROTATE_TOGGLE])
        self._update_scale_total_mode_button(values[a_c.TOT_SCALE_TOGGLE])
        self._update_offset_2d_total_mode_button(values[a_c.TOT_TWO_D_OFFSET_TOGGLE])
        self._update_offset_3d_total_mode_button(values[a_c.TOT_THREE_D_OFFSET_TOGGLE])

        self._update_create_type_setting(values[a_c.CREATE_TYPE])
        self._update_array_type_setting(values[a_c.ARRAY_TYPE])

        self._update_random_seed(values[a_c.RANDOM_ORDER_SEED])
        self._update_random_sequence_seed_field()
        self._update_group_results_checkbox(values[a_c.ARRAY_GROUP_RESULT])
        self._update_reorient_checkbox(values[a_c.REORIENT_ROTATION])
        self._update_autoselect_checkbox(values[a_c.AUTO_SELECT_CREATED])

        # Resume callbacks
        self._set_skip_lock(False)
        self._set_skip_ui_callbacks(False)
        self._set_allow_drag_field_updates(False)
        self.skip_vector_conversion = False

    # ========================== Build UI Elements =============================

    def _create_array_interface(self):
        with ui.VStack(spacing=8, height=0, style={"margin": 0}):
            with ui.HStack():
                with ui.VStack():
                    ui.Spacer()
                    self.reset_all_button = ui.Button(
                        "Reset All",
                        width=80,
                        height=22,
                        tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_RESET_ALL),
                    )
                    ui.Spacer()
                ui.Label(
                    "Preview",
                    alignment=ui.Alignment.RIGHT_CENTER,
                    tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_PREVIEW),
                )
                ui.Spacer(width=10)
                with ui.VStack(width=0, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_PREVIEW)):
                    self.preview_button = ui.Button(width=30, height=30)
                    self.preview_button.style = ui_c.STYLE_BUTTON_PREVIEW_OFF

            with ui.HStack(skip_draw_when_clipped=True, height=0):
                ui.Label("Count", width=50, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_COUNT))
                with ui.VStack(height=15):
                    ui.Spacer()
                    self.count_1d_widget = ui.IntDrag(
                        width=35, min=1, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_COUNT)
                    )
                    ui.Spacer()

            with ui.HStack(skip_draw_when_clipped=True, height=0):
                ui.Label("Translate", width=100, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_TRANSLATE))

                with ui.HStack():
                    self.translate_1d_widget = self._create_vector_widget()

                with ui.VStack(width=0, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_TOTAL)):
                    ui.Spacer()
                    self.translate_1d_total_button = ui.Button(width=15, height=15)
                    ui.Spacer()

            with ui.HStack(skip_draw_when_clipped=True, height=0):
                ui.Label("Rotate", width=100, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_ROTATE))
                with ui.HStack():
                    self.rotate_1d_widget = self._create_vector_widget()
                with ui.VStack(width=0, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_TOTAL)):
                    ui.Spacer()
                    self.rotate_1d_total_button = ui.Button(width=15, height=15)
                    ui.Spacer()

            with ui.HStack(skip_draw_when_clipped=True, height=0):
                self.scale_label = ui.Label(
                    "Scale", width=40, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_SCALE)
                )
                with ui.VStack(width=18):
                    ui.Spacer()
                    self.linked_scale_button = ui.Button(
                        width=18,
                        height=18,
                        tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_LINKED_SCALE),
                    )
                    ui.Spacer()
                ui.Spacer(width=42)

                with ui.HStack():
                    self.scale_1d_widget = self._create_vector_widget(0, 0, 3, None, 0.01)
                with ui.VStack(width=0, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_TOTAL)):
                    ui.Spacer()
                    self.scale_1d_total_button = ui.Button(width=15, height=15)
                    ui.Spacer()

            ui.Separator("Additional Dimensions and Row Offsets", style=ui_c.STYLE_SEPARATOR)
            ui.Spacer(height=15)

            with ui.HStack(skip_draw_when_clipped=True, height=0):
                ui.Label("2D", width=50, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_OFFSET_2D))
                self.count_2d_widget = ui.IntDrag(
                    width=35, min=1, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_FIELD_COUNT_2D)
                )
                ui.Spacer(width=5)
                ui.Spacer(width=10)
                self.offset_2d_widget = self._create_vector_widget()
                with ui.VStack(width=0, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_TOTAL)):
                    ui.Spacer()
                    self.offset_2d_total_button = ui.Button(width=15, height=15)
                    ui.Spacer()

            with ui.HStack(skip_draw_when_clipped=True, height=0):
                ui.Label("3D", width=50, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_OFFSET_3D))
                self.count_3d_widget = ui.IntDrag(width=35, min=1, tooltip=ui_c.TOOLTIP_FIELD_COUNT_3D)
                ui.Spacer(width=5)
                ui.Spacer(width=10)
                self.offset_3d_widget = self._create_vector_widget()
                with ui.VStack(width=0, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_TOTAL)):
                    ui.Spacer()
                    self.offset_3d_total_button = ui.Button(width=15, height=15)
                    ui.Spacer()
            ui.Spacer(height=5)

            self._options = ui.CollapsableFrame("Options", style=ui_c.STYLE_COLLAPSABLE_FRAME)
            self._options.collapsed = True
            with self._options:
                with ui.VStack():
                    with ui.VStack(style={"margin": 0}):
                        with ui.ZStack(style={"margin": 3}):
                            ui.Rectangle(style=ui_c.STYLE_RECT_CREATE_TYPE)
                            self.create_type_collection = ui.RadioCollection()
                            with ui.HStack():
                                ui.Spacer(width=ui.Fraction(1))
                                with ui.HStack(width=40):
                                    with ui.VStack():
                                        self._warning_icon = ui.Button(
                                            width=26, height=26, style=ui_c.STYLE_WARNING_ICON
                                        )
                                        self._warning_icon.visible = False
                                    self._create_instance_label = ui.Label(
                                        "Create Instances",
                                        style=ui_c.STYLE_LABEL,
                                        tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_CREATE_INSTANCES),
                                    )
                                    with ui.VStack():
                                        self._create_instance_radio = ui.RadioButton(
                                            radio_collection=self.create_type_collection,
                                            style=ui_c.STYLE_RADIO_BUTTON,
                                            width=26,
                                            height=26,
                                            tooltip_fn=lambda: self._create_tooltip(
                                                ui_c.TOOLTIP_LABEL_CREATE_INSTANCES
                                            ),
                                        )
                                ui.Spacer(width=10)
                                with ui.HStack(width=30):
                                    ui.Label(
                                        "Create Copies",
                                        tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_CREATE_COPIES),
                                    )
                                    with ui.VStack():
                                        ui.RadioButton(
                                            radio_collection=self.create_type_collection,
                                            style=ui_c.STYLE_RADIO_BUTTON,
                                            width=26,
                                            height=26,
                                            tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_CREATE_COPIES),
                                        )
                                ui.Spacer(width=ui.Fraction(1))
                                self._build_reset_button(
                                    self.create_type_collection.model.add_value_changed_fn,
                                    a_c.CREATE_TYPE_DEFAULT.value - 1,
                                    a_c.CREATE_TYPE_DEFAULT.value,
                                    self._update_create_type_setting,
                                )

                    def _create_option_label(text, tooltip):
                        with ui.HStack():
                            ui.Label(
                                text,
                                tooltip_fn=lambda: self._create_tooltip(tooltip),
                            )

                    with ui.HStack():
                        _create_option_label("Source Selection as ...", ui_c.TOOLTIP_LABEL_ARRAY_TYPE)
                        with ui.HStack():
                            ui.Spacer(width=3, style={"margin": 0})
                            self.array_type_dropdown = ui.ComboBox(
                                0,
                                "Single Stamp",
                                "Ordered Sequence",
                                "Random Sequence",
                                tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_ARRAY_TYPE),
                                alignment=ui.Alignment.RIGHT,
                                style=ui_c.STYLE_COMBOBOX_ARRAY_TYPE,
                            )
                            self._build_reset_button(
                                self.array_type_dropdown.model.add_item_changed_fn,
                                a_c.ARRAY_TYPE_DEFAULT.value - 1,
                                a_c.ARRAY_TYPE_DEFAULT.value,
                                self._update_array_type_setting,
                            )
                    with ui.HStack():
                        _create_option_label("Random Sequence Seed", ui_c.TOOLTIP_RANDOM_ORDER_SEED)
                        with ui.HStack():
                            ui.Spacer(width=3, style={"margin": 0})
                            self.random_sequence_seed_field = ui.IntDrag(
                                width=80,
                                tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_RANDOM_ORDER_SEED),
                                style=ui_c.STYLE_RANDOM_SEED_FIELD,
                            )
                            ui.Spacer(width=5)
                            with ui.VStack(width=0, style={"margin": 0, "padding": 0}):
                                ui.Spacer()
                                self.random_button = ui.Button(
                                    width=21,
                                    height=21,
                                    style=ui_c.STYLE_RANDOM_BUTTON,
                                    tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_RANDOM),
                                )
                                ui.Spacer()
                            ui.Spacer(width=5)
                            ui.Line(style=ui_c.STYLE_LINE)
                            self._build_reset_button(
                                self.random_sequence_seed_field.model.add_value_changed_fn,
                                a_c.RANDOM_ORDER_SEED_DEFAULT,
                                a_c.RANDOM_ORDER_SEED_DEFAULT,
                                self._update_random_seed,
                            )
                    with ui.HStack():
                        _create_option_label("Group Results", ui_c.TOOLTIP_LABEL_GROUP_RESULT)
                        with ui.HStack():
                            self.group_results_checkbox = ui.CheckBox(
                                width=10, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_GROUP_RESULT)
                            )
                            ui.Spacer(width=5)
                            ui.Line(style=ui_c.STYLE_LINE)
                            self._build_reset_button(
                                self.group_results_checkbox.model.add_value_changed_fn,
                                a_c.ARRAY_GROUP_RESULT_DEFAULT,
                                a_c.ARRAY_GROUP_RESULT_DEFAULT,
                                self._update_group_results_checkbox,
                            )
                    with ui.HStack():
                        _create_option_label("Follow Rotation", ui_c.TOOLTIP_LABEL_REORIENT)
                        with ui.HStack():
                            self.reorient_checkbox = ui.CheckBox(
                                width=10, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_REORIENT)
                            )
                            ui.Spacer(width=5)
                            ui.Line(style=ui_c.STYLE_LINE)
                            self._build_reset_button(
                                self.reorient_checkbox.model.add_value_changed_fn,
                                a_c.REORIENT_ROTATION_DEFAULT,
                                a_c.REORIENT_ROTATION_DEFAULT,
                                self._update_reorient_checkbox,
                            )
                    with ui.HStack():
                        _create_option_label("Remember Last Values", ui_c.TOOLTIP_LABEL_REMEMBER_LAST)
                        with ui.HStack():
                            self.remember_values_checkbox = ui.CheckBox(
                                width=10, tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_REMEMBER_LAST)
                            )
                            self.remember_values_checkbox.model.set_value(ui_c.REMEMBER_LAST_DEFAULT)
                            ui.Spacer(width=5)
                            ui.Line(style=ui_c.STYLE_LINE)
                            self._build_reset_button(
                                self.remember_values_checkbox.model.add_value_changed_fn,
                                ui_c.REMEMBER_LAST_DEFAULT,
                                ui_c.REMEMBER_LAST_DEFAULT,
                                self._update_remember_last_values_checkbox,
                            )
                    with ui.HStack():
                        _create_option_label("Auto-Select Created Objects", ui_c.TOOLTIP_LABEL_AUTO_SELECT_CREATED)
                        with ui.HStack():
                            self.autoselect_objects_checkbox = ui.CheckBox(
                                width=10,
                                tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_LABEL_AUTO_SELECT_CREATED),
                            )
                            ui.Spacer(width=5)
                            ui.Line(style=ui_c.STYLE_LINE)
                            self._build_reset_button(
                                self.autoselect_objects_checkbox.model.add_value_changed_fn,
                                a_c.AUTO_SELECT_CREATED_DEFAULT,
                                a_c.AUTO_SELECT_CREATED_DEFAULT,
                                self._update_autoselect_checkbox,
                            )

            ui.Spacer(height=5)
            with ui.HStack(height=22, spacing=10):
                ui.Spacer(width=ui.Fraction(0.5))
                self.apply_button = ui.Button(
                    "Apply",
                    width=ui.Fraction(0.25),
                    style=ui_c.STYLE_BUTTON_APPLY,
                    tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_APPLY),
                )
                self.cancel_button = ui.Button(
                    "Cancel",
                    width=ui.Fraction(0.25),
                    tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_CANCEL),
                )

    def _create_vector_widget(
        self, range_min=0, range_max=0, comp_count=3, additional_widget_kwargs=None, step=1.0
    ) -> ui.MultiFloatDragField:
        widget_kwargs = {"min": range_min, "max": range_max, "step": step}
        if additional_widget_kwargs:
            widget_kwargs.update(additional_widget_kwargs)
        m = self._create_multi_float_drag_with_labels(
            labels=[
                ("X", "vector_label_x", ui_c.STYLE_VECTOR_LABEL),
                ("Y", "vector_label_y", ui_c.STYLE_VECTOR_LABEL),
                ("Z", "vector_label_z", ui_c.STYLE_VECTOR_LABEL),
            ],
            comp_count=comp_count,
            **widget_kwargs,
        )
        return m

    def _create_multi_float_drag_with_labels(self, labels, comp_count, **kwargs) -> None:
        RECT_WIDTH = 13
        SPACING = 20
        with ui.ZStack():
            with ui.HStack():
                if labels:
                    ui.Spacer(width=RECT_WIDTH)
                    widget_kwargs = {"name": "multivalue", "h_spacing": RECT_WIDTH + SPACING}
                else:
                    widget_kwargs = {"name": "multivalue", "h_spacing": 3}
                widget_kwargs.update(kwargs)
                m = ui.MultiFloatDragField(**widget_kwargs)
                ui.Spacer(width=25)
            with ui.HStack():
                if labels:
                    for i in range(comp_count):
                        if i != 0:
                            ui.Spacer(width=SPACING)
                        label = labels[i]
                        with ui.ZStack(width=RECT_WIDTH + 1):
                            ui.Rectangle(
                                name=label[1],
                                style=label[2],
                            )
                            ui.Label(label[0], name="vector_label", alignment=ui.Alignment.CENTER)
                        ui.Spacer()
                    ui.Spacer(width=25)
            with ui.HStack():
                for i in range(comp_count):
                    ui.Spacer()
                    with ui.Placer(offset_x=-20 - i, width=0):
                        self._build_multifloat_component_reset_button(m, i)
            return m

    def _build_multifloat_component_reset_button(
        self, multifloat: ui.MultiFloatDragField, item_index=0
    ) -> ui.Rectangle:
        btn = None
        with ui.VStack():
            ui.Spacer()
            with ui.ZStack(width=15, height=10):
                with ui.HStack(style={"margin_width": 0}):
                    ui.Spacer()
                    with ui.VStack(width=0):
                        ui.Spacer()
                        ui.Rectangle(width=5, height=5, name="reset_invalid", style=ui_c.STYLE_BUTTON_RESET_OFF)
                        ui.Spacer()
                    ui.Spacer()
                btn = ui.Rectangle(
                    width=12,
                    height=12,
                    name="reset",
                    alignment=ui.Alignment.V_CENTER,
                    style=ui_c.STYLE_BUTTON_RESET_ON,
                    tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_RESET),
                )
                btn.visible = False
            ui.Spacer()

        item_value_model = multifloat.model.get_item_value_model(multifloat.model.get_item_children()[item_index])

        btn.set_mouse_pressed_fn(
            lambda x, y, z, w, value_model=item_value_model, b=btn: self._reset_field_value(value_model)
        )
        item_value_model.add_value_changed_fn(
            lambda value, default_value=0, button=btn: self._update_float_field_reset_button(
                value, default_value, button
            )
        )

        return btn

    def _build_reset_button(
        self, change_fn, default_value_to_compare, default_value_to_reset, reset_function
    ) -> ui.Rectangle:
        btn = None
        height_value = 12
        with ui.VStack(width=0, style={"margin": 0}):
            ui.Spacer()
            with ui.ZStack(width=12, height=height_value):
                with ui.HStack(width=12, height=height_value):
                    ui.Spacer(width=3)
                    with ui.VStack(width=12, height=height_value):
                        ui.Spacer()
                        ui.Rectangle(width=5, height=5, name="reset_invalid", style=ui_c.STYLE_BUTTON_RESET_OFF)
                        ui.Spacer()
                btn = ui.Rectangle(
                    width=12,
                    height=12,
                    name="reset",
                    alignment=ui.Alignment.V_CENTER,
                    style=ui_c.STYLE_BUTTON_RESET_ON,
                    tooltip_fn=lambda: self._create_tooltip(ui_c.TOOLTIP_BUTTON_RESET),
                    margin=0,
                )
                btn.visible = False
            ui.Spacer()

        btn.set_mouse_pressed_fn(lambda x, y, z, w: reset_function(default_value_to_reset))

        change_fn(lambda value, x=None: self._update_reset_button(value, default_value_to_compare, btn))

        return btn

    def _create_tooltip(self, text: str):
        with ui.ZStack(style=ui_c.STYLE_TOOLTIP):
            ui.Rectangle()
            ui.Label(text, style=ui_c.STYLE_TOOLTIP_TEXT)

    # ========================== Assign callbacks to UI elements =============================

    def _set_up_ui_elements_functionality(self):
        # Preview
        self.preview_button.set_clicked_fn(self._toggle_preview)

        # Counts
        def _register_drag_field_events(widget, update_fn, get_value, update_args: List = [], min_value=None):
            if min_value is not None:
                widget.model.add_value_changed_fn(lambda model: self._clamp_int_min(model, min_value))

            widget.model.add_value_changed_fn(lambda a: update_fn(get_value(widget.model), *update_args))

            # Allow drag field updates after single mouse press (drag),
            # but not on double-click (type edit) or no mouse button (e.g. tab into field)
            widget.set_mouse_pressed_fn(lambda a, b, c, d: self._set_allow_drag_field_updates(True))

            widget.set_mouse_double_clicked_fn(lambda a, b, c, d: self._set_allow_drag_field_updates(False))

            # Temporarily allow drag field updates on end edit
            widget.model.add_end_edit_fn(lambda a: self._set_allow_drag_field_updates(True))

            # Update value once more to catch type-edited value changes
            widget.model.add_end_edit_fn(lambda a: update_fn(get_value(widget.model), *update_args))

            # Lock drag field updates again
            widget.model.add_end_edit_fn(lambda a: self._set_allow_drag_field_updates(False))

        _register_drag_field_events(
            self.count_1d_widget,
            self._update_count,
            ui.SimpleIntModel.get_value_as_int,
            [
                [self.translate_1d_widget, self.rotate_1d_widget, self.scale_1d_widget],
                [a_c.TOT_TRANSLATE_TOGGLE, a_c.TOT_ROTATE_TOGGLE, a_c.TOT_SCALE_TOGGLE],
                a_c.COUNT,
                self._on_count_changed,
            ],
            1,
        )

        _register_drag_field_events(
            self.count_2d_widget,
            self._update_count,
            ui.SimpleIntModel.get_value_as_int,
            [
                [self.offset_2d_widget],
                [a_c.TOT_TWO_D_OFFSET_TOGGLE],
                a_c.TWO_D_COUNT,
                self._on_two_d_count_changed,
            ],
            1,
        )

        # checks changed 2D count value. if 1, disable 3D count widget and update core with default 3D count values
        self.count_2d_widget.model.add_end_edit_fn(lambda a: self._connect_2d_to_3d_count(a.get_value_as_int()))

        _register_drag_field_events(
            self.count_3d_widget,
            self._update_count,
            ui.SimpleIntModel.get_value_as_int,
            [
                [self.offset_3d_widget],
                [a_c.TOT_THREE_D_OFFSET_TOGGLE],
                a_c.THREE_D_COUNT,
                self._on_three_d_count_changed,
            ],
            1,
        )

        _register_drag_field_events(
            self.random_sequence_seed_field,
            self._update_random_seed,
            ui.SimpleIntModel.get_value_as_int,
        )

        # Vector Values
        def _register_multifield_events(self, widget, function):
            for i, child_item in enumerate(widget.model.get_item_children()):

                widget.model.get_item_value_model(child_item).add_value_changed_fn(
                    lambda value, col=i: function(value, col)
                )

                # Allow drag field updates after single mouse press (drag),
                # but not on double-click (type edit) or no mouse button (e.g. tab into field)
                widget.set_mouse_pressed_fn(lambda a, b, c, d: self._set_field_currently_drag_edited(True, True))

                widget.set_mouse_double_clicked_fn(
                    lambda a, b, c, d: self._set_field_currently_drag_edited(False, False)
                )

                # Temporarily allow drag field updates on end edit
                widget.model.get_item_value_model(child_item).add_end_edit_fn(
                    lambda a: self._set_field_currently_drag_edited(False, True)
                )

                # Update value once more to catch type-edited value changes
                widget.model.get_item_value_model(child_item).add_end_edit_fn(lambda value, col=i: function(value, col))

                # Lock drag field updates again
                widget.model.get_item_value_model(child_item).add_end_edit_fn(
                    lambda a: self._set_field_currently_drag_edited(False, False)
                )

        _register_multifield_events(self, self.translate_1d_widget, self._update_translate)
        _register_multifield_events(self, self.rotate_1d_widget, self._update_rotate)
        _register_multifield_events(self, self.scale_1d_widget, self._update_scale)
        _register_multifield_events(self, self.offset_2d_widget, self._update_offset_2d)
        _register_multifield_events(self, self.offset_3d_widget, self._update_offset_3d)

        # Uniform Scale
        self.linked_scale_button.set_clicked_fn(
            lambda: self._update_linked_scale_button(
                self.linked_scale_button,
                not self._array_core.get_array_value(a_c.LINKED_SCALE_TOGGLE),
            )
        )

        # Total Toggles
        self.translate_1d_total_button.set_clicked_fn(
            lambda: self._update_translate_total_mode_button(
                not self._array_core.get_array_value(a_c.TOT_TRANSLATE_TOGGLE)
            )
        )

        self.rotate_1d_total_button.set_clicked_fn(
            lambda: self._update_rotate_total_mode_button(not self._array_core.get_array_value(a_c.TOT_ROTATE_TOGGLE))
        )

        self.scale_1d_total_button.set_clicked_fn(
            lambda: self._update_scale_total_mode_button(not self._array_core.get_array_value(a_c.TOT_SCALE_TOGGLE))
        )

        self.offset_2d_total_button.set_clicked_fn(
            lambda: self._update_offset_2d_total_mode_button(
                not self._array_core.get_array_value(a_c.TOT_TWO_D_OFFSET_TOGGLE)
            )
        )

        self.offset_3d_total_button.set_clicked_fn(
            lambda: self._update_offset_3d_total_mode_button(
                not self._array_core.get_array_value(a_c.TOT_THREE_D_OFFSET_TOGGLE)
            )
        )

        # Radio Buttons
        self.create_type_collection.model.add_value_changed_fn(
            lambda value: self._update_create_type_setting(value.as_int + 1)
        )

        # Dropdowns
        self.array_type_dropdown.model.add_item_changed_fn(
            lambda value, x: self._update_array_type_setting(value.get_item_value_model().as_int + 1)
        )

        # Checkboxes
        self.group_results_checkbox.model.add_value_changed_fn(
            lambda value: self._update_group_results_checkbox(value.as_bool)
        )

        self.reorient_checkbox.model.add_value_changed_fn(lambda value: self._update_reorient_checkbox(value.as_bool))

        self.remember_values_checkbox.model.add_value_changed_fn(
            lambda value: self._update_remember_last_values_checkbox(value.as_bool)
        )

        self.autoselect_objects_checkbox.model.add_value_changed_fn(
            lambda value: self._update_autoselect_checkbox(value.as_bool)
        )

        # Buttons
        self.cancel_button.set_clicked_fn(self._on_close_clicked)

        self.reset_all_button.set_clicked_fn(self._on_reset_clicked)

        self.apply_button.set_clicked_fn(self._on_apply_clicked)

        self.random_button.set_clicked_fn(self._generate_random_seed)

    # ========================== UI Element Update Functions =============================

    def _toggle_preview(self):
        self._update_preview_button(not self._array_core.get_array_value(a_c.PREVIEW))

    def _update_preview_button(self, value=None):
        if value is None:
            value = self._array_core.get_array_value(a_c.PREVIEW)
        if value is True:
            self.preview_button.style = ui_c.STYLE_BUTTON_PREVIEW_ON
        else:
            self.preview_button.style = ui_c.STYLE_BUTTON_PREVIEW_OFF

        if self.skip_ui_callbacks:
            return

        self._on_preview_changed(value)

    def _update_count_1d(self, value=None, force_core_update: bool = False):
        if value is None:
            value = self._array_core.get_array_value(a_c.COUNT)
        self.count_1d_widget.model.set_value(value)

        if force_core_update:
            self._update_core_value(a_c.COUNT, value)

    def _update_count_2d(self, value=None, force_core_update: bool = False):
        if value is None:
            value = self._array_core.get_array_value(a_c.TWO_D_COUNT)
        self.count_2d_widget.model.set_value(value)

        if force_core_update:
            self._update_core_value(a_c.TWO_D_COUNT, value)

    def _update_count_3d(self, value=None, force_core_update: bool = False):
        if value is None:
            value = self._array_core.get_array_value(a_c.THREE_D_COUNT)
        self.count_3d_widget.model.set_value(value)

        if force_core_update:
            self._update_core_value(a_c.THREE_D_COUNT, value)

    # if 2d offset count is 1, disable 3d offset count and widget, and set core 3d count to 1
    # (but do not cache it in last array values)
    def _connect_2d_to_3d_count(self, value):
        if value == 1:
            self.count_3d_widget.enabled = False
            self.count_3d_widget.style = ui_c.STYLE_VECTOR_DISABLED
            self._update_core_value(a_c.THREE_D_COUNT, a_c.THREE_D_COUNT_DEFAULT, False)
            self._toggle_offset_widget_lock(
                self.offset_3d_widget, self._last_array_values[a_c.TOT_THREE_D_OFFSET_TOGGLE], True
            )
        else:
            self.count_3d_widget.enabled = True
            self.count_3d_widget.style = ui_c.STYLE_VECTOR_ENABLED
            if self._last_array_values[a_c.THREE_D_COUNT] > 1:
                self._toggle_offset_widget_lock(
                    self.offset_3d_widget, self._last_array_values[a_c.TOT_THREE_D_OFFSET_TOGGLE], False
                )
                self._update_core_value(a_c.THREE_D_COUNT, self._last_array_values[a_c.THREE_D_COUNT], True)

    def _toggle_offset_widget_lock(self, widget, total_toggle, lock: bool):
        widget_in_total_mode = total_toggle

        if lock:
            widget.enabled = False
            widget.style = ui_c.STYLE_VECTOR_DISABLED
        else:
            widget.enabled = True
            if widget_in_total_mode:
                widget.style = ui_c.STYLE_VECTOR_ENABLED_TOTAL_MODE
            else:
                widget.style = ui_c.STYLE_VECTOR_ENABLED

        # Check if associated vector is currently in total mode, and force value update
        if widget_in_total_mode:
            self._force_set_multi_values_changed(widget)

    def _update_count(
        self,
        value=None,
        widgets: List[ui.Widget] = None,
        total_toggle_params: List[bool] = None,
        param: str = None,
        on_changed_fn=None,
    ):
        if value is None:
            value = self._array_core.get_array_value(param)

        if self.skip_ui_callbacks or not self.allow_drag_field_updates:
            return

        if on_changed_fn is not None:
            on_changed_fn(value)

        # Enable or disable associated widgets if count is 1
        for i, w in enumerate(widgets):
            if value <= 1:
                self._toggle_offset_widget_lock(w, self._last_array_values[total_toggle_params[i]], True)
            else:
                self._toggle_offset_widget_lock(w, self._last_array_values[total_toggle_params[i]], False)

        # Get all current counts and enable/disable apply button accordingly
        total_count = (
            self._last_array_values[a_c.COUNT]
            + self._last_array_values[a_c.TWO_D_COUNT]
            + self._last_array_values[a_c.THREE_D_COUNT]
        )

        # Disable Apply button if total count is less than 4
        if total_count < 4:
            self.apply_button.enabled = False
        else:
            self.apply_button.enabled = True

    def _update_vector(self, value, col, param, total_param, count_param, changed_fn):
        new_value = Gf.Vec3d(self._array_core.get_array_value(param))

        is_in_total_mode = self._array_core.get_array_value(total_param)
        if is_in_total_mode and not self.skip_vector_conversion:
            new_value[col] = value.as_float / max(1, self._array_core.get_array_value(count_param) - 1)
        else:
            new_value[col] = value.as_float

        if self.skip_ui_callbacks or not self.allow_drag_field_updates:
            return

        changed_fn(new_value)

    def _update_translate(self, value, col):
        self._update_vector(
            value,
            col,
            a_c.INC_TRANSLATE,
            a_c.TOT_TRANSLATE_TOGGLE,
            a_c.COUNT,
            self._on_incremental_translate_changed,
        )

    def _update_rotate(self, value, col):
        self._update_vector(
            value,
            col,
            a_c.INC_ROTATE,
            a_c.TOT_ROTATE_TOGGLE,
            a_c.COUNT,
            self._on_incremental_rotate_changed,
        )

    def _update_scale(self, value, col):
        # Get copy of value to modify before reassigning
        new_values = Gf.Vec3d(self._array_core.get_array_value(a_c.INC_SCALE))
        value_update = value.as_float

        # do not continue update if update value is same as core value
        if new_values[col] == value_update:
            return

        # convert value to total mode if necessary
        is_in_total_mode = self._array_core.get_array_value(a_c.TOT_SCALE_TOGGLE)
        total_mode_factor = max(1, self._array_core.get_array_value(a_c.COUNT) - 1)

        # is scale in total mode?
        if is_in_total_mode:
            value_update = value_update / total_mode_factor

        # update new values
        new_values[col] = value_update
        # create widget values
        widget_values = new_values

        # is linked scale on?
        is_linked_scale_on = self._array_core.get_array_value(a_c.LINKED_SCALE_TOGGLE)

        update_widget_values = True

        # apply linked scale if necessary
        if is_linked_scale_on:
            ref = self._array_core.get_array_value(a_c.LINKED_SCALE)
            # update reference value if ref value was previously zero
            if new_values[col] != 0 and ref[col] == 0:
                update_widget_values = False
                if not self.field_currently_drag_edited:
                    self._update_linked_scale_reference(new_values)
                else:
                    # early out if field is being dragged starting at zero value.
                    # only update again next drag.
                    return

            # calculate multiplication factor for other two components and prevent divide by zero
            factor = new_values[col] / (ref[col] if ref[col] != 0 else 1)

            # update the other two widget values with linked values
            for i in range(3):
                if i != col:
                    new_values[i] = ref[i] * factor
                widget_values[i] = new_values[i]

        # conform widget values to total mode if necessary
        if is_in_total_mode:
            widget_values = Gf.Vec3d(tuple(v * total_mode_factor for v in widget_values))

        if not self.allow_drag_field_updates:
            return

        # update core values before updating widgets to avoid redundant core value updates
        if not self.skip_ui_callbacks:
            self._on_incremental_scale_changed(new_values)

        if update_widget_values:
            # update widget values
            self._set_multi_values(self.scale_1d_widget, widget_values)

    def _update_linked_scale_button(self, button: ui.Button, value=None):
        if value is None:
            value = self._array_core.get_array_value(a_c.LINKED_SCALE_TOGGLE)
            if value is None:
                value = False

        if value:
            # if linked scale toggled on, update core linked scale reference values
            self._update_linked_scale_reference()

            # update button style
            button.style = ui_c.STYLE_LINKED_BUTTON_ON
            # update label style
            self.scale_label.style = ui_c.STYLE_LABEL_SCALE_TOTAL
        else:
            # update button style
            button.style = ui_c.STYLE_LINKED_BUTTON_OFF
            # update label style
            self.scale_label.style = ui_c.STYLE_LABEL_SCALE

        if self.skip_ui_callbacks:
            return

        self._on_linked_scale_changed(value)

    # update linked scale reference values in core
    def _update_linked_scale_reference(self, value=None):
        # if no value is passed in, use current inc_scale to update reference value
        if value is None:
            current_inc_scale = self._array_core.get_array_value(a_c.INC_SCALE)
            # if current inc scale is all zeros, treat them as linked at same value
            if current_inc_scale == Gf.Vec3d(0):
                self._array_core.update_value(
                    a_c.LINKED_SCALE,
                    Gf.Vec3d(1),
                )
            # if current increment value is NOT all zeros, use as is
            else:
                self._array_core.update_value(
                    a_c.LINKED_SCALE,
                    Gf.Vec3d(self._array_core.get_array_value(a_c.INC_SCALE)),
                )
        else:
            self._array_core.update_value(a_c.LINKED_SCALE, Gf.Vec3d(value))

    def _update_offset_2d(self, value, col):
        self._update_vector(
            value,
            col,
            a_c.TWO_D_OFFSET,
            a_c.TOT_TWO_D_OFFSET_TOGGLE,
            a_c.TWO_D_COUNT,
            self._on_two_d_offset_changed,
        )

    def _update_offset_3d(self, value, col):
        self._update_vector(
            value,
            col,
            a_c.THREE_D_OFFSET,
            a_c.TOT_THREE_D_OFFSET_TOGGLE,
            a_c.THREE_D_COUNT,
            self._on_three_d_offset_changed,
        )

    def _update_translate_total_mode_button(self, value=None):
        self._update_total_mode_button(
            self.translate_1d_total_button,
            a_c.TOT_TRANSLATE_TOGGLE,
            value,
            self._on_total_translate_toggle_changed,
            self.translate_1d_widget,
        )

    def _update_rotate_total_mode_button(self, value=None):
        self._update_total_mode_button(
            self.rotate_1d_total_button,
            a_c.TOT_ROTATE_TOGGLE,
            value,
            self._on_total_rotate_toggle_changed,
            self.rotate_1d_widget,
        )

    def _update_scale_total_mode_button(self, value=None):
        self._update_total_mode_button(
            self.scale_1d_total_button,
            a_c.TOT_SCALE_TOGGLE,
            value,
            self._on_total_scale_toggle_changed,
            self.scale_1d_widget,
        )

    def _update_offset_2d_total_mode_button(self, value=None):
        self._update_total_mode_button(
            self.offset_2d_total_button,
            a_c.TOT_TWO_D_OFFSET_TOGGLE,
            value,
            self._on_total_offset_two_d_toggle_changed,
            self.offset_2d_widget,
        )

    def _update_offset_3d_total_mode_button(self, value=None):
        self._update_total_mode_button(
            self.offset_3d_total_button,
            a_c.TOT_THREE_D_OFFSET_TOGGLE,
            value,
            self._on_total_offset_three_d_toggle_changed,
            self.offset_3d_widget,
        )

    def _update_total_mode_button(self, button: ui.Button, param: str, value=None, function=None, row_widget=None):
        if value is None:
            value = self._array_core.get_array_value(param)
            if value is None:
                value = False

        if value:
            button.style = ui_c.STYLE_BUTTON_TOTAL_ON
            if row_widget is not None:
                if row_widget.enabled:
                    row_widget.style = ui_c.STYLE_VECTOR_ENABLED_TOTAL_MODE
        else:
            button.style = ui_c.STYLE_BUTTON_TOTAL_OFF
            if row_widget is not None:
                if row_widget.enabled:
                    row_widget.style = ui_c.STYLE_VECTOR_ENABLED

        if self.skip_ui_callbacks:
            return

        if function is not None:
            function(value)

    # Needs to do some int math to match ArrayParam enum values
    def _update_create_type_setting(self, value: int = None, check_instanceable: bool = True):
        if value is None:
            value = self._array_core.get_array_value(a_c.CREATE_TYPE).value
            self.create_type_collection.model.set_value(value - 1)
        elif type(value) is int:
            try:
                self.create_type_collection.model.set_value(value - 1)

                if self.skip_ui_callbacks:
                    return

                self._on_create_type_changed(value)
            except ValueError:
                carb.log_warn(f"{value} is out of {a_c.CreateType} enum range")
        elif type(value) is a_c.CreateType:
            self.create_type_collection.model.set_value(value.value - 1)

            if self.skip_ui_callbacks:
                return

            self._on_create_type_changed(value)

        # Check for instanceable prims when the create type setting changes
        if check_instanceable:
            prims = self._get_prims_from_selected_paths()
            filtered_prims = self._check_instanceable_prims(prims)
            self._array_core.update_target_prims(filtered_prims)

    # Needs to do some int math to match ArrayParam enum values
    def _update_array_type_setting(self, value: int = None):
        if value is None:
            value = self._array_core.get_array_value(a_c.ARRAY_TYPE).value
            self.array_type_dropdown.model.get_item_value_model().set_value(value - 1)
        elif type(value) is int:
            try:
                self.array_type_dropdown.model.get_item_value_model().set_value(value - 1)

                if self.skip_ui_callbacks:
                    return

                self._on_array_type_changed(a_c.ArrayType(value))
            except ValueError:
                carb.log_warn(f"{value} is out of {a_c.ArrayType} enum range")
        elif type(value) is a_c.ArrayType:
            self.array_type_dropdown.model.get_item_value_model().set_value(value.value - 1)

        self._update_random_sequence_seed_field()

        if self.skip_ui_callbacks:
            return

        self._on_array_type_changed(value)

    def _update_random_seed(self, value=None):
        if value is None:
            value = self._array_core.get_array_value(a_c.RANDOM_ORDER_SEED)
        self.random_sequence_seed_field.model.set_value(value)

        if self.skip_ui_callbacks or not self.allow_drag_field_updates:
            return

        if value != self._array_core.get_array_value(a_c.RANDOM_ORDER_SEED):
            self._on_random_seed_changed(value)

    def _update_random_sequence_seed_field(self):
        if self._array_core.get_array_value(a_c.ARRAY_TYPE) == a_c.ArrayType.RANDOM_SEQUENCE:
            self.random_sequence_seed_field.enabled = True
            self.random_button.enabled = True
        else:
            self.random_sequence_seed_field.enabled = False
            self.random_button.enabled = False

    def _generate_random_seed(self):
        self._set_allow_drag_field_updates(True)
        # generate a random seed. could possibly use sys.maxsize, but huge numbers may be less pretty for user.
        self._update_random_seed(random.randrange(99999))
        self._set_allow_drag_field_updates(False)

    def _update_checkbox(self, checkbox, param, changed_fn, value=None):
        if value is None:
            value = self._array_core.get_array_value(param)
        checkbox.model.set_value(value)

        if self.skip_ui_callbacks:
            return

        changed_fn(value)

    def _update_group_results_checkbox(self, value=None):
        self._update_checkbox(
            self.group_results_checkbox, a_c.ARRAY_GROUP_RESULT, self._on_array_group_result_changed, value
        )

    def _update_reorient_checkbox(self, value=None):
        self._update_checkbox(self.reorient_checkbox, a_c.REORIENT_ROTATION, self._on_reorient_changed, value)

    def _update_remember_last_values_checkbox(self, value=None):
        pass

    # self._update_checkbox(self.remember_values_checkbox, ui_c.REMEMBER_LAST_DEFAULT, self._on_remember_last_changed, value)

    def _update_autoselect_checkbox(self, value=None):
        self._update_checkbox(
            self.autoselect_objects_checkbox, a_c.AUTO_SELECT_CREATED, self._on_auto_select_created_changed, value
        )

    def _update_float_field_reset_button(self, value, default_value, btn):
        btn.visible = value.as_float != default_value

    def _reset_field_value(self, value_model: ui.AbstractValueModel):
        self._set_allow_drag_field_updates(True)
        value_model.set_value(0)
        self._set_allow_drag_field_updates(False)

    def _update_reset_button(self, value, default_value, btn):
        if type(value) is ui.AbstractItemModel:
            value = value.get_item_value_model()

        if type(default_value) is bool:
            value = value.as_bool
        elif type(default_value) is int:
            value = value.as_int
        elif type(default_value) is float:
            value = value.as_float

        btn.visible = value != default_value

    # ========================== Utility Functions =============================

    def _convert_vector_to_total_mode(self, param: str, count: int) -> Gf.Vec3d:
        return Gf.Vec3d(self._array_core.get_array_value(param)) * max(1, (count - 1))

    def _convert_vector_to_incremental_mode(self, param: str, count: int) -> Gf.Vec3d:
        return Gf.Vec3d(self._array_core.get_array_value(param)) / max(1, (count - 1))

    def _clamp_int_min(self, model: ui.SimpleIntModel, min_value=0):
        if model.get_value_as_int() < min_value:
            model.set_value(min_value)

    def _force_set_multi_values_changed(self, multifield: ui.MultiFloatDragField):
        for i in range(3):
            value_model = multifield.model.get_item_value_model(multifield.model.get_item_children()[i])
            value_model._value_changed()

    def _set_multi_values(self, multifield: ui.MultiFloatDragField, vec3d: Gf.Vec3d() = Gf.Vec3d(0, 0, 0)):
        for i in range(3):
            value_model = multifield.model.get_item_value_model(multifield.model.get_item_children()[i])
            value_model.set_value(vec3d[i])

    def _get_multi_values_from_model(self, multifield_model: ui.AbstractItemModel) -> Gf.Vec3d():
        if multifield_model is None:
            return None

        multivalues = Gf.Vec3d(
            multifield_model.get_item_value_model(multifield_model.get_item_children()[0]).as_float,
            multifield_model.get_item_value_model(multifield_model.get_item_children()[1]).as_float,
            multifield_model.get_item_value_model(multifield_model.get_item_children()[2]).as_float,
        )

        return multivalues

    def _get_multi_values(self, multifield_widget: ui.MultiFloatDragField) -> Gf.Vec3d():
        if multifield_widget is None:
            return None

        multivalues = self._get_multi_values_from_model(multifield_widget.model)

        return multivalues

    def _set_skip_lock(self, value: bool):
        self.skip_lock = value

    def _set_skip_ui_callbacks(self, value: bool):
        if not self.skip_lock:
            self.skip_ui_callbacks = value

    def _set_allow_drag_field_updates(self, value: bool = None):
        if not self.skip_lock:
            self.allow_drag_field_updates = value

    def _set_field_currently_drag_edited(self, currently_drag_edited, allow_drag_field_updates):
        self.field_currently_drag_edited = currently_drag_edited
        self._set_allow_drag_field_updates(allow_drag_field_updates)

    def _update_core_value(self, param_name, value, update_last_array_value: bool = True):
        if value != self._array_core.get_array_value(param_name):
            self._array_core.update_value(param_name, value)
            if update_last_array_value:
                self._last_array_values.update({param_name: value})

            # print(f"{param_name} changed to {self._array_core.get_array_value(param_name)}")

    def _update_row_total_or_incremental_mode(self, value, inc_param, count, widget):
        # Update UI with newly converted values
        if value:
            new_value = self._convert_vector_to_total_mode(inc_param, count)
        else:
            new_value = self._array_core.get_array_value(inc_param)

        # Update widget values without updating array core values
        self._set_skip_ui_callbacks(True)
        self._set_multi_values(widget, new_value)
        self._set_skip_ui_callbacks(False)

    def _get_prims_from_selected_paths(self):
        prims = []
        prims = [self._stage.GetPrimAtPath(path) for path in self._selection.get_selected_prim_paths()]
        return prims
