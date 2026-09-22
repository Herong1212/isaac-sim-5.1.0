// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief C++14-compatible implementation of select functionality from C++ `<variant>` library.
#pragma once

#include "TypeTraits.h"

#include <functional> // for std::hash
#include <cstddef>
#include <exception>
#include <memory>
#include <type_traits>
#include <utility>

namespace carb
{

namespace cpp
{

static constexpr std::size_t variant_npos = (std::size_t)-1;

// Forward define.
template <typename... Types>
class variant;

template <std::size_t I, typename T>
struct variant_alternative;

class bad_variant_access final : public std::exception
{
public:
    bad_variant_access() noexcept = default;
    bad_variant_access(const bad_variant_access&) noexcept = default;
    bad_variant_access& operator=(const bad_variant_access&) noexcept = default;
    virtual const char* what() const noexcept override
    {
        return "bad variant access";
    }
};

namespace detail
{

// Common pathway for bad_variant_access.
[[noreturn]] inline void on_bad_variant_access()
{
#if CARB_EXCEPTIONS_ENABLED
    throw bad_variant_access();
#else
    std::terminate();
#endif
}

// This is just the raw data that the variant stores, not the index.
template <bool IsTriviallyDesctructable, typename... Types>
class VariantData;

template <bool IsTriviallyDesctructable>
class VariantData<IsTriviallyDesctructable>
{
    static constexpr size_t size = 0;
};

template <typename T, typename... Types>
class VariantData<true, T, Types...>
{
public:
    static constexpr size_t size = 1 + sizeof...(Types);
    // This is the rest of the types that form the rest of the variant
    using Next = VariantData<true, Types...>;

    union
    {
        CARB_VIZ std::remove_const_t<T> m_value;
        CARB_VIZ Next m_next;
    };
    constexpr VariantData() noexcept
    {
    }

    template <class... Args>
    constexpr VariantData(std::in_place_index_t<0>, Args&&... args) noexcept : m_value(std::forward<Args>(args)...)
    {
    }

    template <size_t I, class... Args>
    constexpr VariantData(std::in_place_index_t<I>, Args&&... args) noexcept
        : m_next(std::in_place_index<I - 1>, std::forward<Args>(args)...)
    {
    }

    constexpr T& get() & noexcept
    {
        return m_value;
    }
    constexpr const T& get() const& noexcept
    {
        return m_value;
    }
    constexpr T&& get() && noexcept
    {
        return std::move(m_value);
    }
    constexpr const T&& get() const&& noexcept
    {
        return std::move(m_value);
    }
};


template <typename T, typename... Types>
class VariantData<false, T, Types...>
{
public:
    static constexpr size_t size = 1 + sizeof...(Types);
    using Next = VariantData<false, Types...>;

    union
    {
        CARB_VIZ std::remove_const_t<T> m_value;
        CARB_VIZ Next m_next;
    };

    constexpr VariantData() noexcept
    {
    }
    template <class... Args>
    constexpr VariantData(std::in_place_index_t<0>, Args&&... args) noexcept : m_value(std::forward<Args>(args)...)
    {
    }

    template <size_t I, class... Args>
    constexpr VariantData(std::in_place_index_t<I>, Args&&... args) noexcept
        : m_next(std::in_place_index<I - 1>, std::forward<Args>(args)...)
    {
    }
    ~VariantData()
    {
    }

    constexpr T& get() & noexcept
    {
        return m_value;
    }
    constexpr const T& get() const& noexcept
    {
        return m_value;
    }
    constexpr T&& get() && noexcept
    {
        return std::move(m_value);
    }
    constexpr const T&& get() const&& noexcept
    {
        return std::move(m_value);
    }
};

template <size_t I>
struct VariantGetFromData
{
    template <class Data>
    static decltype(auto) get(Data&& data)
    {
        return VariantGetFromData<I - 1>::get(data.m_next);
    }
};

template <>
struct VariantGetFromData<0>
{
    template <class Data>
    static decltype(auto) get(Data&& data)
    {
        return data.get();
    }
};

template <size_t I, typename Data>
constexpr decltype(auto) variant_get_from_data(Data&& data)
{
    constexpr size_t size = std::remove_reference_t<Data>::size;
    return VariantGetFromData < I < size ? I : size - 1 > ::get(std::forward<Data>(data));
}

template <size_t I, typename Variant>
constexpr decltype(auto) variant_get_from_variant(Variant&& v)
{
    constexpr size_t size = std::remove_reference_t<Variant>::size;
    return VariantGetFromData < I < size ? I : size - 1 > ::get(std::forward<Variant>(v).m_storage.m_data);
}


// Visitor without index feedback.

template <size_t I>
struct Dispatcher;

template <>
struct Dispatcher<1>
{
    template <typename Functor, typename Impl>
    using return_type = decltype(std::declval<Functor>()(VariantGetFromData<0>::get(std::declval<Impl>().m_data)));

