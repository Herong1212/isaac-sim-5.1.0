// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Implementation of int128_t and uint128_t in carb::math namespace
#pragma once

#include "../cpp/Bit.h"
#include "../cpp/IOStream.h"
#include "../cpp/StringView.h"
#include "MulDiv.h"

#include <iostream>
#include <string> // for std::string and std::hash

#ifdef DOXYGEN_BUILD
//! Pretend we have builtin for documentation builds
#    define CARBLOCAL_USE_BUILTIN_INT128 1
#elif CARB_TOOLCHAIN_CLANG
// Although Clang has built-in uint128 support, on Windows it generates a call to `__udivti3`, which it does not
// provide. See: https://github.com/llvm/llvm-project/issues/25679
// For this reason we use our own uint128_t implementation for Clang on Windows.
#    define CARBLOCAL_USE_BUILTIN_INT128 !CARB_PLATFORM_WINDOWS
#elif CARB_COMPILER_MSC
// No builtin to use
#    define CARBLOCAL_USE_BUILTIN_INT128 0
// MS intrinsics
extern "C"
{
    unsigned char _BitScanReverse64(unsigned long* _Index, uint64_t _Mask);
#    pragma intrinsic(_BitScanReverse64)
#    if CARB_X86_64
    unsigned char _subborrow_u64(unsigned char, unsigned __int64, unsigned __int64, unsigned __int64*);
#        pragma intrinsic(_subborrow_u64)
#    endif
}
#elif CARB_COMPILER_GNUC
#    define CARBLOCAL_USE_BUILTIN_INT128 1
#else
CARB_UNSUPPORTED_COMPILER();
#endif

namespace carb
{
namespace math
{
#if !CARBLOCAL_USE_BUILTIN_INT128
//! \cond DEV
namespace detail
{

inline bool bsr(unsigned& index, uint64_t val) noexcept
{
#    if CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG
    if (val)
    {
        index = 64u - 1u - unsigned(__builtin_clzll(val));
        return true;
    }
    return false;
#    elif CARB_COMPILER_MSC
    unsigned long ulIndex;
    bool ret = _BitScanReverse64(&ulIndex, val);
    index = unsigned(ulIndex);
    return ret;
#    else
    CARB_UNSUPPORTED_COMPILER();
#    endif
}

inline uint8_t sbb(uint8_t cf, uint64_t minuend, uint64_t subtrahend, uint64_t& difference) noexcept
{
#    if CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG
    auto c1 = __builtin_sub_overflow(minuend, subtrahend, &difference);
    auto c2 = __builtin_sub_overflow(difference, cf, &difference);
    return uint8_t(c1 | c2);
#    elif CARB_COMPILER_MSC
#        if CARB_X86_64
    return _subborrow_u64(cf, minuend, subtrahend, &difference);
#        elif CARB_AARCH64
    // Don't have any intrinsics that support carry flag here, so do manual carry check
    auto temp = minuend - subtrahend;
    auto c1 = minuend < temp;
    difference = temp - cf;
    c1 |= (temp < difference);
    return uint8_t(c1);
#        else
    CARB_UNSUPPORTED_ARCHITECTURE();
#        endif
#    else
    CARB_UNSUPPORTED_COMPILER();
#    endif
}

class int128base
{
public:
    explicit operator bool() const noexcept
    {
        return (m_low | m_high) != 0;
    }

    //! Copy constructor.
    constexpr int128base(const int128base&) = default;

    //! Copy-assign operator.
    int128base& operator=(const int128base&) = default;

protected:
    constexpr int128base() noexcept : m_low(0), m_high(0)
    {
    }

    constexpr int128base(uint64_t high, uint64_t low) noexcept : m_low(low), m_high(high)
    {
    }

