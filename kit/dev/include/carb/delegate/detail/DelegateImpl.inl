// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "../../cpp/Atomic.h"
#include "../../cpp/Functional.h"

#include <tuple>
#include <type_traits>

CARB_IGNOREWARNING_CLANG_WITH_PUSH("-Wunused-local-typedef") // unused type alias 'Tuple'

namespace carb
{
namespace delegate
{
namespace detail
{

template <class F, class Tuple, size_t... I, class... Args>
constexpr decltype(auto) applyExtraImpl(F&& f, Tuple&& t, std::index_sequence<I...>, Args&&... args)
{
    return carb::cpp::invoke(std::forward<F>(f), std::get<I>(std::forward<Tuple>(t))..., std::forward<Args>(args)...);
}

// like std::apply() but allows additional args
template <class F, class Tuple, class... Args>
constexpr decltype(auto) applyExtra(F&& f, Tuple&& t, Args&&... args)
{
    return applyExtraImpl(std::forward<F>(f), std::forward<Tuple>(t),
                          std::make_index_sequence<std::tuple_size<std::remove_reference_t<Tuple>>::value>{},
                          std::forward<Args>(args)...);
}

// Returns a unique identifier for a type that doesn't require RTTI like type_info
template <class T>
size_t typeId()
{
    static const bool addr{ false };
    return size_t(std::addressof(addr));
}

template <class Mutex, class Exec, class... Args>
DelegateBase<Mutex, Exec, void(Args...)>::DelegateBase(DelegateBase&& other)
    : m_impl(std::exchange(other.m_impl, std::make_shared<Impl>()))
{
}

template <class Mutex, class Exec, class... Args>
constexpr DelegateBase<Mutex, Exec, void(Args...)>::DelegateBase(std::nullptr_t) : m_impl{}
{
}

template <class Mutex, class Exec, class... Args>
auto DelegateBase<Mutex, Exec, void(Args...)>::operator=(DelegateBase&& other) -> DelegateBase&
{
    swap(other);
    return *this;
}

template <class Mutex, class Exec, class... Args>
void DelegateBase<Mutex, Exec, void(Args...)>::swap(DelegateBase& other)
{
    std::swap(m_impl, other.m_impl);
}

template <class Mutex, class Exec, class... Args>
DelegateBase<Mutex, Exec, void(Args...)>::~DelegateBase()
{
    // The only time that m_impl is allowed to be `nullptr` is an empty DelegateRef.
    if (m_impl)
    {
        // UnbindAll() will wait for calls in progress by unbound callbacks to complete before returning, but will allow
        // calls from the current thread to remain.
        UnbindAll();
    }
}

template <class Mutex, class Exec, class... Args>
template <class Callable, class... BindArgs>
auto DelegateBase<Mutex, Exec, void(Args...)>::Bind(Handle* hOut, Callable&& func, BindArgs&&... args) -> Handle
{
    using Base = KeyedBinding<Handle>;
    struct Binding : Base
    {
        using Tuple = std::tuple<std::decay_t<BindArgs>...>;
        std::decay_t<Callable> func;
        Tuple bindArgs;
        Binding(Handle h, Callable&& func_, BindArgs&&... args)
            : Base(h), func(std::forward<Callable>(func_)), bindArgs(std::forward<BindArgs>(args)...)
        {
        }

        void Call(Args... args) override
        {
            detail::applyExtra(func, bindArgs, args...);
        }
    };
    Handle h(nextHandle());
    if (hOut)
    {
        *hOut = h;
    }
    Binding* b = new Binding(h, std::forward<Callable>(func), std::forward<BindArgs>(args)...);

    std::lock_guard<Mutex> g(m_impl->m_mutex);
    ActiveCall* call = lastCurrentThreadCall();
    if (!call)
    {
        m_impl->m_entries.push_back(*b);
    }
    else
    {
        call->newEntries.push_back(*b);
    }

    return h;
}

template <class Mutex, class Exec, class... Args>
template <class KeyType, class Callable, class... BindArgs>
void DelegateBase<Mutex, Exec, void(Args...)>::BindWithKey(KeyType&& key, Callable&& func, BindArgs&&... args)
{
    static_assert(!std::is_same<Handle, std::decay_t<KeyType>>::value, "Handle not allowed as a key type (use Bind())");
    static_assert(
        !std::is_null_pointer<std::decay_t<KeyType>>::value, "nullptr_t not allowed as a key type (use Bind())");
    using Base = KeyedBinding<std::decay_t<KeyType>>;
    struct Binding : Base
    {
        using Tuple = std::tuple<std::decay_t<BindArgs>...>;
        std::decay_t<Callable> func;
        Tuple bindArgs;
        Binding(KeyType&& key, Callable&& func_, BindArgs&&... args)
            : Base(std::forward<KeyType>(key)),
              func(std::forward<Callable>(func_)),
              bindArgs(std::forward<BindArgs>(args)...)
        {
        }

        void Call(Args... args) override
        {
            detail::applyExtra(func, bindArgs, args...);
        }
    };
    Binding* b = new Binding(std::forward<KeyType>(key), std::forward<Callable>(func), std::forward<BindArgs>(args)...);

    std::lock_guard<Mutex> g(m_impl->m_mutex);
    ActiveCall* call = lastCurrentThreadCall();
    if (!call)
    {
        m_impl->m_entries.push_back(*b);
    }
    else
    {
        call->newEntries.push_back(*b);
    }
}

template <class Mutex, class Exec, class... Args>
template <class KeyType>
bool DelegateBase<Mutex, Exec, void(Args...)>::Unbind(KeyType&& key)
{
    using BindingType = KeyedBinding<std::decay_t<KeyType>>;
    std::unique_lock<Mutex> g(m_impl->m_mutex);
    for (auto iter = m_impl->m_entries.begin(); iter != m_impl->m_entries.end(); ++iter)
    {
        if (iter->getKeyType() == BindingType::keyType())
        {
            BindingType& binding = static_cast<BindingType&>(*iter);
            if (binding.key == key)
            {
                UnbindInternal(g, iter);
                return true;
            }
        }
    }

    // Must belong to a specific list. Find it and remove it.
    for (auto& active : m_impl->m_activeCalls)
    {
        for (auto& entry : active.newEntries)
        {
            if (entry.getKeyType() == BindingType::keyType())
            {
                BindingType& binding = static_cast<BindingType&>(entry);
                if (binding.key == key)
                {
                    active.newEntries.remove(entry);
                    entry.release();
                    return true;
                }
            }
        }
    }

    return false;
}

template <class Mutex, class Exec, class... Args>
template <class KeyType>
bool DelegateBase<Mutex, Exec, void(Args...)>::HasKey(KeyType&& key) const noexcept
{
    using BindingType = KeyedBinding<std::decay_t<KeyType>>;
    std::unique_lock<Mutex> g(m_impl->m_mutex);
    for (auto iter = m_impl->m_entries.begin(); iter != m_impl->m_entries.end(); ++iter)
    {
        if (iter->getKeyType() == BindingType::keyType())
        {
            BindingType& binding = static_cast<BindingType&>(*iter);
            if (binding.key == key)
            {
                return true;
            }
        }
    }

    // May belong to a specific list
    for (auto& active : m_impl->m_activeCalls)
    {
        for (auto& entry : active.newEntries)
        {
            if (entry.getKeyType() == BindingType::keyType())
            {
                BindingType& binding = static_cast<BindingType&>(entry);
                if (binding.key == key)
                {
                    return true;
                }
            }
        }
    }

    return false;
}

template <class Mutex, class Exec, class... Args>
bool DelegateBase<Mutex, Exec, void(Args...)>::UnbindCurrent()
{
    std::unique_lock<Mutex> g(m_impl->m_mutex);

    ActiveCall* ac = lastCurrentThreadCall();
    if (ac && ac->cur != m_impl->m_entries.end())
    {
        UnbindInternal(g, ac->cur);
        return true;
    }
    return false;
}

template <class Mutex, class Exec, class... Args>
void DelegateBase<Mutex, Exec, void(Args...)>::UnbindAll()
{
    std::unique_lock<Mutex> g(m_impl->m_mutex);

    while (m_impl->m_entries.rbegin() != m_impl->m_entries.rend())
    {
        UnbindInternal(g, --m_impl->m_entries.rbegin().base());
        // UnbindInternal() unlocks, so re-lock here
        g.lock();
    }

    for (auto& active : m_impl->m_activeCalls)
    {
        while (!active.newEntries.empty())
        {
            active.newEntries.remove(active.newEntries.front()).release();
        }
    }
}

template <class Mutex, class Exec, class... Args>
size_t DelegateBase<Mutex, Exec, void(Args...)>::Count() const noexcept
{
    // TSan (rightly) complains about a data race here, but this isn't that useful in a multi-threaded setting, so WAR
    CARB_IF_TSAN(std::unique_lock<Mutex> g(m_impl->m_mutex);)
    return m_impl->m_entries.size();
}

template <class Mutex, class Exec, class... Args>
bool DelegateBase<Mutex, Exec, void(Args...)>::HasPending() const noexcept
{
    std::unique_lock<Mutex> g(m_impl->m_mutex);
    for (auto& active : m_impl->m_activeCalls)
    {
        if (!active.newEntries.empty())
            return true;
    }
    return false;
}

template <class Mutex, class Exec, class... Args>
bool DelegateBase<Mutex, Exec, void(Args...)>::IsEmpty() const noexcept
{
    std::unique_lock<Mutex> g(m_impl->m_mutex);
    if (!m_impl->m_entries.empty())
        return false;

    for (auto& active : m_impl->m_activeCalls)
    {
        if (!active.newEntries.empty())
            return false;
    }

    return true;
}

template <class Mutex, class Exec, class... Args>
template <class KeyType>
std::vector<std::decay_t<KeyType>> DelegateBase<Mutex, Exec, void(Args...)>::GetKeysByType() const
{
    std::vector<std::decay_t<KeyType>> vec;

    using BindingType = KeyedBinding<std::decay_t<KeyType>>;
    std::unique_lock<Mutex> g(m_impl->m_mutex);

    for (auto& entry : m_impl->m_entries)
    {
        if (entry.getKeyType() == BindingType::keyType())
        {
            const BindingType& binding = static_cast<const BindingType&>(entry);
            vec.emplace_back(binding.key);
        }
    }

    for (auto& active : m_impl->m_activeCalls)
    {
        for (auto& entry : active.newEntries)
        {
            if (entry.getKeyType() == BindingType::keyType())
            {
                const BindingType& binding = static_cast<const BindingType&>(entry);
                vec.emplace_back(binding.key);
            }
        }
    }

    return vec;
}

template <class Mutex, class Exec, class... Args>
void DelegateBase<Mutex, Exec, void(Args...)>::Call(Args... args)
{
    std::shared_ptr<Impl> impl;
    std::unique_lock<Mutex> g(m_impl->m_mutex);

    // Early out if there is nothing to do
    if (m_impl->m_entries.empty())
    {
        return;
    }

    impl = m_impl; // Hold a reference while calling

    ActiveCall activeCall;
    impl->m_activeCalls.push_back(activeCall);

    activeCall.next = activeCall.cur = impl->m_entries.begin();
    ++activeCall.next;

    for (;;)
    {
        BaseBinding& cc = *activeCall.cur;
        cc.addRef();
        g.unlock();

        cc.Call(args...);

        g.lock();
        cc.release(activeCall.cur == impl->m_entries.end());

        activeCall.cur = activeCall.next;
        if (activeCall.cur == impl->m_entries.end())
        {
            break;
        }

        ++activeCall.next;
    }

    impl->m_activeCalls.remove(activeCall);

    if (!activeCall.newEntries.empty())
    {
        // Add the new entries to the end of the list
        BaseBinding& cc = activeCall.newEntries.front();
        impl->m_entries.splice(impl->m_entries.end(), activeCall.newEntries);
        auto newiter = impl->m_entries.iter_from_value(cc);

        // Add the new entries to any active calls in progress
        for (auto& call : impl->m_activeCalls)
        {
            if (call.next == impl->m_entries.end())
            {
                call.next = newiter;
            }
        }
    }
}

template <class Mutex, class Exec, class... Args>
void DelegateBase<Mutex, Exec, void(Args...)>::operator()(Args... args)
{
    Call(std::forward<Args>(args)...);
}

template <class Mutex, class Exec, class... Args>
struct DelegateBase<Mutex, Exec, void(Args...)>::BaseBinding
{
    constexpr BaseBinding() = default;
    virtual ~BaseBinding() = default;

