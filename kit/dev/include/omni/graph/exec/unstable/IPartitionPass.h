// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IPartitionPass.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IPartitionPass.
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
class INode;
class ITopology;
class IPartitionPass;
class IPartitionPass_abi;

//! Base class for graph partitioning passes.
//!
//! See @rstref{Pass Concepts <ef_pass_concepts>} for an in-depth guide on how this object is used during graph
//! construction.
//!
//! Partition passes are typically run just after population passes and only on newly modified
//! @ref omni::graph::exec::unstable::INodeGraphDef objects. The job of a partition pass is to recognize patterns in the
//! newly populated graph and replace them with a new definition or augment existing ones.
//!
//! Partition passes can only mutate the graph from the @ref omni::graph::exec::unstable::IPartitionPass::commit method
//! using the provided @ref omni::graph::exec::unstable::IGraphBuilder. This will guarantee that the rest of the
//! pipeline is aware of changes made to the graph and avoid potential threading issues.
//!
//! See @ref  groupOmniGraphExecPasses for more pass related functionality.
class IPartitionPass_abi : public omni::core::Inherits<IPass, OMNI_TYPE_ID("omni.graph.exec.unstable.IPartitionPass")>
{
protected:
    //! Call from pass pipeline to initialize the pass for @p topology.
    //!
    //! This interface method implementation must not mutate the given @p topology. Multiple passes can run concurrently
    //! on it.
    //!
    //! @p topology must not be @c nullptr.
    //!
    //! Returns `true` if initialization was successful and the pipeline should issue calls to `run` and `commit`.
    //! Otherwise, this pass will be destroyed and will not participate in partitioning @p topology.
    //!
    //! @thread_safety @ref omni::graph::exec::unstable::IPassPipeline will never call this method concurrently.
    virtual bool initialize_abi(OMNI_ATTR("not_null") ITopology* topology) noexcept = 0;

    //! Call from pass pipeline to discover nodes requiring partitioning.
    //!
    //! No topology changes are permitted at this point. Multiple passes will get a chance to receive this notification.
    //!
    //! The given @p node must not be @c nullptr.
    //!
    //! @thread_safety @ref omni::graph::exec::unstable::IPassPipeline will never call this method concurrently.
    virtual void run_abi(OMNI_ATTR("not_null") INode* node) noexcept = 0;

    //! Call to verify generated partitions and commit new definition/s replacing discovered partitions.
    //!
    //! Commit of partitions is done serially and in the priority order of the pass. Passes with higher order will get
    //! the chance first. This is the only partition pass method that can mutate the graph.
    //!
    //! Because higher priority partition passes may mutate the graph, care must be taken by lower priority passes in
    //! this method to recognize if the nodes selected in @ref omni::graph::exec::unstable::IPartitionPass::run() still
    //! make sense to partition.
    //!
    //! The given @p builder must not be @c nullptr.
    //!
    //! @thread_safety @ref omni::graph::exec::unstable::IPassPipeline will never call this method concurrently.
    virtual void commit_abi(OMNI_ATTR("not_null") IGraphBuilder* builder) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IPartitionPass.
using PartitionPassPtr = omni::core::ObjectPtr<IPartitionPass>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IPartitionPass.gen.h>

//! @copydoc omni::graph::exec::unstable::IPartitionPass_abi
//!
//! @ingroup  groupOmniGraphExecPasses groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IPartitionPass
    : public omni::core::Generated<omni::graph::exec::unstable::IPartitionPass_abi>
{
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/IGraphBuilder.h>
#include <omni/graph/exec/unstable/INode.h>
#include <omni/graph/exec/unstable/ITopology.h>

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IPartitionPass.gen.h>
