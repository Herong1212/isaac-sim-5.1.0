// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnSendMessageBusEventDatabase.h>
#include <omni/graph/action/IActionGraph.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ogn/UsdTypes.h>
#include <omni/graph/core/CppWrappers.h>
#include <omni/kit/IApp.h>
#include <carb/dictionary/IDictionary.h>


namespace omni::graph::action
{

using carb::dictionary::ItemType;

class OgnSendMessageBusEvent
{
public:
    static bool compute(OgnSendMessageBusEventDatabase& db)
    {
        auto& eventName = db.inputs.eventName();

        if (eventName == omni::fabric::kUninitializedToken)
        {
            db.logError("Event Name must not be empty");
            return false;
        }

        omni::kit::IApp* iApp = carb::getCachedInterface<omni::kit::IApp>();
        auto iDictionary = carb::getCachedInterface<carb::dictionary::IDictionary>();


        auto eventNameStr = db.tokenToString(eventName);
        auto eventType = carb::events::typeFromString(eventNameStr);

        carb::events::IEvent* e =
            iApp->getMessageBusEventStream()->createEventPtr(eventType, carb::events::kGlobalSenderId);

        carb::dictionary::Item* item = e->payload;

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

            if (attrObj.iAttribute->getPortType(attrObj) != kAttributePortType_Input)
                continue;

            // Found a dynamic input, pack it into the payload
            NameToken dataNameToken =
                attrObj.iAttribute->removePortTypeFromName(attrObj.iAttribute->getNameToken(attrObj), false);
            const char* dataName = db.tokenToString(dataNameToken);

            auto dataType = attrObj.iAttribute->getResolvedType(attrObj);
            bool isArray = dataType.arrayDepth > 0;
            size_t cc = dataType.componentCount;

            // short form to create the payload item
            auto mk = [=](ItemType itemType) { return iDictionary->createItem(item, dataName, itemType); };

            auto dataHandle = attrObj.iAttribute->getConstAttributeDataHandle(attrObj, db.getInstanceIndex());
            bool convertOk = true;

            switch (dataType.baseType)
            {
            case BaseDataType::eBool:
                if (isArray)
                {
                    // bool[] -> bool[]
                    auto nElements = getElementCount(db.abi_context(), dataHandle);
                    iDictionary->setBoolArray(
                        mk(ItemType::eDictionary), *getDataR<bool*>(db.abi_context(), dataHandle), nElements);
                }
                else
                {
                    // bool -> bool
                    iDictionary->setBool(mk(ItemType::eBool), *getDataR<bool>(db.abi_context(), dataHandle));
                }
                break;
            case BaseDataType::eDouble:
                if (isArray)
                {
                    // double[] | doubleX[] -> double[]
                    auto nElements = getElementCount(db.abi_context(), dataHandle);
                    iDictionary->setFloat64Array(
                        mk(ItemType::eDictionary), *getDataR<double*>(db.abi_context(), dataHandle), nElements * cc);
                }
                else
                {
                    if (cc > 1) // doubleX -> double[]
                    {
                        iDictionary->setFloat64Array(
                            mk(ItemType::eDictionary), getDataR<double>(db.abi_context(), dataHandle), cc);
                    }
                    else
                    {
                        // double -> double
                        iDictionary->setFloat64(mk(ItemType::eFloat), *getDataR<double>(db.abi_context(), dataHandle));
                    }
                }
                break;
            case BaseDataType::eFloat:
                if (isArray)
                {
                    // float[] | floatX[] -> float[]
                    auto nElements = getElementCount(db.abi_context(), dataHandle);
                    iDictionary->setFloatArray(
                        mk(ItemType::eDictionary), *getDataR<float*>(db.abi_context(), dataHandle), nElements * cc);
                }
                else
                {
                    if (cc > 1) // floatX -> float[]
                    {
                        iDictionary->setFloatArray(
                            mk(ItemType::eDictionary), getDataR<float>(db.abi_context(), dataHandle), cc);
                    }
                    else
                    {
                        // float -> float
                        iDictionary->setFloat(mk(ItemType::eFloat), *getDataR<float>(db.abi_context(), dataHandle));
                    }
                }
                break;
            case BaseDataType::eHalf:
                if (isArray)
                {
                    // half[] | halfX[] -> float[]
                    auto nElements = getElementCount(db.abi_context(), dataHandle);
                    std::vector<float> halfs(nElements * cc);
                    auto ptr = *getDataR<pxr::GfHalf*>(db.abi_context(), dataHandle);
                    for (size_t i = 0; i < nElements * cc; ++i)
                        halfs[i] = ptr[i];
                    iDictionary->setFloatArray(mk(ItemType::eDictionary), halfs.data(), halfs.size());
                }
                else
                {
                    if (cc > 0) // halfX -> float[]
                    {
                        float* halfs = CARB_STACK_ALLOC(float, cc);
                        auto ptr = getDataR<pxr::GfHalf>(db.abi_context(), dataHandle);
                        for (size_t i = 0; i < cc; ++i)
                            halfs[i] = ptr[i];
                        iDictionary->setFloatArray(mk(ItemType::eDictionary), halfs, cc);
                    }
                    else
                    {
                        // half -> float
                        iDictionary->setFloat(mk(ItemType::eFloat), *getDataR<pxr::GfHalf>(db.abi_context(), dataHandle));
                    }
                }
                break;
            case BaseDataType::eInt:
                if (isArray)
                {
                    // int[] | intX[] -> int[]
                    auto nElements = getElementCount(db.abi_context(), dataHandle);
                    iDictionary->setIntArray(
                        mk(ItemType::eDictionary), *getDataR<int*>(db.abi_context(), dataHandle), nElements * cc);
                }
                else
                {
                    if (cc > 1) // intX -> int[]
                    {
                        iDictionary->setIntArray(
                            mk(ItemType::eDictionary), getDataR<int>(db.abi_context(), dataHandle), cc);
                    }
                    else
                    {
                        // int -> int
                        iDictionary->setInt(mk(ItemType::eInt), *getDataR<int>(db.abi_context(), dataHandle));
                    }
                }
                break;
            case BaseDataType::eInt64:
                if (isArray)
                {
                    // int64[] -> int64[]
                    auto nElements = getElementCount(db.abi_context(), dataHandle);
                    iDictionary->setInt64Array(
                        mk(ItemType::eDictionary), *getDataR<int64_t*>(db.abi_context(), dataHandle), nElements);
                }
                else
                {
                    // int64 -> int64
                    iDictionary->setInt64(mk(ItemType::eInt), *getDataR<int64_t>(db.abi_context(), dataHandle));
                }
                break;
            case BaseDataType::eRelationship:
                if (dataType.role == AttributeRole::eTarget) // target -> string[]
                {
                    ogn::ArrayInput<TargetPath, ogn::kCpu> targetData(
                        db.getInstanceIndex().index, AttributeRole::eTarget);
                    targetData.setContext(db.abi_context());
                    targetData.setHandle(dataHandle);
                    auto targetData0 = targetData(0);
                    auto nTargets = targetData0.size();

                    std::vector<char const*> strs(nTargets);
                    if (nTargets)
                    {
                        for (size_t i = 0; i < nTargets; ++i)
                            strs[i] = db.pathToString(targetData0[i]);
                    }
                    iDictionary->setStringArray(mk(ItemType::eDictionary), strs.data(), nTargets);
                }
                break;
            case BaseDataType::eToken:
                if (isArray)
                {
                    // token[] -> string[]
                    auto nElements = getElementCount(db.abi_context(), dataHandle);
                    std::vector<char const*> strs(nElements);
                    auto ptr = *getDataR<NameToken*>(db.abi_context(), dataHandle);
                    for (size_t i = 0; i < nElements; ++i)
                        strs[i] = db.tokenToString(ptr[i]);
                    iDictionary->setStringArray(mk(ItemType::eDictionary), strs.data(), nElements);
                }
                else
                {
                    // token -> string
                    auto const p = db.tokenToString(*getDataR<NameToken>(db.abi_context(), dataHandle));
                    iDictionary->setString(mk(ItemType::eString), p);
                }
                break;
            case BaseDataType::eUChar:
            {
                bool isTextOut = (dataType.role == AttributeRole::eText) || (dataType.role == AttributeRole::ePath);
                if (isArray && isTextOut)
                {
                    // uchar[] (string) -> string
                    size_t nElements = getElementCount(db.abi_context(), dataHandle);
                    char const* readPtr = *getDataR<char*>(db.abi_context(), dataHandle);
                    iDictionary->setString(mk(ItemType::eString), readPtr, nElements);
                }
                else if (isArray && !isTextOut)
                {
                    // uchar[] -> int[]
                    auto nElements = getElementCount(db.abi_context(), dataHandle);
                    std::vector<int32_t> ints(nElements);
                    auto ptr = *getDataR<uint8_t*>(db.abi_context(), dataHandle);
                    for (size_t i = 0; i < nElements; ++i)
                        ints[i] = ptr[i];
                    iDictionary->setIntArray(mk(ItemType::eDictionary), ints.data(), nElements);
                }
                else if (!isTextOut)
                {
                    // uchar -> int
                    iDictionary->setInt(mk(ItemType::eInt), *getDataR<uint8_t>(db.abi_context(), dataHandle));
                }
                else
                    convertOk = false;
            }
            break;
            case BaseDataType::eUInt:
                if (isArray)
                {
                    // uint[] -> int64[]
                    auto nElements = getElementCount(db.abi_context(), dataHandle);
                    std::vector<int64_t> ints(nElements);
                    auto ptr = *getDataR<uint32_t*>(db.abi_context(), dataHandle);
                    for (size_t i = 0; i < nElements; ++i)
                        ints[i] = static_cast<int64_t>(ptr[i]);
                    iDictionary->setInt64Array(mk(ItemType::eDictionary), ints.data(), ints.size());
                }
                else
                {
                    // uint -> int64
                    iDictionary->setInt64(
                        mk(ItemType::eInt), static_cast<int64_t>(*getDataR<uint32_t>(db.abi_context(), dataHandle)));
                }
                break;
            case BaseDataType::eUInt64: // warning - possible truncation
                if (isArray)
                {
                    // uint64[] -> int64[]
                    auto nElements = getElementCount(db.abi_context(), dataHandle);
                    std::vector<int64_t> ints(nElements);
                    auto ptr = *getDataR<uint64_t*>(db.abi_context(), dataHandle);
                    for (size_t i = 0; i < nElements; ++i)
                        ints[i] = static_cast<int64_t>(ptr[i]);
                    iDictionary->setInt64Array(mk(ItemType::eDictionary), ints.data(), ints.size());
                }
                else
                {
                    // uint64 -> int64
                    iDictionary->setInt64(
                        mk(ItemType::eInt), static_cast<int64_t>(*getDataR<uint64_t>(db.abi_context(), dataHandle)));
                }
                break;
            default:
                convertOk = false;
            }

            if (!convertOk)
                db.logWarning(db.getInstanceIndex(), "Could not convert attribute %s into payload data", dataName);
        }

        iApp->getMessageBusEventStream()->push(e);

        auto iActionGraph = getInterface();
        iActionGraph->setExecutionEnabled(outputs::execOut.token(), db.getInstanceIndex());
        return true;
    }
};

REGISTER_OGN_NODE();

} // omni::graph::action
