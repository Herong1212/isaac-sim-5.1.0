// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IExecutor.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IExecutor.
#pragma once

#include <omni/graph/exec/unstable/ExecutionTask.h>
#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/SchedulingInfo.h>
#include <omni/graph/exec/unstable/Status.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

class IExecutor_abi;
class IExecutor;
class IScheduleFunction;

//! Executes the nodes in a graph definition.
//!
//! The purpose of an executor is to generate work for the nodes in an graph definition.  @ref
//! omni::graph::exec::unstable::IExecutor is a minimal interface that defines enough methods to accomplish just that.
//!
//! However, @ref omni::graph::exec::unstable::IExecutor's minimal nature is not what most users want when customizing
//! execution for their graph definitions.  Rather, they want something useful.  @ref
//! omni::graph::exec::unstable::Executor is an useful implementation of @ref omni::graph::exec::unstable::IExecutor
//! designed for graph definition authors to extend.  See
//! @ref omni::graph::exec::unstable::Executor's documentation to better understand the purpose, duties, and
//! capabilities of an executor.
//!
//! See @rstref{Execution Concepts <ef_execution_concepts>} for an in-depth guide on how this object is used during
//! execution.
//!
//! See @rstref{Creating an Executor <ef_executor_creation>} for a guide on creating a customize executor for your graph
//! defintion.
//!
//! @thread_safety There are no thread safety requirements for executors.  It is up to the executor implementor to
//! decide if an executor should process nodes in parallel or serially.  Likewise, it is up to the graph definition
//! implementor to instantiate and use a concrete implementation of @ref omni::graph::exec::unstable::IExecutor in a
//! manner meeting the concrete implementation's threading requirements.
class IExecutor_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.exec.unstable.IExecutor")>
{
protected:
    //! Main execute method. Returning status of the execution.
    //!
    //! In practice, what is executed will be defined in the concrete implementation's constructor.
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("nodiscard") Status execute_abi() noexcept = 0;

    //! Request for scheduling of additional work generated during execution of a task.
    //!
    //! @param  fn  Function to call once the work is dispatched.
    //! @param  schedInfo   Scheduling constraints to use when dispatching this work.
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("nodiscard, no_api") Status
        schedule_abi(OMNI_ATTR("not_null") IScheduleFunction* fn, SchedulingInfo schedInfo) noexcept = 0;

    //! Request for scheduling of additional work after the given task has executed but before it has completed.
    //!
    //! @param  task  The current task.  Must not be @c nullptr.
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("nodiscard") Status
        continueExecute_abi(OMNI_ATTR("in, out, not_null, ref") ExecutionTask* task) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IExecutor.
using ExectorPtr = omni::core::ObjectPtr<IExecutor>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IExecutor.gen.h>

//! @copydoc omni::graph::exec::unstable::IExecutor_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IExecutor : public omni::core::Generated<omni::graph::exec::unstable::IExecutor_abi>
{
public:
    //! Schedules the supplied function.
    //!
    //! The given function must have the signature of `Status(void)`.
    //!
    //! @thread_safety See thread safety information in interface description.
    template <typename Fn>
    CARB_NODISCARD inline Status schedule(Fn&& fn, SchedulingInfo schedInfo) noexcept;
};

#include <omni/graph/exec/unstable/ScheduleFunction.h>

#ifndef DOXYGEN_BUILD // templates confuse doxygen :(
template <typename Fn>
inline omni::graph::exec::unstable::Status omni::graph::exec::unstable::IExecutor::schedule(Fn&& fn,
                                                                                            SchedulingInfo schedInfo) noexcept
{
    return schedule_abi(omni::graph::exec::unstable::ScheduleFunction<Fn>::create(std::forward<Fn>(fn)).get(), schedInfo);
}

#endif // DOXYGEN_BUILD

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IExecutor.gen.h>
