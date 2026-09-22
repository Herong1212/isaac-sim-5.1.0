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
//! @brief Carbonite ConcurrentUnorderedMultimap, similar to TBB and Microsoft containers of similar name
#pragma once

#include "detail/ConcurrentUnorderedBase.h"

#include "../detail/ExceptionProlog.h"

namespace carb
{
namespace container
{

template <class Key, class T, class Hash, class KeyEqual, class Allocator>
class ConcurrentUnorderedMultimap;

template <class Key,
          class T,
          class Hash = std::hash<Key>,
          class KeyEqual = std::equal_to<Key>,
          class Allocator = std::allocator<std::pair<const Key, T>>>
class ConcurrentUnorderedMap
    : public detail::ConcurrentUnorderedBase<detail::ConcurrentUnorderedMapTraits<Key, T, Hash, KeyEqual, Allocator, false>>
{
    using TraitsType = detail::ConcurrentUnorderedMapTraits<Key, T, Hash, KeyEqual, Allocator, false>;
    using BaseType = detail::ConcurrentUnorderedBase<TraitsType>;

public:
    using key_type = typename BaseType::key_type;
    using mapped_type = T;
    using value_type = typename BaseType::value_type;
    using size_type = typename BaseType::size_type;
    using difference_type = typename BaseType::difference_type;
    using hasher = typename BaseType::hasher;
    using key_equal = typename BaseType::key_equal;
    using allocator_type = typename BaseType::allocator_type;
    using reference = typename BaseType::reference;
    using const_reference = typename BaseType::const_reference;
    using pointer = typename BaseType::pointer;
    using const_pointer = typename BaseType::const_pointer;
    using iterator = typename BaseType::iterator;
    using const_iterator = typename BaseType::const_iterator;
    using local_iterator = typename BaseType::local_iterator;
    using const_local_iterator = typename BaseType::const_local_iterator;
    using node_type = typename BaseType::node_type;

    using BaseType::BaseType;

    ConcurrentUnorderedMap() = default;
    ConcurrentUnorderedMap(const ConcurrentUnorderedMap&) = default;
    ConcurrentUnorderedMap(const ConcurrentUnorderedMap& other, const allocator_type& alloc) : BaseType(other, alloc)
    {
    }
    ConcurrentUnorderedMap(ConcurrentUnorderedMap&&) = default;
    ConcurrentUnorderedMap(ConcurrentUnorderedMap&& other, const allocator_type& alloc)
        : BaseType(std::move(other), alloc)
    {
    }

    ConcurrentUnorderedMap& operator=(const ConcurrentUnorderedMap&) = default;
    ConcurrentUnorderedMap& operator=(ConcurrentUnorderedMap&&) = default;

    ConcurrentUnorderedMap& operator=(std::initializer_list<value_type> init)
    {
        BaseType::operator=(init);
        return *this;
    }

    mapped_type& operator[](const key_type& key)
    {
        auto it = this->find(key);
        if (it == this->end())
        {
            it = this->emplace(std::piecewise_construct, std::forward_as_tuple(key), std::tuple<>()).first;
        }
        return it->second;
    }

    mapped_type& operator[](key_type&& key)
    {
        auto it = this->find(key);
        if (it == this->end())
        {
            it = this->emplace(std::piecewise_construct, std::forward_as_tuple(std::move(key)), std::tuple<>()).first;
        }
        return it->second;
    }

    mapped_type& at(const key_type& key)
    {
        auto it = this->find(key);
        if (it == this->end())
            CARBLOCAL_THROW(std::out_of_range, "Invalid key");
        return it->second;
    }

    const mapped_type& at(const key_type& key) const
    {
        auto it = this->find(key);
        if (it == this->end())
            CARBLOCAL_THROW(std::out_of_range, "Invalid key");
        return it->second;
    }

    using BaseType::insert;

    template <class P>
    std::enable_if_t<std::is_constructible<value_type, P&&>::value, std::pair<iterator, bool>> insert(P&& value)
    {
        return this->emplace(std::forward<P>(value));
    }

    template <class P>
    std::enable_if_t<std::is_constructible<value_type, P&&>::value, std::pair<iterator, bool>> insert(const_iterator hint,
                                                                                                      P&& value)
    {
        return this->emplace_hint(hint, std::forward<P>(value));
    }

    template <class OtherH, class OtherKE>
    void merge(ConcurrentUnorderedMap<key_type, mapped_type, OtherH, OtherKE, allocator_type>& source)
    {
        this->_merge(source);
    }

    template <class OtherH, class OtherKE>
    void merge(ConcurrentUnorderedMap<key_type, mapped_type, OtherH, OtherKE, allocator_type>&& source)
    {
        this->_merge(std::move(source));
    }

    template <class OtherH, class OtherKE>
    void merge(ConcurrentUnorderedMultimap<key_type, mapped_type, OtherH, OtherKE, allocator_type>& source)
    {
        this->_merge(source);
    }

    template <class OtherH, class OtherKE>
    void merge(ConcurrentUnorderedMultimap<key_type, mapped_type, OtherH, OtherKE, allocator_type>&& source)
    {
        this->_merge(std::move(source));
    }
};

template <class Key,
          class T,
          class Hash = std::hash<Key>,
          class KeyEqual = std::equal_to<Key>,
          class Allocator = std::allocator<std::pair<const Key, T>>>
class ConcurrentUnorderedMultimap
    : public detail::ConcurrentUnorderedBase<detail::ConcurrentUnorderedMapTraits<Key, T, Hash, KeyEqual, Allocator, true>>
{
    using TraitsType = detail::ConcurrentUnorderedMapTraits<Key, T, Hash, KeyEqual, Allocator, true>;
    using BaseType = detail::ConcurrentUnorderedBase<TraitsType>;

public:
    using key_type = typename BaseType::key_type;
    using mapped_type = T;
    using value_type = typename BaseType::value_type;
    using size_type = typename BaseType::size_type;
    using difference_type = typename BaseType::difference_type;
    using hasher = typename BaseType::hasher;
    using key_equal = typename BaseType::key_equal;
    using allocator_type = typename BaseType::allocator_type;
    using reference = typename BaseType::reference;
    using const_reference = typename BaseType::const_reference;
    using pointer = typename BaseType::pointer;
    using const_pointer = typename BaseType::const_pointer;
    using iterator = typename BaseType::iterator;
    using const_iterator = typename BaseType::const_iterator;
    using local_iterator = typename BaseType::local_iterator;
    using const_local_iterator = typename BaseType::const_local_iterator;
    using node_type = typename BaseType::node_type;

    using BaseType::BaseType;
    using BaseType::insert;

    ConcurrentUnorderedMultimap() = default;
    ConcurrentUnorderedMultimap(const ConcurrentUnorderedMultimap&) = default;
    ConcurrentUnorderedMultimap(const ConcurrentUnorderedMultimap& other, const allocator_type& alloc)
        : BaseType(other, alloc)
    {
    }
    ConcurrentUnorderedMultimap(ConcurrentUnorderedMultimap&&) = default;
    ConcurrentUnorderedMultimap(ConcurrentUnorderedMultimap&& other, const allocator_type& alloc)
        : BaseType(std::move(other), alloc)
    {
    }

    ConcurrentUnorderedMultimap& operator=(const ConcurrentUnorderedMultimap&) = default;
    ConcurrentUnorderedMultimap& operator=(ConcurrentUnorderedMultimap&&) = default;

    ConcurrentUnorderedMultimap& operator=(std::initializer_list<value_type> init)
    {
        BaseType::operator=(init);
        return *this;
    }

    template <class P>
    std::enable_if_t<std::is_constructible<value_type, P&&>::value, iterator> insert(P&& value)
    {
        return this->emplace(std::forward<P>(value));
    }

    template <class P>
    std::enable_if_t<std::is_constructible<value_type, P&&>::value, iterator> insert(const_iterator hint, P&& value)
    {
        return this->emplace_hint(hint, std::forward<P>(value));
    }

    template <class OtherH, class OtherKE>
    void merge(ConcurrentUnorderedMap<key_type, mapped_type, OtherH, OtherKE, allocator_type>& source)
    {
        this->_merge(source);
    }

    template <class OtherH, class OtherKE>
    void merge(ConcurrentUnorderedMap<key_type, mapped_type, OtherH, OtherKE, allocator_type>&& source)
    {
        this->_merge(std::move(source));
    }

    template <class OtherH, class OtherKE>
    void merge(ConcurrentUnorderedMultimap<key_type, mapped_type, OtherH, OtherKE, allocator_type>& source)
    {
        this->_merge(source);
    }

    template <class OtherH, class OtherKE>
    void merge(ConcurrentUnorderedMultimap<key_type, mapped_type, OtherH, OtherKE, allocator_type>&& source)
    {
        this->_merge(std::move(source));
    }
};

// Deduction guides
template <typename It,
          typename Hash = std::hash<detail::iterator_key_t<It>>,
          typename KeyEq = std::equal_to<detail::iterator_key_t<It>>,
          typename Alloc = std::allocator<detail::iterator_alloc_pair_t<It>>,
          typename = std::enable_if_t<detail::is_input_iterator_v<It>>,
          typename = std::enable_if_t<detail::is_allocator_v<Alloc>>,
          typename = std::enable_if_t<!detail::is_allocator_v<Hash>>,
          typename = std::enable_if_t<!detail::is_allocator_v<KeyEq>>,
          typename = std::enable_if_t<!std::is_integral_v<Hash>>>
ConcurrentUnorderedMap(It, It, std::size_t = {}, Hash = Hash(), KeyEq = KeyEq(), Alloc = Alloc())
    -> ConcurrentUnorderedMap<detail::iterator_key_t<It>, detail::iterator_mapped_t<It>, Hash, KeyEq, Alloc>;

template <typename Key,
          typename T,
          typename Hash = std::hash<std::remove_const_t<Key>>,
          typename KeyEq = std::equal_to<std::remove_const_t<Key>>,
          typename Alloc = std::allocator<std::pair<const Key, T>>,
          typename = std::enable_if_t<detail::is_allocator_v<Alloc>>,
          typename = std::enable_if_t<!detail::is_allocator_v<Hash>>,
          typename = std::enable_if_t<!detail::is_allocator_v<KeyEq>>,
          typename = std::enable_if_t<!std::is_integral_v<Hash>>>
ConcurrentUnorderedMap(
    std::initializer_list<std::pair<Key, T>>, std::size_t = {}, Hash = Hash(), KeyEq = KeyEq(), Alloc = Alloc())
    -> ConcurrentUnorderedMap<std::remove_const_t<Key>, T, Hash, KeyEq, Alloc>;

template <typename It,
          typename Alloc,
          typename = std::enable_if_t<detail::is_input_iterator_v<It>>,
          typename = std::enable_if_t<detail::is_allocator_v<Alloc>>>
ConcurrentUnorderedMap(It, It, std::size_t, Alloc) -> ConcurrentUnorderedMap<detail::iterator_key_t<It>,
                                                                             detail::iterator_mapped_t<It>,
                                                                             std::hash<detail::iterator_key_t<It>>,
                                                                             std::equal_to<detail::iterator_key_t<It>>,
                                                                             Alloc>;

template <typename It,
          typename Hash,
          typename Alloc,
          typename = std::enable_if_t<detail::is_input_iterator_v<It>>,
          typename = std::enable_if_t<detail::is_allocator_v<Alloc>>,
          typename = std::enable_if_t<!detail::is_allocator_v<Hash>>,
          typename = std::enable_if_t<!std::is_integral_v<Hash>>>
ConcurrentUnorderedMap(It, It, std::size_t, Hash, Alloc)
    -> ConcurrentUnorderedMap<detail::iterator_key_t<It>,
                              detail::iterator_mapped_t<It>,
                              Hash,
                              std::equal_to<detail::iterator_key_t<It>>,
                              Alloc>;

template <typename Key, typename T, typename Alloc, typename = std::enable_if_t<detail::is_allocator_v<Alloc>>>
ConcurrentUnorderedMap(std::initializer_list<std::pair<Key, T>>, std::size_t, Alloc)
    -> ConcurrentUnorderedMap<std::remove_const_t<Key>,
                              T,
                              std::hash<std::remove_const_t<Key>>,
                              std::equal_to<std::remove_const_t<Key>>,
                              Alloc>;

template <typename Key, typename T, typename Alloc, typename = std::enable_if_t<detail::is_allocator_v<Alloc>>>
ConcurrentUnorderedMap(std::initializer_list<std::pair<Key, T>>, Alloc)
    -> ConcurrentUnorderedMap<std::remove_const_t<Key>,
                              T,
                              std::hash<std::remove_const_t<Key>>,
                              std::equal_to<std::remove_const_t<Key>>,
                              Alloc>;

template <typename Key,
          typename T,
          typename Hash,
          typename Alloc,
          typename = std::enable_if_t<detail::is_allocator_v<Alloc>>,
          typename = std::enable_if_t<!detail::is_allocator_v<Hash>>,
          typename = std::enable_if_t<!std::is_integral_v<Hash>>>
ConcurrentUnorderedMap(std::initializer_list<std::pair<Key, T>>, std::size_t, Hash, Alloc)
    -> ConcurrentUnorderedMap<std::remove_const_t<Key>, T, Hash, std::equal_to<std::remove_const_t<Key>>, Alloc>;


template <class It,
          class Hash = std::hash<detail::iterator_key_t<It>>,
          class KeyEq = std::equal_to<detail::iterator_key_t<It>>,
          class Alloc = std::allocator<detail::iterator_alloc_pair_t<It>>,
          class = std::enable_if_t<detail::is_input_iterator_v<It>>,
          typename = std::enable_if_t<detail::is_allocator_v<Alloc>>,
          typename = std::enable_if_t<!detail::is_allocator_v<Hash>>,
          typename = std::enable_if_t<!detail::is_allocator_v<KeyEq>>,
          typename = std::enable_if_t<!std::is_integral_v<Hash>>>
ConcurrentUnorderedMultimap(It, It, std::size_t = {}, Hash = Hash(), KeyEq = KeyEq(), Alloc = Alloc())
    -> ConcurrentUnorderedMultimap<detail::iterator_key_t<It>, detail::iterator_mapped_t<It>, Hash, KeyEq, Alloc>;

template <class Key,
          class T,
          class Hash = std::hash<std::remove_const_t<Key>>,
          class KeyEq = std::equal_to<std::remove_const_t<Key>>,
          class Alloc = std::allocator<std::pair<const Key, T>>,
          typename = std::enable_if_t<detail::is_allocator_v<Alloc>>,
          typename = std::enable_if_t<!detail::is_allocator_v<Hash>>,
          typename = std::enable_if_t<!detail::is_allocator_v<KeyEq>>,
          typename = std::enable_if_t<!std::is_integral_v<Hash>>>
ConcurrentUnorderedMultimap(
    std::initializer_list<std::pair<Key, T>>, std::size_t = {}, Hash = Hash(), KeyEq = KeyEq(), Alloc = Alloc())
    -> ConcurrentUnorderedMultimap<std::remove_const_t<Key>, T, Hash, KeyEq, Alloc>;

template <class It,
          class Alloc,
          typename = std::enable_if_t<detail::is_input_iterator_v<It>>,
          typename = std::enable_if_t<detail::is_allocator_v<Alloc>>>
ConcurrentUnorderedMultimap(It, It, std::size_t, Alloc)
    -> ConcurrentUnorderedMultimap<detail::iterator_key_t<It>,
                                   detail::iterator_mapped_t<It>,
                                   std::hash<detail::iterator_key_t<It>>,
                                   std::equal_to<detail::iterator_key_t<It>>,
                                   Alloc>;

template <typename It,
          typename Hash,
          typename Alloc,
          typename = std::enable_if_t<detail::is_input_iterator_v<It>>,
          typename = std::enable_if_t<detail::is_allocator_v<Alloc>>,
          typename = std::enable_if_t<!detail::is_allocator_v<Hash>>,
          typename = std::enable_if_t<!std::is_integral_v<Hash>>>
ConcurrentUnorderedMultimap(It, It, std::size_t, Hash, Alloc)
    -> ConcurrentUnorderedMultimap<detail::iterator_key_t<It>,
                                   detail::iterator_mapped_t<It>,
                                   Hash,
                                   std::equal_to<detail::iterator_key_t<It>>,
                                   Alloc>;

template <typename Key, typename T, typename Alloc, typename = std::enable_if_t<detail::is_allocator_v<Alloc>>>
ConcurrentUnorderedMultimap(std::initializer_list<std::pair<Key, T>>, std::size_t, Alloc)
    -> ConcurrentUnorderedMultimap<std::remove_const_t<Key>,
                                   T,
                                   std::hash<std::remove_const_t<Key>>,
                                   std::equal_to<std::remove_const_t<Key>>,
                                   Alloc>;

template <typename Key, typename T, typename Alloc, typename = std::enable_if_t<detail::is_allocator_v<Alloc>>>
ConcurrentUnorderedMultimap(std::initializer_list<std::pair<Key, T>>, Alloc)
    -> ConcurrentUnorderedMultimap<std::remove_const_t<Key>,
                                   T,
                                   std::hash<std::remove_const_t<Key>>,
                                   std::equal_to<std::remove_const_t<Key>>,
                                   Alloc>;

template <typename Key,
          typename T,
          typename Hash,
          typename Alloc,
          typename = std::enable_if_t<detail::is_allocator_v<Alloc>>,
          typename = std::enable_if_t<!detail::is_allocator_v<Hash>>,
          typename = std::enable_if_t<!std::is_integral_v<Hash>>>
ConcurrentUnorderedMultimap(std::initializer_list<std::pair<Key, T>>, std::size_t, Hash, Alloc)
    -> ConcurrentUnorderedMultimap<std::remove_const_t<Key>, T, Hash, std::equal_to<std::remove_const_t<Key>>, Alloc>;

template <class Key, class T, class Hash, class KeyEqual, class Allocator>
void swap(ConcurrentUnorderedMap<Key, T, Hash, KeyEqual, Allocator>& lhs,
          ConcurrentUnorderedMap<Key, T, Hash, KeyEqual, Allocator>& rhs)
{
    lhs.swap(rhs);
}

template <class Key, class T, class Hash, class KeyEqual, class Allocator>
void swap(ConcurrentUnorderedMultimap<Key, T, Hash, KeyEqual, Allocator>& lhs,
          ConcurrentUnorderedMultimap<Key, T, Hash, KeyEqual, Allocator>& rhs)
{
    lhs.swap(rhs);
}

} // namespace container
} // namespace carb

#include "../detail/ExceptionEpilog.h"
