// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file
//!
//! @brief TODO

#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/Type.h>
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{

using namespace omni::fabric;

//! @class SdfValueTypeName
//! Represents a value type name, i.e. an attribute's type name.
//! This class fairly simply wraps omni::fabric::Type which has
//! an omni::fabric::BaseDataType and an optional omni::fabric::AttributeRole,
//! along with additional metadata.
//!
//! SdfValueTypeNames defined in sdf/types.h provides an accessor to
//! all valid SdfValueTypeNames (i.e. Fabric types)
//! Usage Example:
//! @code
//! SdfValueTypeName bool_type = SdfValueTypeNames->Bool;
//! SdfValueTypeName float_type = SdfValueTypeNames->Float;
//! @endcode
class SdfValueTypeName
{
public:
    //! Constructs an invalid type name. Uses omni::fabric::BaseDataType::eUnknown.
    SdfValueTypeName();
    //! Constructs a type name from the omni::fabric::Type.
    //! @param type Fabric type
    SdfValueTypeName(const Type& type);
    //! Constructs a type name. See omni::fabric::Type constructor.
    //! @param baseType Base data type. @ref omni::fabric::BaseDataType
    //! @param componentCount Number of components in the full type. Default 1.
    //! @param arrayDepth Number of array levels the type contains. Default 0.
    //! @param role Fabric attribute role. Default omni::fabric::AttributeRole::eNone
    SdfValueTypeName(BaseDataType baseType,
                     uint8_t componentCount = 1,
                     uint8_t arrayDepth = 0,
                     AttributeRole role = AttributeRole::eNone);

    //! Get the TypeC representation of this value type name.
    //! @returns Return integer key that identifies this types.
    operator omni::fabric::TypeC() const;
    //! Get the TypeC representation of this value type name.
    //! @returns Return integer key that identifies this types.
    omni::fabric::TypeC GetAsTypeC() const;

    //! Returns the type name as a token.  This should not be used for
    //! comparison purposes.
    TfToken GetAsToken() const;

    //! Returns the type name as a string.
    std::string GetAsString() const;

    //! Returns @c true if this type name is equal to @p rhs.  Aliases
    //! compare equal.
    bool operator==(const SdfValueTypeName& rhs) const;

    //! Returns @c true if this type name is not equal to @p rhs.
    bool operator!=(const SdfValueTypeName& rhs) const;

    //! Returns the scalar version of this type name if it's an array type
    //! name, otherwise returns this type name.  If there is no scalar type
    //! name then this returns the invalid type name.
    SdfValueTypeName GetScalarType() const;

    //! Returns the array version of this type name if it's an scalar type
    //! name, otherwise returns this type name.  If there is no array type
    //! name then this returns the invalid type name.
    SdfValueTypeName GetArrayType() const;

    //! Returns @c true iff this type is a scalar.  The invalid type is
    //! considered neither scalar nor array.
    bool IsScalar() const;

    //! Returns @c true iff this type is an array.  The invalid type is
    //! considered neither scalar nor array.
    bool IsArray() const;

    /*
    TODO: The whole enchilada

    /// Returns the \c TfType of the type.
    const TfType& GetType() const;

    /// Returns the C++ type name for this type.  This may not be the same
    /// as the type name returned by GetType().GetTypeName(), since that
    /// method may have had additional transformations applied for
    /// readability.
    const std::string& GetCPPTypeName() const;

    /// Returns the type's role.
    const TfToken& GetRole() const;

    /// Returns the default value for the type.
    const VtValue& GetDefaultValue() const;

    /// Returns the default unit enum for the type.
    const TfEnum& GetDefaultUnit() const;

    /// Returns the dimensions of the scalar value, e.g. 3 for a 3D point.
    SdfTupleDimensions GetDimensions() const;

    /// Returns \c true if this type name is equal to \p rhs.  Aliases
    /// compare equal.  Avoid relying on this overload.
    bool operator==(const std::string& rhs) const;

    /// Returns \c true if this type name is equal to \p rhs.  Aliases
    /// compare equal.  Avoid relying on this overload.
    bool operator==(const TfToken& rhs) const;

    /// Returns a hash value for this type name.
    size_t GetHash() const;

    /// Explicit bool conversion operator. Converts to \c true if this is a
    /// valid, non-empty type, \c false otherwise.
    explicit operator bool() const;

    /// Returns all aliases of the type name as tokens.  These should not
    /// be used for comparison purposes.
    std::vector<TfToken> GetAliasesAsTokens() const;

private:

    bool _IsEmpty() const;
    */

private:
    Type m_type;
};

inline SdfValueTypeName::SdfValueTypeName() : SdfValueTypeName(BaseDataType::eUnknown)
{
}

inline SdfValueTypeName::SdfValueTypeName(const Type& type) : m_type(type)
{
}

inline SdfValueTypeName::SdfValueTypeName(BaseDataType baseType,
                                          uint8_t componentCount,
                                          uint8_t arrayDepth,
                                          AttributeRole role)
    : m_type(baseType, componentCount, arrayDepth, role)
{
}

inline SdfValueTypeName::operator omni::fabric::TypeC() const
{
    return omni::fabric::TypeC(m_type);
}

inline omni::fabric::TypeC SdfValueTypeName::GetAsTypeC() const
{
    return omni::fabric::TypeC(m_type);
}

inline TfToken SdfValueTypeName::GetAsToken() const
{
    return TfToken(m_type.getTypeName());
}

inline std::string SdfValueTypeName::GetAsString() const
{
    std::string result(m_type.getTypeName());
    return result;
}

inline bool SdfValueTypeName::operator==(const SdfValueTypeName& rhs) const
{
    return GetAsTypeC() == rhs.GetAsTypeC();
}

inline bool SdfValueTypeName::operator!=(const SdfValueTypeName& rhs) const
{
    return !(GetAsTypeC() == rhs.GetAsTypeC());
}

inline SdfValueTypeName SdfValueTypeName::GetScalarType() const
{
    return SdfValueTypeName(m_type.baseType, m_type.componentCount, 0, m_type.role);
}

inline SdfValueTypeName SdfValueTypeName::GetArrayType() const
{
    return SdfValueTypeName(m_type.baseType, m_type.componentCount, 1, m_type.role);
}

inline bool SdfValueTypeName::IsScalar() const
{
    return m_type.arrayDepth == 0;
}

inline bool SdfValueTypeName::IsArray() const
{
    return m_type.arrayDepth > 0;
}

} // namespace usdrt
