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

/// @file physxSchema/physxCharacterControllerAPI.h

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
// PHYSXCHARACTERCONTROLLERAPI                                                 //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxCharacterControllerAPI
///
/// PhysxCharacterControllerAPI can be applied to a capsuleGeom. It will turn the capsule into a character controller.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref PhysxSchemaTokens.
/// So to set an attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded
/// as the value.

class PhysxSchemaPhysxCharacterControllerAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxCharacterControllerAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxCharacterControllerAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxCharacterControllerAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxCharacterControllerAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxCharacterControllerAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxCharacterControllerAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxCharacterControllerAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxCharacterControllerAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxCharacterControllerAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxCharacterControllerAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxCharacterControllerAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxCharacterControllerAPI>())
        {
            return PhysxSchemaPhysxCharacterControllerAPI(prim);
        }
        return PhysxSchemaPhysxCharacterControllerAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SLOPELIMIT
    // --------------------------------------------------------------------- //
    /// Slope limit which the CCT can climb. The limit is expressed as the cosine of the desired limit angle.
    /// A value of 0 disables this feature.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCharacterController:slopeLimit = 0.3` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSlopeLimitAttr() const;

    /// See GetSlopeLimitAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSlopeLimitAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MOVETARGET
    // --------------------------------------------------------------------- //
    /// Desired target position that CCT should try to reach.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxCharacterController:moveTarget = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetMoveTargetAttr() const;

    /// See GetMoveTargetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMoveTargetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // UPAXIS
    // --------------------------------------------------------------------- //
    /// Up axis for stepping functionality.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxCharacterController:upAxis = "Z"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | X, Y, Z |

    UsdAttribute GetUpAxisAttr() const;

    /// See GetUpAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUpAxisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // NONWALKABLEMODE
    // --------------------------------------------------------------------- //
    /// The non-walkable mode controls if a character controller slides or not on a non-walkable part.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxCharacterController:nonWalkableMode = "preventClimbing"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | preventClimbing, preventClimbingForceSliding |

    UsdAttribute GetNonWalkableModeAttr() const;

    /// See GetNonWalkableModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNonWalkableModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CLIMBINGMODE
    // --------------------------------------------------------------------- //
    /// The climbing mode.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxCharacterController:climbingMode = "easy"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | easy, constrained |

    UsdAttribute GetClimbingModeAttr() const;

    /// See GetClimbingModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateClimbingModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INVISIBLEWALLHEIGHT
    // --------------------------------------------------------------------- //
    /// Height of invisible walls created around non-walkable triangles.
    /// Range: [0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCharacterController:invisibleWallHeight = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetInvisibleWallHeightAttr() const;

    /// See GetInvisibleWallHeightAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateInvisibleWallHeightAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXJUMPHEIGHT
    // --------------------------------------------------------------------- //
    /// Maximum height a jumping character can reach.
    /// Range: [0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCharacterController:maxJumpHeight = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxJumpHeightAttr() const;

    /// See GetMaxJumpHeightAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxJumpHeightAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CONTACTOFFSET
    // --------------------------------------------------------------------- //
    /// The contact offset used by the controller.
    /// Range: [0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCharacterController:contactOffset = 0.1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetContactOffsetAttr() const;

    /// See GetContactOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateContactOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STEPOFFSET
    // --------------------------------------------------------------------- //
    /// Defines the maximum height of an obstacle which the character can climb.
    /// Range: [0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCharacterController:stepOffset = 0.5` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetStepOffsetAttr() const;

    /// See GetStepOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStepOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SCALECOEFF
    // --------------------------------------------------------------------- //
    /// Scale coefficient for underlying kinematic actor.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCharacterController:scaleCoeff = 0.8` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetScaleCoeffAttr() const;

    /// See GetScaleCoeffAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateScaleCoeffAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VOLUMEGROWTH
    // --------------------------------------------------------------------- //
    /// Cached volume growth.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCharacterController:volumeGrowth = 1.5` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVolumeGrowthAttr() const;

    /// See GetVolumeGrowthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVolumeGrowthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIMULATIONOWNER
    // --------------------------------------------------------------------- //
    /// Single PhysicsScene that simulates this character controller.
    /// By default, this is the first PhysicsScene found in the stage using UsdStage::Traverse().
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

inline const TfToken PhysxSchemaPhysxCharacterControllerAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxCharacterControllerAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxCharacterControllerAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxCharacterControllerAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetSlopeLimitAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerSlopeLimit));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateSlopeLimitAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerSlopeLimit),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetMoveTargetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerMoveTarget));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateMoveTargetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerMoveTarget),
                                     SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetUpAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerUpAxis));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateUpAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerUpAxis), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetNonWalkableModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerNonWalkableMode));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateNonWalkableModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerNonWalkableMode),
                                     SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetClimbingModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerClimbingMode));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateClimbingModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerClimbingMode),
                                     SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetInvisibleWallHeightAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerInvisibleWallHeight));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateInvisibleWallHeightAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerInvisibleWallHeight),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetMaxJumpHeightAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerMaxJumpHeight));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateMaxJumpHeightAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerMaxJumpHeight),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetContactOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerContactOffset));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateContactOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerContactOffset),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetStepOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerStepOffset));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateStepOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerStepOffset),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetScaleCoeffAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerScaleCoeff));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateScaleCoeffAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerScaleCoeff),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::GetVolumeGrowthAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerVolumeGrowth));
}

inline UsdAttribute PhysxSchemaPhysxCharacterControllerAPI::CreateVolumeGrowthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCharacterControllerVolumeGrowth),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxCharacterControllerAPI::GetSimulationOwnerRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxCharacterControllerSimulationOwner);
}

inline UsdRelationship PhysxSchemaPhysxCharacterControllerAPI::CreateSimulationOwnerRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxCharacterControllerSimulationOwner,
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
