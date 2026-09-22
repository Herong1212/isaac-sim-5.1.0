"""References widget."""

# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["TrackEditingStringModel", "AddPayloadReferenceWindow", "PayloadReferenceWidget"]

import asyncio
import urllib
import weakref
from functools import lru_cache, partial
from typing import Any, Callable, Union

import carb
import omni.client
import omni.kit.app
import omni.kit.commands
import omni.kit.usd.layers as layers
import omni.ui as ui
import omni.usd
from omni.kit.async_engine import run_coroutine
from pxr import Sdf, Tf, Usd

from .asset_filepicker import check_paths_with_callback, replace_query, show_asset_file_picker
from .prim_selection_payload import PrimSelectionPayload
from .usd_property_widget import UsdPropertiesWidget
from .usd_property_widget_builder import UsdPropertiesWidgetBuilder
from .usd_style import Styles
from .versioning_helper import VersioningHelper

DEFAULT_PRIM_TAG = "<Default Prim>"
REF_LABEL_WIDTH = 80


@lru_cache()
def _get_plus_glyph():
    return ui.get_custom_glyph_code("${glyphs}/menu_context.svg")


def post_notification(
    message: str, info: bool = False, duration: int = 3, hide_after_timeout: bool = True
):  # pragma: no cover
    """Post a notification message to the user."""
    try:
        import omni.kit.notification_manager as nm

        nm.post_notification(
            message,
            status=nm.NotificationStatus.INFO if info else nm.NotificationStatus.WARNING,
            duration=duration,
            hide_after_timeout=hide_after_timeout,
        )
    except ModuleNotFoundError:  # pragma: no cover
        pass


def anchor_reference_asset_path_to_layer(ref: Sdf.Reference, intro_layer: Sdf.Layer, anchor_layer: Sdf.Layer):
    """Anchor a reference asset path to a layer."""
    asset_path = ref.assetPath
    if asset_path:
        asset_path = intro_layer.ComputeAbsolutePath(asset_path)
        asset_url = omni.client.make_relative_url_if_possible(anchor_layer.identifier, asset_path)
        # make a copy as Reference is immutable
        ref = Sdf.Reference(
            assetPath=asset_url,
            primPath=ref.primPath,
            layerOffset=ref.layerOffset,
            customData=ref.customData,
        )
    return ref


def anchor_payload_asset_path_to_layer(ref: Sdf.Payload, intro_layer: Sdf.Layer, anchor_layer: Sdf.Layer):
    """Anchor a payload asset path to a layer."""
    asset_path = ref.assetPath
    if asset_path:
        asset_path = intro_layer.ComputeAbsolutePath(asset_path)
        asset_url = omni.client.make_relative_url_if_possible(anchor_layer.identifier, asset_path)
        # make a copy as Payload is immutable
        ref = Sdf.Payload(
            assetPath=asset_url,
            primPath=ref.primPath,
            layerOffset=ref.layerOffset,
        )
    return ref


# Model that calls edited_fn when end_edit or set_value (not when typing)
class TrackEditingStringModel(ui.SimpleStringModel):
    """Model that calls edited_fn when end_edit or set_value (not when typing)."""

    def __init__(self, value: str = ""):
        super().__init__()
        self._editing = False
        self._edited_fn = []
        self.set_value(value)

    def begin_edit(self):
        """Begin editing the string model."""
        super().begin_edit()
        self._editing = True

    def end_edit(self):
        """End editing the string model."""
        self._editing = False
        super().end_edit()
        self._call_edited_fn()

    def set_value(self, value: str):
        """Set the value of the string model."""
        super().set_value(value)
        if not self._editing:
            self._call_edited_fn()

    def add_edited_fn(self, fn):
        """Add a function to be called when the string model is edited."""
        self._edited_fn.append(fn)

    def clear_edited_fn(self):
        """Clear the functions to be called when the string model is edited."""
        self._edited_fn.clear()

    def _call_edited_fn(self):
        """Call the edited functions when the string model is edited."""
        for fn in self._edited_fn:
            fn(self)


class PayloadReferenceInfo:
    """Payload reference information."""

    def __init__(self, asset_path_field, prim_path_field, prim_path_field_model, checkpoint_model, reload_widget=None):
        self.asset_path_field = asset_path_field
        self.prim_path_field = prim_path_field
        self.prim_path_field_model = prim_path_field_model
        self.checkpoint_model = checkpoint_model
        self.reload_widget = reload_widget

    def destroy(self):
        """Destroy the payload reference information."""
        if self.checkpoint_model:  # pragma: no cover
            self.checkpoint_model.destroy()
        self.asset_path_field = None
        self.prim_path_field = None
        self.prim_path_field_model = None
        self.checkpoint_model = None
        self.reload_widget = None


