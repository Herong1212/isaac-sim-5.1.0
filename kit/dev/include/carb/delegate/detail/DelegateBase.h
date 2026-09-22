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
//! @brief Carbonite Delegate base detail implementation.
#pragma once

#include "../../Defines.h"

#include "../../Strong.h"
#include "../../container/IntrusiveList.h"
#include "../../thread/Util.h"

#include <memory>
#include <mutex>
#include <vector>

namespace carb
{
namespace delegate
{

template <class T>
class DelegateRef;

//! Detail implementation
namespace detail
{

//! \cond DEV
// The default executor class, which works in terms of thread IDs.
struct DefaultExec
{
    using Id = carb::thread::ThreadId;

    Id operator()() const
    {
        return carb::this_thread::getId();
    }
};
//! \endcond

template <class M, class E, class T>
class DelegateBase;

/**
 * Base class for carb::delegate::Delegate.
 *
 * @note This class is not intended to be used directly. Use @ref carb::delegate::Delegate instead.
 * @tparam Mutex The mutex class to be used by this class.
 * @tparam Exec An executor class that reports the current executor (i.e. thread ID)
 * @tparam Args... The arguments for the function-type in use by this delegate class.
 */
template <class Mutex, class Exec, class... Args>
class DelegateBase<Mutex, Exec, void(Args...)>
{
public:
    //! A type representing the function type
    using FunctionType = void(Args...);

    /**
     * A quasi-unique identifier outputted from Bind()
     *
     * \ref Handle is unique as long as it has not rolled over.
     */
    CARB_STRONGTYPE(Handle, size_t);
    CARB_DOC_CONSTEXPR static Handle kInvalidHandle{ 0 }; //!< A value representing an invalid \ref Handle value

    /**
     * Constructs an empty delegate
     */
    DelegateBase() = default;

    /**
     * Move constructor.
     *
     * @param other The Delegate to move from. This Delegate will be left in a valid but empty state.
     */
    DelegateBase(DelegateBase&& other);

    /**
     * Move-assign operator
     *
     * @param other The Delegate to move-assign from. Will be swapped with `*this`.
     *
     * @returns `*this`
     */
    DelegateBase& operator=(DelegateBase&& other);

    /**
     * Destructor.
     *
     * The destructor unbinds all bindings and follows the waiting paradigm explained by \ref UnbindAll(). As the
     * internal state of the delegate is held until all active calls have completed, it is valid to destroy Delegate
     * from a callback.
     */
    ~DelegateBase();

    /**
     * Binds a callable (with optional additional arguments) to the delegate.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     *
     * \note This function can be done from within a callback. If done during a callback, the newly bound callable will
     * not be available to be called until \ref Call() returns, at which point the callback can be called by other
     * threads or outer \ref Call() calls (in the case of recursive calls to \ref Call()).
     *
     * @param hOut An optional pointer that receives a \ref Handle representing the binding to \c Callable. This can
     * be \c nullptr to ignore the \ref Handle. The same \ref Handle is also returned. In a multi-threaded environment,
     * it is possible for \p func to be called before \ref Bind() returns, but \p hOut will have already been assigned.
     * @param func A callable object, such as lambda, functor or [member-]function. Return values are ignored. The
     * callable must take as parameters \p args followed by the \c Args declared in the delegate template signature.
     * @param args Additional optional arguments to bind with \p func. If \p func is a member function pointer the
     * first argument must be the \c this pointer to call the member function with.
     * @return The \ref Handle also passed to \p hOut.
     */
    template <class Callable, class... BindArgs>
    Handle Bind(Handle* hOut, Callable&& func, BindArgs&&... args);

    /**
     * Binds a callable (with optional additional arguments) to the delegate with a user-defined key.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     *
     * \note This function can be done from within a callback. If done during a callback, the newly bound callable will
     * not be available to be called until \ref Call() returns, at which point the callback can be called by other
     * threads or outer \ref Call() calls (in the case of recursive calls to \ref Call()).
     *
     * @param key A user-defined key of any type that supports equality (==) to identify this binding. Although multiple
     * bindings can be referenced by the same key, Unbind() will only remove a single binding.
     * @param func A callable object, such as lambda, functor or [member-]function. Return values are ignored. The
     * callable must take as parameters \p args followed by the \c Args declared in the delegate template signature.
     * @param args Additional optional arguments to bind with \p func. If \p func is a member function pointer the
     * first argument must be the \c this pointer to call the member function with.
     */
    template <class KeyType, class Callable, class... BindArgs>
    void BindWithKey(KeyType&& key, Callable&& func, BindArgs&&... args);

    /**
     * Unbinds any single binding referenced by the given key.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     *
     * This function can be done from within a callback. If the referenced binding is currently executing in
     * another thread, Unbind() will not return until it has finished. Any binding can be safely unbound during a
     * callback. If a binding un-binds itself, the captured arguments and callable object will not be destroyed
     * until just before \ref Call() returns.
     *
     * \note It is guaranteed that when \ref Unbind() returns, the callback is not running and will never run in any
     * threads.
     *
     * @param key A \ref Handle or user-defined key previously passed to \ref BindWithKey().
     * @return \c true if a binding was un-bound; \c false if no binding matching key was found.
     */
    template <class KeyType>
    bool Unbind(KeyType&& key);

