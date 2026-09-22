# pylint: disable=unnecessary-dunder-call
"""Provides commands for manipulating transformation properties of USD prims within the Omniverse Kit."""


import carb
import omni.kit.commands
import omni.usd
from omni.kit.usd_undo import UsdLayerUndo
from pxr import Gf, Sdf, Usd, UsdGeom

from . import xform_op_utils


class EnableXformOpCommand(omni.kit.commands.Command):
    """A command to add an attribute's corresponding XformOp to the xformOpOrder array.

    Args:
        op_attr_path (str): The path of the xformOp attribute to be added to the xformOpOrder.

    Example:
        To add xformOp:translate to the xformOpOrder token array, ensure that the xformOp:translate attribute exists
        and is not already present in the xformOpOrder."""

    def __init__(self, op_attr_path: str):
        """Initializer for the EnableXformOpCommand object."""
        self._op_attr_path = Sdf.Path(op_attr_path)
        self._usd_context = omni.usd.get_context()
        self._prev_xform_ops = None
        self._layer_op_order_map = {}

    def do(self):
        """Executes the command, enabling the specified transformation operation."""
        stage = self._usd_context.get_stage()
        if stage:
            op_attr = stage.GetObjectAtPath(self._op_attr_path)
            if not op_attr:
                return
            precision = xform_op_utils.get_op_precision(op_attr.GetTypeName())
            op_name = op_attr.GetName()
            op_type = xform_op_utils.get_op_type(op_name)
            if op_type is None:
                return
            prim = op_attr.GetPrim()
            if not prim.IsA(UsdGeom.Xformable):
                return
            op_suffix = xform_op_utils.get_op_name_suffix(op_name)
            if op_suffix is None:
                op_suffix = ""
            xform = UsdGeom.Xformable(prim)
            self._prev_xform_ops = xform.GetOrderedXformOps()
            new_target = stage.GetEditTargetForLocalLayer(stage.GetEditTarget().GetLayer())
            with Usd.EditContext(stage, new_target):
                with Sdf.ChangeBlock():
                    added_op = xform.AddXformOp(opType=op_type, precision=precision, opSuffix=op_suffix)

                    # for pivot, we should add its inverse op as well
                    #
                    if xform_op_utils.is_pivot_op(op_name):
                        pivot_op = added_op
                        # Assume that !invert!xformOp:translate:pivot is always a trailing op
                        xform.AddTranslateOp(precision=precision, opSuffix="pivot", isInverseOp=True)

                        # Move the pivot op infront of the transform op as a special case
                        xform_ops = xform.GetOrderedXformOps()
                        new_xform_ops = []
                        found_transform_op = False
                        for op in xform_ops:
                            # wrap the transform op with pivot op
                            if op.GetOpType() == UsdGeom.XformOp.TypeTransform:
                                new_xform_ops.append(pivot_op)
                                new_xform_ops.append(op)
                                found_transform_op = True
                                continue
                            # skip the pivot op if we insert it in front of transform op
                            if (
                                found_transform_op
                                and op.GetOpType() == UsdGeom.XformOp.TypeTranslate
                                and xform_op_utils.is_pivot_op(str(op.GetOpName()))
                                and not xform_op_utils.is_inverse_op(str(op.GetOpName()))
                            ):
                                continue
                            new_xform_ops.append(op)
                        xform.SetXformOpOrder(new_xform_ops, xform.GetResetXformStack())

    def undo(self):
        """Reverts the changes made by the `do` method, effectively undoing the command."""
        stage = self._usd_context.get_stage()
        op_attr = stage.GetObjectAtPath(self._op_attr_path)
        if not op_attr:
            return
        prim = op_attr.GetPrim()
        if not prim.IsA(UsdGeom.Xformable):
            return
        xform = UsdGeom.Xformable(prim)
        with Sdf.ChangeBlock():
            if self._prev_xform_ops:
                new_target = stage.GetEditTargetForLocalLayer(stage.GetEditTarget().GetLayer())
                with Usd.EditContext(stage, new_target):
                    xform.SetXformOpOrder(self._prev_xform_ops)


