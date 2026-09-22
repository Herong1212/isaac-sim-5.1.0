// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file physxSchema/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class PhysxSchemaTokensType

/// Provides standard set of public tokens for PhysxSchema schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// PhysxSchemaTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use PhysxSchemaTokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct PhysxSchemaTokensType
{
    PhysxSchemaTokensType();
    /// @brief "acceleration"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextUpdateModeAttr(), Possible value for
    /// PhysxSchemaPhysxForceAPI::GetPhysxForceModeAttr(), Default value for
    /// PhysxSchemaPhysxForceAPI::GetPhysxForceModeAttr()
    const TfToken acceleration;
    /// @brief "actor0"
    ///
    /// PhysxSchemaPhysxPhysicsAttachment
    const TfToken actor0;
    /// @brief "actor1"
    ///
    /// PhysxSchemaPhysxPhysicsAttachment
    const TfToken actor1;
    /// @brief "alwaysUpdateEnabled"
    ///
    /// PhysxSchemaPhysxCameraAPI
    const TfToken alwaysUpdateEnabled;
    /// @brief "Asynchronous"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneUpdateTypeAttr()
    const TfToken asynchronous;
    /// @brief "attachmentEnabled"
    ///
    /// PhysxSchemaPhysxPhysicsAttachment
    const TfToken attachmentEnabled;
    /// @brief "average"
    ///
    /// Possible value for PhysxSchemaPhysxMaterialAPI::GetPhysxMaterialFrictionCombineModeAttr(), Default value for
    /// PhysxSchemaPhysxMaterialAPI::GetPhysxMaterialFrictionCombineModeAttr(), Possible value for
    /// PhysxSchemaPhysxMaterialAPI::GetPhysxMaterialRestitutionCombineModeAttr(), Default value for
    /// PhysxSchemaPhysxMaterialAPI::GetPhysxMaterialRestitutionCombineModeAttr()
    const TfToken average;
    /// @brief "BitsPerPixel16"
    ///
    /// Possible value for PhysxSchemaPhysxSDFMeshCollisionAPI::GetPhysxSDFMeshCollisionSdfBitsPerSubgridPixelAttr(),
    /// Default value for PhysxSchemaPhysxSDFMeshCollisionAPI::GetPhysxSDFMeshCollisionSdfBitsPerSubgridPixelAttr()
    const TfToken bitsPerPixel16;
    /// @brief "BitsPerPixel32"
    ///
    /// Possible value for PhysxSchemaPhysxSDFMeshCollisionAPI::GetPhysxSDFMeshCollisionSdfBitsPerSubgridPixelAttr()
    const TfToken bitsPerPixel32;
    /// @brief "BitsPerPixel8"
    ///
    /// Possible value for PhysxSchemaPhysxSDFMeshCollisionAPI::GetPhysxSDFMeshCollisionSdfBitsPerSubgridPixelAttr()
    const TfToken bitsPerPixel8;
    /// @brief "bounceThreshold"
    ///
    /// PhysxSchemaPhysxLimitAPI
    const TfToken bounceThreshold;
    /// @brief "brakes0"
    ///
    /// This token represents braking system 0 used in PhysxVehicleBrakesAPI. It also holds the instance name to use for
    /// PhysxVehicleNonlinearCommandResponseAPI when applied to braking system 0.
    const TfToken brakes0;
    /// @brief "brakes1"
    ///
    /// This token represents braking system 1 used in PhysxVehicleBrakesAPI. It also holds the instance name to use for
    /// PhysxVehicleNonlinearCommandResponseAPI when applied to braking system 1.
    const TfToken brakes1;
    /// @brief "buffer"
    ///
    /// PhysxSchemaPhysxCookedDataAPI
    const TfToken buffer;
    /// @brief "clothConstaint"
    ///
    /// This token represents the collection name to use with PhysxCookedDataAPI to represent cooked data of a
    /// clothConstaint.
    const TfToken clothConstaint;
    /// @brief "collisionFilterIndices0"
    ///
    /// PhysxSchemaPhysxPhysicsAttachment
    const TfToken collisionFilterIndices0;
    /// @brief "collisionFilterIndices1"
    ///
    /// PhysxSchemaPhysxPhysicsAttachment
    const TfToken collisionFilterIndices1;
    /// @brief "collisionmeshes"
    ///
    /// This token defines the PhysxMeshMergeCollisionAPI collection that gathers the collision meshes.
    const TfToken collisionmeshes;
    /// @brief "commandValues"
    ///
    /// PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI
    const TfToken commandValues;
    /// @brief "constrained"
    ///
    /// Possible value for PhysxSchemaPhysxCharacterControllerAPI::GetPhysxCharacterControllerClimbingModeAttr()
    const TfToken constrained;
    /// @brief "contactDistance"
    ///
    /// PhysxSchemaPhysxLimitAPI
    const TfToken contactDistance;
    /// @brief "contactOffset"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken contactOffset;
    /// @brief "convexDecomposition"
    ///
    /// This token represents the collection name to use with PhysxCookedDataAPI to represent cooked data of a
    /// convexDecomposition.
    const TfToken convexDecomposition;
    /// @brief "convexHull"
    ///
    /// This token represents the collection name to use with PhysxCookedDataAPI to represent cooked data of a
    /// convexhull.
    const TfToken convexHull;
    /// @brief "damping"
    ///
    /// PhysxSchemaPhysxTendonAttachmentRootAPI, PhysxSchemaPhysxTendonAxisRootAPI, PhysxSchemaPhysxLimitAPI
    const TfToken damping;
    /// @brief "defaultFrictionValue"
    ///
    /// PhysxSchemaPhysxVehicleTireFrictionTable
    const TfToken defaultFrictionValue;
    /// @brief "Disabled"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneUpdateTypeAttr()
    const TfToken disabled;
    /// @brief "drive"
    ///
    /// This token holds the instance name to use for PhysxVehicleNonlinearCommandResponseAPI when applying it to a
    /// basic drive.
    const TfToken drive;
    /// @brief "easy"
    ///
    /// Possible value for PhysxSchemaPhysxCharacterControllerAPI::GetPhysxCharacterControllerClimbingModeAttr(),
    /// Default value for PhysxSchemaPhysxCharacterControllerAPI::GetPhysxCharacterControllerClimbingModeAttr()
    const TfToken easy;
    /// @brief "enableCCD"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken enableCCD;
    /// @brief "filterType0"
    ///
    /// PhysxSchemaPhysxPhysicsAttachment
    const TfToken filterType0;
    /// @brief "filterType1"
    ///
    /// PhysxSchemaPhysxPhysicsAttachment
    const TfToken filterType1;
    /// @brief "flood"
    ///
    /// Possible value for PhysxSchemaPhysxSphereFillCollisionAPI::GetPhysxSphereFillCollisionFillModeAttr(), Default
    /// value for PhysxSchemaPhysxSphereFillCollisionAPI::GetPhysxSphereFillCollisionFillModeAttr()
    const TfToken flood;
    /// @brief "fluidRestOffset"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken fluidRestOffset;
    /// @brief "force"
    ///
    /// Possible value for PhysxSchemaPhysxForceAPI::GetPhysxForceModeAttr()
    const TfToken force;
    /// @brief "forceCoefficient"
    ///
    /// PhysxSchemaPhysxTendonAxisAPI
    const TfToken forceCoefficient;
    /// @brief "frictionValues"
    ///
    /// PhysxSchemaPhysxVehicleTireFrictionTable
    const TfToken frictionValues;
    /// @brief "gearing"
    ///
    /// PhysxSchemaPhysxTendonAttachmentAPI, PhysxSchemaPhysxTendonAxisAPI
    const TfToken gearing;
    /// @brief "Geometry"
    ///
    /// Possible value for PhysxSchemaPhysxPhysicsAttachment::GetFilterType0Attr(), Possible value for
    /// PhysxSchemaPhysxPhysicsAttachment::GetFilterType1Attr()
    const TfToken geometry;
    /// @brief "globalSelfCollisionEnabled"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken globalSelfCollisionEnabled;
    /// @brief "GPU"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneBroadphaseTypeAttr(), Default value for
    /// PhysxSchemaPhysxSceneAPI::GetPhysxSceneBroadphaseTypeAttr()
    const TfToken gPU;
    /// @brief "groundMaterials"
    ///
    /// PhysxSchemaPhysxVehicleTireFrictionTable
    const TfToken groundMaterials;
    /// @brief "indices"
    ///
    /// PhysxSchemaTetrahedralMesh
    const TfToken indices;
    /// @brief "jointAxis"
    ///
    /// PhysxSchemaPhysxTendonAxisAPI
    const TfToken jointAxis;
    /// @brief "limitStiffness"
    ///
    /// PhysxSchemaPhysxTendonAttachmentRootAPI, PhysxSchemaPhysxTendonAxisRootAPI
    const TfToken limitStiffness;
    /// @brief "localPos"
    ///
    /// PhysxSchemaPhysxTendonAttachmentAPI
    const TfToken localPos;
    /// @brief "lowerLimit"
    ///
    /// PhysxSchemaPhysxTendonAttachmentLeafAPI, PhysxSchemaPhysxTendonAxisRootAPI
    const TfToken lowerLimit;
    /// @brief "max"
    ///
    /// Possible value for PhysxSchemaPhysxMaterialAPI::GetPhysxMaterialFrictionCombineModeAttr(), Possible value for
    /// PhysxSchemaPhysxMaterialAPI::GetPhysxMaterialRestitutionCombineModeAttr()
    const TfToken max;
    /// @brief "maxBrakeTorque"
    ///
    /// PhysxSchemaPhysxVehicleBrakesAPI
    const TfToken maxBrakeTorque;
    /// @brief "maxDepenetrationVelocity"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken maxDepenetrationVelocity;
    /// @brief "maxNeighborhood"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken maxNeighborhood;
    /// @brief "maxVelocity"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken maxVelocity;
    /// @brief "MBP"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneBroadphaseTypeAttr()
    const TfToken mBP;
    /// @brief "min"
    ///
    /// Possible value for PhysxSchemaPhysxMaterialAPI::GetPhysxMaterialFrictionCombineModeAttr(), Possible value for
    /// PhysxSchemaPhysxMaterialAPI::GetPhysxMaterialRestitutionCombineModeAttr()
    const TfToken min;
    /// @brief "multiply"
    ///
    /// Possible value for PhysxSchemaPhysxMaterialAPI::GetPhysxMaterialFrictionCombineModeAttr(), Possible value for
    /// PhysxSchemaPhysxMaterialAPI::GetPhysxMaterialRestitutionCombineModeAttr()
    const TfToken multiply;
    /// @brief "negX"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextLongitudinalAxisAttr(), Possible
    /// value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextVerticalAxisAttr()
    const TfToken negX;
    /// @brief "negY"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextLongitudinalAxisAttr(), Possible
    /// value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextVerticalAxisAttr()
    const TfToken negY;
    /// @brief "negZ"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextLongitudinalAxisAttr(), Possible
    /// value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextVerticalAxisAttr()
    const TfToken negZ;
    /// @brief "neighborhoodScale"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken neighborhoodScale;
    /// @brief "nonParticleCollisionEnabled"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken nonParticleCollisionEnabled;
    /// @brief "offset"
    ///
    /// PhysxSchemaPhysxTendonAttachmentRootAPI, PhysxSchemaPhysxTendonAxisRootAPI
    const TfToken offset;
    /// @brief "oneDirectional"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneFrictionTypeAttr()
    const TfToken oneDirectional;
    /// @brief "parentAttachment"
    ///
    /// PhysxSchemaPhysxTendonAttachmentAPI
    const TfToken parentAttachment;
    /// @brief "parentLink"
    ///
    /// PhysxSchemaPhysxTendonAttachmentAPI
    const TfToken parentLink;
    /// @brief "particleContactOffset"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken particleContactOffset;
    /// @brief "particleSystemEnabled"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken particleSystemEnabled;
    /// @brief "patch"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneFrictionTypeAttr(), Default value for
    /// PhysxSchemaPhysxSceneAPI::GetPhysxSceneFrictionTypeAttr()
    const TfToken patch;
    /// @brief "PCM"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneCollisionSystemAttr(), Default value for
    /// PhysxSchemaPhysxSceneAPI::GetPhysxSceneCollisionSystemAttr()
    const TfToken pCM;
    /// @brief "PGS"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneSolverTypeAttr()
    const TfToken pGS;
    /// @brief "physics:body0Indices"
    ///
    /// PhysxSchemaPhysxPhysicsJointInstancer
    const TfToken physicsBody0Indices;
    /// @brief "physics:body0s"
    ///
    /// PhysxSchemaPhysxPhysicsJointInstancer
    const TfToken physicsBody0s;
    /// @brief "physics:body1Indices"
    ///
    /// PhysxSchemaPhysxPhysicsJointInstancer
    const TfToken physicsBody1Indices;
    /// @brief "physics:body1s"
    ///
    /// PhysxSchemaPhysxPhysicsJointInstancer
    const TfToken physicsBody1s;
    /// @brief "physics:gearRatio"
    ///
    /// PhysxSchemaPhysxPhysicsGearJoint
    const TfToken physicsGearRatio;
    /// @brief "physics:hinge"
    ///
    /// PhysxSchemaPhysxPhysicsRackAndPinionJoint
    const TfToken physicsHinge;
    /// @brief "physics:hinge0"
    ///
    /// PhysxSchemaPhysxPhysicsGearJoint
    const TfToken physicsHinge0;
    /// @brief "physics:hinge1"
    ///
    /// PhysxSchemaPhysxPhysicsGearJoint
    const TfToken physicsHinge1;
    /// @brief "physics:localPos0s"
    ///
    /// PhysxSchemaPhysxPhysicsJointInstancer
    const TfToken physicsLocalPos0s;
    /// @brief "physics:localPos1s"
    ///
    /// PhysxSchemaPhysxPhysicsJointInstancer
    const TfToken physicsLocalPos1s;
    /// @brief "physics:localRot0s"
    ///
    /// PhysxSchemaPhysxPhysicsJointInstancer
    const TfToken physicsLocalRot0s;
    /// @brief "physics:localRot1s"
    ///
    /// PhysxSchemaPhysxPhysicsJointInstancer
    const TfToken physicsLocalRot1s;
    /// @brief "physics:position"
    ///
    /// PhysxSchemaJointStateAPI
    const TfToken physicsPosition;
    /// @brief "physics:prismatic"
    ///
    /// PhysxSchemaPhysxPhysicsRackAndPinionJoint
    const TfToken physicsPrismatic;
    /// @brief "physics:protoIndices"
    ///
    /// PhysxSchemaPhysxPhysicsInstancer
    const TfToken physicsProtoIndices;
    /// @brief "physics:prototypes"
    ///
    /// PhysxSchemaPhysxPhysicsInstancer
    const TfToken physicsPrototypes;
    /// @brief "physics:ratio"
    ///
    /// PhysxSchemaPhysxPhysicsRackAndPinionJoint
    const TfToken physicsRatio;
    /// @brief "physics:velocity"
    ///
    /// PhysxSchemaJointStateAPI
    const TfToken physicsVelocity;
    /// @brief "physxArticulation:articulationEnabled"
    ///
    /// PhysxSchemaPhysxArticulationAPI
    const TfToken physxArticulationArticulationEnabled;
    /// @brief "physxArticulation:enabledSelfCollisions"
    ///
    /// PhysxSchemaPhysxArticulationAPI
    const TfToken physxArticulationEnabledSelfCollisions;
    /// @brief "physxArticulationForceSensor:constraintSolverForcesEnabled"
    ///
    /// PhysxSchemaPhysxArticulationForceSensorAPI
    const TfToken physxArticulationForceSensorConstraintSolverForcesEnabled;
    /// @brief "physxArticulationForceSensor:force"
    ///
    /// PhysxSchemaPhysxArticulationForceSensorAPI
    const TfToken physxArticulationForceSensorForce;
    /// @brief "physxArticulationForceSensor:forwardDynamicsForcesEnabled"
    ///
    /// PhysxSchemaPhysxArticulationForceSensorAPI
    const TfToken physxArticulationForceSensorForwardDynamicsForcesEnabled;
    /// @brief "physxArticulationForceSensor:sensorEnabled"
    ///
    /// PhysxSchemaPhysxArticulationForceSensorAPI
    const TfToken physxArticulationForceSensorSensorEnabled;
    /// @brief "physxArticulationForceSensor:torque"
    ///
    /// PhysxSchemaPhysxArticulationForceSensorAPI
    const TfToken physxArticulationForceSensorTorque;
    /// @brief "physxArticulationForceSensor:worldFrameEnabled"
    ///
    /// PhysxSchemaPhysxArticulationForceSensorAPI
    const TfToken physxArticulationForceSensorWorldFrameEnabled;
    /// @brief "physxArticulation:sleepThreshold"
    ///
    /// PhysxSchemaPhysxArticulationAPI
    const TfToken physxArticulationSleepThreshold;
    /// @brief "physxArticulation:solverPositionIterationCount"
    ///
    /// PhysxSchemaPhysxArticulationAPI
    const TfToken physxArticulationSolverPositionIterationCount;
    /// @brief "physxArticulation:solverVelocityIterationCount"
    ///
    /// PhysxSchemaPhysxArticulationAPI
    const TfToken physxArticulationSolverVelocityIterationCount;
    /// @brief "physxArticulation:stabilizationThreshold"
    ///
    /// PhysxSchemaPhysxArticulationAPI
    const TfToken physxArticulationStabilizationThreshold;
    /// @brief "physxAutoAttachment:collisionFilteringOffset"
    ///
    /// PhysxSchemaPhysxAutoAttachmentAPI
    const TfToken physxAutoAttachmentCollisionFilteringOffset;
    /// @brief "physxAutoAttachment:deformableVertexOverlapOffset"
    ///
    /// PhysxSchemaPhysxAutoAttachmentAPI
    const TfToken physxAutoAttachmentDeformableVertexOverlapOffset;
    /// @brief "physxAutoAttachment:enableCollisionFiltering"
    ///
    /// PhysxSchemaPhysxAutoAttachmentAPI
    const TfToken physxAutoAttachmentEnableCollisionFiltering;
    /// @brief "physxAutoAttachment:enableDeformableFilteringPairs"
    ///
    /// PhysxSchemaPhysxAutoAttachmentAPI
    const TfToken physxAutoAttachmentEnableDeformableFilteringPairs;
    /// @brief "physxAutoAttachment:enableDeformableVertexAttachments"
    ///
    /// PhysxSchemaPhysxAutoAttachmentAPI
    const TfToken physxAutoAttachmentEnableDeformableVertexAttachments;
    /// @brief "physxAutoAttachment:enableRigidSurfaceAttachments"
    ///
    /// PhysxSchemaPhysxAutoAttachmentAPI
    const TfToken physxAutoAttachmentEnableRigidSurfaceAttachments;
    /// @brief "physxAutoAttachment:rigidSurfaceSamplingDistance"
    ///
    /// PhysxSchemaPhysxAutoAttachmentAPI
    const TfToken physxAutoAttachmentRigidSurfaceSamplingDistance;
    /// @brief "physxAutoParticleCloth:disableMeshWelding"
    ///
    /// PhysxSchemaPhysxAutoParticleClothAPI
    const TfToken physxAutoParticleClothDisableMeshWelding;
    /// @brief "physxAutoParticleCloth:springBendStiffness"
    ///
    /// PhysxSchemaPhysxAutoParticleClothAPI
    const TfToken physxAutoParticleClothSpringBendStiffness;
    /// @brief "physxAutoParticleCloth:springDamping"
    ///
    /// PhysxSchemaPhysxAutoParticleClothAPI
    const TfToken physxAutoParticleClothSpringDamping;
    /// @brief "physxAutoParticleCloth:springShearStiffness"
    ///
    /// PhysxSchemaPhysxAutoParticleClothAPI
    const TfToken physxAutoParticleClothSpringShearStiffness;
    /// @brief "physxAutoParticleCloth:springStretchStiffness"
    ///
    /// PhysxSchemaPhysxAutoParticleClothAPI
    const TfToken physxAutoParticleClothSpringStretchStiffness;
    /// @brief "physxCamera:subject"
    ///
    /// PhysxSchemaPhysxCameraAPI
    const TfToken physxCameraSubject;
    /// @brief "physxCharacterController:climbingMode"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerClimbingMode;
    /// @brief "physxCharacterController:contactOffset"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerContactOffset;
    /// @brief "physxCharacterController:invisibleWallHeight"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerInvisibleWallHeight;
    /// @brief "physxCharacterController:maxJumpHeight"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerMaxJumpHeight;
    /// @brief "physxCharacterController:moveTarget"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerMoveTarget;
    /// @brief "physxCharacterController:nonWalkableMode"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerNonWalkableMode;
    /// @brief "physxCharacterController:scaleCoeff"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerScaleCoeff;
    /// @brief "physxCharacterController:simulationOwner"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerSimulationOwner;
    /// @brief "physxCharacterController:slopeLimit"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerSlopeLimit;
    /// @brief "physxCharacterController:stepOffset"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerStepOffset;
    /// @brief "physxCharacterController:upAxis"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerUpAxis;
    /// @brief "physxCharacterController:volumeGrowth"
    ///
    /// PhysxSchemaPhysxCharacterControllerAPI
    const TfToken physxCharacterControllerVolumeGrowth;
    /// @brief "physxCollision:contactOffset"
    ///
    /// PhysxSchemaPhysxCollisionAPI
    const TfToken physxCollisionContactOffset;
    /// @brief "physxCollisionCustomGeometry"
    ///
    /// This token represents the custom geometry option for cones and cylinders. The simulation will not use a convex
    /// approximation but a custom geometry instead.
    const TfToken physxCollisionCustomGeometry;
    /// @brief "physxCollision:minTorsionalPatchRadius"
    ///
    /// PhysxSchemaPhysxCollisionAPI
    const TfToken physxCollisionMinTorsionalPatchRadius;
    /// @brief "physxCollision:restOffset"
    ///
    /// PhysxSchemaPhysxCollisionAPI
    const TfToken physxCollisionRestOffset;
    /// @brief "physxCollision:torsionalPatchRadius"
    ///
    /// PhysxSchemaPhysxCollisionAPI
    const TfToken physxCollisionTorsionalPatchRadius;
    /// @brief "physxContactReport:reportPairs"
    ///
    /// PhysxSchemaPhysxContactReportAPI
    const TfToken physxContactReportReportPairs;
    /// @brief "physxContactReport:threshold"
    ///
    /// PhysxSchemaPhysxContactReportAPI
    const TfToken physxContactReportThreshold;
    /// @brief "physxConvexDecompositionCollision:errorPercentage"
    ///
    /// PhysxSchemaPhysxConvexDecompositionCollisionAPI
    const TfToken physxConvexDecompositionCollisionErrorPercentage;
    /// @brief "physxConvexDecompositionCollision:hullVertexLimit"
    ///
    /// PhysxSchemaPhysxConvexDecompositionCollisionAPI
    const TfToken physxConvexDecompositionCollisionHullVertexLimit;
    /// @brief "physxConvexDecompositionCollision:maxConvexHulls"
    ///
    /// PhysxSchemaPhysxConvexDecompositionCollisionAPI
    const TfToken physxConvexDecompositionCollisionMaxConvexHulls;
    /// @brief "physxConvexDecompositionCollision:minThickness"
    ///
    /// PhysxSchemaPhysxConvexDecompositionCollisionAPI
    const TfToken physxConvexDecompositionCollisionMinThickness;
    /// @brief "physxConvexDecompositionCollision:shrinkWrap"
    ///
    /// PhysxSchemaPhysxConvexDecompositionCollisionAPI
    const TfToken physxConvexDecompositionCollisionShrinkWrap;
    /// @brief "physxConvexDecompositionCollision:voxelResolution"
    ///
    /// PhysxSchemaPhysxConvexDecompositionCollisionAPI
    const TfToken physxConvexDecompositionCollisionVoxelResolution;
    /// @brief "physxConvexHullCollision:hullVertexLimit"
    ///
    /// PhysxSchemaPhysxConvexHullCollisionAPI
    const TfToken physxConvexHullCollisionHullVertexLimit;
    /// @brief "physxConvexHullCollision:minThickness"
    ///
    /// PhysxSchemaPhysxConvexHullCollisionAPI
    const TfToken physxConvexHullCollisionMinThickness;
    /// @brief "physxCookedData"
    ///
    /// Property namespace prefix for the PhysxSchemaPhysxCookedDataAPI schema.
    const TfToken physxCookedData;
    /// @brief "physxDeformableBodyMaterial:dampingScale"
    ///
    /// PhysxSchemaPhysxDeformableBodyMaterialAPI
    const TfToken physxDeformableBodyMaterialDampingScale;
    /// @brief "physxDeformableBodyMaterial:density"
    ///
    /// PhysxSchemaPhysxDeformableBodyMaterialAPI
    const TfToken physxDeformableBodyMaterialDensity;
    /// @brief "physxDeformableBodyMaterial:dynamicFriction"
    ///
    /// PhysxSchemaPhysxDeformableBodyMaterialAPI
    const TfToken physxDeformableBodyMaterialDynamicFriction;
    /// @brief "physxDeformableBodyMaterial:elasticityDamping"
    ///
    /// PhysxSchemaPhysxDeformableBodyMaterialAPI
    const TfToken physxDeformableBodyMaterialElasticityDamping;
    /// @brief "physxDeformableBodyMaterial:poissonsRatio"
    ///
    /// PhysxSchemaPhysxDeformableBodyMaterialAPI
    const TfToken physxDeformableBodyMaterialPoissonsRatio;
    /// @brief "physxDeformableBodyMaterial:youngsModulus"
    ///
    /// PhysxSchemaPhysxDeformableBodyMaterialAPI
    const TfToken physxDeformableBodyMaterialYoungsModulus;
    /// @brief "physxDeformable:collisionIndices"
    ///
    /// PhysxSchemaPhysxDeformableBodyAPI
    const TfToken physxDeformableCollisionIndices;
    /// @brief "physxDeformable:collisionPoints"
    ///
    /// PhysxSchemaPhysxDeformableBodyAPI
    const TfToken physxDeformableCollisionPoints;
    /// @brief "physxDeformable:collisionRestPoints"
    ///
    /// PhysxSchemaPhysxDeformableBodyAPI
    const TfToken physxDeformableCollisionRestPoints;
    /// @brief "physxDeformable:deformableEnabled"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableDeformableEnabled;
    /// @brief "physxDeformable:disableGravity"
    ///
    /// PhysxSchemaPhysxDeformableBodyAPI
    const TfToken physxDeformableDisableGravity;
    /// @brief "physxDeformable:enableCCD"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableEnableCCD;
    /// @brief "physxDeformable:maxDepenetrationVelocity"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableMaxDepenetrationVelocity;
    /// @brief "physxDeformable:restPoints"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableRestPoints;
    /// @brief "physxDeformable:selfCollision"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableSelfCollision;
    /// @brief "physxDeformable:selfCollisionFilterDistance"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableSelfCollisionFilterDistance;
    /// @brief "physxDeformable:settlingThreshold"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableSettlingThreshold;
    /// @brief "physxDeformable:simulationIndices"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableSimulationIndices;
    /// @brief "physxDeformable:simulationOwner"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableSimulationOwner;
    /// @brief "physxDeformable:simulationPoints"
    ///
    /// PhysxSchemaPhysxDeformableBodyAPI
    const TfToken physxDeformableSimulationPoints;
    /// @brief "physxDeformable:simulationRestPoints"
    ///
    /// PhysxSchemaPhysxDeformableBodyAPI
    const TfToken physxDeformableSimulationRestPoints;
    /// @brief "physxDeformable:simulationVelocities"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableSimulationVelocities;
    /// @brief "physxDeformable:sleepDamping"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableSleepDamping;
    /// @brief "physxDeformable:sleepThreshold"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableSleepThreshold;
    /// @brief "physxDeformable:solverPositionIterationCount"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableSolverPositionIterationCount;
    /// @brief "physxDeformableSurface:bendingStiffnessScale"
    ///
    /// PhysxSchemaPhysxDeformableSurfaceAPI
    const TfToken physxDeformableSurfaceBendingStiffnessScale;
    /// @brief "physxDeformableSurface:collisionIterationMultiplier"
    ///
    /// PhysxSchemaPhysxDeformableSurfaceAPI
    const TfToken physxDeformableSurfaceCollisionIterationMultiplier;
    /// @brief "physxDeformableSurface:collisionPairUpdateFrequency"
    ///
    /// PhysxSchemaPhysxDeformableSurfaceAPI
    const TfToken physxDeformableSurfaceCollisionPairUpdateFrequency;
    /// @brief "physxDeformableSurface:flatteningEnabled"
    ///
    /// PhysxSchemaPhysxDeformableSurfaceAPI
    const TfToken physxDeformableSurfaceFlatteningEnabled;
    /// @brief "physxDeformableSurfaceMaterial:density"
    ///
    /// PhysxSchemaPhysxDeformableSurfaceMaterialAPI
    const TfToken physxDeformableSurfaceMaterialDensity;
    /// @brief "physxDeformableSurfaceMaterial:dynamicFriction"
    ///
    /// PhysxSchemaPhysxDeformableSurfaceMaterialAPI
    const TfToken physxDeformableSurfaceMaterialDynamicFriction;
    /// @brief "physxDeformableSurfaceMaterial:poissonsRatio"
    ///
    /// PhysxSchemaPhysxDeformableSurfaceMaterialAPI
    const TfToken physxDeformableSurfaceMaterialPoissonsRatio;
    /// @brief "physxDeformableSurfaceMaterial:thickness"
    ///
    /// PhysxSchemaPhysxDeformableSurfaceMaterialAPI
    const TfToken physxDeformableSurfaceMaterialThickness;
    /// @brief "physxDeformableSurfaceMaterial:youngsModulus"
    ///
    /// PhysxSchemaPhysxDeformableSurfaceMaterialAPI
    const TfToken physxDeformableSurfaceMaterialYoungsModulus;
    /// @brief "physxDeformableSurface:maxVelocity"
    ///
    /// PhysxSchemaPhysxDeformableSurfaceAPI
    const TfToken physxDeformableSurfaceMaxVelocity;
    /// @brief "physxDeformable:vertexVelocityDamping"
    ///
    /// PhysxSchemaPhysxDeformableAPI
    const TfToken physxDeformableVertexVelocityDamping;
    /// @brief "physxDiffuseParticles:airDrag"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesAirDrag;
    /// @brief "physxDiffuseParticles:bubbleDrag"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesBubbleDrag;
    /// @brief "physxDiffuseParticles:buoyancy"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesBuoyancy;
    /// @brief "physxDiffuseParticles:collisionDecay"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesCollisionDecay;
    /// @brief "physxDiffuseParticles:diffuseParticlesEnabled"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesDiffuseParticlesEnabled;
    /// @brief "physxDiffuseParticles:divergenceWeight"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesDivergenceWeight;
    /// @brief "physxDiffuseParticles:kineticEnergyWeight"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesKineticEnergyWeight;
    /// @brief "physxDiffuseParticles:lifetime"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesLifetime;
    /// @brief "physxDiffuseParticles:maxDiffuseParticleMultiplier"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesMaxDiffuseParticleMultiplier;
    /// @brief "physxDiffuseParticles:pressureWeight"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesPressureWeight;
    /// @brief "physxDiffuseParticles:threshold"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesThreshold;
    /// @brief "physxDiffuseParticles:useAccurateVelocity"
    ///
    /// PhysxSchemaPhysxDiffuseParticlesAPI
    const TfToken physxDiffuseParticlesUseAccurateVelocity;
    /// @brief "physxDroneCamera:feedForwardVelocityGain"
    ///
    /// PhysxSchemaPhysxCameraDroneAPI
    const TfToken physxDroneCameraFeedForwardVelocityGain;
    /// @brief "physxDroneCamera:followDistance"
    ///
    /// PhysxSchemaPhysxCameraDroneAPI
    const TfToken physxDroneCameraFollowDistance;
    /// @brief "physxDroneCamera:followHeight"
    ///
    /// PhysxSchemaPhysxCameraDroneAPI
    const TfToken physxDroneCameraFollowHeight;
    /// @brief "physxDroneCamera:horizontalVelocityGain"
    ///
    /// PhysxSchemaPhysxCameraDroneAPI
    const TfToken physxDroneCameraHorizontalVelocityGain;
    /// @brief "physxDroneCamera:maxDistance"
    ///
    /// PhysxSchemaPhysxCameraDroneAPI
    const TfToken physxDroneCameraMaxDistance;
    /// @brief "physxDroneCamera:maxSpeed"
    ///
    /// PhysxSchemaPhysxCameraDroneAPI
    const TfToken physxDroneCameraMaxSpeed;
    /// @brief "physxDroneCamera:positionOffset"
    ///
    /// PhysxSchemaPhysxCameraDroneAPI
    const TfToken physxDroneCameraPositionOffset;
    /// @brief "physxDroneCamera:rotationFilterTimeConstant"
    ///
    /// PhysxSchemaPhysxCameraDroneAPI
    const TfToken physxDroneCameraRotationFilterTimeConstant;
    /// @brief "physxDroneCamera:velocityFilterTimeConstant"
    ///
    /// PhysxSchemaPhysxCameraDroneAPI
    const TfToken physxDroneCameraVelocityFilterTimeConstant;
    /// @brief "physxDroneCamera:verticalVelocityGain"
    ///
    /// PhysxSchemaPhysxCameraDroneAPI
    const TfToken physxDroneCameraVerticalVelocityGain;
    /// @brief "physxFollowCamera:cameraPositionTimeConstant"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraCameraPositionTimeConstant;
    /// @brief "physxFollowCamera:followMaxDistance"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraFollowMaxDistance;
    /// @brief "physxFollowCamera:followMaxSpeed"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraFollowMaxSpeed;
    /// @brief "physxFollowCamera:followMinDistance"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraFollowMinDistance;
    /// @brief "physxFollowCamera:followMinSpeed"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraFollowMinSpeed;
    /// @brief "physxFollowCamera:followTurnRateGain"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraFollowTurnRateGain;
    /// @brief "physxFollowCamera:lookAheadMaxSpeed"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraLookAheadMaxSpeed;
    /// @brief "physxFollowCamera:lookAheadMinDistance"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraLookAheadMinDistance;
    /// @brief "physxFollowCamera:lookAheadMinSpeed"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraLookAheadMinSpeed;
    /// @brief "physxFollowCamera:lookAheadTurnRateGain"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraLookAheadTurnRateGain;
    /// @brief "physxFollowCamera:lookPositionHeight"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraLookPositionHeight;
    /// @brief "physxFollowCamera:lookPositionTimeConstant"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraLookPositionTimeConstant;
    /// @brief "physxFollowCamera:pitchAngle"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraPitchAngle;
    /// @brief "physxFollowCamera:pitchAngleTimeConstant"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraPitchAngleTimeConstant;
    /// @brief "physxFollowCamera:positionOffset"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraPositionOffset;
    /// @brief "physxFollowCamera:slowPitchAngleSpeed"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraSlowPitchAngleSpeed;
    /// @brief "physxFollowCamera:slowSpeedPitchAngleScale"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraSlowSpeedPitchAngleScale;
    /// @brief "physxFollowCamera:velocityNormalMinSpeed"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraVelocityNormalMinSpeed;
    /// @brief "physxFollowCamera:yawAngle"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraYawAngle;
    /// @brief "physxFollowCamera:yawRateTimeConstant"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowCameraYawRateTimeConstant;
    /// @brief "physxFollowFollowCamera:lookAheadMaxDistance"
    ///
    /// PhysxSchemaPhysxCameraFollowAPI
    const TfToken physxFollowFollowCameraLookAheadMaxDistance;
    /// @brief "physxFollowLookCamera:downHillGroundAngle"
    ///
    /// PhysxSchemaPhysxCameraFollowLookAPI
    const TfToken physxFollowLookCameraDownHillGroundAngle;
    /// @brief "physxFollowLookCamera:downHillGroundPitch"
    ///
    /// PhysxSchemaPhysxCameraFollowLookAPI
    const TfToken physxFollowLookCameraDownHillGroundPitch;
    /// @brief "physxFollowLookCamera:followReverseDistance"
    ///
    /// PhysxSchemaPhysxCameraFollowLookAPI
    const TfToken physxFollowLookCameraFollowReverseDistance;
    /// @brief "physxFollowLookCamera:followReverseSpeed"
    ///
    /// PhysxSchemaPhysxCameraFollowLookAPI
    const TfToken physxFollowLookCameraFollowReverseSpeed;
    /// @brief "physxFollowLookCamera:upHillGroundAngle"
    ///
    /// PhysxSchemaPhysxCameraFollowLookAPI
    const TfToken physxFollowLookCameraUpHillGroundAngle;
    /// @brief "physxFollowLookCamera:upHillGroundPitch"
    ///
    /// PhysxSchemaPhysxCameraFollowLookAPI
    const TfToken physxFollowLookCameraUpHillGroundPitch;
    /// @brief "physxFollowLookCamera:velocityBlendTimeConstant"
    ///
    /// PhysxSchemaPhysxCameraFollowLookAPI
    const TfToken physxFollowLookCameraVelocityBlendTimeConstant;
    /// @brief "physxForce:force"
    ///
    /// PhysxSchemaPhysxForceAPI
    const TfToken physxForceForce;
    /// @brief "physxForce:forceEnabled"
    ///
    /// PhysxSchemaPhysxForceAPI
    const TfToken physxForceForceEnabled;
    /// @brief "physxForce:mode"
    ///
    /// PhysxSchemaPhysxForceAPI
    const TfToken physxForceMode;
    /// @brief "physxForce:torque"
    ///
    /// PhysxSchemaPhysxForceAPI
    const TfToken physxForceTorque;
    /// @brief "physxForce:worldFrameEnabled"
    ///
    /// PhysxSchemaPhysxForceAPI
    const TfToken physxForceWorldFrameEnabled;
    /// @brief "physxHair:externalCollision"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairExternalCollision;
    /// @brief "physxHair:globalShapeComplianceAtRoot"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairGlobalShapeComplianceAtRoot;
    /// @brief "physxHair:globalShapeComplianceStrandAttenuation"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairGlobalShapeComplianceStrandAttenuation;
    /// @brief "physxHair:interHairRepulsion"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairInterHairRepulsion;
    /// @brief "physxHair:localShapeMatchingCompliance"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairLocalShapeMatchingCompliance;
    /// @brief "physxHair:localShapeMatchingGroupOverlap"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairLocalShapeMatchingGroupOverlap;
    /// @brief "physxHair:localShapeMatchingGroupSize"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairLocalShapeMatchingGroupSize;
    /// @brief "physxHair:localShapeMatchingLinearStretching"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairLocalShapeMatchingLinearStretching;
    /// @brief "physxHairMaterial:contactOffset"
    ///
    /// PhysxSchemaPhysxHairMaterialAPI
    const TfToken physxHairMaterialContactOffset;
    /// @brief "physxHairMaterial:contactOffsetMultiplier"
    ///
    /// PhysxSchemaPhysxHairMaterialAPI
    const TfToken physxHairMaterialContactOffsetMultiplier;
    /// @brief "physxHairMaterial:curveBendStiffness"
    ///
    /// PhysxSchemaPhysxHairMaterialAPI
    const TfToken physxHairMaterialCurveBendStiffness;
    /// @brief "physxHairMaterial:curveThickness"
    ///
    /// PhysxSchemaPhysxHairMaterialAPI
    const TfToken physxHairMaterialCurveThickness;
    /// @brief "physxHairMaterial:density"
    ///
    /// PhysxSchemaPhysxHairMaterialAPI
    const TfToken physxHairMaterialDensity;
    /// @brief "physxHairMaterial:dynamicFriction"
    ///
    /// PhysxSchemaPhysxHairMaterialAPI
    const TfToken physxHairMaterialDynamicFriction;
    /// @brief "physxHairMaterial:youngsModulus"
    ///
    /// PhysxSchemaPhysxHairMaterialAPI
    const TfToken physxHairMaterialYoungsModulus;
    /// @brief "physxHair:segmentLength"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairSegmentLength;
    /// @brief "physxHair:twosidedAttachment"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairTwosidedAttachment;
    /// @brief "physxHair:velSmoothing"
    ///
    /// PhysxSchemaPhysxHairAPI
    const TfToken physxHairVelSmoothing;
    /// @brief "physxJoint:armature"
    ///
    /// PhysxSchemaPhysxJointAPI
    const TfToken physxJointArmature;
    /// @brief "physxJoint:enableProjection"
    ///
    /// PhysxSchemaPhysxJointAPI
    const TfToken physxJointEnableProjection;
    /// @brief "physxJoint:jointFriction"
    ///
    /// PhysxSchemaPhysxJointAPI
    const TfToken physxJointJointFriction;
    /// @brief "physxJoint:maxJointVelocity"
    ///
    /// PhysxSchemaPhysxJointAPI
    const TfToken physxJointMaxJointVelocity;
    /// @brief "physxLimit"
    ///
    /// Property namespace prefix for the PhysxSchemaPhysxLimitAPI schema.
    const TfToken physxLimit;
    /// @brief "physxMaterial:compliantContactDamping"
    ///
    /// PhysxSchemaPhysxMaterialAPI
    const TfToken physxMaterialCompliantContactDamping;
    /// @brief "physxMaterial:compliantContactStiffness"
    ///
    /// PhysxSchemaPhysxMaterialAPI
    const TfToken physxMaterialCompliantContactStiffness;
    /// @brief "physxMaterial:frictionCombineMode"
    ///
    /// PhysxSchemaPhysxMaterialAPI
    const TfToken physxMaterialFrictionCombineMode;
    /// @brief "physxMaterial:improvePatchFriction"
    ///
    /// PhysxSchemaPhysxMaterialAPI
    const TfToken physxMaterialImprovePatchFriction;
    /// @brief "physxMaterial:restitutionCombineMode"
    ///
    /// PhysxSchemaPhysxMaterialAPI
    const TfToken physxMaterialRestitutionCombineMode;
    /// @brief "physxParticleAnisotropy:max"
    ///
    /// PhysxSchemaPhysxParticleAnisotropyAPI
    const TfToken physxParticleAnisotropyMax;
    /// @brief "physxParticleAnisotropy:min"
    ///
    /// PhysxSchemaPhysxParticleAnisotropyAPI
    const TfToken physxParticleAnisotropyMin;
    /// @brief "physxParticleAnisotropy:particleAnisotropyEnabled"
    ///
    /// PhysxSchemaPhysxParticleAnisotropyAPI
    const TfToken physxParticleAnisotropyParticleAnisotropyEnabled;
    /// @brief "physxParticleAnisotropy:scale"
    ///
    /// PhysxSchemaPhysxParticleAnisotropyAPI
    const TfToken physxParticleAnisotropyScale;
    /// @brief "physxParticle:fluid"
    ///
    /// PhysxSchemaPhysxParticleSetAPI
    const TfToken physxParticleFluid;
    /// @brief "physxParticleIsosurface:gridFilteringPasses"
    ///
    /// PhysxSchemaPhysxParticleIsosurfaceAPI
    const TfToken physxParticleIsosurfaceGridFilteringPasses;
    /// @brief "physxParticleIsosurface:gridSmoothingRadius"
    ///
    /// PhysxSchemaPhysxParticleIsosurfaceAPI
    const TfToken physxParticleIsosurfaceGridSmoothingRadius;
    /// @brief "physxParticleIsosurface:gridSpacing"
    ///
    /// PhysxSchemaPhysxParticleIsosurfaceAPI
    const TfToken physxParticleIsosurfaceGridSpacing;
    /// @brief "physxParticleIsosurface:isosurfaceEnabled"
    ///
    /// PhysxSchemaPhysxParticleIsosurfaceAPI
    const TfToken physxParticleIsosurfaceIsosurfaceEnabled;
    /// @brief "physxParticleIsosurface:maxSubgrids"
    ///
    /// PhysxSchemaPhysxParticleIsosurfaceAPI
    const TfToken physxParticleIsosurfaceMaxSubgrids;
    /// @brief "physxParticleIsosurface:maxTriangles"
    ///
    /// PhysxSchemaPhysxParticleIsosurfaceAPI
    const TfToken physxParticleIsosurfaceMaxTriangles;
    /// @brief "physxParticleIsosurface:maxVertices"
    ///
    /// PhysxSchemaPhysxParticleIsosurfaceAPI
    const TfToken physxParticleIsosurfaceMaxVertices;
    /// @brief "physxParticleIsosurface:numMeshNormalSmoothingPasses"
    ///
    /// PhysxSchemaPhysxParticleIsosurfaceAPI
    const TfToken physxParticleIsosurfaceNumMeshNormalSmoothingPasses;
    /// @brief "physxParticleIsosurface:numMeshSmoothingPasses"
    ///
    /// PhysxSchemaPhysxParticleIsosurfaceAPI
    const TfToken physxParticleIsosurfaceNumMeshSmoothingPasses;
    /// @brief "physxParticleIsosurface:surfaceDistance"
    ///
    /// PhysxSchemaPhysxParticleIsosurfaceAPI
    const TfToken physxParticleIsosurfaceSurfaceDistance;
    /// @brief "physxParticle:particleEnabled"
    ///
    /// PhysxSchemaPhysxParticleAPI
    const TfToken physxParticleParticleEnabled;
    /// @brief "physxParticle:particleGroup"
    ///
    /// PhysxSchemaPhysxParticleAPI
    const TfToken physxParticleParticleGroup;
    /// @brief "physxParticle:particleSystem"
    ///
    /// PhysxSchemaPhysxParticleAPI
    const TfToken physxParticleParticleSystem;
    /// @brief "physxParticle:pressure"
    ///
    /// PhysxSchemaPhysxParticleClothAPI
    const TfToken physxParticlePressure;
    /// @brief "physxParticle:restPoints"
    ///
    /// PhysxSchemaPhysxParticleClothAPI
    const TfToken physxParticleRestPoints;
    /// @brief "physxParticleSampling:maxSamples"
    ///
    /// PhysxSchemaPhysxParticleSamplingAPI
    const TfToken physxParticleSamplingMaxSamples;
    /// @brief "physxParticleSampling:particles"
    ///
    /// PhysxSchemaPhysxParticleSamplingAPI
    const TfToken physxParticleSamplingParticles;
    /// @brief "physxParticleSampling:samplingDistance"
    ///
    /// PhysxSchemaPhysxParticleSamplingAPI
    const TfToken physxParticleSamplingSamplingDistance;
    /// @brief "physxParticleSampling:volume"
    ///
    /// PhysxSchemaPhysxParticleSamplingAPI
    const TfToken physxParticleSamplingVolume;
    /// @brief "physxParticle:selfCollision"
    ///
    /// PhysxSchemaPhysxParticleAPI
    const TfToken physxParticleSelfCollision;
    /// @brief "physxParticle:selfCollisionFilter"
    ///
    /// PhysxSchemaPhysxParticleClothAPI
    const TfToken physxParticleSelfCollisionFilter;
    /// @brief "physxParticle:simulationPoints"
    ///
    /// PhysxSchemaPhysxParticleSetAPI
    const TfToken physxParticleSimulationPoints;
    /// @brief "physxParticleSmoothing:particleSmoothingEnabled"
    ///
    /// PhysxSchemaPhysxParticleSmoothingAPI
    const TfToken physxParticleSmoothingParticleSmoothingEnabled;
    /// @brief "physxParticleSmoothing:strength"
    ///
    /// PhysxSchemaPhysxParticleSmoothingAPI
    const TfToken physxParticleSmoothingStrength;
    /// @brief "physxParticle:springDampings"
    ///
    /// PhysxSchemaPhysxParticleClothAPI
    const TfToken physxParticleSpringDampings;
    /// @brief "physxParticle:springIndices"
    ///
    /// PhysxSchemaPhysxParticleClothAPI
    const TfToken physxParticleSpringIndices;
    /// @brief "physxParticle:springRestLengths"
    ///
    /// PhysxSchemaPhysxParticleClothAPI
    const TfToken physxParticleSpringRestLengths;
    /// @brief "physxParticle:springStiffnesses"
    ///
    /// PhysxSchemaPhysxParticleClothAPI
    const TfToken physxParticleSpringStiffnesses;
    /// @brief "physxPBDMaterial:adhesion"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialAdhesion;
    /// @brief "physxPBDMaterial:adhesionOffsetScale"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialAdhesionOffsetScale;
    /// @brief "physxPBDMaterial:cflCoefficient"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialCflCoefficient;
    /// @brief "physxPBDMaterial:cohesion"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialCohesion;
    /// @brief "physxPBDMaterial:damping"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialDamping;
    /// @brief "physxPBDMaterial:density"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialDensity;
    /// @brief "physxPBDMaterial:drag"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialDrag;
    /// @brief "physxPBDMaterial:friction"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialFriction;
    /// @brief "physxPBDMaterial:gravityScale"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialGravityScale;
    /// @brief "physxPBDMaterial:lift"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialLift;
    /// @brief "physxPBDMaterial:particleAdhesionScale"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialParticleAdhesionScale;
    /// @brief "physxPBDMaterial:particleFrictionScale"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialParticleFrictionScale;
    /// @brief "physxPBDMaterial:surfaceTension"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialSurfaceTension;
    /// @brief "physxPBDMaterial:viscosity"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialViscosity;
    /// @brief "physxPBDMaterial:vorticityConfinement"
    ///
    /// PhysxSchemaPhysxPBDMaterialAPI
    const TfToken physxPBDMaterialVorticityConfinement;
    /// @brief "physxPhysicsDistanceJoint:springDamping"
    ///
    /// PhysxSchemaPhysxPhysicsDistanceJointAPI
    const TfToken physxPhysicsDistanceJointSpringDamping;
    /// @brief "physxPhysicsDistanceJoint:springEnabled"
    ///
    /// PhysxSchemaPhysxPhysicsDistanceJointAPI
    const TfToken physxPhysicsDistanceJointSpringEnabled;
    /// @brief "physxPhysicsDistanceJoint:springStiffness"
    ///
    /// PhysxSchemaPhysxPhysicsDistanceJointAPI
    const TfToken physxPhysicsDistanceJointSpringStiffness;
    /// @brief "physxRigidBody:angularDamping"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyAngularDamping;
    /// @brief "physxRigidBody:cfmScale"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyCfmScale;
    /// @brief "physxRigidBody:contactSlopCoefficient"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyContactSlopCoefficient;
    /// @brief "physxRigidBody:disableGravity"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyDisableGravity;
    /// @brief "physxRigidBody:enableCCD"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyEnableCCD;
    /// @brief "physxRigidBody:enableGyroscopicForces"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyEnableGyroscopicForces;
    /// @brief "physxRigidBody:enableSpeculativeCCD"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyEnableSpeculativeCCD;
    /// @brief "physxRigidBody:linearDamping"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyLinearDamping;
    /// @brief "physxRigidBody:lockedPosAxis"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyLockedPosAxis;
    /// @brief "physxRigidBody:lockedRotAxis"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyLockedRotAxis;
    /// @brief "physxRigidBody:maxAngularVelocity"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyMaxAngularVelocity;
    /// @brief "physxRigidBody:maxContactImpulse"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyMaxContactImpulse;
    /// @brief "physxRigidBody:maxDepenetrationVelocity"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyMaxDepenetrationVelocity;
    /// @brief "physxRigidBody:maxLinearVelocity"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyMaxLinearVelocity;
    /// @brief "physxRigidBody:retainAccelerations"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyRetainAccelerations;
    /// @brief "physxRigidBody:sleepThreshold"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodySleepThreshold;
    /// @brief "physxRigidBody:solveContact"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodySolveContact;
    /// @brief "physxRigidBody:solverPositionIterationCount"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodySolverPositionIterationCount;
    /// @brief "physxRigidBody:solverVelocityIterationCount"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodySolverVelocityIterationCount;
    /// @brief "physxRigidBody:stabilizationThreshold"
    ///
    /// PhysxSchemaPhysxRigidBodyAPI
    const TfToken physxRigidBodyStabilizationThreshold;
    /// @brief "physxScene:bounceThreshold"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneBounceThreshold;
    /// @brief "physxScene:broadphaseType"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneBroadphaseType;
    /// @brief "physxScene:collisionSystem"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneCollisionSystem;
    /// @brief "physxScene:enableCCD"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneEnableCCD;
    /// @brief "physxScene:enableEnhancedDeterminism"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneEnableEnhancedDeterminism;
    /// @brief "physxScene:enableExternalForcesEveryIteration"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneEnableExternalForcesEveryIteration;
    /// @brief "physxScene:enableGPUDynamics"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneEnableGPUDynamics;
    /// @brief "physxScene:enableSceneQuerySupport"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneEnableSceneQuerySupport;
    /// @brief "physxScene:enableStabilization"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneEnableStabilization;
    /// @brief "physxScene:frictionCorrelationDistance"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneFrictionCorrelationDistance;
    /// @brief "physxScene:frictionOffsetThreshold"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneFrictionOffsetThreshold;
    /// @brief "physxScene:frictionType"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneFrictionType;
    /// @brief "physxScene:gpuCollisionStackSize"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuCollisionStackSize;
    /// @brief "physxScene:gpuFoundLostAggregatePairsCapacity"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuFoundLostAggregatePairsCapacity;
    /// @brief "physxScene:gpuFoundLostPairsCapacity"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuFoundLostPairsCapacity;
    /// @brief "physxScene:gpuHeapCapacity"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuHeapCapacity;
    /// @brief "physxScene:gpuMaxDeformableSurfaceContacts"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuMaxDeformableSurfaceContacts;
    /// @brief "physxScene:gpuMaxHairContacts"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuMaxHairContacts;
    /// @brief "physxScene:gpuMaxNumPartitions"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuMaxNumPartitions;
    /// @brief "physxScene:gpuMaxParticleContacts"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuMaxParticleContacts;
    /// @brief "physxScene:gpuMaxRigidContactCount"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuMaxRigidContactCount;
    /// @brief "physxScene:gpuMaxRigidPatchCount"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuMaxRigidPatchCount;
    /// @brief "physxScene:gpuMaxSoftBodyContacts"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuMaxSoftBodyContacts;
    /// @brief "physxScene:gpuTempBufferCapacity"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuTempBufferCapacity;
    /// @brief "physxScene:gpuTotalAggregatePairsCapacity"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneGpuTotalAggregatePairsCapacity;
    /// @brief "physxScene:invertCollisionGroupFilter"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneInvertCollisionGroupFilter;
    /// @brief "physxScene:maxBiasCoefficient"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneMaxBiasCoefficient;
    /// @brief "physxScene:maxPositionIterationCount"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneMaxPositionIterationCount;
    /// @brief "physxScene:maxVelocityIterationCount"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneMaxVelocityIterationCount;
    /// @brief "physxScene:minPositionIterationCount"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneMinPositionIterationCount;
    /// @brief "physxScene:minVelocityIterationCount"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneMinVelocityIterationCount;
    /// @brief "physxSceneQuasistatic:enableQuasistatic"
    ///
    /// PhysxSchemaPhysxSceneQuasistaticAPI
    const TfToken physxSceneQuasistaticEnableQuasistatic;
    /// @brief "physxScene:reportKinematicKinematicPairs"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneReportKinematicKinematicPairs;
    /// @brief "physxScene:reportKinematicStaticPairs"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneReportKinematicStaticPairs;
    /// @brief "physxScene:solverType"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneSolverType;
    /// @brief "physxScene:timeStepsPerSecond"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneTimeStepsPerSecond;
    /// @brief "physxScene:updateType"
    ///
    /// PhysxSchemaPhysxSceneAPI
    const TfToken physxSceneUpdateType;
    /// @brief "physxSDFMeshCollision:sdfBitsPerSubgridPixel"
    ///
    /// PhysxSchemaPhysxSDFMeshCollisionAPI
    const TfToken physxSDFMeshCollisionSdfBitsPerSubgridPixel;
    /// @brief "physxSDFMeshCollision:sdfEnableRemeshing"
    ///
    /// PhysxSchemaPhysxSDFMeshCollisionAPI
    const TfToken physxSDFMeshCollisionSdfEnableRemeshing;
    /// @brief "physxSDFMeshCollision:sdfMargin"
    ///
    /// PhysxSchemaPhysxSDFMeshCollisionAPI
    const TfToken physxSDFMeshCollisionSdfMargin;
    /// @brief "physxSDFMeshCollision:sdfNarrowBandThickness"
    ///
    /// PhysxSchemaPhysxSDFMeshCollisionAPI
    const TfToken physxSDFMeshCollisionSdfNarrowBandThickness;
    /// @brief "physxSDFMeshCollision:sdfResolution"
    ///
    /// PhysxSchemaPhysxSDFMeshCollisionAPI
    const TfToken physxSDFMeshCollisionSdfResolution;
    /// @brief "physxSDFMeshCollision:sdfSubgridResolution"
    ///
    /// PhysxSchemaPhysxSDFMeshCollisionAPI
    const TfToken physxSDFMeshCollisionSdfSubgridResolution;
    /// @brief "physxSDFMeshCollision:sdfTriangleCountReductionFactor"
    ///
    /// PhysxSchemaPhysxSDFMeshCollisionAPI
    const TfToken physxSDFMeshCollisionSdfTriangleCountReductionFactor;
    /// @brief "physxSphereFillCollision:fillMode"
    ///
    /// PhysxSchemaPhysxSphereFillCollisionAPI
    const TfToken physxSphereFillCollisionFillMode;
    /// @brief "physxSphereFillCollision:maxSpheres"
    ///
    /// PhysxSchemaPhysxSphereFillCollisionAPI
    const TfToken physxSphereFillCollisionMaxSpheres;
    /// @brief "physxSphereFillCollision:seedCount"
    ///
    /// PhysxSchemaPhysxSphereFillCollisionAPI
    const TfToken physxSphereFillCollisionSeedCount;
    /// @brief "physxSphereFillCollision:voxelResolution"
    ///
    /// PhysxSchemaPhysxSphereFillCollisionAPI
    const TfToken physxSphereFillCollisionVoxelResolution;
    /// @brief "physxSurfaceVelocity:surfaceAngularVelocity"
    ///
    /// PhysxSchemaPhysxSurfaceVelocityAPI
    const TfToken physxSurfaceVelocitySurfaceAngularVelocity;
    /// @brief "physxSurfaceVelocity:surfaceVelocity"
    ///
    /// PhysxSchemaPhysxSurfaceVelocityAPI
    const TfToken physxSurfaceVelocitySurfaceVelocity;
    /// @brief "physxSurfaceVelocity:surfaceVelocityEnabled"
    ///
    /// PhysxSchemaPhysxSurfaceVelocityAPI
    const TfToken physxSurfaceVelocitySurfaceVelocityEnabled;
    /// @brief "physxSurfaceVelocity:surfaceVelocityLocalSpace"
    ///
    /// PhysxSchemaPhysxSurfaceVelocityAPI
    const TfToken physxSurfaceVelocitySurfaceVelocityLocalSpace;
    /// @brief "physxTendon"
    ///
    /// Property namespace prefix for the PhysxSchemaPhysxTendonAttachmentLeafAPI schema., Property namespace prefix for
    /// the PhysxSchemaPhysxTendonAttachmentRootAPI schema., Property namespace prefix for the
    /// PhysxSchemaPhysxTendonAttachmentAPI schema., Property namespace prefix for the PhysxSchemaPhysxTendonAxisRootAPI
    /// schema., Property namespace prefix for the PhysxSchemaPhysxTendonAxisAPI schema.
    const TfToken physxTendon;
    /// @brief "physxTriangleMeshCollision:weldTolerance"
    ///
    /// PhysxSchemaPhysxTriangleMeshCollisionAPI
    const TfToken physxTriangleMeshCollisionWeldTolerance;
    /// @brief "physxTriangleMeshSimplificationCollision:metric"
    ///
    /// PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI
    const TfToken physxTriangleMeshSimplificationCollisionMetric;
    /// @brief "physxTriangleMeshSimplificationCollision:weldTolerance"
    ///
    /// PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI
    const TfToken physxTriangleMeshSimplificationCollisionWeldTolerance;
    /// @brief "physxTrigger:enterScriptType"
    ///
    /// PhysxSchemaPhysxTriggerAPI
    const TfToken physxTriggerEnterScriptType;
    /// @brief "physxTrigger:leaveScriptType"
    ///
    /// PhysxSchemaPhysxTriggerAPI
    const TfToken physxTriggerLeaveScriptType;
    /// @brief "physxTrigger:onEnterScript"
    ///
    /// PhysxSchemaPhysxTriggerAPI
    const TfToken physxTriggerOnEnterScript;
    /// @brief "physxTrigger:onLeaveScript"
    ///
    /// PhysxSchemaPhysxTriggerAPI
    const TfToken physxTriggerOnLeaveScript;
    /// @brief "physxTrigger:triggeredCollisions"
    ///
    /// PhysxSchemaPhysxTriggerStateAPI
    const TfToken physxTriggerTriggeredCollisions;
    /// @brief "physxVehicleAckermannSteering:maxSteerAngle"
    ///
    /// PhysxSchemaPhysxVehicleAckermannSteeringAPI
    const TfToken physxVehicleAckermannSteeringMaxSteerAngle;
    /// @brief "physxVehicleAckermannSteering:strength"
    ///
    /// PhysxSchemaPhysxVehicleAckermannSteeringAPI
    const TfToken physxVehicleAckermannSteeringStrength;
    /// @brief "physxVehicleAckermannSteering:trackWidth"
    ///
    /// PhysxSchemaPhysxVehicleAckermannSteeringAPI
    const TfToken physxVehicleAckermannSteeringTrackWidth;
    /// @brief "physxVehicleAckermannSteering:wheel0"
    ///
    /// PhysxSchemaPhysxVehicleAckermannSteeringAPI
    const TfToken physxVehicleAckermannSteeringWheel0;
    /// @brief "physxVehicleAckermannSteering:wheel1"
    ///
    /// PhysxSchemaPhysxVehicleAckermannSteeringAPI
    const TfToken physxVehicleAckermannSteeringWheel1;
    /// @brief "physxVehicleAckermannSteering:wheelBase"
    ///
    /// PhysxSchemaPhysxVehicleAckermannSteeringAPI
    const TfToken physxVehicleAckermannSteeringWheelBase;
    /// @brief "physxVehicleAutoGearBox:downRatios"
    ///
    /// PhysxSchemaPhysxVehicleAutoGearBoxAPI
    const TfToken physxVehicleAutoGearBoxDownRatios;
    /// @brief "physxVehicleAutoGearBox:latency"
    ///
    /// PhysxSchemaPhysxVehicleAutoGearBoxAPI
    const TfToken physxVehicleAutoGearBoxLatency;
    /// @brief "physxVehicleAutoGearBox:upRatios"
    ///
    /// PhysxSchemaPhysxVehicleAutoGearBoxAPI
    const TfToken physxVehicleAutoGearBoxUpRatios;
    /// @brief "physxVehicleBrakes"
    ///
    /// Property namespace prefix for the PhysxSchemaPhysxVehicleBrakesAPI schema.
    const TfToken physxVehicleBrakes;
    /// @brief "physxVehicleClutch:strength"
    ///
    /// PhysxSchemaPhysxVehicleClutchAPI
    const TfToken physxVehicleClutchStrength;
    /// @brief "physxVehicleContext:forwardAxis"
    ///
    /// PhysxSchemaPhysxVehicleContextAPI
    const TfToken physxVehicleContextForwardAxis;
    /// @brief "physxVehicleContext:longitudinalAxis"
    ///
    /// PhysxSchemaPhysxVehicleContextAPI
    const TfToken physxVehicleContextLongitudinalAxis;
    /// @brief "physxVehicleContext:upAxis"
    ///
    /// PhysxSchemaPhysxVehicleContextAPI
    const TfToken physxVehicleContextUpAxis;
    /// @brief "physxVehicleContext:updateMode"
    ///
    /// PhysxSchemaPhysxVehicleContextAPI
    const TfToken physxVehicleContextUpdateMode;
    /// @brief "physxVehicleContext:verticalAxis"
    ///
    /// PhysxSchemaPhysxVehicleContextAPI
    const TfToken physxVehicleContextVerticalAxis;
    /// @brief "physxVehicleController:accelerator"
    ///
    /// PhysxSchemaPhysxVehicleControllerAPI
    const TfToken physxVehicleControllerAccelerator;
    /// @brief "physxVehicleController:brake"
    ///
    /// PhysxSchemaPhysxVehicleControllerAPI
    const TfToken physxVehicleControllerBrake;
    /// @brief "physxVehicleController:brake0"
    ///
    /// PhysxSchemaPhysxVehicleControllerAPI
    const TfToken physxVehicleControllerBrake0;
    /// @brief "physxVehicleController:brake1"
    ///
    /// PhysxSchemaPhysxVehicleControllerAPI
    const TfToken physxVehicleControllerBrake1;
    /// @brief "physxVehicleController:handbrake"
    ///
    /// PhysxSchemaPhysxVehicleControllerAPI
    const TfToken physxVehicleControllerHandbrake;
    /// @brief "physxVehicleController:steer"
    ///
    /// PhysxSchemaPhysxVehicleControllerAPI
    const TfToken physxVehicleControllerSteer;
    /// @brief "physxVehicleController:steerLeft"
    ///
    /// PhysxSchemaPhysxVehicleControllerAPI
    const TfToken physxVehicleControllerSteerLeft;
    /// @brief "physxVehicleController:steerRight"
    ///
    /// PhysxSchemaPhysxVehicleControllerAPI
    const TfToken physxVehicleControllerSteerRight;
    /// @brief "physxVehicleController:targetGear"
    ///
    /// PhysxSchemaPhysxVehicleControllerAPI
    const TfToken physxVehicleControllerTargetGear;
    /// @brief "physxVehicle:drive"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleDrive;
    /// @brief "physxVehicleDriveBasic:peakTorque"
    ///
    /// PhysxSchemaPhysxVehicleDriveBasicAPI
    const TfToken physxVehicleDriveBasicPeakTorque;
    /// @brief "physxVehicleDriveStandard:autoGearBox"
    ///
    /// PhysxSchemaPhysxVehicleDriveStandardAPI
    const TfToken physxVehicleDriveStandardAutoGearBox;
    /// @brief "physxVehicleDriveStandard:clutch"
    ///
    /// PhysxSchemaPhysxVehicleDriveStandardAPI
    const TfToken physxVehicleDriveStandardClutch;
    /// @brief "physxVehicleDriveStandard:engine"
    ///
    /// PhysxSchemaPhysxVehicleDriveStandardAPI
    const TfToken physxVehicleDriveStandardEngine;
    /// @brief "physxVehicleDriveStandard:gears"
    ///
    /// PhysxSchemaPhysxVehicleDriveStandardAPI
    const TfToken physxVehicleDriveStandardGears;
    /// @brief "physxVehicleEngine:dampingRateFullThrottle"
    ///
    /// PhysxSchemaPhysxVehicleEngineAPI
    const TfToken physxVehicleEngineDampingRateFullThrottle;
    /// @brief "physxVehicleEngine:dampingRateZeroThrottleClutchDisengaged"
    ///
    /// PhysxSchemaPhysxVehicleEngineAPI
    const TfToken physxVehicleEngineDampingRateZeroThrottleClutchDisengaged;
    /// @brief "physxVehicleEngine:dampingRateZeroThrottleClutchEngaged"
    ///
    /// PhysxSchemaPhysxVehicleEngineAPI
    const TfToken physxVehicleEngineDampingRateZeroThrottleClutchEngaged;
    /// @brief "physxVehicleEngine:idleRotationSpeed"
    ///
    /// PhysxSchemaPhysxVehicleEngineAPI
    const TfToken physxVehicleEngineIdleRotationSpeed;
    /// @brief "physxVehicleEngine:maxRotationSpeed"
    ///
    /// PhysxSchemaPhysxVehicleEngineAPI
    const TfToken physxVehicleEngineMaxRotationSpeed;
    /// @brief "physxVehicleEngine:moi"
    ///
    /// PhysxSchemaPhysxVehicleEngineAPI
    const TfToken physxVehicleEngineMoi;
    /// @brief "physxVehicleEngine:peakTorque"
    ///
    /// PhysxSchemaPhysxVehicleEngineAPI
    const TfToken physxVehicleEnginePeakTorque;
    /// @brief "physxVehicleEngine:torqueCurve"
    ///
    /// PhysxSchemaPhysxVehicleEngineAPI
    const TfToken physxVehicleEngineTorqueCurve;
    /// @brief "physxVehicleGears:ratios"
    ///
    /// PhysxSchemaPhysxVehicleGearsAPI
    const TfToken physxVehicleGearsRatios;
    /// @brief "physxVehicleGears:ratioScale"
    ///
    /// PhysxSchemaPhysxVehicleGearsAPI
    const TfToken physxVehicleGearsRatioScale;
    /// @brief "physxVehicleGears:switchTime"
    ///
    /// PhysxSchemaPhysxVehicleGearsAPI
    const TfToken physxVehicleGearsSwitchTime;
    /// @brief "physxVehicle:highForwardSpeedSubStepCount"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleHighForwardSpeedSubStepCount;
    /// @brief "physxVehicle:lateralStickyTireDamping"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleLateralStickyTireDamping;
    /// @brief "physxVehicle:lateralStickyTireThresholdSpeed"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleLateralStickyTireThresholdSpeed;
    /// @brief "physxVehicle:lateralStickyTireThresholdTime"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleLateralStickyTireThresholdTime;
    /// @brief "physxVehicle:limitSuspensionExpansionVelocity"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleLimitSuspensionExpansionVelocity;
    /// @brief "physxVehicle:longitudinalStickyTireDamping"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleLongitudinalStickyTireDamping;
    /// @brief "physxVehicle:longitudinalStickyTireThresholdSpeed"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleLongitudinalStickyTireThresholdSpeed;
    /// @brief "physxVehicle:longitudinalStickyTireThresholdTime"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleLongitudinalStickyTireThresholdTime;
    /// @brief "physxVehicle:lowForwardSpeedSubStepCount"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleLowForwardSpeedSubStepCount;
    /// @brief "physxVehicle:minActiveLongitudinalSlipDenominator"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleMinActiveLongitudinalSlipDenominator;
    /// @brief "physxVehicle:minLateralSlipDenominator"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleMinLateralSlipDenominator;
    /// @brief "physxVehicle:minLongitudinalSlipDenominator"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleMinLongitudinalSlipDenominator;
    /// @brief "physxVehicle:minPassiveLongitudinalSlipDenominator"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleMinPassiveLongitudinalSlipDenominator;
    /// @brief "physxVehicleMultiWheelDifferential:averageWheelSpeedRatios"
    ///
    /// PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI
    const TfToken physxVehicleMultiWheelDifferentialAverageWheelSpeedRatios;
    /// @brief "physxVehicleMultiWheelDifferential:torqueRatios"
    ///
    /// PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI
    const TfToken physxVehicleMultiWheelDifferentialTorqueRatios;
    /// @brief "physxVehicleMultiWheelDifferential:wheels"
    ///
    /// PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI
    const TfToken physxVehicleMultiWheelDifferentialWheels;
    /// @brief "physxVehicleNCR"
    ///
    /// Property namespace prefix for the PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI schema.
    const TfToken physxVehicleNCR;
    /// @brief "physxVehicleSteering:angleMultipliers"
    ///
    /// PhysxSchemaPhysxVehicleSteeringAPI
    const TfToken physxVehicleSteeringAngleMultipliers;
    /// @brief "physxVehicleSteering:maxSteerAngle"
    ///
    /// PhysxSchemaPhysxVehicleSteeringAPI
    const TfToken physxVehicleSteeringMaxSteerAngle;
    /// @brief "physxVehicleSteering:wheels"
    ///
    /// PhysxSchemaPhysxVehicleSteeringAPI
    const TfToken physxVehicleSteeringWheels;
    /// @brief "physxVehicle:subStepThresholdLongitudinalSpeed"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleSubStepThresholdLongitudinalSpeed;
    /// @brief "physxVehicleSuspension:camberAtMaxCompression"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionAPI
    const TfToken physxVehicleSuspensionCamberAtMaxCompression;
    /// @brief "physxVehicleSuspension:camberAtMaxDroop"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionAPI
    const TfToken physxVehicleSuspensionCamberAtMaxDroop;
    /// @brief "physxVehicleSuspension:camberAtRest"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionAPI
    const TfToken physxVehicleSuspensionCamberAtRest;
    /// @brief "physxVehicleSuspensionCompliance:suspensionForceAppPoint"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionComplianceAPI
    const TfToken physxVehicleSuspensionComplianceSuspensionForceAppPoint;
    /// @brief "physxVehicleSuspensionCompliance:tireForceAppPoint"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionComplianceAPI
    const TfToken physxVehicleSuspensionComplianceTireForceAppPoint;
    /// @brief "physxVehicleSuspensionCompliance:wheelCamberAngle"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionComplianceAPI
    const TfToken physxVehicleSuspensionComplianceWheelCamberAngle;
    /// @brief "physxVehicleSuspensionCompliance:wheelToeAngle"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionComplianceAPI
    const TfToken physxVehicleSuspensionComplianceWheelToeAngle;
    /// @brief "physxVehicle:suspensionLineQueryType"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleSuspensionLineQueryType;
    /// @brief "physxVehicleSuspension:maxCompression"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionAPI
    const TfToken physxVehicleSuspensionMaxCompression;
    /// @brief "physxVehicleSuspension:maxDroop"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionAPI
    const TfToken physxVehicleSuspensionMaxDroop;
    /// @brief "physxVehicleSuspension:springDamperRate"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionAPI
    const TfToken physxVehicleSuspensionSpringDamperRate;
    /// @brief "physxVehicleSuspension:springStrength"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionAPI
    const TfToken physxVehicleSuspensionSpringStrength;
    /// @brief "physxVehicleSuspension:sprungMass"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionAPI
    const TfToken physxVehicleSuspensionSprungMass;
    /// @brief "physxVehicleSuspension:travelDistance"
    ///
    /// PhysxSchemaPhysxVehicleSuspensionAPI
    const TfToken physxVehicleSuspensionTravelDistance;
    /// @brief "physxVehicleTankController:thrust0"
    ///
    /// PhysxSchemaPhysxVehicleTankControllerAPI
    const TfToken physxVehicleTankControllerThrust0;
    /// @brief "physxVehicleTankController:thrust1"
    ///
    /// PhysxSchemaPhysxVehicleTankControllerAPI
    const TfToken physxVehicleTankControllerThrust1;
    /// @brief "physxVehicleTankDifferential:numberOfWheelsPerTrack"
    ///
    /// PhysxSchemaPhysxVehicleTankDifferentialAPI
    const TfToken physxVehicleTankDifferentialNumberOfWheelsPerTrack;
    /// @brief "physxVehicleTankDifferential:thrustIndexPerTrack"
    ///
    /// PhysxSchemaPhysxVehicleTankDifferentialAPI
    const TfToken physxVehicleTankDifferentialThrustIndexPerTrack;
    /// @brief "physxVehicleTankDifferential:trackToWheelIndices"
    ///
    /// PhysxSchemaPhysxVehicleTankDifferentialAPI
    const TfToken physxVehicleTankDifferentialTrackToWheelIndices;
    /// @brief "physxVehicleTankDifferential:wheelIndicesInTrackOrder"
    ///
    /// PhysxSchemaPhysxVehicleTankDifferentialAPI
    const TfToken physxVehicleTankDifferentialWheelIndicesInTrackOrder;
    /// @brief "physxVehicleTire:camberStiffness"
    ///
    /// PhysxSchemaPhysxVehicleTireAPI
    const TfToken physxVehicleTireCamberStiffness;
    /// @brief "physxVehicleTire:camberStiffnessPerUnitGravity"
    ///
    /// PhysxSchemaPhysxVehicleTireAPI
    const TfToken physxVehicleTireCamberStiffnessPerUnitGravity;
    /// @brief "physxVehicleTire:frictionTable"
    ///
    /// PhysxSchemaPhysxVehicleTireAPI
    const TfToken physxVehicleTireFrictionTable;
    /// @brief "physxVehicleTire:frictionVsSlipGraph"
    ///
    /// PhysxSchemaPhysxVehicleTireAPI
    const TfToken physxVehicleTireFrictionVsSlipGraph;
    /// @brief "physxVehicleTire:lateralStiffnessGraph"
    ///
    /// PhysxSchemaPhysxVehicleTireAPI
    const TfToken physxVehicleTireLateralStiffnessGraph;
    /// @brief "physxVehicleTire:latStiffX"
    ///
    /// PhysxSchemaPhysxVehicleTireAPI
    const TfToken physxVehicleTireLatStiffX;
    /// @brief "physxVehicleTire:latStiffY"
    ///
    /// PhysxSchemaPhysxVehicleTireAPI
    const TfToken physxVehicleTireLatStiffY;
    /// @brief "physxVehicleTire:longitudinalStiffness"
    ///
    /// PhysxSchemaPhysxVehicleTireAPI
    const TfToken physxVehicleTireLongitudinalStiffness;
    /// @brief "physxVehicleTire:longitudinalStiffnessPerUnitGravity"
    ///
    /// PhysxSchemaPhysxVehicleTireAPI
    const TfToken physxVehicleTireLongitudinalStiffnessPerUnitGravity;
    /// @brief "physxVehicleTire:restLoad"
    ///
    /// PhysxSchemaPhysxVehicleTireAPI
    const TfToken physxVehicleTireRestLoad;
    /// @brief "physxVehicle:vehicleEnabled"
    ///
    /// PhysxSchemaPhysxVehicleAPI
    const TfToken physxVehicleVehicleEnabled;
    /// @brief "physxVehicleWheelAttachment:collisionGroup"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentCollisionGroup;
    /// @brief "physxVehicleWheelAttachment:driven"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentDriven;
    /// @brief "physxVehicleWheelAttachment:index"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentIndex;
    /// @brief "physxVehicleWheelAttachment:suspension"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentSuspension;
    /// @brief "physxVehicleWheelAttachment:suspensionForceAppPointOffset"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentSuspensionForceAppPointOffset;
    /// @brief "physxVehicleWheelAttachment:suspensionFrameOrientation"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentSuspensionFrameOrientation;
    /// @brief "physxVehicleWheelAttachment:suspensionFramePosition"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentSuspensionFramePosition;
    /// @brief "physxVehicleWheelAttachment:suspensionTravelDirection"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentSuspensionTravelDirection;
    /// @brief "physxVehicleWheelAttachment:tire"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentTire;
    /// @brief "physxVehicleWheelAttachment:tireForceAppPointOffset"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentTireForceAppPointOffset;
    /// @brief "physxVehicleWheelAttachment:wheel"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentWheel;
    /// @brief "physxVehicleWheelAttachment:wheelCenterOfMassOffset"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentWheelCenterOfMassOffset;
    /// @brief "physxVehicleWheelAttachment:wheelFrameOrientation"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentWheelFrameOrientation;
    /// @brief "physxVehicleWheelAttachment:wheelFramePosition"
    ///
    /// PhysxSchemaPhysxVehicleWheelAttachmentAPI
    const TfToken physxVehicleWheelAttachmentWheelFramePosition;
    /// @brief "physxVehicleWheelController:brakeTorque"
    ///
    /// PhysxSchemaPhysxVehicleWheelControllerAPI
    const TfToken physxVehicleWheelControllerBrakeTorque;
    /// @brief "physxVehicleWheelController:driveTorque"
    ///
    /// PhysxSchemaPhysxVehicleWheelControllerAPI
    const TfToken physxVehicleWheelControllerDriveTorque;
    /// @brief "physxVehicleWheelController:steerAngle"
    ///
    /// PhysxSchemaPhysxVehicleWheelControllerAPI
    const TfToken physxVehicleWheelControllerSteerAngle;
    /// @brief "physxVehicleWheel:dampingRate"
    ///
    /// PhysxSchemaPhysxVehicleWheelAPI
    const TfToken physxVehicleWheelDampingRate;
    /// @brief "physxVehicleWheel:mass"
    ///
    /// PhysxSchemaPhysxVehicleWheelAPI
    const TfToken physxVehicleWheelMass;
    /// @brief "physxVehicleWheel:maxBrakeTorque"
    ///
    /// PhysxSchemaPhysxVehicleWheelAPI
    const TfToken physxVehicleWheelMaxBrakeTorque;
    /// @brief "physxVehicleWheel:maxHandBrakeTorque"
    ///
    /// PhysxSchemaPhysxVehicleWheelAPI
    const TfToken physxVehicleWheelMaxHandBrakeTorque;
    /// @brief "physxVehicleWheel:maxSteerAngle"
    ///
    /// PhysxSchemaPhysxVehicleWheelAPI
    const TfToken physxVehicleWheelMaxSteerAngle;
    /// @brief "physxVehicleWheel:moi"
    ///
    /// PhysxSchemaPhysxVehicleWheelAPI
    const TfToken physxVehicleWheelMoi;
    /// @brief "physxVehicleWheel:radius"
    ///
    /// PhysxSchemaPhysxVehicleWheelAPI
    const TfToken physxVehicleWheelRadius;
    /// @brief "physxVehicleWheel:toeAngle"
    ///
    /// PhysxSchemaPhysxVehicleWheelAPI
    const TfToken physxVehicleWheelToeAngle;
    /// @brief "physxVehicleWheel:width"
    ///
    /// PhysxSchemaPhysxVehicleWheelAPI
    const TfToken physxVehicleWheelWidth;
    /// @brief "points0"
    ///
    /// PhysxSchemaPhysxPhysicsAttachment
    const TfToken points0;
    /// @brief "points1"
    ///
    /// PhysxSchemaPhysxPhysicsAttachment
    const TfToken points1;
    /// @brief "posX"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextLongitudinalAxisAttr(), Possible
    /// value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextVerticalAxisAttr()
    const TfToken posX;
    /// @brief "posY"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextLongitudinalAxisAttr(), Possible
    /// value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextVerticalAxisAttr()
    const TfToken posY;
    /// @brief "posZ"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextLongitudinalAxisAttr(), Possible
    /// value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextVerticalAxisAttr()
    const TfToken posZ;
    /// @brief "preventClimbing"
    ///
    /// Possible value for PhysxSchemaPhysxCharacterControllerAPI::GetPhysxCharacterControllerNonWalkableModeAttr(),
    /// Default value for PhysxSchemaPhysxCharacterControllerAPI::GetPhysxCharacterControllerNonWalkableModeAttr()
    const TfToken preventClimbing;
    /// @brief "preventClimbingForceSliding"
    ///
    /// Possible value for PhysxSchemaPhysxCharacterControllerAPI::GetPhysxCharacterControllerNonWalkableModeAttr()
    const TfToken preventClimbingForceSliding;
    /// @brief "quasistaticactors"
    ///
    /// This token defines the PhysxSceneQuasistaticAPI collection that gathers the quasistatic actors.
    const TfToken quasistaticactors;
    /// @brief "raycast"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleAPI::GetPhysxVehicleSuspensionLineQueryTypeAttr(), Default value for
    /// PhysxSchemaPhysxVehicleAPI::GetPhysxVehicleSuspensionLineQueryTypeAttr(), Possible value for
    /// PhysxSchemaPhysxSphereFillCollisionAPI::GetPhysxSphereFillCollisionFillModeAttr()
    const TfToken raycast;
    /// @brief "physxVehicle:referenceFrameIsCenterOfMass"
    ///
    /// This token represents a boolean custom metadata attribute that defines whether some vehicle wheel attachment
    /// properties are defined relative to the vehicle prim coordinate frame or relative to the vehicle center of mass
    /// coordinate frame. The affected properties are: suspensionTravelDirection, suspensionFramePosition,
    /// suspensionFrameOrientation, suspensionForceAppPointOffset, wheelCenterOfMassOffset and tireForceAppPointOffset.
    /// This custom metadata can be set on the prim that has PhysxVehicleAPI applied. Note that using the center of mass
    /// frame as reference (=True) is deprecated and will not be supported for much longer.
    const TfToken referenceFrameIsCenterOfMass;
    /// @brief "restitution"
    ///
    /// PhysxSchemaPhysxLimitAPI
    const TfToken restitution;
    /// @brief "restLength"
    ///
    /// PhysxSchemaPhysxTendonAttachmentLeafAPI, PhysxSchemaPhysxTendonAxisRootAPI
    const TfToken restLength;
    /// @brief "restOffset"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken restOffset;
    /// @brief "rotX"
    ///
    /// Possible value for PhysxSchemaPhysxTendonAxisAPI::GetJointAxisAttr()
    const TfToken rotX;
    /// @brief "rotY"
    ///
    /// Possible value for PhysxSchemaPhysxTendonAxisAPI::GetJointAxisAttr()
    const TfToken rotY;
    /// @brief "rotZ"
    ///
    /// Possible value for PhysxSchemaPhysxTendonAxisAPI::GetJointAxisAttr()
    const TfToken rotZ;
    /// @brief "SAP"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneBroadphaseTypeAttr()
    const TfToken sAP;
    /// @brief "SAT"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneCollisionSystemAttr()
    const TfToken sAT;
    /// @brief "scriptBuffer"
    ///
    /// Possible value for PhysxSchemaPhysxTriggerAPI::GetPhysxTriggerEnterScriptTypeAttr(), Possible value for
    /// PhysxSchemaPhysxTriggerAPI::GetPhysxTriggerLeaveScriptTypeAttr()
    const TfToken scriptBuffer;
    /// @brief "scriptFile"
    ///
    /// Possible value for PhysxSchemaPhysxTriggerAPI::GetPhysxTriggerEnterScriptTypeAttr(), Default value for
    /// PhysxSchemaPhysxTriggerAPI::GetPhysxTriggerEnterScriptTypeAttr(), Possible value for
    /// PhysxSchemaPhysxTriggerAPI::GetPhysxTriggerLeaveScriptTypeAttr(), Default value for
    /// PhysxSchemaPhysxTriggerAPI::GetPhysxTriggerLeaveScriptTypeAttr()
    const TfToken scriptFile;
    /// @brief "sdf"
    ///
    /// This token represents the SDF triangle mesh approximation.
    const TfToken sdf;
    /// @brief "simulationOwner"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken simulationOwner;
    /// @brief "solidRestOffset"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken solidRestOffset;
    /// @brief "solverPositionIterationCount"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken solverPositionIterationCount;
    /// @brief "speedResponses"
    ///
    /// PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI
    const TfToken speedResponses;
    /// @brief "speedResponsesPerCommandValue"
    ///
    /// PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI
    const TfToken speedResponsesPerCommandValue;
    /// @brief "sphereFill"
    ///
    /// This token represents sphere fill approximation.
    const TfToken sphereFill;
    /// @brief "state"
    ///
    /// Property namespace prefix for the PhysxSchemaJointStateAPI schema.
    const TfToken state;
    /// @brief "steer"
    ///
    /// This token holds the instance name to use for PhysxVehicleNonlinearCommandResponseAPI when applying it to the
    /// steering system.
    const TfToken steer;
    /// @brief "stiffness"
    ///
    /// PhysxSchemaPhysxTendonAttachmentRootAPI, PhysxSchemaPhysxTendonAxisRootAPI, PhysxSchemaPhysxLimitAPI
    const TfToken stiffness;
    /// @brief "surface"
    ///
    /// Possible value for PhysxSchemaPhysxSphereFillCollisionAPI::GetPhysxSphereFillCollisionFillModeAttr()
    const TfToken surface;
    /// @brief "sweep"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleAPI::GetPhysxVehicleSuspensionLineQueryTypeAttr()
    const TfToken sweep;
    /// @brief "Synchronous"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneUpdateTypeAttr(), Default value for
    /// PhysxSchemaPhysxSceneAPI::GetPhysxSceneUpdateTypeAttr()
    const TfToken synchronous;
    /// @brief "tendonEnabled"
    ///
    /// PhysxSchemaPhysxTendonAttachmentRootAPI, PhysxSchemaPhysxTendonAxisRootAPI
    const TfToken tendonEnabled;
    /// @brief "TGS"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneSolverTypeAttr(), Default value for
    /// PhysxSchemaPhysxSceneAPI::GetPhysxSceneSolverTypeAttr()
    const TfToken tGS;
    /// @brief "torqueMultipliers"
    ///
    /// PhysxSchemaPhysxVehicleBrakesAPI
    const TfToken torqueMultipliers;
    /// @brief "transX"
    ///
    /// Possible value for PhysxSchemaPhysxTendonAxisAPI::GetJointAxisAttr()
    const TfToken transX;
    /// @brief "transY"
    ///
    /// Possible value for PhysxSchemaPhysxTendonAxisAPI::GetJointAxisAttr()
    const TfToken transY;
    /// @brief "transZ"
    ///
    /// Possible value for PhysxSchemaPhysxTendonAxisAPI::GetJointAxisAttr()
    const TfToken transZ;
    /// @brief "triangleMesh"
    ///
    /// This token represents the collection name to use with PhysxCookedDataAPI to represent cooked data of a
    /// TriangleMesh.
    const TfToken triangleMesh;
    /// @brief "twoDirectional"
    ///
    /// Possible value for PhysxSchemaPhysxSceneAPI::GetPhysxSceneFrictionTypeAttr()
    const TfToken twoDirectional;
    /// @brief "undefined"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextLongitudinalAxisAttr(), Default
    /// value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextLongitudinalAxisAttr(), Possible value for
    /// PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextVerticalAxisAttr(), Default value for
    /// PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextVerticalAxisAttr()
    const TfToken undefined;
    /// @brief "upperLimit"
    ///
    /// PhysxSchemaPhysxTendonAttachmentLeafAPI, PhysxSchemaPhysxTendonAxisRootAPI
    const TfToken upperLimit;
    /// @brief "velocityChange"
    ///
    /// Possible value for PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextUpdateModeAttr(), Default value for
    /// PhysxSchemaPhysxVehicleContextAPI::GetPhysxVehicleContextUpdateModeAttr()
    const TfToken velocityChange;
    /// @brief "Vertices"
    ///
    /// Possible value for PhysxSchemaPhysxPhysicsAttachment::GetFilterType0Attr(), Possible value for
    /// PhysxSchemaPhysxPhysicsAttachment::GetFilterType1Attr()
    const TfToken vertices;
    /// @brief "wheels"
    ///
    /// PhysxSchemaPhysxVehicleBrakesAPI
    const TfToken wheels;
    /// @brief "wind"
    ///
    /// PhysxSchemaPhysxParticleSystem
    const TfToken wind;
    /// @brief "X"
    ///
    /// Possible value for PhysxSchemaPhysxCharacterControllerAPI::GetPhysxCharacterControllerUpAxisAttr()
    const TfToken x;
    /// @brief "Y"
    ///
    /// Possible value for PhysxSchemaPhysxCharacterControllerAPI::GetPhysxCharacterControllerUpAxisAttr()
    const TfToken y;
    /// @brief "Z"
    ///
    /// Possible value for PhysxSchemaPhysxCharacterControllerAPI::GetPhysxCharacterControllerUpAxisAttr(), Default
    /// value for PhysxSchemaPhysxCharacterControllerAPI::GetPhysxCharacterControllerUpAxisAttr()
    const TfToken z;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline PhysxSchemaTokensType::PhysxSchemaTokensType()
    : acceleration("acceleration"),
      actor0("actor0"),
      actor1("actor1"),
      alwaysUpdateEnabled("alwaysUpdateEnabled"),
      asynchronous("Asynchronous"),
      attachmentEnabled("attachmentEnabled"),
      average("average"),
      bitsPerPixel16("BitsPerPixel16"),
      bitsPerPixel32("BitsPerPixel32"),
      bitsPerPixel8("BitsPerPixel8"),
      bounceThreshold("bounceThreshold"),
      brakes0("brakes0"),
      brakes1("brakes1"),
      buffer("buffer"),
      clothConstaint("clothConstaint"),
      collisionFilterIndices0("collisionFilterIndices0"),
      collisionFilterIndices1("collisionFilterIndices1"),
      collisionmeshes("collisionmeshes"),
      commandValues("commandValues"),
      constrained("constrained"),
      contactDistance("contactDistance"),
      contactOffset("contactOffset"),
      convexDecomposition("convexDecomposition"),
      convexHull("convexHull"),
      damping("damping"),
      defaultFrictionValue("defaultFrictionValue"),
      disabled("Disabled"),
      drive("drive"),
      easy("easy"),
      enableCCD("enableCCD"),
      filterType0("filterType0"),
      filterType1("filterType1"),
      flood("flood"),
      fluidRestOffset("fluidRestOffset"),
      force("force"),
      forceCoefficient("forceCoefficient"),
      frictionValues("frictionValues"),
      gearing("gearing"),
      geometry("Geometry"),
      globalSelfCollisionEnabled("globalSelfCollisionEnabled"),
      gPU("GPU"),
      groundMaterials("groundMaterials"),
      indices("indices"),
      jointAxis("jointAxis"),
      limitStiffness("limitStiffness"),
      localPos("localPos"),
      lowerLimit("lowerLimit"),
      max("max"),
      maxBrakeTorque("maxBrakeTorque"),
      maxDepenetrationVelocity("maxDepenetrationVelocity"),
      maxNeighborhood("maxNeighborhood"),
      maxVelocity("maxVelocity"),
      mBP("MBP"),
      min("min"),
      multiply("multiply"),
      negX("negX"),
      negY("negY"),
      negZ("negZ"),
      neighborhoodScale("neighborhoodScale"),
      nonParticleCollisionEnabled("nonParticleCollisionEnabled"),
      offset("offset"),
      oneDirectional("oneDirectional"),
      parentAttachment("parentAttachment"),
      parentLink("parentLink"),
      particleContactOffset("particleContactOffset"),
      particleSystemEnabled("particleSystemEnabled"),
      patch("patch"),
      pCM("PCM"),
      pGS("PGS"),
      physicsBody0Indices("physics:body0Indices"),
      physicsBody0s("physics:body0s"),
      physicsBody1Indices("physics:body1Indices"),
      physicsBody1s("physics:body1s"),
      physicsGearRatio("physics:gearRatio"),
      physicsHinge("physics:hinge"),
      physicsHinge0("physics:hinge0"),
      physicsHinge1("physics:hinge1"),
      physicsLocalPos0s("physics:localPos0s"),
      physicsLocalPos1s("physics:localPos1s"),
      physicsLocalRot0s("physics:localRot0s"),
      physicsLocalRot1s("physics:localRot1s"),
      physicsPosition("physics:position"),
      physicsPrismatic("physics:prismatic"),
      physicsProtoIndices("physics:protoIndices"),
      physicsPrototypes("physics:prototypes"),
      physicsRatio("physics:ratio"),
      physicsVelocity("physics:velocity"),
      physxArticulationArticulationEnabled("physxArticulation:articulationEnabled"),
      physxArticulationEnabledSelfCollisions("physxArticulation:enabledSelfCollisions"),
      physxArticulationForceSensorConstraintSolverForcesEnabled(
          "physxArticulationForceSensor:constraintSolverForcesEnabled"),
      physxArticulationForceSensorForce("physxArticulationForceSensor:force"),
      physxArticulationForceSensorForwardDynamicsForcesEnabled(
          "physxArticulationForceSensor:forwardDynamicsForcesEnabled"),
      physxArticulationForceSensorSensorEnabled("physxArticulationForceSensor:sensorEnabled"),
      physxArticulationForceSensorTorque("physxArticulationForceSensor:torque"),
      physxArticulationForceSensorWorldFrameEnabled("physxArticulationForceSensor:worldFrameEnabled"),
      physxArticulationSleepThreshold("physxArticulation:sleepThreshold"),
      physxArticulationSolverPositionIterationCount("physxArticulation:solverPositionIterationCount"),
      physxArticulationSolverVelocityIterationCount("physxArticulation:solverVelocityIterationCount"),
      physxArticulationStabilizationThreshold("physxArticulation:stabilizationThreshold"),
      physxAutoAttachmentCollisionFilteringOffset("physxAutoAttachment:collisionFilteringOffset"),
      physxAutoAttachmentDeformableVertexOverlapOffset("physxAutoAttachment:deformableVertexOverlapOffset"),
      physxAutoAttachmentEnableCollisionFiltering("physxAutoAttachment:enableCollisionFiltering"),
      physxAutoAttachmentEnableDeformableFilteringPairs("physxAutoAttachment:enableDeformableFilteringPairs"),
      physxAutoAttachmentEnableDeformableVertexAttachments("physxAutoAttachment:enableDeformableVertexAttachments"),
      physxAutoAttachmentEnableRigidSurfaceAttachments("physxAutoAttachment:enableRigidSurfaceAttachments"),
      physxAutoAttachmentRigidSurfaceSamplingDistance("physxAutoAttachment:rigidSurfaceSamplingDistance"),
      physxAutoParticleClothDisableMeshWelding("physxAutoParticleCloth:disableMeshWelding"),
      physxAutoParticleClothSpringBendStiffness("physxAutoParticleCloth:springBendStiffness"),
      physxAutoParticleClothSpringDamping("physxAutoParticleCloth:springDamping"),
      physxAutoParticleClothSpringShearStiffness("physxAutoParticleCloth:springShearStiffness"),
      physxAutoParticleClothSpringStretchStiffness("physxAutoParticleCloth:springStretchStiffness"),
      physxCameraSubject("physxCamera:subject"),
      physxCharacterControllerClimbingMode("physxCharacterController:climbingMode"),
      physxCharacterControllerContactOffset("physxCharacterController:contactOffset"),
      physxCharacterControllerInvisibleWallHeight("physxCharacterController:invisibleWallHeight"),
      physxCharacterControllerMaxJumpHeight("physxCharacterController:maxJumpHeight"),
      physxCharacterControllerMoveTarget("physxCharacterController:moveTarget"),
      physxCharacterControllerNonWalkableMode("physxCharacterController:nonWalkableMode"),
      physxCharacterControllerScaleCoeff("physxCharacterController:scaleCoeff"),
      physxCharacterControllerSimulationOwner("physxCharacterController:simulationOwner"),
      physxCharacterControllerSlopeLimit("physxCharacterController:slopeLimit"),
      physxCharacterControllerStepOffset("physxCharacterController:stepOffset"),
      physxCharacterControllerUpAxis("physxCharacterController:upAxis"),
      physxCharacterControllerVolumeGrowth("physxCharacterController:volumeGrowth"),
      physxCollisionContactOffset("physxCollision:contactOffset"),
      physxCollisionCustomGeometry("physxCollisionCustomGeometry"),
      physxCollisionMinTorsionalPatchRadius("physxCollision:minTorsionalPatchRadius"),
      physxCollisionRestOffset("physxCollision:restOffset"),
      physxCollisionTorsionalPatchRadius("physxCollision:torsionalPatchRadius"),
      physxContactReportReportPairs("physxContactReport:reportPairs"),
      physxContactReportThreshold("physxContactReport:threshold"),
      physxConvexDecompositionCollisionErrorPercentage("physxConvexDecompositionCollision:errorPercentage"),
      physxConvexDecompositionCollisionHullVertexLimit("physxConvexDecompositionCollision:hullVertexLimit"),
      physxConvexDecompositionCollisionMaxConvexHulls("physxConvexDecompositionCollision:maxConvexHulls"),
      physxConvexDecompositionCollisionMinThickness("physxConvexDecompositionCollision:minThickness"),
      physxConvexDecompositionCollisionShrinkWrap("physxConvexDecompositionCollision:shrinkWrap"),
      physxConvexDecompositionCollisionVoxelResolution("physxConvexDecompositionCollision:voxelResolution"),
      physxConvexHullCollisionHullVertexLimit("physxConvexHullCollision:hullVertexLimit"),
      physxConvexHullCollisionMinThickness("physxConvexHullCollision:minThickness"),
      physxCookedData("physxCookedData"),
      physxDeformableBodyMaterialDampingScale("physxDeformableBodyMaterial:dampingScale"),
      physxDeformableBodyMaterialDensity("physxDeformableBodyMaterial:density"),
      physxDeformableBodyMaterialDynamicFriction("physxDeformableBodyMaterial:dynamicFriction"),
      physxDeformableBodyMaterialElasticityDamping("physxDeformableBodyMaterial:elasticityDamping"),
      physxDeformableBodyMaterialPoissonsRatio("physxDeformableBodyMaterial:poissonsRatio"),
      physxDeformableBodyMaterialYoungsModulus("physxDeformableBodyMaterial:youngsModulus"),
      physxDeformableCollisionIndices("physxDeformable:collisionIndices"),
      physxDeformableCollisionPoints("physxDeformable:collisionPoints"),
      physxDeformableCollisionRestPoints("physxDeformable:collisionRestPoints"),
      physxDeformableDeformableEnabled("physxDeformable:deformableEnabled"),
      physxDeformableDisableGravity("physxDeformable:disableGravity"),
      physxDeformableEnableCCD("physxDeformable:enableCCD"),
      physxDeformableMaxDepenetrationVelocity("physxDeformable:maxDepenetrationVelocity"),
      physxDeformableRestPoints("physxDeformable:restPoints"),
      physxDeformableSelfCollision("physxDeformable:selfCollision"),
      physxDeformableSelfCollisionFilterDistance("physxDeformable:selfCollisionFilterDistance"),
      physxDeformableSettlingThreshold("physxDeformable:settlingThreshold"),
      physxDeformableSimulationIndices("physxDeformable:simulationIndices"),
      physxDeformableSimulationOwner("physxDeformable:simulationOwner"),
      physxDeformableSimulationPoints("physxDeformable:simulationPoints"),
      physxDeformableSimulationRestPoints("physxDeformable:simulationRestPoints"),
      physxDeformableSimulationVelocities("physxDeformable:simulationVelocities"),
      physxDeformableSleepDamping("physxDeformable:sleepDamping"),
      physxDeformableSleepThreshold("physxDeformable:sleepThreshold"),
      physxDeformableSolverPositionIterationCount("physxDeformable:solverPositionIterationCount"),
      physxDeformableSurfaceBendingStiffnessScale("physxDeformableSurface:bendingStiffnessScale"),
      physxDeformableSurfaceCollisionIterationMultiplier("physxDeformableSurface:collisionIterationMultiplier"),
      physxDeformableSurfaceCollisionPairUpdateFrequency("physxDeformableSurface:collisionPairUpdateFrequency"),
      physxDeformableSurfaceFlatteningEnabled("physxDeformableSurface:flatteningEnabled"),
      physxDeformableSurfaceMaterialDensity("physxDeformableSurfaceMaterial:density"),
      physxDeformableSurfaceMaterialDynamicFriction("physxDeformableSurfaceMaterial:dynamicFriction"),
      physxDeformableSurfaceMaterialPoissonsRatio("physxDeformableSurfaceMaterial:poissonsRatio"),
      physxDeformableSurfaceMaterialThickness("physxDeformableSurfaceMaterial:thickness"),
      physxDeformableSurfaceMaterialYoungsModulus("physxDeformableSurfaceMaterial:youngsModulus"),
      physxDeformableSurfaceMaxVelocity("physxDeformableSurface:maxVelocity"),
      physxDeformableVertexVelocityDamping("physxDeformable:vertexVelocityDamping"),
      physxDiffuseParticlesAirDrag("physxDiffuseParticles:airDrag"),
      physxDiffuseParticlesBubbleDrag("physxDiffuseParticles:bubbleDrag"),
      physxDiffuseParticlesBuoyancy("physxDiffuseParticles:buoyancy"),
      physxDiffuseParticlesCollisionDecay("physxDiffuseParticles:collisionDecay"),
      physxDiffuseParticlesDiffuseParticlesEnabled("physxDiffuseParticles:diffuseParticlesEnabled"),
      physxDiffuseParticlesDivergenceWeight("physxDiffuseParticles:divergenceWeight"),
      physxDiffuseParticlesKineticEnergyWeight("physxDiffuseParticles:kineticEnergyWeight"),
      physxDiffuseParticlesLifetime("physxDiffuseParticles:lifetime"),
      physxDiffuseParticlesMaxDiffuseParticleMultiplier("physxDiffuseParticles:maxDiffuseParticleMultiplier"),
      physxDiffuseParticlesPressureWeight("physxDiffuseParticles:pressureWeight"),
      physxDiffuseParticlesThreshold("physxDiffuseParticles:threshold"),
      physxDiffuseParticlesUseAccurateVelocity("physxDiffuseParticles:useAccurateVelocity"),
      physxDroneCameraFeedForwardVelocityGain("physxDroneCamera:feedForwardVelocityGain"),
      physxDroneCameraFollowDistance("physxDroneCamera:followDistance"),
      physxDroneCameraFollowHeight("physxDroneCamera:followHeight"),
      physxDroneCameraHorizontalVelocityGain("physxDroneCamera:horizontalVelocityGain"),
      physxDroneCameraMaxDistance("physxDroneCamera:maxDistance"),
      physxDroneCameraMaxSpeed("physxDroneCamera:maxSpeed"),
      physxDroneCameraPositionOffset("physxDroneCamera:positionOffset"),
      physxDroneCameraRotationFilterTimeConstant("physxDroneCamera:rotationFilterTimeConstant"),
      physxDroneCameraVelocityFilterTimeConstant("physxDroneCamera:velocityFilterTimeConstant"),
      physxDroneCameraVerticalVelocityGain("physxDroneCamera:verticalVelocityGain"),
      physxFollowCameraCameraPositionTimeConstant("physxFollowCamera:cameraPositionTimeConstant"),
      physxFollowCameraFollowMaxDistance("physxFollowCamera:followMaxDistance"),
      physxFollowCameraFollowMaxSpeed("physxFollowCamera:followMaxSpeed"),
      physxFollowCameraFollowMinDistance("physxFollowCamera:followMinDistance"),
      physxFollowCameraFollowMinSpeed("physxFollowCamera:followMinSpeed"),
      physxFollowCameraFollowTurnRateGain("physxFollowCamera:followTurnRateGain"),
      physxFollowCameraLookAheadMaxSpeed("physxFollowCamera:lookAheadMaxSpeed"),
      physxFollowCameraLookAheadMinDistance("physxFollowCamera:lookAheadMinDistance"),
      physxFollowCameraLookAheadMinSpeed("physxFollowCamera:lookAheadMinSpeed"),
      physxFollowCameraLookAheadTurnRateGain("physxFollowCamera:lookAheadTurnRateGain"),
      physxFollowCameraLookPositionHeight("physxFollowCamera:lookPositionHeight"),
      physxFollowCameraLookPositionTimeConstant("physxFollowCamera:lookPositionTimeConstant"),
      physxFollowCameraPitchAngle("physxFollowCamera:pitchAngle"),
      physxFollowCameraPitchAngleTimeConstant("physxFollowCamera:pitchAngleTimeConstant"),
      physxFollowCameraPositionOffset("physxFollowCamera:positionOffset"),
      physxFollowCameraSlowPitchAngleSpeed("physxFollowCamera:slowPitchAngleSpeed"),
      physxFollowCameraSlowSpeedPitchAngleScale("physxFollowCamera:slowSpeedPitchAngleScale"),
      physxFollowCameraVelocityNormalMinSpeed("physxFollowCamera:velocityNormalMinSpeed"),
      physxFollowCameraYawAngle("physxFollowCamera:yawAngle"),
      physxFollowCameraYawRateTimeConstant("physxFollowCamera:yawRateTimeConstant"),
      physxFollowFollowCameraLookAheadMaxDistance("physxFollowFollowCamera:lookAheadMaxDistance"),
      physxFollowLookCameraDownHillGroundAngle("physxFollowLookCamera:downHillGroundAngle"),
      physxFollowLookCameraDownHillGroundPitch("physxFollowLookCamera:downHillGroundPitch"),
      physxFollowLookCameraFollowReverseDistance("physxFollowLookCamera:followReverseDistance"),
      physxFollowLookCameraFollowReverseSpeed("physxFollowLookCamera:followReverseSpeed"),
      physxFollowLookCameraUpHillGroundAngle("physxFollowLookCamera:upHillGroundAngle"),
      physxFollowLookCameraUpHillGroundPitch("physxFollowLookCamera:upHillGroundPitch"),
      physxFollowLookCameraVelocityBlendTimeConstant("physxFollowLookCamera:velocityBlendTimeConstant"),
      physxForceForce("physxForce:force"),
      physxForceForceEnabled("physxForce:forceEnabled"),
      physxForceMode("physxForce:mode"),
      physxForceTorque("physxForce:torque"),
      physxForceWorldFrameEnabled("physxForce:worldFrameEnabled"),
      physxHairExternalCollision("physxHair:externalCollision"),
      physxHairGlobalShapeComplianceAtRoot("physxHair:globalShapeComplianceAtRoot"),
      physxHairGlobalShapeComplianceStrandAttenuation("physxHair:globalShapeComplianceStrandAttenuation"),
      physxHairInterHairRepulsion("physxHair:interHairRepulsion"),
      physxHairLocalShapeMatchingCompliance("physxHair:localShapeMatchingCompliance"),
      physxHairLocalShapeMatchingGroupOverlap("physxHair:localShapeMatchingGroupOverlap"),
      physxHairLocalShapeMatchingGroupSize("physxHair:localShapeMatchingGroupSize"),
      physxHairLocalShapeMatchingLinearStretching("physxHair:localShapeMatchingLinearStretching"),
      physxHairMaterialContactOffset("physxHairMaterial:contactOffset"),
      physxHairMaterialContactOffsetMultiplier("physxHairMaterial:contactOffsetMultiplier"),
      physxHairMaterialCurveBendStiffness("physxHairMaterial:curveBendStiffness"),
      physxHairMaterialCurveThickness("physxHairMaterial:curveThickness"),
      physxHairMaterialDensity("physxHairMaterial:density"),
      physxHairMaterialDynamicFriction("physxHairMaterial:dynamicFriction"),
      physxHairMaterialYoungsModulus("physxHairMaterial:youngsModulus"),
      physxHairSegmentLength("physxHair:segmentLength"),
      physxHairTwosidedAttachment("physxHair:twosidedAttachment"),
      physxHairVelSmoothing("physxHair:velSmoothing"),
      physxJointArmature("physxJoint:armature"),
      physxJointEnableProjection("physxJoint:enableProjection"),
      physxJointJointFriction("physxJoint:jointFriction"),
      physxJointMaxJointVelocity("physxJoint:maxJointVelocity"),
      physxLimit("physxLimit"),
      physxMaterialCompliantContactDamping("physxMaterial:compliantContactDamping"),
      physxMaterialCompliantContactStiffness("physxMaterial:compliantContactStiffness"),
      physxMaterialFrictionCombineMode("physxMaterial:frictionCombineMode"),
      physxMaterialImprovePatchFriction("physxMaterial:improvePatchFriction"),
      physxMaterialRestitutionCombineMode("physxMaterial:restitutionCombineMode"),
      physxParticleAnisotropyMax("physxParticleAnisotropy:max"),
      physxParticleAnisotropyMin("physxParticleAnisotropy:min"),
      physxParticleAnisotropyParticleAnisotropyEnabled("physxParticleAnisotropy:particleAnisotropyEnabled"),
      physxParticleAnisotropyScale("physxParticleAnisotropy:scale"),
      physxParticleFluid("physxParticle:fluid"),
      physxParticleIsosurfaceGridFilteringPasses("physxParticleIsosurface:gridFilteringPasses"),
      physxParticleIsosurfaceGridSmoothingRadius("physxParticleIsosurface:gridSmoothingRadius"),
      physxParticleIsosurfaceGridSpacing("physxParticleIsosurface:gridSpacing"),
      physxParticleIsosurfaceIsosurfaceEnabled("physxParticleIsosurface:isosurfaceEnabled"),
      physxParticleIsosurfaceMaxSubgrids("physxParticleIsosurface:maxSubgrids"),
      physxParticleIsosurfaceMaxTriangles("physxParticleIsosurface:maxTriangles"),
      physxParticleIsosurfaceMaxVertices("physxParticleIsosurface:maxVertices"),
      physxParticleIsosurfaceNumMeshNormalSmoothingPasses("physxParticleIsosurface:numMeshNormalSmoothingPasses"),
      physxParticleIsosurfaceNumMeshSmoothingPasses("physxParticleIsosurface:numMeshSmoothingPasses"),
      physxParticleIsosurfaceSurfaceDistance("physxParticleIsosurface:surfaceDistance"),
      physxParticleParticleEnabled("physxParticle:particleEnabled"),
      physxParticleParticleGroup("physxParticle:particleGroup"),
      physxParticleParticleSystem("physxParticle:particleSystem"),
      physxParticlePressure("physxParticle:pressure"),
      physxParticleRestPoints("physxParticle:restPoints"),
      physxParticleSamplingMaxSamples("physxParticleSampling:maxSamples"),
      physxParticleSamplingParticles("physxParticleSampling:particles"),
      physxParticleSamplingSamplingDistance("physxParticleSampling:samplingDistance"),
      physxParticleSamplingVolume("physxParticleSampling:volume"),
      physxParticleSelfCollision("physxParticle:selfCollision"),
      physxParticleSelfCollisionFilter("physxParticle:selfCollisionFilter"),
      physxParticleSimulationPoints("physxParticle:simulationPoints"),
      physxParticleSmoothingParticleSmoothingEnabled("physxParticleSmoothing:particleSmoothingEnabled"),
      physxParticleSmoothingStrength("physxParticleSmoothing:strength"),
      physxParticleSpringDampings("physxParticle:springDampings"),
      physxParticleSpringIndices("physxParticle:springIndices"),
      physxParticleSpringRestLengths("physxParticle:springRestLengths"),
      physxParticleSpringStiffnesses("physxParticle:springStiffnesses"),
      physxPBDMaterialAdhesion("physxPBDMaterial:adhesion"),
      physxPBDMaterialAdhesionOffsetScale("physxPBDMaterial:adhesionOffsetScale"),
      physxPBDMaterialCflCoefficient("physxPBDMaterial:cflCoefficient"),
      physxPBDMaterialCohesion("physxPBDMaterial:cohesion"),
      physxPBDMaterialDamping("physxPBDMaterial:damping"),
      physxPBDMaterialDensity("physxPBDMaterial:density"),
      physxPBDMaterialDrag("physxPBDMaterial:drag"),
      physxPBDMaterialFriction("physxPBDMaterial:friction"),
      physxPBDMaterialGravityScale("physxPBDMaterial:gravityScale"),
      physxPBDMaterialLift("physxPBDMaterial:lift"),
      physxPBDMaterialParticleAdhesionScale("physxPBDMaterial:particleAdhesionScale"),
      physxPBDMaterialParticleFrictionScale("physxPBDMaterial:particleFrictionScale"),
      physxPBDMaterialSurfaceTension("physxPBDMaterial:surfaceTension"),
      physxPBDMaterialViscosity("physxPBDMaterial:viscosity"),
      physxPBDMaterialVorticityConfinement("physxPBDMaterial:vorticityConfinement"),
      physxPhysicsDistanceJointSpringDamping("physxPhysicsDistanceJoint:springDamping"),
      physxPhysicsDistanceJointSpringEnabled("physxPhysicsDistanceJoint:springEnabled"),
      physxPhysicsDistanceJointSpringStiffness("physxPhysicsDistanceJoint:springStiffness"),
      physxRigidBodyAngularDamping("physxRigidBody:angularDamping"),
      physxRigidBodyCfmScale("physxRigidBody:cfmScale"),
      physxRigidBodyContactSlopCoefficient("physxRigidBody:contactSlopCoefficient"),
      physxRigidBodyDisableGravity("physxRigidBody:disableGravity"),
      physxRigidBodyEnableCCD("physxRigidBody:enableCCD"),
      physxRigidBodyEnableGyroscopicForces("physxRigidBody:enableGyroscopicForces"),
      physxRigidBodyEnableSpeculativeCCD("physxRigidBody:enableSpeculativeCCD"),
      physxRigidBodyLinearDamping("physxRigidBody:linearDamping"),
      physxRigidBodyLockedPosAxis("physxRigidBody:lockedPosAxis"),
      physxRigidBodyLockedRotAxis("physxRigidBody:lockedRotAxis"),
      physxRigidBodyMaxAngularVelocity("physxRigidBody:maxAngularVelocity"),
      physxRigidBodyMaxContactImpulse("physxRigidBody:maxContactImpulse"),
      physxRigidBodyMaxDepenetrationVelocity("physxRigidBody:maxDepenetrationVelocity"),
      physxRigidBodyMaxLinearVelocity("physxRigidBody:maxLinearVelocity"),
      physxRigidBodyRetainAccelerations("physxRigidBody:retainAccelerations"),
      physxRigidBodySleepThreshold("physxRigidBody:sleepThreshold"),
      physxRigidBodySolveContact("physxRigidBody:solveContact"),
      physxRigidBodySolverPositionIterationCount("physxRigidBody:solverPositionIterationCount"),
      physxRigidBodySolverVelocityIterationCount("physxRigidBody:solverVelocityIterationCount"),
      physxRigidBodyStabilizationThreshold("physxRigidBody:stabilizationThreshold"),
      physxSceneBounceThreshold("physxScene:bounceThreshold"),
      physxSceneBroadphaseType("physxScene:broadphaseType"),
      physxSceneCollisionSystem("physxScene:collisionSystem"),
      physxSceneEnableCCD("physxScene:enableCCD"),
      physxSceneEnableEnhancedDeterminism("physxScene:enableEnhancedDeterminism"),
      physxSceneEnableExternalForcesEveryIteration("physxScene:enableExternalForcesEveryIteration"),
      physxSceneEnableGPUDynamics("physxScene:enableGPUDynamics"),
      physxSceneEnableSceneQuerySupport("physxScene:enableSceneQuerySupport"),
      physxSceneEnableStabilization("physxScene:enableStabilization"),
      physxSceneFrictionCorrelationDistance("physxScene:frictionCorrelationDistance"),
      physxSceneFrictionOffsetThreshold("physxScene:frictionOffsetThreshold"),
      physxSceneFrictionType("physxScene:frictionType"),
      physxSceneGpuCollisionStackSize("physxScene:gpuCollisionStackSize"),
      physxSceneGpuFoundLostAggregatePairsCapacity("physxScene:gpuFoundLostAggregatePairsCapacity"),
      physxSceneGpuFoundLostPairsCapacity("physxScene:gpuFoundLostPairsCapacity"),
      physxSceneGpuHeapCapacity("physxScene:gpuHeapCapacity"),
      physxSceneGpuMaxDeformableSurfaceContacts("physxScene:gpuMaxDeformableSurfaceContacts"),
      physxSceneGpuMaxHairContacts("physxScene:gpuMaxHairContacts"),
      physxSceneGpuMaxNumPartitions("physxScene:gpuMaxNumPartitions"),
      physxSceneGpuMaxParticleContacts("physxScene:gpuMaxParticleContacts"),
      physxSceneGpuMaxRigidContactCount("physxScene:gpuMaxRigidContactCount"),
      physxSceneGpuMaxRigidPatchCount("physxScene:gpuMaxRigidPatchCount"),
      physxSceneGpuMaxSoftBodyContacts("physxScene:gpuMaxSoftBodyContacts"),
      physxSceneGpuTempBufferCapacity("physxScene:gpuTempBufferCapacity"),
      physxSceneGpuTotalAggregatePairsCapacity("physxScene:gpuTotalAggregatePairsCapacity"),
      physxSceneInvertCollisionGroupFilter("physxScene:invertCollisionGroupFilter"),
      physxSceneMaxBiasCoefficient("physxScene:maxBiasCoefficient"),
      physxSceneMaxPositionIterationCount("physxScene:maxPositionIterationCount"),
      physxSceneMaxVelocityIterationCount("physxScene:maxVelocityIterationCount"),
      physxSceneMinPositionIterationCount("physxScene:minPositionIterationCount"),
      physxSceneMinVelocityIterationCount("physxScene:minVelocityIterationCount"),
      physxSceneQuasistaticEnableQuasistatic("physxSceneQuasistatic:enableQuasistatic"),
      physxSceneReportKinematicKinematicPairs("physxScene:reportKinematicKinematicPairs"),
      physxSceneReportKinematicStaticPairs("physxScene:reportKinematicStaticPairs"),
      physxSceneSolverType("physxScene:solverType"),
      physxSceneTimeStepsPerSecond("physxScene:timeStepsPerSecond"),
      physxSceneUpdateType("physxScene:updateType"),
      physxSDFMeshCollisionSdfBitsPerSubgridPixel("physxSDFMeshCollision:sdfBitsPerSubgridPixel"),
      physxSDFMeshCollisionSdfEnableRemeshing("physxSDFMeshCollision:sdfEnableRemeshing"),
      physxSDFMeshCollisionSdfMargin("physxSDFMeshCollision:sdfMargin"),
      physxSDFMeshCollisionSdfNarrowBandThickness("physxSDFMeshCollision:sdfNarrowBandThickness"),
      physxSDFMeshCollisionSdfResolution("physxSDFMeshCollision:sdfResolution"),
      physxSDFMeshCollisionSdfSubgridResolution("physxSDFMeshCollision:sdfSubgridResolution"),
      physxSDFMeshCollisionSdfTriangleCountReductionFactor("physxSDFMeshCollision:sdfTriangleCountReductionFactor"),
      physxSphereFillCollisionFillMode("physxSphereFillCollision:fillMode"),
      physxSphereFillCollisionMaxSpheres("physxSphereFillCollision:maxSpheres"),
      physxSphereFillCollisionSeedCount("physxSphereFillCollision:seedCount"),
      physxSphereFillCollisionVoxelResolution("physxSphereFillCollision:voxelResolution"),
      physxSurfaceVelocitySurfaceAngularVelocity("physxSurfaceVelocity:surfaceAngularVelocity"),
      physxSurfaceVelocitySurfaceVelocity("physxSurfaceVelocity:surfaceVelocity"),
      physxSurfaceVelocitySurfaceVelocityEnabled("physxSurfaceVelocity:surfaceVelocityEnabled"),
      physxSurfaceVelocitySurfaceVelocityLocalSpace("physxSurfaceVelocity:surfaceVelocityLocalSpace"),
      physxTendon("physxTendon"),
      physxTriangleMeshCollisionWeldTolerance("physxTriangleMeshCollision:weldTolerance"),
      physxTriangleMeshSimplificationCollisionMetric("physxTriangleMeshSimplificationCollision:metric"),
      physxTriangleMeshSimplificationCollisionWeldTolerance("physxTriangleMeshSimplificationCollision:weldTolerance"),
      physxTriggerEnterScriptType("physxTrigger:enterScriptType"),
      physxTriggerLeaveScriptType("physxTrigger:leaveScriptType"),
      physxTriggerOnEnterScript("physxTrigger:onEnterScript"),
      physxTriggerOnLeaveScript("physxTrigger:onLeaveScript"),
      physxTriggerTriggeredCollisions("physxTrigger:triggeredCollisions"),
      physxVehicleAckermannSteeringMaxSteerAngle("physxVehicleAckermannSteering:maxSteerAngle"),
      physxVehicleAckermannSteeringStrength("physxVehicleAckermannSteering:strength"),
      physxVehicleAckermannSteeringTrackWidth("physxVehicleAckermannSteering:trackWidth"),
      physxVehicleAckermannSteeringWheel0("physxVehicleAckermannSteering:wheel0"),
      physxVehicleAckermannSteeringWheel1("physxVehicleAckermannSteering:wheel1"),
      physxVehicleAckermannSteeringWheelBase("physxVehicleAckermannSteering:wheelBase"),
      physxVehicleAutoGearBoxDownRatios("physxVehicleAutoGearBox:downRatios"),
      physxVehicleAutoGearBoxLatency("physxVehicleAutoGearBox:latency"),
      physxVehicleAutoGearBoxUpRatios("physxVehicleAutoGearBox:upRatios"),
      physxVehicleBrakes("physxVehicleBrakes"),
      physxVehicleClutchStrength("physxVehicleClutch:strength"),
      physxVehicleContextForwardAxis("physxVehicleContext:forwardAxis"),
      physxVehicleContextLongitudinalAxis("physxVehicleContext:longitudinalAxis"),
      physxVehicleContextUpAxis("physxVehicleContext:upAxis"),
      physxVehicleContextUpdateMode("physxVehicleContext:updateMode"),
      physxVehicleContextVerticalAxis("physxVehicleContext:verticalAxis"),
      physxVehicleControllerAccelerator("physxVehicleController:accelerator"),
      physxVehicleControllerBrake("physxVehicleController:brake"),
      physxVehicleControllerBrake0("physxVehicleController:brake0"),
      physxVehicleControllerBrake1("physxVehicleController:brake1"),
      physxVehicleControllerHandbrake("physxVehicleController:handbrake"),
      physxVehicleControllerSteer("physxVehicleController:steer"),
      physxVehicleControllerSteerLeft("physxVehicleController:steerLeft"),
      physxVehicleControllerSteerRight("physxVehicleController:steerRight"),
      physxVehicleControllerTargetGear("physxVehicleController:targetGear"),
      physxVehicleDrive("physxVehicle:drive"),
      physxVehicleDriveBasicPeakTorque("physxVehicleDriveBasic:peakTorque"),
      physxVehicleDriveStandardAutoGearBox("physxVehicleDriveStandard:autoGearBox"),
      physxVehicleDriveStandardClutch("physxVehicleDriveStandard:clutch"),
      physxVehicleDriveStandardEngine("physxVehicleDriveStandard:engine"),
      physxVehicleDriveStandardGears("physxVehicleDriveStandard:gears"),
      physxVehicleEngineDampingRateFullThrottle("physxVehicleEngine:dampingRateFullThrottle"),
      physxVehicleEngineDampingRateZeroThrottleClutchDisengaged(
          "physxVehicleEngine:dampingRateZeroThrottleClutchDisengaged"),
      physxVehicleEngineDampingRateZeroThrottleClutchEngaged("physxVehicleEngine:dampingRateZeroThrottleClutchEngaged"),
      physxVehicleEngineIdleRotationSpeed("physxVehicleEngine:idleRotationSpeed"),
      physxVehicleEngineMaxRotationSpeed("physxVehicleEngine:maxRotationSpeed"),
      physxVehicleEngineMoi("physxVehicleEngine:moi"),
      physxVehicleEnginePeakTorque("physxVehicleEngine:peakTorque"),
      physxVehicleEngineTorqueCurve("physxVehicleEngine:torqueCurve"),
      physxVehicleGearsRatios("physxVehicleGears:ratios"),
      physxVehicleGearsRatioScale("physxVehicleGears:ratioScale"),
      physxVehicleGearsSwitchTime("physxVehicleGears:switchTime"),
      physxVehicleHighForwardSpeedSubStepCount("physxVehicle:highForwardSpeedSubStepCount"),
      physxVehicleLateralStickyTireDamping("physxVehicle:lateralStickyTireDamping"),
      physxVehicleLateralStickyTireThresholdSpeed("physxVehicle:lateralStickyTireThresholdSpeed"),
      physxVehicleLateralStickyTireThresholdTime("physxVehicle:lateralStickyTireThresholdTime"),
      physxVehicleLimitSuspensionExpansionVelocity("physxVehicle:limitSuspensionExpansionVelocity"),
      physxVehicleLongitudinalStickyTireDamping("physxVehicle:longitudinalStickyTireDamping"),
      physxVehicleLongitudinalStickyTireThresholdSpeed("physxVehicle:longitudinalStickyTireThresholdSpeed"),
      physxVehicleLongitudinalStickyTireThresholdTime("physxVehicle:longitudinalStickyTireThresholdTime"),
      physxVehicleLowForwardSpeedSubStepCount("physxVehicle:lowForwardSpeedSubStepCount"),
      physxVehicleMinActiveLongitudinalSlipDenominator("physxVehicle:minActiveLongitudinalSlipDenominator"),
      physxVehicleMinLateralSlipDenominator("physxVehicle:minLateralSlipDenominator"),
      physxVehicleMinLongitudinalSlipDenominator("physxVehicle:minLongitudinalSlipDenominator"),
      physxVehicleMinPassiveLongitudinalSlipDenominator("physxVehicle:minPassiveLongitudinalSlipDenominator"),
      physxVehicleMultiWheelDifferentialAverageWheelSpeedRatios(
          "physxVehicleMultiWheelDifferential:averageWheelSpeedRatios"),
      physxVehicleMultiWheelDifferentialTorqueRatios("physxVehicleMultiWheelDifferential:torqueRatios"),
      physxVehicleMultiWheelDifferentialWheels("physxVehicleMultiWheelDifferential:wheels"),
      physxVehicleNCR("physxVehicleNCR"),
      physxVehicleSteeringAngleMultipliers("physxVehicleSteering:angleMultipliers"),
      physxVehicleSteeringMaxSteerAngle("physxVehicleSteering:maxSteerAngle"),
      physxVehicleSteeringWheels("physxVehicleSteering:wheels"),
      physxVehicleSubStepThresholdLongitudinalSpeed("physxVehicle:subStepThresholdLongitudinalSpeed"),
      physxVehicleSuspensionCamberAtMaxCompression("physxVehicleSuspension:camberAtMaxCompression"),
      physxVehicleSuspensionCamberAtMaxDroop("physxVehicleSuspension:camberAtMaxDroop"),
      physxVehicleSuspensionCamberAtRest("physxVehicleSuspension:camberAtRest"),
      physxVehicleSuspensionComplianceSuspensionForceAppPoint("physxVehicleSuspensionCompliance:suspensionForceAppPoint"),
      physxVehicleSuspensionComplianceTireForceAppPoint("physxVehicleSuspensionCompliance:tireForceAppPoint"),
      physxVehicleSuspensionComplianceWheelCamberAngle("physxVehicleSuspensionCompliance:wheelCamberAngle"),
      physxVehicleSuspensionComplianceWheelToeAngle("physxVehicleSuspensionCompliance:wheelToeAngle"),
      physxVehicleSuspensionLineQueryType("physxVehicle:suspensionLineQueryType"),
      physxVehicleSuspensionMaxCompression("physxVehicleSuspension:maxCompression"),
      physxVehicleSuspensionMaxDroop("physxVehicleSuspension:maxDroop"),
      physxVehicleSuspensionSpringDamperRate("physxVehicleSuspension:springDamperRate"),
      physxVehicleSuspensionSpringStrength("physxVehicleSuspension:springStrength"),
      physxVehicleSuspensionSprungMass("physxVehicleSuspension:sprungMass"),
      physxVehicleSuspensionTravelDistance("physxVehicleSuspension:travelDistance"),
      physxVehicleTankControllerThrust0("physxVehicleTankController:thrust0"),
      physxVehicleTankControllerThrust1("physxVehicleTankController:thrust1"),
      physxVehicleTankDifferentialNumberOfWheelsPerTrack("physxVehicleTankDifferential:numberOfWheelsPerTrack"),
      physxVehicleTankDifferentialThrustIndexPerTrack("physxVehicleTankDifferential:thrustIndexPerTrack"),
      physxVehicleTankDifferentialTrackToWheelIndices("physxVehicleTankDifferential:trackToWheelIndices"),
      physxVehicleTankDifferentialWheelIndicesInTrackOrder("physxVehicleTankDifferential:wheelIndicesInTrackOrder"),
      physxVehicleTireCamberStiffness("physxVehicleTire:camberStiffness"),
      physxVehicleTireCamberStiffnessPerUnitGravity("physxVehicleTire:camberStiffnessPerUnitGravity"),
      physxVehicleTireFrictionTable("physxVehicleTire:frictionTable"),
      physxVehicleTireFrictionVsSlipGraph("physxVehicleTire:frictionVsSlipGraph"),
      physxVehicleTireLateralStiffnessGraph("physxVehicleTire:lateralStiffnessGraph"),
      physxVehicleTireLatStiffX("physxVehicleTire:latStiffX"),
      physxVehicleTireLatStiffY("physxVehicleTire:latStiffY"),
      physxVehicleTireLongitudinalStiffness("physxVehicleTire:longitudinalStiffness"),
      physxVehicleTireLongitudinalStiffnessPerUnitGravity("physxVehicleTire:longitudinalStiffnessPerUnitGravity"),
      physxVehicleTireRestLoad("physxVehicleTire:restLoad"),
      physxVehicleVehicleEnabled("physxVehicle:vehicleEnabled"),
      physxVehicleWheelAttachmentCollisionGroup("physxVehicleWheelAttachment:collisionGroup"),
      physxVehicleWheelAttachmentDriven("physxVehicleWheelAttachment:driven"),
      physxVehicleWheelAttachmentIndex("physxVehicleWheelAttachment:index"),
      physxVehicleWheelAttachmentSuspension("physxVehicleWheelAttachment:suspension"),
      physxVehicleWheelAttachmentSuspensionForceAppPointOffset(
          "physxVehicleWheelAttachment:suspensionForceAppPointOffset"),
      physxVehicleWheelAttachmentSuspensionFrameOrientation("physxVehicleWheelAttachment:suspensionFrameOrientation"),
      physxVehicleWheelAttachmentSuspensionFramePosition("physxVehicleWheelAttachment:suspensionFramePosition"),
      physxVehicleWheelAttachmentSuspensionTravelDirection("physxVehicleWheelAttachment:suspensionTravelDirection"),
      physxVehicleWheelAttachmentTire("physxVehicleWheelAttachment:tire"),
      physxVehicleWheelAttachmentTireForceAppPointOffset("physxVehicleWheelAttachment:tireForceAppPointOffset"),
      physxVehicleWheelAttachmentWheel("physxVehicleWheelAttachment:wheel"),
      physxVehicleWheelAttachmentWheelCenterOfMassOffset("physxVehicleWheelAttachment:wheelCenterOfMassOffset"),
      physxVehicleWheelAttachmentWheelFrameOrientation("physxVehicleWheelAttachment:wheelFrameOrientation"),
      physxVehicleWheelAttachmentWheelFramePosition("physxVehicleWheelAttachment:wheelFramePosition"),
      physxVehicleWheelControllerBrakeTorque("physxVehicleWheelController:brakeTorque"),
      physxVehicleWheelControllerDriveTorque("physxVehicleWheelController:driveTorque"),
      physxVehicleWheelControllerSteerAngle("physxVehicleWheelController:steerAngle"),
      physxVehicleWheelDampingRate("physxVehicleWheel:dampingRate"),
      physxVehicleWheelMass("physxVehicleWheel:mass"),
      physxVehicleWheelMaxBrakeTorque("physxVehicleWheel:maxBrakeTorque"),
      physxVehicleWheelMaxHandBrakeTorque("physxVehicleWheel:maxHandBrakeTorque"),
      physxVehicleWheelMaxSteerAngle("physxVehicleWheel:maxSteerAngle"),
      physxVehicleWheelMoi("physxVehicleWheel:moi"),
      physxVehicleWheelRadius("physxVehicleWheel:radius"),
      physxVehicleWheelToeAngle("physxVehicleWheel:toeAngle"),
      physxVehicleWheelWidth("physxVehicleWheel:width"),
      points0("points0"),
      points1("points1"),
      posX("posX"),
      posY("posY"),
      posZ("posZ"),
      preventClimbing("preventClimbing"),
      preventClimbingForceSliding("preventClimbingForceSliding"),
      quasistaticactors("quasistaticactors"),
      raycast("raycast"),
      referenceFrameIsCenterOfMass("physxVehicle:referenceFrameIsCenterOfMass"),
      restitution("restitution"),
      restLength("restLength"),
      restOffset("restOffset"),
      rotX("rotX"),
      rotY("rotY"),
      rotZ("rotZ"),
      sAP("SAP"),
      sAT("SAT"),
      scriptBuffer("scriptBuffer"),
      scriptFile("scriptFile"),
      sdf("sdf"),
      simulationOwner("simulationOwner"),
      solidRestOffset("solidRestOffset"),
      solverPositionIterationCount("solverPositionIterationCount"),
      speedResponses("speedResponses"),
      speedResponsesPerCommandValue("speedResponsesPerCommandValue"),
      sphereFill("sphereFill"),
      state("state"),
      steer("steer"),
      stiffness("stiffness"),
      surface("surface"),
      sweep("sweep"),
      synchronous("Synchronous"),
      tendonEnabled("tendonEnabled"),
      tGS("TGS"),
      torqueMultipliers("torqueMultipliers"),
      transX("transX"),
      transY("transY"),
      transZ("transZ"),
      triangleMesh("triangleMesh"),
      twoDirectional("twoDirectional"),
      undefined("undefined"),
      upperLimit("upperLimit"),
      velocityChange("velocityChange"),
      vertices("Vertices"),
      wheels("wheels"),
      wind("wind"),
      x("X"),
      y("Y"),
      z("Z")
{
}

struct PhysxSchemaTokensTypeAccessor
{
    const PhysxSchemaTokensType* operator->()
    {
        static const PhysxSchemaTokensType tokens;
        return &tokens;
    }
};


inline PhysxSchemaTokensTypeAccessor PhysxSchemaTokens;


} // namespace usdrt
