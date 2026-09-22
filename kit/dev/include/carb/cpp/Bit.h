// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief C++14-compatible implementation of select functionality from C++ `<bit>` library.
#pragma once

#include "TypeTraits.h"
#include "detail/ImplDummy.h"
#include "../extras/CpuInfo.h"

#include <limits>
#include <type_traits>

#if CARB_HAS_CPP20
#    include <bit>
#endif

#if !defined(DOXYGEN_BUILD) && !defined(__cpp_lib_bitops)

// CARB_POPCNT is 1 if the compiler is targeting a CPU with AVX instructions or GCC reports popcnt is available. It is
// undefined at the bottom of the file.
#    if defined(__AVX__) /* MSC/GCC */ || defined(__POPCNT__) /* GCC */
#        define CARB_POPCNT 1
#    else
#        define CARB_POPCNT 0
#    endif

// CARB_LZCNT is 1 if the compiler is targeting a CPU with AVX2 instructions or GCC reports lzcnt is available. It is
// undefined at the bottom of the file.
#    if defined(__AVX2__) /* MSC/GCC */ || defined(__LZCNT__) /* GCC */
#        define CARB_LZCNT 1
#    else
#        define CARB_LZCNT 0
#    endif

#    if CARB_COMPILER_MSC
extern "C"
{
#        if CARB_AARCH64
#            if _MSC_VER >= 1932 || CARB_TOOLCHAIN_CLANG
#                pragma intrinsic(_CountOneBits)
#                pragma intrinsic(_CountOneBits64)
    unsigned int _CountOneBits(unsigned long);
    unsigned int _CountOneBits64(unsigned __int64);
#            else
    // VS2019 is missing these intrinsics. Fixed in VS2022 Update 1
    // See: https://developercommunity.visualstudio.com/t/-countonebits-intrinsics-are-not-defined-for-arm64/957551
    inline unsigned int _CountOneBits64(unsigned __int64 val)
    {
        // Naive impl
        int count = 0;
        while (val != 0)
        {
            ++count;
            val = val & (val - 1);
        }
        return count;
    }
    inline unsigned int _CountOneBits(unsigned long val)
    {
        return _CountOneBits64(val);
    }
#            endif
#        else
#            pragma intrinsic(__popcnt)
#            pragma intrinsic(__popcnt64)
    unsigned int __popcnt(unsigned int value);
    unsigned __int64 __popcnt64(unsigned __int64 value);
#        endif
#        pragma intrinsic(_BitScanReverse)
#        pragma intrinsic(_BitScanReverse64)
#        pragma intrinsic(_BitScanForward)
#        pragma intrinsic(_BitScanForward64)
    unsigned char _BitScanReverse(unsigned long* _Index, unsigned long _Mask);
    unsigned char _BitScanReverse64(unsigned long* _Index, unsigned __int64 _Mask);
    unsigned char _BitScanForward(unsigned long* _Index, unsigned long _Mask);
    unsigned char _BitScanForward64(unsigned long* _Index, unsigned __int64 _Mask);
#        if CARB_LZCNT
#            pragma intrinsic(__lzcnt)
#            pragma intrinsic(__lzcnt16)
#            pragma intrinsic(__lzcnt64)
    unsigned int __lzcnt(unsigned int);
    unsigned short __lzcnt16(unsigned short);
    unsigned __int64 __lzcnt64(unsigned __int64);
#        endif
}
#    elif CARB_COMPILER_GNUC
#    else
CARB_UNSUPPORTED_PLATFORM();
#    endif
#endif