def build_path_field(
    stage,
    init_value: str,
    jump_button: bool,
    use_payloads: bool,
    layer: Sdf.Layer = None,
    is_live: bool = False,
    in_session: bool = False,
    outdated: bool = False,
    from_local_stack=True,
    auto_reload: bool = False,
):
    """Build a path field."""
    with ui.HStack(style={"Button": {"margin": 0, "padding": 1, "border_radius": 2, "background_color": 0x00000000}}):

        def assign_value_fn(model, path):
            model.set_value(path)

        def assign_reference_value(
            stage_weak, model_weak, path: str, assign_value_fn: Callable[[Any, str], None], frame=None
        ):
            stage = stage_weak()
            model = model_weak() if stage else None
            if not model:  # pragma: no cover
                return

            edit_layer = stage.GetEditTarget().GetLayer()
            # make the path relative to current edit target layer
            # OMPE-41028: If the current relative url is an absolute local path, and the layer is non-local, prepend
            #  the `file` scheme to the local path to make sure it resolves correctly; Currently on Linux, an abs
            #  local path may get recognized as relative without the explicit file scheme
            if omni.client.is_local_url(path) and not omni.client.is_local_url(edit_layer.identifier):
                relative_url = omni.client.normalize_url(omni.client.make_file_url_if_possible(path))
            else:
                relative_url = omni.client.make_relative_url_if_possible(edit_layer.identifier, path)
            assign_value_fn(model, relative_url)

        def drop_accept(url: str):
            if len(url.split("\n")) > 1:
                carb.log_warn("build_path_field multifile drag/drop not supported")
                return False

            # TODO support filtering by file extension
            if "." not in url:
                # TODO dragging from stage view also result in a drop, which is a prim path not an asset path
                # For now just check if dot presents in the url (indicating file extension).
                return False  # pragma: no cover
            return True

        with ui.ZStack():
            model = TrackEditingStringModel(value=urllib.parse.unquote(init_value))
            string_field = ui.StringField(
                model=model, enabled=not is_live and not in_session, name="layer_path", identifier="path_field"
            )
            string_field.set_accept_drop_fn(drop_accept)
            string_field.set_drop_fn(
                lambda event, model_weak=weakref.ref(model), stage_weak=weakref.ref(stage): assign_reference_value(
                    stage_weak, model_weak, event.mime_data, assign_value_fn=assign_value_fn
                )
            )
            if is_live:  # pragma: no cover
                string_field.set_style(Styles.LIVE_SEL)
            if in_session:  # pragma: no cover
                string_field.set_style(Styles.LIVE_GREEN_DARKER)
            if outdated:  # pragma: no cover
                string_field.set_style(Styles.RELOAD_SEL)

        ui.Spacer(width=3)

        # RELOAD BUTTON with drop-down.
        usd_context = omni.usd.get_context_from_stage(stage)
        if layer and usd_context:
            try:
                from omni.kit.widget.live_session_management.reload_widget import build_reload_widget

                ref_id = layer.ComputeAbsolutePath(model.get_value_as_string())
                g_reload = carb.settings.get_settings().get_as_bool(layers.SETTINGS_AUTO_RELOAD_NON_SUBLAYERS)
                reload_widget = build_reload_widget(ref_id, usd_context, outdated, auto_reload, g_reload)
                reload_widget.visible = not is_live
                # reload_widget.enabled = not in_session or outdated or auto_update

            except ImportError:  # pragma: no cover
                reload_widget = None
        else:  # pragma: no cover
            reload_widget = None

        # BROWSE BUTTON
        if from_local_stack:
            try:
                from omni.kit.window.file_importer import get_file_importer

                ui.Button(
                    style=Styles.BROWSE_BTN,
                    name="browse",
                    width=20,
                    tooltip="Browse..." if get_file_importer() is not None else "File importer not available",
                    clicked_fn=lambda model_weak=weakref.ref(model), stage_weak=weakref.ref(stage), layer_weak=(
                        weakref.ref(layer) if layer else None
                    ): show_asset_file_picker(
                        "Select Payload..." if use_payloads else "Select Reference...",
                        assign_value_fn,
                        model_weak,
                        stage_weak,
                        layer_weak=layer_weak,
                        on_selected_fn=assign_reference_value,
                    ),
                    enabled=get_file_importer() is not None,
                    visible=not is_live and not in_session,
                    identifier="browse_button",
                )
            except ModuleNotFoundError:
                pass

        # FIND BUTTON
        if jump_button:
            ui.Spacer(width=3)
            # Button to jump to the file in Content Window

            async def locate_file(model, weak_layer):
                # omni.kit.window.content_browser is optional dependency
                try:
                    import omni.client

                    url = model.get_value_as_string()
                    if len(url) == 0:  # pragma: no cover
                        return

                    if weak_layer:
                        weak_layer = weak_layer()
                        if weak_layer:
                            url = weak_layer.ComputeAbsolutePath(url)

                    # Remove the checkpoint and branch so navigate_to works
                    url = replace_query(url, None)

                    result, _ = await omni.client.stat_async(url)
                    if result == omni.client.Result.OK:
                        import omni.kit.window.content_browser

                        instance = omni.kit.window.content_browser.get_instance()
                        instance.navigate_to(url)
                    else:
                        post_notification(f'Cannot locate file "{url}"')

                except Exception as e:  # pragma: no cover  # pylint: disable=broad-exception-caught
                    carb.log_warn(f"Failed to locate file: {e}")

            locate_button = ui.Button(
                style=Styles.FIND_BTN,
                name="find",
                width=20,
                tooltip="Locate File",
                clicked_fn=lambda model=model, weak_layer=weakref.ref(layer) if layer else None: asyncio.ensure_future(
                    locate_file(model, weak_layer)
                ),
                identifier="locate_button",
            )

            # disable locate_button if file not found
            def on_complete(result, url, widget):
                if result != omni.client.Result.OK:
                    widget.enabled = False
                    widget.set_style(Styles.FIND_BTN_MISSING)
                    widget.tooltip = f'Cannot locate file "{url}"'
                else:
                    widget.enabled = True
                    widget.set_style(Styles.FIND_BTN)
                    widget.tooltip = "Locate File"

            asyncio.ensure_future(
                UsdPropertiesWidgetBuilder.validate_url(
                    model, layer, lambda r, u, w=locate_button: on_complete(r, u, w)
                )
            )

    return [string_field, reload_widget]


