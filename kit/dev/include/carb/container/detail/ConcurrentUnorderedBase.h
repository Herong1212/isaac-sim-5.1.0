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

#include "../../cpp/Bit.h"

#include "ContainerHelpers.h"
#include "TemplateHelpers.h"
#include "NodeHandle.h"
#include "PartitionTable.h"

#include <algorithm>
#include <iterator>
#include <memory>
#include <type_traits>

#include "../../detail/ExceptionProlog.h"

namespace carb
{
namespace container
{
namespace detail
{

template <class Hash, bool = std::is_empty<Hash>::value && !std::is_final<Hash>::value>
class HashBase : private Hash
{
public:
    using hasher = Hash;

    HashBase() = default;
    HashBase(hasher h) : Hash(std::move(h))
    {
    }
    const hasher& h() const
    {
        return *this;
    }
};

template <class Hash>
class HashBase<Hash, false>
{
    Hash m_hash;

public:
    using hasher = Hash;

    HashBase() = default;
    HashBase(hasher h) : m_hash(std::move(h))
    {
    }
    const hasher& h() const
    {
        return m_hash;
    }
};

template <class KeyEqual, bool = std::is_empty<KeyEqual>::value && !std::is_final<KeyEqual>::value>
class KeyEqualBase : private KeyEqual
{
public:
    using key_equal = KeyEqual;

    KeyEqualBase() = default;
    KeyEqualBase(key_equal k) : KeyEqual(std::move(k))
    {
    }
    const key_equal& ke() const
    {
        return *this;
    }
};

template <class KeyEqual>
class KeyEqualBase<KeyEqual, false>
{
    KeyEqual m_key_equal;

public:
    using key_equal = KeyEqual;

    KeyEqualBase() = default;
    KeyEqualBase(key_equal k) : m_key_equal(std::move(k))
    {
    }
    const key_equal& ke() const
    {
        return m_key_equal;
    }
};

template <class Key, class Hash, class KeyEqual>
class HashCompare : private HashBase<Hash>, private KeyEqualBase<KeyEqual>
{
    using is_transparent_hash = SupportsTransparent<Key, Hash, KeyEqual>;

public:
    using hasher = typename HashBase<Hash>::hasher;
    using key_equal = typename KeyEqualBase<KeyEqual>::key_equal;

    HashCompare() = default;
    HashCompare(hasher hash, key_equal equal)
        : HashBase<Hash>(std::move(hash)), KeyEqualBase<KeyEqual>(std::move(equal))
    {
    }

    std::size_t operator()(const Key& key) const
    {
        return std::size_t(this->h()(key));
    }

    bool operator()(const Key& key1, const Key& key2) const
    {
        return this->ke()(key1, key2);
    }

    template <class K, class = std::enable_if_t<is_transparent_hash::value, K>>
    std::size_t operator()(const K& key) const
    {
        return std::size_t(this->h()(key));
    }

    template <class K1, class K2, class = std::enable_if_t<is_transparent_hash::value, K1>>
    bool operator()(const K1& key1, const K2& key2) const
    {
        return this->ke()(key1, key2);
    }

    hasher hash_function() const
    {
        return this->h();
    }

    key_equal key_eq() const
    {
        return this->ke();
    }
};

template <class Key, class T, class Hash, class KeyEqual, class Allocator, bool TAllowMulti>
struct ConcurrentUnorderedMapTraits
{
    using value_type = std::pair<const Key, T>;
    using key_type = Key;
    using allocator_type = Allocator;
    using HashCompareType = HashCompare<Key, Hash, KeyEqual>;
    static constexpr bool AllowMulti = TAllowMulti;

    static constexpr const key_type& get_key(const value_type& value)
    {
        return value.first;
    }
};

struct Split_t
{
};

template <class Traits>
class ConcurrentUnorderedBase;

template <class Container, class Value>
class SListIterator
{
public:
    using value_type = Value;
    using difference_type = typename Container::difference_type;
    using pointer = value_type*;
    using reference = value_type&;
    using iterator_category = std::forward_iterator_tag;

    constexpr SListIterator() noexcept : m_node(nullptr)
    {
    }

    constexpr SListIterator(const SListIterator<Container, typename Container::value_type>& other) noexcept
        : m_node(other.m_node)
    {
    }

    SListIterator& operator=(const SListIterator<Container, typename Container::value_type>& other)
    {
        m_node = other.m_node;
        return *this;
    }

    reference operator*() const noexcept
    {
        return m_node->value();
    }

    pointer operator->() const noexcept
    {
        return m_node->storage();
    }

    SListIterator& operator++() noexcept
    {
        auto next = m_node->next();
        while (next && next->isHole())
            next = next->next();
        m_node = static_cast<NodePtr>(next);
        return *this;
    }

    SListIterator operator++(int) noexcept
    {
        SListIterator temp = *this;
        ++*this;
        return temp;
    }

private:
    using NodePtr = typename Container::ValueNodePtr;
    template <class U, class V>
    friend class SListIterator;
    template <class Traits>
    friend class ConcurrentUnorderedBase;
    template <class U, class V, class W>
    friend bool operator==(const SListIterator<U, V>& lhs, const SListIterator<U, W>& rhs);
    template <class U, class V, class W>
    friend bool operator!=(const SListIterator<U, V>& lhs, const SListIterator<U, W>& rhs);

    SListIterator(NodePtr node) noexcept : m_node(node)
    {
    }

    NodePtr getNodePtr() const noexcept
    {
        return m_node;
    }

    NodePtr m_node;
};

template <class Container, class T, class U>
bool operator==(const SListIterator<Container, T>& lhs, const SListIterator<Container, U>& rhs)
{
    return lhs.m_node == rhs.m_node;
}

template <class Container, class T, class U>
bool operator!=(const SListIterator<Container, T>& lhs, const SListIterator<Container, U>& rhs)
{
    return lhs.m_node != rhs.m_node;
}

template <class TKeyType>
class SListNode
{
public:
    using NodePtr = SListNode*;
    using KeyType = TKeyType;

    constexpr SListNode(KeyType key) noexcept : m_next(nullptr), m_orderKey(key)
    {
    }

    void init(KeyType key)
    {
        m_orderKey = key;
    }

    KeyType getOrderKey() const noexcept
    {
        return m_orderKey;
    }

    bool isHole() const noexcept
    {
        // Bit 0 is 0 for "hole" nodes that don't hold a value
        return !(m_orderKey & 0x1);
    }

    NodePtr next() const noexcept
    {
        return m_next.load(std::memory_order_acquire);
    }

