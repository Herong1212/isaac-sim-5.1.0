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
#include <OgnReadPrimAttributeDatabase.h>

#include <omni/fabric/IToken.h>
#include <omni/fabric/usd/PathConversion.h>
#include <omni/graph/core/IAttributeType.h>
#include <omni/graph/core/StringUtils.h>
#include <omni/graph/core/CppWrappers.h>
#include <omni/graph/core/unstable/Dirtyable.h>
#include <omni/kit/exec/core/unstable/IExecutionContext.h>
#include <omni/usd/UsdContext.h>
#include <omni/fabric/FabricUSD.h>

#include <tbb/concurrent_unordered_map.h>

#include "PrimCommon.h"
#include "ReadPrimCommon.h"
#include "CoverageUtils.h"

using namespace omni::fabric;

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{
namespace
{

// This node type implements the IDirtyable ONI.
class DirtyableImpl : public Dirtyable
{
public:
    DirtyableImpl(const char* const nodeTypeName) noexcept : Dirtyable(nodeTypeName)
    {
    }

private:
    const bool isNodeDirty(const NodeObj& nodeObj,
                           kit::exec::core::unstable::IExecutionContext* const executionContext,
                           InstanceIndex instanceIndex) noexcept override
    {
        // Fill the per-node data container if necessary.
        const uint64_t graphInstanceId = nodeObj.iNode->getGraphInstanceID(nodeObj.nodeHandle, instanceIndex).id.token;
        if (m_nodeObjToAttribute.find(nodeObj.nodeHandle) == m_nodeObjToAttribute.end())
        {
            m_nodeObjToAttribute.emplace(
                nodeObj.nodeHandle, tbb::concurrent_unordered_map<uint64_t, std::pair<pxr::SdfPath, pxr::VtValue>>());
        }
        if (m_nodeObjToAttribute.at(nodeObj.nodeHandle).find(graphInstanceId) ==
            m_nodeObjToAttribute.at(nodeObj.nodeHandle).end())
        {
            m_nodeObjToAttribute.at(nodeObj.nodeHandle).emplace(graphInstanceId, std::pair<pxr::SdfPath, pxr::VtValue>());
        }

        // Grab the default graph context object.
        const GraphObj graphObj = nodeObj.iNode->getGraph(nodeObj);
        const GraphContextObj graphContextObj = graphObj.iGraph->getDefaultGraphContext(graphObj);

        // Get the cached attribute path and value.
        pxr::SdfPath& cachedAttributePath = m_nodeObjToAttribute.at(nodeObj.nodeHandle).at(graphInstanceId).first;
        pxr::VtValue& cachedAttributeValue = m_nodeObjToAttribute.at(nodeObj.nodeHandle).at(graphInstanceId).second;

        // Get the current attribute.
        pxr::UsdAttribute currentAttribute;
        try
        {
            currentAttribute = nodes::findSelectedAttribute(graphContextObj, nodeObj, instanceIndex);
        }
        catch (...)
        {
            return false;
        }

        // If both the cached attribute and current attribute are invalid, return false (the state
        // being tracked by this node has not changed, so it does not need to dirty itself and
        // propagate donwstream compute requests).
        if (cachedAttributePath.IsEmpty() && cachedAttributeValue.IsEmpty() && !currentAttribute.IsValid())
        {
            return false;
        }

        // We can quickly determine that the node must be dirtied if one of the following two conditions
        // are met:
        // 1. If the cached attribute is invalid while the current attribute is valid; this usually occurs
        //    when an instance of this node type has its previosuly-unfilled target attribute set to a
        //    concrete value.
        // 2. If the cached attribute is valid while the current attribute is invalid; this usually occurs
        //    when an instance of this node type clears its previously-filled target attribute.
        // In either case, make sure to update the attribute cache before dirtying the node.
        else if ((cachedAttributePath.IsEmpty() && cachedAttributeValue.IsEmpty() && currentAttribute.IsValid()) ||
                 (!cachedAttributePath.IsEmpty() && !cachedAttributeValue.IsEmpty() && !currentAttribute.IsValid()))
        {
            updateCachedAttribute(
                nodeObj, graphContextObj, cachedAttributePath, cachedAttributeValue, currentAttribute, instanceIndex);
            return true;
        }

        // If both the cached attribute and current attribute are valid, more granular checks are required
        // in order to determine if an attribute change has occurred that would necessitate dirtying the node.
        // First check if the current attribute's path is different from the cached attribute path; if they
        // differ, update the attribute cache before dirtying the node.
        const pxr::SdfPath& currentAttributePath = currentAttribute.GetPath();
        if (cachedAttributePath != currentAttributePath)
        {
            updateCachedAttribute(
                nodeObj, graphContextObj, cachedAttributePath, cachedAttributeValue, currentAttribute, instanceIndex);
            return true;
        }

        // Dirty the node if the current attribute's value is different from the cached attribute value. Make sure
        // to update the attribute cache as well.
        pxr::VtValue currentAttributeValue = getAttributeValue(nodeObj, graphContextObj, currentAttribute, instanceIndex);
        if (cachedAttributeValue != currentAttributeValue)
        {
            cachedAttributeValue = currentAttributeValue;

            // Set the reimportAtTime flag to true if necessary; this will be used later during the node's compute() to
            // pull the latest data associated with the attribute being read.
            const pxr::UsdTimeCode* const usdTimeCode = getInputUsdTimeCode(nodeObj, graphContextObj, instanceIndex);
            if (!usdTimeCode->IsDefault())
            {
                const AttributeObj stateReimportAtTimeAttrObj =
                    nodeObj.iNode->getAttribute(nodeObj, state::reimportAtTime.m_name);
                const AttributeDataHandle stateReimportAtTimeDataHandle =
                    stateReimportAtTimeAttrObj.iAttribute->getAttributeDataHandle(
                        stateReimportAtTimeAttrObj, instanceIndex);
                bool* const stateReimportAtTime = getDataW<bool>(graphContextObj, stateReimportAtTimeDataHandle);
                *stateReimportAtTime = true;
            }

            return true;
        }

        return false;
    }

    void clearSharedState(const NodeObj& nodeObj) noexcept override
    {
        (void)m_nodeObjToAttribute.unsafe_erase(nodeObj.nodeHandle);
    }

    void clearPerInstanceState(const NodeObj& nodeObj, const GraphInstanceID& graphInstanceId) noexcept override
    {
        if (m_nodeObjToAttribute.find(nodeObj.nodeHandle) != m_nodeObjToAttribute.end())
        {
            (void)m_nodeObjToAttribute.at(nodeObj.nodeHandle).unsafe_erase(graphInstanceId.id.token);
        }
    }

    // Helper method to get the current node's input USD time code.
    const pxr::UsdTimeCode* const getInputUsdTimeCode(const NodeObj& nodeObj,
                                                      const GraphContextObj graphContextObj,
                                                      const InstanceIndex& instanceIndex) const noexcept
    {
        const AttributeObj usdTimeCodeAttrObj = nodeObj.iNode->getAttribute(nodeObj, "inputs:usdTimecode");
        const ConstAttributeDataHandle usdTimeCodeDataHandle =
            usdTimeCodeAttrObj.iAttribute->getConstAttributeDataHandle(usdTimeCodeAttrObj, instanceIndex);
        return getDataR<pxr::UsdTimeCode>(graphContextObj, usdTimeCodeDataHandle);
    }

    // Helper method to obtain the pxr::VtValue associated with a UsdAttribute.
    pxr::VtValue getAttributeValue(const NodeObj& nodeObj,
                                   const GraphContextObj graphContextObj,
                                   const pxr::UsdAttribute& attribute,
                                   const InstanceIndex& instanceIndex) const noexcept
    {
        pxr::VtValue attributeValue;
        if (!attribute.IsValid())
        {
            return attributeValue;
        }

        const pxr::UsdTimeCode* const usdTimeCode = getInputUsdTimeCode(nodeObj, graphContextObj, instanceIndex);
        usdTimeCode->IsDefault() ? attribute.Get(&attributeValue) : attribute.Get(&attributeValue, *usdTimeCode);
        return attributeValue;
    }

    // Helper method to update the cached UsdAttribute path and value associated with a given ReadPrimAttribute node.
    void updateCachedAttribute(const NodeObj& nodeObj,
                               const GraphContextObj graphContextObj,
                               pxr::SdfPath& cachedAttributePath,
                               pxr::VtValue& cachedAttributeValue,
                               const pxr::UsdAttribute& currentAttribute,
                               const InstanceIndex& instanceIndex) const noexcept
    {
        cachedAttributePath = currentAttribute.GetPath();
        cachedAttributeValue = getAttributeValue(nodeObj, graphContextObj, currentAttribute, instanceIndex);
    }

    // Cache of attribute paths/values for each unique node object (and instance) of type OgnReadPrimAttribute. Note
    // that we store these separately instead of in a single pxr::UsdAttribute object in order to prevent automatic
    // updates to the cached attribute from occurring before we get a chance to dirty the node.
    tbb::concurrent_unordered_map<NodeHandle, tbb::concurrent_unordered_map<uint64_t, std::pair<pxr::SdfPath, pxr::VtValue>>>
        m_nodeObjToAttribute;
};

REGISTER_OGN_NODE_INTERFACE(DirtyableImpl, "omni.graph.nodes.ReadPrimAttribute") // May throw.

} // anonymous namespace
} // namespace unstable
} // namespace core