    template <size_t I, typename Functor, typename Impl>
    static decltype(auto) issue(Functor&& functor, Impl&& impl)
    {
        return std::forward<Functor>(functor)(variant_get_from_data<I>(std::forward<Impl>(impl).m_data));
    }
};

template <>
struct Dispatcher<2>
{
    template <typename Functor, typename Impl1, typename Impl2>
    using return_type = decltype(std::declval<Functor>()(VariantGetFromData<0>::get(std::declval<Impl1>().m_data),
                                                         VariantGetFromData<0>::get(std::declval<Impl2>().m_data)));

    template <size_t I, typename Functor, typename Impl1, typename Impl2>
    static decltype(auto) issue(Functor&& functor, Impl1&& impl1, Impl2&& impl2)
    {
        constexpr size_t size1 = std::remove_reference<Impl1>::type::size;
        constexpr size_t I1 = I % size1;
        constexpr size_t I2 = I / size1;
        return functor(variant_get_from_data<I1>(std::forward<Impl1>(impl1).m_data),
                       variant_get_from_data<I2>(std::forward<Impl2>(impl2).m_data));
    }
};

template <typename... Impl>
struct TotalStates;

template <typename Impl>
struct TotalStates<Impl>
{
    static constexpr size_t value = std::remove_reference<Impl>::type::size;
};

template <typename Impl, typename... Rem>
struct TotalStates<Impl, Rem...>
{
    static constexpr size_t value = std::remove_reference<Impl>::type::size * TotalStates<Rem...>::value;
};

template <typename... Ts>
struct Package
{
};

template <typename Functor, typename... Impl>
struct VisitHelperTable
{
    template <typename Ids>
    struct Instance;
};

template <typename Functor, typename... Impl>
template <size_t... Ids>
struct VisitHelperTable<Functor, Impl...>::Instance<std::index_sequence<Ids...>>
{
    using dispatcher = Dispatcher<sizeof...(Impl)>;
    using return_type = typename dispatcher::template return_type<Functor, Impl...>;
    using f_table_type = return_type (*)(Functor&&, Impl&&...);
    static f_table_type& table(size_t id)
    {
        static f_table_type tbl[] = { &Dispatcher<sizeof...(Impl)>::template issue<Ids, Functor>... };
        return tbl[id];
    }
};

inline size_t computeIndex()
{
    return 0;
}

template <class Impl, class... Impls>
constexpr size_t computeIndex(Impl&& impl, Impls&&... impls)
{
    if (impl.index() != variant_npos)
    {
        constexpr size_t size = std::remove_reference<Impl>::type::size;
        return impl.index() + size * computeIndex(impls...);
    }
    on_bad_variant_access();
}

template <int I>
struct VisitHelper;

template <>
struct VisitHelper<-1>
{
    template <typename Functor, typename... Impl>
    static constexpr decltype(auto) issue(Functor&& functor, Impl&&... impl)
    {
        constexpr size_t size = TotalStates<Impl...>::value;
        size_t index = computeIndex(impl...);
        auto& entry = VisitHelperTable<Functor, Impl...>::template Instance<std::make_index_sequence<size>>::table(index);
        return entry(std::forward<Functor>(functor), std::forward<Impl>(impl)...);
    }
};

#define VISIT_1(n)                                                                                                     \
    case (n):                                                                                                          \
        return dispatcher::template issue<n, Functor>(std::forward<Functor>(functor), std::forward<Impl>(impl)...);

#define VISIT_2(n)                                                                                                     \
    VISIT_1(n)                                                                                                         \
    VISIT_1(n + 1)
#define VISIT_4(n)                                                                                                     \
    VISIT_2(n)                                                                                                         \
    VISIT_2(n + 2)
#define VISIT_8(n)                                                                                                     \
    VISIT_4(n)                                                                                                         \
    VISIT_4(n + 4)
#define VISIT_16(n)                                                                                                    \
    VISIT_8(n)                                                                                                         \
    VISIT_8(n + 8)

template <>
struct VisitHelper<0>
{
    template <typename Functor, typename... Impl>
    static constexpr decltype(auto) issue(Functor&& functor, Impl&&... impl)
    {
        size_t index = computeIndex(impl...);
        using dispatcher = Dispatcher<sizeof...(Impl)>;
        switch (index)
        {
            default:
                VISIT_1(0)
        }
    }
};
template <>
struct VisitHelper<1>
{
    template <typename Functor, typename... Impl>
    static constexpr decltype(auto) issue(Functor&& functor, Impl&&... impl)
    {
        size_t index = computeIndex(impl...);
        using dispatcher = Dispatcher<sizeof...(Impl)>;
        switch (index)
        {
            default:
                VISIT_2(0)
        }
    }
};

template <>
struct VisitHelper<2>
{
    template <typename Functor, typename... Impl>
    static constexpr decltype(auto) issue(Functor&& functor, Impl&&... impl)
    {
        size_t index = computeIndex(impl...);
        using dispatcher = Dispatcher<sizeof...(Impl)>;
        switch (index)
        {
            default:
                VISIT_4(0)
        }
    }
};
template <>
struct VisitHelper<3>
{
    template <typename Functor, typename... Impl>
    static constexpr decltype(auto) issue(Functor&& functor, Impl&&... impl)
    {
        size_t index = computeIndex(impl...);
        using dispatcher = Dispatcher<sizeof...(Impl)>;
        switch (index)
        {
            default:
                VISIT_8(0)
        }
    }
};
template <>
struct VisitHelper<4>
{
    template <typename Functor, typename... Impl>
    static constexpr decltype(auto) issue(Functor&& functor, Impl&&... impl)
    {
        size_t index = computeIndex(impl...);
        using dispatcher = Dispatcher<sizeof...(Impl)>;
        switch (index)
        {
            default:
                VISIT_16(0)
        }
    }
};

#undef VISIT_1
#undef VISIT_2
#undef VISIT_4
#undef VISIT_8
#undef VISIT_16

// Use this as the definition so that the template parameters can auto-deduce.
template <typename Functor, typename... Variant>
decltype(auto) visitor(Functor&& functor, Variant&&... variant)
{
    constexpr size_t size = TotalStates<Variant...>::value;
    constexpr int version = size <= 1 ? 0 : size <= 2 ? 1 : size <= 4 ? 2 : size <= 8 ? 3 : size <= 16 ? 4 : -1;
    return VisitHelper<version>::issue(std::forward<Functor>(functor), std::forward<Variant>(variant)...);
}

// Internal helper that generates smaller code when scanning two variants.

template <size_t I, typename Functor, typename Data1, typename Data2>
decltype(auto) visitSameOnce(Functor&& functor, Data1&& data1, Data2&& data2)
{
    return std::forward<Functor>(functor)(
        variant_get_from_data<I>(std::forward<Data1>(data1)), variant_get_from_data<I>(std::forward<Data2>(data2)));
}

template <typename Functor,
          typename Data1,
          typename Data2,
          typename Ids = std::make_index_sequence<std::remove_reference<Data1>::type::size>>
struct VisitSameHelperTable;

template <typename Functor, typename Data1, typename Data2, size_t... Ids>
struct VisitSameHelperTable<Functor, Data1, Data2, std::index_sequence<Ids...>>
{
    using return_type = decltype(std::declval<Functor>()(
        VariantGetFromData<0>::get(std::declval<Data1>()), VariantGetFromData<0>::get(std::declval<Data2>())));
    using f_table_type = return_type (*)(Functor&&, Data1&&, Data2&&);
    static f_table_type& table(size_t id)
    {
        static f_table_type tbl[] = { &visitSameOnce<Ids, Functor, Data1, Data2>... };
        return tbl[id];
    }
};

template <int I>
struct VisitSameHelper;

template <>
struct VisitSameHelper<-1>
{
    template <typename Functor, typename Data1, typename Data2>
    static constexpr decltype(auto) issue(Functor&& functor, size_t index, Data1&& data1, Data2&& data2)
    {
        constexpr auto& entry = VisitSameHelperTable<Functor, Data1, Data2>::table(index);
        return entry(std::forward<Functor>(functor), std::forward<Data1>(data1), std::forward<Data2>(data2));
    }
};

#define VISIT_SAME_1(n)                                                                                                \
    case (n):                                                                                                          \
        return functor(variant_get_from_data<n>(std::forward<Data1>(data1)),                                           \
                       variant_get_from_data<n>(std::forward<Data2>(data2)));
#define VISIT_SAME_2(n)                                                                                                \
    VISIT_SAME_1(n)                                                                                                    \
    VISIT_SAME_1(n + 1)
#define VISIT_SAME_4(n)                                                                                                \
    VISIT_SAME_2(n)                                                                                                    \
    VISIT_SAME_2(n + 2)
#define VISIT_SAME_8(n)                                                                                                \
    VISIT_SAME_4(n)                                                                                                    \
    VISIT_SAME_4(n + 4)
#define VISIT_SAME_16(n)                                                                                               \
    VISIT_SAME_8(n)                                                                                                    \
    VISIT_SAME_8(n + 8)

template <>
struct VisitSameHelper<0>
{
    template <typename Functor, typename Data1, typename Data2>
    static constexpr decltype(auto) issue(Functor&& functor, size_t index, Data1&& data1, Data2&& data2)
    {
        switch (index)
        {
            default:
                VISIT_SAME_1(0);
        }
    }
};
template <>
struct VisitSameHelper<1>
{
    template <typename Functor, typename Data1, typename Data2>
    static constexpr decltype(auto) issue(Functor&& functor, size_t index, Data1&& data1, Data2&& data2)
    {
        switch (index)
        {
            default:
                VISIT_SAME_2(0);
        }
    }
};

template <>
struct VisitSameHelper<2>
{
    template <typename Functor, typename Data1, typename Data2>
    static constexpr decltype(auto) issue(Functor&& functor, size_t index, Data1&& data1, Data2&& data2)
    {
        switch (index)
        {
            default:
                VISIT_SAME_4(0);
        }
    }
};
template <>
struct VisitSameHelper<3>
{
    template <typename Functor, typename Data1, typename Data2>
    static constexpr decltype(auto) issue(Functor&& functor, size_t index, Data1&& data1, Data2&& data2)
    {
        switch (index)
        {
            default:
                VISIT_SAME_8(0);
        }
    }
};
template <>
struct VisitSameHelper<4>
{
    template <typename Functor, typename Data1, typename Data2>
    static constexpr decltype(auto) issue(Functor&& functor, size_t index, Data1&& data1, Data2&& data2)
    {
        switch (index)
        {
            default:
                VISIT_SAME_16(0);
        }
    }
};

#undef VISIT_SAME_1
#undef VISIT_SAME_2
#undef VISIT_SAME_4
#undef VISIT_SAME_8
#undef VISIT_SAME_16

// Use this as the definition so that the template parameters can auto-deduce.
template <typename Functor, typename Variant1, typename Variant2>
decltype(auto) visitor_same(Functor&& functor, size_t typeIndex, Variant1&& data1, Variant2&& data2)
{
    constexpr int size = std::remove_reference<Variant1>::type::size;
    constexpr int version = size <= 1 ? 0 : size <= 2 ? 1 : size <= 4 ? 2 : size <= 8 ? 3 : size <= 16 ? 4 : -1;
    return VisitSameHelper<version>::issue(std::forward<Functor>(functor), typeIndex,
                                           std::forward<Variant1>(data1).m_storage.m_data,
                                           std::forward<Variant2>(data2).m_storage.m_data);
}

template <std::size_t I, typename T, typename... Candiates>
struct GetIndexOfHelper;

template <std::size_t I, typename T, typename Candiate>
struct GetIndexOfHelper<I, T, Candiate>
{
    static constexpr size_t value = I;
};

template <std::size_t I, typename T, typename FirstCandiate, typename... Candiates>
struct GetIndexOfHelper<I, T, FirstCandiate, Candiates...>
{
    static constexpr size_t value =
        std::is_same<T, FirstCandiate>::value ? I : GetIndexOfHelper<I + 1, T, Candiates...>::value;
};

template <typename T, typename... Candiates>
static constexpr size_t index_of_v = GetIndexOfHelper<0, T, Candiates...>::value;

template <typename T, typename... Candiates>
static constexpr size_t index_of_init_v =
    GetIndexOfHelper<0, std::remove_const_t<std::remove_reference_t<T>>, std::remove_const_t<Candiates>...>::value;

template <bool IsTriviallyDesctructable, typename... Types>
class VariantStorageImpl;

template <typename... Types>
class VariantStorageImpl<true, Types...>
{
public:
    using data = VariantData<true, Types...>;
    static constexpr size_t size = data::size;
    CARB_VIZ size_t m_index;
    data m_data;

