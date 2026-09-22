# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import carb
import numpy as np
import omni.graph.core as og
import omni.timeline
import omni.usd
import usdrt
from omni.replicator.core import functional as F
from omni.replicator.core import utils
from pxr import Gf, Sdf, UsdShade, Vt
from scipy.spatial.transform import Rotation as R


def get_type(name):
    if "matrix" not in name:
        if "4d" in name or "double4" in name:
            return Sdf.ValueTypeNames.Double4
        elif "4f" in name or "float4" in name:
            return Sdf.ValueTypeNames.Float4
        elif "3d" in name or "double3" in name:
            return Sdf.ValueTypeNames.Double3
        elif "3f" in name or "float3" in name:
            return Sdf.ValueTypeNames.Float3
        elif "2d" in name or "double2" in name:
            return Sdf.ValueTypeNames.Double2
        elif "2f" in name or "float2" in name:
            return Sdf.ValueTypeNames.Float2
        elif name == "float":
            return Sdf.ValueTypeNames.Float
        elif name == "double":
            return Sdf.ValueTypeNames.Double
        elif name == "asset":
            return Sdf.ValueTypeNames.Asset
        elif name == "token":
            return Sdf.ValueTypeNames.Token
        elif name == "bool":
            return Sdf.ValueTypeNames.Bool
        elif name == "token[]":
            return Sdf.ValueTypeNames.TokenArray
        elif name == "bool[]":
            return Sdf.ValueTypeNames.BoolArray
    else:
        if name == "matrix4d":
            return Sdf.ValueTypeNames.Matrix4d
        elif name == "matrix4f":
            return Sdf.ValueTypeNames.Matrix4f
        elif name == "matrix3d":
            return Sdf.ValueTypeNames.Matrix3d
        elif name == "matrix3f":
            return Sdf.ValueTypeNames.Matrix3f
        elif name == "matrix2d":
            return Sdf.ValueTypeNames.Matrix2d
        elif name == "matrix2f":
            return Sdf.ValueTypeNames.Matrix2f
    return None


def get_typed_container(name):
    if "matrix" not in name:
        if "4d" in name or "double4" in name:
            return Gf.Vec4d
        elif "4f" in name or "float4" in name:
            return Gf.Vec4f
        elif "3d" in name or "double3" in name:
            return Gf.Vec3d
        elif "3f" in name or "float3" in name:
            return Gf.Vec3f
        elif "2d" in name or "double2" in name:
            return Gf.Vec2d
        elif "2f" in name or "float2" in name:
            return Gf.Vec2f
        elif name == "float" or name == "double":
            return float
        elif name == "asset":
            return Sdf.AssetPath
        elif name == "token":
            return Vt.Token
    else:
        if name == "matrix4d":
            return Gf.Matrix4d
        elif name == "matrix4f":
            return Gf.Matrix4f
        elif name == "matrix3d":
            return Gf.Matrix3d
        elif name == "matrix3f":
            return Gf.Matrix3f
        elif name == "matrix2d":
            return Gf.Matrix2d
        elif name == "matrix2f":
            return Gf.Matrix2f
    return None


ROTATION_ATTRIBUTES = [
    "xformOp:rotateXYZ",
    "xformOp:rotateXZY",
    "xformOp:rotateYXZ",
    "xformOp:rotateYZX",
    "xformOp:rotateZXY",
    "xformOp:rotateZYX",
    "xformOp:orient",
    "xformOp:transform",
]

INSTANCE_ATTRIBUTES = [
    "positions",
    "xformOp:translate",
    "orientations",
    "xformOp:rotateXYZ",
    "xformOp:rotateXZY",
    "xformOp:rotateYXZ",
    "xformOp:rotateYZX",
    "xformOp:rotateZXY",
    "xformOp:rotateZYX",
    "scales",
    "xformOp:scale",
]


def get_pi_attribute_name(attribute_name):
    if "rotate" in attribute_name and attribute_name in INSTANCE_ATTRIBUTES:
        return "orientations"
    elif attribute_name == "xformOp:translate":
        return "positions"
    elif attribute_name == "xformOp:scale":
        return "scales"
    return attribute_name


