// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnMultigateDatabase.h>
#include <carb/extras/StringUtils.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnMultigate
{
public:
    // The output that will be activated on the next compute.
    uint32_t m_nextLevel{ 0 };

    static bool setExecutionEnabled(NodeObj nodeObj, const char* attribName, InstanceIndex instIndex)
    {
        auto iNode = nodeObj.iNode;
        if (!iNode->getAttributeExists(nodeObj, attribName))
            return false;

        AttributeObj attrObj = iNode->getAttribute(nodeObj, attribName);
        auto iActionGraph = getInterface();
        iActionGraph->setExecutionEnabled(attrObj.iAttribute->getNameToken(attrObj), instIndex);
        return true;
    }

    static bool compute(OgnMultigateDatabase& db)
    {
        OgnMultigate& state = db.perInstanceState<OgnMultigate>();
        NodeObj nodeObj = db.abi_node();

        if (getInterface()->getExecutionEnabled(inputs::reset.token(), db.getInstanceIndex()))
        {
            state.m_nextLevel = 0;
            return true;
        }

        bool hasSetExecution = false;

        // Set the execution values

        // lots of room to append digits to the output name
        std::array<char, 32> outputName;

        auto formatAttrName = [&outputName](uint32_t n)
        { carb::extras::formatString(outputName.data(), outputName.size(), "outputs:output%d", n); };

        for (uint32_t i = 0;; i++)
        {
            formatAttrName(i);
            if (i == state.m_nextLevel && setExecutionEnabled(nodeObj, outputName.data(), db.getInstanceIndex()))
            {
                hasSetExecution = true;
            }
            else if (i != state.m_nextLevel && nodeObj.iNode->getAttributeExists(nodeObj, outputName.data()))
            {
                // keep looping while we are matching attributes (shouldn't be any holes in the sequence)
            }
            else
            {
                // Failure
                if (!hasSetExecution)
                {
                    // We haven't found the desired output, so we'll reset to 0
                    formatAttrName(0);
                    setExecutionEnabled(nodeObj, outputName.data(), db.getInstanceIndex());
                    state.m_nextLevel = 0;
                }
                break;
            }
        }
        state.m_nextLevel += 1;
        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
