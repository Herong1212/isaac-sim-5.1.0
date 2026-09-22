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

/// @file physxSchema/physxVehicleControllerAPI.h

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
// PHYSXVEHICLECONTROLLERAPI                                                   //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleControllerAPI
///
/// PhysX vehicle controller that samples user input to drive the vehicle. Has to be applied to a prim with
/// PhysxVehicleAPI applied.

class PhysxSchemaPhysxVehicleControllerAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleControllerAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleControllerAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleControllerAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleControllerAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleControllerAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleControllerAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleControllerAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleControllerAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleControllerAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleControllerAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleControllerAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleControllerAPI>())
        {
            return PhysxSchemaPhysxVehicleControllerAPI(prim);
        }
        return PhysxSchemaPhysxVehicleControllerAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ACCELERATOR
    // --------------------------------------------------------------------- //
    /// Driven vehicle. Throttle input, 0.0 to 1.0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleController:accelerator = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetAcceleratorAttr() const;

    /// See GetAcceleratorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAcceleratorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BRAKE0
    // --------------------------------------------------------------------- //
    /// Brake control for braking system "brakes0" (see PhysxVehicleBrakesAPI)
    /// that triggers the connected brakes and defines the brake strength.
    /// Value has to be in range [0.0, 1.0].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleController:brake0 = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBrake0Attr() const;

    /// See GetBrake0Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBrake0Attr() const;

public:
    // --------------------------------------------------------------------- //
    // BRAKE1
    // --------------------------------------------------------------------- //
    /// Brake control for braking system "brakes1" (see PhysxVehicleBrakesAPI)
    /// that triggers the connected brakes and defines the brake strength.
    /// Value has to be in range [0.0, 1.0].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleController:brake1 = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBrake1Attr() const;

    /// See GetBrake1Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBrake1Attr() const;

public:
    // --------------------------------------------------------------------- //
    // BRAKE
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use brake0/brake1 instead.
    ///
    /// Driven vehicle. Brake input, 0.0 to 1.0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleController:brake = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBrakeAttr() const;

    /// See GetBrakeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBrakeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // HANDBRAKE
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use brake0/brake1 instead.
    ///
    /// Driven vehicle. Handbrake input, 0.0 to 1.0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleController:handbrake = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetHandbrakeAttr() const;

    /// See GetHandbrakeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateHandbrakeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STEER
    // --------------------------------------------------------------------- //
    /// Steer control for the steering system (see PhysxVehicleSteeringAPI).
    /// Defines the extent of the wheels' steer angles with respect to the
    /// maximum steer angle. Value has to be in range [-1.0, 1.0].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleController:steer = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSteerAttr() const;

    /// See GetSteerAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSteerAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STEERLEFT
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use steer instead.
    ///
    /// Driven vehicle. Left steering input. 0.0 to 1.0. Net steering is the aggregate of steerRight and steerLeft.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleController:steerLeft = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSteerLeftAttr() const;

    /// See GetSteerLeftAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSteerLeftAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STEERRIGHT
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use steer instead.
    ///
    /// Driven vehicle. Right steering input, 0.0 to 1.0. Net steering is the aggregate of steerRight and steerLeft.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleController:steerRight = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSteerRightAttr() const;

    /// See GetSteerRightAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSteerRightAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TARGETGEAR
    // --------------------------------------------------------------------- //
    /// Driven vehicle. Desired gear to shift into. -1 = Reverse, 0 = Neutral, 1 = First etc.
    /// The special value 255 is used to denote automatic forward gear shifting (similar to <D> in
    /// automatic transmissions).
    ///
    /// Note: if set to automatic gear shifting, the vehicle is expected to have an autobox
    /// defined (see PhysxVehicleAutoGearBoxAPI).
    ///
    /// Note: please be aware that the target gear definition differs from the PhysX vehicle API.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxVehicleController:targetGear = 255` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetTargetGearAttr() const;

    /// See GetTargetGearAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTargetGearAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleControllerAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleControllerAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleControllerAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleControllerAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::GetAcceleratorAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerAccelerator));
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::CreateAcceleratorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerAccelerator),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::GetBrake0Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerBrake0));
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::CreateBrake0Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerBrake0), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::GetBrake1Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerBrake1));
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::CreateBrake1Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerBrake1), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::GetBrakeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerBrake));
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::CreateBrakeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerBrake), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::GetHandbrakeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerHandbrake));
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::CreateHandbrakeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerHandbrake),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::GetSteerAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerSteer));
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::CreateSteerAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerSteer), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::GetSteerLeftAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerSteerLeft));
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::CreateSteerLeftAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerSteerLeft),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::GetSteerRightAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerSteerRight));
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::CreateSteerRightAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerSteerRight),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::GetTargetGearAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerTargetGear));
}

inline UsdAttribute PhysxSchemaPhysxVehicleControllerAPI::CreateTargetGearAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleControllerTargetGear), SdfValueTypeNames->Int,
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