namespace nodes
{
static thread_local bool recurseGuard{ false };

class OgnReadPrimAttribute
{
    static bool importAtTime(omni::fabric::FabricId fabricId,
                             NodeObj const& nodeObj,
                             pxr::UsdPrim const& prim,
                             TokenC srcName,
                             pxr::SdfTimeCode const& time,
                             OgnReadPrimAttributeDatabase& db,
                             size_t offset)
    {
        CARB_PROFILE_ZONE(1, "ImportAtTime");
        IFabricUsd* iFabricUsd = carb::getCachedInterface<IFabricUsd>();

        // Handle the case where the prim is not yet available
        if (!prim.IsValid())
        {
            CARB_LOG_WARN("Attempted to import time from invalid prim from node '%s' and source '%s'",
                          nodeObj.iNode->getPrimPath(nodeObj), omni::fabric::toTfToken(srcName).GetText());
            return false;
        }

        pxr::SdfPath importPath = prim.GetPath();
        bool force = false;
        if (UsdTimeCode::Default() != time)
        {
            force = true;
            char const* primPath = nodeObj.iNode->getPrimPath(nodeObj);
            static constexpr char const kImportSubPath[] = "/Import";
            std::string storingPath;
            storingPath.reserve(strlen(primPath) + sizeof(kImportSubPath));
            storingPath = primPath;
            storingPath += kImportSubPath;
            importPath = pxr::SdfPath(storingPath);
        }

        {
            CARB_PROFILE_ZONE(1, "ImportUSDToFabric");
            BucketId srcPrimBucketId =
                omni::graph::nodes::addAttribToCache(prim, importPath, srcName, iFabricUsd, fabricId, time, force);

            if (srcPrimBucketId == kInvalidBucketId)
            {
                OgnReadPrimAttributeDatabase::logError(
                    nodeObj, "Unable to add prim %s to fabric", prim.GetPath().GetText());
                return false;
            }
        }

        db.state.time(offset) = time.GetValue();
        db.state.srcPath(offset) = asInt(prim.GetPath()).path;
        db.state.srcPathAsToken(offset) = asInt(prim.GetPath().GetAsToken()).token;
        db.state.importPath(offset) = asInt(importPath).path;
        db.state.srcAttrib(offset) = srcName.token;

        return true;
    }

