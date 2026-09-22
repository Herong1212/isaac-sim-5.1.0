// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include "PrimCommon.h"

#include <OgnWriteSettingDatabase.h>
#include <carb/settings/ISettings.h>
#include <carb/settings/SettingsUtils.h>
#include <carb/dictionary/IDictionary.h>
#include <omni/graph/core/ogn/TypeConversion.h>

namespace omni
{
namespace graph
{
namespace nodes
{
// unnamed namespace to avoid multiple declaration when linking
namespace
{

template <typename T>
void setSetting(OgnWriteSettingDatabase& db, const char* settingPath)
{
    carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
    auto const inputValue = db.inputs.value().template get<T>();
    settings->set(settingPath, *inputValue);
}

template <typename T>
void setSettingArray(OgnWriteSettingDatabase& db, const char* settingPath)
{
    carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
    auto const inputValue = db.inputs.value().template get<T[]>();
    size_t arrayLen = db.inputs.value().size();
    settings->setArray(settingPath, inputValue->data(), arrayLen);
}

template <typename T, size_t N>
void setSettingArray(OgnWriteSettingDatabase& db, const char* settingPath)
{
    carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
    auto const inputValue = db.inputs.value().template get<T[N]>();
    settings->setArray(settingPath, *inputValue, N);
}

template <>
void setSetting<OgnToken>(OgnWriteSettingDatabase& db, const char* settingPath)
{
    carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
    auto const inputValue = db.inputs.value().template get<OgnToken>();
    char const* inputString = db.tokenToString(*inputValue);
    settings->set(settingPath, inputString);
}

template <>
void setSettingArray<OgnToken>(OgnWriteSettingDatabase& db, const char* settingPath)
{
    carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
    auto const inputValue = db.inputs.value().template get<OgnToken[]>();
    std::vector<char const*> inputString(inputValue.size());
    for (size_t i = 0; i < inputValue.size(); i++)
        inputString[i] = db.tokenToString((*inputValue)[i]);
    settings->setArray(settingPath, inputString.data(), inputString.size());
}

} // namespace

class OgnWriteSetting
{
public:
    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        AttributeObj attrObj = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::settingPath.m_token);
        attrObj.iAttribute->registerValueChangedCallback(attrObj, onValueChanged, true);
        onValueChanged(attrObj, nullptr);
    }

    // ----------------------------------------------------------------------------
    // Called by OG to resolve the input type
    static void onConnectionTypeResolve(NodeObj const& nodeObj)
    {
        auto attrObj = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::settingPath.m_token);

        auto graphObj = nodeObj.iNode->getGraph(nodeObj);
        if (graphObj.graphHandle == kInvalidGraphHandle)
            return;

        auto context = graphObj.iGraph->getDefaultGraphContext(graphObj);
        if (context.contextHandle == kInvalidGraphContextHandle)
            return;

        ConstAttributeDataHandle attrDataHandle =
            attrObj.iAttribute->getAttributeDataHandle(attrObj, kAccordingToContextIndex);
        if (!attrDataHandle.isValid())
            return;

        auto stringLen = getElementCount(context, attrDataHandle);
        auto cstrPtrPtr = getDataR<char const*>(context, attrDataHandle);
        if (stringLen && cstrPtrPtr && *cstrPtrPtr)
        {
            try
            {
                std::string settingPath{ *cstrPtrPtr, stringLen };
                Type type{ BaseDataType::eUnknown };
                if (settingPath.size() > 1)
                    type = omni::graph::nodes::getSettingType(settingPath.c_str(), true);
                omni::graph::nodes::tryResolveInputAttribute(nodeObj, inputs::value.m_token, type);
            }
            catch (std::runtime_error const& e)
            {
                nodeObj.iNode->logComputeMessageOnInstance(
                    nodeObj, kAccordingToContextIndex, ogn::Severity::eWarning, e.what());
            }
        }
    }

