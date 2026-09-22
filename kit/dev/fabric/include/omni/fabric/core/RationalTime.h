// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <cmath>
#include <cstdint>
#include <string>

#include <carb/logging/Log.h>

namespace omni
{
namespace fabric
{

// Each frame in the history buffer is timestamped with a frame time, stored as
// a rational number to minimize rounding issues. See threadgate::TimeRatio.
//
// README:
// Many of the operations below take math shortcuts. In addition, dealing with
// two structs having numerator and denoninator can lead to misreads about what's
// actually happening. Some of these implementation functions require a second read
// to validate mentally.
//
// Taking operator> as an example:
// Consider, TimeA = 1/2 and TimeB = 7/17, and we intend to do if (TimeA > TimeB) ...
//
//    bool operator>(const RationalTime& rhs) const
//    {
//        RationalTime thisReduced = reduce();
//        RationalTime rhsReduced = rhs.reduce();
//        int64_t val1 = thisReduced.numerator * rhsReduced.denominator;
//        int64_t val2 = rhsReduced.numerator * thisReduced.denominator;
//        return val1 > val2;
//    }
//
// Then:
//
// <init>
//     *this = {1,2}
//     rhs = {7,17}
//
// RationalTime thisReduced = reduce();
//     thisReduced = {1,2}
//
// RationalTime rhsReduced = rhs.reduce();
//     rhsReduced = {7,17}
//
//
// int64_t val1 = thisReduced.numerator * rhsReduced.denominator;
//     val1 = 1 * 17 = 17
//
// int64_t val2 = rhsReduced.numerator * thisReduced.denominator;
//     val2 = 7 * 2 = 14
//
// return val1 > val2;
//     return 17 > 14
//
// Written longhand, this is similar to doing...
// 1     17          7     2       17       14
// -  x  --    >    --  x  -   =   --   >   --
// 2     17         17     2       34       34
//
// ... but since we know the math we are doing is to reach a common denominator,
// we can drop the denominator in the final comparison.
//
// The operator> overload is just one example of such math shortcuts.
//
struct RationalTime
{
    int64_t numerator;
    uint64_t denominator;

    inline constexpr RationalTime()
        : numerator(0)
        , denominator(0u)
    {
    }

    inline constexpr RationalTime(int64_t n, uint64_t d)
        : numerator(n)
        , denominator(d)
    {
    }

    template<typename T>
    inline constexpr RationalTime(const std::initializer_list<T>& init)
    {
        typename std::initializer_list<T>::const_iterator it = init.begin();
        numerator = (it != init.end()) ? *it++ : 0;
        denominator = (it != init.end()) ? *it : 0;
    }

    // Minimize denominator small by dividing by gcd(numerator,denominator)
    RationalTime reduce() const
    {
        RationalTime result{ 0, 0 };

        int64_t gcdNumDen = gcd(numerator, denominator);

        if (gcdNumDen != 0)
        {
            result.numerator = numerator / gcdNumDen;
            result.denominator = denominator / gcdNumDen;
        }

        return result;
    }

    bool operator==(RationalTime rhs) const
    {
        RationalTime thisReduced = reduce();
        RationalTime rhsReduced = rhs.reduce();

        return (thisReduced.numerator == rhsReduced.numerator) && (thisReduced.denominator == rhsReduced.denominator);
    }

    bool operator!=(const RationalTime& rhs) const
    {
        return !(*this == rhs);
    }

    bool operator<(const RationalTime& rhs) const
    {
        RationalTime thisReduced = reduce();
        RationalTime rhsReduced = rhs.reduce();
        int64_t val1 = thisReduced.numerator * rhsReduced.denominator;
        int64_t val2 = rhsReduced.numerator * thisReduced.denominator;
        return val1 < val2;
    }
    bool operator<=(const RationalTime& rhs) const
    {
        RationalTime thisReduced = reduce();
        RationalTime rhsReduced = rhs.reduce();
        int64_t val1 = thisReduced.numerator * rhsReduced.denominator;
        int64_t val2 = rhsReduced.numerator * thisReduced.denominator;
        return val1 <= val2;
    }

    bool operator>(const RationalTime& rhs) const
    {
        RationalTime thisReduced = reduce();
        RationalTime rhsReduced = rhs.reduce();
        int64_t val1 = thisReduced.numerator * rhsReduced.denominator;
        int64_t val2 = rhsReduced.numerator * thisReduced.denominator;
        return val1 > val2;
    }
    bool operator>=(const RationalTime& rhs) const
    {
        RationalTime thisReduced = reduce();
        RationalTime rhsReduced = rhs.reduce();
        int64_t val1 = thisReduced.numerator * rhsReduced.denominator;
        int64_t val2 = rhsReduced.numerator * thisReduced.denominator;
        return val1 >= val2;
    }

