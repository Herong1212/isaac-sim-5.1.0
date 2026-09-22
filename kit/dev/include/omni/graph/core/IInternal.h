// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include <carb/Interface.h>

#include <omni/graph/core/unstable/IPrivateNodeGraphDef.h>
#include <omni/graph/core/unstable/IPrivateNodeDef.h>
#include <omni/graph/core/Handle.h>

#include <cstddef>

namespace omni
{
namespace graph
{
namespace core
{

/**
 * This class contains functions and member variables that are intended only for internal
 * use by the omni.graph.core extension but which, for technical reasons, we are forced to
 * expose externally.
 *
 * This class is explicitly exempt from the usual rules about deprecation and backwards compatibility.
 * Members may be added, removed, or changed at any time without notice.
 */
struct IInternal
{
    CARB_PLUGIN_INTERFACE("omni::graph::core::IInternal", 1, 3);

    // NOTE: In the Python implementation all methods and members should begin with a single underscore (_)
    //       to further drive home that they are meant for internal use only.

    /**
     * Mark an attribute as deprecated, meaning that it should no longer be used and will be removed in a future version.
     *
     * @param[in] attrObj The attribute being deprecated.
     * @param[in] message Message explaining what users should do to deal with the deprecation.
     */
    void(CARB_ABI* deprecateAttribute)(const AttributeObj& attrObj, const char *message);

    /**
     * Factory method used to create internal generic graph definition wrapping private class
     *
     * @param[in] builder Graph builder requesting this construction
     * @param[in] definitionName The name associated with this definition. Used by the pass pipeline
     * @param[in] graphObj Authoring graph this definition belongs to
     * @param[in] isInstanced Is this graph a graph instance
     */
    unstable::IPrivateNodeGraphDef* (CARB_ABI* createPrivateGraphDef)(
        const GraphObj& graphObj,
        bool isInstanced);

    /**
     * Factory method used to create internal generic node definition wrapping private class
     *
     * @param[in] nodeObj Authoring node this definition belongs to
     */
    unstable::IPrivateNodeDef*(CARB_ABI* createPrivateNodeDef)(const NodeObj& nodeObj);

    /**
     * Factory method used to create internal generic node definition wrapping private class
     * that has specific segment infos
     *
     * @param[in] nodeObj Authoring node this definition belongs to
     * @param[in] segStart The first instance index at which the def refers to (segment start)
     * @param[in] segLen The number of instances in the segment (segment length)
     */
    unstable::IPrivateNodeDef*(CARB_ABI* createPrivateNodeDefWithSegInfo)(const NodeObj& nodeObj,
                                                                          InstanceIndex segStart,
                                                                          size_t segLen);
};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IInternal, createPrivateNodeDefWithSegInfo, 3)

} // namespace core
} // namespace graph
} // namespace omni
