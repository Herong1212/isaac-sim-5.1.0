// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include "../../carb/cpp/TypeTraits.h"

#include <type_traits>

//! \cond DEV

namespace omni
{
namespace detail
{

//! This is defined by the exposition-only concept "converts-from-any-cvref" in 22.5.3.2/1 [optional.ctor]. Generally
//! tests if a given \c T can be constructed from a \c W by value, const value, reference, or const reference. This is
//! used for wrapper monads like \c optional and \c expected to disquality overloads in cases of ambiguity with copy or
//! move constructors. For example, constructing `optional<optional<string>> x{optional<string>{"hi"}}` should use the
//! value-constructing overload (22.5.3.2/23) instead of the converting constructor (22.5.3.2/33). Note that the end
//! result is the same.
template <typename T, typename W>
using ConvertsFromAnyCvRef = std::disjunction<std::is_constructible<T, W&>,
                                              std::is_convertible<W&, T>,
                                              std::is_constructible<T, W>,
                                              std::is_convertible<W, T>,
                                              std::is_constructible<T, W const&>,
                                              std::is_convertible<W const&, T>,
                                              std::is_constructible<T, W const>,
                                              std::is_convertible<W const, T>>;

} // namespace detail
} // namespace omni

//! \endcond
