// Copyright (c) 2021-2021, NVIDIA CORPORATION. All rights reserved.
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

#include <OgnWriteAnimationGraphVariableDatabase.h>
#include <omni/timeline/ITimeline.h>
#include <ICharacter.h>
#include "PrimCommon.h"

// Helper to attempt to resolve an input attribute to the given type
bool tryResolveInputAttribute(omni::graph::core::NodeObj const& nodeObj,
                              omni::graph::core::NameToken attrName,
                              omni::graph::core::Type usdAttribType)
{
    bool usdAttribIsValid = (usdAttribType.baseType != BaseDataType::eUnknown);

    AttributeObj inAttrib{ nodeObj.iNode->getAttributeByToken(nodeObj, attrName) };
    Type valueType{ inAttrib.iAttribute->getResolvedType(inAttrib) };
    bool inputsValueResolved = (valueType.baseType != BaseDataType::eUnknown);

    bool inputsValueIsDisconnected = (inAttrib.iAttribute->getUpstreamConnectionCount(inAttrib) == 0);

    if (inputsValueIsDisconnected)
    {
        /* Disconnected logic
        +--------------+-----------+-----------+
        | inputs:value | usdAttrib |  action   |
        +--------------+-----------+-----------+
        | resolved     | null      | unresolve |
        | resolved     | conflict  | unresolve |
        | resolved     | matches   | ok        |
        | unresolved   | null      | ok        |
        | unresolved   | valid     | resolve   |
        +--------------+-----------+-----------+
        */
        if (inputsValueResolved and ((not usdAttribIsValid) or (not usdAttribType.compatibleRawData(valueType))))
        {
            inAttrib.iAttribute->setResolvedType(inAttrib, Type(BaseDataType::eUnknown));
        }

        if ((not inputsValueResolved) and usdAttribIsValid)
        {
            inAttrib.iAttribute->setResolvedType(inAttrib, usdAttribType);
        }
    }
    else if (inputsValueResolved and usdAttribIsValid and (not usdAttribType.compatibleRawData(valueType)))
    {
        ogn::OmniGraphDatabase::logError(
            nodeObj, "Type error for inputs:value connection: %s is not compatible with %s",
                                         usdAttribType.getTypeName().c_str(), valueType.getTypeName().c_str());
        return false;
    }

    return true;
}

namespace omni
{
namespace anim
{
namespace graph
{

class OgnWriteAnimationGraphVariable
{
public:
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        std::array<NameToken, 3> attribNames{ inputs::variableName.m_token, inputs::graph.m_token, inputs::value.m_token };
        for (auto const& attribName : attribNames)
        {
            AttributeObj attribObj = nodeObj.iNode->getAttributeByToken(nodeObj, attribName);
            attribObj.iAttribute->registerValueChangedCallback(attribObj, onValueChanged, true);
        }
        onValueChanged(nodeObj.iNode->getAttributeByToken(nodeObj, inputs::variableName.m_token), nullptr);
    }

    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
       onValueChanged(nodeObj.iNode->getAttributeByToken(nodeObj, inputs::variableName.m_token), nullptr);
    }

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

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        if (context.contextHandle == kInvalidGraphContextHandle)
            return;

        auto typeInterface{ carb::getCachedInterface<omni::graph::core::IAttributeType>() };

        PXR_NS::UsdAttribute attrib;
        try
        {
            attrib = omni::anim::graph::findSelectedVariable(context, nodeObj, false);
        }
        catch (std::runtime_error const&)
        {
            // Ignore errors in this callback - error will be reported at the next compute
            return;
        }

        auto typeName{ attrib ? attrib.GetTypeName().GetAsToken() : PXR_NS::TfToken() };
        Type attribType{ typeInterface->typeFromSdfTypeName(typeName.GetText()) };
        tryResolveInputAttribute(nodeObj, inputs::value.m_token, attribType);
    }

