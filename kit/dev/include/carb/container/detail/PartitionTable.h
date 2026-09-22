// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include "AllocatorTraits.h"

#include <memory>
#include <stdexcept>
#include <type_traits>

#include "../../cpp/Bit.h"
#include "../../thread/Util.h"

#include "../../detail/ExceptionProlog.h"

namespace carb
{
namespace container
{

//! @cond DEV
namespace detail
{

template <class T, class Allocator, class TDerivedType, std::size_t PointersPerEmbeddedTable>
class PartitionTableBase
{
protected:
    using DerivedType = TDerivedType;

public:
    using value_type = T;
    using PartitionType = T*;
    using AtomicPartitionType = std::atomic<PartitionType>;
    using PartitionTableType = AtomicPartitionType*;

    using size_type = std::size_t;
    using PartitionIndexType = size_type;

    using allocator_type = Allocator;

    using AllocatorTraitsType = std::allocator_traits<allocator_type>;
    using PartitionTableAllocatorType = typename AllocatorTraitsType::template rebind_alloc<AtomicPartitionType>;

    PartitionTableBase(const allocator_type& alloc = allocator_type()) : m_pair(InitBoth{}, alloc, nullptr)
    {
        m_pair.second.store(m_embeddedTable, std::memory_order_relaxed);
        zeroOutTable(m_embeddedTable, kEmbeddedPointerCount);
    }

    PartitionTableBase(const PartitionTableBase& other)
        : m_pair(InitBoth{},
                 PartitionTableAllocatorTraits::select_on_container_copy_construction(other.m_pair.first()),
                 nullptr)
    {
        m_pair.second.store(m_embeddedTable, std::memory_order_relaxed);
        zeroOutTable(m_embeddedTable, kEmbeddedPointerCount);
        CARBLOCAL_TRY_BEGIN
        {
            _transfer(other, CopyBodyType{ *this });
        }
        CARBLOCAL_CATCH_ALL
        {
            clear();
        }
    }

    PartitionTableBase(const PartitionTableBase& other, const allocator_type& alloc)
        : m_pair(InitBoth{}, alloc, nullptr)
    {
        m_pair.second.store(m_embeddedTable, std::memory_order_relaxed);
        zeroOutTable(m_embeddedTable, kEmbeddedPointerCount);
        CARBLOCAL_TRY_BEGIN
        {
            _transfer(other, CopyBodyType{ *this });
        }
        CARBLOCAL_CATCH_ALL
        {
            clear();
        }
    }

    PartitionTableBase(PartitionTableBase&& other) : m_pair(InitBoth{}, std::move(other.m_pair.first()), nullptr)
    {
        m_pair.second.store(m_embeddedTable, std::memory_order_relaxed);
        zeroOutTable(m_embeddedTable, kEmbeddedPointerCount);
        _move(std::move(other));
    }

    PartitionTableBase(PartitionTableBase&& other, const allocator_type& alloc) : m_pair(InitBoth{}, alloc, nullptr)
    {
        m_pair.second.store(m_embeddedTable, std::memory_order_relaxed);
        zeroOutTable(m_embeddedTable, kEmbeddedPointerCount);
        using is_always_equal = typename PartitionTableAllocatorTraits::is_always_equal;
        _moveConstructWithAlloc(std::move(other), alloc, is_always_equal{});
    }

    ~PartitionTableBase()
    {
        clear();
    }

    PartitionTableBase& operator=(const PartitionTableBase& other)
    {
        if (this != &other)
        {
            copy_assign_allocators(m_pair.first(), other.m_pair.first());
            _transfer(other, CopyBodyType{ *this });
        }
        return *this;
    }

    PartitionTableBase& operator=(PartitionTableBase&& other) noexcept(DerivedType::kIsNoexceptAssignment)
    {
        using propagate = typename PartitionTableAllocatorTraits::propagate_on_container_move_assignment;
        using is_always_equal = typename PartitionTableAllocatorTraits::is_always_equal;

        if (this != &other)
        {
            move_assign_allocators(m_pair.first(), other.m_pair.first());
            _moveAssign(std::move(other), std::disjunction<is_always_equal, propagate>{});
        }
        return *this;
    }

    void swap(PartitionTableBase& other) noexcept(DerivedType::kIsNoexceptSwap)
    {
        using propagate = typename PartitionTableAllocatorTraits::propagate_on_container_swap;
        using is_always_equal = typename PartitionTableAllocatorTraits::is_always_equal;

        if (this != &other)
        {
            swap_allocators(m_pair.first(), other.m_pair.first());
            _swap(other, std::disjunction<is_always_equal, propagate>{});
        }
    }

    PartitionType getPartition(PartitionIndexType index) const
    {
        return getTable()[index] + partitionBase(index);
    }

