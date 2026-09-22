// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IPassPipeline.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IPassPipeline.
#pragma once

#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/Stamp.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class IGraphBuilderContext;
class IPassPipeline;
class IPassPipeline_abi;
class INodeGraphDef;

//! Runs registered passes.
//!
//! The role of pass pipeline is to populate and prepare the execution graph. The base implementation runs passes based
//! on the type and registration order. Most applications will define their own pass pipeline to control how the
//! execution graph is generated.
//!
//! See @rstref{Pass Concepts <ef_pass_concepts>} for an in-depth guide on how passes are used during graph
//! construction.
//!
//! See @ref omni::graph::exec::unstable::PassPipeline for a concrete implementation of this interface.
//!
//! See @ref groupOmniGraphExecPasses for more pass related functionality.
class IPassPipeline_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.exec.unstable.IPassPipeline")>
{
protected:
    //! Test if the pipeline needs to rebuild (mostly for its acceleration structures).
    //!
    //! An example of when a pipeline would need to be reconstructed is when a pass is either added or removed from @ref
    //! omni::graph::exec::unstable::IPassRegistry.
    virtual bool needsConstruction_abi() noexcept = 0;

    //! Build the pipeline (mostly for its acceleration structures).
    virtual void construct_abi() noexcept = 0;

    //! Test if pipeline needs to run (after topology changes in the graph).
    virtual bool needsRun_abi(Stamp globalTopology) noexcept = 0;

    //! Run the graph transformations pipeline
    virtual void run_abi(OMNI_ATTR("not_null") IGraphBuilderContext* builderContext,
                         OMNI_ATTR("not_null") INodeGraphDef* nodeGraphDef) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IPassPipeline.
using PassPipelinePtr = omni::core::ObjectPtr<IPassPipeline>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IPassPipeline.gen.h>

//! @copydoc omni::graph::exec::unstable::IPassPipeline_abi
//!
//! @ingroup  groupOmniGraphExecPasses groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IPassPipeline
    : public omni::core::Generated<omni::graph::exec::unstable::IPassPipeline_abi>
{
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/IGraphBuilder.h>
#include <omni/graph/exec/unstable/IGraphBuilderContext.h>
#include <omni/graph/exec/unstable/INodeGraphDef.h>

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IPassPipeline.gen.h>