def write_attribute(db, sample_prims, attribute_name, samples, input_attribute_type):
    prim0 = sample_prims[0]
    # If attribute name is not an xform attribute and prim0 is a material or shader, add inputs: prefix
    is_xform_attribute = "xformOp" in attribute_name or prim0.HasAttribute(attribute_name)
    is_material = prim0.GetTypeName() in ("Material", "Shader")
    prefix = "inputs:" if not is_xform_attribute and is_material and not attribute_name.startswith("inputs:") else ""
    attribute_name = f"{prefix}{attribute_name}"

    if input_attribute_type and not is_xform_attribute:
        # Add attribute if it doesn't exist and type is specified
        for prim in sample_prims:
            if not prim.HasAttribute(attribute_name):
                prim.CreateAttribute(attribute_name, get_type(input_attribute_type), False)

    # Reshape samples
    # Find attribute datatype
    if prim0.HasAttribute(attribute_name) and hasattr(prim0.GetAttribute(attribute_name).GetTypeName, "type"):
        attribute_type = prim0.GetAttribute(attribute_name).GetTypeName().type.pythonClass
        if attribute_type:
            dimension = attribute_type.dimension
        if not isinstance(dimension, tuple):
            dimension = (dimension,)
        # if "matrix" in str(attribute_name):
        #     samples = [attribute_type(s) for s in samples.reshape((-1, *dimension))]
        # else:
        samples = [attribute_type(s.tolist()) for s in samples.reshape((-1, *dimension))]

    if isinstance(samples, np.ndarray):
        samples = samples.tolist()

    if attribute_name in ROTATION_ATTRIBUTES:
        F.modify.rotation(sample_prims, samples)
    elif attribute_name == "xformOp:translate":
        F.modify.position(sample_prims, samples)
    elif attribute_name == "xformOp:scale":
        F.modify.scale(sample_prims, samples)
    else:
        F.modify.attribute(sample_prims, attribute_name, samples)


