// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <cassert>
#include <cmath>
#include <cstdint>
#include <limits>
#include <string>

#include <omni/fabric/core/Macros.h>
#include <omni/fabric/core/RationalTime.h>

namespace omni
{
namespace fabric
{

double computeTheta(const double& start, const double& end);

// Each frame in the history buffer is timestamped with a frame time, stored as
// a rational number to minimize rounding issues. See threadgate::TimeRatio.
struct FabricTime
{
    inline constexpr FabricTime()
        : m_type(FabricTime::Type::NaN)
        , m_rep()
    {
    }

    inline constexpr FabricTime(const RationalTime& rationalTime)
        : m_type(FabricTime::Type::Rational)
        , m_rep(rationalTime)
    {
    }

    inline constexpr FabricTime(const double doubleTime)
        : m_type(FabricTime::Type::Double)
        , m_rep(doubleTime)
    {
    }

    inline constexpr FabricTime(int64_t n, uint64_t d)
        : m_type(FabricTime::Type::Rational)
        , m_rep(n, d)
    {
    }

    template<typename T>
    inline constexpr FabricTime(const std::initializer_list<T>& args)
        : m_type(FabricTime::Type::Rational)
        , m_rep(args)
    {
    }

    inline constexpr static FabricTime NaN()
    {
        return FabricTime();
    }

    inline explicit operator double() const
    {
        switch(m_type)
        {
            case FabricTime::Type::NaN:
            {
                return std::numeric_limits<double>::quiet_NaN();
            } break;
            case FabricTime::Type::Rational:
            {
                return (double)m_rep.rationalTime;
            } break;
            case FabricTime::Type::Double:
            {
                return (double)m_rep.doubleTime;
            } break;
        }

        return 0.0;
    }

    inline explicit operator RationalTime() const
    {
        return asRationalTime();
    }

    inline bool isValid() const
    {
        switch(m_type)
        {
            case FabricTime::Type::NaN:
            {
                return false;
            } break;
            case FabricTime::Type::Rational:
            {
                return m_rep.rationalTime.denominator != 0u;
            } break;
            case FabricTime::Type::Double:
            {
                return !std::isnan(m_rep.doubleTime) && !std::isinf(m_rep.doubleTime);
            } break;
        }

        return false;
    }

    static constexpr double kDoubleToRationalDefaultTolerance = 1e-7;

    inline RationalTime asRationalTime(int iterations = 1000, double tolerance = kDoubleToRationalDefaultTolerance) const
    {
        if (m_type == FabricTime::Type::NaN)
        {
            return kInvalidRationalTime;
        }
        else if (m_type == FabricTime::Type::Rational)
        {
            return m_rep.rationalTime;
        }

        // uses continued fraction expansion, like in https://kevinboone.me/rationalize.html?i=1

        double value = m_rep.doubleTime;

        int64_t coeff = static_cast<int64_t>(value);
        value = value - coeff;

        int64_t prevN = 1;
        int64_t currN = coeff;

        int64_t prevD = 0;
        int64_t currD = 1;

        for(int i = 0; i < iterations; ++i)
        {
            if ((abs((double(currN) / currD) - m_rep.doubleTime) < tolerance) || std::isinf(value) || value == 0.0)
            {
                break;
            }

            value = 1.0 / value;
            coeff = static_cast<int64_t>(value);
            value = value - coeff;

            const int64_t nextN = coeff * currN + prevN;
            const int64_t nextD = coeff * currD + prevD;

            prevN = currN;
            currN = nextN;

            prevD = currD;
            currD = nextD;
        }

        return RationalTime{currN, currD};
    }

    inline FabricTime alignDown(const FabricTime& alignment)
    {
        if (m_type == FabricTime::Type::Rational && alignment.m_type == FabricTime::Type::Rational)
        {
            return m_rep.rationalTime.alignDown(alignment.m_rep.rationalTime);
        }
        else
        {
            const double value = (double)*this;
            return std::floor(value / (double)(alignment)) * (double)(alignment);
        }
    }

