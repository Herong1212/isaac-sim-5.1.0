#pragma once

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

namespace TranscoderRadarAttributes
{
namespace inputs
{
using cudaStream_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaStream("inputs:cudaStream", "uint64", kExtendedAttributeType_Regular, 0);
using decoderPath_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> decoderPath("inputs:decoderPath", "string", kExtendedAttributeType_Regular, "/usr/local/driveworks/bin/libsample_radar_plugin_new.so", 55);
using device_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> device("inputs:device", "string", kExtendedAttributeType_Regular, "CONTINENTAL_ARS430", 18);
using dumpPackets_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> dumpPackets("inputs:dumpPackets", "bool", kExtendedAttributeType_Regular, false);
using eventIDs_t = const ogn::const_array<int>&;
ogn::AttributeInitializer<const int*, ogn::kOgnInput> eventIDs("inputs:eventIDs", "int[]", kExtendedAttributeType_Regular, nullptr, 0);
using eventTypes_t = const ogn::const_array<int>&;
ogn::AttributeInitializer<const int*, ogn::kOgnInput> eventTypes("inputs:eventTypes", "int[]", kExtendedAttributeType_Regular, nullptr, 0);
using fileName_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> fileName("inputs:fileName", "string", kExtendedAttributeType_Regular, "", 0);
using format_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> format("inputs:format", "string", kExtendedAttributeType_Regular, "RDI_1_0_8_V2", 12);
using interfaceIP_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> interfaceIP("inputs:interfaceIP", "string", kExtendedAttributeType_Regular, "127.0.0.1", 9);
using messageTypes_t = const ogn::const_array<int>&;
ogn::AttributeInitializer<const int*, ogn::kOgnInput> messageTypes("inputs:messageTypes", "int[]", kExtendedAttributeType_Regular, nullptr, 0);
using meta_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> meta("inputs:meta", "uint64", kExtendedAttributeType_Regular, 0);
using remoteIP_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> remoteIP("inputs:remoteIP", "string", kExtendedAttributeType_Regular, "239.0.0.1", 9);
using remotePort_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> remotePort("inputs:remotePort", "int", kExtendedAttributeType_Regular, 10001);
using serviceID_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> serviceID("inputs:serviceID", "uint64", kExtendedAttributeType_Regular, 2726985729);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace TranscoderRadarAttributes;
namespace ITranscoderRadar
{
// Transcodes RTSensor buffer data to sensor specific formats and dumps in file
class TranscoderRadarDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerTranscoderRadar.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerTranscoderRadar.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerTranscoderRadar.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerTranscoderRadar.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerTranscoderRadar;
    static std::tuple<int, int, int>sm_generatorVersionTranscoderRadar;
    static std::tuple<int, int, int>sm_targetVersionTranscoderRadar;
    static constexpr size_t staticAttributeCount = 17;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : cudaStream{offset}
        , decoderPath{offset,AttributeRole::eText}
        , device{offset,AttributeRole::eText}
        , dumpPackets{offset}
        , eventIDs{offset}
        , eventTypes{offset}
        , fileName{offset,AttributeRole::eText}
        , format{offset,AttributeRole::eText}
        , interfaceIP{offset,AttributeRole::eText}
        , messageTypes{offset}
        , meta{offset}
        , remoteIP{offset,AttributeRole::eText}
        , remotePort{offset}
        , serviceID{offset}
        , src{offset}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaStream;
        ogn::ArrayInput<const char,ogn::kCpu> decoderPath;
        ogn::ArrayInput<const char,ogn::kCpu> device;
        ogn::SimpleInput<const bool,ogn::kCpu> dumpPackets;
        ogn::ArrayInput<const int,ogn::kCpu> eventIDs;
        ogn::ArrayInput<const int,ogn::kCpu> eventTypes;
        ogn::ArrayInput<const char,ogn::kCpu> fileName;
        ogn::ArrayInput<const char,ogn::kCpu> format;
        ogn::ArrayInput<const char,ogn::kCpu> interfaceIP;
        ogn::ArrayInput<const int,ogn::kCpu> messageTypes;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> meta;
        ogn::ArrayInput<const char,ogn::kCpu> remoteIP;
        ogn::SimpleInput<const int,ogn::kCpu> remotePort;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> serviceID;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    TranscoderRadarDatabase(NodeObj const& nodeObjParam)
    : OmniGraphDatabase()
    , inputs{m_offset.index}
    {
        GraphContextObj const* contexts = nullptr;
        NodeObj const* nodes = nullptr;
        size_t handleCount = nodeObjParam.iNode->getAutoInstances(nodeObjParam, contexts, nodes);
        _ctor(contexts, nodes, handleCount);
        _init();
    }