    static bool compute(OgnWriteAnimationGraphVariableDatabase& db)
    {
        if (!db.inputs.value().resolved())
            return true;

        auto timeline = omni::timeline::getTimeline(); // TODO: from context?
        if (timeline->isPlaying())
        {
            const char* skelRootPath = getSkeletonRootPath(db);
            if (skelRootPath && strlen(skelRootPath) > 0)
            {
                // todo: we should renaeme and move the Character methods onto IAnimGraph and rename to AnimGraphHandle
                auto ag = carb::getCachedInterface<omni::anim::graph::ICharacter>();
                auto character = ag->getCharacter(skelRootPath);
                if (character == Invalid)
                {
                    db.logWarning("Invalid character: '%s'", skelRootPath);
                    return state::InvalidInput;
                }
                const char* variableName = db.tokenToString(db.inputs.variableName());

                const auto ogValue = db.inputs.value();
                omni::graph::core::Type ogType = ogValue.type();

                // handle each supported data/component/array type that omni.anim.graph.core supports
                if (ogType.baseType == omni::graph::core::BaseDataType::eBool)
                {
                    if (ogType.arrayDepth == 0)
                    {
                        const auto dataObj = ogValue.get<bool>();
                        ag->setVariableBool(character, variableName, *dataObj);
                    }
                    else
                    {
                        const auto dataObj = ogValue.get<bool[]>();
                        std::vector<bool> values;
                        values.reserve(dataObj->size());
                        for (const auto& value : *dataObj)
                        {
                            values.push_back(value);
                        }
                        auto boolRef = values.front();
                        ag->setVariableBoolArray(character, variableName, { reinterpret_cast<bool*>(&boolRef), values.size() });
                    }
                }
                else if (ogType.baseType == omni::graph::core::BaseDataType::eInt)
                {
                    if (ogType.arrayDepth == 0)
                    {
                        const auto dataObj = ogValue.get<int32_t>();
                        ag->setVariableInt(character, variableName, *dataObj);
                    }
                    else
                    {
                        const auto dataObj = ogValue.get<int32_t[]>();
                        std::vector<int32_t> values;
                        values.reserve(dataObj->size());
                        for (const auto& value : *dataObj)
                        {
                            values.push_back(value);
                        }
                        ag->setVariableIntArray(character, variableName, { &values.front(), values.size() });
                    }
                }
                else if (ogType.baseType == omni::graph::core::BaseDataType::eFloat)
                {
                    if (ogType.componentCount == 1)
                    {
                        if (ogType.arrayDepth == 0)
                        {
                            const auto dataObj = ogValue.get<float>();
                            ag->setVariableFloat(character, variableName, *dataObj);
                        }
                        else
                        {
                            const auto dataObj = ogValue.get<float[]>();
                            std::vector<float> values;
                            values.reserve(dataObj->size());
                            for (const auto& value : *dataObj)
                            {
                                values.push_back(value);
                            }
                            ag->setVariableFloatArray(character, variableName, { &values.front(), values.size() });
                        }
                    }
                    else if (ogType.componentCount == 3)
                    {
                        if (ogType.arrayDepth == 0)
                        {
                            const auto dataObj = ogValue.get<float[3]>();
                            ag->setVariableFloat3(character, variableName, { dataObj[0], dataObj[1], dataObj[2] });
                        }
                        else
                        {
                            const auto dataObj = ogValue.get<float[][3]>();
                            std::vector<carb::Float3> values;
                            values.reserve(dataObj->size());
                            for (const auto& dataValue : *dataObj)
                            {
                                values.push_back({dataValue[0], dataValue[1], dataValue[2]});
                            }
                            ag->setVariableFloat3Array(character, variableName, { &values.front(), values.size() });
                        }
                    }
                    else if (ogType.componentCount == 4)
                    {
                        if (ogType.arrayDepth == 0)
                        {
                            const auto dataObj = ogValue.get<float[4]>();
                            ag->setVariableFloat4(
                                character, variableName, { dataObj[0], dataObj[1], dataObj[2], dataObj[3] });
                        }
                        else
                        {
                            const auto dataObj = ogValue.get<float[][4]>();
                            std::vector<carb::Float4> values;
                            values.reserve(dataObj->size());
                            for (const auto& dataValue : *dataObj)
                            {
                                values.push_back({dataValue[0], dataValue[1], dataValue[2], dataValue[3]});
                            }
                            ag->setVariableFloat4Array(character, variableName, { &values.front(), values.size() });
                        }
                    }
                }
                else if (ogType.baseType == omni::graph::core::BaseDataType::eToken)
                {
                    if (ogType.arrayDepth == 0)
                    {
                        const auto dataObj = ogValue.get<OgnToken>();
                        ag->setVariableString(character, variableName, db.tokenToString(*dataObj));
                    }
                    else
                    {
                        const auto dataObj = ogValue.get<OgnToken[]>();
                        std::vector<const char*> values;
                        values.reserve(dataObj->size());
                        for (const auto& value : *dataObj)
                        {
                            values.push_back(db.tokenToString(value));
                        }
                        ag->setVariableStringArray(character, variableName, { &values.front(), values.size() });
                    }
                }
                else if (ogType.baseType == omni::graph::core::BaseDataType::eUChar && ogType.role == omni::graph::core::AttributeRole::eText)
                {
                    auto const inputValueData = ogValue.get<uint8_t[]>();
                    std::string str;
                    str.reserve(inputValueData.size());
                    str.append(reinterpret_cast<char const*>(inputValueData->data()), inputValueData.size());
                    ag->setVariableString(character, variableName, str.c_str());
                }
                else
                {
                    db.logError("Unable to write animation graph variable for variableName with type: %s", ogType.getTypeName().c_str());
                    return state::InvalidInput;
                }
            }
            else
            {
                return state::InvalidInput;
            }
        }
        db.outputs.execOut() = kExecutionAttributeStateEnabled;
        return true;
    }
};

REGISTER_OGN_NODE()
}
}
}
