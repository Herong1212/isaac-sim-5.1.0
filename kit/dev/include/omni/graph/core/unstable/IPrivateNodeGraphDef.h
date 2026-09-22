// Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file IPrivateNodeGraphDef.h
//!
//! @brief Defines @ref omni::graph::core::unstable::IPrivateNodeGraphDef.
#pragma once

#include <omni/graph/core/Handle.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/exec/unstable/ConstName.h>
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

// forward declarations needed by interface declaration
class IDef;
class INode;
class ExecutionTask;

}
}

namespace core
{
namespace unstable
{

// forward declarations needed by interface declaration
class IPrivateNodeGraphDef;
class IPrivateNodeGraphDef_abi;

//! This is a private interface.  Rather than directly using this private interface,
//! access the functionality this interface provides by subclassing GenericGraphDef
class IPrivateNodeGraphDef_abi
    : public omni::core::Inherits<exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.core.unstable.IPrivateNodeGraphDef")>
{
protected:
    //! Returns a handle to authoring graph associated with this definition.
    virtual GraphObj getAuthoringGraph_abi() noexcept = 0;

    //! Returns True if this graph is used as part of instancing pipeline, false otherwise.
    //!
    //! @note   We will most likely remove this before making this interface stable
    virtual bool isInstanced_abi() noexcept = 0;

    //! Internal binding to receive invalidation messages.
    //!
    //! @note   Once OG will provide topology changed notifications we can register to, this should go away.
    virtual void attachToAuthoring_abi(OMNI_ATTR("not_null") omni::graph::exec::unstable::IDef* definition) noexcept = 0;

    //! Pre-execution call can be used to setup the graph state prior to execution or skip entirely the execution.
    //!
    //! The given task must not be @c nullptr.
    virtual omni::graph::exec::unstable::Status preExecute_abi(OMNI_ATTR(
        "in, out, not_null, ref") omni::graph::exec::unstable::ExecutionTask* info) noexcept = 0;

    //! Post-execution call can be used to finalize the execution, e.g. transfer computation results to consumers.
    //!
    //! The given task must not be @c nullptr.
    virtual omni::graph::exec::unstable::Status postExecute_abi(OMNI_ATTR(
        "in, out, not_null, ref") omni::graph::exec::unstable::ExecutionTask* info) noexcept = 0;

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
#include <omni/graph/core/unstable/IPrivateNodeGraphDef.gen.h>

// custom API declaration

//! @copydoc omni::graph::core::IPrivateNodeGraphDef_abi
class omni::graph::core::unstable::IPrivateNodeGraphDef
    : public omni::core::Generated<omni::graph::core::unstable::IPrivateNodeGraphDef_abi>
{
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/IGraphBuilder.h>
#include <omni/graph/exec/unstable/INode.h>

// custom API implementation

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/core/unstable/IPrivateNodeGraphDef.gen.h>