    CARB_DEPRECATED("Passing the graph context to the temporary stack allocated database is not necessary anymore: you can safely remove this parameter")
    TranscoderRadarDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : TranscoderRadarDatabase(nodeObjParam)
    {}

    //Main constructor
    TranscoderRadarDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
    : OmniGraphDatabase()
    , inputs{m_offset.index}
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::cudaStream.m_token, inputs::decoderPath.m_token, inputs::device.m_token, inputs::dumpPackets.m_token,
                    inputs::eventIDs.m_token, inputs::eventTypes.m_token, inputs::fileName.m_token, inputs::format.m_token,
                    inputs::interfaceIP.m_token, inputs::messageTypes.m_token, inputs::meta.m_token, inputs::remoteIP.m_token,
                    inputs::remotePort.m_token, inputs::serviceID.m_token, inputs::src.m_token
                )
            , kAccordingToContextIndex);
            inputs.cudaStream.setContext(contextObj);
            inputs.cudaStream.setHandle(std::get<0>(inputDataHandles0));
            inputs.decoderPath.setContext(contextObj);
            inputs.decoderPath.setHandle(std::get<1>(inputDataHandles0));
            inputs.device.setContext(contextObj);
            inputs.device.setHandle(std::get<2>(inputDataHandles0));
            inputs.dumpPackets.setContext(contextObj);
            inputs.dumpPackets.setHandle(std::get<3>(inputDataHandles0));
            inputs.eventIDs.setContext(contextObj);
            inputs.eventIDs.setHandle(std::get<4>(inputDataHandles0));
            inputs.eventTypes.setContext(contextObj);
            inputs.eventTypes.setHandle(std::get<5>(inputDataHandles0));
            inputs.fileName.setContext(contextObj);
            inputs.fileName.setHandle(std::get<6>(inputDataHandles0));
            inputs.format.setContext(contextObj);
            inputs.format.setHandle(std::get<7>(inputDataHandles0));
            inputs.interfaceIP.setContext(contextObj);
            inputs.interfaceIP.setHandle(std::get<8>(inputDataHandles0));
            inputs.messageTypes.setContext(contextObj);
            inputs.messageTypes.setHandle(std::get<9>(inputDataHandles0));
            inputs.meta.setContext(contextObj);
            inputs.meta.setHandle(std::get<10>(inputDataHandles0));
            inputs.remoteIP.setContext(contextObj);
            inputs.remoteIP.setHandle(std::get<11>(inputDataHandles0));
            inputs.remotePort.setContext(contextObj);
            inputs.remotePort.setHandle(std::get<12>(inputDataHandles0));
            inputs.serviceID.setContext(contextObj);
            inputs.serviceID.setHandle(std::get<13>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<14>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.radar.TranscoderRadar");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::cudaStream.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::decoderPath.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::device.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::dumpPackets.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::eventIDs.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::eventTypes.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::fileName.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::format.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::interfaceIP.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::messageTypes.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::meta.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::remoteIP.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::remotePort.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::serviceID.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.radar");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Transcodes RTSensor buffer data to sensor specific formats and dumps in file");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda Stream Input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::decoderPath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "decoder path id");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"/usr/local/driveworks/bin/libsample_radar_plugin_new.so\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::device.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "device id");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"CONTINENTAL_ARS430\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::dumpPackets.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Dump packets as dwBinFile");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::eventIDs.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Event IDs from SOME/IP Header 1. Only for NCD transcoders.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::eventTypes.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Event Types of their respective Event ID from SOME/IP Header 1. Only for NCD transcoders.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::fileName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "File name of the dwBinFile");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::format.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "format used for sent data");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"RDI_1_0_8_V2\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::interfaceIP.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "local interface to use");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"127.0.0.1\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::messageTypes.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "message Types of their respective Event ID from SOME/IP Header 1. Only for NCD transcoders.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::meta.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Meta Data");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::remoteIP.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Remote IP of UDP channel");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"239.0.0.1\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::remotePort.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Remote port of UDP channel");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "10001");
        attr = iNode->getAttributeByToken(nodeObj, inputs::serviceID.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Service ID and Method ID from SOME/IP Header 1. Only for NCD transcoders.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "2726985729");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
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
        sm_stateManagerTranscoderRadar.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cudaStream.isValid()
            && inputs.decoderPath.isValid()
            && inputs.device.isValid()
            && inputs.dumpPackets.isValid()
            && inputs.eventIDs.isValid()
            && inputs.eventTypes.isValid()
            && inputs.fileName.isValid()
            && inputs.format.isValid()
            && inputs.interfaceIP.isValid()
            && inputs.messageTypes.isValid()
            && inputs.meta.isValid()
            && inputs.remoteIP.isValid()
            && inputs.remotePort.isValid()
            && inputs.serviceID.isValid()
            && inputs.src.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cudaStream.invalidateCachedPointer();
            inputs.decoderPath.invalidateCachedPointer();
            inputs.device.invalidateCachedPointer();
            inputs.dumpPackets.invalidateCachedPointer();
            inputs.eventIDs.invalidateCachedPointer();
            inputs.eventTypes.invalidateCachedPointer();
            inputs.fileName.invalidateCachedPointer();
            inputs.format.invalidateCachedPointer();
            inputs.interfaceIP.invalidateCachedPointer();
            inputs.messageTypes.invalidateCachedPointer();
            inputs.meta.invalidateCachedPointer();
            inputs.remoteIP.invalidateCachedPointer();
            inputs.remotePort.invalidateCachedPointer();
            inputs.serviceID.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            return;
        }
        inputs.decoderPath.invalidateCachedPointer();
        inputs.device.invalidateCachedPointer();
        inputs.eventIDs.invalidateCachedPointer();
        inputs.eventTypes.invalidateCachedPointer();
        inputs.fileName.invalidateCachedPointer();
        inputs.format.invalidateCachedPointer();
        inputs.interfaceIP.invalidateCachedPointer();
        inputs.messageTypes.invalidateCachedPointer();
        inputs.remoteIP.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cudaStream.m_token) {
                inputs.cudaStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::decoderPath.m_token) {
                inputs.decoderPath.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::device.m_token) {
                inputs.device.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::dumpPackets.m_token) {
                inputs.dumpPackets.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::eventIDs.m_token) {
                inputs.eventIDs.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::eventTypes.m_token) {
                inputs.eventTypes.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::fileName.m_token) {
                inputs.fileName.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::format.m_token) {
                inputs.format.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::interfaceIP.m_token) {
                inputs.interfaceIP.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::messageTypes.m_token) {
                inputs.messageTypes.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::meta.m_token) {
                inputs.meta.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::remoteIP.m_token) {
                inputs.remoteIP.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::remotePort.m_token) {
                inputs.remotePort.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::serviceID.m_token) {
                inputs.serviceID.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::src.m_token) {
                inputs.src.invalidateCachedPointer();
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
        if( !inputs.cudaStream.canVectorize()
            || !inputs.dumpPackets.canVectorize()
            || !inputs.meta.canVectorize()
            || !inputs.remotePort.canVectorize()
            || !inputs.serviceID.canVectorize()
            || !inputs.src.canVectorize()
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
        if(token == inputs::cudaStream.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cudaStream.setHandle(hdl);
            return;
        }
        if(token == inputs::decoderPath.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.decoderPath.setHandle(hdl);
            return;
        }
        if(token == inputs::device.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.device.setHandle(hdl);
            return;
        }
        if(token == inputs::dumpPackets.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.dumpPackets.setHandle(hdl);
            return;
        }
        if(token == inputs::eventIDs.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.eventIDs.setHandle(hdl);
            return;
        }
        if(token == inputs::eventTypes.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.eventTypes.setHandle(hdl);
            return;
        }
        if(token == inputs::fileName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.fileName.setHandle(hdl);
            return;
        }
        if(token == inputs::format.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.format.setHandle(hdl);
            return;
        }
        if(token == inputs::interfaceIP.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.interfaceIP.setHandle(hdl);
            return;
        }
        if(token == inputs::messageTypes.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.messageTypes.setHandle(hdl);
            return;
        }
        if(token == inputs::meta.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.meta.setHandle(hdl);
            return;
        }
        if(token == inputs::remoteIP.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.remoteIP.setHandle(hdl);
            return;
        }
        if(token == inputs::remotePort.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.remotePort.setHandle(hdl);
            return;
        }
        if(token == inputs::serviceID.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.serviceID.setHandle(hdl);
            return;
        }
        if(token == inputs::src.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.src.setHandle(hdl);
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
ogn::StateManager TranscoderRadarDatabase::sm_stateManagerTranscoderRadar;
std::tuple<int, int, int> TranscoderRadarDatabase::sm_generatorVersionTranscoderRadar{std::make_tuple(1,79,2)};
std::tuple<int, int, int> TranscoderRadarDatabase::sm_targetVersionTranscoderRadar{std::make_tuple(2,184,5)};
}
using namespace ITranscoderRadar;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<TranscoderRadar, TranscoderRadarDatabase> s_registration("omni.sensors.nv.radar.TranscoderRadar", 1, "omni.sensors.nv.radar"); \
}