    virtual size_t getKeyType() const = 0;

    virtual void Call(Args...) = 0;

    void addRef() noexcept
    {
        auto old = refCount.fetch_add(1, std::memory_order_relaxed);
        CARB_UNUSED(old);
        CARB_ASSERT(old != 0); // no resurrection
        CARB_ASSERT((old + 1) != 0); // no rollover
    }
    void addRefs(size_t count) noexcept
    {
        auto old = refCount.fetch_add(count, std::memory_order_relaxed);
        CARB_UNUSED(old);
        CARB_ASSERT(old != 0); // no resurrection
        CARB_ASSERT((old + count) >= old); // no rollover or negative
    }
    void release(bool notifyLastRef = false)
    {
        auto const current = (refCount.fetch_sub(1, std::memory_order_release) - 1);
        CARB_ASSERT((current + 1) != 0); // no rollover/double-release
        if (current == 1 && notifyLastRef)
        {
            refCount.notify_one();
        }
        if (current == 0)
        {
            std::atomic_thread_fence(std::memory_order_acquire);
            delete this;
        }
    }
    void waitForLastRef()
    {
        auto ref = refCount.load(std::memory_order_relaxed);
        while (ref != 1)
        {
            refCount.wait(ref, std::memory_order_relaxed);
            ref = refCount.load(std::memory_order_relaxed);
        }
    }

