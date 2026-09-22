// Copyright (c) 2021-2022, NVIDIA CORPORATION. All rights reserved.
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

#include <carb/Defines.h>

#include <usdrt/gf/vec.h>

#include <float.h>

namespace usdrt
{

struct GfRect2i
{
public:
    // In order to make GfRect2i a POD type we need to give up on non-default constructor
    // pxr::GfRect2i initializes to empty, so we're not 100% compatible here!
    GfRect2i() = default;
    constexpr GfRect2i(const GfRect2i&) = default;

    /// Helper typedef.
    using MinMaxType = GfVec2i;

    static const size_t dimension = MinMaxType::dimension;
    using ScalarType = MinMaxType::ScalarType;

    /// Constructs a rectangle with \p min and \p max corners.
    constexpr GfRect2i(const GfVec2i& min, const GfVec2i& max) : _min(min), _max(max)
    {
    }

    /// Constructs a rectangle with \p min corner and the indicated \p width
    /// and \p height.
    GfRect2i(const GfVec2i& min, int width, int height) : _min(min), _max(min + GfVec2i(width - 1, height - 1))
    {
    }

    /// Returns true if the rectangle is a null rectangle.
    ///
    /// A null rectangle has both the width and the height set to 0, that is
    /// \code
    ///     GetMaxX() == GetMinX() - 1
    /// \endcode
    /// and
    /// \code
    ///     GetMaxY() == GetMinY() - 1
    /// \endcode
    /// Remember that if \c GetMinX() and \c GetMaxX() return the same value
    /// then the rectangle has width 1, and similarly for the height.
    ///
    /// A null rectangle is both empty, and not valid.
    bool IsNull() const
    {
        return GetWidth() == 0 && GetHeight() == 0;
    }

    /// Returns true if the rectangle is empty.
    ///
    /// An empty rectangle has one or both of its min coordinates strictly
    /// greater than the corresponding max coordinate.
    ///
    /// An empty rectangle is not valid.
    bool IsEmpty() const
    {
        return GetWidth() <= 0 || GetHeight() <= 0;
    }

    /// Return true if the rectangle is valid (equivalently, not empty).
    bool IsValid() const
    {
        return !IsEmpty();
    }

    /// Returns a normalized rectangle, i.e. one that has a non-negative width
    /// and height.
    ///
    /// \c GetNormalized() swaps the min and max x-coordinates to
    /// ensure a non-negative width, and similarly for the
    /// y-coordinates.
    GfRect2i GetNormalized() const
    {
        GfVec2i min, max;

        if (_max[0] < _min[0])
        {
            min[0] = _max[0];
            max[0] = _min[0];
        }
        else
        {
            min[0] = _min[0];
            max[0] = _max[0];
        }

        if (_max[1] < _min[1])
        {
            min[1] = _max[1];
            max[1] = _min[1];
        }
        else
        {
            min[1] = _min[1];
            max[1] = _max[1];
        }

        return GfRect2i(min, max);
    }

    /// Returns the min corner of the rectangle.
    const GfVec2i& GetMin() const
    {
        return _min;
    }

    /// Returns the max corner of the rectangle.
    const GfVec2i& GetMax() const
    {
        return _max;
    }

    /// Return the X value of min corner.
    ///
    int GetMinX() const
    {
        return _min[0];
    }

    /// Set the X value of the min corner.
    ///
    void SetMinX(int x)
    {
        _min[0] = x;
    }

    /// Return the X value of the max corner.
    ///
    int GetMaxX() const
    {
        return _max[0];
    }

    /// Set the X value of the max corner
    void SetMaxX(int x)
    {
        _max[0] = x;
    }

    /// Return the Y value of the min corner
    ///
    int GetMinY() const
    {
        return _min[1];
    }

    /// Set the Y value of the min corner.
    ///
    void SetMinY(int y)
    {
        _min[1] = y;
    }