    inline FabricTime alignUp(const FabricTime& alignment)
    {
        if (m_type == FabricTime::Type::Rational && alignment.m_type == FabricTime::Type::Rational)
        {
            return m_rep.rationalTime.alignUp(alignment.m_rep.rationalTime);
        }
        else
        {
            const double value = (double)*this;
            return std::ceil(value / (double)(alignment)) * (double)(alignment);
        }
    }

    inline bool operator==(const FabricTime& other) const
    {
        if (m_type == FabricTime::Type::Rational && other.m_type == FabricTime::Type::Rational)
        {
            return m_rep.rationalTime == other.m_rep.rationalTime;
        }
        else
        {
            return (double)(*this) == (double)(other);
        }
    }

    inline bool operator!=(const FabricTime& other) const
    {
        return !(*this == other);
    }

    inline bool operator<(const FabricTime& other) const
    {
        if (m_type == FabricTime::Type::Rational && other.m_type == FabricTime::Type::Rational)
        {
            return m_rep.rationalTime < other.m_rep.rationalTime;
        }
        else
        {
            return (double)(*this) < (double)(other);
        }
    }

    inline bool operator<=(const FabricTime& other) const
    {
        if (m_type == FabricTime::Type::Rational && other.m_type == FabricTime::Type::Rational)
        {
            return m_rep.rationalTime <= other.m_rep.rationalTime;
        }
        else
        {
            return (double)(*this) <= (double)(other);
        }
    }

    inline bool operator>(const FabricTime& other) const
    {
        if (m_type == FabricTime::Type::Rational && other.m_type == FabricTime::Type::Rational)
        {
            return m_rep.rationalTime > other.m_rep.rationalTime;
        }
        else
        {
            return (double)(*this) > (double)(other);
        }
    }

    inline bool operator>=(const FabricTime& other) const
    {
        if (m_type == FabricTime::Type::Rational && other.m_type == FabricTime::Type::Rational)
        {
            return m_rep.rationalTime >= other.m_rep.rationalTime;
        }
        else
        {
            return (double)(*this) >= (double)(other);
        }
    }

    inline FabricTime operator-(const FabricTime& other) const
    {
        if (m_type == FabricTime::Type::Rational && other.m_type == FabricTime::Type::Rational)
        {
            return FabricTime(m_rep.rationalTime - other.m_rep.rationalTime);
        }
        else
        {
            return FabricTime((double)(*this) - (double)(other));
        }
    }

    inline FabricTime operator+(const FabricTime& other) const
    {
        if (m_type == FabricTime::Type::Rational && other.m_type == FabricTime::Type::Rational)
        {
            return FabricTime(m_rep.rationalTime + other.m_rep.rationalTime);
        }
        else
        {
            return FabricTime((double)(*this) + (double)(other));
        }
    }

    inline FabricTime operator*(const FabricTime& other) const
    {
        if (m_type == FabricTime::Type::Rational && other.m_type == FabricTime::Type::Rational)
        {
            return FabricTime(m_rep.rationalTime * other.m_rep.rationalTime);
        }
        else
        {
            return FabricTime((double)(*this) * (double)(other));
        }
    }

    inline FabricTime operator/(const FabricTime& other) const
    {
        if (m_type == FabricTime::Type::Rational && other.m_type == FabricTime::Type::Rational)
        {
            return FabricTime(m_rep.rationalTime / other.m_rep.rationalTime);
        }
        else
        {
            return FabricTime((double)(*this) / (double)(other));
        }
    }

    inline FabricTime operator*(int64_t b) const
    {
        switch(m_type)
        {
            case FabricTime::Type::NaN:
            {
                return FabricTime::NaN();
            } break;
            case FabricTime::Type::Rational:
            {
                return FabricTime(m_rep.rationalTime * b);
            } break;
            case FabricTime::Type::Double:
            {
                return FabricTime(m_rep.doubleTime * b);
            } break;
        }

        return FabricTime::NaN();
    }

