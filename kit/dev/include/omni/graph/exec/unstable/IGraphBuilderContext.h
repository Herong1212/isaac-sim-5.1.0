// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IGraphBuilderContext.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IGraphBuilderContext.
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
class IGraph;
class IGraphBuilder;
class IGraphBuilderContext;
class IGraphBuilderContext_abi;
class INodeGraphDef;

//! Common state for graph builders.
class IGraphBuilderContext_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                  OMNI_TYPE_ID("omni.graph.exec.unstable.IGraphBuilderContext")>
{
protected:
    //! Current construction version.
    //!
    //! Incremented after each pass pipeline run to include definitions that were created before the run.
    virtual Stamp getConstructionStamp_abi() noexcept = 0;

    //! Return owner of all graphs this builder touches
    //!
    //! The returned @ref omni::graph::exec::unstable::IGraph will *not* have
    //! @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") IGraph* getGraph_abi() noexcept = 0;

    //! Run transformation pipeline on the given graph.
    //!
    //! The given graph definition must not be @c nullptr.
    virtual void runTransformations_abi(OMNI_ATTR("not_null") INodeGraphDef* nodeGraphDef) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IGraphBuilderContext.
using GraphBuilderContextPtr = omni::core::ObjectPtr<IGraphBuilderContext>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IGraphBuilderContext.gen.h>

//! @copydoc omni::graph::exec::unstable::IGraphBuilderContext_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IGraphBuilderContext
    : public omni::core::Generated<omni::graph::exec::unstable::IGraphBuilderContext_abi>
{
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/IGraph.h>
#include <omni/graph/exec/unstable/IGraphBuilder.h>
#include <omni/graph/exec/unstable/INodeGraphDef.h>

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IGraphBuilderContext.gen.h>
