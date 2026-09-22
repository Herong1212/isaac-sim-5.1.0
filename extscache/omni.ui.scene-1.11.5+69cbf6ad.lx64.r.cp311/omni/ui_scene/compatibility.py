## Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
__all__ = ["add_intersection_attributes"]

from . import scene as sc
import carb


def _deprecate_warning(func, old, new):
    """Returns decorated function that prints a warning when it's executed"""

    def inner(*args, **kwargs):
        carb.log_warn(f"[omni.ui.scene] Method {old} is deprecated. Please use {new} instead.")
        return func(*args, **kwargs)

    return inner


def _add_compatibility(obj, old, new, deprecate_warning=True):
    """Add the attribute old that equals to new"""
    new_obj = getattr(obj, new)
    if deprecate_warning:
        if isinstance(new_obj, property):
            setattr(
                obj,
                old,
                property(
                    fget=_deprecate_warning(new_obj.fget, obj.__name__ + "." + old, obj.__name__ + "." + new),
                    fset=_deprecate_warning(new_obj.fset, obj.__name__ + "." + old, obj.__name__ + "." + new),
                ),
            )
        else:
            setattr(obj, old, _deprecate_warning(new_obj, obj.__name__ + "." + old, obj.__name__ + "." + new))
    else:
        setattr(obj, old, new_obj)


def add_intersection_attributes():
    """Assigns deprecated methods that print warnings when executing"""
    for item in [
        sc.AbstractGesture,
        sc.AbstractShape,
        sc.Arc,
        sc.Line,
        sc.Points,
        sc.PolygonMesh,
        sc.Rectangle,
        sc.Screen,
    ]:
        _add_compatibility(item, "intersection", "gesture_payload")
        _add_compatibility(item, "get_intersection", "get_gesture_payload")

    _add_compatibility(sc.AbstractGesture, "Intersection", "GesturePayload", False)