    carb::cpp::atomic_size_t refCount{ 1 };
    carb::container::IntrusiveListLink<BaseBinding> link;
};

template <class Mutex, class Exec, class... Args>
template <class KeyType>
struct DelegateBase<Mutex, Exec, void(Args...)>::KeyedBinding : BaseBinding
{
    // Ensure that KeyType is a decayed type
    static_assert(std::is_same<std::decay_t<KeyType>, KeyType>::value, "Must be decayed!");

    static size_t keyType()
    {
        return detail::typeId<KeyType>();
    }

    virtual size_t getKeyType() const override
    {
        return keyType();
    }

    KeyType const key;

    template <class Key>
    constexpr KeyedBinding(Key&& key_) : BaseBinding(), key(std::forward<Key>(key_))
    {
    }
};

template <class Mutex, class Exec, class... Args>
struct DelegateBase<Mutex, Exec, void(Args...)>::ActiveCall
{
    typename Container::iterator cur;
    typename Container::iterator next;
    ExecutorId executorId{ Exec{}() };
    Container newEntries;

    carb::container::IntrusiveListLink<ActiveCall> link;
};

template <class Mutex, class Exec, class... Args>
struct DelegateBase<Mutex, Exec, void(Args...)>::Impl : public std::enable_shared_from_this<Impl>
{
    mutable Mutex m_mutex;
    Container m_entries;
    ActiveCallList m_activeCalls;