    value_type& operator[](size_type index)
    {
        return subscript<true>(index);
    }

    const value_type& operator[](size_type index) const
    {
        return const_cast<PartitionTableBase*>(this)->subscript<true>(index);
    }

    PartitionTableAllocatorType& get_allocator()
    {
        return m_pair.first();
    }

    const PartitionTableAllocatorType& get_allocator() const
    {
        return m_pair.first();
    }

    void enablePartition(PartitionType& partition, PartitionTableType table, PartitionIndexType part_index, size_type index)
    {
        if (PartitionType newPartition = self()->createPartition(table, part_index, index))
        {
            PartitionType disabled_part = nullptr;
            if (!table[part_index].compare_exchange_strong(disabled_part, newPartition - partitionBase(part_index)))
            {
                self()->deallocPartition(newPartition, part_index);
            }
        }

        partition = table[part_index].load(std::memory_order_acquire);
        CARB_ASSERT(partition);
    }

    void deletePartition(PartitionIndexType part_index)
    {
        PartitionType del = self()->nullifyPartition(getTable(), part_index);
        if (del == kPartitionAllocationFailure)
            return;

        del += partitionBase(part_index);

        self()->destroyPartition(del, part_index);
    }

    size_type partitionCount(PartitionTableType table) const
    {
        return table == m_embeddedTable ? kEmbeddedPointerCount : kPointersPerLongTable;
    }

    size_type capacity() const noexcept
    {
        PartitionTableType table = getTable();
        size_type numPartitions = partitionCount(table);
        for (size_type part_index = 0; part_index != numPartitions; ++part_index)
        {
            // Check if allocated
            if (table[part_index].load(std::memory_order_relaxed) <= kPartitionAllocationFailure)
                return partitionBase(part_index);
        }
        return partitionBase(numPartitions);
    }

    size_type findLastAllocatedPartition(PartitionTableType table) const noexcept
    {
        size_type end = 0;
        size_type numPartitions = partitionCount(table);
        for (size_type part_index = 0; part_index != numPartitions; ++part_index)
        {
            // Check if allocated
            if (table[part_index].load(std::memory_order_relaxed) > kPartitionAllocationFailure)
                end = part_index + 1;
        }
        return end;
    }

    void reserve(size_type n)
    {
        if (n > AllocatorTraitsType::max_size(m_pair.first()))
            CARBLOCAL_THROW(std::length_error, "Exceeded allocator length limits");

        size_type const size = m_size.load(std::memory_order_relaxed);
        PartitionIndexType const start_part_idx = size == 0 ? 0 : partitionIndexOf(size - 1) + 1;
        for (PartitionIndexType part_idx = start_part_idx; partitionBase(part_idx) < n; ++part_idx)
        {
            subscript<true>(partitionBase(part_idx)); // access to create
        }
    }

    void clear()
    {
        clearPartitions();
        clearTable();
        m_size.store(0, std::memory_order_relaxed);
        m_firstBlock.store(0, std::memory_order_relaxed);
    }

    void clearPartitions()
    {
        PartitionTableType current = getTable();
        for (size_type i = partitionCount(current); i != 0; --i)
        {
            if (current[i - 1].load(std::memory_order_relaxed))
                deletePartition(i - 1);
        }
    }

    void clearTable()
    {
        PartitionTableType current = getTable();
        if (current != m_embeddedTable)
        {
            // If the active table is not the embedded one, delete the active table
            for (size_type i = 0; i != kPointersPerLongTable; ++i)
            {
                PartitionTableAllocatorTraits::destroy(m_pair.first(), &current[i]);
            }

            PartitionTableAllocatorTraits::deallocate(m_pair.first(), current, kPointersPerLongTable);
            m_pair.second.store(m_embeddedTable, std::memory_order_relaxed);
            zeroOutTable(m_embeddedTable, kEmbeddedPointerCount);
        }
    }

    void ensureTable(PartitionTableType& table, size_type start_index, size_type end_index)
    {
        // extend the partition table if active is embedded and the index doesn't fit in the embedded table.
        if (table == m_embeddedTable && end_index > kEmbeddedTableSize)
        {
            if (start_index <= kEmbeddedTableSize)
            {
                CARBLOCAL_TRY_BEGIN
                {
                    table = self()->allocateLongTable(m_embeddedTable, start_index);

                    // If another thread beat us to it, reload the table.
                    if (table)
                        m_pair.second.store(table, std::memory_order_release);
                    else
                        table = m_pair.second.load(std::memory_order_acquire);
                }
                CARBLOCAL_CATCH_ALL
                {
                    m_allocFailed.store(true, std::memory_order_relaxed);
                }
            }
            else
            {
                thread::AtomicBackoff<> backoff;
                do
                {
                    if (m_allocFailed.load(std::memory_order_relaxed))
                        CARBLOCAL_THROW0(std::bad_alloc);
                    backoff.pause();
                    table = m_pair.second.load(std::memory_order_acquire);
                } while (table == m_embeddedTable);
            }
        }
    }

