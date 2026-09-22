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

#include <carb/Defines.h>

#include <usdrt/gf/vec.h>

namespace omni
{
namespace math
{
namespace linalg
{

// specializing range for 1 dimensions to use float and match GfRange1(d|f)
template <typename T>
class range1
{
public:
    static const size_t dimension = 1;
    using MinMaxType = T;
    using ScalarType = T;
    using ThisType = range1<T>;

    /// Sets the range to an empty interval
    // TODO check whether this can be deprecated.
    void inline SetEmpty()
    {
        _min = std::numeric_limits<ScalarType>::max();
        _max = -std::numeric_limits<ScalarType>::max();
    }

    /// The default constructor creates an empty range.
    range1()
    {
        SetEmpty();
    }
    constexpr range1(const ThisType&) = default;

    constexpr explicit range1(ScalarType size) : _min(-size), _max(size)
    {
    }

    /// This constructor initializes the minimum and maximum points.
    constexpr range1(ScalarType min, ScalarType max) : _min(min), _max(max)
    {
    }

    /// Returns the minimum value of the range.
    ScalarType GetMin() const
    {
        return _min;
    }

    /// Returns the maximum value of the range.
    ScalarType GetMax() const
    {
        return _max;
    }

    /// Returns the size of the range.
    ScalarType GetSize() const
    {
        return _max - _min;
    }

    /// Returns the midpoint of the range, that is, 0.5*(min+max).
    /// Note: this returns zero in the case of default-constructed ranges,
    /// or ranges set via SetEmpty().
    ScalarType GetMidpoint() const
    {
        return static_cast<ScalarType>(0.5) * _min + static_cast<ScalarType>(0.5) * _max;
    }

    /// Sets the minimum value of the range.
    void SetMin(ScalarType min)
    {
        _min = min;
    }

    /// Sets the maximum value of the range.
    void SetMax(ScalarType max)
    {
        _max = max;
    }

    /// Returns whether the range is empty (max < min).
    bool IsEmpty() const
    {
        return _min > _max;
    }

    /// Modifies the range if necessary to surround the given value.
    /// \deprecated Use UnionWith() instead.
    void ExtendBy(ScalarType point)
    {
        UnionWith(point);
    }

    /// Modifies the range if necessary to surround the given range.
    /// \deprecated Use UnionWith() instead.
    void ExtendBy(const ThisType& range)
    {
        UnionWith(range);
    }

    /// Returns true if the \p point is located inside the range. As with all
    /// operations of this type, the range is assumed to include its extrema.
    bool Contains(const ScalarType& point) const
    {
        return (point >= _min && point <= _max);
    }

    /// Returns true if the \p range is located entirely inside the range. As
    /// with all operations of this type, the ranges are assumed to include
    /// their extrema.
    bool Contains(const ThisType& range) const
    {
        return Contains(range._min) && Contains(range._max);
    }

    /// Returns true if the \p point is located inside the range. As with all
    /// operations of this type, the range is assumed to include its extrema.
    /// \deprecated Use Contains() instead.
    bool IsInside(ScalarType point) const
    {
        return Contains(point);
    }

    /// Returns true if the \p range is located entirely inside the range. As
    /// with all operations of this type, the ranges are assumed to include
    /// their extrema.
    /// \deprecated Use Contains() instead.
    bool IsInside(const ThisType& range) const
    {
        return Contains(range);
    }

    /// Returns true if the \p range is located entirely outside the range. As
    /// with all operations of this type, the ranges are assumed to include
    /// their extrema.
    bool IsOutside(const ThisType& range) const
    {
        return (range._max < _min || range._min > _max);
    }

    /// Returns the smallest \c GfRange1f which contains both \p a and \p b.
    static ThisType GetUnion(const ThisType& a, const ThisType& b)
    {
        auto res = a;
        _FindMin(res._min, b._min);
        _FindMax(res._max, b._max);
        return res;
    }

    /// Extend \p this to include \p b.
    const ThisType& UnionWith(const ThisType& b)
    {
        _FindMin(_min, b._min);
        _FindMax(_max, b._max);
        return *this;
    }

    /// Extend \p this to include \p b.
    const ThisType& UnionWith(const ScalarType& b)
    {
        _FindMin(_min, b);
        _FindMax(_max, b);
        return *this;
    }

