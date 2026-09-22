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
import omni.kit
import omni.timeline
import omni.usd
from omni.replicator.core.functional import physics
from pxr import Gf, PhysxSchema, Sdf, UsdGeom, UsdPhysics, UsdShade, Vt

EPS = 1e-8


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


def get_pi_attribute_name(attribute_name):
    if attribute_name == "physics:velocity":
        return "velocities"
    elif attribute_name == "physics:angularVelocity":
        return "angularVelocities"
    return attribute_name


RIGID_BODY_ATTRIBUTES = ["physics:velocity", "physics:angularVelocity"]

# not an actual attribute, indicates that we need to add the collider api
COLLIDER_ATTRIBUTE = ["physics:approximation"]

# Offset attribute
OFFSET_ATTRIBUTE = ["physxCollision:contactOffset", "physxCollision:restOffset"]

MASS_ATTRIBUTES = [
    "physics:mass",
    "physics:density",
    "physics:centerOfMass",
    "physics:diagonalInertia",
    "physics:principalAxes",
]

DRIVE_ATTRIBUTES = [
    "drive:linear:physics:stiffness",
    "drive:linear:physics:damping",
    "drive:angular:physics:stiffness",
    "drive:angular:physics:damping",
    "drive:transX:physics:stiffness",
    "drive:transX:physics:damping",
    "drive:transY:physics:stiffness",
    "drive:transY:physics:damping",
    "drive:transZ:physics:stiffness",
    "drive:transZ:physics:damping",
    "drive:rotX:physics:stiffness",
    "drive:rotX:physics:damping",
    "drive:rotY:physics:stiffness",
    "drive:rotY:physics:damping",
    "drive:rotZ:physics:stiffness",
    "drive:rotZ:physics:damping",
    # these last two attributes are not actual attributes, they indicate that the drive attribute
    # must be resolved on a per-prim basis
    "rep:physics:resolveStiffness",
    "rep:physics:resolveDamping",
]

MATERIAL_ATTRIBUTES = ["physics:staticFriction", "physics:dynamicFriction", "physics:restitution"]


INSTANCE_ATTRIBUTES = [
    "velocities",
    "angularVelocities",
    "physics:velocity",
    "physics:angularVelocity",
    "accelerations",
]


