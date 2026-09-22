// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/CudaUtils.h>
#include <carb/Defines.h>

#include <cmath>
#include <stddef.h>
#include <type_traits>

// Helper to simplify the syntax when selecting different features for PoD types.
template <class T>
struct is_trivial
{
    template <class Q = T>
    typename std::enable_if<std::is_trivial<Q>::value, bool>::type check()
    {
        return true;
    }

    template <class Q = T>
    typename std::enable_if<!std::is_trivial<Q>::value, bool>::type check()
    {
        return false;
    }
};

// This is a templated, fixed-component-count (N), tuple class, intended to
// have data layout identical to a raw array of type T, so that data interchange
// wrappers can cast a T* to a tuple<T,N>* as appropriate, as long as they
// have ensured that there are at least N elements pointed-to.
//
// It provides a constructor for conversion between different T, but
// intentionally does not allow for conversion between different N.
// Conversion between different T is also explicit, to avoid accidental
// conversions.  Some functionality similar to std::array<T,N> is also
// provided, and the data layout should be equivalent.
//
// For example, tuple<float,3> would be a tuple of 3 floats.
//
// It also provides some convenience functions that allow for simple operations on the values
// as a single unit such as unary and binary operators.
//
namespace omni {
namespace graph {
namespace core {
template <typename T, size_t N>
class tuple
{
public:
    // Some standard types, similar to std::array and std::tuple.
    using value_type = T;
    using size_type = size_t;
    using difference_type = ptrdiff_t;
    using reference = value_type&;
    using const_reference = const value_type&;
    using pointer = value_type*;
    using const_pointer = const value_type*;
    using iterator = pointer;
    using const_iterator = const_pointer;

    // static constexpr variable to be able to refer to the tuple size from the type,
    // from outside this class definition.
    static constexpr size_t tuple_size = N;

    // Defaulted default constructor is needed for POD type,
    // but it cannot be constexpr, since it leaves v uninitialized.
    tuple() noexcept = default;
    constexpr tuple(const tuple<T, N>& that) noexcept = default;
    constexpr tuple& operator=(const tuple<T, N>& that) noexcept = default;
    // constexpr tuple(const tuple<T, N>&& that) noexcept = default;
    // constexpr tuple& operator=(const tuple<T, N>&& that) noexcept = default;

    // Construct a tuple with all components equal to value.
    explicit tuple(const T& value) noexcept
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] = value;
        }
    }

