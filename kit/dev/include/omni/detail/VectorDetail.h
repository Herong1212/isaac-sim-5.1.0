// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//!
//! @brief implementation details for omni::vector
#pragma once

#include <iterator>
#include <memory>
#include <type_traits>

namespace omni
{

//! \cond DEV
namespace detail
{

template <class Elem, bool IsEnum = std::is_enum<Elem>::value>
struct UnwrapEnum
{
    using type = std::underlying_type_t<Elem>;
};

template <class Elem>
struct UnwrapEnum<Elem, false>
{
    using type = Elem;
};

template <class Elem>
using UnwrapEnum_t = typename UnwrapEnum<Elem>::type;

// Type discriminator for character types (char/signed char/unsigned char)
template <class T>
struct IsCharacter : std::false_type
{
};

template <>
struct IsCharacter<char> : std::true_type
{
};

template <>
struct IsCharacter<signed char> : std::true_type
{
};

template <>
struct IsCharacter<unsigned char> : std::true_type
{
};

template <class It, class T>
struct FillMemsetIsSafeHelper
{
    using value_type = typename std::iterator_traits<It>::value_type;

    using raw_type = UnwrapEnum_t<T>;
    using raw_value_type = UnwrapEnum_t<value_type>;

    using type = std::bool_constant<
        std::conjunction<std::is_pointer<It>,
                         std::disjunction<std::conjunction<IsCharacter<raw_type>, IsCharacter<raw_value_type>>,
                                          std::conjunction<std::is_same<bool, raw_type>, std::is_same<bool, raw_value_type>>>,
                         std::is_convertible<T, value_type>>::value>;
};

template <class It, class T>
inline typename FillMemsetIsSafeHelper<It, T>::type FillMemsetIsSafe(const It&, const T&)
{
    return {};
}

// Resolve an iterator class to a pointer
template <class Ptr>
inline auto resolvePtr(Ptr p)
{
    return std::addressof(*p);
}

template <class T>
inline T* resolvePtr(T* p)
{
    return p;
}

template <class It, class Alloc>
inline void implDestroyRange(It first, It last, Alloc& al, std::false_type)
{
    for (; first != last; ++first)
    {
        std::allocator_traits<Alloc>::destroy(al, resolvePtr(first));
    }
}

template <class It, class Alloc>
inline void implDestroyRange(It, It, Alloc&, std::true_type)
{
    // Trivial, nothing to do.
}

template <class Alloc>
inline void destroyRange(typename std::allocator_traits<Alloc>::pointer first,
                         typename std::allocator_traits<Alloc>::pointer last,
                         Alloc& al)
{
    using Val = typename Alloc::value_type;
    implDestroyRange(first, last, al, std::bool_constant<std::is_trivially_destructible<Val>::value>{});
}

// The destructor will destroy everything emplaced, unless release() is called before destruction.
template <class It, class Alloc>
class BackoutOnThrow
{
public:
    CARB_PREVENT_COPY(BackoutOnThrow);

    BackoutOnThrow(It dest, Alloc& al) : first(dest), last(dest), al(al)
    {
    }

    ~BackoutOnThrow()
    {
        destroyRange(first, last, al);
    }

    template <class... Args>
    void emplace_back(Args&&... args)
    {
        std::allocator_traits<Alloc>::construct(al, resolvePtr(last), std::forward<Args>(args)...);
        ++last;
    }