    void setNext(NodePtr next) noexcept
    {
        m_next.store(next, std::memory_order_release);
    }

    bool trySetNext(NodePtr expected, NodePtr next)
    {
        return m_next.compare_exchange_strong(expected, next);
    }

private:
    std::atomic<NodePtr> m_next;
    KeyType m_orderKey;
};

CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Warray-bounds") // GCC11: array subscript X is partly outside array bounds of Y
template <class ValueType, class TKeyType>
class ValueNode : public SListNode<TKeyType>
{
public:
    using BaseType = SListNode<TKeyType>;
    using KeyType = typename BaseType::KeyType;
    using value_type = ValueType;

    constexpr ValueNode(KeyType orderKey) noexcept : BaseType(orderKey)
    {
    }
    ~ValueNode()
    {
    }

    value_type* storage() noexcept
    {
        return &m_value;
    }

    value_type& value() noexcept
    {
        return *storage();
    }

private:
    // Encapsulate in a union so value is indeterminate until explicitly constructed.
    union
    {
        value_type m_value;
    };
};
CARB_IGNOREWARNING_GNUC_POP

template <class Traits>
class ConcurrentUnorderedBase
{
    using SelfType = ConcurrentUnorderedBase<Traits>;
    using TraitsType = Traits;
    using HashCompareType = typename TraitsType::HashCompareType;
    class PartitionTable;

public:
    using value_type = typename TraitsType::value_type;
    using key_type = typename TraitsType::key_type;
    using allocator_type = typename TraitsType::allocator_type;

private:
    using AllocatorTraitsType = std::allocator_traits<allocator_type>;
    static_assert(std::is_same<typename AllocatorTraitsType::value_type, value_type>::value,
                  "value_type of allocator and container must match");
    using KeyType = std::size_t;

public:
    using size_type = std::size_t;
    using difference_type = std::ptrdiff_t;

    using iterator = SListIterator<SelfType, value_type>;
    using const_iterator = SListIterator<SelfType, const value_type>;
    using local_iterator = iterator;
    using const_local_iterator = const_iterator;

    using reference = value_type&;
    using const_reference = const value_type&;
    using pointer = typename AllocatorTraitsType::pointer;
    using const_pointer = typename AllocatorTraitsType::const_pointer;

    using hasher = typename HashCompareType::hasher;
    using key_equal = typename HashCompareType::key_equal;

private:
    using ListNodeType = SListNode<KeyType>;
    using ValueNodeType = ValueNode<value_type, KeyType>;
    using NodePtr = ListNodeType*;
    using ValueNodePtr = ValueNodeType*;

    using ValueNodeAllocatorType = typename AllocatorTraitsType::template rebind_alloc<ValueNodeType>;
    using NodeAllocatorType = typename AllocatorTraitsType::template rebind_alloc<ListNodeType>;

    using ValueNodeAllocatorTraits = std::allocator_traits<ValueNodeAllocatorType>;
    using NodeAllocatorTraits = std::allocator_traits<NodeAllocatorType>;

    // Picks a power of two not lower than `val`
    static constexpr size_type singleBitCeil(size_type val) noexcept
    {
        return size_type(1) << cpp::detail::log2(size_type(val ? val : 1) * 2 - 1);
    }

    template <class T>
    using IsTransparent = dependent_bool<SupportsTransparent<key_type, hasher, key_equal>, T>;

public:
    using node_type = node_handle<key_type, value_type, ValueNodeType, allocator_type>;

    explicit ConcurrentUnorderedBase(size_type bucket_count,
                                     const hasher& hash = hasher(),
                                     const key_equal& equal = key_equal(),
                                     const allocator_type& alloc = allocator_type())
        : m_size(0),
          m_bucketCount(singleBitCeil(bucket_count)),
          m_pair(InitBoth{}, HashCompareType(hash, equal), float(kInitialMaxLoadFactor)),
          m_head(KeyType(0)),
          m_partitions(alloc)
    {
    }

    ConcurrentUnorderedBase() : ConcurrentUnorderedBase(kInitialBucketCount)
    {
    }

    ConcurrentUnorderedBase(size_type bucket_count, const allocator_type& alloc)
        : ConcurrentUnorderedBase(bucket_count, hasher(), key_equal(), alloc)
    {
    }

    ConcurrentUnorderedBase(size_type bucket_count, const hasher& hash, const allocator_type& alloc)
        : ConcurrentUnorderedBase(bucket_count, hash, key_equal(), alloc)
    {
    }

    explicit ConcurrentUnorderedBase(const allocator_type& alloc)
        : ConcurrentUnorderedBase(kInitialBucketCount, hasher(), key_equal(), alloc)
    {
    }

    template <class InputIterator>
    ConcurrentUnorderedBase(InputIterator first,
                            InputIterator last,
                            size_type bucket_count = kInitialBucketCount,
                            const hasher& hash = hasher(),
                            const key_equal& equal = key_equal(),
                            const allocator_type& alloc = allocator_type())
        : ConcurrentUnorderedBase(bucket_count, hash, equal, alloc)
    {
        insert(first, last);
    }

    template <class InputIterator>
    ConcurrentUnorderedBase(InputIterator first, InputIterator last, size_type bucket_count, const allocator_type& alloc)
        : ConcurrentUnorderedBase(first, last, bucket_count, hasher(), key_equal(), alloc())
    {
    }

    template <class InputIterator>
    ConcurrentUnorderedBase(
        InputIterator first, InputIterator last, size_type bucket_count, const hasher& hash, const allocator_type& alloc)
        : ConcurrentUnorderedBase(first, last, bucket_count, hash, key_equal(), alloc)
    {
    }

    ConcurrentUnorderedBase(const ConcurrentUnorderedBase& other)
        : m_size(other.m_size.load(std::memory_order_relaxed)),
          m_bucketCount(other.m_bucketCount.load(std::memory_order_relaxed)),
          m_pair(InitBoth{}, other.m_pair.first(), other.m_pair.second),
          m_head(other.m_head.getOrderKey()),
          m_partitions(other.m_partitions)
    {
        CARBLOCAL_TRY_BEGIN
        {
            _copy(other);
        }
        CARBLOCAL_CATCH_ALL
        {
            clear();
        }
    }

    ConcurrentUnorderedBase(const ConcurrentUnorderedBase& other, const allocator_type& alloc)
        : m_size(other.m_size.load(std::memory_order_relaxed)),
          m_bucketCount(other.m_bucketCount.load(std::memory_order_relaxed)),
          m_pair(InitBoth{}, other.m_pair.first(), other.m_pair.second),
          m_head(other.m_head.getOrderKey()),
          m_partitions(other.m_partitions, alloc)
    {
        CARBLOCAL_TRY_BEGIN
        {
            _copy(other);
        }
        CARBLOCAL_CATCH_ALL
        {
            clear();
        }
    }

