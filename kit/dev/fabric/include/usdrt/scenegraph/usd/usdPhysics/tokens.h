// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file usdPhysics/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class UsdPhysicsTokensType

/// Provides standard set of public tokens for UsdPhysics schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// UsdPhysicsTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use UsdPhysicsTokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct UsdPhysicsTokensType
{
    UsdPhysicsTokensType();
    /// @brief "acceleration"
    ///
    /// Possible value for UsdPhysicsDriveAPI::GetPhysicsTypeAttr()
    const TfToken acceleration;
    /// @brief "angular"
    ///
    /// This token represents the angular degree of freedom used in Revolute Joint Drive.
    const TfToken angular;
    /// @brief "boundingCube"
    ///
    /// Possible value for UsdPhysicsMeshCollisionAPI::GetPhysicsApproximationAttr()
    const TfToken boundingCube;
    /// @brief "boundingSphere"
    ///
    /// Possible value for UsdPhysicsMeshCollisionAPI::GetPhysicsApproximationAttr()
    const TfToken boundingSphere;
    /// @brief "colliders"
    ///
    /// This token represents the collection name to use with UsdCollectionAPI to represent colliders of a
    /// CollisionGroup prim.
    const TfToken colliders;
    /// @brief "convexDecomposition"
    ///
    /// Possible value for UsdPhysicsMeshCollisionAPI::GetPhysicsApproximationAttr()
    const TfToken convexDecomposition;
    /// @brief "convexHull"
    ///
    /// Possible value for UsdPhysicsMeshCollisionAPI::GetPhysicsApproximationAttr()
    const TfToken convexHull;
    /// @brief "distance"
    ///
    /// This token represents the distance limit used for generic D6 joint.
    const TfToken distance;
    /// @brief "drive"
    ///
    /// Property namespace prefix for the UsdPhysicsDriveAPI schema.
    const TfToken drive;
    /// @brief "force"
    ///
    /// Possible value for UsdPhysicsDriveAPI::GetPhysicsTypeAttr(), Default value for
    /// UsdPhysicsDriveAPI::GetPhysicsTypeAttr()
    const TfToken force;
    /// @brief "kilogramsPerUnit"
    ///
    /// Stage-level metadata that encodes a scene's linear unit of measure as kilograms per encoded unit.
    const TfToken kilogramsPerUnit;
    /// @brief "limit"
    ///
    /// Property namespace prefix for the UsdPhysicsLimitAPI schema.
    const TfToken limit;
    /// @brief "linear"
    ///
    /// This token represents the linear degree of freedom used in Prismatic Joint Drive.
    const TfToken linear;
    /// @brief "meshSimplification"
    ///
    /// Possible value for UsdPhysicsMeshCollisionAPI::GetPhysicsApproximationAttr()
    const TfToken meshSimplification;
    /// @brief "none"
    ///
    /// Possible value for UsdPhysicsMeshCollisionAPI::GetPhysicsApproximationAttr(), Default value for
    /// UsdPhysicsMeshCollisionAPI::GetPhysicsApproximationAttr()
    const TfToken none;
    /// @brief "physics:angularVelocity"
    ///
    /// UsdPhysicsRigidBodyAPI
    const TfToken physicsAngularVelocity;
    /// @brief "physics:approximation"
    ///
    /// UsdPhysicsMeshCollisionAPI
    const TfToken physicsApproximation;
    /// @brief "physics:axis"
    ///
    /// UsdPhysicsSphericalJoint, UsdPhysicsPrismaticJoint, UsdPhysicsRevoluteJoint
    const TfToken physicsAxis;
    /// @brief "physics:body0"
    ///
    /// UsdPhysicsJoint
    const TfToken physicsBody0;
    /// @brief "physics:body1"
    ///
    /// UsdPhysicsJoint
    const TfToken physicsBody1;
    /// @brief "physics:breakForce"
    ///
    /// UsdPhysicsJoint
    const TfToken physicsBreakForce;
    /// @brief "physics:breakTorque"
    ///
    /// UsdPhysicsJoint
    const TfToken physicsBreakTorque;
    /// @brief "physics:centerOfMass"
    ///
    /// UsdPhysicsMassAPI
    const TfToken physicsCenterOfMass;
    /// @brief "physics:collisionEnabled"
    ///
    /// UsdPhysicsJoint, UsdPhysicsCollisionAPI
    const TfToken physicsCollisionEnabled;
    /// @brief "physics:coneAngle0Limit"
    ///
    /// UsdPhysicsSphericalJoint
    const TfToken physicsConeAngle0Limit;
    /// @brief "physics:coneAngle1Limit"
    ///
    /// UsdPhysicsSphericalJoint
    const TfToken physicsConeAngle1Limit;
    /// @brief "physics:damping"
    ///
    /// UsdPhysicsDriveAPI
    const TfToken physicsDamping;
    /// @brief "physics:density"
    ///
    /// UsdPhysicsMaterialAPI, UsdPhysicsMassAPI
    const TfToken physicsDensity;
    /// @brief "physics:diagonalInertia"
    ///
    /// UsdPhysicsMassAPI
    const TfToken physicsDiagonalInertia;
    /// @brief "physics:dynamicFriction"
    ///
    /// UsdPhysicsMaterialAPI
    const TfToken physicsDynamicFriction;
    /// @brief "physics:excludeFromArticulation"
    ///
    /// UsdPhysicsJoint
    const TfToken physicsExcludeFromArticulation;
    /// @brief "physics:filteredGroups"
    ///
    /// UsdPhysicsCollisionGroup
    const TfToken physicsFilteredGroups;
    /// @brief "physics:filteredPairs"
    ///
    /// UsdPhysicsFilteredPairsAPI
    const TfToken physicsFilteredPairs;
    /// @brief "physics:gravityDirection"
    ///
    /// UsdPhysicsScene
    const TfToken physicsGravityDirection;
    /// @brief "physics:gravityMagnitude"
    ///
    /// UsdPhysicsScene
    const TfToken physicsGravityMagnitude;
    /// @brief "physics:high"
    ///
    /// UsdPhysicsLimitAPI
    const TfToken physicsHigh;
    /// @brief "physics:invertFilteredGroups"
    ///
    /// UsdPhysicsCollisionGroup
    const TfToken physicsInvertFilteredGroups;
    /// @brief "physics:jointEnabled"
    ///
    /// UsdPhysicsJoint
    const TfToken physicsJointEnabled;
    /// @brief "physics:kinematicEnabled"
    ///
    /// UsdPhysicsRigidBodyAPI
    const TfToken physicsKinematicEnabled;
    /// @brief "physics:localPos0"
    ///
    /// UsdPhysicsJoint
    const TfToken physicsLocalPos0;
    /// @brief "physics:localPos1"
    ///
    /// UsdPhysicsJoint
    const TfToken physicsLocalPos1;
    /// @brief "physics:localRot0"
    ///
    /// UsdPhysicsJoint
    const TfToken physicsLocalRot0;
    /// @brief "physics:localRot1"
    ///
    /// UsdPhysicsJoint
    const TfToken physicsLocalRot1;
    /// @brief "physics:low"
    ///
    /// UsdPhysicsLimitAPI
    const TfToken physicsLow;
    /// @brief "physics:lowerLimit"
    ///
    /// UsdPhysicsPrismaticJoint, UsdPhysicsRevoluteJoint
    const TfToken physicsLowerLimit;
    /// @brief "physics:mass"
    ///
    /// UsdPhysicsMassAPI
    const TfToken physicsMass;
    /// @brief "physics:maxDistance"
    ///
    /// UsdPhysicsDistanceJoint
    const TfToken physicsMaxDistance;
    /// @brief "physics:maxForce"
    ///
    /// UsdPhysicsDriveAPI
    const TfToken physicsMaxForce;
    /// @brief "physics:mergeGroup"
    ///
    /// UsdPhysicsCollisionGroup
    const TfToken physicsMergeGroup;
    /// @brief "physics:minDistance"
    ///
    /// UsdPhysicsDistanceJoint
    const TfToken physicsMinDistance;
    /// @brief "physics:principalAxes"
    ///
    /// UsdPhysicsMassAPI
    const TfToken physicsPrincipalAxes;
    /// @brief "physics:restitution"
    ///
    /// UsdPhysicsMaterialAPI
    const TfToken physicsRestitution;
    /// @brief "physics:rigidBodyEnabled"
    ///
    /// UsdPhysicsRigidBodyAPI
    const TfToken physicsRigidBodyEnabled;
    /// @brief "physics:simulationOwner"
    ///
    /// UsdPhysicsCollisionAPI, UsdPhysicsRigidBodyAPI
    const TfToken physicsSimulationOwner;
    /// @brief "physics:startsAsleep"
    ///
    /// UsdPhysicsRigidBodyAPI
    const TfToken physicsStartsAsleep;
    /// @brief "physics:staticFriction"
    ///
    /// UsdPhysicsMaterialAPI
    const TfToken physicsStaticFriction;
    /// @brief "physics:stiffness"
    ///
    /// UsdPhysicsDriveAPI
    const TfToken physicsStiffness;
    /// @brief "physics:targetPosition"
    ///
    /// UsdPhysicsDriveAPI
    const TfToken physicsTargetPosition;
    /// @brief "physics:targetVelocity"
    ///
    /// UsdPhysicsDriveAPI
    const TfToken physicsTargetVelocity;
    /// @brief "physics:type"
    ///
    /// UsdPhysicsDriveAPI
    const TfToken physicsType;
    /// @brief "physics:upperLimit"
    ///
    /// UsdPhysicsPrismaticJoint, UsdPhysicsRevoluteJoint
    const TfToken physicsUpperLimit;
    /// @brief "physics:velocity"
    ///
    /// UsdPhysicsRigidBodyAPI
    const TfToken physicsVelocity;
    /// @brief "rotX"
    ///
    /// This token represents the rotate around X axis degree of freedom used in Joint Limits and Drives.
    const TfToken rotX;
    /// @brief "rotY"
    ///
    /// This token represents the rotate around Y axis degree of freedom used in Joint Limits and Drives.
    const TfToken rotY;
    /// @brief "rotZ"
    ///
    /// This token represents the rotate around Z axis degree of freedom used in Joint Limits and Drives.
    const TfToken rotZ;
    /// @brief "transX"
    ///
    /// This token represents the translate around X axis degree of freedom used in Joint Limits and Drives.
    const TfToken transX;
    /// @brief "transY"
    ///
    /// This token represents the translate around Y axis degree of freedom used in Joint Limits and Drives.
    const TfToken transY;
    /// @brief "transZ"
    ///
    /// This token represents the translate around Z axis degree of freedom used in Joint Limits and Drives.
    const TfToken transZ;
    /// @brief "X"
    ///
    /// Possible value for UsdPhysicsSphericalJoint::GetPhysicsAxisAttr(), Default value for
    /// UsdPhysicsSphericalJoint::GetPhysicsAxisAttr(), Possible value for
    /// UsdPhysicsPrismaticJoint::GetPhysicsAxisAttr(), Default value for
    /// UsdPhysicsPrismaticJoint::GetPhysicsAxisAttr(), Possible value for
    /// UsdPhysicsRevoluteJoint::GetPhysicsAxisAttr(), Default value for UsdPhysicsRevoluteJoint::GetPhysicsAxisAttr()
    const TfToken x;
    /// @brief "Y"
    ///
    /// Possible value for UsdPhysicsSphericalJoint::GetPhysicsAxisAttr(), Possible value for
    /// UsdPhysicsPrismaticJoint::GetPhysicsAxisAttr(), Possible value for UsdPhysicsRevoluteJoint::GetPhysicsAxisAttr()
    const TfToken y;
    /// @brief "Z"
    ///
    /// Possible value for UsdPhysicsSphericalJoint::GetPhysicsAxisAttr(), Possible value for
    /// UsdPhysicsPrismaticJoint::GetPhysicsAxisAttr(), Possible value for UsdPhysicsRevoluteJoint::GetPhysicsAxisAttr()
    const TfToken z;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline UsdPhysicsTokensType::UsdPhysicsTokensType()
    : acceleration("acceleration"),
      angular("angular"),
      boundingCube("boundingCube"),
      boundingSphere("boundingSphere"),
      colliders("colliders"),
      convexDecomposition("convexDecomposition"),
      convexHull("convexHull"),
      distance("distance"),
      drive("drive"),
      force("force"),
      kilogramsPerUnit("kilogramsPerUnit"),
      limit("limit"),
      linear("linear"),
      meshSimplification("meshSimplification"),
      none("none"),
      physicsAngularVelocity("physics:angularVelocity"),
      physicsApproximation("physics:approximation"),
      physicsAxis("physics:axis"),
      physicsBody0("physics:body0"),
      physicsBody1("physics:body1"),
      physicsBreakForce("physics:breakForce"),
      physicsBreakTorque("physics:breakTorque"),
      physicsCenterOfMass("physics:centerOfMass"),
      physicsCollisionEnabled("physics:collisionEnabled"),
      physicsConeAngle0Limit("physics:coneAngle0Limit"),
      physicsConeAngle1Limit("physics:coneAngle1Limit"),
      physicsDamping("physics:damping"),
      physicsDensity("physics:density"),
      physicsDiagonalInertia("physics:diagonalInertia"),
      physicsDynamicFriction("physics:dynamicFriction"),
      physicsExcludeFromArticulation("physics:excludeFromArticulation"),
      physicsFilteredGroups("physics:filteredGroups"),
      physicsFilteredPairs("physics:filteredPairs"),
      physicsGravityDirection("physics:gravityDirection"),
      physicsGravityMagnitude("physics:gravityMagnitude"),
      physicsHigh("physics:high"),
      physicsInvertFilteredGroups("physics:invertFilteredGroups"),
      physicsJointEnabled("physics:jointEnabled"),
      physicsKinematicEnabled("physics:kinematicEnabled"),
      physicsLocalPos0("physics:localPos0"),
      physicsLocalPos1("physics:localPos1"),
      physicsLocalRot0("physics:localRot0"),
      physicsLocalRot1("physics:localRot1"),
      physicsLow("physics:low"),
      physicsLowerLimit("physics:lowerLimit"),
      physicsMass("physics:mass"),
      physicsMaxDistance("physics:maxDistance"),
      physicsMaxForce("physics:maxForce"),
      physicsMergeGroup("physics:mergeGroup"),
      physicsMinDistance("physics:minDistance"),
      physicsPrincipalAxes("physics:principalAxes"),
      physicsRestitution("physics:restitution"),
      physicsRigidBodyEnabled("physics:rigidBodyEnabled"),
      physicsSimulationOwner("physics:simulationOwner"),
      physicsStartsAsleep("physics:startsAsleep"),
      physicsStaticFriction("physics:staticFriction"),
      physicsStiffness("physics:stiffness"),
      physicsTargetPosition("physics:targetPosition"),
      physicsTargetVelocity("physics:targetVelocity"),
      physicsType("physics:type"),
      physicsUpperLimit("physics:upperLimit"),
      physicsVelocity("physics:velocity"),
      rotX("rotX"),
      rotY("rotY"),
      rotZ("rotZ"),
      transX("transX"),
      transY("transY"),
      transZ("transZ"),
      x("X"),
      y("Y"),
      z("Z")
{
}

struct UsdPhysicsTokensTypeAccessor
{
    const UsdPhysicsTokensType* operator->()
    {
        static const UsdPhysicsTokensType tokens;
        return &tokens;
    }
};


inline UsdPhysicsTokensTypeAccessor UsdPhysicsTokens;


} // namespace usdrt