def write_attribute_legacy(db, stage, sample_prims, attribute_name, samples, input_attribute_type):
    # whether to use point instancer or its prototypes
    use_instance = attribute_name in INSTANCE_ATTRIBUTES

    prim0 = sample_prims[0]
    attribute_type = prim0.GetAttribute(attribute_name).GetTypeName().type.pythonClass

    # going through all of the prims/prototypes of point instancers
    prims_and_protos = list()
    for prim in sample_prims:
        if not use_instance and prim.GetTypeName() == "PointInstancer":
            protos = prim.GetRelationship("prototypes").GetTargets()
            prims_and_protos.extend([stage.GetPrimAtPath(str(path)) for path in protos])
        else:
            prims_and_protos.append(prim)

    num_samples = 0
    pi_attribute_name = get_pi_attribute_name(attribute_name)

    # validate input
    try:
        for prim in prims_and_protos:
            if prim.GetTypeName() == "PointInstancer":
                num_samples += len(prim.GetAttribute("protoIndices").Get())
                name = pi_attribute_name
                attribute_type = str(prims_and_protos[0].GetAttribute(attribute_name).GetTypeName())
            elif UsdShade.Material(prim):
                shader = UsdShade.Shader(omni.usd.get_shader_from_material(prim, True))
                prim = shader.GetPrim()
                if not attribute_name.startswith("inputs:"):
                    attribute_name = f"inputs:{attribute_name}"

                if prim.HasAttribute(attribute_name):
                    attribute_type = str(prim.GetAttribute(attribute_name).GetTypeName())
                name = attribute_name

                num_samples += 1
            else:
                num_samples += 1
                if not prim.HasAttribute(attribute_name) and prim.HasAttribute(f"inputs:{attribute_name}"):
                    # fallback to inputs prefix
                    attribute_name = f"inputs:{attribute_name}"
                name = attribute_name
                attribute_type = str(prims_and_protos[0].GetAttribute(attribute_name).GetTypeName())

            if not prim.HasAttribute(name):
                # TODO handle material inputs
                if input_attribute_type:
                    prim.CreateAttribute(name, get_type(input_attribute_type))
                    attribute_type = str(prim.GetAttribute(attribute_name).GetTypeName())
                    op_order = prim.GetAttribute("xformOpOrder").Get()
                    if not op_order:
                        op_order = []
                    if "xformOp" in name:
                        # Enforce op order: translate > rotate > scale
                        enforced_op_order = {}
                        new_op_order = []
                        for op in [*op_order, name]:
                            new_op_order.append(op)
                            if "translate" in op.lower():
                                enforced_op_order[op] = 0
                            elif "rotate" in op.lower():
                                enforced_op_order[op] = 1
                            elif "scale" in op.lower():
                                enforced_op_order[op] = 2
                            else:
                                # Only keep translate, rotate or scale xform ops
                                new_op_order.pop(-1)

                        new_op_order = sorted(new_op_order, key=lambda x: enforced_op_order[x])
                    else:
                        new_op_order = op_order

                    if len(new_op_order) != 0:
                        prim.GetAttribute("xformOpOrder").Set(new_op_order)
                else:
                    db.log_error(
                        f"Attribute '{name}' could not be found for prim at {prim.GetPath()}. ",
                        "Available attributes: {attribute_names}. To create the attribute, a datatype is required.",
                    )

        if isinstance(samples, (list, tuple)):
            pass
        else:
            samples = samples.reshape(num_samples, -1)

        if not use_instance and len(samples) != num_samples:
            db.log_error(
                "Expected the number of attributes in inputs:values and number of prims to be the same, "
                + f"instead received {len(samples)} attributes and {num_samples} prims"
            )

    except Exception as error:
        db.log_error(f"WritePrimAttribute Error: {error}")
        db.outputs.execOut = og.ExecutionAttributeState.DISABLED
        return False

    typed_container = get_typed_container(attribute_type)

    # Make sure samples are floats if needed
    if (
        typed_container == Gf.Vec4f
        or typed_container == Gf.Vec4d
        or typed_container == Gf.Vec3f
        or typed_container == Gf.Vec3d
        or typed_container == Gf.Vec2d
        or typed_container == Gf.Vec2f
    ):
        samples = samples.astype(float)

    with Sdf.ChangeBlock():
        idx = 0
        for prim in prims_and_protos:
            if prim.GetTypeName() == "PointInstancer":
                attribute = prim.GetAttribute(pi_attribute_name)
                num_attr = len(prim.GetAttribute("protoIndices").Get())
                if "rotate" in attribute_name:
                    # lower case because USD uses intrinsic Euler angles
                    euler_rot = attribute_name[-3:].lower()
                    quat_rot = R.from_euler(euler_rot, np.array(samples[idx : idx + num_attr]), degrees=True).as_quat()
                    sampled_vals = [Gf.Quath(q[-1], *q[:3]) for q in quat_rot]
                else:
                    sampled_vals = [
                        OgnWritePrimAttribute.get_attribute(typed_container, samples[idx])
                        for idx in range(idx, idx + num_attr)
                    ]
                idx += num_attr
            else:
                if UsdShade.Material(prim):
                    shader = UsdShade.Shader(omni.usd.get_shader_from_material(prim, True))
                    if attribute_name[:7] == "inputs:":
                        attribute = shader.GetPrim().GetAttribute(attribute_name)
                    else:
                        attribute = shader.GetPrim().GetAttribute(f"inputs:{attribute_name}")

                else:
                    attribute = prim.GetAttribute(attribute_name)
                    if not attribute:
                        db.log_error(f"No attribute of name {attribute_name} found on prim {prim}")
                        continue

                if isinstance(samples, (list, tuple)):
                    sample_type = type(samples[idx])
                else:
                    sample_type = samples[idx].dtype
                # Handle strings
                if sample_type == np.dtype("<U1"):
                    sampled_vals = typed_container("".join(samples[idx]))
                elif sample_type == np.dtype("bool"):
                    sampled_vals = bool(samples[idx])
                else:
                    sampled_vals = OgnWritePrimAttribute.get_attribute(typed_container, samples[idx])
                idx += 1

                if attribute_name in ROTATION_ATTRIBUTES:
                    # Assume that rotation is always sampled as XYZ rotation
                    rotaton_angles_xyz = sampled_vals

                    rotation = (
                        Gf.Rotation(Gf.Vec3d.XAxis(), rotaton_angles_xyz[0])
                        * Gf.Rotation(Gf.Vec3d.YAxis(), rotaton_angles_xyz[1])
                        * Gf.Rotation(Gf.Vec3d.ZAxis(), rotaton_angles_xyz[2])
                    )
                    rotation_op = utils.select_rotation_op(prim)
                    utils.set_rotation_by_op(prim, rotation_op, rotation)
                    continue

            attribute.Set(sampled_vals)