    /// Return the Y value of the max corner
    int GetMaxY() const
    {
        return _max[1];
    }

    /// Set the Y value of the max corner
    void SetMaxY(int y)
    {
        _max[1] = y;
    }

    /// Sets the min corner of the rectangle.
    void SetMin(const GfVec2i& min)
    {
        _min = min;
    }

    /// Sets the max corner of the rectangle.
    void SetMax(const GfVec2i& max)
    {
        _max = max;
    }

    /// Returns the center point of the rectangle.
    GfVec2i GetCenter() const
    {
        return (_min + _max) / 2;
    }

    /// Move the rectangle by \p displ.
    void Translate(const GfVec2i& displacement)
    {
        _min += displacement;
        _max += displacement;
    }

    /// Return the area of the rectangle.
    unsigned long GetArea() const
    {
        return (unsigned long)GetWidth() * (unsigned long)GetHeight();
    }

    /// Returns the size of the rectangle as a vector (width,height).
    GfVec2i GetSize() const
    {
        return GfVec2i(GetWidth(), GetHeight());
    }

    /// Returns the width of the rectangle.
    ///
    /// \note If the min and max x-coordinates are coincident, the width is
    /// one.
    int GetWidth() const
    {
        return (_max[0] - _min[0]) + 1;
    }

    /// Returns the height of the rectangle.
    ///
    /// \note If the min and max y-coordinates are coincident, the height is
    /// one.
    int GetHeight() const
    {
        return (_max[1] - _min[1]) + 1;
    }

    /// Computes the intersection of two rectangles.
    GfRect2i GetIntersection(const GfRect2i& that) const
    {
        if (IsEmpty())
            return *this;
        else if (that.IsEmpty())
            return that;
        else
            return GfRect2i(GfVec2i(GfMax(_min[0], that._min[0]), GfMax(_min[1], that._min[1])),
                            GfVec2i(GfMin(_max[0], that._max[0]), GfMin(_max[1], that._max[1])));
    }

    /// Computes the intersection of two rectangles.
    /// \deprecated Use GetIntersection() instead
    GfRect2i Intersect(const GfRect2i& that) const
    {
        return GetIntersection(that);
    }

    /// Computes the union of two rectangles.
    GfRect2i GetUnion(const GfRect2i& that) const
    {
        if (IsEmpty())
            return that;
        else if (that.IsEmpty())
            return *this;
        else
            return GfRect2i(GfVec2i(GfMin(_min[0], that._min[0]), GfMin(_min[1], that._min[1])),
                            GfVec2i(GfMax(_max[0], that._max[0]), GfMax(_max[1], that._max[1])));
    }

    /// Computes the union of two rectangles
    /// \deprecated Use GetUnion() instead.
    GfRect2i Union(const GfRect2i& that) const
    {
        return GetUnion(that);
    }

    /// Returns true if the specified point in the rectangle.
    bool Contains(const GfVec2i& p) const
    {
        return ((p[0] >= _min[0]) && (p[0] <= _max[0]) && (p[1] >= _min[1]) && (p[1] <= _max[1]));
    }

    /// Returns true if \p r1 and \p r2 are equal.
    friend bool operator==(const GfRect2i& r1, const GfRect2i& r2)
    {
        return r1._min == r2._min && r1._max == r2._max;
    }

    /// Returns true if \p r1 and \p r2 are different.
    friend bool operator!=(const GfRect2i& r1, const GfRect2i& r2)
    {
        return !(r1 == r2);
    }

    /// Computes the union of two rectangles.
    /// \see GetUnion()
    GfRect2i operator+=(const GfRect2i& that)
    {
        *this = GetUnion(that);
        return *this;
    }

    friend GfRect2i operator+(const GfRect2i r1, const GfRect2i& r2)
    {
        GfRect2i tmp(r1);
        tmp += r2;
        return tmp;
    }

private:
    GfVec2i _min = { 0, 0 };
    GfVec2i _max = { -1, -1 };
};

}
