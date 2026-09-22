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
//! @brief Interface definition for IMessageQueue
#pragma once

#include "MessageQueueTypes.h"
#include "../../omni/Expected.h"
#include "../IObject.h"

#include <type_traits>

//! The latest version available of the carb::eventdispatcher::IMessageQueueFactory interface.
#define carb_eventdispatcher_IMessageQueueFactory_latest CARB_HEXVERSION(1, 1)
#ifndef carb_eventdispatcher_IMessageQueueFactory
//! The version to request of the carb::eventdispatcher::IMessageQueueFactory interface.
#    define carb_eventdispatcher_IMessageQueueFactory CARB_HEXVERSION(1, 0)
#endif

namespace carb
{

namespace eventdispatcher
{

/**
 * An instance of a message queue.
 *
 * A message queue is a one-way weak coupling device that allows "messages" to be sent from a variety of senders and
 * received by a specific target. A message queue has a push-side and a pop-side. The push-side can be accessed by any
 * thread. The pop-side can only be accessed by the owning thread, or a group of threads if no owning thread is
 * specified. Violations of this policy are enforced by \ref omni::unexpected return values containing an error code.
 *
 * Can be created with \ref IMessageQueueFactory::createMessageQueue(), or an existing message queue can be found with
 * \ref IMessageQueueFactory::getMessageQueue().
 */
class IMessageQueue : public carb::IObject
{
public:
    //! The \ref omni::expected type returned by \ref IMessageQueue functions.
    using ExpectedType = omni::expected<void, omni::core::Result>;

    //! The \ref omni::unexpected type representing an error by \ref IMessageQueue functions.
    using UnexpectedType = omni::unexpected<omni::core::Result>;

    //! Retrieves the unique name of this message queue.
    //!
    //! @thread_safety May be called by any thread at any time without requiring synchronization.
    //! @returns The unique name of this message queue.
    virtual RStringKey getName() const = 0;

    //! Retrieves the thread ID of the thread which owns this message queue.
    //!
    //! @thread_safety May be called by any thread at any time without requiring synchronization.
    //! @returns The thread ID of the thread which owns this message queue, or zero if no one thread owns this message
    //!     queue.
    virtual thread::ThreadId getOwningThread() const = 0;

    //! @defgroup popside Pop-side functions
    //!
    //! Unless otherwise specified, may be called by owning thread only if the message queue is configured with a
    //! single owning thread.
    //! @{

    //! Returns whether this message queue has pending messages.
    //!
    //! @thread_safety Though this is a pop-side function, it can be called by any thread. However, the value may be
    //!     stale by the time it is read *unless* called by the owning thread in a single-owner-thread situation.
    //! @returns `true` if the message queue appears to have messages, `false` otherwise.
    virtual bool hasMessages() const = 0;

    //! @private
    virtual void internalPeek(ExpectedType& result, MessageFn fn, void* userData) const = 0;

    //! @private
    virtual void internalPop(ExpectedType& result, MessageFn fn, void* userData) = 0;

    //! @private
    virtual void internalAwaitMessage(ExpectedType& result, uint64_t nsToWait, NotifyFn notify, void* userData) const = 0;

    //! @private
    virtual void internalStop(ExpectedType& result) = 0;

    /**
     * Inspects the message at the front of the queue, if any, without removing it.
     *
     * The message is not removed when this function is called. Call \ref pop() to process and remove the message.
     * @warning This function only works in a single-owner-thread situation. Otherwise the function will always return
     *  \ref omni::unexpected with @ref omni::core::kResultNotSupported.
     * @par Errors
     * Accessible via the @ref omni::unexpected return value.
     * * @ref omni::core::kResultNotSupported - Calling this function is not supported in multi-owner-thread mode.
     * * @ref omni::core::kResultAccessDenied - Called by a thread that is not the owner thread.
     * * @ref omni::core::kResultNoMoreItems - The queue was empty.
     * * @ref omni::core::kResultOperationAborted - The queue has been stopped.
     * @param func An invocable that is called as `void(const Event&)`.
     * @returns a \ref omni::expected with `void` if \p func was called with the first item in the queue, otherwise a
     *  \ref omni::unexpected with an above-listed error.
     */
    template <class Func>
    ExpectedType peek(Func&& func) const;

