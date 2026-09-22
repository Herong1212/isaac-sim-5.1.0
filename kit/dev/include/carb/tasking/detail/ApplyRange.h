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
//! \brief carb.tasking parallel algorithm implementation details
#pragma once

#include "../../Defines.h"

#if CARB_VERSION_ATLEAST(carb_tasking_ITasking, 2, 5)
namespace carb
{
namespace tasking
{

//! An empty type used to invoke splitting constructors.
class Split_t
{
};

//! An instantiation of \ref Split_t.
constexpr static Split_t Split{};

// Opaque types outside of carb.tasking
class ThreadLocalStorage;
struct TaskBundle;

//! \cond DEV
namespace detail
{

struct ApplyRangeState;

// ApplyRange interface
class IApplyRange
{
public:
    virtual uint32_t getThreadCount() const noexcept = 0;
    virtual void beginApplyRange(ApplyRangeState& state, void* arg) const noexcept = 0;
    virtual void finishApplyRange(ApplyRangeState& state,
                                  OnTaskFn func,
                                  void* (*resolve)(void*),
                                  std::atomic_bool& wait) const noexcept = 0;
    virtual void queueTask(OnTaskFn func, void* data) const noexcept = 0;
    virtual TaskBundle* currentTask() const noexcept = 0;
    virtual bool isStolen(TaskBundle* tb) const noexcept = 0;
};

using Depth_t = uint8_t;

constexpr Depth_t kInitDepth = 5;
constexpr Depth_t kDemandAddDepth = 1;

constexpr size_t kInitialChunks = 2;

template <class T>
class Range
{
public:
    using const_iterator = T;
    using value_type = T;
    using size_type = size_t;

    constexpr Range(T begin, T end, T step = 1) noexcept : m_end(end), m_begin(begin), m_step(step)
    {
        CARB_ASSERT(m_step > 0);
    }

    constexpr Range(Range& other, Split_t) noexcept : m_end(other.end()), m_begin(split(other)), m_step(other.m_step)
    {
        CARB_ASSERT(!(begin() < other.end()) && !(other.end() < begin()));
    }

    constexpr const_iterator begin() const noexcept
    {
        return m_begin;
    }

    constexpr const_iterator end() const noexcept
    {
        return m_end;
    }

    constexpr size_type size() const noexcept
    {
        return m_end - m_begin;
    }

    constexpr size_type step() const noexcept
    {
        return m_step;
    }

    constexpr bool empty() const noexcept
    {
        // Assume that T is only less-than-comparable
        return !(m_begin < m_end);
    }

    constexpr bool canDivide() const noexcept
    {
        // Assume that T is only less-than-comparable
        return step() < size();
    }

private:
    T m_end;
    T m_begin;
    T m_step;

    static T split(Range& other)
    {
        CARB_ASSERT(other.canDivide());
        auto mid = other.m_begin + (other.m_end - other.m_begin) / size_t(2);
        other.m_end = mid;
        return mid;
    }
};

struct Node
{
    Node* m_parent = nullptr;
    std::atomic_int m_refCount{ 0 };

    Node() = default;
    Node(Node* parent, int refCount) : m_parent(parent), m_refCount(refCount)
    {
        CARB_ASSERT(refCount > 0);
    }
};

struct WaitNode : Node
{
    WaitNode() : Node{ nullptr, 1 }
    {
    }

    std::atomic_bool m_wait{ true };
};

struct TreeNode : public Node
{
    std::atomic_bool m_childStolen{ false };

    TreeNode(Node* parent, int refCount) : Node(parent, refCount)
    {
    }

    template <class Task>
    static void markTaskStolen(Task& t)
    {
        static_cast<TreeNode*>(t.m_parent)->m_childStolen.store(true, std::memory_order_relaxed);
    }

    template <class Task>
    static bool isPeerStolen(Task& t)
    {
        return static_cast<TreeNode*>(t.m_parent)->m_childStolen.load(std::memory_order_relaxed);
    }

