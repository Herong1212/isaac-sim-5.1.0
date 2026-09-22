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

/// @file usdVol/field3DAsset.h

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
// FIELD3DASSET                                                                //
// -------------------------------------------------------------------------- //

/// @class UsdVolField3DAsset
///
/// Field3D field primitive. The FieldAsset filePath attribute must
/// specify a file in the Field3D format on disk.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdVolTokens.
/// So to set an attribute to the value "rightHanded", use UsdVolTokens->rightHanded
/// as the value.

class UsdVolField3DAsset : public UsdVolFieldAsset
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdVolField3DAsset on UsdPrim @p prim.
    /// Equivalent to UsdVolField3DAsset::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdVolField3DAsset(const UsdPrim& prim = UsdPrim()) : UsdVolFieldAsset(prim)
    {
    }

    /// Construct a UsdVolField3DAsset on the prim held by @p schemaObj .
    /// Should be preferred over UsdVolField3DAsset(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdVolField3DAsset(const UsdSchemaBase& schemaObj) : UsdVolFieldAsset(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdVolField3DAsset()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdVolField3DAsset Define(const UsdStageRefPtr& stage, const SdfPath& path);

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
    /// allowed tokens reflects the available choices for Field3d
    /// volumes.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token fieldDataType` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdVolTokens "Allowed Values" | half, float, double, half3, float3, double3 |

    UsdAttribute GetFieldDataTypeAttr() const;

    /// See GetFieldDataTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFieldDataTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FIELDPURPOSE
    // --------------------------------------------------------------------- //
    /// Optional token which can be used to indicate the purpose or
    /// grouping of an individual field. Clients which consume Field3D
    /// files should treat this as the Field3D field \em name.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token fieldPurpose` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |

    UsdAttribute GetFieldPurposeAttr() const;

    /// See GetFieldPurposeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFieldPurposeAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdVolField3DAsset::_GetStaticTfType()
{
    const static TfToken token("UsdVolField3DAsset");
    return token;
}

/* virtual */
inline const TfToken UsdVolField3DAsset::_GetTfTypeToken() const
{
    const static TfToken token("UsdVolField3DAsset");
    return token;
}

/* static */
inline UsdVolField3DAsset UsdVolField3DAsset::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdVolField3DAsset();
    }
    return UsdVolField3DAsset(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdVolField3DAsset::GetFieldDataTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdVolTokens->fieldDataType));
}

inline UsdAttribute UsdVolField3DAsset::CreateFieldDataTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdVolTokens->fieldDataType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdVolField3DAsset::GetFieldPurposeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdVolTokens->fieldPurpose));
}

inline UsdAttribute UsdVolField3DAsset::CreateFieldPurposeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdVolTokens->fieldPurpose), SdfValueTypeNames->Token,
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
