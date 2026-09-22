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

from typing import Any, List, Optional, Union

import carb
import omni.physx
import omni.replicator.core as rep
import omni.replicator.core.functional as F
import pxr
import usdrt
from omni.replicator.core import utils
from pxr import Sdf, UsdGeom

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

VALID_COLLIDER_APPROXIMATIONS = [
    "none",  # triangleMesh
    "convexDecomposition",
    "convexHull",
    "boundingSphere",
    "boundingCube",
    "meshSimplification",
    "sdf",
    "sphereFill",
]

INSTANCE_ATTRIBUTES = [
    "velocities",
    "angularVelocities",
    "physics:velocity",
    "physics:angularVelocity",
    "accelerations",
]

DEFAULTS_RIGID_BODY = {
    "maxDepenetrationVelocity": 100000,
    "angularDamping": 0.001,  # dimensionless
    "maxLinearVelocity": 1000,  # m/s NOTE: to be adjusted by scene units
    "maxAngularVelocity": 2500,  # degrees/s
    "enableCCD": True,
    "solverPositionIterationCount": 128,
    "approximation": "convexHull",
}

DEFAULTS_PHYSICS_SCENE = {
    "path": "/PhysicsScene",
    "enableCCD": True,
    "enableGPUDynamics": False,
    "broadphaseType": "MBP",
    "timeStepsPerSecond": 240,
}


def _get_pi_attribute_name(attribute_name: str):
    if attribute_name == "physics:velocity":
        return "velocities"
    if attribute_name == "physics:angularVelocity":
        return "angularVelocities"
    return attribute_name


def _get_typed_container(name: str, use_usdrt: bool):
    module = usdrt if use_usdrt else pxr

    matrix_map = {
        "matrix4d": module.Gf.Matrix4d,
        "matrix4f": module.Gf.Matrix4f,
        "matrix3d": module.Gf.Matrix3d,
        "matrix3f": module.Gf.Matrix3f,
        "matrix2d": module.Gf.Matrix2d,
        "matrix2f": module.Gf.Matrix2f,
    }

    if "matrix" not in name:
        if "4d" in name or "double4" in name:
            return module.Gf.Vec4d
        if "4f" in name or "float4" in name:
            return module.Gf.Vec4f
        if "3d" in name or "double3" in name:
            return module.Gf.Vec3d
        if "3f" in name or "float3" in name:
            return module.Gf.Vec3f
        if "2d" in name or "double2" in name:
            return module.Gf.Vec2d
        if "2f" in name or "float2" in name:
            return module.Gf.Vec2f
        if name in ("float", "double"):
            return float
        if name == "asset":
            return module.Sdf.AssetPath
        if name == "token":
            return module.Vt.Token
    elif name in matrix_map:
        return matrix_map[name]
    return None