    void reduce()
    {
    }
};

template <class Body>
struct ReductionTreeNode : public TreeNode
{
    alignas(alignof(Body)) char m_space[sizeof(Body)];
    Body& m_left;
    bool m_hasRight{ false };

    ReductionTreeNode(Node* parent, int refCount, Body& left) : TreeNode(parent, refCount), m_left(left)
    {
    }
    ~ReductionTreeNode()
    {
        if (m_hasRight)
            reinterpret_cast<Body*>(m_space)->~Body();
    }

    void reduce()
    {
        if (m_hasRight)
            m_left.reduce(*reinterpret_cast<Body*>(m_space));
    }
};

template <class TNode>
void collapse(Node* n)
{
    for (;;)
    {
        CARB_ASSERT(n);
        CARB_ASSERT(n->m_refCount.load(std::memory_order_relaxed) > 0);
        if (--n->m_refCount > 0)
            return;
        Node* parent = n->m_parent;
        if (!parent)
            break;

        auto self = static_cast<TNode*>(n);
        self->reduce();
        self->~TNode();
        carb::deallocate(self);
        n = parent;
    }

    // Done, wakeup the waiting thread
    auto& wait = static_cast<WaitNode*>(n)->m_wait;
    wait.store(false, std::memory_order_release);
    carb::getCachedInterface<ITasking>()->futexWakeup(wait, 1);
}

template <class T, size_t N = 1>
class AlignedArray
{
public:
    T* begin() const
    {
        auto ptr = reinterpret_cast<uintptr_t>(&m_aligned);
        return reinterpret_cast<T*>(ptr);
    }

    T* end() const
    {
        return begin() + N;
    }

private:
    alignas(alignof(T)) std::uint8_t m_aligned[N * sizeof(T)];
};

template <class T, Depth_t MaxCapacity>
class RangeQueue
{
public:
    RangeQueue(const T& val) : m_head(0), m_tail(0), m_size(1)
    {
        m_depth[0] = 0;
        new (static_cast<void*>(m_pool.begin())) T(val);
    }
    ~RangeQueue()
    {
        while (!empty())
            pop_back();
    }

    bool empty() const
    {
        return m_size == 0;
    }

    Depth_t size() const
    {
        return m_size;
    }

    void splitToFill(Depth_t maxDepth)
    {
        while (m_size < MaxCapacity && canDivide(maxDepth))
        {
            auto prev = m_head;
            m_head = (m_head + 1) % MaxCapacity;
            new (m_pool.begin() + m_head) T(std::move(m_pool.begin()[prev]));
            m_pool.begin()[prev].~T();
            new (m_pool.begin() + prev) T(m_pool.begin()[m_head], Split);
            m_depth[m_head] = ++m_depth[prev];
            ++m_size;
        }
    }

    void pop_back()
    {
        CARB_ASSERT(m_size > 0);
        m_pool.begin()[m_head].~T();
        --m_size;
        m_head = (m_head + MaxCapacity - 1) % MaxCapacity;
    }

    void pop_front()
    {
        CARB_ASSERT(m_size > 0);
        m_pool.begin()[m_tail].~T();
        --m_size;
        m_tail = (m_tail + 1) % MaxCapacity;
    }

    T& back()
    {
        CARB_ASSERT(m_size > 0);
        return m_pool.begin()[m_head];
    }

    T& front()
    {
        CARB_ASSERT(m_size > 0);
        return m_pool.begin()[m_tail];
    }

    Depth_t frontDepth() const
    {
        CARB_ASSERT(m_size > 0);
        return m_depth[m_tail];
    }

    Depth_t backDepth() const
    {
        CARB_ASSERT(m_size > 0);
        return m_depth[m_head];
    }