namespace carb
{
namespace cpp
{
namespace detail
{
#if !defined(DOXYGEN_BUILD) && !defined(__cpp_lib_bitops)

// Naive implementation of popcnt for CPUs without built in instructions.
template <class T, std::enable_if_t<std::is_unsigned<T>::value, bool> = true>
constexpr int popCountImpl(T val) noexcept
{
    int count = 0;
    while (val != 0)
    {
        ++count;
        val = val & (val - 1);
    }
    return count;
}

// The Helper class is specialized by type and size since many intrinsics have different names for different sizes.
template <class T, size_t Size = sizeof(T)>
class Helper;

// Specialization for functions where sizeof(T) >= 1
template <class T>
class Helper<T, 1>
{
public:
    static_assert(std::numeric_limits<T>::is_specialized, "Requires numeric type");
    using Signed = typename std::make_signed_t<T>;
    using Unsigned = typename std::make_unsigned_t<T>;
    // popCount implementation for 1-4 bytes integers
    static int popCount(const T& val)
    {
#    if CARB_COMPILER_MSC
#        if !CARB_POPCNT // Skip the check if we know we have the instruction
        // Only use the intrinsic if it's supported on the CPU
        static extras::CpuInfo cpuInfo;
        if (!cpuInfo.popcntSupported())
        {
            return popCountImpl((Unsigned)val);
        }
        else
#        endif
        {
#        if CARB_X86_64
            return (int)__popcnt((unsigned long)(Unsigned)val);
#        else
            return (int)_CountOneBits((unsigned long)(Unsigned)val);
#        endif
        }
#    else
        return __builtin_popcount((unsigned long)(Unsigned)val);
#    endif
    }
    static constexpr void propagateHighBit(T& n)
    {
        n |= (n >> 1);
        n |= (n >> 2);
        n |= (n >> 4);
    }

    static int countl_zero(T val)
    {
#    if CARB_LZCNT
#        if CARB_COMPILER_MSC
        return int(__lzcnt16((unsigned short)(Unsigned)val)) - (16 - std::numeric_limits<T>::digits);
#        else
        return int(__builtin_ia32_lzcnt_u16((unsigned short)(Unsigned)val)) - (16 - std::numeric_limits<T>::digits);
#        endif
#    else
#        if CARB_COMPILER_MSC
        unsigned long index;
        constexpr static int diff = std::numeric_limits<unsigned long>::digits - std::numeric_limits<T>::digits;
        return _BitScanReverse(&index, (unsigned long)(Unsigned)val) ?
                   (std::numeric_limits<unsigned long>::digits - 1 - index - diff) :
                   std::numeric_limits<T>::digits;
#        else
        // According to docs, undefined if val == 0
        return val ? __builtin_clz((unsigned int)(Unsigned)val) - (32 - std::numeric_limits<T>::digits) :
                     std::numeric_limits<T>::digits;
#        endif
#    endif
    }

    static int countr_zero(T val)
    {
        if (val == 0)
        {
            return std::numeric_limits<T>::digits;
        }
        else
        {
#    if CARB_COMPILER_MSC
            unsigned long result;
            _BitScanForward(&result, (unsigned long)(Unsigned)val);
            return (int)result;
#    else
            return __builtin_ctz((unsigned int)(Unsigned)val);
#    endif
        }
    }
};

// Specialization for functions where sizeof(T) >= 2
template <class T>
class Helper<T, 2> : public Helper<T, 1>
{
public:
    using Base = Helper<T, 1>;
    using typename Base::Signed;
    using typename Base::Unsigned;
    static constexpr void propagateHighBit(T& n)
    {
        Base::propagateHighBit(n);
        n |= (n >> 8);
    }
};

// Specialization for functions where sizeof(T) >= 4
template <class T>
class Helper<T, 4> : public Helper<T, 2>
{
public:
    using Base = Helper<T, 2>;
    using typename Base::Signed;
    using typename Base::Unsigned;
    static constexpr void propagateHighBit(T& n)
    {
        Base::propagateHighBit(n);
        n |= (n >> 16);
    }

#    if CARB_LZCNT
#        if CARB_COMPILER_MSC
    static int countl_zero(T val)
    {
        static_assert(std::numeric_limits<T>::digits == 32, "Invalid assumption");
        return int(__lzcnt((unsigned int)(Unsigned)val));
    }
#        else
    static int countl_zero(T val)
    {
        static_assert(std::numeric_limits<T>::digits == 32, "Invalid assumption");
        return int(__builtin_ia32_lzcnt_u32((unsigned int)(Unsigned)val));
    }
#        endif
#    endif
};

// Specialization for functions where sizeof(T) >= 8
template <class T>
class Helper<T, 8> : public Helper<T, 4>
{
public:
    using Base = Helper<T, 4>;
    using typename Base::Signed;
    using typename Base::Unsigned;

