// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief carb.events interface definition file.
#pragma once

#include "EventsTypes.h"

#include "../Interface.h"
#include "../InterfaceUtils.h"
#include "../RString.h"
#include "../dictionary/IDictionary.h"

#include "../../omni/Vector.h"

#include <utility>

//! The version number of the latest @ref carb::events::IEvents interface.
#define carb_events_IEvents_latest CARB_HEXVERSION(1, 4)
#ifndef carb_events_IEvents
//! The default version number of the @ref carb::events::IEvents interface to use for this
//! build.  This macro may be overridden in the project settings to instead use the latest
//! version of the interface.
#    define carb_events_IEvents CARB_HEXVERSION(1, 3)
#endif

namespace carb
{

/**
 * Namespace for the *carb.events* plugin.
 */
namespace events
{

/**
 * Event object which is sent and received. Lifetime is managed by carb::IObject refcounting.
 */
class IEvent : public IObject
{
public:
    EventType type; //!< Event type.
    SenderId sender; //!< The sender of the event, or carb::events::kGlobalSenderId.
    dictionary::Item* payload; //!< Event payload is dictionary Item. Any data can be put into.

    /**
     * Helper function to build a *carb.dictionary* of values.
     * @param param The key/value pair to include in the *carb.dictionary*.
     */
    template <typename ValueT>
    void setValues(const std::pair<const char*, ValueT>& param);

    /**
     * Helper function to build a *carb.dictionary* of values.
     * @param param The key/value pair to include in the *carb.dictionary*.
     * @param params Additional key/value pairs.
     */
    template <typename ValueT, typename... ValuesT>
    void setValues(const std::pair<const char*, ValueT>& param, ValuesT&&... params);

    /**
     * Stops propagation of an event during dispatch.
     */
    virtual void consume() = 0;

    /**
     * Attaches a \ref carb::IObject to this event by name and holds a reference to the object.
     *
     * The object can be retrieved with \ref retrieveObject(). If an object is already stored under the given name, the
     * stored object is released and \p ptr is stored instead. References to stored objects are released when `*this` is
     * destroyed. To clear the current reference for a given \p name, pass \p ptr as `nullptr`.
     * @thread_safety This function is thread safe: all `attachObject()` calls are serialized with each other and all
     *   calls with \ref retrieveObject().
     * @param name The name of the object to attach. Must not be `nullptr`. The same name must be passed to
     * \ref retrieveObject() in order to retrieve the pointer. This parameter is case-sensitive.
     * @param ptr The pointer to attach to \c *this with the given \p name.
     */
    virtual void attachObject(const char* name, carb::IObject* ptr) = 0;

    /**
     * Retrieves a previously-stored \ref carb::IObject from this event by name.
     *
     * The object was previously set with \ref attachObject(). The object remains attached to `*this` until `*this` is
     * destroyed or it is overwritten with a different object (or `nullptr`) by calling \ref attachObject() again.
     * @thread_safety This function is thread safe: `retrieveObject()` can be called concurrently and will serialize
     *   calls to \ref attachObject().
     * @param name The name of the object to retrieve. Must not be `nullptr`. This parameter is case-sensitive.
     * @returns The object previously passed to \ref attachObject(). May be nullptr
     */
    carb::ObjectPtr<carb::IObject> retrieveObject(const char* name)
    {
        // cannot pass ObjectPtr by value across ABI boundaries
        carb::ObjectPtr<carb::IObject> ptr{};
        internalRetrieveObject(name, ptr);
        return ptr;
    }

    //! @private
    virtual void internalRetrieveObject(const char* name, carb::ObjectPtr<carb::IObject>& out) = 0;

#if CARB_VERSION_ATLEAST(carb_events_IEvents, 1, 4)
    /**
     * Retrieves the names of all objects attached to this event.
     * @thread_safety This function is thread-safe with respect to \ref attachObject() and \ref retrieveObject().
     *   However, the list may be modified by another thread after the output vector is filled.
     * @param out Receives the names of all objects attached to this event. The vector is not cleared; the names are
     *   appended to existing entries.
     */
    virtual void getObjectNames(omni::vector<RString>& out) const = 0;
#endif
};

/// Helper definition for IEvent smart pointer.
using IEventPtr = ObjectPtr<IEvent>;


/**
 * Subscription holder is created by all event listening subscription functions. Subscription is valid while the holder
 * is alive.
 */
class ISubscription : public IObject
{
public:
    /**
     * Unsubscribes the associated IEventListener.
     */
    virtual void unsubscribe() = 0;

