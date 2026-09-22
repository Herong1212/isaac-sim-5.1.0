// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file IGenericNodeGraphDef.h
//!
//! @brief Defines @ref omni::graph::core::unstable::IGenericNodeGraphDef.
#pragma once

#include <omni/graph/exec/unstable/INodeGraphDef.h>

#include <omni/graph/core/Handle.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/inspect/IInspector.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class INode;
class IGraphBuilder;

}
}

namespace core
{
namespace unstable
{

// forward declarations needed by interface declaration
class IGenericNodeGraphDef;
class IGenericNodeGraphDef_abi;

//! Node graph definition interface for OmniGraph graph.
//!
//! This interface allows us to reason about OmniGraph graphs during graph transformation phase and access authoring
//! graph associated with this definition.
class IGenericNodeGraphDef_abi : public omni::core::Inherits<exec::unstable::INodeGraphDef, OMNI_TYPE_ID("omni.graph.core.unstable.IGenericNodeGraphDef")>
{
protected:
    //! Returns a handle to authoring graph associated with this definition.
    virtual GraphObj getAuthoringGraph_abi() noexcept = 0;

    //! Returns True if this graph is used as part of instancing pipeline, false otherwise.
    //!
    //! @note   We will most likely remove this before making this interface stable
    virtual bool isInstanced_abi() noexcept = 0;

    //! Returns execution node associated with a given authoring node, or nullptr
    //! if no association was discovered in this definition.
    //!
    //! The returned @ref INode will *not* have @ref omni::core::IObject::acquire() called before being
    //! returned.
    virtual OMNI_ATTR("no_acquire") omni::graph::exec::unstable::INode* getExecutionNode_abi(
        OMNI_ATTR("in, not_null, ref") const NodeObj* nodeObj) noexcept = 0;

    //! Construct the graph.
    //!
    //! Construction can happen for entire execution graph or only affected by a topological change definitions.
    virtual omni::graph::exec::unstable::IGraphBuilder* build_abi(omni::graph::exec::unstable::IGraphBuilder* builder) noexcept = 0;

    //! Inspect the state of the graph
    virtual bool inspect_abi(
        OMNI_ATTR("not_null") inspect::IInspector* inspector) noexcept = 0;

    //! Acquire internal information about bucketing of instances for vectorized execution
    //!
    //! Arguments must not be @c nullptr.
    virtual void getInstanceInfo_abi(OMNI_ATTR("in, not_null, ref")
                                         omni::graph::exec::unstable::ExecutionTask const* info,
                                     OMNI_ATTR("out, not_null, ref") omni::graph::core::InstanceIndex* retBaseInstanceIndex,
                                     OMNI_ATTR("out, not_null, ref") size_t* retNumberOfInstances) noexcept = 0;
};

} // namespace unstable
} // namespace core
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/core/unstable/IGenericNodeGraphDef.gen.h>

// custom API declaration

//! @copydoc omni::graph::core::IGenericNodeGraphDef_abi
class omni::graph::core::unstable::IGenericNodeGraphDef : public omni::core::Generated<omni::graph::core::unstable::IGenericNodeGraphDef_abi>
{ };

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/INode.h>
#include <omni/graph/exec/unstable/IGraphBuilder.h>
#include <omni/graph/exec/unstable/ExecutorFactory.h>

// custom API implementation

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/core/unstable/IGenericNodeGraphDef.gen.h>
