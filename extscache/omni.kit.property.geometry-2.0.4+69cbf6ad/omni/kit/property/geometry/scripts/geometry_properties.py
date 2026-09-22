from functools import partial
from typing import Any, Callable

import carb
import omni.ext
import omni.kit.app
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from pxr import Sdf, Tf, Usd, UsdGeom, UsdUI

_extension_instance = None


def get_instance():
    """Return the current instance of the extension.

    Returns:
        Any: The current extension instance if set; otherwise, None.
    """
    return _extension_instance


def register_custom_visual_attribute(
    attribute_name: str,
    display_name: str,
    type_name: str,
    default_value: Any,
    predicate: Callable[[Any], bool] = None,
):
    if _extension_instance:
        return _extension_instance.register_custom_visual_attribute(
            attribute_name, display_name, type_name, default_value, predicate
        )
    return None


def deregister_custom_visual_attribute(attribute_name: str):
    if _extension_instance:
        return _extension_instance.deregister_custom_visual_attribute(attribute_name)
    return None


class GeometryPropertyExtension(omni.ext.IExt):
    """A class for extending and modifying geometry properties in the USD stage.

    This extension registers widgets and menu entries to manage geometry and visual attributes associated with prims. It integrates with the application window to provide interactive controls for toggling various rendering and property settings such as instanceable state, wireframe display, and shadow properties, among others. The extension also supports the registration of custom visual attributes, allowing dynamic updates to prim properties based on user interaction.

    Designed to interface with the Omniverse Kit SDK, the class carefully validates prim selection and type before executing property commands. It leverages the underlying command system to update attribute states and ensures the property widgets are correctly registered and unregistered during the extension lifecycle.

    Example usage:
    .. code-block:: python

        extension = GeometryPropertyExtension()
        extension.on_startup('my_extension')
    """

    def __init__(self):
        """Initializes a new GeometryPropertyExtension instance."""
        self._registered = False
        self._button_menu_entry = []
        self._visual_property_widget = None
        super().__init__()

    def on_startup(self, ext_id):
        """Handles startup operations including widget registration and menu entry creation.

        Args:
            ext_id (str): Extension identifier for startup configuration.
        """
        global _extension_instance
        _extension_instance = self

        self._register_widget()

        # +add menu item(s)
        from omni.kit.property.usd import PrimPathWidget

        context_menu = omni.kit.widget.context_menu.get_instance()
        if context_menu is None:
            carb.log_error("context_menu is disabled!")  # pragma: no cover
            return  # pragma: no cover

        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Instanceable",
                show_fn=self._is_prim_selected,
                onclick_fn=self._click_toggle_instanceable,
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Wireframe Mode",
                name_fn=partial(self._get_primvar_state, prim_name="wireframe", text_name=" Wireframe Mode"),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="wireframe"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Do Not Cast Shadows",
                name_fn=partial(
                    self._get_primvar_state, prim_name="doNotCastShadows", text_name=" Do Not Cast Shadows"
                ),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="doNotCastShadows"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Enable Shadow Terminator Fix",
                name_fn=partial(
                    self._get_primvar_state,
                    prim_name="enableShadowTerminatorFix",
                    text_name=" Enable Shadow Terminator Fix",
                ),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="enableShadowTerminatorFix"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Enable Fast Refraction Shadow",
                name_fn=partial(
                    self._get_primvar_state,
                    prim_name="enableFastRefractionShadow",
                    text_name=" Enable Fast Refraction Shadow",
                ),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="enableFastRefractionShadow"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Disable RT SSS Transmission",
                name_fn=partial(
                    self._get_primvar_state,
                    prim_name="disableRtSssTransmission",
                    text_name=" Disable RT SSS Transmission",
                ),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="disableRtSssTransmission"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Multimatted ID:",
                name_fn=partial(self._get_primvar_state, prim_name="multimatte_id", text_name=" ID for multimatte"),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="multimatte_id"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Enable Holdout Object",
                name_fn=partial(self._get_primvar_state, prim_name="holdoutObject", text_name=" Enable Holdout Object"),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="holdoutObject"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Invisible To Secondary Rays",
                name_fn=partial(
                    self._get_primvar_state,
                    prim_name="invisibleToSecondaryRays",
                    text_name=" Invisible To Secondary Rays",
                ),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="invisibleToSecondaryRays"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Is Procedural Volume",
                name_fn=partial(self._get_primvar_state, prim_name="isVolume", text_name=" Is Volume"),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="isVolume"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Matte Object",
                name_fn=partial(self._get_primvar_state, prim_name="isMatteObject", text_name=" Matte Object"),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="isMatteObject"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Invisible to Primary Ray",
                name_fn=partial(
                    self._get_primvar_state, prim_name="hideForCamera", text_name=" Invisible to Primary Ray"
                ),
                show_fn=[partial(self._prim_is_type, prim_type=UsdGeom.Boundable)],
                onclick_fn=partial(self._click_set_primvar, prim_name="hideForCamera"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Is Light",
                name_fn=partial(self._get_primvar_state, prim_name="isLight", text_name=" Is Light"),
                show_fn=[partial(self._prim_is_type, prim_type=UsdGeom.Boundable)],
                onclick_fn=partial(self._click_set_primvar, prim_name="isLight"),
            )
        )
        self._button_menu_entry.append(
            PrimPathWidget.add_button_menu_entry(
                "Rendering/Toggle Disable Auto Lod",
                name_fn=partial(
                    self._get_primvar_state, prim_name="disableAutoLod", text_name=" Disable Auto LOD generation"
                ),
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Boundable),
                onclick_fn=partial(self._click_set_primvar, prim_name="disableAutoLod"),
            )
        )

    def on_shutdown(self):  # pragma: no cover
        """Handles shutdown operations by unregistering widgets and releasing the extension instance."""
        if self._registered:
            self._unregister_widget()

        # release menu item(s)
        from omni.kit.property.usd import PrimPathWidget

        for item in self._button_menu_entry:
            PrimPathWidget.remove_button_menu_entry(item)

        global _extension_instance
        _extension_instance = None

    def register_custom_visual_attribute(
        self,
        attribute_name: str,
        display_name: str,
        type_name: str,
        default_value: Any,
        predicate: Callable[[Any], bool] = None,
    ):
        """Add custom attribute with placeholder.

        Args:
            attribute_name (str): Name of the attribute.
            display_name (str): Display name for the attribute.
            type_name (str): Type name of the attribute.
            default_value (Any): Default value assigned to the attribute.
            predicate (Callable[[Any], bool]): Function returning a boolean for attribute condition.
        """
        if self._visual_property_widget:
            self._visual_property_widget.add_custom_attribute(
                attribute_name, display_name, type_name, default_value, predicate
            )

    def deregister_custom_visual_attribute(self, attribute_name: str):
        """Removes the custom visual attribute from the visual property widget.

        Args:
            attribute_name (str): Name of the attribute to remove.
        """
        if self._visual_property_widget:
            self._visual_property_widget.remove_custom_attribute(attribute_name)

    def _prim_is_type(self, objects: dict, prim_type: Tf.Type) -> bool:
        """
        Checks if prims are given class/schema
        """
        if "stage" not in objects or "prim_list" not in objects or not objects["stage"]:  # pragma: no cover
            return False

        stage = objects["stage"]
        if not stage:  # pragma: no cover
            return False

        prim_list = objects["prim_list"]
        for path in prim_list:
            if isinstance(path, Usd.Prim):
                prim = path  # pragma: no cover
            else:
                prim = stage.GetPrimAtPath(path)
            if prim and not prim.IsA(prim_type):
                return False  # pragma: no cover

        return len(prim_list) > 0

    def _is_prim_selected(self, objects: dict):
        """
        Checks if any prims are selected
        """
        if not any(item in objects for item in ["prim", "prim_list"]):  # pragma: no cover
            return False
        return True

    def _register_widget(self):
        import omni.kit.window.property as p

        from .prim_geometry_widget import GeometrySchemaAttributesWidget, ImageableSchemaAttributesWidget
        from .prim_kind_widget import PrimKindWidget

        w = p.get_window()
        if w:

            w.register_widget(
                "prim",
                "geometry",
                GeometrySchemaAttributesWidget(
                    "Geometry",
                    UsdGeom.Xformable,
                    [
                        UsdGeom.BasisCurves,
                        UsdGeom.Capsule,
                        UsdGeom.Cone,
                        UsdGeom.Cube,
                        UsdGeom.Cylinder,
                        UsdGeom.HermiteCurves,
                        UsdGeom.Mesh,
                        UsdGeom.NurbsCurves,
                        UsdGeom.NurbsPatch,
                        UsdGeom.PointInstancer,
                        UsdGeom.Points,
                        UsdGeom.Subset,
                        UsdGeom.Sphere,
                        UsdGeom.Xform,
                        UsdGeom.Gprim,
                        UsdGeom.PointBased,
                        UsdGeom.Boundable,
                        UsdGeom.Curves,
                        UsdGeom.Imageable,
                        UsdGeom.PointBased,
                        UsdGeom.Subset,
                        UsdGeom.ModelAPI,
                        UsdGeom.MotionAPI,
                        UsdGeom.PrimvarsAPI,
                        UsdGeom.XformCommonAPI,
                        UsdGeom.ModelAPI,
                        UsdUI.Backdrop,
                        UsdUI.NodeGraphNodeAPI,
                        UsdUI.SceneGraphPrimAPI,
                    ],
                    [
                        "proceduralMesh:parameterCheck",
                        "outputs:parameterCheck",
                        "refinementEnableOverride",
                        "refinementLevel",
                        "primvars:doNotCastShadows",
                        "primvars:enableShadowTerminatorFix",
                        "primvars:enableFastRefractionShadow",
                        "primvars:disableRtSssTransmission",
                        "primvars:disableAutoLod",
                        "primvars:holdoutObject",
                        "primvars:invisibleToSecondaryRays",
                        "primvars:isMatteObject",
                        "primvars:isVolume",
                        "primvars:multimatte_id",
                        "primvars:numSplits",
                        "primvars:endcaps",
                        UsdGeom.Tokens.proxyPrim,
                    ],
                    [
                        "primvars:displayColor",
                        "primvars:displayOpacity",
                        "doubleSided",
                        "purpose",
                        "visibility",
                        "xformOpOrder",
                    ],
                ),
            )

            self._visual_property_widget = ImageableSchemaAttributesWidget(
                "Visual",
                UsdGeom.Imageable,
                [],
                ["primvars:displayColor", "primvars:displayOpacity", "doubleSided", "singleSided"],
                [],
            )

            w.register_widget(
                "prim",
                "geometry_imageable",
                self._visual_property_widget,
            )

            w.register_widget("prim", "kind", PrimKindWidget())
            self._registered = True

    def _unregister_widget(self):  # pragma: no cover
        import omni.kit.window.property as p

        w = p.get_window()
        if w:
            w.unregister_widget("prim", "geometry")
            w.unregister_widget("prim", "geometry_imageable")
            w.unregister_widget("prim", "kind")
            self._registered = False

    def _click_set_primvar(self, payload: PrimSelectionPayload, prim_name: str):
        stage = payload.get_stage()
        if not stage:  # pragma: no cover
            return

        omni.kit.commands.execute("TogglePrimVarCommand", prim_path=payload.get_paths(), prim_name=prim_name)

    def _get_primvar_state(self, objects: dict, prim_name: str, text_prefix: str = "", text_name: str = "") -> str:
        if "stage" not in objects or "prim_list" not in objects or not objects["stage"]:  # pragma: no cover
            return None
        stage = objects["stage"]
        primvar_state = []
        for path in objects["prim_list"]:
            prim = stage.GetPrimAtPath(path) if isinstance(path, Sdf.Path) else path
            if prim:
                primvars_api = UsdGeom.PrimvarsAPI(prim)
                is_primvar = primvars_api.GetPrimvar(prim_name)
                if is_primvar:
                    primvar_state.append(is_primvar.Get())
                else:
                    primvar_state.append(False)

        if primvar_state == [False] * len(primvar_state):
            return f"{text_prefix}Set{text_name}"
        if primvar_state == [True] * len(primvar_state):
            return f"{text_prefix}Clear{text_name}"

        return f"{text_prefix}Toggle{text_name}"  # pragma: no cover

    def _click_toggle_instanceable(self, payload: PrimSelectionPayload):
        omni.kit.commands.execute("ToggleInstanceableCommand", prim_path=payload.get_paths())
