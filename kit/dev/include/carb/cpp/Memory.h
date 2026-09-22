// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief C++14-compatible implementation of select functionality from C++ `<memory>` library.
#pragma once

#include "../Defines.h"

#include <memory>
#include <type_traits>

namespace carb
{
namespace cpp
{

//! \cond DEV
namespace detail
{

template <class T, class = void>
struct IsMSVCIterator : std::false_type
{
};

// OVCC-1775: MSVC iterators assert in debug if you try to take the address of them.
#if CARB_COMPILER_MSC
template <class T>
struct IsMSVCIterator<T, std::void_t<decltype(std::declval<T>()._Unwrapped())>>
    : public std::is_pointer<decltype(std::declval<T>()._Unwrapped())>
{
};
#endif

template <class T>
inline constexpr bool IsMSVCIterator_v = IsMSVCIterator<T>::value;

} // namespace detail
//! \endcond

//! Call the destructor of \a p.
template <typename T>
constexpr std::enable_if_t<!std::is_array<T>::value> destroy_at(T* const p) noexcept(std::is_nothrow_destructible<T>::value)
{
    p->~T();
}

//! Call the destructor of all \a array elements.
//!
//! \tparam T The element type of the array must have a \c noexcept destructor. There no mechanism to safely use this
//!         function if an element throws. This is a departure from the C++20, wherein an exception thrown from a
//!         destructor will result in either \c std::terminate or an "implementation defined manner." Instead, we force
//!         you to handle potential exceptions by disallowing it.
template <typename T, std::size_t N>
constexpr void destroy_at(T (*array)[N]) noexcept
{
    static_assert(noexcept(carb::cpp::destroy_at(array[0])),
                  "destroy_at for array requires elements to have noexcept destructor");

    for (T& elem : *array)
    {
        carb::cpp::destroy_at(std::addressof(elem));
    }
}

#if !CARB_HAS_CPP20 || defined DOXYGEN_BUILD

//! Construct a \c T in \a place using the provided \a args.
//!
//! \note
//! This differs from the C++20 definition by not being \c constexpr, since placement new is not \c constexpr before
//! C++20. When C++20 is enabled, this function disappears in favor of \c std::construct_at.
template <typename T, typename... TArgs>
T* construct_at(T* place, TArgs&&... args) noexcept
    CARB_NO_DOC((noexcept(::new (static_cast<void*>(place)) T(std::forward<TArgs>(args)...))))
{
    return ::new (static_cast<void*>(place)) T(std::forward<TArgs>(args)...);
}

//! Obtain the address represented by \a p without forming a reference to the object pointed to by \a p.
//! Raw pointer overload: If \c T is a function type, the program is ill-formed. Otherwise, returns \a p unmodified.
template <class T>
constexpr T* to_address(T* p) noexcept
{
    static_assert(!std::is_function_v<T>, "Ill-formed if T is a function type");
    return p;
}

#    ifndef DOXYGEN_BUILD
template <class Ptr, std::enable_if_t<detail::IsMSVCIterator_v<Ptr>, bool> = false>
constexpr auto to_address(const Ptr& p) noexcept
{
    return p._Unwrapped();
}
#    endif

//! \brief Fancy pointer overload: returns `to_address(p.operator->())`.
//!
//! \tparam Ptr A fancy pointer type that defines `operator->()`
//! \param p The fancy pointer
//! \return The raw pointer result of `p.operator->()`
//!
//! \note Only available if \c p has an \c operator-> that returns a pointer.
CARB_NO_DOC(
    template <
        class Ptr,
        std::enable_if_t<!detail::IsMSVCIterator_v<Ptr> && std::is_pointer_v<decltype(std::declval<Ptr>().operator->())>, bool> = false>
)
constexpr auto to_address(const Ptr& p) noexcept
{
    return to_address(p.operator->());
}

#else

using std::construct_at;
using std::to_address;

#endif

} // namespace cpp
} // namespace carb
