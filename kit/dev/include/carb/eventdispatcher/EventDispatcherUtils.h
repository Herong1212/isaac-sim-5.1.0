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
//! @brief Utilities for *carb.eventdispatcher.plugin*
#pragma once

#include "IEventDispatcher.h"
#include "IMessageQueue.h"

namespace carb
{
namespace eventdispatcher
{

/**
 * Pops all entries from a message queue and dispatches them.
 *
 * Effectively:
 * ```cpp
 * auto ed = carb::getCachedInterface<IEventDispatcher>();
 * IMessageQueue::ExpectedType exp;
 * while ((exp = p->pop([&](const Event& e) { ed->internalDispatch(e); })).has_value())
 *     ;
 * return exp;
 * ```
 * @param p The \ref IMessageQueue to pop in a loop.
 * @returns An expected value that is the first unexpected result from \ref IMessageQueue::pop.
 */
inline IMessageQueue::ExpectedType popAllAndDispatch(IMessageQueue* p) noexcept
{
    auto ed = carb::getCachedInterface<IEventDispatcher>();
    IMessageQueue::ExpectedType exp;
    while ((exp = p->pop([&](const Event& e) { ed->internalDispatch(e); })).has_value())
        ;
    return exp;
}

} // namespace eventdispatcher
} // namespace carb
