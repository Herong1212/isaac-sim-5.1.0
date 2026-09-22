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
//! @brief Math utility for doing a large multiply-divide operation.
#pragma once

#include "../cpp/Optional.h"

#if CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG
#elif CARB_COMPILER_MSC
extern "C"
{
#    if CARB_X86_64
    unsigned char _addcarry_u64(unsigned char, unsigned __int64, unsigned __int64, unsigned __int64*);
    unsigned __int64 _umul128(unsigned __int64, unsigned __int64, unsigned __int64*);
    unsigned __int64 _udiv128(unsigned __int64, unsigned __int64, unsigned __int64, unsigned __int64*);
#        pragma intrinsic(_addcarry_u64)
#        pragma intrinsic(_umul128)
#        pragma intrinsic(_udiv128)
#    elif CARB_AARCH64
    unsigned __int64 __umulh(unsigned __int64, unsigned __int64);
#        pragma intrinsic(__umulh)
#    else
    CARB_UNSUPPORTED_ARCHITECTURE();
#    endif
}
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

namespace carb
{
namespace math
{
//! \cond DEV
namespace detail
{

inline uint8_t adc(uint8_t cf, uint64_t addend1, uint64_t addend2, uint64_t& sum) noexcept
{
#if CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG
    auto c1 = __builtin_add_overflow(addend1, addend2, &sum);
    auto c2 = __builtin_add_overflow(sum, cf, &sum);
    return uint8_t(c1 | c2);
#elif CARB_COMPILER_MSC
#    if CARB_X86_64
    return _addcarry_u64(cf, addend1, addend2, &sum);
#    elif CARB_AARCH64
    // Don't have any intrinsics that support carry flag here, so do manual carry check
    auto temp = addend1 + addend2;
    auto c1 = temp < addend1;
    sum = temp + cf;
    c1 |= (sum < temp);
    return uint8_t(c1);
#    else
    CARB_UNSUPPORTED_ARCHITECTURE();
#    endif
#else
    CARB_UNSUPPORTED_COMPILER();
#endif
}

inline unsigned clz(uint64_t val) noexcept
{
#if CARB_COMPILER_MSC
    unsigned long index;
    return _BitScanReverse64(&index, val) ? 64u - 1u - index : 64u;
#elif CARB_COMPILER_GNUC
    return val ? unsigned(__builtin_clzll(val)) : 64u;
#else
    CARB_UNSUPPORTED_COMPILER();
#endif
}

inline uint64_t umul128(uint64_t multiplier, uint64_t multiplicand, uint64_t& productHigh) noexcept
{
#if CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG
#    if CARB_X86_64
    uint64_t low;
    asm("mulq %[multiplicand]"
        : "=d"(productHigh), "=a"(low)
        : "a"(multiplier), [multiplicand] "rm"(multiplicand)
        : "cc" /* flags */
    );
    return low;
#    elif CARB_AARCH64
    // Combining these instructions into one asm block usually results in a runtime error since the compiler uses the x0
    // register both for the multiplier as well as the result from the umulh instruction.
    uint64_t low;
    asm("umulh %[high], %[u], %[v]" : [high] "=r"(productHigh) : [u] "r"(multiplier), [v] "r"(multiplicand));
    asm("mul %[low], %[u], %[v]" : [low] "=r"(low) : [u] "r"(multiplier), [v] "r"(multiplicand));
    return low;
#    else
    CARB_UNSUPPORTED_ARCHITECTURE();
#    endif
#elif CARB_COMPILER_MSC
#    if CARB_X86_64
    return _umul128(multiplier, multiplicand, &productHigh);
#    elif CARB_AARCH64
    productHigh = __umulh(multiplier, multiplicand);
    return multiplier * multiplicand;
#    else
    CARB_UNSUPPORTED_ARCHITECTURE();
#    endif
#else
    CARB_UNSUPPORTED_COMPILER();
#endif
}

inline uint64_t udiv128(uint64_t dividendHigh, uint64_t dividendLow, uint64_t divisor, uint64_t* remainder = nullptr) noexcept
{
#if CARB_AARCH64
    // aarch64 doesn't have 128-bit divide, so we do Knuth's long division (Algorithm D)
    CARB_ASSERT(divisor != 0); // divide-by-zero
    CARB_ASSERT(dividendHigh < divisor); // overflow

    unsigned s = clz(divisor);
    if (s)
    {
        divisor <<= s;
        dividendHigh <<= s;
        dividendHigh |= (dividendLow >> (64 - s));
        dividendLow <<= s;
    }

    // High quotient
    uint64_t qhat = dividendHigh / unsigned(divisor >> 32);
    uint64_t rhat = dividendHigh % unsigned(divisor >> 32);

    while (unsigned(qhat >> 32) != 0 ||
           uint64_t(unsigned(qhat)) * unsigned(divisor) > ((rhat << 32) | unsigned(dividendLow >> 32)))
    {
        --qhat;
        rhat += unsigned(divisor >> 32);
        if (unsigned(rhat >> 32))
            break;
    }

    unsigned q1 = unsigned(qhat);
    uint64_t uhat = ((dividendHigh << 32) | unsigned(dividendLow >> 32)) - q1 * divisor;

    qhat = uhat / unsigned(divisor >> 32);
    rhat = uhat % unsigned(divisor >> 32);

    while (unsigned(qhat >> 32) != 0 ||
           uint64_t(unsigned(qhat)) * unsigned(divisor) > ((rhat << 32) | unsigned(dividendLow)))
    {
        --qhat;
        rhat += unsigned(divisor >> 32);
        if (unsigned(rhat >> 32))
            break;
    }

    unsigned q0 = unsigned(qhat);

    if (remainder)
        *remainder = (((uhat << 32) | unsigned(dividendLow)) - q0 * divisor) >> s;
    return uint64_t(q1) << 32 | q0;
#elif CARB_X86_64
#    if CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG
    uint64_t quotient, rem;
    asm("divq %4" : "=a"(quotient), "=d"(rem) : "1"(dividendHigh), "0"(dividendLow), "rm"(divisor) : "cc" /*flags*/);
    if (remainder)
        *remainder = rem;
    return quotient;
#    elif CARB_COMPILER_MSC
    uint64_t rem;
    uint64_t quotient = _udiv128(dividendHigh, dividendLow, divisor, &rem);
    if (remainder)
        *remainder = rem;
    return quotient;
#    else
    CARB_UNSUPPORTED_COMPILER();
#    endif
#else
    CARB_UNSUPPORTED_ARCHITECTURE();
#endif
}

} // namespace detail
//! \endcond

/**
 * A rounding policy for `mulDiv` that rounds the result toward zero, the default behavior for integer division.
 *
 * When passed to \ref mulDiv(), this policy will always round the result toward zero. Positive numbers round toward the
 * floor; negative numbers round less negative. This is the default for integer operations, so this rounding policy is
 * effectively a no-op.
 * Use @ref round_toward_zero or @ref round_floor with the call to @ref mulDiv().
 */
struct round_toward_zero_t
{
    //! @private
    void operator()(uint64_t&, uint64_t&, uint64_t) noexcept
    {
        // nothing needed; integer math already rounds towards zero
    }
};
//! An instantiation of the \ref round_toward_zero_t policy type that can be passed to \ref mulDiv().
CARB_WEAKLINK round_toward_zero_t round_toward_zero;
//! An alias of \ref round_toward_zero.
CARB_WEAKLINK round_toward_zero_t round_floor;

/**
 * A rounding policy for `mulDiv` that rounds the result away from zero.
 *
 * When passed to \ref mulDiv(), this policy will always round the result away from zero. Positive numbers round toward
 * the ceiling; negative numbers round further negative. This works by adding `divisor - 1` to the temporary value
 * before the divide operation.
 * Use @ref round_away_from_zero or @ref round_ceil with the call to @ref mulDiv().
 */
struct round_away_from_zero_t
{
    //! @private
    void operator()(uint64_t& high, uint64_t& low, uint64_t divisor) noexcept
    {
        high += detail::adc(0, low, divisor - 1, low);
    }
};
//! An instantiation of the \ref round_away_from_zero_t policy type that can be passed to \ref mulDiv().
CARB_WEAKLINK round_away_from_zero_t round_away_from_zero;
//! An alias of \ref round_away_from_zero.
CARB_WEAKLINK round_away_from_zero_t round_ceil;

/**
 * A rounding policy for `mulDiv` that rounds the result to the nearest neighbor.
 *
 * If the absolute value of the result is a positive half integer (0.5), the result is rounded away from zero. This
 * works by adding `divisor / 2` to the temporary value before the divide operation.
 * Use @ref round_nearest_neighbor with the call to @ref mulDiv().
 */
struct round_nearest_neighbor_t
{
    //! @private
    void operator()(uint64_t& high, uint64_t& low, uint64_t divisor) noexcept
    {
        high += detail::adc(0, low, divisor / 2, low);
    }
};
//! An instantiation of the \ref round_nearest_neighbor_t policy type that can be passed to \ref mulDiv().
CARB_WEAKLINK round_nearest_neighbor_t round_nearest_neighbor;

/**
 * Multiplies two 64-bit unsigned integers and then divides the 128-bit result by a third 64-bit unsigned integer.
 *
 * Typically multiplying \p num * \p multiplier can result in overflowing a 64-bit value. This function uses a 128-bit
 * temporary value for the multiplication operation, and then divides it by a 64-bit value. Effectively performs:
 * ```cpp
 * uint128_t temp = uint128_t(num) * multiplier;
 * if (!divisor || (temp >> 64) >= divisor)
 *     return cpp::nullopt; // overflow or divide by zero
 * return uint64_t(round(temp / divisor));
 * ```
 *
 * If the result will not fit in a 64-bit value, or \p divisor is zero, `carb::cpp::nullopt` is returned to indicate
 * the math error.
 *
 * @param round The rounding policy to use. See @ref round_toward_zero, @ref round_away_from_zero and
 *   @ref round_nearest_neighbor.
 * @param num The multiplicand.
 * @param multiplier The multiplier, multiplied with \p num produces a 128-bit value.
 * @param divisor The divisor, used to divide the 128-bit product of \p num X \p multiplier.
 * @returns A \ref carb::cpp::optional containing the 64-bit result of the operation. If @p divisor is zero, or the
 *  result would not fit in a 64-bit value, `carb::cpp::nullopt` is returned instead.
 */
template <class RoundPolicy>
[[nodiscard]] cpp::optional<uint64_t> mulDiv(RoundPolicy round, uint64_t num, uint64_t multiplier, uint64_t divisor) noexcept
{
    // No divide-by-zero
    CARB_UNLIKELY_IF(!divisor)
    {
        return cpp::nullopt;
    }

    uint64_t high, low;
    low = detail::umul128(num, multiplier, high);

    // Apply rounding policy
    round(high, low, divisor);

    // Fail on overflow
    if (high >= divisor)
        return {};

    return cpp::make_optional(detail::udiv128(high, low, divisor));
}

/**
 * Multiplies two 64-bit signed integers and then divides the 128-bit result by a third 64-bit signed integer.
 *
 * Typically multiplying \p num * \p multiplier can result in overflowing a 64-bit value. This function uses a 128-bit
 * temporary value for the multiplication operation, and then divides it by a 64-bit value. Effectively performs:
 * ```cpp
 * int128_t temp = int128_t(num) * multiplier;
 * if (!divisor || (abs(temp) >> 64) >= abs(divisor))
 *     return cpp::nullopt; // overflow or divide by zero
 * return int64_t(round(temp / divisor));
 * ```
 *
 * If the result will not fit in a 64-bit value, or \p divisor is zero, `carb::cpp::nullopt` is returned to indicate
 * the math error.
 *
 * @param round The rounding policy to use. See @ref round_toward_zero, @ref round_away_from_zero and
 *   @ref round_nearest_neighbor.
 * @param num The multiplicand.
 * @param multiplier The multiplier, multiplied with \p num produces a 128-bit value.
 * @param divisor The divisor, used to divide the 128-bit product of \p num X \p multiplier.
 * @returns A \ref carb::cpp::optional containing the 64-bit result of the operation. If @p divisor is zero, or the
 *  result would not fit in a 64-bit value, `carb::cpp::nullopt` is returned instead.
 */
template <class RoundPolicy>
[[nodiscard]] cpp::optional<int64_t> mulDiv(RoundPolicy round, int64_t num, int64_t multiplier, int64_t divisor) noexcept
{
    bool const negative = (num ^ multiplier ^ divisor) < 0;

    auto&& absolute = [](int64_t val) noexcept { return val >= 0 ? uint64_t(val) : uint64_t(-val); };

    auto uresult = mulDiv(round, absolute(num), absolute(multiplier), absolute(divisor));
    if (!uresult)
        return cpp::nullopt;

    // Change the sign
    int64_t result = negative ? -int64_t(uresult.value()) : int64_t(uresult.value());

    // Overflow occurred if the sign doesn't match expected
    if (result == 0 || negative == (result < 0))
        return cpp::make_optional(result);
    return cpp::nullopt;
}

/**
 * Multiplies two 64-bit floating-point values and then divides the result by a third 64-bit floating-point value.
 *
 * If the \p divisor is zero, `carb::cpp::nullopt` is returned to indicate the math error.
 *
 * @note This function rounds toward nearest neighbor, that is, results midway between representable values are rounded
 *  toward the nearest value with an even (0) least significant bit. This is the default for floating-point math. In
 *  order to use a different rounding mode, use `std::fesetround()` before calling this function, but be advised that
 *  compiler flags may be required and/or floating-point optimizations may need to be disabled.
 * @tparam RoundPolicy Ignored, provided for compatibility with integer `mulDiv` functions.
 * @param num The multiplicand.
 * @param multiplier The multiplier, multiplied with \p num.
 * @param divisor The divisor, used to divide the product of \p num X \p multiplier.
 * @returns A \ref carb::cpp::optional containing the 64-bit result of the operation. If @p divisor is zero
 *  `carb::cpp::nullopt` is returned instead.
 */
template <class RoundPolicy>
[[nodiscard]] cpp::optional<double> mulDiv(RoundPolicy /*ignored*/, double num, double multiplier, double divisor) noexcept
{
    if (divisor == 0.)
        return cpp::nullopt;
    return (num * multiplier) / divisor;
}

/**
 * Multiplies two 64-bit unsigned integers and then divides the 128-bit result by a third 64-bit unsigned integer.
 *
 * Typically multiplying \p num * \p multiplier can result in overflowing a 64-bit value. This function uses a 128-bit
 * temporary value for the multiplication operation, and then divides it by a 64-bit value. Effectively performs:
 * ```cpp
 * uint128_t temp = uint128_t(num) * multiplier;
 * if (!divisor || (temp >> 64) >= divisor)
 *     return cpp::nullopt; // overflow or divide by zero
 * return uint64_t(temp / divisor);
 * ```
 *
 * If the result will not fit in a 64-bit value, or \p divisor is zero, `carb::cpp::nullopt` is returned to indicate
 * the math error.
 * @note This function rounds toward zero, the default for integer math. If a different rounding mode is desired, pass
 *  a rounding policy as the first parameter.
 * @param num The multiplicand.
 * @param multiplier The multiplier, multiplied with \p num produces a 128-bit value.
 * @param divisor The divisor, used to divide the 128-bit product of \p num X \p multiplier.
 * @returns A \ref carb::cpp::optional containing the 64-bit result of the operation. If @p divisor is zero, or the
 *  result would not fit in a 64-bit value, `carb::cpp::nullopt` is returned instead.
 */
[[nodiscard]] inline cpp::optional<uint64_t> mulDiv(uint64_t num, uint64_t multiplier, uint64_t divisor) noexcept
{
    return mulDiv(round_toward_zero, num, multiplier, divisor);
}

/**
 * Multiplies two 64-bit signed integers and then divides the 128-bit result by a third 64-bit signed integer.
 *
 * Typically multiplying \p num * \p multiplier can result in overflowing a 64-bit value. This function uses a 128-bit
 * temporary value for the multiplication operation, and then divides it by a 64-bit value. Effectively performs:
 * ```cpp
 * int128_t temp = int128_t(num) * multiplier;
 * if (!divisor || (abs(temp) >> 64) >= abs(divisor))
 *     return cpp::nullopt; // overflow or divide by zero
 * return int64_t(temp / divisor);
 * ```
 *
 * If the result will not fit in a 64-bit value, or \p divisor is zero, `carb::cpp::nullopt` is returned to indicate
 * the math error.
 *
 * @note This function rounds toward zero, the default for integer math. If a different rounding mode is desired, pass
 *  a rounding policy as the first parameter.
 * @param num The multiplicand.
 * @param multiplier The multiplier, multiplied with \p num produces a 128-bit value.
 * @param divisor The divisor, used to divide the 128-bit product of \p num X \p multiplier.
 * @returns A \ref carb::cpp::optional containing the 64-bit result of the operation. If @p divisor is zero, or the
 *  result would not fit in a 64-bit value, `carb::cpp::nullopt` is returned instead.
 */
[[nodiscard]] inline cpp::optional<int64_t> mulDiv(int64_t num, int64_t multiplier, int64_t divisor) noexcept
{
    return mulDiv(round_toward_zero, num, multiplier, divisor);
}

/**
 * Multiplies two 64-bit floating-point values and then divides the result by a third 64-bit floating-point value.
 *
 * If the \p divisor is zero, `carb::cpp::nullopt` is returned to indicate the math error. Effectively performs:
 * ```cpp
 * if (divisor == 0.0)
 *     return cpp::nullopt;
 * return (num * multiplier) / divisor;
 * ```
 *
 * @note This function rounds toward nearest neighbor, that is, results midway between representable values are rounded
 *  toward the nearest value with an even (0) least significant bit. This is the default for floating-point math. In
 *  order to use a different rounding mode, use `std::fesetround()` before calling this function, but be advised that
 *  compiler flags may be required and/or floating-point optimizations may need to be disabled.
 * @param num The multiplicand.
 * @param multiplier The multiplier, multiplied with \p num.
 * @param divisor The divisor, used to divide the product of \p num X \p multiplier.
 * @returns A \ref carb::cpp::optional containing the 64-bit result of the operation. If @p divisor is zero
 *  `carb::cpp::nullopt` is returned instead.
 */
[[nodiscard]] inline cpp::optional<double> mulDiv(double num, double multiplier, double divisor) noexcept
{
    return mulDiv([] {}, num, multiplier, divisor);
}

} // namespace math
} // namespace carb
