# Copyright (c) 2020-2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = []

import weakref
from pathlib import Path
from typing import List

import carb
import omni.ext
import omni.kit.app
import omni.ui as ui
import omni.usd
from carb.eventdispatcher import get_eventdispatcher
from pxr import Sdf, UsdGeom

from .attribute_context_menu import AttributeContextMenu
from .control_state_manager import ControlStateManager
from .prim_path_widget import PrimPathWidget
from .prim_selection_payload import PrimSelectionPayload
from .usd_style import Styles

ICON_PATH = ""
EXTENSION_PATH = ""
SHOW_PREFERENCES_PATH = "/exts/omni.kit.property.usd/show_prefs"


class UsdPropertyWidgets(omni.ext.IExt):
    """A class that extends the OmniKit extension interface to provide USD property widgets.

    UsdPropertyWidgets is responsible for managing the registration and unregistration of various USD related widgets in the OmniKit application. It utilizes a selection notification system to update property windows when USD stage selection changes occur. This class also handles startup and shutdown logic for USD property widgets, ensuring that preferences and widgets are appropriately registered or unregistered with the application. It interacts with other custom classes, such as AttributeContextMenu and ControlStateManager, to offer a comprehensive user interface for USD property manipulation.
    """

    def __init__(self):
        """Initializes the USD Property Widgets extension."""
        self._registered = False
        self._examples = None
        self._selection_notifiers = []
        self._hooks = []
        self._usd_preferences = None
        self._attribute_context_menu = None
        self._control_state_manager = None
        self._attribute_context_menu = None
        super().__init__()

    def on_startup(self, ext_id):
        """Method called when the extension starts up.

        Args:
            ext_id (str): The ID of the extension being started."""
        global EXTENSION_PATH, ICON_PATH

        manager = omni.kit.app.get_app().get_extension_manager()
        EXTENSION_PATH = manager.get_extension_path(ext_id)
        ICON_PATH = Path(EXTENSION_PATH).joinpath("data").joinpath("icons")
        Styles.on_startup()
        self._selection_notifiers.append(SelectionNotifier())  # default context
        self._usd_preferences = None
        self._hooks = []
        self._attribute_context_menu = AttributeContextMenu()
        self._control_state_manager = ControlStateManager(ICON_PATH)

        self._hooks.append(
            manager.subscribe_to_extension_enable(
                lambda _: self._register_widget(),
                lambda _: self._unregister_widget(),
                ext_name="omni.kit.window.property",
                hook_name="omni.usd listener",
            )
        )

        from .usd_property_widget_builder import UsdPropertiesWidgetBuilder

        UsdPropertiesWidgetBuilder.startup()

        manager = omni.kit.app.get_app().get_extension_manager()

        if carb.settings.get_settings().get(SHOW_PREFERENCES_PATH):
            self._hooks.append(
                manager.subscribe_to_extension_enable(
                    on_enable_fn=lambda _: self._register_preferences(),
                    on_disable_fn=lambda _: self._unregister_preferences(),
                    ext_name="omni.kit.window.preferences",
                    hook_name="omni.kit.property.usd omni.kit.window.preferences listener",
                )
            )

    def on_shutdown(self):
        """Method called when the extension is shutting down."""
        from .usd_property_widget_builder import UsdPropertiesWidgetBuilder

        UsdPropertiesWidgetBuilder.shutdown()

        self._control_state_manager.destory()
        self._control_state_manager = None

        self._attribute_context_menu.destroy()
        self._attribute_context_menu = None

        for notifier in self._selection_notifiers:
            notifier.stop()
        self._selection_notifiers.clear()
        self._hooks = None

        if self._registered:
            self._unregister_widget()

        self._unregister_preferences()

    def _register_preferences(self):
        from .property_preferences_page import PropertyUsdPreferences

        self._usd_preferences = omni.kit.window.preferences.register_page(PropertyUsdPreferences())

    def _unregister_preferences(self):
        if self._usd_preferences:
            import omni.kit.window.preferences

            omni.kit.window.preferences.unregister_page(self._usd_preferences)
            self._usd_preferences = None

    def _register_widget(self):
        try:
            import omni.kit.window.property as p

            from .references_widget import PayloadReferenceWidget
            from .usd_property_widget import RawUsdPropertiesWidget
            from .variants_widget import VariantsWidget

            w = p.get_window()
            if w:
                w.register_widget("prim", "path", PrimPathWidget())
                w.register_widget("prim", "references", PayloadReferenceWidget())
                w.register_widget("prim", "payloads", PayloadReferenceWidget(use_payloads=True))
                w.register_widget("prim", "variants", VariantsWidget())
                w.register_widget(
                    "prim",
                    "attribute",
                    RawUsdPropertiesWidget(title="Raw USD Properties", collapsed=True, enable_adapter=True),
                    False,
                )

                # A few examples. Expected to be removed at some point.
                # self._examples = Examples(w)
                for notifier in self._selection_notifiers:
                    notifier.start()
                    notifier.notify_property_window()  # force a refresh
                self._registered = True
        except Exception as exc:  # pylint: disable=broad-exception-caught  # pragma: no cover
            carb.log_error(f"register_widget error {exc}")

    def _unregister_widget(self):
        try:
            import omni.kit.window.property as p

            w = p.get_window()
            if w:
                for notifier in self._selection_notifiers:
                    notifier.stop()
                w.unregister_widget("prim", "attribute")
                w.unregister_widget("prim", "variants")
                w.unregister_widget("prim", "references")
                w.unregister_widget("prim", "payloads")
                w.unregister_widget("prim", "path")
                if self._examples:
                    self._examples.clean(w)
                    self._examples = None
                self._registered = False
        except Exception as e:  # pylint: disable=broad-exception-caught  # pragma: no cover
            carb.log_warn(f"Unable to unregister omni.usd.widget: {e}")