def create_physics_scene(path: str = None, **kwargs) -> None:
    """Creates a new prim and applies the ``UsdPhysics.Scene`` schema to it.

    If a physics scene at ``path`` already exists, no new scene is created, but kwarg attibutes will be set as
        specified. Unless specified, default values are as defined in the schema.

    Args:
        path: Path to physics scene prim. If ``None``, the default path ``/PhysicsScene`` is used.
        **kwargs: Allows setting schema attribute belonging to ``UsdPhysics.Scene`` or
            ``PhysxSchema.PhysxSceneAPI``. The ``<schema>:`` prefix may be omitted when specifying the kwarg.

            - broadphaseType
                Broad phase algorithm used in the simulation. Select from ``["GPU", "MBP", "SAP"]``. Defaults
                to "MBP".
            - collisionSystem
                Collision detection system. Select from ``[PCM, SAT]``.
            - enableCCD
                Enables a second broad phase check after integration that makes it possible to prevent objects from
                tunneling through each other.
            - enableGpuDynamics
                Enables the GPU Dynamics pipeline. Required for GPU only features like deformables.
                Defaults to ``False``.
            - invertCollisionGroupFilter
                Boolean attribute indicating whether inverted collision group filtering should be used.
                By default two collisions, that do have a collisionGroup set, collide with each other. Adding
                a collisionGroup into a collisionGroup filtering will mean that the collision between those groups
                will be disabled. This boolean attribute does invert the default behavior. Hence two collisions with
                defined collisionGroups will not collide with each other by default and one does enable the
                collisions between the groups through the "CollisionGroup" filtering.
            - gravityDirection
                Gravity direction vector in simulation world space. Will be
                normalized before use. A zero vector is a request to use the negative
                upAxis. Unitless.
            - gravityMagnitude
                Gravity acceleration magnitude in simulation world space.
                A negative value is a request to use a value equivalent to earth
                gravity regardless of the metersPerUnit scaling used by this scene.
                Units: stage units / second / second.
            - maxPositionIterationCount
                Maximum position iteration count for all actors (rigid bodies, cloth, particles etc).
                Note that this setting will override solver iteration settings of individual actors that have requested more
                iterations.
                Range: [1, 255]
            - maxVelocityIterationCount
                Maximum velocity iteration count for all actors (rigid bodies, cloth, particles etc).
                Note that this setting will override solver iteration settings of individual actors that have requested more
                iterations.
                Range: [0, 255]
            - minPositionIterationCount
                Minimum position iteration count for all actors (rigid bodies, cloth, particles etc).
                Range: [1, 255]
            - minVelocityIterationCount
                Minimum velocity iteration count for all actors (rigid bodies, cloth, particles etc).
                Range: [0, 255]
            - reportKinematicKinematicPairs
                Boolean attribute indicating whether kinematic vs kinematic pairs
                generate contact reports.
            - reportKinematicStaticPairs
                Boolean attribute indicating whether kinematic vs static pairs
                generate contact reports.
            - solverType
                Solver used for the simulation. Select from ``[PGS, TGS]``.
            - timestepsPerSecond
                Simulation scene steps defined as number of steps per second.

    """
    if path and (not isinstance(path, str) or not pxr.Sdf.Path.IsValidPathString(path)):
        raise ValueError(f"Received invalid 'path': '{path}'")

    if path is None:
        path = DEFAULTS_PHYSICS_SCENE["path"]

    stage = omni.usd.get_context().get_stage()
    if not stage.GetPrimAtPath(path).IsValid():
        pxr.UsdPhysics.Scene.Define(stage, path)
    physics_scene_prim = stage.GetPrimAtPath(path)
    physx_scene_api = pxr.PhysxSchema.PhysxSceneAPI.Apply(physics_scene_prim)

    physx_scene_attributes = physx_scene_api.GetSchemaAttributeNames()
    physics_scene_attributes = pxr.UsdPhysics.Scene.GetSchemaAttributeNames()

    for attr, value in kwargs.items():
        if ":" in attr and attr in (physics_scene_attributes + physx_scene_attributes):
            physics_scene_prim.GetAttribute(attr).Set(value)
        elif f"physxScene:{attr}" in physx_scene_attributes:
            physics_scene_prim.GetAttribute(f"physxScene:{attr}").Set(value)
        elif f"physics:{attr}" in physics_scene_attributes:
            physics_scene_prim.GetAttribute(f"physics:{attr}").Set(value)
        else:
            raise ValueError(
                f"Attribute {attr} could not be found in the available schemas. Valid attributes: "
                f"{physics_scene_attributes + physx_scene_attributes}"
            )


def _simulate_physics(time: float, step_dt: float) -> None:
    physx_sim_interface = omni.physx.get_physx_simulation_interface()
    num_steps = int(time / step_dt)
    for _ in range(num_steps):
        physx_sim_interface.simulate(step_dt, 0)
    physx_sim_interface.fetch_results()


def _simulate_physics_scene(time: float, step_dt: float, physics_scene: str) -> None:
    scene_int = pxr.PhysicsSchemaTools.sdfPathToInt(physics_scene)
    physx_sim_interface = omni.physx.get_physx_simulation_interface()
    num_steps = int(time / step_dt)
    for _ in range(num_steps):
        physx_sim_interface.simulate_scene(scene_int, step_dt, 0)
    physx_sim_interface.fetch_results_scene(scene_int)