    ConcurrentUnorderedBase(ConcurrentUnorderedBase&& other)
        : m_size(other.m_size.load(std::memory_order_relaxed)),
          m_bucketCount(other.m_bucketCount.load(std::memory_order_relaxed)),
          m_pair(InitBoth{}, std::move(other.m_pair.first()), std::move(other.m_pair.second)),
          m_head(other.m_head.getOrderKey()),
          m_partitions(std::move(other.m_partitions))
    {
        _moveContent(std::move(other));
    }

    ConcurrentUnorderedBase(ConcurrentUnorderedBase&& other, const allocator_type& alloc)
        : m_size(other.m_size.load(std::memory_order_relaxed)),
          m_bucketCount(other.m_bucketCount.load(std::memory_order_relaxed)),
          m_pair(InitBoth{}, std::move(other.m_pair.first()), std::move(other.m_pair.second)),
          m_head(other.m_head.getOrderKey()),
          m_partitions(std::move(other.m_partitions), alloc)
    {
        using is_always_equal = typename AllocatorTraitsType::is_always_equal;
        _moveConstructWithAlloc(std::move(other), alloc, is_always_equal{});
    }

    ConcurrentUnorderedBase(std::initializer_list<value_type> init,
                            size_type bucket_count = kInitialBucketCount,
                            const hasher& hash = hasher(),
                            const key_equal& equal = key_equal(),
                            const allocator_type& alloc = allocator_type())
        : ConcurrentUnorderedBase(init.begin(), init.end(), bucket_count, hash, equal, alloc)
    {
    }

    ConcurrentUnorderedBase(std::initializer_list<value_type> init, size_type bucket_count, const allocator_type& alloc)
        : ConcurrentUnorderedBase(init, bucket_count, hasher(), key_equal(), alloc)
    {
    }

    ConcurrentUnorderedBase(std::initializer_list<value_type> init,
                            size_type bucket_count,
                            const hasher& hash,
                            const allocator_type& alloc)
        : ConcurrentUnorderedBase(init, bucket_count, hash, key_equal(), alloc)
    {
    }

    ~ConcurrentUnorderedBase()
    {
        _clear();
    }

    ConcurrentUnorderedBase& operator=(const ConcurrentUnorderedBase& other)
    {
        if (this != &other)
        {
            clear();
            m_size.store(other.m_size.load(std::memory_order_relaxed), std::memory_order_relaxed);
            m_bucketCount.store(other.m_bucketCount.load(std::memory_order_relaxed), std::memory_order_relaxed);
            m_pair.first() = other.m_pair.first();
            m_pair.second = other.m_pair.second;
            m_partitions = other.m_partitions;
            _copy(other);
        }
        return *this;
    }

    ConcurrentUnorderedBase& operator=(ConcurrentUnorderedBase&& other)
    {
        if (this != &other)
        {
            clear();
            m_size.store(other.m_size.load(std::memory_order_relaxed), std::memory_order_relaxed);
            m_bucketCount.store(other.m_bucketCount.load(std::memory_order_relaxed), std::memory_order_relaxed);
            m_pair.first() = std::move(other.m_pair.first());
            m_pair.second = std::move(other.m_pair.second);
            m_partitions = std::move(other.m_partitions);

            using propagate = typename AllocatorTraitsType::propagate_on_container_move_assignment;
            using is_always_equal = typename AllocatorTraitsType::is_always_equal;
            _moveAssign(std::move(other), std::disjunction<propagate, is_always_equal>{});
        }
        return *this;
    }

    ConcurrentUnorderedBase& operator=(std::initializer_list<value_type> init)
    {
        clear();
        insert(init);
        return *this;
    }

    void swap(ConcurrentUnorderedBase& other) noexcept(PartitionTable::kIsNoexceptSwap)
    {
        if (this != &other)
        {
            using propagate = typename AllocatorTraitsType::propagate_on_container_swap;
            using is_always_equal = typename AllocatorTraitsType::is_always_equal;
            _swap(other, std::disjunction<propagate, is_always_equal>{});
        }
    }

    allocator_type get_allocator() const noexcept
    {
        return m_partitions.get_allocator();
    }

    const_iterator cbegin() const noexcept
    {
        return const_iterator(_firstValueNode(const_cast<NodePtr>(&m_head)));
    }
    const_iterator begin() const noexcept
    {
        return cbegin();
    }
    iterator begin() noexcept
    {
        return iterator(_firstValueNode(&m_head));
    }

    const_iterator cend() const noexcept
    {
        return const_iterator(nullptr);
    }
    const_iterator end() const noexcept
    {
        return cend();
    }
    iterator end() noexcept
    {
        return iterator(nullptr);
    }

    [[nodiscard]] bool empty() const noexcept
    {
        return size() == 0;
    }
    size_type size() const noexcept
    {
        return m_size.load(std::memory_order_relaxed);
    }
    size_type max_size() const noexcept
    {
        return AllocatorTraitsType::max_size(get_allocator());
    }

    void clear() noexcept
    {
        _clear();
    }

    template <bool Multi = TraitsType::AllowMulti>
    std::enable_if_t<!Multi, std::pair<iterator, bool>> insert(const value_type& value)
    {
        return _insertValue(value);
    }

    template <bool Multi = TraitsType::AllowMulti>
    std::enable_if_t<!Multi, std::pair<iterator, bool>> insert(value_type&& value)
    {
        return _insertValue(std::move(value));
    }

    template <bool Multi = TraitsType::AllowMulti>
    std::enable_if_t<Multi, iterator> insert(const value_type& value)
    {
        return _insertValue(value).first;
    }

    template <bool Multi = TraitsType::AllowMulti>
    std::enable_if_t<Multi, iterator> insert(value_type&& value)
    {
        return _insertValue(std::move(value)).first;
    }

    iterator insert(const_iterator, const value_type& value)
    {
        return insert(value).first;
    }

    iterator insert(const_iterator, value_type&& value)
    {
        return insert(std::move(value)).first;
    }

    template <class InputIterator>
    void insert(InputIterator first, InputIterator last)
    {
        for (; first != last; ++first)
            insert(*first);
    }

    void insert(std::initializer_list<value_type> init)
    {
        insert(init.begin(), init.end());
    }

    struct insert_return_type
    {
        iterator position;
        bool inserted;
        node_type node;
    };