    constexpr VariantStorageImpl() noexcept : m_index(variant_npos), m_data{}
    {
    }

    template <size_t I, class... Args>
    constexpr VariantStorageImpl(std::in_place_index_t<I>, Args&&... args) noexcept
        : m_index(I), m_data{ std::in_place_index<I>, std::forward<Args>(args)... }
    {
    }
    constexpr size_t index() const
    {
        return m_index;
    }

    void destroy()
    {
        m_index = variant_npos;
    }
};

template <typename... Types>
class VariantStorageImpl<false, Types...>
{
public:
    using data = VariantData<false, Types...>;
    static constexpr size_t size = data::size;
    CARB_VIZ size_t m_index;
    data m_data;

    constexpr VariantStorageImpl() noexcept : m_index(variant_npos), m_data{}
    {
    }

    template <size_t I, class... Args>
    constexpr VariantStorageImpl(std::in_place_index_t<I>, Args&&... args) noexcept
        : m_index(I), m_data{ std::in_place_index<I>, std::forward<Args>(args)... }
    {
    }

    constexpr size_t index() const
    {
        return m_index;
    }

    void destroy()
    {
        if (m_index != variant_npos)
        {
            detail::visitor(
                [](auto& obj) {
                    using type = typename std::remove_reference<decltype(obj)>::type;
                    obj.~type();
                },
                *this);
        }
        m_index = variant_npos;
    }

