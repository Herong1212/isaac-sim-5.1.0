// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief carb.tasking helper functions
#pragma once

#include "TaskingTypes.h"

#include "../thread/Futex.h"
#include "../cpp/Functional.h"
#include "../cpp/Optional.h"
#include "../cpp/Variant.h"
#include "../Memory.h"

#include <atomic>
#include <chrono>
#include <future>
#include <iterator>
#include <utility>
#include <type_traits>
#include <vector>

namespace carb
{
namespace tasking
{

#ifndef DOXYGEN_BUILD
namespace detail
{

template <class T>
struct CarbDeleter
{
    void operator()(T* p) noexcept
    {
        p->~T();
        carb::deallocate(p);
    }
};

template <class T, class U = std::remove_cv_t<T>>
inline void carbDelete(T* p) noexcept
{
    if (p)
    {
        p->~T();
        carb::deallocate(const_cast<U*>(p));
    }
}

[[noreturn]] inline void future_error(std::future_errc err, const char* explanation)
{
#    if CARB_EXCEPTIONS_ENABLED
    CARB_UNUSED(explanation);
    throw std::future_error(err);
#    else
    CARB_FATAL_UNLESS(false, "future_errc(%d): %s", int(err), explanation);
#    endif
}

template <class T>
inline void check_future_valid(T* me)
{
    CARB_UNLIKELY_IF(!me->valid())
    {
        future_error(std::future_errc::no_state, "no state");
    }
}

template <class T>
struct is_literal_string
{
    constexpr static bool value = false;
};

template <size_t N>
struct is_literal_string<const char (&)[N]>
{
    constexpr static bool value = true;
};

Counter* const kListOfCounters{ (Counter*)(size_t)-1 };

template <class Rep, class Period>
uint64_t convertDuration(const std::chrono::duration<Rep, Period>& dur)
{
    auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(cpp::detail::clampDuration(dur)).count();
    return uint64_t(::carb_max(std::chrono::nanoseconds::rep(0), ns));
}

template <class Clock, class Duration>
uint64_t convertAbsTime(const std::chrono::time_point<Clock, Duration>& tp)
{
    return convertDuration(tp - Clock::now());
}

template <class F, class Tuple, size_t... I, class... Args>
decltype(auto) applyExtraImpl(F&& f, Tuple&& t, std::index_sequence<I...>, Args&&... args)
{
    CARB_UNUSED(t); // Can get C4100: unreferenced formal parameter on MSVC when Tuple is empty.
    return cpp::invoke(std::forward<F>(f), std::get<I>(std::forward<Tuple>(t))..., std::forward<Args>(args)...);
}

template <class F, class Tuple, class... Args>
decltype(auto) applyExtra(F&& f, Tuple&& t, Args&&... args)
{
    return applyExtraImpl(std::forward<F>(f), std::forward<Tuple>(t),
                          std::make_index_sequence<std::tuple_size<std::remove_reference_t<Tuple>>::value>{},
                          std::forward<Args>(args)...);
}

// U looks like an iterator convertible to V when dereferenced
template <class U, class V>
using IsForwardIter = std::conjunction<
    std::negation<typename std::is_convertible<typename std::iterator_traits<U>::iterator_category, std::random_access_iterator_tag>>,
    typename std::is_convertible<typename std::iterator_traits<U>::iterator_category, std::forward_iterator_tag>,
    std::is_convertible<decltype(*std::declval<U&>()), V>>;

template <class U, class V>
using IsRandomAccessIter = std::conjunction<
    typename std::is_convertible<typename std::iterator_traits<U>::iterator_category, std::random_access_iterator_tag>,
    std::is_convertible<decltype(*std::declval<U&>()), V>>;

// Must exactly fit within a pointer, appropriate alignment, and be trivially copyable
template <class T>
using TriviallyBitCastable = std::conjunction<std::bool_constant<sizeof(T) == sizeof(void*)>,
                                              std::bool_constant<(alignof(T) <= alignof(void*))>,
                                              std::is_trivially_copyable<T>>;

// Must fit within a pointer, appropriate alignment, and be trivially copyable
template <class T>
using TriviallyFitsWithinPointer = std::conjunction<std::bool_constant<(sizeof(T) < sizeof(void*))>,
                                                    std::bool_constant<(alignof(T) <= alignof(void*))>,
                                                    std::is_trivially_copyable<T>>;

template <class Functor,
          class FuncType = typename std::decay_t<Functor>,
          std::enable_if_t<TriviallyBitCastable<FuncType>::value, bool> = false>
inline void generateTaskFunc(TaskDesc& desc, Functor&& func)
{
    // Use SFINAE to have this version of generateTaskFunc() contribute to resolution only if Functor is bit_cast-able
    // to void*
    FuncType f(std::forward<Functor>(func));
    desc.taskArg = cpp::bit_cast<void*>(f);
    desc.task = [](void* arg) {
        FuncType f = cpp::bit_cast<FuncType>(arg);
        f();
    };
}

template <class Functor,
          class FuncType = typename std::decay_t<Functor>,
          std::enable_if_t<TriviallyFitsWithinPointer<FuncType>::value, bool> = false>
inline void generateTaskFunc(TaskDesc& desc, Functor&& func)
{
    // Use SFINAE to have this version of generateTaskFunc() contribute to resolution only if Functor is smaller than a
    // void*, so that we can use the taskArg as the instance. On my machine, this is about a tenth of the time for the
    // below specialization, and happens more frequently.
    struct Padded // must be the same size as (void*)
    {
        FuncType f;
        char padding[sizeof(void*) - sizeof(f)] = {};
        Padded(Functor&& f) : f(std::forward<Functor>(f))
        {
        }
    };
    static_assert(sizeof(Padded) == sizeof(void*), "Internal error");
    new (&desc.taskArg) Padded(std::forward<Functor>(func));
    desc.task = [](void* arg) {
        Padded p = carb::cpp::bit_cast<Padded>(arg);
        p.f();
    };
    // FuncType is trivially destructible so we don't need a cancel func
}

template <class Functor,
          class FuncType = typename std::decay_t<Functor>,
          std::enable_if_t<std::conjunction<std::negation<TriviallyFitsWithinPointer<FuncType>>,
                                            std::negation<TriviallyBitCastable<FuncType>>>::value,
                           bool> = false>
inline void generateTaskFunc(TaskDesc& desc, Functor&& func)
{
    // Use SFINAE to have this version of generateTaskFunc() contribute to resolution only if Functor will NOT fit
    // within a void*, so that the heap can be used only if necessary
    // Need to allocate
    desc.taskArg = new (carb::allocate(sizeof(FuncType), alignof(FuncType))) FuncType(std::forward<Functor>(func));
    desc.task = [](void* arg) {
        std::unique_ptr<FuncType, detail::CarbDeleter<FuncType>> p(static_cast<FuncType*>(arg));
        (*p)();
    };
    desc.cancel = [](void* arg) { detail::carbDelete(static_cast<FuncType*>(arg)); };
}

template <class T>
class SharedState;

template <>
class SharedState<void>
{
    std::atomic_size_t m_refs{ 1 };

public:
    enum FromTask_t
    {
        FromTask
    };

