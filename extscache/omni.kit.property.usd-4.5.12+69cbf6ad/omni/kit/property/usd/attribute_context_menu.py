# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = []

import contextlib
import weakref
from functools import partial

import carb
import omni.kit.commands
import omni.kit.undo
import omni.kit.widget.context_menu
import omni.usd
from omni.kit.usd.layers import LayerEditMode, get_layers
from pxr import Sdf

from .usd_attribute_model import (
    GfVecAttributeModel,
    MdlEnumAttributeModel,
    TfTokenAttributeModel,
    UsdAttributeModel,
    UsdBase,
)


class AttributeContextMenuEvent:
    """
    Event for the attribute context menu.
    """

    def __init__(self, widget, attribute_paths, stage, time_code, model, comp_index):
        self.widget = widget
        self.attribute_paths = attribute_paths
        self.stage = stage
        self.time_code = time_code
        self.model = model
        self.comp_index = comp_index
        self.type = 0


class AttributeContextMenu:
    """
    Attribute context menu.
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Get the instance of the attribute context menu.
        """
        return weakref.proxy(cls._instance)

    def __init__(self):
        """
        Initialize the attribute context menu.
        """
        self._paste_menu_entry = None
        self._delete_menu_entry = None
        self._copy_path_menu_entry = None
        self._copy_menu_entry = None
        self._register_context_menus()

        AttributeContextMenu._instance = self

    def __del__(self):
        """
        Delete the attribute context menu.
        """
        self.destroy()

    def destroy(self):
        """
        Destroy the attribute context menu.
        """
        self._copy_menu_entry = None
        self._paste_menu_entry = None
        self._delete_menu_entry = None
        self._copy_path_menu_entry = None

        AttributeContextMenu._instance = None

    def on_mouse_event(self, event: AttributeContextMenuEvent):
        """
        On mouse event.

        Args:
            event (AttributeContextMenuEvent): The event.
        """
        import omni.kit.menu.core

        # check its expected event
        if event.type != int(omni.kit.menu.core.MenuEventType.ACTIVATE):  # pragma: no cover
            return

        # setup objects, this is passed to all functions
        objects = {
            "widget": event.widget,
            "stage": event.stage,
            "attribute_paths": event.attribute_paths,
            "time_code": event.time_code,
            "model": event.model,
            "comp_index": event.comp_index,
        }

        menu_list = omni.kit.widget.context_menu.get_menu_dict("attribute", "omni.kit.property.usd")

        stage = event.stage
        if stage:
            usd_context = omni.usd.get_context()
            layers = get_layers(usd_context)
            edit_mode = layers.get_edit_mode()
            auto_authoring = layers.get_auto_authoring()
            layers_state = layers.get_layers_state()
            if edit_mode == LayerEditMode.SPECS_LINKING:
                per_layer_link_menu = []
                for layer in stage.GetLayerStack():
                    if auto_authoring.is_auto_authoring_layer(layer.identifier):
                        continue

                    layer_name = layers_state.get_layer_name(layer.identifier)
                    per_layer_link_menu.append(
                        {
                            "name": {
                                f"{layer_name}": [
                                    {
                                        "name": "Link",
                                        "show_fn": [],
                                        "onclick_fn": partial(self._link_attributes, True, layer.identifier),
                                    },
                                    {
                                        "name": "Unlink",
                                        "show_fn": [],
                                        "onclick_fn": partial(self._link_attributes, False, layer.identifier),
                                    },
                                ]
                            }
                        }
                    )

                menu_list.append(
                    {
                        "name": {"Layers": per_layer_link_menu},
                        "glyph": "",
                    }
                )

            menu_list.extend([{"name": ""}])
            menu_list.append(
                {
                    "name": {
                        "Locks": [
                            {
                                "name": "Lock",
                                "show_fn": [],
                                "onclick_fn": partial(self._lock_attributes, True),
                            },
                            {
                                "name": "Unlock",
                                "show_fn": [],
                                "onclick_fn": partial(self._lock_attributes, False),
                            },
                        ]
                    },
                    "glyph": "",
                }
            )

        omni.kit.widget.context_menu.get_instance().show_context_menu("attribute", objects, menu_list)

    def _link_attributes(self, link_or_unlink, layer_identifier, objects):
        """
        Link attributes.

        Args:
            link_or_unlink (bool): Whether to link or unlink.
            layer_identifier (str): The layer identifier.
        """
        attribute_paths = objects.get("attribute_paths", None)
        if not attribute_paths:  # pragma: no cover
            return

        if link_or_unlink:
            command = "LinkSpecs"
        else:
            command = "UnlinkSpecs"

        omni.kit.commands.execute(command, spec_paths=attribute_paths, layer_identifiers=layer_identifier)

    def _lock_attributes(self, lock_or_unlock, objects):
        """
        Lock attributes.

        Args:
            lock_or_unlock (bool): Whether to lock or unlock.
        """
        attribute_paths = objects.get("attribute_paths", None)
        if attribute_paths:
            if lock_or_unlock:
                command = "LockSpecs"
            else:
                command = "UnlockSpecs"

            omni.kit.commands.execute(command, spec_paths=attribute_paths)

    def _register_context_menus(self):
        """
        Register the context menus.
        """
        self._register_copy_paste_menus()
        self._register_delete_prop_menu()
        self._register_copy_prop_path_menu()

    def _register_copy_paste_menus(self):
        """
        Register the copy paste menus.
        """

        def can_show_copy_paste(obj):
            """
            Can show copy paste.

            Args:
                obj (dict): The object.
            """
            model = obj.get("model", None)
            return isinstance(model, UsdBase) if model else False

        def can_copy(obj):
            """
            Can copy.

            Args:
                obj (dict): The object.

            Returns:
                bool: Whether the copy is enabled.
            """
            model: UsdBase = obj.get("model", None)

            # Only support copying during single select per OM-20206
            paths = model.get_property_paths() if model else []
            if len(paths) > 1:  # pragma: no cover
                return False

            comp_index = obj.get("comp_index", -1)
            return not model.is_comp_ambiguous(comp_index) and isinstance(
                model, (UsdAttributeModel, TfTokenAttributeModel, MdlEnumAttributeModel, GfVecAttributeModel)
            )

        def on_copy(obj):
            """
            On copy.

            Args:
                obj (dict): The object.
            """
            model = obj.get("model", None)
            if not model:  # pragma: no cover
                return

            if isinstance(model, UsdAttributeModel):
                value_str = model.get_value_as_string(elide_big_array=False)
            elif isinstance(model, TfTokenAttributeModel):
                value_str = model.get_value_as_token()
            elif isinstance(model, MdlEnumAttributeModel):
                value_str = model.get_value_as_string()
            elif isinstance(model, GfVecAttributeModel):
                value_str = str(model.construct_vector_from_item())
            else:  # pragma: no cover
                carb.log_warn("Unsupported type to copy")
                return

            omni.kit.clipboard.copy(value_str)

        menu = {
            "name": "Copy",
            "show_fn": can_show_copy_paste,
            "enabled_fn": can_copy,
            "onclick_fn": on_copy,
        }
        self._copy_menu_entry = omni.kit.widget.context_menu.add_menu(menu, "attribute", "omni.kit.property.usd")

        # If type conversion fails, function raise exception and disables menu entry/quit paste
        def convert_type(value_type, value_str: str):
            import ast

            if value_type in (str, Sdf.AssetPath, Sdf.Path):
                return value_str
            if value_type == Sdf.AssetPathArray:
                # Copied AssetPathArray is in this format:
                # [@E:/USD/foo.usd@, @E:/USD/bar.usd@]
                # parse it manually
                value_str = value_str.strip("[] ")
                paths = value_str.split(", ")
                paths = [path.strip("@") for path in paths]
                return paths

            retval = ""
            with contextlib.suppress(Exception):
                retval = value_type(ast.literal_eval(value_str))

            return retval

        def can_paste(obj):
            """
            Can paste.

            Args:
                obj (dict): The object.

            Returns:
                bool: Whether the paste is enabled.
            """
            model = obj.get("model", None)
            widget = obj.get("widget", None)
            if not model:  # pragma: no cover
                return False

            if not widget or not widget.enabled:  # pragma: no cover
                return False

            comp_index = obj.get("comp_index", -1)

            paste = omni.kit.clipboard.paste()
            if paste:
                ret = True
                if isinstance(model, UsdAttributeModel):
                    value = model.get_value_by_comp(comp_index)
                    if not convert_type(type(value), paste):
                        return False
                elif isinstance(model, TfTokenAttributeModel):  # pragma: no cover
                    if not model.is_allowed_token(paste):
                        raise ValueError(f"Token {paste} is not allowed on this attribute")
                elif isinstance(model, MdlEnumAttributeModel):  # pragma: no cover
                    if not model.is_allowed_enum_string(paste):
                        raise ValueError(f"Enum {paste} is not allowed on this attribute")
                elif isinstance(model, GfVecAttributeModel):  # pragma: no cover
                    value = model.get_value()
                    if not convert_type(type(value), paste):
                        return False
                else:  # pragma: no cover
                    carb.log_warn("Unsupported type to paste to")
                    ret = False
                return ret

            return False  # pragma: no cover

        def on_paste(obj):
            """
            On paste.

            Args:
                obj (dict): The object.
            """
            model = obj.get("model", None)
            if not model:  # pragma: no cover
                return

            comp_index = obj.get("comp_index", -1)
            value = model.get_value_by_comp(comp_index)

            paste = omni.kit.clipboard.paste()
            if paste:
                if isinstance(model, (UsdAttributeModel, TfTokenAttributeModel, GfVecAttributeModel)):
                    typed_value = convert_type(type(value), paste)
                    model.set_value(typed_value)
                elif isinstance(model, MdlEnumAttributeModel):
                    model.set_from_enum_string(paste)

        menu = {
            "name": "Paste",
            "show_fn": can_show_copy_paste,
            "enabled_fn": can_paste,
            "onclick_fn": on_paste,
        }
        self._paste_menu_entry = omni.kit.widget.context_menu.add_menu(menu, "attribute", "omni.kit.property.usd")

    def _register_delete_prop_menu(self):
        """
        Register the delete property menu.
        """

        def can_show_delete(obj):
            """
            Can show delete.

            Args:
                obj (dict): The object.
            """
            model = obj.get("model", None)
            if not model:  # pragma: no cover
                return False

            stage = model.stage
            if not stage:  # pragma: no cover
                return False

            # OM-49324 Hide the Remove context menu for xformOp attributes
            # Cannot simply remove an xformOp attribute. Leave it to transform widget context menu
            paths = model.get_attribute_paths()
            for path in paths:
                # TODO: Usdrt does not have Property objects
                prop = stage.GetPropertyAtPath(path)
                if not prop or prop.GetName().startswith("xformOp:"):  # pragma: no cover
                    return False

            return isinstance(model, UsdBase)

        def can_delete(obj):
            """
            Can delete.

            Args:
                obj (dict): The object.

            Returns:
                bool: Whether the delete is enabled.
            """
            model = obj.get("model", None)
            if not model:  # pragma: no cover
                return False

            stage = model.stage
            if not stage:  # pragma: no cover
                return False

            paths = model.get_attribute_paths()
            for path in paths:
                prop = stage.GetPropertyAtPath(path)
                if prop:
                    prim = prop.GetPrim()
                    prim_definition = prim.GetPrimDefinition()

                    # If the property is part of a schema, it cannot be completely removed. Removing it will simply reset to default value
                    # usdrt don't support it
                    with contextlib.suppress(Exception):
                        prop_spec = prim_definition.GetSchemaPropertySpec(prop.GetPath().name)
                        if prop_spec:
                            return False

                else:  # pragma: no cover
                    return False
            return True  # pragma: no cover

        def on_delete(obj):
            """
            On delete.

            Args:
                obj (dict): The object.
            """
            model = obj.get("model", None)
            if model:
                paths = model.get_attribute_paths()
                with omni.kit.undo.group():
                    for path in paths:
                        omni.kit.commands.execute("RemoveProperty", prop_path=path)

        menu = {
            "name": "Remove",
            "show_fn": can_show_delete,
            "enabled_fn": can_delete,
            "onclick_fn": on_delete,
        }
        self._delete_menu_entry = omni.kit.widget.context_menu.add_menu(menu, "attribute", "omni.kit.property.usd")

    def _register_copy_prop_path_menu(self):
        """
        Register the copy property path menu.
        """

        def can_show_copy_path(obj):
            """
            Can show copy path.

            Args:
                obj (dict): The object.

            Returns:
                bool: Whether the copy path is enabled.
            """
            model = obj.get("model", None)
            stage = model.stage if model else None
            return isinstance(model, UsdBase) if stage else False

        def can_copy_path(obj):
            """
            Can copy path.

            Args:
                obj (dict): The object.

            Returns:
                bool: Whether the copy path is enabled.
            """
            model = obj.get("model", None)
            stage = model.stage if model else None
            paths = model.get_attribute_paths() if stage else []
            return len(paths) == 1

        def on_copy_path(obj):
            """
            On copy path.

            Args:
                obj (dict): The object.
            """
            model = obj.get("model", None)
            if model:
                paths = model.get_attribute_paths()
                omni.kit.clipboard.copy(paths[-1].pathString)

        menu = {
            "name": "Copy Property Path",
            "show_fn": can_show_copy_path,
            "enabled_fn": can_copy_path,
            "onclick_fn": on_copy_path,
        }
        self._copy_path_menu_entry = omni.kit.widget.context_menu.add_menu(menu, "attribute", "omni.kit.property.usd")