    /**
     * Returns the name of the subscription.
     *
     * @note If a name was not given when the @ref IEventStream subscription function was called, a name is generated
     * based on the address of the @ref IEventListener::onEvent() function.
     *
     * @returns The name of the subscription.
     */
    virtual const char* getName() const noexcept = 0;

#if CARB_VERSION_ATLEAST(carb_events_IEvents, 1, 3)
    /**
     * Returns the order of the subscription.
     *
     * @returns The order of the subscription.
     */
    virtual Order getOrder() const noexcept = 0;

    /**
     * Sets the order of the subscription.
     *
     * @param order The order of the subscription.
     */
    virtual void setOrder(Order order) noexcept = 0;

    /**
     * Returns the enabled state of the subscription.
     *
     * @returns The enabled state of the subscription.
     */
    virtual bool isEnabled() const noexcept = 0;

    /**
     * Sets the enabled state of the subscription.
     *
     * @param enabled The enabled state of the subscription.
     */
    virtual void setEnabled(bool enabled) noexcept = 0;
#endif
};

/// Helper definition for ISubscription smart pointer.
using ISubscriptionPtr = ObjectPtr<ISubscription>;


/**
 * Event stream is fundamental primitive used to send, receive and listen for events. Different event system models can
 * be designed using it. It is thread-safe and can also be used as a sync primitive. Similar to Go Language Channels.
 *
 * Basically stream is just a queue with listeners:
 *
 * @code{.txt}
 *                                 +------------------+
 *       push() / pushBlocked()    |                  |   tryPop() / pop()
 *    +--------------------------->+   IEventStream   +------------------------>
 *                            ^    |                  |    ^
 *                            |    +------------------+    |
 *          subscribeToPush() |                            |  subscribeToPop()
 *                            |                            |
 *                            |                            |
 *                  +---------+--------+          +--------+---------+
 *                  |  IEventListener  |          |  IEventListener  |
 *                  +------------------+          +------------------+
 * @endcode
 *
 * 1. You can push to stream and pop events (acts like a queue).
 * 2. Given the stream you can listen for pushed and/or popped events. That is basically immediate callbacks vs deferred
 *      callbacks.
 * 3. Blocking methods (pushBlocked() and pop()) will block the thread until event is popped (for push method) or any
 *      event is pushed (for pop method). That can be used as thread sync.
 * 4. Pumping of stream is just popping all events until it is empty.
 * 5. EventType allows you to filter which events to listen for. IEventStream may contain only one type, conceptually
 *      more like channels, or a lot of events - like event bus.
 * 6. Listeners are subscribed specifying the order in which they want to receive events. When processing, they may
 *      consume an event which stops other listeners from receiving it (only when being dispatched).
 */
class IEventStream : public IObject
{
public:
    /**
     * Create new event of certain type.
     * @param eventType The type of event to create.
     * @param sender The sender of the event, or carb::events::kGlobalSenderId.
     * @returns A pointer to a newly created event.
     */
    virtual IEvent* createEventPtr(EventType eventType, SenderId sender) = 0;

    /**
     * @copydoc createEventPtr(EventType,SenderId)
     * @param values Key/value pairs as passed to IEvent::setValues().
     */
    template <typename... ValuesT>
    ObjectPtr<IEvent> createEvent(EventType eventType, SenderId sender, ValuesT&&... values);

    /**
     * Dispatch event immediately without putting it into stream.
     * @param e The event to dispatch.
     */
    virtual void dispatch(IEvent* e) = 0;

    /**
     * Push event into the stream.
     * @param e The event to push.
     */
    virtual void push(IEvent* e) = 0;

    /**
     * Push event into the stream and block until it is dispatched by some other thread.
     * @param e The event to push.
     */
    virtual void pushBlocked(IEvent* e) = 0;

    /**
     * Get approximate number of events waiting for dispatch in the stream.
     * @thread_safety While safe to call from multiple threads, since there is no lock involved this value should be
     *      considered approximate as another thread could modify the number before the return value is read. This call
     *      is strongly ordered with respect to other calls.
     * @returns The approximate number of events waiting for dispatch in the stream.
     */
    virtual size_t getCount() = 0;