    // Algorithm derived from assembly at https://skanthak.hier-im-netz.de/integer.html
    static int128base udivmodti4(int128base dividend, int128base divisor, int128base* remainder) noexcept
    {
        auto&& less = [](const int128base& lhs, const int128base& rhs) noexcept {
            if (lhs.m_high < rhs.m_high)
                return true;
            if (rhs.m_high < lhs.m_high)
                return false;
            return lhs.m_low < rhs.m_low;
        };
        if (less(dividend, divisor)) // dividend < divisor?
        {
            // trivial
            if (remainder)
                *remainder = dividend;
            return {};
        }

        unsigned index;
        int128base quotient;
        if (!bsr(index, divisor.m_high)) // high qword of divisor == 0?
        {
            if (dividend.m_high < divisor.m_low)
            {
                // Normal division
                // dividend < divisor * 2**64; quotient < 2**64
                quotient = int128base(0, udiv128(dividend.m_high, dividend.m_low, divisor.m_low,
                                                 remainder ? (remainder->m_high = 0, &remainder->m_low) : nullptr));
            }
            else
            {
                // Long division
                uint64_t rem;
                quotient.m_high = udiv128(0, dividend.m_high, divisor.m_low, &rem);
                quotient.m_low = udiv128(rem, dividend.m_low, divisor.m_low,
                                         remainder ? (remainder->m_high = 0, &remainder->m_low) : nullptr);
            }
        }
        else
        {
            // Extended division
            index ^= 0x3F; // index = number of leading '0' bits in (high qword of) divisor
            if (!index) // divisor >= 2**127?
            {
                // special case: dividend >= divisor >= 2**127
                // quotient: 1, remainder: dividend - divisor
                quotient = int128base(0, 1);
                if (remainder)
                {
                    auto borrow = sbb(0, dividend.m_low, divisor.m_low, remainder->m_low);
                    sbb(borrow, dividend.m_high, divisor.m_high, remainder->m_high);
                }
                return quotient;
            }

            quotient.m_high = quotient.m_low = 0;
            // shift the divisor by the number of leading '0' bits
            uint64_t divisorH = (divisor.m_high << index) | (divisor.m_low >> (64 - index));
            int128base temp;
            temp.m_high = dividend.m_high;
            if (temp.m_high >= divisorH)
            {
                // high qword of dividend >= divisor'
                // subtract divisorH from temp.high to prevent possible quotient overflow and set most significant bit
                // of quotient"
                temp.m_high -= divisorH;
                quotient.m_low = 1;
            }
            // temp.low = temp.high:dividend.m_low / divisorH
            // temp.high = temp.high:dividend.m_low % divisorH
            temp.m_low = udiv128(temp.m_high, dividend.m_low, divisorH, &temp.m_high);
            // Shift quotient by number of leading zeros in divisor and mix in bits from temp.low
            quotient.m_low = (quotient.m_low << index) | (temp.m_low >> (64 - index));

            divisorH = uint64_t(int64_t(divisor.m_high) * int64_t(quotient.m_low));
            // temp = divisor.m_low * quot
            temp.m_low = umul128(divisor.m_low, quotient.m_low, temp.m_high);
            // temp.high += divisorH
            if (adc(0, temp.m_high, divisorH, temp.m_high)) // had carry?
            {
                --quotient.m_low;
                // temp.low -= divisor.m_low; temp.high -= divisor.m_low; former borrows from latter
                auto borrow = sbb(0, temp.m_low, divisor.m_low, temp.m_low);
                sbb(borrow, temp.m_high, divisor.m_low, temp.m_high);
            }

            // Fix up quotient and calculate remainder
            int128base rem;

            // rem = dividend.m_high:dividend.m_low - temp
            auto borrow = sbb(0, dividend.m_low, temp.m_low, rem.m_low);
            borrow = sbb(borrow, dividend.m_high, temp.m_high, rem.m_high);
            if (borrow)
            {
                // remainder is off by divisor and quot is off by 1
                --quotient.m_low;
                auto carry = adc(0, rem.m_low, divisor.m_low, rem.m_low);
                adc(carry, rem.m_high, divisor.m_high, rem.m_high);
            }

            // Remainder
            if (remainder)
                *remainder = rem;
        }
        return quotient;
    }

    static int128base divmodti4(int128base dividend, int128base divisor, int128base* remainder) noexcept
    {
        int64_t const dvd_neg = dividend.m_ihigh >> 63;

        // dividend = abs(dividend)
        dividend.m_ihigh ^= dvd_neg;
        dividend.m_ilow ^= dvd_neg;
        auto borrow = sbb(0, dividend.m_low, uint64_t(dvd_neg), dividend.m_low);
        sbb(borrow, dividend.m_high, uint64_t(dvd_neg), dividend.m_high);

        int64_t const dvr_neg = divisor.m_ihigh >> 63;

        // divisor = abs(divisor)
        divisor.m_ihigh ^= dvr_neg;
        divisor.m_ilow ^= dvr_neg;
        borrow = sbb(0, divisor.m_low, uint64_t(dvr_neg), divisor.m_low);
        sbb(borrow, divisor.m_high, uint64_t(dvr_neg), divisor.m_high);

        int128base quotient = udivmodti4(dividend, divisor, remainder);

        // Fix up quotient negation (negate if dvd_neg ^ dvr_neg)
        int64_t const quot_neg = dvd_neg ^ dvr_neg;
        quotient.m_ihigh ^= quot_neg;
        quotient.m_ilow ^= quot_neg;
        borrow = sbb(0, quotient.m_low, uint64_t(quot_neg), quotient.m_low);
        sbb(borrow, quotient.m_high, uint64_t(quot_neg), quotient.m_high);

        // Fix up remainder negation (negate if dvd_neg < 0)
        if (dvd_neg && remainder)
        {
            remainder->m_ihigh = -remainder->m_ihigh;
            borrow = !!remainder->m_ilow;
            remainder->m_ilow = -remainder->m_ilow;
            sbb(borrow, remainder->m_high, 0, remainder->m_high);
        }
        return quotient;
    }

    static int128base udivti3(int128base dividend, int128base divisor) noexcept
    {
        return udivmodti4(dividend, divisor, nullptr);
    }

    static int128base umodti3(int128base dividend, int128base divisor) noexcept
    {
        int128base remainder;
        udivmodti4(dividend, divisor, &remainder);
        return remainder;
    }