class AddPayloadReferenceWindow:
    """Add a payload reference window."""

    def __init__(self, payload: PrimSelectionPayload, on_payref_added_fn: Callable, use_payloads=False):
        self._payrefs = None
        self._use_payloads = use_payloads
        self._prim_path_model = ui.SimpleStringModel()
        self._stage = payload.get_stage()
        self._payload = payload
        self._on_payref_added_fn = on_payref_added_fn

    def set_payload(self, payload: PrimSelectionPayload):
        """Set the payload."""
        self._stage = payload.get_stage()
        self._payload = payload

    def show(self, payrefs: Union[Sdf.Reference, Sdf.Payload]):
        """Show the payload reference window."""
        self._payrefs = payrefs
        fallback = None
        if self._stage and not self._stage.GetRootLayer().anonymous:
            # If asset path is empty, open the USD rootlayer folder
            # But only if filepicker didn't already have a folder remembered (thus fallback)
            fallback = self._stage.GetRootLayer().identifier

        self._prim_path_model.set_value(DEFAULT_PRIM_TAG)

        def _on_import(weak_self, filename, dirname, selections=None):
            path = omni.client.combine_urls(dirname, filename)
            check_paths_with_callback([path], callback=partial(_on_file_selected, weak_self))

        def _on_file_selected(weak_self, paths):
            # pylint: disable=protected-access

            weak_self = weak_self()
            if not weak_self:  # pragma: no cover
                return
            if not paths and len(paths) != 1:  # pragma: no cover
                return

            asset_path = paths[0]
            edit_layer = weak_self._stage.GetEditTarget().GetLayer()
            # make the path relative to current edit target layer
            # OMPE-41028: If the current relative url is an absolute local path, and the layer is non-local, prepend
            #  the `file` scheme to the local path to make sure it resolves correctly; Currently on Linux, an abs
            #  local path may get recognized as relative without the explicit file scheme
            if omni.client.is_local_url(asset_path) and not omni.client.is_local_url(edit_layer.identifier):
                asset_url = omni.client.normalize_url(omni.client.make_file_url_if_possible(asset_path))
            else:
                asset_url = omni.client.make_relative_url_if_possible(edit_layer.identifier, asset_path)

            prim_path = self._prim_path_model.get_value_as_string()
            if str(prim_path) == DEFAULT_PRIM_TAG:
                prim_path = Sdf.Path()

            payrefs = weak_self._payrefs
            if not payrefs:
                stage = weak_self._stage
                payload_prim_path = weak_self._payload[-1]
                if not stage or not payload_prim_path:  # pragma: no cover
                    carb.log_warn(f"Cannot create payload/reference as stage/prim {payload_prim_path} is invalid")
                    return
                anchor_prim = stage.GetPrimAtPath(payload_prim_path)
                if not anchor_prim:  # pragma: no cover
                    carb.log_warn(f"Cannot create payload/reference as failed to get prim {payload_prim_path}")
                    return

                if weak_self._use_payloads:
                    anchor_prim.GetPayloads().SetPayloads([])
                    payrefs = anchor_prim.GetPayloads()
                    if not payrefs:  # pragma: no cover
                        carb.log_warn("Failed to create payload")
                        return
                else:
                    anchor_prim.GetReferences().SetReferences([])
                    payrefs = anchor_prim.GetReferences()
                    if not payrefs:  # pragma: no cover
                        carb.log_warn("Failed to create reference")
                        return

            command_kwargs = {"stage": payrefs.GetPrim().GetStage(), "prim_path": payrefs.GetPrim().GetPath()}
            if weak_self._use_payloads:
                if prim_path:
                    payref = Sdf.Payload(asset_url, prim_path)
                else:
                    payref = Sdf.Payload(asset_url)
                command = "AddPayload"
                command_kwargs["payload"] = payref
            else:
                if prim_path:
                    payref = Sdf.Reference(asset_url, prim_path)
                else:
                    payref = Sdf.Reference(asset_url)
                command = "AddReference"
                command_kwargs["reference"] = payref

            omni.kit.commands.execute(command, **command_kwargs)

            weak_self._on_payref_added_fn(payrefs.GetPrim())

        try:
            from omni.kit.window.file_importer import ImportOptionsDelegate, get_file_importer

            class AddPayloadReferenceOptionsDelegate(ImportOptionsDelegate):
                """Add a payload reference options delegate."""

                def __init__(self, prim_path_model):
                    super().__init__(build_fn=self._build_ui_impl, destroy_fn=self._destroy_impl)
                    self._widget = None
                    self._prim_path_model = prim_path_model

                def should_load_payload(self):
                    """Should the payload by loaded."""
                    if self._load_payload_checkbox:
                        return self._load_payload_checkbox.model.get_value_as_bool()
                    return False

                def _build_ui_impl(self):
                    self._widget = ui.Frame()
                    with self._widget:
                        with ui.HStack(height=0, spacing=2):
                            ui.Label("Prim Path", width=0)
                            ui.StringField().model = self._prim_path_model

                def _destroy_impl(self, _):  # pragma: no cover
                    self._prim_path_model = None
                    self._widget = None

            file_importer = get_file_importer()
            if file_importer:
                file_importer.show_window(
                    title="Select Payload..." if self._use_payloads else "Select Reference...",
                    import_button_label="Select",
                    import_handler=partial(_on_import, weakref.ref(self)),
                    hide_window_on_import=False,
                )
            if fallback and not file_importer.get_dialog().get_current_directory():
                file_importer.get_dialog().set_current_directory(fallback)
            file_importer.add_import_options_frame(
                "Payload Options" if self._use_payloads else "Reference Options",
                AddPayloadReferenceOptionsDelegate(self._prim_path_model),
            )
        except ModuleNotFoundError:
            pass

    def destroy(self):
        """Destroy the payload reference window."""
        self._payrefs = None
        self._prim_path_model = None


