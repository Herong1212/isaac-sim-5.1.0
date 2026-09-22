// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// TODO USD COPYRIGHT AS WELL?
#pragma once

/// @file physxSchema/physxSceneAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/physxSchema/tokens.h"


// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
// --(END CUSTOM INCLUDES)--

#include <omni/core/IObject.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/base/vt/array.h>
#include <usdrt/scenegraph/interface/IRtAttribute.h>
#include <usdrt/scenegraph/interface/IRtPrim.h>
#include <usdrt/scenegraph/interface/IRtPrimRange.h>
#include <usdrt/scenegraph/interface/IRtRelationship.h>
#include <usdrt/scenegraph/interface/IRtStage.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/usd/sdf/types.h>
#include <usdrt/scenegraph/usd/sdf/valueTypeName.h>
#include <usdrt/scenegraph/usd/usd/attribute.h>
#include <usdrt/scenegraph/usd/usd/common.h>
#include <usdrt/scenegraph/usd/usd/prim.h>
#include <usdrt/scenegraph/usd/usd/timeCode.h>

namespace usdrt
{

// -------------------------------------------------------------------------- //
// PHYSXSCENEAPI                                                               //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxSceneAPI
///
/// PhysX scene extended parameters.
/// Default PhysX material for the scene can be set by using material bind with purpose physics onto the PhysicsScene
/// prim. For any described attribute @em Fallback @em Value or @em Allowed @em Values below that are text/tokens, the
/// actual token is published and defined in @ref PhysxSchemaTokens. So to set an attribute to the value "rightHanded",
/// use PhysxSchemaTokens->rightHanded as the value.

class PhysxSchemaPhysxSceneAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxSceneAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxSceneAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxSceneAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxSceneAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxSceneAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxSceneAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxSceneAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxSceneAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxSceneAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxSceneAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxSceneAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxSceneAPI>())
        {
            return PhysxSchemaPhysxSceneAPI(prim);
        }
        return PhysxSchemaPhysxSceneAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // BOUNCETHRESHOLD
    // --------------------------------------------------------------------- //
    /// A contact with a relative velocity below this will not bounce.
    /// Range: [0, inf)
    /// Default: 0.2 * tolerancesSpeed
    /// Units: distance / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxScene:bounceThreshold = 0.2` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBounceThresholdAttr() const;

    /// See GetBounceThresholdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBounceThresholdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FRICTIONOFFSETTHRESHOLD
    // --------------------------------------------------------------------- //
    /// A threshold of contact separation distance used to decide if a contact point will experience friction forces.
    /// Range: [0, inf)
    /// Default: 0.04 * tolerancesLength
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxScene:frictionOffsetThreshold = 0.04` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFrictionOffsetThresholdAttr() const;

    /// See GetFrictionOffsetThresholdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFrictionOffsetThresholdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FRICTIONCORRELATIONDISTANCE
    // --------------------------------------------------------------------- //
    /// Friction correlation distance used to decide whether contacts are close enough to be merged into a single
    /// friction anchor point or not. Range: [0, inf) Default: 0.025 * tolerancesLength Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxScene:frictionCorrelationDistance = 0.025` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFrictionCorrelationDistanceAttr() const;

    /// See GetFrictionCorrelationDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFrictionCorrelationDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXBIASCOEFFICIENT
    // --------------------------------------------------------------------- //
    /// The maximum bias coefficient used in the constraint solver.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxScene:maxBiasCoefficient = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxBiasCoefficientAttr() const;

    /// See GetMaxBiasCoefficientAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxBiasCoefficientAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONSYSTEM
    // --------------------------------------------------------------------- //
    /// Collision detection system.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxScene:collisionSystem = "PCM"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | PCM, SAT |

    UsdAttribute GetCollisionSystemAttr() const;

    /// See GetCollisionSystemAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionSystemAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SOLVERTYPE
    // --------------------------------------------------------------------- //
    /// Solver used for the simulation.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxScene:solverType = "TGS"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | PGS, TGS |

    UsdAttribute GetSolverTypeAttr() const;

    /// See GetSolverTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSolverTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BROADPHASETYPE
    // --------------------------------------------------------------------- //
    /// Broad phase algorithm used in the simulation.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxScene:broadphaseType = "GPU"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | GPU, MBP, SAP |

    UsdAttribute GetBroadphaseTypeAttr() const;

    /// See GetBroadphaseTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBroadphaseTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FRICTIONTYPE
    // --------------------------------------------------------------------- //
    /// Friction type used in simulation.
    ///
    /// Note: "oneDirectional" is deprecated.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxScene:frictionType = "patch"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | patch, oneDirectional, twoDirectional |

    UsdAttribute GetFrictionTypeAttr() const;

    /// See GetFrictionTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFrictionTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLECCD
    // --------------------------------------------------------------------- //
    /// Enables a second broad phase check after integration that makes it possible to prevent objects from tunneling
    /// through each other.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxScene:enableCCD = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableCCDAttr() const;

    /// See GetEnableCCDAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableCCDAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLESTABILIZATION
    // --------------------------------------------------------------------- //
    /// Enables additional stabilization pass in solver.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxScene:enableStabilization = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableStabilizationAttr() const;

    /// See GetEnableStabilizationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableStabilizationAttr() const;