    /**
     * Indicates if a binding exists in `*this` with the given key or Handle.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     * However, without external synchronization, it is possible for the result of this function to be incorrect by the
     * time it is used.
     *
     * @param key A \ref Handle or user-defined key previously passed to \ref BindWithKey().
     * @returns \c true if a binding exists with the given \p key; \c false if no binding matching key was found.
     */
    template <class KeyType>
    bool HasKey(KeyType&& key) const noexcept;

    /**
     * Unbinds the currently executing callback without needing an identifying key.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     *
     * \note If not done within the context of a callback, this function has no effect.
     *
     * @return \c true if a binding was un-bound; \c false if there is no current binding.
     */
    bool UnbindCurrent();

    /**
     * Unbinds all bound callbacks, possibly waiting for active calls to complete.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     *
     * Unbinds all currently bound callbacks. This function will wait to return until bindings that it unbinds have
     * completed all calls in other threads. It is safe to perform this operation from within a callback.
     */
    void UnbindAll();

    /**
     * Returns the number of active bound callbacks.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     *
     * \note This function returns the count of \a active bound callbacks only. Pending callbacks (that were added with
     * \ref Bind() during \ref Call()) are not counted. Use \ref HasPending() to determine if pending bindings exist.
     *
     * @returns the number of active bound callbacks.
     */
    size_t Count() const noexcept;

    /**
     * Checks whether the Delegate has any pending bindings.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     * The nature of this function is such that the result may be stale by the time it is read in the calling thread,
     * unless the calling thread has at least one pending binding.
     *
     * \note This function returns \c true if any \a pending bound callbacks exist. This will only ever be non-zero if
     * one or more threads are currently in the \ref Call() function.
     *
     * @returns \c true if any pending bindings exist; \c false otherwise.
     */
    bool HasPending() const noexcept;

    /**
     * Checks whether the Delegate contains no pending or active bound callbacks.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     * However, without external synchronization, it is possible for the result of this function to be incorrect by the
     * time it is used.
     *
     * @returns \c true if there are no active or pending callbacks present in `*this`; \c false otherwise.
     */
    bool IsEmpty() const noexcept;

    /**
     * Given a type, returns a \c std::vector containing a copy of all keys used for bindings.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     *
     * \note This function can be done from within a callback. Pending callbacks (that were added with \ref Bind()
     * during \ref Call()) are included, even if they are pending in other threads. Note that in a multi-threaded
     * environment, the actual keys in use by Delegate may change after this function returns; in such cases, an
     * external mutex is recommended. \c KeyType must be Copyable in order for this function to compile.
     *
     * @tparam KeyType \ref Handle or a type previously passed to \ref BindWithKey()
     * @return a \c std::vector of copies of keys of the given type in use by this Delegate.
     */
    template <class KeyType>
    std::vector<std::decay_t<KeyType>> GetKeysByType() const;

    /**
     * Calls all bound callbacks for this Delegate.
     *
     * \thread_safety: Thread-safe with respect to other Delegate operations except for construction and destruction.
     *
     * \note This function can be done concurrently in multiple threads simultaneously. Recursive calls to \ref Call()
     * are allowed but the caller must take care to avoid endless recursion. Callbacks are free to call \ref Bind(),
     * \ref Unbind() or any other Delegate function. No internal locks are held while callbacks are called.
     *
     * @param args The arguments to pass to the callbacks.
     */
    void Call(Args... args);

    /**
     * Syntactic sugar for \ref Call()
     */
    void operator()(Args... args);

    /**
     * Swaps with another Delegate.
     *
     * @param other The Delegate to swap with.
     */
    void swap(DelegateBase& other);

protected:
    //! @private
    constexpr DelegateBase(std::nullptr_t);
    //! @private
    DelegateBase(const DelegateBase& copy) : m_impl(copy.m_impl)
    {
    }

    //! @private
    void copy(const DelegateBase& other)
    {
        m_impl = other.m_impl;
    }

    //! @private
    void reset()
    {
        m_impl.reset();
    }

    //! @private
    bool isValid() const noexcept
    {
        return m_impl != nullptr;
    }

private:
    //! A type representing the mutex type
    using MutexType = Mutex;

    //! A type representing the executor
    using ExecType = Exec;

    //! A type representing an executor ID
    using ExecutorId = typename Exec::Id;

    // Forward declaration of the base class for bindings.
    struct BaseBinding;

    // Forward declaration of the keyed bindings class.
    template <class Key>
    struct KeyedBinding;

    // The container for storing bindings.
    using Container = carb::container::IntrusiveList<BaseBinding, &BaseBinding::link>;

    // Forward declaration of a call in progress.
    struct ActiveCall;

    // The container for storing active calls.
    using ActiveCallList = carb::container::IntrusiveList<ActiveCall, &ActiveCall::link>;

    // Forward declaration of our internal implementation.
    struct Impl;

    ActiveCall* lastCurrentThreadCall();
    const ActiveCall* lastCurrentThreadCall() const;
    void UnbindInternal(std::unique_lock<Mutex>& g, typename Container::iterator iter);

    static size_t nextHandle();

    std::shared_ptr<Impl> m_impl{ std::make_shared<Impl>() };
};

} // namespace detail
} // namespace delegate
} // namespace carb

#include "DelegateImpl.inl"
