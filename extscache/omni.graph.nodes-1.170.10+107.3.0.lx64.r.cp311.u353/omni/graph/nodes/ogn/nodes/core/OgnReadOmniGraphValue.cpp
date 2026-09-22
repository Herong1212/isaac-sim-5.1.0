// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <OgnReadOmniGraphValueDatabase.h>

#include <omni/graph/core/IAttributeType.h>
#include <omni/graph/core/StringUtils.h>
#include <omni/graph/core/CppWrappers.h>
#include <omni/usd/UsdContext.h>

#include "PrimCommon.h"
#include "CoverageUtils.h"

using namespace omni::fabric;

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnReadOmniGraphValue
{
    // ----------------------------------------------------------------------------
    // Called by OG when our queried attrib changes. We want to catch the case of changing the queried attribute
    // interactively
    static void onValueChanged(const AttributeObj& attrObj, void const* userData)
    {
        onConnectionTypeResolve(attrObj.iAttribute->getNode(attrObj));
    }

public:
    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        // We need to check resolution if any of our relevant inputs change
        std::array<NameToken, 2> attribNames{ inputs::path.token(), inputs::name.token() };
        for (auto const& attribName : attribNames)
        {
            AttributeObj attribObj = nodeObj.iNode->getAttributeByToken(nodeObj, attribName);
            attribObj.iAttribute->registerValueChangedCallback(attribObj, onValueChanged, true);
        }
    }

    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
        // FIXME: Be pedantic about validity checks - this can be run directly by the TfNotice so who knows
        // when or where this is happening
        GraphObj graphObj{ nodeObj.iNode->getGraph(nodeObj) };
        FIREWALL_RETURN(graphObj.graphHandle == kInvalidGraphHandle); // LCOV_EXCL_LINE

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        FIREWALL_RETURN(context.contextHandle == kInvalidGraphContextHandle); // LCOV_EXCL_LINE

        // reasoning on the "current" instance
        const auto instIdx = kAccordingToContextIndex;

        // Get the queried attribute path
        ConstAttributeDataHandle constHandle =
            getAttributeR(context, nodeObj.nodeContextHandle, inputs::path.token(), instIdx);
        FIREWALL_RETURN(!constHandle.isValid()); // LCOV_EXCL_LINE

        const char* pathCStr = *getDataR<const char*>(context, constHandle);
        if (!pathCStr)
            return;
        std::string pathStr(pathCStr, getElementCount(context, constHandle));
        if (pathStr == "")
            return;
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
        auto path = pathInterface->getHandle(std::string(pathStr).c_str());

        // Get the queried attribute name
        constHandle = getAttributeR(context, nodeObj.nodeContextHandle, inputs::name.token(), instIdx);
        if (!constHandle.isValid())
            return;
        NameToken attributeName = *getDataR<NameToken>(context, constHandle);
        const char* attributeNameStr = context.iToken->getText(attributeName);
        if (!attributeNameStr || strlen(attributeNameStr) == 0)
            return;

        // Get the queried attribute
        ConstAttributeDataHandle inputDataHandle;
        NodeObj inputNodeObj = graphObj.iGraph->getNode(graphObj, std::string(pathStr).c_str());
        if (inputNodeObj.nodeHandle != kInvalidNodeHandle)
        {
            // node
            AttributeObj inputAttrib = inputNodeObj.iNode->getAttributeByToken(inputNodeObj, attributeName);
            if (!inputAttrib.iAttribute->isValid(inputAttrib))
                return;
            inputDataHandle = inputAttrib.iAttribute->getConstAttributeDataHandle(inputAttrib, instIdx);
        }
        else
        {
            // bundle
            ConstBundleHandle attributeHandle(path.path);
            if (!attributeHandle.isValid())
                return;
            const Token attrName(attributeName);
            inputDataHandle = getAttributeR(context, attributeHandle, attrName);
        }
        if (!inputDataHandle.isValid())
            return;

        // Try resolve output
        Type attribType = context.iAttributeData->getType(context, inputDataHandle);
        tryResolveOutputAttribute(nodeObj, outputs::value.token(), attribType);
    }

    static bool compute(OgnReadOmniGraphValueDatabase& db)
    {
        // Get interfaces
        auto& nodeObj = db.abi_node();
        const GraphContextObj context = db.abi_context();
        GraphObj graph = nodeObj.iNode->getGraph(nodeObj);
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();

        // Get queried attribute path
        auto const& pathStr = db.inputs.path();
        if (pathStr.empty())
        {
            return false;
        }
        auto path = pathInterface->getHandle(std::string(pathStr).c_str());

        // Get queried attribute name
        NameToken attributeName = db.inputs.name();
        const char* attributeNameStr = db.tokenToString(attributeName);
        if (std::string(attributeNameStr) == "")
        {
            db.logWarning("Attribute path is set, but name is empty");
            return false;
        }

        // Get queried attribute
        ConstAttributeDataHandle inputDataHandle;
        NodeObj inputNodeObj = graph.iGraph->getNode(graph, std::string(pathStr).c_str());
        if (inputNodeObj.nodeHandle != kInvalidNodeHandle)
        {
            // node
            AttributeObj inputAttrib = inputNodeObj.iNode->getAttributeByToken(inputNodeObj, attributeName);
            if (inputAttrib.iAttribute->isValid(inputAttrib))
            {
                inputDataHandle = inputAttrib.iAttribute->getConstAttributeDataHandle(inputAttrib, db.getInstanceIndex());
            }
        }
        else
        {
            // bundle
            ConstBundleHandle attributeHandle(path.path);
            if (!attributeHandle.isValid())
            {
                return false;
            }
            const Token attrName(attributeNameStr);
            inputDataHandle = getAttributeR(context, attributeHandle, attrName);
        }
        if (!inputDataHandle.isValid())
        {
            db.logWarning(
                "Attribute \"%s.%s\" can't be found in Fabric", ((std::string)pathStr).c_str(), attributeNameStr);
            return false;
        }

        Type attribType = context.iAttributeData->getType(context, inputDataHandle);

        // Determine if the output attribute has already been resolved to an incompatible type
        if (db.outputs.value().resolved())
        {
            Type outType = db.outputs.value().type();
            if (!attribType.compatibleRawData(outType))
            {
                db.logError("%s is not compatible with type %s, please disconnect to change source attrib",
                            attributeNameStr, getOgnTypeName(db.outputs.value().type()).c_str());
                return false;
            }
        }

        // If it's resolved, we already know that it is compatible from the above check of the USD. This
        // should never happen because of onConnectionTypeResolve
        AttributeObj outAttrib = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::value.m_token);
        if (!db.outputs.value().resolved())
        {
            /* LCOV_EXCL_START */
            outAttrib.iAttribute->setResolvedType(outAttrib, attribType);
            db.outputs.value().reset(
                context, outAttrib.iAttribute->getAttributeDataHandle(outAttrib, db.getInstanceIndex()), outAttrib);
            /* LCOV_EXCL_STOP*/
        }

        // Copy queried attribute value to node's output
        AttributeDataHandle outDataHandle =
            outAttrib.iAttribute->getAttributeDataHandle(outAttrib, db.getInstanceIndex());
        context.iAttributeData->copyData(outDataHandle, context, inputDataHandle);

        return true;
    }
};

REGISTER_OGN_NODE()
} // namespace nodes
} // namespace graph
} // namespace omni
