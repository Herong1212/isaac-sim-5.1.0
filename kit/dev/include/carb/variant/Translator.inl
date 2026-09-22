// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief Translator definitions for *carb.variant.plugin*
#pragma once

#include "../Strong.h"
#include "../cpp/Bit.h"

#include "../InterfaceUtils.h"
#include "../container/detail/TemplateHelpers.h"

#include <deque>
#include <list>
#include <map>
#include <set>
#include <unordered_map>
#include <unordered_set>

namespace carb
{
namespace dictionary
{
struct Item;
}

namespace variant
{

template <>
struct Translator<std::nullptr_t, void>
{
    RString type() const noexcept
    {
        return eNull;
    }
    void* data(std::nullptr_t) const noexcept
    {
        return nullptr;
    }
    std::nullptr_t value(void*) const noexcept
    {
        return nullptr;
    }
};

template <class T>
struct Translator<T,
                  typename std::enable_if_t<std::is_integral_v<T> && !std::is_same_v<bool, T> &&
                                            (sizeof(T) == 1 || sizeof(T) == 2 || sizeof(T) == 4 || sizeof(T) == 8) &&
                                            sizeof(T) <= sizeof(void*)>>
{
    constexpr RString type() const noexcept
    {
        constexpr bool s = std::is_signed_v<T>;
        switch (sizeof(T))
        {
            case 1:
                return s ? eInt8 : eUInt8;
            case 2:
                return s ? eInt16 : eUInt16;
            case 4:
                return s ? eInt32 : eUInt32;
            case 8:
                return s ? eInt64 : eUInt64;
        }
        CARB_ASSERT(false); // Should never get here
        return {};
    }
    void* data(T val) const noexcept
    {
        void* p{};
        memcpy(&p, &val, sizeof(T));
        return p;
    }
    T value(void* val) const noexcept
    {
        T t;
        memcpy(&t, &val, sizeof(T));
        return t;
    }
};

template <class T>
struct Translator<T,
                  typename std::enable_if_t<std::is_floating_point_v<T> && (sizeof(T) == 4 || sizeof(T) == 8) &&
                                            sizeof(T) <= sizeof(void*)>>
{
    RString type() const noexcept
    {
        return sizeof(T) == 4 ? eFloat : eDouble;
    }
    void* data(T val) const noexcept
    {
        void* p{};
        memcpy(&p, &val, sizeof(T));
        return p;
    }
    T value(void* val) const noexcept
    {
        T t;
        memcpy(&t, &val, sizeof(T));
        return t;
    }
};

// Enum types => underlying type
template <class T>
struct Translator<T, typename std::enable_if_t<std::is_enum_v<T>>> : public Translator<std::underlying_type_t<T>>
{
    using Underlying = std::underlying_type_t<T>;
    using BaseTranslator = Translator<Underlying>;
    using BaseTranslator::type;
    void* data(T val) const noexcept
    {
        return BaseTranslator::data(Underlying(val));
    }
    T value(void* val) const noexcept
    {
        return T(BaseTranslator::value(val));
    }
};

template <>
struct Translator<omni::string, void>
{
    RString type() const noexcept
    {
        return eString;
    }
    void* data(omni::string str) const noexcept
    {
        return new (carb::allocate(sizeof(omni::string))) omni::string(std::move(str));
    }
    const omni::string& value(void* val) const noexcept
    {
        return *static_cast<const omni::string*>(val);
    }
};

template <>
struct Translator<std::string, void> : public Translator<omni::string>
{
    void* data(const std::string& str) const noexcept
    {
        return new (carb::allocate(sizeof(omni::string))) omni::string(str.c_str(), str.length());
    }
    std::string value(void* val) const noexcept
    {
        auto& str = Translator<omni::string>::value(val);
        return std::string(str.c_str(), str.length());
    }
};

template <>
struct Translator<bool, void>
{
    RString type() const noexcept
    {
        return eBool;
    }
    void* data(bool b) const noexcept
    {
        void* p{};
        memcpy(&p, &b, sizeof(b));
        return p;
    }
    bool value(void* val) const noexcept
    {
        bool b;
        memcpy(&b, &val, sizeof(b));
        return b;
    }
};

//! \cond DEV
namespace detail
{
// Helper that is true_type if pointer-type T is pointer-type U excluding const/volatile
// Used to enable types for both const/volatile and non-const/volatile
template <class T, class U>
struct IsCVOrNot
    : std::integral_constant<bool,
                             std::is_pointer_v<T> &&
                                 std::is_same_v<std::remove_cv_t<std::remove_pointer_t<T>>, std::remove_pointer_t<U>>>
{
};
template <class T, class U>
constexpr bool IsCVOrNot_v = IsCVOrNot<T, U>::value;

struct StringRep
{
    mutable std::atomic_uint32_t refs{ 1 };
    uint32_t const len;
    const char str[1] = { '\0' }; // actual length is `len`