class OgnWritePhysics:
    @staticmethod
    def compute(db) -> bool:
        stage = omni.usd.get_context().get_stage()
        sample_prim_paths = db.inputs.prims
        attribute_name = db.inputs.attribute
        values = db.inputs.values
        overwrite_rigid_body = db.inputs.overwriteRigidBody
        physics_scene_paths = [str(ps) for ps in db.inputs.physicsScene]

        sample_prims = [stage.GetPrimAtPath(str(prim_path)) for prim_path in sample_prim_paths]

        # going through all of the prims/prototypes of point instancers
        prims_and_protos = list()
        for prim in sample_prims:
            if prim.GetTypeName() == "PointInstancer":
                protos = prim.GetRelationship("prototypes").GetTargets()
                prims_and_protos.extend([stage.GetPrimAtPath(str(path)) for path in protos])
            else:
                prims_and_protos.append(prim)

        num_samples = 0
        pi_attribute_name = get_pi_attribute_name(attribute_name)

        if len(sample_prims) == 0 or attribute_name is None or attribute_name == "" or values is None:
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            return True

        # validate input
        try:
            for prim in sample_prims:
                if prim.GetTypeName() == "PointInstancer":
                    num_samples += len(prim.GetAttribute("protoIndices").Get())
                else:
                    num_samples += 1

            if attribute_name not in (
                RIGID_BODY_ATTRIBUTES
                + COLLIDER_ATTRIBUTE
                + MASS_ATTRIBUTES
                + DRIVE_ATTRIBUTES
                + MATERIAL_ATTRIBUTES
                + OFFSET_ATTRIBUTE
            ):
                raise ValueError(f"Expected to get a physics attribute instead received {attribute_name}")
            samples = values.array_value()

            if not isinstance(samples, np.ndarray):
                samples = np.array(samples)

            # FIXME: temp solution for static value
            # Repeat static value

            if samples.size == 1:
                samples = np.repeat(samples, num_samples, axis=0)
            samples = samples.reshape(num_samples, -1)

        except Exception as error:
            db.log_error(f"WritePhysics Error: {error}")
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        # setup global physics scene if one hasn't been set
        if not stage.GetPrimAtPath("/PhysicsScene").IsValid():
            physics.create_physics_scene(
                path="/PhysicsScene",
                enableCCD=True,
                enableGPUDynamics=False,
                broadphaseType="MBP",
                timeStepsPerSecond=240,
            )
        for prim in prims_and_protos:
            if prim.GetTypeName() != "PointInstancer":
                # check if we need to apply a rigid body API
                if not prim.HasAPI(UsdPhysics.RigidBodyAPI) and attribute_name in RIGID_BODY_ATTRIBUTES:
                    physics.apply_rigid_body(prim, physics_scene_paths, overwrite_rigid_body)

                # check if we need to apply mass api
                elif not prim.HasAPI(UsdPhysics.MassAPI) and attribute_name in MASS_ATTRIBUTES:
                    UsdPhysics.MassAPI.Apply(prim)
                # check if we need to apply drive api
                elif not prim.HasAPI(UsdPhysics.DriveAPI) and attribute_name in DRIVE_ATTRIBUTES:
                    if "revolute" in prim.GetTypeName().lower():
                        drive_type = UsdPhysics.Tokens.angular
                    elif "prismatic" in prim.GetTypeName().lower():
                        drive_type = UsdPhysics.Tokens.linear
                    # ambiguity as to what API to apply to D6 joint
                    elif prim.GetTypeName() == "PhysicsJoint":
                        raise ValueError("D6 joint must already have drive API")
                    else:
                        raise ValueError(
                            f"Expected joint to be Revolute, Prismatic, or D6, instead received {prim.GetTypeName()}"
                        )
                    UsdPhysics.DriveAPI.Apply(prim, drive_type)
                # check if we need to add material/physics material api
                elif attribute_name in MATERIAL_ATTRIBUTES:
                    material_prim = prim
                    if material_prim.GetTypeName() != "Material":
                        material_bindings = prim.GetRelationship("material:binding").GetTargets()
                        # check if we need to create a material
                        if len(material_bindings) == 0:
                            binding_api = UsdShade.MaterialBindingAPI.Apply(prim)
                            material_path = f"{str(prim.GetPath())}/PhysicsMaterial"
                            material = UsdShade.Material.Define(stage, material_path)
                            material_prim = stage.GetPrimAtPath(str(material_path))
                            # Passed in strength-list may have None as members, re-resolve default strength in that case
                            material = UsdShade.Material(material_prim)
                            binding_api.Bind(material, UsdShade.Tokens.weakerThanDescendants)
                        else:
                            material_prim = stage.GetPrimAtPath(str(material_bindings[0]))
                    if not material_prim.HasAPI(UsdPhysics.MaterialAPI):
                        UsdPhysics.MaterialAPI.Apply(material_prim)
                # check if we need to apply collision API
                if not prim.HasAPI(UsdPhysics.CollisionAPI) and (
                    attribute_name in RIGID_BODY_ATTRIBUTES
                    or attribute_name in COLLIDER_ATTRIBUTE
                    or attribute_name in OFFSET_ATTRIBUTE
                ):
                    physics.apply_collider(prim, physics_scene_paths)

        attribute_type = str(prims_and_protos[0].GetAttribute(attribute_name).GetTypeName())
        typed_container = get_typed_container(attribute_type)

        with Sdf.ChangeBlock():
            idx = 0
            for prim in sample_prims:
                # check if we need to resolve drive attribute name with respect to joint type
                if attribute_name == "rep:physics:resolveStiffness" or attribute_name == "rep:physics:resolveDamping":
                    if "prismatic" in prim.GetTypeName().lower():
                        stiffness_name = "drive:linear:physics:stiffness"
                        damping_name = "drive:linear:physics:damping"
                    elif "revolute" in prim.GetTypeName().lower():
                        stiffness_name = "drive:angular:physics:stiffness"
                        damping_name = "drive:angular:physics:damping"
                    elif prim.GetTypeName() == "PhysicsJoint":
                        raise NotImplementedError(
                            "Stiffness/damping attribute resolution is not implemented for D6 joints due to possible ambiguities."
                            + "Use `omni.replicator.core.modify.attribute` and provide the full name of the stiffness/damping attribute to randomize."
                        )
                    if "stiffness" in attribute_name.lower():
                        attribute = prim.GetAttribute(stiffness_name)
                    else:
                        attribute = prim.GetAttribute(damping_name)
                    # typed container can be different if we are using attributes on different drives
                    attribute_type = str(attribute.GetTypeName())
                    typed_container = get_typed_container(attribute_type)
                elif attribute_name in MATERIAL_ATTRIBUTES:
                    if prim.GetTypeName() == "Material":
                        attribute = prim.GetAttribute(attribute_name)
                    # if we want to modify material properties on a prim which is not of type `Material`, fetch the
                    # material that is bound to it
                    else:
                        material_path = prim.GetRelationship("material:binding").GetTargets()[0]
                        material_prim = stage.GetPrimAtPath(str(material_path))
                        attribute = material_prim.GetAttribute(attribute_name)
                    # typed container can be different
                    attribute_type = str(attribute.GetTypeName())
                    typed_container = get_typed_container(attribute_type)
                elif attribute_name in COLLIDER_ATTRIBUTE:
                    attribute = UsdPhysics.MeshCollisionAPI(prim).GetApproximationAttr()
                else:
                    attribute = prim.GetAttribute(attribute_name)

                if prim.GetTypeName() == "PointInstancer":
                    attribute = prim.GetAttribute(pi_attribute_name)
                    num_attr = len(prim.GetAttribute("protoIndices").Get())
                    sampled_vals = [
                        OgnWritePhysics.get_attribute(typed_container, samples[idx])
                        for idx in range(idx, idx + num_attr)
                    ]
                    idx += num_attr
                else:
                    sampled_vals = OgnWritePhysics.get_attribute(typed_container, samples[idx])
                    idx += 1
                attribute.Set(sampled_vals)

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True

    @staticmethod
    def get_attribute(typed_container, sample):
        if typed_container:
            return typed_container(*(sample.tolist()))
        else:
            return tuple(sample)

    @staticmethod
    def initialize(graph_context, node):
        connected_function_callback = OgnWritePhysics.on_connected_callback
        node.register_on_connected_callback(connected_function_callback)

    @staticmethod
    def on_connected_callback(upstream_attr, downstream_attr):
        if downstream_attr.get_name() != "inputs:values":
            return

        if downstream_attr.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
            upstream_resolved_type = upstream_attr.get_resolved_type()
            if upstream_resolved_type.base_type != og.BaseDataType.UNKNOWN:
                downstream_attr.set_resolved_type(upstream_resolved_type)