class SelectionNotifier:
    """
    A class to represent the selection notifier.
    """

    def __init__(self, usd_context_id="", property_window_context_id=""):
        """
        Initializes the selection notifier.

        Args:
            usd_context_id: The USD context ID.
            property_window_context_id: The property window context ID.
        """
        self._usd_context = omni.usd.get_context(usd_context_id)
        self._selection = self._usd_context.get_selection()
        self._property_window_context_id = property_window_context_id
        self._stage_event_sub = None

    def start(self):
        """
        Starts the selection notifier.
        """
        self._stage_event_sub = [
            get_eventdispatcher().observe_event(
                observer_name="omni.kit.property.usd:widgets",
                event_name=self._usd_context.stage_event_name(event),
                on_event=func,
            )
            for event, func in (
                (omni.usd.StageEventType.CLOSING, lambda _: self._on_stage_closing()),
                (omni.usd.StageEventType.CLOSED, lambda _: self._on_stage_closing()),
                (omni.usd.StageEventType.SELECTION_CHANGED, lambda _: self._on_selection_changed()),
            )
        ]

    def stop(self):
        """
        Stops the selection notifier.
        """
        self._stage_event_sub = None

    def _on_stage_closing(self):
        """Handles stage closing or closed"""
        omni.usd.get_context().get_selection().set_selected_prim_paths([], True)
        self.notify_property_window(save_scroll_pos=False)

    def _on_selection_changed(self):
        """Handles stage selection changed event"""
        self.notify_property_window(save_scroll_pos=True)

    def _keep_scroll_pos(self, w, old_payload, new_payload):
        if (not isinstance(old_payload, PrimSelectionPayload) or not isinstance(new_payload, PrimSelectionPayload)) or (
            old_payload.get_stage() != new_payload.get_stage()
        ):
            w.save_scroll_pos(reset=True)
            return

        stage = old_payload.get_stage()
        old_types = {stage.GetPrimAtPath(p).GetTypeName() for p in old_payload if p and stage.GetPrimAtPath(p)}
        new_types = {stage.GetPrimAtPath(p).GetTypeName() for p in new_payload if p and stage.GetPrimAtPath(p)}
        if old_types != new_types:
            w.save_scroll_pos(reset=True)
            return

        w.save_scroll_pos()

    def notify_property_window(self, save_scroll_pos: bool = False):
        """
        Notifies the property window.

        Args:
            save_scroll_pos: Whether to save the scroll position.
        """
        import omni.kit.window.property as p

        # TODO _property_window_context_id
        w = p.get_window()
        if w and self._usd_context:
            stage = None
            selected_paths = []
            if self._usd_context.get_stage_state() == omni.usd.StageState.OPENED:
                stage = weakref.ref(self._usd_context.get_stage())
                selected_paths = [Sdf.Path(path) for path in self._selection.get_selected_prim_paths()]
            payload = PrimSelectionPayload(stage, selected_paths)
            if save_scroll_pos:
                self._keep_scroll_pos(w, w.get_payload(), payload)
            else:
                self._keep_scroll_pos(w, None, None)

            w.notify("prim", payload)

    _notify_property_window = notify_property_window


