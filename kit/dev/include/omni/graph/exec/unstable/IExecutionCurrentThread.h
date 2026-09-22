// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IExecutionCurrentThread.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IExecutionCurrentThread.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/Status.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class ExecutionTask;
class IExecutionContext;
class IExecutionCurrentThread_abi;
class IExecutionCurrentThread;
class IExecutionStateInfo;
class IExecutor;
class IGraph;

//! Encapsulates the execution state for the current thread allowing callers to determine quantities like the @ref
//! omni::graph::exec::unstable::ExecutionTask currently executing on the thread.
//!
//! Because methods in this interface return thread local data, all methods in this interface are thread safe.
//!
//! This interface is usually accessed as a singleton via one of the following helper methods:
//!
//! - @ref omni::graph::exec::unstable::getCurrentTask()
//!
//! - @ref omni::graph::exec::unstable::getCurrentExecutor()
//!
//! This interface contains methods for graph and task execution.  Users should not call these methods directly.  See
//! the methods' docs below for the correct way to perform execution.
//!
//! See @rstref{Execution Concepts <ef_execution_concepts>} for an in-depth guide on how this object is used during
//! execution.
//!
//! @thread_safety Methods in this interface are thread safe.
class IExecutionCurrentThread_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                  OMNI_TYPE_ID("omni.graph.exec.unstable.IExecutionCurrentThread")>
{
protected:
    //! Executes the given @ref omni::graph::exec::unstable::IGraph on the current thread.
    //!
    //! Do not call this function directly, rather, call @ref omni::graph::exec::unstable::IExecutionContext::execute().
    //!
    //! From an ABI point-of-view, the purpose of this method is to handle the special case of the top-level @ref
    //! omni::graph::exec::unstable::INodeGraphDef being contained by @ref omni::graph::exec::unstable::IGraph rather
    //! than pointed to by a node in another @ref omni::graph::exec::unstable::INodeGraphDef.  Meaningful values are set
    //! for the threads current task and executor (see @ref omni::graph::exec::unstable::getCurrentTask() and @ref
    //! omni::graph::exec::unstable::getCurrentExecutor()).
    //!
    //! For further details on the meaning of the returned value, see @rstref{Error Handling<ef_error_handling>}.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("nodiscard") Status executeGraph_abi(OMNI_ATTR("not_null") IGraph* graph,
                                                           OMNI_ATTR("not_null") IExecutionContext* context) noexcept = 0;

    //! Executes the given task on the current thread.
    //!
    //! Do not call this function directly, rather, call @ref omni::graph::exec::unstable::ExecutionTask::execute().
    //!
    //! This method executes the definition of the node pointed to by the given task.  Importantly, this method sets
    //! thread local data to track the currently running task and executor (see @ref
    //! omni::graph::exec::unstable::getCurrentTask() and @ref omni::graph::exec::unstable::getCurrentExecutor()).
    //!
    //! Both the given task and executor must not be @c nullptr.
    //!
    //! The node in the given task will be executed and its status set.  This status can be retrieved with @ref
    //! omni::graph::exec::unstable::ExecutionTask::getExecutionStatus().
    //!
    //! Once the node has been executed, @ref omni::graph::exec::unstable::IExecutor::continueExecute() is called and
    //! its status returned.  The returned status may not be the same as the status set on the task that was executed.
    //!
    //! For further details on the meaning of the returned value, see @rstref{Error Handling<ef_error_handling>}.
    //!
    //! It is not an error if the given node does not have an attached definition.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("nodiscard") Status execute_abi(OMNI_ATTR("in, out, not_null, ref") ExecutionTask* task,
                                                      OMNI_ATTR("not_null") IExecutor* executor) noexcept = 0;

    //! Access the task currently executing on the current thread.
    //!
    //! This is useful when needing to access execution context state without having to pass it to every function.
    //!
    //! Do not call this function directly, rather, call @ref omni::graph::exec::unstable::getCurrentTask().
    //!
    //! May return @c nullptr if no task is active on the current thread.
    //!
    //! @thread_safety This method is thread safe.
    virtual ExecutionTask* getCurrentTask_abi() noexcept = 0;

    //! Access the executor currently executing on the current thread.
    //!
    //! Useful when needing to spawn extra work within the scope of the graph.
    //!
    //! Do not call this function directly, rather, call @ref omni::graph::exec::unstable::getCurrentExecutor().
    //!
    //! The returned @ref omni::graph::exec::unstable::IExecutor does *not* have @ref omni::core::IObject::acquire()
    //! called before being returned.
    //!
    //! May return @c nullptr if an executor is not executing on the curren thread.  Note, @c nullptr may be returned
    //! even if @ref omni::graph::exec::unstable::getCurrentTask() returns a valid value.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("no_acquire") IExecutor* getCurrentExecutor_abi() noexcept = 0;
};

