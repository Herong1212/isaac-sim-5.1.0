#pragma once

#include <omni/graph/core/ISchedulingHints2.h>
#include <carb/InterfaceUtils.h>
#include <omni/graph/core/NodeTypeRegistrar.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/CppWrappers.h>
#include <omni/fabric/Enums.h>
using omni::fabric::PtrToPtrKind;
#include <map>
#include <vector>
#include <tuple>
#include <omni/graph/core/OgnHelpers.h>
#include <array>
#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/ArrayAttribute.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>

namespace SaveVDBAttributes
{
namespace inputs
{
using assetPath_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> assetPath("inputs:assetPath", "token", kExtendedAttributeType_Regular);
using compressionMode_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> compressionMode("inputs:compressionMode", "token", kExtendedAttributeType_Regular);
using data_t = const ogn::const_array<uint32_t>&;
ogn::AttributeInitializer<const uint32_t*, ogn::kOgnInput> data("inputs:data", "uint[]", kExtendedAttributeType_Regular, nullptr, 0);
using execIn_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> execIn("inputs:execIn", "execution", kExtendedAttributeType_Regular);
}
namespace outputs
{
using execOut_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> execOut("outputs:execOut", "execution", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace SaveVDBAttributes;
namespace ISaveVDB
{
// Saves a VDB from file and puts it in a memory buffer.
class SaveVDBDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken none;
        NameToken blosc;
        NameToken zip;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerSaveVDB.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerSaveVDB.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerSaveVDB.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerSaveVDB.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
    }
    template <typename StateInformation>
    CARB_DEPRECATED("internalState is deprecated. Use sharedState or perInstanceState instead")
    StateInformation& internalState(size_t relativeIdx = 0) {
        return sInternalState<StateInformation>(abi_node(), m_offset + relativeIdx);
    }
    template <typename StateInformation>
    StateInformation& sharedState() {
        return sSharedState<StateInformation>(abi_node());
    }
    template <typename StateInformation>
    StateInformation& perInstanceState(size_t relativeIdx = 0) {
        return sPerInstanceState<StateInformation>(abi_node(), m_offset + relativeIdx);
    }
    template <typename StateInformation>
    StateInformation& perInstanceState(GraphInstanceID instanceId) {
        return sPerInstanceState<StateInformation>(abi_node(), instanceId);
    }
    static ogn::StateManager sm_stateManagerSaveVDB;
    static std::tuple<int, int, int>sm_generatorVersionSaveVDB;
    static std::tuple<int, int, int>sm_targetVersionSaveVDB;
    static constexpr size_t staticAttributeCount = 7;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : assetPath{offset}
        , compressionMode{offset}
        , data{offset}
        , execIn{offset,AttributeRole::eExecution}
        {}
        ogn::SimpleInput<const NameToken,ogn::kCpu> assetPath;
        ogn::SimpleInput<const NameToken,ogn::kCpu> compressionMode;
        bool has_compressionMode() const { return compressionMode.isValid(); };
        ogn::ArrayInput<const uint32_t,ogn::kCpu> data;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> execIn;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : execOut{offset,AttributeRole::eExecution}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> execOut;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    SaveVDBDatabase(NodeObj const& nodeObjParam)
    : OmniGraphDatabase()
    , inputs{m_offset.index}
    , outputs{m_offset.index}
    {
        GraphContextObj const* contexts = nullptr;
        NodeObj const* nodes = nullptr;
        size_t handleCount = nodeObjParam.iNode->getAutoInstances(nodeObjParam, contexts, nodes);
        _ctor(contexts, nodes, handleCount);
        _init();
    }

    CARB_DEPRECATED("Passing the graph context to the temporary stack allocated database is not necessary anymore: you can safely remove this parameter")
    SaveVDBDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : SaveVDBDatabase(nodeObjParam)
    {}

    //Main constructor
    SaveVDBDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
    : OmniGraphDatabase()
    , inputs{m_offset.index}
    , outputs{m_offset.index}
    {
        _ctor(contextObjParam, nodeObjParam, handleCount);
        _init();
    }

private:
    void _init() {
        GraphContextObj const& contextObj = abi_context();
        NodeObj const& nodeObj = abi_node();
        {
            auto inputDataHandles0 = getAttributesR<
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::assetPath.m_token, inputs::compressionMode.m_token, inputs::data.m_token, inputs::execIn.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::execOut.m_token
                )
            , kAccordingToContextIndex);
            inputs.assetPath.setContext(contextObj);
            inputs.assetPath.setHandle(std::get<0>(inputDataHandles0));
            inputs.compressionMode.setContext(contextObj);
            inputs.compressionMode.setHandle(std::get<1>(inputDataHandles0));
            inputs.data.setContext(contextObj);
            inputs.data.setHandle(std::get<2>(inputDataHandles0));
            inputs.execIn.setContext(contextObj);
            inputs.execIn.setHandle(std::get<3>(inputDataHandles0));
            outputs.execOut.setContext(contextObj);
            outputs.execOut.setHandle(std::get<0>(outputDataHandles0));
        }
        tryGetDynamicAttributes<AttributePortType::kAttributePortType_Input>(staticAttributeCount, m_dynamicInputs);
        tryGetDynamicAttributes<AttributePortType::kAttributePortType_Output>(staticAttributeCount, m_dynamicOutputs);
        tryGetDynamicAttributes<AttributePortType::kAttributePortType_State>(staticAttributeCount, m_dynamicStates);

