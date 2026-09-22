// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "Types.h"

#include <carb/Types.h>

#include <memory>
#include <vector>

namespace omni
{
namespace anim
{
namespace navigation
{


// Int32Array

inline Int32Array::Int32Array(size_t size, int value) : m_impl{ std::make_unique<Int32ArrayImpl>(size, value) }
{
}

inline Int32Array::Int32Array(size_t size, const int* data) : m_impl{ std::make_unique<Int32ArrayImpl>(size, data) }
{
}

inline Int32Array::Int32Array(const Int32Array& other)
{
    if (other.m_impl)
    {
        m_impl = std::make_unique<Int32ArrayImpl>(*other.m_impl);
    }
}

inline Int32Array::Int32Array(const Int32Array::Int32ArrayImpl& impl) : m_impl{ std::make_unique<Int32ArrayImpl>(impl) }
{
}

inline Int32Array::~Int32Array() = default;

inline size_t Int32Array::size() const
{
    if (m_impl)
    {
        return m_impl->size();
    }
    return 0;
}

inline int* Int32Array::data()
{
    if (m_impl)
    {
        return m_impl->data();
    }
    return nullptr;
}

inline void Int32Array::clear()
{
    if (m_impl)
    {
        m_impl->clear();
    }
}

inline bool Int32Array::empty() const
{
    if (m_impl)
    {
        return m_impl->empty();
    }
    return true;
}

inline void Int32Array::resize(size_t size, int value)
{
    if (m_impl)
    {
        m_impl->resize(size, value);
    }
}

inline void Int32Array::copy(size_t size, const int* data)
{
    if (m_impl)
    {
        m_impl->copy(size, data);
    }
}

inline int& Int32Array::operator[](size_t index)
{
    if (m_impl)
    {
        return (*m_impl)[index];
    }
    static int dummy;
    return dummy;
}

inline const int& Int32Array::operator[](size_t index) const
{
    if (m_impl)
    {
        return (*m_impl)[index];
    }
    static int dummy;
    return dummy;
}

// Float32Array

inline Float32Array::Float32Array(size_t size, float value) : m_impl{ std::make_unique<Float32ArrayImpl>(size, value) }
{
}

inline Float32Array::Float32Array(size_t size, const float* data)
    : m_impl{ std::make_unique<Float32ArrayImpl>(size, data) }
{
}


inline Float32Array::Float32Array(const Float32Array& other)
{
    if (other.m_impl)
    {
        m_impl = std::make_unique<Float32ArrayImpl>(*other.m_impl);
    }
}

inline Float32Array::Float32Array(const Float32Array::Float32ArrayImpl& impl)
    : m_impl{ std::make_unique<Float32ArrayImpl>(impl) }
{
}

inline Float32Array::~Float32Array() = default;

inline size_t Float32Array::size() const
{
    if (m_impl)
    {
        return m_impl->size();
    }
    return 0;
}

inline float* Float32Array::data()
{
    if (m_impl)
    {
        return m_impl->data();
    }
    return nullptr;
}

inline void Float32Array::clear()
{
    if (m_impl)
    {
        m_impl->clear();
    }
}

inline bool Float32Array::empty() const
{
    if (m_impl)
    {
        return m_impl->empty();
    }
    return true;
}

inline void Float32Array::resize(size_t size, float value)
{
    if (m_impl)
    {
        m_impl->resize(size, value);
    }
}

inline void Float32Array::copy(size_t size, const float* data)
{
    if (m_impl)
    {
        m_impl->copy(size, data);
    }
}

inline float& Float32Array::operator[](size_t index)
{
    if (m_impl)
    {
        return (*m_impl)[index];
    }
    static float dummy;
    return dummy;
}

inline const float& Float32Array::operator[](size_t index) const
{
    if (m_impl)
    {
        return (*m_impl)[index];
    }
    static float dummy;
    return dummy;
}


// Vec3Array

inline Vec3Array::Vec3Array(size_t size, const carb::Float3& value)
    : m_impl{ std::make_unique<Vec3ArrayImpl>(size, value) }
{
}

inline Vec3Array::Vec3Array(size_t size, const carb::Float3* data)
    : m_impl{ std::make_unique<Vec3ArrayImpl>(size, data) }
{
}

inline Vec3Array::Vec3Array(const Vec3Array& other)
{
    if (other.m_impl)
    {
        m_impl = std::make_unique<Vec3ArrayImpl>(*other.m_impl);
    }
}

inline Vec3Array::Vec3Array(const Vec3Array::Vec3ArrayImpl& impl) : m_impl{ std::make_unique<Vec3ArrayImpl>(impl) }
{
}

inline Vec3Array::~Vec3Array() = default;

inline size_t Vec3Array::size() const
{
    if (m_impl)
    {
        return m_impl->size();
    }
    return 0;
}

inline carb::Float3* Vec3Array::data()
{
    if (m_impl)
    {
        return m_impl->data();
    }
    return nullptr;
}

inline void Vec3Array::clear()
{
    if (m_impl)
    {
        m_impl->clear();
    }
}

inline bool Vec3Array::empty() const
{
    if (m_impl)
    {
        return m_impl->empty();
    }
    return true;
}

inline void Vec3Array::resize(size_t size, const carb::Float3& value)
{
    if (m_impl)
    {
        m_impl->resize(size, value);
    }
}

inline void Vec3Array::copy(size_t size, const carb::Float3* data)
{
    if (m_impl)
    {
        m_impl->copy(size, data);
    }
}

inline carb::Float3& Vec3Array::operator[](size_t index)
{
    if (m_impl)
    {
        return (*m_impl)[index];
    }
    static carb::Float3 dummy;
    return dummy;
}

inline const carb::Float3& Vec3Array::operator[](size_t index) const
{
    if (m_impl)
    {
        return (*m_impl)[index];
    }
    static carb::Float3 dummy;
    return dummy;
}


}
}
}
