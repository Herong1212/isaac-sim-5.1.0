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

/// @file physxSchema/physxConvexDecompositionCollisionAPI.h

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
// PHYSXCONVEXDECOMPOSITIONCOLLISIONAPI                                        //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxConvexDecompositionCollisionAPI
///
/// PhysX convex decomposition extended parameters

class PhysxSchemaPhysxConvexDecompositionCollisionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxConvexDecompositionCollisionAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxConvexDecompositionCollisionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxConvexDecompositionCollisionAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxConvexDecompositionCollisionAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxConvexDecompositionCollisionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxConvexDecompositionCollisionAPI(const UsdSchemaBase& schemaObj)
        : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxConvexDecompositionCollisionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxConvexDecompositionCollisionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxConvexDecompositionCollisionAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxConvexDecompositionCollisionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxConvexDecompositionCollisionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxConvexDecompositionCollisionAPI>())
        {
            return PhysxSchemaPhysxConvexDecompositionCollisionAPI(prim);
        }
        return PhysxSchemaPhysxConvexDecompositionCollisionAPI();
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
    /// | Declaration | `int physxConvexDecompositionCollision:hullVertexLimit = 64` |
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
    // MAXCONVEXHULLS
    // --------------------------------------------------------------------- //
    /// Maximum of convex hulls created during convex decomposition.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxConvexDecompositionCollision:maxConvexHulls = 32` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetMaxConvexHullsAttr() const;

    /// See GetMaxConvexHullsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxConvexHullsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MINTHICKNESS
    // --------------------------------------------------------------------- //
    /// Convex hull min thickness.
    /// Range: [0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxConvexDecompositionCollision:minThickness = 0.001` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMinThicknessAttr() const;

    /// See GetMinThicknessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinThicknessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VOXELRESOLUTION
    // --------------------------------------------------------------------- //
    /// Voxel resolution used for convex decomposition.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxConvexDecompositionCollision:voxelResolution = 500000` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetVoxelResolutionAttr() const;

    /// See GetVoxelResolutionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVoxelResolutionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ERRORPERCENTAGE
    // --------------------------------------------------------------------- //
    /// Convex decomposition errorPercentage parameter.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxConvexDecompositionCollision:errorPercentage = 10` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetErrorPercentageAttr() const;

    /// See GetErrorPercentageAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateErrorPercentageAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHRINKWRAP
    // --------------------------------------------------------------------- //
    /// Attempts to adjust the convex hull points so that they are projected onto the surface of the original graphics
    /// mesh.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxConvexDecompositionCollision:shrinkWrap = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetShrinkWrapAttr() const;

    /// See GetShrinkWrapAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShrinkWrapAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxConvexDecompositionCollisionAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxConvexDecompositionCollisionAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxConvexDecompositionCollisionAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxConvexDecompositionCollisionAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::GetHullVertexLimitAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionHullVertexLimit));
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::CreateHullVertexLimitAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionHullVertexLimit),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::GetMaxConvexHullsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionMaxConvexHulls));
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::CreateMaxConvexHullsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionMaxConvexHulls),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::GetMinThicknessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionMinThickness));
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::CreateMinThicknessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionMinThickness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::GetVoxelResolutionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionVoxelResolution));
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::CreateVoxelResolutionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionVoxelResolution),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::GetErrorPercentageAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionErrorPercentage));
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::CreateErrorPercentageAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionErrorPercentage),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::GetShrinkWrapAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionShrinkWrap));
}

inline UsdAttribute PhysxSchemaPhysxConvexDecompositionCollisionAPI::CreateShrinkWrapAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxConvexDecompositionCollisionShrinkWrap),
                                     SdfValueTypeNames->Bool,
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
