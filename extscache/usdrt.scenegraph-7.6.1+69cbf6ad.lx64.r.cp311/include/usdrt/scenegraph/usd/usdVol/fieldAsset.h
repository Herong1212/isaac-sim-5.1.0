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

/// @file usdVol/fieldAsset.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdVol/fieldBase.h"
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
// FIELDASSET                                                                  //
// -------------------------------------------------------------------------- //

/// @class UsdVolFieldAsset
///
/// Base class for field primitives defined by an external file.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdVolTokens.
/// So to set an attribute to the value "rightHanded", use UsdVolTokens->rightHanded
/// as the value.

class UsdVolFieldAsset : public UsdVolFieldBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractTyped;


    /// Construct a UsdVolFieldAsset on UsdPrim @p prim.
    /// Equivalent to UsdVolFieldAsset::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdVolFieldAsset(const UsdPrim& prim = UsdPrim()) : UsdVolFieldBase(prim)
    {
    }

    /// Construct a UsdVolFieldAsset on the prim held by @p schemaObj .
    /// Should be preferred over UsdVolFieldAsset(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdVolFieldAsset(const UsdSchemaBase& schemaObj) : UsdVolFieldBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdVolFieldAsset()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FILEPATH
    // --------------------------------------------------------------------- //
    /// An asset path attribute that points to a file on disk.
    /// For each supported file format, a separate FieldAsset
    /// subclass is required.
    ///
    /// This attribute's value can be animated over time, as most
    /// volume asset formats represent just a single timeSample of
    /// a volume.  However, it does not, at this time, support
    /// any pattern substitutions like "$F".
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `asset filePath` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |

    UsdAttribute GetFilePathAttr() const;

    /// See GetFilePathAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFilePathAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FIELDNAME
    // --------------------------------------------------------------------- //
    /// Name of an individual field within the file specified by
    /// the filePath attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token fieldName` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |

    UsdAttribute GetFieldNameAttr() const;

    /// See GetFieldNameAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFieldNameAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FIELDINDEX
    // --------------------------------------------------------------------- //
    /// A file can contain multiple fields with the same
    /// name. This optional attribute is an index used to
    /// disambiguate between these multiple fields with the same
    /// name.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int fieldIndex` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetFieldIndexAttr() const;

    /// See GetFieldIndexAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFieldIndexAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FIELDDATATYPE
    // --------------------------------------------------------------------- //
    /// Token which is used to indicate the data type of an
    /// individual field. Authors use this to tell consumers more
    /// about the field without opening the file on disk. The list of
    /// allowed tokens is specified with the specific asset type.
    /// A missing value is considered an error.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token fieldDataType` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |

    UsdAttribute GetFieldDataTypeAttr() const;

    /// See GetFieldDataTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFieldDataTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VECTORDATAROLEHINT
    // --------------------------------------------------------------------- //
    /// Optional token which is used to indicate the role of a vector
    /// valued field. This can drive the data type in which fields
    /// are made available in a renderer or whether the vector values
    /// are to be transformed.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token vectorDataRoleHint = "None"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdVolTokens "Allowed Values" | None, Point, Normal, Vector, Color |

    UsdAttribute GetVectorDataRoleHintAttr() const;

    /// See GetVectorDataRoleHintAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVectorDataRoleHintAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdVolFieldAsset::_GetStaticTfType()
{
    const static TfToken token("UsdVolFieldAsset");
    return token;
}

/* virtual */
inline const TfToken UsdVolFieldAsset::_GetTfTypeToken() const
{
    const static TfToken token("UsdVolFieldAsset");
    return token;
}


inline UsdAttribute UsdVolFieldAsset::GetFilePathAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdVolTokens->filePath));
}

inline UsdAttribute UsdVolFieldAsset::CreateFilePathAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdVolTokens->filePath), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdVolFieldAsset::GetFieldNameAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdVolTokens->fieldName));
}

inline UsdAttribute UsdVolFieldAsset::CreateFieldNameAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdVolTokens->fieldName), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdVolFieldAsset::GetFieldIndexAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdVolTokens->fieldIndex));
}

inline UsdAttribute UsdVolFieldAsset::CreateFieldIndexAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdVolTokens->fieldIndex), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute UsdVolFieldAsset::GetFieldDataTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdVolTokens->fieldDataType));
}

inline UsdAttribute UsdVolFieldAsset::CreateFieldDataTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdVolTokens->fieldDataType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdVolFieldAsset::GetVectorDataRoleHintAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdVolTokens->vectorDataRoleHint));
}

inline UsdAttribute UsdVolFieldAsset::CreateVectorDataRoleHintAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdVolTokens->vectorDataRoleHint), SdfValueTypeNames->Token,
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
