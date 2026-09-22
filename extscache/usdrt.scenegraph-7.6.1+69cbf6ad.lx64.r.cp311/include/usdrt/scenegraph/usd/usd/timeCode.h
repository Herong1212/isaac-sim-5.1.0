// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file usd/timeCode.h
//!
//! @brief UsdTimeCode represents a time value as a double.

#include <cmath>
#include <limits>

namespace usdrt
{
//! @class UsdTimeCode
//!
//! Represent a time value as a double.
//!
//! This is a generic time measurement representing time sampled data.
class UsdTimeCode
{
public:
    //! Construct with optional time value.
    //! @param t time value as `double`.
    constexpr UsdTimeCode(double t = 0.0) noexcept : m_value(t)
    {
    }

    //! Produce a UsdTimeCode representing the lowest/earliest possible
    //! timeCode.
    static UsdTimeCode EarliestTime()
    {
        return UsdTimeCode(std::numeric_limits<double>::lowest());
    }

    //! Produce a UsdTimeCode representing 'default'.
    ///
    /// @note In inequality comparisons, Default() is considered less than any
    /// numeric TimeCode, including EarliestTime().
    static UsdTimeCode Default()
    {
        return UsdTimeCode(std::numeric_limits<double>::quiet_NaN());
    }

    //! @returns Return true if this time represents the lowest/earliest possible
    //! timeCode, false otherwise.
    bool IsEarliestTime() const
    {
        return IsNumeric() && (m_value == std::numeric_limits<double>::lowest());
    }

    //! @returns Return true if this time represents the 'default' sentinel value, false
    //! otherwise.  This is equivalent to !IsNumeric().
    bool IsDefault() const
    {
        return std::isnan(m_value);
    }

    //! @returns Return true if this time represents a numeric value, false otherwise.
    //! This is equivalent to !IsDefault().
    bool IsNumeric() const
    {
        return !IsDefault();
    }

    //! Get the numeric value for this time.
    //! @returns Return the numeric value for this time.  If this time @a IsDefault(),
    /// return a quiet NaN value.
    double GetValue() const
    {
        return m_value;
    }

#ifndef DOXYGEN_BUILD
    friend bool operator==(const UsdTimeCode& lhs, const UsdTimeCode& rhs)
    {
        return lhs.IsDefault() == rhs.IsDefault() && (lhs.IsDefault() || (lhs.GetValue() == rhs.GetValue()));
    }

    friend bool operator!=(const UsdTimeCode& lhs, const UsdTimeCode& rhs)
    {
        return !(lhs == rhs);
    }

    friend bool operator<(const UsdTimeCode& lhs, const UsdTimeCode& rhs)
    {
        return (lhs.IsDefault() && rhs.IsNumeric()) ||
               (lhs.IsNumeric() && rhs.IsNumeric() && lhs.GetValue() < rhs.GetValue());
    }

    friend bool operator>=(const UsdTimeCode& lhs, const UsdTimeCode& rhs)
    {
        return !(lhs < rhs);
    }

    friend bool operator<=(const UsdTimeCode& lhs, const UsdTimeCode& rhs)
    {
        return lhs.IsDefault() || (rhs.IsNumeric() && lhs.GetValue() <= rhs.GetValue());
    }

    friend bool operator>(const UsdTimeCode& lhs, const UsdTimeCode& rhs)
    {
        return !(lhs <= rhs);
    }
#endif // DOXYGEN_BUILD

private:
    double m_value;
};

} // namespace usdrt
