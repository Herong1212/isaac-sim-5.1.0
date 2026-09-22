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

/// @file physxSchema/physxVehicleContextAPI.h

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
// PHYSXVEHICLECONTEXTAPI                                                      //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleContextAPI
///
/// PhysX vehicles general settings. Has to be applied to a PhysicsScene prim.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref PhysxSchemaTokens.
/// So to set an attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded
/// as the value.

class PhysxSchemaPhysxVehicleContextAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleContextAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleContextAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleContextAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleContextAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleContextAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleContextAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleContextAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleContextAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleContextAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleContextAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleContextAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleContextAPI>())
        {
            return PhysxSchemaPhysxVehicleContextAPI(prim);
        }
        return PhysxSchemaPhysxVehicleContextAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // UPDATEMODE
    // --------------------------------------------------------------------- //
    /// The dynamics of the vehicle simulation can get applied to the PhysX rigid
    /// body by either applying an acceleration or by using a velocity delta.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxVehicleContext:updateMode = "velocityChange"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | velocityChange, acceleration |

    UsdAttribute GetUpdateModeAttr() const;

    /// See GetUpdateModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUpdateModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // UPAXIS
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use verticalAxis instead.
    ///
    /// The normalized vector defining the general up direction to use for vehicles.
    /// Has to match one of the base axes (1,0,0), (0,1,0) etc. Arbitrary axes are not
    /// supported.
    ///
    /// Note: will be ignored if verticalAxis is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxVehicleContext:upAxis` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetUpAxisAttr() const;

    /// See GetUpAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUpAxisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FORWARDAXIS
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use longitudinalAxis instead.
    ///
    /// The normalized vector defining the general forward direction to use for vehicles.
    /// Has to match one of the base axes (1,0,0), (0,1,0) etc. Arbitrary axes are not
    /// supported.
    ///
    /// Note: will be ignored if longitudinalAxis is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxVehicleContext:forwardAxis` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetForwardAxisAttr() const;

    /// See GetForwardAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateForwardAxisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VERTICALAXIS
    // --------------------------------------------------------------------- //
    /// The axis defining the general up direction to use for vehicles.
    ///
    /// Note: the "undefined" token value is only a valid option for indicating that the
    /// deprecated attribute upAxis should be used instead. Else, a valid axis has to be
    /// chosen.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxVehicleContext:verticalAxis = "undefined"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | posX, negX, posY, negY, posZ, negZ, undefined |

    UsdAttribute GetVerticalAxisAttr() const;

    /// See GetVerticalAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVerticalAxisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LONGITUDINALAXIS
    // --------------------------------------------------------------------- //
    /// The axis defining the general forward direction to use for vehicles.
    ///
    /// Note: the "undefined" token value is only a valid option for indicating that the
    /// deprecated attribute forwardAxis should be used instead. Else, a valid axis has to
    /// be chosen.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxVehicleContext:longitudinalAxis = "undefined"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | posX, negX, posY, negY, posZ, negZ, undefined |

    UsdAttribute GetLongitudinalAxisAttr() const;

    /// See GetLongitudinalAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLongitudinalAxisAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleContextAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleContextAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleContextAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleContextAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleContextAPI::GetUpdateModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleContextUpdateMode));
}

inline UsdAttribute PhysxSchemaPhysxVehicleContextAPI::CreateUpdateModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleContextUpdateMode), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleContextAPI::GetUpAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleContextUpAxis));
}

inline UsdAttribute PhysxSchemaPhysxVehicleContextAPI::CreateUpAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleContextUpAxis), SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleContextAPI::GetForwardAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleContextForwardAxis));
}

inline UsdAttribute PhysxSchemaPhysxVehicleContextAPI::CreateForwardAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleContextForwardAxis),
                                     SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleContextAPI::GetVerticalAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleContextVerticalAxis));
}

inline UsdAttribute PhysxSchemaPhysxVehicleContextAPI::CreateVerticalAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleContextVerticalAxis),
                                     SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleContextAPI::GetLongitudinalAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleContextLongitudinalAxis));
}

inline UsdAttribute PhysxSchemaPhysxVehicleContextAPI::CreateLongitudinalAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleContextLongitudinalAxis),
                                     SdfValueTypeNames->Token,
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
