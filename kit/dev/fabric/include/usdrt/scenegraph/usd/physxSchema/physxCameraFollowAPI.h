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

/// @file physxSchema/physxCameraFollowAPI.h

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
// PHYSXCAMERAFOLLOWAPI                                                        //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxCameraFollowAPI
///
/// PhysX camera that follows behind the subject as it moves.

class PhysxSchemaPhysxCameraFollowAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxCameraFollowAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxCameraFollowAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxCameraFollowAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxCameraFollowAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxCameraFollowAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxCameraFollowAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxCameraFollowAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxCameraFollowAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxCameraFollowAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxCameraFollowAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxCameraFollowAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxCameraFollowAPI>())
        {
            return PhysxSchemaPhysxCameraFollowAPI(prim);
        }
        return PhysxSchemaPhysxCameraFollowAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // YAWANGLE
    // --------------------------------------------------------------------- //
    /// The yaw angle of the follow vector around the subject. Zero is directly behind the subject. e.g. 0 degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:yawAngle` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetYawAngleAttr() const;

    /// See GetYawAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateYawAngleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PITCHANGLE
    // --------------------------------------------------------------------- //
    /// The pitch angle of the follow vector around the subject. Zero is directly behind the subject. e.g. 15 degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:pitchAngle` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetPitchAngleAttr() const;

    /// See GetPitchAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePitchAngleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PITCHANGLETIMECONSTANT
    // --------------------------------------------------------------------- //
    /// Time constant to filter the pitch angle, in seconds. Used to pitch the camera up and down when driving up or
    /// down hills. e.g. 0.2 seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:pitchAngleTimeConstant` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetPitchAngleTimeConstantAttr() const;

    /// See GetPitchAngleTimeConstantAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePitchAngleTimeConstantAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SLOWSPEEDPITCHANGLESCALE
    // --------------------------------------------------------------------- //
    /// Scale of the camera pitch angle at slow speed. This lowers the camera behind the subject at slow speeds. e.g.
    /// 0.5
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:slowSpeedPitchAngleScale` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSlowSpeedPitchAngleScaleAttr() const;

    /// See GetSlowSpeedPitchAngleScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSlowSpeedPitchAngleScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SLOWPITCHANGLESPEED
    // --------------------------------------------------------------------- //
    /// Scale of the camera pitch angle at slow speed. This lowers the camera behind the subject at slow speeds. e.g.
    /// 1000 cm/sec
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:slowPitchAngleSpeed` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSlowPitchAngleSpeedAttr() const;

    /// See GetSlowPitchAngleSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSlowPitchAngleSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VELOCITYNORMALMINSPEED
    // --------------------------------------------------------------------- //
    /// The minimum speed, below which, the subject look vector must be used because the normalized velocity vector is
    /// too erratic. e.g. 600.0 cm/sec
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:velocityNormalMinSpeed` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVelocityNormalMinSpeedAttr() const;

    /// See GetVelocityNormalMinSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVelocityNormalMinSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FOLLOWMINSPEED
    // --------------------------------------------------------------------- //
    /// The minimum speed used for a linear interpolation to compute the follow distance of the camera. e.g. 300.0
    /// cm/sec
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:followMinSpeed` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFollowMinSpeedAttr() const;

    /// See GetFollowMinSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFollowMinSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FOLLOWMINDISTANCE
    // --------------------------------------------------------------------- //
    /// The minimum distance used for a linear interpolation to compute the follow distance of the camera. e.g. 1500.0
    /// cm
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:followMinDistance` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFollowMinDistanceAttr() const;

    /// See GetFollowMinDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFollowMinDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FOLLOWMAXSPEED
    // --------------------------------------------------------------------- //
    /// The maximum speed used for a linear interpolation to compute the follow distance of the camera. e.g. 3000.0
    /// cm/sec
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:followMaxSpeed` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFollowMaxSpeedAttr() const;

    /// See GetFollowMaxSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFollowMaxSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FOLLOWMAXDISTANCE
    // --------------------------------------------------------------------- //
    /// The maximum distance used for a linear interpolation to compute the follow distance of the camera. e.g. 1000.0
    /// cm
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:followMaxDistance` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFollowMaxDistanceAttr() const;

    /// See GetFollowMaxDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFollowMaxDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // YAWRATETIMECONSTANT
    // --------------------------------------------------------------------- //
    /// Time constant to filter the subject yaw rate, in seconds. Use to look into turns. e.g. 0.2 sec
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:yawRateTimeConstant` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetYawRateTimeConstantAttr() const;

    /// See GetYawRateTimeConstantAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateYawRateTimeConstantAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FOLLOWTURNRATEGAIN
    // --------------------------------------------------------------------- //
    /// A scale factor that multiplies the filtered yaw rate to yaw the camera position behind the subject. Can be any
    /// positive or negative number. e.g. 0.2
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:followTurnRateGain` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetFollowTurnRateGainAttr() const;

    /// See GetFollowTurnRateGainAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFollowTurnRateGainAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CAMERAPOSITIONTIMECONSTANT
    // --------------------------------------------------------------------- //
    /// Filter time constant for the position of the camera for each axis, in seconds. e.g. (0.5 sec, 0.1 sec, 0.5 sec)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxFollowCamera:cameraPositionTimeConstant` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetCameraPositionTimeConstantAttr() const;

    /// See GetCameraPositionTimeConstantAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCameraPositionTimeConstantAttr() const;

