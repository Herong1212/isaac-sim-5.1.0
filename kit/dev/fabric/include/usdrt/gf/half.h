// Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file
//!
//! @brief TODO

#include <usdrt/gf/defines.h>
#include <usdrt/gf/traits.h>

#include <stdint.h>
#include <type_traits>

namespace omni
{
namespace math
{
namespace linalg
{

class half
{
public:
    half() noexcept = default;
    constexpr half(const half&) noexcept = default;
    constexpr half& operator=(const half&) noexcept = default;

    // TODO: Change this to be explicit, once OGN default value code supports explicit conversions.
    // Converting to half-precision can be dangerous if unintentional, so make sure it's intentional.
    CUDA_CALLABLE half(float f) noexcept : v(floatToHalf(f))
    {
        static_assert(std::is_pod<half>::value, "half should be a POD type.");
    }
    // NOTE: This is two roundings, so could occasionally produce a suboptimal rounded value.
    explicit CUDA_CALLABLE half(double f) noexcept : v(floatToHalf(float(f)))
    {
    }

    explicit CUDA_CALLABLE half(int i) noexcept : v(floatToHalf(float(i)))
    {
    }

    explicit CUDA_CALLABLE operator float() const noexcept
    {
        return halfToFloat(v);
    }

    explicit CUDA_CALLABLE operator double() const noexcept
    {
        return double(halfToFloat(v));
    }

    explicit CUDA_CALLABLE operator int() const noexcept
    {
        return int(halfToFloat(v));
    }

    CUDA_CALLABLE bool operator<(const half& rhs) const noexcept
    {
        return halfToFloat(v) < halfToFloat(rhs.bits());
    }

    CUDA_CALLABLE bool operator<=(const half& rhs) const noexcept
    {
        return halfToFloat(v) <= halfToFloat(rhs.bits());
    }

    CUDA_CALLABLE bool operator>(const half& rhs) const noexcept
    {
        return halfToFloat(v) > halfToFloat(rhs.bits());
    }

    CUDA_CALLABLE bool operator>=(const half& rhs) const noexcept
    {
        return halfToFloat(v) >= halfToFloat(rhs.bits());
    }

    CUDA_CALLABLE bool operator==(const half& rhs) const noexcept
    {
        return bits() == rhs.bits();
    }

    CUDA_CALLABLE bool operator!=(const half& rhs) const noexcept
    {
        return bits() != rhs.bits();
    }

    CUDA_CALLABLE half operator-() const noexcept
    {
        half result(-halfToFloat(v));
        return result;
    }

    CUDA_CALLABLE half& operator+=(const half& rhs) noexcept
    {
        v = floatToHalf(halfToFloat(v) + halfToFloat(rhs.bits()));
        return *this;
    }

    CUDA_CALLABLE half& operator-=(const half& rhs) noexcept
    {
        v = floatToHalf(halfToFloat(v) - halfToFloat(rhs.bits()));
        return *this;
    }

    CUDA_CALLABLE half& operator*=(const half& rhs) noexcept
    {
        v = floatToHalf(halfToFloat(v) * halfToFloat(rhs.bits()));
        return *this;
    }

    CUDA_CALLABLE half& operator/=(const half& rhs) noexcept
    {
        v = floatToHalf(halfToFloat(v) / halfToFloat(rhs.bits()));
        return *this;
    }

#ifndef DOXYGEN_BUILD
    friend CUDA_CALLABLE half operator+(half lhs, const half& rhs)
    {
        lhs += rhs;
        return lhs;
    }

    friend CUDA_CALLABLE half operator-(half lhs, const half& rhs)
    {
        lhs -= rhs;
        return lhs;
    }

    friend CUDA_CALLABLE half operator*(half lhs, const half& rhs)
    {
        lhs *= rhs;
        return lhs;
    }

    friend CUDA_CALLABLE half operator/(half lhs, const half& rhs)
    {
        lhs /= rhs;
        return lhs;
    }
#endif // DOXYGEN_BUILD

    CUDA_CALLABLE uint16_t& bits() noexcept
    {
        return v;
    }

    CUDA_CALLABLE const uint16_t& bits() const noexcept
    {
        return v;
    }

#ifndef DOXYGEN_BUILD
    constexpr static uint32_t s_floatMantissaBitCount = 23;
    constexpr static uint32_t s_floatMantissaMask = (uint32_t(1) << s_floatMantissaBitCount) - 1;
    constexpr static uint32_t s_floatExponentBitCount = 8;
    constexpr static uint32_t s_floatShiftedExponentMask = (uint32_t(1) << s_floatExponentBitCount) - 1;
    constexpr static uint32_t s_floatExponentExcess = 0x7F;
    constexpr static uint32_t s_floatInfExpWithExcess = s_floatShiftedExponentMask;

    constexpr static uint16_t s_halfMantissaBitCount = 10;
    constexpr static uint16_t s_halfMantissaMask = (uint16_t(1) << s_halfMantissaBitCount) - 1;
    constexpr static uint16_t s_halfExponentBitCount = 5;
    constexpr static uint16_t s_halfShiftedExponentMask = (uint16_t(1) << s_halfExponentBitCount) - 1;
    constexpr static uint16_t s_halfExponentExcess = 0xF;
    constexpr static uint16_t s_halfInfExpWithExcess = s_halfShiftedExponentMask;

