//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// TODO USD COPYRIGHT AS WELL?
#pragma once

//! @file
//!
//! @brief TODO

// GENERATED FILE DO NOT EDIT

/// \file physxSchema/plane.h

#include "usdrt/scenegraph/usd/physxSchema/tokens.h"
#include "usdrt/scenegraph/usd/usdGeom/mesh.h"

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
// PLANE                                                                       //
// -------------------------------------------------------------------------- //


/// \class PhysxSchemaPlane
///
/// Plane geometry primitive. The definition of a plane is a point - Xformable and a normal axis.
///
/// For any described attribute \em Fallback \em Value or \em Allowed \em Values below
/// that are text/tokens, the actual token is published and defined in \ref PhysxSchemaTokens.
/// So to set an attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded
/// as the value.
///

class PhysxSchemaPlane : public UsdGeomMesh
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// \sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a PhysxSchemaPlane on UsdPrim \p prim .
    /// Equivalent to PhysxSchemaPlane::Get(prim.GetStage(), prim.GetPath())
    /// for a \em valid \p prim, but will not immediately throw an error for
    /// an invalid \p prim
    explicit PhysxSchemaPlane(const UsdPrim& prim = UsdPrim()) : UsdGeomMesh(prim)
    {
    }

    /// Construct a PhysxSchemaPlane on the prim held by \p schemaObj .
    /// Should be preferred over PhysxSchemaPlane(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPlane(const UsdSchemaBase& schemaObj) : UsdGeomMesh(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPlane()
    {
    }

    static const TfToken _GetStaticTfType();


public:
    // --------------------------------------------------------------------- //
    // AXIS
    // --------------------------------------------------------------------- //
    /// The axis along which the plane normal is aligned.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token axis = "Z"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | X, Y, Z |

    UsdAttribute GetAxisAttr() const;

    /// See GetAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    UsdAttribute CreateAxisAttr() const;
};

inline const TfToken PhysxSchemaPlane::_GetStaticTfType()
{
    return TfToken("PhysxSchemaPlane");
}


inline UsdAttribute PhysxSchemaPlane::GetAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->axis));
}

inline UsdAttribute PhysxSchemaPlane::CreateAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->axis), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}


}

// ===================================================================== //
// Feel free to add custom code below this line. It will be preserved by
// the code generator.
//
// Just remember to wrap code in the appropriate delimiters:
// 'namespace usdrt {', '}'.
// ===================================================================== //
// --(BEGIN CUSTOM CODE)--
