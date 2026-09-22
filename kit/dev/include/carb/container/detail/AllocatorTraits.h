// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief Implementation detail
#pragma once

#include "../../Defines.h"

#include <memory>

namespace carb
{
namespace container
{

//! \cond DEV
namespace detail
{

template <class Allocator>
void copy_assign_allocators_impl(Allocator& lhs, const Allocator& rhs, std::true_type)
{
    lhs = rhs;
}

template <class Allocator>
void copy_assign_allocators_impl(Allocator&, const Allocator&, std::false_type)
{
}

template <class Allocator>
void copy_assign_allocators(Allocator& lhs, const Allocator& rhs)
{
    using propagate = typename std::allocator_traits<Allocator>::propagate_on_container_copy_assignment;
    copy_assign_allocators_impl(lhs, rhs, propagate{});
}

template <class Allocator>
void move_assign_allocators_impl(Allocator& lhs, Allocator& rhs, std::true_type)
{
    lhs = std::move(rhs);
}

template <class Allocator>
void move_assign_allocators_impl(Allocator& lhs, Allocator& rhs, std::false_type)
{
}

template <class Allocator>
void move_assign_allocators(Allocator& lhs, Allocator& rhs)
{
    using type = typename std::allocator_traits<Allocator>::propagate_on_container_move_assignment;
    move_assign_allocators_impl(lhs, rhs, type{});
}

template <class Allocator>
void swap_allocators_impl(Allocator& lhs, Allocator& rhs, std::true_type)
{
    using std::swap;
    swap(lhs, rhs);
}

template <class Allocator>
void swap_allocators_impl(Allocator& lhs, Allocator& rhs, std::false_type)
{
}

template <class Allocator>
void swap_allocators(Allocator& lhs, Allocator& rhs)
{
    using type = typename std::allocator_traits<Allocator>::propagate_on_container_swap;
    swap_allocators_impl(lhs, rhs, type{});
}

} // namespace detail
//! \endcond

} // namespace container
} // namespace carb