    /**
     * Pops the message at the front of the queue and calls a function with the message.
     *
     * The message is removed from the queue atomically before processing. In a single-owner-thread situation, this
     * function must be called within the context of the owning thread.
     * @par Errors
     * Accessible via the @ref omni::unexpected return value.
     * * @ref omni::core::kResultAccessDenied - Called by a thread that is not the owner thread.
     * * @ref omni::core::kResultNoMoreItems - The queue was empty.
     * * @ref omni::core::kResultOperationAborted - The queue has been stopped.
     * @param func An invocable that is called as `void(const Event&)`.
     * @returns a \ref omni::expected with `void` if \p func was called with the popped first item in the queue,
     *  otherwise a \ref omni::unexpected with an above-listed error.
     */
    template <class Func>
    ExpectedType pop(Func&& func);

    /**
     * Blocks the current thread or task until a message is available in the queue.
     *
     * Note, if \ref carb::tasking::ITasking is available and started when this is called, this function will wait in a
     *  task-safe manner.
     * @thread_safety Though this is a pop-side function, it can be called by any thread.
     * @par Errors
     * Accessible via the @ref omni::unexpected return value.
     * * @ref omni::core::kResultOperationAborted - The queue has been stopped.
     * @returns a \ref omni::expected with `void` when a message becomes available, or a \ref omni::unexpected with an
     *  above-listed error.
     */
    omni::expected<void, omni::core::Result> awaitMessage() const;

    /**
     * Blocks the current thread or task until a message is available in the queue, or a timeout duration expires.
     *
     * Note, if \ref carb::tasking::ITasking is available and started when this is called, this function will wait in a
     *  task-safe manner.
     * @thread_safety Though this is a pop-side function, it can be called by any thread.
     * @par Errors
     * Accessible via the @ref omni::unexpected return value.
     * * @ref omni::core::kResultOperationAborted - The queue has been stopped.
     * * @ref omni::core::kResultTimedOut - The timeout period expired.
     * @param duration The time period to wait.
     * @returns a \ref omni::expected with `void` when a message becomes available, or a \ref omni::unexpected with an
     *  above-listed error.
     */
    template <class Rep, class Period>
    omni::expected<void, omni::core::Result> awaitMessageFor(const std::chrono::duration<Rep, Period>& duration) const;

    /**
     * Blocks the current thread or task until a message is available in the queue, or a timeout time arrives.
     *
     * Note, if \ref carb::tasking::ITasking is available and started when this is called, this function will wait in a
     *  task-safe manner.
     * @thread_safety Though this is a pop-side function, it can be called by any thread.
     * @par Errors
     * Accessible via the @ref omni::unexpected return value.
     * * @ref omni::core::kResultOperationAborted - The queue has been stopped.
     * * @ref omni::core::kResultTimedOut - The timeout period expired.
     * @param when The clock time to timeout at.
     * @returns a \ref omni::expected with `void` when a message becomes available, or a \ref omni::unexpected with an
     *  above-listed error.
     */
    template <class Clock, class Duration>
    omni::expected<void, omni::core::Result> awaitMessageUntil(const std::chrono::time_point<Clock, Duration>& when) const;

    /**
     * Stops the message queue before destruction.
     *
     * This is a one-time, irreversible command to a message queue that the queue is no longer processing messages. It
     * is not required to call this function before the last reference is removed and `*this` is destroyed.
     *
     * When `stop()` returns it is guaranteed that:
     * * Any future attempts to push messages or pop messages will result in a \ref omni::core::kResultOperationAborted
     *   error returned as a \ref omni::unexpected.
     * * All threads or tasks that are awaiting a message or waiting for a message to be processed have been unblocked.
     *   The existing function calls and future function calls will return \ref omni::core::kResultOperationAborted
     *   through a \ref omni::unexpected.
     * * The message queue is removed from \ref IMessageQueueFactory; attempts to retrieve the message queue by name
     *   will return an empty \ref IMessageQueuePtr and a new message queue with the same name can be created again.
     *
     * Subsequent calls to this function have no effect.
     * @warning It is undefined behavior to call this from within the invocable objects passed to \ref pop() or
     *  \ref peek(). Instead, it is recommended that the handlers for \ref pop() or \ref peek() set a flag that can be
     *  checked after the \ref pop() or \ref peek() returns which then calls \c stop().
     * @par Errors
     * Accessible via the @ref omni::unexpected return value.
     * * @ref omni::core::kResultAccessDenied - Called by a thread that is not the owner thread.
     * * @ref omni::core::kResultOperationAborted - stop() has already been issued.
     * @returns a \ref omni::expected with `void` if the stop was successful, or a \ref omni::unexpected with an
     *  above-listed error.
     */
    ExpectedType stop();

