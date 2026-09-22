// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IScheduleFunction.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IScheduleFunction.
#pragma once

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

class IScheduleFunction_abi;
class IScheduleFunction;
template <typename T>
class ScheduleFunction;

//! Interface wrapping a function (possibly with storage). Used to wrap a task when passing generated work to the
//! scheduler.
//!
//! This interface is used by @ref omni::graph::exec::unstable::IExecutor::schedule_abi(). Manual instantiation of this
//! interface can be avoided by simply calling @ref omni::graph::exec::unstable::IExecutor::schedule(), which will wrap
//! the given invocable object in an instance of this interface.
//!
//! @thread_safety See thread safety notes in @ref omni::graph::exec::unstable::IExecutor.
class IScheduleFunction_abi : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                                          OMNI_TYPE_ID("omni.graph.exec.unstable.IScheduleFunction")>
{
protected:
    //! Main execute method. Returning status of the execution.
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("nodiscard") Status invoke_abi() noexcept = 0;
};

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IScheduleFunction.gen.h>

//! @copydoc omni::graph::exec::unstable::IScheduleFunction_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IScheduleFunction
    : public omni::core::Generated<omni::graph::exec::unstable::IScheduleFunction_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IScheduleFunction.gen.h>
