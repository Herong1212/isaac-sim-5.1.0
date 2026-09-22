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

/// @file physxSchema/physxConvexHullCollisionAPI.h

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
// PHYSXCONVEXHULLCOLLISIONAPI                                                 //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxConvexHullCollisionAPI
///
/// PhysX convex hull collision extended parameters

class PhysxSchemaPhysxConvexHullCollisionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxConvexHullCollisionAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxConvexHullCollisionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxConvexHullCollisionAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxConvexHullCollisionAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxConvexHullCollisionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxConvexHullCollisionAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxConvexHullCollisionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxConvexHullCollisionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxConvexHullCollisionAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxConvexHullCollisionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxConvexHullCollisionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxConvexHullCollisionAPI>())
        {
            return PhysxSchemaPhysxConvexHullCollisionAPI(prim);
        }
        return PhysxSchemaPhysxConvexHullCollisionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // HULLVERTEXLIMIT
    // --------------------------------------------------------------------- //
    /// Convex hull vertex limit used for convex hull cooking.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxConvexHullCollision:hullVertexLimit = 64` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetHullVertexLimitAttr() const;

    /// See GetHullVertexLimitAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateHullVertexLimitAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MINTHICKNESS
    // --------------------------------------------------------------------- //
    /// Convex hull minimum thickness.
    /// Range: [0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxConvexHullCollision:minThickness = 0.001` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMinThicknessAttr() const;

    /// See GetMinThicknessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinThicknessAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxConvexHullCollisionAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxConvexHullCollisionAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxConvexHullCollisionAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxConvexHullCollisionAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxConvexHullCollisionAPI::GetHullVertexLimitAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxConvexHullCollisionHullVertexLimit));
}

inline UsdAttribute PhysxSchemaPhysxConvexHullCollisionAPI::CreateHullVertexLimitAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxConvexHullCollisionHullVertexLimit),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxConvexHullCollisionAPI::GetMinThicknessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxConvexHullCollisionMinThickness));
}

inline UsdAttribute PhysxSchemaPhysxConvexHullCollisionAPI::CreateMinThicknessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxConvexHullCollisionMinThickness),
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
