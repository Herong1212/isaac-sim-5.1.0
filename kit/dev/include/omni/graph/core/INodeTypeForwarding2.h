// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// This file contains the definition of the INodeTypeForwarding2 ONI class, the stable and supported version of
// the unstable::INodeTypeForwarding class.

#include <omni/core/Omni.h>
#include <omni/core/IObject.h>
#include <omni/inspect/IInspector.h>
// Surround the include with a temporary define to prevent the deprecation warning, which does not apply here
#define INODE_TYPE_FORWARDING_STABLE
#include <omni/graph/core/unstable/INodeTypeForwarding.h>
#undef INODE_TYPE_FORWARDING_STABLE

namespace omni {
namespace graph {
namespace core {

OMNI_DECLARE_INTERFACE(INodeTypeForwarding2);

/**
 * @brief Interface that creates a forward on a request for a node type to a different node type
 *
 * There are a couple of different common use cases for needing a forward:
 * - Node type gets renamed
 * - Node type moves from one extension to another
 *
 * The node type forward specifies the unique node type name so if extension omni.my.extension has a node whose type
 * is specified as "MyNode" then the forward must be from "omni.my.extension.MyNode".
 *
 * The forwarding is version-based as well, where the version is a minimum number required for forwarding, the usual
 * node version update mechanism not withstanding. For example, if you set up a forward from "omni.nodes.MyNode" version
 * 2 to "omni.my_nodes.MyNode" version 3 then any larger version number is forwarded to the same location:
 * - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3)
 * - omni.nodes.MyNode(3) -> omni.my_nodes.MyNode(3)
 * - omni.nodes.MyNode(4) -> omni.my_nodes.MyNode(3)
 *
 * The forwards can also have multiple versions forwarding to different locations, so if on top of the above forward
 * you also add a forward from "omni.nodes.MyNode" version 3 to "omni.new_nodes.MyNode" version 4 then these become
 * the example forward locations:
 * - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3)
 * - omni.nodes.MyNode(3) -> omni.new_nodes.MyNode(4)
 * - omni.nodes.MyNode(4) -> omni.new_nodes.MyNode(4)
 *
 * Version numbers lower than the first forward are left as-is
 * - omni.nodes.MyNode(1) -> omni.nodes.MyNode(1)
 *
 * @note The usual mechanism of calling updateVersionNumber on a node is only applied after a forward so in the above
 *       cases requesting omni.nodes.MyNode(2) does not call updateVersionNumber(1,2) on your omni.nodes.MyNode
 *       implementation.
 *
 * Node type forwards are associative, so if A forwards to B and B forwards to C then when you request A you get C.
 * Adding a new forward from omni.my_nodes.MyNode(3) to omni.new_nodes.MyNode(2) above yields this forwarding:
 * - omni.nodes.MyNode(2) -> omni.my_nodes.MyNode(3) -> omni.new_nodes.MyNode(2)
 * - omni.nodes.MyNode(3) -> omni.new_nodes.MyNode(4)
 * - omni.nodes.MyNode(4) -> omni.new_nodes.MyNode(4)
 */
class INodeTypeForwarding2_abi
    : public omni::core::Inherits<unstable::INodeTypeForwarding, OMNI_TYPE_ID("omni.graph.core.INodeTypeForwarding2")>
{
protected:
    /**
     * Runs the inspector on the scheduling hints.
     *
     * @param[in] inspector The inspector class
     * @return true if the inspection ran successfully, false if the inspection type is not supported
     */
    virtual bool inspect_abi(OMNI_ATTR("not_null") omni::inspect::IInspector* inspector) noexcept = 0;
};

} // namespace core
} // namespace graph
} // namespace omni

#include "INodeTypeForwarding2.gen.h"