    constexpr SharedState() noexcept = default;
    // Refs are increased by 1 because the future is "retrieved". Only called from GenerateFuture. It's important that
    // m_object.type gets set to eTaskContext because isTask() must always return true for the life of the object, even
    // if we don't have a TaskContext yet. Otherwise there is a race between the task fulfilling the promise and the
    // future being read (OVCC-1500).
    constexpr SharedState(FromTask_t) noexcept
        : m_refs(2), m_futureRetrieved(true), m_object{ ObjectType::eTaskContext, nullptr }
    {
    }
    virtual ~SharedState() = default;

    void addRef() noexcept
    {
        m_refs.fetch_add(1, std::memory_order_relaxed);
    }

    void release()
    {
        if (m_refs.fetch_sub(1, std::memory_order_release) == 1)
        {
            std::atomic_thread_fence(std::memory_order_acquire);
            detail::carbDelete(this);
        }
    }

    void set()
    {
        State prev = eUnset;
        CARB_UNLIKELY_IF(!m_futex.compare_exchange_strong(prev, isTask() ? eTaskPending : eReady))
        {
            detail::future_error(std::future_errc::promise_already_satisfied, "promise already satisfied");
        }
    }
    void get()
    {
    }

    void notify();

    void markReady()
    {
        m_futex.store(eReady, std::memory_order_release);
    }

    bool ready() const
    {
        return m_futex.load(std::memory_order_acquire) == eReady;
    }

    bool isTask() const
    {
        return m_object.type == ObjectType::eTaskContext;
    }

