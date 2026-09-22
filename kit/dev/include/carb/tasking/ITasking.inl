// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "../cpp/Bit.h"

#include "detail/ApplyRange.h"

#include <type_traits>

namespace carb
{
namespace tasking
{

namespace detail
{

template <class R>
struct GenerateFuture
{
    using SharedState = detail::SharedState<R>;
    struct Releaser
    {
        void operator()(SharedState* p)
        {
            p->release();
        }
    };
    using SharedStatePtr = std::unique_ptr<SharedState, Releaser>;

    template <class Tuple, size_t... I>
    static constexpr void callTupleImpl(Tuple&& t, std::index_sequence<I...>)
    {
        SharedState* state = std::get<0>(std::forward<Tuple>(t)).get();
        state->set(carb::cpp::invoke(std::get<1>(std::forward<Tuple>(t)), std::get<I + 2>(std::forward<Tuple>(t))...));
    }

    template <class Tuple>
    static constexpr void callTuple(Tuple&& t)
    {
        callTupleImpl(std::forward<Tuple>(t),
                      std::make_index_sequence<std::tuple_size<std::remove_reference_t<Tuple>>::value - 2>{});
    }

    template <class Callable, class... Args>
    Future<R> operator()(ITasking* tasking, Counter* counter, TaskDesc& desc, Callable&& func, Args&&... args)
    {
        auto* state = new (carb::allocate(sizeof(SharedState))) SharedState(SharedState::FromTask);
        using Tuple = std::tuple<SharedStatePtr, std::decay_t<Callable>, std::decay_t<Args>...>;
        Tuple* t =
            new (carb::allocate(sizeof(Tuple))) Tuple(state, std::forward<Callable>(func), std::forward<Args>(args)...);
        detail::generateTaskFunc(desc, [t]() {
            std::unique_ptr<Tuple, detail::CarbDeleter<Tuple>> p(t);
            callTuple(std::move(*t));
        });
        CARB_ASSERT(desc.taskArg == t);
        CARB_ASSERT(!desc.cancel);
        desc.cancel = [](void* arg) { detail::carbDelete(static_cast<Tuple*>(arg)); };
        return Future<R>(tasking->internalAddTask(desc, counter), state);
    }

    template <class Callable, class Rep, class Period, class... Args>
    Future<R> operator()(ITasking* tasking,
                         const std::chrono::duration<Rep, Period>& dur,
                         Counter* counter,
                         TaskDesc& desc,
                         Callable&& func,
                         Args&&... args)
    {
        auto* state = new (carb::allocate(sizeof(SharedState))) SharedState(SharedState::FromTask);
        using Tuple = std::tuple<SharedStatePtr, std::decay_t<Callable>, std::decay_t<Args>...>;
        Tuple* t =
            new (carb::allocate(sizeof(Tuple))) Tuple(state, std::forward<Callable>(func), std::forward<Args>(args)...);
        detail::generateTaskFunc(desc, [t]() {
            std::unique_ptr<Tuple, detail::CarbDeleter<Tuple>> p(t);
            callTuple(std::move(*t));
        });
        CARB_ASSERT(desc.taskArg == t);
        CARB_ASSERT(!desc.cancel);
        desc.cancel = [](void* arg) { detail::carbDelete(static_cast<Tuple*>(arg)); };
        return Future<R>(tasking->internalAddDelayedTask(detail::convertDuration(dur), desc, counter), state);
    }

    template <class Callable, class Clock, class Duration, class... Args>
    Future<R> operator()(ITasking* tasking,
                         const std::chrono::time_point<Clock, Duration>& when,
                         Counter* counter,
                         TaskDesc& desc,
                         Callable&& func,
                         Args&&... args)
    {
        auto* state = new (carb::allocate(sizeof(SharedState))) SharedState(SharedState::FromTask);
        using Tuple = std::tuple<SharedStatePtr, std::decay_t<Callable>, std::decay_t<Args>...>;
        Tuple* t =
            new (carb::allocate(sizeof(Tuple))) Tuple(state, std::forward<Callable>(func), std::forward<Args>(args)...);
        detail::generateTaskFunc(desc, [t]() {
            std::unique_ptr<Tuple, detail::CarbDeleter<Tuple>> p(t);
            callTuple(std::move(*t));
        });
        CARB_ASSERT(desc.taskArg == t);
        CARB_ASSERT(!desc.cancel);
        desc.cancel = [](void* arg) { detail::carbDelete(static_cast<Tuple*>(arg)); };
        return Future<R>(tasking->internalAddDelayedTask(detail::convertAbsTime(when), desc, counter), state);
    }
};

template <>
struct GenerateFuture<void>
{
    template <class Callable>
    Future<void> operator()(ITasking* tasking, Counter* counter, TaskDesc& desc, Callable&& func)
    {
        detail::generateTaskFunc(desc, std::forward<Callable>(func));
        return Future<>(tasking->internalAddTask(desc, counter));
    }

    template <class Callable, class... Args>
    Future<void> operator()(ITasking* tasking, Counter* counter, TaskDesc& desc, Callable&& func, Args&&... args)
    {
        using Tuple = std::tuple<std::decay_t<Args>...>;
        detail::generateTaskFunc(
            desc, [func = std::forward<Callable>(func), args = Tuple(std::forward<Args>(args)...)]() mutable {
                std::apply(std::move(func), std::move(args));
            });
        return Future<>(tasking->internalAddTask(desc, counter));
    }