    bool canDivide(Depth_t maxDepth)
    {
        return backDepth() < maxDepth && back().canDivide();
    }

private:
    Depth_t m_head, m_tail, m_size;
    Depth_t m_depth[MaxCapacity];
    AlignedArray<T, MaxCapacity> m_pool;
};

class DefaultPartitioner
{
public:
    static constexpr unsigned kRangeQueueSize = 8;

    DefaultPartitioner(detail::IApplyRange& ar, size_t concurrency)
        : m_ar(ar), m_divisor(concurrency), m_maxDepth(kInitDepth)
    {
        m_divisor *= kInitialChunks;
    }

    DefaultPartitioner(DefaultPartitioner& other, Split_t)
        : m_ar(other.m_ar), m_divisor(split(other)), m_maxDepth(other.m_maxDepth)
    {
    }

    template <class ApplyRangeType, class Range>
    void execute(ApplyRangeType& ar, Range& range)
    {
        while (range.canDivide() && this->canDivide())
        {
            ar.divideWork();
        }
        this->doWork(ar, range);
    }

    bool canDivide()
    {
        if (m_divisor > 1)
            return true;

        if (m_divisor && m_maxDepth)
        {
            --m_maxDepth;
            m_divisor = 0;
            return true;
        }
        return false;
    }

    template <class Task>
    bool hasDemand(Task& t)
    {
        if (TreeNode::isPeerStolen(t))
        {
            m_maxDepth += kDemandAddDepth;
            return true;
        }
        return false;
    }

    template <class ApplyRangeType, class Range>
    void doWork(ApplyRangeType& ar, Range& range)
    {
        if (!range.canDivide() || !this->maxDepth())
        {
            ar.runBody(range);
        }
        else
        {
            RangeQueue<Range, kRangeQueueSize> rangeQueue(range);
            do
            {
                rangeQueue.splitToFill(this->maxDepth());
                if (this->hasDemand(ar))
                {
                    if (rangeQueue.size() > 1)
                    {
                        ar.divideWork(rangeQueue.front(), rangeQueue.frontDepth());
                        rangeQueue.pop_front();
                        continue;
                    }
                    if (rangeQueue.canDivide(this->maxDepth()))
                        continue;
                }
                ar.runBody(rangeQueue.back());
                rangeQueue.pop_back();
            } while (!rangeQueue.empty());
        }
    }


    template <class Task>
    bool evalStolen(Task& t, TaskBundle* tb)
    {
        if (!this->m_divisor)
        {
            this->m_divisor = 1;
            if (t.m_parent->m_refCount >= 2 && m_ar.isStolen(tb))
            {
                TreeNode::markTaskStolen(t);
                if (!m_maxDepth)
                    ++m_maxDepth;
                m_maxDepth += kDemandAddDepth;
                return true;
            }
        }
        return false;
    }

    Depth_t maxDepth() const
    {
        return m_maxDepth;
    }

    void rebaseDepth(Depth_t base)
    {
        CARB_ASSERT(base <= m_maxDepth);
        auto temp = m_maxDepth - base;
        m_maxDepth = Depth_t(temp); // GCC7 -Werror=conversion fix
    }

private:
    template <class Range, class Exec, class Partitioner>
    friend struct ApplyRange;

    static size_t split(DefaultPartitioner& other)
    {
        return other.m_divisor /= size_t(2);
    }

    detail::IApplyRange& m_ar;
    size_t m_divisor;
    Depth_t m_maxDepth;
};

struct ApplyRangeState
{
    bool isExternalThread;
    bool recursive;
    ThreadLocalStorage* tls;
    void* arg;
};

template <class Range, class Exec, class Partitioner>
struct ApplyRange
{
    detail::IApplyRange& m_ar;
    Range m_range;
    const Exec m_exec;
    Node* m_parent;
    ApplyRange* m_topmost;
    Partitioner m_partition;
    bool m_onStack{ false };

