// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <omni/graph/core/CppWrappers.h>
#include <omni/graph/core/StringUtils.h>
#include <omni/graph/core/IAttributeType.h>
#include <omni/graph/core/IDataModel.h>
#include <omni/kit/PythonInterOpHelper.h>
#include <omni/usd/UsdContext.h>

#include "PrimCommon.h"

using namespace omni::fabric;
using namespace omni::graph::core;

namespace
{
//static const PXR_NS::TfToken kForceWriteBack("ForceWriteBack");
//static const PXR_NS::TfToken kUsdPrim("UsdPrim");
//static const PXR_NS::TfToken kMesh("Mesh");
//static const PXR_NS::TfToken kType("node:type");
//static const PXR_NS::TfToken kTypeVersion("node:typeVersion");
//static const PXR_NS::TfToken kIsTerminalNode("IsTerminalNode");
//static const PXR_NS::TfToken kSourcePrimPath("sourcePrimPath");
//
static const PXR_NS::TfToken kInputsVariableName("inputs:variableName");
static const PXR_NS::TfToken kInputsTargetPath("inputs:targetPath");
static const PXR_NS::TfToken kInputsGraph("inputs:graph");
}


namespace omni
{
namespace anim
{
namespace graph
{


// -----------------------------------------------------------------------------------------
std::tuple<omni::fabric::FabricId, PXR_NS::UsdStageRefPtr> getFabricForNode(const GraphContextObj& graphContext,
                                                                         const NodeObj& nodeObj)
{
    // Find our stage
    long stageId = graphContext.iContext->getStageId(graphContext);
    auto stage = PXR_NS::UsdUtilsStageCache::Get().Find(PXR_NS::UsdStageCache::Id::FromLongInt(stageId));
    if (!stage)
    {
        CARB_LOG_ERROR("Could not find USD stage %ld", stageId);
        return { omni::fabric::kInvalidFabricId, nullptr };
    }
    GraphObj graphObj = nodeObj.iNode->getGraph(nodeObj);
    omni::fabric::FabricId fabricId = omni::fabric::kInvalidFabricId;
    graphObj.iGraph->getFabricId(graphObj, fabricId);

    if (fabricId == omni::fabric::kInvalidFabricId)
    {
        CARB_LOG_ERROR("Could not find Fabric id");
        return { omni::fabric::kInvalidFabricId, nullptr };
    }

    return { fabricId, stage };
}

// -----------------------------------------------------------------------------------------
PXR_NS::SdfPath getRelationshipPrimPath(const GraphContextObj& context,
                                     const NodeObj& nodeObj,
                                     PXR_NS::TfToken primInput,
                                     bool throwOnNoPrimSpecified)
{
    // Read the path from the relationship input on this compute node
    const INode& iNode = *nodeObj.iNode;
    const char* thisPrimPathStr = iNode.getPrimPath(nodeObj);
    long stageId = context.iContext->getStageId(context);
    auto stage = PXR_NS::UsdUtilsStageCache::Get().Find(PXR_NS::UsdStageCache::Id::FromLongInt(stageId));
    const PXR_NS::UsdPrim thisPrim = stage->GetPrimAtPath(PXR_NS::SdfPath(thisPrimPathStr));
    if (!thisPrim.IsValid())
    {
        throw std::runtime_error("Could not find node's prim to read relationships from");
    }

    const PXR_NS::UsdRelationship relationship = thisPrim.GetRelationship(primInput);

    PXR_NS::SdfPathVector paths;
    relationship.GetTargets(&paths);
    if (paths.empty())
    {
        if (throwOnNoPrimSpecified)
            throw std::runtime_error("No input prim specified");
        else
            return PXR_NS::SdfPath::EmptyPath();
    }

    if (paths.size() > 1)
    {
        throw std::runtime_error("More than one input prim specified");
    }

    return paths[0];
}

// -----------------------------------------------------------------------------------------

PXR_NS::UsdAttribute findSelectedVariable(GraphContextObj const& context, NodeObj const& nodeObj, bool isTargetAttr)
{
    // Find our stage
    PXR_NS::UsdStageRefPtr stage;
    omni::fabric::FabricId fabricId;
    std::tie(fabricId, stage) = getFabricForNode(context, nodeObj);
    if (fabricId == omni::fabric::kInvalidFabricId)
        throw std::runtime_error("Internal error");

    // Find the input prim path one of 2 ways
    PXR_NS::SdfPath srcPath;

    ConstAttributeDataHandle constHandle;
    if (isTargetAttr)
    {
        constHandle = getAttributeR(context, nodeObj.nodeContextHandle, asInt(kInputsTargetPath), kAccordingToContextIndex);
        if (!constHandle.isValid())
            throw std::runtime_error(formatString("Attribute %s does not exist", kInputsTargetPath.GetText()));
        char const* srcPrimPathStr = context.iToken->getText(*getDataR<NameToken>(context, constHandle));
        if (!srcPrimPathStr || strlen(srcPrimPathStr) == 0)
        {
            return {};
        }
        srcPath = PXR_NS::SdfPath(srcPrimPathStr);
    }
    else
    {
        srcPath = getRelationshipPrimPath(
            context, nodeObj, kInputsGraph, /*throwOnNoPrimSpecified*/ false); // may throw std::runtime_error
        if (srcPath.IsEmpty())
            return {};


    }

    // Find the source prim and attrib
    constHandle = getAttributeR(context, nodeObj.nodeContextHandle, asInt(kInputsVariableName), kAccordingToContextIndex);
    if (!constHandle.isValid())
        throw std::runtime_error(formatString("Attribute %s does not exist", kInputsVariableName.GetText()));
    NameToken varName{ *getDataR<NameToken>(context, constHandle) };
    char const* varNameStr{ context.iToken->getText(varName) };

    // We expect to have blank variable name attribute when first placed, so this is not an exception
    if (!varNameStr || strlen(varNameStr) == 0)
        return {};

    // Find our graph
    PXR_NS::UsdPrim prim{ stage->GetPrimAtPath(srcPath) };
    if (!prim)
    {
        throw std::runtime_error(formatString("Attribute %s does not exist", srcPath.GetText()));
    }

    // Find our variable attribute
    std::string varAttrNameStr = "anim:graph:variable:";
    varAttrNameStr.append(varNameStr);
    PXR_NS::TfToken varNameToken(varAttrNameStr.c_str());
    PXR_NS::UsdAttribute attrib{ prim.GetAttribute(varNameToken) };
    if (!attrib)
    {
        // Could be that it is just not authored
        auto const foundProperties =
            prim.GetProperties([&varNameToken](PXR_NS::TfToken const& propName) { return propName == varNameToken; });
        if (!foundProperties.empty())
        {
            attrib = foundProperties[0].As<PXR_NS::UsdAttribute>();
        }
        if (!attrib)
            throw std::runtime_error(formatString("Variable Name %s does not exist", varNameStr));
    }
    return attrib;
}

} // graph
} // anim
} // omni
