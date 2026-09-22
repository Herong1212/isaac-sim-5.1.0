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

# pylint: disable=protected-access

from typing import List, Optional, Tuple, Union

import omni.graph.core as og
import omni.kit
import omni.timeline
import omni.usd

from .distribution import choice
from .utils import ReplicatorItem, ReplicatorWrapper, utils


def _play():
    timeline_iface = omni.timeline.get_timeline_interface()
    timeline_iface.play()


@ReplicatorWrapper
def _write_physics_node(
    input_prims, attribute, values, attribute_type, overwrite_rigid_body=False, physics_scene=None
) -> ReplicatorItem:
    node = utils.create_node("omni.replicator.core.OgnWritePhysics", physicsScene=physics_scene)
    node.get_attribute("inputs:attribute").set(attribute)
    node.get_attribute("inputs:overwriteRigidBody").set(overwrite_rigid_body)
    # TODO: TEMP solution. Need to follow OgnWritePrimAttribute to resolve the type inside the node.
    node.get_attribute("inputs:values").set_resolved_type(og.Controller.attribute_type(f"{attribute_type}"))

    if not isinstance(values, ReplicatorItem):
        values = choice([values])
    utils._setup_random_attribute(write_node=node, attribute_value=values, prim_path=input_prims)

    return node


@ReplicatorWrapper
def rigid_body(
    velocity: Union[ReplicatorItem, Tuple[float, float, float]] = (0.0, 0.0, 0.0),
    angular_velocity: Union[ReplicatorItem, Tuple[float, float, float]] = None,
    contact_offset: float = None,
    rest_offset: float = None,
    overwrite: bool = False,
    physics_scene: str = None,
    input_prims: Union[ReplicatorItem, List] = None,
) -> None:
    """Randomizes the velocity and angular velocity of the prims specified in ``input_prims``. If they do not have
    the ``RigidBodyAPI`` then one will be created for the prim.

    Args:
        velocity: The velocity of the prim.
        angular_velocty: The angular velocity of the prim (degrees / time).

        contact_offset: Offset used when generating contact points. If it is ``None``, it will determined by scene's
            current ``meters_per_unit``. Default: ``None``.
        rest_offset: Offset used when generating rest contact points. If it is ``None``, it will determined by scene's
            current ``meters_per_unit``. Default: ``None``.
        overwrite: If True, apply rigid body to the input prim and remove any rigid body already applied to a descendent
            of the input prim. If False, rigid body is only be applied to the input prim if no descendent is already
            specified as a rigid body. This is because PhysX does not allow nested rigid body hierarchies.
        physics_scene: If provided, the assign the rigid body to physics scene at specified path. If ``None``, the
            rigid body is assigned to the default physics scene.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.create.cube():
        ...     rep.physics.rigid_body(
        ...         velocity=rep.distribution.uniform((0, 0, 0), (100, 100, 100)),
        ...         angular_velocity=rep.distribution.uniform((30, 30, 30), (300, 300, 300))
        ...     )
        omni.replicator.core.physics.rigid_body
    """
    if contact_offset is not None:
        _write_physics_node(
            input_prims,
            "physxCollision:contactOffset",
            contact_offset,
            "float[]",
            overwrite,
            physics_scene=physics_scene,
        )
    if rest_offset is not None:
        _write_physics_node(
            input_prims, "physxCollision:restOffset", rest_offset, "float[]", overwrite, physics_scene=physics_scene
        )

    if velocity is not None:
        _write_physics_node(
            input_prims, "physics:velocity", velocity, "double[]", overwrite, physics_scene=physics_scene
        )
    if angular_velocity is not None:
        _write_physics_node(
            input_prims, "physics:angularVelocity", angular_velocity, "double[]", overwrite, physics_scene=physics_scene
        )


@ReplicatorWrapper
def collider(
    approximation_shape: str = "convexHull",
    contact_offset: float = None,
    rest_offset: float = None,
    physics_scene: str = None,
    input_prims: Union[ReplicatorItem, List] = None,
) -> None:
    """Applies the Physx Collision API to the prims specified in ``input_prims``.

    Args:
        approximation_shape: The approximation used in the collider (by default, convex hull). Other approximations
            include "convexDecomposition", "boundingSphere", "boundingCube", "meshSimplification", and "none". "none"
            will just use default mesh geometry.
        contact_offset: Offset used when generating contact points. If it is ``None``, it will determined by scene's
            current ``meters_per_unit``. Default: ``None``.
        rest_offset: Offset used when generating rest contact points. If it is ``None``, it will determined by scene's
            current ``meters_per_unit``. Default: ``None``.
        physics_scene: If provided, the assign the collider to physics scene at specified path. If ``None``, the
            collider is assigned to the default physics scene.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.create.cube():
        ...     rep.physics.collider()
        omni.replicator.core.physics.collider
    """
    if contact_offset is not None:
        _write_physics_node(
            input_prims, "physxCollision:contactOffset", contact_offset, "float[]", physics_scene=physics_scene
        )
    if rest_offset is not None:
        _write_physics_node(
            input_prims, "physxCollision:restOffset", rest_offset, "float[]", physics_scene=physics_scene
        )

    _write_physics_node(
        input_prims, "physics:approximation", approximation_shape, "token[]", physics_scene=physics_scene
    )