    static int128base divti3(int128base dividend, int128base divisor) noexcept
    {
        int64_t const dvd_neg = dividend.m_ihigh >> 63; // dividend < 0 ? -1 : 0

        // dividend = abs(dividend)
        dividend.m_ihigh ^= dvd_neg;
        dividend.m_ilow ^= dvd_neg;
        auto borrow = sbb(0, dividend.m_low, uint64_t(dvd_neg), dividend.m_low);
        sbb(borrow, dividend.m_high, uint64_t(dvd_neg), dividend.m_high);

        int64_t const dvr_neg = divisor.m_ihigh >> 63; // divisor < 0 ? -1 : 0

        // divisor = abs(divisor)
        divisor.m_ihigh ^= dvr_neg;
        divisor.m_ilow ^= dvr_neg;
        borrow = sbb(0, divisor.m_low, uint64_t(dvr_neg), divisor.m_low);
        sbb(borrow, divisor.m_high, uint64_t(dvr_neg), divisor.m_high);

        int128base quotient = udivmodti4(dividend, divisor, nullptr);

        // Fix up negation (negate if dvd_neg ^ dvr_neg)
        int64_t const quot_neg = dvd_neg ^ dvr_neg;
        quotient.m_ihigh ^= quot_neg;
        quotient.m_ilow ^= quot_neg;
        borrow = sbb(0, quotient.m_low, uint64_t(quot_neg), quotient.m_low);
        sbb(borrow, quotient.m_high, uint64_t(quot_neg), quotient.m_high);

        return quotient;
    }

    static int128base modti3(int128base dividend, int128base divisor) noexcept
    {
        int64_t const dvr_neg = divisor.m_ihigh >> 63; // divisor < 0 ? -1 : 0

        // divisor = abs(divisor)
        divisor.m_ihigh ^= dvr_neg;
        divisor.m_ilow ^= dvr_neg;
        auto borrow = sbb(0, divisor.m_low, uint64_t(dvr_neg), divisor.m_low);
        sbb(borrow, divisor.m_high, uint64_t(dvr_neg), divisor.m_high);

        int64_t const dvd_neg = dividend.m_ihigh >> 63; // dividend < 0 ? -1 : 0

        // dividend = abs(dividend)
        dividend.m_ihigh ^= dvd_neg;
        dividend.m_ilow ^= dvd_neg;
        borrow = sbb(0, dividend.m_low, uint64_t(dvd_neg), dividend.m_low);
        sbb(borrow, dividend.m_high, uint64_t(dvd_neg), dividend.m_high);

        int128base remainder;
        udivmodti4(dividend, divisor, &remainder);

        // Fix up negation (negate if dividend is negative)
        remainder.m_ihigh ^= dvd_neg;
        remainder.m_ilow ^= dvd_neg;
        borrow = sbb(0, remainder.m_low, uint64_t(dvd_neg), remainder.m_low);
        sbb(borrow, remainder.m_high, uint64_t(dvd_neg), remainder.m_high);

        return remainder;
    }

    CARB_IGNOREWARNING_MSC_WITH_PUSH(4201) // nonstandard extension used: nameless struct/union
    union
    {
        struct
        {
            uint64_t m_low;
            uint64_t m_high;
        };
        struct
        {
            int64_t m_ilow;
            int64_t m_ihigh;
        };
        static_assert(cpp::endian::native == cpp::endian::little, "Assumes little endian");
    };
    CARB_IGNOREWARNING_MSC_POP
};

} // namespace detail
//! \endcond

// macros for boilerplate
#    define CARBLOCAL_BINARY_MATH_OP(type, op)                                                                         \
        template <class T, std::enable_if_t<std::is_integral<T>::value, bool> = false>                                 \
        type& operator op##=(T rhs) noexcept                                                                           \
        {                                                                                                              \
            *this op## = type(rhs);                                                                                    \
            return *this;                                                                                              \
        }                                                                                                              \
        friend type operator op(type lhs, const type& rhs) noexcept                                                    \
        {                                                                                                              \
            lhs op## = rhs;                                                                                            \
            return lhs;                                                                                                \
        }                                                                                                              \
        template <class T, std::enable_if_t<std::is_integral<T>::value, bool> = false>                                 \
        friend type operator op(type lhs, T rhs) noexcept                                                              \
        {                                                                                                              \
            lhs op## = type(rhs);                                                                                      \
            return lhs;                                                                                                \
        }                                                                                                              \
        template <class T, std::enable_if_t<std::is_integral<T>::value, bool> = false>                                 \
        friend type operator op(T lhs, const type& rhs) noexcept                                                       \
        {                                                                                                              \
            type temp(lhs);                                                                                            \
            temp op## = rhs;                                                                                           \
            return temp;                                                                                               \
        }

#    define CARBLOCAL_OP_PROMOTE(type, op)                                                                             \
        template <class T, std::enable_if_t<std::is_integral<T>::value, bool> = false>                                 \
        friend bool operator op(const type& lhs, T rhs) noexcept                                                       \
        {                                                                                                              \
            return lhs op type(rhs);                                                                                   \
        }                                                                                                              \
        template <class T, std::enable_if_t<std::is_integral<T>::value, bool> = false>                                 \
        friend bool operator op(T lhs, const type& rhs) noexcept                                                       \
        {                                                                                                              \
            return type(lhs) op rhs;                                                                                   \
        }

#    define CARBLOCAL_OP_DERIVE(type, op, ...)                                                                         \
        friend bool operator op(const type& lhs, const type& rhs) noexcept                                             \
        {                                                                                                              \
            return __VA_ARGS__;                                                                                        \
        }                                                                                                              \
        CARBLOCAL_OP_PROMOTE(type, op)

class uint128_t;

class int128_t : public detail::int128base
{
    using base = detail::int128base;

public:
    constexpr int128_t() noexcept = default;

