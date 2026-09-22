// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief Carbonite Tasking Delegate implementation.
#pragma once

#include "../delegate/detail/DelegateBase.h"

#include "TaskingUtils.h"

namespace carb
{

namespace tasking
{

//! \cond DEV
namespace detail
{

struct TaskingExec
{
    using Id = TaskContext;

    Id operator()() const noexcept
    {
        auto tasking = carb::getCachedInterface<ITasking>();

        TaskContext taskContext = tasking ? tasking->getTaskContext() : kInvalidTaskContext;
        if (taskContext == kInvalidTaskContext)
        {
            // There won't be overlap here because TaskContext has a bit set in the upper word, and thread IDs are only
            // 32-bit
            static_assert(sizeof(carb::this_thread::getId()) == sizeof(uint32_t), "Invalid assumption");
            taskContext = TaskContext(carb::this_thread::getId());
        }

        return taskContext;
    }
};

} // namespace detail
//! \endcond

template <class T>
class Delegate;

template <class T>
class DelegateRef;

/**
 * Implements a task-aware, task-safe callback system that can have multiple subscribers.
 *
 * @note This task-aware delegate requires that the *carb.tasking* plugin is registered prior to instantiation.
 *
 * A delegate is a weak-coupling callback system. Essentially, a system uses Delegate to have a callback that can
 * be received by multiple subscribers.
 *
 * Delegate has two ways to uniquely identify a bound callback: `Bind()` will output a `Handle`, or the
 * caller can provide a key of any type with `BindWithKey()`. Either the `Handle` or the given key can be passed to
 * `Unbind()` in order to remove a callback.
 *
 * Delegate can call all bound callbacks with the `Call()` function. Recursive calling is allowed with caveats listed
 * below.
 *
 * Delegate is thread-safe and task-safe for all operations. `Call()` can occur simultaneously in multiple tasks or
 * threads. An `Unbind()` will wait if the bound callback is currently executing in another thread or task.
 *
 * Delegate can be destroyed from a binding (during `Call()`) as the internal state is not disposed of
 * until all active calls have been completed. See `~Delegate()`.
 *
 * Delegate does not hold any internal locks while calling bound callbacks. It is strongly recommended to avoid
 * holding locks when invoking Delegate's `Call()` function.
 *
 * These tenets make up the basis of Carbonite's Basic Callback Hygiene as described in the @rstdoc{../../../../CODING}.
 */
template <class... Args>
class Delegate<void(Args...)>
    : public delegate::detail::DelegateBase<::carb::tasking::MutexWrapper, detail::TaskingExec, void(Args...)>
{
    using Base = delegate::detail::DelegateBase<::carb::tasking::MutexWrapper, detail::TaskingExec, void(Args...)>;

public:
    /**
     * Constructs an empty delegate
     */
    Delegate() = default;

    /**
     * Move constructor.
     *
     * @param other The Delegate to move from. This Delegate will be left in a valid but empty state.
     */
    Delegate(Delegate&& other) : Base(std::move(other))
    {
    }

    /**
     * Move-assign operator
     *
     * @param other The Delegate to move-assign from. Will be swapped with `*this`.
     *
     * @returns `*this`
     */
    Delegate& operator=(Delegate&& other)
    {
        Base::swap(other);
        return *this;
    }

private:
    template <class U>
    friend class DelegateRef;

    // Null constructor, only for DelegateRef use.
    constexpr Delegate(std::nullptr_t) : Base(nullptr)
    {
    }

    // Copy constructor, only for DelegateRef use.
    Delegate(const Delegate& other) : Base(other)
    {
    }

    // Copy-assign operator, only for DelegateRef use.
    Delegate& operator=(const Delegate& other)
    {
        Base::copy(other);
        return *this;
    }
};

/**
 * Holds a reference to a Delegate.
 *
 * Though Delegate is non-copyable, \c DelegateRef can be thought of as a `std::shared_ptr` for Delegate.
 * This allows a Delegate's bindings to remain active even though the original Delegate has been destroyed, which can
 * allow calls in progress to complete, or a mutex protecting the original Delegate to be unlocked.
 */
template <class... Args>
class DelegateRef<void(Args...)>
{
public:
    //! The Delegate type that is referenced.
    using DelegateType = Delegate<void(Args...)>;