public:
    // --------------------------------------------------------------------- //
    // UPDATETYPE
    // --------------------------------------------------------------------- //
    /// Type of update for a PhysX scene.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxScene:updateType = "Synchronous"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | Synchronous, Asynchronous, Disabled |

    UsdAttribute GetUpdateTypeAttr() const;

    /// See GetUpdateTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUpdateTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLEGPUDYNAMICS
    // --------------------------------------------------------------------- //
    /// Enables the GPU dynamics pipeline. Required for GPU only features like deformables.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxScene:enableGPUDynamics = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableGPUDynamicsAttr() const;

    /// See GetEnableGPUDynamicsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableGPUDynamicsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLEENHANCEDDETERMINISM
    // --------------------------------------------------------------------- //
    /// Provides improved determinism at the expense of performance.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxScene:enableEnhancedDeterminism = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableEnhancedDeterminismAttr() const;

    /// See GetEnableEnhancedDeterminismAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableEnhancedDeterminismAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLEEXTERNALFORCESEVERYITERATION
    // --------------------------------------------------------------------- //
    /// Enables greater TGS solver stability - Currently just supported with PhysxParticleSystem gravity application.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxScene:enableExternalForcesEveryIteration = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableExternalForcesEveryIterationAttr() const;

    /// See GetEnableExternalForcesEveryIterationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableExternalForcesEveryIterationAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLESCENEQUERYSUPPORT
    // --------------------------------------------------------------------- //
    /// Enables scene query support for collision shapes.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxScene:enableSceneQuerySupport = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableSceneQuerySupportAttr() const;

    /// See GetEnableSceneQuerySupportAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableSceneQuerySupportAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TIMESTEPSPERSECOND
    // --------------------------------------------------------------------- //
    /// Simulation scene step defined as number of steps per second.
    /// Note that application might cap the number of simulation steps to avoid
    /// running more simulations steps with a low frame rate.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:timeStepsPerSecond = 60` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetTimeStepsPerSecondAttr() const;

    /// See GetTimeStepsPerSecondAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTimeStepsPerSecondAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUTEMPBUFFERCAPACITY
    // --------------------------------------------------------------------- //
    /// Gpu temp buffer capacity.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint64 physxScene:gpuTempBufferCapacity = 16777216` |
    /// | C++ Type | uint64_t |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt64 |

    UsdAttribute GetGpuTempBufferCapacityAttr() const;

    /// See GetGpuTempBufferCapacityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuTempBufferCapacityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUMAXRIGIDCONTACTCOUNT
    // --------------------------------------------------------------------- //
    /// Gpu max rigid contact count.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuMaxRigidContactCount = 524288` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuMaxRigidContactCountAttr() const;

    /// See GetGpuMaxRigidContactCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuMaxRigidContactCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUMAXRIGIDPATCHCOUNT
    // --------------------------------------------------------------------- //
    /// Gpu max rigid patch count.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuMaxRigidPatchCount = 81920` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuMaxRigidPatchCountAttr() const;

    /// See GetGpuMaxRigidPatchCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuMaxRigidPatchCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUHEAPCAPACITY
    // --------------------------------------------------------------------- //
    /// Gpu heap capacity.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuHeapCapacity = 67108864` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuHeapCapacityAttr() const;

    /// See GetGpuHeapCapacityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuHeapCapacityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUFOUNDLOSTPAIRSCAPACITY
    // --------------------------------------------------------------------- //
    /// Gpu found lost pairs capacity.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuFoundLostPairsCapacity = 262144` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuFoundLostPairsCapacityAttr() const;

    /// See GetGpuFoundLostPairsCapacityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuFoundLostPairsCapacityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUFOUNDLOSTAGGREGATEPAIRSCAPACITY
    // --------------------------------------------------------------------- //
    /// Gpu found lost aggregate pairs capacity.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuFoundLostAggregatePairsCapacity = 1024` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuFoundLostAggregatePairsCapacityAttr() const;

    /// See GetGpuFoundLostAggregatePairsCapacityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuFoundLostAggregatePairsCapacityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUTOTALAGGREGATEPAIRSCAPACITY
    // --------------------------------------------------------------------- //
    /// Gpu total aggregate pairs capacity.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuTotalAggregatePairsCapacity = 1024` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuTotalAggregatePairsCapacityAttr() const;

    /// See GetGpuTotalAggregatePairsCapacityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuTotalAggregatePairsCapacityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUMAXSOFTBODYCONTACTS
    // --------------------------------------------------------------------- //
    /// Gpu max soft body contacts.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuMaxSoftBodyContacts = 1048576` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuMaxSoftBodyContactsAttr() const;

    /// See GetGpuMaxSoftBodyContactsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuMaxSoftBodyContactsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUMAXDEFORMABLESURFACECONTACTS
    // --------------------------------------------------------------------- //
    /// Gpu max deformable surface contacts.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuMaxDeformableSurfaceContacts = 1048576` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuMaxDeformableSurfaceContactsAttr() const;

    /// See GetGpuMaxDeformableSurfaceContactsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuMaxDeformableSurfaceContactsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUMAXPARTICLECONTACTS
    // --------------------------------------------------------------------- //
    /// Gpu max particle contacts.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuMaxParticleContacts = 1048576` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuMaxParticleContactsAttr() const;

    /// See GetGpuMaxParticleContactsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuMaxParticleContactsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUMAXHAIRCONTACTS
    // --------------------------------------------------------------------- //
    /// Gpu max hair contacts.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuMaxHairContacts = 1048576` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuMaxHairContactsAttr() const;

    /// See GetGpuMaxHairContactsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuMaxHairContactsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUMAXNUMPARTITIONS
    // --------------------------------------------------------------------- //
    /// Limitation for the partitions in the GPU dynamics pipeline. This variable must be a power of 2. A value greater
    /// than 32 is currently not supported.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuMaxNumPartitions = 8` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuMaxNumPartitionsAttr() const;

    /// See GetGpuMaxNumPartitionsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuMaxNumPartitionsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GPUCOLLISIONSTACKSIZE
    // --------------------------------------------------------------------- //
    /// Gpu collision stack size.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxScene:gpuCollisionStackSize = 67108864` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetGpuCollisionStackSizeAttr() const;

    /// See GetGpuCollisionStackSizeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGpuCollisionStackSizeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INVERTCOLLISIONGROUPFILTER
    // --------------------------------------------------------------------- //
    /// Boolean attribute indicating whether inverted collision group filtering should be used.
    /// By default two collisions, that do have a collisionGroup set, collide with each other. Adding
    /// a collisionGroup into a collisionGroup filtering will mean that the collision between those groups
    /// will be disabled. This boolean attribute does invert the default behavior. Hence two collisions with
    /// defined collisionGroups will not collide with each other by default and one does enable the
    /// collisions between the groups through the "CollisionGroup" filtering.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxScene:invertCollisionGroupFilter = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetInvertCollisionGroupFilterAttr() const;

    /// See GetInvertCollisionGroupFilterAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateInvertCollisionGroupFilterAttr() const;