    /**
     * Pop and dispatches a single event from the stream, blocking until one becomes available.
     * @warning This function blocks until an event is available.
     * @returns The event that was popped and dispatched.
     */
    ObjectPtr<IEvent> pop();

    /// @copydoc pop()
    virtual IEvent* popPtr() = 0;

    /**
     * Pops and dispatches a single event from the stream, if available.
     * @note Unlike pop(), this function does not wait for an event to become available.
     * @returns The event that was popped and dispatched, or `nullptr` if no event was available.
     */
    ObjectPtr<IEvent> tryPop();

    /// @copydoc tryPop()
    virtual IEvent* tryPopPtr() = 0;

    /**
     * Dispatches and pops all available events from the stream.
     */
    void pump();

    /**
     * Subscribe to receive notification when event stream is popped.
     * @sa pump() pop() tryPop()
     * @note Adding or removing a subscription from \ref IEventListener::onEvent() is perfectly valid. The newly added
     *   subscription will not be called until the next event.
     * @warning Recursively pushing and/or popping events from within \ref IEventListener::onEvent() is not recommended
     *   and can lead to undefined behavior.
     * @param listener The listener to subscribe. IEventListener::onEvent() will be called for each popped event. If an
     *   event listener calls IEvent::consume() on the given event, propagation of the event will stop and no more event
     *   listeners will receive the event.
     * @param order An optional value used to specify the order tier. Lower order tiers will be notified first.
     *   Multiple IEventListener objects at the same `order` are notified in the order in which they subscribed.
     * @param subscriptionName An optional name for the subscription for debugging purposes. Names do not need to be
     *   unique. If `nullptr`, an internal name will be determined.
     * @returns A ISubscription pointer. The subscription is valid as long as the ISubscription pointer is referenced.
     *   Alternately, the IEventListener can be unsubscribed by calling ISubscription::unsubscribe().
     */
    ObjectPtr<ISubscription> createSubscriptionToPop(IEventListener* listener,
                                                     Order order = kDefaultOrder,
                                                     const char* subscriptionName = nullptr);
    /// @copydoc createSubscriptionToPop()
    /// @param eventType A specific event to listen for.
    ObjectPtr<ISubscription> createSubscriptionToPopByType(EventType eventType,
                                                           IEventListener* listener,
                                                           Order order = kDefaultOrder,
                                                           const char* subscriptionName = nullptr);
    /// @copydoc createSubscriptionToPop()
    virtual ISubscription* createSubscriptionToPopPtr(IEventListener* listener,
                                                      Order order = kDefaultOrder,
                                                      const char* subscriptionName = nullptr) = 0;
    /// @copydoc createSubscriptionToPop()
    /// @param eventType A specific event to listen for.
    virtual ISubscription* createSubscriptionToPopByTypePtr(EventType eventType,
                                                            IEventListener* listener,
                                                            Order order = kDefaultOrder,
                                                            const char* subscriptionName = nullptr) = 0;

    /**
     * Subscribe to receive notification when an event is pushed into the event stream.
     * @sa push() pushBlocked()
     * @note Adding or removing a subscription from \ref IEventListener::onEvent() is perfectly valid. The newly added
     *   subscription will not be called until the next event.
     * @warning Recursively pushing and/or popping events from within \ref IEventListener::onEvent() is not recommended
     *   and can lead to undefined behavior.
     * @param listener The listener to subscribe. IEventListener::onEvent() will be called for each pushed event. The
     *   IEvent::consume() function has no effect for notifications of push events.
     * @param order An optional value used to specify the order tier. Lower order tiers will be notified first.
     *   Multiple IEventListener objects at the same `order` are notified in the order in which they subscribed.
     * @param subscriptionName An optional name for the subscription for debugging purposes. Names do not need to be
     *   unique. If `nullptr`, an internal name will be determined.
     * @returns A ISubscription pointer. The subscription is valid as long as the ISubscription pointer is referenced.
     *   Alternately, the IEventListener can be unsubscribed by calling ISubscription::unsubscribe().
     */
    ObjectPtr<ISubscription> createSubscriptionToPush(IEventListener* listener,
                                                      Order order = kDefaultOrder,
                                                      const char* subscriptionName = nullptr);
    /// @copydoc createSubscriptionToPush()
    /// @param eventType A specific event to listen for.
    ObjectPtr<ISubscription> createSubscriptionToPushByType(EventType eventType,
                                                            IEventListener* listener,
                                                            Order order = kDefaultOrder,
                                                            const char* subscriptionName = nullptr);
    /// @copydoc createSubscriptionToPush()
    virtual ISubscription* createSubscriptionToPushPtr(IEventListener* listener,
                                                       Order order = kDefaultOrder,
                                                       const char* subscriptionName = nullptr) = 0;
    /// @copydoc createSubscriptionToPush()
    /// @param eventType A specific event to listen for.
    virtual ISubscription* createSubscriptionToPushByTypePtr(EventType eventType,
                                                             IEventListener* listener,
                                                             Order order = kDefaultOrder,
                                                             const char* subscriptionName = nullptr) = 0;

