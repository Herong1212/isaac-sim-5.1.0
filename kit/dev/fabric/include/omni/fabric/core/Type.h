// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <limits>
#include <sstream>
#include <string>
#include <type_traits>

#include <carb/Defines.h>

namespace omni
{
namespace fabric
{

/**
 * @brief TypeC are integer keys that identify types, like float3, int[] etc.
 *
 * There isn't a USD type that can be cast to TypeC,
 * please use omni::fabric::usdTypeToTypeC().
 */
struct TypeC
{
    uint32_t type{ 0 }; //!< Raw data of the type
    //! Less-than operator for a TypeC
    constexpr bool operator<(const TypeC& other) const
    {
        return type < other.type;
    }
    //! Equality operator for a TypeC
    constexpr bool operator==(const TypeC& other) const
    {
        return type == other.type;
    }
    //! Inequality operator for a TypeC
    constexpr bool operator!=(const TypeC& other) const
    {
        return type != other.type;
    }
};

static_assert(std::is_standard_layout<TypeC>::value, "Struct must be standard layout as it is used in C-ABI interfaces");

//! Simple constant to flag an uninitialized type
static constexpr TypeC kUnknownType{ 0 };
static constexpr uint32_t kUnknownTypeEncoded{ 0 };

// begin-base-data-type
enum class BaseDataType : uint8_t
{
    eUnknown = 0, //!< The base type is not defined
    eBool,  //!< Boolean type
    eUChar,  //!< Unsigned character (8-bit)
    eInt,  //!< 32-bit integer
    eUInt,  //!< 32-bit unsigned integer
    eInt64,  //!< 64-bit integer
    eUInt64,  //!< 64-bit unsigned integer

    eHalf,  //!< Half-precision floating point number
    eFloat,  //!< Full-precision floating point number
    eDouble,  //!< Double-precision floating point number

    eToken,  //!< Unique token identifying a constant shared string

    // RELATIONSHIP is stored as a 64-bit integer internally, but shouldn't be
    // treated as an integer type by nodes.
    eRelationship,  //!< 64-bit handle to a USD relationship

    // For internal use only
    eAsset,  //!< (INTERNAL) Handle to a USD asset
    eDeprecated1,  //!< (INTERNAL) Handle to a USD prim
    eConnection,  //!< (INTERNAL) Special type connecting to USD elements

    // eTags are attributes that have a name but no type or value
    eTag,

    ePath, //!< To use for scalar PathC attributes

    eCompactTransform, //!< A mixed precision TRS struct. Translation is double precision.