def simulate(time: float, step_dt: float, physics_scene: Optional[str] = None) -> None:
    """Simulate physics for specified ``time`` without rendering.

    Args:
        time: The length of time in seconds for which to simulate physics
        step_dt: The time in seconds for each physics step.
        physics_scene (optional): The physics scene to simulate. If ``None``, physics
            is simulated globally. Defaults to None.

    Notes:
        - If the ``omni.physics.fabric extension`` is not enabled or if it is set to "USD" simulation mode, disabling
            physics prim sleeping with the ``/physics/disableSleeping`` flag is recommended to avoid prims from
            freezing in place.
    """
    if physics_scene is None:
        _simulate_physics(time=time, step_dt=step_dt)
    else:
        _simulate_physics_scene(time=time, step_dt=step_dt, physics_scene=physics_scene)


def apply_rigid_body(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    physics_scene: Union[str, List[str]] = None,
    overwrite_rigid_body: bool = True,
    with_collider: bool = True,
    approximation: str = None,
    **kwargs,
) -> None:
    """Applies the ``UsdPhysics.RigidBodyAPI`` and ``PhysxSchema.PhysxRigidBodyAPI`` schemas to the specified prims.

    Unless specified, default values are defined in their respective schema.

    Args:
        prims: The prims to apply a rigid body to.
        physics_scene: If provided, the assign the rigid body to physics scene at specified path. If ``None``, the
            rigid body is assigned to the default physics scene. Identical to setting ``simulationOwner`` kwarg. If
            ``simulationOwner`` kwargs specified, ``physics_scene`` attribute is ignored.
        overwrite_rigid_body: If ``True``, apply rigid body to the specified prim and remove any rigid body already
            applied to a descendent prim. If ``False``, rigid body is only be applied to the input prim if no
            descendent is already specified as a rigid body. This is because PhysX does not allow nested rigid body
            hierarchies.
        with_collider: If ``True``, apply a collider to the rigid body.
        approximation: The mesh's collision approximation. If ``None``, defaults to ``convexHull``. Ignored if
            ``with_collider`` is ``False``.
        **kwargs: Allows setting schema attribute belonging to ``PhysxSchema.PhysxRigidBodyAPI`` or
            ``UsdPhysics.RigidBodyAPI``. The ``<schema>:`` prefix may be omitted when specifying the kwarg.

            - rigidBodyEnabled
                Determines if the rigid body is enabled.
            - kinematicEnabled
                Determines whether the body is kinematic or not. A kinematic
                body is a body that is moved through animated poses or through
                user defined poses. The simulation derives velocities for the
                kinematic body based on the external motion. When a continuous motion
                is not desired, this kinematic flag should be set to false.
            - simulationOwner
                Single PhysicsScene that will simulate this body. By
                default this is the first PhysicsScene found in the stage using
                ``UsdStage.Traverse()``.
            - startsAsleep
                Determines if the body is asleep when the simulation starts.
            - velocity
                Linear velocity in the same space as the node's xform.
                Units: stage units / second
            - angularVelocity
                Angular velocity in the same space as the node's xform.
                Units: degrees / second
            - angularDamping
                Angular damping coefficient.
                Range: [0, inf)
                Units: dimensionless
            - cfmScale
                Constraint-force-mixing Scale.
                Range: [0, 1]
                Units: dimensionless
            - contactSlopCoefficient
                Tolerance on the angular influence of a contact that can help improve the behavior of
                rolling approximate collision shapes. Specifically, the angular component of a normal constraint in a
                contact is zeroed if normal.cross(offset) falls below this tolerance. The tolerance is scaled such that
                the behavior improvement persists through a range of angular velocities of a rolling shape.
                Range: [0, inf)
                Units: stage units
            - disableGravity
                Disable gravity for the rigid body
            - enableCCD
                Enable swept integration for the rigid body.
            - enableGyroscopicForces
                Enables computation of gyroscopic forces on the rigid body.
            - enableSpeculativeCcd
                Register a rigid body to dynamically adjust contact offset based on velocity.
                This can be used to achieve a CCD effect.
            - linearDamping
                Linear damping coefficient.
                Range: [0, inf)
                Units: dimensionless
            - lockedPosAxis
                Collection of flags providing a mechanism to lock motion along/around a specific axis
                (1 << 0, 1 << 1, 1 << 2).
            - lockedRotAxis
                Collection of flags providing a mechanism to lock motion along/around a specific axis
                (1 << 0, 1 << 1, 1 << 2).
            - maxAngularVelocity
                Maximum allowable angular velocity for rigid body.
                Range: [0, inf)
                Units: degrees / seconds
            - maxContactImpulse
                Sets a limit on the impulse that may be applied at a contact. The maximum impulse at a
                contact between two dynamic or kinematic bodies will be the minimum of the two limit values. For a
                collision between a static and a dynamic body, the impulse is limited by the value for the dynamic body.
                Range: [0, inf)
                Units: force * seconds = mass * stage units / seconds
            - maxDepenetrationVelocity
                The maximum depenetration velocity permitted to be introduced by the solver.
                Range: [0, inf)
                Units: stage units / seconds
            - maxLinearVelocity
                Maximum allowable linear velocity for the rigid body. (stage_units / seconds)
                Range: [0, inf)
                Units: stage units / seconds
            - retainAccelerations
                Mass-normalized kinetic energy threshold below which a rigid body may go to sleep.
                Range: [0, inf)
                Units: stage units * stage units / seconds / seconds
            - solveContact
                Process the contacts of this rigid body in the dynamics solver.
            - solverPositionIterationCount
                Solver position iteration counts for the body.
                Range [1, 255]
            - solverVelocityIterationCount
                Solver velocity iteration counts for the body.
                Range [0, 255]
            - stabilizationThreshold
                Mass-normalized kinetic energy threshold below which a rigid body may participate in
                stabilization.
                Range: [0, inf)
                Units: stage units * stage units / seconds / seconds

    """

    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]

    stage = prims[0].GetStage()
    scene_meters_per_unit = pxr.UsdGeom.GetStageMetersPerUnit(stage)

    if approximation is None:
        approximation = DEFAULTS_RIGID_BODY["approximation"]

    for prim in prims:
        if physics_scene is not None:
            if not isinstance(physics_scene, list):
                physics_scene = [physics_scene]
            physics_scene = [
                str(ps.GetPath()) if isinstance(ps, (pxr.Usd.Prim, pxr.UsdPhysics.Scene)) else ps
                for ps in physics_scene
            ]

        if kwargs.get("maxDepenetrationVelocity") is None:
            kwargs["maxDepenetrationVelocity"] = DEFAULTS_RIGID_BODY["maxDepenetrationVelocity"] / scene_meters_per_unit

        if kwargs.get("maxLinearVelocity") is None:
            kwargs["maxLinearVelocity"] = DEFAULTS_RIGID_BODY["maxLinearVelocity"] / scene_meters_per_unit

        # Iterate through its children and make sure all its children does not have rigid body api.
        children_prims = prim.GetAllChildren()

        for child_prim in children_prims:
            children_prims.extend(child_prim.GetAllChildren())

            if child_prim.HasAPI(pxr.UsdPhysics.RigidBodyAPI):
                if overwrite_rigid_body:
                    remove_rigid_body(child_prim)
                else:
                    carb.log_warn(
                        f"Prim {prim} has child prim {child_prim} which has rigid body api. Skipping applying rigid body."
                    )
                    return

        physics_rigid_body_api = pxr.UsdPhysics.RigidBodyAPI.Apply(prim)
        physics_rigid_body_attributes = physics_rigid_body_api.GetSchemaAttributeNames()
        physx_rigid_body_api = pxr.PhysxSchema.PhysxRigidBodyAPI.Apply(prim)
        physx_rigid_body_attributes = physx_rigid_body_api.GetSchemaAttributeNames()

        for attr, value in kwargs.items():
            if ":" in attr and attr in (physics_rigid_body_attributes + physx_rigid_body_attributes):
                prim.GetAttribute(attr).Set(value)
            elif f"physics:{attr}" in physics_rigid_body_attributes:
                prim.GetAttribute(f"physics:{attr}").Set(value)
            elif f"physxRigidBody:{attr}" in physx_rigid_body_attributes:
                prim.GetAttribute(f"physxRigidBody:{attr}").Set(value)
            else:
                raise ValueError(
                    f"Attribute {attr} could not be found in the available schemas. Valid attributes: "
                    f"{physics_rigid_body_attributes + physx_rigid_body_attributes}"
                )

        if physics_scene is not None and "simulationOwner" not in kwargs:
            physics_rigid_body_api.GetSimulationOwnerRel().SetTargets(physics_scene)

        if with_collider:
            apply_collider(prims=prim, physics_scene=physics_scene, approximation=approximation)