    //! @}

    //! @defgroup pushside Push-side functions that can be called by any thread
    //! @{

    //! @private
    virtual void internalPush(ExpectedType& result, const EventData& data, bool wait, NotifyFn notify, void* userData) = 0;

    /**
     * Sends a message to the message queue recipient, without waiting.
     *
     * This function can handle a series of immediate key/value pairs. In order to provide a variable number of
     *  key/value pairs, use \ref pushAsyncIter().
     * @thread_safety Safe to call concurrently. Messages pushed by a given thread will always be received in the same
     *  order as pushed (first-in-first-out). Messages pushed simultaneously in parallel by different threads are
     *  serialized in the queue and may be interlaced.
     * @par Errors
     * Accessible via the \ref omni::unexpected return value.
     * * @ref omni::core::kResultOperationAborted - stop() has already been issued.
     * * @ref omni::core::kResultOutOfMemory - memory could not be allocated for the message.
     * @param eventName The name of the event for the message.
     * @param payload Zero or more key/value pairs that are used as the payload for the message and may be queried by
     *  the message queue owner(s) when the message is popped from the queue. Each argument must be of type
     *  `std::pair<RStringKey, T>` where the first parameter is the key and the second is the value. The value must
     *  be a type understood by a \ref variant::Translator specialization. Each key must be unique, otherwise it is not
     *  defined which non-unique value is obtained when the key is queried.
     * @returns a \ref omni::expected with `void` if the stop was successful, or a \ref omni::unexpected with an
     *  above-listed error.
     * @code{.cpp}
     *  mq->pushAsync(RString("My event"), std::make_pair(RStringKey("param1"), 7));
     * @endcode
     */
    template <class... Args>
    ExpectedType pushAsync(RString eventName, Args&&... payload);

    /**
     * Sends a message to the message queue recipient, without waiting.
     *
     * @thread_safety Safe to call concurrently. Messages by all threads are serialized in the queue and received by the
     *  owner(s) in order pushed.
     * @par Errors
     * Accessible via the \ref omni::unexpected return value.
     * * @ref omni::core::kResultOperationAborted - stop() has already been issued.
     * * @ref omni::core::kResultOutOfMemory - memory could not be allocated for the message.
     * @tparam InIter An InputIterator that is forward-iterable and resolves to a \ref NamedVariant when dereferenced.
     *  The entries are used as the message payload and may be queried by observers. Each key must be unique, otherwise
     *  it is not defined which non-unique value is obtained when the key is queried.
     * @param eventName The name of the event for the message.
     * @param begin An InputIterator that, with \p end, forms the range `[begin, end)` of the message key/value pairs.
     * @param end An InputIterator that, with \p begin, forms the range `[begin, end)` of the message key/value pairs.
     * @returns a \ref omni::expected with `void` if the stop was successful, or a \ref omni::unexpected with an
     *  above-listed error.
     * @code{.cpp}
     *  std::vector fields{ NamedVariant{ RStringKey("param1"), Variant(7) } };
     *  mq->pushAsyncIter(RString("My event"), fields.begin(), fields.end());
     * @endcode
     */
    template <class InIter>
    ExpectedType pushAsyncIter(RString eventName, InIter begin, InIter end);

