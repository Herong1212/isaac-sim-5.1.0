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

/// @file physxSchema/physxDeformableSurfaceAPI.h

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
// PHYSXDEFORMABLESURFACEAPI                                                   //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxDeformableSurfaceAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to a UsdGeomMesh that is to be simulated as a deformable surface.
/// See PhysxDeformableAPI for information on how to define the deformable surface's material properties.

class PhysxSchemaPhysxDeformableSurfaceAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxDeformableSurfaceAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxDeformableSurfaceAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxDeformableSurfaceAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxDeformableSurfaceAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxDeformableSurfaceAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxDeformableSurfaceAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxDeformableSurfaceAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxDeformableSurfaceAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxDeformableSurfaceAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxDeformableSurfaceAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxDeformableSurfaceAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxDeformableSurfaceAPI>())
        {
            return PhysxSchemaPhysxDeformableSurfaceAPI(prim);
        }
        return PhysxSchemaPhysxDeformableSurfaceAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FLATTENINGENABLED
    // --------------------------------------------------------------------- //
    /// If enabled, bending forces are applied such that the surface flattens, i.e., neighboring triangles become
    /// coplanar. If disabled, the forces drive toward the bend at the rest state.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxDeformableSurface:flatteningEnabled = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetFlatteningEnabledAttr() const;

    /// See GetFlatteningEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFlatteningEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BENDINGSTIFFNESSSCALE
    // --------------------------------------------------------------------- //
    /// Scales bending stiffness computed from Young's modulus, Poisson's ratio, and the cloth thickness.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableSurface:bendingStiffnessScale = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBendingStiffnessScaleAttr() const;

    /// See GetBendingStiffnessScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBendingStiffnessScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONPAIRUPDATEFREQUENCY
    // --------------------------------------------------------------------- //
    /// Determines how often collision pairs are updated in each time step.
    /// By default, the pairs of contact points are computed only at the beginning of each time step, and the pairs are
    /// kept during the time step. Increasing this value will update the contact pairs more frequently providing better
    /// contact points, e.g., 2 means collision pairs are updated twice in each time step: at the beginning of the time
    /// step, and in the middle of the time step (i.e., at the middle solver iteration). Range [1,
    /// solverPositionIterationCount/2]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxDeformableSurface:collisionPairUpdateFrequency = 1` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetCollisionPairUpdateFrequencyAttr() const;

    /// See GetCollisionPairUpdateFrequencyAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionPairUpdateFrequencyAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONITERATIONMULTIPLIER
    // --------------------------------------------------------------------- //
    /// Determines how many collision subiterations are used in each solver iteration.
    /// By defualt, collision constraints are applied once in each solver iteration,
    /// and increasing this value will apply collision constraints more frequently in each solver iteration,
    /// e.g., 2 means collision constraints are applied twice in each solver iteration (thus, the collision constraints
    /// are applied 2 x solverPositionIterationCount times in each time step). Increasing this value does not update
    /// collision pairs more frequently, see collisionPairUpdateFrequency. Range [1, solverPositionIterationCount/2]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uint physxDeformableSurface:collisionIterationMultiplier = 1` |
    /// | C++ Type | unsigned int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->UInt |

    UsdAttribute GetCollisionIterationMultiplierAttr() const;

    /// See GetCollisionIterationMultiplierAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionIterationMultiplierAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXVELOCITY
    // --------------------------------------------------------------------- //
    /// Maximum velocity. The velocity of each vertex is clamped by the max velocity.
    /// Range: [0, inf)
    /// Units: distance / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableSurface:maxVelocity = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxVelocityAttr() const;

    /// See GetMaxVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxVelocityAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxDeformableSurfaceAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxDeformableSurfaceAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxDeformableSurfaceAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxDeformableSurfaceAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceAPI::GetFlatteningEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceFlatteningEnabled));
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceAPI::CreateFlatteningEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceFlatteningEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceAPI::GetBendingStiffnessScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceBendingStiffnessScale));
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceAPI::CreateBendingStiffnessScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceBendingStiffnessScale),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceAPI::GetCollisionPairUpdateFrequencyAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceCollisionPairUpdateFrequency));
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceAPI::CreateCollisionPairUpdateFrequencyAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceCollisionPairUpdateFrequency),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceAPI::GetCollisionIterationMultiplierAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceCollisionIterationMultiplier));
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceAPI::CreateCollisionIterationMultiplierAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceCollisionIterationMultiplier),
                                     SdfValueTypeNames->UInt,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceAPI::GetMaxVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaxVelocity));
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceAPI::CreateMaxVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaxVelocity),
                                     SdfValueTypeNames->Float,
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
