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
#include "AllocatorTraits.h"

namespace carb
{
namespace container
{

//! \cond DEV
namespace detail
{

struct node_handle_accessor
{
    template <class NodeHandleType>
    static typename NodeHandleType::node* getNodePtr(NodeHandleType& handle)
    {
        return handle.getNodePtr();
    }

    template <class NodeHandleType>
    static NodeHandleType construct(typename NodeHandleType::node* ptr)
    {
        return NodeHandleType(ptr);
    }

    template <class NodeHandleType>
    static void deactivate(NodeHandleType& handle)
    {
        handle.deactivate();
    }
};

template <class Value, class Node, class Allocator>
class node_handle_base
{
public:
    using allocator_type = Allocator;

    node_handle_base() : m_members(ValueInitFirst{}, nullptr)
    {
    }
    node_handle_base(node_handle_base&& other)
        : m_members(InitBoth{}, std::move(other.m_members.first()), std::exchange(other.m_members.second, nullptr))
    {
    }
    ~node_handle_base()
    {
        _destroy();
    }

    node_handle_base& operator=(node_handle_base&& other)
    {
        _destroy();
        m_members.second = other.m_members.second;
        move_assign_allocators(m_members.first(), other.m_members.first());
        other.deactivate();
        return *this;
    }

    [[nodiscard]] bool empty() const noexcept
    {
        return m_members.second == nullptr;
    }

    explicit operator bool() const noexcept
    {
        return !empty();
    }

    void swap(node_handle_base& other)
    {
        using std::swap;
        swap_allocators(m_members.first(), other.m_members.first());
        swap(m_members.second, other.m_members.second);
    }

    allocator_type get_allocator() const
    {
        return m_members.first();
    }

protected:
    using node = Node;
    using AllocatorTraitsType = std::allocator_traits<allocator_type>;

    node_handle_base(node* p) : m_members(ValueInitFirst{}, p)
    {
    }

    void _destroy()
    {
        if (m_members.second)
        {
            AllocatorTraitsType::destroy(m_members.first(), m_members.second->storage());
            typename AllocatorTraitsType::template rebind_alloc<node> node_allocator(m_members.first());
            node_allocator.deallocate(m_members.second, 1);
        }
    }

    node* getNodePtr() const noexcept
    {
        return m_members.second;
    }

    void deactivate() noexcept
    {
        m_members.second = nullptr;
    }

    EmptyMemberPair<allocator_type, node*> m_members;
};

template <class Key, class Value, class Node, class Allocator>
class node_handle : public node_handle_base<Value, Node, Allocator>
{
    using BaseType = node_handle_base<Value, Node, Allocator>;

public:
    using key_type = Key;
    using mapped_type = typename Value::second_type;
    using allocator_type = typename BaseType::allocator_type;

    node_handle() = default;

    key_type& key() const noexcept
    {
        CARB_ASSERT(!this->empty());
        return *const_cast<key_type*>(&(this->m_members.second->value().first));
    }

    mapped_type& mapped() const noexcept
    {
        CARB_ASSERT(!this->empty());
        return this->m_members.second->value().second;
    }

private:
    friend struct node_handle_accessor;

    node_handle(typename BaseType::node* p) : BaseType(p)
    {
    }
};

template <class Key, class Node, class Allocator>
class node_handle<Key, Key, Node, Allocator> : public node_handle_base<Key, Node, Allocator>
{
    using BaseType = node_handle_base<Key, Node, Allocator>;

public:
    using value_type = Key;
    using allocator_type = typename BaseType::allocator_type;

    node_handle() = default;

    value_type& value() const
    {
        CARB_ASSERT(!this->empty());
        return *const_cast<value_type*>(&(this->m_members.second->value()));
    }

private:
    friend struct node_handle_accessor;

    node_handle(typename BaseType::node* p) : BaseType(p)
    {
    }
};

template <class Key, class Value, class Node, class Allocator>
void swap(node_handle<Key, Value, Node, Allocator>& lhs, node_handle<Key, Value, Node, Allocator>& rhs)
{
    lhs.swap(rhs);
}

} // namespace detail
//! \endcond

} // namespace container
} // namespace carb