    enum State : uint8_t
    {
        eReady = 0,
        eUnset,
        eInProgress,
        eTaskPending,
    };

    std::atomic<State> m_futex{ eUnset };
    std::atomic_bool m_futureRetrieved{ false };
    Object m_object{ ObjectType::eFutex1, &m_futex };
};

template <class T>
class SharedState<T&> final : public SharedState<void>
{
public:
    constexpr SharedState() noexcept = default;
    constexpr SharedState(FromTask_t) noexcept : SharedState<void>(FromTask)
    {
    }

    bool isSet() const noexcept
    {
        return m_value != nullptr;
    }

    T& get() const
    {
        CARB_UNLIKELY_IF(!m_value)
        {
            detail::future_error(std::future_errc::broken_promise, "broken promise");
        }
        return *m_value;
    }
    void set(T& val)
    {
        State prev = eUnset;
        CARB_UNLIKELY_IF(!m_futex.compare_exchange_strong(prev, eInProgress, std::memory_order_acquire))
        {
            detail::future_error(std::future_errc::promise_already_satisfied, "promise already satisfied");
        }
        m_value = std::addressof(val);
        const State newState = this->isTask() ? eTaskPending : eReady;
#    if CARB_ASSERT_ENABLED
        CARB_ASSERT(m_futex.exchange(newState, std::memory_order_release) == eInProgress);
#    else
        m_futex.store(newState, std::memory_order_release);
#    endif
    }

    T* m_value{ nullptr };
};

template <class T>
class SharedState final : public SharedState<void>
{
public:
    using Type = typename std::decay<T>::type;

    constexpr SharedState() noexcept = default;
    constexpr SharedState(FromTask_t) noexcept : SharedState<void>(FromTask)
    {
    }

    bool isSet() const noexcept
    {
        return m_type.has_value();
    }

    const T& get_ref() const
    {
        CARB_UNLIKELY_IF(!m_type)
        {
            detail::future_error(std::future_errc::broken_promise, "broken promise");
        }
        return m_type.value();
    }

    T get()
    {
        CARB_UNLIKELY_IF(!m_type)
        {
            detail::future_error(std::future_errc::broken_promise, "broken promise");
        }
        return std::move(m_type.value());
    }
    void set(const T& value)
    {
        State prev = eUnset;
        CARB_UNLIKELY_IF(!m_futex.compare_exchange_strong(prev, eInProgress, std::memory_order_acquire))
        {
            detail::future_error(std::future_errc::promise_already_satisfied, "promise already satisfied");
        }
        m_type.emplace(value);
        const State newState = this->isTask() ? eTaskPending : eReady;
#    if CARB_ASSERT_ENABLED
        CARB_ASSERT(m_futex.exchange(newState, std::memory_order_release) == eInProgress);
#    else
        m_futex.store(newState, std::memory_order_release);
#    endif
    }
    void set(T&& value)
    {
        State prev = eUnset;
        CARB_UNLIKELY_IF(!m_futex.compare_exchange_strong(prev, eInProgress, std::memory_order_acquire))
        {
            detail::future_error(std::future_errc::promise_already_satisfied, "promise already satisfied");
        }
        m_type.emplace(std::move(value));
        const State newState = this->isTask() ? eTaskPending : eReady;
#    if CARB_ASSERT_ENABLED
        CARB_ASSERT(m_futex.exchange(newState, std::memory_order_release) == eInProgress);
#    else
        m_futex.store(newState, std::memory_order_release);
#    endif
    }

    carb::cpp::optional<Type> m_type;
};

} // namespace detail
#endif

class TaskGroup;

/**
 * Helper class to ensure correct compliance with the requiredObject parameter of ITasking::add[Throttled]SubTask() and
 * wait() functions.
 *
 * The following may be converted into a RequiredObject: TaskContext, Future, Any, All, Counter*, or CounterWrapper.
 */
struct RequiredObject final : public Object
{
    /**
     * Constructor that accepts a `std::nullptr_t`.
     */
    constexpr RequiredObject(std::nullptr_t) : Object{ ObjectType::eNone, nullptr }
    {
    }

    /**
     * Constructor that accepts an object that can be converted to Counter*.
     *
     * @param c An object convertible to Counter*. This can be Any, All, Counter* or CounterWrapper.
     */
    template <class T, std::enable_if_t<std::is_convertible<T, Counter*>::value, bool> = false>
    constexpr RequiredObject(T&& c) : Object{ ObjectType::eCounter, static_cast<Counter*>(c) }
    {
    }

