"""Provides a custom extension to manipulate USD property widgets for transformations in Omniverse Kit."""

__all__ = ["TransformPropertyExtension"]

from functools import partial
from pathlib import Path

import carb
import omni.ext
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from pxr import Tf, Usd, UsdGeom

from . import transform_builder, xform_op_utils
from .transform_widget import TransformAttributeWidget


class TransformPropertyExtension(omni.ext.IExt):
    """A class designed to extend the functionality of USD property widgets in Omniverse Kit.

    This extension adds context menu options and a custom widget to manipulate transformation properties of USD prims. It enables adding, disabling, deleting, and enabling various transformation operations like translate, rotate, scale, and pivot directly from the property window's context menu. It also handles the startup and shutdown processes for registering and unregistering the custom widget and menu items.
    """

    def __init__(self):
        """Initializes the TransformPropertyExtension object."""
        self._registered = False
        self._settings = None
        self._on_enable_menu = None
        self._separator_menu = None
        self._on_disable_menu = None
        self._on_delete_menu = None
        self._on_enable_menu = None
        self._add_button_menu = []

        super().__init__()

    def on_startup(self, ext_id):
        """Called when the extension is started.

        Args:
            ext_id (str): The ID of the extension being started."""
        manager = omni.kit.app.get_app().get_extension_manager()
        extension_path = manager.get_extension_path(ext_id)
        transform_builder.ICON_PATH = Path(extension_path).joinpath("data").joinpath("icons")
        self._register_widget()

        self._register_context_menu()

        from omni.kit.property.usd import PrimPathWidget

        self._add_button_menu = []
        context_menu = omni.kit.widget.context_menu.get_instance()
        if context_menu is None:
            carb.log_error("context_menu is disabled!")
            return
        self._settings = carb.settings.get_settings()

        self._add_button_menu.append(
            PrimPathWidget.add_button_menu_entry(
                "TransformOp/Translate, Rotate, Scale",
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Xformable),
                onclick_fn=partial(
                    self._add_xform_op,
                    add_translate_op=True,
                    add_rotate_xyz_op=True,
                    add_orient_op=False,
                    add_scale_op=True,
                    add_transform_op=False,
                ),
            )
        )
        self._add_button_menu.append(
            PrimPathWidget.add_button_menu_entry(
                "TransformOp/Translate, Orient, Scale",
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Xformable),
                onclick_fn=partial(
                    self._add_xform_op,
                    add_translate_op=True,
                    add_rotate_xyz_op=False,
                    add_orient_op=True,
                    add_scale_op=True,
                    add_transform_op=False,
                ),
            )
        )
        self._add_button_menu.append(
            PrimPathWidget.add_button_menu_entry(
                "TransformOp/Transform",
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Xformable),
                onclick_fn=partial(
                    self._add_xform_op,
                    add_translate_op=False,
                    add_rotate_xyz_op=False,
                    add_orient_op=False,
                    add_scale_op=False,
                    add_transform_op=True,
                ),
            )
        )
        self._add_button_menu.append(
            PrimPathWidget.add_button_menu_entry(
                "TransformOp/Pivot",
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Xformable),
                onclick_fn=partial(
                    self._add_xform_op,
                    add_translate_op=False,
                    add_rotate_xyz_op=False,
                    add_orient_op=False,
                    add_scale_op=False,
                    add_transform_op=False,
                    add_pivot=True,
                ),
            )
        )
        self._add_button_menu.append(
            PrimPathWidget.add_button_menu_entry(
                "TransformOp/",
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Xformable),
            )
        )
        self._add_button_menu.append(
            PrimPathWidget.add_button_menu_entry(
                "TransformOp/Translate",
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Xformable),
                onclick_fn=partial(
                    self._add_xform_op,
                    add_translate_op=True,
                    add_rotate_xyz_op=False,
                    add_orient_op=False,
                    add_scale_op=False,
                    add_transform_op=False,
                ),
            )
        )
        self._add_button_menu.append(
            PrimPathWidget.add_button_menu_entry(
                "TransformOp/Rotate",
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Xformable),
                onclick_fn=partial(
                    self._add_xform_op,
                    add_translate_op=False,
                    add_rotate_xyz_op=True,
                    add_orient_op=False,
                    add_scale_op=False,
                    add_transform_op=False,
                ),
            )
        )
        self._add_button_menu.append(
            PrimPathWidget.add_button_menu_entry(
                "TransformOp/Orient",
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Xformable),
                onclick_fn=partial(
                    self._add_xform_op,
                    add_translate_op=False,
                    add_rotate_xyz_op=False,
                    add_orient_op=True,
                    add_scale_op=False,
                    add_transform_op=False,
                ),
            )
        )
        self._add_button_menu.append(
            PrimPathWidget.add_button_menu_entry(
                "TransformOp/Scale",
                show_fn=partial(self._prim_is_type, prim_type=UsdGeom.Xformable),
                onclick_fn=partial(
                    self._add_xform_op,
                    add_translate_op=False,
                    add_rotate_xyz_op=False,
                    add_orient_op=False,
                    add_scale_op=True,
                    add_transform_op=False,
                ),
            )
        )

    def on_shutdown(self):
        """Called when the extension is shut down."""
        if self._registered:
            self._unregister_widget()

        # release menu item(s)
        from omni.kit.property.usd import PrimPathWidget

        for item in self._add_button_menu:
            PrimPathWidget.remove_button_menu_entry(item)

        # release context menu items
        self._unregister_context_menu()

    def _add_xform_op(
        self,
        payload: PrimSelectionPayload,
        add_translate_op: bool,
        add_rotate_xyz_op: bool,
        add_orient_op: bool,
        add_scale_op: bool,
        add_transform_op: bool,
        add_pivot=False,
    ):
        # Retrieve the default precision
        default_xform_op_precision = self._settings.get("/persistent/app/primCreation/DefaultXformOpPrecision")
        if default_xform_op_precision is None:
            self._settings.set_default_string("/persistent/app/primCreation/DefaultXformOpPrecision", "Double")
            default_xform_op_precision = "Double"

        _precision = None
        if default_xform_op_precision == "Double":
            _precision = UsdGeom.XformOp.PrecisionDouble
        elif default_xform_op_precision == "Float":
            _precision = UsdGeom.XformOp.PrecisionFloat
        elif default_xform_op_precision == "Half":
            _precision = UsdGeom.XformOp.PrecisionHalf

        # No operation is carried out if precision is not properly set
        if _precision is None:
            carb.log_error(
                "The default xform op precision is not properly set! Please set it in the Edit/Preferences/Stage window!"
            )
            return

        # Retrieve the default rotation order
        default_rotation_order = self._settings.get("/persistent/app/primCreation/DefaultRotationOrder")
        if default_rotation_order is None:
            self._settings.set_default_string("persistent/app/primCreation/DefaultRotationOrder", "XYZ")
            default_rotation_order = "XYZ"

        omni.kit.commands.execute(
            "AddXformOp",
            payload=payload,
            precision=_precision,
            rotation_order=default_rotation_order,
            add_translate_op=add_translate_op,
            add_rotate_xyz_op=add_rotate_xyz_op,
            add_orient_op=add_orient_op,
            add_scale_op=add_scale_op,
            add_transform_op=add_transform_op,
            add_pivot_op=add_pivot,
        )
        import omni.kit.window.property as p

        p.get_window().request_rebuild()

    def _prim_is_type(self, objects: dict, prim_type: Tf.Type) -> bool:
        """
        Checks if prims are given class/schema
        """
        if "stage" not in objects or "prim_list" not in objects or not objects["stage"]:
            return False

        stage = objects["stage"]
        if not stage:
            return False

        prim_list = objects["prim_list"]
        for path in prim_list:
            if isinstance(path, Usd.Prim):
                prim = path
            else:
                prim = stage.GetPrimAtPath(path)
            if prim and not prim.IsA(prim_type):
                return False

        return len(prim_list) > 0

    def _register_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        if w:
            w.register_widget("prim", "transform", TransformAttributeWidget(title="Transform", collapsed=False))
            self._registered = True

    def _unregister_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        if w:
            w.unregister_widget("prim", "transform")
            self._registered = False

    # Context menu to Disable/Delete/Enable transform widgets
    def _register_context_menu(self):
        import omni.kit.widget.context_menu

        menu_sep = {
            "name": "",
        }
        self._separator_menu = omni.kit.widget.context_menu.add_menu(menu_sep, "attribute", "omni.kit.property.usd")

        # Disable Menu
        def _can_show_disable(objects):
            # pylint: disable=protected-access

            model = objects.get("model", None)
            if hasattr(model, "transform_widget"):
                builder_widget = model.transform_widget
                if builder_widget and (
                    (xform_op_utils.is_reset_xform_stack_op(builder_widget._op_name))
                    or (builder_widget._op_name is not None and builder_widget._attr_path is not None)
                    or (builder_widget._op_name is not None and builder_widget._attr_path is None)
                ):
                    return True
            return False

        def _on_disable(objects):
            # pylint: disable=protected-access

            model = objects.get("model", None)
            if model and hasattr(model, "transform_widget"):
                builder_widget = model.transform_widget
                if builder_widget:
                    builder_widget._delete_op_only()

        menu_disable = {"name": "Disable", "show_fn": _can_show_disable, "onclick_fn": _on_disable}
        self._on_disable_menu = omni.kit.widget.context_menu.add_menu(
            menu_disable, "attribute", "omni.kit.property.usd"
        )

        # Delete Menu
        def _can_show_delete(objects):
            # pylint: disable=protected-access
            model = objects.get("model", None)
            if model and hasattr(model, "transform_widget"):
                builder_widget = model.transform_widget
                if builder_widget:
                    if xform_op_utils.is_reset_xform_stack_op(builder_widget._op_name):
                        return False
                    if builder_widget._attr_path is not None:
                        return True
            return False

        def _on_delete(objects):
            # pylint: disable=protected-access

            model = objects.get("model", None)
            if model and hasattr(model, "transform_widget"):
                builder_widget = model.transform_widget
                if builder_widget:
                    if builder_widget._op_name is not None:
                        builder_widget._delete_op_and_attribute()
                    else:
                        builder_widget._delete_non_op_attribute()

        menu_delete = {"name": "Delete", "show_fn": _can_show_delete, "onclick_fn": _on_delete}

        self._on_delete_menu = omni.kit.widget.context_menu.add_menu(menu_delete, "attribute", "omni.kit.property.usd")

        # Enable Menu
        def _can_show_enable(objects):
            # pylint: disable=protected-access
            model = objects.get("model", None)
            if model and hasattr(model, "transform_widget"):
                builder_widget = model.transform_widget
                if builder_widget and builder_widget._op_name is None and builder_widget._attr_path is not None:
                    return True
            return False

        def _on_enable(objects):
            # pylint: disable=protected-access
            model = objects.get("model", None)
            if model and hasattr(model, "transform_widget"):
                builder_widget = model.transform_widget
                if builder_widget:
                    builder_widget._add_non_op_attribute_to_op()

        menu_enable = {"name": "Enable", "show_fn": _can_show_enable, "onclick_fn": _on_enable}

        self._on_enable_menu = omni.kit.widget.context_menu.add_menu(menu_enable, "attribute", "omni.kit.property.usd")

    def _unregister_context_menu(self):
        self._separator_menu = None
        self._on_disable_menu = None
        self._on_delete_menu = None
        self._on_enable_menu = None
