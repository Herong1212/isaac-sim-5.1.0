// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file IActionGraph.h
//!
//! @brief Defines @ref omni::graph::action::IActionGraph_abi
#pragma once

#include <omni/core/IObject.h>
#include <omni/core/Omni.h>
#include <omni/graph/core/iComputeGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

//! Declare the IActionGraph interface definition
OMNI_DECLARE_INTERFACE(IActionGraph);

/**
 * @brief Functions for implementing nodes which are used in `Action Graph`.
 *
 * Nodes in `Action Graph` have special functionality which is not present in other graph types.
 */
class IActionGraph_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.action.IActionGraph")>
{
protected:
    /**
     * @brief Indicate that the given output attribute should be enabled, so that execution flow should continue
     * along downstream networks.
     *
     * @note This should only be called from within a node @c compute function.
     *
     * @param[in] attributeName attribute on the current node to be set
     * @param[in] instanceIdx In vectorized context, the instance index relative to the currently targeted graph
     *
     * @return Success if executed successfully
     */
    virtual OMNI_ATTR("no_py") omni::core::Result
        setExecutionEnabled_abi(omni::graph::core::NameToken attributeName,
                                omni::graph::core::InstanceIndex instanceIdx) noexcept = 0;

    /**
     * @brief  Indicate that the given output attribute should be enabled, and the current node should be pushed to the
     * execution @c stack. This means that when the downstream execution flow has completed, this node will be
     * @c popped from the execution stack and its @c compute function will be called again.
     *
     * @note This should only be called from within a node @c compute function.
     *
     * @param[in] attributeName attribute on the current node to be set
     * @param[in] instanceIdx In vectorized context, the instance index relative to the currently targeted graph
     *
     * @return Success if executed successfully
     */
    virtual OMNI_ATTR("no_py") omni::core::Result
        setExecutionEnabledAndPushed_abi(omni::graph::core::NameToken attributeName,
                                         omni::graph::core::InstanceIndex instanceIdx) noexcept = 0;
    /**
     * @brief Indicate that the current execution flow should be blocked at the given node, and the node should be
     * @c ticked every update of the Graph (@c compute function called), until it calls \ref endLatentState_abi.
     *
     * @note This should only be called from within a node @c compute function.
     *
     * @param[in] instanceIdx In vectorized context, the instance index relative to the currently targeted graph
     *
     * @return Success if executed successfully
     */
    virtual OMNI_ATTR("no_py") omni::core::Result
        startLatentState_abi(omni::graph::core::InstanceIndex instanceIdx) noexcept = 0;

    /**
     * @brief Indicate that the current execution flow should be un-blocked at the given node, if it is currently in a
     * latent state. It is an error to call this function before calling \ref startLatentState_abi.
     *
     * @note This should only be called from within a node @c compute function.
     *
     * @param[in] instanceIdx In vectorized context, the instance index relative to the currently targeted graph
     *
     * @return Success if executed successfully
     */
    virtual OMNI_ATTR("no_py") omni::core::Result
        endLatentState_abi(omni::graph::core::InstanceIndex instanceIdx) noexcept = 0;

    /**
     * @brief Read the current latent state of the node. This state is set using \ref startLatentState_abi and \ref endLatentState_abi
     *
     * @note This should only be called from within a node @c compute function.
     *
     * @param[in] instanceIdx In vectorized context, the instance index relative to the currently targeted graph
     * @returns true if the node is currently in a latent state
     *
     * @return false if the node is not in a latent state, or the call failed
     */
    virtual OMNI_ATTR("no_py") bool
        getLatentState_abi(omni::graph::core::InstanceIndex instanceIdx) noexcept = 0;

    /**
     * @brief Read the enabled state of an input execution attribute. An input attribute is considered enabled if it is
     * connected to the upstream node that was computed immediately prior to the currently computing node. Event nodes
     * and nodes in latent state may not have any enabled input.
     *
     * @note This should only be called from within a node @c compute function.
     *
     * @param[in] attributeName attribute on the current node to be set
     * @param[in] instanceIdx In vectorized context, the instance index relative to the currently targeted graph
     * @returns true if the given attribute is considered enabled.
     *
     * @return false if the attribute is considered disabled or the call failed
     */
    virtual OMNI_ATTR("no_py") bool
        getExecutionEnabled_abi(omni::graph::core::NameToken attributeName,
                                omni::graph::core::InstanceIndex instanceIdx) noexcept = 0;
};

//! Access the IActionGraph interface. This is more efficient than creating an instance each time it is needed.
//!
//! The returned pointer is a singleton managed by *omni.graph.action_core*, and does *not* have @ref
//! omni::core::IObject::acquire() called on it before being returned.  The caller should *not* call @ref
//! omni::core::IObject::release() on the returned raw pointer.
//!
//! @thread_safety This method is thread safe.
inline IActionGraph* getInterface() noexcept;

} // namespace action
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "IActionGraph.gen.h"

// additional headers needed for API implementation
#include <omni/core/ITypeFactory.h>

inline omni::graph::action::IActionGraph* omni::graph::action::getInterface() noexcept
{
    // createType() always calls acquire() and returns an ObjectPtr to make sure release() is called. we don't want to
    // hold a ref here to avoid static destruction issues. here we allow the returned ObjectPtr to destruct (after
    // calling get()) to release our ref. we know the DLL in which the singleton was created is maintaining a ref and
    // will keep the singleton alive for the lifetime of the DLL.
    static auto sSingleton = omni::core::createType<omni::graph::action::IActionGraph>().get();
    return sSingleton;
}

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "IActionGraph.gen.h"