    ~VariantStorageImpl()
    {
        destroy();
    }
};

template <typename... Types>
using VariantStorage = VariantStorageImpl<std::conjunction<std::is_trivially_destructible<Types>...>::value, Types...>;

} // namespace detail

struct monostate
{
    constexpr monostate()
    {
    }
};

constexpr bool operator==(monostate, monostate) noexcept
{
    return true;
}
constexpr bool operator!=(monostate, monostate) noexcept
{
    return false;
}
constexpr bool operator<(monostate, monostate) noexcept
{
    return false;
}
constexpr bool operator>(monostate, monostate) noexcept
{
    return false;
}
constexpr bool operator<=(monostate, monostate) noexcept
{
    return true;
}
constexpr bool operator>=(monostate, monostate) noexcept
{
    return true;
}

template <typename Type>
struct variant_alternative<0, variant<Type>>
{
    using type = Type;
};
template <typename Type, typename... OtherTypes>
struct variant_alternative<0, variant<Type, OtherTypes...>>
{
    using type = Type;
};
template <size_t I, typename Type, typename... OtherTypes>
struct variant_alternative<I, variant<Type, OtherTypes...>>
{
    using type = typename variant_alternative<I - 1, variant<OtherTypes...>>::type;
};

template <std::size_t I, typename T>
using variant_alternative_t = typename variant_alternative<I, T>::type;

/**
 * A C++14 compliant version of std::variant.
 *
 * This class is a not quite standards conformant implementation of std::variant. Where it doesn't comply it is in the
 * sense that it doesn't support everything. Such as all constexpr usages. Part of this is because it isn't possible on
 * a C++14 compiler, the other part is full coverage of this class is difficult. Feel free to expand this class and make
 * it more conforming to all use cases the standard version can given it will still compile on C++14.
 *
 * There are two specific differences this implementation has that were done on purpose:
 *
 * 1. This class is standard layout if and only if, all of the Types are standard layout.
 * 2. This class is ABI-safe, if and only if all types are ABI-safe. Its format will not change and is as follows in
 * memory:
 *
 * struct VariantAsCMemory
 * {
 *     size_t index;
 *     union {
 *         Type0 type0;
 *         Type1 type1;
 *         etc...
 *     }
 * };
 */
template <typename... Types>
class CARB_VIZ variant
{
    template <class Visitor, class... Variants>
    friend constexpr decltype(auto) visit(Visitor&& vis, Variants&&... variants);

