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
//! @brief Carbonite Delegate implementation.
#pragma once

#include "detail/DelegateBase.h"

#include "../thread/Mutex.h"

namespace carb
{

//! Namespace for Carbonite delegate implementation.
namespace delegate
{


template <class T>
class Delegate;

template <class T>
class DelegateRef;

/**
 * Implements a thread-safe callback system that can have multiple subscribers.
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
 * Delegate is thread-safe for all operations. `Call()` can occur simultaneously in multiple threads. An `Unbind()`
 * will wait if the bound callback is currently executing in another thread.
 *
 * Delegate can be destroyed from a binding (during `Call()`) as the internal state is not disposed of
 * until all active calls have been completed. See `~Delegate()`.
 *
 * Delegate does not hold any internal locks while calling bound callbacks. It is strongly recommended to avoid
 * holding locks when invoking Delegate's `Call()` function.
 *
 * These tenets make up the basis of Carbonite's Basic Callback Hygiene as described in the @rstdoc{../../../../CODING}.
 *
 * @warning This delegate is not recommended for use when called from with a *carb.tasking* task. Instead, use
 *   \ref carb::tasking::Delegate.
 */
template <class... Args>
class Delegate<void(Args...)> : public detail::DelegateBase<::carb::thread::mutex, detail::DefaultExec, void(Args...)>
{
    using Base = detail::DelegateBase<::carb::thread::mutex, detail::DefaultExec, void(Args...)>;

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

//! A helper class for determining the type of a \ref carb::delegate::DelegateRef based on a
//! \ref carb::delegate::Delegate.  @tparam Del a \ref carb::delegate::Delegate
template <class Del>
struct RefFromDelegate
{
    //! The type of \ref DelegateRef that should be used for a \ref Delegate of type `Del`
    using type = DelegateRef<typename Del::FunctionType>;
};

//! Definition helper for `RefFromDelegate<Del>::type`
template <class Del>
using RefFromDelegate_t = typename RefFromDelegate<Del>::type;

} // namespace delegate

} // namespace carb

CARB_INCLUDE_PURIFY_TEST({
    using namespace carb::delegate;
    Delegate<void()> d, d2{ Delegate<void()>{} }, d3 = Delegate<void()>();
    auto b = d.Bind(nullptr, [] {});
    d.Bind(nullptr, [](bool) {}, true);
    d.BindWithKey(0, [] {});
    d.BindWithKey(1, [](bool) {}, false);
    d.Unbind(1);
    d.Unbind(b);
    d.HasKey(0);
    d.UnbindCurrent();
    d2.UnbindAll();
    d.Count();
    d.HasPending();
    d.IsEmpty();
    d.GetKeysByType<int>();
    d.Call();
    d();
    d.swap(d3);

    DelegateRef<void()> dr(d), dr2{};
    DelegateRef<void()> dr3(dr);
    DelegateRef<void()> dr4(std::move(dr2));
    DelegateRef<void()> dr5 = std::move(dr4);
    DelegateRef<void()> dr6 = dr5;
    CARB_UNUSED(bool(dr6));
    dr6.reset();
    dr5.reset(d);
    dr5.get();
    (*dr).Call();
    dr->Call();
});