    void execute()
    {
        m_partition.evalStolen(*this, m_ar.currentTask());
        m_partition.execute(*this, m_range);
        finalize();
    }

    static void execute(void* p)
    {
        static_cast<ApplyRange*>(p)->execute();
    }

    void finalize()
    {
        auto parent = m_parent;
        auto onStack = m_onStack;
        if (!onStack)
            this->~ApplyRange();

        collapse<TreeNode>(parent);

        if (!onStack)
            carb::deallocate(this);
    }

    ApplyRange(detail::IApplyRange& ar, const Range& range, const Exec& exec, Partitioner& partitioner)
        : m_ar(ar),
          m_range(range),
          m_exec(exec),
          m_parent(nullptr),
          m_topmost(this),
          m_partition(partitioner),
          m_onStack(true)
    {
    }

    ApplyRange(ApplyRange& parent, Split_t)
        : m_ar(parent.m_ar),
          m_range(parent.m_range, Split),
          m_exec(parent.m_exec),
          m_parent(nullptr),
          m_topmost(parent.m_topmost),
          m_partition(parent.m_partition, Split)
    {
    }

    ApplyRange(ApplyRange& parent, const Range& range, Depth_t depth)
        : m_ar(parent.m_ar),
          m_range(range),
          m_exec(parent.m_exec),
          m_parent(nullptr),
          m_topmost(parent.m_topmost),
          m_partition(parent.m_partition, Split)
    {
        m_partition.rebaseDepth(depth);
    }

    static void Run(detail::IApplyRange& ar, const Range& range, const Exec& exec, Partitioner& partitioner)
    {
        CARB_ASSERT(!range.empty());

        ApplyRange taskData{ ar, range, exec, partitioner };
        CARB_ASSERT(taskData.m_onStack);

        ApplyRangeState state = {};
        ar.beginApplyRange(state, &taskData);

        WaitNode waiter;
        taskData.m_parent = &waiter;

        // Run the first task locally
        taskData.execute();

        ar.finishApplyRange(state, &ApplyRange::execute,
                            [](void* arg) -> void* { return static_cast<ApplyRange*>(arg)->m_topmost; }, waiter.m_wait);
    }

    void runBody(Range& range)
    {
        CARB_ASSERT(!range.empty());
        m_exec(range.begin(), range.end());
    }

    void divideWork()
    {
        divideWorkInternal(*this, Split);
    }

    void divideWork(const Range& range, Depth_t depth)
    {
        divideWorkInternal(*this, range, depth);
    }

private:
    template <class... Args>
    void divideWorkInternal(Args&&... args)
    {
        // Both of these are allocated using the same size so that we get better/faster heap memory reuse
        static_assert(sizeof(ApplyRange) <= (2 * CARB_CACHELINE_SIZE), "broken assumption");
        auto taskData =
            new (carb::allocate(2 * CARB_CACHELINE_SIZE, CARB_CACHELINE_SIZE)) ApplyRange(std::forward<Args>(args)...);
        CARB_ASSERT(!taskData->m_onStack);

        static_assert(sizeof(TreeNode) <= (2 * CARB_CACHELINE_SIZE), "broken assumption");
        taskData->m_parent = m_parent =
            new (carb::allocate(2 * CARB_CACHELINE_SIZE, CARB_CACHELINE_SIZE)) TreeNode(m_parent, 2);

        m_ar.queueTask(execute, taskData);
    }
};

template <class Range, class Body, class Partitioner>
struct ParallelReduce
{
    detail::IApplyRange& m_ar;
    Range m_range;
    Body* m_body;
    Node* m_parent;
    ParallelReduce* m_topmost;
    Partitioner m_partition;
    bool m_onStack{ false };
    bool m_right{ false };

    using TreeNodeType = ReductionTreeNode<Body>;

