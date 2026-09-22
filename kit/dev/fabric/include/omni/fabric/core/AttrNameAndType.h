// Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/IToken.h>
#include <omni/fabric/IPath.h>

#include <omni/fabric/Type.h>

namespace omni
{
namespace fabric
{
// Basic types
// Types and methods ending in C are intended to be used with C-ABI interfaces.

// PathToAttributesMap allows metadata to be attached to attributes.
// The metadata that exist currently are for (fabric) internal use only.
// Abstractly it holds an array for each attribute, where element 0
// (NameSuffix::none) is the value itself, and other elements are the metadata.
// It is called NameSuffix because conceptually each metadatum adds a
// new attribute with a name suffix specifying the type of metadata.
// For example, suppose you have an attribute "points" that has an attached
// elemCount. Conceptually you have two attributes "points" and
// "points_elemCount".
enum class NameSuffix
{
    none = 0, // Index NameSuffix::value is the index of the data itself


    // The following metadata is present on USD attributes that connect to others
    connection // The target(prim, attribute) of the connection
};

inline std::string toString(NameSuffix suffix)
{
    if (suffix == NameSuffix::connection)
        return "_connection";
    else if (suffix == NameSuffix::none)
        return "";

    return "";
}

inline std::ostream& operator<<(std::ostream& s, const NameSuffix& nameSuffix)
{
    s << toString(nameSuffix);
    return s;
}

struct AssetPath
{
    TokenC assetPath;
    TokenC resolvedPath;
};
static_assert(sizeof(AssetPath) == 16,
              "Changing the size of AssetPath requires updating BaseDataType::eAsset returned in Type.h");

struct Connection
{
    PathC path;
    TokenC attrName;
};
static_assert(sizeof(Connection) == 2 * sizeof(uint64_t),
              "Changing the size of Connection requires updating the baseTypeSize returned in Type.h");

template<typename TokenT>
struct AttributeName
{
    TokenT name;
    NameSuffix suffix;

    AttributeName() : name(TokenT()), suffix(NameSuffix::none)
    {
    }

    template<typename OtherTokenT>
    AttributeName(const OtherTokenT& name, NameSuffix suffix) : name(name), suffix(suffix)
    {
    }

    // Note that in the name comparisons below TokenC masks off USD's lifetime bit.
    // For example, tokens created from the same string are considered equal even
    // if one was created with finite lifetime and the other infinite lifetime.
    bool operator<(const AttributeName& rhs) const
    {
        if (TokenC(name) < TokenC(rhs.name))
            return true;
        if (TokenC(rhs.name) < TokenC(name))
            return false;

        return suffix < rhs.suffix;
    }

    bool operator==(const AttributeName& other) const
    {
        return (name == other.name) && (suffix == other.suffix);
    }
};
using AttrNameCounted = AttributeName<Token>;
using AttrNameBorrowed = AttributeName<TokenC>;
static_assert(std::is_standard_layout<AttrNameBorrowed>::value,
              "AttrNameBorrowed must be standard layout as it is used in C-ABI interfaces");
using AttrName = AttributeName<TokenC>; // DEPRECATE
static_assert(std::is_standard_layout<AttrName>::value,
              "AttrName must be standard layout as it is used in C-ABI interfaces");

// AttrNameAndType specifies the name and type of an attribute. When the user
// searches for buckets of prims they use this type to specify which attributes
// the prims must have. Also the user can query the name and type of an
// attribute at a given path, and the output has this type.

template<typename TokenT>
struct AttributeTypeAndName
{
    Type type;
    TokenT name;
    NameSuffix suffix;

    AttributeTypeAndName() : type(), name(), suffix(NameSuffix::none)
    {
    }

    template <typename OtherTokenT>
    AttributeTypeAndName(const AttributeTypeAndName<OtherTokenT>& other)
        : type(other.type), name(other.name), suffix(other.suffix)
    {
    }

    template <typename OtherTokenT>
    AttributeTypeAndName(Type type, const AttributeName<OtherTokenT>& name)
        : type(type), name(name.name), suffix(name.suffix)
    {
    }

    template <typename OtherTokenT>
    AttributeTypeAndName(Type type, const OtherTokenT& name, NameSuffix suffix = NameSuffix::none)
        : type(type), name(name), suffix(suffix)
    {
    }

    // Note that in the name comparisons below TokenC masks off USD's lifetime bit.
    // For example, tokens created from the same string are considered equal even
    // if one was created with finite lifetime and the other infinite lifetime.
    bool operator<(const AttributeTypeAndName& rhs) const
    {
        if (TypeC(type) < TypeC(rhs.type))
            return true;
        if (TypeC(rhs.type) < TypeC(type))
            return false;
        if (TokenC(name) < TokenC(rhs.name))
            return true;
        if (TokenC(rhs.name) < TokenC(name))
            return false;

        return suffix < rhs.suffix;
    }

    inline bool operator==(const AttributeTypeAndName& other) const
    {
        return type == other.type && name == other.name && suffix == other.suffix;
    }

    inline operator AttributeName<TokenC>() const
    {
        return AttributeName<TokenC>{ name, suffix };
    }
};
using AttrTypeAndNameCounted = AttributeTypeAndName<Token>;
using AttrTypeAndNameBorrowed = AttributeTypeAndName<TokenC>;
static_assert(std::is_standard_layout<AttrTypeAndNameBorrowed>::value,
              "AttrTypeAndNameBorrowed must be standard layout as it is used in C-ABI interfaces");
using AttrNameAndType = AttributeTypeAndName<Token>; // DEPRECATE
static_assert(std::is_standard_layout<AttrNameAndType>::value,
              "AttrNameAndType must be standard layout as it is used in C-ABI interfaces");

// NOTE: This type alias provides source level compatibility. Usage of the original AttrNameAndType structure has
// been replaced with what was previously called AttrNameAndType_v2 and the _v2 suffix dropped. This alias allows code
// which still refers to AttrNameAndType_v2 to compile.
using AttrNameAndType_v2 = AttrNameAndType;

} // namespace fabric
} // namespace omni

namespace std
{

template <typename TokenT>
struct hash<omni::fabric::AttributeName<TokenT>>
{
    // Use the same hash_combine as boost
    template <class T>
    static inline void hash_combine(std::size_t& seed, const T& v)
    {
        std::hash<T> hasher;
        seed ^= hasher(v) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    }

    std::size_t operator()(const omni::fabric::AttributeName<TokenT>& key) const
    {
        size_t hash = std::hash<omni::fabric::Token>{}(key.name);
        hash_combine(hash, uint32_t(key.suffix));
        return hash;
    }
};

template <typename TokenT>
struct hash<omni::fabric::AttributeTypeAndName<TokenT>>
{
    // Use the same hash_combine as boost
    template <class T>
    static inline void hash_combine(std::size_t& seed, const T& v)
    {
        std::hash<T> hasher;
        seed ^= hasher(v) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    }

    std::size_t operator()(const omni::fabric::AttributeTypeAndName<TokenT>& key) const
    {
        size_t hash = std::hash<omni::fabric::Type>{}(key.type);
        hash_combine(hash, std::hash<omni::fabric::Token>{}(key.name));
        hash_combine(hash, uint32_t(key.suffix));
        return hash;
    }
};

} // namespace std