class ChangeRotationOpCommand(omni.kit.commands.Command):
    """A command to change the rotation XformOp in a USD stage.

    This command updates the xformOpOrder, deletes the source xformOp attribute, creates a destination xformOp attribute, and copies the values from the source to the destination. If the operation is an inverse operation, it will add '!invert!' in the xformOpOrder.

        Args:
            src_op_attr_path (str): Path of the source xformOp attribute.
            op_name (str): Name of the operation.
            dst_op_attr_name (str): Path of the destination xformOp attribute.
            is_inverse_op (bool): Indicates if the operation is an inverse operation.
            auto_target_layer (bool): Automatically target the correct layer for changes.

        Example:
            To change from xformOp:rotateZYX to xformOp:rotateXYZ, this command will:
                1) Update the xformOpOrder.
                2) Delete the xformOp:rotateZYX attribute.
                3) Create the xformOp:rotateXYZ attribute.
                4) Copy the values from xformOp:rotateZYX to xformOp:rotateXYZ."""

    def __init__(
        self,
        src_op_attr_path: str,
        op_name: str,
        dst_op_attr_name: str,
        is_inverse_op: bool,
        auto_target_layer: bool = True,
    ):
        """Initializes the ChangeRotationOpCommand instance."""
        self._src_op_attr_path = Sdf.Path(src_op_attr_path)
        self._op_name = op_name
        self._dst_op_attr_name = dst_op_attr_name
        self._is_inverse_op = is_inverse_op
        self._auto_target_layer = auto_target_layer
        self._usd_context = omni.usd.get_context()
        self._usd_undos = {}

    def _get_undo(self, layer):
        if layer is not None:
            undo = self._usd_undos.get(layer)
            if undo is not None:
                return undo
            self._usd_undos[layer] = UsdLayerUndo(layer)
            return self._usd_undos[layer]
        return None

    def _change_rotation_op(self):
        stage = self._usd_context.get_stage()

        src_op_attr = stage.GetObjectAtPath(self._src_op_attr_path)
        src_op_attr_name = src_op_attr.GetName()
        if src_op_attr_name is None or self._dst_op_attr_name is None or src_op_attr_name == self._dst_op_attr_name:
            return

        prim = src_op_attr.GetPrim()
        if not prim:
            return

        op_order_attr = prim.GetAttribute("xformOpOrder")
        if not op_order_attr:
            return

        with Sdf.ChangeBlock():
            current_authoring_layer = stage.GetEditTarget().GetLayer()

            # change xforpOpOrder
            layer_info, _ = omni.usd.get_attribute_effective_defaultvalue_layer_info(stage, op_order_attr)
            auto_target_session_layer = (
                omni.usd.get_prop_auto_target_session_layer(stage, op_order_attr.GetPath())
                if self._auto_target_layer
                else None
            )
            if (
                layer_info == omni.usd.Value_On_Layer.ON_CURRENT_LAYER
                or layer_info == omni.usd.Value_On_Layer.ON_WEAKER_LAYER
                or (
                    layer_info == omni.usd.Value_On_Layer.ON_STRONGER_LAYER
                    and auto_target_session_layer is not None
                    and self._auto_target_layer is True
                )
            ):
                if self._op_name:
                    order = op_order_attr.Get()
                    old_op_name = self._op_name
                    new_op_name = self._dst_op_attr_name = (
                        self._dst_op_attr_name if not self._is_inverse_op else "!invert!" + self._dst_op_attr_name
                    )
                    for i in range(len(order)):
                        if order.__getitem__(i) == old_op_name:
                            order.__setitem__(i, new_op_name)
                            break
                    if auto_target_session_layer:
                        undo = self._get_undo(auto_target_session_layer)
                        undo.reserve(op_order_attr.GetPath())
                        with Usd.EditContext(stage, auto_target_session_layer):
                            op_order_attr.Set(order)
                    else:
                        undo = self._get_undo(current_authoring_layer)
                        undo.reserve(op_order_attr.GetPath())
                        op_order_attr.Set(order)

                # copy to new attribute
                old_dst_op_attr = prim.GetAttribute(self._dst_op_attr_name)
                # the dst_op_attr may already exist
                if old_dst_op_attr:
                    layer_info, _ = omni.usd.get_attribute_effective_value_layer_info(stage, old_dst_op_attr)
                    auto_target_session_layer = (
                        omni.usd.get_prop_auto_target_session_layer(stage, old_dst_op_attr.GetPath())
                        if self._auto_target_layer
                        else None
                    )

                    value_on_session_ok = (
                        layer_info == omni.usd.Value_On_Layer.ON_STRONGER_LAYER
                        and self._auto_target_layer is True
                        and auto_target_session_layer is not None
                    )
                    value_update_ok = (
                        layer_info == omni.usd.Value_On_Layer.ON_CURRENT_LAYER
                        or layer_info == omni.usd.Value_On_Layer.ON_WEAKER_LAYER
                        or value_on_session_ok
                    )

                    if value_update_ok:
                        if auto_target_session_layer is not None:
                            undo = self._get_undo(auto_target_session_layer)
                            undo.reserve(old_dst_op_attr.GetPath())
                            with Usd.EditContext(stage, auto_target_session_layer):
                                src_op_attr.FlattenTo(prim, self._dst_op_attr_name)
                        else:
                            undo = self._get_undo(current_authoring_layer)
                            undo.reserve(old_dst_op_attr.GetPath())
                            src_op_attr.FlattenTo(prim, self._dst_op_attr_name)

                        source_auto_target_sessiolayer = (
                            omni.usd.get_prop_auto_target_session_layer(stage, self._src_op_attr_path)
                            if self._auto_target_layer
                            else None
                        )
                        if source_auto_target_sessiolayer is not None:
                            undo = self._get_undo(source_auto_target_sessiolayer)
                            undo.reserve(self._src_op_attr_path)
                            with Usd.EditContext(stage, source_auto_target_sessiolayer):
                                prim.RemoveProperty(src_op_attr_name)
                        else:
                            undo = self._get_undo(current_authoring_layer)
                            undo.reserve(self._src_op_attr_path)
                            prim.RemoveProperty(src_op_attr_name)
                    else:
                        carb.log_warn(
                            f"{self._dst_op_attr_name} has value authoring in stronger layer, cannot overwrite it! "
                        )
                else:
                    dst_op_attr_path = prim.GetPath().AppendProperty(self._dst_op_attr_name)
                    auto_target_session_layer = (
                        omni.usd.get_prop_auto_target_session_layer(stage, old_dst_op_attr.GetPath())
                        if self._auto_target_layer
                        else None
                    )
                    if auto_target_session_layer is not None:
                        undo = self._get_undo(auto_target_session_layer)
                        undo.reserve(dst_op_attr_path)
                        with Usd.EditContext(stage, auto_target_session_layer):
                            src_op_attr.FlattenTo(prim, self._dst_op_attr_name)
                    else:
                        undo = self._get_undo(current_authoring_layer)
                        undo.reserve(dst_op_attr_path)
                        src_op_attr.FlattenTo(prim, self._dst_op_attr_name)

                    source_auto_target_sessiolayer = (
                        omni.usd.get_prop_auto_target_session_layer(stage, self._src_op_attr_path)
                        if self._auto_target_layer
                        else None
                    )
                    if source_auto_target_sessiolayer is not None:
                        undo = self._get_undo(source_auto_target_sessiolayer)
                        undo.reserve(self._src_op_attr_path)
                        with Usd.EditContext(stage, source_auto_target_sessiolayer):
                            prim.RemoveProperty(src_op_attr_name)
                    else:
                        undo = self._get_undo(current_authoring_layer)
                        undo.reserve(self._src_op_attr_path)
                        prim.RemoveProperty(src_op_attr_name)

            else:
                carb.log_warn(
                    "xformOpOrder has value authoring a stronger persistent layer, cannot authoring rotate order! "
                )

    def do(self):
        """Executes the rotation operation change."""
        stage = self._usd_context.get_stage()
        if not stage:
            return

        self._change_rotation_op()

    def undo(self):
        """Reverts the rotation operation change."""
        for undo in self._usd_undos.values():
            undo.undo()


