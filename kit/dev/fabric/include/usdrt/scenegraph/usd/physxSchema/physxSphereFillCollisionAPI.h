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

/// @file physxSchema/physxSphereFillCollisionAPI.h

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
// PHYSXSPHEREFILLCOLLISIONAPI                                                 //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxSphereFillCollisionAPI
///
/// PhysX sphere fill extended parameters
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref PhysxSchemaTokens.
/// So to set an attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded
/// as the value.

class PhysxSchemaPhysxSphereFillCollisionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxSphereFillCollisionAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxSphereFillCollisionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxSphereFillCollisionAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxSphereFillCollisionAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxSphereFillCollisionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxSphereFillCollisionAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxSphereFillCollisionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxSphereFillCollisionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxSphereFillCollisionAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxSphereFillCollisionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxSphereFillCollisionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxSphereFillCollisionAPI>())
        {
            return PhysxSchemaPhysxSphereFillCollisionAPI(prim);
        }
        return PhysxSchemaPhysxSphereFillCollisionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // MAXSPHERES
    // --------------------------------------------------------------------- //
    /// Maximum of spheres produced. Range (2, 4000)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxSphereFillCollision:maxSpheres = 128` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetMaxSpheresAttr() const;

    /// See GetMaxSpheresAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxSpheresAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VOXELRESOLUTION
    // --------------------------------------------------------------------- //
    /// Voxel resolution used for the algorithm. Range (10 000, 1 000 000)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxSphereFillCollision:voxelResolution = 50000` |
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
    // SEEDCOUNT
    // --------------------------------------------------------------------- //
    /// Seed count used for the algorithm. Range (16, 4000)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxSphereFillCollision:seedCount = 1000` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetSeedCountAttr() const;

    /// See GetSeedCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSeedCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FILLMODE
    // --------------------------------------------------------------------- //
    /// Fill mode for the the algorithm.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxSphereFillCollision:fillMode = "flood"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | flood, raycast, surface |

    UsdAttribute GetFillModeAttr() const;

    /// See GetFillModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFillModeAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxSphereFillCollisionAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxSphereFillCollisionAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxSphereFillCollisionAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxSphereFillCollisionAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxSphereFillCollisionAPI::GetMaxSpheresAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSphereFillCollisionMaxSpheres));
}

inline UsdAttribute PhysxSchemaPhysxSphereFillCollisionAPI::CreateMaxSpheresAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSphereFillCollisionMaxSpheres),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSphereFillCollisionAPI::GetVoxelResolutionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSphereFillCollisionVoxelResolution));
}

inline UsdAttribute PhysxSchemaPhysxSphereFillCollisionAPI::CreateVoxelResolutionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSphereFillCollisionVoxelResolution),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSphereFillCollisionAPI::GetSeedCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSphereFillCollisionSeedCount));
}

inline UsdAttribute PhysxSchemaPhysxSphereFillCollisionAPI::CreateSeedCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSphereFillCollisionSeedCount),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSphereFillCollisionAPI::GetFillModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSphereFillCollisionFillMode));
}

inline UsdAttribute PhysxSchemaPhysxSphereFillCollisionAPI::CreateFillModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSphereFillCollisionFillMode),
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