        collectMappedAttributes(m_mappedAttributes);

        m_canCachePointers = contextObj.iContext->canCacheAttributePointers ?
                                 contextObj.iContext->canCacheAttributePointers(contextObj) : true;
    }

public:
    static void initializeType(const NodeTypeObj& nodeTypeObj)
    {
        const INodeType* iNodeType = nodeTypeObj.iNodeType;
        auto iTokenPtr = carb::getCachedInterface<omni::fabric::IToken>();
        if( ! iTokenPtr ) {
            CARB_LOG_ERROR("IToken not found when initializing omni.volume.SaveVDB");
            return;
        }
        auto& iToken{ *iTokenPtr };
        SaveVDBDatabase::tokens.none = iToken.getHandle("None");
        SaveVDBDatabase::tokens.blosc = iToken.getHandle("Blosc");
        SaveVDBDatabase::tokens.zip = iToken.getHandle("Zip");

        inputs::assetPath.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::compressionMode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::data.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::execIn.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::execOut.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.volume_nodes");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTags, "VDB");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataUiName, "Save VDB");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "{\"none\": \"None\", \"blosc\": \"Blosc\", \"zip\": \"Zip\"}");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "Omni Volume");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Saves a VDB from file and puts it in a memory buffer.");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExclusions, "tests");
        auto __schedulingInfo = nodeTypeObj.iNodeType->getSchedulingHints(nodeTypeObj);
        CARB_ASSERT(__schedulingInfo, "Could not acquire the scheduling hints");
        if (__schedulingInfo)
        {
            __schedulingInfo->setDataAccess(eAccessLocation::eGlobal, eAccessType::eWrite);
            auto __schedulingInfo2 = omni::core::cast<ISchedulingHints2>(__schedulingInfo).get();
            if (__schedulingInfo2)
            {
            }
        }
        iNodeType->setHasState(nodeTypeObj, true);
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::assetPath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Path to VDB file to save.");
        attr = iNode->getAttributeByToken(nodeObj, inputs::compressionMode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The compression mode to use when encoding");
        attr.iAttribute->setMetadata(attr, kOgnMetadataAllowedTokens, "None,Blosc,Zip");
        attr.iAttribute->setMetadata(attr, "default", "None");
        attr.iAttribute->setMetadata(attr, kOgnMetadataAllowedTokensRaw, "{\"none\": \"None\", \"blosc\": \"Blosc\", \"zip\": \"Zip\"}");
        attr.iAttribute->setIsOptionalForCompute(attr, true);
        attr = iNode->getAttributeByToken(nodeObj, inputs::data.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Data to save to file in NanoVDB or OpenVDB memory format.");
        attr = iNode->getAttributeByToken(nodeObj, inputs::execIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Input execution");
        attr = iNode->getAttributeByToken(nodeObj, outputs::execOut.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Output execution");
    }
    std::vector<ogn::DynamicInput> const& getDynamicInputs() const
    {
        return m_dynamicInputs;
    }
    gsl::span<ogn::DynamicOutput> getDynamicOutputs()
    {
        return m_dynamicOutputs;
    }
    gsl::span<ogn::DynamicState> getDynamicStates()
    {
        return m_dynamicStates;
    }
    static void release(const NodeObj& nodeObj, GraphInstanceID instanceID)
    {
        sm_stateManagerSaveVDB.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.assetPath.isValid()
            && inputs.data.isValid()
            && inputs.execIn.isValid()
            && outputs.execOut.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.assetPath.invalidateCachedPointer();
            inputs.compressionMode.invalidateCachedPointer();
            inputs.data.invalidateCachedPointer();
            inputs.execIn.invalidateCachedPointer();
            outputs.execOut.invalidateCachedPointer();
            return;
        }
        inputs.data.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::assetPath.m_token) {
                inputs.assetPath.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::compressionMode.m_token) {
                inputs.compressionMode.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::data.m_token) {
                inputs.data.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::execIn.m_token) {
                inputs.execIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::execOut.m_token) {
                outputs.execOut.invalidateCachedPointer();
                continue;
            }
            bool found = false;
            for (auto& __a : m_dynamicInputs) {
                if (__a().name() == attrib) {
                    __a.invalidateCachedPointer();
                    found = true;
                    break;
                }
            }
            if(found) continue;
            for (auto& __a : m_dynamicOutputs) {
                if (__a().name() == attrib) {
                    __a.invalidateCachedPointer();
                    found = true;
                    break;
                }
            }
            if(found) continue;
            for (auto& __a : m_dynamicStates) {
                if (__a().name() == attrib) {
                    __a.invalidateCachedPointer();
                    found = true;
                    break;
                }
            }
            if(found) continue;
        }
    }
    bool canVectorize() const {
        if( !inputs.assetPath.canVectorize()
            || !inputs.compressionMode.canVectorize()
            || !inputs.execIn.canVectorize()
            || !outputs.execOut.canVectorize()
        ) return false;
        for (auto const& __a : m_dynamicInputs) {
            if(!__a.canVectorize()) return false;
        }
        for (auto const& __a : m_dynamicOutputs) {
            if(!__a.canVectorize()) return false;
        }
        for (auto const& __a : m_dynamicStates) {
            if(!__a.canVectorize()) return false;
        }
        return true;
    }
    void onTypeResolutionChanged(AttributeObj const& attr) {
        if (! attr.isValid()) return;
        NameToken token = attr.iAttribute->getNameToken(attr);
        for (auto& __a : m_dynamicInputs) {
            if (__a().name() == token) {
                __a.fetchDetails(attr);
                return;
            }
        }
        for (auto& __a : m_dynamicOutputs) {
            if (__a().name() == token) {
                __a.fetchDetails(attr);
                return;
            }
        }
        for (auto& __a : m_dynamicStates) {
            if (__a().name() == token) {
                __a.fetchDetails(attr);
                return;
            }
        }
    }
    void onDynamicAttributesChanged(AttributeObj const& attribute, bool isAttributeCreated) {
        onDynamicAttributeCreatedOrRemoved(m_dynamicInputs, m_dynamicOutputs, m_dynamicStates, attribute, isAttributeCreated);
    }
    void onDataLocationChanged(AttributeObj const& attr) {
        if (! attr.isValid()) return;
        updateMappedAttributes(m_mappedAttributes, attr);
        NameToken token = attr.iAttribute->getNameToken(attr);
        if(token == inputs::assetPath.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.assetPath.setHandle(hdl);
            return;
        }
        if(token == inputs::compressionMode.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.compressionMode.setHandle(hdl);
            return;
        }
        if(token == inputs::data.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.data.setHandle(hdl);
            return;
        }
        if(token == inputs::execIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.execIn.setHandle(hdl);
            return;
        }
        if(token == outputs::execOut.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.execOut.setHandle(hdl);
            return;
        }
        for (auto& __a : m_dynamicInputs) {
            if (__a().name() == token) {
                __a.fetchDetails(attr);
                return;
            }
        }
        for (auto& __a : m_dynamicOutputs) {
            if (__a().name() == token) {
                __a.fetchDetails(attr);
                return;
            }
        }
        for (auto& __a : m_dynamicStates) {
            if (__a().name() == token) {
                __a.fetchDetails(attr);
                return;
            }
        }
    }
};
ogn::StateManager SaveVDBDatabase::sm_stateManagerSaveVDB;
std::tuple<int, int, int> SaveVDBDatabase::sm_generatorVersionSaveVDB{std::make_tuple(1,79,2)};
std::tuple<int, int, int> SaveVDBDatabase::sm_targetVersionSaveVDB{std::make_tuple(2,184,5)};
SaveVDBDatabase::TokenManager SaveVDBDatabase::tokens;
}
using namespace ISaveVDB;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<SaveVDB, SaveVDBDatabase> s_registration("omni.volume.SaveVDB", 1, "omni.volume_nodes"); \
}