    static constexpr PartitionIndexType partitionIndexOf(size_type index)
    {
        return size_type(::carb::cpp::detail::log2(size_type(index | 1)));
    }

    static constexpr size_type partitionBase(size_type index)
    {
        return size_type(1) << index & ~size_type(1);
    }

    static constexpr size_type partitionSize(size_type index)
    {
        return index == 0 ? 2 : size_type(1) << index;
    }

private:
    DerivedType* self()
    {
        return static_cast<DerivedType*>(this);
    }

    struct CopyBodyType
    {
        void operator()(PartitionIndexType index, PartitionType from, PartitionType to) const
        {
            m_table.self()->copyPartition(index, from, to);
        }
        PartitionTableBase& m_table;
    };

    struct MoveBodyType
    {
        void operator()(PartitionIndexType index, PartitionType from, PartitionType to) const
        {
            m_table.self()->movePartition(index, from, to);
        }
        PartitionTableBase& m_table;
    };

    template <class TransferBody>
    void _transfer(const PartitionTableBase& other, TransferBody transfer_part)
    {
        self()->destroyElements();

        ensureFirstBlock(other.m_firstBlock.load(std::memory_order_relaxed));
        m_size.store(other.m_size.load(std::memory_order_relaxed), std::memory_order_relaxed);

        PartitionTableType other_table = other.getTable();
        size_type end_part_size = partitionSize(other.findLastAllocatedPartition(other_table));

        // If an exception occurred in other, then the size may be greater than the size of the end partition
        size_type other_size = end_part_size < other.m_size.load(std::memory_order_relaxed) ?
                                   other.m_size.load(std::memory_order_relaxed) :
                                   end_part_size;
        other_size = m_allocFailed ? kEmbeddedTableSize : other_size;

        for (PartitionIndexType i = 0; partitionBase(i) < other_size; ++i)
        {
            // If the partition in the other table is enabled, transfer it
            if (other_table[i].load(std::memory_order_relaxed) == kPartitionAllocationFailure)
            {
                m_size = partitionBase(i);
                break;
            }
            else if (other_table[i].load(std::memory_order_relaxed) != nullptr)
            {
                subscript<true>(partitionBase(i));
                transfer_part(i, other.getTable()[i].load(std::memory_order_relaxed) + partitionBase(i),
                              getTable()[i].load(std::memory_order_relaxed) + partitionBase(i));
            }
        }
    }

    void _move(PartitionTableBase&& other)
    {
        clear();
        m_firstBlock.store(other.m_firstBlock.load(std::memory_order_relaxed), std::memory_order_relaxed);
        m_size.store(other.m_size.load(std::memory_order_relaxed), std::memory_order_relaxed);

        // If an active table in `other` is embedded, restore all of the embedded partitions
        if (other.getTable() == other.m_embeddedTable)
        {
            for (size_type i = 0; i != kEmbeddedPointerCount; ++i)
            {
                PartitionType other_part = other.m_embeddedTable[i].load(std::memory_order_relaxed);
                m_embeddedTable[i].store(other_part, std::memory_order_relaxed);
                other.m_embeddedTable[i].store(nullptr, std::memory_order_relaxed);
            }
            m_pair.second.store(m_embeddedTable, std::memory_order_relaxed);
        }
        else
        {
            m_pair.second.store(other.m_pair.second, std::memory_order_relaxed);
            other.m_pair.second.store(other.m_embeddedTable, std::memory_order_relaxed);
            zeroOutTable(other.m_embeddedTable, kEmbeddedPointerCount);
        }
        other.m_size.store(0, std::memory_order_relaxed);
    }

    void _moveConstructWithAlloc(PartitionTableBase&& other,
                                 const allocator_type&,
                                 /*is_always_equal*/ std::true_type)
    {
        _move(std::move(other));
    }

    void _moveConstructWithAlloc(PartitionTableBase&& other, const allocator_type& alloc, std::false_type)
    {
        if (other.m_pair.first() == alloc)
        {
            // Allocators are equal, normal move
            _move(std::move(other));
        }
        else // Not equal, need allocation
        {
            CARBLOCAL_TRY_BEGIN
            {
                _transfer(other, MoveBodyType{ *this });
            }
            CARBLOCAL_CATCH_ALL
            {
                clear();
            }
        }
    }

    void _moveAssign(PartitionTableBase&& other, std::true_type)
    {
        _move(std::move(other));
    }

