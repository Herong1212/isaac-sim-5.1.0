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

/// @file physxSchema/physxCollisionAPI.h

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
// PHYSXCOLLISIONAPI                                                           //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxCollisionAPI
///
/// PhysX collision extended parameters

class PhysxSchemaPhysxCollisionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxCollisionAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxCollisionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxCollisionAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxCollisionAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxCollisionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxCollisionAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxCollisionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxCollisionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxCollisionAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxCollisionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxCollisionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxCollisionAPI>())
        {
            return PhysxSchemaPhysxCollisionAPI(prim);
        }
        return PhysxSchemaPhysxCollisionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // CONTACTOFFSET
    // --------------------------------------------------------------------- //
    /// Contact offset of a collision shape. Default value -inf means default is picked by the simulation based on the
    /// shape extent. Range: [maximum(0, restOffset), inf) Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCollision:contactOffset = -inf` |
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
    // RESTOFFSET
    // --------------------------------------------------------------------- //
    /// Rest offset of a collision shape. Default value -inf means that the simulation sets a suitable value.
    /// For rigid bodies, this value is zero.
    /// Range: [0, contactOffset]
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCollision:restOffset = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRestOffsetAttr() const;

    /// See GetRestOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRestOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TORSIONALPATCHRADIUS
    // --------------------------------------------------------------------- //
    /// Defines the radius of the contact patch used to apply torsional friction.
    /// Range: [0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCollision:torsionalPatchRadius = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetTorsionalPatchRadiusAttr() const;

    /// See GetTorsionalPatchRadiusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTorsionalPatchRadiusAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MINTORSIONALPATCHRADIUS
    // --------------------------------------------------------------------- //
    /// Defines the minimum radius of the contact patch used to apply torsional friction.
    /// Range: [0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxCollision:minTorsionalPatchRadius = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMinTorsionalPatchRadiusAttr() const;

    /// See GetMinTorsionalPatchRadiusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinTorsionalPatchRadiusAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxCollisionAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxCollisionAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxCollisionAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxCollisionAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxCollisionAPI::GetContactOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCollisionContactOffset));
}

inline UsdAttribute PhysxSchemaPhysxCollisionAPI::CreateContactOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCollisionContactOffset), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCollisionAPI::GetRestOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCollisionRestOffset));
}

inline UsdAttribute PhysxSchemaPhysxCollisionAPI::CreateRestOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCollisionRestOffset), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCollisionAPI::GetTorsionalPatchRadiusAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCollisionTorsionalPatchRadius));
}

inline UsdAttribute PhysxSchemaPhysxCollisionAPI::CreateTorsionalPatchRadiusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCollisionTorsionalPatchRadius),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxCollisionAPI::GetMinTorsionalPatchRadiusAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxCollisionMinTorsionalPatchRadius));
}

inline UsdAttribute PhysxSchemaPhysxCollisionAPI::CreateMinTorsionalPatchRadiusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxCollisionMinTorsionalPatchRadius),
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