    // popCount implementation for 8 byte integers
    static int popCount(const T& val)
    {
        static_assert(sizeof(T) == sizeof(uint64_t), "Unexpected size");
#    if CARB_COMPILER_MSC
#        if !CARB_POPCNT // Skip the check if we know we have the instruction
        // Only use the intrinsic if it's supported on the CPU
        static extras::CpuInfo cpuInfo;
        if (!cpuInfo.popcntSupported())
        {
            return popCountImpl((Unsigned)val);
        }
        else
#        endif
        {
#        if CARB_X86_64
            return (int)__popcnt64((Unsigned)val);
#        else
            return (int)_CountOneBits64((Unsigned)val);
#        endif
        }
#    else
        return __builtin_popcountll((Unsigned)val);
#    endif
    }
    static constexpr void propagateHighBit(T& n)
    {
        Base::propagateHighBit(n);
        n |= (n >> 32);
    }

    static int countl_zero(T val)
    {
#    if CARB_LZCNT
#        if CARB_COMPILER_MSC
        return int(__lzcnt64((Unsigned)val));
#        else
        return int(__builtin_ia32_lzcnt_u64((Unsigned)val));
#        endif
#    else
#        if CARB_COMPILER_MSC
        unsigned long index;
        static_assert(sizeof(val) == sizeof(unsigned __int64), "Invalid assumption");
        return _BitScanReverse64(&index, val) ? std::numeric_limits<T>::digits - 1 - index :
                                                std::numeric_limits<T>::digits;
#        else
        // According to docs, undefined if val == 0
        return val ? __builtin_clzll((Unsigned)val) : std::numeric_limits<T>::digits;
#        endif
#    endif
    }