    /**
     * Constructor that accepts an object that can be converted to TaskContext.
     *
     * @param tc A TaskContext or object convertible to TaskContext, such as a Future.
     */
    template <class T, std::enable_if_t<std::is_convertible<T, TaskContext>::value, bool> = true>
    constexpr RequiredObject(T&& tc)
        : Object{ ObjectType::eTaskContext, reinterpret_cast<void*>(static_cast<TaskContext>(tc)) }
    {
    }

    /**
     * Constructor that accepts a TaskGroup&.
     */
    constexpr RequiredObject(const TaskGroup& tg);

    /**
     * Constructor that accepts a TaskGroup*. `nullptr` may be provided.
     */
    constexpr RequiredObject(const TaskGroup* tg);

private:
    friend struct ITasking;
    template <class U>
    friend class Future;
    template <class U>
    friend class SharedFuture;

    constexpr RequiredObject(const Object& o) : Object(o)
    {
    }

    void get(TaskDesc& desc);
};

/**
 * Specifies an "all" grouping of RequiredObject(s).
 *
 * @note *ALL* RequiredObject(s) given in the constructor must become signaled before the All object will be considered
 * signaled.
 *
 * All and Any objects can be nested as they are convertible to RequiredObject.
 */
struct All final
{
    /**
     * Constructor that accepts an initializer_list of RequiredObject(s).
     * @param il The `initializer_list` of RequiredObject(s).
     */
    All(std::initializer_list<RequiredObject> il);

    /**
     * Constructor that accepts begin and end iterators that produce RequiredObject objects.
     * @param begin The beginning iterator.
     * @param end An off-the-end iterator just beyond the end of the list.
     */
    template <class InputIt, std::enable_if_t<detail::IsForwardIter<InputIt, RequiredObject>::value, bool> = false>
    All(InputIt begin, InputIt end);

    //! @private
    template <class InputIt, std::enable_if_t<detail::IsRandomAccessIter<InputIt, RequiredObject>::value, bool> = false>
    All(InputIt begin, InputIt end);

    /**
     * Convertible to RequiredObject.
     */
    operator RequiredObject() const
    {
        return RequiredObject(m_counter);
    }

private:
    friend struct RequiredObject;
    Counter* m_counter;

    operator Counter*() const
    {
        return m_counter;
    }
};

/**
 * Specifies an "any" grouping of RequiredObject(s).
 *
 * @note *ANY* RequiredObject given in the constructor that is or becomes signaled will cause the Any object to become
 * signaled.
 *
 * All and Any objects can be nested as they are convertible to RequiredObject.
 */
struct Any final
{
    /**
     * Constructor that accepts an initializer_list of RequiredObject objects.
     * @param il The initializer_list of RequiredObject objects.
     */
    Any(std::initializer_list<RequiredObject> il);

    /**
     * Constructor that accepts begin and end iterators that produce RequiredObject objects.
     * @param begin The beginning iterator.
     * @param end An off-the-end iterator just beyond the end of the list.
     */
    template <class InputIt, std::enable_if_t<detail::IsForwardIter<InputIt, RequiredObject>::value, bool> = false>
    Any(InputIt begin, InputIt end);

    //! @private
    template <class InputIt, std::enable_if_t<detail::IsRandomAccessIter<InputIt, RequiredObject>::value, bool> = false>
    Any(InputIt begin, InputIt end);

    /**
     * Convertible to RequiredObject.
     */
    operator RequiredObject() const
    {
        return RequiredObject(m_counter);
    }

private:
    friend struct RequiredObject;
    Counter* m_counter;

    operator Counter*() const
    {
        return m_counter;
    }
};

/**
 * Helper class to provide correct types to the Trackers class.
 *
 * The following types are valid trackers:
 * - Anything convertible to Counter*, such as CounterWrapper. Counters are deprecated however. The Counter is
 *   incremented before the task can possibly begin executing and decremented when the task finishes.
 * - Future<void>&: This can be used to atomically populate a Future<void> before the task could possibly start
 *   executing.
 * - Future<void>*: Can be `nullptr`, but if not, can be used to atomically populate a Future<void> before the task
 *   could possibly start executing.
 * - TaskContext&: By providing a reference to a TaskContext it will be atomically filled before the task could possibly
 *   begin executing.
 * - TaskContext*: By providing a pointer to a TaskContext (that can be `nullptr`), it will be atomically filled before
 *   the task could possibly begin executing, if valid.
 */
struct Tracker final : Object
{
    /**
     * Constructor that accepts a `std::nullptr_t`.
     */
    constexpr Tracker(std::nullptr_t) : Object{ ObjectType::eNone, nullptr }
    {
    }

