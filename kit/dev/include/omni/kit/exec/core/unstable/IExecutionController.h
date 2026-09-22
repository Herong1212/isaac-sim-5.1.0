// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IExecutionController.h
//!
//! @brief Defines @ref omni::kit::exec::core::unstable::IExecutionController.
#pragma once

#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/Status.h>
#include <omni/kit/IStageUpdate.h> // StageUpdateSettings

#include <type_traits>

//! @defgroup groupOmniKitExecCoreInterfaces API Interfaces
//!
//! @brief Convenience interfaces backed by a stable ABI.

namespace omni
{

namespace graph
{

namespace exec
{
namespace unstable
{

class IDef;
class IGraph;
class IScheduleFunction;

} // namespace unstable
} // namespace exec
} // namespace graph

namespace kit
{

namespace exec
{

//! Main namespace for Kit's integration of @ref omni::graph::exec.
namespace core
{

//! In-development interfaces for Kit's integration with Execution Framework.
//! Do not take dependencies on any code in this namespace.
namespace unstable
{

// Forward declarations needed by interface declaration.
class IExecutionContext;
class IExecutionController;
class IExecutionController_abi;

//! @ref omni::kit::exec::core::unstable::IExecutionController encapsulates a @ref omni::graph::exec::unstable::IGraph
//! which helps orchestrates part of the computation for one of Kit's @c UsdContext.
//!
//! See @ref omni::kit::exec::core::unstable::IExecutionControllerFactory.
class IExecutionController_abi
    : public omni::core::Inherits<graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.kit.exec.core.unstable.IExecutionController")>
{
protected:
    //! Populates or updates the internal @ref omni::graph::exec::unstable::IGraph.
    //!
    //! @thread_safety This method is thread safe, but not thread-efficient (i.e., it's protected with various mutex
    //! locks).
    virtual void compile_abi() noexcept = 0;

    //! Searches for the @ref omni::graph::exec::unstable::IDef and executes it.  Useful for on-demand execution.
    //!
    //! The @ref omni:graph::exec::unstable::Status of the execution of the definition is returned.  If the definition
    //! is shared by multiple nodes, the definition will be executed at each path and the return status or'd together.
    //!
    //! It is up to the caller to ensure the given definition is up-to-date/built.
    //!
    //! @p execDef must not be @c nullptr or the top-level execution graph's @ref NodeGraphDef (i.e., the top-level
    //! execution graph can only be evaluated using the @ref
    //! omni::kit::exec::core::unstable::IExecutionController_abi::execute_abi method).
    //!
    //! @thread_safety This method is thread safe, but not thread-efficient (i.e., it's protected with various mutex
    //! locks).
    virtual OMNI_ATTR("nodiscard") omni::graph::exec::unstable::Status
        executeDefinition_abi(OMNI_ATTR("not_null") omni::graph::exec::unstable::IDef* execDef) noexcept = 0;

    //! Executes the internal graph at the given time.
    //!
    //! The execution graph will be compiled (if deemed necessary) before executing.
    //!
    //! @p updateSettings may be @c nullptr.
    //!
    //! @thread_safety This method is thread safe, but not thread-efficient (i.e., it's protected with various mutex
    //! locks).
    virtual OMNI_ATTR("nodiscard") omni::graph::exec::unstable::Status
        execute_abi(double currentTime,
                    float elapsedSecs,
                    double absoluteSimTime,
                    OMNI_ATTR("in") const omni::kit::StageUpdateSettings* updateSettings) noexcept = 0;

    //! Returns the context owned by this controller
    //!
    //! The returned @ref omni::kit::exec::core::unstable::IExecutionContext will *not* have @ref
    //! omni::core::IObject::acquire() called before being returned.
    //!
    //! The returned pointer is always valid.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") IExecutionContext* getContext_abi() noexcept = 0;

    //! Returns the graph owned by this controller
    //!
    //! The returned @ref omni::graph::exec::unstable::IGraph will *not* have @ref
    //! omni::core::IObject::acquire() called before being returned.
    //!
    //! The returned pointer is always valid.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") omni::graph::exec::unstable::IGraph* getGraph_abi() noexcept = 0;

    //! Schedule a pre-processing function that will run before the next compilation that's
    //! invoked from this controller.
    //!
    //! Pre-process tasks can be scheduled at any point in time, and are guaranteed to run in isolation of any
    //! other graph compilation, execution and/or post-processing tasks (even in a multithreaded environment where many
    //! threads attempt to use an individual controller for graph evaluations).
    //!
    //! Typically, pre-process tasks on a controller are used to handle "messy" actions that can potentially affect
    //! global state prior to continuing with any compilation/execution actions. For example, OmniGraph utilizes these
    //! pre-process tasks in the query compute system to update some internal implementation details so that it remains
    //! up-to-date with the execution graph topology.
    //!
    //! The given function @p fn must not be @c nullptr.
    //!
    //! The @p persist flag allows one to specify whether or not the task should be destructed immediately after being
    //! executed. A value of @c false will result in the task being treated as a one-off (i.e. destroyed after
    //! evaluating), while a value of @c true will result in the task getting evaluated each time before all subsequent
    //! graph compilations, until the module (i.e. .dll/.so) in which the task was originally enqueued from gets
    //! unloaded.
    //!
    //! @thread_safety This method is thread safe. Note that pre-process tasks are consumed serially and schedulable
    //! in parallel.
    virtual OMNI_ATTR("no_api") void schedulePreProcessTask_abi(OMNI_ATTR("not_null")
                                                                    graph::exec::unstable::IScheduleFunction* fn,
                                                                const bool persist,
                                                                const uint64_t moduleHash) noexcept = 0;

    //! Schedule a post-processing function that will run after the current execution cycle that was
    //! invoked from this controller (either via the @ref omni::kit::exec::core::unstable::IExecutionController::execute
    //! or @ref omni::kit::exec::core::unstable::IExecutionController::executeDefinition methods).
    //!
    //! Post-process tasks can only be scheduled during execution, and are guaranteed to run in isolation of any
    //! other graph compilation, execution and/or pre-processing tasks (even in a multithreaded environment where many
    //! threads attempt to use an individual controller for graph evaluations).
    //!
    //! Typically, post-process tasks on a controller are used to handle "messy" actions that can potentially affect
    //! global state prior to continuing with any execution actions. For example, different modules will use
    //! post-process tasks to defer execution graph invalidation/reconstruction if they detect that the graph topology
    //! needs to be updated *during execution*; the deferral is necessary since we cannot invalidate the graph topology
    //! from within execution.
    //!
    //! The given function must not be @c nullptr.
    //!
    //! @thread_safety This method is thread safe. Note that post-process tasks are consumed serially and schedulable
    //! in parallel.
    virtual OMNI_ATTR("no_api") void schedulePostProcessTask_abi(
        OMNI_ATTR("not_null") graph::exec::unstable::IScheduleFunction* fn) noexcept = 0;
};

//! Smart pointer for @ref omni::kit::exec::core::unstable::IExecutionController.
using ExecutionControllerPtr = omni::core::ObjectPtr<IExecutionController>;

} // namespace unstable
} // namespace core
} // namespace exec
} // namespace kit
} // namespace omni