    void _moveAssign(PartitionTableBase&& other, std::false_type)
    {
        if (m_pair.first() == other.m_pair.first())
        {
            // Allocators are equal, normal move
            _move(std::move(other));
        }
        else // Not equal, need allocation
        {
            _transfer(other, MoveBodyType{ *this });
        }
    }

    void _swap(PartitionTableBase& other, std::true_type)
    {
        _swapMembers(other);
    }

    void _swap(PartitionTableBase& other, std::false_type)
    {
        CARB_ASSERT(m_pair.first() == other.m_pair.first(), "Swapping with unequal allocators is not allowed");
        _swapMembers(other);
    }

    void _swapMembers(PartitionTableBase& other)
    {
        // Need to swap the embedded tables if the active table in *this or `other` is embedded
        if (getTable() == m_embeddedTable || other.getTable() == other.m_embeddedTable)
        {
            for (size_type i = 0; i != kEmbeddedPointerCount; ++i)
            {
                PartitionType current_part = m_embeddedTable[i].load(std::memory_order_relaxed);
                PartitionType other_part = other.m_embeddedTable[i].load(std::memory_order_relaxed);

                m_embeddedTable[i].store(other_part, std::memory_order_relaxed);
                other.m_embeddedTable[i].store(current_part, std::memory_order_relaxed);
            }
        }

        PartitionTableType current_part_table = getTable();
        PartitionTableType other_part_table = other.getTable();

        // If an active table is an embedded one, store an active table in other to the embedded one from other
        if (current_part_table == m_embeddedTable)
            other.m_pair.second.store(other.m_embeddedTable, std::memory_order_relaxed);
        else
            other.m_pair.second.store(current_part_table, std::memory_order_relaxed);

        if (other_part_table == other.m_embeddedTable)
            m_pair.second.store(m_embeddedTable, std::memory_order_relaxed);
        else
            m_pair.second.store(other_part_table, std::memory_order_relaxed);

        auto first_block = other.m_firstBlock.load(std::memory_order_relaxed);
        other.m_firstBlock.store(m_firstBlock.load(std::memory_order_relaxed), std::memory_order_relaxed);
        m_firstBlock.store(first_block, std::memory_order_relaxed);

        auto size = other.m_size.load(std::memory_order_relaxed);
        other.m_size.store(m_size.load(std::memory_order_relaxed), std::memory_order_relaxed);
        m_size.store(size, std::memory_order_relaxed);
    }

protected:
    using PartitionTableAllocatorTraits = std::allocator_traits<PartitionTableAllocatorType>;

    static constexpr size_type kEmbeddedPointerCount = PointersPerEmbeddedTable;
    static constexpr size_type kPointersPerLongTable = sizeof(size_type) * 8;

    const PartitionType kPartitionAllocationFailure = reinterpret_cast<PartitionType>(1);
    static constexpr size_type kEmbeddedTableSize = partitionSize(kEmbeddedPointerCount);

    template <bool AllowOutOfRange>
    value_type& subscript(size_type index)
    {
        PartitionIndexType part_index = partitionIndexOf(index);
        PartitionTableType table = m_pair.second.load(std::memory_order_acquire);
        PartitionType part = nullptr;

        if (AllowOutOfRange)
        {
            if (DerivedType::kAllowTableExtending)
                ensureTable(table, index, index + 1);

            part = table[part_index].load(std::memory_order_acquire);
            // Disabled? => enable
            if (!part)
                enablePartition(part, table, part_index, index);

            // Throw on allocation failure
            if (part == kPartitionAllocationFailure)
                CARBLOCAL_THROW0(std::bad_alloc);
        }
        else
            part = table[part_index].load(std::memory_order_acquire);

        CARB_ASSERT(part);
        return part[index];
    }

    void ensureFirstBlock(PartitionIndexType index)
    {
        size_type zero = 0;
        if (m_firstBlock.load(std::memory_order_relaxed) == zero)
            m_firstBlock.compare_exchange_strong(zero, index); // allowed to fail
    }

    static void zeroOutTable(PartitionTableType table, size_type count)
    {
        for (size_type i = 0; i != count; ++i)
            table[i].store(nullptr, std::memory_order_relaxed);
    }

    PartitionTableType getTable() const
    {
        return m_pair.second.load(std::memory_order_acquire);
    }

    EmptyMemberPair<PartitionTableAllocatorType, std::atomic<PartitionTableType>> m_pair;
    AtomicPartitionType m_embeddedTable[kEmbeddedPointerCount];
    std::atomic<size_type> m_firstBlock{ 0 };
    std::atomic<size_type> m_size{ 0 };
    std::atomic_bool m_allocFailed{ false };
};

} // namespace detail
//! @endcond
} // namespace container
} // namespace carb

#include "../../detail/ExceptionEpilog.h"