    static int64_t gcd(int64_t a, int64_t b)
    {
        while (b != 0)
        {
            int64_t t = b;
            b = a % b;
            a = t;
        }
        return std::max(a, -a);
    }

    inline explicit operator double() const
    {
        // TODO: Would it be better to explicitly use a tagged nan?
        // return denominator ? ((double)numerator / (double)denominator) : std::nan("");
        //
        return ((double)numerator / (double)denominator);
    }

    RationalTime alignDown(const RationalTime& alignment) const
    {
        int64_t scaledNumerator = numerator * alignment.denominator;
        int64_t scaledAlignment = alignment.numerator * denominator;

        if (scaledNumerator >= 0) {
            scaledNumerator = (scaledNumerator / scaledAlignment) * scaledAlignment;
        } else {
            scaledNumerator = ((scaledNumerator - scaledAlignment + 1) / scaledAlignment) * scaledAlignment;
        }

        return {scaledNumerator, denominator * alignment.denominator};
    }

    RationalTime alignUp(const RationalTime& alignment) const
    {
        int64_t scaledNumerator = numerator * alignment.denominator;
        int64_t scaledAlignment = alignment.numerator * denominator;

        if (scaledNumerator >= 0) {
            scaledNumerator = ((scaledNumerator + scaledAlignment - 1) / scaledAlignment) * scaledAlignment;
        } else {
            scaledNumerator = (scaledNumerator / scaledAlignment) * scaledAlignment;
        }

        return {scaledNumerator, denominator * alignment.denominator};
    }

    RationalTime operator-(RationalTime b) const
    {
        RationalTime result;
        result.numerator = numerator * int64_t(b.denominator) - b.numerator * int64_t(denominator);
        result.denominator = denominator * b.denominator;

        return result.reduce();
    }

    RationalTime operator+(RationalTime b) const
    {
        RationalTime result;
        result.numerator = numerator * int64_t(b.denominator) + b.numerator * int64_t(denominator);
        result.denominator = denominator * b.denominator;

        return result.reduce();
    }

    RationalTime operator*(const RationalTime& other) const
    {
        RationalTime result;
        result.numerator = numerator * other.numerator;
        result.denominator = denominator * other.denominator;

        return result.reduce();
    }

    RationalTime operator/(const RationalTime& other) const
    {
        RationalTime result;
        result.numerator = numerator * other.denominator;
        result.denominator = denominator * other.numerator;

        return result.reduce();
    }

    RationalTime operator*(int64_t b) const
    {
        RationalTime result;
        result.numerator = numerator * b;
        result.denominator = denominator;

        return result.reduce();
    }

    inline std::string toString() const
    {
        return std::to_string(numerator) + "/" + std::to_string(denominator);
    }
};
static const RationalTime kInvalidRationalTime{ 0, 0 };

inline RationalTime operator*(int64_t scalar, const RationalTime& time)
{
    return RationalTime( scalar * time.numerator, time.denominator );
}

inline double computeTheta(const RationalTime& start, const RationalTime& end, const RationalTime& time)
{
    if (start == end)
    {
        return 0.0;
    }

    if ((double)start.denominator == 0.0 || (double)end.denominator == 0.0)
    {
        CARB_LOG_WARN_ONCE("StageAtTime computeTheta(): cannot divide by a denominator with a value of zero.");
        return 0.0;
    }
    else
    {
        double a_t = (double)start.numerator / (double)start.denominator;
        double b_t = (double)end.numerator / (double)end.denominator;

        double c_t = (double)time.numerator / (double)time.denominator;
        return (c_t - a_t) / (b_t - a_t);
    }
}

static_assert(std::is_standard_layout<RationalTime>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

} // namespace fabric
} // namespace omni

inline std::ostream& operator<<(std::ostream& os, const omni::fabric::RationalTime& rt)
{
    return os << rt.numerator << "/" << rt.denominator;
}

inline bool isinf(const omni::fabric::RationalTime& time)
{
    return time.numerator != 0.0 && time.denominator == 0.0;
}

inline bool isnan(const omni::fabric::RationalTime& time)
{
    return time.numerator == 0.0 && time.denominator == 0.0;
}
