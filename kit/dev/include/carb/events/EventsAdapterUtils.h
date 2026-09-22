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
//! @brief carb.events adapter to carb.eventdispatcher
#pragma once

#include "IEvents.h"
#include "../eventdispatcher/IEventDispatcher.h"
#include "../../omni/String.h"

namespace carb
{
namespace events
{

#if CARB_VERSION_ATLEAST(carb_eventdispatcher_IEventDispatcher, 1, 3)
/**
 * Registers an alias between an IEvents `EventType` and IEventDispatcher event names.
 *
 * This is generally recommended for use with \ref AdapterType::eFullAlias. This allows event adapters created of type
 * \ref AdapterType::eFullAlias to map \p eventType with the corresponding \ref eventdispatcher::IEventDispatcher event
 * names for pushing (\p pushEvent) and popping (\p popEvent).
 *
 * Corresponding with the \ref IEventsAdapter created from type \ref AdapterType::eFullAlias, the following event names
 * will be aliased (where `<eventType>` is a base-10 rendering of \p eventType as if by the `PRIu64` printf format
 * specifier):
 * * `AdapterAlias:<eventType>:immediate` becomes an alias to \p pushEvent.
 * * `AdapterAlias:<eventType>` becomes an alias to \p popEvent.
 *
 * When the aliases are no longer needed, \ref unregisterEventAlias() can be used to remove them.
 * @see EventType eventdispatcher::IEventDispatcher::addEventAlias unregisterEventAlias
 * @param eventType The \ref EventType to use with aliasing. May not be 0.
 * @param pushEvent The \ref eventdispatcher::IEventDispatcher event name to use for push (immediate) events.
 * @param popEvent The \ref eventdispatcher::IEventDispatcher event name to use for pop (deferred) events.
 * @returns \c true if the aliases were created; \c false if either alias could not be created or \p eventType was 0.
 */
inline bool registerEventAlias(EventType eventType, RString pushEvent, RString popEvent)
{
    auto ed = carb::getCachedInterface<eventdispatcher::IEventDispatcher>();
    if (!ed || eventType == 0 || (pushEvent.isEmpty() && popEvent.isEmpty()))
        return false;
    omni::string scratch(omni::formatted, "AdapterAlias:%" PRIu64 ":immediate", eventType);
    bool r1 = pushEvent.isEmpty() ? true : ed->addEventAlias(pushEvent, RString(scratch.c_str(), scratch.length()));
    scratch.resize(scratch.size() - cpp::string_view(":immediate").length());
    bool r2 = popEvent.isEmpty() ? true : ed->addEventAlias(popEvent, RString(scratch.c_str(), scratch.length()));
    return r1 && r2;
}

/**
 * Unregisters an alias between an IEvents `EventType` and IEventDispatcher event names.
 *
 * This is the opposite behavior from \ref registerEventAlias when called with the same arguments.
 *
 * @see EventType eventdispatcher::IEventDispatcher::removeEventAlias registerEventAlias
 * @param eventType The \ref EventType used with aliasing. May not be 0.
 * @param pushEvent The \ref eventdispatcher::IEventDispatcher event name used for push (immediate) events.
 * @param popEvent The \ref eventdispatcher::IEventDispatcher event name used for pop (deferred) events.
 * @returns \c true if the aliases were removed; \c false if either alias could not be removed or \p eventType was 0.
 */
inline bool unregisterEventAlias(EventType eventType, RString pushEvent, RString popEvent)
{
    auto ed = carb::getCachedInterface<eventdispatcher::IEventDispatcher>();
    if (eventType == 0 || (pushEvent.isEmpty() && popEvent.isEmpty()))
        return false;
    omni::string scratch(omni::formatted, "AdapterAlias:%" PRIu64 ":immediate", eventType);
    bool r1 = pushEvent.isEmpty() ? true : ed->removeEventAlias(pushEvent, RString(scratch.c_str(), scratch.length()));
    scratch.resize(scratch.size() - cpp::string_view(":immediate").length());
    bool r2 = popEvent.isEmpty() ? true : ed->removeEventAlias(popEvent, RString(scratch.c_str(), scratch.length()));
    return r1 && r2;
}
#endif

} // namespace events
} // namespace carb
