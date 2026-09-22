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

#include "TemplateHelpers.h"

#include <type_traits>

namespace carb
{
namespace container
{

//! \cond DEV
namespace detail
{

template <class Key, class Hasher, class KeyEqual, class = void>
struct SupportsTransparent : std::false_type
{
};

template <class Key, class Hasher, class KeyEqual>
struct SupportsTransparent<Key, Hasher, KeyEqual, std::void_t<typename Hasher::is_transparent, typename KeyEqual::is_transparent>>
    : std::true_type
{
};

struct is_iterator_impl
{
    template <class T>
    using iter_traits_category = typename std::iterator_traits<T>::iterator_category;
    template <class T>
    using input_iter_category =
        std::enable_if_t<std::is_base_of<std::input_iterator_tag, iter_traits_category<T>>::value>;
};

template <class T>
using is_input_iterator = supports_t<T, is_iterator_impl::iter_traits_category, is_iterator_impl::input_iter_category>;

template <class T>
inline constexpr bool is_input_iterator_v = is_input_iterator<T>::value;

} // namespace detail
//! \endcond

} // namespace container
} // namespace carb