class RemoveXformOpCommand(omni.kit.commands.Command):
    """A command to remove an XformOp from the xformOpOrder attribute without deleting the attribute itself.

    Args:
        op_order_attr_path (str): The path of the xformOpOrder attribute.
        op_name (str): The name of the xformOp to be removed.
        op_order_index (int): The index of the xformOp in the xformOpOrder array.

    Example:
        If one needs to remove xformOp:translate from the xformOpOrder token array,
        this command would be used while keeping the xformOp:translate attribute intact."""

    def __init__(self, op_order_attr_path: str, op_name: str, op_order_index: int):
        """Initializes the RemoveXformOpCommand.

        Detailed documentation is optional."""
        self._op_order_attr_path = Sdf.Path(op_order_attr_path)
        self._op_order_index = op_order_index
        self._op_name = op_name
        self._usd_context = omni.usd.get_context()
        self._usd_undo = None

    def do(self):
        """Executes the command to remove a specific XformOp."""
        stage = self._usd_context.get_stage()
        if not stage:
            return
        usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())
        usd_undo.reserve(self._op_order_attr_path)

        order_attr = stage.GetObjectAtPath(self._op_order_attr_path)
        if order_attr:
            with Sdf.ChangeBlock():
                op_order = order_attr.Get()
                if self._op_order_index < len(op_order):
                    op_name = op_order.__getitem__(self._op_order_index)

                    # when remove pivot op also need to remove invert pivot op
                    is_pivot_op = xform_op_utils.is_pivot_op(op_name)
                    inv_op_name = xform_op_utils.get_inverse_op_Name(op_name, True) if is_pivot_op else None

                    if op_name == self._op_name:
                        new_order = []
                        for i in range(len(op_order)):
                            if i != self._op_order_index:
                                if is_pivot_op and inv_op_name == op_order.__getitem__(i):
                                    continue
                                new_order.append(op_order.__getitem__(i))
                        # new_token_order = Vt.TokenArray(new_order)
                        order_attr.Set(new_order)
        self._usd_undo = usd_undo

    def undo(self):
        """Reverts the removal of a specific XformOp."""
        if self._usd_undo is None:
            return
        self._usd_undo.undo()