@ReplicatorWrapper
def mass(  # pylint: disable=redefined-outer-name
    mass: Optional[float] = None,
    density: Optional[float] = None,
    center_of_mass: Optional[List] = None,
    diagonal_inertia: Optional[List] = None,
    principal_axes: Optional[List] = None,
    input_prims: Union[ReplicatorItem, List] = None,
) -> None:
    """Applies the Physx Mass API to the prims specified in ``input_prims``, if necessary. This function sets up
    randomization parameters for various mass-related properties in the mass API.

    Args:
        mass: The mass of the prim. By default mass is derived from the volume of the collision geometry
            multiplied by a density.
        density: The density of the prim.
        center_of_mass: Center of the mass of the prim in local coordinates.
        diagonal_inertia: Constructs a diagonalized inertia tensor along the principal axes.
        principal_axes: A quaternion (wxyz) representing the orientation of the principal axes in the local coordinate
            frame.
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.create.cube():
        ...     rep.physics.mass(mass=rep.distribution.uniform(1.0, 50.0))
        omni.replicator.core.physics.mass
    """
    if mass is not None:
        _write_physics_node(input_prims, "physics:mass", mass, "float[]")
    if density is not None:
        _write_physics_node(input_prims, "physics:density", density, "float[]")
    if center_of_mass is not None:
        _write_physics_node(input_prims, "physics:centerOfMass", center_of_mass, "double[]")
    if diagonal_inertia is not None:
        _write_physics_node(input_prims, "physics:diagonalInertia", diagonal_inertia, "double[]")
    if principal_axes is not None:
        _write_physics_node(input_prims, "physics:principalAxes", principal_axes, "double[]")


@ReplicatorWrapper
def drive_properties(
    stiffness: Union[ReplicatorItem, float] = 0.0,
    damping: Union[ReplicatorItem, float] = 0.0,
    input_prims: Union[ReplicatorItem, List] = None,
) -> None:
    """Applies the Drive API to the prims specified in ``input_prims``, if necessary. Prims must be either revolute or
    prismatic joints. For D6 joint randomization, please refer to ``omni.replicator.core.modify.attribute`` and provide
    the exact attribute name of the drive parameter to be randomized.

    Args:
        stiffness: The stiffness of the drive (unitless).
        damping: The damping of the drive (unitless).
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.
    """
    if stiffness is not None:
        _write_physics_node(input_prims, "rep:physics:resolveStiffness", stiffness, "float")
    if damping is not None:
        _write_physics_node(input_prims, "rep:physics:resolveDamping", damping, "float")


@ReplicatorWrapper
def physics_material(
    static_friction: Union[ReplicatorItem, float] = None,
    dynamic_friction: Union[ReplicatorItem, float] = None,
    restitution: Union[ReplicatorItem, float] = None,
    input_prims: Union[ReplicatorItem, List] = None,
) -> None:
    """If input prim is a material, the physics material API will be applied if necessary.
    Otherwise, if the prim has a bound material, then randomizations will be made on this material (where once again,
    with the physics material API being bound if necessary). If the prim does not have a bound material, then a physics
    material will be created at ``<prim_path>/PhysicsMaterial`` and bound at the prim.

    Args:
        static_friction: Static friction coefficient (unitless).
        dynamic_friction: Dynamic friction coefficient (unitless).
        restitution: Restitution coefficient (unitless).
        input_prims: The prims to be modified. If using ``with`` syntax, this argument can be omitted.

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.create.cube():
        ...     rep.physics.physics_material(
        ...         static_friction=rep.distribution.uniform(0.0, 1.0),
        ...         dynamic_friction=rep.distribution.uniform(0.0, 1.0),
        ...         restitution=rep.distribution.uniform(0.0, 1.0)
        ...     )
        omni.replicator.core.physics.physics_material
    """
    if static_friction is not None:
        _write_physics_node(input_prims, "physics:staticFriction", static_friction, "float")
    if dynamic_friction is not None:
        _write_physics_node(input_prims, "physics:dynamicFriction", dynamic_friction, "float")
    if restitution is not None:
        _write_physics_node(input_prims, "physics:restitution", restitution, "float")


@ReplicatorWrapper
def simulate(time: float, step_dt: float = None, physics_scene: str = None):
    return utils.create_node(
        "omni.replicator.core.OgnPhysicsSimulate", simulationTime=time, stepDt=step_dt, physicsScene=physics_scene
    )


@ReplicatorWrapper
def reset(physics_scene: str = None):
    return utils.create_node("omni.replicator.core.OgnPhysicsReset", physicsScene=physics_scene)
