// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "../Defines.h"

#include "../cpp/Bit.h"
#include "../math/Int128.h"

#include <string>

namespace carb
{
namespace extras
{

namespace detail
{

// 0x0000000001000000000000000000013B
constexpr auto kFnv128Prime = math::make_uint128_t(0x0000000001000000, 0x000000000000013B);

} // namespace detail

struct hash128_t
{
    uint64_t d[2];
};
static_assert(sizeof(math::uint128_t) == sizeof(hash128_t), "Invalid assumption");
// assumes little-endian
static_assert(carb::cpp::endian::native == carb::cpp::endian::little, "Invalid assumption");


// FNV-1a 128-bit basis: 0x6c62272e07bb014262b821756295c58d
constexpr static hash128_t kFnv128Basis = { 0x62b821756295c58d, 0x6c62272e07bb0142 };

inline hash128_t hash128FromHexString(const char* buffer, const char** end = nullptr)
{
    math::uint128_t u128 = {};

    // skip 0x if necessary
    if (buffer[0] == '0' && buffer[1] == 'x')
        buffer += 2;

    while (*buffer)
    {
        unsigned num;
        if (*buffer >= '0' && *buffer <= '9')
            num = unsigned(*buffer - '0');
        else if (*buffer >= 'a' && *buffer <= 'z')
            num = unsigned(*buffer - 'a' + 10);
        else if (*buffer >= 'A' && *buffer <= 'Z')
            num = unsigned(*buffer - 'A' + 10);
        else
        {
            // Error
            CARB_ASSERT(0);
            if (end)
                *end = buffer;
            return cpp::bit_cast<hash128_t>(u128);
        }

        u128 *= 16;
        u128 += num;
        ++buffer;
    }

    if (end)
        *end = buffer;
    return cpp::bit_cast<hash128_t>(u128);
}

// Deprecated function
CARB_DEPRECATED("Use hash128FromHexString() instead") inline bool hashFromString(const char* buffer, hash128_t& hash)
{
    const char* end;
    hash = hash128FromHexString(buffer, &end);
    return *end == '\0';
}

inline hash128_t fnv128hash(const uint8_t* data, size_t size, hash128_t seed = kFnv128Basis)
{
    auto u128 = cpp::bit_cast<math::uint128_t>(seed);

    const uint8_t* const end = data + size;

    // Align
    if (CARB_UNLIKELY(!!(size_t(data) & 0x7) && (end - data) >= 8))
    {
        do
        {
            u128 ^= *(data++);
            u128 *= detail::kFnv128Prime;
        } while (!!(size_t(data) & 0x7));
    }

    // Unroll the loop
    while ((end - data) >= 8)
    {
        uint64_t val = *reinterpret_cast<const uint64_t*>(data);
#define HASH_STEP(v)                                                                                                   \
    u128 ^= uint8_t(v);                                                                                                \
    u128 *= detail::kFnv128Prime
        HASH_STEP(val);
        HASH_STEP(val >>= 8);
        HASH_STEP(val >>= 8);
        HASH_STEP(val >>= 8);
        HASH_STEP(val >>= 8);
        HASH_STEP(val >>= 8);
        HASH_STEP(val >>= 8);
        HASH_STEP(val >>= 8);
#undef HASH_STEP
        data += 8;
    }

    // Handle remaining
    while (data != end)
    {
        u128 ^= *(data++);
        u128 *= detail::kFnv128Prime;
    }

    return cpp::bit_cast<hash128_t>(u128);
}

namespace detail
{
// this can't be a lambda because there's no consistent way to add this
// attribute to a lambda between GCC 7 and 9
CARB_ATTRIBUTE(no_sanitize_address) inline uint64_t read64(const void* data)
{
    return *static_cast<const uint64_t*>(data);
}
} // namespace detail

inline hash128_t fnv128hashString(const char* data, hash128_t seed = kFnv128Basis)
{
    auto u128 = cpp::bit_cast<math::uint128_t>(seed);

    if (!!(size_t(data) & 0x7))
    {
        // Align
        for (;;)
        {
            if (*data == '\0')
                return cpp::bit_cast<hash128_t>(u128);

            u128 ^= uint8_t(*(data++));
            u128 *= detail::kFnv128Prime;

            if (!(size_t(data) & 0x7))
                break;
        }
    }

    // Use a bit trick often employed in strlen() implementations to return a non-zero value if any byte within a word
    // is zero. This can sometimes be falsely positive for UTF-8 strings, so handle those
    for (;;)
    {
        uint64_t val = ::carb::extras::detail::read64(data);
        if (CARB_LIKELY(!((val - 0x0101010101010101) & 0x8080808080808080)))
        {
            // None of the next 8 bytes are zero
#define HASH_STEP(v)                                                                                                   \
    u128 ^= uint8_t(v);                                                                                                \
    u128 *= detail::kFnv128Prime
            HASH_STEP(val);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
#undef HASH_STEP
        }
        else
        {
            uint8_t b;
// One of the next 8 bytes *might* be zero
#define HASH_STEP(v)                                                                                                   \
    b = uint8_t(v);                                                                                                    \
    if (CARB_UNLIKELY(!b))                                                                                             \
        return cpp::bit_cast<hash128_t>(u128);                                                                         \
    u128 ^= b;                                                                                                         \
    u128 *= detail::kFnv128Prime
            HASH_STEP(val);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
            HASH_STEP(val >>= 8);
#undef HASH_STEP
        }
        data += 8;
    }
}


constexpr bool operator==(const hash128_t& lhs, const hash128_t& rhs)
{
    return lhs.d[0] == rhs.d[0] && lhs.d[1] == rhs.d[1];
}

constexpr bool operator!=(const hash128_t& lhs, const hash128_t& rhs)
{
    return !(lhs == rhs);
}

constexpr bool operator<(const hash128_t& lhs, const hash128_t& rhs)
{
    if (lhs.d[1] < rhs.d[1])
        return true;
    if (rhs.d[1] < lhs.d[1])
        return false;
    return lhs.d[0] < rhs.d[0];
}

constexpr bool operator>(const hash128_t& lhs, const hash128_t& rhs)
{
    return rhs < lhs;
}

constexpr bool operator<=(const hash128_t& lhs, const hash128_t& rhs)
{
    return !(lhs > rhs);
}

constexpr bool operator>=(const hash128_t& lhs, const hash128_t& rhs)
{
    return !(lhs < rhs);
}

} // namespace extras
} // namespace carb

namespace std
{

template <>
struct hash<carb::extras::hash128_t>
{
    using argument_type = carb::extras::hash128_t;
    using result_type = std::size_t;
    result_type operator()(argument_type const& s) const noexcept
    {
        return s.d[0] ^ s.d[1];
    }
};

inline std::string to_string(const carb::extras::hash128_t& hash)
{
    std::string strBuffer(32, '0');

    constexpr static char nibbles[] = {
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f',
    };
    auto fill64 = [](char* buffer, uint64_t v) {
        buffer += 16;
        while (v != 0)
        {
            *(--buffer) = nibbles[v & 0xf];
            v >>= 4;
        }
    };
    fill64(std::addressof(strBuffer.at(16)), hash.d[0]);
    fill64(std::addressof(strBuffer.at(0)), hash.d[1]);
    return strBuffer;
}

} // namespace std