def apply_collider(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    physics_scene: Union[str, List[str]] = None,
    **kwargs,
):
    r"""Apply the ``UsdPhysics.CollisionAPI``, ``UsdPhysics.MeshCollisionAPI`` and ``PhysxSchema.PhysxCollisionAPI``
    schemas to the specified prim.

    Unless specified, default values are defined in their respective schema. ``PhysxSchema.PhysxCollisionAPI``
    kwargs attributes and descriptions correspond to ``omni.usd.schema.physx-106.2.1``.

    Notes:
        ``approximation`` defaults to ``triangleMesh``. However, ``triangleMesh`` is not compatible with dynamic bodies.

    Args:
        prims: The prim to apply a collider to.
        physics_scene: If provided, the assign the rigid body to physics scene at specified path. If ``None``, the
            rigid body is assigned to the default physics scene.

        **kwargs: Allows setting schema attribute belonging to ``UsdPhysics.CollisionAPI``,
            ``UsdPhysics.MeshCollisionAPI`` or ``PhysxSchema.PhysxCollisionAPI``. The ``<schema>:``
            prefix may be omitted when specifying the kwarg.

            - collisionEnabled
                Determines if the PhysicsCollisionAPI is enabled.
            - simulationOwner
                Single PhysicsScene that will simulate this collider.
                By default this object belongs to the first PhysicsScene.
                Note that if a RigidBodyAPI in the hierarchy above has a different
                simulationOwner then it has a precedence over this relationship.
            - approximation
                Determines the mesh's collision approximation:

                - none
                    The mesh geometry is used directly as a collider without any
                    approximation.
                - convexDecomposition
                    A convex mesh decomposition is performed. This
                    results in a set of convex mesh colliders.
                - convexHull
                    A convex hull of the mesh is generated and used as the
                    collider.
                - boundingSphere
                    A bounding sphere is computed around the mesh and used
                    as a collider.
                - boundingCube
                    An optimally fitting box collider is computed around the
                    mesh.
                - meshSimplification
                    A mesh simplification step is performed, resulting
                    in a simplified triangle mesh collider.

                Allowed Tokens: ["none", "convexDecomposition", "convexHull", "boundingSphere", "boundingCube",
                "meshSimplification"]
            - contactOffset
                Contact offset of a collision shape. Default value -inf means default is picked by the
                simulation based on the shape extent.
                Range: [maximum(0, restOffset), inf)
                Units: stage units
            - minTorsionalPatchRadius
                Defines the minimum radius of the contact patch used to apply torsional friction.
                Range: [0, inf)
                Units: stage units
            - restOffset
                Rest offset of a collision shape. Default value -inf means that the simulation sets a
                suitable value. For rigid bodies, this value is zero.
                Range: [0, contactOffset]
                Units: stage units
            - torsionalPatchRadius
                Defines the radius of the contact patch used to apply torsional friction.
                Range: [0, inf)
                Units: stage units
    """
    # TODO support usdrt prims
    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]

    if isinstance(physics_scene, str):
        physics_scene = [physics_scene]

    for prim in prims:
        physics_collision_api = pxr.UsdPhysics.CollisionAPI.Apply(prim)
        physics_mesh_collision_api = pxr.UsdPhysics.MeshCollisionAPI.Apply(prim)
        physx_collision_api = pxr.PhysxSchema.PhysxCollisionAPI.Apply(prim)
        if kwargs.get("approximation") == "sdf":
            pxr.PhysxSchema.PhysxSDFMeshCollisionAPI.Apply(prim)

        physics_collision_attributes = physics_collision_api.GetSchemaAttributeNames()
        physics_mesh_collision_attributes = physics_mesh_collision_api.GetSchemaAttributeNames()
        physics_attributes = physics_collision_attributes + physics_mesh_collision_attributes
        physx_collision_attributes = physx_collision_api.GetSchemaAttributeNames()

        for attr, value in kwargs.items():
            if value is None:
                continue
            if ":" in attr and attr in (physics_attributes + physx_collision_attributes):
                prim.GetAttribute(attr).Set(value)
            elif f"physics:{attr}" in physics_attributes:
                prim.GetAttribute(f"physics:{attr}").Set(value)
            elif f"physxRigidBody:{attr}" in physx_collision_attributes:
                prim.GetAttribute(f"physxCollision:{attr}").Set(value)
            else:
                raise ValueError(
                    f"Attribute {attr} could not be found in the available schemas. Valid attributes: "
                    f"{physics_attributes + physx_collision_attributes}"
                )

        if physics_scene is not None and "simulationOwner" not in kwargs:
            physics_collision_api.GetSimulationOwnerRel().SetTargets(physics_scene)