    template <bool Multi = TraitsType::AllowMulti>
    std::enable_if_t<!Multi, insert_return_type> insert(node_type&& node)
    {
        return _insertNode(std::move(node));
    }

    template <bool Multi = TraitsType::AllowMulti>
    std::enable_if_t<Multi, iterator> insert(node_type&& node)
    {
        auto result = _insertNode(std::move(node));
        CARB_ASSERT(result.inserted);
        CARB_ASSERT(result.node.empty());
        return result.position;
    }

    iterator insert(const_iterator, node_type&& node)
    {
        return _insertNode(std::move(node)).position;
    }

    template <bool Multi = TraitsType::AllowMulti, class... Args>
    std::enable_if_t<!Multi, std::pair<iterator, bool>> emplace(Args&&... args)
    {
        return _emplace(std::forward<Args>(args)...);
    }

    template <bool Multi = TraitsType::AllowMulti, class... Args>
    std::enable_if_t<Multi, iterator> emplace(Args&&... args)
    {
        return _emplace(std::forward<Args>(args)...).first;
    }

    template <typename... Args>
    iterator emplace_hint(const_iterator, Args&&... args)
    {
        return emplace(std::forward<Args>(args)...).first;
    }

    iterator unsafe_erase(const_iterator pos)
    {
        return iterator(_firstValueNode(_erase(pos.getNodePtr())));
    }

    iterator unsafe_erase(iterator pos)
    {
        return iterator(_firstValueNode(_erase(pos.getNodePtr())));
    }

    iterator unsafe_erase(const_iterator first, const_iterator last)
    {
        while (first != last)
            first = unsafe_erase(first);
        return iterator(first.getNodePtr());
    }

    size_type unsafe_erase(const key_type& key)
    {
        return _keyErase(key);
    }

    template <class K>
    typename std::enable_if_t<IsTransparent<K>::value && !std::is_convertible<K, const_iterator>::value &&
                                  !std::is_convertible<K, iterator>::value,
                              size_type>
    unsafe_erase(const K& key)
    {
        return _keyErase(key);
    }

    node_type unsafe_extract(const_iterator pos)
    {
        _extract(pos.getNodePtr());
        return node_handle_accessor::construct<node_type>(pos.getNodePtr());
    }

    node_type unsafe_extract(iterator pos)
    {
        _extract(pos.getNodePtr());
        return node_handle_accessor::construct<node_type>(pos.getNodePtr());
    }

    node_type unsafe_extract(const key_type& key)
    {
        iterator item = find(key);
        return item == end() ? node_type() : unsafe_extract(item);
    }

    template <class K>
    typename std::enable_if_t<IsTransparent<K>::value && !std::is_convertible<K, const_iterator>::value &&
                                  !std::is_convertible<K, iterator>::value,
                              node_type>
    unsafe_extract(const K& key)
    {
        iterator item = find(key);
        return item == end() ? node_type() : unsafe_extract(item);
    }

    iterator find(const key_type& key)
    {
        ValueNodePtr result = _find(key);
        return result == nullptr ? end() : iterator(result);
    }

    const_iterator find(const key_type& key) const
    {
        ValueNodePtr result = const_cast<SelfType*>(this)->_find(key);
        return result == nullptr ? end() : const_iterator(result);
    }

    template <class K>
    typename std::enable_if_t<IsTransparent<K>::value, iterator> find(const K& key)
    {
        ValueNodePtr result = _find(key);
        return result == nullptr ? end() : iterator(result);
    }

    template <class K>
    typename std::enable_if_t<IsTransparent<K>::value, const_iterator> find(const K& key) const
    {
        ValueNodePtr result = const_cast<SelfType*>(this)->_find(key);
        return result == nullptr ? end() : const_iterator(result);
    }

    std::pair<iterator, iterator> equal_range(const key_type& key)
    {
        auto result = _equalRange(key);
        return std::make_pair(iterator(result.first), iterator(result.second));
    }

    std::pair<const_iterator, const_iterator> equal_range(const key_type& key) const
    {
        auto result = const_cast<SelfType*>(this)->_equalRange(key);
        return std::make_pair(const_iterator(result.first), const_iterator(result.second));
    }

    template <class K>
    typename std::enable_if_t<IsTransparent<K>::value, std::pair<iterator, iterator>> equal_range(const K& key)
    {
        auto result = _equalRange(key);
        return std::make_pair(iterator(result.first), iterator(result.second));
    }

    template <class K>
    typename std::enable_if_t<IsTransparent<K>::value, std::pair<const_iterator, const_iterator>> equal_range(const K& key) const
    {
        auto result = const_cast<SelfType*>(this)->_equalRange(key);
        return std::make_pair(const_iterator(result.first), const_iterator(result.second));
    }

    size_type count(const key_type& key) const
    {
        return _count(key);
    }

    template <class K>
    typename std::enable_if_t<IsTransparent<K>::value, size_type> count(const K& key) const
    {
        return _count(key);
    }

    bool contains(const key_type& key) const
    {
        return find(key) != end();
    }

    template <class K>
    typename std::enable_if_t<IsTransparent<K>::value, bool> contains(const K& key) const
    {
        return find(key) != end();
    }

    const_local_iterator unsafe_cbegin(size_type n) const
    {
        return const_local_iterator(_firstValueNode(const_cast<SelfType*>(this)->_getBucket(n)));
    }
    const_local_iterator unsafe_begin(size_type n) const
    {
        return unsafe_cbegin(n);
    }
    local_iterator unsafe_begin(size_type n)
    {
        return local_iterator(_firstValueNode(_getBucket(n)));
    }

    const_local_iterator unsafe_cend(size_type n) const
    {
        const size_type bucket_count = m_bucketCount.load(std::memory_order_relaxed);
        return n != bucket_count - 1 ? unsafe_cbegin(_getNextBucketIndex(n)) : const_local_iterator(nullptr);
    }

    const_local_iterator unsafe_end(size_type n) const
    {
        return unsafe_cend(n);
    }

    local_iterator unsafe_end(size_type n)
    {
        const size_type bucket_count = m_bucketCount.load(std::memory_order_relaxed);
        return n != bucket_count - 1 ? unsafe_begin(_getNextBucketIndex(n)) : local_iterator(nullptr);
    }

    size_type unsafe_bucket_count() const
    {
        return m_bucketCount.load(std::memory_order_relaxed);
    }

    size_type unsafe_max_bucket_count() const
    {
        return max_size();
    }

    size_type unsafe_bucket_size(size_type n) const
    {
        return size_type(std::distance(unsafe_begin(n), unsafe_end(n)));
    }