    static int countr_zero(T val)
    {
        if (val == 0)
        {
            return std::numeric_limits<T>::digits;
        }
        else
        {
#    if CARB_COMPILER_MSC
            unsigned long result;
            _BitScanForward64(&result, (Unsigned)val);
            return (int)result;
#    else
            return __builtin_ctzll((Unsigned)val);
#    endif
        }
    }
};
#endif

/** @cond DEV */
template <class T>
using IsUnsignedIntegral = std::conjunction<std::is_unsigned<T>, std::is_integral<T>>;

template <class T>
std::enable_if_t<IsUnsignedIntegral<T>::value, unsigned> log2(const T in) noexcept
{
    CARB_ASSERT(in > 0, "Undefined");
#if CARB_COMPILER_MSC
    unsigned long out;
    _BitScanReverse64(&out, (uint64_t)in);
    return out;
#elif CARB_COMPILER_GNUC
    return 63 ^ __builtin_clzll(in);
#else
    CARB_UNSUPPORTED_COMPILER()
#endif
}

inline uint8_t reverse_byte(uint8_t in) noexcept
{
    // clang-format off
    constexpr static uint8_t reversed[] = {
        0x00, 0x80, 0x40, 0xC0, 0x20, 0xA0, 0x60, 0xE0, 0x10, 0x90, 0x50, 0xD0, 0x30, 0xB0, 0x70, 0xF0,
        0x08, 0x88, 0x48, 0xC8, 0x28, 0xA8, 0x68, 0xE8, 0x18, 0x98, 0x58, 0xD8, 0x38, 0xB8, 0x78, 0xF8,
        0x04, 0x84, 0x44, 0xC4, 0x24, 0xA4, 0x64, 0xE4, 0x14, 0x94, 0x54, 0xD4, 0x34, 0xB4, 0x74, 0xF4,
        0x0C, 0x8C, 0x4C, 0xCC, 0x2C, 0xAC, 0x6C, 0xEC, 0x1C, 0x9C, 0x5C, 0xDC, 0x3C, 0xBC, 0x7C, 0xFC,
        0x02, 0x82, 0x42, 0xC2, 0x22, 0xA2, 0x62, 0xE2, 0x12, 0x92, 0x52, 0xD2, 0x32, 0xB2, 0x72, 0xF2,
        0x0A, 0x8A, 0x4A, 0xCA, 0x2A, 0xAA, 0x6A, 0xEA, 0x1A, 0x9A, 0x5A, 0xDA, 0x3A, 0xBA, 0x7A, 0xFA,
        0x06, 0x86, 0x46, 0xC6, 0x26, 0xA6, 0x66, 0xE6, 0x16, 0x96, 0x56, 0xD6, 0x36, 0xB6, 0x76, 0xF6,
        0x0E, 0x8E, 0x4E, 0xCE, 0x2E, 0xAE, 0x6E, 0xEE, 0x1E, 0x9E, 0x5E, 0xDE, 0x3E, 0xBE, 0x7E, 0xFE,
        0x01, 0x81, 0x41, 0xC1, 0x21, 0xA1, 0x61, 0xE1, 0x11, 0x91, 0x51, 0xD1, 0x31, 0xB1, 0x71, 0xF1,
        0x09, 0x89, 0x49, 0xC9, 0x29, 0xA9, 0x69, 0xE9, 0x19, 0x99, 0x59, 0xD9, 0x39, 0xB9, 0x79, 0xF9,
        0x05, 0x85, 0x45, 0xC5, 0x25, 0xA5, 0x65, 0xE5, 0x15, 0x95, 0x55, 0xD5, 0x35, 0xB5, 0x75, 0xF5,
        0x0D, 0x8D, 0x4D, 0xCD, 0x2D, 0xAD, 0x6D, 0xED, 0x1D, 0x9D, 0x5D, 0xDD, 0x3D, 0xBD, 0x7D, 0xFD,
        0x03, 0x83, 0x43, 0xC3, 0x23, 0xA3, 0x63, 0xE3, 0x13, 0x93, 0x53, 0xD3, 0x33, 0xB3, 0x73, 0xF3,
        0x0B, 0x8B, 0x4B, 0xCB, 0x2B, 0xAB, 0x6B, 0xEB, 0x1B, 0x9B, 0x5B, 0xDB, 0x3B, 0xBB, 0x7B, 0xFB,
        0x07, 0x87, 0x47, 0xC7, 0x27, 0xA7, 0x67, 0xE7, 0x17, 0x97, 0x57, 0xD7, 0x37, 0xB7, 0x77, 0xF7,
        0x0F, 0x8F, 0x4F, 0xCF, 0x2F, 0xAF, 0x6F, 0xEF, 0x1F, 0x9F, 0x5F, 0xDF, 0x3F, 0xBF, 0x7F, 0xFF
    };
    // clang-format on
    return reversed[in];
}

template <class T>
std::enable_if_t<IsUnsignedIntegral<T>::value, T> reverse_bits(const T in) noexcept
{
    T out;
    auto pin = reinterpret_cast<const uint8_t*>(&in);
    auto pout = reinterpret_cast<uint8_t*>(&out);

    for (ptrdiff_t i = sizeof(T) - 1; i >= 0; --i)
        pout[i] = reverse_byte(pin[(sizeof(T) - 1) - i]);

    return out;
}

template <class T>
std::enable_if_t<IsUnsignedIntegral<T>::value, T> reverse_n_bits(const T in, std::size_t n) noexcept
{
    CARB_ASSERT(n != 0, "Undefined behavior");
    return reverse_bits(in) >> (std::numeric_limits<T>::digits - n);
}
/** @endcond */
} // namespace detail

#if defined(DOXYGEN_BUILD)
/**
 * Indicates the endianness of all scalar types for the current system.
 *
 * Endianness refers to byte ordering of scalar types larger than one byte. Take for example a 32-bit scalar with the
 * value "1".
 * On a little-endian system, the least-significant ("littlest") bytes are ordered first in memory. "1" would be
 * represented as:
 * @code{.txt}
 * 01 00 00 00
 * @endcode
 *
 * On a big-endian system, the most-significant ("biggest") bytes are ordered first in memory. "1" would be represented
 * as:
 * @code{.txt}
 * 00 00 00 01
 * @endcode
 */
enum class endian
{
    little = 0, //!< An implementation-defined value representing little-endian scalar types.
    big = 1, //!< An implementation-defined value representing big-endian scalar types.
    native = little //!< Will be either @ref endian::little or @ref endian::big depending on the target platform.
};
#elif defined(__cpp_lib_endian)
using endian = std::endian;
#else
enum class endian
{
#    if CARB_COMPILER_GNUC
    little = __ORDER_LITTLE_ENDIAN__,
    big = __ORDER_BIG_ENDIAN__,
    native = __BYTE_ORDER__
#    else
    little = 0,
    big = 1,
#        if CARB_X86_64 || CARB_AARCH64
    native = little
#        else
    CARB_UNSUPPORTED_PLATFORM();
#        endif
#    endif
};
#endif

#if CARB_COMPILER_MSC && _MSC_VER >= 1926
// VS 2019 16.6 has it https://github.com/microsoft/STL/issues/22#issuecomment-571378845
#    define CARBLOCAL_HAS_BUILTIN_BIT_CAST 1
#elif defined(__has_builtin) && !defined(NV_SONAR_BUILD)
#    if __has_builtin(__builtin_bit_cast) // most compilers don't like this combined with previous
#        define CARBLOCAL_HAS_BUILTIN_BIT_CAST 1
#    endif
#endif

#if !defined(DOXYGEN_BUILD) && defined(__cpp_lib_bit_cast)
using std::bit_cast;
#elif !defined(DOXYGEN_BUILD) && defined(CARBLOCAL_HAS_BUILTIN_BIT_CAST)
template <class To,
          class From,
          std::enable_if_t<std::conjunction<std::bool_constant<sizeof(To) == sizeof(From)>,
                                            std::is_trivially_copyable<To>,
                                            std::is_trivially_copyable<From>>::value,
                           bool> = false>
constexpr To bit_cast(const From& src) noexcept
{
    return __builtin_bit_cast(To, src);
}
#else
/**
 * Re-interprets the bits @p src as type `To`.
 *
 * @note The `To` and `From` types must exactly match size and both be trivially copyable.
 *
 * See: https://en.cppreference.com/w/cpp/numeric/bit_cast
 * @tparam To The object type to convert to.
 * @tparam From The (typically inferred) object type to convert from.
 * @param src The source object to reinterpret.
 * @returns The reinterpreted object.
 */
template <class To,
          class From CARB_NO_DOC(,
                                 std::enable_if_t<std::conjunction<std::bool_constant<sizeof(To) == sizeof(From)>,
                                                                   std::is_trivially_copyable<To>,
                                                                   std::is_trivially_copyable<From>>::value,
                                                  bool> = false)>
To bit_cast(const From& src) noexcept // requires compiler support to be constexpr
{
    // This union allows us to bypass `dest`'s constructor and just trivially copy into it.
    union
    {
        detail::NontrivialDummyType dummy;
        To dest;
    } u = {};
    std::memcpy(reinterpret_cast<void*>(&u.dest), &src, sizeof(From));
    return u.dest;
}
#endif
#undef CARBLOCAL_HAS_BUILTIN_BIT_CAST

#if defined(__cpp_lib_bitops) && !defined(DOXYGEN_BUILD)
// Use C++20 definitions
using std::bit_ceil;
using std::bit_floor;
using std::bit_width;
using std::countl_one;
using std::countl_zero;
using std::countr_one;
using std::countr_zero;
using std::has_single_bit;
using std::popcount;

// Wrapper implementations guaranteed to be constexpr
template <class T>
constexpr int popcount_constexpr(T val) noexcept
{
    return std::popcount(val);
}

template <class T>
constexpr int countl_zero_constexpr(T val) noexcept
{
    return std::countl_zero(val);
}

template <class T>
constexpr int countr_zero_constexpr(T val) noexcept
{
    return std::countr_zero(val);
}

template <class T>
constexpr int countl_one_constexpr(T val) noexcept
{
    return std::countl_one(val);
}

template <class T>
constexpr int countr_one_constexpr(T val) noexcept
{
    return std::countr_one(val);
}

template <class T>
constexpr auto bit_width_constexpr(T val) noexcept
{
    return std::bit_width(val);
}
#else
/**
 * Checks if a given value is an integral power of 2
 * @see https://en.cppreference.com/w/cpp/numeric/has_single_bit
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns \c true if \p val is not zero and has a single bit set (integral power of two); \c false otherwise.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
constexpr bool has_single_bit(T val) noexcept
{
    return val != T(0) && (val & (val - 1)) == T(0);
}

/**
 * Finds the smallest integral power of two not less than the given value.
 * @see https://en.cppreference.com/w/cpp/numeric/bit_ceil
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The smallest integral power of two that is not smaller than \p val. Undefined if the resulting value is not
 *  representable in \c T.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
constexpr T bit_ceil(T val) noexcept
{
    if (val <= 1)
        return T(1);

    // Yes, this could be implemented with a `nlz` instruction but cannot be constexpr without compiler support.
    --val;
    detail::Helper<T>::propagateHighBit(val);
    ++val;
    return val;
}

/**
 * Finds the largest integral power of two not greater than the given value.
 * @see https://en.cppreference.com/w/cpp/numeric/bit_floor
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The largest integral power of two not greater than \p val.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
constexpr T bit_floor(T val) noexcept
{
    // Yes, this could be implemented with a `nlz` instruction but cannot be constexpr without compiler support.
    detail::Helper<T>::propagateHighBit(val);
    return val - (val >> 1);
}

/**
 * Returns the number of 1 bits in the value of x.
 *
 * @note Unlike std::popcount, this function is not constexpr. This is because the compiler intrinsics used to
 * implement this function are not constexpr until C++20, so it was decided to drop constexpr in favor of being able to
 * use compiler intrinsics. If a constexpr implementation is required, use \ref popcount_constexpr().
 *
 * @note (Intel/AMD CPUs) This function will check to see if the CPU supports the `popcnt` instruction (Intel Nehalem
 * micro-architecture, 2008; AMD Jaguar micro-architecture, 2013), and if it is not supported, will use a fallback
 * function that is ~85% slower than the `popcnt` instruction. If the compiler indicates that the target CPU has that
 * instruction, the CPU support check can be skipped, saving about 20%. This is accomplished with command-line switches:
 * `/arch:AVX` (or higher) for Visual Studio or `-march=sandybridge` (or several other `-march` options) for GCC.
 *
 * @param[in] val The unsigned integer value to test.
 * @returns The number of 1 bits in the value of \p val.
 */
template <class T, std::enable_if_t<std::is_unsigned<T>::value, bool> = true>
int popcount(T val) noexcept
{
    return detail::Helper<T>::popCount(val);
}

/**
 * Returns the number of 1 bits in the value of x.
 *
 * @note Unlike \ref popcount(), this function is `constexpr` as it does not make use of intrinsics. Therefore, at
 * runtime it is recommended to use \ref popcount() instead of this function.
 *
 * @param[in] val The unsigned integer value to test.
 * @returns The number of 1 bits in the value of \p val.
 */
template <class T, std::enable_if_t<std::is_unsigned<T>::value, bool> = true>
constexpr int popcount_constexpr(T val) noexcept
{
    return detail::popCountImpl(val);
}

/**
 * Returns the number of consecutive 0 bits in the value of val, starting from the most significant bit ("left").
 * @see https://en.cppreference.com/w/cpp/numeric/countl_zero
 *
 * @note Unlike std::countl_zero, this function is not constexpr. This is because the compiler intrinsics used to
 * implement this function are not constexpr until C++20, so it was decided to drop constexpr in favor of being able to
 * use compiler intrinsics. If a constexpr implementation is required, use \ref countl_zero_constexpr().
 *
 * @note (Intel/AMD CPUs) To support backwards compatibility with older CPUs, by default this is implemented with a
 * `bsr` instruction (i386+), that is slightly less performant (~3%) than the more modern `lzcnt` instruction. This
 * function implementation will switch to using `lzcnt` if the compiler indicates that instruction is supported. On
 * Visual Studio this is provided by passing `/arch:AVX2` command-line switch, or on GCC with `-march=haswell` (or
 * several other
 * `-march` options). The `lzcnt` instruction was
 * <a href="https://en.wikipedia.org/wiki/X86_Bit_manipulation_instruction_set">introduced</a> on Intel's Haswell micro-
 * architecture and AMD's Jaguar and Piledriver micro-architectures.
 *
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The number of consecutive 0 bits in the provided value, starting from the most significant bit.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
int countl_zero(T val) noexcept
{
    return detail::Helper<T>::countl_zero(val);
}

/**
 * Returns the number of consecutive 0 bits in the value of val, starting from the most significant bit ("left").
 * @see https://en.cppreference.com/w/cpp/numeric/countl_zero
 *
 * @note Unlike \ref countl_zero(), this function is `constexpr` as it does not make use of intrinsics. Therefore, at
 * runtime it is recommended to use \ref countl_zero() instead of this function.
 *
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The number of consecutive 0 bits in the provided value, starting from the most significant bit.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
constexpr int countl_zero_constexpr(T val) noexcept
{
    if (val == 0)
        return std::numeric_limits<T>::digits;

    unsigned zeros = 0;
    for (T shift = std::numeric_limits<T>::digits >> 1; shift; shift >>= 1)
    {
        T temp = val >> shift;
        if (temp)
            val = temp;
        else
            zeros |= shift;
    }
    return int(zeros);
}

/**
 * Returns the number of consecutive 0 bits in the value of val, starting from the least significant bit ("right").
 * @see https://en.cppreference.com/w/cpp/numeric/countr_zero
 *
 * @note Unlike std::countr_zero, this function is not constexpr. This is because the compiler intrinsics used to
 * implement this function are not constexpr until C++20, so it was decided to drop constexpr in favor of being able to
 * use compiler intrinsics. If a constexpr implementation is required, use \ref countr_zero_constexpr().
 *
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The number of consecutive 0 bits in the provided value, starting from the least significant bit.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
int countr_zero(T val) noexcept
{
    return detail::Helper<T>::countr_zero(val);
}

#    pragma push_macro("max")
#    undef max

/**
 * Returns the number of consecutive 0 bits in the value of val, starting from the least significant bit ("right").
 * @see https://en.cppreference.com/w/cpp/numeric/countr_zero
 *
 * @note Unlike \ref countr_zero(), this function is `constexpr` as it does not make use of intrinsics. Therefore, at
 * runtime it is recommended to use \ref countr_zero() instead of this function.
 *
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The number of consecutive 0 bits in the provided value, starting from the least significant bit.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
constexpr int countr_zero_constexpr(T val) noexcept
{
    if (val == 0)
        return std::numeric_limits<T>::digits;
    if (val & 1)
        return 0;

    int zeros = 0;
    T shift = std::numeric_limits<T>::digits >> 1;
    T mask = std::numeric_limits<T>::max() >> shift;
    while (shift)
    {
        if (!(val & mask))
        {
            val >>= shift;
            zeros |= shift;
        }
        shift >>= 1;
        mask >>= shift;
    }
    return zeros;
}

#    pragma pop_macro("max")

/**
 * Returns the number of consecutive 1 bits in the value of val, starting from the most significant bit ("left").
 * @see https://en.cppreference.com/w/cpp/numeric/countl_one
 *
 * @note Unlike std::countl_one, this function is not constexpr. This is because the compiler intrinsics used to
 * implement this function are not constexpr until C++20, so it was decided to drop constexpr in favor of being able to
 * use compiler intrinsics. If a constexpr implementation is required, use \ref countl_one_constexpr().
 *
 * @note (Intel/AMD CPUs) To support backwards compatibility with older CPUs, by default this is implemented with a
 * `bsr` instruction (i386+), that is slightly less performant (~3%) than the more modern `lzcnt` instruction. This
 * function implementation will switch to using `lzcnt` if the compiler indicates that instruction is supported. On
 * Visual Studio this is provided by passing `/arch:AVX2` command-line switch, or on GCC with `-march=haswell` (or
 * several other
 * `-march` options). The `lzcnt` instruction was
 * <a href="https://en.wikipedia.org/wiki/X86_Bit_manipulation_instruction_set">introduced</a> on Intel's Haswell micro-
 * architecture and AMD's Jaguar and Piledriver micro-architectures.
 *
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The number of consecutive 1 bits in the provided value, starting from the most significant bit.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
int countl_one(T val) noexcept
{
    return detail::Helper<T>::countl_zero(T(~val));
}

/**
 * Returns the number of consecutive 1 bits in the value of val, starting from the most significant bit ("left").
 * @see https://en.cppreference.com/w/cpp/numeric/countl_zero
 *
 * @note Unlike \ref countl_one(), this function is `constexpr` as it does not make use of intrinsics. Therefore, at
 * runtime it is recommended to use \ref countl_one() instead of this function.
 *
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The number of consecutive 0 bits in the provided value, starting from the most significant bit.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
constexpr int countl_one_constexpr(T val) noexcept
{
    return countl_zero_constexpr(T(~val));
}

/**
 * Returns the number of consecutive 1 bits in the value of val, starting from the least significant bit ("right").
 * @see https://en.cppreference.com/w/cpp/numeric/countr_one
 *
 * @note Unlike std::countr_one, this function is not constexpr. This is because the compiler intrinsics used to
 * implement this function are not constexpr until C++20, so it was decided to drop constexpr in favor of being able to
 * use compiler intrinsics. If a constexpr implementation is required, use \ref countr_one_constexpr().
 *
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The number of consecutive 1 bits in the provided value, starting from the least significant bit.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
int countr_one(T val) noexcept
{
    return detail::Helper<T>::countr_zero(T(~val));
}

/**
 * Returns the number of consecutive 1 bits in the value of val, starting from the least significant bit ("right").
 * @see https://en.cppreference.com/w/cpp/numeric/countr_one
 *
 * @note Unlike \ref countr_one(), this function is `constexpr` as it does not make use of intrinsics. Therefore, at
 * runtime it is recommended to use \ref countr_one() instead of this function.
 *
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The number of consecutive 1 bits in the provided value, starting from the least significant bit.
 */
template <class T, std::enable_if_t<detail::IsUnsignedIntegral<T>::value, bool> = false>
constexpr int countr_one_constexpr(T val) noexcept
{
    return countr_zero_constexpr(T(~val));
}

/**
 * Returns the number of bits needed to store \p val, or 0, if \p val is 0
 *
 * Same as 1 + floor(log2(x)).
 *
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The number of bits needed to store \p val
 */
template <class T>
int bit_width(T val) noexcept
{
    return std::numeric_limits<T>::digits - countl_zero(val);
}

/**
 * Returns the number of bits needed to store \p val, or 0, if \p val is 0
 *
 * Same as 1 + floor(log2(x)).
 *
 * @note Unlike \ref bit_width(), this function is `constexpr` as it does not make use of intrinsics. Therefore, at
 * runtime it is recommended to use \ref bit_width() instead of this function.
 *
 * @tparam T An unsigned integral type
 * @param val An unsigned integral value
 * @returns The number of bits needed to store \p val
 */
template <class T>
constexpr int bit_width_constexpr(T val) noexcept
{
    return std::numeric_limits<T>::digits - countl_zero_constexpr(val);
}
#endif


} // namespace cpp
} // namespace carb

#undef CARB_LZCNT
#undef CARB_POPCNT