    template <std::size_t I, class Variant>
    friend constexpr decltype(auto) detail::variant_get_from_variant(Variant&& v);

    template <typename Functor, typename Variant1, typename Variant2>
    friend decltype(auto) detail::visitor_same(Functor&& functor, size_t typeIndex, Variant1&& data1, Variant2&& data2);

private:
    using storage = detail::VariantStorage<Types...>;
    using data = typename storage::data;
    using self_type = variant<Types...>;

    storage m_storage;

public:
    constexpr static auto size = storage::size;

    constexpr variant() noexcept : m_storage{ std::in_place_index_t<0>() }
    {
    }

    ~variant() = default;

    constexpr variant(const variant& other) noexcept
    {
        m_storage.m_index = other.index();
        if (m_storage.m_index != variant_npos)
        {
            detail::visitor_same(
                [](auto& dest, auto& src) {
                    using type = typename std::remove_reference<decltype(src)>::type;
                    new (&dest) type(src);
                },
                other.index(), *this, other);
            m_storage.m_index = other.index();
        }
    }

    constexpr variant(variant&& other) noexcept
    {
        m_storage.m_index = other.index();
        if (m_storage.m_index != variant_npos)
        {
            CARB_ASSERT(m_storage.m_index < sizeof...(Types));
            detail::visitor_same(
                [](auto& dest, auto&& src) {
                    using type = typename std::remove_reference<decltype(src)>::type;
                    new (&dest) type(std::move(src));
                },
                other.index(), *this, other);
            other.m_storage.m_index = variant_npos;
        }
    }