    template <class T, std::enable_if_t<std::conjunction<std::is_integral<T>, std::is_signed<T>>::value, bool> = true>
    constexpr explicit int128_t(T lower) noexcept : base(lower < 0 ? uint64_t(-1) : uint64_t(0), uint64_t(lower))
    {
    }

    template <class T, std::enable_if_t<std::conjunction<std::is_integral<T>, std::is_unsigned<T>>::value, bool> = true>
    constexpr explicit int128_t(T lower) noexcept : base(0, uint64_t(lower))
    {
    }

    constexpr explicit int128_t(const uint128_t& other) noexcept;

    constexpr int128_t(const int128_t&) = default;
    int128_t& operator=(const int128_t&) = default;

    friend int128_t make_int128_t(uint64_t high, uint64_t low) noexcept;

    friend int128_t divide_and_modulus(const int128_t& dividend, const int128_t& divisor, int128_t& modulus);

    friend int64_t cast_to_int64_t(const int128_t& val) noexcept;

    int128_t& operator++() noexcept
    {
        if (++m_low == 0)
            ++m_high;
        return *this;
    }
    int128_t operator++(int) noexcept
    {
        int128_t prev = *this;
        this->operator++();
        return prev;
    }
    int128_t& operator--() noexcept
    {
        if (m_low-- == 0)
            --m_high;
        return *this;
    }
    int128_t operator--(int) noexcept
    {
        int128_t prev = *this;
        this->operator--();
        return prev;
    }

