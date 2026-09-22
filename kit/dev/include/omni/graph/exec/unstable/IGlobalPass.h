// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IGlobalPass.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IGlobalPass.
#pragma once

#include <omni/graph/exec/unstable/IPass.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class IGraphBuilder;
class IGlobalPass;
class IGlobalPass_abi;

//! Base class for global passes.
//!
//! See @rstref{Pass Concepts <ef_pass_concepts>} for an in-depth guide on how this object is used during
//! graph construction.
//!
//! The purpose of a global pass is to perform global transformations on the graph.
//!
//! This transformation category should be considered as a last resort given its global impact on the topology which
//! prevents threading at the pass pipeline level.
//!
//! Register a global pass with @ref OMNI_GRAPH_EXEC_REGISTER_GLOBAL_PASS().
//!
//! See @ref groupOmniGraphExecPasses for more pass related functionality.
//!
//! @thread_safety Only a single global pass is active in a graph definition at a time.
class IGlobalPass_abi : public omni::core::Inherits<IPass, OMNI_TYPE_ID("omni.graph.exec.unstable.IGlobalPass")>
{
protected:
    //! Called from a pass pipeline to apply global graph transformations.
    //!
    //! The given @p builder supplies the graph definition to transform.  @p builder must not be @c nullptr.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual void run_abi(OMNI_ATTR("not_null") IGraphBuilder* builder) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IGlobalPass.
using GlobalPassPtr = omni::core::ObjectPtr<IGlobalPass>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IGlobalPass.gen.h>

//! @copydoc omni::graph::exec::unstable::IGlobalPass_abi
//!
//! @ingroup  groupOmniGraphExecPasses groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IGlobalPass
    : public omni::core::Generated<omni::graph::exec::unstable::IGlobalPass_abi>
{
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/IGraphBuilder.h>

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IGlobalPass.gen.h>