class PayloadReferenceWidget(UsdPropertiesWidget):
    """Payload reference widget."""

    def __init__(self, use_payloads=False):
        super().__init__(
            title="Payloads" if use_payloads else "References", collapsed=False, multi_edit=False, enable_adapter=True
        )
        self._ref_list_op = None
        self._payrefs = None
        self._ref_dict = {}
        self._add_ref_window = [None, None]
        self._ref_and_layers = []
        self._checkpoint_combobox = None
        self._use_payloads = use_payloads
        self._payload_loaded_cb = None
        self._update_value_task_or_future = None
        self._set_loaded_task_or_future = None
        self._live_syncing = None
        self._layers_state = None
        self._layers_interface = None
        self._sessions_dict = {}
        self._is_live = False
        self._in_sess = False
        self._outdated = False
        self._layers_event_sub = None
        self._sub_mod_references = []
        self._on_settings_change(None, None)
        self._sub_mod_references.append(
            omni.kit.app.SettingChangeSubscription(
                "/persistent/exts/omni.kit.property.usd/references_check_missing", self._on_settings_change
            )
        )
        self._sub_mod_references.append(
            omni.kit.app.SettingChangeSubscription(
                "/persistent/exts/omni.kit.property.usd/references_hide_max", self._on_settings_change
            )
        )
        self._show_loading_msg = False
        self._auto_reload = True
        self._abs_path = None
        self._button_frame = None
        self._stage_event_sub = None

        # +add menu item(s)
        from .prim_path_widget import PrimPathWidget

        PrimPathWidget.add_button_menu_entry(
            "Payload" if use_payloads else "Reference",
            show_fn=self._prim_is_selected,
            onclick_fn=lambda payload, u=self._use_payloads: self._on_add_payload_reference(payload, u),
        )

    def _on_settings_change(self, item, event_type):
        self._check_missing_refs = carb.settings.get_settings().get_as_bool(
            "/persistent/exts/omni.kit.property.usd/references_check_missing"
        )
        self._references_hide_max = carb.settings.get_settings().get_as_int(
            "/persistent/exts/omni.kit.property.usd/references_hide_max"
        )

    def _undo_redo_on_change(self, cmds):
        async def update_value(cmds):
            if cmds and "SetPayLoadLoadSelectedPrimsCommand" in cmds:
                last_prim = self._get_prim(self._payload[-1])
                if last_prim:
                    self._payload_loaded_cb.model.set_value(last_prim.IsLoaded())

        if cmds and self._payload_loaded_cb:
            self._update_value_task_or_future = run_coroutine(update_value(cmds))

    def _on_layer_event(self, event: carb.events.IEvent):
        payload = layers.get_layer_event_payload(event)
        if payload.event_type == layers.LayerEventType.LIVE_SESSION_LIST_CHANGED:
            self._update_session_widget_states()
        elif payload.event_type == layers.LayerEventType.OUTDATE_STATE_CHANGED:
            outdated_references = self._layers_state.get_outdated_non_sublayer_identifiers()
            if not outdated_references:
                return

            outdated_ids = self._layers_state.get_outdated_non_sublayer_identifiers()

            for ref, layer in self._ref_and_layers:
                abs_path = (
                    omni.client.combine_urls(layer.identifier, ref.assetPath) if len(ref.assetPath) else ref.assetPath
                )
                if abs_path in outdated_ids:
                    self._ref_dict[ref].asset_path_field.set_style(Styles.RELOAD_ORANGE)
                    self._ref_dict[ref].reload_widget.set_style(Styles.RELOAD_ORANGE)

    def _update_session_widget_states(self):
        if not self._live_syncing:
            return

        for _, item in self._sessions_dict.items():
            combo = item["combo"]
            hint = item["hint"]
            reset = item["reset"]
            live = item["live"]

            if not combo.model.is_default_session_selected:
                combo.model.refresh_sessions()

            default = not combo.model.current_session or combo.model.is_default_session_selected
            reset.name = "default" if default else "changed"
            reset.set_style(Styles.DEFAULT_BTN)

            if combo.model.empty():
                hint.visible = True
                hint.text = "No Sessions"
                combo.enabled = False
                reset.enabled = False
                live.visible = False
            else:
                hint.visible = False
                combo.enabled = True
                reset.enabled = True
                live.visible = True

    def _on_add_payload_reference(self, payload: PrimSelectionPayload, use_payloads: bool):
        ref_window_index = 0 if self._use_payloads else 1
        if not self._add_ref_window[ref_window_index]:
            self._add_ref_window[ref_window_index] = AddPayloadReferenceWindow(
                payload, self._on_payload_reference_added, use_payloads=use_payloads
            )
        else:
            self._add_ref_window[ref_window_index].set_payload(payload)
        self._add_ref_window[ref_window_index].show(self._payrefs)

    def _on_payload_reference_added(self, prim: Usd.Prim):
        property_window = omni.kit.window.property.get_window()
        if property_window:
            property_window.request_rebuild()

    def _prim_is_selected(self, objects: dict):
        stage = objects["stage"] if "prim_list" in objects and "stage" in objects else None
        return len(objects["prim_list"]) == 1 if stage else False

    def clean(self):
        self.reset()
        for window in self._add_ref_window:
            if window:
                window.destroy()
        self._add_ref_window = [None, None]
        self._stage_event_sub = None
        self._layers_event_sub = None
        self._live_syncing = None
        self._layers_state = None
        super().clean()

    def reset(self):
        if self._listener:
            self._listener.Revoke()
            self._listener = None
        omni.kit.undo.unsubscribe_on_change(self._undo_redo_on_change)
        self._ref_list_op = None
        self._payrefs = None
        for _, info in self._ref_dict.items():
            info.destroy()
        for _, item in self._sessions_dict.items():  # pragma: no cover
            item["combo"].model.destroy()
            # Don't explicitly destroy ui.Widget
            # self._sessions_dict[key]["combo"].destroy()
            item["users"].destroy()
        self._ref_dict.clear()
        self._ref_and_layers.clear()
        self._sessions_dict.clear()
        if self._checkpoint_combobox:
            self._checkpoint_combobox.destroy()
            self._checkpoint_combobox = None
        super().reset()

    def on_new_payload(self, payload):
        """See PropertyWidget.on_new_payload"""
        if not super().on_new_payload(payload):
            return False
        if not self._payload or len(self._payload) != 1:  # single edit for now
            return False

        anchor_prim = None
        for prim_path in self._payload:
            prim = self._get_prim(prim_path)
            if not prim:  # pragma: no cover
                return False
            anchor_prim = prim

        # only show if prim has payloads/references
        if anchor_prim:
            if self._use_payloads:
                ref_and_layers = omni.usd.get_composed_payloads_from_prim(anchor_prim)
            else:
                ref_and_layers = omni.usd.get_composed_references_from_prim(anchor_prim)

            if self._references_hide_max and len(ref_and_layers) >= self._references_hide_max:
                self._show_loading_msg = True
                omni.kit.window.property.managed_frame.set_collapsed_state("Property/References", True)

            return len(ref_and_layers) > 0
        return False  # pragma: no cover

    def build_impl(self):
        """
        See PropertyWidget.build_impl
        """
        if not self._use_payloads:
            super().build_impl()
        else:

            def on_checkbox_toggle(layer_name, model):
                async def set_loaded(layer_name, state):
                    omni.kit.commands.execute(
                        "SetPayLoadLoadSelectedPrimsCommand", selected_paths=[layer_name], value=state
                    )

                self._set_loaded_task_or_future = run_coroutine(set_loaded(layer_name, model.get_value_as_bool()))

            last_prim = self._get_prim(self._payload[-1])
            if not last_prim:  # pragma: no cover
                return

            self._button_frame = ui.Frame()
            with self._button_frame:
                with ui.ZStack():
                    super().build_impl()
                    with ui.HStack():
                        ui.Spacer(width=ui.Fraction(0.5))
                        with ui.VStack(width=0, height=0, content_clipping=True):
                            ui.Spacer(height=5)
                            self._payload_loaded_cb = ui.CheckBox()
                            self._payload_loaded_cb.model.set_value(last_prim.IsLoaded())
                            self._payload_loaded_cb.model.add_value_changed_fn(
                                partial(on_checkbox_toggle, last_prim.GetPath().pathString)
                            )
                        ui.Spacer(width=5)

    def on_collapsed_changed(self, collapsed):
        super().on_collapsed_changed(collapsed)
        if not self._listener and not collapsed:
            self.request_rebuild()

    def build_items(self):
        self.reset()

        if len(self._payload) == 0:  # pragma: no cover
            return

        if self._collapsed:
            return

        last_prim = self._get_prim(self._payload[-1])
        if not last_prim:  # pragma: no cover
            return

        stage = last_prim.GetStage()
        if not stage:  # pragma: no cover
            return

        self._listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, stage)
        omni.kit.undo.subscribe_on_change(self._undo_redo_on_change)

        if self._use_payloads:
            self._payrefs = last_prim.GetPayloads()
            self._ref_and_layers = omni.usd.get_composed_payloads_from_prim(last_prim, False)
        else:
            self._payrefs = last_prim.GetReferences()
            self._ref_and_layers = omni.usd.get_composed_references_from_prim(last_prim, False)

        if self._show_loading_msg:

            async def rebuild_again():
                await omni.kit.app.get_app().next_update_async()
                await omni.kit.app.get_app().next_update_async()
                self.request_rebuild()

            UsdPropertiesWidgetBuilder.create_label(
                f"Loading {len(self._ref_and_layers)} references....",
                additional_label_kwargs={"width": REF_LABEL_WIDTH},
            )

            self._show_loading_msg = False
            run_coroutine(rebuild_again())
            return

        ref_window_index = 0 if self._use_payloads else 1
        self._add_ref_window[ref_window_index] = AddPayloadReferenceWindow(
            self._payload, self._on_payload_reference_added, use_payloads=self._use_payloads
        )

        # no vertical spacing for this VStack to make live sessions flush with reference/payload.
        with ui.VStack(height=0, spacing=0, name="frame_v_stack"):
            if self._payrefs:
                if self._payload_loaded_cb:
                    self._payload_loaded_cb.enabled = True

                usd_context = omni.usd.get_context_from_stage(self._payload.get_stage())
                if usd_context:
                    self._layers_interface = layers.get_layers(usd_context)
                    self._live_syncing = self._layers_interface.get_live_syncing()
                    self._layers_state = self._layers_interface.get_layers_state()
                    self._layers_event_sub = self._layers_interface.get_event_stream().create_subscription_to_pop(
                        self._on_layer_event, name="Session Start Window Events"
                    )

                    auto_reload_ids = self._layers_state.get_auto_reload_layers()
                    outdated_layer_ids = self._layers_state.get_outdated_non_sublayer_identifiers()
                else:
                    auto_reload_ids = []
                    outdated_layer_ids = []

                for ref, layer in self._ref_and_layers:
                    if (
                        omni.client.is_local_url(ref.assetPath)
                        and not omni.client.is_local_url(layer.identifier)
                        and omni.client.stat(ref.assetPath)[0] == omni.client.Result.OK
                    ):
                        self._abs_path = omni.client.normalize_url(omni.client.make_file_url_if_possible(ref.assetPath))
                    else:
                        self._abs_path = (
                            omni.client.combine_urls(layer.identifier, ref.assetPath)
                            if len(ref.assetPath)
                            else ref.assetPath
                        )
                    self._is_live = (
                        self._live_syncing.is_live_session_layer(self._abs_path) if self._live_syncing else False
                    )
                    self._in_sess = (
                        self._live_syncing.is_prim_in_live_session(last_prim.GetPath(), self._abs_path)
                        if self._live_syncing
                        else False
                    )
                    self._outdated = self._abs_path in outdated_layer_ids
                    self._auto_reload = self._abs_path in auto_reload_ids
                    self._build_payload_reference(ref, layer)
                    if self._in_sess and self._payload_loaded_cb:
                        self._payload_loaded_cb.enabled = False

            def on_add_payload_reference(weak_self):
                # pylint: disable=protected-access

                weak_self = weak_self()
                if not weak_self:  # pragma: no cover
                    return

                weak_self._add_ref_window[ref_window_index].show(weak_self._payrefs)

            ui.Button(
                f"{_get_plus_glyph()} Add Payload" if self._use_payloads else f"{_get_plus_glyph()} Add Reference",
                clicked_fn=lambda weak_self=weakref.ref(self): on_add_payload_reference(weak_self),
                identifier="add_button",
            )

        self._update_session_widget_states()

    def _build_payload_reference(self, payref: Sdf.Reference, intro_layer: Sdf.Layer):
        def filter_match(name: str) -> bool:
            matches = self._filter.matches(name)
            if matches:
                self._any_item_visible = True
            return matches

        stage = self._payrefs.GetPrim().GetStage()
        # OM-90719: Only reference or payload from local layer stack can be removed.
        # https://openusd.org/release/usdfaq.html#list-edited-composition-arcs
        is_payref_from_local_stack = stage and stage.HasLocalLayer(intro_layer)

        with ui.Frame():
            with ui.VStack():
                stack = ui.ZStack()
                with stack:
                    ref_bg = ui.Rectangle(name="backdrop-live" if self._is_live else "backdrop")
                    ref_bg.set_style(Styles.BACK_DROP)

                    style = {"VStack::ref_group": {"margin_width": 0.2, "margin_height": 0.2}}
                    with ui.VStack(name="ref_group", spacing=5, style=style):
                        with ui.HStack(spacing=5):
                            ui.Spacer(width=5)
                            with ui.VStack(spacing=5):
                                highlight = self._filter.name
                                match = filter_match("Asset Path")
                                ui.Spacer(height=0.1)
                                if match:
                                    asset_path_field, reload_widget = self._build_asset_path_ui(
                                        payref, intro_layer, highlight, is_payref_from_local_stack
                                    )
                                else:  # pragma: no cover
                                    asset_path_field, reload_widget = None, None

                                if not self._in_sess:
                                    ui.Spacer(height=0.1)

                                match = filter_match("Prim Path")
                                if match:
                                    prim_path_field, prim_path_field_model = self._build_prim_path_ui(
                                        payref, intro_layer, highlight, is_payref_from_local_stack
                                    )
                                else:  # pragma: no cover
                                    prim_path_field, prim_path_field_model = None, None

                                if is_payref_from_local_stack:
                                    match = filter_match("Checkpoint")
                                    checkpoint_model = (
                                        self._build_checkpoint_ui(payref, intro_layer, highlight) if match else None
                                    )
                                else:
                                    checkpoint_model = None

                                if filter_match("Live Sync"):
                                    self._build_livesync_ui(payref, intro_layer, highlight)

                                if not self._is_live:
                                    ui.Spacer(height=0.1)

                            if is_payref_from_local_stack:
                                self._build_remove_payload_reference_button(payref, intro_layer)

                    self._ref_dict[payref] = PayloadReferenceInfo(
                        asset_path_field, prim_path_field, prim_path_field_model, checkpoint_model, reload_widget
                    )
                if not self._is_live:
                    # this is the spacer that separates individual reference/payloads
                    ui.Spacer(height=5)

    def _build_asset_path_ui(
        self, payref: Union[Sdf.Reference, Sdf.Payload], intro_layer: Sdf.Layer, highlight: str, from_local_stack=True
    ):
        label_text = "Asset Path" if not self._is_live else "Live Session"

        stack = ui.HStack()
        with stack:
            label_field = UsdPropertiesWidgetBuilder.create_label(
                label_text, additional_label_kwargs={"width": REF_LABEL_WIDTH, "highlight": highlight}
            )
            if self._is_live:  # pragma: no cover
                label_field.set_style(Styles.LIVE_SEL)

            asset_path_field, reload_widget = build_path_field(
                self._payload.get_stage(),
                payref.assetPath,
                True,
                self._use_payloads,
                intro_layer,
                self._is_live,
                self._in_sess,
                self._outdated,
                from_local_stack,
                self._auto_reload,
            )
            # If payload/reference doesn't exist
            if payref.assetPath:
                if omni.client.is_local_url(payref.assetPath) and not omni.client.is_local_url(intro_layer.identifier):
                    status, _ = omni.client.stat(payref.assetPath)
                else:
                    status, _ = omni.client.stat(
                        intro_layer.ComputeAbsolutePath(payref.assetPath)
                    )  # pylint: disable=unpacking-non-sequence
                # check if it exist local file
                if status != omni.client.Result.OK:  # pragma: no cover
                    asset_path_field.set_style({"color": Styles.REFERENCE_ERROR})

            asset_path_field.model.add_edited_fn(
                lambda model, stage=self._payrefs.GetPrim().GetStage(), prim_path=self._payrefs.GetPrim().GetPath(), payref=payref: self._on_payload_reference_edited(
                    model, stage, prim_path, payref, intro_layer
                )
            )
            if self._is_live or self._in_sess:
                asset_path_field.enabled = False
            else:
                asset_path_field.enabled = from_local_stack

            asset_path_field.set_tooltip(urllib.parse.unquote(self._abs_path))

        return [asset_path_field, reload_widget]

    def _is_ref_prim_valid(self, stage, prim, abs_asset_path, ref_prim_path):
        # check prim_path is valid
        if not prim:  # pragma: no cover
            return False

        # asset_path "" which means this stage
        if not abs_asset_path:
            if str(ref_prim_path) == DEFAULT_PRIM_TAG:
                return bool(stage.GetDefaultPrim())

            return bool(stage.GetPrimAtPath(ref_prim_path)) if ref_prim_path else True

        layer = Sdf.Find(abs_asset_path)
        if not layer:
            return False

        if ref_prim_path and str(ref_prim_path) != DEFAULT_PRIM_TAG:
            return bool(layer.GetPrimAtPath(ref_prim_path))

        if layer.defaultPrim:
            return bool(layer.GetPrimAtPath(Sdf.Path.absoluteRootPath.AppendChild(layer.defaultPrim)))

        return False

    def _build_prim_path_ui(
        self, payref: Union[Sdf.Reference, Sdf.Payload], intro_layer: Sdf.Layer, highlight: str, from_local_stack=True
    ):
        last_prim = self._get_prim(self._payload[-1])
        stack = ui.HStack()
        with stack:
            UsdPropertiesWidgetBuilder.create_label(
                "Prim Path", additional_label_kwargs={"width": REF_LABEL_WIDTH, "highlight": highlight}
            )
            prim_path = payref.primPath
            if not prim_path:
                prim_path = DEFAULT_PRIM_TAG
            prim_path_field_model = TrackEditingStringModel(str(prim_path))
            prim_path_field = ui.StringField(model=prim_path_field_model, identifier="payref_prim_path")
            prim_path_field.set_tooltip(self._payrefs.GetPrim().GetStage().GetDefaultPrim().GetPath().pathString)
            prim_path_field.model.add_edited_fn(
                lambda model, stage=self._payrefs.GetPrim().GetStage(), prim_path=self._payrefs.GetPrim().GetPath(), payref=payref: self._on_payload_reference_edited(
                    model, stage, prim_path, payref, intro_layer
                )
            )
            prim_path_field.enabled = from_local_stack

            if self._is_live:  # pragma: no cover
                stack.visible = False
                prim_path_field.enabled = False
            if self._in_sess:  # pragma: no cover
                prim_path_field.set_style(Styles.LIVE_GREEN_DARKER)
                prim_path_field.enabled = False

            asset_abs_path = intro_layer.ComputeAbsolutePath(payref.assetPath) if payref.assetPath else ""
            if self._check_missing_refs and not self._is_ref_prim_valid(
                self._payrefs.GetPrim().GetStage(), last_prim, asset_abs_path, prim_path
            ):
                prim_path_field.set_style({"color": Styles.REFERENCE_ERROR})

        return prim_path_field, prim_path_field_model

    def _build_checkpoint_ui(self, payref: Union[Sdf.Reference, Sdf.Payload], intro_layer: Sdf.Layer, highlight: str):
        if VersioningHelper.is_versioning_enabled():
            try:
                # Use checkpoint widget in the drop down menu for more detailed information
                from omni.kit.widget.versioning.checkpoint_combobox import CheckpointCombobox

                stack = ui.HStack()
                with stack:
                    UsdPropertiesWidgetBuilder.create_label(
                        "Checkpoint", additional_label_kwargs={"width": REF_LABEL_WIDTH, "highlight": highlight}
                    )

                    def on_selection_changed(
                        selection,
                        stage: Usd.Stage,
                        prim_path: Sdf.Path,
                        payref: Union[Sdf.Reference, Sdf.Payload],
                        intro_layer: Sdf.Layer,
                    ):
                        self._on_payload_reference_checkpoint_edited(selection, stage, prim_path, payref)

                    self._checkpoint_combobox = CheckpointCombobox(
                        self._abs_path,
                        lambda selection, stage=self._payrefs.GetPrim().GetStage(), prim_path=self._payrefs.GetPrim().GetPath(), payref=payref: on_selection_changed(
                            selection, stage, prim_path, payref, intro_layer
                        ),
                    )

                    # reset button
                    def reset_func(payref, stage, prim_path):
                        on_selection_changed(None, stage, prim_path, payref, intro_layer)

                    checkpoint = ""
                    client_url = omni.client.break_url(payref.assetPath)
                    if client_url.query:
                        _, checkpoint = omni.client.get_branch_and_checkpoint_from_query(client_url.query)
                    ui.Spacer(width=4)
                    ui.Image(
                        name="changed" if checkpoint else "default",
                        mouse_pressed_fn=lambda x, y, b, a, s=self._payrefs.GetPrim().GetStage(), r=payref, p=self._payrefs.GetPrim().GetPath(): reset_func(
                            r, s, p
                        ),
                        style=Styles.DEFAULT_BTN,
                        width=12,
                        height=18,
                        tooltip="Reset Checkpoint" if checkpoint else "",
                    )

                    def on_have_server_info(server: str, support_checkpoint: bool, stack: ui.HStack):
                        if not support_checkpoint or self._is_live:
                            stack.visible = False

                    VersioningHelper.check_server_checkpoint_support(
                        VersioningHelper.extract_server_from_url(self._abs_path),
                        lambda s, c, t=stack: on_have_server_info(s, c, t),
                    )
                    stack.visible = stack.enabled = not self._in_sess and not self._is_live

                return
            except ImportError as e:  # pragma: no cover
                # If the widget is not available, create a simple combo box instead
                carb.log_warn(f"Checkpoint widget in Payload/Reference is not available due to: {e}")

    def _on_session_list_changed(self, model):
        self._update_session_widget_states()

    def _build_livesync_ui(
        self, payref: Union[Sdf.Reference, Sdf.Payload], intro_layer: Sdf.Layer, highlight: str
    ):  # pragma: no cover
        try:
            if self._is_live or not self._live_syncing:
                return

            if omni.client.stat(self._abs_path)[0] != omni.client.Result.OK:  # pylint: disable=unsubscriptable-object
                return

            _, checkpoint = omni.client.get_branch_and_checkpoint_from_query(self._abs_path)
            if not omni.client.is_omni_objects_enabled(self._abs_path) or checkpoint:
                return

            from omni.kit.widget.live_session_management import LiveSessionModel, LiveSessionUserList
            from omni.kit.widget.live_session_management.utils import join_live_session

            abs_path = (
                omni.client.combine_urls(intro_layer.identifier, payref.assetPath)
                if len(payref.assetPath)
                else payref.assetPath
            )
            # If the prim is an USD instance and prototype is in a live session already, don't build
            # widget as prototype prim will control the state of current live session.
            prim_path = self._payrefs.GetPrim().GetPath()
            if self._live_syncing.is_prim_in_live_session(prim_path, abs_path, from_reference_or_payload_only=True):
                return

            session_model = LiveSessionModel(self._layers_interface, abs_path, False)
            session_model.add_value_changed(self._on_session_list_changed)
            session_model.refresh_sessions()

            def _switch_live_session(session_model):
                prim_path = self._payrefs.GetPrim().GetPath()
                if self._live_syncing.is_prim_in_live_session(prim_path, abs_path):
                    self._live_syncing.stop_live_session(abs_path, prim_path=prim_path)
                    self._live_syncing.join_live_session(session_model.current_session, prim_path)

            session_model.add_value_changed(_switch_live_session)

            with ui.HStack():
                # livesync label
                UsdPropertiesWidgetBuilder.create_label(
                    "Live Sync", additional_label_kwargs={"width": REF_LABEL_WIDTH, "highlight": highlight}
                )
                ui.Spacer()

                # user participants layout
                with ui.VStack(width=0):
                    ui.Spacer()
                    user_layout = LiveSessionUserList(
                        self._live_syncing.usd_context,
                        abs_path,
                        show_myself=False,
                        maximum_users=3,
                        prim_path=self._payrefs.GetPrim().GetPath(),
                    )
                    ui.Spacer()

                # livesync button
                def _join_live_session(session_model, payload_loaded_cb):
                    prim_path = self._payrefs.GetPrim().GetPath()
                    current_session = session_model.current_session
                    if self._live_syncing.is_prim_in_live_session(prim_path, abs_path):
                        self._live_syncing.stop_live_session(abs_path, prim_path=prim_path)
                        if not self._live_syncing.is_prim_in_live_session(prim_path, abs_path) and payload_loaded_cb:
                            payload_loaded_cb.enabled = True
                    elif current_session:
                        join_live_session(self._layers_interface, abs_path, current_session, prim_path)
                        if self._live_syncing.is_prim_in_live_session(prim_path, abs_path) and payload_loaded_cb:
                            payload_loaded_cb.enabled = False

                def _on_live_sync_button(model, payload_loaded_cb, x, y, b, m):
                    if b == 0:
                        _join_live_session(model, payload_loaded_cb)

                live_layout = ui.ZStack(width=0, style=Styles.LIVE_STATE_PAYREF)
                tooltip = "Join Live Session" if not self._in_sess else "Leave Live Session"
                with live_layout:
                    with ui.HStack():
                        ui.Spacer(width=2)
                        with ui.VStack():
                            ui.Spacer()
                            ui.Image(name="lightning-live" if self._in_sess else "lightning", width=14, height=14)
                            ui.Spacer()
                    live_button = ui.InvisibleButton(width=14, identifier="live_button", tooltip=tooltip)
                    live_button.set_mouse_pressed_fn(
                        partial(_on_live_sync_button, session_model, self._payload_loaded_cb)
                    )

                # session combobox
                with ui.ZStack(width=0):
                    tooltip = "Live Session Name"
                    combo = ui.ComboBox(session_model, width=100, height=0, name="sessions-menu", tooltip=tooltip)
                    combo.set_style(Styles.SESSIONS_MENU)
                    with ui.HStack(width=0):
                        ui.Spacer(width=5)
                        hint = ui.Label("Updating Menu", alignment=ui.Alignment.LEFT_CENTER)

                ui.Spacer(width=4)

                # reset session
                def _on_reset(session_model, x, y, b, m):
                    if b == 0:
                        session_model.select_default_session()
                        self._update_session_widget_states()

                reset_button = ui.Image(
                    width=12,
                    height=18,
                    tooltip="Reset to Default",
                )
                reset_button.set_mouse_pressed_fn(partial(_on_reset, session_model))

            self._sessions_dict[abs_path] = {
                "combo": combo,
                "hint": hint,
                "users": user_layout,
                "reset": reset_button,
                "live": live_layout,
            }
        except ImportError:  # pragma: no cover
            # If the widget is not available, create a simple combo box instead
            carb.log_warn("omni.kit.widget.live_session_management should be enabled to support live prim.")

    def _build_remove_payload_reference_button(self, payref, intro_layer):
        def on_remove_payload_reference(ref, layer_weak, payrefs):
            if not ref or not payrefs:  # pragma: no cover
                return

            stage = payrefs.GetPrim().GetStage()
            edit_target_layer = stage.GetEditTarget().GetLayer()
            intro_layer = layer_weak() if layer_weak else None

            if self._use_payloads:
                # When removing a payload on a different layer, the deleted assetPath should be relative to edit target layer, not introducing layer
                if intro_layer and intro_layer != edit_target_layer:
                    ref = anchor_payload_asset_path_to_layer(ref, intro_layer, edit_target_layer)

                omni.kit.commands.execute(
                    "RemovePayload",
                    stage=stage,
                    prim_path=payrefs.GetPrim().GetPath(),
                    payload=ref,
                )
            else:
                # When removing a reference on a different layer, the deleted assetPath should be relative to edit target layer, not introducing layer
                if intro_layer and intro_layer != edit_target_layer:
                    ref = anchor_reference_asset_path_to_layer(ref, intro_layer, edit_target_layer)

                omni.kit.commands.execute(
                    "RemoveReference",
                    stage=stage,
                    prim_path=payrefs.GetPrim().GetPath(),
                    reference=ref,
                )

        with ui.ZStack(width=16, style=Styles.REMOVE_BTN):
            ui.Rectangle(visible=self._is_live)
            ui.Button(
                style=Styles.REMOVE_BTN,
                clicked_fn=lambda ref=payref, layer_weak=(
                    weakref.ref(intro_layer) if intro_layer else None
                ), refs=self._payrefs: on_remove_payload_reference(ref, layer_weak, refs),
                width=16,
                visible=not self._is_live and not self._in_sess,
                enabled=not self._in_sess,
                identifier="remove_button",
            )

    def _on_payload_reference_edited(
        self,
        model_or_item,
        stage: Usd.Stage,
        prim_path: Sdf.Path,
        payref: Union[Sdf.Reference, Sdf.Payload],
        intro_layer: Sdf.Layer,
    ):
        ref_prim_path = self._ref_dict[payref].prim_path_field.model.get_value_as_string()
        # any references with invalid paths get deleted
        if ref_prim_path and ref_prim_path[0] != "/":
            ref_prim_path = "/" + ref_prim_path
        ref_prim_path = (
            Sdf.Path(ref_prim_path) if ref_prim_path and str(ref_prim_path) != DEFAULT_PRIM_TAG else Sdf.Path()
        )
        new_asset_path = self._ref_dict[payref].asset_path_field.model.get_value_as_string()

        try:
            from omni.kit.widget.versioning.checkpoints_model import CheckpointItem

            if isinstance(model_or_item, CheckpointItem):
                new_asset_path = replace_query(new_asset_path, model_or_item.get_relative_path())
            elif model_or_item is None:
                new_asset_path = replace_query(new_asset_path, None)
        except ModuleNotFoundError:  # pragma: no cover
            pass

        # When replacing a reference/payload on a different layer, the replaced assetPath should be relative to edit target layer, not introducing layer
        edit_target_layer = stage.GetEditTarget().GetLayer()
        if intro_layer != edit_target_layer:
            if self._use_payloads:
                payref = anchor_payload_asset_path_to_layer(payref, intro_layer, edit_target_layer)
            else:
                payref = anchor_reference_asset_path_to_layer(payref, intro_layer, edit_target_layer)

        if omni.client.equal_urls(payref.assetPath, new_asset_path) and payref.primPath == ref_prim_path:
            return False

        if self._use_payloads:
            _, _ = omni.kit.commands.execute(
                "ReplacePayload",
                stage=stage,
                prim_path=prim_path,
                old_payload=payref,
                new_payload=Sdf.Payload(assetPath=new_asset_path, primPath=ref_prim_path),
            )
        else:
            _, _ = omni.kit.commands.execute(
                "ReplaceReference",
                stage=stage,
                prim_path=prim_path,
                old_reference=payref,
                new_reference=Sdf.Reference(assetPath=new_asset_path, primPath=ref_prim_path),
            )

        return True

    def _on_payload_reference_checkpoint_edited(
        self, model_or_item, stage: Usd.Stage, prim_path: Sdf.Path, payref: Union[Sdf.Reference, Sdf.Payload]
    ):
        new_asset_path = self._ref_dict[payref].asset_path_field.model.get_value_as_string()

        try:
            from omni.kit.widget.versioning.checkpoints_model import CheckpointItem

            if isinstance(model_or_item, CheckpointItem):
                new_asset_path = replace_query(new_asset_path, model_or_item.get_relative_path())
            elif model_or_item is None:
                new_asset_path = replace_query(new_asset_path, None)
        except ModuleNotFoundError:  # pragma: no cover
            pass

        if self._use_payloads:
            new_ref = Sdf.Payload(
                assetPath=new_asset_path.replace("\\", "/"), primPath=payref.primPath, layerOffset=payref.layerOffset
            )
            if payref != new_ref:
                omni.kit.commands.execute(
                    "ReplacePayload",
                    stage=stage,
                    prim_path=prim_path,
                    old_payload=payref,
                    new_payload=new_ref,
                )
            return

        new_ref = Sdf.Reference(
            assetPath=new_asset_path.replace("\\", "/"), primPath=payref.primPath, layerOffset=payref.layerOffset
        )
        if payref != new_ref:
            omni.kit.commands.execute(
                "ReplaceReference",
                stage=stage,
                prim_path=prim_path,
                old_reference=payref,
                new_reference=new_ref,
            )
