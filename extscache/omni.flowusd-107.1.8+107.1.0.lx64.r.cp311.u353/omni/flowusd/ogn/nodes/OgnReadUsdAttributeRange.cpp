// Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

// clang-format off
#include "UsdPCH.h"

#include <OgnReadUsdAttributeRangeDatabase.h>

#include <omni/usd/UsdContext.h>
#include <omni/usd/UsdUtils.h>

#include <omni/fabric/FabricUSD.h>

#include "PrimCommon.h"
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{

/// <summary>
/// This node, unlike the original OgnReadPrimAttribute, returns output array in a range specified by 'firstElement' and
/// 'rangeSize' and the input array is not copied to Fabric.
/// </summary>
class OgnReadUsdAttributeRange
{
    struct AccelerationSetup
    {
        bool m_correctlySetup{ false };
        AttributeDataHandle m_dstHandle{ AttributeDataHandle::invalidValue() };
        pxr::UsdTimeCode m_time{ pxr::UsdTimeCode::Default() };
        pxr::SdfPath m_srcPathName;
        pxr::TfToken m_attrName;
        bool m_recurseGuard{ false };
        size_t m_firstElement = ~0u;
        size_t m_rangeSize = ~0u;
    };
    GraphInstanceSpecific<AccelerationSetup> setupCache{};

    // Returns 0 if the attribute is not an array or the array is empty
    uint64_t getAttributeArraySize(GraphContextObj const& context, NodeObj const& nodeObj, pxr::SdfTimeCode const& time)
    {
        auto& localSetup = setupCache.local(nodeObj);

        pxr::UsdStageRefPtr stage = usd::UsdContext::getContext()->getStage();
        if (!stage)
            return false;

        pxr::UsdAttribute attr;
        auto prim = stage->GetPrimAtPath(localSetup.m_srcPathName);
        if (prim.IsValid())
        {
            attr = prim.GetAttribute(localSetup.m_attrName);
        }
        else
        {
            // Prim not cached in local setup yet
            try
            {
                attr = omni::graph::nodes::findSelectedAttribute(context, nodeObj, kAccordingToContextIndex);
            }
            catch (std::runtime_error const& error)
            {
                OgnReadUsdAttributeRangeDatabase::logError(nodeObj, error.what());
                return 0;
            }
        }

        if (!attr)
            return 0;

        if (!attr.IsAuthored())
        {
            if (UsdTimeCode::Default() != time)
            {
                CARB_LOG_ERROR("Access a non authored attrib %s with a specific timestamp is not allowed",
                               attr.GetName().GetText());
                return 0;
            }
        }

        auto const type = attr.GetTypeName();
        if (type.IsArray())
        {
            pxr::VtValue val;
            attr.Get(&val, time);
            return val.GetArraySize();
        }

        return 0;
    }

    template <typename T>
    bool tryCopyAssumingType(NodeObj const& nodeObj, GraphContextObj const& context)
    {
        auto& localSetup = setupCache.local(nodeObj);

        pxr::UsdStageRefPtr stage = usd::UsdContext::getContext()->getStage();
        if (!stage)
            return false;

        auto prim = stage->GetPrimAtPath(localSetup.m_srcPathName);
        if (!prim.IsValid())
            return false;

        pxr::UsdAttribute attr = prim.GetAttribute(localSetup.m_attrName);
        if (!attr.IsValid())
            return false;

        pxr::VtArray<T> srcArray;
        omni::usd::UsdUtils::getAttributeArray<T>(attr, srcArray, localSetup.m_time);

        void* dstData_ptr = nullptr;
        context.iAttributeData->getDataW(&dstData_ptr, context, &localSetup.m_dstHandle, 1u);
        dstData_ptr = *((void**)dstData_ptr);
        assert(dstData_ptr);

        // Determine the size of the element to copy
        Type const type = context.iAttributeData->getType(context, localSetup.m_dstHandle);
        const IAttributeType& iAttributeType = *carb::getCachedInterface<IAttributeType>();
        size_t elementSize = iAttributeType.baseDataSize(type) * type.componentCount;

        // Copy range to the output attribute
        memcpy(dstData_ptr, srcArray.cdata() + localSetup.m_firstElement, localSetup.m_rangeSize * elementSize);

        return true;
    }

    bool copy(NodeObj const& nodeObj,
              GraphContextObj const& context,
              InstanceIndex idx,
              pxr::SdfTimeCode const& time,
              size_t firstElement,
              size_t rangeSize)
    {
        auto& localSetup = setupCache.local(nodeObj);

        // Clamp values before caching
        size_t srcSize = getAttributeArraySize(context, nodeObj, time);
        if (srcSize > 0)
        {
            // Clamp input values to the actual size of the original array
            firstElement = std::min(firstElement, srcSize);
            rangeSize = std::min(firstElement + rangeSize, srcSize) - firstElement;

            // Setup destination array size
            context.iAttributeData->setElementCount(context, localSetup.m_dstHandle, rangeSize);
        }

        // Cache values
        localSetup.m_time = time;
        localSetup.m_firstElement = firstElement;
        localSetup.m_rangeSize = rangeSize;

        if (srcSize == 0)
        {
            // Empty array, only element count set to the destination array
            return true;
        }

        // All possible types
        Type const type = context.iAttributeData->getType(context, localSetup.m_dstHandle);
        switch (type.baseType)
        {
        case BaseDataType::eDouble:
            switch (type.componentCount)
            {
            case 1:
                return tryCopyAssumingType<double>(nodeObj, context);
            case 2:
                return tryCopyAssumingType<GfVec2d>(nodeObj, context);
            case 3:
                return tryCopyAssumingType<GfVec3d>(nodeObj, context);
            case 4:
                return tryCopyAssumingType<GfVec4d>(nodeObj, context);
            }
        case BaseDataType::eFloat:
            switch (type.componentCount)
            {
            case 1:
                return tryCopyAssumingType<float>(nodeObj, context);
            case 2:
                return tryCopyAssumingType<GfVec2f>(nodeObj, context);
            case 3:
                return tryCopyAssumingType<GfVec3f>(nodeObj, context);
            case 4:
                return tryCopyAssumingType<GfVec4f>(nodeObj, context);
            }
        case BaseDataType::eHalf:
            switch (type.componentCount)
            {
            case 1:
                return tryCopyAssumingType<GfHalf>(nodeObj, context);
            case 2:
                return tryCopyAssumingType<GfVec2h>(nodeObj, context);
            case 3:
                return tryCopyAssumingType<GfVec3h>(nodeObj, context);
            case 4:
                return tryCopyAssumingType<GfVec4h>(nodeObj, context);
            }
        case BaseDataType::eInt:
            switch (type.componentCount)
            {
            case 1:
                return tryCopyAssumingType<int32_t>(nodeObj, context);
            case 2:
                return tryCopyAssumingType<GfVec2i>(nodeObj, context);
            case 3:
                return tryCopyAssumingType<GfVec3i>(nodeObj, context);
            case 4:
                return tryCopyAssumingType<GfVec4i>(nodeObj, context);
            }
        case BaseDataType::eInt64:
            return tryCopyAssumingType<int64_t>(nodeObj, context);
        case BaseDataType::eUChar:
            return tryCopyAssumingType<unsigned char>(nodeObj, context);
        case BaseDataType::eUInt:
            return tryCopyAssumingType<uint32_t>(nodeObj, context);
        case BaseDataType::eUInt64:
            return tryCopyAssumingType<uint64_t>(nodeObj, context);
        }

        nodeObj.iNode->logComputeMessageOnInstance(nodeObj, idx, ogn::Severity::eError, "Failed to resolve input type");
        CARB_LOG_ERROR("Failed to resolve input type: %s", type.getTypeName().c_str());

        return false;
    }

    void setup(NodeObj const& nodeObj, GraphContextObj const& context, InstanceIndex instanceIndex)
    {
        auto& localSetup = setupCache.local(nodeObj);
        if (localSetup.m_recurseGuard)
            return;

        localSetup.m_recurseGuard = true;
        struct AtScopeExit
        {
            AtScopeExit(bool& val) : m_val(val)
            {
            }
            ~AtScopeExit()
            {
                m_val = false;
            }
            bool& m_val;
        } scope(localSetup.m_recurseGuard);

        auto typeInterface{ carb::getCachedInterface<omni::graph::core::IAttributeType>() };

        localSetup.m_correctlySetup = false;

        pxr::UsdAttribute attrib;
        try
        {
            attrib = omni::graph::nodes::findSelectedAttribute(context, nodeObj, instanceIndex);
        }
        catch (std::runtime_error const& error)
        {
            OgnReadUsdAttributeRangeDatabase::logError(nodeObj, error.what());
            return;
        }
        if (!attrib)
        {
            // Couldn't get the indicated attribute for some expected reason
            return;
        }

        auto typeName{ attrib ? attrib.GetTypeName().GetAsToken() : pxr::TfToken() };
        Type attribType{ typeInterface->typeFromSdfTypeName(typeName.GetText()) };
        tryResolveOutputAttribute(nodeObj, outputs::value.m_token, attribType);

        // Get interfaces
        const INode& iNode = *nodeObj.iNode;

        pxr::UsdPrim prim{ attrib.GetPrim() };
        localSetup.m_srcPathName = prim.GetPath();
        localSetup.m_attrName = attrib.GetName();

        // If it's resolved, we already know that it is compatible from the above check of the USD
        AttributeObj outAttrib = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::value.m_token);
        Type outType = outAttrib.iAttribute->getResolvedType(outAttrib);
        if (outType == Type())
        {
            // Not resolved, so we have to resolve it now. This node is strange in that the resolved output type
            // depends on external state instead of other attributes.
            outAttrib.iAttribute->setResolvedType(outAttrib, attribType);
        }

        // Finally we ensure that that the FC connection to the source prim attribute is in-place
        localSetup.m_dstHandle = outAttrib.iAttribute->getAttributeDataHandle(outAttrib, instanceIndex);
        if ((AttrKey)localSetup.m_dstHandle == AttributeDataHandle::invalidValue())
        {
            OgnReadUsdAttributeRangeDatabase::logError(
                nodeObj,
                formatString("Internal error resolving attribute %s", context.iToken->getText(outputs::value.m_token))
                    .c_str());
            return;
        }
        localSetup.m_correctlySetup = true;
    }

    // ----------------------------------------------------------------------------
    // Called by OG when our prim attrib changes. We want to catch the case of changing the prim attribute interactively
    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        // FIXME: Be pedantic about validity checks - this can be run directly by the TfNotice so who knows
        // when or where this is happening
        NodeObj nodeObj{ attrObj.iAttribute->getNode(attrObj) };
        if (nodeObj.nodeHandle == kInvalidNodeHandle)
            return;

        GraphObj graphObj{ nodeObj.iNode->getGraph(nodeObj) };
        if (graphObj.graphHandle == kInvalidGraphHandle)
            return;

        // no setup if graph is disabled (during python edition for instance)
        if (graphObj.iGraph->isDisabled(graphObj))
            return;

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        if (context.contextHandle == kInvalidGraphContextHandle)
            return;

        OgnReadUsdAttributeRange& instance =
            OgnReadUsdAttributeRangeDatabase::sSharedState<OgnReadUsdAttributeRange>(nodeObj);
        auto& localSetup = instance.setupCache.local(graphObj);
        instance.setup(nodeObj, context, kAccordingToContextIndex);
    }