    size_type unsafe_bucket(const key_type& key) const
    {
        return m_pair.first()(key) % m_bucketCount.load(std::memory_order_relaxed);
    }

    float load_factor() const
    {
        return float(size() / float(m_bucketCount.load(std::memory_order_acquire)));
    }

    float max_load_factor() const
    {
        return m_pair.second;
    }

    void max_load_factor(float f)
    {
        if (f != f || f < 0.f)
            CARBLOCAL_THROW(std::out_of_range, "invalid hash load factor");
        m_pair.second = f;
    }

    void rehash(size_type num_buckets)
    {
        auto current = m_bucketCount.load(std::memory_order_acquire);
        while (current < num_buckets && !m_bucketCount.compare_exchange_strong(current, singleBitCeil(num_buckets)))
            ;
    }

    void reserve(size_type elements)
    {
        auto current = m_bucketCount.load(std::memory_order_acquire);
        auto needed = current;

        // max_load_factor() is currently unsafe, so we can assume that max load factor won't be changed during this
        while (needed * max_load_factor() < elements)
            needed <<= 1;

        while (!m_bucketCount.compare_exchange_strong(current, needed) && current < needed)
            ;
    }

    hasher hash_function() const
    {
        return m_pair.first().hash_function();
    }
    key_equal key_eq() const
    {
        return m_pair.first().key_eq();
    }

protected:
    static constexpr bool AllowMulti = TraitsType::AllowMulti;

    template <class SourceType>
    void _merge(SourceType&& source)
    {
        static_assert(
            std::is_same<node_type, typename std::decay_t<SourceType>::node_type>::value, "Incompatible containers");

        for (auto source_prev = &source.m_head; source_prev->next() != nullptr; /* in loop */)
        {
            if (!source_prev->next()->isHole())
            {
                ValueNodePtr curr = static_cast<ValueNodePtr>(source_prev->next());
                // If multimapping is allowed or the key is not present in *this, extract the node
                if (AllowMulti || !contains(TraitsType::get_key(curr->value())))
                {
                    NodePtr next_node = curr->next();
                    source._unlinkNode(source_prev, curr, next_node);

                    KeyType old_order_key = curr->getOrderKey();

                    // If insertion fails the node must be returned to `source`
                    auto result = _insertNode(node_handle_accessor::construct<node_type>(curr));
                    if (!result.inserted)
                    {
                        CARB_ASSERT(!AllowMulti); // Should have succeeded
                        CARB_ASSERT(source_prev->next() == next_node); // Concurrent operations are bad here

                        curr->init(old_order_key);
                        CARB_ASSERT(old_order_key >= source_prev->getOrderKey() &&
                                    (!next_node || old_order_key <= next_node->getOrderKey()));

                        curr->setNext(next_node);
                        source_prev->setNext(curr);
                        source_prev = curr;
                        node_handle_accessor::deactivate(result.node);
                    }
                    else
                        source.m_size.fetch_sub(1, std::memory_order_relaxed);
                }
                else
                    source_prev = curr;
            }
            else
                source_prev = source_prev->next();
        }
    }

private:
    template <class Container, class Value>
    friend class SListIterator;
    template <class OtherTraits>
    friend class ConcurrentUnorderedBase;

    static constexpr size_type kEmbeddedPointerCount = sizeof(size_type) * 8 - 1;

    class PartitionTable
        : public PartitionTableBase<std::atomic<NodePtr>, allocator_type, PartitionTable, kEmbeddedPointerCount>
    {
        using AtomicNodePtr = std::atomic<NodePtr>;
        using BaseType = PartitionTableBase<AtomicNodePtr, allocator_type, PartitionTable, kEmbeddedPointerCount>;
        using BaseAllocatorType = typename BaseType::allocator_type;
        using PartitionAllocatorType = typename AllocatorTraitsType::template rebind_alloc<AtomicNodePtr>;
        using PartitionAllocatorTraits = std::allocator_traits<PartitionAllocatorType>;
        using PartitionType = typename BaseType::PartitionType;

    public:
        static constexpr bool kAllowTableExtending = false;
        static constexpr bool kIsNoexceptAssignment =
            std::conjunction<std::is_nothrow_move_assignable<hasher>,
                             std::is_nothrow_move_assignable<key_equal>,
                             typename PartitionAllocatorTraits::is_always_equal>::value;
        static constexpr bool kIsNoexceptSwap =
            std::conjunction<std::is_nothrow_swappable<hasher>,
                             std::is_nothrow_swappable<key_equal>,
                             typename PartitionAllocatorTraits::is_always_equal>::value;

        PartitionTable(const BaseAllocatorType& alloc = BaseAllocatorType()) : BaseType(alloc)
        {
        }

        PartitionTable(const PartitionTable&) = default;

        PartitionTable(const PartitionTable& other, const BaseAllocatorType& alloc) : BaseType(other, alloc)
        {
        }

        PartitionTable(PartitionTable&&) = default;

        PartitionTable(PartitionTable&& other, const BaseAllocatorType& alloc) : BaseType(std::move(other), alloc)
        {
        }

        PartitionTable& operator=(const PartitionTable& other) = default;
        PartitionTable& operator=(PartitionTable&& other) = default;

        PartitionType createPartition(typename BaseType::PartitionTableType,
                                      typename BaseType::PartitionIndexType part_index,
                                      size_type)
        {
            PartitionAllocatorType alloc(this->get_allocator());
            size_type seg_size = this->partitionSize(part_index);
            PartitionType new_part = PartitionAllocatorTraits::allocate(alloc, seg_size);
            for (size_type i = 0; i != seg_size; ++i)
                PartitionAllocatorTraits::construct(alloc, new_part + i, nullptr);
            return new_part;
        }

        PartitionType nullifyPartition(typename BaseType::PartitionTableType table, size_type part_index)
        {
            PartitionType target_part = table[part_index].load(std::memory_order_relaxed);
            table[part_index].store(nullptr, std::memory_order_relaxed);
            return target_part;
        }

        void deallocPartition(PartitionType address, size_type index)
        {
            destroyPartition(address, index);
        }

        void destroyPartition(PartitionType address, size_type index)
        {
            PartitionAllocatorType alloc(this->get_allocator());
            for (size_type i = 0; i != this->partitionSize(index); ++i)
                PartitionAllocatorTraits::destroy(alloc, address + i);
            PartitionAllocatorTraits::deallocate(alloc, address, this->partitionSize(index));
        }

        void copyPartition(size_type index, PartitionType, PartitionType to)
        {
            if (index == 0)
            {
                // The first element in the first partition is embedded into the table (m_head), so it shouldn't be
                // stored here; it's stored during copy/move
                to[1].store(nullptr, std::memory_order_relaxed);
            }
            else
            {
                for (size_type i = 0; i != this->partitionSize(index); ++i)
                    to[i].store(nullptr, std::memory_order_relaxed);
            }
        }

        void movePartition(size_type index, PartitionType from, PartitionType to)
        {
            if (index == 0)
            {
                // The first element in the first partition is embedded into the table (m_head), so it shouldn't be
                // stored here; it's stored during copy/move
                to[1].store(from[1].load(std::memory_order_relaxed), std::memory_order_relaxed);
            }
            else
            {
                for (size_type i = 0; i != this->partitionSize(index); ++i)
                {
                    to[i].store(from[i].load(std::memory_order_relaxed), std::memory_order_relaxed);
                    from[i].store(nullptr, std::memory_order_relaxed);
                }
            }
        }

        typename BaseType::PartitionTableType allocateLongTable(const typename BaseType::AtomicPartitionType*, size_type)
        {
            CARB_ASSERT(false); // not allowed
            return nullptr;
        }

        void destroyElements() // required but unused
        {
        }

    private:
        using SelfType = PartitionTable;
    };