    /**
     * Default constructor.
     *
     * Creates an empty DelegateRef such that `bool(*this)` would be `false`.
     */
    constexpr DelegateRef() noexcept : m_delegate{ nullptr }
    {
    }

    /**
     * Constructor.
     *
     * Constructs a DelegateRef that holds a strong reference to \p delegate.
     * @param delegate The Delegate object to hold a reference to.
     */
    explicit DelegateRef(DelegateType& delegate) : m_delegate(delegate)
    {
    }

    /**
     * Copy constructor.
     *
     * References the same underlying Delegate that \p other references. If \p other is empty, `*this` will also be
     * empty.
     * @param other A DelegateRef to copy.
     */
    DelegateRef(const DelegateRef& other) : m_delegate(other.m_delegate)
    {
    }

    /**
     * Move constructor.
     *
     * Moves the reference from \p other to `*this`. If \p other is empty, `*this` will also be empty. \p other is left
     * in a valid but empty state.
     * @param other A DelegateRef to move.
     */
    DelegateRef(DelegateRef&& other) = default;

    /**
     * Destructor
     */
    ~DelegateRef()
    {
        // The Delegate destructor calls UnbindAll(), which we definitely don't want. So just reset our reference.
        m_delegate.reset();
    }

    /**
     * Copy-assign.
     *
     * References the same underlying Delegate that \p other references and releases any existing reference. The order
     * of these operations is unspecified, so assignment from `*this` is undefined behavior.
     * @param other A DelegateRef to copy.
     * @returns `*this`.
     */
    DelegateRef& operator=(const DelegateRef& other)
    {
        m_delegate = other.m_delegate;
        return *this;
    }

    /**
     * Move-assign.
     *
     * Moves the reference from \p other to `*this` and releases any existing reference. The order of these operations
     * is unspecified, so assignment from `*this` is undefined behavior. If \p other is empty, `*this` will also be
     * empty. \p other is left in a valid but empty state.
     * @param other A DelegateRef to move.
     * @returns `*this`.
     */
    DelegateRef& operator=(DelegateRef&& other) = default;

    /**
     * Checks whether the DelegateRef holds a valid reference.
     * @returns `true` if `*this` holds a valid reference; `false` otherwise.
     */
    explicit operator bool() const noexcept
    {
        return m_delegate.isValid();
    }

    /**
     * Clears the DelegateRef to an empty reference.
     *
     * Postcondition: `bool(*this)` will be `false`.
     */
    void reset()
    {
        m_delegate.reset();
    }

    /**
     * References a different Delegate and releases any existing reference.
     * @param delegate The Delegate to reference.
     */
    void reset(DelegateType& delegate)
    {
        m_delegate = delegate;
    }

    /**
     * Swaps the reference with another DelegateRef.
     * @param other A DelegateRef to swap with.
     */
    void swap(DelegateRef& other)
    {
        m_delegate.swap(other);
    }

    /**
     * Retrieves the underlying DelegateType.
     * @returns a pointer to the referenced Delegate, or `nullptr` if `bool(*this)` would return false.
     */
    DelegateType* get() const noexcept
    {
        return m_delegate.isValid() ? const_cast<DelegateType*>(&m_delegate) : nullptr;
    }

    /**
     * Dereferences *this.
     * @returns a reference to the referenced Delegate. If `bool(*this)` would return false, behavior is undefined.
     */
    DelegateType& operator*() const noexcept
    {
        CARB_ASSERT(*this);
        return const_cast<DelegateType&>(m_delegate);
    }

    /**
     * Dereferences *this.
     * @returns a pointer to the referenced Delegate. If `bool(*this)` would return false, behavior is undefined.
     */
    DelegateType* operator->() const noexcept
    {
        CARB_ASSERT(*this);
        return const_cast<DelegateType*>(&m_delegate);
    }

private:
    DelegateType m_delegate;
};

//! A helper class for determining the type of a \ref carb::tasking::DelegateRef based on a
//! \ref carb::tasking::Delegate.  @tparam Del a \ref carb::tasking::Delegate
template <class Del>
struct RefFromDelegate
{
    //! The type of \ref DelegateRef that should be used for a \ref Delegate of type `Del`
    using type = DelegateRef<typename Del::FunctionType>;
};

//! Definition helper for `RefFromDelegate<Del>::type`
template <class Del>
using RefFromDelegate_t = typename RefFromDelegate<Del>::type;

} // namespace tasking

} // namespace carb