    template <class T>
    constexpr variant(const T& value) noexcept
        : m_storage{ std::in_place_index_t<detail::index_of_init_v<T, Types...>>(), value }
    {
    }
    template <class T,
              typename std::enable_if<!std::is_same<variant, std::remove_reference_t<std::remove_const_t<T>>>::value,
                                      bool>::type = true>
    constexpr variant(T&& value) noexcept
        : m_storage{ std::in_place_index_t<detail::index_of_init_v<T, Types...>>(), std::move(value) }
    {
    }
    template <class T, class... Args>
    constexpr explicit variant(std::in_place_type_t<T>, Args&&... args)
        : m_storage{ std::in_place_index_t<detail::index_of_init_v<T, Types...>>(), std::forward<Args>(args)... }
    {
    }
    template <std::size_t I, class... Args>
    constexpr explicit variant(std::in_place_index_t<I>, Args&&... args)
        : m_storage{ std::in_place_index_t<I>(), std::forward<Args>(args)... }
    {
    }

    constexpr variant& operator=(const variant& rhs)
    {
        if (this != &rhs)
        {
            if (m_storage.m_index != variant_npos)
            {
                m_storage.destroy();
            }
            if (rhs.m_storage.m_index != variant_npos)
            {
                detail::visitor_same(
                    [](auto& dest, auto& src) {
                        using type = typename std::remove_reference<decltype(src)>::type;
                        new (&dest) type(src);
                    },
                    rhs.index(), *this, rhs);
                m_storage.m_index = rhs.m_storage.m_index;
            }
        }
        return *this;
    }

    constexpr variant& operator=(variant&& rhs)
    {
        if (this == &rhs)
            return *this;

        if (m_storage.m_index != variant_npos)
        {
            m_storage.destroy();
        }
        m_storage.m_index = rhs.m_storage.m_index;
        if (m_storage.m_index != variant_npos)
        {
            CARB_ASSERT(m_storage.m_index < sizeof...(Types));
            detail::visitor_same(
                [](auto& dest, auto&& src) {
                    using type = typename std::remove_reference<decltype(src)>::type;
                    new (&dest) type(std::move(src));
                },
                rhs.index(), *this, rhs);
            rhs.m_storage.m_index = variant_npos;
        }
        return *this;
    }

    template <class T,
              typename std::enable_if<!std::is_same<variant, std::remove_reference_t<std::remove_const_t<T>>>::value,
                                      bool>::type = true>
    variant& operator=(T&& t) noexcept
    {
        constexpr size_t I = detail::index_of_init_v<T, Types...>;
        using type = variant_alternative_t<I, self_type>;
        type& v = detail::variant_get_from_data<I>(m_storage.m_data);
        if (index() == I)
        {
            v = std::move(t);
        }
        else
        {
            m_storage.destroy();
            new (&v) type(std::move(t));
            m_storage.m_index = I;
        }
        return *this;
    }