    /**
     * Sets the notification order for named subscriptions.
     * @note If multiple subscriptions exist with the same name, all are updated.
     * @param subscriptionName the name previously assigned when the subscription was created.
     * @param order The new order tier. Lower order tiers will be notified first. Multiple IEventListener objects at the
     *   same `order` are notified in the order in which they originally subscribed.
     * @returns `true` if the subscription was found and updated; `false` otherwise.
     */
    virtual bool setSubscriptionToPopOrder(const char* subscriptionName, Order order) = 0;
    /// @copydoc setSubscriptionToPopOrder
    virtual bool setSubscriptionToPushOrder(const char* subscriptionName, Order order) = 0;

    /**
     * Retrieves the notification order for a named subscription.
     * @param subscriptionName the name previously assigned when the subscription was created.
     * @param order Must be a valid pointer that will receive the current order tier.
     * @returns `true` if the subscription was found; `false` if the subscription was not found or @p order is
     *   `nullptr`.
     */
    virtual bool getSubscriptionToPopOrder(const char* subscriptionName, Order* order) = 0;
    /// @copydoc setSubscriptionToPopOrder
    virtual bool getSubscriptionToPushOrder(const char* subscriptionName, Order* order) = 0;

    /**
     * Returns the name of the IEventStream.
     *
     * @note If a name was not given when @ref IEvents::createEventStream() was called, a name is generated based on the
     * function that called @ref IEvents::createEventStream().
     *
     * @returns The name of the IEventStream.
     */
    virtual const char* getName() const noexcept = 0;

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //                                                    Helpers                                                     //
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * @defgroup helpers Helper functions
     * @sa createEvent() push() pushBlocked() dispatch()
     * @{
     */

    /**
     * @copydoc createEvent
     */
    template <typename... ValuesT>
    IEvent* createEventPtr(EventType eventType, SenderId sender, ValuesT&&... values);

    /**
     * Helper function that combines createEvent() with push().
     * @param eventType The type of event to create.
     * @param sender The sender of the event, or carb::events::kGlobalSenderId.
     */
    void pushWithSender(EventType eventType, SenderId sender);

    /// @copydoc pushWithSender
    /// @param values Key/value pairs as passed to IEvent::setValues().
    template <typename... ValuesT>
    void pushWithSender(EventType eventType, SenderId sender, ValuesT&&... values);

    /**
     * Helper function that combines createEvent() with push().
     * @param eventType The type of event to create.
     * @param values Key/value pairs as passed to IEvent::setValues().
     */
    template <typename... ValuesT>
    void push(EventType eventType, ValuesT&&... values);

    /**
     * Helper function that combines createEvent() with pushBlocked().
     * @param eventType The type of event to create.
     * @param sender The sender of the event, or carb::events::kGlobalSenderId.
     */
    void pushBlockedWithSender(EventType eventType, SenderId sender);

    /// @copydoc pushBlockedWithSender
    /// @param values Key/value pairs as passed to IEvent::setValues().
    template <typename... ValuesT>
    void pushBlockedWithSender(EventType eventType, SenderId sender, ValuesT&&... values);

    /**
     * Helper function that combines createEvent() with pushBlocked().
     * @param eventType The type of event to create.
     * @param values Key/value pairs as passed to IEvent::setValues().
     */
    template <typename... ValuesT>
    void pushBlocked(EventType eventType, ValuesT&&... values);

    /**
     * Helper function that combines createEvent() with dispatch().
     * @param eventType The type of event to create.
     * @param sender The sender of the event, or carb::events::kGlobalSenderId.
     * @param values Key/value pairs as passed to IEvent::setValues().
     */
    template <typename... ValuesT>
    void dispatch(EventType eventType, SenderId sender, ValuesT&&... values);

    /**
     * Helper function that combines createEvent() with dispatch().
     * @param eventType The type of event to create.
     * @param sender The sender of the event, or carb::events::kGlobalSenderId.
     */
    void dispatch(EventType eventType, SenderId sender);
    ///@}

#if CARB_VERSION_ATLEAST(carb_events_IEvents, 1, 3)
    /**
     * Returns the number of subscriptions.
     * @returns the number of subscriptions
     */
    virtual size_t getSubscriptionToPopCount() const = 0;
    /// @copydoc getSubscriptionToPopCount
    virtual size_t getSubscriptionToPushCount() const = 0;

    /**
     * Calls a callback with all of the pop-side subscriptions. The order is unspecified.
     * @warning An internal lock is held while calling the callback. The callback must not call any other IEventStream
     *  functions or undefined behavior occurs.
     * @param callback The callback to call with each subscription.
     * @param userData An opaque pointer to pass to the callback.
     * @returns `true` if the callback was called for all subscriptions; `false` if the callback returned `false` to
     *   terminate iteration.
     */
    virtual bool walkSubscriptionsToPop(SubscriptionCallback callback, void* userData) const = 0;

    /**
     * Calls a callback with all of the push-side subscriptions. The order is unspecified.
     * @warning An internal lock is held while calling the callback. The callback must not call any other IEventStream
     *  functions or undefined behavior occurs.
     * @param callback The callback to call with each subscription.
     * @param userData An opaque pointer to pass to the callback.
     * @returns `true` if the callback was called for all subscriptions; `false` if the callback returned `false` to
     *   terminate iteration.
     */
    virtual bool walkSubscriptionsToPush(SubscriptionCallback callback, void* userData) const = 0;
#endif
};

/// Helper definition for IEventStream smart pointer.
using IEventStreamPtr = ObjectPtr<IEventStream>;

/**
 * Interface definition for *carb.events*.
 */
struct IEvents
{
    // 1.0 - Initial release
    // 1.1 - added internalCreateEventStream
    // 1.2 - added attachObject() and retrieveObject() to IEvent
    // 1.3 - API additions for more control over subscriptions
    // 1.4 - added getObjectNames() to IEvent
    CARB_PLUGIN_INTERFACE_EX("carb::events::IEvents", carb_events_IEvents_latest, carb_events_IEvents)