    constexpr static uint32_t s_mantissaBitCountDiff = s_floatMantissaBitCount - s_halfMantissaBitCount;
    constexpr static uint32_t s_exponentExcessDiff = s_floatExponentExcess - s_halfExponentExcess;
#endif // DOXYGEN_BUILD

    static CUDA_CALLABLE float halfToFloat(uint16_t i) noexcept
    {
        // Extract parts
        uint32_t sign = uint32_t(i >> 15);
        uint16_t exponent = (i >> s_halfMantissaBitCount) & s_halfShiftedExponentMask;
        uint16_t mantissa = (i & s_halfMantissaMask);
        // Shift parts
        uint32_t newExponent = (uint32_t(exponent) + s_exponentExcessDiff);
        uint32_t newMantissa = (mantissa << s_mantissaBitCountDiff);
        if (exponent == s_halfInfExpWithExcess)
        {
            // Infinity or NaN
            newExponent = s_floatInfExpWithExcess;
        }
        else if (exponent == 0)
        {
            // Denormal
            if (mantissa == 0)
            {
                // Zero
                newExponent = 0;
            }
            else
            {
                // Non-zero denormal
                ++newExponent;
                do
                {
                    newMantissa <<= 1;
                    --newExponent;
                } while (!(newMantissa & (s_floatMantissaMask + 1)));
                newMantissa &= s_floatMantissaMask;
            }
        }
        uint32_t result = (sign << 31) | (newExponent << s_floatMantissaBitCount) | newMantissa;
        static_assert(sizeof(uint32_t) == sizeof(float),
                      "The following union requires that uint32_t and float are the same size.");
        union
        {
            uint32_t result_i;
            float result_f;
        };
        result_i = result;
        return result_f;
    }

    static CUDA_CALLABLE uint16_t floatToHalf(float f) noexcept
    {
        static_assert(sizeof(uint32_t) == sizeof(float),
                      "The following union requires that uint32_t and float are the same size.");
        union
        {
            uint32_t input_i;
            float input_f;
        };
        input_f = f;
        uint32_t i = input_i;
        // Extract parts
        uint32_t sign = uint32_t(i >> 31);
        uint32_t exponent = (i >> s_floatMantissaBitCount) & s_floatShiftedExponentMask;
        uint32_t mantissa = (i & s_floatMantissaMask);

        bool atLeastHalf = false;
        bool nonZeroLowBits = false;
        uint16_t newExponent;
        uint16_t newMantissa;
        if (exponent >= (s_exponentExcessDiff + s_halfInfExpWithExcess))
        {
            // New value will be infinity or NaN
            newExponent = s_halfInfExpWithExcess;
            if (exponent == s_floatInfExpWithExcess)
            {
                // Old value was infinity or NaN
                newMantissa = (mantissa >> s_mantissaBitCountDiff);
                if (mantissa != 0 && newMantissa == 0)
                {
                    // Preserve NaN
                    newMantissa = 1;
                }
            }
            else
            {
                // New infinity
                newMantissa = 0;
            }
        }
        // NOTE: s_exponentExcessDiff is the smallest half-precision exponent with single-precision's excess.
        else if (exponent <= s_exponentExcessDiff)
        {
            // New value will be denormal (unless rounded up to normal)
            newExponent = 0;
            if (exponent < (s_exponentExcessDiff - s_halfMantissaBitCount))
            {
                // Zero
                newMantissa = 0;
            }
            else
            {
                // Non-zero denormal
                mantissa += (s_floatMantissaMask + 1);
                std::size_t shift = (s_exponentExcessDiff + 1) + s_mantissaBitCountDiff - exponent;
                newMantissa = (mantissa >> shift);

                atLeastHalf = ((mantissa >> (shift - 1)) & 1);
                nonZeroLowBits = (mantissa & ((1 << (shift - 1)) - 1)) != 0;
            }
        }
        else
        {
            // New value will be normal (unless rounded up to infinity)
            newMantissa = (mantissa >> s_mantissaBitCountDiff);
            newExponent = exponent - s_exponentExcessDiff;

            atLeastHalf = ((mantissa >> (s_mantissaBitCountDiff - 1)) & 1);
            nonZeroLowBits = (mantissa & ((1 << (s_mantissaBitCountDiff - 1)) - 1)) != 0;
        }

        // Round half to even
        bool odd = (newMantissa & 1);
        newMantissa += atLeastHalf && (nonZeroLowBits || odd);
        if (newMantissa == (s_halfMantissaMask + 1))
        {
            newMantissa = 0;
            ++newExponent;
        }

        uint16_t result = (sign << 15) | (newExponent << s_halfMantissaBitCount) | newMantissa;
        return result;
    }

private:
    uint16_t v;
};

}
}
}

namespace usdrt
{

using GfHalf = omni::math::linalg::half;

template <>
struct GfIsFloatingPoint<GfHalf> : public std::integral_constant<bool, true>
{
};

}