    void execute()
    {
        m_partition.evalStolen(*this, m_ar.currentTask());

        CARB_ASSERT(m_parent);
        if (m_right && m_parent->m_refCount.load(std::memory_order_acquire) == 2)
        {
            TreeNodeType* parent = static_cast<TreeNodeType*>(m_parent);
            m_body = new (parent->m_space) Body(*m_body, Split);
            parent->m_hasRight = true;
        }
        CARB_ASSERT(m_body);

        m_partition.execute(*this, m_range);
        finalize();
    }

    static void execute(void* p)
    {
        static_cast<ParallelReduce*>(p)->execute();
    }

    void finalize()
    {
        auto parent = m_parent;
        auto onStack = m_onStack;
        if (!onStack)
            this->~ParallelReduce();

        collapse<TreeNodeType>(parent);

        if (!onStack)
            carb::deallocate(this);
    }

    ParallelReduce(detail::IApplyRange& ar, const Range& range, Body& body, Partitioner& partitioner)
        : m_ar(ar),
          m_range(range),
          m_body(&body),
          m_parent(nullptr),
          m_topmost(this),
          m_partition(partitioner),
          m_onStack(true)
    {
    }

    ParallelReduce(ParallelReduce& parent, Split_t split)
        : m_ar(parent.m_ar),
          m_range(parent.m_range, split),
          m_body(parent.m_body),
          m_parent(nullptr),
          m_topmost(parent.m_topmost),
          m_partition(parent.m_partition, split),
          m_right(true)
    {
        parent.m_right = false;
    }

    ParallelReduce(ParallelReduce& parent, const Range& range, Depth_t depth)
        : m_ar(parent.m_ar),
          m_range(range),
          m_body(parent.m_body),
          m_parent(nullptr),
          m_topmost(parent.m_topmost),
          m_partition(parent.m_partition, Split),
          m_right(true)
    {
        m_partition.rebaseDepth(depth);
        parent.m_right = false;
    }

    static void Run(detail::IApplyRange& ar, const Range& range, Body& body, Partitioner& partitioner)
    {
        CARB_ASSERT(!range.empty());

        ParallelReduce taskData{ ar, range, body, partitioner };
        CARB_ASSERT(taskData.m_onStack);

        ApplyRangeState state = {};
        ar.beginApplyRange(state, &taskData);

        WaitNode waiter;
        taskData.m_parent = &waiter;

        // Run the first task locally
        taskData.execute();

        ar.finishApplyRange(state, &ParallelReduce::execute,
                            [](void* arg) -> void* { return static_cast<ParallelReduce*>(arg)->m_topmost; },
                            waiter.m_wait);
    }

    void runBody(Range& range)
    {
        CARB_ASSERT(!range.empty());
        (*m_body)(range.begin(), range.end());
    }

    void divideWork()
    {
        divideWorkInternal(*this, Split);
    }

    void divideWork(const Range& range, Depth_t depth)
    {
        divideWorkInternal(*this, range, depth);
    }

private:
    template <class... Args>
    void divideWorkInternal(Args&&... args)
    {
        // Both of these are allocated using the same size so that we get better/faster heap memory reuse
        static_assert(sizeof(ParallelReduce) <= (2 * CARB_CACHELINE_SIZE), "broken assumption");
        auto taskData = new (carb::allocate(2 * CARB_CACHELINE_SIZE, CARB_CACHELINE_SIZE))
            ParallelReduce(std::forward<Args>(args)...);
        CARB_ASSERT(!taskData->m_onStack);

        static_assert(sizeof(ParallelReduce) <= (2 * CARB_CACHELINE_SIZE), "broken assumption");
        taskData->m_parent = m_parent =
            new (carb::allocate(2 * CARB_CACHELINE_SIZE, CARB_CACHELINE_SIZE)) TreeNodeType(m_parent, 2, *m_body);

        m_ar.queueTask(execute, taskData);
    }
};

} // namespace detail
//! \endcond

} // namespace tasking
} // namespace carb
#endif