    void _clear()
    {
        NodePtr curr = m_head.next(), next;

        m_head.setNext(nullptr);

        for (; curr; curr = next)
        {
            next = curr->next();
            destroyNode(curr);
        }

        m_size.store(0, std::memory_order_relaxed);
        m_partitions.clear();
    }

    void _destroyHoleNode(NodePtr node)
    {
        CARB_ASSERT(node->isHole());
        NodeAllocatorType alloc(m_partitions.get_allocator());
        NodeAllocatorTraits::destroy(alloc, node);
        NodeAllocatorTraits::deallocate(alloc, node, 1);
    }

    void destroyNode(NodePtr node)
    {
        if (node->isHole())
        {
            _destroyHoleNode(node);
        }
        else
        {
            auto val_node = static_cast<ValueNodePtr>(node);
            ValueNodeAllocatorType alloc(m_partitions.get_allocator());
            ValueNodeAllocatorTraits::destroy(alloc, val_node->storage());
            ValueNodeAllocatorTraits::destroy(alloc, val_node);
            ValueNodeAllocatorTraits::deallocate(alloc, val_node, 1);
        }
    }

    struct InsertResult
    {
        ValueNodePtr remaining_node;
        ValueNodePtr node_with_equal_key;
        bool inserted;
    };

    template <class ValueType>
    std::pair<iterator, bool> _insertValue(ValueType&& value)
    {
        auto create_value_node = [&value, this](KeyType order_key) -> ValueNodePtr {
            return _createValueNode(order_key, std::forward<ValueType>(value));
        };

        auto insert_result = _insert(value, create_value_node);

        if (insert_result.remaining_node)
        {
            CARB_ASSERT(!insert_result.inserted);
            destroyNode(insert_result.remaining_node);
        }

        return { iterator(insert_result.node_with_equal_key), insert_result.inserted };
    }

    insert_return_type _insertNode(node_type&& node)
    {
        if (!node.empty())
        {
            ValueNodePtr insert_node = node_handle_accessor::getNodePtr(node);
            auto init_node = [&insert_node](KeyType order_key) -> ValueNodePtr {
                insert_node->init(order_key);
                return insert_node;
            };
            auto insert_result = _insert(insert_node->value(), init_node);
            if (insert_result.inserted)
            {
                CARB_ASSERT(insert_result.remaining_node == nullptr);
                node_handle_accessor::deactivate(node);
            }
            return { iterator(insert_result.node_with_equal_key), insert_result.inserted, std::move(node) };
        }
        return { end(), false, std::move(node) };
    }

    template <class ValueType, class CreateInsertNode>
    InsertResult _insert(ValueType&& value, CreateInsertNode create_insert_node)
    {
        static_assert(std::is_same<typename std::decay_t<ValueType>, value_type>::value, "Incorrect type");
        const key_type& key = TraitsType::get_key(value);
        KeyType hash_key = KeyType(m_pair.first()(key));

        KeyType order_key = _splitOrderKeyRegular(hash_key);
        NodePtr prev = _prepareBucket(hash_key);
        CARB_ASSERT(prev);

        auto search_result = _searchAfter(prev, order_key, key);

        if (search_result.second)
            return InsertResult{ nullptr, search_result.first, false };

        ValueNodePtr new_node = create_insert_node(order_key);
        NodePtr curr = search_result.first;

        while (!_tryInsert(prev, new_node, curr))
        {
            search_result = _searchAfter(prev, order_key, key);
            if (search_result.second)
                return InsertResult{ new_node, search_result.first, false };
            curr = search_result.first;
        }

        auto size = m_size.fetch_add(1);
        _modifyTableSize(size + 1, m_bucketCount.load(std::memory_order_acquire));
        return InsertResult{ nullptr, static_cast<ValueNodePtr>(new_node), true };
    }

    template <class... Args>
    std::pair<iterator, bool> _emplace(Args&&... args)
    {
        ValueNodePtr insert_node = _createValueNode(0, std::forward<Args>(args)...);

        auto init_node = [&insert_node](KeyType order_key) -> ValueNodePtr {
            insert_node->init(order_key);
            return insert_node;
        };

        auto insert_result = _insert(insert_node->value(), init_node);

        if (!insert_result.inserted)
        {
            insert_node->init(_splitOrderKeyRegular(1));
            destroyNode(insert_node);
        }

        return { iterator(insert_result.node_with_equal_key), insert_result.inserted };
    }

    std::pair<ValueNodePtr, bool> _searchAfter(NodePtr& prev, KeyType order_key, const key_type& key)
    {
        NodePtr curr = prev->next();

        while (curr != nullptr && (curr->getOrderKey() < order_key ||
                                   (curr->getOrderKey() == order_key &&
                                    !m_pair.first()(TraitsType::get_key(static_cast<ValueNodePtr>(curr)->value()), key))))
        {
            prev = curr;
            curr = curr->next();
        }

        bool const found = curr != nullptr && curr->getOrderKey() == order_key && !AllowMulti;
        return { static_cast<ValueNodePtr>(curr), found };
    }

    void _modifyTableSize(size_type total_elements, size_type current_size)
    {
        // Double table if possible
        if ((float(total_elements) / float(current_size)) > m_pair.second)
            m_bucketCount.compare_exchange_strong(current_size, 2u * current_size);
    }

