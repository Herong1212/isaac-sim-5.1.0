// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IApplyOnEachFunction.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IApplyOnEachFunction.
#pragma once

#include <omni/graph/exec/unstable/IBase.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

class IApplyOnEachFunction_abi;
class IApplyOnEachFunction;
class ExecutionPath;

//! Interface wrapping a function (possibly with storage) to apply on all instantiations of a given definition.
//!
//! This interface is used by @ref omni::graph::exec::unstable::IExecutionContext::applyOnEachDef_abi() and @ref
//! omni::graph::exec::unstable::IExecutionContext::applyOnEachDefWithName_abi().  Manual instantiation of this
//! interface can be avoided by simply calling @ref omni::graph::exec::unstable::IExecutionContext::applyOnEach() which
//! will wrap the given invocable object in an instance of this interface.
//!
//! @thread_safety Within an invocation of @ref omni::graph::exec::unstable::IExecutionContext::applyOnEach(), this
//! callback will executed serially. However, other threads may also invoke
//! omni::graph::exec::unstable::IExecutionContext::applyOnEach(), meaning the @p callback must coordinate access to
//! shared data.
class IApplyOnEachFunction_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                  OMNI_TYPE_ID("omni.graph.exec.unstable.IApplyOnEachFunction")>
{
protected:
    //! Invokes the wrapped function.
    //!
    //! @p path points to a definition found by @ref omni::graph::exec::unstable::IExecutionContext::applyOnEach().  The
    //! given @p path must not be @c nullptr.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual void invoke_abi(OMNI_ATTR("in, not_null, ref") const ExecutionPath* path) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IApplyOnEachFunction.
using ApplyOnEachFunctionPtr = omni::core::ObjectPtr<IApplyOnEachFunction>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IApplyOnEachFunction.gen.h>

//! @copydoc omni::graph::exec::unstable::IApplyOnEachFunction_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IApplyOnEachFunction
    : public omni::core::Generated<omni::graph::exec::unstable::IApplyOnEachFunction_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IApplyOnEachFunction.gen.h>