    /**
     * Create new event stream.
     * @param name An optional name to give the event stream for logging and profiling. Names do not need to be unique
     *   but are recommended to be unique. If `nullptr`, an internal name will be determined.
     * @returns A pointer to the new event stream.
     */
    IEventStreamPtr createEventStream(const char* name = nullptr) noexcept;

    /**
     * Create new event stream.
     * @rst
     * .. deprecated:: ``carb::events::IEvents::internalCreateEventStream`` instead.
     * @endrst
     * @returns A pointer to the new event stream.
     */
    CARB_DEPRECATED("Use internalCreateEventStream instead") virtual IEventStream* createEventStreamPtr() = 0;

    /**
     * Get a unique sender identifier.
     * @note The sender identifier may be a previously released sender identifier.
     * @returns A unique sender identifier. When finished with the sender identifier, it should be returned with
     *   releaseUniqueSenderId().
     */
    virtual SenderId acquireUniqueSenderId() = 0;

    /**
     * Releases a unique sender identifier previously acquired with acquireUniqueSenderId().
     * @param senderId The previously acquired senderId.
     */
    virtual void releaseUniqueSenderId(SenderId senderId) = 0;

    //! @private
    virtual IEventStream* internalCreateEventStream(const char* name) noexcept = 0;
};


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                                Inline Functions                                                    //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


////////////// IEvent //////////////

template <typename ValueT>
inline void IEvent::setValues(const std::pair<const char*, ValueT>& param)
{
    carb::getCachedInterface<dictionary::IDictionary>()->makeAtPath<ValueT>(this->payload, param.first, param.second);
}

template <typename ValueT, typename... ValuesT>
inline void IEvent::setValues(const std::pair<const char*, ValueT>& param, ValuesT&&... params)
{
    this->setValues<ValueT>(param);
    this->setValues(std::forward<ValuesT>(params)...);
}


////////////// IEventStream //////////////

template <typename... ValuesT>
inline IEvent* IEventStream::createEventPtr(EventType type, SenderId sender, ValuesT&&... values)
{
    IEvent* e = createEventPtr(type, sender);
    e->setValues(std::forward<ValuesT>(values)...);
    return e;
}

inline ObjectPtr<ISubscription> IEventStream::createSubscriptionToPop(IEventListener* listener,
                                                                      Order order,
                                                                      const char* name)
{
    return stealObject(this->createSubscriptionToPopPtr(listener, order, name));
}

inline ObjectPtr<ISubscription> IEventStream::createSubscriptionToPopByType(EventType eventType,
                                                                            IEventListener* listener,
                                                                            Order order,
                                                                            const char* name)
{
    return stealObject(this->createSubscriptionToPopByTypePtr(eventType, listener, order, name));
}

inline ObjectPtr<ISubscription> IEventStream::createSubscriptionToPush(IEventListener* listener,
                                                                       Order order,
                                                                       const char* name)
{
    return stealObject(this->createSubscriptionToPushPtr(listener, order, name));
}

inline ObjectPtr<ISubscription> IEventStream::createSubscriptionToPushByType(EventType eventType,
                                                                             IEventListener* listener,
                                                                             Order order,
                                                                             const char* name)
{
    return stealObject(this->createSubscriptionToPushByTypePtr(eventType, listener, order, name));
}

template <typename... ValuesT>
inline void IEventStream::pushWithSender(EventType type, SenderId sender, ValuesT&&... values)
{
    IEvent* e = createEventPtr(type, sender, std::forward<ValuesT>(values)...);
    push(e);
    e->release();
}

inline void IEventStream::pushWithSender(EventType type, SenderId sender)
{
    IEvent* e = createEventPtr(type, sender);
    push(e);
    e->release();
}

template <typename... ValuesT>
inline ObjectPtr<IEvent> IEventStream::createEvent(EventType eventType, SenderId sender, ValuesT&&... values)
{
    return carb::stealObject(this->createEventPtr(eventType, sender, std::forward<ValuesT>(values)...));
}

template <typename... ValuesT>
inline void IEventStream::push(EventType type, ValuesT&&... values)
{
    return pushWithSender(type, kGlobalSenderId, std::forward<ValuesT>(values)...);
}

template <typename... ValuesT>
inline void IEventStream::pushBlockedWithSender(EventType type, SenderId sender, ValuesT&&... values)
{
    IEvent* e = createEventPtr(type, sender, std::forward<ValuesT>(values)...);
    pushBlocked(e);
    e->release();
}

inline void IEventStream::pushBlockedWithSender(EventType type, SenderId sender)
{
    IEvent* e = createEventPtr(type, sender);
    pushBlocked(e);
    e->release();
}

template <typename... ValuesT>
inline void IEventStream::pushBlocked(EventType type, ValuesT&&... values)
{
    return pushBlockedWithSender(type, kGlobalSenderId, std::forward<ValuesT>(values)...);
}

template <typename... ValuesT>
inline void IEventStream::dispatch(EventType type, SenderId sender, ValuesT&&... values)
{
    IEvent* e = createEventPtr(type, sender, std::forward<ValuesT>(values)...);
    dispatch(e);
    e->release();
}

inline void IEventStream::dispatch(EventType type, SenderId sender)
{
    IEvent* e = createEventPtr(type, sender);
    dispatch(e);
    e->release();
}

inline void IEventStream::pump()
{
    const size_t eventCount = this->getCount();
    for (size_t i = 0; i < eventCount; i++)
    {
        IEvent* e = this->tryPopPtr();
        if (!e)
            break;
        e->release();
    }
}

inline ObjectPtr<IEvent> IEventStream::pop()
{
    return carb::stealObject(this->popPtr());
}

inline ObjectPtr<IEvent> IEventStream::tryPop()
{
    return carb::stealObject(this->tryPopPtr());
}

inline ObjectPtr<IEventStream> IEvents::createEventStream(const char* name) noexcept
{
    return carb::stealObject(this->internalCreateEventStream(name));
}

} // namespace events
} // namespace carb
