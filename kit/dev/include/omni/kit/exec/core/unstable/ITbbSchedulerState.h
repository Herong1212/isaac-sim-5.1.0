// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file ITbbSchedulerState.h
//!
//! @brief Defines @ref omni::kit::exec::core::unstable::ITbbSchedulerState.
#pragma once

#include <omni/core/Omni.h>
#include <omni/graph/exec/unstable/IBase.h>

namespace omni
{
namespace kit
{
namespace exec
{
namespace core
{
namespace unstable
{

struct TbbSchedulerState;

// forward declarations needed by interface declaration
class ITbbSchedulerState;
class ITbbSchedulerState_abi;

//! Returns a global scheduler state based on TBB.
//!
//! This object is a singleton.  Access it with @ref omni::kit::exec::core::unstable::getTbbSchedulerState().
//!
//! Use of this object should be transparent to the user as it is an implementation detail of
//! @ref omni::kit::exec::core::unstable::ParallelSpawner.
//!
//! Temporary interface.  Will be replaced with something more generic.
class ITbbSchedulerState_abi
    : public omni::core::Inherits<graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.kit.exec.core.unstable.ITbbSchedulerState")>
{
protected:
    //! Returns the needed data to access the serial task queue.
    virtual TbbSchedulerState* getState_abi() noexcept = 0;

    //! Record that a task has been spawned
    virtual void recordTaskSpawned_abi() noexcept = 0;
    //! Record that a task has been enqueued
    virtual void recordTaskEnqueued_abi() noexcept = 0;
    //! Record that a task has been executed
    virtual void recordTaskExecuted_abi() noexcept = 0;
    //! Record that a parallel task has been pushed to queue
    virtual void recordPushedParallelTask_abi() noexcept = 0;
    //! Record that an isolate task has been pushed to queue
    virtual void recordPushedIsolateTask_abi() noexcept = 0;
    //! Record that a serial task has been pushed to queue
    virtual void recordPushedSerialTask_abi() noexcept = 0;

    //! Check if logging should occur and potentially log metrics
    virtual void checkAndLog_abi() noexcept = 0;
};

//! Returns the singleton @ref omni::kit::exec::core::unstable::ITbbSchedulerState.
//!
//! May return @c nullptr if the *omni.kit.exec.core* extension has not been loaded.
//!
//! The returned pointer does not have @ref omni::core::IObject::acquire() called on it.
inline ITbbSchedulerState* getTbbSchedulerState() noexcept;

} // namespace unstable
} // namespace core
} // namespace exec
} // namespace kit
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/kit/exec/core/unstable/ITbbSchedulerState.gen.h>

//! @copydoc omni::kit::exec::core::unstable::ITbbSchedulerState_abi
class omni::kit::exec::core::unstable::ITbbSchedulerState
    : public omni::core::Generated<omni::kit::exec::core::unstable::ITbbSchedulerState_abi>
{
};

inline omni::kit::exec::core::unstable::ITbbSchedulerState* omni::kit::exec::core::unstable::getTbbSchedulerState() noexcept
{
    // createType() always calls acquire() and returns an ObjectPtr to make sure release() is called. we don't want to
    // hold a ref here to avoid static destruction issues. here we allow the returned ObjectPtr to destruct (after
    // calling get()) to release our ref. we know the DLL in which the singleton was created is maintaining a ref and
    // will keep the singleton alive for the lifetime of the DLL.
    static auto sSingleton = omni::core::createType<ITbbSchedulerState>().get();
    return sSingleton;
}

//! Convenience macros for recording task metrics (only if logger is available)

#define OMNI_KIT_EXEC_RECORD_TASK_SPAWNED()                                                                            \
    do                                                                                                                 \
    {                                                                                                                  \
        auto* logger = omni::kit::exec::core::unstable::getTbbSchedulerState();                                        \
        if (CARB_UNLIKELY(logger != nullptr))                                                                          \
        {                                                                                                              \
            logger->recordTaskSpawned();                                                                               \
        }                                                                                                              \
    } while (0)

#define OMNI_KIT_EXEC_RECORD_TASK_ENQUEUED()                                                                           \
    do                                                                                                                 \
    {                                                                                                                  \
        auto* logger = omni::kit::exec::core::unstable::getTbbSchedulerState();                                        \
        if (CARB_UNLIKELY(logger != nullptr))                                                                          \
        {                                                                                                              \
            logger->recordTaskEnqueued();                                                                              \
        }                                                                                                              \
    } while (0)

#define OMNI_KIT_EXEC_RECORD_TASK_EXECUTED()                                                                           \
    do                                                                                                                 \
    {                                                                                                                  \
        auto* logger = omni::kit::exec::core::unstable::getTbbSchedulerState();                                        \
        if (CARB_UNLIKELY(logger != nullptr))                                                                          \
        {                                                                                                              \
            logger->recordTaskExecuted();                                                                              \
        }                                                                                                              \
    } while (0)

#define OMNI_KIT_EXEC_CHECK_AND_LOG_METRICS()                                                                          \
    do                                                                                                                 \
    {                                                                                                                  \
        auto* logger = omni::kit::exec::core::unstable::getTbbSchedulerState();                                        \
        if (CARB_UNLIKELY(logger != nullptr))                                                                          \
        {                                                                                                              \
            logger->checkAndLog();                                                                                     \
        }                                                                                                              \
    } while (0)

#define OMNI_KIT_EXEC_RECORD_PUSHED_PARALLEL_TASK()                                                                    \
    do                                                                                                                 \
    {                                                                                                                  \
        auto* logger = omni::kit::exec::core::unstable::getTbbSchedulerState();                                        \
        if (CARB_UNLIKELY(logger != nullptr))                                                                          \
        {                                                                                                              \
            logger->recordPushedParallelTask();                                                                        \
        }                                                                                                              \
    } while (0)

#define OMNI_KIT_EXEC_RECORD_PUSHED_ISOLATE_TASK()                                                                     \
    do                                                                                                                 \
    {                                                                                                                  \
        auto* logger = omni::kit::exec::core::unstable::getTbbSchedulerState();                                        \
        if (CARB_UNLIKELY(logger != nullptr))                                                                          \
        {                                                                                                              \
            logger->recordPushedIsolateTask();                                                                         \
        }                                                                                                              \
    } while (0)

#define OMNI_KIT_EXEC_RECORD_PUSHED_SERIAL_TASK()                                                                      \
    do                                                                                                                 \
    {                                                                                                                  \
        auto* logger = omni::kit::exec::core::unstable::getTbbSchedulerState();                                        \
        if (CARB_UNLIKELY(logger != nullptr))                                                                          \
        {                                                                                                              \
            logger->recordPushedSerialTask();                                                                          \
        }                                                                                                              \
    } while (0)


// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/kit/exec/core/unstable/ITbbSchedulerState.gen.h>
