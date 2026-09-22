// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnSwitchTokenDatabase.h>
#include <carb/dictionary/DictionaryUtils.h>
#include <carb/dictionary/IDictionary.h>
#include <carb/events/EventsUtils.h>
#include <carb/extras/StringUtils.h>
#include <cstring>
#include <omni/graph/action/IActionGraph.h>

static constexpr size_t kMaxAttrNameLen{ 17 };
static constexpr char k3Dots[] = "...";

namespace omni
{
namespace graph
{
namespace action
{

using namespace omni::fabric;
using namespace carb::events;

class OgnSwitchToken
{
    carb::ObjectPtr<ISubscription> m_nodeChangedSub;

    // ----------------------------------------------------------------------------
    static AttributeObj getCorrespondingOutputAttrib(NodeObj nodeObj, char const* branchName)
    {
        char buffer[32];
        char const* suffix = branchName + std::strlen("inputs:branch");
        (void)carb::extras::formatString(buffer, sizeof(buffer), "outputs:output%s", suffix);
        AttributeObj outputAttrObj = nodeObj.iNode->getAttribute(nodeObj, buffer);
        if (!outputAttrObj.isValid())
            throw std::runtime_error(formatString("Could not find attribute %s", buffer));
        return outputAttrObj;
    }

    // ----------------------------------------------------------------------------
    // Return a shorter version of the given string with ... in the middle
    static std::array<char, kMaxAttrNameLen + 1> ellipsisStr(char const* val, size_t valLen)
    {
        constexpr size_t snipSize{ (kMaxAttrNameLen - 3 / 2) };
        std::array<char, kMaxAttrNameLen + 1> uiLabel{};
        auto writeIter = std::copy(val, val + snipSize, uiLabel.begin());
        writeIter = std::copy(k3Dots, k3Dots + 3, writeIter);
        std::copy(val + valLen - snipSize, val + valLen, writeIter);
        return uiLabel;
    }

    // ----------------------------------------------------------------------------
    static void onValueChanged(const AttributeObj& attrObj, const void* userData)
    {
        // Get the new value
        NodeObj nodeObj = attrObj.iAttribute->getNode(attrObj);
        if (nodeObj.nodeHandle == kInvalidNodeHandle)
            return;

        auto graphObj = nodeObj.iNode->getGraph(nodeObj);
        if (!graphObj.isValid())
            return;

        auto context = graphObj.iGraph->getDefaultGraphContext(graphObj);
        if (!context.isValid())
            return;

        std::string name = attrObj.iAttribute->getName(attrObj);
        if (name.size() < 14)
            return;

        auto const* pBranchVal = getDataR<NameToken>(
            context, attrObj.iAttribute->getConstAttributeDataHandle(attrObj, kAccordingToContextIndex));
        if (!pBranchVal)
            return;

        Token branchTok{ *pBranchVal };

        if (!branchTok.size())
            return;

        // Set metadata on corresponding output attrib
        try
        {
            AttributeObj outputAttrObj = getCorrespondingOutputAttrib(nodeObj, name.c_str());
            char const* branchVal = branchTok.getText();
            size_t const branchValLen = strlen(branchVal);
            if (branchValLen > kMaxAttrNameLen)
            {
                // Too long - instead use middle-ellipsis
                auto uiLabel = ellipsisStr(branchVal, branchValLen);
                outputAttrObj.iAttribute->setMetadata(outputAttrObj, kOgnMetadataUiName, uiLabel.data());
            }
            else
                outputAttrObj.iAttribute->setMetadata(outputAttrObj, kOgnMetadataUiName, branchTok.getText());
        }
        catch (std::exception const& ex)
        {
            nodeObj.iNode->logComputeMessageOnInstance(nodeObj, kAuthoringGraphIndex, ogn::Severity::eError, ex.what());
        }
    }

public:
    // ----------------------------------------------------------------------------
    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        auto& state = OgnSwitchTokenDatabase::sSharedState<OgnSwitchToken>(nodeObj);
        // Callback anytime an attribute is added to this node so we can monitor value changed
        state.m_nodeChangedSub = carb::events::createSubscriptionToPop(
            nodeObj.iNode->getEventStream(nodeObj).get(),
            [nodeObj](carb::events::IEvent* e)
            {
                switch (static_cast<INodeEvent>(e->type))
                {
                case INodeEvent::eCreateAttribute:
                {
                    carb::dictionary::IDictionary* iDict = carb::dictionary::getCachedDictionaryInterface();
                    auto name = iDict->get<char const*>(e->payload, "attribute");
                    if (name && std::strstr(name, "inputs:branch") == name)
                    {
                        AttributeObj attribObj = nodeObj.iNode->getAttribute(nodeObj, name);
                        if (attribObj.isValid())
                        {
                            attribObj.iAttribute->registerValueChangedCallback(attribObj, onValueChanged, false);
                        }
                    }
                }
                default:
                    break;
                }
            });

        // Hook up all the existing attributes to value changed callback
        size_t nAttribs = nodeObj.iNode->getAttributeCount(nodeObj);
        if (!nAttribs)
            return;
        std::vector<AttributeObj> allAttribs;
        allAttribs.resize(nAttribs);
        nodeObj.iNode->getAttributes(nodeObj, allAttribs.data(), nAttribs);

        for (auto& attribObj : allAttribs)
        {
            char const* name = attribObj.iAttribute->getName(attribObj);
            if (name && std::strstr(name, "inputs:branch") == name)
            {
                attribObj.iAttribute->registerValueChangedCallback(attribObj, onValueChanged, false);
            }
        }
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnSwitchTokenDatabase& db)
    {
        NodeObj nodeObj = db.abi_node();
        GraphContextObj context = db.abi_context();

        NameToken const value = db.inputs.value();

        // Check which branch matches the input value
        size_t nAttribs = nodeObj.iNode->getAttributeCount(nodeObj);
        if (!nAttribs)
            return false;
        std::vector<AttributeObj> allAttribs;
        allAttribs.resize(nAttribs);
        nodeObj.iNode->getAttributes(nodeObj, allAttribs.data(), nAttribs);

        for (auto& attribObj : allAttribs)
        {
            char const* name = attribObj.iAttribute->getName(attribObj);
            if (name && std::strstr(name, "inputs:branch") == name)
            {
                auto const* pBranchVal = getDataR<NameToken>(
                    context, attribObj.iAttribute->getConstAttributeDataHandle(attribObj, db.getInstanceIndex()));
                if (value == *pBranchVal)
                {
                    try
                    {
                        AttributeObj outputAttrObj = getCorrespondingOutputAttrib(nodeObj, name);
                        auto iActionGraph = getInterface();
                        iActionGraph->setExecutionEnabled(
                            outputAttrObj.iAttribute->getNameToken(outputAttrObj), db.getInstanceIndex());
                    }
                    catch (std::exception const& ex)
                    {
                        db.logError(ex.what());
                        return false;
                    }
                    break;
                }
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