    /**
     * Sends a message to the message queue recipient, without waiting.
     *
     * @thread_safety Safe to call concurrently. Messages by all threads are serialized in the queue and received by the
     *  owner(s) in order pushed.
     * @par Errors
     * Accessible via the \ref omni::unexpected return value.
     * * @ref omni::core::kResultOperationAborted - stop() has already been issued.
     * * @ref omni::core::kResultOutOfMemory - memory could not be allocated for the message.
     * @tparam R A range type. Since this implementation is for pre-C++20 and C++20 ranges are not available, this is an
     *  approximation: this type must work with `std::begin()` and `std::end()` to produce an iterator type that
     *  conforms to *InputIterator*. The iterator must resolve to a `std::pair<RStringKey, T>` when dereferenced, where
     *  the first parameter is the key and the second parameter is the value and must be a type understood by a
     *  \ref variant::Translator specialization. Each key must be unique, otherwise it is not defined which non-unique
     *  value is obtained when the key is queried.
     * @param eventName The name of the event for the message.
     * @param range The range to use as message parameters. See explanation of the `R` type above.
     * @returns a \ref omni::expected with `void` if the stop was successful, or a \ref omni::unexpected with an
     *  above-listed error.
     * @code{.cpp}
     *  mq->pushAsyncRange(RString("My event"), { { RStringKey("param1"), 7 } });
     * @endcode
     */
    template <class R CARB_NO_DOC(
        ,
        std::enable_if_t<std::is_same<void, std::void_t<decltype(std::begin(std::declval<R>()), std::end(std::declval<R>()))>>::value,
                         bool> = false)>
    ExpectedType pushAsyncRange(RString eventName, R&& range)
    {
        // Implementation needs to be inline because certain compilers get very confused about the SFINAE
        std::vector<NamedVariant> variants;
        for (auto& r : range)
            variants.emplace_back(detail::translate(r));
        std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
        CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                    "Message has duplicate keys");
        EventData data{ eventName, variants.size(), variants.data() };
        ExpectedType result;
        internalPush(result, data, false, nullptr, nullptr);
        return result;
    }
#ifndef DOXYGEN_BUILD
    // Enable implicit initializer_list since {} cannot be deduced to a type
    template <class T>
    ExpectedType pushAsyncRange(RString eventName, std::initializer_list<std::pair<RStringKey, T>> range)
    {
        return pushAsyncRange<std::initializer_list<std::pair<RStringKey, T>>>(eventName, std::move(range));
    }
#endif

    /**
     * Sends a message to the message queue recipient and blocks the current thread or task until it has been popped and
     * processed.
     *
     * This function can handle a series of immediate key/value pairs. In order to provide a variable number of
     * key/value pairs, use \ref pushAndWaitIter(). If \ref carb::tasking::ITasking is available and started when this
     * is called, this function will wait in a task-safe manner.
     * @warning If this is called by the owning thread, the message will be pushed asynchronously, but the function will
     *  return \ref omni::unexpected with \ref omni::core::kResultWouldBlock.
     * @thread_safety Safe to call concurrently. Messages by all threads are serialized in the queue and received by the
     *  owner(s) in order pushed.
     * @par Errors
     * Accessible via the \ref omni::unexpected return value.
     * * @ref omni::core::kResultOutOfMemory - memory could not be allocated for the message.
     * * @ref omni::core::kResultOperationAborted - The queue has been stopped (the message was not processed).
     * * @ref omni::core::kResultWouldBlock - This function was called by the owner thread which would have resulted in
     *   a hang (\c true is returned).
     * @param eventName The name of the event for the message.
     * @param payload Zero or more key/value pairs that are used as the payload for the message and may be queried by
     *  the message queue owner(s) when the message is popped from the queue. Each argument must be of type
     *  `std::pair<RStringKey, T>` where the first parameter is the key and the second is the value. The value must
     *  be a type understood by a \ref variant::Translator specialization. Each key must be unique, otherwise it is not
     *  defined which non-unique value is obtained when the key is queried.
     * @returns a \ref omni::expected with `void` when the message has been processed, or a \ref omni::unexpected with
     *  an above-listed error.
     * @code{.cpp}
     *  mq->pushAndWait(RString("My event"), std::make_pair(RStringKey("param1"), 7));
     * @endcode
     */
    template <class... Args>
    ExpectedType pushAndWait(RString eventName, Args&&... payload);

