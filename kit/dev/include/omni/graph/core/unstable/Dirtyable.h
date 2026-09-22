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
//! @brief Defines @ref omni::graph::core::unstable::Dirtyable.
#pragma once

#include <omni/graph/core/Handle.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/unstable/IDirtyable.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

//! Core Dirtyable implementation for @ref omni::graph::core::unstable::IDirtyable
//!
//! See @ref omni::graph::core::unstable::IDirtyable for documentation on this type.
class Dirtyable : public exec::unstable::Implements<IDirtyable>
{
protected:
    explicit Dirtyable(const char* const nodeTypeName) noexcept : m_nodeTypeName(nodeTypeName){};

    virtual const bool isNodeDirty(const NodeObj& nodeObj,
                                   kit::exec::core::unstable::IExecutionContext* const executionContext,
                                   const InstanceIndex instanceIndex) noexcept
    {
        return false;
    }

    virtual const bool isComputeRequestPropagator(const AttributeObj& outputAttributeObj,
                                                  kit::exec::core::unstable::IExecutionContext* const executionContext,
                                                  const InstanceIndex instanceIndex) noexcept
    {
        return true;
    }

    virtual void clearSharedState(const NodeObj& nodeObj) noexcept {};

    virtual void clearPerInstanceState(const NodeObj& nodeObj, const GraphInstanceID& graphInstanceId) noexcept {};

private:
    const bool isNodeDirty_abi(const NodeObj& nodeObj,
                               kit::exec::core::unstable::IExecutionContext* const executionContext,
                               const InstanceIndex instanceIndex) noexcept override
    {
        const std::string nodeTypeName = nodeObj.iNode->getNodeTypeObj(nodeObj).iNodeType->getNodeType();
        if (nodeTypeName != m_nodeTypeName)
        {
            CARB_LOG_ERROR(
                "Node type mismatch; input node has type \"%s\", while this "
                "instance of the IDirtyable interface was registered against "
                "a node type of \"%s\".",
                nodeTypeName.c_str(), m_nodeTypeName.c_str());
            return false;
        }

        return isNodeDirty(nodeObj, executionContext, instanceIndex);
    }

    const bool isComputeRequestPropagator_abi(const AttributeObj& outputAttributeObj,
                                              kit::exec::core::unstable::IExecutionContext* const executionContext,
                                              const InstanceIndex instanceIndex) noexcept override
    {
        const NodeObj& nodeObj = outputAttributeObj.iAttribute->getNode(outputAttributeObj);
        const std::string nodeTypeName = nodeObj.iNode->getNodeTypeObj(nodeObj).iNodeType->getNodeType();
        if (nodeTypeName != m_nodeTypeName)
        {
            CARB_LOG_ERROR(
                "Node type mismatch; input node has type \"%s\", while this "
                "instance of the IDirtyable interface was registered against "
                "a node type of \"%s\".",
                nodeTypeName.c_str(), m_nodeTypeName.c_str());
            return true;
        }

        return isComputeRequestPropagator(outputAttributeObj, executionContext, instanceIndex);
    }

    void clearSharedState_abi(const NodeObj& nodeObj) noexcept override
    {
        const std::string nodeTypeName = nodeObj.iNode->getNodeTypeObj(nodeObj).iNodeType->getNodeType();
        if (nodeTypeName != m_nodeTypeName)
        {
            CARB_LOG_ERROR(
                "Node type mismatch; input node has type \"%s\", while this "
                "instance of the IDirtyable interface was registered against "
                "a node type of \"%s\".",
                nodeTypeName.c_str(), m_nodeTypeName.c_str());
            return;
        }

        clearSharedState(nodeObj);
    }

    void clearPerInstanceState_abi(const NodeObj& nodeObj, const GraphInstanceID& graphInstanceId) noexcept override
    {
        const std::string nodeTypeName = nodeObj.iNode->getNodeTypeObj(nodeObj).iNodeType->getNodeType();
        if (nodeTypeName != m_nodeTypeName)
        {
            CARB_LOG_ERROR(
                "Node type mismatch; input node has type \"%s\", while this "
                "instance of the IDirtyable interface was registered against "
                "a node type of \"%s\".",
                nodeTypeName.c_str(), m_nodeTypeName.c_str());
            return;
        }

        clearPerInstanceState(nodeObj, graphInstanceId);
    }

    std::string m_nodeTypeName;
};

} // namespace unstable
} // namespace core
} // namespace graph
} // namespace omni
