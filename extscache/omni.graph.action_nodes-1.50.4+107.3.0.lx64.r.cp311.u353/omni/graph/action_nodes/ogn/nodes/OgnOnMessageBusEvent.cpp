// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnOnMessageBusEventDatabase.h>
#include <omni/graph/action/IActionGraph.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ogn/UsdTypes.h>
#include <omni/graph/core/CppWrappers.h>
#include <omni/kit/IApp.h>
#include <carb/dictionary/IDictionary.h>
#include <carb/events/EventsUtils.h>

#include "ActionNodeCommon.h"

#include <shared_mutex>

namespace omni::graph::action
{

class OgnOnMessageBusEvent
{
public:
    exec::unstable::Stamp m_setStamp; // stamp set when the event occurs
    exec::unstable::SyncStamp m_syncStamp; // stamp set by each instance
    std::atomic_bool m_subDirty{ true }; // set when sub needs to be changed
    carb::events::ISubscriptionPtr m_sub; // smart pointer for message bus subscription
    carb::dictionary::Item* m_currentPayload{ nullptr }; // The last payload we received
    std::shared_mutex m_mutex; // protect m_sub and m_currentPayload

    // ----------------------------------------------------------------------------
    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        AttributeObj attribObj = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::eventName.m_token);
        attribObj.iAttribute->registerValueChangedCallback(attribObj, onValueChanged, true);
    }

    // ----------------------------------------------------------------------------
    static void onValueChanged(const AttributeObj& attrObj, const void* userData)
    {
        // inputs:eventName has changed, so we need to change our subscription
        NodeObj nodeObj = attrObj.iAttribute->getNode(attrObj);
        OgnOnMessageBusEvent& authoringState = OgnOnMessageBusEventDatabase::sSharedState<OgnOnMessageBusEvent>(nodeObj);
        authoringState.m_subDirty = true;
        nodeObj.iNode->requestCompute(nodeObj);
    }

    static bool compute(OgnOnMessageBusEventDatabase& db)
    {
        auto& eventName = db.inputs.eventName();

        OgnOnMessageBusEvent& authoringState =
            OgnOnMessageBusEventDatabase::sSharedState<OgnOnMessageBusEvent>(db.abi_node());
        auto& localState = db.perInstanceState<OgnOnMessageBusEvent>();

        // Check for subscription needed
        if (authoringState.m_subDirty.exchange(false))
        {
            if (authoringState.m_sub)
                authoringState.m_sub.detach()->unsubscribe();

            if (eventName != omni::fabric::kUninitializedToken)
            {
                omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>();

                auto eventNameStr = db.tokenToString(eventName);
                auto eventType = carb::events::typeFromString(eventNameStr);
                auto const& nodeObj = db.abi_node();

                authoringState.m_sub = carb::events::createSubscriptionToPushByType(
                    app->getMessageBusEventStream(), eventType,
                    [nodeObj](carb::events::IEvent* e)
                    {
                        if (e)
                        {
                            OgnOnMessageBusEvent& authoringState =
                                OgnOnMessageBusEventDatabase::sSharedState<OgnOnMessageBusEvent>(nodeObj);
                            auto iDictionary = carb::getCachedInterface<carb::dictionary::IDictionary>();

                            // protect modification of our shared state
                            std::unique_lock lock(authoringState.m_mutex);

                            if (authoringState.m_currentPayload)
                                iDictionary->destroyItem(authoringState.m_currentPayload);
                            authoringState.m_currentPayload = iDictionary->duplicateItem(e->payload);

                            if (nodeObj.iNode->isValid(nodeObj))
                                nodeObj.iNode->requestCompute(nodeObj);
                            authoringState.m_setStamp.next();
                        }
                    });
            }
            // Don't trigger execOut because we just modified our eventName
            localState.m_syncStamp.sync(authoringState.m_setStamp);
            return true;
        }

        if (!localState.m_syncStamp.makeSync(authoringState.m_setStamp))
            return true; // we don't have a new payload, so we are done

        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        auto iDictionary = carb::getCachedInterface<carb::dictionary::IDictionary>();

        // read lock because we will be using the shared payload IDictionary
        std::shared_lock lock(authoringState.m_mutex);

        // activate our output pin now because the node will compute successfully
        auto iActionGraph = getInterface();

        iActionGraph->setExecutionEnabled(outputs::execOut.token(), db.getInstanceIndex());

        carb::dictionary::Item* payload = authoringState.m_currentPayload;
        if (!payload)
            return true; // no payload is ok - we are done

        auto const& nodeObj = db.abi_node();
        size_t nAttrs = nodeObj.iNode->getAttributeCount(nodeObj);
        if (!nAttrs)
            return true; // no attributes at all? Very strange but fine.

        std::vector<AttributeObj> allAttrs;
        allAttrs.resize(nAttrs);
        nodeObj.iNode->getAttributes(nodeObj, allAttrs.data(), nAttrs);
        for (auto& attrObj : allAttrs)
        {
            if (!attrObj.iAttribute->isDynamic(attrObj))
                continue;

            if (attrObj.iAttribute->getPortType(attrObj) != kAttributePortType_Output)
                continue;

            // Found a dynamic output - try to unpack a payload value
            NameToken dataNameToken =
                attrObj.iAttribute->removePortTypeFromName(attrObj.iAttribute->getNameToken(attrObj), false);
            const char* dataName = db.tokenToString(dataNameToken);

            using carb::dictionary::ItemType;
            using omni::graph::core::BaseDataType;

            auto item = iDictionary->getItem(payload, dataName);
            if (!item)
                continue; // Nothing in the payload for this output

            auto dataType = attrObj.iAttribute->getResolvedType(attrObj);
            bool isArray = dataType.arrayDepth > 0;
            auto itemType = iDictionary->getItemType(item);
            size_t nChildren = itemType == ItemType::eDictionary ? iDictionary->getItemChildCount(item) : 0;
            size_t nElements = nChildren / dataType.componentCount;

            auto dataHandle = attrObj.iAttribute->getAttributeDataHandle(attrObj, db.getInstanceIndex());
            bool convertOk = true;

            switch (dataType.baseType)
            {
            case BaseDataType::eBool:
                if (isArray)
                {
                    // bool[] -> bool[]
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, nElements);
                    if (nElements)
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eBool, item)))
                            iDictionary->getAsBoolArray(item, *getDataW<bool*>(db.abi_context(), dataHandle), nChildren);
                    }
                }
                else if ((convertOk = iDictionary->isAccessibleAs(ItemType::eBool, item)))
                {
                    // bool -> bool
                    *getDataW<bool>(db.abi_context(), dataHandle) = iDictionary->getAsBool(item);
                }
                else
                    convertOk = false;
                break;
            case BaseDataType::eDouble:
                if (isArray)
                {
                    // double[] -> double[] | doubleX[]
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, nElements);
                    if (nElements)
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eFloat, item)))
                            iDictionary->getAsFloat64Array(
                                item, *getDataW<double*>(db.abi_context(), dataHandle), nChildren);
                    }
                }
                else
                {
                    if (nChildren > 0) // double[] -> doubleX
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eFloat, item)))
                            iDictionary->getAsFloat64Array(
                                item, getDataW<double>(db.abi_context(), dataHandle), nChildren);
                    }
                    else if ((convertOk = iDictionary->isAccessibleAs(ItemType::eFloat, item)))
                    {
                        // double -> double
                        *getDataW<double>(db.abi_context(), dataHandle) = iDictionary->getAsFloat64(item);
                    }
                }
                break;
            case BaseDataType::eFloat:
                if (isArray)
                {
                    // float[] -> float[] | floatX[]
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, nElements);
                    if (nElements)
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eFloat, item)))
                            iDictionary->getAsFloatArray(
                                item, *getDataW<float*>(db.abi_context(), dataHandle), nChildren);
                    }
                }
                else
                {
                    if (nChildren > 0) // float[] -> floatX
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eFloat, item)))
                            iDictionary->getAsFloatArray(item, getDataW<float>(db.abi_context(), dataHandle), nChildren);
                    }
                    else if ((convertOk = iDictionary->isAccessibleAs(ItemType::eFloat, item)))
                    {
                        // float -> float
                        *getDataW<float>(db.abi_context(), dataHandle) = iDictionary->getAsFloat(item);
                    }
                }
                break;
            case BaseDataType::eHalf:
                if (isArray)
                {
                    // float[] -> half[] | halfX[]
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, nElements);
                    if (nElements)
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eFloat, item)))
                        {
                            std::vector<float> halfs(nChildren);
                            iDictionary->getAsFloatArray(item, halfs.data(), nChildren);
                            auto ptr = *getDataW<pxr::GfHalf*>(db.abi_context(), dataHandle);
                            for (size_t i = 0; i < nChildren; ++i)
                                ptr[i] = halfs[i];
                        }
                    }
                }
                else
                {
                    if (nChildren > 0) // float[] -> halfX
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eFloat, item)))
                        {
                            float* halfs = CARB_STACK_ALLOC(float, nChildren);
                            iDictionary->getAsFloatArray(item, halfs, nChildren);
                            auto ptr = getDataW<pxr::GfHalf>(db.abi_context(), dataHandle);
                            for (size_t i = 0; i < nChildren; ++i)
                                ptr[i] = halfs[i];
                        }
                    }
                    else if ((convertOk = iDictionary->isAccessibleAs(ItemType::eFloat, item)))
                    {
                        // float -> half
                        *getDataW<pxr::GfHalf>(db.abi_context(), dataHandle) = iDictionary->getAsFloat(item);
                    }
                }
                break;
            case BaseDataType::eInt:
                if (isArray)
                {
                    // int[] -> int[] | intX[]
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, nElements);
                    if (nElements)
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eInt, item)))
                            iDictionary->getAsIntArray(
                                item, *getDataW<int32_t*>(db.abi_context(), dataHandle), nChildren);
                    }
                }
                else
                {
                    if (nChildren > 0) // array -> intX
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eInt, item)))
                            iDictionary->getAsIntArray(item, getDataW<int32_t>(db.abi_context(), dataHandle), nChildren);
                    }
                    else if ((convertOk = iDictionary->isAccessibleAs(ItemType::eInt, item)))
                    {
                        // int -> int
                        *getDataW<int32_t>(db.abi_context(), dataHandle) = iDictionary->getAsInt(item);
                    }
                }
                break;
            case BaseDataType::eInt64:
                if (isArray)
                {
                    // int64[] -> int64[]
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, nElements);
                    if (nElements)
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eInt, item)))
                            iDictionary->getAsInt64Array(
                                item, *getDataW<int64_t*>(db.abi_context(), dataHandle), nChildren);
                    }
                }
                else
                {
                    // int64 -> int64
                    if ((convertOk = iDictionary->isAccessibleAs(ItemType::eInt, item)))
                        *getDataW<int64_t>(db.abi_context(), dataHandle) = iDictionary->getAsInt64(item);
                }
                break;
            case BaseDataType::eRelationship:
                if (dataType.role == AttributeRole::eTarget)
                {
                    if ((convertOk = iDictionary->isAccessibleAs(ItemType::eString, item)))
                    {
                        size_t strLen{ 0 };
                        const char* sourcePtr = iDictionary->getStringBuffer(item, &strLen);

                        ogn::ArrayOutput<TargetPath, ogn::kCpu> targetData(
                            db.getInstanceIndex().index, AttributeRole::eTarget);
                        targetData.setContext(db.abi_context());
                        targetData.setHandle(dataHandle);
                        auto targetData0 = targetData(0);
                        targetData0.resize(1);
                        targetData0[0] = db.stringToPath(sourcePtr);
                    }
                    else
                    {
                        convertOk = (iDictionary->isAccessibleAsArrayOf(ItemType::eString, item) ||
                                     ((itemType == ItemType::eDictionary) && (nElements == 0)));
                        if (convertOk)
                        {
                            ogn::ArrayOutput<TargetPath, ogn::kCpu> targetData(
                                db.getInstanceIndex().index, AttributeRole::eTarget);
                            targetData.setContext(db.abi_context());
                            targetData.setHandle(dataHandle);
                            auto targetData0 = targetData(0);
                            targetData0.resize(nChildren);

                            if (nChildren)
                            {
                                std::vector<char const*> strs(nChildren);
                                iDictionary->getStringBufferArray(item, strs.data(), nChildren);
                                for (size_t i = 0; i < nChildren; ++i)
                                    targetData0[i] = db.stringToPath(strs[i]);
                            }
                        }
                    }
                }
                break;
            case BaseDataType::eToken:
                if (isArray)
                {
                    // string[] -> token[]
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, nElements);
                    if (nElements)
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eString, item)))
                        {
                            std::vector<char const*> strs(nChildren);
                            iDictionary->getStringBufferArray(item, strs.data(), nChildren);
                            auto ptr = *getDataW<NameToken*>(db.abi_context(), dataHandle);
                            for (size_t i = 0; i < nChildren; ++i)
                                ptr[i] = db.stringToToken(strs[i]);
                        }
                    }
                }
                else
                {
                    // string -> token
                    if ((convertOk = iDictionary->isAccessibleAs(ItemType::eString, item)))
                    {
                        size_t sLen;
                        *getDataW<NameToken>(db.abi_context(), dataHandle) =
                            db.stringToToken(iDictionary->getStringBuffer(item, &sLen));
                    }
                }
                break;
            case BaseDataType::eUChar:
            {
                bool isTextOut = (dataType.role == AttributeRole::eText) || (dataType.role == AttributeRole::ePath);
                if (isArray && isTextOut && (itemType == ItemType::eString))
                {
                    // string -> uchar[] (string)
                    size_t strLen{ 0 };
                    const char* sourcePtr = iDictionary->getStringBuffer(item, &strLen);
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, strLen);
                    auto writePtr = *getDataW<char*>(db.abi_context(), dataHandle);
                    memcpy(writePtr, sourcePtr, strLen);
                }
                else if (isArray && !isTextOut)
                {
                    // int[] -> uchar[]
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, nElements);
                    if (nElements)
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eInt, item)))
                        {
                            std::vector<int32_t> ints(nChildren);
                            iDictionary->getAsIntArray(item, ints.data(), nChildren);
                            auto ptr = *getDataW<uint8_t*>(db.abi_context(), dataHandle);
                            for (size_t i = 0; i < nChildren; ++i)
                                ptr[i] = ints[i];
                        }
                    }
                }
                else if (!isTextOut)
                {
                    // int -> uchar
                    if ((convertOk = iDictionary->isAccessibleAs(ItemType::eInt, item)))
                        *getDataW<uint8_t>(db.abi_context(), dataHandle) = iDictionary->getAsInt(item);
                }
                else
                    convertOk = false;
            }
            break;
            case BaseDataType::eUInt:
                if (isArray)
                {
                    // int64[] -> uint[]
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, nElements);
                    if (nElements)
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eInt, item)))
                        {
                            std::vector<int64_t> ints(nChildren);
                            iDictionary->getAsInt64Array(item, ints.data(), nChildren);
                            auto ptr = *getDataW<uint32_t*>(db.abi_context(), dataHandle);
                            for (size_t i = 0; i < nChildren; ++i)
                                ptr[i] = static_cast<uint32_t>(ints[i]);
                        }
                    }
                }
                else
                {
                    // int64 -> uint
                    if ((convertOk = iDictionary->isAccessibleAs(ItemType::eInt, item)))
                        *getDataW<uint32_t>(db.abi_context(), dataHandle) =
                            static_cast<uint32_t>(iDictionary->getAsInt64(item));
                }
                break;
            case BaseDataType::eUInt64: // warning - possible truncation
                if (isArray)
                {
                    // int64[] -> uint64[]
                    db.abi_context().iAttributeData->setElementCount(db.abi_context(), dataHandle, nElements);
                    if (nElements)
                    {
                        if ((convertOk = iDictionary->isAccessibleAsArrayOf(ItemType::eInt, item)))
                        {
                            std::vector<int64_t> ints(nChildren);
                            iDictionary->getAsInt64Array(item, ints.data(), nChildren);
                            auto ptr = *getDataW<uint64_t*>(db.abi_context(), dataHandle);
                            for (size_t i = 0; i < nChildren; ++i)
                                ptr[i] = ints[i];
                        }
                    }
                }
                else
                {
                    // int64 -> uint64
                    if ((convertOk = iDictionary->isAccessibleAs(ItemType::eInt, item)))
                        *getDataW<uint64_t>(db.abi_context(), dataHandle) = iDictionary->getAsInt64(item);
                }
                break;
            default:
                convertOk = false;
            }

            if (!convertOk)
                db.logWarning(
                    "Could not convert payload %s to the attribute type %s", dataName, dataType.getTypeName().c_str());
        }
        return true;
    }
};

REGISTER_OGN_NODE();

} // omni::graph::action