    ~Impl()
    {
        // Cannot be destroyed while in an active call!
        CARB_CHECK(m_activeCalls.empty());
    }
};

template <class Mutex, class Exec, class... Args>
auto DelegateBase<Mutex, Exec, void(Args...)>::lastCurrentThreadCall() -> ActiveCall*
{
    if (!m_impl->m_activeCalls.empty())
    {
        const auto executorId = Exec{}();
        for (auto iter = m_impl->m_activeCalls.rbegin(); iter != m_impl->m_activeCalls.rend(); ++iter)
        {
            if (iter->executorId == executorId)
            {
                return std::addressof(*iter);
            }
        }
    }
    return nullptr;
}

template <class Mutex, class Exec, class... Args>
auto DelegateBase<Mutex, Exec, void(Args...)>::lastCurrentThreadCall() const -> const ActiveCall*
{
    if (!m_impl->m_activeCalls.empty())
    {
        const auto executorId = Exec{}();
        for (auto iter = m_impl->m_activeCalls.rbegin(); iter != m_impl->m_activeCalls.rend(); ++iter)
        {
            if (iter->executorId == executorId)
            {
                return std::addressof(*iter);
            }
        }
    }
    return nullptr;
}

template <class Mutex, class Exec, class... Args>
void DelegateBase<Mutex, Exec, void(Args...)>::UnbindInternal(std::unique_lock<Mutex>& g,
                                                              typename Container::iterator iter)
{
    // Found it. See if it's involved in any active calls and wait.
    bool hasActiveInOtherThreads = false;
    size_t thisExecutorActiveCount = 0;
    if (!m_impl->m_activeCalls.empty())
    {
        const auto thisExecutor = Exec{}();
        for (auto& active : m_impl->m_activeCalls)
        {
            // Skip if next
            if (active.next == iter)
            {
                ++active.next;
            }
            // Handle if current
            if (active.cur == iter)
            {
                // Clear the current entry. This signals to the ActiveCall that we're waiting on it.
                active.cur = m_impl->m_entries.end();
                if (active.executorId != thisExecutor)
                {
                    hasActiveInOtherThreads = true;
                }
                else
                {
                    // Since we want to wait for the last ref, release any references that the current thread has on it.
                    ++thisExecutorActiveCount;
                    iter->release();
                }
            }
        }
    }

    BaseBinding& cc = *iter;
    m_impl->m_entries.remove(iter);
    g.unlock();

    if (hasActiveInOtherThreads)
    {
        cc.waitForLastRef();
    }
    if (thisExecutorActiveCount)
    {
        // Add back any references that the current thread was holding
        cc.addRefs(thisExecutorActiveCount);
    }
    // Release the implicit ref. If the current thread was holding any references, the earliest Call() will be the one
    // to actually release it.
    cc.release();
}

template <class Mutex, class Exec, class... Args>
size_t DelegateBase<Mutex, Exec, void(Args...)>::nextHandle()
{
    static std::atomic_size_t handle{ 1 };
    size_t val;
    do
    {
        val = handle.fetch_add(1, std::memory_order_relaxed);
    } while (CARB_UNLIKELY(val == 0));
    return val;
}

} // namespace detail
} // namespace delegate

} // namespace carb

CARB_IGNOREWARNING_CLANG_POP