    /// Returns the smallest \c GfRange1f which contains both \p a and \p b
    /// \deprecated Use GetUnion() instead.
    static ThisType Union(const ThisType& a, const ThisType& b)
    {
        return GetUnion(a, b);
    }

    /// Extend \p this to include \p b.
    /// \deprecated Use UnionWith() instead.
    const ThisType& Union(const ThisType& b)
    {
        return UnionWith(b);
    }

    /// Extend \p this to include \p b.
    /// \deprecated Use UnionWith() instead.
    const ThisType& Union(ScalarType b)
    {
        return UnionWith(b);
    }

    /// Returns a \c GfRange1f that describes the intersection of \p a and \p b.
    static ThisType GetIntersection(const ThisType& a, const ThisType& b)
    {
        auto res = a;
        _FindMax(res._min, b._min);
        _FindMin(res._max, b._max);
        return res;
    }

    /// Returns a \c GfRange1f that describes the intersection of \p a and \p b.
    /// \deprecated Use GetIntersection() instead.
    static ThisType Intersection(const ThisType& a, const ThisType& b)
    {
        return GetIntersection(a, b);
    }

    /// Modifies this range to hold its intersection with \p b and returns the
    /// result
    const ThisType& IntersectWith(const ThisType& b)
    {
        _FindMax(_min, b._min);
        _FindMin(_max, b._max);
        return *this;
    }

    /// Modifies this range to hold its intersection with \p b and returns the
    /// result.
    /// \deprecated Use IntersectWith() instead.
    const ThisType& Intersection(const ThisType& b)
    {
        return IntersectWith(b);
    }

    /// unary sum.
    ThisType operator+=(const ThisType& b)
    {
        _min += b._min;
        _max += b._max;
        return *this;
    }

    /// unary difference.
    ThisType operator-=(const ThisType& b)
    {
        _min -= b._max;
        _max -= b._min;
        return *this;
    }

    /// unary multiply.
    ThisType operator*=(double m)
    {
        if (m > 0)
        {
            _min *= m;
            _max *= m;
        }
        else
        {
            float tmp = _min;
            _min = _max * m;
            _max = tmp * m;
        }
        return *this;
    }

    /// unary division.
    ThisType operator/=(double m)
    {
        return *this *= (1.0 / m);
    }

    /// binary sum.
    ThisType operator+(const ThisType& b) const
    {
        return ThisType(_min + b._min, _max + b._max);
    }


    /// binary difference.
    ThisType operator-(const ThisType& b) const
    {
        return ThisType(_min - b._max, _max - b._min);
    }

    /// scalar multiply.
    friend ThisType operator*(double m, const ThisType& r)
    {
        return (m > 0 ? ThisType(r._min * m, r._max * m) : ThisType(r._max * m, r._min * m));
    }

    /// scalar multiply.
    friend ThisType operator*(const ThisType& r, double m)
    {
        return (m > 0 ? ThisType(r._min * m, r._max * m) : ThisType(r._max * m, r._min * m));
    }

    /// scalar divide.
    friend ThisType operator/(const ThisType& r, double m)
    {
        return r * (1.0 / m);
    }

    inline bool operator==(const ThisType& other) const
    {
        return _min == static_cast<ScalarType>(other.GetMin()) && _max == static_cast<ScalarType>(other.GetMax());
    }
    inline bool operator!=(const ThisType& other) const
    {
        return !(*this == other);
    }

    /// Compute the squared distance from a point to the range.
    double GetDistanceSquared(ScalarType p) const
    {
        double dist = 0.0;

        if (p < _min)
        {
            // p is left of box
            dist += GfSqr(_min - p);
        }
        else if (p > _max)
        {
            // p is right of box
            dist += GfSqr(p - _max);
        }

        return dist;
    }

private:
    /// Minimum and maximum points.
    ScalarType _min, _max;

    /// Extends minimum point if necessary to contain given point.
    static void _FindMin(ScalarType& dest, ScalarType point)
    {
        if (point < dest)
        {
            dest = point;
        }
    }

    /// Extends maximum point if necessary to contain given point.
    static void _FindMax(ScalarType& dest, ScalarType point)
    {
        if (point > dest)
        {
            dest = point;
        }
    }
};

template <typename T>
class range2
{
public:
    static const size_t dimension = 2;
    using ScalarType = T;
    using MinMaxType = omni::math::linalg::vec2<T>;
    using ThisType = range2<T>;

