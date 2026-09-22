// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnMultisequenceDatabase.h>
#include <carb/extras/StringUtils.h>
#include <omni/graph/action/IActionGraph.h>


namespace omni
{
namespace graph
{
namespace action
{

class OgnMultisequence
{
public:
    static bool setExecutionEnabled(NodeObj nodeObj, const char* attribName, bool andPushed, InstanceIndex instIndex)
    {
        auto iNode = nodeObj.iNode;
        if (!iNode->getAttributeExists(nodeObj, attribName))
            return false;

        AttributeObj attrObj = iNode->getAttribute(nodeObj, attribName);
        auto iActionGraph = getInterface();
        if (andPushed)
            iActionGraph->setExecutionEnabledAndPushed(attrObj.iAttribute->getNameToken(attrObj), instIndex);
        else
            iActionGraph->setExecutionEnabled(attrObj.iAttribute->getNameToken(attrObj), instIndex);
        return true;
    }

    // Which branch we should take next
    uint32_t m_nextOutput{ 0 };

    static bool compute(OgnMultisequenceDatabase& db)
    {
        auto iActionGraph = getInterface();
        OgnMultisequence& state = db.perInstanceState<OgnMultisequence>();
        NodeObj nodeObj = db.abi_node();

        if (iActionGraph->getExecutionEnabled(inputs::execIn.token(), db.getInstanceIndex()))
            state.m_nextOutput = 0;

        // Set the execution values
        uint32_t executionIndex = 0;

        // lots of room to append digits to the output name
        std::array<char, 32> outputName;

        auto formatAttrName = [&outputName](uint32_t n)
        { carb::extras::formatString(outputName.data(), outputName.size(), "outputs:output%d", n); };

        for (uint32_t i = 0;; ++i)
        {
            formatAttrName(i);
            if (i == state.m_nextOutput && setExecutionEnabled(nodeObj, outputName.data(), true, db.getInstanceIndex()))
            {
                executionIndex = i;
            }
            else if (i != state.m_nextOutput && nodeObj.iNode->getAttributeExists(nodeObj, outputName.data()))
            {
                // keep looping while we are matching attributes (shouldn't be any holes in the sequence)
            }
            else
            {
                // Check for end of sequence
                if (executionIndex == i - 1)
                {
                    formatAttrName(executionIndex);
                    setExecutionEnabled(nodeObj, outputName.data(), false, db.getInstanceIndex());
                    state.m_nextOutput = 0;
                }
                else
                {
                    ++state.m_nextOutput;
                }
                break;
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