    /**
     * Constructor that accepts a Counter* or an object convertible to Counter*, such as CounterWrapper.
     *
     * @param c The object convertible to Counter*.
     */
    template <class T, std::enable_if_t<std::is_convertible<T, Counter*>::value, bool> = false>
    constexpr Tracker(T&& c) : Object{ ObjectType::eCounter, reinterpret_cast<void*>(static_cast<Counter*>(c)) }
    {
    }

    /**
     * Constructor that accepts a task name.
     *
     * @note This is not a Tracker per se; this is syntactic sugar to name a task as it is created.
     * @tparam T A type that is convertible to `const char*`.
     * @param name Either a `const char*` (dynamic string) or a `const char (&)[N]` (literal string) as the string name
     *     for a task.
     * @see ITasking::nameTask()
     */
    template <class T, std::enable_if_t<std::is_convertible<T, const char*>::value, bool> = false>
    constexpr Tracker(T&& name)
        : Object{ detail::is_literal_string<T>::value ? ObjectType::eTaskNameLiteral : ObjectType::eTaskName,
                  const_cast<void*>(reinterpret_cast<const void*>(name)) }
    {
    }

    /**
     * Constructor that accepts a Future<void>&. The Future will be initialized before the task can begin.
     */
    Tracker(Future<>& fut) : Object{ ObjectType::ePtrTaskContext, fut.ptask() }
    {
    }

    /**
     * Constructor that accepts a Future<void>*. The Future<void> will be initialized before the task can begin.
     * The Future<void> pointer can be `nullptr`.
     */
    Tracker(Future<>* fut) : Object{ ObjectType::ePtrTaskContext, fut ? fut->ptask() : nullptr }
    {
    }

    /**
     * Constructor that accepts a SharedFuture<void>&. The SharedFuture will be initialized before the task can begin.
     */
    Tracker(SharedFuture<>& fut) : Object{ ObjectType::ePtrTaskContext, fut.ptask() }
    {
    }

    /**
     * Constructor that accepts a SharedFuture<void>*. The SharedFuture<void> will be initialized before the task can
     * begin. The SharedFuture<void> pointer can be `nullptr`.
     */
    Tracker(SharedFuture<>* fut) : Object{ ObjectType::ePtrTaskContext, fut ? fut->ptask() : nullptr }
    {
    }

    /**
     * Constructor that accepts a TaskContext&. The value will be atomically written before the task can begin.
     */
    constexpr Tracker(TaskContext& ctx) : Object{ ObjectType::ePtrTaskContext, &ctx }
    {
    }

    /**
     * Constructor that accepts a TaskContext*. The value will be atomically written before the task can begin.
     * The TaskContext* can be `nullptr`.
     */
    constexpr Tracker(TaskContext* ctx) : Object{ ObjectType::ePtrTaskContext, ctx }
    {
    }

    /**
     * Constructor that accepts a TaskGroup&. The TaskGroup will be entered immediately and left when the task finishes.
     * The TaskGroup must exist until the task completes.
     */
    Tracker(TaskGroup& grp);

    /**
     * Constructor that accepts a TaskGroup*. The TaskGroup will be entered immediately and left when the task finishes.
     * The TaskGroup* can be `nullptr` in which case nothing happens. The TaskGroup must exist until the task completes.
     */
    Tracker(TaskGroup* grp);

private:
    friend struct Trackers;
};

/**
 * Helper class to ensure correct compliance with trackers parameter of ITasking::addTask() variants
 */
struct Trackers final
{
    /**
     * Default constructor.
     */
    constexpr Trackers() : m_variant{}
    {
    }

    /**
     * Constructor that accepts a single Tracker.
     *
     * @param t The type passed to the Tracker constructor.
     */
    template <class T, std::enable_if_t<std::is_constructible<Tracker, T>::value, bool> = false>
    constexpr Trackers(T&& t) : m_variant(Tracker(t))
    {
    }

