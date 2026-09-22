"""This module provides utilities for working with transform operations in USD, including identifying, manipulating, and querying various aspects of transform operations."""

import carb
import omni.kit
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from pxr import Sdf, UsdGeom

XFROM_OP_PREFIX = "xformOp:"
INVERSE_PREFIX = "!invert!"
INVERSE_XFORM_OP_PREFIX = "!invert!xformOp:"
RESET_XFORM_STACK = UsdGeom.XformOpTypes.resetXformStack
XFROM_OP_TYPE_NAME = [
    "translate",
    "scale",
    "rotateX",
    "rotateY",
    "rotateZ",
    "rotateXYZ",
    "rotateXZY",
    "rotateYXZ",
    "rotateYZX",
    "rotateZXY",
    "rotateZYX",
    "orient",
    "transform",
]


def is_inverse_op(op_name: str):
    """Checks if an operation name represents an inverse operation.

    Args:
        op_name (str): The name of the operation to check.

    Returns:
        bool: True if it's an inverse operation, otherwise False."""
    return op_name.startswith(INVERSE_XFORM_OP_PREFIX)


def is_reset_xform_stack_op(op_name: str):
    """Checks if an operation name indicates a reset transform stack operation.

    Args:
        op_name (str): The name of the operation to check.

    Returns:
        bool: True if it resets the transform stack, otherwise False."""
    return op_name == RESET_XFORM_STACK


def get_op_type_name(op_name: str):
    """Extracts the operation type name from an operation name.

    Args:
        op_name (str): The full name of the operation.

    Returns:
        str or None: The operation type name or None if not extractable."""
    test_name = op_name
    if is_inverse_op(op_name):
        test_name = op_name.split(INVERSE_PREFIX, 1)[1]
    if test_name.startswith(XFROM_OP_PREFIX):
        names = test_name.split(":")
        if len(names) >= 2 and names[1] in XFROM_OP_TYPE_NAME:
            return names[1]
    return None


def get_op_type(op_name: str):
    """Retrieves the USDGeom Xform operation type for a given operation name.

    Args:
        op_name (str): The name of the operation.

    Returns:
        UsdGeom.XformOp.Type or None: The operation type or None if not found."""
    lookup = {
        "translate": UsdGeom.XformOp.TypeTranslate,
        "scale": UsdGeom.XformOp.TypeScale,
        "rotateX": UsdGeom.XformOp.TypeRotateX,
        "rotateY": UsdGeom.XformOp.TypeRotateY,
        "rotateZ": UsdGeom.XformOp.TypeRotateZ,
        "rotateXYZ": UsdGeom.XformOp.TypeRotateXYZ,
        "rotateXZY": UsdGeom.XformOp.TypeRotateXZY,
        "rotateYXZ": UsdGeom.XformOp.TypeRotateYXZ,
        "rotateYZX": UsdGeom.XformOp.TypeRotateYZX,
        "rotateZXY": UsdGeom.XformOp.TypeRotateZXY,
        "rotateZYX": UsdGeom.XformOp.TypeRotateZYX,
        "orient": UsdGeom.XformOp.TypeOrient,
        "transform": UsdGeom.XformOp.TypeTransform,
    }

    op_type_name = get_op_type_name(op_name)
    if op_type_name in lookup:
        return lookup[op_type_name]
    return None


def get_op_name_suffix(op_name: str):
    """Extracts the suffix from an operation name if present.

    Args:
        op_name (str): The full name of the operation.

    Returns:
        str or None: The operation name suffix or None if not available."""
    test_name = op_name
    if is_inverse_op(op_name):
        test_name = op_name.split(INVERSE_PREFIX, 1)[1]
    if test_name.startswith(XFROM_OP_PREFIX):
        names = test_name.split(":", 2)
        if len(names) >= 3:
            return names[2]
    return None