    eCount // for compile-time checks
};
// end-base-data-type

/**
 * @brief Insertion operator for the base data type of an attribute
 *
 * @param s Output stream on which to emit the string representation of the base data type
 * @param type Base type to be emitted
 * @return std::ostream& Input stream for chaining
 */
inline std::ostream& operator<<(std::ostream& s, const BaseDataType& type)
{
    static const char* names[] = { "unknown", "bool",   "uchar", "int", "uint",  "int64", "uint64", "half",
                                   "float", "double", "token", "rel", "asset", "prim", "connection", "tag", "path", "compactTransform" };
    static_assert(sizeof(names) / sizeof(names[0]) == uint8_t(BaseDataType::eCount),
                  "BaseDataType::eCount must match the string table length");

    if (type <= BaseDataType::eTag)
    {
        return s << names[uint8_t(type)];
    }
    return s;
}

/**
 * @brief Get the name of the base data type as a string
 *
 * @param b Base data type to represent as a string
 * @return std::string containing the name of the base data type value
 */
inline std::string getBaseTypeName(BaseDataType b)
{
    std::ostringstream name;
    name << b;
    return name.str();
}

// ==============================================================================================================
// begin-roles
/**
 * @brief The role enum provides an interpretation of the base data as a specific type
 *
 * The roles are meant to provide some guidance on how to use the data after extraction from Fabric.
 * For example a length calculation makes sense for a "vector" role but not for a "position" role.
 * Some of the roles correspond to an equivalent role in USD, others are Fabric-specific.
 */
enum class AttributeRole : uint8_t
{
    eNone = 0, //!< No special role
    eVector,  //!< A vector in space
    eNormal,  //!< A surface normal
    ePosition,  //!< A position in space
    eColor,  //!< A color representation
    eTexCoord,  //!< Texture coordinates
    eQuaternion,  //!< A 4d quaternion vector
    eTransform,  //!< For instances, TRS components
    eFrame,  //!< A 4x4 matrix representing a coordinate frame
    eTimeCode,  //!< A double value representing a time code
    // eText is not a USD role. If a uchar[] attribute has role eText then
    // the corresponding USD attribute will have type "string", and be human
    // readable in USDA. If it doesn't, then it will have type "uchar[]" in USD
    // and appear as an array of numbers in USDA.
    eText,  //!< (Non-USD) Interpret uchar-array as a string
    eAppliedSchema,  //!< (Non-USD) eTag representing a USD applied schema
    ePrimTypeName,  //!< (Non-USD) eTag representing a USD prim type
    eExecution,  //!< (Non-USD) UInt value used for control flow in OmniGraph Action Graphs
    eMatrix,  //!< A 4x4 or 3x3 matrix
    eObjectId,  //!< (Non-USD) UInt64 value used for Python object identification
    eBundle,  //!< (Non-USD) Representation of the OmniGraph "bundle" type, which is a set of attributes
    ePath,  //!< (Non-USD) uchar-array representing a string that is interpreted as a USD Sdf Path
    eInstancedAttribute,  //!< (Non-USD) eTag used in place of attribute types on instanced prims
    eAncestorPrimTypeName,  //!< (Non-USD) eTag representing an ancestor type of a USD prim type
    eTarget,  //!< (Non-USD) eRelationship representing path data in OmniGraph
    eUnknown,

    eCount // for compile-time checks
};
// end-roles

/**
 * @brief Insertion operator for the name of an attribute role type
 *
 * @param s Stream to get the emitted name
 * @param type Role type to be emitted
 * @return std::ostream& Input stream for chaining
 */
inline std::ostream& operator<<(std::ostream& s, const AttributeRole& type)
{
    static const char* names[] = { "none",
                                   "vector",
                                   "normal",
                                   "position",
                                   "color",
                                   "texCoord",
                                   "quaternion",
                                   "transform",
                                   "frame",
                                   "timecode",
                                   "text",
                                   "appliedSchema",
                                   "primTypeName",
                                   "execution",
                                   "matrix",
                                   "objectId",
                                   "bundle",
                                   "path",
                                   "instancedAttribute",
                                   "ancestorPrimTypeName",
                                   "target",
                                   "unknown" };
    static_assert(sizeof(names) / sizeof(names[0]) == uint8_t(AttributeRole::eCount),
                  "AttributeRole::eCount must match the string table length");

    if (type <= AttributeRole::eUnknown)
    {
        return s << names[uint8_t(type)];
    }
    return s;
}

/**
 * @brief Get the Attribute Role Name as a string
 *
 * @param r Role type whose name is to be returned
 * @return std::string Name representing the role passed in
 */
inline std::string getAttributeRoleName(AttributeRole r)
{
    std::ostringstream name;
    name << r;
    return name.str();
}

// ==============================================================================================================
/**
 * @brief Representation of an attribute data type
 *
 * The type is intentionally as simple as possible, so that it can be trivially passed around and copied.
 */
struct Type
{
    BaseDataType baseType; //!< Underlying type of a single data element (1 byte)

    //! Number of components in the full type (1 byte).
    //! 1 for raw base types; 2 for vector2f, int2, etc; 3 for point3d, normal3f, etc;
    //! 4 for quatf, color4d, float4, matrix2f etc; 9 for matrix3f, etc; 16 for matrix4d, etc.
    uint8_t componentCount;

    //! Number of array levels the type contains (1 byte)
    //! 0 for a single value (e.g. float)
    //! 1 for an array (e.g. float[])
    //! 2 for an array of arrays (e.g. float[][] - not yet supported)
    uint8_t arrayDepth;