    NodePtr _insertHoleNode(NodePtr parentHole, KeyType order_key)
    {
        NodePtr prevNode = parentHole;

        NodePtr holeNode = _createHoleNode(order_key);
        NodePtr nextNode;

        do
        {
            nextNode = prevNode->next();
            // Walk through the list while the order key is less than requested
            while (nextNode && nextNode->getOrderKey() < order_key)
            {
                prevNode = std::exchange(nextNode, nextNode->next());
            }

            if (nextNode && nextNode->getOrderKey() == order_key)
            {
                // Already inserted by another thread => destroy node and exit
                _destroyHoleNode(holeNode);
                return nextNode;
            }
        } while (!_tryInsert(prevNode, holeNode, nextNode));

        return holeNode;
    }

    static bool _tryInsert(NodePtr prev_node, NodePtr new_node, NodePtr current_next_node)
    {
        new_node->setNext(current_next_node);
        return prev_node->trySetNext(current_next_node, new_node);
    }

    NodePtr _prepareBucket(KeyType hash_key)
    {
        size_type bucket = hash_key % m_bucketCount.load(std::memory_order_acquire);
        return _getBucket(bucket);
    }

    NodePtr _getBucket(size_type bucket_index)
    {
        if (!m_partitions[bucket_index].load(std::memory_order_acquire))
            _initBucket(bucket_index);
        return m_partitions[bucket_index].load(std::memory_order_acquire);
    }

    void _initBucket(size_type bucket)
    {
        // First bucket goes to m_head
        if (bucket == 0)
        {
            NodePtr prev = nullptr;
            m_partitions[0].compare_exchange_strong(prev, &m_head);
            return;
        }

        size_type parent_bucket = _getParent(bucket);

        while (!m_partitions[parent_bucket].load(std::memory_order_acquire))
            _initBucket(parent_bucket);

        CARB_ASSERT(m_partitions[parent_bucket].load(std::memory_order_acquire));
        NodePtr parent = m_partitions[parent_bucket].load(std::memory_order_acquire);

        NodePtr holeNode = _insertHoleNode(parent, _splitOrderKeyHole(bucket));
        m_partitions[bucket].store(holeNode, std::memory_order_release);
    }

    NodePtr _createHoleNode(KeyType order_key)
    {
        NodeAllocatorType alloc(m_partitions.get_allocator());
        NodePtr hole = NodeAllocatorTraits::allocate(alloc, 1);
        NodeAllocatorTraits::construct(alloc, hole, order_key);
        return hole;
    }

    template <class... Args>
    ValueNodePtr _createValueNode(KeyType order_key, Args&&... args)
    {
        ValueNodeAllocatorType alloc(m_partitions.get_allocator());
        ValueNodePtr new_node = ValueNodeAllocatorTraits::allocate(alloc, 1);
        ValueNodeAllocatorTraits::construct(alloc, new_node, order_key);

        CARBLOCAL_TRY_BEGIN
        {
            ValueNodeAllocatorTraits::construct(alloc, new_node->storage(), std::forward<Args>(args)...);
        }
        CARBLOCAL_CATCH_ALL
        {
            ValueNodeAllocatorTraits::destroy(alloc, new_node);
            ValueNodeAllocatorTraits::deallocate(alloc, new_node, 1);
        }

        return new_node;
    }

    ValueNodePtr _firstValueNode(NodePtr first_node) const noexcept
    {
        while (first_node != nullptr && first_node->isHole())
            first_node = first_node->next();
        return static_cast<ValueNodePtr>(first_node);
    }

    NodePtr _erase(ValueNodePtr node_to_erase)
    {
        CARB_ASSERT(node_to_erase);
        NodePtr next = node_to_erase->next();
        _extract(node_to_erase);
        destroyNode(node_to_erase);
        return next;
    }

    template <class K>
    size_type _keyErase(const K& key)
    {
        auto range = equal_range(key);
        size_type erased = 0;

        for (auto it = range.first; it != range.second;)
        {
            it = unsafe_erase(it);
            ++erased;
        }
        return erased;
    }

    void _extract(ValueNodePtr node_to_extract)
    {
        const key_type& key = TraitsType::get_key(node_to_extract->value());
        KeyType hash_key = KeyType(m_pair.first()(key));

        NodePtr prev = _prepareBucket(hash_key);

        for (auto node = prev->next(); node; prev = node, node = node->next())
        {
            if (node == node_to_extract)
            {
                _unlinkNode(prev, node, node_to_extract->next());
                m_size.store(m_size.load(std::memory_order_relaxed) - 1, std::memory_order_relaxed);
                return;
            }
            CARB_ASSERT(node->getOrderKey() <= node_to_extract->getOrderKey());
        }
    }

    void _unlinkNode(NodePtr prev_node, NodePtr node_to_unlink, NodePtr next_node)
    {
        CARB_ASSERT(
            prev_node->next() == node_to_unlink && node_to_unlink->next() == next_node, "Unsafe in concurrent mode");
        prev_node->setNext(next_node);
        node_to_unlink->setNext(nullptr);
    }

    template <class K>
    ValueNodePtr _find(const K& key)
    {
        KeyType hash_key = KeyType(m_pair.first()(key));
        KeyType order_key = _splitOrderKeyRegular(hash_key);

        for (NodePtr curr = _prepareBucket(hash_key); curr; curr = curr->next())
        {
            if (curr->getOrderKey() > order_key)
                return nullptr; // not in the table
            else if (curr->getOrderKey() == order_key &&
                     m_pair.first()(TraitsType::get_key(static_cast<ValueNodePtr>(curr)->value()), key))
            {
                return static_cast<ValueNodePtr>(curr);
            }
        }
        return nullptr;
    }

    template <class K>
    std::pair<ValueNodePtr, ValueNodePtr> _equalRange(const K& key)
    {
        KeyType hash_key = KeyType(m_pair.first()(key));
        KeyType order_key = _splitOrderKeyRegular(hash_key);

        for (NodePtr curr = _prepareBucket(hash_key); curr; curr = curr->next())
        {
            if (curr->getOrderKey() > order_key)
                return { nullptr, nullptr }; // not in the table
            else if (curr->getOrderKey() == order_key &&
                     m_pair.first()(TraitsType::get_key(static_cast<ValueNodePtr>(curr)->value()), key))
            {
                ValueNodePtr first = static_cast<ValueNodePtr>(curr);
                NodePtr last = first;
                do
                {
                    last = last->next();
                } while (AllowMulti && last != nullptr && !last->isHole() &&
                         m_pair.first()(TraitsType::get_key(static_cast<ValueNodePtr>(last)->value()), key));
                return { first, _firstValueNode(last) };
            }
        }
        return { nullptr, nullptr };
    }

