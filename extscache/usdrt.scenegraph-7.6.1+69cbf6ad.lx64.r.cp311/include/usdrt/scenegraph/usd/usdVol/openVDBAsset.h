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

/// @file usdVol/openVDBAsset.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdVol/fieldAsset.h"
#include "usdrt/scenegraph/usd/usdVol/tokens.h"


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
// OPENVDBASSET                                                                //
// -------------------------------------------------------------------------- //

/// @class UsdVolOpenVDBAsset
///
/// OpenVDB field primitive. The FieldAsset filePath attribute must
/// specify a file in the OpenVDB format on disk.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdVolTokens.
/// So to set an attribute to the value "rightHanded", use UsdVolTokens->rightHanded
/// as the value.

class UsdVolOpenVDBAsset : public UsdVolFieldAsset
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdVolOpenVDBAsset on UsdPrim @p prim.
    /// Equivalent to UsdVolOpenVDBAsset::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdVolOpenVDBAsset(const UsdPrim& prim = UsdPrim()) : UsdVolFieldAsset(prim)
    {
    }

    /// Construct a UsdVolOpenVDBAsset on the prim held by @p schemaObj .
    /// Should be preferred over UsdVolOpenVDBAsset(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdVolOpenVDBAsset(const UsdSchemaBase& schemaObj) : UsdVolFieldAsset(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdVolOpenVDBAsset()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdVolOpenVDBAsset Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FIELDDATATYPE
    // --------------------------------------------------------------------- //
    /// Token which is used to indicate the data type of an
    /// individual field. Authors use this to tell consumers more
    /// about the field without opening the file on disk. The list of
    /// allowed tokens reflects the available choices for OpenVDB
    /// volumes.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token fieldDataType` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdVolTokens "Allowed Values" | half, float, double, int, uint, int64, half2, float2, double2, int2,
    /// half3, float3, double3, int3, matrix3d, matrix4d, quatd, bool, mask, string |

    UsdAttribute GetFieldDataTypeAttr() const;

    /// See GetFieldDataTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFieldDataTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FIELDCLASS
    // --------------------------------------------------------------------- //
    /// Optional token which can be used to indicate the class of
    /// an individual grid. This is a mapping to openvdb::GridClass
    /// where the values are GRID_LEVEL_SET, GRID_FOG_VOLUME,
    /// GRID_STAGGERED, and GRID_UNKNOWN.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token fieldClass` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdVolTokens "Allowed Values" | levelSet, fogVolume, staggered, unknown |

    UsdAttribute GetFieldClassAttr() const;

    /// See GetFieldClassAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFieldClassAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdVolOpenVDBAsset::_GetStaticTfType()
{
    const static TfToken token("UsdVolOpenVDBAsset");
    return token;
}

/* virtual */
inline const TfToken UsdVolOpenVDBAsset::_GetTfTypeToken() const
{
    const static TfToken token("UsdVolOpenVDBAsset");
    return token;
}

/* static */
inline UsdVolOpenVDBAsset UsdVolOpenVDBAsset::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdVolOpenVDBAsset();
    }
    return UsdVolOpenVDBAsset(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdVolOpenVDBAsset::GetFieldDataTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdVolTokens->fieldDataType));
}

inline UsdAttribute UsdVolOpenVDBAsset::CreateFieldDataTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdVolTokens->fieldDataType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdVolOpenVDBAsset::GetFieldClassAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdVolTokens->fieldClass));
}

inline UsdAttribute UsdVolOpenVDBAsset::CreateFieldClassAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdVolTokens->fieldClass), SdfValueTypeNames->Token,
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