    //! Interpretation of the raw data in the type (1 byte)
    //! This doesn't change the basic storage size of the data type at all, only the interpretation of
    //! what the data represents (e.g. raw float[3] versus 3-d point versus 3-element color)
    AttributeRole role;

    /**
     * @brief Constructor for a fully defined type definition
     */
    constexpr Type(BaseDataType baseType,
                   uint8_t componentCount = 1,
                   uint8_t arrayDepth = 0,
                   AttributeRole role = AttributeRole::eNone)
        : baseType(baseType), componentCount(componentCount), arrayDepth(arrayDepth), role(role)
    {
    }

    /**
     * @brief Contructor for an uninitialized type
     */
    constexpr Type() : Type(BaseDataType::eUnknown)
    {
    }

    static constexpr BaseDataType DecodeBaseType(const uint32_t& u32)
    {
        return BaseDataType(u32 & 0xff);
    }

    static constexpr uint8_t DecodeComponentCount(const uint32_t& u32)
    {
        return (u32 >> 8) & 0xff;
    }

    static constexpr uint8_t DecodeArrayDepth(const uint32_t& u32)
    {
        return (u32 >> 16) & 0xff;
    }

    static constexpr AttributeRole DecodeRole(const uint32_t& u32)
    {
        return AttributeRole( (u32 >> 24) & 0xff );
    }

    /**
     * @brief Raw POD constructor
     *
     * @param u Raw type to be copied (represented as bytes)
     */
    constexpr explicit Type(const TypeC& t)
        : baseType(DecodeBaseType(t.type))
        , componentCount(DecodeComponentCount(t.type))
        , arrayDepth(DecodeArrayDepth(t.type))
        , role(DecodeRole(t.type))
    {
    }

    /**
     * @brief Byte-initialized constructor
     *
     * @param t Raw type to be copied (represented as bytes)
     */
    constexpr explicit Type(const uint32_t u)
        : baseType(DecodeBaseType(u))
        , componentCount(DecodeComponentCount(u))
        , arrayDepth(DecodeArrayDepth(u))
        , role(DecodeRole(u))
    {
    }

    /**
     * @brief Cast operator
     *
     * @return TypeC
     */
    constexpr explicit operator TypeC() const
    {
        return TypeC { encode() };
    }

    /**
     * @brief Conversion function
     *
     * @return TypeC
     */
    constexpr TypeC asTypeC() const
    {
        return TypeC{ encode() };
    }

    /**
     * @brief Check validity of this type.
     *
     * @return Boolean validity of this type.
     */
    constexpr bool isValid() const
    {
        return baseType != BaseDataType::eUnknown && componentCount > 0;
    }

    /**
     * @brief Equality operator
     *
     * Two types are considered equal if all of their parts are equal
     *
     * @param rhs Type to compare against
     * @return true if the types are identical
     * @return false if the types have any difference
     */
    constexpr bool operator==(const Type& rhs) const
    {
        return compatibleRawData(rhs) && role == rhs.role;
    }

    /**
     * @brief Inequality operator
     *
     * Two types are considered not equal if any of their parts are not equal
     *
     * @param rhs Type to compare against
     * @return true if the types are not identical
     * @return false if the types have no difference
     */
    constexpr bool operator!=(const Type& rhs) const
    {
        return !((*this) == rhs);
    }

    /**
     * @brief Less-than operator
     *
     * One type is considered lexically less-than another if its byte representation is smaller
     *
     * @param rhs Type to compare against
     * @return true if the type's byte representation is smaller than that of @p rhs
     * @return false if the type's byte representation is larger or equal to that of @p rhs
     */
    constexpr bool operator<(const Type& rhs) const
    {
        return encode() < rhs.encode();
    }

    /**
     * @brief Encode the type definition into a 32-bit unsigned integer as a bit map
     *
     * @return uint32_t Encoded value of the type
    */
    constexpr uint32_t encode() const
    {
        const uint32_t u32 = uint8_t(role) << 24 | uint32_t(arrayDepth << 16) | uint32_t(componentCount << 8) | uint8_t(baseType);
        return u32;
    }