    inline std::string toString() const
    {
        switch(m_type)
        {
        case omni::fabric::FabricTime::Type::NaN:
            return "NaN";

        case omni::fabric::FabricTime::Type::Rational:
            return m_rep.rationalTime.toString();

        case omni::fabric::FabricTime::Type::Double:
            return std::to_string(m_rep.doubleTime);
        }

        assert(false && "unreachable");
        return "NaN";
    }

    enum class Type
    {
        NaN,
        Rational,
        Double
    };

    Type m_type;
    union Rep
    {
        inline constexpr Rep()
            : doubleTime(std::numeric_limits<double>::quiet_NaN())
        {
        }

        inline constexpr Rep(const RationalTime& r)
            : rationalTime(r)
        {
        }

        inline constexpr Rep(const double& d)
            : doubleTime(d)
        {
        }

        inline constexpr Rep(int64_t n, uint64_t d)
            : rationalTime{n, d}
        {
        }

        template<typename T>
        inline constexpr Rep(const std::initializer_list<T>& args)
            : rationalTime(args)
        {
        }

        RationalTime rationalTime;
        double doubleTime;
    } m_rep;
};
FABRIC_ENFORCE_STANDARD_LAYOUT(FabricTime);
static const FabricTime kInvalidFabricTime(kInvalidRationalTime);

inline FabricTime operator*(int64_t b, const FabricTime& time)
{
    return time * b;
}

inline double computeTheta(const double& start, const double& end, const double& time)
{
    if (start == end)
    {
        return 0.0;
    }

    if (std::isnan(start) || std::isnan(end))
    {
        CARB_LOG_WARN_ONCE(
            "StageAtTime computeTheta(): cannot divide by a denominator with a value of zero.");
        return 0.0;
    }
    else
    {
        const double a_t = (double)(start);
        const double b_t = (double)(end);

        const double c_t = (double)(time);
        return (c_t - a_t) / (b_t - a_t);
    }
}

inline double computeTheta(const FabricTime& start, const FabricTime& end, const FabricTime& time)
{
    if (start.m_type == FabricTime::Type::Rational && end.m_type == FabricTime::Type::Rational && time.m_type == FabricTime::Type::Rational)
    {
        return computeTheta(start.m_rep.rationalTime, end.m_rep.rationalTime, (RationalTime)time);
    }
    else
    {
        return computeTheta((double)start, (double)end, (double)time);
    }
}

} // namespace fabric
} // namespace omni

inline std::ostream& operator<<(std::ostream& os, const omni::fabric::FabricTime& time)
{
    switch(time.m_type)
    {
    case omni::fabric::FabricTime::Type::NaN:
        return os << "NaN";

    case omni::fabric::FabricTime::Type::Rational:
        return os << time.m_rep.rationalTime;

    case omni::fabric::FabricTime::Type::Double:
        return os << time.m_rep.doubleTime;
    }

    assert(false && "unreachable");
    return os;
}

inline bool isinf(const omni::fabric::FabricTime& time)
{
    switch(time.m_type)
    {
        case omni::fabric::FabricTime::Type::NaN:
        {
            return false;
        } break;
        case omni::fabric::FabricTime::Type::Rational:
        {
            return isinf(time.m_rep.rationalTime);
        } break;
        case omni::fabric::FabricTime::Type::Double:
        {
            return std::isinf(time.m_rep.doubleTime);
        } break;
    }

    return false;
}

inline bool isnan(const omni::fabric::FabricTime& time)
{
    switch(time.m_type)
    {
        case omni::fabric::FabricTime::Type::NaN:
        {
            return true;
        } break;
        case omni::fabric::FabricTime::Type::Rational:
        {
            return isnan(time.m_rep.rationalTime);
        } break;
        case omni::fabric::FabricTime::Type::Double:
        {
            return std::isnan(time.m_rep.doubleTime);
        } break;
    }

    return true;
}
