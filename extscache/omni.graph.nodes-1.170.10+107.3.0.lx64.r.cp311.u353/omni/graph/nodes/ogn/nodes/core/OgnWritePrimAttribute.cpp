// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "UsdPCH.h"
// clang-format on

#include <memory>

#include "PrimCommon.h"
#include "CoverageUtils.h"
#include "LayerIdentifierResolver.h"

#include <omni/fabric/FabricUSD.h>
#include <omni/fabric/usd/PathConversion.h>
#include <omni/usd/UsdContext.h>

#include <OgnWritePrimAttributeDatabase.h>

using namespace omni::fabric;

namespace omni
{
namespace graph
{
namespace nodes
{

// WARNING!
// The following code uses low-level ABI functionality and should not be copied for other purposes when such
// low level access is not required. Please use the OGN-generated API whenever possible.

static const pxr::TfType s_tokenTfType = pxr::SdfValueTypeNames->Token.GetType();
static const TypeC s_tokenType = TypeC(Type(BaseDataType::eToken));
static thread_local bool recursiveSetupGuard = false;

class OgnWritePrimAttribute
{
    static void setup(NodeObj const& nodeObj, GraphObj const& graphObj, OgnWritePrimAttributeDatabase& db, size_t offset)
    {
        // Check for re-entering setup and avoid. EG When input is being resolved we may get onConnectionTypeResolve()
        if (recursiveSetupGuard)
            return;

        CARB_PROFILE_ZONE(1, "setup");
        recursiveSetupGuard = true;
        std::shared_ptr<nullptr_t> atScopeExit(nullptr, [](auto) { recursiveSetupGuard = false; });

        InstanceIndex instanceIndex = db.getInstanceIndex() + offset;

        db.state.correctlySetup(offset) = false;

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        FIREWALL_RETURN(context.contextHandle == kInvalidGraphContextHandle); // LCOV_EXCL_LINE

        auto typeInterface{ carb::getCachedInterface<omni::graph::core::IAttributeType>() };

        pxr::UsdAttribute attrib;
        try
        {
            attrib = omni::graph::nodes::findSelectedAttribute(context, nodeObj, instanceIndex);
        }
        catch (std::runtime_error const&)
        {
            // Ignore errors in this callback - error will be reported at the next compute
            return;
        }

        if (!attrib)
        {
            // Couldn't get the indicated attribute for some expected reason
            return;
        }

        // Since we are a sink of data, we can assume that if our inputs:value is connected, it will be resolved by
        // propagation from upstream. We do not want to resolve/unresolve our inputs:value if we are connected because
        // this could create a type conflict with the upstream network. So instead we will only resolve/unresolve
        // when we are disconnected, and otherwise error out if we see a conflict.

        auto typeName{ attrib ? attrib.GetTypeName().GetAsToken() : pxr::TfToken() };
        Type usdAttribType{ typeInterface->typeFromSdfTypeName(typeName.GetText()) };

        if (!tryResolveInputAttribute(nodeObj, inputs::value.m_token, usdAttribType))
            return;

        AttributeObj srcData = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::value.m_token);
        Type srcDataType = srcData.iAttribute->getResolvedType(srcData);
        TypeC srcDataTypeC(srcDataType);

        // no need to continue if we are not resolved yet
        if (srcDataType == Type(BaseDataType::eUnknown))
            return;

        IFabricUsd* iFabricUsd = carb::getCachedInterface<IFabricUsd>();

        // Find our stage
        pxr::UsdStageRefPtr stage;
        omni::fabric::FabricId fabricId;
        std::tie(fabricId, stage) = getTargetFabricStage(context);
        FIREWALL_RETURN(fabricId == omni::fabric::kInvalidFabricId); // LCOV_EXCL_LINE

        pxr::UsdPrim destPrim{ attrib.GetPrim() };

        NameToken destAttribName = asInt(attrib.GetName());

        // Add the destination Prim to FC
        BucketId destPrimBucketId = omni::graph::nodes::addAttribToCache(
            destPrim, destPrim.GetPath(), destAttribName, iFabricUsd, fabricId, UsdTimeCode::Default());

        // FIREWALL check
        if (destPrimBucketId == kInvalidBucketId)
        {
            /* LCOV_EXCL_START */
            OgnWritePrimAttributeDatabase::logError(
                nodeObj, "Unable to add prim %s to fabric", destPrim.GetPrimPath().GetText());
            return;
            /* LCOV_EXCL_STOP */
        }

        PathC destPath = asInt(destPrim.GetPrimPath());