    StringRep(cpp::zstring_view sv) noexcept : len(uint32_t(sv.length()))
    {
        memcpy(const_cast<char*>(str), sv.data(), sv.length() + 1);
    }

    [[nodiscard]] static StringRep* construct(cpp::zstring_view sv) noexcept
    {
        return new (carb::allocate(sizeof(StringRep) + sv.length(), alignof(StringRep))) StringRep(sv);
    }
    static StringRep* fromData(void* s) noexcept
    {
        return reinterpret_cast<StringRep*>(static_cast<std::byte*>(s) - offsetof(StringRep, str));
    }
};
static_assert(std::is_standard_layout_v<StringRep>);
} // namespace detail
//! \endcond

// [const] char*
template <class T>
struct Translator<T, typename std::enable_if_t<detail::IsCVOrNot_v<T, char*>>>
{
    RString type() const noexcept
    {
        return eCharPtr;
    }
    void* data(T p) const noexcept
    {
        return const_cast<char*>(p);
    }
    const char* value(void* val) const noexcept
    {
        return static_cast<const char*>(val);
    }
};

// [const] dictionary::Item*
template <class T>
struct Translator<T, typename std::enable_if_t<detail::IsCVOrNot_v<T, dictionary::Item*>>>
{
    RString type() const noexcept
    {
        return eDictionary;
    }
    void* data(T p) const noexcept
    {
        return (void*)p;
    }
    const dictionary::Item* value(void* p) const noexcept
    {
        return static_cast<const dictionary::Item*>(p);
    }
};

template <class T, class U>
struct Translator<Strong<T, U>, void> : public Translator<T>
{
    using Parent = Translator<T>;
    void* data(Strong<T, U> val) const noexcept
    {
        return Parent::data(val.get());
    }
    const Strong<T, U> value(void* p) const noexcept
    {
        return Strong<T, U>{ Parent::value(p) };
    }
};

template <>
struct Translator<VariantArrayPtr, void>
{
    RString type() const noexcept
    {
        return eVariantArray;
    }
    void* data(VariantArrayPtr p) const noexcept
    {
        // Keep the ref-count that `p` held by detaching the smart pointer.
        return p.detach();
    }
    VariantArrayPtr value(void* p) const noexcept
    {
        return VariantArrayPtr(static_cast<VariantArray*>(p));
    }
};

// [const] VariantArray*
template <class T>
struct Translator<T, typename std::enable_if_t<detail::IsCVOrNot_v<T, VariantArray*>>>
{
    RString type() const noexcept
    {
        return eVariantArray;
    }
    void* data(VariantArray* p) const noexcept // IObject requires non-const
    {
        if (p)
            p->addRef();
        return p;
    }
    T value(void* p) const noexcept
    {
        return static_cast<VariantArray*>(p);
    }
};

//! \cond DEV
namespace detail
{
template <class C>
using has_reserve = decltype(std::declval<C>().reserve(std::declval<size_t>()));

template <class C>
using has_insert = decltype(std::declval<C>().insert(std::declval<typename C::value_type>()));

template <class Container>
struct ContainerAsArray
{
    RString type() const noexcept
    {
        return eVariantArray;
    }
    void* data(const Container& in) const noexcept
    {
        auto array = getCachedInterface<IVariant>()->createArray();
        array->reserve(in.size());
        for (auto& val : in)
            array->push_back(Variant(val));
        return array.detach(); // Keep the ref-count that 'array' held
    }
    Container value(void* p) const
    {
        auto array = static_cast<VariantArray*>(p);
        Container c;
        using T = typename Container::value_type;
        if constexpr (container::detail::supports_t<Container, has_reserve>::value)
        {
            c.reserve(array->size());
        }
        for (auto& var : *array)
            if (auto val = var.getValue<T>())
            {
                if constexpr (container::detail::supports_t<Container, has_insert>::value)
                    c.insert(std::move(val.value()));
                else
                    c.push_back(std::move(val.value()));
            }
        return c;
    }
};

template <class Container>
struct ContainerAsMap
{
    RString type() const noexcept
    {
        return eVariantMap;
    }
    void* data(const Container& in) const noexcept
    {
        auto map = getCachedInterface<IVariant>()->createMap();
        for (auto& val : in)
            (*map)[Variant(val.first)] = Variant(val.second);
        return map.detach();
    }
    Container value(void* p) const
    {
        auto map = static_cast<VariantMap*>(p);
        Container c;
        using Key = typename Container::key_type;
        using Value = typename Container::mapped_type;
        for (auto& pair : *map)
        {
            auto key = pair.first.getValue<Key>();
            auto value = pair.second.getValue<Value>();
            if (key && value)
            {
                c[std::move(key.value())] = std::move(value.value());
            }
        }
        return c;
    }
};
} // namespace detail
//! \endcond

template <typename T, typename Alloc>
struct Translator<std::vector<T, Alloc>, void> : detail::ContainerAsArray<std::vector<T, Alloc>>
{
};

template <typename T, typename Alloc>
struct Translator<std::list<T, Alloc>, void> : detail::ContainerAsArray<std::list<T, Alloc>>
{
};

template <typename T, typename Alloc>
struct Translator<std::deque<T, Alloc>, void> : detail::ContainerAsArray<std::deque<T, Alloc>>
{
};

template <typename T, typename Alloc>
struct Translator<std::set<T, Alloc>, void> : detail::ContainerAsArray<std::set<T, Alloc>>
{
};

template <typename T, typename Alloc>
struct Translator<std::unordered_set<T, Alloc>, void> : detail::ContainerAsArray<std::unordered_set<T, Alloc>>
{
};

template <typename K, typename V, typename Compare, typename Alloc>
struct Translator<std::map<K, V, Compare, Alloc>, void> : detail::ContainerAsMap<std::map<K, V, Compare, Alloc>>
{
};

template <typename K, typename V, typename Hash, typename Equal, typename Alloc>
struct Translator<std::unordered_map<K, V, Hash, Equal, Alloc>, void>
    : detail::ContainerAsMap<std::unordered_map<K, V, Hash, Equal, Alloc>>
{
};

template <>
struct Translator<std::pair<Variant, Variant>, void>
{
    RString type() const noexcept
    {
        return eVariantPair;
    }
    void* data(std::pair<Variant, Variant> pair) const noexcept
    {
        void* mem = carb::allocate(sizeof(VariantPair));
        return new (mem) VariantPair{ std::move(pair.first), std::move(pair.second) };
    }
    std::pair<Variant, Variant> value(void* p) const noexcept
    {
        auto pair = static_cast<VariantPair*>(p);
        return std::make_pair(pair->first, pair->second);
    }
};

template <bool Uncased, class Base>
struct Translator<carb::detail::RStringTraits<Uncased, Base>, void>
{
    constexpr static bool IsKey = std::is_same_v<Base, carb::detail::RStringKeyBase>;
    using RStringType = typename std::conditional_t<Uncased,
                                                    std::conditional_t<IsKey, RStringUKey, RStringU>,
                                                    std::conditional_t<IsKey, RStringKey, RString>>;
    static_assert(sizeof(RStringType) <= sizeof(void*), "RStringType must fit within a void*");
    static_assert(std::is_trivially_copyable_v<RStringType>, "");