    /**
     * Constructor that accepts an initializer_list of Tracker objects.
     *
     * @param il The `std::initializer_list` of Tracker objects.
     */
    constexpr Trackers(std::initializer_list<Tracker> il)
    {
        switch (il.size())
        {
            case 0:
                break;
            case 1:
                m_variant.emplace<Tracker>(*il.begin());
                break;
            default:
                m_variant.emplace<TrackerVec>(std::move(il));
        }
    }

    /**
     * Constructor that accepts an initializer_list of Tracker objects and additional Tracker objects.
     *
     * @param il The `std::initializer_list` of Tracker objects.
     * @param p A pointer to additional Tracker objects; size specified by @p count.
     * @param count The number of additional Tracker objects in the list specified by @p p.
     */
    Trackers(std::initializer_list<Tracker> il, Tracker const* p, size_t count) : m_variant(std::in_place_index<2>)
    {
        switch (il.size() + count)
        {
            case 0:
                break;
            case 1:
                m_variant.emplace<Tracker>(il.size() == 0 ? *p : *il.begin());
                break;
            default:
            {
                auto& vec = m_variant.emplace<TrackerVec>();
                vec.reserve(il.size() + count);
                vec.insert(vec.end(), il.begin(), il.end());
                vec.insert(vec.end(), p, p + count);
            }
        }
    }

    /**
     * Retrieves a list of Tracker objects managed by this helper object.
     *
     * @param trackers Receives a pointer to a list of Tracker objects.
     * @param count Receives the count of Tracker objects.
     */
    void output(Tracker const*& trackers, size_t& count) const
    {
        static_assert(sizeof(Object) == sizeof(Tracker), "");
        Object const* pOut;
        fill(pOut, count);
        trackers = static_cast<Tracker const*>(pOut);
    }

    CARB_PREVENT_COPY(Trackers);

    /**
     * Trackers is move-constructible.
     */
    Trackers(Trackers&&) = default;
    /**
     * Trackers is move-assignable.
     */
    Trackers& operator=(Trackers&&) = default;

private:
    friend struct ITasking;
    using TrackerVec = std::vector<Tracker, carb::Allocator<Tracker>>;
    using Variant = carb::cpp::variant<carb::cpp::monostate, Tracker, TrackerVec>;
    Variant m_variant;
    Counter* fill(carb::tasking::Object const*& trackers, size_t& count) const
    {
        if (m_variant.index() == 0)
        {
            trackers = nullptr;
            count = 0;
            return nullptr;
        }

        if (auto* vec = carb::cpp::get_if<TrackerVec>(&m_variant))
        {
            trackers = vec->data();
            count = vec->size();
        }
        else
        {
            const Tracker& t = carb::cpp::get<Tracker>(m_variant);
            trackers = &t;
            count = 1;
        }
        return detail::kListOfCounters;
    }
};

//! A macro that can be used to mark a function as async, that is, it always executes in the context of a task.
//!
//! Generally the body of the function has one of @ref CARB_ASSERT_ASYNC, @ref CARB_CHECK_ASYNC, or
//! @ref CARB_FATAL_UNLESS_ASYNC.
//!
//! @code{.cpp}
//! void CARB_ASYNC Context::loadTask();
//! @endcode
#define CARB_ASYNC

//! A macro that can be used to mark a function as possibly async, that is, it may execute in the context of a task.
//! @code{.cpp}
//! void CARB_MAYBE_ASYNC Context::loadTask();
//! @endcode
#define CARB_MAYBE_ASYNC

//! Helper macro that results in a boolean expression which is `true` if the current thread is running in task context.
#define CARB_IS_ASYNC                                                                                                  \
    (::carb::getCachedInterface<carb::tasking::ITasking>()->getTaskContext() != ::carb::tasking::kInvalidTaskContext)

//! A macro that is used to assert that a scope is running in task context in debug builds only.
#define CARB_ASSERT_ASYNC CARB_ASSERT(CARB_IS_ASYNC)

//! A macro that is used to assert that a scope is running in task context in debug and checked builds.
#define CARB_CHECK_ASYNC CARB_CHECK(CARB_IS_ASYNC)

//! A macro that is used to assert that a scope is running in task context.
#define CARB_FATAL_UNLESS_ASYNC CARB_FATAL_UNLESS(CARB_IS_ASYNC, "Not running in task context!")

} // namespace tasking
} // namespace carb