    static void setup(NodeObj const& nodeObj,
                      GraphContextObj const& context,
                      pxr::SdfTimeCode const& time,
                      OgnReadPrimAttributeDatabase& db,
                      size_t offset,
                      bool isInCompute)
    {
        if (recurseGuard)
            return;

        CARB_PROFILE_ZONE(1, "setup");
        recurseGuard = true;
        std::shared_ptr<nullptr_t> atScopExist(nullptr, [](auto) { recurseGuard = false; });

        auto typeInterface{ carb::getCachedInterface<omni::graph::core::IAttributeType>() };
        InstanceIndex instanceIndex = db.getInstanceIndex() + offset;

        db.state.correctlySetup(offset) = false;

        pxr::UsdAttribute attrib;
        try
        {
            attrib = omni::graph::nodes::findSelectedAttribute(context, nodeObj, instanceIndex);
        }
        catch (std::runtime_error const& error)
        {
            if (isInCompute)
                OgnReadPrimAttributeDatabase::logError(nodeObj, error.what());
            return;
        }
        if (!attrib)
        {
            // Couldn't get the indicated attribute for some expected reason
            if (isInCompute)
                OgnReadPrimAttributeDatabase::logError(nodeObj, "Prim has not been set");
            return;
        }

        auto typeName{ attrib ? attrib.GetTypeName().GetAsToken() : pxr::TfToken() };
        Type attribType{ typeInterface->typeFromSdfTypeName(typeName.GetText()) };
        tryResolveOutputAttribute(nodeObj, outputs::value.m_token, attribType);

        // Get interfaces
        const INode& iNode = *nodeObj.iNode;

        pxr::UsdPrim prim{ attrib.GetPrim() };

        if (!attrib.IsAuthored())
        {
            if (UsdTimeCode::Default() != time)
            {
                CARB_LOG_ERROR("Access a non authored attrib %s:%s with a specific timestamp is not allowed",
                               attrib.GetName().GetText(), prim.GetPath().GetText());
                return;
            }

            // fabric only cares about _authored_ attributes, so in order to make use of fabric mirrored arrays we
            // have to contrive to have values authored, even if we just want to read them.
            //
            // FIXME: OM-36961 exists to work around this issue some other way.
            CARB_LOG_INFO("%s: Attribute %s is not authored, authoring now", iNode.getPrimPath(nodeObj),
                          attrib.GetPath().GetText());

            // --------------------------------------------------------------------------------------
            // Get PrimVar into fabric by creating it on the prim
            if (pxr::UsdGeomPrimvar::IsPrimvar(attrib))
            {
                try
                {
                    addPrimvarToFabric(prim, attrib);
                }
                catch (std::runtime_error const& error)
                {
                    OgnReadPrimAttributeDatabase::logError(nodeObj, error.what());
                    return;
                }
            }
            else
            {
                // --------------------------------------------------------------------------------------
                // Get non-primvar into fabric by authoring the attribute with the composed value
                pxr::VtValue val;
                if (!attrib.Get(&val))
                    val = attrib.GetTypeName().GetDefaultValue();

                if (!attrib.Set(val))
                {
                    OgnReadPrimAttributeDatabase::logError(nodeObj, "Unable to author %s with value of type %s",
                                                           attrib.GetPath().GetText(), val.GetTypeName().c_str());
                    return;
                }
            }
        }

        // Fill Fabric with USD data
        pxr::UsdStageRefPtr stage;
        omni::fabric::FabricId fabricId;
        std::tie(fabricId, stage) = getTargetFabricStage(context);
        FIREWALL_RETURN(fabricId == omni::fabric::kInvalidFabricId); // LCOV_EXCL_LINE

        if (!importAtTime(fabricId, nodeObj, prim, asInt(attrib.GetName()), time, db, offset))
            return;

        // If it's resolved, we already know that it is compatible from the above check of the USD
        AttributeObj outAttrib = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::value.m_token);
        Type outType = outAttrib.iAttribute->getResolvedType(outAttrib);
        if (outType == Type())
        {
            // Not resolved, so we have to resolve it now. This node is strange in that the resolved output type
            // depends on external state instead of other attributes.
            outAttrib.iAttribute->setResolvedType(outAttrib, attribType);
        }