    struct Unpadded
    {
        RStringType val;
    };
    struct Padded
    {
        RStringType val;
        uint32_t padding;
    };
    using Conversion = typename std::conditional_t<IsKey, Unpadded, Padded>;

    RString type() const noexcept
    {
        if (IsKey)
            return Uncased ? eRStringUKey : eRStringKey;
        return Uncased ? eRStringU : eRString;
    }
    void* data(const RStringType& rstring) const noexcept
    {
        Conversion c = {};
        c.val = rstring;
        return carb::cpp::bit_cast<void*>(c);
    }
    RStringType value(void* p) const noexcept
    {
        Conversion c = carb::cpp::bit_cast<Conversion>(p);
        return c.val;
    }
};

template <class T>
struct Translator<T,
                  std::enable_if_t<std::disjunction_v<typename std::is_same<RString, T>,
                                                      typename std::is_same<RStringU, T>,
                                                      typename std::is_same<RStringKey, T>,
                                                      typename std::is_same<RStringUKey, T>>>>
    : public Translator<carb::detail::RStringTraits<
          T::IsUncased,
          typename std::conditional_t<std::disjunction_v<typename std::is_same<RStringKey, T>, typename std::is_same<RStringUKey, T>>,
                                      carb::detail::RStringKeyBase,
                                      carb::detail::RStringBase>>>
{
};

template <>
struct Translator<VariantMapPtr, void>
{
    RString type() const noexcept
    {
        return eVariantMap;
    }
    void* data(VariantMapPtr p) const noexcept
    {
        // Keep the ref-count that `p` held by detaching the smart pointer.
        return p.detach();
    }
    VariantMapPtr value(void* p) const noexcept
    {
        return VariantMapPtr(static_cast<VariantMap*>(p));
    }
};

// [const] VariantMap*
template <class T>
struct Translator<T, typename std::enable_if_t<detail::IsCVOrNot_v<T, VariantMap*>>>
{
    RString type() const noexcept
    {
        return eVariantMap;
    }
    void* data(VariantMap* p) const noexcept // IObject requires non-const
    {
        if (p)
            p->addRef();
        return p;
    }
    T value(void* p) const noexcept
    {
        return static_cast<VariantMap*>(p);
    }
};

// Generic ObjectPtr translator
template <class T>
struct Translator<typename carb::ObjectPtr<T>,
                  typename std::enable_if_t<std::conjunction_v<std::negation<detail::IsCVOrNot<T*, VariantMap*>>,
                                                               std::negation<detail::IsCVOrNot<T*, VariantArray*>>>>>
{
    using Ptr = typename carb::ObjectPtr<T>;
    RString type() const noexcept
    {
        return eIObject;
    }
    void* data(Ptr p) const noexcept
    {
        // Keep the ref-count that `p` held by detaching the smart pointer.
        return p.detach();
    }
    Ptr value(void* p) const noexcept
    {
        return Ptr(static_cast<T*>(p));
    }
};

// [const] pointer type that inherits from IObject (excluding VariantMap* and VariantArray*)
template <class T>
struct Translator<T,
                  typename std::enable_if_t<std::conjunction_v<std::is_convertible<std::remove_cv_t<T>, IObject*>,
                                                               std::negation<detail::IsCVOrNot<T, VariantMap*>>,
                                                               std::negation<detail::IsCVOrNot<T, VariantArray*>>>>>
{
    RString type() const noexcept
    {
        return eIObject;
    }
    void* data(T p) const noexcept // IObject requires non-const
    {
        if (p)
            p->addRef();
        return p;
    }
    T value(void* p) const noexcept
    {
        return static_cast<T>(p);
    }
};

// NOTE: If you add a new Translator here, make sure that it is documented in the comment block for Translator in
// VariantTypes.h

} // namespace variant
} // namespace carb