    /**
     * Sends a message to the message queue recipient and blocks the current thread or task until it has been popped and
     * processed.
     *
     * If \ref carb::tasking::ITasking is available and started when this is called, this function will wait in a
     * task-safe manner.
     * @warning If this is called by the owning thread, the message will be pushed asynchronously, but the function will
     *  return \ref omni::unexpected with \ref omni::core::kResultWouldBlock.
     * @thread_safety Safe to call concurrently. Messages by all threads are serialized in the queue and received by the
     *  owner(s) in order pushed.
     * @par Errors
     * Accessible via the \ref omni::unexpected return value.
     * * @ref omni::core::kResultOutOfMemory - memory could not be allocated for the message.
     * * @ref omni::core::kResultOperationAborted - The queue has been stopped (the message was not processed).
     * * @ref omni::core::kResultWouldBlock - This function was called by the owner thread which would have resulted in
     *   a hang (\c true is returned).
     * @tparam R A range type. Since this implementation is for pre-C++20 and C++20 ranges are not available, this is an
     *  approximation: this type must work with `std::begin()` and `std::end()` to produce an iterator type that
     *  conforms to *InputIterator*. The iterator must resolve to a `std::pair<RStringKey, T>` when dereferenced, where
     *  the first parameter is the key and the second parameter is the value and must be a type understood by a
     *  \ref variant::Translator specialization. Each key must be unique, otherwise it is not defined which non-unique
     *  value is obtained when the key is queried.
     * @param eventName The name of the event for the message.
     * @param range The range to use as message parameters. See explanation of the `R` type above.
     * @returns a \ref omni::expected with `void` when the message has been processed, or a \ref omni::unexpected with
     *  an above-listed error.
     * @code{.cpp}
     *  mq->pushAndWaitRange(RString("My event"), { std::make_pair(RStringKey("param1"), 7) });
     * @endcode
     */
    template <class R CARB_NO_DOC(
        ,
        std::enable_if_t<std::is_same<void, std::void_t<decltype(std::begin(std::declval<R>()), std::end(std::declval<R>()))>>::value,
                         bool> = false)>
    ExpectedType pushAndWaitRange(RString eventName, R&& range)
    {
        // Implementation needs to be inline because certain compilers get very confused about the SFINAE
        std::vector<NamedVariant> variants;
        for (auto& r : range)
            variants.emplace_back(detail::translate(r));
        std::sort(variants.begin(), variants.end(), detail::NamedVariantLess{});
        CARB_ASSERT(std::adjacent_find(variants.begin(), variants.end(), detail::NamedVariantEqual{}) == variants.end(),
                    "Message has duplicate keys");
        EventData data{ eventName, variants.size(), variants.data() };
        ExpectedType result;
        internalPush(result, data, true, nullptr, nullptr);
        return result;
    }
#ifndef DOXYGEN_BUILD
    // Enable implicit initializer_list since {} cannot be deduced to a type
    template <class T>
    ExpectedType pushAndWaitRange(RString eventName, std::initializer_list<std::pair<RStringKey, T>> range)
    {
        return pushAndWaitRange<std::initializer_list<std::pair<RStringKey, T>>>(eventName, std::move(range));
    }
#endif

    /**
     * Sends a message to the message queue recipient and blocks the current thread or task until it has been popped and
     * processed.
     *
     * If \ref carb::tasking::ITasking is available and started when this is called, this function will wait in a
     * task-safe manner.
     * @warning If this is called by the owning thread, the message will be pushed asynchronously, but the function will
     *  return \ref omni::unexpected with \ref omni::core::kResultWouldBlock.
     * @thread_safety Safe to call concurrently. Messages by all threads are serialized in the queue and received by the
     *  owner(s) in order pushed.
     * @par Errors
     * Accessible via the \ref omni::unexpected return value.
     * * @ref omni::core::kResultOutOfMemory - memory could not be allocated for the message.
     * * @ref omni::core::kResultOperationAborted - The queue has been stopped (the message was not processed).
     * * @ref omni::core::kResultWouldBlock - This function was called by the owner thread which would have resulted in
     *   a hang (\c true is returned).
     * @tparam InIter An InputIterator that is forward-iterable and resolves to a \ref NamedVariant when dereferenced.
     *  The entries are used as the message payload and may be queried by observers. Each key must be unique, otherwise
     *  it is not defined which non-unique value is obtained when the key is queried.
     * @param eventName The name of the event for the message.
     * @param begin An InputIterator that, with \p end, forms the range `[begin, end)` of the message key/value pairs.
     * @param end An InputIterator that, with \p begin, forms the range `[begin, end)` of the message key/value pairs.
     * @returns a \ref omni::expected with `void` when the message has been processed, or a \ref omni::unexpected with
     *  an above-listed error.
     * @code{.cpp}
     *  std::vector fields{ NamedVariant{ RStringKey("param1"), Variant(7) } };
     *  mq->pushAndWaitIter(RString("My event"), fields.begin(), fields.end());
     * @endcode
     */
    template <class InIter>
    ExpectedType pushAndWaitIter(RString eventName, InIter begin, InIter end);