def remove_rigid_body(prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]]) -> None:
    """Remove a rigid body schema from the specified prim.

    Removes the ``pxr.PhysxSchema.PhysxRigidBodyAPI`` and ``pxr.UsdPhysics.RigidBodyAPI`` schemas from the specified
    prim, if they are applied.

    Args:
        prims: The prims to remove the rigid body schema from.
    """
    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]

    for prim in prims:
        if prim.HasAPI(pxr.UsdPhysics.RigidBodyAPI):
            prim.RemoveAPI(pxr.UsdPhysics.RigidBodyAPI)

        if prim.HasAPI(pxr.PhysxSchema.PhysxRigidBodyAPI):
            prim.RemoveAPI(pxr.PhysxSchema.PhysxRigidBodyAPI)


def remove_collider(prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]]) -> None:
    """Remove a collider schema from the specified prims.

    Args:
        prims: The prims to remove the collider from.
    """
    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]

    for prim in prims:
        if prim.HasAPI(pxr.UsdPhysics.CollisionAPI):
            prim.RemoveAPI(pxr.UsdPhysics.CollisionAPI)
        if prim.HasAPI(pxr.UsdPhysics.MeshCollisionAPI):
            prim.RemoveAPI(pxr.UsdPhysics.MeshCollisionAPI)
        if prim.HasAPI(pxr.PhysxSchema.PhysxCollisionAPI):
            prim.RemoveAPI(pxr.PhysxSchema.PhysxCollisionAPI)


