// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Span.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::Span.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>

#include <cstdint>
#include <type_traits>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! A pointer along with the number of items the pointer points to.
//!
//! This object is ABI-safe and can be passed by pointer or value through the ABI.
template <typename T>
class Span
{
public:
    //! Constructor.
    Span(T* buffer, uint64_t count) noexcept : m_buffer(buffer), m_count(count)
    {
        // LCOV_EXCL_START
        static_assert(CARB_OFFSETOF2(Span<T>, m_buffer) == 0, "unexpected buffer offset");
        static_assert(CARB_OFFSETOF2(Span<T>, m_count) == 8, "unexpected count offset");
        static_assert(16 == sizeof(Span<T>), "Span is an unexpected size");
        OMNI_STATIC_ASSERT_CAN_BE_PASSED_BY_VALUE_IN_ABI(Span<T>);
        // LCOV_EXCL_STOP
    }

    //! Returns a pointer to the beginning of the array.
    T* begin() noexcept
    {
        return m_buffer;
    }

    //! Returns a const pointer to the beginning of the array.
    const T* begin() const noexcept
    {
        return m_buffer;
    }

    //! Returns a pointer to one past the end of the array.
    T* end() noexcept
    {
        return m_buffer + m_count;
    }

    //! Returns a const pointer to one past the end of the array.
    const T* end() const noexcept
    {
        return m_buffer + m_count;
    }

    //! Return @c true if the span is empty.
    bool empty() const noexcept
    {
        return (0 == m_count);
    }

    //! Returns a reference to the first element.
    //!
    //! Calling when the span is empty is undefined behavior.
    T& front() noexcept
    {
        return *(begin());
    }

    //! Returns a const reference to the first element.
    //!
    //! Calling when the span is empty is undefined behavior.
    const T& front() const noexcept
    {
        return *(begin());
    }

    //! Returns a reference to the last element.
    //!
    //! Calling when the span is empty is undefined behavior.
    T& back() noexcept
    {
        return *(end() - 1);
    }

    //! Returns a const reference to the last element.
    //!
    //! Calling when the span is empty is undefined behavior.
    const T& back() const noexcept
    {
        return *(end() - 1);
    }

    //! Returns a pointer to the beginning of the array.
    T* data() noexcept
    {
        return m_buffer;
    }

    //! Returns a pointer to the beginning of the array.
    const T* data() const noexcept
    {
        return m_buffer;
    }

    //! Returns the number of items in the array.
    uint64_t size() const noexcept
    {
        return m_count;
    }

private:
    T* m_buffer{ nullptr };
    uint64_t m_count{ 0 };
};

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
