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
//! @brief C++20 coroutine helpers
#pragma once

#include "Defines.h"

#if CARB_HAS_CPP20 && defined __cpp_lib_coroutine

#    include <coroutine>

namespace carb
{
namespace coro
{

//! A minimal C++20 coroutine implementation for coroutines that can be ignored.
struct Ignore
{
    //! Defines the promise_type required by C++20 coroutines.
    struct promise_type
    {
#    ifndef DOXYGEN_BUILD
        // clang-format off
        Ignore get_return_object() { return Ignore{}; }
        void unhandled_exception() noexcept {}
        void return_void() noexcept {}
        std::suspend_never initial_suspend() noexcept { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }
        // clang-format on
#    endif
    };
};

//! A complex C++20 coroutine type that supports results and awaiting.
template <class Result = void>
struct Task
{
    //! Default constructor.
    constexpr Task() noexcept = default;

    //! Destructor.
    ~Task()
    {
        if (m_handle)
            m_handle.destroy();
    }

    CARB_PREVENT_COPY(Task);

    //! Move constructor.
    //! @param other The \ref Task to move from.
    Task(Task&& other) : m_handle(std::move(other.m_handle))
    {
        other.m_handle = {};
    }

    //! Move-assign operator.
    //! @param other The \ref Task to move from.
    //! @returns `*this`.
    Task& operator=(Task&& other)
    {
        std::swap(other.m_handle, m_handle);
        return *this;
    }

    //! The promise_type required by C++20 coroutines.
    struct promise_type;

#    ifndef DOXYGEN_BUILD
    // Awaiter implementations. Lots of boilerplate C++20 required functions.
    // The gist is that Awaiter will store the handle of the calling coroutine as `m_continuation` in the promise, and
    // the ResumeCaller 'awaiter' will resume that coroutine.
    struct Awaiter
    {
        std::coroutine_handle<promise_type> m_handle;

        bool await_ready() const noexcept
        {
            return !m_handle || m_handle.done();
        }

        auto await_suspend(std::coroutine_handle<> caller) noexcept
        {
            m_handle.promise().m_continuation = caller;
            return m_handle;
        }

        // clang-format off
        template <typename T = Result> requires(std::is_same_v<T, void>)
        void await_resume() noexcept
        {
            if (m_handle.promise().m_exc)
                std::rethrow_exception(m_handle.promise().m_exc);
        }

        template <typename T = Result> requires(!std::is_same_v<T, void>)
        T await_resume() noexcept
        {
            if (m_handle.promise().m_exc)
                std::rethrow_exception(m_handle.promise().m_exc);
            return m_handle.promise().m_result;
        }
        // clang-format on
    };

    struct ResumeCaller
    {
        // clang-format off
        bool await_ready() const noexcept { return false; }
        template <typename P>
        auto await_suspend(std::coroutine_handle<P> handle) noexcept { return handle.promise().m_continuation; }
        void await_resume() const noexcept {}
        // clang-format on
    };

    auto operator co_await() noexcept
    {
        return Awaiter{ m_handle };
    }
#    endif

    // error: X has a field Y whose type depends on the type Z which has no linkage
    // GCC bug fixed with https://gcc.gnu.org/bugzilla/show_bug.cgi?id=70413#c9
#    if !CARB_TOOLCHAIN_CLANG
    CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wsubobject-linkage")
#    endif

    //! Awaits *this and then invokes the given invocable object with the result.
    //!
    //! Since every function that uses `co_await` is itself a coroutine, calling this function is a simple coroutine
    //! function that does the `co_await` and therefore can be called from non-coroutine functions, and functions that
    //! cannot be coroutines, like `main()`.
    //! @note This function is only available if `Result` is not `void`.
    //! @param func The invocable object that is called as `void(Result)`. Any return value is ignored.
    //! @returns A \ref Ignore coroutine object that can be ignored.
    template <class Func>
    CARB_NO_DOC(requires(!std::is_same_v<Result, void>))
    Ignore await_and_then_call(Func&& func)
    {
        func(co_await *this);
        co_return;
    }

    //! Awaits this.
    //!
    //! Since every function that uses `co_await` is itself a coroutine, calling this function is a simple coroutine
    //! function that does the `co_await` and therefore can be called from non-coroutine functions, and functions that
    //! cannot be coroutines, like `main()`.
    //! @note This function is only available if `Result` is `void`.
    //! @returns A \ref Basic coroutine object that can be ignored.
    template <class T = Result>
    CARB_NO_DOC(requires(std::is_same_v<T, void>))
    Ignore await()
    {
        co_await *this;
        co_return;
    }

    CARB_IGNOREWARNING_GNUC_POP

private:
    explicit Task(std::coroutine_handle<promise_type> handle) : m_handle(handle)
    {
    }

    std::coroutine_handle<promise_type> m_handle;
};

#    ifndef DOXYGEN_BUILD
template <class Result>
struct Task<Result>::promise_type
{
    std::coroutine_handle<> m_continuation;
    std::exception_ptr m_exc;
    Result m_result;

    // clang-format off
    Task get_return_object() { return Task{ std::coroutine_handle<promise_type>::from_promise(*this) }; }
    void unhandled_exception() noexcept { m_exc = std::current_exception(); }
    void return_value(Result r) noexcept { m_result = std::move(r); }
    std::suspend_always initial_suspend() noexcept { return {}; }
    ResumeCaller final_suspend() noexcept { return {}; }
    // clang-format on
};

template <>
struct Task<void>::promise_type
{
    std::coroutine_handle<> m_continuation;
    std::exception_ptr m_exc;

    // clang-format off
    Task<> get_return_object() { return Task<>{ std::coroutine_handle<promise_type>::from_promise(*this) }; }
    void unhandled_exception() noexcept { m_exc = std::current_exception(); }
    void return_void() noexcept {}
    std::suspend_always initial_suspend() noexcept { return {}; }
    Task<>::ResumeCaller final_suspend() noexcept { return {}; }
    // clang-format on
};
#    endif

} // namespace coro
} // namespace carb

#endif
