// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnOnImpulseEventDatabase.h>
#include <omni/graph/action/IActionGraph.h>

#include "ActionNodeCommon.h"

namespace omni
{
namespace graph
{
namespace action
{

class OgnOnImpulseEvent
{
public:
    // ----------------------------------------------------------------------------
    // Called by OG when our state attrib changes.
    static void onValueChanged(const AttributeObj& attrObj, const void* userData)
    {
        // state::enableImpulse has changed, so we need to compute ASAP
        NodeObj nodeObj = attrObj.iAttribute->getNode(attrObj);
        nodeObj.iNode->requestCompute(nodeObj);
    }

    // ----------------------------------------------------------------------------
    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        AttributeObj attribObj = nodeObj.iNode->getAttributeByToken(nodeObj, state::enableImpulse.m_token);
        attribObj.iAttribute->registerValueChangedCallback(attribObj, onValueChanged, true);
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnOnImpulseEventDatabase& db)
    {
        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        bool enableImpulse = db.state.enableImpulse();
        if (enableImpulse)
        {
            auto iActionGraph = getInterface();
            iActionGraph->setExecutionEnabled(outputs::execOut.token(), db.getInstanceIndex());
            db.state.enableImpulse() = false;
        }
        return true;
    }

    // ----------------------------------------------------------------------------
    static bool updateNodeVersion(const GraphContextObj& context, const NodeObj& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            if (oldVersion < 2)
            {
                // We added inputs:onlyPlayback default true - to maintain previous behavior we should set this to false
                const bool val{ false };
                nodeObj.iNode->createAttribute(nodeObj, "inputs:onlyPlayback", Type(BaseDataType::eBool), &val, nullptr,
                                               kAttributePortType_Input, kExtendedAttributeType_Regular, nullptr);
            }
            return true;
        }
        return false;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