class OgnWritePrimAttribute:
    @staticmethod
    def compute(db) -> bool:
        input_attribute_type = db.inputs.attributeType
        attribute_name = db.inputs.attribute
        sample_prim_paths = db.inputs.prims
        values = db.inputs.values

        if len(sample_prim_paths) == 0 or attribute_name is None or attribute_name == "" or values is None:
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            return True

        use_fsd = F.utils.get_is_fsd_enabled()

        if use_fsd:
            stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
        else:
            stage = omni.usd.get_context().get_stage()

        prim0 = stage.GetPrimAtPath(str(sample_prim_paths[0]))
        is_xform_attribute = "xformOp" in attribute_name or prim0.HasAttribute(attribute_name)
        if not is_xform_attribute:
            sample_prim_paths = utils.get_non_xform_prims(sample_prim_paths)

        if len(values.array_value()) == 0:
            db.log_error("Attribute 'values' is empty.")
        samples = values.array_value()

        sample_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in sample_prim_paths]

        if use_fsd:
            write_attribute(db, sample_prims, attribute_name, samples, input_attribute_type)
        else:
            write_attribute_legacy(db, stage, sample_prims, attribute_name, samples, input_attribute_type)

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True

    @staticmethod
    def get_attribute(typed_container, sample):
        if typed_container:
            if typed_container == Vt.Token or typed_container == Sdf.AssetPath:
                return typed_container(sample)
            return typed_container(*sample)
        else:
            return tuple(sample)

    @staticmethod
    def initialize(graph_context, node):
        function_callback = OgnWritePrimAttribute.on_value_changed_callback
        node.get_attribute("inputs:attributeType").register_value_changed_callback(function_callback)

        # FIXME: Temp fix for OM-73243
        if node.get_attribute("inputs:attributeType").get():
            input_type = node.get_attribute("inputs:attributeType").get()

            # HACK: omni.graph does not have asset[] type
            if input_type == "asset":
                input_type = "token"

            node.get_attribute("inputs:values").set_resolved_type(og.Controller.attribute_type(f"{input_type}[]"))

        connected_function_callback = OgnWritePrimAttribute.on_connected_callback
        node.register_on_connected_callback(connected_function_callback)

    @staticmethod
    def on_value_changed_callback(attr) -> None:
        node = attr.get_node()
        output_attr = node.get_attribute("inputs:values")

        if output_attr.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
            specified_type = attr.get_array(False, False, 0)

            # HACK: omni.graph does not have asset[] type
            if specified_type == "asset":
                specified_type = "token"

            output_attr.set_resolved_type(og.Controller.attribute_type(f"{specified_type}[]"))

    @staticmethod
    def on_connected_callback(upstream_attr, downstream_attr):
        if downstream_attr.get_name() != "inputs:values":
            return

        if downstream_attr.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
            upstream_resolved_type = upstream_attr.get_resolved_type()
            if upstream_resolved_type.base_type != og.BaseDataType.UNKNOWN:
                downstream_attr.set_resolved_type(upstream_resolved_type)