//! Smart pointer managing an instance of @ref IExecutionCurrentThread.
using ExecutionCurrentThreadPtr = omni::core::ObjectPtr<IExecutionCurrentThread>;

//! Access current thread's execution state.
//!
//! The returned pointer is a singleton managed by *omni.graph.exec*, and does *not* have @ref
//! omni::core::IObject::acquire() called on it before being returned.  The caller should *not* call @ref
//! omni::core::IObject::release() on the returned raw pointer.
//!
//! This method always returns a valid pointer.
//!
//! @thread_safety This method is thread safe.
inline IExecutionCurrentThread* getCurrentThread() noexcept;

//! Access task currently executed on a calling thread.
//!
//! May return @c nullptr if no task is active on the current thread.
//!
//! @thread_safety This method is thread safe.
inline ExecutionTask* getCurrentTask() noexcept;

//! Access executor currently used on the current thread.
//!
//! Useful when needing to spawn extra work within the scope of the graph.
//!
//! The returned @ref IExecutor does *not* have @ref omni::core::IObject::acquire() called before being returned.
//!
//! May return @c nullptr if an executor is not executing on the current thread.  Note, @c nullptr may be returned even
//! if @ref omni::graph::exec::unstable::getCurrentTask() returns a valid value (the use of executors is not a strict
//! requirement).
//!
//! @thread_safety This method is thread safe.
inline IExecutor* getCurrentExecutor() noexcept;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IExecutionCurrentThread.gen.h>

//! @copydoc omni::graph::exec::unstable::IExecutionCurrentThread_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IExecutionCurrentThread
    : public omni::core::Generated<omni::graph::exec::unstable::IExecutionCurrentThread_abi>
{
};

// additional headers needed for API implementation
#include <omni/core/ITypeFactory.h>
#include <omni/graph/exec/unstable/ExecutionTask.h>
#include <omni/graph/exec/unstable/IExecutionContext.h>
#include <omni/graph/exec/unstable/IExecutor.h>
#include <omni/graph/exec/unstable/IGraph.h>

inline omni::graph::exec::unstable::IExecutionCurrentThread* omni::graph::exec::unstable::getCurrentThread() noexcept
{
    // createType() always calls acquire() and returns an ObjectPtr to make sure release() is called. we don't want to
    // hold a ref here to avoid static destruction issues. here we allow the returned ObjectPtr to destruct (after
    // calling get()) to release our ref. we know the DLL in which the singleton was created is maintaining a ref and
    // will keep the singleton alive for the lifetime of the DLL.
    static auto sSingleton = omni::core::createType<IExecutionCurrentThread>().get();
    return sSingleton;
}

inline omni::graph::exec::unstable::ExecutionTask* omni::graph::exec::unstable::getCurrentTask() noexcept
{
    return getCurrentThread()->getCurrentTask();
}

inline omni::graph::exec::unstable::IExecutor* omni::graph::exec::unstable::getCurrentExecutor() noexcept
{
    return getCurrentThread()->getCurrentExecutor();
}

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IExecutionCurrentThread.gen.h>
