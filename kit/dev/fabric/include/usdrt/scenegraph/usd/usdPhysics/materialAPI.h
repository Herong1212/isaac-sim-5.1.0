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

/// @file usdPhysics/materialAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdPhysics/tokens.h"


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
// PHYSICSMATERIALAPI                                                          //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsMaterialAPI
///
/// Adds simulation material properties to a Material. All collisions
/// that have a relationship to this material will have their collision response
/// defined through this material.

class UsdPhysicsMaterialAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdPhysicsMaterialAPI on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsMaterialAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsMaterialAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdPhysicsMaterialAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsMaterialAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsMaterialAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsMaterialAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysicsMaterialAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdPhysicsMaterialAPI object is returned upon success.
    /// An invalid (or empty) UsdPhysicsMaterialAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdPhysicsMaterialAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdPhysicsMaterialAPI>())
        {
            return UsdPhysicsMaterialAPI(prim);
        }
        return UsdPhysicsMaterialAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DYNAMICFRICTION
    // --------------------------------------------------------------------- //
    /// Dynamic friction coefficient. Unitless.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:dynamicFriction = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDynamicFrictionAttr() const;

    /// See GetDynamicFrictionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDynamicFrictionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STATICFRICTION
    // --------------------------------------------------------------------- //
    /// Static friction coefficient. Unitless.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:staticFriction = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetStaticFrictionAttr() const;

    /// See GetStaticFrictionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStaticFrictionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RESTITUTION
    // --------------------------------------------------------------------- //
    /// Restitution coefficient. Unitless.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:restitution = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRestitutionAttr() const;

    /// See GetRestitutionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRestitutionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DENSITY
    // --------------------------------------------------------------------- //
    /// If non-zero, defines the density of the material. This can be
    /// used for body mass computation, see PhysicsMassAPI.
    /// Note that if the density is 0.0 it is ignored.
    /// Units: mass/distance/distance/distance.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:density = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDensityAttr() const;

    /// See GetDensityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDensityAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsMaterialAPI::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsMaterialAPI");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsMaterialAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsMaterialAPI");
    return token;
}


inline UsdAttribute UsdPhysicsMaterialAPI::GetDynamicFrictionAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsDynamicFriction));
}

inline UsdAttribute UsdPhysicsMaterialAPI::CreateDynamicFrictionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsDynamicFriction), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsMaterialAPI::GetStaticFrictionAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsStaticFriction));
}

inline UsdAttribute UsdPhysicsMaterialAPI::CreateStaticFrictionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsStaticFriction), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsMaterialAPI::GetRestitutionAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsRestitution));
}

inline UsdAttribute UsdPhysicsMaterialAPI::CreateRestitutionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsRestitution), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsMaterialAPI::GetDensityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsDensity));
}

inline UsdAttribute UsdPhysicsMaterialAPI::CreateDensityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsDensity), SdfValueTypeNames->Float,
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
