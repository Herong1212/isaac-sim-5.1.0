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

/// @file physxSchema/physxVehicleSuspensionAPI.h

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
// PHYSXVEHICLESUSPENSIONAPI                                                   //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleSuspensionAPI
///
/// Properties of a PhysX vehicle wheel suspension. If the suspension setup does not need to be shared
/// among vehicle instances, it can be applied to the prim which has PhysxVehicleWheelAttachmentAPI
/// applied. If the intent is to share the suspension setup, PhysxVehicleSuspensionAPI can be
/// applied to a separate prim which can be linked to (see PhysxVehicleWheelAttachmentAPI).

class PhysxSchemaPhysxVehicleSuspensionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleSuspensionAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleSuspensionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleSuspensionAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleSuspensionAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleSuspensionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleSuspensionAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleSuspensionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleSuspensionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleSuspensionAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleSuspensionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleSuspensionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleSuspensionAPI>())
        {
            return PhysxSchemaPhysxVehicleSuspensionAPI(prim);
        }
        return PhysxSchemaPhysxVehicleSuspensionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SPRINGSTRENGTH
    // --------------------------------------------------------------------- //
    /// Spring strength of suspension unit (units: force / distance = mass / seconds / seconds).
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleSuspension:springStrength` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpringStrengthAttr() const;

    /// See GetSpringStrengthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringStrengthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRINGDAMPERRATE
    // --------------------------------------------------------------------- //
    /// Spring damper rate of suspension unit (units: force * seconds / distance = mass / seconds).
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleSuspension:springDamperRate` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpringDamperRateAttr() const;

    /// See GetSpringDamperRateAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpringDamperRateAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TRAVELDISTANCE
    // --------------------------------------------------------------------- //
    /// Distance the wheel can travel along the suspension when going from max compression to
    /// max droop (units: distance). The value has to be positive.
    ///
    /// Note: either this attribute or the deprecated maxCompression/maxDroop have to
    /// to be specified (with the former taking precedence). When migrating from the
    /// deprecated attributes, travelDistance can be set to the sum of maxCompression
    /// and maxDroop.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleSuspension:travelDistance` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetTravelDistanceAttr() const;

    /// See GetTravelDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTravelDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXCOMPRESSION
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use travelDistance instead.
    ///
    /// Maximum compression from rest state allowed by suspension spring (units: distance).
    /// The value has to be positive.
    ///
    /// Note: will be ignored if travelDistance is authored.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleSuspension:maxCompression` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxCompressionAttr() const;

    /// See GetMaxCompressionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxCompressionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXDROOP
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use travelDistance instead.
    ///
    /// Maximum elongation from rest state allowed by suspension spring (units: distance).
    /// The value has to be positive unless it should get computed automatically in which case any
    /// negative number can be used to indicate as much. It is highly recommended to chose a value
    /// close to: sprungMass * gravity / springStrength.
    ///
    /// Note: will be ignored if travelDistance is authored.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleSuspension:maxDroop` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxDroopAttr() const;

    /// See GetMaxDroopAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxDroopAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPRUNGMASS
    // --------------------------------------------------------------------- //
    /// Mass of vehicle that is supported by suspension spring (units: mass).
    /// If set to 0, the sprung mass will get computed automatically.
    ///
    /// Note: it is not possible for a vehicle to have some sprung mass values being user-defined and some
    /// being computed automatically. Either all values have to be user-defined or all have to be set to 0
    /// for auto-computation.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleSuspension:sprungMass = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSprungMassAttr() const;

    /// See GetSprungMassAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSprungMassAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CAMBERATREST
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use PhysxVehicleSuspensionComplianceAPI instead.
    ///
    /// Camber angle (in radians) of wheel when the suspension is at its rest position.
    ///
    /// Note: will be ignored if PhysxVehicleSuspensionComplianceAPI is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleSuspension:camberAtRest` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCamberAtRestAttr() const;

    /// See GetCamberAtRestAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCamberAtRestAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CAMBERATMAXCOMPRESSION
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use PhysxVehicleSuspensionComplianceAPI instead.
    ///
    /// Camber angle (in radians) of wheel when the suspension is at maximum compression.
    ///
    /// Note: will be ignored if PhysxVehicleSuspensionComplianceAPI is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleSuspension:camberAtMaxCompression` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCamberAtMaxCompressionAttr() const;

    /// See GetCamberAtMaxCompressionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCamberAtMaxCompressionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CAMBERATMAXDROOP
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use PhysxVehicleSuspensionComplianceAPI instead.
    ///
    /// Camber angle (in radians) of wheel when the suspension is at maximum droop.
    ///
    /// Note: will be ignored if PhysxVehicleSuspensionComplianceAPI is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleSuspension:camberAtMaxDroop` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCamberAtMaxDroopAttr() const;

    /// See GetCamberAtMaxDroopAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCamberAtMaxDroopAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleSuspensionAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleSuspensionAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleSuspensionAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleSuspensionAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::GetSpringStrengthAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionSpringStrength));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::CreateSpringStrengthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionSpringStrength),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::GetSpringDamperRateAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionSpringDamperRate));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::CreateSpringDamperRateAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionSpringDamperRate),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::GetTravelDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionTravelDistance));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::CreateTravelDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionTravelDistance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::GetMaxCompressionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionMaxCompression));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::CreateMaxCompressionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionMaxCompression),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::GetMaxDroopAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionMaxDroop));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::CreateMaxDroopAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionMaxDroop), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::GetSprungMassAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionSprungMass));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::CreateSprungMassAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionSprungMass),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::GetCamberAtRestAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionCamberAtRest));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::CreateCamberAtRestAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionCamberAtRest),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::GetCamberAtMaxCompressionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionCamberAtMaxCompression));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::CreateCamberAtMaxCompressionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionCamberAtMaxCompression),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::GetCamberAtMaxDroopAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionCamberAtMaxDroop));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionAPI::CreateCamberAtMaxDroopAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionCamberAtMaxDroop),
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
