// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IDef.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IDef.
#pragma once

#include <omni/graph/exec/unstable/ConstName.h>
#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/SchedulingInfo.h>
#include <omni/graph/exec/unstable/Status.h>
#include <omni/graph/exec/unstable/Types.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

class IDef;
class IDef_abi;
class ExecutionTask;

//! Base class for all node definitions.
//!
//! See @rstref{Execution Concepts <ef_execution_concepts>} for an in-depth guide on how this object is used during
//! execution.
//!
//! @thread_safety Since definitions can be shared by multiple nodes, and nodes can be executed in parallel,
//! implementations of this interface should expect their methods to be called in parallel.
class IDef_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.exec.unstable.IDef")>
{
protected:
    //! Execute the node definition.
    //!
    //! The given task must not be @c nullptr.
    //!
    //! Prefer calling @ref omni::graph::exec::unstable::ExecutionTask::execute() rather than this method as @ref
    //! omni::graph::exec::unstable::ExecutionTask::execute() populates information such as @ref
    //! omni::graph::exec::unstable::getCurrentTask().
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("nodiscard") Status
        execute_abi(OMNI_ATTR("in, out, not_null, ref") ExecutionTask* info) noexcept = 0;

    //! Provides runtime information about scheduling constraints for a given task/node.
    //!
    //! The provided @ref omni::graph::exec::unstable::ExecutionTask can be used to determine the path of the current
    //! definition.
    //!
    //! The given task must not be @c nullptr.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual SchedulingInfo getSchedulingInfo_abi(OMNI_ATTR("in, not_null, ref") const ExecutionTask* info) noexcept = 0;

    //! Return unique definition identifier.
    //!
    //! The returned pointer is never @c nullptr.  The lifetime of the data returned is tied to the lifetime of this
    //! object.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("ref") const ConstName* getName_abi() noexcept = 0;
};

//! Smart pointer managing an instance of @ref omni::graph::exec::unstable::IDef.
using DefPtr = omni::core::ObjectPtr<IDef>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IDef.gen.h>

//! @copydoc omni::graph::exec::unstable::IDef_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IDef : public omni::core::Generated<omni::graph::exec::unstable::IDef_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IDef.gen.h>
