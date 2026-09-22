# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["LayerWindow"]
from .layer_delegate import LayerDelegate
from .layer_icons import LayerIcons
from .layer_model import LayerModel, LayerItem, PrimSpecItem
from .layer_model_utils import LayerModelUtils
from .layer_settings import LayerSettings
from .layer_color_scheme import LayerColorScheme
from .layer_option_button import LayerOptionsButton, LayerOptionItem
from .selection_watch import SelectionWatch
from .models.save_all_model import SaveAllModel
from .models.layer_scope_model import LayerScopeModel
from .models.layer_auto_authoring import LayerAutoAuthoringModel
from .external_drag_drop_helper import setup_external_drag_drop, destroy_external_drag_drop
from omni.kit.usd.layers import LayerUtils
from enum import Enum
from functools import partial
from pxr import Sdf

import asyncio
import carb
import carb.settings
import omni
import omni.ui as ui
import weakref
import omni.kit.usd.layers as layers
import omni.kit.notification_manager as nm
from omni.kit.widget.searchfield import SearchField

class LiveSessionButtonOptions(Enum):
    QUIT_ONLY = 0
    MERGE_AND_QUIT = 1


class LayerWindow:
    """The Layer 2 window"""

    def __init__(self, window_name, usd_context):
        self._handling_mode_change = False
        self._settings = carb.settings.get_settings()
        self._visiblity_changed_listener = None
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
        self._window = ui.Window(
            window_name, width=600, height=800, flags=window_flags, dockPreference=ui.DockPreference.RIGHT_TOP
        )

        self._window.set_visibility_changed_fn(self._visibility_changed_fn)
        self._window.deferred_dock_in("Stage", ui.DockPolicy.TARGET_WINDOW_IS_ACTIVE)
        self._window.dock_order = 1

        self._usd_context = usd_context
        self._layers = layers.get_layers(self._usd_context)
        self._layers_state = layers.get_layers_state(self._usd_context)
        self._model = LayerModel(self._usd_context)
        weakref_model = weakref.ref(self._model)
        self._delegate = LayerDelegate(self._usd_context)
        self._save_all_model = SaveAllModel(self._model)
        self._layer_scope_model = LayerScopeModel(self._model)
        self._auto_authoring_model = LayerAutoAuthoringModel(self._model)
        self._model.add_dirtiness_listener(self._on_dirtiness_changed)
        self._model.add_layer_muteness_scope_listener(self._on_muteness_scope_changed)
        self._model.add_stage_attach_listener(self._on_stage_attached)

        self._layers_event_subs = []
        for event in [
            layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
            layers.LayerEventType.EDIT_MODE_CHANGED,
        ]:
            layers_event_sub = self._layers.get_event_stream().create_subscription_to_pop_by_type(
                event, self._on_layer_events, name=f"Layers Window {str(event)}"
            )
            self._layers_event_subs.append(layers_event_sub)

        style = {
            "Image::avartar": {"image_url": LayerIcons().get("avartar")},
            "Image::drop_down": {"image_url": LayerIcons().get("drop_down")},
            "Image::layers_lightning": {"image_url": LayerIcons().get("lightning"), "color": 0xFF00FFFF},
            "Image::layer_auto_authoring": {"image_url": LayerIcons().get("layers")},
            "Image::layers": {"image_url": LayerIcons().get("layers")},
            "Image::layers_outdate": {"image_url": LayerIcons().get("layers"), "color": 0xFF0097FF},
            "Image::layers_edit_target": {"image_url": LayerIcons().get("layers"), "color": 0xFF57B44D},
            "Image::layers_edit_target:selected": {"image_url": LayerIcons().get("layers"), "color": 0xFF10781A},
            "Image::layers_live_sync": {"image_url": LayerIcons().get("live_syncing")},
            "Image::layers_live_sync:selected": {"image_url": LayerIcons().get("live_syncing"), "color": 0xFF10781A},
            "Image::layers_missing": {"image_url": LayerIcons().get("layers"), "color": LayerColorScheme().LAYER_LABEL_MISSING},
            "Image::layers_missing:selected": {"image_url": LayerIcons().get("layers"), "color": LayerColorScheme().LAYER_LABEL_MISSING},
            "Image::layers_has_child_edit_target": {"image_url": LayerIcons().get("layers_half_green")},
            "Image::layer_read_only_lock": {"image_url": LayerIcons().get("layer_read_only_lock")},
            "Button.Image::filter": {"image_url": LayerIcons().get("filter"), "color": 0xFF8A8777},
            "Button.Image::options": {"image_url": LayerIcons().get("options"), "color": 0xFF8A8777},
            "Button.Image::layer_save": {"image_url": LayerIcons().get("layer_save")},
            "Button.Image::layer_save:checked": {"image_url": LayerIcons().get("layer_save")},
            "Button.Image::layer_scope": {"image_url": LayerIcons().get("layers_switch_local")},
            "Button.Image::layer_scope:checked": {"image_url": LayerIcons().get("layers_switch_global")},
            "Button.Image::layerdelete": {"image_url": LayerIcons().get("trash"), "color": 0xFFFFFFFF},
            "Button.Image::layerinsert": {"image_url": LayerIcons().get("insert_layer"), "color": 0xFFFFFFFF},
            "Button.Image::layeradd": {"image_url": LayerIcons().get("new_layer"), "color": 0xFFFFFFFF},
            "Button.Image::dirty": {"image_url": LayerIcons().get("layer_save"), "color": 0xFFB0B0B0},
            "Button.Image::dirty_selected": {"image_url": LayerIcons().get("layer_save"), "color": 0xFF575757},
            "Button.Image::dirty_readonly": {"image_url": LayerIcons().get("layer_read_only")},
            "Button.Image::dirty:checked": {"image_url": LayerIcons().get("layer_save"), "color": 0xFFFFBF00},
            "Button.Image::dirty_selected:checked": {"image_url": LayerIcons().get("layer_save"), "color": 0xFF8B622D},
            "Button.Image::live_update": {"image_url": LayerIcons().get("lightning"), "color": 0xFFA0A0A0},
            "Button.Image::live_update:checked": {"image_url": LayerIcons().get("lightning"), "color": 0xFF00B86B},
            "Button.Image::lock": {"image_url": LayerIcons().get("lock_open")},
            "Button.Image::lock:checked": {"image_url": LayerIcons().get("lock"), "color": 0xFFFF901E},
            "Button.Image::muteness_enable": {"image_url": LayerIcons().get("eye_on")},
            "Button.Image::muteness_enable:checked": {"image_url": LayerIcons().get("eye_off")},
            "Button.Image::muteness_enable:selected": {"color": 0xFFFFFFFF},
            "Button.Image::muteness_disable": {"image_url": LayerIcons().get("eye_on"), "color": 0xFFA0A0A0},
            "Button.Image::muteness_disable:checked": {
                "image_url": LayerIcons().get("eye_off"),
                "color": 0xFFB0B0B0,
            },
            "Button.Image::muteness_disable:selected": {"color": 0xFF23211F},
            "Button::filter": {"background_color": 0x0, "margin": 0},
            "Button::options": {"background_color": 0x0, "margin": 0},
            "Button::options:hovered": {"background_color": 0x0, "margin": 0},
            "Button::layer_save": {"background_color": 0x0, "margin": 0},
            "Button::layer_save:checked": {"background_color": 0x0, "margin": 0},
            "Button::layer_save:pressed": {"background_color": 0x0, "margin": 0},
            "Button::layer_save:hovered": {"background_color": 0x0, "margin": 0},
            "Button::layer_scope": {"background_color": 0x0, "margin": 0},
            "Button::layer_scope:checked": {"background_color": 0x0, "margin": 0},
            "Button::layer_scope:pressed": {"background_color": 0x0, "margin": 0},
            "Button::layer_scope:hovered": {"background_color": 0x0, "margin": 0},
            "Button::layerdelete": {"background_color": 0x0, "margin": 0},
            "Button::layerinsert": {"background_color": 0x0, "margin": 0},
            "Button::layeradd": {"background_color": 0x0, "margin": 0},
            "Button::dirty": {"background_color": 0x0, "margin": 0},
            "Button::dirty_selected": {"background_color": 0x0, "margin": 0},
            "Button::dirty:checked": {"background_color": 0x0},
            "Button::dirty_selected:checked": {"background_color": 0x0},
            "Button::dirty_readonly": {"background_color": 0x0, "margin": 0},
            "Button::dirty_readonly:checked": {"background_color": 0x0},
            "Button::dirty_readonly:pressed": {"background_color": 0x0},
            "Button::lock": {"background_color": 0x0, "margin": 0},
            "Button::lock:checked": {"background_color": 0x0},
            "Button::lock:hovered": {"background_color": 0x0},
            "Button::lock:pressed": {"background_color": 0x0},
            "Button::muteness_enable": {"background_color": 0x0, "margin": 0},
            "Button::muteness_enable:checked": {"background_color": 0x0},
            "Button::muteness_enable:hovered": {"background_color": 0x0},
            "Button::muteness_enable:pressed": {"background_color": 0x0},
            "Button::muteness_disable": {"background_color": 0x0, "margin": 0},
            "Button::muteness_disable:checked": {"background_color": 0x0},
            "Button::muteness_disable:hovered": {"background_color": 0x0},
            "Button::muteness_disable:pressed": {"background_color": 0x0},
            "Button::live_update": {"background_color": 0x0, "margin": 0},
            "Button::live_update:checked": {"background_color": 0x0},
            "Button::live_update:hovered": {"background_color": 0x0},
            "Button::live_update:pressed": {"background_color": 0x0},
            "Label::search": {"color": 0xFF808080, "margin_width": 4},
            "Label::auto_authoring_off": {"color": 0xFF4B4BB0, "font_size": 14},
            "Label::auto_authoring_on": {"color": 0xFF00B775, "font_size": 14},
            "Rectangle::edit_target": {"background_color": 0xFF3E652F},
            "Rectangle::edit_target_with_corner": {"background_color": 0xFF3E652F, "border_radius": 4},
            "Rectangle::edit_layer_with_corner": {"background_color": 0xFF12697B, "border_radius": 4},
            "Rectangle::normal": {"background_color": 0xFF444444},
            "Rectangle::selected": {"background_color": 0x0},
            "Rectangle::hovering": {"background_color": 0x0, "border_radius": 2, "margin": 0, "padding": 0},
            "Rectangle::hovering:hovered": {"background_color": 0xFF9E9E9E},
            "TreeView": {
                "background_color": 0xFF23211F,
                "background_selected_color": 0x664F4D43,
                "secondary_color": 0x0,
                "secondary_selected_color": 0x0,
                "border_width": 1.5,
            },
            "LayerView.ScrollingFrame": {"background_color": 0xFF23211F},
            "LayerView.Header": {"background_color": 0xFF343432, "color": 0xFFCCCCCC, "font_size": 13.0},
            "LayerView.Image::object_icon_grey": {"color": 0x80FFFFFF},
            "LayerView.Item": {"color": LayerColorScheme().LAYER_LABEL_NORMAL},
            "LayerView.Item::object_name_grey": {"color": LayerColorScheme().LAYER_LABEL_DISABLED},
            "LayerView.Item::object_name_missing": {"color": LayerColorScheme().LAYER_LABEL_MISSING},
            "LayerView.Item::object_name_missing:selected": {"color": LayerColorScheme().LAYER_LABEL_MISSING_SELECTED},
            "LayerView.Item:selected": {"color": 0xFFFFFFFF},
            "LayerView.Item::object_name_outdated": {"color": LayerColorScheme().OUTDATED},
            "LayerView.Item::object_name_outdated:selected": {"color": LayerColorScheme().OUTDATED},

            "LayerView.Item::edit_target": {"color": 0xFFFFFFFF},
            "LayerView:selected": {"background_color": 0xFF8A8777},
            "TreeView:drop": {
                "background_color": ui.color.shade(ui.color("#34C7FF3B")),
                "background_selected_color": ui.color.shade(ui.color("#34C7FF3B")),
                "border_color": ui.color.shade(ui.color("#2B87AA")),
            },
            "Button.Image::merge_down": {"image_url": LayerIcons().get("merge_down"), "color": 0xFFB0B0B0},
            "Button.Image::merge_down_selected": {"image_url": LayerIcons().get("merge_down"), "color": 0xFF575757},
            "Button.Image::merge_down:checked": {"image_url": LayerIcons().get("merge_down"), "color": 0xFFFFC118},
            "Button.Image::merge_down_selected:checked": {"image_url": LayerIcons().get("merge_down"), "color": 0xFFFFC118},
            "Button::merge_down": {"background_color": 0x0, "margin": 0},
            "Button::merge_down:checked": {"background_color": 0x0},
            "Button::merge_down:hovered": {"background_color": 0x0},
            "Button::merge_down:pressed": {"background_color": 0x0},
            "Button::merge_down_selected": {"background_color": 0x0, "margin": 0},
            "Button::merge_down_selected:checked": {"background_color": 0x0},
            "Button::merge_down_selected:hovered": {"background_color": 0x0},
            "Button::merge_down_selected:pressed": {"background_color": 0x0},

            "Button.Image::auto_authoring": {"image_url": LayerIcons().get("layers")},
            "Button::auto_authoring": {"background_color": 0x0, "margin": 0},
            "Button::auto_authoring:checked": {"background_color": 0x0},
            "Button::auto_authoring:hovered": {"background_color": 0x0},
            "Button::auto_authoring:pressed": {"background_color": 0x0},

            "Button.Image::latest": {"image_url": LayerIcons().get("reload_dark"), "color": 0xFFB0B0B0},
            "Button.Image::latest:checked": {"image_url": LayerIcons().get("reload_dark"), "color": LayerColorScheme().OUTDATED},
            "Button::latest": {"background_color": 0x0, "margin": 0},
            "Button::latest:checked": {"background_color": 0x0},
            "Button::latest:hovered": {"background_color": 0x0},
            "Button::latest:pressed": {"background_color": 0x0},
        }

        use_default_style = carb.settings.get_settings().get_as_string("/persistent/app/window/useDefaultStyle") or False
        if use_default_style:
            style = {}
        with self._window.frame:
            with ui.VStack(spacing=3, style=style):
                with ui.ZStack(height=0):
                    with ui.HStack():
                        # Search field
                        with ui.VStack(height=0):
                            ui.Spacer(height=4)
                            self._search = SearchField(
                                width=ui.Fraction(1), height=20,
                                on_search_fn=lambda filters: self._filter_by_text("".join(filters) if filters else ""),
                                show_tokens=False, separator=None
                            )
                            ui.Spacer(height=4)

                        # Delta button
                        with ui.HStack(width=0):
                            with ui.ZStack(width=0, height=0):
                                with ui.VStack(width=0, height=0):
                                    ui.Spacer()
                                    with ui.HStack(width=24, height=0):
                                        ui.Spacer()
                                        with ui.VStack(width=0, height=0):
                                            self._auto_authoring_image = ui.ToolButton(
                                                self._auto_authoring_model, name="auto_authoring", width=24, height=24
                                            )
                                        ui.Spacer()
                                    self._auto_authoring_image.set_tooltip(
                                        "Auto Authoring Mode (Experimental)\n\n"
                                        "Under auto authoring mode, all edits will be automatically forwarded to\n"
                                        "the layer that has the strongest opinion to ease the burden of working with\n"
                                        "multiple sublayers to manage delta changes."
                                    )

                                with ui.VStack(height=0):
                                    ui.Spacer(height=20)
                                    self._auto_authoring_label = ui.Label(
                                        "AA", style={"font_size": 12}, height=0, alignment=omni.ui.Alignment.CENTER
                                    )

                        # Options button
                        with ui.HStack(width=0, height=0):
                            ui.Spacer(width=2)
                            with ui.VStack(height=0):
                                ui.Spacer(height=4)
                                with ui.ZStack(width=20, height=20):
                                    ui.Rectangle(name="hovering")
                                    self._save_all_button = ui.ToolButton(self._save_all_model, name="dirty")
                                ui.Spacer(height=4)
                            ui.Spacer(width=2)
                        with ui.HStack(width=48, spacing=0):
                            ui.Spacer()
                            scope_button = ui.ToolButton(
                                self._layer_scope_model, name="layer_scope", width=48, height=28
                            )
                            scope_button.set_tooltip("Switch L/G to persist muteness or not. (Mode G for save)")
                            ui.Spacer()

                        with ui.HStack(width=24, height=0):
                            ui.Spacer()
                            with ui.VStack(width=0, height=0):
                                ui.Spacer(height=4)
                                self._option_button = LayerOptionsButton(self._on_reload_layers)
                                self.__sub_options = self._option_button.model.subscribe_item_changed_fn(self.__on_option_changed)
                                ui.Spacer(height=4)
                            ui.Spacer()

                        # Place holder to align buttons
                        ui.Spacer(width=24)
                        ui.Spacer(width=16, height=0)
                with ui.ScrollingFrame(
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    style_type_name_override="LayerView.ScrollingFrame",
                ):
                    self._layer_view = ui.TreeView(
                        self._model,
                        delegate=self._delegate,
                        column_widths=[ui.Fraction(1), 24, 24, 24, 24, 24, 26],
                        header_visible=False,
                        root_visible=False,
                        drop_between_items=True,
                    )

                self._delegate.set_tree_view(self._layer_view)
                weakref_treeview = weakref.ref(self._layer_view)
                with ui.ScrollingFrame(
                    height=32,
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    style_type_name_override="LayerView.ScrollingFrame",
                ):
                    with ui.HStack(height=0):
                        ui.Spacer()
                        button = ui.Button(
                            width=32,
                            height=32,
                            name="layerinsert",
                            clicked_fn=lambda: self._toolbar_action(weakref_treeview, weakref_model, 0),
                        )
                        button.set_tooltip("Insert Sublayer")
                        button = ui.Button(
                            width=32,
                            height=32,
                            name="layeradd",
                            clicked_fn=lambda: self._toolbar_action(weakref_treeview, weakref_model, 1),
                        )
                        button.set_tooltip("Create Sublayer")
                        with ui.VStack(width=0):
                            button = ui.Button(
                                width=32,
                                height=32,
                                name="layerdelete",
                                clicked_fn=lambda: self._toolbar_action(weakref_treeview, weakref_model, 2),
                            )
                            button.set_tooltip("Remove Sublayer")
                        ui.Spacer()

        self._selection = SelectionWatch(self._usd_context, self._layer_view, self._delegate)

        self._update_save_all_button()
        self._update_delta_button()

    def _update_delta_button(self):
        edit_mode = self._layers.get_edit_mode()
        if edit_mode == layers.LayerEditMode.NORMAL:
            self._auto_authoring_image.set_style({})
        else:
            self._auto_authoring_image.set_style({"color": LayerColorScheme().LAYER_LIVE_MODE_BUTTON_ENABLED})

    def _visibility_changed_fn(self, visible):
        if self._visiblity_changed_listener:
            self._visiblity_changed_listener(visible)

        if not visible:
            self._layer_view.selection = []
            self._selection.destroy()
            self._selection = None
        else:
            self._selection = SelectionWatch(self._usd_context, self._layer_view, self._delegate)

    def set_visibility_changed_listener(self, listener):
        self._visiblity_changed_listener = listener

    @property
    def layer_view(self):
        return self._layer_view

    def destroy(self):
        """
        Called by extension before destroying this object. It doesn't happen automatically.
        Without this hot reloading doesn't work.
        """
        self._handling_mode_change = False
        self._auto_authoring_image = None
        self._visiblity_changed_listener = None
        self._layers_event_subs = []
        if self._layer_view:
            self._layer_view.set_mouse_pressed_fn(None)
        self._layer_view = None
        if self._search:
            self._search.destroy()
            self._search = None
        self._save_all_button = None
        self._auto_authoring_label = None

        self.__sub_options = None
        self._option_button.destroy()

        if self._model:
            self._model.destroy()
            self._model = None

        if self._save_all_model:
            self._save_all_model.destroy()
            self._save_all_model = None

        if self._layer_scope_model:
            self._layer_scope_model.destroy()
            self._layer_scope_model = None

        if self._auto_authoring_model:
            self._auto_authoring_model.destroy()
            self._auto_authoring_model = None

        self._window = None
        if self._selection:
            self._selection.destroy()
            self._selection = None
        if self._delegate:
            self._delegate.destroy()
        self._delegate = None
        destroy_external_drag_drop()

    def _clear_filter_types(self):
        self.animations_menu.checked = False
        self.audio_menu.checked = False
        self.cameras_menu.checked = False
        self.lights_menu.checked = False
        self.materials_menu.checked = False

    def __on_option_changed(self, model, item: LayerOptionItem):
        if item:
            if item.name == "Auto Authoring Layers (Experimental)":
                if self._handling_mode_change:
                    return
                self._handling_mode_change = True

                self._option_button.set_item_value("Spec Linking Mode (Experimental)", False)
                item.update_value()
                LayerModelUtils.set_auto_authoring_mode(self._model, item.value)

                self._handling_mode_change = False
            elif item.name == "Spec Linking Mode (Experimental)":
                if self._handling_mode_change:
                    return
                self._handling_mode_change = True

                # Here do not update item value because we do not want to save this settings in persistent
                if item.value:
                    self._option_button.set_item_value("Auto Authoring Layers (Experimental)", False)
                    edit_mode = layers.LayerEditMode.SPECS_LINKING
                else:
                    edit_mode = layers.LayerEditMode.NORMAL
                self._layers.set_edit_mode(edit_mode)

                self._handling_mode_change = False
            else:
                item.update_value()
                if item.name == "Auto Reload Layers" and item.value:
                    self._on_reload_layers()
                if item.name in ["Auto Reload Layers", "Show Layer Contents", "Show Session Layer", "Show MetricsAssembler Layer"]:
                    self._model.refresh()

    def _on_reload_layers(self):
        self._layers_state.reload_outdated_sublayers()

    @staticmethod
    def _set_widget_visible(widget: ui.Widget, visible):
        """Utility for using in lambdas"""
        widget.visible = visible

    def _filter_by_text(self, filter_text: str):
        """Set the search filter string to the models and widgets"""
        layer_view = self._layer_view
        layer_view.visible = True
        layer_view.keep_alive = not not filter_text
        layer_view.keep_expanded = not not filter_text
        layer_view.model.filter_by_text(filter_text)

        self._delegate.set_highlighting(text=filter_text)

    def _update_save_all_button(self):
        if not self._model.root_layer_item:
            return

        is_in_live_session = self._model.root_layer_item.is_in_live_session
        if is_in_live_session:
            self._save_all_button.set_tooltip("Cannot save Layer edits in Live Session.")
        else:
            self._save_all_button.set_tooltip("Save all Layer edits")

        if not is_in_live_session and self._save_all_model.get_value_as_bool():
            self._save_all_button.enabled = True
            self._save_all_button.checked = True
        else:
            self._save_all_button.enabled = False
            self._save_all_button.checked = False

    def _on_dirtiness_changed(self):
        self._update_save_all_button()

    def _is_selection_from_same_layer(self, selection):
        if not selection:
            return None

        item = selection[0]
        if isinstance(item, LayerItem):
            layer_item = item
        elif isinstance(item, PrimSpecItem):
            layer_item = item.layer_item
        else:
            layer_item = None

        for i in range(1, len(selection)):
            if isinstance(selection[i], LayerItem):
                item = selection[i]
            elif isinstance(selection[i], PrimSpecItem):
                item = selection[i].layer_item

            if layer_item != item:
                return None

        return layer_item

    # action == 0: insert
    # action == 1: create
    # action == 2: delete
    def _toolbar_action(self, weakref_treeview: weakref, weakref_model: weakref, action: int):
        tree_view = weakref_treeview()
        model = weakref_model()
        if not tree_view or not model:
            return

        selection = tree_view.selection
        if action == 2:
            to_remove_layer_items = []
            for item in selection:
                if isinstance(item, LayerItem):
                    to_remove_layer_items.append(item)

            if len(to_remove_layer_items) > 1:
                LayerModelUtils.remove_layers(to_remove_layer_items)
            if len(to_remove_layer_items) == 1:
                LayerModelUtils.remove_layer(to_remove_layer_items[0])
        else:
            layer_item = self._is_selection_from_same_layer(selection)
            # By default, it will insert layer for root layer
            if not layer_item or layer_item.reserved:
                if layer_item and layer_item == model.session_layer_item:
                    parent_item = model.session_layer_item
                else:
                    parent_item = model.root_layer_item
                sublayer_position = 0
            elif layer_item and layer_item.parent:
                if layer_item.is_in_live_session:
                    layer_item = layer_item.live_session_layer

                parent_item = layer_item.parent
                sublayer_position = LayerUtils.get_sublayer_position_in_parent(
                    parent_item.identifier, layer_item.identifier
                )
            else:
                parent_item = model.root_layer_item
                sublayer_position = 0

            if action == 0:
                LayerModelUtils.insert_sublayer(parent_item, sublayer_position)
            elif action == 1:
                LayerModelUtils.create_sublayer(parent_item, sublayer_position)

    def _on_muteness_scope_changed(self):
        self._layer_scope_model._value_changed()

    def _on_stage_attached(self, attached: bool):
        if attached:
            self._update_save_all_button()
            self._delegate.on_stage_attached()
            self._layer_scope_model._value_changed()
        else:
            # https://nvidia-omniverse.atlassian.net/browse/OM-29539
            # It must clear selection to notify listeners.
            self._layer_view.selection = []

        setup_external_drag_drop("Layer", self._model)

    def _on_layer_events(self, events):
        payload = layers.get_layer_event_payload(events)
        if not payload:
            return

        if payload.event_type == layers.LayerEventType.EDIT_MODE_CHANGED:
            edit_mode = self._layers.get_edit_mode()
            self._handling_mode_change = True
            self._option_button.set_item_value("Auto Authoring Layers (Experimental)", edit_mode == layers.LayerEditMode.AUTO_AUTHORING)
            self._option_button.set_item_value("Spec Linking Mode (Experimental)", edit_mode == layers.LayerEditMode.SPECS_LINKING)
            self._handling_mode_change = False
            self._update_delta_button()
        elif payload.event_type == layers.LayerEventType.LIVE_SESSION_STATE_CHANGED:
            if not self._model.root_layer_item:
                return

            is_live_mode = self._model.root_layer_item.is_in_live_session
            if is_live_mode:
                self._option_button.set_item_value("Show Session Layer", True)
            self._layer_view.set_expanded(self._model.session_layer_item, is_live_mode, False)
            self._layer_view.set_expanded(self._model.root_layer_item, not is_live_mode, False)
            self._update_save_all_button()

    def get_layer_model(self):
        return self._model

    def remove_layer_selection_changed_fn(self, fn):
        if self._selection:
            self._selection.remove_layer_selection_changed_fn(fn)

    def add_layer_selection_changed_fn(self, fn):
        if self._selection:
            self._selection.add_layer_selection_changed_fn(fn)

    def get_current_focused_layer_item(self):
        if self._selection:
            return self._selection.get_current_focused_layer_item()
        else:
            return None

    def set_current_focused_layer_item(self, layer_identifier):
        if not self._model or not self._selection:
            return

        layer_item = self._model.get_layer_item_by_identifier(layer_identifier)
        self._selection.set_current_focused_layer_item(layer_item)

    def set_visible(self, value):
        self._window.visible = value

    def is_visible(self):
        if self._window:
            return self._window.visible

        return False
