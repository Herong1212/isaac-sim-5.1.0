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

/// @file physxSchema/physxDeformableAPI.h

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
// PHYSXDEFORMABLEAPI                                                          //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxDeformableAPI
///
/// Do not apply. Base API that provides attributes common to both deformable bodies and surfaces.
/// Derived APIs are applied to UsdGeomMesh in order to create a deformable physics object.
/// Note that the UsdGeomMesh points attribute becomes a read-only attribute for a deformable as the mesh is driven by
/// the simulation.
///

class PhysxSchemaPhysxDeformableAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxDeformableAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxDeformableAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxDeformableAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxDeformableAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxDeformableAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxDeformableAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxDeformableAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxDeformableAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxDeformableAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxDeformableAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxDeformableAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxDeformableAPI>())
        {
            return PhysxSchemaPhysxDeformableAPI(prim);
        }
        return PhysxSchemaPhysxDeformableAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DEFORMABLEENABLED
    // --------------------------------------------------------------------- //
    /// Enable or disable the deformable object.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxDeformable:deformableEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetDeformableEnabledAttr() const;

    /// See GetDeformableEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDeformableEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SOLVERPOSITIONITERATIONCOUNT
    // --------------------------------------------------------------------- //
    /// Number of solver position iterations per time step.
    /// Range: [1, 255]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxDeformable:solverPositionIterationCount = 16` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetSolverPositionIterationCountAttr() const;

    /// See GetSolverPositionIterationCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSolverPositionIterationCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VERTEXVELOCITYDAMPING
    // --------------------------------------------------------------------- //
    /// Artificial damping on the vertex velocity, which may approximate aerodynamic drag.
    /// Range: [0, inf)
    /// Units: 1/seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformable:vertexVelocityDamping = 0.005` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVertexVelocityDampingAttr() const;

    /// See GetVertexVelocityDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVertexVelocityDampingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SLEEPDAMPING
    // --------------------------------------------------------------------- //
    /// Additional damping term if vertex velocity drops below settlingThreshold.
    /// Range: [0, inf)
    /// Units: 1/seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformable:sleepDamping = 10` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSleepDampingAttr() const;

    /// See GetSleepDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSleepDampingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SLEEPTHRESHOLD
    // --------------------------------------------------------------------- //
    /// Velocity threshold under which the vertex becomes a candidate for sleeping.
    /// Range: [0, inf)
    /// Units: distance/seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformable:sleepThreshold = 0.05` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSleepThresholdAttr() const;

    /// See GetSleepThresholdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSleepThresholdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SETTLINGTHRESHOLD
    // --------------------------------------------------------------------- //
    /// Threshold vertex velocity under which sleep damping is applied in addition to velocity damping.
    /// Range: [0, inf]
    /// Units: distance/seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformable:settlingThreshold = 0.1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSettlingThresholdAttr() const;

    /// See GetSettlingThresholdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSettlingThresholdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXDEPENETRATIONVELOCITY
    // --------------------------------------------------------------------- //
    /// The maximum velocity permitted to be introduced by the solver to depenetrate intersections.
    /// Range: [0, inf)
    /// Units: distance / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformable:maxDepenetrationVelocity = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxDepenetrationVelocityAttr() const;

    /// See GetMaxDepenetrationVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxDepenetrationVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SELFCOLLISION
    // --------------------------------------------------------------------- //
    /// Enables self collisions on the deformable, preventing self intersections.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxDeformable:selfCollision = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetSelfCollisionAttr() const;

    /// See GetSelfCollisionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSelfCollisionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SELFCOLLISIONFILTERDISTANCE
    // --------------------------------------------------------------------- //
    /// Distance under which self-collisions are disabled. Default value -inf means default is picked by the simulation.
    /// Range: [2*physxCollision:restOffset, max_float]
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformable:selfCollisionFilterDistance = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSelfCollisionFilterDistanceAttr() const;

    /// See GetSelfCollisionFilterDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSelfCollisionFilterDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLECCD
    // --------------------------------------------------------------------- //
    /// Distance based CCD.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxDeformable:enableCCD = 0` |
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
    // RESTPOINTS
    // --------------------------------------------------------------------- //
    /// Rest points of the UsdGeomMesh in local coordinates.
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] physxDeformable:restPoints` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetRestPointsAttr() const;

    /// See GetRestPointsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRestPointsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIMULATIONVELOCITIES
    // --------------------------------------------------------------------- //
    /// Simulation mesh vertex velocities in local coordinates.
    /// Units: distance / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] physxDeformable:simulationVelocities` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetSimulationVelocitiesAttr() const;

    /// See GetSimulationVelocitiesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSimulationVelocitiesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIMULATIONINDICES
    // --------------------------------------------------------------------- //
    /// Simulation mesh indices.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int[] physxDeformable:simulationIndices` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSimulationIndicesAttr() const;

    /// See GetSimulationIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSimulationIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIMULATIONOWNER
    // --------------------------------------------------------------------- //
    /// Single PhysicsScene that simulates this deformable. By default,
    /// this is the first PhysicsScene found in the stage using UsdStage::Traverse().
    ///
    UsdRelationship GetSimulationOwnerRel() const;

    /// See GetSimulationOwnerRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateSimulationOwnerRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxDeformableAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxDeformableAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxDeformableAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxDeformableAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetDeformableEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableDeformableEnabled));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateDeformableEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableDeformableEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetSolverPositionIterationCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSolverPositionIterationCount));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateSolverPositionIterationCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSolverPositionIterationCount),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetVertexVelocityDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableVertexVelocityDamping));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateVertexVelocityDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableVertexVelocityDamping),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetSleepDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSleepDamping));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateSleepDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSleepDamping), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetSleepThresholdAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSleepThreshold));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateSleepThresholdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSleepThreshold), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetSettlingThresholdAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSettlingThreshold));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateSettlingThresholdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSettlingThreshold),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetMaxDepenetrationVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableMaxDepenetrationVelocity));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateMaxDepenetrationVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableMaxDepenetrationVelocity),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetSelfCollisionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSelfCollision));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateSelfCollisionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSelfCollision), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetSelfCollisionFilterDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSelfCollisionFilterDistance));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateSelfCollisionFilterDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSelfCollisionFilterDistance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetEnableCCDAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableEnableCCD));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateEnableCCDAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableEnableCCD), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetRestPointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableRestPoints));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateRestPointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableRestPoints),
                                     SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetSimulationVelocitiesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSimulationVelocities));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateSimulationVelocitiesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSimulationVelocities),
                                     SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::GetSimulationIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSimulationIndices));
}

inline UsdAttribute PhysxSchemaPhysxDeformableAPI::CreateSimulationIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSimulationIndices),
                                     SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxDeformableAPI::GetSimulationOwnerRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxDeformableSimulationOwner);
}

inline UsdRelationship PhysxSchemaPhysxDeformableAPI::CreateSimulationOwnerRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxDeformableSimulationOwner,
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
