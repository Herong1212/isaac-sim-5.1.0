# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.usd

from typing import List, Tuple
from pxr import Sdf, Usd


class TransformHelper:
    """Internal. Helper to handle transform attributes."""

    def __init__(self):
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._transform_names = [
            "xformOp:translate",
            "xformOp:translate:pivot",
            "xformOp:transform",
            "xformOp:rotateXYZ",
            "xformOp:rotateXZY",
            "xformOp:rotateYXZ",
            "xformOp:rotateYZX",
            "xformOp:rotateZYX",
            "xformOp:rotateZXY",
            "xformOp:rotateX",
            "xformOp:rotateY",
            "xformOp:rotateZ",
            "xformOp:orient",
            "xformOp:scale",
        ]

    def is_transform(self, source_path: str) -> bool:
        """If the source name is an attribute path with xformOp.

        Args:
            source_path (str): The attribute name.

        Returns:
            bool: True if the source name is an transform attribute, or False otherwise.
        """

        return source_path in self._transform_names

    def get_transform_attr(self, attrs: List[Usd.Attribute]) -> Tuple[Usd.Attribute, List[Usd.Attribute], Usd.Attribute, Usd.Attribute]:
        """Finds all transform attributes from list.

        Args:
            attrs (List[Usd.Attribute]): A list of attributes.

        Returns:
            Tuple[Usd.Attribute, List[Usd.Attribute], Usd.Attribute, Usd.Attribute]: A tuple that includes
                tranlate, list of rotations, scale, and order attributes. It's None or empty if corresponding attribute is
                not found.
        """

        attr_translate = None
        attr_rotate = None
        attr_scale = None
        attr_order = None

        # get xformOpOrder 1st as this is going to effect what types are used
        for attr in attrs:
            if attr.GetName() in ["xformOpOrder"]:
                attr_order = attr

        if attr_order is not None:
            attr_order_array = attr_order.Get()
            if attr_order_array is None:
                attr_order_array = []

            for attr in attrs:
                name = attr.GetName()
                if len(attr_order_array) > 0 and not name in attr_order_array:
                    continue

                if name == "xformOp:translate" and attr_translate is None:
                    attr_translate = attr

                elif name == "xformOp:transform" and attr_translate is None:
                    attr_translate = attr
                    attr_rotate = [attr]
                    attr_scale = attr

                elif name == "xformOp:rotateX" or name == "xformOp:rotateY" or name == "xformOp:rotateZ":
                    if attr_rotate is None:
                        attr_rotate = [attr]
                    else:
                        attr_rotate.append(attr)

                elif (
                    name.startswith("xformOp:rotate") or name in ["xformOp:orient", "xformOp:transform"]
                ) and attr_rotate is None:
                    attr_rotate = [attr]

                elif name in ["xformOp:scale", "xformOp:transform"] and attr_scale is None:
                    attr_scale = attr

        return attr_translate, attr_rotate, attr_scale, attr_order

    def order_attrs(self, attrs, order):
        for key_name in order[::-1]:
            for attr in attrs:
                if attr == key_name:
                    attrs.insert(0, attrs.pop(attrs.index(attr)))
                    break

        return attrs

    def add_to_attr_order(self, attr_order, path, use_placeholder=False):
        order = attr_order.Get()
        if order is None:
            order = []
        else:
            order = [item for item in order]

        if path in order:
            return attr_order

        order.append(path)
        order = self.order_attrs(order, self._transform_names)

        if use_placeholder:
            if not isinstance(attr_order, omni.kit.usd.PlaceholderAttribute):
                attr_new = omni.kit.usd.PlaceholderAttribute(attr_order.GetName())
                attr_new.SetPath(attr_order.GetPath().pathString)
                attr_new.SetTypeName(attr_order.GetTypeName())
                attr_new.Set(order)
                return attr_new
            attr_order.Set(order)
        else:
            attr_order.Set(order)

        return attr_order

    def is_common_attr(self, source_attr):
        # exclude array types
        if "[]" in str(source_attr.GetTypeName()):
            return

        paths = self._selection.get_selected_prim_paths()
        stage = self._usd_context.get_stage()
        if self.is_transform(source_attr.GetName()):
            # FIXME: multi-object transform editing is broken so ignore
            return False
        #            for path in paths:
        #                prim = stage.GetPrimAtPath(path) if path else None
        #                if prim is None:
        #                    continue
        #                if not prim.IsA(UsdGeom.Xformable):
        #                    return False
        #
        #            return True

        for path in paths:
            prim = stage.GetPrimAtPath(path) if path else None
            if prim is None:
                continue

            is_common = False
            for attr in prim.GetAttributes():
                if source_attr.GetName() == attr.GetName():
                    is_common = True

            if not is_common:
                return False

        return True
