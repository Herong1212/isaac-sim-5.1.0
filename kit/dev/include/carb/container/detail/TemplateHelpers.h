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

#include "../../cpp/TypeTraits.h"

#include <memory>
#include <type_traits>

namespace carb
{
namespace container
{

//! \cond DEV
namespace detail
{

template <class T, class, template <typename> class... Checks>
struct supports
{
    using type = std::false_type;
};

template <class T, template <typename> class... Checks>
struct supports<T, std::void_t<Checks<T>...>, Checks...>
{
    using type = std::true_type;
};

template <class T, template <typename> class... Checks>
using supports_t = typename supports<T, void, Checks...>::type;

template <class A>
using alloc_value_type = typename A::value_type;
template <class A>
using alloc_ptr_t = typename std::allocator_traits<A>::pointer;
template <class A>
using has_allocate = decltype(std::declval<alloc_ptr_t<A>&>() = std::declval<A>().allocate(0));
template <class A>
using has_deallocate = decltype(std::declval<A>().deallocate(std::declval<alloc_ptr_t<A>>(), 0));

template <class T>
using is_allocator = supports_t<T, alloc_value_type, has_allocate, has_deallocate>;

template <class Iterator>
using iterator_value_t = typename std::iterator_traits<Iterator>::value_type;

template <class Iterator>
using iterator_key_t = std::remove_const_t<typename iterator_value_t<Iterator>::first_type>;

template <class Iterator>
using iterator_mapped_t = typename iterator_value_t<Iterator>::second_type;

template <class Iterator>
using iterator_alloc_pair_t = std::pair<std::add_const_t<iterator_key_t<Iterator>>, iterator_mapped_t<Iterator>>;

template <class T>
inline constexpr bool is_allocator_v = is_allocator<T>::value;

template <class Trait, class T>
struct dependent_bool : std::bool_constant<bool(Trait::value)>
{
};

} // namespace detail
//! \endcond

} // namespace container
} // namespace carb