    range2()
    {
        SetEmpty();
    }
    constexpr range2(const ThisType&) = default;

    constexpr explicit range2(ScalarType size) : _min(-size), _max(size)
    {
    }

    /// Sets the range to an empty interval
    // TODO check whether this can be deprecated.
    constexpr void inline SetEmpty()
    {
        _min = MinMaxType(std::numeric_limits<ScalarType>::max());
        _max = MinMaxType(-std::numeric_limits<ScalarType>::max());
    }

    /// This constructor initializes the minimum and maximum points.
    constexpr range2(const MinMaxType& min, const MinMaxType& max) : _min(min), _max(max)
    {
    }

    /// Returns the minimum value of the range.
    const MinMaxType& GetMin() const
    {
        return _min;
    }

    /// Returns the maximum value of the range.
    const MinMaxType& GetMax() const
    {
        return _max;
    }

    /// Returns the size of the range.
    MinMaxType GetSize() const
    {
        return _max - _min;
    }

    /// Returns the midpoint of the range, that is, 0.5*(min+max).
    /// Note: this returns zero in the case of default-constructed ranges,
    /// or ranges set via SetEmpty().
    MinMaxType GetMidpoint() const
    {
        return static_cast<ScalarType>(0.5) * _min + static_cast<ScalarType>(0.5) * _max;
    }

    /// Sets the minimum value of the range.
    void SetMin(const MinMaxType& min)
    {
        _min = min;
    }

    /// Sets the maximum value of the range.
    void SetMax(const MinMaxType& max)
    {
        _max = max;
    }

    /// Returns whether the range is empty (max < min).
    bool IsEmpty() const
    {
        return _min[0] > _max[0] || _min[1] > _max[1];
    }

    /// Modifies the range if necessary to surround the given value.
    /// \deprecated Use UnionWith() instead.
    void ExtendBy(const MinMaxType& point)
    {
        UnionWith(point);
    }

    /// Modifies the range if necessary to surround the given range.
    /// \deprecated Use UnionWith() instead.
    void ExtendBy(const ThisType& range)
    {
        UnionWith(range);
    }

    /// Returns true if the \p point is located inside the range. As with all
    /// operations of this type, the range is assumed to include its extrema.
    bool Contains(const MinMaxType& point) const
    {
        return (point[0] >= _min[0] && point[0] <= _max[0] && point[1] >= _min[1] && point[1] <= _max[1]);
    }

    /// Returns true if the \p range is located entirely inside the range. As
    /// with all operations of this type, the ranges are assumed to include
    /// their extrema.
    bool Contains(const ThisType& range) const
    {
        return Contains(range._min) && Contains(range._max);
    }

    /// Returns true if the \p point is located inside the range. As with all
    /// operations of this type, the range is assumed to include its extrema.
    /// \deprecated Use Contains() instead.
    bool IsInside(const MinMaxType& point) const
    {
        return Contains(point);
    }

    /// Returns true if the \p range is located entirely inside the range. As
    /// with all operations of this type, the ranges are assumed to include
    /// their extrema.
    /// \deprecated Use Contains() instead.
    bool IsInside(const ThisType& range) const
    {
        return Contains(range);
    }

    /// Returns true if the \p range is located entirely outside the range. As
    /// with all operations of this type, the ranges are assumed to include
    /// their extrema.
    bool IsOutside(const ThisType& range) const
    {
        return ((range._max[0] < _min[0] || range._min[0] > _max[0]) ||
                (range._max[1] < _min[1] || range._min[1] > _max[1]));
    }

    /// Returns the smallest \c ThisType which contains both \p a and \p b.
    static ThisType GetUnion(const ThisType& a, const ThisType& b)
    {
        auto res = a;
        _FindMin(res._min, b._min);
        _FindMax(res._max, b._max);
        return res;
    }

    /// Extend \p this to include \p b.
    const ThisType& UnionWith(const ThisType& b)
    {
        _FindMin(_min, b._min);
        _FindMax(_max, b._max);
        return *this;
    }

    /// Extend \p this to include \p b.
    const ThisType& UnionWith(const MinMaxType& b)
    {
        _FindMin(_min, b);
        _FindMax(_max, b);
        return *this;
    }

    /// Returns the smallest \c ThisType which contains both \p a and \p b
    /// \deprecated Use GetUnion() instead.
    static ThisType Union(const ThisType& a, const ThisType& b)
    {
        return GetUnion(a, b);
    }