        // Read the type info of the destination attribute
        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        auto stageReaderWriterId = iStageReaderWriter->createOrGetFromFabricId(fabricId);
        if (iStageReaderWriter->attributeExists(stageReaderWriterId, destPath, destAttribName) == 0)
        {
            // Failed to add the attribute - it might not be authored

            // --------------------------------------------------------------------------------------
            // Get PrimVar into fabric by creating it on the prim
            if (pxr::UsdGeomPrimvar::IsPrimvar(attrib))
            {
                // Primvars have to go through prim var api. Note that we don't set the value here. That is because we
                // will be subsequently writing into the attribute through Fabric.
                if (auto primVarAPI = pxr::UsdGeomPrimvarsAPI(destPrim))
                {
                    if (pxr::UsdGeomPrimvar primVar = primVarAPI.FindPrimvarWithInheritance(attrib.GetName()))
                    {
                        primVarAPI.CreatePrimvar(attrib.GetName(), primVar.GetTypeName());
                    }
                }
            }
            else
            {
                // --------------------------------------------------------------------------------------
                // Get non-primvar into fabric by authoring the attribute with the composed value
                pxr::VtValue val;
                if (!attrib.Get(&val))
                {
                    val = attrib.GetTypeName().GetDefaultValue();
                }

                if (!attrib.Set(val))
                {
                    OgnWritePrimAttributeDatabase::logError(nodeObj, "Unable to author %s with value of type %s",
                                                            attrib.GetPath().GetText(), val.GetTypeName().c_str());
                    return;
                }
            }

            // FIREWALL check
            if (omni::graph::nodes::addAttribToCache(destPrim, destPrim.GetPath(), destAttribName, iFabricUsd, fabricId,
                                                     UsdTimeCode::Default()) == kInvalidBucketId)
            {
                /* LCOV_EXCL_START */
                OgnWritePrimAttributeDatabase::logError(
                    nodeObj, "Unable to add prim %s to fabric", destPrim.GetPrimPath().GetText());
                return;
                /* LCOV_EXCL_STOP */
            }
        }

        TypeC destDataTypeC = TypeC(iStageReaderWriter->getType(stageReaderWriterId, destPath, destAttribName));
        // FIREWALL check
        if (destDataTypeC == kUnknownType)
        {
            /* LCOV_EXCL_START */
            OgnWritePrimAttributeDatabase::logError(
                nodeObj, "Unable to add prim %s to fabric", destPrim.GetPrimPath().GetText());
            return;
            /* LCOV_EXCL_STOP */
        }

        Type destDataType(destDataTypeC);
        if (!ogn::areTypesCompatible(srcDataType, destDataType))
        {
            OgnWritePrimAttributeDatabase::logError(
                nodeObj, "Attribute %s.%s is not compatible with type '%s', please disconnect to change target attribute",
                destPrim.GetPrimPath().GetText(), toTfToken(destAttribName).GetText(), srcDataType.getTypeName().c_str());
            return;
        }

        db.state.destPath(offset) = destPath.path;
        db.state.destPathToken(offset) = asInt(destPrim.GetPrimPath().GetToken()).token;
        db.state.destAttrib(offset) = destAttribName.token;
        db.state.correctlySetup(offset) =
            iStageReaderWriter->attributeExists(stageReaderWriterId, destPath, destAttribName);
    }

public:
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

        OgnWritePrimAttributeDatabase db(nodeObj);
        setup(nodeObj, graphObj, db, 0);
    }

    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        // We need to check resolution if any of our relevant inputs change
        static std::array<NameToken, 5> const attribNames{ inputs::name.m_token, inputs::usePath.m_token,
                                                           inputs::primPath.m_token, inputs::prim.m_token,
                                                           inputs::value.m_token };
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

        OgnWritePrimAttributeDatabase db(nodeObj);
        setup(nodeObj, graphObj, db, 0);
    }

