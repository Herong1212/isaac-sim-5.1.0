// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file INodeDef.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::INodeDef.
#pragma once

#include <omni/graph/exec/unstable/IDef.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

class INodeDef_abi;
class INodeDef;

//! Opaque node definition.
//!
//! Nodes are opaque because the Execution Framework has no knowledge or what the execution method will do and does not
//! orchestrate generation and dispatch of the tasks.
//!
//! Node definitions can be shared across multiple nodes and graphs. The implementation should leverage execution task
//! to operate within proper task state.
//!
//! See @rstref{Execution Concepts <ef_execution_concepts>} for an in-depth guide on how this object is used during
//! execution.
//!
//! See also @ref omni::graph::exec::unstable::ExecutionTask, @ref omni::graph::exec::unstable::ExecutionPath.
class INodeDef_abi : public omni::core::Inherits<IDef, OMNI_TYPE_ID("omni.graph.exec.unstable.INodeDef")>
{
};

//! Smart pointer managing an instance of @ref omni::graph::exec::unstable::INodeDef.
using NodeDefPtr = omni::core::ObjectPtr<INodeDef>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/INodeDef.gen.h>

//! @copydoc omni::graph::exec::unstable::INodeDef_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::INodeDef : public omni::core::Generated<omni::graph::exec::unstable::INodeDef_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/INodeDef.gen.h>
