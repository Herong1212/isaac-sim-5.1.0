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

/// @file physxSchema/physxCameraFollowLookAPI.h

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
// PHYSXCAMERAFOLLOWLOOKAPI                                                    //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxCameraFollowLookAPI
///
/// PhysX camera that follows behind the subject's forward vector as it moves. Assumes the subject is always upright and
/// does not roll.

class PhysxSchemaPhysxCameraFollowLookAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxCameraFollowLookAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxCameraFollowLookAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxCameraFollowLookAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxCameraFollowLookAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxCameraFollowLookAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxCameraFollowLookAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxCameraFollowLookAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxCameraFollowLookAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxCameraFollowLookAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxCameraFollowLookAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxCameraFollowLookAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxCameraFollowLookAPI>())
        {
            return PhysxSchemaPhysxCameraFollowLookAPI(prim);
        }
        return PhysxSchemaPhysxCameraFollowLookAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DOWNHILLGROUNDANGLE
    // --------------------------------------------------------------------- //
    /// The minimum pitch angle of the terrain used for a linear interpolation to adjust the pitch of the camera. e.g.
    /// -45.0 degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowLookCamera:downHillGroundAngle` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDownHillGroundAngleAttr() const;

    /// See GetDownHillGroundAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDownHillGroundAngleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DOWNHILLGROUNDPITCH
    // --------------------------------------------------------------------- //
    /// The minimum pitch angle of the camera used for a linear interpolation to adjust the pitch of the camera.
    /// e.g. 10.0 degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowLookCamera:downHillGroundPitch` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDownHillGroundPitchAttr() const;

    /// See GetDownHillGroundPitchAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDownHillGroundPitchAttr() const;

public:
    // --------------------------------------------------------------------- //
    // UPHILLGROUNDANGLE
    // --------------------------------------------------------------------- //
    /// The maximum pitch angle of the terrain used for a linear interpolation to adjust the pitch of the camera.
    /// e.g. 45.0 degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowLookCamera:upHillGroundAngle` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetUpHillGroundAngleAttr() const;

    /// See GetUpHillGroundAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUpHillGroundAngleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // UPHILLGROUNDPITCH
    // --------------------------------------------------------------------- //
    /// The maximum pitch angle of the camera used for a linear interpolation to adjust the pitch of the camera.
    /// e.g. 10.0 degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowLookCamera:upHillGroundPitch` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetUpHillGroundPitchAttr() const;

    /// See GetUpHillGroundPitchAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUpHillGroundPitchAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VELOCITYBLENDTIMECONSTANT
    // --------------------------------------------------------------------- //
    /// Filter time constant to blend between the look and velocity vectors, in seconds. e.g. 0.1 seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowLookCamera:velocityBlendTimeConstant` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVelocityBlendTimeConstantAttr() const;

    /// See GetVelocityBlendTimeConstantAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVelocityBlendTimeConstantAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FOLLOWREVERSESPEED
    // --------------------------------------------------------------------- //
    /// The positive, maximum speed, when driving in reverse, used for a linear interpolation to compute the follow
    /// distance of the camera. e.g. 1500.0 cm/sec
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowLookCamera:followReverseSpeed` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFollowReverseSpeedAttr() const;

    /// See GetFollowReverseSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFollowReverseSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FOLLOWREVERSEDISTANCE
    // --------------------------------------------------------------------- //
    /// The maximum distance, when driving in reverse, used for a linear interpolation to compute the follow distance of
    /// the camera. e.g. 3000.0 cm
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowLookCamera:followReverseDistance` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFollowReverseDistanceAttr() const;

    /// See GetFollowReverseDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFollowReverseDistanceAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxCameraFollowLookAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxCameraFollowLookAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxCameraFollowLookAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxCameraFollowLookAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::GetDownHillGroundAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraDownHillGroundAngle));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::CreateDownHillGroundAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraDownHillGroundAngle),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::GetDownHillGroundPitchAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraDownHillGroundPitch));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::CreateDownHillGroundPitchAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraDownHillGroundPitch),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::GetUpHillGroundAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraUpHillGroundAngle));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::CreateUpHillGroundAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraUpHillGroundAngle),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::GetUpHillGroundPitchAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraUpHillGroundPitch));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::CreateUpHillGroundPitchAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraUpHillGroundPitch),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::GetVelocityBlendTimeConstantAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraVelocityBlendTimeConstant));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::CreateVelocityBlendTimeConstantAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraVelocityBlendTimeConstant),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::GetFollowReverseSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraFollowReverseSpeed));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::CreateFollowReverseSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraFollowReverseSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::GetFollowReverseDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraFollowReverseDistance));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowLookAPI::CreateFollowReverseDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowLookCameraFollowReverseDistance),
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