        db.state.correctlySetup(offset) = true;
    }

    /**
     * Adds the given primvar attrib to fabric.At the moment this requires explicit authoring of the value
     * @param prim: The prim which is in FC, but doesn't have the given primvar
     * @param attrib: The primvar attribute for the prim, which has no value
     * @throws: std::runtime_error on failure
     * @
     */
    static void addPrimvarToFabric(pxr::UsdPrim prim, pxr::UsdAttribute& attrib)
    {
        // Primvars have to go through prim var api
        if (auto primVarAPI = pxr::UsdGeomPrimvarsAPI(prim))
        {
            if (pxr::UsdGeomPrimvar primVar = primVarAPI.FindPrimvarWithInheritance(attrib.GetName()))
            {
                if (auto newPrimVar = primVarAPI.CreatePrimvar(attrib.GetName(), primVar.GetTypeName()))
                {
                    if (auto& newAttr = newPrimVar.GetAttr())
                    {
                        // Get the inherited primvar attrib value
                        pxr::VtValue val;
                        if (primVar.Get(&val))
                        {
                            if (!newAttr.Set(val))
                            {
                                throw std::runtime_error(
                                    formatString("Unable to author primvar %s with value of type %s",
                                                 newAttr.GetPath().GetText(), val.GetTypeName().c_str()));
                            }
                        }
                        else
                        {
                            // We don't have any value to copy, so lets use the default
                            auto const& defaultValue = primVar.GetTypeName().GetDefaultValue();
                            if (!newAttr.Set(defaultValue))
                            {
                                throw std::runtime_error(formatString(
                                    "Unable to author primvar %s with default value", newAttr.GetPath().GetText()));
                            }
                        }
                    }
                }
            }
        }
    }