    /// Extend \p this to include \p b.
    /// \deprecated Use UnionWith() instead.
    const ThisType& Union(const ThisType& b)
    {
        return UnionWith(b);
    }

    /// Extend \p this to include \p b.
    /// \deprecated Use UnionWith() instead.
    const ThisType& Union(const MinMaxType& b)
    {
        return UnionWith(b);
    }

    /// Returns a \c ThisType that describes the intersection of \p a and \p b.
    static ThisType GetIntersection(const ThisType& a, const ThisType& b)
    {
        auto res = a;
        _FindMax(res._min, b._min);
        _FindMin(res._max, b._max);
        return res;
    }

    /// Returns a \c ThisType that describes the intersection of \p a and \p b.
    /// \deprecated Use GetIntersection() instead.
    static ThisType Intersection(const ThisType& a, const ThisType& b)
    {
        return GetIntersection(a, b);
    }

    /// Modifies this range to hold its intersection with \p b and returns the
    /// result
    const ThisType& IntersectWith(const ThisType& b)
    {
        _FindMax(_min, b._min);
        _FindMin(_max, b._max);
        return *this;
    }

    /// Modifies this range to hold its intersection with \p b and returns the
    /// result.
    /// \deprecated Use IntersectWith() instead.
    const ThisType& Intersection(const ThisType& b)
    {
        return IntersectWith(b);
    }

    /// unary sum.
    ThisType& operator+=(const ThisType& b)
    {
        _min += b._min;
        _max += b._max;
        return *this;
    }

    /// unary difference.
    ThisType& operator-=(const ThisType& b)
    {
        _min -= b._max;
        _max -= b._min;
        return *this;
    }

    /// unary multiply.
    ThisType& operator*=(double m)
    {
        if (m > 0)
        {
            _min *= m;
            _max *= m;
        }
        else
        {
            auto tmp = _min;
            _min = _max * m;
            _max = tmp * m;
        }
        return *this;
    }

    /// unary division.
    ThisType& operator/=(double m)
    {
        return *this *= (1.0 / m);
    }

    /// binary sum.
    ThisType operator+(const ThisType& b) const
    {
        return ThisType(_min + b._min, _max + b._max);
    }


    /// binary difference.
    ThisType operator-(const ThisType& b) const
    {
        return ThisType(_min - b._max, _max - b._min);
    }

    /// scalar multiply.
    friend ThisType operator*(double m, const ThisType& r)
    {
        return (m > 0 ? ThisType(r._min * m, r._max * m) : ThisType(r._max * m, r._min * m));
    }

    /// scalar multiply.
    friend ThisType operator*(const ThisType& r, double m)
    {
        return (m > 0 ? ThisType(r._min * m, r._max * m) : ThisType(r._max * m, r._min * m));
    }

    /// scalar divide.
    friend ThisType operator/(const ThisType& r, double m)
    {
        return r * (1.0 / m);
    }

    /// The min and max points must match exactly for equality.
    bool operator==(const ThisType& b) const
    {
        return (_min == b._min && _max == b._max);
    }

    bool operator!=(const ThisType& b) const
    {
        return !(*this == b);
    }

    /// Compute the squared distance from a point to the range.
    double GetDistanceSquared(const MinMaxType& p) const
    {
        double dist = 0.0;

        if (p[0] < _min[0])
        {
            // p is left of box
            dist += GfSqr(_min[0] - p[0]);
        }
        else if (p[0] > _max[0])
        {
            // p is right of box
            dist += GfSqr(p[0] - _max[0]);
        }
        if (p[1] < _min[1])
        {
            // p is front of box
            dist += GfSqr(_min[1] - p[1]);
        }
        else if (p[1] > _max[1])
        {
            // p is back of box
            dist += GfSqr(p[1] - _max[1]);
        }

        return dist;
    }

    /// Returns the ith corner of the range, in the following order:
    /// SW, SE, NW, NE.

    MinMaxType GetCorner(size_t i) const
    {
        if (i > 3)
        {
            return _min;
        }

        return MinMaxType((i & 1 ? _max : _min)[0], (i & 2 ? _max : _min)[1]);
    }

    /// Returns the ith quadrant of the range, in the following order:
    /// SW, SE, NW, NE.