def modify_attribute(
    prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]],
    attribute_name: str,
    value: Any,
) -> None:
    """Apply physics attribute of specified prim.

    Args:
        prim: The prim whose attribute will be modified.
        attribute_name: Attribute name.
        value: Attribute value to set.
    """
    for prim in prims:
        use_usdrt = isinstance(prim, usdrt.Usd.Prim)
        # check if we need to resolve drive attribute name with respect to joint type
        if attribute_name in ("rep:physics:resolveStiffness", "rep:physics:resolveDamping"):
            if "prismatic" in prim.GetTypeName().lower():
                stiffness_name = "drive:linear:physics:stiffness"
                damping_name = "drive:linear:physics:damping"
            elif "revolute" in prim.GetTypeName().lower():
                stiffness_name = "drive:angular:physics:stiffness"
                damping_name = "drive:angular:physics:damping"
            elif prim.GetTypeName() == "PhysicsJoint":
                raise NotImplementedError(
                    "Stiffness/damping attribute resolution is not implemented for D6 joints due to possible ambiguities."
                    "Use `omni.replicator.core.modify.attribute` and provide the full name of the stiffness/damping "
                    "attribute to randomize."
                )
            if "stiffness" in attribute_name.lower():
                attribute = prim.GetAttribute(stiffness_name)
            else:
                attribute = prim.GetAttribute(damping_name)
            # typed container can be different if we are using attributes on different drives
            attribute_type = str(attribute.GetTypeName())
            typed_container = _get_typed_container(attribute_type, use_usdrt)
        elif attribute_name in MATERIAL_ATTRIBUTES:
            if prim.GetTypeName() == "Material":
                attribute = prim.GetAttribute(attribute_name)
            # if we want to modify material properties on a prim which is not of type `Material`, fetch the
            # material that is bound to it
            else:
                material_path = prim.GetRelationship("material:binding").GetTargets()[0]
                material_prim = prim.GetStage().GetPrimAtPath(str(material_path))
                attribute = material_prim.GetAttribute(attribute_name)
            # typed container can be different
            attribute_type = str(attribute.GetTypeName())
            typed_container = _get_typed_container(attribute_type, use_usdrt)
        elif attribute_name in COLLIDER_ATTRIBUTE:
            attribute = pxr.UsdPhysics.MeshCollisionAPI(prim).GetApproximationAttr()
        else:
            attribute = prim.GetAttribute(attribute_name)

        if prim.GetTypeName() == "PointInstancer":
            pi_attribute_name = _get_pi_attribute_name(attribute_name)
            attribute = prim.GetAttribute(pi_attribute_name)
            num_attr = len(prim.GetAttribute("protoIndices").Get())
            sampled_vals = [pxr.OgnWritePhysics.get_attribute(typed_container, value[i]) for i in range(num_attr)]
        else:
            sampled_vals = pxr.OgnWritePhysics.get_attribute(typed_container, value)
        attribute.Set(sampled_vals)