    template <class K>
    size_type _count(const K& key) const
    {
        if (AllowMulti)
        {
            auto range = equal_range(key);
            return std::distance(range.first, range.second);
        }
        return contains(key) ? 1 : 0;
    }

    void _copy(const ConcurrentUnorderedBase& other)
    {
        NodePtr last_node = &m_head;
        m_partitions[0].store(&m_head, std::memory_order_relaxed);

        for (NodePtr node = other.m_head.next(); node; node = node->next())
        {
            NodePtr new_node;
            if (!node->isHole())
                new_node = _createValueNode(node->getOrderKey(), static_cast<ValueNodePtr>(node)->value());
            else
            {
                new_node = _createHoleNode(node->getOrderKey());
                m_partitions[cpp::detail::reverse_bits(node->getOrderKey())].store(new_node, std::memory_order_relaxed);
            }

            last_node->setNext(new_node);
            last_node = new_node;
        }
    }

    void _move(ConcurrentUnorderedBase&& other)
    {
        NodePtr last_node = &m_head;
        m_partitions[0].store(&m_head, std::memory_order_relaxed);

        for (NodePtr node = other.m_head.next(); node; node = node->next())
        {
            NodePtr new_node;
            if (!node->isHole())
                new_node = _createValueNode(node->getOrderKey(), std::move(static_cast<ValueNodePtr>(node)->value()));
            else
            {
                new_node = _createHoleNode(node->getOrderKey());
                m_partitions[cpp::detail::reverse_bits(node->getOrderKey())].store(new_node, std::memory_order_relaxed);
            }

            last_node->setNext(new_node);
            last_node = new_node;
        }
    }

    void _moveContent(ConcurrentUnorderedBase&& other)
    {
        m_head.setNext(other.m_head.next());
        other.m_head.setNext(nullptr);
        m_partitions[0].store(&m_head, std::memory_order_relaxed);

        other.m_bucketCount.store(kInitialBucketCount, std::memory_order_relaxed);
        other.m_pair.second = kInitialMaxLoadFactor;
        other.m_size.store(0, std::memory_order_relaxed);
    }

    void _moveConstructWithAlloc(ConcurrentUnorderedBase&& other, const allocator_type&, std::true_type)
    {
        _moveContent(std::move(other));
    }

    void _moveConstructWithAlloc(ConcurrentUnorderedBase&& other, const allocator_type& alloc, std::false_type)
    {
        if (alloc == other.m_partitions.get_allocator())
            _moveContent(std::move(other));
        else
        {
            CARBLOCAL_TRY_BEGIN
            {
                _move(std::move(other));
            }
            CARBLOCAL_CATCH_ALL
            {
                clear();
            }
        }
    }

    void _moveAssign(ConcurrentUnorderedBase&& other, std::true_type)
    {
        _moveContent(std::move(other));
    }

    void _moveAssign(ConcurrentUnorderedBase&& other, std::false_type)
    {
        if (m_partitions.get_allocator() == other.m_partitions.get_allocator())
            _moveContent(std::move(other));
        else
        {
            CARBLOCAL_TRY_BEGIN
            {
                _move(std::move(other));
            }
            CARBLOCAL_CATCH_ALL
            {
                clear();
            }
        }
    }

    void _swap(ConcurrentUnorderedBase& other, std::true_type)
    {
        _swapMembers(other);
    }

    void _swap(ConcurrentUnorderedBase& other, std::false_type)
    {
        CARB_ASSERT(m_partitions.get_allocator() == other.get_allocator(), "Equal allocators required");
        _swapMembers(other);
    }

    void _swapMembers(ConcurrentUnorderedBase& other)
    {
        NodePtr first_node = m_head.next();
        m_head.setNext(other.m_head.next());
        other.m_head.setNext(first_node);

        size_type current_size = m_size.load(std::memory_order_relaxed);
        m_size.store(other.m_size.load(std::memory_order_relaxed), std::memory_order_relaxed);
        other.m_size.store(current_size, std::memory_order_relaxed);

        size_type bucket_count = m_bucketCount.load(std::memory_order_relaxed);
        m_bucketCount.store(other.m_bucketCount.load(std::memory_order_relaxed), std::memory_order_relaxed);
        other.m_bucketCount.store(bucket_count, std::memory_order_relaxed);

        using std::swap;
        swap(m_pair.first(), other.m_pair.first());
        swap(m_pair.second, other.m_pair.second);
        m_partitions.swap(other.m_partitions);

        m_partitions[0].store(&m_head, std::memory_order_relaxed);
        other.m_partitions[0].store(&other.m_head, std::memory_order_relaxed);
    }

    static constexpr KeyType _splitOrderKeyRegular(KeyType hash)
    {
        return cpp::detail::reverse_bits(hash) | 1;
    }

    static constexpr KeyType _splitOrderKeyHole(KeyType hash)
    {
        return cpp::detail::reverse_bits(hash) & ~KeyType(1);
    }

    size_type _getParent(size_type bucket) const
    {
        CARB_ASSERT(bucket != 0);
        return bucket & ~(size_type(1) << cpp::detail::log2(bucket)); // Turn off bucket's highest bit
    }

    size_type _getNextBucketIndex(size_type bucket) const
    {
        size_type bits = cpp::detail::log2(m_bucketCount.load(std::memory_order_relaxed));
        size_type reversed = cpp::detail::reverse_n_bits(bucket, bits) + 1;
        return cpp::detail::reverse_n_bits(reversed, bits);
    }

    static constexpr size_type kInitialBucketCount = 8;
    static constexpr float kInitialMaxLoadFactor = 4;

    std::atomic<size_type> m_size;
    std::atomic<size_type> m_bucketCount;
    EmptyMemberPair<HashCompareType, float /* max_load_factor */> m_pair;
    ListNodeType m_head;
    PartitionTable m_partitions;
};

template <class Traits>
bool operator==(const ConcurrentUnorderedBase<Traits>& lhs, const ConcurrentUnorderedBase<Traits>& rhs)
{
    if (&lhs == &rhs)
        return true;
    if (lhs.size() != rhs.size())
        return false;
    return std::is_permutation(lhs.begin(), lhs.end(), rhs.begin(), rhs.end());
}

template <class Traits>
bool operator!=(const ConcurrentUnorderedBase<Traits>& lhs, const ConcurrentUnorderedBase<Traits>& rhs)
{
    return !(lhs == rhs);
}

} // namespace detail
} // namespace container
} // namespace carb

#include "../../detail/ExceptionEpilog.h"