    /**
     * @brief Decode a 32-bit unsigned integer into an omni::fabric::Type definition
     *
     * @return Type Decoded value of the type
    */
    constexpr Type& decode(const uint32_t u32)
    {
        // Matches little endian interpretation of the four bytes
        baseType = DecodeBaseType(u32);
        componentCount = DecodeComponentCount(u32);
        arrayDepth = DecodeArrayDepth(u32);
        role = DecodeRole(u32);
        return *this;
    }

    /**
     * Role-insensitive equality check, useful for checking for compatible raw data types.
     *
     * @param otherType Type to compare with
     *
     * @return true if the types are equal, ignoring their roles
     * @return false if the types are not equal, not including their roles
     */
    constexpr bool compatibleRawData(const Type& otherType) const
    {
        return baseType == otherType.baseType && componentCount == otherType.componentCount &&
               arrayDepth == otherType.arrayDepth;
    }

    /**
     * @brief Check to see if this is one of the matrix types
     *
     * @return true if this type is one of the known matrix types
     * @return false if this type is not one of the known matrix types
     */
    constexpr bool isMatrixType() const
    {
        return (role == AttributeRole::eMatrix) || (role == AttributeRole::eFrame) || (role == AttributeRole::eTransform);
    }
    /**
     * @brief Returns the component-level dimension of the type
     *
     * The difference between this value and the raw componentCount is that for matrix types it is the square root of
     * the count (e.g. a 3x3 matrix has componentCount=9 but dimension=3)
     *
     * @return The dimension of the type
     */
    constexpr uint8_t dimension() const
    {
        if (isMatrixType())
        {
            return componentCount == 4 ? 2 : (componentCount == 9 ? 3 : (componentCount == 16 ? 4 : componentCount));
        }
        return componentCount;
    }

    /**
     * @brief Get a string representing the type, in Fabric format
     *
     * "Fabric form" means appending the component count directory to the name of the type and
     * enclosing the role in parentheses, so an array of double points would be "double3[] (position)"
     *
     * @return std::string String representation of the type name
     */
    std::string getTypeName() const
    {
        std::ostringstream typeName;
        typeName << baseType;

        if (componentCount > 1)
            typeName << uint32_t(componentCount);

        if (arrayDepth == 1)
            typeName << "[]";
        else if (arrayDepth == 2)
            typeName << "[][]";

        // Some roles are hidden from USD
        // TODO: Should these be hidden just because USD hides them or should Fabric expose them?
        if ((role != AttributeRole::eNone) && (role != AttributeRole::eObjectId) && (role != AttributeRole::eBundle) &&
            (role != AttributeRole::ePath) && (role != AttributeRole::eTarget))
        {
            typeName << " (" << role << ")";
        }

        return typeName.str();
    }

    /**
     * @brief Finds the size of a single element of the base data type
     *
     * @return constexpr size_t Size of one element of the type's base data element (e.g. a float in a float[3] array)
     */
    constexpr size_t baseTypeSize() const
    {
        switch (this->baseType)
        {
        case BaseDataType::eUnknown:
            return 0;
        case BaseDataType::eBool:
            return sizeof(bool);
        case BaseDataType::eUChar:
            return sizeof(char);
        case BaseDataType::eInt:
            return sizeof(int);
        case BaseDataType::eUInt:
            return sizeof(unsigned int);
        case BaseDataType::eInt64:
            return sizeof(int64_t);
        case BaseDataType::eUInt64:
            return sizeof(uint64_t);
        // The usd implementation of half uses a short for storage. Most Half impls do similar things.
        case BaseDataType::eHalf:
            return sizeof(unsigned short);
        case BaseDataType::eFloat:
            return sizeof(float);
        case BaseDataType::eDouble:
            return sizeof(double);
        case BaseDataType::eToken:
            return sizeof(uint64_t);
        // RELATIONSHIP is stored as a 64-bit integer internally, but shouldn't be
        // treated as an integer type by nodes.
        case BaseDataType::eRelationship:
            return sizeof(int64_t);

        // For internal use only
        case BaseDataType::eAsset:
            return 16; // sizeof(omni::fabric::AssetPath)

        case BaseDataType::eDeprecated1:
            return 32; // sizeof(pxr::UsdPrim);
        case BaseDataType::eConnection:
            return 2 * sizeof(uint64_t); // sizeof(omni::fabric::Connection)
        // Tags do not receive internal storage and have size 0
        case BaseDataType::eTag:
            return 0;
        case BaseDataType::ePath:
            return sizeof(uint64_t);
        case BaseDataType::eCompactTransform:
            return 56;  //< Note this needs to match sizeof(omni::fabric::CompactTransform)
        case BaseDataType::eCount:
            break;
        };
        return 0;
    }