    constexpr bool valueless_by_exception() const noexcept
    {
        return m_storage.m_index == variant_npos;
    }

    template <class T, class... Args>
    auto emplace(Args&&... args) -> std::remove_const_t<std::remove_reference_t<T>>&
    {
        m_storage.destroy();
        using place_type = std::remove_const_t<std::remove_reference_t<T>>;
        m_storage.m_index = detail::index_of_v<place_type, Types...>;
        return *(new (&detail::variant_get_from_data<detail::index_of_v<T, Types...>>(m_storage.m_data))
                     place_type(std::forward<Args>(args)...));
    }

    constexpr std::size_t index() const noexcept
    {
        return m_storage.m_index;
    }

    // C++26 function.
    template <class Visitor>
    constexpr auto visit(Visitor&& vis);
};

template <class T, class... Types>
constexpr bool holds_alternative(const variant<Types...>& v) noexcept
{
    return v.index() == detail::index_of_v<T, Types...>;
}

template <std::size_t I, class... Types>
inline constexpr std::add_pointer_t<variant_alternative_t<I, variant<Types...>>> get_if(variant<Types...>* pv) noexcept
{
    return (pv && I == pv->index()) ? &detail::variant_get_from_variant<I>(*pv) : nullptr;
}

template <std::size_t I, class... Types>
constexpr std::add_pointer_t<const variant_alternative_t<I, variant<Types...>>> get_if(const variant<Types...>* pv) noexcept
{
    return (pv && I == pv->index()) ? &detail::variant_get_from_variant<I>(*pv) : nullptr;
}

template <class T, class... Types>
constexpr std::add_pointer_t<T> get_if(variant<Types...>* pv) noexcept
{
    return get_if<detail::index_of_v<T, Types...>>(pv);
}

template <class T, class... Types>
constexpr std::add_pointer_t<const T> get_if(const variant<Types...>* pv) noexcept
{
    return get_if<detail::index_of_v<T, Types...>>(pv);
}

// Don't support moves yet...
template <std::size_t I, class... Types>
constexpr variant_alternative_t<I, variant<Types...>>& get(variant<Types...>& v)
{
    auto o = get_if<I>(&v);
    if (o)
    {
        return *o;
    }
    detail::on_bad_variant_access();
}

template <std::size_t I, class... Types>
constexpr const variant_alternative_t<I, variant<Types...>>& get(const variant<Types...>& v)
{
    auto o = get_if<I>(&v);
    if (o)
    {
        return *o;
    }
    detail::on_bad_variant_access();
}

template <class T, class... Types>
constexpr T& get(variant<Types...>& v)
{
    auto o = get_if<T>(&v);
    if (o)
    {
        return *o;
    }
    detail::on_bad_variant_access();
}

template <class T, class... Types>
constexpr const T& get(const variant<Types...>& v)
{
    auto o = get_if<T>(&v);
    if (o)
    {
        return *o;
    }
    detail::on_bad_variant_access();
}

// Comparison
template <class... Types>
constexpr bool operator==(const variant<Types...>& v, const variant<Types...>& w)
{
    return v.index() == w.index() &&
           detail::visitor_same([](const auto& a, const auto& b) { return a == b; }, v.index(), v, w);
}
template <class... Types>
constexpr bool operator!=(const variant<Types...>& v, const variant<Types...>& w)
{
    return v.index() != w.index() ||
           detail::visitor_same([](const auto& a, const auto& b) { return a != b; }, v.index(), v, w);
}
template <class... Types>
constexpr bool operator<(const variant<Types...>& v, const variant<Types...>& w)
{
    // If w.valueless_by_exception(), false; otherwise if v.valueless_by_exception(), true
    if (w.valueless_by_exception())
        return false;
    if (v.valueless_by_exception())
        return true;
    return v.index() < w.index() ||
           (v.index() == w.index() &&
            detail::visitor_same([](const auto& a, const auto& b) { return a < b; }, v.index(), v, w));
}
template <class... Types>
constexpr bool operator>(const variant<Types...>& v, const variant<Types...>& w)
{
    // If v.valueless_by_exception(), false; otherwise if w.valueless_by_exception(), true
    if (v.valueless_by_exception())
        return false;
    if (w.valueless_by_exception())
        return true;
    return v.index() > w.index() ||
           (v.index() == w.index() &&
            detail::visitor_same([](const auto& a, const auto& b) { return a > b; }, v.index(), v, w));
}
template <class... Types>
constexpr bool operator<=(const variant<Types...>& v, const variant<Types...>& w)
{
    // If v.valueless_by_exception(), true; otherwise if w.valueless_by_exception(), false
    if (v.valueless_by_exception())
        return true;
    if (w.valueless_by_exception())
        return false;
    return v.index() < w.index() ||
           (v.index() == w.index() &&
            detail::visitor_same([](const auto& a, const auto& b) { return a <= b; }, v.index(), v, w));
}
template <class... Types>
constexpr bool operator>=(const variant<Types...>& v, const variant<Types...>& w)
{
    // If w.valueless_by_exception(), true; otherwise if v.valueless_by_exception(), false
    if (w.valueless_by_exception())
        return true;
    if (v.valueless_by_exception())
        return false;
    return v.index() > w.index() ||
           (v.index() == w.index() &&
            detail::visitor_same([](const auto& a, const auto& b) { return a >= b; }, v.index(), v, w));
}

template <class Visitor, class... Variants>
constexpr decltype(auto) visit(Visitor&& vis, Variants&&... variants)
{
    return detail::visitor(std::forward<Visitor>(vis), std::forward<Variants>(variants).m_storage...);
}

template <class... Types>
template <class Visitor>
constexpr auto variant<Types...>::visit(Visitor&& vis)
{
    return detail::visitor(std::forward<Visitor>(vis), this->m_storage);
}

} // namespace cpp
} // namespace carb

