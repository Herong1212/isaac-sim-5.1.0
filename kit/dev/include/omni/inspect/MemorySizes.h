// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// Collection of helpers to get memory size information

#include <array>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <type_traits>

namespace omni {
namespace inspect {

// Uncomment this to enable debug output in this file
// #define MEMORY_DEBUG
constexpr bool memoryDebug{
#ifdef MEMORY_DEBUG
    true
#else
    false
#endif
};

template <typename> struct sfinae_true : std::true_type {};
template <typename> struct sfinae_false : std::false_type {};
using SizeFunction = std::add_pointer<size_t()>::type;
//
// This detail implementation will allow switching on map types so that their size can be recursively calculated
//
namespace detail
{
    // Until C++17...
    template <typename... Ts> using void_t = void;

    // Check for map-like objects
    template<typename Object, typename U = void> struct isMappishImpl : std::false_type {};
    template<typename Object>
    struct isMappishImpl<Object, void_t<typename Object::key_type,
                                     typename Object::mapped_type,
                                     decltype(std::declval<Object&>()[std::declval<const typename Object::key_type&>()])>>
    : std::true_type {};

    // Check for array types, whose size is entirely described by the object size
    template<typename Contained> struct isArrayImpl : std::false_type {};
    template<typename Contained, size_t Size>
    struct isArrayImpl<std::array<Contained, Size>> : std::true_type {};

    // Check for other iterable types
    template<typename Contained> struct isIterableImpl : std::false_type {};
    template<typename Contained, typename Allocator>
    struct isIterableImpl<std::vector<Contained, Allocator>> : std::true_type {};
    template<typename Contained, typename Allocator>
    struct isIterableImpl<std::set<Contained, Allocator>> : std::true_type {};
    template<typename Contained, typename Allocator>
    struct isIterableImpl<std::unordered_set<Contained, Allocator>> : std::true_type {};

    template <typename Object, typename Enable = void> struct hasCalculateMemorySizeFunctionImpl : std::false_type {};
    template <typename Object>
    struct hasCalculateMemorySizeFunctionImpl<Object, void_t<decltype(std::declval<const Object&>().calculateMemorySize())>>
    : std::true_type {};
}
template <typename Object> struct isMappish : detail::isMappishImpl<Object>::type {};
template <typename Object> struct isArray : detail::isArrayImpl<Object>::type {};
template <typename Object> struct isIterable : detail::isIterableImpl<Object>::type {};
template <typename Object> struct hasCalculateMemorySizeFunction : detail::hasCalculateMemorySizeFunctionImpl<Object>::type {};

//
// Fallback to sizeof()
template <typename Object, std::enable_if_t<! hasCalculateMemorySizeFunction<Object>{} && ! isMappish<Object>{} && ! isIterable<Object>{} && ! isArray<Object>{}, bool> = 0>
size_t calculateMemorySize(const Object& object)
{
    memoryDebug && (std::cout << "POD " << typeid(object).name() << " = " << sizeof(Object) << std::endl);
    return sizeof(Object);
}

// If the object has a calculateMemorySize() function use it
//
template <typename Object, typename std::enable_if_t<hasCalculateMemorySizeFunction<Object>{}, bool> = 0>
size_t calculateMemorySize(const Object& object)
{
    memoryDebug && (std::cout << "Has Method " << typeid(object).name() << " = " << object.calculateMemorySize() << std::endl);
    return object.calculateMemorySize();
}

//
// Third check, has to be at the end so that recursive calls work, handle map-like objects (map, unordered_map)
template <typename Object, std::enable_if_t<isMappish<Object>{}, bool> = 0>
size_t calculateMemorySize(const Object& object)
{
    size_t size = sizeof(Object);
    for(auto it = object.begin(); it != object.end(); ++it)
    {
        size += calculateMemorySize(it->first);
        size += calculateMemorySize(it->second);
    }
    memoryDebug && (std::cout << "Mappish " << typeid(object).name() << " = " << size << std::endl);
    return size;
}

//
// Fourth check, handle the array type, which doesn't have a separately allocated set of members
template <typename Object, std::enable_if_t<isArray<Object>{}, bool> = 0>
size_t calculateMemorySize(const Object& object)
{
    memoryDebug && (std::cout << "Array " << typeid(object).name() << " = " << sizeof(Object) << std::endl);
    return sizeof(Object);
}

//
// Fifth check, has to be at the end so that recursive calls work, handle the rest of the single object container-like objects
// (set, unordered_set, vector)
template <typename Object, std::enable_if_t<isIterable<Object>{} && ! isArray<Object>{}, bool> = 0>
size_t calculateMemorySize(const Object& object)
{
    size_t size = sizeof(Object);
    for(const auto& member : object)
    {
        size += calculateMemorySize(member);
    }
    memoryDebug && (std::cout << "Iterable " << typeid(object).name() << " = " << size << std::endl);
    return size;
}

// Helper macro to make it easy to add the memory used by class members to the IInspector
#define INSPECT_MEMORY_CLASS_MEMBER(INSPECTOR, OBJECT, MEMBER_NAME) \
    INSPECTOR.useMemory(&(OBJECT.MEMBER_NAME), omni::inspect::calculateMemorySize(OBJECT.MEMBER_NAME));

} // namespace inspect
} // namespace omni