    // ----------------------------------------------------------------------------
    static bool computeVectorized(OgnWritePrimAttributeDatabase& db, size_t count)
    {
        if (!db.inputs.value().resolved())
            return true;

        NodeObj nodeObj = db.abi_node();
        GraphContextObj context = db.abi_context();
        GraphObj graphObj = nodeObj.iNode->getGraph(nodeObj);
        long stageId = context.iContext->getStageId(context);
        auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));

        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();

        auto usePath = db.inputs.usePath.vectorized(count);
        auto primPath = db.inputs.primPath.vectorized(count);
        auto name = db.inputs.name.vectorized(count);
        auto execOut = db.outputs.execOut.vectorized(count);
        auto usdWriteBack = db.inputs.usdWriteBack.vectorized(count);
        auto layerIdentifier = db.inputs.layerIdentifier.vectorized(count);

        auto correctlySetup = db.state.correctlySetup.vectorized(count);
        auto destPathToken = db.state.destPathToken.vectorized(count);
        auto destAttrib = db.state.destAttrib.vectorized(count);
        auto destPath = db.state.destPath.vectorized(count);
        auto layerIdentifierState = db.state.layerIdentifier.vectorized(count);
        auto resolvedLayerIdentifier = db.state.resolvedLayerIdentifier.vectorized(count);

        // Fast path through ABI when using target
        omni::fabric::FabricId graphFabricId;
        graphObj.iGraph->getFabricId(graphObj, graphFabricId);
        ConstAttributeDataHandle hdl = db.inputs.prim.abi_handle();
        auto prims = getDataR<PathC const*>(context, hdl);
        auto graphReaderWriterId = iStageReaderWriter->createOrGetFromFabricId(graphFabricId);
        size_t const* sizes = iStageReaderWriter->getArrayAttributeSizeRdPtr(graphReaderWriterId, hdl.path(), hdl.name());

        for (size_t idx = 0; idx < count; ++idx)
        {
            if (!correctlySetup[idx])
            {
                setup(db.abi_node({ idx }), graphObj, db, idx);
            }
            else
            {
                bool pathOk = false;
                if (usePath[idx])
                    pathOk = primPath[idx].token == destPathToken[idx];
                else
                    pathOk = sizes[idx] && prims[idx][0] == destPath[idx];

                if (!pathOk || name[idx] != destAttrib[idx])
                    setup(db.abi_node({ idx }), graphObj, db, idx);
            }

            if (layerIdentifierState[idx] != layerIdentifier[idx])
            {
                if (layerIdentifier[idx] != fabric::kUninitializedToken)
                    resolvedLayerIdentifier[idx] = resolveLayerIdentifier(
                        db.abi_node({ idx }), stage, inputs::layerIdentifier.m_token, layerIdentifier[idx]);
                else
                    resolvedLayerIdentifier[idx] = fabric::kUninitializedToken;

                layerIdentifierState[idx] = layerIdentifier[idx];
            }
        }

        // for array or GPU attributes, go through the data model to properly handle the copy
        // this needs to be consulted after the setup has been done
        Type type = db.inputs.value().type();
        bool gpuValid = context.iAttributeData->gpuValid(db.inputs.value().abi_handle(), context);
        const bool useDataModel = type.arrayDepth || gpuValid || !db.inputs.value.canVectorize();

        if (useDataModel)
        {
            CARB_PROFILE_ZONE(1, "DoWork_DataModel");
            for (size_t idx = 0; idx < count; ++idx)
            {
                if (correctlySetup[idx])
                {
                    copyAttributeData(context, destPath[idx], destAttrib[idx], db.inputs.value(idx).abi_handle(),
                                      usdWriteBack[idx], resolvedLayerIdentifier[idx]);
                    execOut[idx] = kExecutionAttributeStateEnabled;
                }
            }
        }
        else
        {
            CARB_PROFILE_ZONE(1, "DoWork_Direct");

            std::vector<AttributeDataHandle> writeBackHandles;
            writeBackHandles.reserve(count);

            // gather src base pointer
            uint8_t const* srcData = nullptr;
            size_t stride = 0;
            db.inputs.value().rawData(srcData, stride);

            pxr::UsdStageRefPtr stage;
            omni::fabric::FabricId stageFabricId;
            std::tie(stageFabricId, stage) = getTargetFabricStage(context);
            auto stageReaderWriterId = iStageReaderWriter->createOrGetFromFabricId(stageFabricId);

            NameToken lastLayer = resolvedLayerIdentifier[0];

            for (size_t idx = 0; idx < count; ++idx)
            {
                if (resolvedLayerIdentifier[idx] != lastLayer)
                {
                    if (!writeBackHandles.empty())
                    {
                        CARB_PROFILE_ZONE(1, "RegisterWriteBack");
                        context.iContext->registerForUSDWriteBacksToLayer(
                            context, writeBackHandles.data(), writeBackHandles.size(), lastLayer);
                        writeBackHandles.clear();
                    }
                    lastLayer = resolvedLayerIdentifier[idx];
                }

                if (correctlySetup[idx])
                {
                    if (void* dst =
                            iStageReaderWriter->getAttribute(stageReaderWriterId, destPath[idx], destAttrib[idx]).ptr)
                    {
                        if (usdWriteBack[idx])
                            writeBackHandles.emplace_back(AttrKey{ destPath[idx], destAttrib[idx] });

                        void const* const src = srcData + idx * stride;
                        memcpy(dst, src, stride);
                        execOut[idx] = kExecutionAttributeStateEnabled;
                    }
                    else
                    {
                        db.logError("Target attribute not available for %s:%s", db.pathToString(destPath[idx]),
                                    db.tokenToString(destAttrib[idx]));
                    }
                }
            }
            if (!writeBackHandles.empty())
            {
                CARB_PROFILE_ZONE(1, "RegisterWriteBack");
                context.iContext->registerForUSDWriteBacksToLayer(
                    context, writeBackHandles.data(), writeBackHandles.size(), lastLayer);
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()
} // namespace nodes
} // namespace graph
} // namespace omni
