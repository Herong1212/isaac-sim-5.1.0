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

#include <OgnReadSettingDatabase.h>

#include <carb/settings/ISettings.h>
#include <carb/settings/SettingsUtils.h>
#include <carb/dictionary/IDictionary.h>

using carb::dictionary::ItemType;

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
void getSetting(OgnReadSettingDatabase& db)
{
    carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
    std::string strSettingPath = db.inputs.settingPath();
    char const* settingPath = strSettingPath.c_str();

    auto outputValue = db.outputs.value().template get<T>();
    *outputValue = settings->get<T>(settingPath);
}
} // namespace

class OgnReadSetting
{
public:
    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        AttributeObj attrObj = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::settingPath.m_token);
        attrObj.iAttribute->registerValueChangedCallback(attrObj, onValueChanged, true);
        onValueChanged(attrObj, nullptr);

        bool registered = nodeObj.iNode->registerConnectedCallback(nodeObj, ks_connectCallback);
        CARB_CHECK(registered, "Failed to register ConnectedCallback");

        registered = nodeObj.iNode->registerDisconnectedCallback(nodeObj, ks_disconnectCallback);
        CARB_CHECK(registered, "Failed to register DisconnectedCallback");
    }

    static void release(const NodeObj& nodeObj)
    {
        nodeObj.iNode->deregisterConnectedCallback(nodeObj, ks_connectCallback);
        nodeObj.iNode->deregisterDisconnectedCallback(nodeObj, ks_disconnectCallback);
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

        Type type(BaseDataType::eUnknown);
        auto stringLen = getElementCount(context, attrDataHandle);
        auto cstrPtrPtr = getDataR<char const*>(context, attrDataHandle);
        if (stringLen && cstrPtrPtr && *cstrPtrPtr)
        {
            std::string strSettingPath = std::string(*cstrPtrPtr, stringLen);
            try
            {
                type = resolvePathType(strSettingPath.c_str(), nodeObj);
            }
            catch (std::runtime_error const& e)
            {
                nodeObj.iNode->logComputeMessageOnInstance(
                    nodeObj, kAccordingToContextIndex, ogn::Severity::eError, e.what());
            }
        }

        omni::graph::nodes::tryResolveOutputAttribute(nodeObj, outputs::value.m_token, type);
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

    static bool compute(OgnReadSettingDatabase& db)
    {
        carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
        std::string strSettingPath = db.inputs.settingPath();
        char const* settingPath = strSettingPath.c_str();

        auto const valueType = db.outputs.value().type();
        size_t arrayLen = settings->getArrayLength(settingPath);

        // Settings arrays are not thread-safe. ISettings docs recommend using locks
        carb::settings::ScopedRead readLock;
        switch (valueType.baseType)
        {
        case BaseDataType::eBool:
            switch (valueType.arrayDepth)
            {
            case 0:
                getSetting<bool>(db);
                break;
            case 1:
            {
                auto outputValue = db.outputs.value().template get<bool[]>();
                outputValue->resize(arrayLen);
                settings->getAsBoolArray(settingPath, outputValue->data(), arrayLen);
                break;
            }
            }
            break;
        case BaseDataType::eInt:
            switch (valueType.componentCount)
            {
            case 1:
                switch (valueType.arrayDepth)
                {
                case 0:
                    getSetting<int32_t>(db);
                    break;
                case 1:
                {
                    auto outputValue = db.outputs.value().template get<int32_t[]>();
                    outputValue->resize(arrayLen);
                    settings->getAsIntArray(settingPath, outputValue->data(), arrayLen);
                    break;
                }
                }
                break;
            case 2:
            {
                auto outputValue = db.outputs.value().template get<int32_t[2]>();
                settings->getAsIntArray(settingPath, *outputValue, 2);
                break;
            }
            case 3:
            {
                auto outputValue = db.outputs.value().template get<int32_t[3]>();
                settings->getAsIntArray(settingPath, *outputValue, 3);
                break;
            }
            case 4:
            {
                auto outputValue = db.outputs.value().template get<int32_t[4]>();
                settings->getAsIntArray(settingPath, *outputValue, 4);
                break;
            }
            }
            break;
        case BaseDataType::eInt64:
            switch (valueType.arrayDepth)
            {
            case 0:
                getSetting<int64_t>(db);
                break;
            case 1:
            {
                auto outputValue = db.outputs.value().template get<int64_t[]>();
                outputValue->resize(arrayLen);
                settings->getAsInt64Array(settingPath, outputValue->data(), arrayLen);
                break;
            }
            }
            break;
        case BaseDataType::eFloat:
            switch (valueType.componentCount)
            {
            case 1:
                switch (valueType.arrayDepth)
                {
                case 0:
                    getSetting<float>(db);
                    break;
                case 1:
                {
                    auto outputValue = db.outputs.value().template get<float[]>();
                    outputValue->resize(arrayLen);
                    settings->getAsFloatArray(settingPath, outputValue->data(), arrayLen);
                    break;
                }
                }
                break;
            case 2:
            {
                auto outputValue = db.outputs.value().template get<float[2]>();
                settings->getAsFloatArray(settingPath, *outputValue, 2);
                break;
            }
            case 3:
            {
                auto outputValue = db.outputs.value().template get<float[3]>();
                settings->getAsFloatArray(settingPath, *outputValue, 3);
                break;
            }
            case 4:
            {
                auto outputValue = db.outputs.value().template get<float[4]>();
                settings->getAsFloatArray(settingPath, *outputValue, 4);
                break;
            }
            }
            break;
        case BaseDataType::eDouble:
            switch (valueType.componentCount)
            {
            case 1:
                switch (valueType.arrayDepth)
                {
                case 0:
                    getSetting<double>(db);
                    break;
                case 1:
                {
                    auto outputValue = db.outputs.value().template get<double[]>();
                    outputValue->resize(arrayLen);
                    settings->getAsFloat64Array(settingPath, outputValue->data(), arrayLen);
                    break;
                }
                }
                break;
            case 2:
            {
                auto outputValue = db.outputs.value().template get<double[2]>();
                settings->getAsFloat64Array(settingPath, *outputValue, 2);
                break;
            }
            case 3:
            {
                auto outputValue = db.outputs.value().template get<double[3]>();
                settings->getAsFloat64Array(settingPath, *outputValue, 3);
                break;
            }
            case 4:
            {
                auto outputValue = db.outputs.value().template get<double[4]>();
                settings->getAsFloat64Array(settingPath, *outputValue, 4);
                break;
            }
            }
            break;
        case BaseDataType::eToken:
            switch (valueType.arrayDepth)
            {
            case 0:
            {
                auto outputValue = db.outputs.value().template get<OgnToken>();
                std::string stringSetting = carb::settings::getString(settings, settingPath);
                *outputValue = db.stringToToken(stringSetting.c_str());
                break;
            }
            case 1:
            {
                auto outputValue = db.outputs.value().template get<OgnToken[]>();
                outputValue->resize(arrayLen);
                std::vector<std::string> stringSetting = carb::settings::getStringArray(settings, settingPath);
                for (size_t i = 0; i < arrayLen; i++)
                    (*outputValue)[i] = db.stringToToken(stringSetting[i].c_str());
                break;
            }
            }
            break;
        default:
        {
            db.logError("Type %s not supported", getOgnTypeName(valueType).c_str());
            return false;
        }
        }

        return true;
    }

private:
    BaseDataType m_connectedType = BaseDataType::eUnknown;

    /**
     * Resolves the path type to the connected data type if the path is a string type, otherwise use the path
     * type directly.
     *
     * @param settinPath path of the setting
     * @param nodeObj node object containing connectedType state
     * @return converted Type
     */
    static Type resolvePathType(const char* settingPath, NodeObj const& nodeObj)
    {
        const auto& state = OgnReadSettingDatabase::sSharedState<OgnReadSetting>(nodeObj);
        BaseDataType connectedType = state.m_connectedType;
        Type type = omni::graph::nodes::getSettingType(settingPath, true);

        // For string types, if the connected type is set, we use it and rely on casting
        if (type.baseType == BaseDataType::eToken && connectedType != BaseDataType::eUnknown)
        {
            CARB_LOG_VERBOSE("OGNReadSetting Using connected BaseDataType %s for %s",
                             omni::fabric::getBaseTypeName(connectedType).c_str(), settingPath);
            type.baseType = connectedType;
        }

        return type;
    }

    static void connected(const omni::graph::core::AttributeObj& srcAttr,
                          const omni::graph::core::AttributeObj& dstAttr,
                          bool connected)
    {

        if (!dstAttr.isValid())
        {
            CARB_LOG_ERROR("connection dstAttr is invalid");
            return;
        }
        if (!srcAttr.isValid())
        {
            CARB_LOG_ERROR("connection srcAttr is invalid");
            return;
        }

        const char* srcAttrTypeName = srcAttr.iAttribute->getName(srcAttr);

        auto srcNode = srcAttr.iAttribute->getNode(srcAttr);
        if (!srcNode.isValid())
        {
            CARB_LOG_ERROR("srcAttr: %s, source node is invalid", srcAttrTypeName);
            return;
        }

        NodeTypeObj srcNodeTypeObj = srcNode.iNode->getNodeTypeObj(srcNode);
        if (!srcNodeTypeObj.isValid())
        {
            CARB_LOG_ERROR("srcAttr: %s, source nodeTypeObj is invalid", srcAttrTypeName);
            return;
        }

        const char* srcNodeTypeName = srcNodeTypeObj.iNodeType->getTypeName(srcNodeTypeObj);
        const auto& srcAttrTokenNoPort =
            srcAttr.iAttribute->removePortTypeFromName(srcAttr.iAttribute->getNameToken(srcAttr), false);

        // Only process this callback if we are the src node, to get the connected type
        if ((srcAttrTokenNoPort != srcAttr.iAttribute->removePortTypeFromName(outputs::value.token(), false)) ||
            (strcmp(srcNodeTypeName, "omni.graph.nodes.ReadSetting") != 0))
        {
            return;
        }

        // Set connected type
        auto& state = OgnReadSettingDatabase::sSharedState<OgnReadSetting>(srcNode);

        if (connected)
        {
            state.m_connectedType = dstAttr.iAttribute->getResolvedType(dstAttr).baseType;
            CARB_LOG_VERBOSE("OGNReadSetting Connected, found connected type %s",
                             omni::fabric::getBaseTypeName(state.m_connectedType).c_str());
        }
        else
        {
            state.m_connectedType = BaseDataType::eUnknown;
            CARB_LOG_VERBOSE("OGNReadSetting Disconnected cleared connected type");
        }
        onConnectionTypeResolve(srcNode);
    }

    static void connectionCallback(const omni::graph::core::AttributeObj& srcAttr,
                                   const omni::graph::core::AttributeObj& dstAttr,
                                   void*)
    {
        connected(srcAttr, dstAttr, true);
    }

    static void disconnectionCallback(const omni::graph::core::AttributeObj& srcAttr,
                                      const omni::graph::core::AttributeObj& dstAttr,
                                      void*)
    {
        connected(srcAttr, dstAttr, false);
    }

    constexpr static omni::graph::core::ConnectionCallback ks_connectCallback{ connectionCallback, nullptr };
    constexpr static omni::graph::core::ConnectionCallback ks_disconnectCallback{ disconnectionCallback, nullptr };
};

REGISTER_OGN_NODE()
} // namespace nodes
} // namespace graph
} // namespace omni