    template <class Callable, class Rep, class Period>
    Future<void> operator()(ITasking* tasking,
                            const std::chrono::duration<Rep, Period>& dur,
                            Counter* counter,
                            TaskDesc& desc,
                            Callable&& func)
    {
        detail::generateTaskFunc(desc, std::forward<Callable>(func));
        return Future<>(tasking->internalAddDelayedTask(detail::convertDuration(dur), desc, counter));
    }

    template <class Callable, class Rep, class Period, class... Args>
    Future<void> operator()(ITasking* tasking,
                            const std::chrono::duration<Rep, Period>& dur,
                            Counter* counter,
                            TaskDesc& desc,
                            Callable&& func,
                            Args&&... args)
    {
        using Tuple = std::tuple<std::decay_t<Args>...>;
        detail::generateTaskFunc(
            desc, [func = std::forward<Callable>(func), args = Tuple(std::forward<Args>(args)...)]() mutable {
                std::apply(std::move(func), std::move(args));
            });
        return Future<>(tasking->internalAddDelayedTask(detail::convertDuration(dur), desc, counter));
    }

    template <class Callable, class Clock, class Duration>
    Future<void> operator()(ITasking* tasking,
                            const std::chrono::time_point<Clock, Duration>& when,
                            Counter* counter,
                            TaskDesc& desc,
                            Callable&& func)
    {
        detail::generateTaskFunc(desc, std::forward<Callable>(func));
        return Future<>(tasking->internalAddDelayedTask(detail::convertAbsTime(when), desc, counter));
    }