class RemoveXformOpAndAttrbuteCommand(omni.kit.commands.Command):
    """A command to remove an XformOp and its attribute from the xformOpOrder array.

    Args:
        op_order_attr_path (str): Path of the xformOpOrder attribute.
        op_name (str): Name of the xformOp to be removed.
        op_order_index (int): Index of the xformOp in the xformOpOrder array.

    Example:
        To remove xformOp:translate from the xformOpOrder token array while keeping the xformOp:translate attribute itself.
    """

    def __init__(self, op_order_attr_path: str, op_name: str, op_order_index: int):
        """Constructor for the command that removes an XformOp and its attribute."""
        self._op_order_attr_path = Sdf.Path(op_order_attr_path)  # the xformOpOrder attribute path
        self._op_name = op_name  # xformOpName
        self._op_order_index = op_order_index
        self._usd_context = omni.usd.get_context()
        self._usd_undo = None

    def do(self):
        """Executes the command to remove the specified xformOp and its attribute."""
        stage = omni.usd.get_context().get_stage()
        if stage:
            usd_undo = UsdLayerUndo(stage.GetEditTarget().GetLayer())
            self._usd_undo = usd_undo
            order_attr = stage.GetObjectAtPath(self._op_order_attr_path)
            if order_attr:
                with Sdf.ChangeBlock():
                    op_order = order_attr.Get()
                    if self._op_order_index < len(op_order):
                        op_name = op_order.__getitem__(self._op_order_index)
                        if op_name == self._op_name:
                            # if it is an pivot op to remove, we'd also remove it's companion inverse pivot op
                            is_pivot_op = xform_op_utils.is_pivot_op(op_name)
                            inverse_pivot_op_name = (
                                xform_op_utils.get_inverse_op_Name(op_name, True) if is_pivot_op else None
                            )

                            attr_name = xform_op_utils.get_op_attr_name(op_name)
                            can_delete_attr = True
                            new_order = []
                            for i in range(len(op_order)):
                                # exclude the op
                                if i != self._op_order_index:
                                    # if it is a pivot also exclude the inverse op
                                    if is_pivot_op and op_order.__getitem__(i) == inverse_pivot_op_name:
                                        continue
                                    other_op_name = op_order.__getitem__(i)
                                    new_order.append(other_op_name)
                                    if attr_name == xform_op_utils.get_op_attr_name(other_op_name):
                                        can_delete_attr = False
                            # new_token_order = Vt.TokenArray(new_order)
                            usd_undo.reserve(self._op_order_attr_path)
                            order_attr.Set(new_order)
                            if can_delete_attr:
                                prim = order_attr.GetPrim()
                                if prim:
                                    usd_undo.reserve(prim.GetPath().AppendProperty(attr_name))
                                    prim.RemoveProperty(attr_name)

    def undo(self):
        """Undoes the removal of the specified xformOp and its attribute."""
        if self._usd_undo is None:
            return
        self._usd_undo.undo()