    //! @}
};

//! A type defined as `carb::ObjectPtr<IMessageQueue>`.
using IMessageQueuePtr = carb::ObjectPtr<IMessageQueue>;

/**
 * The interface that functions as a message queue factory.
 */
struct IMessageQueueFactory
{
    CARB_PLUGIN_INTERFACE_EX("carb::eventdispatcher::IMessageQueueFactory",
                             carb_eventdispatcher_IMessageQueueFactory_latest,
                             carb_eventdispatcher_IMessageQueueFactory);

    //! @private
    IMessageQueue*(CARB_ABI* internalCreateMessageQueue)(RStringKey name,
                                                         const MessageQueueParams& params,
                                                         omni::core::Result& result,
                                                         bool& existing);
    //! @private
    IMessageQueue*(CARB_ABI* internalGetMessageQueue)(RStringKey name);

#if CARB_VERSION_ATLEAST(carb_eventdispatcher_IMessageQueueFactory, 1, 1)
    /**
     * Adds an alias that can be used to refer to a different message queue.
     *
     * After a successful call, @ref getMessageQueue called with @p alias will return the @ref IMessageQueue instance
     * created with name @p target. A message queue may have multiple aliases. The target message queue does not have to
     * be created yet.
     * @thread_safety Safe to call while any thread is performing any operation against @ref IMessageQueueFactory.
     * @param target The target message queue name.
     * @param alias The alias name.
     * @retval true A new alias was created.
     * @retval false @p target and @p alias are the same, either @p target or @p alias are empty, @p target is already
     *   an alias, or @p alias is already used.
     */
    bool(CARB_ABI* addAlias)(RStringKey target, RStringKey alias);

    /**
     * Removes a previously-added message queue alias.
     *
     * Removes an alias that was previously added with @ref addAlias. Once removed, the @p alias is free to be used
     * again as an alias for a different message queue or to create a new message queue.
     * @thread_safety Safe to call while any thread is performing any operation against @ref IMessageQueueFactory.
     * @param target The target message queue name.
     * @param alias The alias name previously added with @ref addAlias.
     * @retval true The alias was removed successfully.
     * @retval false @p target and @p alias are the same, either @p target or @p alias are empty, @p target is not an
     *   alias target, or @p alias is not an alias of @p target.
     */
    bool(CARB_ABI* removeAlias)(RStringKey target, RStringKey alias);
#endif

    // ^^^^ Interface functions
    // vvvv Helper functions

    /**
     * Creates a message queue with the given name and parameters, or returns an existing message queue with the given
     * name.
     *
     * @thread_safety Safe to call while any thread is performing any operation against @ref IMessageQueueFactory.
     * @par Errors
     * Accessible via the \ref omni::unexpected return value.
     * * @ref omni::core::kResultOutOfMemory - A new message queue could not be created.
     * * @ref omni::core::kResultInvalidArgument - The sizeOf field of \p params is invalid, or \p name is empty.
     * @param name The unique name of the message queue. If the name already exists, the message queue will not be
     *  created but the previously-created message queue will be returned (\p params will be ignored). Since names must
     *  be unique, a scheme such as reverse-DNS is recommended. Empty names are not allowed.
     * @param params The parameters to use when creating the message queue. These are ignored if a message queue already
     *  exists with \p name.
     * @retval std::pair<IMessageQueuePtr,bool> A successful return produces a `std::pair` with `first` being a
     *  non-empty \ref IMessageQueuePtr object, and `second` as a `bool` that is `true` if the message queue was newly
     *  created based on \p params, or `false` if the message queue previously existed.
     * @retval omni::core::Result An error return produces a \ref omni::unexpected containing an error code
     *  corresponding to the above list.
     */
    omni::expected<std::pair<IMessageQueuePtr, bool>, omni::core::Result> createMessageQueue(
        RStringKey name, const MessageQueueParams& params);

    /**
     * Retrieves a message queue with the given name.
     *
     * If there is no message queue with the given name, an empty \ref IMessageQueuePtr is returned.
     * @thread_safety Safe to call while any thread is performing any operation against @ref IMessageQueueFactory.
     * @param name The unique name of the message queue, previously passed to \ref createMessageQueue(). Empty names are
     *   not allowed.
     * @returns A \ref IMessageQueuePtr containing the located message queue, or an empty object if no queue exists with
     *      the given name.
     */
    IMessageQueuePtr getMessageQueue(RStringKey name);
};

} // namespace eventdispatcher
} // namespace carb

#ifndef __INTELLISENSE__
#    include "IMessageQueue.inl"
#endif