public:
    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        // Value changed is only called from USD changes, Fabric changes need to be checked in compute
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
        if (graphObj.graphHandle == kInvalidGraphHandle)
            return;

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        if (context.contextHandle == kInvalidGraphContextHandle)
            return;

        OgnReadUsdAttributeRange& instance =
            OgnReadUsdAttributeRangeDatabase::sSharedState<OgnReadUsdAttributeRange>(nodeObj);
        auto& localSetup = instance.setupCache.local(graphObj);
        instance.setup(nodeObj, context, kAccordingToContextIndex);
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnReadUsdAttributeRangeDatabase& db)
    {
        NodeObj nodeObj = db.abi_node();
        GraphContextObj ctx = db.abi_context();

        auto firstElement = db.inputs.firstElement();
        auto rangeSize = db.inputs.rangeSize();

        auto time = db.inputs.usdTimecode();
        if (time == -1)
            time = UsdTimeCode::Default().GetValue();

        OgnReadUsdAttributeRange& instance =
            OgnReadUsdAttributeRangeDatabase::sSharedState<OgnReadUsdAttributeRange>(db.abi_node());

        if (rangeSize == 0)
        {
            // skip copying data and expect the user just wants to read the size of the input array
            db.outputs.inputArraySize() = instance.getAttributeArraySize(ctx, nodeObj, time);

            return true;
        }

        auto& localSetup = instance.setupCache.local(nodeObj);

        if (!localSetup.m_correctlySetup)
        {
            instance.setup(nodeObj, ctx, db.getInstanceIndex());
        }
        else
        {
            auto path = db.inputs.usePath() ? db.inputs.primPath() : db.stringToToken(db.inputs.prim.path());
            auto statePath = localSetup.m_srcPathName.GetToken();
            if (path != omni::fabric::asInt(statePath))
                instance.setup(nodeObj, ctx, db.getInstanceIndex());
        }

        if (localSetup.m_correctlySetup)
        {
            db.outputs.inputArraySize() = instance.getAttributeArraySize(ctx, nodeObj, time);

            pxr::UsdStageRefPtr stage = usd::UsdContext::getContext()->getStage();
            if (!stage)
                return false;

            if (!instance.copy(nodeObj, ctx, db.getInstanceIndex(), time, firstElement, rangeSize))
                return false;

            return true;
        }

        return false;
    }
};

REGISTER_OGN_NODE()
} // namespace nodes
} // namespace graph
} // namespace omni