class AddXformOpCommand(omni.kit.commands.Command):
    """A class that encapsulates a command to add various transformation operations (xformOps) to a USD prim's xformOpOrder.

    This command allows for adding translation, rotation, scaling, orientation, transformation matrix, and pivot operations. The precision for these operations can be specified. It also handles the proper ordering of these operations within the xformOpOrder attribute of the prim.

        Args:
            payload: The payload containing information about the stage and prims to modify.
            precision (UsdGeom.XformOp.Precision): The precision of the xformOps to be added.
            rotation_order (str): The order of rotation components (e.g., 'XYZ').
            add_translate_op (bool): Whether to add a translate operation.
            add_orient_op (bool): Whether to add an orientation operation.
            add_scale_op (bool): Whether to add a scale operation.
            add_transform_op (bool): Whether to add a transform operation (4x4 matrix).
            add_pivot_op (bool): Whether to add a pivot operation.
            add_rotateXYZ_op (bool, optional): Whether to add a rotate operation in XYZ order. Deprecated in favor of add_rotate_xyz_op.
            add_rotate_xyz_op (bool, optional): Whether to add a rotate operation in specified order."""

    def __init__(
        self,
        payload,
        precision,
        rotation_order,
        add_translate_op,
        add_orient_op,
        add_scale_op,
        add_transform_op,
        add_pivot_op,
        add_rotateXYZ_op=None,  # noqa N803
        add_rotate_xyz_op=None,
    ):
        """Initializes the command to add a transformation operation."""
        self._payload = payload
        self._precision = precision
        self._rotation_op_name = "xformOp:rotate" + rotation_order
        self._add_translate_op = add_translate_op

        if add_rotate_xyz_op is None and add_rotateXYZ_op is None:
            raise TypeError(
                "TypeError: AddXformOpCommand.__init__() missing 1 required positional argument: 'add_rotate_xyz_op'"
            )
        if add_rotate_xyz_op is not None:
            self._add_rotate_op = add_rotate_xyz_op
        elif add_rotateXYZ_op is not None:
            self._add_rotate_op = add_rotateXYZ_op
            omni.kit.app.log_deprecation(
                "AddXformOpCommand: add_rotateXYZ_op is deprecated, use add_rotate_xyz_op instead"
            )

        self._add_orient_op = add_orient_op
        self._add_scale_op = add_scale_op
        self._add_transform_op = add_transform_op
        self._add_pivot_op = add_pivot_op
        self._usd_undo = None
        self._prv_xform_op_order = {}
        self._translate_attr_added = {}
        self._rotate_attr_added = {}
        self._orient_attr_added = {}
        self._scale_attr_added = {}
        self._transform_attr_added = {}
        self._pivot_attr_added = {}

    def do(self):
        """Executes the command to add the specified transformation operation."""

        stage = self._payload.get_stage()
        if not stage:
            return

        for path in self._payload:
            if path:
                selected_prim = stage.GetPrimAtPath(path)
                selected_xformable = UsdGeom.Xformable(selected_prim)

                path_string = path.pathString

                translate_attr_exist = bool(selected_prim.GetAttribute("xformOp:translate").IsValid())
                rotate_attr_exist = bool(selected_prim.GetAttribute(self._rotation_op_name).IsValid())
                scale_attr_exist = bool(selected_prim.GetAttribute("xformOp:scale").IsValid())
                orient_attr_exist = bool(selected_prim.GetAttribute("xformOp:orient").IsValid())
                transform_attr_exist = bool(selected_prim.GetAttribute("xformOp:transform").IsValid())
                pivot_attr_exist = bool(selected_prim.GetAttribute("xformOp:translate:pivot").IsValid())

                xform_op_order_attr = selected_xformable.GetXformOpOrderAttr()

                translate_op_exist = rotate_op_exist = scale_op_exist = orient_op_exist = transform_op_exist = (
                    pivot_op_exist
                ) = False
                self._translate_attr_added[path_string] = self._rotate_attr_added[path_string] = False
                self._orient_attr_added[path_string] = self._scale_attr_added[path_string] = self._transform_attr_added[
                    path_string
                ] = False
                self._pivot_attr_added[path_string] = False

                with Sdf.ChangeBlock():
                    # In a rare case, there is no xformOpOrder attribute
                    if not xform_op_order_attr:
                        xform_op_order_attr = selected_xformable.CreateXformOpOrderAttr()
                    xform_op_order = xform_op_order_attr.Get()
                    ordered_xform_op = selected_xformable.GetOrderedXformOps()
                    for op in ordered_xform_op:
                        if op.GetOpName() == "xformOp:translate":
                            translate_op_exist = True
                        elif op.GetOpName() == self._rotation_op_name:
                            rotate_op_exist = True
                        elif op.GetOpName() == "xformOp:scale":
                            scale_op_exist = True
                        elif op.GetOpName() == "xformOp:orient":
                            orient_op_exist = True
                        elif op.GetOpName() == "xformOp:transform":
                            transform_op_exist = True
                        elif op.GetOpType() == UsdGeom.XformOp.TypeTranslate and "pivot" in op.SplitName():
                            pivot_op_exist = True
                    self._prv_xform_op_order[path_string] = xform_op_order

                    # Translate Op
                    if self._add_translate_op is True:
                        if translate_attr_exist and translate_op_exist:
                            carb.log_warn(f"The translate Op in prim {path} already exist!")
                        # There is already translate attribute exist
                        elif translate_op_exist is False:
                            selected_xformable.AddTranslateOp(precision=self._precision)
                            if translate_attr_exist is False:
                                if self._precision == UsdGeom.XformOp.PrecisionDouble:
                                    selected_prim.CreateAttribute(
                                        "xformOp:translate", Sdf.ValueTypeNames.Double3, False
                                    ).Set(Gf.Vec3d(0, 0, 0))
                                elif self._precision == UsdGeom.XformOp.PrecisionFloat:
                                    selected_prim.CreateAttribute(
                                        "xformOp:translate", Sdf.ValueTypeNames.Float3, False
                                    ).Set(Gf.Vec3f(0, 0, 0))
                                elif self._precision == UsdGeom.XformOp.PrecisionHalf:
                                    selected_prim.CreateAttribute(
                                        "xformOp:translate", Sdf.ValueTypeNames.Half3, False
                                    ).Set(Gf.Vec3h(0, 0, 0))
                                else:
                                    carb.log_error("Illegal translate value precision setting!")
                                    return
                                self._translate_attr_added[path_string] = True
                        else:
                            carb.log_error(
                                f"Illegal prim {path}: xformOp:translate in xformOpOrder but no corresponding attribute!"
                            )
                            return

                    # Rotate Op
                    if self._add_rotate_op is True:
                        if rotate_attr_exist and rotate_op_exist:
                            carb.log_warn(f"The rotate Op in prim {path} already exist!")
                        # There is already translate attribute exist
                        elif rotate_op_exist is False:
                            rotation_op_type = xform_op_utils.get_op_type(self._rotation_op_name)
                            if rotation_op_type:
                                selected_xformable.AddXformOp(rotation_op_type, precision=self._precision)
                            if rotate_attr_exist is False:
                                if self._precision == UsdGeom.XformOp.PrecisionDouble:
                                    selected_prim.CreateAttribute(
                                        self._rotation_op_name, Sdf.ValueTypeNames.Double3, False
                                    ).Set(Gf.Vec3d(0, 0, 0))
                                elif self._precision == UsdGeom.XformOp.PrecisionFloat:
                                    selected_prim.CreateAttribute(
                                        self._rotation_op_name, Sdf.ValueTypeNames.Float3, False
                                    ).Set(Gf.Vec3f(0, 0, 0))
                                elif self._precision == UsdGeom.XformOp.PrecisionHalf:
                                    selected_prim.CreateAttribute(
                                        self._rotation_op_name, Sdf.ValueTypeNames.Half3, False
                                    ).Set(Gf.Vec3h(0, 0, 0))
                                else:
                                    carb.log_error("Illegal rotate value precision setting!")
                                    return
                                self._rotate_attr_added[path_string] = True
                        else:
                            carb.log_error(
                                f"Illegal prim {path}: xformOp:rotate in xformOpOrder but no corresponding attribute!"
                            )
                            return

                    # Orient Op
                    if self._add_orient_op is True:
                        if orient_attr_exist and orient_op_exist:
                            carb.log_warn(f"The orient Op in prim {path} already exist!")
                        # There is already translate attribute exist
                        elif orient_op_exist is False:
                            selected_xformable.AddOrientOp(precision=self._precision)
                            if orient_attr_exist is False:
                                if self._precision == UsdGeom.XformOp.PrecisionDouble:
                                    selected_prim.CreateAttribute(
                                        "xformOp:orient", Sdf.ValueTypeNames.Quatd, False
                                    ).Set(Gf.Quatd(1.0))
                                elif self._precision == UsdGeom.XformOp.PrecisionFloat:
                                    selected_prim.CreateAttribute(
                                        "xformOp:orient", Sdf.ValueTypeNames.Quatf, False
                                    ).Set(Gf.Quatf(1.0))
                                elif self._precision == UsdGeom.XformOp.PrecisionHalf:
                                    selected_prim.CreateAttribute(
                                        "xformOp:orient", Sdf.ValueTypeNames.Quath, False
                                    ).Set(Gf.Quath(1.0))
                                else:
                                    carb.log_error("Illegal orient value precision setting!")
                                    return
                                self._orient_attr_added[path_string] = True
                        else:
                            carb.log_error(
                                f"Illegal prim {path}: xformOp:orient in xformOpOrder but no corresponding attribute!"
                            )
                            return

                    # Scale Op
                    if self._add_scale_op is True:
                        if scale_attr_exist and scale_op_exist:
                            carb.log_warn(f"The scale Op in prim {path} already exist!")
                        # There is already translate attribute exist
                        elif scale_op_exist is False:
                            selected_xformable.AddScaleOp(precision=self._precision)
                            if scale_attr_exist is False:
                                if self._precision == UsdGeom.XformOp.PrecisionDouble:
                                    selected_prim.CreateAttribute(
                                        "xformOp:scale", Sdf.ValueTypeNames.Double3, False
                                    ).Set(Gf.Vec3d(1.0, 1.0, 1.0))
                                elif self._precision == UsdGeom.XformOp.PrecisionFloat:
                                    selected_prim.CreateAttribute(
                                        "xformOp:scale", Sdf.ValueTypeNames.Float3, False
                                    ).Set(Gf.Vec3f(1.0, 1.0, 1.0))
                                elif self._precision == UsdGeom.XformOp.PrecisionHalf:
                                    selected_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Half3, False).Set(
                                        Gf.Vec3h(1.0, 1.0, 1.0)
                                    )
                                else:
                                    carb.log_error("Illegal scale value precision setting!")
                                    return
                                self._scale_attr_added[path_string] = True
                        else:
                            carb.log_error(
                                f"Illegal prim {path}: xformOp:scale in xformOpOrder but no corresponding attribute!"
                            )
                            return

                    # Transform Op
                    if self._add_transform_op is True:
                        if transform_attr_exist and transform_op_exist:
                            carb.log_warn(f"The transform Op in prim {path} already exist!")
                        # There is already transform attribute exist
                        elif transform_op_exist is False:
                            selected_xformable.AddTransformOp(precision=self._precision)
                            if transform_attr_exist is False:
                                # there is only Matrix4d type
                                selected_prim.CreateAttribute(
                                    "xformOp:transform", Sdf.ValueTypeNames.Matrix4d, False
                                ).Set(Gf.Matrix4d(1.0))
                                self._transform_attr_added[path_string] = True
                        else:
                            carb.log_error(
                                f"Illegal prim {path}: xformOp:transform in xformOpOrder but no corresponding attribute!"
                            )
                            return

                    # Pivot Op
                    if self._add_pivot_op is True:
                        if pivot_attr_exist and pivot_op_exist:
                            carb.log_warn(f"The pivot Op in the prim {path} already exist!")
                        elif pivot_op_exist is False:
                            # Parse the xformOpOrder to find out the rotateion-related & scale-related op's index
                            # there might be multiple rotation & scale op to consider
                            xform_op_size = len(ordered_xform_op)
                            rotate_or_transform_start_index = rotate_or_transform_end_index = scale_start_index = (
                                scale_end_index
                            ) = xform_op_size
                            for index in range(xform_op_size):
                                op = ordered_xform_op[index]
                                op_type = op.GetOpType()
                                # Suffixed op doesn't count
                                if op_type > UsdGeom.XformOp.TypeInvalid and len(op.GetOpName().split(":")) > 2:
                                    continue
                                if (
                                    op_type >= UsdGeom.XformOp.TypeRotateX  # pylint: disable=chained-comparison
                                    and op_type <= UsdGeom.XformOp.TypeTransform  # pylint: disable=chained-comparison
                                ):
                                    rotate_or_transform_end_index = index
                                    if rotate_or_transform_start_index == xform_op_size:
                                        rotate_or_transform_start_index = index
                                elif op_type == UsdGeom.XformOp.TypeScale:
                                    scale_end_index = index
                                    if scale_start_index == xform_op_size:
                                        scale_start_index = index

                            if rotate_or_transform_start_index == xform_op_size and scale_start_index == xform_op_size:
                                carb.log_warn(
                                    "There is no rotate, orient, transform or scale Op for this prim. No rotation Pivot is added."
                                )
                                return
                            # Add the pivot op and invert pivot op and then reorder it
                            pivot_op = selected_xformable.AddTranslateOp(precision=self._precision, opSuffix="pivot")
                            inv_pivot_op = selected_xformable.AddTranslateOp(
                                precision=self._precision, opSuffix="pivot", isInverseOp=True
                            )

                            # pivot and inv pivot to wrap the rotate & scale op. pivot heading inv pivot trailing
                            pivot_index = min(rotate_or_transform_start_index, scale_start_index)
                            inv_pivot_index = max(rotate_or_transform_end_index, scale_end_index)
                            inv_pivot_index = inv_pivot_index + 1  # insert after

                            # if the inverse pivot op is at the tail, just append it
                            if inv_pivot_index >= len(ordered_xform_op):
                                ordered_xform_op.append(inv_pivot_op)
                            else:
                                ordered_xform_op.insert(inv_pivot_index, inv_pivot_op)

                            # It is important to insert pivot_op after inv_pivot_op
                            ordered_xform_op.insert(pivot_index, pivot_op)

                            selected_xformable.SetXformOpOrder(
                                ordered_xform_op, selected_xformable.GetResetXformStack()
                            )
                            # Create xformOp:translate:pivot attribute
                            if pivot_attr_exist is False:
                                if self._precision == UsdGeom.XformOp.PrecisionDouble:
                                    selected_prim.CreateAttribute(
                                        "xformOp:translate:pivot", Sdf.ValueTypeNames.Double3, False
                                    ).Set(Gf.Vec3d(0.0, 0.0, 0.0))
                                elif self._precision == UsdGeom.XformOp.PrecisionFloat:
                                    selected_prim.CreateAttribute(
                                        "xformOp:translate:pivot", Sdf.ValueTypeNames.Float3, False
                                    ).Set(Gf.Vec3f(0.0, 0.0, 0.0))
                                elif self._precision == UsdGeom.XformOp.PrecisionHalf:
                                    selected_prim.CreateAttribute(
                                        "xformOp:translate:pivot", Sdf.ValueTypeNames.Half3, False
                                    ).Set(Gf.Vec3h(0.0, 0.0, 0.0))
                                else:
                                    carb.log_error("Illegal scale value precision setting!")
                                    return
                                self._pivot_attr_added[path_string] = True

    def undo(self):
        """Reverts the addition of the transformation operation."""
        stage = self._payload.get_stage()
        if not stage:
            return
        for path in self._payload:
            if path:
                selected_prim = stage.GetPrimAtPath(path)
                selected_xformable = UsdGeom.Xformable(selected_prim)
                path_string = path.pathString
                with Sdf.ChangeBlock():
                    xform_op_order_attr = selected_xformable.GetXformOpOrderAttr()
                    if xform_op_order_attr:
                        if self._prv_xform_op_order[path_string]:
                            xform_op_order_attr.Set(self._prv_xform_op_order[path_string])
                        else:
                            selected_prim.RemoveProperty(xform_op_order_attr.GetName())

                    if self._translate_attr_added[path_string]:
                        selected_prim.RemoveProperty("xformOp:translate")
                        self._translate_attr_added[path_string] = False
                    if self._rotate_attr_added[path_string]:
                        selected_prim.RemoveProperty(self._rotation_op_name)
                        self._rotate_attr_added[path_string] = False
                    if self._orient_attr_added[path_string]:
                        selected_prim.RemoveProperty("xformOp:orient")
                        self._orient_attr_added[path_string] = False
                    if self._scale_attr_added[path_string]:
                        selected_prim.RemoveProperty("xformOp:scale")
                        self._scale_attr_added[path_string] = False
                    if self._transform_attr_added[path_string]:
                        selected_prim.RemoveProperty("xformOp:transform")
                        self._transform_attr_added[path_string] = False
                    if self._pivot_attr_added[path_string]:
                        selected_prim.RemoveProperty("xformOp:translate:pivot")
                        self._pivot_attr_added[path_string] = False


omni.kit.commands.register_all_commands_in_module(__name__)