    ThisType GetQuadrant(size_t i) const
    {
        if (i > 3)
        {
            return {};
        }

        auto a = GetCorner(i);
        auto b = .5 * (_min + _max);

        return ThisType(
            MinMaxType(GfMin(a[0], b[0]), GfMin(a[1], b[1])), MinMaxType(GfMax(a[0], b[0]), GfMax(a[1], b[1])));
    }

    /// The unit square.
    static constexpr ThisType UnitSquare()
    {
        return ThisType(MinMaxType(0), MinMaxType(1));
    }


private:
    /// Minimum and maximum points.
    MinMaxType _min, _max;

    /// Extends minimum point if necessary to contain given point.
    static void _FindMin(MinMaxType& dest, const MinMaxType& point)
    {
        if (point[0] < dest[0])
        {
            dest[0] = point[0];
        }
        if (point[1] < dest[1])
        {
            dest[1] = point[1];
        }
    }

    /// Extends maximum point if necessary to contain given point.
    static void _FindMax(MinMaxType& dest, const MinMaxType& point)
    {
        if (point[0] > dest[0])
        {
            dest[0] = point[0];
        }
        if (point[1] > dest[1])
        {
            dest[1] = point[1];
        }
    }
};

template <typename T>
class range3
{
public:
    static const size_t dimension = 3;
    using ScalarType = T;
    using MinMaxType = omni::math::linalg::vec3<T>;
    using ThisType = range3<T>;

    range3()
    {
        SetEmpty();
    }
    constexpr range3(const ThisType&) = default;

    constexpr explicit range3(ScalarType size) : _min(-size), _max(size)
    {
    }

    /// Sets the range to an empty interval
    // TODO check whether this can be deprecated.
    constexpr void inline SetEmpty()
    {
        _min = MinMaxType(std::numeric_limits<ScalarType>::max());
        _max = MinMaxType(-std::numeric_limits<ScalarType>::max());
    }

    /// This constructor initializes the minimum and maximum points.
    constexpr range3(const MinMaxType& min, const MinMaxType& max) : _min(min), _max(max)
    {
    }

    /// Returns the minimum value of the range.
    const MinMaxType& GetMin() const
    {
        return _min;
    }

    /// Returns the maximum value of the range.
    const MinMaxType& GetMax() const
    {
        return _max;
    }

    /// Returns the size of the range.
    MinMaxType GetSize() const
    {
        return _max - _min;
    }

    /// Returns the midpoint of the range, that is, 0.5*(min+max).
    /// Note: this returns zero in the case of default-constructed ranges,
    /// or ranges set via SetEmpty().
    MinMaxType GetMidpoint() const
    {
        return static_cast<ScalarType>(0.5) * _min + static_cast<ScalarType>(0.5) * _max;
    }

    /// Sets the minimum value of the range.
    void SetMin(const MinMaxType& min)
    {
        _min = min;
    }

    /// Sets the maximum value of the range.
    void SetMax(const MinMaxType& max)
    {
        _max = max;
    }

    /// Returns whether the range is empty (max < min).
    bool IsEmpty() const
    {
        return _min[0] > _max[0] || _min[1] > _max[1] || _min[2] > _max[2];
    }

    /// Modifies the range if necessary to surround the given value.
    /// \deprecated Use UnionWith() instead.
    void ExtendBy(const MinMaxType& point)
    {
        UnionWith(point);
    }

    /// Modifies the range if necessary to surround the given range.
    /// \deprecated Use UnionWith() instead.
    void ExtendBy(const ThisType& range)
    {
        UnionWith(range);
    }

    /// Returns true if the \p point is located inside the range. As with all
    /// operations of this type, the range is assumed to include its extrema.
    bool Contains(const MinMaxType& point) const
    {
        return (point[0] >= _min[0] && point[0] <= _max[0] && point[1] >= _min[1] && point[1] <= _max[1] &&
                point[2] >= _min[2] && point[2] <= _max[2]);
    }

    /// Returns true if the \p range is located entirely inside the range. As
    /// with all operations of this type, the ranges are assumed to include
    /// their extrema.
    bool Contains(const ThisType& range) const
    {
        return Contains(range._min) && Contains(range._max);
    }

    /// Returns true if the \p point is located inside the range. As with all
    /// operations of this type, the range is assumed to include its extrema.
    /// \deprecated Use Contains() instead.
    bool IsInside(const MinMaxType& point) const
    {
        return Contains(point);
    }

