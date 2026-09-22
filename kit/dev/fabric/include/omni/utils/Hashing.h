// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "HashTypes.h"
#define XXH_INLINE_ALL /* XXH128_hash_t */
#include <xxhash/xxhash.h>
#include <carb/extras/Hash.h>

#include <cstdint>
#include <string>
#include <type_traits>
#include <vector>

namespace omni
{
    namespace detail
    {
#if CARB_HAS_CPP17
        template <typename T>
        using HasUniqueObjectRepresentations = std::has_unique_object_representations<T>;
#else
        // Absent C++17 the hashing code cannot verify input values don't have padding bits.
        template <typename T>
        struct HasUniqueObjectRepresentations: public std::integral_constant<bool, true>
        {};
#endif

        template <typename T>
        struct IsFundamentalOrEnum: public std::integral_constant<bool,
            std::disjunction<std::is_fundamental<T>, std::is_enum<T>>::value>
        {};
    }

    // Returns a hash value which incorporates a given hashed value `seed` and the std::hash of an arbitrary value `v`.
    // Derived from Boost.
    template <typename T>
    inline std::size_t hashCombine(std::size_t seed, const T& v)
    {
        std::hash<T> hasher;
        return seed ^ (hasher(v) + 0x9e3779b9 + (seed << 6) + (seed >> 2));
    }

    // Returns a hash value incorporating a given hashed value `seed` with the std::hash of arbitrary values.
    template <typename First, typename... Rest>
    inline uint64_t hashCombine(std::size_t seed, const First& first, const Rest&... rest)
    {
        return hashCombine(hashCombine(seed, first), rest...);
    }

    // Returns a hash value incorporating the std::hash values of the given values.
    template <typename First, typename... Rest>
    inline uint64_t hashValues(const First& first, const Rest&... rest)
    {
        return hashCombine(0, first, rest...);
    }

    inline hash128_t toHash128_t(const XXH128_hash_t& other)
    {
        return { other.low64, other.high64 };
    }


    struct Hash128Builder
    {
        XXH3_state_t state;

        Hash128Builder()
        {
            XXH3_128bits_reset(&state);
        }

        Hash128Builder& operator<<(const char* string)
        {
            addBuffer(string, strlen(string));
            return *this;
        }

        Hash128Builder& operator<<(const std::string& string)
        {
            return *this << string.c_str();
        }

        // Vector inserter.
        //
        // Only supported for vectors of fundamental or enum types to avoid accidentally hashing things that should not
        // be hashed. Use addRawValue() or define your own inserter in the omni namespace for custom types.
        template<typename T>
        Hash128Builder& operator<<(const std::vector<T>& valueVector)
        {
            static_assert(detail::IsFundamentalOrEnum<T>::value,
                "Hash128Builder::operator<<(const std::vector<T>&) is only supported for vectors of fundamental or enum types!");

            if (!valueVector.empty())
            {
                addBuffer(valueVector.data(), sizeof(T) * valueVector.size());
            }
            return *this;
        }

        // Value inserter.
        //
        // Only supported for fundamental types to avoid accidentally hashing things that should not be hashed.
        // Use addRawValue() or define your own inserter in the omni namespace for custom types.
        template<typename T>
        Hash128Builder& operator<<(const T& value)
        {
            static_assert(detail::IsFundamentalOrEnum<T>::value,
                "Hash128Builder::operator<<(const T&) is only supported for fundamental and enum types!");

            addRawValue(value);
            return *this;
        }

        Hash128Builder& operator<<(hash128_t hash)
        {
            addRawValue(hash);
            return *this;
        }

        Hash128Builder& operator<<(carb::extras::hash128_t hash)
        {
            addRawValue(hash);
            return *this;
        }

        void addBuffer(const void* data, size_t sizeInBytes)
        {
            XXH3_128bits_update(&state, data, sizeInBytes);
        }

        // Hashes the bits of the given value.
        //
        // Only supported for unique object representation types to avoid accidentally hashing objects with implicit
        // padding.
        // If your custom type contains implicit padding either define your own inserter in the omni namespace or, if
        // you're really sure you want to hash implicit padding, use addBuffer().
        template <typename T>
        void addRawValue(const T& value)
        {
            static_assert(detail::HasUniqueObjectRepresentations<T>::value,
                "Hash128Builder::addRawValue is not supported for types with implicit padding");

            XXH3_128bits_update(&state, &value, sizeof(T));
        }

        hash128_t getHash() const
        {
            return toHash128_t(XXH3_128bits_digest(&state));
        }
    };

} // omni

namespace std
{
    // std::hash template specialization for hash128_t. Useful to use hash128_t as key in an
    // std::unordered_map or similar containers
    template <>
    struct hash<omni::hash128_t>
    {
        std::size_t operator()(const omni::hash128_t& k) const
        {
            // hash128_t has exceptional entropy and distribution properties. For the purpose of
            // cereating a lower grade hash that is suitable for std::unordered_map, we can simply
            // pick the lower 64 bits of the hash.
            return std::size_t{ k.lower };
        }
    };
} // namespace std
