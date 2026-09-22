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
//! @brief Type definitions for IMessageQueue
#pragma once

#include "EventDispatcherTypes.h"

#include "../thread/Util.h"

namespace carb
{
namespace eventdispatcher
{

//! Parameters used in MessageQueue creation.
//! @see IMessageQueueFactory
struct MessageQueueParams
{
    //! Must be equal to `sizeof(MessageQueueParams)`. Used as a version for this struct.
    size_t sizeOf = sizeof(MessageQueueParams);

    //! The thread that owns the message queue. If zero, the message queue can be popped by multiple threads. If a
    //! specific thread owns the message queue then an error will occur if any other thread attempts to pop the message
    //! queue, and the message queue will be optimized for the owning thread. Message queues that are created from a
    //! task (\ref carb::tasking::ITasking) or thread pool should use zero here instead of using the calling thread.
    thread::ThreadId owningThread = 0;
};

//! @private
using MessageFn = void (*)(const Event& event, void* userdata);

//! @private
using NotifyFn = void (*)(bool stopped, void* userdata);

} // namespace eventdispatcher
} // namespace carb