    /// Returns true if the \p range is located entirely inside the range. As
    /// with all operations of this type, the ranges are assumed to include
    /// their extrema.
    /// \deprecated Use Contains() instead.
    bool IsInside(const ThisType& range) const
    {
        return Contains(range);
    }

    /// Returns true if the \p range is located entirely outside the range. As
    /// with all operations of this type, the ranges are assumed to include
    /// their extrema.
    bool IsOutside(const ThisType& range) const
    {
        return ((range._max[0] < _min[0] || range._min[0] > _max[0]) ||
                (range._max[1] < _min[1] || range._min[1] > _max[1]) ||
                (range._max[2] < _min[2] || range._min[2] > _max[2]));
    }

    /// Returns the smallest \c ThisType which contains both \p a and \p b.
    static ThisType GetUnion(const ThisType& a, const ThisType& b)
    {
        ThisType res = a;
        _FindMin(res._min, b._min);
        _FindMax(res._max, b._max);
        return res;
    }

    /// Extend \p this to include \p b.
    const ThisType& UnionWith(const ThisType& b)
    {
        _FindMin(_min, b._min);
        _FindMax(_max, b._max);
        return *this;
    }

    /// Extend \p this to include \p b.
    const ThisType& UnionWith(const MinMaxType& b)
    {
        _FindMin(_min, b);
        _FindMax(_max, b);
        return *this;
    }

    /// Returns the smallest \c ThisType which contains both \p a and \p b
    /// \deprecated Use GetUnion() instead.
    static ThisType Union(const ThisType& a, const ThisType& b)
    {
        return GetUnion(a, b);
    }

    /// Extend \p this to include \p b.
    /// \deprecated Use UnionWith() instead.
    const ThisType& Union(const ThisType& b)
    {
        return UnionWith(b);
    }

    /// Extend \p this to include \p b.
    /// \deprecated Use UnionWith() instead.
    const ThisType& Union(const MinMaxType& b)
    {
        return UnionWith(b);
    }

    /// Returns a \c ThisType that describes the intersection of \p a and \p b.
    static ThisType GetIntersection(const ThisType& a, const ThisType& b)
    {
        ThisType res = a;
        _FindMax(res._min, b._min);
        _FindMin(res._max, b._max);
        return res;
    }

    /// Returns a \c ThisType that describes the intersection of \p a and \p b.
    /// \deprecated Use GetIntersection() instead.
    static ThisType Intersection(const ThisType& a, const ThisType& b)
    {
        return GetIntersection(a, b);
    }

    /// Modifies this range to hold its intersection with \p b and returns the
    /// result
    const ThisType& IntersectWith(const ThisType& b)
    {
        _FindMax(_min, b._min);
        _FindMin(_max, b._max);
        return *this;
    }

    /// Modifies this range to hold its intersection with \p b and returns the
    /// result.
    /// \deprecated Use IntersectWith() instead.
    const ThisType& Intersection(const ThisType& b)
    {
        return IntersectWith(b);
    }

    /// unary sum.
    ThisType& operator+=(const ThisType& b)
    {
        _min += b._min;
        _max += b._max;
        return *this;
    }

    /// unary difference.
    ThisType& operator-=(const ThisType& b)
    {
        _min -= b._max;
        _max -= b._min;
        return *this;
    }

    /// unary multiply.
    ThisType& operator*=(double m)
    {
        if (m > 0)
        {
            _min *= m;
            _max *= m;
        }
        else
        {
            MinMaxType tmp = _min;
            _min = _max * m;
            _max = tmp * m;
        }
        return *this;
    }

    /// unary division.
    ThisType& operator/=(double m)
    {
        return *this *= (1.0 / m);
    }

    /// binary sum.
    ThisType operator+(const ThisType& b) const
    {
        return ThisType(_min + b._min, _max + b._max);
    }


    /// binary difference.
    ThisType operator-(const ThisType& b) const
    {
        return ThisType(_min - b._max, _max - b._min);
    }

    /// scalar multiply.
    friend ThisType operator*(double m, const ThisType& r)
    {
        return (m > 0 ? ThisType(r._min * m, r._max * m) : ThisType(r._max * m, r._min * m));
    }

    /// scalar multiply.
    friend ThisType operator*(const ThisType& r, double m)
    {
        return (m > 0 ? ThisType(r._min * m, r._max * m) : ThisType(r._max * m, r._min * m));
    }