class Examples:
    """
    Examples of showing how to use PropertyWindow APIs.
    """

    def __init__(self, w):
        """
        Initializes the examples.

        Args:
            w: The property window.
        """
        from .usd_property_widget import SchemaPropertiesWidget

        # Example of PropertySchemeDelegate
        class MeshWidget(SchemaPropertiesWidget):
            """
            A class to represent the mesh widget.
            """

            def __init__(self):
                """
                Initializes the mesh widget.
                """
                super().__init__("Mesh", UsdGeom.Mesh, False)

            def _group_helper(self, attr, group_prefix):
                """
                Helper to group attributes.
                """
                if attr.attr_name.startswith(group_prefix):
                    import re

                    attr.override_display_group(group_prefix.capitalize())
                    attr.override_display_name(re.sub(r"(\w)([A-Z])", r"\1 \2", attr.attr_name[len(group_prefix) :]))
                    return True
                return False

            def _filter_props_to_build(self, props):
                """
                Filters the properties to build.
                """
                schema_attr_names = self._schema.GetSchemaAttributeNames(self._include_inherited)
                schema_attr_names.append("material:binding")
                return [attr for attr in props if attr.GetName() in schema_attr_names]

            # Example of how to use _customize_props_layout
            def _customize_props_layout(self, props):
                """
                Customizes the properties layout.
                """
                auto_arrange = False
                if auto_arrange:
                    for attr in props:
                        if (
                            not self._group_helper(attr, "crease")
                            and not self._group_helper(attr, "corner")
                            and not self._group_helper(attr, "face")
                        ):
                            attr.override_display_group("Other")
                    return props

                from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
                from omni.kit.window.property.templates import HORIZONTAL_SPACING

                from .custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty

                frame = CustomLayoutFrame(hide_extra=False)
                with frame:
                    with CustomLayoutGroup("Face"):
                        CustomLayoutProperty("faceVertexCounts", "Vertex Counts")
                        CustomLayoutProperty("faceVertexIndices", "Vertex Indices")
                    with CustomLayoutGroup("Corner"):
                        CustomLayoutProperty("cornerIndices", "Indices")
                        CustomLayoutProperty("cornerSharpnesses", "Sharpnesses")
                    with CustomLayoutGroup("Crease"):
                        CustomLayoutProperty("creaseIndices", "Indices")
                        CustomLayoutProperty("creaseLengths", "Lengths")
                    with CustomLayoutGroup("CustomItems"):
                        with CustomLayoutGroup("Nested"):

                            def build_fn(
                                stage,
                                attr_name,
                                metadata,
                                property_type,
                                prim_paths: List[Sdf.Path],
                                additional_label_kwargs=None,
                                additional_widget_kwarg=None,
                            ):
                                with ui.HStack(spacing=HORIZONTAL_SPACING):
                                    UsdPropertiesWidgetBuilder.create_label(
                                        "Cool Label", additional_label_kwargs={"tooltip": "Cool Tooltip"}
                                    )
                                    ui.Button("Cool Button")
                                with ui.HStack(spacing=HORIZONTAL_SPACING):
                                    UsdPropertiesWidgetBuilder.create_label("Very Cool Label")
                                    ui.Button("Super Cool Button")

                            CustomLayoutProperty(None, None, build_fn=build_fn)
                return frame.apply(props)

            def get_additional_kwargs(self, ui_prop):
                if ui_prop[0] == "material:binding":
                    from pxr import UsdShade

                    return None, {"target_picker_filter_type_list": [UsdShade.Material], "targets_limit": 1}
                return None, None

        w.register_widget("prim", "mesh", MeshWidget())
        self._w = w

    def __del__(self):
        """
        Deletes the examples.
        """
        self._w.unregister_widget("prim", "mesh")

    def clean(self, w):
        """
        Cleans the examples.

        Args:
            w: The property window.
        """
