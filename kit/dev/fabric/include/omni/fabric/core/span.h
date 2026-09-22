// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

namespace omni
{
namespace fabric
{

template <typename T>
struct SpanOf
{
    T* elements;
    size_t count;

    inline T* begin() const
    {
        return elements;
    }

    inline T* end() const
    {
        return elements ? elements + count : nullptr;
    }

    inline bool empty() const
    {
        return (elements==nullptr) || (count==0);
    }

    inline bool inconsistent() const
    {
        return (elements && !count) || (!elements && count);
    }

    inline bool isValid() const
    {
        return elements && count;
    }
};

template <typename T>
inline SpanOf<T> make_spanOf(T* addr, size_t n)
{
    return SpanOf<T>{addr, n};
}

template <typename T>
inline SpanOf<const T> make_const_spanOf(T* addr, size_t n)
{
    return SpanOf<const T>{addr, n};
}

template <typename T,  size_t Size>
inline SpanOf<T> make_spanOf(T (&v)[Size])
{
    return SpanOf<T>{v, Size};
}

template <typename T,  size_t Size>
inline SpanOf<const T> make_const_spanOf(T (&v)[Size])
{
    return SpanOf<const T>{v, Size};
}

template <typename T>
inline SpanOf<T> make_spanOf(std::vector<T>& v)
{
    return v.empty() ? SpanOf<T>{nullptr, 0} : SpanOf<T>{v.data(), v.size()};
}

template <typename T>
inline SpanOf<const T> make_const_spanOf(const std::vector<T>& v)
{
    return v.empty() ? SpanOf<const T>{nullptr, 0} : SpanOf<const T>{v.data(), v.size()};
}

template <typename T>
inline SpanOf<T> empty_spanOf()
{
    return SpanOf<T>{nullptr, 0};
}

template <typename T>
inline SpanOf<const T> empty_const_spanOf()
{
    return SpanOf<const T>{nullptr, 0};
}

template <typename T>
inline SpanOf<T> operator + (SpanOf<T> s, size_t offset)
{
    T* e = s.elements ? s.elements + offset : nullptr;
    size_t c = s.count > offset ? s.count - offset : 0;
    return SpanOf<T>{e,c};
}

} // namespace fabric
} // namespace omni