public:
    // --------------------------------------------------------------------- //
    // POSITIONOFFSET
    // --------------------------------------------------------------------- //
    /// Position offset from the subject center of mass from which the camera follow vector and look vector are
    /// computed. e.g. (0.0 cm, 10.0 cm, 0.0 cm)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxFollowCamera:positionOffset` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetPositionOffsetAttr() const;

    /// See GetPositionOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePositionOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOOKAHEADMINSPEED
    // --------------------------------------------------------------------- //
    /// The minimum speed used for a linear interpolation to compute the look ahead distance of the camera look point.
    /// e.g. 0.0 cm/sec
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:lookAheadMinSpeed` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLookAheadMinSpeedAttr() const;

    /// See GetLookAheadMinSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLookAheadMinSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOOKAHEADMINDISTANCE
    // --------------------------------------------------------------------- //
    /// The minimum distance used for a linear interpolation to compute the look ahead distance of the camera look
    /// point. e.g. 0.0 cm
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:lookAheadMinDistance` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLookAheadMinDistanceAttr() const;

    /// See GetLookAheadMinDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLookAheadMinDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOOKAHEADMAXSPEED
    // --------------------------------------------------------------------- //
    /// The maximum speed used for a linear interpolation to compute the look ahead distance of the camera look point.
    /// e.g. 2000.0 cm
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:lookAheadMaxSpeed` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLookAheadMaxSpeedAttr() const;

    /// See GetLookAheadMaxSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLookAheadMaxSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOOKAHEADMAXDISTANCE
    // --------------------------------------------------------------------- //
    /// The maximum distance used for a linear interpolation to compute the look ahead distance of the camera look
    /// point. e.g.  500.0 cm
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowFollowCamera:lookAheadMaxDistance` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLookAheadMaxDistanceAttr() const;

    /// See GetLookAheadMaxDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLookAheadMaxDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOOKAHEADTURNRATEGAIN
    // --------------------------------------------------------------------- //
    /// A scale factor that multiplies the filtered yaw rate to yaw the camera look point left or right. Can be any
    /// positive or negative number. e.g. 0.2
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:lookAheadTurnRateGain` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLookAheadTurnRateGainAttr() const;

    /// See GetLookAheadTurnRateGainAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLookAheadTurnRateGainAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOOKPOSITIONHEIGHT
    // --------------------------------------------------------------------- //
    /// Distance to elevate the camera look point. e.g. 50.0 cm
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxFollowCamera:lookPositionHeight` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLookPositionHeightAttr() const;

    /// See GetLookPositionHeightAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLookPositionHeightAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOOKPOSITIONTIMECONSTANT
    // --------------------------------------------------------------------- //
    /// Filter time constant for the camera look point, in seconds. e.g. (0.2 sec, 0.5 sec, 0.2 sec)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxFollowCamera:lookPositionTimeConstant` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetLookPositionTimeConstantAttr() const;

    /// See GetLookPositionTimeConstantAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLookPositionTimeConstantAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxCameraFollowAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxCameraFollowAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxCameraFollowAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxCameraFollowAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetYawAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraYawAngle));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateYawAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraYawAngle), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetPitchAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraPitchAngle));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreatePitchAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraPitchAngle), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetPitchAngleTimeConstantAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraPitchAngleTimeConstant));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreatePitchAngleTimeConstantAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraPitchAngleTimeConstant),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetSlowSpeedPitchAngleScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraSlowSpeedPitchAngleScale));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateSlowSpeedPitchAngleScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraSlowSpeedPitchAngleScale),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetSlowPitchAngleSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraSlowPitchAngleSpeed));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateSlowPitchAngleSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraSlowPitchAngleSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetVelocityNormalMinSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraVelocityNormalMinSpeed));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateVelocityNormalMinSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraVelocityNormalMinSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetFollowMinSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraFollowMinSpeed));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateFollowMinSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraFollowMinSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetFollowMinDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraFollowMinDistance));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateFollowMinDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraFollowMinDistance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetFollowMaxSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraFollowMaxSpeed));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateFollowMaxSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraFollowMaxSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetFollowMaxDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraFollowMaxDistance));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateFollowMaxDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraFollowMaxDistance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetYawRateTimeConstantAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraYawRateTimeConstant));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateYawRateTimeConstantAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraYawRateTimeConstant),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetFollowTurnRateGainAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraFollowTurnRateGain));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateFollowTurnRateGainAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraFollowTurnRateGain),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetCameraPositionTimeConstantAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraCameraPositionTimeConstant));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateCameraPositionTimeConstantAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraCameraPositionTimeConstant),
                                     SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetPositionOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraPositionOffset));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreatePositionOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraPositionOffset),
                                     SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetLookAheadMinSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookAheadMinSpeed));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateLookAheadMinSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookAheadMinSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetLookAheadMinDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookAheadMinDistance));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateLookAheadMinDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookAheadMinDistance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetLookAheadMaxSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookAheadMaxSpeed));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateLookAheadMaxSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookAheadMaxSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetLookAheadMaxDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowFollowCameraLookAheadMaxDistance));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateLookAheadMaxDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowFollowCameraLookAheadMaxDistance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetLookAheadTurnRateGainAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookAheadTurnRateGain));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateLookAheadTurnRateGainAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookAheadTurnRateGain),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetLookPositionHeightAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookPositionHeight));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateLookPositionHeightAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookPositionHeight),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::GetLookPositionTimeConstantAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookPositionTimeConstant));
}

inline UsdAttribute PhysxSchemaPhysxCameraFollowAPI::CreateLookPositionTimeConstantAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxFollowCameraLookPositionTimeConstant),
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