    /// scalar divide.
    friend ThisType operator/(const ThisType& r, double m)
    {
        return r * (1.0 / m);
    }

    /// The min and max points must match exactly for equality.
    bool operator==(const ThisType& b) const
    {
        return (_min == b._min && _max == b._max);
    }

    bool operator!=(const ThisType& b) const
    {
        return !(*this == b);
    }

    /// Compute the squared distance from a point to the range.

    double GetDistanceSquared(const MinMaxType& p) const
    {
        double dist = 0.0;

        if (p[0] < _min[0])
        {
            // p is left of box
            dist += GfSqr(_min[0] - p[0]);
        }
        else if (p[0] > _max[0])
        {
            // p is right of box
            dist += GfSqr(p[0] - _max[0]);
        }
        if (p[1] < _min[1])
        {
            // p is front of box
            dist += GfSqr(_min[1] - p[1]);
        }
        else if (p[1] > _max[1])
        {
            // p is back of box
            dist += GfSqr(p[1] - _max[1]);
        }
        if (p[2] < _min[2])
        {
            // p is below of box
            dist += GfSqr(_min[2] - p[2]);
        }
        else if (p[2] > _max[2])
        {
            // p is above of box
            dist += GfSqr(p[2] - _max[2]);
        }

        return dist;
    }

    /// Returns the ith corner of the range, in the following order:
    /// LDB, RDB, LUB, RUB, LDF, RDF, LUF, RUF. Where L/R is left/right,
    /// D/U is down/up, and B/F is back/front.

    MinMaxType GetCorner(size_t i) const
    {
        if (i > 7)
        {
            return _min;
        }
        return MinMaxType((i & 1 ? _max : _min)[0], (i & 2 ? _max : _min)[1], (i & 4 ? _max : _min)[2]);
    }

    /// Returns the ith octant of the range, in the following order:
    /// LDB, RDB, LUB, RUB, LDF, RDF, LUF, RUF. Where L/R is left/right,
    /// D/U is down/up, and B/F is back/front.

    ThisType GetOctant(size_t i) const
    {
        if (i > 7)
        {
            return {};
        }

        auto a = GetCorner(i);
        auto b = .5 * (_min + _max);

        return ThisType(MinMaxType(GfMin(a[0], b[0]), GfMin(a[1], b[1]), GfMin(a[2], b[2])),
                        MinMaxType(GfMax(a[0], b[0]), GfMax(a[1], b[1]), GfMax(a[2], b[2])));
    }

    /// The unit cube.
    static constexpr const ThisType UnitCube()
    {
        return ThisType(MinMaxType(0), MinMaxType(1));
    }

private:
    /// Minimum and maximum points.
    MinMaxType _min, _max;

    /// Extends minimum point if necessary to contain given point.
    static void _FindMin(MinMaxType& dest, const MinMaxType& point)
    {
        if (point[0] < dest[0])
        {
            dest[0] = point[0];
        }
        if (point[1] < dest[1])
        {
            dest[1] = point[1];
        }
        if (point[2] < dest[2])
        {
            dest[2] = point[2];
        }
    }

    /// Extends maximum point if necessary to contain given point.
    static void _FindMax(MinMaxType& dest, const MinMaxType& point)
    {
        if (point[0] > dest[0])
        {
            dest[0] = point[0];
        }
        if (point[1] > dest[1])
        {
            dest[1] = point[1];
        }
        if (point[2] > dest[2])
        {
            dest[2] = point[2];
        }
    }
};

}
}
}

namespace usdrt
{

using GfRange1d = omni::math::linalg::range1<double>;
using GfRange1f = omni::math::linalg::range1<float>;
using GfRange2d = omni::math::linalg::range2<double>;
using GfRange2f = omni::math::linalg::range2<float>;
using GfRange3d = omni::math::linalg::range3<double>;
using GfRange3f = omni::math::linalg::range3<float>;

template <>
struct GfIsGfRange<GfRange1d>
{
    static const bool value = true;
};

template <>
struct GfIsGfRange<GfRange1f>
{
    static const bool value = true;
};

template <>
struct GfIsGfRange<GfRange2d>
{
    static const bool value = true;
};

template <>
struct GfIsGfRange<GfRange2f>
{
    static const bool value = true;
};

template <>
struct GfIsGfRange<GfRange3d>
{
    static const bool value = true;
};


template <>
struct GfIsGfRange<GfRange3f>
{
    static const bool value = true;
};

}
