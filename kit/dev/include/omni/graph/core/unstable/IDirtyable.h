// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file IDirtyable.h
//!
//! @brief Defines @ref omni::graph::core::unstable::IDirtyable.
#pragma once

#include <omni/graph/core/Handle.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/unstable/INodeTypeCustomInterfaceBase.h>
#include <omni/kit/exec/core/unstable/IExecutionContext.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

// Forward declarations needed by interface declaration.
class IDirtyable;
class IDirtyable_abi;

//! Defines an interface that OmniGraph nodes can implement to define customized dirtying behavior outside of the
//! OG core. This interface is then utilized by lazy graphs to correctly handle and propagate dirtying logic without
//! the need for hard-coding exceptions for handling specific node types in said graph definition.
//!
//! Think of this interface as a "contract" between the lazy graph executor and OmniGraph nodes that wish to define
//! custom dirtying logic when they're placed inside of lazy graphs for evaluation.
//!
//! Rather than implementing this interface directly, consider deriving from @ref
//! omni::graph::core::unstable::Dirtyable, which will help reduce some of the boilerplate/redundant safety checks that
//! would otherwise need to be repeated in typical use cases.
class IDirtyable_abi
    : public omni::core::Inherits<INodeTypeCustomInterfaceBase, OMNI_TYPE_ID("omni.graph.core.unstable.IDirtyable")>
{
protected:
    //! Queries whether or not the @p nodeObj with the given @p instanceIndex has been marked dirty (via whatever custom
    //! logic the user has implemented to make the determination).
    //!
    //! This method is invoked by lazy graph definitions in the pre-execution phase to give implementors a chance to
    //! dirty themselves before execution.
    //!
    //! @thread_safety It is required that this method be implemented in a threadsafe fashion.
    virtual const bool isNodeDirty_abi(const NodeObj& nodeObj,
                                       kit::exec::core::unstable::IExecutionContext* const executionContext,
                                       const InstanceIndex instanceIndex) noexcept = 0;

    //! Queries whether or not a given @p outputAttributeObj propagates compute requests downstream to all of its
    //! connections if the node (of instance @p instanceIndex) it resides on has been marked dirty and executed.
    //!
    //! This method is invoked during lazy graph execution on nodes that both:
    //! - Implement the IDirtyable interface.
    //! - Have been dirtied and evaluated in the current execution phase.
    //! to help prune entire branches from unnecessary updates if specific output attributes "block" dirty propagation.
    //!
    //! Note that dirty propagation logic/gating defined via this method will be respected regardless of how the node
    //! gets dirtied (i.e. by using @ref omni::graph::core::unstable::isNodeDirty_abi directly, by undergoing an
    //! authored attribute change, or by having its upstream compute status set to true).
    //!
    //! @thread_safety It is required that this method be implemented in a threadsafe fashion.
    virtual const bool isComputeRequestPropagator_abi(const AttributeObj& outputAttributeObj,
                                                      kit::exec::core::unstable::IExecutionContext* const executionContext,
                                                      const InstanceIndex instanceIndex) noexcept = 0;
};

} // namespace unstable
} // namespace core
} // namespace graph
} // namespace omni

// Generated API declaration.
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/core/unstable/IDirtyable.gen.h>

//! @copydoc omni::graph::core::unstable::IDirtyable_abi
class omni::graph::core::unstable::IDirtyable : public omni::core::Generated<omni::graph::core::unstable::IDirtyable_abi>
{
};

// Additional headers needed for API implementation.

// Generated API implementation.
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/core/unstable/IDirtyable.gen.h>
