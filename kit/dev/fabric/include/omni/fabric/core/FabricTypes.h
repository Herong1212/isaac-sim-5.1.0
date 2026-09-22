// Copyright (c) 2019-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/IdTypes.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <omni/fabric/Ordered_Set.h>
#include <omni/fabric/FabricTime.h>
#include <omni/fabric/RationalTime.h>
#include <omni/fabric/core/Intrinsics.h>
#include <omni/fabric/core/Macros.h>

#include <carb/cpp/Span.h>
#include <carb/extras/Hash.h>

#include <type_traits>
#include <inttypes.h>
#include <vector>

namespace omni
{
namespace fabric
{

#ifndef DOXYGEN_BUILD

template <typename U, typename V>
constexpr bool not_pointers_not_enum = !std::is_pointer<U>::value && !std::is_pointer<V>::value && !std::is_enum<U>::value && !std::is_enum<V>::value;

template <typename U, typename V>
constexpr bool u_is_pointer_only = std::is_pointer<U>::value && (std::is_same<V,size_t>::value || std::is_same<V,uintptr_t>::value || std::is_same<V,uint64_t>::value);

template <typename U, typename V>
constexpr bool v_is_pointer_only = std::is_pointer<V>::value && (std::is_same<U,size_t>::value || std::is_same<U,uintptr_t>::value || std::is_same<U,uint64_t>::value);

template <typename U, typename V>
constexpr bool u_is_enum_only = std::is_enum<U>::value && !std::is_enum<V>::value;

template <typename U, typename V>
constexpr bool v_is_enum_only = std::is_enum<V>::value && !std::is_enum<U>::value;

template <typename U, typename V, std::enable_if_t<not_pointers_not_enum<U,V>,bool> = true>
inline U safeConvert(V v)
{
    static_assert(std::is_same<U,V>::value, "Specialize me!");
    return v;
}

template <typename U, typename V, std::enable_if_t<u_is_pointer_only<U,V>,bool> = true>
inline U safeConvert(V v)
{
    return (U)v;
}

template <typename U, typename V, std::enable_if_t<v_is_pointer_only<U,V>,bool> = true>
inline U safeConvert(V v)
{
    return (U)v;
}

template <typename U, typename V, std::enable_if_t<u_is_enum_only<U,V>,bool> = true>
inline U safeConvert(V v)
{
    const size_t u_max = (size_t)std::numeric_limits< std::underlying_type_t<U> >::max();
    const size_t v_max = (size_t)std::numeric_limits<V>::max();
    if(v_max > u_max)
    {
        CARB_ASSERT(v <= u_max);
    }
    return (U)v;
}

template <typename U, typename V, std::enable_if_t<v_is_enum_only<U,V>,bool> = true>
inline U safeConvert(V v)
{
    const size_t u_max = (size_t)std::numeric_limits<U>::max();
    const size_t v_max = (size_t)std::numeric_limits< std::underlying_type_t<V> >::max();
    if(v_max > u_max)
    {
        CARB_ASSERT(v <= u_max);
    }
    return (U)v;
}

template <>
inline uint8_t safeConvert(uint64_t v)
{
    CARB_ASSERT(v <= (uint64_t)std::numeric_limits<uint8_t>::max());
    return (uint8_t)v;
}

template <>
inline uint16_t safeConvert(uint64_t v)
{
    CARB_ASSERT(v <= (uint64_t)std::numeric_limits<uint16_t>::max());
    return (uint16_t)v;
}

template <>
inline uint32_t safeConvert(uint64_t v)
{
    CARB_ASSERT(v <= (uint64_t)std::numeric_limits<uint32_t>::max());
    return (uint32_t)v;
}

template <>
inline uint64_t safeConvert(uint8_t v)
{
    return v;
}

template <>
inline uint64_t safeConvert(uint32_t v)
{
    return v;
}

template <>
inline long safeConvert(uint64_t v)
{
    CARB_ASSERT(v <= (uint64_t)std::numeric_limits<long>::max());
    return (long)v;
}

template <>
inline int safeConvert(uint32_t v)
{
    CARB_ASSERT(v <= (uint32_t)std::numeric_limits<int>::max());
    return (int)v;
}

template <typename U>
inline U safeConvert(BucketId v)
{
    return safeConvert<U>(v.id);
}

#endif // DOXYGEN_BUILD

template <class T, size_t Extent = carb::cpp::dynamic_extent>
using FabricSpan [[deprecated]] = carb::cpp::span<T, Extent>;

template <class T, size_t Extent = carb::cpp::dynamic_extent>
using Span = carb::cpp::span<T, Extent>;

template <class T>
inline Span<T> makeSpan(T* base, size_t Extent) noexcept { return Span<T>(base,Extent); }

template <class T, std::size_t N>
inline Span<T,N> makeSpan(T (&arr)[N]) noexcept { return carb::cpp::span<T,N>(arr); }

template <class T>
inline Span<T> makeSpan(std::vector<T>& v) noexcept { return carb::cpp::span<T>(v.data(),v.size()); }

template <class T>
inline Span<const T> makeSpan(const std::vector<T>& v) noexcept { return carb::cpp::span<const T>(v.data(),v.size()); }

template <class S, class T, size_t Extent = carb::cpp::dynamic_extent>
inline Span<S,Extent> convertSpan(Span<T,Extent> s) noexcept { return Span<S,Extent>((S*)s.data(),s.size()); }

template <class T, size_t Extent = carb::cpp::dynamic_extent>
inline bool noDataSpan(Span<T,Extent>& s) noexcept { return s.data()==nullptr || s.empty(); }

template <class T, size_t Extent = carb::cpp::dynamic_extent>
inline bool hasDataSpan(Span<T,Extent> s) noexcept { return s.data() && s.size(); }


// Fabric buckets UsdPrims according to their type and the UsdAttributes
// they have. For example, all the UsdGeomMeshes can go in one bucket, all the
// UsdSkelAnimations in another. The user can then quickly get a contiguous
// array of all the meshes, without having to traverse the whole stage.
//
// The name of a bucket is its set of attribute names (Tokens).
// As in the USD API, these tokens are the names used in USDA files, not C++
// type names like UsdGeomMesh.
//
// Example (using C++11 initializer lists to create the sets):
//   Bucket meshes = { Token("Mesh") };
//   Bucket skelAnimations = { Token("SkelAnimation") };
//
// For efficiency, set is an ordered c++ array, not std::set
using BucketNamesAndTypes = omni::fabric::set<AttrNameAndType>;
using BucketNames = omni::fabric::set<AttrName>;
using Bucket = BucketNamesAndTypes;
// Buckets store attribute values in contiguous arrays, and in C++ array
// indices are size_t
using ArrayIndex = size_t;
const ArrayIndex kInvalidArrayIndex = 0xffff'ffff'ffff'ffff;

struct BucketIdAndIndex
{
    BucketId bucketId;
    ArrayIndex bucketIndex;
};
static_assert(std::is_standard_layout<BucketIdAndIndex>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

// A struct that represents a subset of a bucket
struct BucketSubset
{
    BucketId bucket; // The target bucket from which we define a subset

    omni::fabric::set<TokenC>* attributes; // The subset of attributes to consider - only used if allAttributes ==
                                           // false, MUST be set otherwise
    omni::fabric::set<PathC>* paths; // The subset of paths to consider - only used if allPaths == false, MUST be set
                                     // otherwise

    bool allAttributes; // attribute filtering or not
    bool allPaths; // path filtering or not
};
static_assert(std::is_standard_layout<BucketSubset>::value,
              "BucketSubset must be standard layout as it is used in C-ABI interfaces");

// Content hash of an array attribute
using ContentHashType = carb::extras::hash128_t;
// Timeout in microseconds
using TimeSpanUS = uint64_t;

struct SparseAttributeContext
{
    // content hash of the sparse attribute data
    ContentHashType contentHash;
    // opaque context value from and only for the responsible populator system
    uint64_t populatorContextValue;
};

struct SparseArrayAttributeData
{
    // Source path that originally populated the sparse value
    // It is important to make this part of the sparse array attribute values because while a value might
    // be copied to a different path, the populator system doesn't know about this and potentially requires the original
    // path to find the data when population of the array data is requested
    PathC sourcePath;
    // Path of the populator system. The path only serves as a unique id to identify the populator system
    PathC populatorPath;
    // opaque context value from and only for the responsible populator system
    uint64_t populatorContextValue;
};

// Fabric stores data in untyped (byte) arrays.
// For conversion back to typed arrays, getArraySpan methods return the
// element size in bytes. They also return elementCount to allow the caller to
// wrap the array in std::span, or bounds check array access themselves.
// Fabric methods can't return std::span or gsl::span directly, because they
// are not C-ABI compatible. So we define SpanC/ConstSpanC, which are.
struct ConstSpanC
{
    const uint8_t* ptr;
    size_t elementCount;
    size_t elementSize;

    bool isValid() const
    {
        return ptr && elementCount && elementSize;
    }
};
static_assert(std::is_standard_layout<ConstSpanC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct SpanC
{
    uint8_t* ptr;
    size_t elementCount;
    size_t elementSize;

    // Casting SpanC to ConstSpanC is allowed, but not vice versa
    operator ConstSpanC() const
    {
        return { ptr, elementCount, elementSize };
    }

    bool isValid() const
    {
        return ptr && elementCount && elementSize;
    }
};
static_assert(std::is_standard_layout<SpanC>::value, "Struct must be standard layout as it is used in C-ABI interfaces");

struct ConstSpanWithTypeC
{
    const uint8_t* ptr;
    size_t elementCount;
    size_t elementSize;
    TypeC type;

    constexpr static ConstSpanWithTypeC empty()
    {
        return { nullptr, 0, 0, kUnknownType };
    }

    constexpr ConstSpanC toConstSpanC() const
    {
        return { ptr, elementCount, elementSize };
    }

    bool isValid() const
    {
        return ptr && elementCount && elementSize && Type(type).isValid();
    }

    template <typename T>
    carb::cpp::span<const T> getTypedSpan() const
    {
        if (VERIFY(Type(type).isCompatibleWith<T>()))
        {
            return carb::cpp::span<const T>(reinterpret_cast<const T*>(ptr), elementCount);
        }
        return carb::cpp::span<const T>();
    }

    template <typename T>
    const T* getTypedPointer() const
    {
        if (VERIFY(Type(type).isCompatibleWith<T>()))
        {
            return reinterpret_cast<const T*>(ptr);
        }
        return nullptr;
    }
};
static_assert(std::is_standard_layout<ConstSpanWithTypeC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct SpanWithTypeC
{
    uint8_t* ptr;
    size_t elementCount;
    size_t elementSize;
    TypeC type;

    constexpr static SpanWithTypeC empty()
    {
        return { nullptr, 0, 0, kUnknownType };
    }

    // Casting SpanWithTypeC to ConstSpanWithTypeC is allowed, but not vice versa
    operator ConstSpanWithTypeC() const
    {
        return { ptr, elementCount, elementSize, type };
    }

    constexpr SpanC toSpanC()
    {
        return { ptr, elementCount, elementSize };
    }

    constexpr ConstSpanC toConstSpanC() const
    {
        return { ptr, elementCount, elementSize };
    }

    bool isValid() const
    {
        return ptr && elementCount && elementSize && Type(type).isValid();
    }

    template<typename T>
    carb::cpp::span<T> getTypedSpan() const
    {
        if (VERIFY(Type(type).isCompatibleWith<T>()))
        {
            return carb::cpp::span<T>(reinterpret_cast<T*>(ptr), elementCount);
        }
        return carb::cpp::span<T>();
    }

    template<typename T>
    T* getTypedPointer() const
    {
        if (VERIFY(Type(type).isCompatibleWith<T>()))
        {
            return reinterpret_cast<T*>(ptr);
        }
        return nullptr;
    }
};
static_assert(std::is_standard_layout<SpanWithTypeC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

template <typename T>
struct ConstSpanOfC
{
    const T* ptr;
    size_t elementCount;

    operator ConstSpanC() const
    {
        return { ptr, elementCount, sizeof(T) };
    }

    const T& operator[](size_t index) const
    {
        CARB_ASSERT(index < elementCount);
        return ptr[index];
    }

    bool isValid() const
    {
        return ptr && elementCount;
    }
};
typedef ConstSpanOfC<size_t> ConstSpanSizeC;
static_assert(std::is_standard_layout<ConstSpanSizeC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

template <typename T>
struct SpanOfC
{
    T* ptr;
    size_t elementCount;

    // Casting to ConstSpanOfC<> is allowed, but not vice versa
    operator ConstSpanOfC<T>() const
    {
        return { ptr, elementCount };
    }

    operator SpanC() const
    {
        return { reinterpret_cast<uint8_t*>(ptr), elementCount, sizeof(T) };
    }

    T& operator[](size_t index)
    {
        CARB_ASSERT(index < elementCount);
        return ptr[index];
    }

    bool isValid() const
    {
        return ptr && elementCount;
    }
};
typedef SpanOfC<size_t> SpanSizeC;
static_assert(std::is_standard_layout<SpanSizeC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");


template <typename T>
struct ConstSpanWithTypeOfC
{
    const T* ptr;
    size_t elementCount;
    TypeC type;

    operator ConstSpanWithTypeC() const
    {
        return { reinterpret_cast<const uint8_t*>(ptr), elementCount, sizeof(T), type };
    }

    const T& operator[](size_t index) const
    {
        CARB_ASSERT(index < elementCount);
        return ptr[index];
    }

    ConstSpanC toConstSpanC() const
    {
        return { ptr, elementCount, sizeof(T) };
    }

    ConstSpanWithTypeC toConstSpanWithTypeC() const
    {
        return { reinterpret_cast<const uint8_t*>(ptr), elementCount, sizeof(T), type };
    }

    bool isValid() const
    {
        return ptr && elementCount;
    }
};

template <typename T>
struct SpanWithTypeOfC
{
    T* ptr;
    size_t elementCount;
    TypeC type;

    // Casting to ConstSpanWithTypeOfC<> is allowed, but not vice versa
    operator ConstSpanWithTypeOfC<T>() const
    {
        return { ptr, elementCount };
    }

    T& operator[](size_t index)
    {
        CARB_ASSERT(index < elementCount);
        return ptr[index];
    }

    ConstSpanC toConstSpanC() const
    {
        return { reinterpret_cast<uint8_t*>(ptr), elementCount, sizeof(T) };
    }

    SpanC toSpanC() const
    {
        return { reinterpret_cast<uint8_t*>(ptr), elementCount, sizeof(T) };
    }

    ConstSpanWithTypeC toConstSpanWithTypeC() const
    {
        return { reinterpret_cast<uint8_t*>(ptr), elementCount, sizeof(T), type };
    }

    SpanWithTypeC toSpanWithTypeC() const
    {
        return { reinterpret_cast<uint8_t*>(ptr), elementCount, sizeof(T), type };
    }

    bool isValid() const
    {
        return ptr && elementCount;
    }
};


// An ArrayPointersAndSizesC is an array of immutably sized mutable
// data arrays
//
// Rules (enforced by const):
// {
//     ArrayPointersAndSizesC ps;
//
//     // Allowed: Changing inner array values
//     ps.arrayPtrs[0][0] = 1
//
//     // Disallowed: Changing array pointers
//     ps.arrayPtrs[0] = (uint8_t*)p;
//
//     // Disallowed: Changing inner array sizes
//     ps.sizes[0] = 1;
// }
struct ArrayPointersAndSizesC
{
    uint8_t* const* arrayPtrs;
    const size_t* sizes;
    size_t elementCount;
};
static_assert(std::is_standard_layout<ArrayPointersAndSizesC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct ArrayPointersAndSizesWithTypeC
{
    uint8_t* const* arrayPtrs;
    const size_t* sizes;
    size_t elementCount;
    TypeC type;

    constexpr static ArrayPointersAndSizesWithTypeC empty()
    {
        return { nullptr, nullptr, 0, kUnknownType };
    }

    constexpr ArrayPointersAndSizesC toArrayPointersAndSizesC()
    {
        return { arrayPtrs, sizes, elementCount };
    }
};
static_assert(std::is_standard_layout<ArrayPointersAndSizesWithTypeC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

// A ConstArrayPointersAndSizesC is an array of immutably sized immutable
// data arrays
//
// Rules (enforced by const):
// {
//     ConstArrayPointersAndSizesC ps;
//
//     // Disallowed: Changing inner array values
//     ps.arrayPtrs[0][0] = 1
//
//     // Disallowed: Changing array pointers
//     ps.arrayPtrs[0] = (uint8_t*)p;
//
//     // Disallowed: Changing inner array sizes
//     ps.sizes[0] = 1;
// }
struct ConstArrayPointersAndSizesC
{
    const uint8_t* const* arrayPtrs;
    const size_t* sizes;
    size_t elementCount;
};
static_assert(std::is_standard_layout<ConstArrayPointersAndSizesC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct ConstArrayPointersAndSizesWithTypeC
{
    const uint8_t* const* arrayPtrs;
    const size_t* sizes;
    size_t elementCount;
    TypeC type;

    constexpr static ConstArrayPointersAndSizesWithTypeC empty()
    {
        return { nullptr, nullptr, 0, kUnknownType };
    }

    constexpr ConstArrayPointersAndSizesC toConstArrayPointersAndSizesC()
    {
        return { arrayPtrs, sizes, elementCount };
    }
};
static_assert(std::is_standard_layout<ConstArrayPointersAndSizesWithTypeC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct ConstPathSpanC
{
    const Path* ptr;
    size_t elementCount;
};
static_assert(std::is_standard_layout<ConstPathSpanC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

using ConstPathCSpan = ConstPathSpanC;

struct ConstAttrNameAndTypeSpanC
{
    const AttrNameAndType* ptr;
    size_t elementCount;
};
static_assert(std::is_standard_layout<ConstAttrNameAndTypeSpanC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct ConstChangedIndicesC
{
    bool allIndicesChanged;
    ConstSpanSizeC changedIndices;
};
static_assert(std::is_standard_layout<ConstChangedIndicesC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct ConstChangedIndicesSpanC
{
    const ConstChangedIndicesC* ptr;
    size_t elementCount;
};
static_assert(std::is_standard_layout<ConstChangedIndicesSpanC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct BucketChangesC
{
    // Which attributes changed
    ConstAttrNameAndTypeSpanC changedAttributes;

    // For each attribute, which prims changed?
    ConstChangedIndicesSpanC changedIndices;
    ConstPathCSpan pathArray;
};
static_assert(std::is_standard_layout<BucketChangesC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct AddedPrimIndicesC
{
    // Which prims were added?
    ConstSpanSizeC addedIndices;
};
static_assert(std::is_standard_layout<AddedPrimIndicesC>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct StageWithHistorySnapshot
{
    bool valid;
    size_t id;
};
static_assert(std::is_standard_layout<StageWithHistorySnapshot>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct AttrCreateSpec
{
    AttrNameAndType nameAndType;

    // If non-null, a pointer to the desired initial value of the attribute
    const void* value;

    // If nameAndType.type.isArray(), then arrayElemCount is the number of
    // elements, else it is ignored
    size_t arrayElemCount;
};
static_assert(std::is_standard_layout<AttrCreateSpec>::value,
    "Struct must be standard layout as it is used in C-ABI interfaces");

struct DirectoryEntry;
using DirectoryIndex = DirectoryEntry*;
constexpr DirectoryIndex DirectoryNullIndex = nullptr;

struct FabricPrimFilter
{
    Span<AttrNameAndType> requireAll;
    Span<AttrNameAndType> requireAny;
    Span<AttrNameAndType> requireNone;
};
static_assert(std::is_standard_layout<FabricPrimFilter>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct FabricAttrFilter
{
    Span<AttrNameAndType> passFilter;
    Span<AttrNameAndType> rejectFilter;
};
static_assert(std::is_standard_layout<FabricAttrFilter>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

struct FabricCopyFilter
{
    FabricPrimFilter primFilter;
    FabricAttrFilter attrFilter;
};
static_assert(std::is_standard_layout<FabricCopyFilter>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

} // namespace fabric
} // namespace omni