    template <class Callable, class Clock, class Duration, class... Args>
    Future<void> operator()(ITasking* tasking,
                            const std::chrono::time_point<Clock, Duration>& when,
                            Counter* counter,
                            TaskDesc& desc,
                            Callable&& func,
                            Args&&... args)
    {
        using Tuple = std::tuple<std::decay_t<Args>...>;
        detail::generateTaskFunc(
            desc, [func = std::forward<Callable>(func), args = Tuple(std::forward<Args>(args)...)]() mutable {
                std::apply(std::move(func), std::move(args));
            });
        return Future<>(tasking->internalAddDelayedTask(detail::convertAbsTime(when), desc, counter));
    }
};

inline void SharedState<void>::notify()
{
    CARB_ASSERT(m_futex.load(std::memory_order_relaxed) == eReady);
    carb::getCachedInterface<ITasking>()->futexWakeup(m_futex, UINT_MAX);
}

} // namespace detail

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Future<T>
template <class T>
inline Future<T>::Future(Future&& rhs) noexcept : m_state(std::exchange(rhs.m_state, nullptr))
{
}

template <class T>
inline constexpr Future<T>::Future(detail::SharedState<T>* state) noexcept : m_state(state)
{
    // State has already been ref-counted.
}

template <class T>
inline Future<T>::Future(TaskContext task, detail::SharedState<T>* state) noexcept : m_state(state)
{
    // State has already been ref-counted and the SharedState should have been TaskContext type from construction.
    CARB_ASSERT(m_state->m_object.type == ObjectType::eTaskContext);
    m_state->m_object.data = cpp::bit_cast<void*>(task);
}

template <class T>
inline Future<T>::~Future()
{
    if (m_state)
        m_state->release();
}

template <class T>
inline Future<T>& Future<T>::operator=(Future&& rhs) noexcept
{
    std::swap(m_state, rhs.m_state);
    return *this;
}

template <class T>
inline bool Future<T>::valid() const noexcept
{
    return m_state != nullptr;
}

template <class T>
inline bool Future<T>::try_wait() const
{
    detail::check_future_valid(this);
    if (!m_state->ready())
    {
        if (!carb::getCachedInterface<ITasking>()->try_wait(*this))
            return false;
        m_state->markReady();
    }
    return true;
}

template <class T>
inline void Future<T>::wait() const
{
    detail::check_future_valid(this);
    if (!m_state->ready())
    {
        carb::getCachedInterface<ITasking>()->wait(*this);
        m_state->markReady();
    }
}

template <class T>
template <class Rep, class Period>
inline bool Future<T>::wait_for(const std::chrono::duration<Rep, Period>& dur) const
{
    detail::check_future_valid(this);
    if (!m_state->ready())
    {
        if (!carb::getCachedInterface<ITasking>()->wait_for(dur, *this))
            return false;
        m_state->markReady();
    }
    return true;
}

template <class T>
template <class Clock, class Duration>
inline bool Future<T>::wait_until(const std::chrono::time_point<Clock, Duration>& when) const
{
    detail::check_future_valid(this);
    if (!m_state->ready())
    {
        if (!carb::getCachedInterface<ITasking>()->wait_until(when, *this))
            return false;
        m_state->markReady();
    }
}

template <class T>
inline T Future<T>::get()
{
    detail::check_future_valid(this);
    Future local(std::move(*this));
    local.wait();
    return local.m_state->get();
}

template <class T>
inline bool Future<T>::isCanceled() const
{
    detail::check_future_valid(this);
    return try_wait() && !m_state->isSet();
}

template <class T>
inline SharedFuture<T> Future<T>::share()
{
    return SharedFuture<T>(std::move(*this));
}

template <class T>
inline const TaskContext* Future<T>::task_if() const
{
    return m_state && m_state->isTask() ? reinterpret_cast<const TaskContext*>(&m_state->m_object.data) : nullptr;
}

template <class T>
inline Future<T>::operator RequiredObject() const
{
    return valid() ? m_state->m_object : RequiredObject{ Object{ ObjectType::eNone, nullptr } };
}

template <class T>
template <class Callable, class... Args>
inline auto Future<T>::then(Priority prio, Trackers&& trackers, Callable&& f, Args&&... args)
{
    detail::check_future_valid(this);
    RequiredObject req = *this;
    return carb::getCachedInterface<ITasking>()->addSubTask(
        req, prio, std::move(trackers),
        [t = std::move(*this), f = std::forward<Callable>(f),
         args = std::make_tuple(std::forward<Args>(args)...)]() mutable {
            return detail::applyExtra(std::move(f), std::move(args), t.get());
        });
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Future<void>
inline Future<void>::~Future()
{
    if (auto s = state())
    {
        s->release();
    }
}

inline Future<void>::Future(Future&& rhs) noexcept : m_obj(std::exchange(rhs.m_obj, { ObjectType::eNone, nullptr }))
{
}

inline Future<void>& Future<void>::operator=(Future&& rhs) noexcept
{
    std::swap(m_obj, rhs.m_obj);
    return *this;
}

inline Future<void>::Future(TaskContext task) : m_obj{ ObjectType::eTaskContext, reinterpret_cast<void*>(task) }
{
}

inline Future<void>::Future(detail::SharedState<void>* state) : m_obj{ ObjectType::eSharedState, state }
{
    // Has already been referenced, so no need to addRef
    CARB_ASSERT(state);
}

inline bool Future<void>::valid() const noexcept
{
    if (state())
        return true;
    return reinterpret_cast<TaskContext>(m_obj.data) != kInvalidTaskContext;
}

inline bool Future<void>::try_wait() const
{
    detail::check_future_valid(this);
    auto s = state();
    if (!s || !s->ready())
    {
        if (!carb::getCachedInterface<ITasking>()->try_wait(*this))
            return false;
        if (s)
            s->markReady();
    }
    return true;
}

inline void Future<void>::wait() const
{
    detail::check_future_valid(this);
    auto s = state();
    if (!s || !s->ready())
    {
        carb::getCachedInterface<ITasking>()->wait(*this);
        if (s)
            s->markReady();
    }
}

template <class Rep, class Period>
inline bool Future<void>::wait_for(const std::chrono::duration<Rep, Period>& dur) const
{
    detail::check_future_valid(this);
    auto s = state();
    if (!s || !s->ready())
    {
        if (!carb::getCachedInterface<ITasking>()->wait_for(dur, *this))
            return false;
        if (s)
            s->markReady();
    }
    return true;
}

template <class Clock, class Duration>
inline bool Future<void>::wait_until(const std::chrono::time_point<Clock, Duration>& when) const
{
    detail::check_future_valid(this);
    auto s = state();
    if (!s || !s->ready())
    {
        if (!carb::getCachedInterface<ITasking>()->wait_until(when, *this))
            return false;
        if (s)
            s->markReady();
    }
    return true;
}

inline void Future<void>::get()
{
    detail::check_future_valid(this);
    Future local(std::move(*this));
    local.wait();
}

inline SharedFuture<void> Future<void>::share()
{
    return SharedFuture<void>(std::move(*this));
}

inline const TaskContext* Future<void>::task_if() const
{
    auto s = state();
    if (s && s->isTask())
        return reinterpret_cast<TaskContext*>(&s->m_object.data);
    return m_obj.type == ObjectType::eTaskContext ? reinterpret_cast<const TaskContext*>(&m_obj.data) : nullptr;
}

inline Future<void>::operator RequiredObject() const
{
    auto s = state();
    return s ? s->m_object : m_obj;
}

template <class Callable, class... Args>
inline auto Future<void>::then(Priority prio, Trackers&& trackers, Callable&& f, Args&&... args)
{
    return carb::getCachedInterface<ITasking>()->addSubTask(
        *this, prio, std::move(trackers),
        [f = std::forward<Callable>(f), args = std::make_tuple(std::forward<Args>(args)...)]() mutable {
            return std::apply(std::move(f), std::move(args));
        });
}

inline TaskContext* Future<void>::ptask()
{
    if (auto s = state())
        s->release();
    m_obj = Object{ ObjectType::eTaskContext, nullptr };
    return reinterpret_cast<TaskContext*>(&m_obj.data);
}

inline detail::SharedState<void>* Future<void>::state() const noexcept
{
    return m_obj.type == ObjectType::eSharedState ? static_cast<detail::SharedState<void>*>(m_obj.data) : nullptr;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SharedFuture<T>
template <class T>
inline SharedFuture<T>::SharedFuture(const SharedFuture<T>& other) noexcept : m_state(other.m_state)
{
    if (m_state)
        m_state->addRef();
}

template <class T>
inline SharedFuture<T>::SharedFuture(SharedFuture<T>&& other) noexcept : m_state(std::exchange(other.m_state, nullptr))
{
}

template <class T>
inline SharedFuture<T>::SharedFuture(Future<T>&& fut) noexcept : m_state(std::exchange(fut.m_state, nullptr))
{
}

template <class T>
inline SharedFuture<T>::~SharedFuture()
{
    if (m_state)
        m_state->release();
}

template <class T>
inline SharedFuture<T>& SharedFuture<T>::operator=(const SharedFuture<T>& other)
{
    if (other.m_state)
        other.m_state->addRef();
    if (m_state)
        m_state->release();
    m_state = other.m_state;
    return *this;
}

template <class T>
inline SharedFuture<T>& SharedFuture<T>::operator=(SharedFuture<T>&& other) noexcept
{
    std::swap(m_state, other.m_state);
    return *this;
}

template <class T>
inline const T& SharedFuture<T>::get() const
{
    detail::check_future_valid(this);
    wait();
    return m_state->get_ref();
}

template <class T>
inline bool SharedFuture<T>::valid() const noexcept
{
    return m_state != nullptr;
}

template <class T>
inline bool SharedFuture<T>::try_wait() const
{
    detail::check_future_valid(this);
    if (!m_state->ready())
    {
        if (!carb::getCachedInterface<ITasking>()->try_wait(*this))
            return false;
        m_state->markReady();
    }
    return true;
}

template <class T>
inline void SharedFuture<T>::wait() const
{
    detail::check_future_valid(this);
    if (!m_state->ready())
    {
        carb::getCachedInterface<ITasking>()->wait(*this);
        m_state->markReady();
    }
}

template <class T>
template <class Rep, class Period>
inline bool SharedFuture<T>::wait_for(const std::chrono::duration<Rep, Period>& dur) const
{
    detail::check_future_valid(this);
    if (!m_state->ready())
    {
        if (!carb::getCachedInterface<ITasking>()->wait_for(dur, *this))
            return false;
        m_state->markReady();
    }
    return true;
}

template <class T>
template <class Clock, class Duration>
inline bool SharedFuture<T>::wait_until(const std::chrono::time_point<Clock, Duration>& when) const
{
    detail::check_future_valid(this);
    if (!m_state->ready())
    {
        if (!carb::getCachedInterface<ITasking>()->wait_until(when, *this))
            return false;
        m_state->markReady();
    }
    return true;
}

template <class T>
inline bool SharedFuture<T>::isCanceled() const
{
    detail::check_future_valid(this);
    return try_wait() && !m_state->m_type.has_value();
}

template <class T>
inline SharedFuture<T>::operator RequiredObject() const
{
    return m_state ? m_state->m_object : Object{ ObjectType::eNone, nullptr };
}

template <class T>
inline const TaskContext* SharedFuture<T>::task_if() const
{
    return m_state && m_state->isTask() ? reinterpret_cast<TaskContext*>(&m_state->m_object.data) : nullptr;
}

template <class T>
template <class Callable, class... Args>
inline auto SharedFuture<T>::then(Priority prio, Trackers&& trackers, Callable&& f, Args&&... args)
{
    detail::check_future_valid(this);
    RequiredObject req = *this;
    return carb::getCachedInterface<ITasking>()->addSubTask(
        req, prio, std::move(trackers),
        [t = *this, f = std::forward<Callable>(f), args = std::make_tuple(std::forward<Args>(args)...)]() mutable {
            return detail::applyExtra(std::move(f), std::move(args), t.get());
        });
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SharedFuture<T&>
template <class T>
inline SharedFuture<T&>::SharedFuture(const SharedFuture& other) noexcept : m_state(other.m_state)
{
    if (m_state)
        m_state->addRef();
}

template <class T>
inline SharedFuture<T&>::SharedFuture(SharedFuture&& other) noexcept : m_state(std::exchange(other.m_state, nullptr))
{
}

template <class T>
inline SharedFuture<T&>::SharedFuture(Future<T&>&& fut) noexcept : m_state(std::exchange(fut.m_state, nullptr))
{
}

template <class T>
inline SharedFuture<T&>::~SharedFuture()
{
    if (m_state)
        m_state->release();
}

template <class T>
inline SharedFuture<T&>& SharedFuture<T&>::operator=(const SharedFuture& other)
{
    if (other.m_state)
        other.m_state->addRef();
    if (m_state)
        m_state->release();
    m_state = other.m_state;
    return *this;
}

template <class T>
inline SharedFuture<T&>& SharedFuture<T&>::operator=(SharedFuture&& other) noexcept
{
    std::swap(m_state, other.m_state);
    return *this;
}

template <class T>
inline T& SharedFuture<T&>::get() const
{
    detail::check_future_valid(this);
    wait();
    return m_state->get();
}

template <class T>
inline bool SharedFuture<T&>::valid() const noexcept
{
    return m_state != nullptr;
}

template <class T>
inline bool SharedFuture<T&>::try_wait() const
{
    detail::check_future_valid(this);
    if (CARB_UNLIKELY(!m_state->ready()))
    {
        if (!carb::getCachedInterface<ITasking>()->try_wait(*this))
            return false;
        m_state->markReady();
    }
    return true;
}

template <class T>
inline void SharedFuture<T&>::wait() const
{
    detail::check_future_valid(this);
    if (CARB_UNLIKELY(!m_state->ready()))
    {
        carb::getCachedInterface<ITasking>()->wait(*this);
        m_state->markReady();
    }
}

template <class T>
template <class Rep, class Period>
inline bool SharedFuture<T&>::wait_for(const std::chrono::duration<Rep, Period>& dur) const
{
    detail::check_future_valid(this);
    if (CARB_UNLIKELY(!m_state->ready()))
    {
        if (!carb::getCachedInterface<ITasking>()->wait_for(dur, *this))
            return false;
        m_state->markReady();
    }
    return true;
}

template <class T>
template <class Clock, class Duration>
inline bool SharedFuture<T&>::wait_until(const std::chrono::time_point<Clock, Duration>& when) const
{
    detail::check_future_valid(this);
    if (CARB_UNLIKELY(!m_state->ready()))
    {
        if (!carb::getCachedInterface<ITasking>()->wait_until(when, *this))
            return false;
        m_state->markReady();
    }
    return true;
}

template <class T>
inline bool SharedFuture<T&>::isCanceled() const
{
    detail::check_future_valid(this);
    return try_wait() && !m_state->m_value;
}

template <class T>
inline SharedFuture<T&>::operator RequiredObject() const
{
    return m_state ? m_state->m_object : Object{ ObjectType::eNone, nullptr };
}

template <class T>
inline const TaskContext* SharedFuture<T&>::task_if() const
{
    return m_state && m_state->isTask() ? reinterpret_cast<const TaskContext*>(&m_state->m_object.data) : nullptr;
}

template <class T>
template <class Callable, class... Args>
inline auto SharedFuture<T&>::then(Priority prio, Trackers&& trackers, Callable&& f, Args&&... args)
{
    detail::check_future_valid(this);
    RequiredObject req = *this;
    return carb::getCachedInterface<ITasking>()->addSubTask(
        req, prio, std::move(trackers),
        [t = *this, f = std::forward<Callable>(f), args = std::make_tuple(std::forward<Args>(args)...)]() mutable {
            return detail::applyExtra(std::move(f), std::move(args), t.get());
        });
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SharedFuture<void>
inline SharedFuture<void>::SharedFuture(const SharedFuture<void>& other) noexcept : m_obj(other.m_obj)
{
    if (auto s = state())
        s->addRef();
}

inline SharedFuture<void>::SharedFuture(SharedFuture<void>&& other) noexcept
    : m_obj(std::exchange(other.m_obj, { ObjectType::eNone, nullptr }))
{
}

inline SharedFuture<void>::SharedFuture(Future<void>&& fut) noexcept
    : m_obj(std::exchange(fut.m_obj, { ObjectType::eNone, nullptr }))
{
}

inline SharedFuture<void>::~SharedFuture()
{
    if (auto s = state())
        s->release();
}

inline SharedFuture<void>& SharedFuture<void>::operator=(const SharedFuture<void>& other)
{
    if (auto s = other.state())
        s->addRef();
    if (auto s = state())
        s->release();
    m_obj = other.m_obj;
    return *this;
}

inline SharedFuture<void>& SharedFuture<void>::operator=(SharedFuture<void>&& other) noexcept
{
    std::swap(m_obj, other.m_obj);
    return *this;
}

inline void SharedFuture<void>::get() const
{
    detail::check_future_valid(this);
    wait();
}

inline bool SharedFuture<void>::valid() const noexcept
{
    if (state())
        return true;
    return reinterpret_cast<TaskContext>(m_obj.data) != kInvalidTaskContext;
}

inline bool SharedFuture<void>::try_wait() const
{
    detail::check_future_valid(this);
    auto s = state();
    if (s && s->ready())
        return true;
    return carb::getCachedInterface<ITasking>()->try_wait(*this);
}

inline void SharedFuture<void>::wait() const
{
    detail::check_future_valid(this);
    auto s = state();
    if (s && s->ready())
        return;
    carb::getCachedInterface<ITasking>()->wait(*this);
}

template <class Rep, class Period>
inline bool SharedFuture<void>::wait_for(const std::chrono::duration<Rep, Period>& dur) const
{
    detail::check_future_valid(this);
    auto s = state();
    if (s && s->ready())
        return true;
    return carb::getCachedInterface<ITasking>()->wait_for(dur, *this);
}

template <class Clock, class Duration>
inline bool SharedFuture<void>::wait_until(const std::chrono::time_point<Clock, Duration>& when) const
{
    detail::check_future_valid(this);
    auto s = state();
    if (s && s->ready())
        return true;
    return carb::getCachedInterface<ITasking>()->wait_until(when, *this);
}

inline SharedFuture<void>::operator RequiredObject() const
{
    if (auto s = state())
        return s->m_object;
    return m_obj;
}


inline const TaskContext* SharedFuture<void>::task_if() const
{
    auto s = state();
    if (s && s->isTask())
        return reinterpret_cast<const TaskContext*>(s->m_object.data);
    return m_obj.type == ObjectType::eTaskContext ? reinterpret_cast<const TaskContext*>(&m_obj.data) : nullptr;
}

template <class Callable, class... Args>
inline auto SharedFuture<void>::then(Priority prio, Trackers&& trackers, Callable&& f, Args&&... args)
{
    return carb::getCachedInterface<ITasking>()->addSubTask(
        *this, prio, std::move(trackers),
        [f = std::forward<Callable>(f), args = std::make_tuple(std::forward<Args>(args)...)]() mutable {
            return detail::applyExtra(std::move(f), std::move(args));
        });
}

inline detail::SharedState<void>* SharedFuture<void>::state() const
{
    return m_obj.type == ObjectType::eSharedState ? static_cast<detail::SharedState<void>*>(m_obj.data) : nullptr;
}

inline TaskContext* SharedFuture<void>::ptask()
{
    if (auto s = state())
        s->release();
    m_obj = Object{ ObjectType::eTaskContext, nullptr };
    return reinterpret_cast<TaskContext*>(&m_obj.data);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Promise<T>
template <class T>
inline Promise<T>::Promise() : m_state(new (carb::allocate(sizeof(State))) State())
{
}

template <class T>
inline Promise<T>::Promise(Promise&& other) noexcept : m_state(std::exchange(other.m_state, nullptr))
{
}

template <class T>
inline Promise<T>::~Promise()
{
    if (m_state)
    {
        auto old = m_state->m_futex.load(std::memory_order_relaxed);
        CARB_ASSERT(old == State::eReady || old == State::eUnset); // Should only be unset or set.
        if (old != 0)
        {
            // Mark as canceled since the promise is broken.
            m_state->m_futex.store(State::eReady, std::memory_order_release);
            m_state->notify();
        }
        m_state->release();
    }
}

template <class T>
inline Promise<T>& Promise<T>::operator=(Promise&& other) noexcept
{
    std::swap(m_state, other.m_state);
    return *this;
}

template <class T>
inline void Promise<T>::swap(Promise& other) noexcept
{
    std::swap(m_state, other.m_state);
}

template <class T>
inline Future<T> Promise<T>::get_future()
{
    CARB_UNLIKELY_IF(m_state->m_futureRetrieved.exchange(true, std::memory_order_acquire))
    {
        detail::future_error(std::future_errc::future_already_retrieved, "future already retrieved");
    }
    m_state->addRef();
    return Future<T>(m_state);
}

template <class T>
inline void Promise<T>::set_value(const T& value)
{
    m_state->set(value);
    m_state->notify();
}

template <class T>
inline void Promise<T>::set_value(T&& value)
{
    m_state->set(std::move(value));
    m_state->notify();
}

template <class T>
inline void Promise<T>::setCanceled()
{
    auto prev = State::eUnset;
    CARB_UNLIKELY_IF(!m_state->m_futex.compare_exchange_strong(prev, State::eReady, std::memory_order_seq_cst))
    {
        detail::future_error(std::future_errc::promise_already_satisfied, "promise already satisfied");
    }
    m_state->notify();
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Promise<T&>

template <class T>
inline Promise<T&>::Promise() : m_state(new (carb::allocate(sizeof(State))) State())
{
}

template <class T>
inline Promise<T&>::Promise(Promise&& other) noexcept : m_state(std::exchange(other.m_state, nullptr))
{
}

template <class T>
inline Promise<T&>::~Promise()
{
    if (m_state)
    {
        auto old = m_state->m_futex.load(std::memory_order_relaxed);
        CARB_ASSERT(old == State::eReady || old == State::eUnset);
        if (old != 0)
        {
            // Mark as canceled since the promise is broken.
            m_state->m_futex.store(State::eReady, std::memory_order_release);
            m_state->notify();
        }
        m_state->release();
    }
}

template <class T>
inline Promise<T&>& Promise<T&>::operator=(Promise&& other) noexcept
{
    std::swap(m_state, other.m_state);
    return *this;
}

template <class T>
inline void Promise<T&>::swap(Promise& other) noexcept
{
    std::swap(m_state, other.m_state);
}

template <class T>
inline Future<T&> Promise<T&>::get_future()
{
    CARB_UNLIKELY_IF(m_state->m_futureRetrieved.exchange(true, std::memory_order_acquire))
    {
        detail::future_error(std::future_errc::future_already_retrieved, "future already retrieved");
    }
    m_state->addRef();
    return Future<T&>(m_state);
}

template <class T>
inline void Promise<T&>::set_value(T& value)
{
    m_state->set(value);
    m_state->notify();
}

template <class T>
inline void Promise<T&>::setCanceled()
{
    auto prev = State::eUnset;
    CARB_UNLIKELY_IF(!m_state->m_futex.compare_exchange_strong(prev, State::eReady, std::memory_order_seq_cst))
    {
        detail::future_error(std::future_errc::promise_already_satisfied, "promise already satisfied");
    }
    m_state->notify();
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Promise<void>
inline Promise<void>::Promise() : m_state(new (carb::allocate(sizeof(State))) State())
{
}

inline Promise<void>::Promise(Promise&& other) noexcept : m_state(std::exchange(other.m_state, nullptr))
{
}

inline Promise<void>::~Promise()
{
    if (m_state)
    {
        auto old = m_state->m_futex.load(std::memory_order_relaxed);
        CARB_ASSERT(old == State::eReady || old == State::eUnset); // Should only be unset or set.
        if (old != 0)
        {
            // Mark as canceled since the promise is broken.
            m_state->m_futex.store(State::eReady, std::memory_order_release);
            m_state->notify();
        }
        m_state->release();
    }
}

inline Promise<void>& Promise<void>::operator=(Promise&& other) noexcept
{
    std::swap(m_state, other.m_state);
    return *this;
}


inline void Promise<void>::swap(Promise& other) noexcept
{
    std::swap(m_state, other.m_state);
}

inline Future<void> Promise<void>::get_future()
{
    CARB_UNLIKELY_IF(m_state->m_futureRetrieved.exchange(true, std::memory_order_acquire))
    {
        detail::future_error(std::future_errc::future_already_retrieved, "future already retrieved");
    }
    m_state->addRef();
    return Future<void>(m_state);
}

inline void Promise<void>::set_value()
{
    m_state->set();
    m_state->notify();
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ITasking

inline void ITasking::yieldUntilCounterPinThread(RequiredObject obj)
{
    PinGuard pin;
    wait(std::move(obj));
}

inline void ITasking::yieldUntilCounter(RequiredObject obj)
{
    wait(obj);
}

inline bool ITasking::timedYieldUntilCounter(RequiredObject obj, uint64_t timeoutNs)
{
    return internalTimedWait(obj, timeoutNs);
}

inline void ITasking::lockMutex(Mutex* mutex)
{
    bool b = timedLockMutex(mutex, kInfinite);
    CARB_ASSERT(b);
    CARB_UNUSED(b);
}

inline bool ITasking::waitForTask(TaskContext task)
{
    return internalTimedWait({ ObjectType::eTaskContext, reinterpret_cast<void*>(task) }, kInfinite);
}

inline bool ITasking::try_wait(RequiredObject req)
{
    return internalTimedWait(req, 0);
}

inline void ITasking::wait(RequiredObject req)
{
    bool b = internalTimedWait(req, kInfinite);
    CARB_ASSERT(b);
    CARB_UNUSED(b);
}

template <class Rep, class Period>
inline bool ITasking::wait_for(std::chrono::duration<Rep, Period> dur, RequiredObject req)
{
    return internalTimedWait(req, detail::convertDuration(dur));
}

template <class Clock, class Duration>
inline bool ITasking::wait_until(std::chrono::time_point<Clock, Duration> when, RequiredObject req)
{
    return internalTimedWait(req, detail::convertAbsTime(when));
}

inline void ITasking::waitSemaphore(Semaphore* sema)
{
    bool b = timedWaitSemaphore(sema, kInfinite);
    CARB_ASSERT(b);
    CARB_UNUSED(b);
}

inline void ITasking::lockSharedMutex(SharedMutex* mutex)
{
    bool b = timedLockSharedMutex(mutex, kInfinite);
    CARB_ASSERT(b);
    CARB_UNUSED(b);
}

inline void ITasking::lockSharedMutexExclusive(SharedMutex* mutex)
{
    bool b = timedLockSharedMutexExclusive(mutex, kInfinite);
    CARB_ASSERT(b);
    CARB_UNUSED(b);
}

inline void ITasking::waitConditionVariable(ConditionVariable* cv, Mutex* mutex)
{
    bool b = timedWaitConditionVariable(cv, mutex, kInfinite);
    CARB_ASSERT(b);
    CARB_UNUSED(b);
}

inline void ITasking::bindTrackers(RequiredObject requiredObject, Trackers&& trackers)
{
    const Tracker* ptrackers{};
    size_t numTrackers{};
    trackers.output(ptrackers, numTrackers);
    internalBindTrackers(requiredObject, ptrackers, numTrackers);
}

template <class Callable, class... Args>
inline auto ITasking::awaitSyncTask(Priority priority, Callable&& f, Args&&... args)
{
    if (getTaskContext() != kInvalidTaskContext)
    {
        // Call directly
        return carb::cpp::invoke(std::forward<Callable>(f), std::forward<Args>(args)...);
    }
    else
    {
        // Call within a task and return the result.
        return addTask(priority, {}, std::forward<Callable>(f), std::forward<Args>(args)...).get();
    }
}

template <class Callable, class... Args>
inline auto ITasking::addTask(Priority priority, Trackers&& trackers, Callable&& f, Args&&... args)
{
    TaskDesc desc{};
    desc.priority = priority;
    using RetType = typename cpp::invoke_result_t<Callable, Args...>;
    return detail::GenerateFuture<RetType>()(this, trackers.fill(desc.trackers, desc.numTrackers), desc,
                                             std::forward<Callable>(f), std::forward<Args>(args)...);
}

template <class Callable, class... Args>
inline auto ITasking::addThrottledTask(
    Semaphore* throttler, Priority priority, Trackers&& trackers, Callable&& f, Args&&... args)
{
    TaskDesc desc{};
    desc.priority = priority;
    desc.waitSemaphore = throttler;
    using RetType = typename cpp::invoke_result_t<Callable, Args...>;
    return detail::GenerateFuture<RetType>()(this, trackers.fill(desc.trackers, desc.numTrackers), desc,
                                             std::forward<Callable>(f), std::forward<Args>(args)...);
}

template <class Callable, class... Args>
inline auto ITasking::addSubTask(
    RequiredObject requiredObj, Priority priority, Trackers&& trackers, Callable&& f, Args&&... args)
{
    TaskDesc desc{};
    desc.priority = priority;
    desc.requiredObject = requiredObj;
    using RetType = typename cpp::invoke_result_t<Callable, Args...>;
    return detail::GenerateFuture<RetType>()(this, trackers.fill(desc.trackers, desc.numTrackers), desc,
                                             std::forward<Callable>(f), std::forward<Args>(args)...);
}

template <class Callable, class... Args>
inline auto ITasking::addThrottledSubTask(
    RequiredObject requiredObj, Semaphore* throttler, Priority priority, Trackers&& trackers, Callable&& f, Args&&... args)
{
    TaskDesc desc{};
    desc.priority = priority;
    desc.requiredObject = requiredObj;
    desc.waitSemaphore = throttler;
    using RetType = typename cpp::invoke_result_t<Callable, Args...>;
    return detail::GenerateFuture<RetType>()(this, trackers.fill(desc.trackers, desc.numTrackers), desc,
                                             std::forward<Callable>(f), std::forward<Args>(args)...);
}

template <class Callable, class Rep, class Period, class... Args>
inline auto ITasking::addTaskIn(
    const std::chrono::duration<Rep, Period>& dur, Priority priority, Trackers&& trackers, Callable&& f, Args&&... args)
{
    using RetType = typename cpp::invoke_result_t<Callable, Args...>;
    TaskDesc desc{};
    desc.priority = priority;
    return detail::GenerateFuture<RetType>()(this, dur, trackers.fill(desc.trackers, desc.numTrackers), desc,
                                             std::forward<Callable>(f), std::forward<Args>(args)...);
}

template <class Callable, class Clock, class Duration, class... Args>
inline auto ITasking::addTaskAt(const std::chrono::time_point<Clock, Duration>& when,
                                Priority priority,
                                Trackers&& trackers,
                                Callable&& f,
                                Args&&... args)
{
    using RetType = typename cpp::invoke_result_t<Callable, Args...>;
    TaskDesc desc{};
    desc.priority = priority;
    return detail::GenerateFuture<RetType>()(this, when, trackers.fill(desc.trackers, desc.numTrackers), desc,
                                             std::forward<Callable>(f), std::forward<Args>(args)...);
}

template <class Callable, class... Args>
inline void ITasking::applyRange(size_t range, Callable f, Args&&... args)
{
#if CARB_VERSION_ATLEAST(carb_tasking_ITasking, 2, 5)
    auto& ar = internalGetIApplyRange(carb_tasking_ITasking);

    uint32_t taskThreads;
    CARB_UNLIKELY_IF(range <= 1 || (taskThreads = ar.getThreadCount()) <= 1)
    {
        for (size_t i = 0; i != range; ++i)
            cpp::invoke(f, args..., i);
        return;
    }

    auto lambda = [&](size_t begin, size_t end) noexcept(noexcept(cpp::invoke(f, std::declval<Args>()..., size_t(0)))) {
        do
        {
            cpp::invoke(f, args..., begin++);
        } while (begin != end);
    };
    detail::DefaultPartitioner partitioner{ ar, taskThreads };
    detail::ApplyRange<detail::Range<size_t>, decltype(lambda), detail::DefaultPartitioner>::Run(
        ar, detail::Range<size_t>(0, range), lambda, partitioner);
#else
    CARB_UNLIKELY_IF(range <= 1)
    {
        for (size_t i = 0; i != range; ++i)
            cpp::invoke(f, args..., i);
        return;
    }
    using Tuple = std::tuple<std::decay_t<Args>...>;
    using Data = carb::EmptyMemberPair<Tuple, Callable*>;
    Data data{ carb::InitBoth{}, Tuple{ std::forward<Args>(args)... }, &f };
    auto callFunctor = [](size_t index, void* context) {
        Data* pData = static_cast<Data*>(context);
        detail::applyExtra(*pData->second, pData->first(), index);
    };
    return internalApplyRange(range, callFunctor, &data);
#endif
}

template <class Callable, class... Args>
inline void ITasking::applyRangeBatch(size_t range, size_t batchHint, Callable f, Args&&... args)
{
#if CARB_VERSION_ATLEAST(carb_tasking_ITasking, 2, 5)
    auto& ar = internalGetIApplyRange(carb_tasking_ITasking);

    uint32_t taskThreads;
    CARB_UNLIKELY_IF(range <= 1 || range <= batchHint || (taskThreads = ar.getThreadCount()) <= 1)
    {
        if (range)
            cpp::invoke(std::forward<Callable>(f), std::forward<Args>(args)..., 0, range);
        return;
    }

    auto lambda = [&](size_t begin, size_t end) noexcept(noexcept(cpp::invoke(
                      f, std::declval<Args>()..., size_t(0), size_t(1)))) { cpp::invoke(f, args..., begin, end); };
    detail::DefaultPartitioner partitioner{ ar, taskThreads };
    detail::ApplyRange<detail::Range<size_t>, decltype(lambda), detail::DefaultPartitioner>::Run(
        ar, detail::Range<size_t>(0, range, ::carb_max<size_t>(1, batchHint)), lambda, partitioner);
#else
    CARB_UNLIKELY_IF(range <= 1 || range <= batchHint)
    {
        if (range)
            cpp::invoke(f, std::forward<Args>(args)..., 0, range);
        return;
    }
    using Tuple = std::tuple<std::decay_t<Args>...>;
    using Data = carb::EmptyMemberPair<Tuple, Callable*>;
    Data data{ carb::InitBoth{}, Tuple{ std::forward<Args>(args)... }, &f };
    auto callFunctor = [](size_t startIndex, size_t endIndex, void* context) {
        Data* pData = static_cast<Data*>(context);
        detail::applyExtra(*pData->second, pData->first(), startIndex, endIndex);
    };
    return internalApplyRangeBatch(range, batchHint, callFunctor, &data);
#endif
}

template <class T, class Callable, class... Args>
inline void ITasking::parallelFor(T begin, T end, Callable f, Args&&... args)
{
    using Tuple = std::tuple<std::decay_t<Args>...>;
    using Tuple2 = std::tuple<const T, Callable*>;
    using Data = carb::EmptyMemberPair<Tuple, Tuple2>;
    Data data{ carb::InitBoth{}, Tuple{ std::forward<Args>(args)... }, Tuple2{ begin, &f } };
    auto callFunctor = [](size_t index, void* context) {
        Data* pData = static_cast<Data*>(context);
        detail::applyExtra(*std::get<1>(pData->second), pData->first(), std::get<0>(pData->second) + T(index));
    };
    CARB_ASSERT(end >= begin);
    return internalApplyRange(size_t(end - begin), callFunctor, &data);
}

template <class T, class Callable, class... Args>
inline void ITasking::parallelFor(T begin, T end, T step, Callable f, Args&&... args)
{
    using Tuple = std::tuple<std::decay_t<Args>...>;
    using Tuple2 = std::tuple<const T, const T, Callable*>;
    using Data = carb::EmptyMemberPair<Tuple, Tuple2>;
    Data data{ carb::InitBoth{}, Tuple{ std::forward<Args>(args)... }, Tuple2{ begin, step, &f } };
    auto callFunctor = [](size_t index, void* context) {
        Data* pData = static_cast<Data*>(context);
        detail::applyExtra(*std::get<2>(pData->second), pData->first(),
                           std::get<0>(pData->second) + (std::get<1>(pData->second) * T(index)));
    };
    CARB_ASSERT(step != T(0));
    CARB_ASSERT((end >= begin && step >= T(0)) || (step < T(0)));
    return internalApplyRange(size_t((end - begin) / step), callFunctor, &data);
}

#if CARB_VERSION_ATLEAST(carb_tasking_ITasking, 2, 5)
template <class Body>
inline void ITasking::parallelReduce(size_t range, size_t batchHint, Body& body)
{
    CARB_LIKELY_IF(range != 0)
    {
        auto& ar = internalGetIApplyRange(carb_tasking_ITasking);

        detail::DefaultPartitioner partitioner{ ar, ar.getThreadCount() };
        detail::ParallelReduce<detail::Range<size_t>, Body, detail::DefaultPartitioner>::Run(
            ar, detail::Range<size_t>(0, range, ::carb_max<size_t>(1, batchHint)), body, partitioner);
    }
}
#endif

} // namespace tasking
} // namespace carb
