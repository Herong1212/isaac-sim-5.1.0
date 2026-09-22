import os
import random
import re

import numpy as np
from pxr import Gf

from ..utility.metadata import enable_semantics
from ..utility.misc import (
    error,
    tentative_retrieve,
    to_array,
)
from ..utility.scene import reset_velocity, set_physics_properties
from ..utility.xform import get_total_xform, get_xform_op, set_xform_ops


def get_op_name(op):
    return list(op.keys())[0]


def get_op_value(op):
    return list(op.values())[0]


class Mutable_DEV:  # noqa
    def __init__(self, name):
        self.name = name

    def initialize_prim(self, metadata, scene):
        if not self.prim:
            error(f"prim does not exist for mutable {self.name}")
        if tentative_retrieve("tracked", metadata, bool, False):
            enable_semantics(self.prim, self.name)
        elif tentative_retrieve("attach_label", metadata, bool, False):
            enable_semantics(self.prim, self.name, semantic_class="attach_label")
        if "physics" in metadata:
            friction = scene.physics_global["friction"]
            linear_damping = scene.physics_global["linear_damping"]
            angular_damping = scene.physics_global["angular_damping"]
            is_concave = tentative_retrieve("concave", metadata, bool, False)
            if metadata["physics"] == "collision":
                set_physics_properties(self.prim, False, friction)
            elif metadata["physics"] == "rigidbody":
                set_physics_properties(self.prim, True, friction, linear_damping, angular_damping, is_concave)
            else:
                error(f'unrecognized physics mode {metadata["physics"]}')
        self.set_up_transform_operators_for_prim(metadata)

    def set_up_transform_operators_for_prim(self, metadata):
        if not self.prim:
            error(f"prim does not exist for mutable {self.name}")
        if "transform_operators" in metadata:
            set_xform_ops(
                self.prim, [(get_op_name(op).replace("_", ":"), None) for op in metadata["transform_operators"]]
            )
        else:
            set_xform_ops(self.prim, [])

    def step(self, metadata):
        if self.prim is not None:
            if "transform_operators" in metadata:
                self.update_prim_transform(metadata)
            if "physics" in metadata and metadata["physics"] == "rigidbody":
                reset_velocity(self.prim)  # otherwise, faster and faster
            self.global_transform = to_array(get_total_xform(self.prim))
            # NOTE: not recorded in output metadata

    def update_prim_transform(self, metadata):  # move to xform/py
        self.set_up_transform_operators_for_prim(metadata)
        transform_operators = metadata["transform_operators"]
        for op in transform_operators:
            value = get_op_value(op)
            if isinstance(value, list):
                if len(value) == 0:
                    error(f"empty list for transform operator {get_op_name(op)}")
                elif isinstance(value[0], list):
                    value = Gf.Matrix4d(value)
                elif len(value) == 4:
                    value = Gf.Quatf(*value)
                else:
                    value = tuple(value)
            get_xform_op(self.prim, get_op_name(op).replace("_", ":")).Set(value)