namespace std
{

template <>
struct hash<carb::cpp::monostate>
{
    [[nodiscard]] size_t operator()(const carb::cpp::monostate&) const
    {
        // Just return something reasonable, there is not state with monostate.
        // This is just a random hex value.
        return 0x5f631327531c2962ull;
    }
};

template <typename... Types>
struct hash<carb::cpp::variant<Types...>>
{
    [[nodiscard]] size_t operator()(const carb::cpp::variant<Types...>& vis) const
    {
        // Valueless
        if (vis.index() == carb::cpp::variant_npos)
        {
            return 0;
        }
        return carb::hashCombine(std::hash<size_t>{}(vis.index()), carb::cpp::visit(
                                                                       // Invoking dohash directly is a compile
                                                                       // error.
                                                                       [](const auto& s) { return dohash(s); }, vis));
    }

private:
    // This is a simple way to remove the C-Ref qualifiers.
    template <class T>
    static size_t dohash(const T& t)
    {
        return std::hash<T>{}(t);
    }
};

} // namespace std

CARB_INCLUDE_PURIFY_TEST({
    using my_variant = carb::cpp::variant<int, float>;
    static_assert(std::is_same<int, carb::cpp::variant_alternative<0, my_variant>::type>::value, "1");
    static_assert(std::is_same<float, carb::cpp::variant_alternative_t<1, my_variant>>::value, "2");
    static_assert(carb::cpp::variant_npos == size_t(-1), "3");
    static_assert(sizeof(carb::cpp::bad_variant_access), "4");
    static_assert(!std::is_same<void, decltype(carb::cpp::get<int>(std::declval<my_variant>()))>::value, "5");
    static_assert(!std::is_same<void, decltype(carb::cpp::get<0>(std::declval<my_variant>()))>::value, "6");
    static_assert(!std::is_same<void, decltype(carb::cpp::get_if<int>(std::declval<my_variant*>()))>::value, "7");
    static_assert(!std::is_same<void, decltype(carb::cpp::get_if<0>(std::declval<my_variant*>()))>::value, "8");
    static_assert(
        std::is_same<bool, decltype(carb::cpp::holds_alternative<int>(std::declval<my_variant>()))>::value, "9");
    static_assert(std::is_class<carb::cpp::monostate>::value, "10");
    struct my_visitor
    {
        void operator()(int)
        {
        }
        void operator()(float)
        {
        }
    };
    static_assert(std::is_function<decltype(carb::cpp::visit<my_visitor, my_variant>)>::value, "11");
});
