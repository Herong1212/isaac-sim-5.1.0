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

/// @file physxSchema/physxCameraDroneAPI.h

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
// PHYSXCAMERADRONEAPI                                                         //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxCameraDroneAPI
///
/// PhysX drone camera that follows its subject from the air as it drives.

class PhysxSchemaPhysxCameraDroneAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxCameraDroneAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxCameraDroneAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxCameraDroneAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxCameraDroneAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxCameraDroneAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxCameraDroneAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxCameraDroneAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxCameraDroneAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxCameraDroneAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxCameraDroneAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxCameraDroneAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxCameraDroneAPI>())
        {
            return PhysxSchemaPhysxCameraDroneAPI(prim);
        }
        return PhysxSchemaPhysxCameraDroneAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FOLLOWHEIGHT
    // --------------------------------------------------------------------- //
    /// The height above the subject that the drone attmepts to maintain. e.g. 15 meters
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDroneCamera:followHeight` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFollowHeightAttr() const;

    /// See GetFollowHeightAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFollowHeightAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FOLLOWDISTANCE
    // --------------------------------------------------------------------- //
    /// The distance from the subject that the drone attempts to maintain. e.g. 30 meters
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDroneCamera:followDistance` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFollowDistanceAttr() const;

    /// See GetFollowDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFollowDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXDISTANCE
    // --------------------------------------------------------------------- //
    /// The maximum distance allowed from the subject before the drone resets to the target position. e.g. 100 meters
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDroneCamera:maxDistance` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxDistanceAttr() const;

    /// See GetMaxDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXSPEED
    // --------------------------------------------------------------------- //
    /// The maximum speed the drone is allowed to move. e.g. 20.0 meters/second
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDroneCamera:maxSpeed` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxSpeedAttr() const;

    /// See GetMaxSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // HORIZONTALVELOCITYGAIN
    // --------------------------------------------------------------------- //
    /// The higher the gain, the faster the drone will accelerate towards the target position. e.g. 1.0
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDroneCamera:horizontalVelocityGain` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetHorizontalVelocityGainAttr() const;

    /// See GetHorizontalVelocityGainAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateHorizontalVelocityGainAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VERTICALVELOCITYGAIN
    // --------------------------------------------------------------------- //
    /// The higher the gain, the higher the climb or descent rate of the drone to get to the target altitude. e.g. 1.0
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDroneCamera:verticalVelocityGain` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVerticalVelocityGainAttr() const;

    /// See GetVerticalVelocityGainAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVerticalVelocityGainAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FEEDFORWARDVELOCITYGAIN
    // --------------------------------------------------------------------- //
    /// The higher the gain, the more closely the drone will match the velocity of the subject and the more connected it
    /// will appear. e.g. 0.1
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDroneCamera:feedForwardVelocityGain` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFeedForwardVelocityGainAttr() const;

    /// See GetFeedForwardVelocityGainAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFeedForwardVelocityGainAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VELOCITYFILTERTIMECONSTANT
    // --------------------------------------------------------------------- //
    /// The velocity of the drone is filtered to make it appear as if it is accelerating. e.g. 1.0 seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDroneCamera:velocityFilterTimeConstant` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVelocityFilterTimeConstantAttr() const;

    /// See GetVelocityFilterTimeConstantAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVelocityFilterTimeConstantAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ROTATIONFILTERTIMECONSTANT
    // --------------------------------------------------------------------- //
    /// The angular velocity of the drone is filtered to make it appear as if it is accelerating. e.g. 0.2 seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDroneCamera:rotationFilterTimeConstant` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRotationFilterTimeConstantAttr() const;

    /// See GetRotationFilterTimeConstantAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRotationFilterTimeConstantAttr() const;

public:
    // --------------------------------------------------------------------- //
    // POSITIONOFFSET
    // --------------------------------------------------------------------- //
    /// An offset vector from the subject origin at which the drone looks. e.g. (0.0 m, 0.0 m, 0.0 m)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxDroneCamera:positionOffset` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetPositionOffsetAttr() const;

    /// See GetPositionOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePositionOffsetAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxCameraDroneAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxCameraDroneAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxCameraDroneAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxCameraDroneAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::GetFollowHeightAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraFollowHeight));
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::CreateFollowHeightAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraFollowHeight), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::GetFollowDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraFollowDistance));
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::CreateFollowDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraFollowDistance), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::GetMaxDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraMaxDistance));
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::CreateMaxDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraMaxDistance), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::GetMaxSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraMaxSpeed));
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::CreateMaxSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraMaxSpeed), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::GetHorizontalVelocityGainAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraHorizontalVelocityGain));
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::CreateHorizontalVelocityGainAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraHorizontalVelocityGain),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::GetVerticalVelocityGainAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraVerticalVelocityGain));
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::CreateVerticalVelocityGainAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraVerticalVelocityGain),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::GetFeedForwardVelocityGainAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraFeedForwardVelocityGain));
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::CreateFeedForwardVelocityGainAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraFeedForwardVelocityGain),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::GetVelocityFilterTimeConstantAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraVelocityFilterTimeConstant));
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::CreateVelocityFilterTimeConstantAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraVelocityFilterTimeConstant),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::GetRotationFilterTimeConstantAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraRotationFilterTimeConstant));
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::CreateRotationFilterTimeConstantAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraRotationFilterTimeConstant),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::GetPositionOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraPositionOffset));
}

inline UsdAttribute PhysxSchemaPhysxCameraDroneAPI::CreatePositionOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDroneCameraPositionOffset),
                                     SdfValueTypeNames->Float3,
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