public:
    // --------------------------------------------------------------------- //
    // REPORTKINEMATICKINEMATICPAIRS
    // --------------------------------------------------------------------- //
    /// Boolean attribute indicating whether kinematic vs kinematic pairs
    /// generate contact reports.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxScene:reportKinematicKinematicPairs = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetReportKinematicKinematicPairsAttr() const;

    /// See GetReportKinematicKinematicPairsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateReportKinematicKinematicPairsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // REPORTKINEMATICSTATICPAIRS
    // --------------------------------------------------------------------- //
    /// Boolean attribute indicating whether kinematic vs static pairs
    /// generate contact reports.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxScene:reportKinematicStaticPairs = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetReportKinematicStaticPairsAttr() const;

    /// See GetReportKinematicStaticPairsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateReportKinematicStaticPairsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MINPOSITIONITERATIONCOUNT
    // --------------------------------------------------------------------- //
    /// Minimum position iteration count for all actors (rigid bodies, cloth, particles etc).
    /// Range: [1, 255]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform uint physxScene:minPositionIterationCount = 1` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetMinPositionIterationCountAttr() const;

    /// See GetMinPositionIterationCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinPositionIterationCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXPOSITIONITERATIONCOUNT
    // --------------------------------------------------------------------- //
    /// Maximum position iteration count for all actors (rigid bodies, cloth, particles etc).
    /// Note that this setting will override solver iteration settings of individual actors that have requested more
    /// iterations. Range: [1, 255]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform uint physxScene:maxPositionIterationCount = 255` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetMaxPositionIterationCountAttr() const;

    /// See GetMaxPositionIterationCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxPositionIterationCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MINVELOCITYITERATIONCOUNT
    // --------------------------------------------------------------------- //
    /// Minimum velocity iteration count for all actors (rigid bodies, cloth, particles etc).
    /// Range: [0, 255]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform uint physxScene:minVelocityIterationCount = 0` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetMinVelocityIterationCountAttr() const;

    /// See GetMinVelocityIterationCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinVelocityIterationCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXVELOCITYITERATIONCOUNT
    // --------------------------------------------------------------------- //
    /// Maximum velocity iteration count for all actors (rigid bodies, cloth, particles etc).
    /// Note that this setting will override solver iteration settings of individual actors that have requested more
    /// iterations. Range: [0, 255]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform uint physxScene:maxVelocityIterationCount = 255` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetMaxVelocityIterationCountAttr() const;

    /// See GetMaxVelocityIterationCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxVelocityIterationCountAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxSceneAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxSceneAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxSceneAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxSceneAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetBounceThresholdAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneBounceThreshold));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateBounceThresholdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneBounceThreshold), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetFrictionOffsetThresholdAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneFrictionOffsetThreshold));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateFrictionOffsetThresholdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneFrictionOffsetThreshold),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetFrictionCorrelationDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneFrictionCorrelationDistance));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateFrictionCorrelationDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneFrictionCorrelationDistance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetMaxBiasCoefficientAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneMaxBiasCoefficient));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateMaxBiasCoefficientAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneMaxBiasCoefficient), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetCollisionSystemAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneCollisionSystem));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateCollisionSystemAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneCollisionSystem), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetSolverTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneSolverType));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateSolverTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneSolverType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetBroadphaseTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneBroadphaseType));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateBroadphaseTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneBroadphaseType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetFrictionTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneFrictionType));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateFrictionTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneFrictionType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetEnableCCDAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableCCD));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateEnableCCDAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableCCD), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetEnableStabilizationAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableStabilization));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateEnableStabilizationAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableStabilization), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetUpdateTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneUpdateType));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateUpdateTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneUpdateType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetEnableGPUDynamicsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableGPUDynamics));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateEnableGPUDynamicsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableGPUDynamics), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetEnableEnhancedDeterminismAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableEnhancedDeterminism));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateEnableEnhancedDeterminismAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableEnhancedDeterminism),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetEnableExternalForcesEveryIterationAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableExternalForcesEveryIteration));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateEnableExternalForcesEveryIterationAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableExternalForcesEveryIteration),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetEnableSceneQuerySupportAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableSceneQuerySupport));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateEnableSceneQuerySupportAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneEnableSceneQuerySupport),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetTimeStepsPerSecondAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneTimeStepsPerSecond));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateTimeStepsPerSecondAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneTimeStepsPerSecond), SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuTempBufferCapacityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuTempBufferCapacity));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuTempBufferCapacityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuTempBufferCapacity),
                                     SdfValueTypeNames->UInt64,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuMaxRigidContactCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxRigidContactCount));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuMaxRigidContactCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxRigidContactCount),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuMaxRigidPatchCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxRigidPatchCount));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuMaxRigidPatchCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxRigidPatchCount), SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuHeapCapacityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuHeapCapacity));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuHeapCapacityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuHeapCapacity), SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuFoundLostPairsCapacityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuFoundLostPairsCapacity));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuFoundLostPairsCapacityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuFoundLostPairsCapacity),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuFoundLostAggregatePairsCapacityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuFoundLostAggregatePairsCapacity));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuFoundLostAggregatePairsCapacityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuFoundLostAggregatePairsCapacity),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuTotalAggregatePairsCapacityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuTotalAggregatePairsCapacity));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuTotalAggregatePairsCapacityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuTotalAggregatePairsCapacity),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuMaxSoftBodyContactsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxSoftBodyContacts));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuMaxSoftBodyContactsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxSoftBodyContacts),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuMaxDeformableSurfaceContactsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxDeformableSurfaceContacts));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuMaxDeformableSurfaceContactsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxDeformableSurfaceContacts),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuMaxParticleContactsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxParticleContacts));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuMaxParticleContactsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxParticleContacts),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuMaxHairContactsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxHairContacts));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuMaxHairContactsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxHairContacts), SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuMaxNumPartitionsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxNumPartitions));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuMaxNumPartitionsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuMaxNumPartitions), SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetGpuCollisionStackSizeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuCollisionStackSize));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateGpuCollisionStackSizeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneGpuCollisionStackSize), SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetInvertCollisionGroupFilterAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneInvertCollisionGroupFilter));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateInvertCollisionGroupFilterAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneInvertCollisionGroupFilter),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetReportKinematicKinematicPairsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneReportKinematicKinematicPairs));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateReportKinematicKinematicPairsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneReportKinematicKinematicPairs),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetReportKinematicStaticPairsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneReportKinematicStaticPairs));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateReportKinematicStaticPairsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneReportKinematicStaticPairs),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetMinPositionIterationCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneMinPositionIterationCount));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateMinPositionIterationCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneMinPositionIterationCount),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetMaxPositionIterationCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneMaxPositionIterationCount));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateMaxPositionIterationCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneMaxPositionIterationCount),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetMinVelocityIterationCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneMinVelocityIterationCount));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateMinVelocityIterationCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneMinVelocityIterationCount),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::GetMaxVelocityIterationCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneMaxVelocityIterationCount));
}

inline UsdAttribute PhysxSchemaPhysxSceneAPI::CreateMaxVelocityIterationCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneMaxVelocityIterationCount),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}


} // namespace usdrt
// ===================================================================== //
// Feel free to add custom code below this line. It will be preserved by
// the code generator.
//
// Just remember to wrap code in the appropriate delimiters:
// 'namespace usdrt {', '}'.
// ===================================================================== //
// --(BEGIN CUSTOM CODE)--