    // ----------------------------------------------------------------------------
    // Called by OG when our prim attrib changes. We want to catch the case of changing the prim attribute interactively
    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        // FIXME: Be pedantic about validity checks - this can be run directly by the TfNotice so who knows
        // when or where this is happening
        NodeObj nodeObj{ attrObj.iAttribute->getNode(attrObj) };
        FIREWALL_RETURN(nodeObj.nodeHandle == kInvalidNodeHandle); // LCOV_EXCL_LINE

        GraphObj graphObj{ nodeObj.iNode->getGraph(nodeObj) };
        FIREWALL_RETURN(graphObj.graphHandle == kInvalidGraphHandle); // LCOV_EXCL_LINE

        // no setup if graph is disabled (during python edition for instance)
        if (graphObj.iGraph->isDisabled(graphObj))
            return;

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        FIREWALL_RETURN(context.contextHandle == kInvalidGraphContextHandle); // LCOV_EXCL_LINE

        OgnReadPrimAttributeDatabase db(nodeObj);
        setup(nodeObj, context, db.state.time(), db, 0, false);
    }

public:
    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        // We need to check resolution if any of our relevant inputs change
        std::array<NameToken, 4> attribNames{ inputs::name.m_token, inputs::usePath.m_token, inputs::primPath.m_token,
                                              inputs::prim.m_token };
        for (auto const& attribName : attribNames)
        {
            AttributeObj attribObj = nodeObj.iNode->getAttributeByToken(nodeObj, attribName);
            attribObj.iAttribute->registerValueChangedCallback(attribObj, onValueChanged, true);
        }
    }

    // ----------------------------------------------------------------------------
    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
        GraphObj graphObj{ nodeObj.iNode->getGraph(nodeObj) };
        FIREWALL_RETURN(graphObj.graphHandle == kInvalidGraphHandle); // LCOV_EXCL_LINE

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        FIREWALL_RETURN(context.contextHandle == kInvalidGraphContextHandle); // LCOV_EXCL_LINE

        OgnReadPrimAttributeDatabase db(nodeObj);
        setup(nodeObj, context, db.state.time(), db, 0, false);
    }

    // ----------------------------------------------------------------------------
    static bool computeVectorized(OgnReadPrimAttributeDatabase& db, size_t count)
    {
        GraphContextObj ctx = db.abi_context();

        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();

        pxr::UsdStageRefPtr stage;
        omni::fabric::FabricId stageFabricId;
        std::tie(stageFabricId, stage) = getTargetFabricStage(ctx);
        FIREWALL_RETURN(stageFabricId == omni::fabric::kInvalidFabricId, false); // LCOV_EXCL_LINE

        GraphObj graphObj = ctx.iContext->getGraph(ctx);
        omni::fabric::FabricId graphFabricId = omni::fabric::kInvalidFabricId;
        graphObj.iGraph->getFabricId(graphObj, graphFabricId);

        //////////////////////////////////////////////////////////////////////////
        // Gather vectorized data
        auto time = db.inputs.usdTimecode.vectorized(count);
        auto usePath = db.inputs.usePath.vectorized(count);
        auto primPath = db.inputs.primPath.vectorized(count);
        auto name = db.inputs.name.vectorized(count);

        auto correctlySetup = db.state.correctlySetup.vectorized(count);
        auto stateTime = db.state.time.vectorized(count);
        auto importPath = db.state.importPath.vectorized(count);
        auto srcPath = db.state.srcPath.vectorized(count);
        auto srcPathAsToken = db.state.srcPathAsToken.vectorized(count);
        auto srcAttrib = db.state.srcAttrib.vectorized(count);
        auto reimportAtTime = db.state.reimportAtTime.vectorized(count);

        // Fast path through ABI when using target
        ConstAttributeDataHandle hdl = db.inputs.prim.abi_handle();
        auto prims = getDataR<PathC const*>(ctx, hdl);
        auto graphReaderWriterId = iStageReaderWriter->createOrGetFromFabricId(graphFabricId);
        size_t const* sizes = iStageReaderWriter->getArrayAttributeSizeRdPtr(graphReaderWriterId, hdl.path(), hdl.name());

        //////////////////////////////////////////////////////////////////////////
        // Make sure setup is correctly performed
        {
            CARB_PROFILE_ZONE(1, "CheckSetup");
            for (size_t idx = 0; idx < count; ++idx)
            {
                if (!correctlySetup[idx])
                {
                    setup(db.abi_node({ idx }), ctx, time[idx], db, idx, true);
                }
                else
                {
                    bool pathOk = false;
                    if (usePath[idx])
                        pathOk = primPath[idx] == srcPathAsToken[idx];
                    else
                        pathOk = sizes[idx] && prims[idx][0] == srcPath[idx];

                    if (!pathOk || name[idx] != srcAttrib[idx])
                        setup(db.abi_node({ idx }), ctx, time[idx], db, idx, true);
                }

                if (correctlySetup[idx] && (UsdTimeCode(time[idx]) != stateTime[idx] || reimportAtTime[idx]))
                {
                    PathC primPathC(srcPath[idx]);
                    auto prim = stage->GetPrimAtPath(toSdfPath(primPathC));
                    correctlySetup[idx] =
                        importAtTime(stageFabricId, db.abi_node({ idx }), prim, name[idx], time[idx], db, idx);
                    reimportAtTime[idx] = false;
                }
            }
        }

        //////////////////////////////////////////////////////////////////////////
        // Do the copy by the data model or by hand if possible

        // for array or GPU attributes, go through the data model to properly handle the copy
        Type const type = db.outputs.value().type();
        bool const useDataModel = type.arrayDepth || ctx.iAttributeData->gpuValid(db.outputs.value().abi_handle(), ctx);

        if (useDataModel)
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                if (correctlySetup[idx])
                {
                    pxr::SdfPath path = toSdfPath((PathC const&)importPath[idx]);
                    pxr::TfToken childNameToken = toTfToken((TokenC const&)srcAttrib[idx]);
                    path = path.AppendProperty(childNameToken);
                    PathC result = asInt(path);

                    ConstAttributeDataHandle const src{ AttrKey{ result, stageFabricId } };
                    db.abi_context().iAttributeData->copyData(db.outputs.value(idx).abi_handle(), ctx, src);
                }
            }
        }
        else
        {
            // gather dst base pointer
            uint8_t* dstData = nullptr;
            size_t stride = 0;
            db.outputs.value().rawData(dstData, stride);

            // retrieve src pointers
            std::vector<void const*> srcData;
            srcData.resize(count);
            {
                CARB_PROFILE_ZONE(1, "Retrieve Pointers");
                auto stageReaderWriterId = iStageReaderWriter->createOrGetFromFabricId(stageFabricId);
                for (size_t idx = 0; idx < count; ++idx)
                {
                    if (correctlySetup[idx])
                    {
                        srcData[idx] =
                            iStageReaderWriter->getAttributeRd(stageReaderWriterId, importPath[idx], srcAttrib[idx]).ptr;
                    }
                    else
                    {
                        srcData[idx] = nullptr;
                    }
                }
            }

            for (size_t idx = 0; idx < count; ++idx)
            {
                if (correctlySetup[idx])
                {
                    void* dst = dstData + idx * stride;
                    if (srcData[idx])
                        memcpy(dst, srcData[idx], stride);
                    else
                        db.logError("computeVectorized attempting to memcpy from nullptr");
                }
            }
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
                return upgradeUsdTimeCodeInput(context, nodeObj);
            }
        }
        return false;
    }
};

REGISTER_OGN_NODE()
} // namespace nodes
} // namespace graph
} // namespace omni