    // Type conversion constructor is explicit, to avoid unintentional conversions.
    // Conversions are done on individual components.
    template <typename OTHER_T>
    explicit tuple(const tuple<OTHER_T, N>& that) noexcept
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] = (T)(that[i]);
        }
    }

    template <typename OTHER_T, typename... Args>
    constexpr tuple(OTHER_T a, Args... args) noexcept
    {
        initHelper<0>(a, args...);
    }

    // This is a compile-time constant value
    static constexpr size_type size() noexcept
    {
        return N;
    }

    // Access a single component of this tuple.
    constexpr T& operator[](size_t i) noexcept
    {
        // Ensure that this type is a POD type if T is a POD type.
        // This check is unrelated to this operator, but the static_assert
        // must be inside some function that is likely to be called.
        static_assert(std::is_trivial<tuple<T, N>>::value == std::is_trivial<T>::value,
                      "tuple<T,N> should be a POD type iff T is a POD type.");

        CUDA_SAFE_ASSERT(i < N);
        return v[i];
    }
    constexpr const T& operator[](size_t i) const noexcept
    {
        CUDA_SAFE_ASSERT(i < N);
        return v[i];
    }

    // Get a pointer to the data of this tuple.
    constexpr T* data() noexcept
    {
        return v;
    }
    constexpr const T* data() const noexcept
    {
        return v;
    }

    // Iterator functions for compatibility with templated code that expects an iterable container.
    constexpr iterator begin() noexcept
    {
        return v;
    }
    constexpr const_iterator begin() const noexcept
    {
        return v;
    }
    constexpr const_iterator cbegin() const noexcept
    {
        return v;
    }
    constexpr iterator end() noexcept
    {
        return v + N;
    }
    constexpr const_iterator end() const noexcept
    {
        return v + N;
    }
    constexpr const_iterator cend() const noexcept
    {
        return v + N;
    }

    // Since this is a fixed-component-count tuple class,
    // it should never be empty, so this should always return false.
    // The compiler probably won't allow N to be 0, but if it ever
    // does, it would return true in that unlikely case.
    static constexpr bool empty() noexcept
    {
        return N == 0;
    }

    // Add two of the tuples together
    constexpr tuple& operator+=(const tuple<T, N>& that) noexcept
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] += that[i];
        }
        return *this;
    }
    // passing lhs by value helps optimize chained a+b+c
    friend tuple<T, N> operator+(tuple<T, N> lhs, const tuple<T, N>& rhs)
    {
        lhs += rhs;
        return lhs;
    }

    // Subtract another tuple from this one
    constexpr tuple& operator-=(const tuple<T, N>& that) noexcept
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] -= that[i];
        }
        return *this;
    }
    // passing lhs by value helps optimize chained a-b-c
    friend tuple<T, N> operator-(tuple<T, N> lhs, const tuple<T, N>& rhs)
    {
        lhs -= rhs;
        return lhs;
    }

    // Multiply all elements of the tuple by a constant
    constexpr tuple& operator*=(const T& multiplier) noexcept
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] *= multiplier;
        }
        return *this;
    }
    // passing lhs by value helps optimize chained (a*b)*c
    friend tuple<T, N> operator*(tuple<T, N> lhs, const T& multiplier)
    {
        lhs *= multiplier;
        return lhs;
    }

    // Divide all elements of the tuple by a constant
    constexpr tuple& operator/=(const T& divisor) noexcept
    {
        for (size_t i = 0; i < N; ++i)
        {
            v[i] /= divisor;
        }
        return *this;
    }
    // passing lhs by value helps optimize chained (a/b)/c
    friend tuple<T, N> operator/(tuple<T, N> lhs, const T& divisor)
    {
        lhs /= divisor;
        return lhs;
    }

    // Helper function for PoD types that computes length
    constexpr double length() const
    {
        T myLength{ (T)0 };
        for (size_t i = 0; i < N; ++i)
        {
            myLength += operator[](i) * operator[](i);
        }
        return std::sqrt(myLength);
    }

    // Helper function for PoD types that returns a normalized version of the tuple
    constexpr tuple<T, N> normalized() const
    {
        using FloatOrDouble = std::conditional_t<std::is_same<T, double>::value, double, float>;
        tuple<T, N> asNormalizedVector{ *this };
        double vectorLength = length();
        // If the length is zero then the vector is zero so it can be returned directly.
        if (vectorLength != 0.0)
        {
            for (size_t i = 0; i < N; ++i)
            {
                // This convoluted set of casts is required in order to avoid a warning for GfHalf specialization
                asNormalizedVector[i] = static_cast<T>(static_cast<FloatOrDouble>(static_cast<double>(asNormalizedVector[i]) / vectorLength));
            }
        }
        return asNormalizedVector;
    }

    // Uses the elementwise less-than in order from first to last for non-PoD types.
    // Should only be called if the elements have that operator.
    constexpr bool lessThanByElement(const tuple<T, N>& rhs) const
    {
        for (size_t i = 0; i < N; ++i)
        {
            if (operator[](i) < rhs[i])
            {
                return true;
            }
            else if (rhs[i] < operator[](i))
            {
                return false;
            }
        }
        return false;
    }
    // Algorithm for "<" that uses the vector length for comparison. Does not use the length()
    // method because for comparison purposes the expensive sqrt() is not needed.
    constexpr bool lessThanByLength(const tuple<T, N>& rhs) const
    {
        T myLength{ (T)0 };
        T rhsLength{ (T)0 };
        for (size_t i = 0; i < N; ++i)
        {
            myLength += operator[](i) * operator[](i);
            rhsLength += rhs[i] * rhs[i];
        }
        return myLength < rhsLength;
    }

    // Ordering is by vector length for PoDs and by ordering of elements in order if not
    constexpr bool operator<(const tuple<T, N>& rhs) const
    {
        return is_trivial<T>().check() ? lessThanByLength(rhs) : lessThanByElement(rhs);
    }

    // Uses the elementwise less-than in order from first to last for non-PoD types.
    // Should only be called if the elements have that operator.
    constexpr bool greaterThanByElement(const tuple<T, N>& rhs) const
    {
        for (size_t i = 0; i < N; ++i)
        {
            if (operator[](i) > rhs[i])
            {
                return true;
            }
            else if (rhs[i] > operator[](i))
            {
                return false;
            }
        }
        return false;
    }
    // Algorithm for "<" that uses the vector length for comparison
    constexpr bool greaterThanByLength(const tuple<T, N>& rhs) const
    {
        T myLength{ (T)0 };
        T rhsLength{ (T)0 };
        for (size_t i = 0; i < N; ++i)
        {
            myLength += operator[](i) * operator[](i);
            rhsLength += rhs[i] * rhs[i];
        }
        // No need to take sqrt as only the relative difference is important
        return myLength > rhsLength;
    }

    // Ordering is by vector length for PoDs and by ordering of elements in order if not
    constexpr bool operator>(const tuple<T, N>& rhs) const
    {
        return is_trivial<T>().check() ? greaterThanByLength(rhs) : greaterThanByElement(rhs);
    }

    // Equality is element-wise
    constexpr bool operator==(const tuple<T, N>& rhs) const
    {
        for (size_t i = 0; i < N; ++i)
        {
            if (operator[](i) != rhs[i])
            {
                return false;
            }
        }
        return true;
    }

    // Derivative operators, where just as efficient as separate implementation
    constexpr bool operator!=(const tuple<T, N>& rhs) const
    {
        return !operator==(rhs);
    }
    constexpr bool operator>=(const tuple<T, N>& rhs) const
    {
        return !operator<(rhs);
    }
    constexpr bool operator<=(const tuple<T, N>& rhs) const
    {
        return !operator>(rhs);
    }

private:
    T v[N];

    template <size_t i, typename OTHER_T>
    constexpr void initHelper(OTHER_T a)
    {
        static_assert(i == N - 1, "Variadic constructor of tuple<T, N> requires N arguments");
        v[i] = (T)(a);
    }
    template <size_t i, typename OTHER_T, typename... Args>
    constexpr void initHelper(OTHER_T a, Args... args)
    {
        v[i] = (T)(a);
        initHelper<i + 1>(args...);
    }
};

} // namespace core
} // namespace graph
} // namespace omni