    It release()
    {
        first = last;
        return last;
    }

private:
    It first;
    It last;
    Alloc& al;
};

struct GeneralPtrIteratorTag
{
};
struct TriviallyCopyablePtrIteratorTag : GeneralPtrIteratorTag
{
};
struct TrivialPtrIteratorTag : GeneralPtrIteratorTag
{
};

template <class A, class B>
struct IsSameSize : std::bool_constant<sizeof(A) == sizeof(B)>
{
};

template <class A, class B>
struct BothOrNeitherBool : std::bool_constant<std::is_same<bool, A>::value == std::is_same<bool, B>::value>
{
};

template <class Source, class Dest>
struct ImplPtrCategory
{
    using USource = UnwrapEnum_t<Source>;
    using UDest = UnwrapEnum_t<Dest>;
    using type = std::conditional_t<std::conjunction<IsSameSize<USource, UDest>,
                                                     std::is_integral<USource>,
                                                     std::is_integral<UDest>,
                                                     BothOrNeitherBool<USource, UDest>>::value,
                                    TrivialPtrIteratorTag,
                                    GeneralPtrIteratorTag>;
};

template <class Elem>
struct ImplPtrCategory<Elem, Elem>
{
    using type =
        std::conditional_t<std::is_trivially_copyable<Elem>::value,
                           std::conditional_t<std::is_trivial<Elem>::value, TrivialPtrIteratorTag, TriviallyCopyablePtrIteratorTag>,
                           GeneralPtrIteratorTag>;
};

template <class Any>
struct ImplPtrCategory<Any*, const Any*>
{
    using type = TrivialPtrIteratorTag;
};

template <class Any>
struct ImplPtrCategory<Any*, volatile Any*>
{
    using type = TrivialPtrIteratorTag;
};

template <class Any>
struct ImplPtrCategory<Any*, const volatile Any*>
{
    using type = TrivialPtrIteratorTag;
};

template <class Source, class Dest>
inline GeneralPtrIteratorTag getPtrCopyCategory(const Source&, const Dest&)
{
    return {};
}

template <class Source, class Dest>
inline std::conditional_t<std::is_trivially_assignable<Dest&, Source&>::value,
                          typename ImplPtrCategory<std::remove_cv_t<Source>, std::remove_cv_t<Dest>>::type,
                          GeneralPtrIteratorTag>
getPtrCopyCategory(Source* const&, Dest* const&)
{
    return {};
}

template <class Source, class Dest>
inline GeneralPtrIteratorTag getPtrMoveCategory(const Source&, const Dest&)
{
    return {};
}

template <class Source, class Dest>
inline std::conditional_t<std::is_trivially_assignable<Dest&, Source>::value,
                          typename ImplPtrCategory<std::remove_cv_t<Source>, std::remove_cv_t<Dest>>::type,
                          GeneralPtrIteratorTag>
getPtrMoveCategory(Source* const&, Dest* const&)
{
    return {};
}

template <class It>
using UseMemsetValueConstruct = std::bool_constant<
    std::conjunction<std::is_pointer<It>,
                     std::is_scalar<typename std::iterator_traits<It>::value_type>,
                     std::negation<std::is_volatile<typename std::iterator_traits<It>::value_type>>,
                     std::negation<std::is_member_pointer<typename std::iterator_traits<It>::value_type>>>::value>;

template <class InIt, class OutIt>
inline OutIt copyMemmove(InIt first, InIt last, OutIt dest)
{
    const char* const firstCh = const_cast<const char*>(reinterpret_cast<const volatile char*>(first));
    const char* const lastCh = const_cast<const char*>(reinterpret_cast<const volatile char*>(last));
    char* const destCh = const_cast<char*>(reinterpret_cast<volatile char*>(dest));
    const auto count = size_t(lastCh - firstCh);
    std::memmove(destCh, firstCh, count);
    return reinterpret_cast<OutIt>(destCh + count);
}

template <class It1, class It2>
inline It2 copyMemmoveReverse(It1 first, It1 last, It2 dest)
{
    const char* const firstCh = const_cast<const char*>(reinterpret_cast<const volatile char*>(first));
    const char* const lastCh = const_cast<const char*>(reinterpret_cast<const volatile char*>(last));
    char* const destCh = const_cast<char*>(reinterpret_cast<volatile char*>(dest));
    const auto count = size_t(lastCh - firstCh);
    return static_cast<It2>(std::memmove(destCh - count, firstCh, count));
}

template <class It, class Diff, class Alloc>
inline It implUninitDefaultConstruct(It first, Diff count, Alloc&, std::true_type)
{
    char* const firstCh = reinterpret_cast<char*>(first);
    char* const lastCh = reinterpret_cast<char*>(first + count);
    std::memset(firstCh, 0, size_t(lastCh - firstCh));
    return first + count;
}

template <class It, class Diff, class Alloc>
inline It implUninitDefaultConstruct(It first, Diff count, Alloc& al, std::false_type)
{
    BackoutOnThrow<It, Alloc> backout{ first, al };
    for (; 0 < count; --count)
    {
        backout.emplace_back();
    }
    return backout.release();
}

template <class It, class Diff, class Alloc>
inline It implUninitFillN(
    const It first, Diff count, const typename std::iterator_traits<It>::value_type& val, Alloc& al, std::false_type)
{
    BackoutOnThrow<It, Alloc> backout{ first, al };
    for (; 0 < count; --count)
    {
        backout.emplace_back(val);
    }
    return backout.release();
}

template <class It, class Diff, class Alloc>
inline It implUninitFillN(
    const It first, Diff count, const typename std::iterator_traits<It>::value_type& val, Alloc&, std::true_type)
{
    std::memset(first, static_cast<unsigned char>(val), static_cast<size_t>(count));
    return first + count;
}

template <class InIt, class FwdIt, class Alloc>
inline FwdIt implUninitCopy(InIt first, InIt last, const FwdIt dest, Alloc& al, GeneralPtrIteratorTag)
{
    BackoutOnThrow<FwdIt, Alloc> backout{ dest, al };
    for (; first != last; ++first)
    {
        backout.emplace_back(*first);
    }
    return backout.release();
}

template <class A, class B, class Alloc>
inline B* implUninitCopy(A* const first, A* const last, B* const dest, Alloc&, TrivialPtrIteratorTag)
{
    return copyMemmove(first, last, dest);
}

template <class InIt, class FwdIt, class Alloc>
inline FwdIt implUninitMove(InIt first, const InIt last, const FwdIt dest, Alloc& al, GeneralPtrIteratorTag)
{
    BackoutOnThrow<FwdIt, Alloc> backout{ dest, al };
    for (; first != last; ++first)
    {
        backout.emplace_back(std::move(*first));
    }
    return backout.release();
}

template <class A, class B, class Alloc>
inline B* implUninitMove(A* const first, A* const last, B* const dest, Alloc&, TrivialPtrIteratorTag)
{
    return copyMemmove(first, last, dest);
}

////////

template <class It, class Diff, class Alloc>
inline It uninitDefaultConstruct(It first, Diff count, Alloc& al)
{
    return implUninitDefaultConstruct(first, count, al, std::bool_constant<UseMemsetValueConstruct<It>::value>{});
}

template <class InIt, class FwdIt, class Alloc>
inline FwdIt uninitCopy(const InIt first, const InIt last, FwdIt dest, Alloc& al)
{
    return implUninitCopy(first, last, dest, al, getPtrCopyCategory(first, dest));
}

template <class InIt, class FwdIt, class Alloc>
inline FwdIt uninitMove(const InIt first, const InIt last, FwdIt dest, Alloc& al)
{
    return implUninitMove(first, last, dest, al, getPtrMoveCategory(first, dest));
}

template <class It, class Diff, class Alloc>
inline It uninitFillN(const It first, const Diff count, const typename std::iterator_traits<It>::value_type& val, Alloc& al)
{
    return implUninitFillN(first, count, val, al, FillMemsetIsSafe(first, val));
}

} // namespace detail
//! \endcond

} // namespace omni