    int128_t& operator+=(const int128_t& other) noexcept
    {
        auto carry = detail::adc(0, m_low, other.m_low, m_low);
        detail::adc(carry, m_high, other.m_high, m_high);
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(int128_t, +)

    int128_t& operator-=(const int128_t& other) noexcept
    {
        auto borrow = detail::sbb(0, m_low, other.m_low, m_low);
        detail::sbb(borrow, m_high, other.m_high, m_high);
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(int128_t, -)

    int128_t& operator*=(int128_t other) noexcept
    {
        // 128-bit multiply is:
        //    otherH otherL
        // X   thisH  thisL
        // ---------------------
        //    thisL*otherH thisL*otherL
        // +  thisH*otherL         0
        m_ihigh *= other.m_ilow;
        other.m_ihigh *= m_ilow;
        m_low = detail::umul128(m_low, other.m_low, other.m_low);
        m_ihigh += other.m_ihigh;
        m_ihigh += other.m_ilow;
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(int128_t, *)

    int128_t& operator/=(const int128_t& other) noexcept
    {
        base::operator=(divti3(*this, other));
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(int128_t, /)

    int128_t& operator%=(const int128_t& other) noexcept
    {
        base::operator=(modti3(*this, other));
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(int128_t, %)

    int128_t& operator&=(const int128_t& other) noexcept
    {
        m_low &= other.m_ilow;
        m_high &= other.m_ihigh;
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(int128_t, &)

    int128_t& operator|=(const int128_t& other) noexcept
    {
        m_low |= other.m_ilow;
        m_high |= other.m_ihigh;
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(int128_t, |)

    int128_t& operator^=(const int128_t& other) noexcept
    {
        m_low ^= other.m_ilow;
        m_high ^= other.m_ihigh;
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(int128_t, ^)

    friend int128_t operator+(const int128_t& val) noexcept
    {
        return val;
    }

    friend int128_t operator-(const int128_t& val) noexcept
    {
        int128_t ret = ~val;
        ++ret;
        return ret;
    }

    friend int128_t operator~(const int128_t& val) noexcept
    {
        return int128_t(~val.m_high, ~val.m_low);
    }

    friend bool operator<(const int128_t& lhs, const int128_t& rhs) noexcept
    {
        // The asm for this should be simple, but requires access to the overflow flag (Linux x86-64 example):
        //   cmp rdi, qword ptr [rdx]   ; effectively (rdi - *rdx) to set flags and ignore the result.
        //   sbb rsi, qword ptr [rdx+8] ; subtract with borrow, sets OF and SF among others
        //   setl al                    ; "set less": sets al to 1 if OF != SF
        //   ret

        auto const diff = lhs - rhs;

        // Since we don't have access to the ALU flags, we emulate them ourself:
        // From https://teaching.idallen.com/dat2343/11w/notes/040_overflow.txt
        // Signed less-than is true if OverflowFlag != SignFlag
        // OverflowFlag is true if (sign(lhs.high) ^ sign(rhs.high)) && (sign(lhs.high) ^ sign(diff.high))
        //    that is, if sign of lhs and rhs differ and the sign of the difference doesn't match lhs
        // Truth table (signs of [l]hs, [r]hs, [d]iff shown as 0 if positive, 1 if negative; SF is [d]iff)
        //   l  -  r  =  d/SF | (l^r) (l^d)   OF   d/SF = Less
        //  ------------------+-------------------------------
        //   0  -  0  =   0   |   0  &  0  =  0  ^  0   =  0
        //   0  -  0  =   1   |   0  &  1  =  0  ^  1   =  1
        //   0  -  1  =   0   |   1  &  0  =  0  ^  0   =  0
        //   0  -  1  =   1   |   1  &  1  =  1  ^  1   =  0
        //   1  -  0  =   0   |   1  &  1  =  1  ^  0   =  1
        //   1  -  0  =   1   |   1  &  0  =  0  ^  1   =  1
        //   1  -  1  =   0   |   0  &  1  =  0  ^  0   =  0
        //   1  -  1  =   1   |   0  &  0  =  0  ^  1   =  1
        int64_t const kOverflowFlag = ((lhs.m_ihigh ^ rhs.m_ihigh) & (lhs.m_ihigh ^ diff.m_ihigh)) >> 63; // sign extend
        int64_t const kSignFlag = diff.m_ihigh >> 63; // sign extend
        return !!(kOverflowFlag ^ kSignFlag);
    }
    CARBLOCAL_OP_PROMOTE(int128_t, <)

    friend bool operator==(const int128_t& lhs, const int128_t& rhs) noexcept
    {
        return lhs.m_ilow == rhs.m_ilow && lhs.m_ihigh == rhs.m_ihigh;
    }
    CARBLOCAL_OP_PROMOTE(int128_t, ==)

    CARBLOCAL_OP_DERIVE(int128_t, !=, !(rhs == lhs))
    CARBLOCAL_OP_DERIVE(int128_t, >, (rhs < lhs))
    CARBLOCAL_OP_DERIVE(int128_t, <=, !(rhs < lhs))
    CARBLOCAL_OP_DERIVE(int128_t, >=, !(lhs < rhs))

    int128_t& operator<<=(unsigned shift) noexcept
    {
        shift &= 127; // Intel-ism
        if (shift >= 64)
        {
            m_high = m_low << (shift - 64);
            m_low = 0;
        }
        else if (shift != 0)
        {
            m_high = (m_high << shift) | (m_low >> (64 - shift));
            m_low <<= shift;
        }
        return *this;
    }
    friend int128_t operator<<(int128_t lhs, unsigned shift) noexcept
    {
        lhs <<= shift;
        return lhs;
    }
    int128_t& operator>>=(unsigned shift) noexcept
    {
        shift &= 127; // Intel-ism
        if (shift >= 64)
        {
            m_ilow = m_ihigh >> (shift - 64);
            m_ihigh >>= 63; // sign extend
        }
        else if (shift != 0)
        {
            m_low = (m_low >> shift) | (m_high << (64 - shift));
            m_ihigh >>= shift;
        }
        return *this;
    }
    friend int128_t operator>>(int128_t lhs, unsigned shift) noexcept
    {
        lhs >>= shift;
        return lhs;
    }

    friend std::ostream& operator<<(std::ostream& os, const int128_t& val);

    friend std::string to_string(const int128_t& val);

private:
    constexpr int128_t(base b) noexcept : base(b)
    {
    }
    constexpr int128_t(uint64_t high, uint64_t low) noexcept : base(high, low)
    {
    }
};

class uint128_t : public detail::int128base
{
    using base = detail::int128base;

public:
    constexpr uint128_t() noexcept = default;

    template <class T, std::enable_if_t<std::conjunction<std::is_integral<T>, std::is_signed<T>>::value, bool> = true>
    constexpr explicit uint128_t(T lower) noexcept : base(lower < 0 ? uint64_t(-1) : uint64_t(0), uint64_t(lower))
    {
    }

    template <class T, std::enable_if_t<std::conjunction<std::is_integral<T>, std::is_unsigned<T>>::value, bool> = true>
    constexpr explicit uint128_t(T lower) noexcept : base(0, uint64_t(lower))
    {
    }

    constexpr explicit uint128_t(const int128_t& other) noexcept;

    constexpr uint128_t(const uint128_t&) = default;
    uint128_t& operator=(const uint128_t&) = default;

    friend constexpr uint128_t make_uint128_t(uint64_t high, uint64_t low) noexcept;

    friend uint128_t divide_and_modulus(const uint128_t& dividend, const uint128_t& divisor, uint128_t& modulus);

    friend uint64_t cast_to_uint64_t(const uint128_t& val) noexcept;

    uint128_t& operator++() noexcept
    {
        if (++m_low == 0)
            ++m_high;
        return *this;
    }
    uint128_t operator++(int) noexcept
    {
        uint128_t prev = *this;
        this->operator++();
        return prev;
    }
    uint128_t& operator--() noexcept
    {
        if (m_low-- == 0)
            --m_high;
        return *this;
    }
    uint128_t operator--(int) noexcept
    {
        uint128_t prev = *this;
        this->operator--();
        return prev;
    }

    uint128_t& operator+=(const uint128_t& other) noexcept
    {
        auto carry = detail::adc(0, m_low, other.m_low, m_low);
        detail::adc(carry, m_high, other.m_high, m_high);
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(uint128_t, +)

    uint128_t& operator-=(const uint128_t& other) noexcept
    {
        auto borrow = detail::sbb(0, m_low, other.m_low, m_low);
        detail::sbb(borrow, m_high, other.m_high, m_high);
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(uint128_t, -)

    uint128_t& operator*=(uint128_t other) noexcept
    {
        // 128-bit multiply is:
        //    otherH otherL
        // X   thisH  thisL
        // ---------------------
        //    thisL*otherH thisL*otherL
        // +  thisH*otherL         0
        m_high *= other.m_low;
        other.m_high *= m_low;
        m_low = detail::umul128(m_low, other.m_low, other.m_low);
        m_high += other.m_high;
        m_high += other.m_low;
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(uint128_t, *)

    uint128_t& operator/=(const uint128_t& other) noexcept
    {
        base::operator=(udivti3(*this, other));
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(uint128_t, /)

    uint128_t& operator%=(const uint128_t& other) noexcept
    {
        base::operator=(umodti3(*this, other));
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(uint128_t, %)

    uint128_t& operator&=(const uint128_t& other) noexcept
    {
        m_low &= other.m_low;
        m_high &= other.m_high;
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(uint128_t, &)

    uint128_t& operator|=(const uint128_t& other) noexcept
    {
        m_low |= other.m_low;
        m_high |= other.m_high;
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(uint128_t, |)

    uint128_t& operator^=(const uint128_t& other) noexcept
    {
        m_low ^= other.m_low;
        m_high ^= other.m_high;
        return *this;
    }
    CARBLOCAL_BINARY_MATH_OP(uint128_t, ^)

    friend uint128_t operator+(const uint128_t& val) noexcept
    {
        return val;
    }

    friend uint128_t operator~(const uint128_t& val) noexcept
    {
        return uint128_t(~val.m_high, ~val.m_low);
    }

    friend bool operator<(const uint128_t& lhs, const uint128_t& rhs) noexcept
    {
        if (lhs.m_high < rhs.m_high)
            return true;
        if (rhs.m_high < lhs.m_high)
            return false;
        return lhs.m_low < rhs.m_low;
    }
    CARBLOCAL_OP_PROMOTE(uint128_t, <)

    friend bool operator==(const uint128_t& lhs, const uint128_t& rhs) noexcept
    {
        return lhs.m_low == rhs.m_low && lhs.m_high == rhs.m_high;
    }
    CARBLOCAL_OP_PROMOTE(uint128_t, ==)

    CARBLOCAL_OP_DERIVE(uint128_t, !=, !(rhs == lhs))
    CARBLOCAL_OP_DERIVE(uint128_t, >, (rhs < lhs))
    CARBLOCAL_OP_DERIVE(uint128_t, <=, !(rhs < lhs))
    CARBLOCAL_OP_DERIVE(uint128_t, >=, !(lhs < rhs))

    uint128_t& operator<<=(unsigned shift) noexcept
    {
        shift &= 127; // Intel-ism
        if (shift >= 64)
        {
            m_high = m_low << (shift - 64);
            m_low = 0;
        }
        else if (shift != 0)
        {
            m_high = (m_high << shift) | (m_low >> (64 - shift));
            m_low <<= shift;
        }
        return *this;
    }
    friend uint128_t operator<<(uint128_t lhs, unsigned shift) noexcept
    {
        lhs <<= shift;
        return lhs;
    }
    uint128_t& operator>>=(unsigned shift) noexcept
    {
        shift &= 127; // Intel-ism
        if (shift >= 64)
        {
            m_low = m_high >> (shift - 64);
            m_high = 0;
        }
        else if (shift != 0)
        {
            m_low = (m_low >> shift) | (m_high << (64 - shift));
            m_high >>= shift;
        }
        return *this;
    }
    friend uint128_t operator>>(uint128_t lhs, unsigned shift) noexcept
    {
        lhs >>= shift;
        return lhs;
    }

    friend std::ostream& operator<<(std::ostream& os, const uint128_t& val);

    friend std::string to_string(const uint128_t& val);

private:
    constexpr uint128_t(base b) : base(b)
    {
    }
    constexpr uint128_t(uint64_t high, uint64_t low) noexcept : base(high, low)
    {
    }
};

inline constexpr int128_t::int128_t(const uint128_t& other) noexcept : base(other)
{
}

inline constexpr uint128_t::uint128_t(const int128_t& other) noexcept : base(other)
{
}

inline int128_t make_int128_t(uint64_t high, uint64_t low) noexcept
{
    return int128_t(high, low);
}

inline int64_t cast_to_int64_t(const int128_t& val) noexcept
{
    return int64_t(val.m_low);
}

inline int128_t divide_and_modulus(const int128_t& dividend, const int128_t& divisor, int128_t& modulus)
{
    return int128_t(int128_t::divmodti4(dividend, divisor, &modulus));
}

inline constexpr uint128_t make_uint128_t(uint64_t high, uint64_t low) noexcept
{
    return uint128_t(high, low);
}

inline uint64_t cast_to_uint64_t(const uint128_t& val) noexcept
{
    return val.m_low;
}

inline uint128_t divide_and_modulus(const uint128_t& dividend, const uint128_t& divisor, uint128_t& modulus)
{
    return uint128_t(uint128_t::udivmodti4(dividend, divisor, &modulus));
}

#    undef CARBLOCAL_BINARY_MATH_OP
#    undef CARBLOCAL_OP_PROMOTE
#    undef CARBLOCAL_OP_DERIVE
#else /* CARBLOCAL_USE_BUILTIN_INT128 */
//! The 128-bit signed integer type.
using int128_t = __int128;
//! The 128-bit unsigned integer type.
using uint128_t = unsigned __int128;

/**
 * Creates a signed 128-bit integer from two unsigned 64-bit integers.
 * @param high The high 64 bits.
 * @param low The low 64 bits.
 * @returns A signed 128-bit integer value as if by `(int128_t(high) << 64) + low`.
 */
inline int128_t make_int128_t(uint64_t high, uint64_t low) noexcept
{
    return (int128_t(high) << 64) + low;
}

/**
 * Performs a division operation with two signed 128-bit integers and provides both the quotient and remainder.
 *
 * Effectively:
 * ```cpp
 * quotient = dividend / divisor;
 * modulus = dividend % divisor;
 * ```
 * @param dividend The 128-bit signed dividend.
 * @param divisor The 128-bit signed divisor.
 * @param modulus Receives the 128-bit signed remainder.
 * @returns The 128-bit signed quotient.
 */
inline int128_t divide_and_modulus(const int128_t& dividend, const int128_t& divisor, int128_t& modulus) noexcept
{
    modulus = dividend % divisor;
    return dividend / divisor;
}

/**
 * Truncates the signed 128-bit value, returning only the lowest 64-bits.
 * @param val The signed 128-bit value to truncate.
 * @returns The least significant 64 bits of @p val.
 */
inline int64_t cast_to_int64_t(const int128_t& val) noexcept
{
    return int64_t(val);
}

/**
 * Creates an unsigned 128-bit integer from two unsigned 64-bit integers.
 * @param high The high 64 bits.
 * @param low The low 64 bits.
 * @returns An unsigned 128-bit integer value as if by `(uint128_t(high) << 64) + low`.
 */
inline constexpr uint128_t make_uint128_t(uint64_t high, uint64_t low) noexcept
{
    return (uint128_t(high) << 64) + low;
}

/**
 * Performs a division operation on two unsigned 128-bit integers and provides both the quotient and remainder.
 *
 * Effectively:
 * ```cpp
 * quotient = dividend / divisor;
 * modulus = dividend % divisor;
 * ```
 * @param dividend The 128-bit unsigned dividend.
 * @param divisor The 128-bit unsigned divisor.
 * @param modulus Receives the 128-bit unsigned remainder.
 * @returns The 128-bit unsigned quotient.
 */
inline uint128_t divide_and_modulus(const uint128_t& dividend, const uint128_t& divisor, uint128_t& modulus) noexcept
{
    modulus = dividend % divisor;
    return dividend / divisor;
}

/**
 * Truncates the unsigned 128-bit value, returning only the lowest 64-bits.
 * @param val The signed 128-bit value to truncate.
 * @returns The least significant 64 bits of @p val.
 */
inline uint64_t cast_to_uint64_t(const uint128_t& val) noexcept
{
    return uint64_t(val);
}

#endif /* CARBLOCAL_USE_BUILTIN_INT128 */

//! \cond DEV
namespace detail
{

struct formatter128
{
public:
    formatter128() noexcept = default;

    cpp::string_view format(uint128_t val) noexcept
    {
        using digit_pair = char[2];
        constexpr static digit_pair kDigits[] = {
            { '0', '0' }, { '0', '1' }, { '0', '2' }, { '0', '3' }, { '0', '4' }, { '0', '5' }, { '0', '6' },
            { '0', '7' }, { '0', '8' }, { '0', '9' }, { '1', '0' }, { '1', '1' }, { '1', '2' }, { '1', '3' },
            { '1', '4' }, { '1', '5' }, { '1', '6' }, { '1', '7' }, { '1', '8' }, { '1', '9' }, { '2', '0' },
            { '2', '1' }, { '2', '2' }, { '2', '3' }, { '2', '4' }, { '2', '5' }, { '2', '6' }, { '2', '7' },
            { '2', '8' }, { '2', '9' }, { '3', '0' }, { '3', '1' }, { '3', '2' }, { '3', '3' }, { '3', '4' },
            { '3', '5' }, { '3', '6' }, { '3', '7' }, { '3', '8' }, { '3', '9' }, { '4', '0' }, { '4', '1' },
            { '4', '2' }, { '4', '3' }, { '4', '4' }, { '4', '5' }, { '4', '6' }, { '4', '7' }, { '4', '8' },
            { '4', '9' }, { '5', '0' }, { '5', '1' }, { '5', '2' }, { '5', '3' }, { '5', '4' }, { '5', '5' },
            { '5', '6' }, { '5', '7' }, { '5', '8' }, { '5', '9' }, { '6', '0' }, { '6', '1' }, { '6', '2' },
            { '6', '3' }, { '6', '4' }, { '6', '5' }, { '6', '6' }, { '6', '7' }, { '6', '8' }, { '6', '9' },
            { '7', '0' }, { '7', '1' }, { '7', '2' }, { '7', '3' }, { '7', '4' }, { '7', '5' }, { '7', '6' },
            { '7', '7' }, { '7', '8' }, { '7', '9' }, { '8', '0' }, { '8', '1' }, { '8', '2' }, { '8', '3' },
            { '8', '4' }, { '8', '5' }, { '8', '6' }, { '8', '7' }, { '8', '8' }, { '8', '9' }, { '9', '0' },
            { '9', '1' }, { '9', '2' }, { '9', '3' }, { '9', '4' }, { '9', '5' }, { '9', '6' }, { '9', '7' },
            { '9', '8' }, { '9', '9' }
        };

        char* out = &buffer[CARB_COUNTOF(buffer) - 1];
        *out = '\0'; // NUL terminate
        char* const end = out;
        while (val >= 100)
        {
            // Since our division is very slow (integer division is slow anyways), use a lookup table and do digits two
            // at a time. See Alexandrescu's talk "Three Optimization Tips for C++", tip from {fmt} library.
            uint128_t mod;
            val = divide_and_modulus(val, uint128_t(100), mod);
            auto& lookup = kDigits[cast_to_uint64_t(mod)];
            out -= 2;
            CARB_ASSERT(out >= buffer);
            memcpy(out, lookup, sizeof(lookup));
        }
        if (val < 10)
        {
            *--out = char('0' + (unsigned char)cast_to_uint64_t(val));
        }
        else
        {
            out -= 2;
            auto& lookup = kDigits[cast_to_uint64_t(val)];
            out[0] = lookup[0];
            out[1] = lookup[1];
        }
        return cpp::string_view{ out, size_t(end - out) };
    }

    cpp::string_view format(int128_t val_) noexcept
    {
        bool const negative = val_ < 0;
        uint128_t val = negative ? uint128_t(0) - uint128_t(val_) : uint128_t(val_);
        auto sv = format(val);
        if (!negative)
            return sv;
        auto p = const_cast<char*>(sv.data());
        *--p = '-';
        return cpp::string_view(p, sv.length() + 1);
    }

    cpp::string_view format_hex(int128_t val) noexcept
    {
        return format_hex(uint128_t(val));
    }

    cpp::string_view format_hex(uint128_t val) noexcept
    {
        constexpr static char kDigitsHex[] = "0123456789ABCDEF";
        char* out = &buffer[CARB_COUNTOF(buffer) - 1];
        *out = '\0'; // NUL terminate
        char* const end = out;
        while (val >= 0x10)
        {
            *--out = kDigitsHex[cast_to_uint64_t(val) & 0xf];
            val >>= 4;
        }
        *--out = kDigitsHex[cast_to_uint64_t(val) & 0xf];
        return cpp::string_view{ out, size_t(end - out) };
    }

private:
    char buffer[41]; // 39 characters + optional '-' + NUL
};

} // namespace detail
//! \endcond

/**
 * Formats a signed 128-bit integer as a string.
 * @param val The 128-bit signed integer.
 * @returns a `std::string` with the decimal value of @p val.
 */
inline std::string to_string(const int128_t& val)
{
    detail::formatter128 formatter;
    auto sv = formatter.format(val);
    return std::string(sv);
}

/**
 * Formats an unsigned 128-bit integer as a string.
 * @param val The 128-bit unsigned integer.
 * @returns a `std::string` with the decimal value of @p val.
 */
inline std::string to_string(const uint128_t& val)
{
    detail::formatter128 formatter;
    auto sv = formatter.format(val);
    return std::string(sv);
}

} // namespace math
} // namespace carb

#ifndef DOXYGEN_BUILD
#    ifndef __GLIBCXX_TYPE_INT_N_0 // gnuc extension
//! Hash support for int128_t
template <>
struct std::hash<carb::math::int128_t>
{
    //! @private
    size_t operator()(const carb::math::int128_t& val) const noexcept
    {
        return carb::hashBuffer(&val, sizeof(val));
    }
};

//! Hash support for uint128_t
template <>
struct std::hash<carb::math::uint128_t>
{
    //! @private
    size_t operator()(const carb::math::uint128_t& val) const noexcept
    {
        return carb::hashBuffer(&val, sizeof(val));
    }
};
#    endif
#endif

// operator<< support
#if !defined(DOXYGEN_BUILD) && !CARB_TOOLCHAIN_CLANG && (CARB_COMPILER_GNUC && __GNUC__ >= 10)
// GCC 10+ really wants this in the std namespace which seems weird.
namespace std
{
#else
namespace carb
{
namespace math
{
#endif

/**
 * Stream insertion operator for signed 128-bit integers.
 *
 * Will format as hex or decimal depending on the mode of the stream. Hex formatting is always unsigned. Octal
 * formatting is not supported and will format as decimal.
 * @param os The stream to insert into.
 * @param val The signed 128-bit integer.
 * @returns os
 */
inline ::std::ostream& operator<<(::std::ostream& os, const ::carb::math::int128_t& val)
{
    ::carb::math::detail::formatter128 formatter;
    auto sv = !(os.flags() & ::std::ios_base::hex) ? formatter.format(val) : formatter.format_hex(val);
    os << sv;
    return os;
}

/**
 * Stream insertion operator for unsigned 128-bit integers.
 *
 * Will format as hex or decimal depending on the mode of the stream. Octal formatting is not supported and will format
 * as decimal.
 * @param os The stream to insert into.
 * @param val The unsigned 128-bit integer.
 * @returns os
 */
inline ::std::ostream& operator<<(::std::ostream& os, const ::carb::math::uint128_t& val)
{
    ::carb::math::detail::formatter128 formatter;
    auto sv = !(os.flags() & ::std::ios_base::hex) ? formatter.format(val) : formatter.format_hex(val);
    os << sv;
    return os;
}

#if !defined(DOXYGEN_BUILD) && !CARB_TOOLCHAIN_CLANG && (CARB_COMPILER_GNUC && __GNUC__ >= 10)
}
#else
}
}
#endif

#undef CARBLOCAL_USE_BUILTIN_INT128