def reset() -> None:
    """Reset the physics simulation."""
    physx_interface = omni.physx.acquire_physx_interface()
    physx_interface.reset_simulation()


def put_to_sleep(prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]]) -> None:
    """Put the specified prims to sleep."""
    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]

    physx_sim_interface = omni.physx.get_physx_simulation_interface()
    stage_id = omni.usd.get_context().get_stage_id()

    for prim in prims:
        body_path = pxr.PhysicsSchemaTools.sdfPathToInt(prim.GetPath())
        physx_sim_interface.put_to_sleep(stage_id, body_path)


def wake_up(prims: Union[pxr.Usd.Prim, usdrt.Usd.Prim, List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]]]) -> None:
    """Wake up the specified prims."""
    if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        prims = [prims]

    physx_sim_interface = omni.physx.get_physx_simulation_interface()
    stage_id = omni.usd.get_context().get_stage_id()

    for prim in prims:
        body_path = pxr.PhysicsSchemaTools.sdfPathToInt(prim.GetPath())
        physx_sim_interface.wake_up(stage_id, body_path)


def create_camera_collision_prims(
    camera_prim: Union[Sdf.Path, pxr.Usd.Prim, usdrt.Usd.Prim, usdrt.Sdf.Path],
    camera_coll_radius: float = 0.02,
    camera_coll_view_dist: float = 0.4,
) -> None:
    """Create camera collision prims for the specified camera prim.

    Creates two collision primitives - a sphere around the camera position and a cone extending
    in front of the camera view direction. The sphere prevents objects from getting too close to
    the camera while the cone keeps the camera's view path clear of obstacles.

    The sphere radius and cone length can be customized via the camera_coll_radius and
    camera_coll_view_dist parameters respectively. The cone has a fixed angle that provides
    reasonable coverage of the camera's view frustum.

    The collision primitives are created as invisible meshes parented under the camera.

    Args:
        camera_prim: The camera prim to create collision prims for.
        camera_coll_radius: The radius in meters around the camera that must be free of collisions.
        camera_coll_view_dist: The distance in meters in front of the camera that must be free of collisions.
    """
    if not utils.is_camera_prim(camera_prim):
        raise ValueError(f"Camera prim {camera_prim} is not a valid camera prim.")

    stage = omni.usd.get_context().get_stage()

    meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage)

    radius_in_units = camera_coll_radius / meters_per_unit
    view_dist_in_units = camera_coll_view_dist / meters_per_unit

    if isinstance(camera_prim, (Sdf.Path, usdrt.Sdf.Path)):
        camera_prim = stage.GetPrimAtPath(str(camera_prim))

    if camera_prim.GetTypeName() == "Xform":
        for child in camera_prim.GetChildren():
            if child.GetTypeName() == "Camera":
                camera_prim = child
                break

    sphere_scale = (
        radius_in_units / (0.5 / meters_per_unit),
        radius_in_units / (0.5 / meters_per_unit),
        radius_in_units / (0.5 / meters_per_unit),
    )
    F.create.sphere(
        name="cameraSphere",
        parent=camera_prim.GetParent(),
        position=(0, 0, 0),
        rotation=(0, 90, 0),
        scale=sphere_scale,
        visible=False,
    )

    cone_position = (0, 0, -view_dist_in_units / (0.02 / meters_per_unit))
    cone_scale = ((0.003) / meters_per_unit, view_dist_in_units / 100, (0.003) / meters_per_unit)
    F.create.cone(
        name="cameraCone",
        parent=camera_prim.GetParent(),
        position=cone_position,
        rotation=(90, 0, 0),
        scale=cone_scale,
        visible=False,
    )