def is_pivot_op(op_name: str):
    """Determines if an operation name signifies a pivot operation.

    Args:
        op_name (str): The name of the operation to check.

    Returns:
        bool: True if it's a pivot operation, otherwise False."""
    op_suffix = get_op_name_suffix(op_name)
    if op_suffix is not None and op_suffix == "pivot":
        return True
    return False


def is_valid_op_name(op_name: str):
    """Checks if an operation name is valid based on predefined criteria.

    Args:
        op_name (str): The name of the operation to validate.

    Returns:
        bool: True if the operation name is valid, otherwise False."""
    if is_reset_xform_stack_op(op_name):
        return True
    if get_op_type_name(op_name) is not None:
        return True
    return False


def get_op_attr_name(op_name: str):
    """Gets the operation attribute name if it's a valid operation name.

    Args:
        op_name (str): The name of the operation.

    Returns:
        str or None: The operation attribute name or None if invalid."""
    if not is_valid_op_name(op_name):
        return None
    if is_reset_xform_stack_op(op_name):
        return None
    if is_inverse_op(op_name):
        return op_name.split(INVERSE_PREFIX, 1)[1]
    return op_name


def get_inverse_op_name(ori_op_name, desired_invert):
    """Determines the inverse operation name based on the desired inversion state.

    Args:
        ori_op_name (str): The original operation name to invert.
        desired_invert (bool): Whether an inverse operation is desired.

    Returns:
        str: The inverse operation name or the original name based on the inversion state."""
    if is_reset_xform_stack_op(ori_op_name):
        return ori_op_name
    if desired_invert and not is_inverse_op(ori_op_name):
        return INVERSE_PREFIX + ori_op_name
    if not desired_invert and is_inverse_op(ori_op_name):
        return ori_op_name.split(INVERSE_PREFIX, 1)[1]
    return ori_op_name


def get_op_precision(attr_type_name: Sdf.ValueTypeName):
    """Determines the precision of an operation based on its attribute type name.

    Args:
        attr_type_name (Sdf.ValueTypeName): The attribute type name.

    Returns:
        UsdGeom.XformOp.Precision: The precision of the operation."""
    if attr_type_name in [Sdf.ValueTypeNames.Float3, Sdf.ValueTypeNames.Quatf, Sdf.ValueTypeNames.Float]:
        return UsdGeom.XformOp.PrecisionFloat
    if attr_type_name in [
        Sdf.ValueTypeNames.Double3,
        Sdf.ValueTypeNames.Quatd,
        Sdf.ValueTypeNames.Double,
        Sdf.ValueTypeNames.Matrix4d,
    ]:
        return UsdGeom.XformOp.PrecisionDouble
    if attr_type_name in [Sdf.ValueTypeNames.Half3, Sdf.ValueTypeNames.Quath, Sdf.ValueTypeNames.Half]:
        return UsdGeom.XformOp.PrecisionHalf
    return UsdGeom.XformOp.PrecisionDouble


def _add_trs_op(payload: PrimSelectionPayload):

    settings = carb.settings.get_settings()
    # Retrieve the default precision
    default_xform_op_precision = settings.get("/persistent/app/primCreation/DefaultXformOpPrecision")
    if default_xform_op_precision is None:
        settings.set_default_string("/persistent/app/primCreation/DefaultXformOpPrecision", "Double")
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
    default_rotation_order = settings.get("/persistent/app/primCreation/DefaultRotationOrder")
    if default_rotation_order is None:
        settings.set_default_string("persistent/app/primCreation/DefaultRotationOrder", "XYZ")
        default_rotation_order = "XYZ"

    omni.kit.commands.execute(
        "AddXformOp",
        payload=payload,
        precision=_precision,
        rotation_order=default_rotation_order,
        add_translate_op=True,
        add_rotate_xyz_op=True,
        add_orient_op=False,
        add_scale_op=True,
        add_transform_op=False,
        add_pivot_op=False,
    )


# backward compatibility
get_inverse_op_Name = get_inverse_op_name  # noqa: N816
