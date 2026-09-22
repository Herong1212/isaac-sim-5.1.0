// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file IActionGraphNodes.h
//!
//! @brief Defines @ref omni::graph::action::unstable::IActionGraphNodes_abi
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
namespace unstable
{

OMNI_DECLARE_INTERFACE(IActionGraphNodes);

//! Used to declare a node type for special handling
enum class NodeTypeSpecialBehavior
{
    eDefault,   //< No special behavior
    eOnClosing, //< Nodes triggers immediately before the graph is closed
    eOnLoaded   //< Nodes triggers after the graph has loaded
};


class IActionGraphNodes_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.action.unstable.IActionGraphNodes")>
{
protected:
    /**
     * @brief Register a special behavior for the given node type. This is a low-level feature that should not
     * normally be necessary to use.
     *
     * @param[in] nodeTypeName Name of the node type
     */
    virtual OMNI_ATTR("no_py") void
        setNodeTypeSpecialBehavior_abi(OMNI_ATTR("c_str, in") const char* nodeTypeName,
            NodeTypeSpecialBehavior behaviorType) noexcept = 0;
};

} // namespace unstable
} // namespace action
} // namespace graph
} // namespace omni

#include "IActionGraphNodes.gen.h"