    /**
     * @brief Checks to see if the type is an array type, of any depth >= 1
     *
     * @return true If the type is an array type
     * @return false If the type is a scalar type (including those with componentCount > 1)
     */
    constexpr bool isArray() const
    {
        // Due to legacy support the relationship type has been defined as a scalar value but is secretly an array due
        // to typeinfo...
        return this->arrayDepth > 0 || this->baseType == BaseDataType::eRelationship;
    }

    /**
     * @brief Get the total size of the data storage used by this type
     *
     * @note This does not include any array elements for array types, only the pointer to their storage, but does include
     *       multiple components as part of the same basic data.
     *
     * @return constexpr size_t Size of the data described by the type
     */
    constexpr size_t size() const
    {
        return baseTypeSize() * componentCount;
    }

    /**
     * @brief Find the size of elements in the array, if this is an array
     *
     * @return size_t Size of elements in the array, or 0 if this type is not an array
     */
    CARB_DEPRECATED("Use size(). Arrays only differ by arrayDepth now, and pointers have their own BaseDataType.")
    size_t arrayElemSize() const
    {
        return size();
    }

    /**
     * @brief Deduce the BaseDataType enum value for a typename T.
     *
     * @return BaseDataType for T
     */
    template <typename T>
    static constexpr BaseDataType getBaseDataType();

    /**
     * @brief Construct as much Type information as we can for a typename T.
     *
     * @return Type for T
     */
    template <typename T>
    static constexpr Type getType();

private:
    /**
     * @brief Check compatibility of this Type versus a typename T (internal work).
     *
     * @return bool True if this is compatible with T.
     */
    template <typename T>
    bool isCompatibleWithInternal() const;

public:
    /**
     * @brief Check compatibility of this Type versus a typename T (public endpoint).
     *
     * @return bool True if this is compatible with T.
     */
    template <typename T>
    bool isCompatibleWith() const;
};

static_assert(Type(kUnknownType).encode() == kUnknownTypeEncoded, "Bad encoding for kUnknownType!");

/**
 * @brief Insertion operator for the type
 *
 * @param s Stream to which the string is to be emitted
 * @param type Attribute data type to be represented as a string in the stream
 * @return std::ostream& Input stream for chaining
 */
inline std::ostream& operator<<(std::ostream& s, const Type& type)
{
    s << type.getTypeName();
    return s;
}

/**
 * @brief Get the Type Name as a string
 *
 * @param t Type whose name is to be retrieved
 * @return std::string "Fabric style" name of the type
 */
inline std::string getTypeName(const Type& t)
{
    std::ostringstream name;
    name << t;
    return name.str();
}

} // namespace fabric
} // namespace omni

namespace std
{
/**
 * @brief Implements a simple hash value for a type definition so that types can be used in maps
 */
template <>
struct hash<omni::fabric::Type>
{
    //! Returns a hash value for the type, using its bit-value for the hash
    std::size_t operator()(const omni::fabric::Type& key) const
    {
        return omni::fabric::TypeC(key).type;
    }
};

/**
 * @brief Implements a simple hash value for a type-as-bits so that it can be used in maps
 */
template <>
struct hash<omni::fabric::TypeC>
{
    //! Returns a hash value for the type, using its bit-value for the hash
    std::size_t operator()(const omni::fabric::TypeC& key) const
    {
        return key.type;
    }
};
} // namespace std

#include "impl/Type.inl"