// Generated API declaration.
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/kit/exec/core/unstable/IExecutionController.gen.h>

//! @copydoc omni::kit::exec::core::unstable::IExecutionController_abi
//!
//! @ingroup groupOmniKitExecCoreInterfaces
class omni::kit::exec::core::unstable::IExecutionController
    : public omni::core::Generated<omni::kit::exec::core::unstable::IExecutionController_abi>
{
public:
    //! @copydoc omni::kit::exec::core::unstable::IExecutionController::schedulePreProcessTask_abi
    //!
    //! This inline implementation wraps lambda into an @ref omni::graph::exec::unstable::IScheduleFunction.
    //!
    //! The supplied function should have the signature of `void()`.
    template <typename Fn>
    inline void schedulePreProcessTask(Fn&& callback, const bool persist) noexcept;

    //! @copydoc omni::kit::exec::core::unstable::IExecutionController::schedulePostProcessTask_abi
    //!
    //! This inline implementation wraps lambda into an @ref omni::graph::exec::unstable::IScheduleFunction.
    //!
    //! The supplied function should have the signature of `void()`.
    template <typename Fn>
    inline void schedulePostProcessTask(Fn&& callback) noexcept;
};

// Additional headers needed for API implementation.
#include <omni/graph/exec/unstable/IDef.h>
#include <omni/graph/exec/unstable/IGraph.h>
#include <omni/graph/exec/unstable/ScheduleFunction.h>
#include <omni/kit/exec/core/unstable/IExecutionContext.h>
#include <omni/kit/exec/core/unstable/IExecutionControllerFactory.h>

template <typename Fn>
inline void omni::kit::exec::core::unstable::IExecutionController::schedulePreProcessTask(Fn&& callback,
                                                                                          const bool persist) noexcept
{
    schedulePreProcessTask_abi(
        omni::graph::exec::unstable::ScheduleFunction<Fn>::create(std::forward<Fn>(callback)).get(), persist,
        omni::kit::exec::core::unstable::detail::getModuleHash());
}

template <typename Fn>
inline void omni::kit::exec::core::unstable::IExecutionController::schedulePostProcessTask(Fn&& callback) noexcept
{
    if (getContext()->inExecute())
    {
        schedulePostProcessTask_abi(
            omni::graph::exec::unstable::ScheduleFunction<Fn>::create(std::forward<Fn>(callback)).get());
    }
}

// Generated API implementation.
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/kit/exec/core/unstable/IExecutionController.gen.h>