    // ----------------------------------------------------------------------------
    // Called by OG when the value of the settingPath changes
    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        auto nodeObj = attrObj.iAttribute->getNode(attrObj);
        if (nodeObj.nodeHandle == kInvalidNodeHandle)
            return;

        onConnectionTypeResolve(nodeObj);
    }

    static bool compute(OgnWriteSettingDatabase& db)
    {
        auto const valueType = db.inputs.value().type();
        std::string strSettingPath = (std::string)db.inputs.settingPath();
        const char* settingPath = strSettingPath.c_str();

        Type pathType;
        try
        {
            pathType = omni::graph::nodes::getSettingType(settingPath, true);
            if (!ogn::areTypesCompatible(valueType, pathType))
            {
                std::stringstream ss;
                ss << valueType;
                db.logError("Setting Path '%s' is not compatible with type '%s'", settingPath, ss.str());
                return false;
            }
        }
        catch (std::runtime_error const& e)
        {
            db.logWarning(e.what());
        }

        switch (valueType.baseType)
        {
        case BaseDataType::eBool:
            switch (valueType.arrayDepth)
            {
            case 0:
                setSetting<bool>(db, settingPath);
                break;
            case 1:
                setSettingArray<bool>(db, settingPath);
                break;
            }
            break;
        case BaseDataType::eInt:
            switch (valueType.componentCount)
            {
            case 1:
                switch (valueType.arrayDepth)
                {
                case 0:
                    setSetting<int32_t>(db, settingPath);
                    break;
                case 1:
                    setSettingArray<int32_t>(db, settingPath);
                    break;
                }
                break;
            case 2:
                setSettingArray<int32_t, 2>(db, settingPath);
                break;
            case 3:
                setSettingArray<int32_t, 3>(db, settingPath);
                break;
            case 4:
                setSettingArray<int32_t, 4>(db, settingPath);
                break;
            }
            break;
        case BaseDataType::eInt64:
            switch (valueType.arrayDepth)
            {
            case 0:
                setSetting<int64_t>(db, settingPath);
                break;
            case 1:
                setSettingArray<int64_t>(db, settingPath);
                break;
            }
            break;
        case BaseDataType::eFloat:
            switch (valueType.componentCount)
            {
            case 1:
                switch (valueType.arrayDepth)
                {
                case 0:
                    setSetting<float>(db, settingPath);
                    break;
                case 1:
                    setSettingArray<float>(db, settingPath);
                    break;
                }
                break;
            case 2:
                setSettingArray<float, 2>(db, settingPath);
                break;
            case 3:
                setSettingArray<float, 3>(db, settingPath);
                break;
            case 4:
                setSettingArray<float, 4>(db, settingPath);
                break;
            }
            break;
        case BaseDataType::eDouble:
            switch (valueType.componentCount)
            {
            case 1:
                switch (valueType.arrayDepth)
                {
                case 0:
                    setSetting<double>(db, settingPath);
                    break;
                case 1:
                    setSettingArray<double>(db, settingPath);
                    break;
                }
                break;
            case 2:
                setSettingArray<double, 2>(db, settingPath);
                break;
            case 3:
                setSettingArray<double, 3>(db, settingPath);
                break;
            case 4:
                setSettingArray<double, 4>(db, settingPath);
                break;
            }
            break;
        case BaseDataType::eToken:
            switch (valueType.arrayDepth)
            {
            case 0:
                setSetting<OgnToken>(db, settingPath);
                break;
            case 1:
                setSettingArray<OgnToken>(db, settingPath);
                break;
            }
            break;
        default:
        {
            db.logError("Type %s not supported", getOgnTypeName(valueType).c_str());
            return false;
        }
        }

        db.outputs.execOut() = kExecutionAttributeStateEnabled;

        return true;
    }
};

REGISTER_OGN_NODE()
} // namespace nodes
} // namespace graph
} // namespace omni
