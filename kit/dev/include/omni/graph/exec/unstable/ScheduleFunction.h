// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file ScheduleFunction.h
//!
//! @brief Helpers for @ref omni::graph::exec::unstable::IScheduleFunction.
#pragma once

#include <omni/graph/exec/unstable/IScheduleFunction.h>

#include <type_traits>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{
namespace detail
{

#ifndef DOXYGEN_BUILD

template <typename Fn>
struct ScheduleFunctionHelper
{
    static omni::graph::exec::unstable::Status invoke(Fn&& fn) noexcept
    {
        return fn();
    }

    static auto capture(Fn&& fn) noexcept
    {
        return std::move(fn);
    }
};

template <>
struct ScheduleFunctionHelper<IScheduleFunction*&>
{
    static omni::graph::exec::unstable::Status invoke(IScheduleFunction* fn) noexcept
    {
        return fn->invoke();
    }

    static auto capture(IScheduleFunction* fn) noexcept
    {
        return omni::core::borrow(fn);
    }
};

template <>
struct ScheduleFunctionHelper<omni::core::ObjectPtr<IScheduleFunction>&>
{
    static omni::graph::exec::unstable::Status invoke(omni::core::ObjectPtr<IScheduleFunction>& fn) noexcept
    {
        return fn->invoke();
    }

    static omni::core::ObjectPtr<IScheduleFunction> capture(omni::core::ObjectPtr<IScheduleFunction>& fn) noexcept
    {
        return std::move(fn);
    }
};

#endif

} // namespace detail

//! Helper function to efficiently call an invocable object (i.e. std::function, function ptr, IScheduleFunction*).
template <typename Fn>
omni::graph::exec::unstable::Status invokeScheduleFunction(Fn&& fn) noexcept
{
    return detail::ScheduleFunctionHelper<Fn>::invoke(std::forward<Fn>(fn));
}

//! Helper function to efficiently capture an invocable object (i.e. std::function, function ptr, IScheduleFunction*).
//!
//! Suitable when capturing the invocable object in a lambda to be passed to a scheduler.
//!
//! Use this function when an @ref IScheduleFunction will be invoked at a later time by a scheduler.  This function will
//! call @ref omni::core::IObject::acquire() on the @ref IScheduleFunction.
//!
//! If an invocable object that is not a @ref IScheduleFunction is passed to this function, @c std::move() will be
//! called.
template <typename Fn>
auto captureScheduleFunction(Fn&& fn) noexcept
    -> decltype(detail::ScheduleFunctionHelper<Fn>::capture(std::forward<Fn>(fn)))
{
    return detail::ScheduleFunctionHelper<Fn>::capture(std::forward<Fn>(fn));
}

//! Core ScheduleFunction implementation for @ref omni::graph::exec::unstable::IScheduleFunction
//!
//! See @ref omni::graph::exec::unstable::IScheduleFunction for documentation on this type.
template <typename Fn>
class ScheduleFunction : public Implements<IScheduleFunction>
{
public:
    static omni::core::ObjectPtr<ScheduleFunction> create(Fn&& fn) noexcept
    {
        return omni::core::steal(new ScheduleFunction(std::forward<Fn>(fn)));
    }

protected:
    ScheduleFunction(Fn&& fn) noexcept : m_fn(std::move(fn))
    {
    }

    Status invoke_abi() noexcept override
    {
        if constexpr (std::is_invocable_r_v<Status, Fn>)
        {
            return m_fn();
        }
        else
        {
            m_fn();
            return Status::eSuccess;
        }
    }

private:
    Fn m_fn;
};

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
