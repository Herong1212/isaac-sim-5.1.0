// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IPopulatePass.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IPopulatePass.
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
class IPopulatePass;
class IPopulatePass_abi;

//! Base class for populate passes.
//!
//! See @rstref{Pass Concepts <ef_pass_concepts>} for an in-depth guide on how this object is used during graph
//! construction.
//!
//! The purpose of a populate pass is to populate a node with a definition.  That definition can be an existing
//! defintion, shared definition, or a new definition.  Likewise, the definition may be either opaque or a graph.
//!
//! Population passes are the main avenue to translate data in the authoring layer to the core Execution Framework.
//!
//! Register a populate pass with @ref OMNI_GRAPH_EXEC_REGISTER_POPULATE_PASS().  When registering a pass, a "name to
//! match" is also specified.  This name is the name of a node or definition on which the registered pass should
//! populate.
//!
//! Populate passes are typically the first pass type to run in the pass pipeline. When a node is encountered during
//! construction, only a single populate pass will get a chance to populate the newly discovered node. If no pass is
//! registered against the node's name, the node definition's name is used to find a population pass to run.
//!
//! Minimal rebuild of the execution graph topology should be considered by the pass each time it runs. Pass pipeline
//! leaves the responsibility of deciding if pass needs to run to the implementation. At minimum it can rely on
//! verifying that the topology of the @ref omni::graph::exec::unstable::NodeGraphDef it generated before is still valid
//! or @ref omni::graph::exec::unstable::NodeDef has not changed.
//!
//! See @ref  groupOmniGraphExecPasses for more pass related functionality.
//!
//! @thread_safety Only a single population pass is run on a node at a time.  However, many threads may be concurrently
//! populating the overall execution graph and care must be taken if a population pass accesses shared state outside of
//! the node's state.
class IPopulatePass_abi : public omni::core::Inherits<IPass, OMNI_TYPE_ID("omni.graph.exec.unstable.IPopulatePass")>
{
protected:
    //! Called from a pass pipeline to apply graph transformations on a given node (definition or topology).
    //!
    //! The given @p builder supplies the graph definition in which the node resides.  @p builder must not be @c
    //! nullptr.
    //!
    //! @p node is the node to populate.  Either the node's name matches the name of this population pass or the name of
    //! the currently attached definition to the node matches. @p node must not be @c nullptr.
    //!
    //! This method is expected to do one of the follow:
    //!
    //! - Set the node's definition to a new definition, shared definition, or @c nullptr.
    //!
    //! - If the node has an attached graph definition, update the graph definition.
    //!
    //! - Do nothing if the definition is up-to-date.  It is up to this method to determine if the definition is
    //!   up-to-date.
    //!
    //! When updating a definition, implementers should strive to perform the minimal amount of work.  This means
    //! instead of tearing down a definition and rebuilding it from scratch, try to detect what has changed and only
    //! update that part of the definition.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual void run_abi(OMNI_ATTR("not_null") IGraphBuilder* builder, OMNI_ATTR("not_null") INode* node) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IPopulatePass.
using PopulatePassPtr = omni::core::ObjectPtr<IPopulatePass>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IPopulatePass.gen.h>

//! @copydoc omni::graph::exec::unstable::IPopulatePass_abi
//!
//! @ingroup  groupOmniGraphExecPasses groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IPopulatePass
    : public omni::core::Generated<omni::graph::exec::unstable::IPopulatePass_abi>
{
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/IGraphBuilder.h>
#include <omni/graph/exec/unstable/INode.h>

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IPopulatePass.gen.h>
