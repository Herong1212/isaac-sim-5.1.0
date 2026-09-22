// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <cstdint>

namespace omni
{
    //////////////////////////////////////////////////////////////////////////
    // Hashing functions. These expose the same functions used internally
    // by the resource manager to compute data deduplication.
    //////////////////////////////////////////////////////////////////////////

    // Use this table to estimate how many bits in a hash are required to minimize the chance of a
    // collisision:
    //    1. Liberally estimate the size of the world (number of objects you are going to hash and
    //       coexisting at runtime).
    //    2. Look in the table for a any number higher than your estimate.
    //    3. Now look at the column header to see the probability of at least one collision.
    //    4. Anything lower than p=1.0e-12 means direct comparison of hashes is safer and less likely
    //       than your computer to be destroyed by a metheorite within the next hour.
    // |           |            |   Number of hashed elements such that probability of collision >= p   |
    // | Hash bits | Hash space | p=1.0e-18 | p=1.0e-15 | p=1.0e-12 | p=1.0e-9  | p=1.0e-6  | p=1.0e-3  |
    // |-----------|------------|-----------|-----------|-----------|-----------|-----------|-----------|
    // |     32    |   4.3e9    |   2       |   2       |   2       |   2.9     |   93      |   2.9e6   |
    // |     64    |   1.8e19   |   6.1     |   1.9e2   |   6.1e3   |   1.9e5   |   6.1e6   |   1.9e8   |
    // |    128    |   3.4e38   |   2.6e10  |   8.2e11  |   2.6e13  |   8.2e14  |   2.6e16  |   8.3e17  |

    // The 128 bits hash type. Prefer 128 hash bits when it is desirable to run hash-based
    // with minimal chance of hash collision.
    struct hash128_t
    {
        hash128_t() = default;
        hash128_t(const hash128_t& other) = default;
        explicit hash128_t(uint64_t value) : lower(value), upper(value)
        {
        }

        hash128_t(uint64_t lower_, uint64_t upper_) : lower(lower_), upper(upper_)
        {
        }

        hash128_t& operator=(const hash128_t& other) = default;
        hash128_t& operator=(uint64_t value)
        {
            lower = value;
            upper = value;
            return *this;
        }

        // A hash is considered valid if not zero
        explicit operator bool() const
        {
            return (lower != 0) & (upper != 0);
        }

        // A minimal set of comparison operators to use std containers and algorithms
        bool operator==(const hash128_t& other) const
        {
            return (lower == other.lower) & (upper == other.upper);
        }
        bool operator!=(const hash128_t& other) const
        {
            return (lower != other.lower) | (upper != other.upper);
        }
        bool operator<(const hash128_t& other) const
        {
            return (upper == other.upper) ? (lower < other.lower) : (upper < other.upper);
        }

        uint64_t lower = 0;
        uint64_t upper = 0;
    };

    struct hash128POD_t
    {
        uint64_t lower;
        uint64_t upper;
    };

    inline hash128POD_t toPod(hash128_t value) { return { value.lower, value.upper}; }
    inline hash128_t fromPod(const hash128POD_t& value) { return { value.lower, value.upper }; }

    // A hash is considered valid if not zero
    inline bool isValid(const hash128_t& h)
    {
        // Call the overloaded bool operator
        return static_cast<bool>(h);
    }

} // omni
