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
#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/ArrayAttribute.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>

namespace TranscoderUltrasonicAttributes
{
namespace inputs
{
using cudaStream_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaStream("inputs:cudaStream", "uint64", kExtendedAttributeType_Regular, 0);
using dumpPackets_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> dumpPackets("inputs:dumpPackets", "bool", kExtendedAttributeType_Regular, false);
using fileFormat_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> fileFormat("inputs:fileFormat", "string", kExtendedAttributeType_Regular, "bin", 3);
using fileName_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> fileName("inputs:fileName", "string", kExtendedAttributeType_Regular, "uss.h5", 6);
using format_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> format("inputs:format", "string", kExtendedAttributeType_Regular, "", 0);
using hydraTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTime("inputs:hydraTime", "double", kExtendedAttributeType_Regular, 0.0);
using interfaceIP_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> interfaceIP("inputs:interfaceIP", "string", kExtendedAttributeType_Regular, "127.0.0.1", 9);
using meta_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> meta("inputs:meta", "uint64", kExtendedAttributeType_Regular, 0);
using remoteIP_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> remoteIP("inputs:remoteIP", "string", kExtendedAttributeType_Regular, "127.0.0.1", 9);
using remotePort_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> remotePort("inputs:remotePort", "int", kExtendedAttributeType_Regular, 12001);
using signalScaler_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> signalScaler("inputs:signalScaler", "float", kExtendedAttributeType_Regular, 1.0f);
using simTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTime("inputs:simTime", "double", kExtendedAttributeType_Regular, 0.0);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
using timestampMode_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> timestampMode("inputs:timestampMode", "string", kExtendedAttributeType_Regular, "VENDOR", 6);
using vendor_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> vendor("inputs:vendor", "string", kExtendedAttributeType_Regular, "generic", 7);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace TranscoderUltrasonicAttributes;
namespace ITranscoderUltrasonic
{
// Transcodes RTSensor buffer data to sensor specific formats and transmits it via udp
class TranscoderUltrasonicDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerTranscoderUltrasonic.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerTranscoderUltrasonic.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerTranscoderUltrasonic.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerTranscoderUltrasonic.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerTranscoderUltrasonic;
    static std::tuple<int, int, int>sm_generatorVersionTranscoderUltrasonic;
    static std::tuple<int, int, int>sm_targetVersionTranscoderUltrasonic;
    static constexpr size_t staticAttributeCount = 17;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : cudaStream{offset}
        , dumpPackets{offset}
        , fileFormat{offset,AttributeRole::eText}
        , fileName{offset,AttributeRole::eText}
        , format{offset,AttributeRole::eText}
        , hydraTime{offset}
        , interfaceIP{offset,AttributeRole::eText}
        , meta{offset}
        , remoteIP{offset,AttributeRole::eText}
        , remotePort{offset}
        , signalScaler{offset}
        , simTime{offset}
        , src{offset}
        , timestampMode{offset,AttributeRole::eText}
        , vendor{offset,AttributeRole::eText}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaStream;
        ogn::SimpleInput<const bool,ogn::kCpu> dumpPackets;
        ogn::ArrayInput<const char,ogn::kCpu> fileFormat;
        ogn::ArrayInput<const char,ogn::kCpu> fileName;
        ogn::ArrayInput<const char,ogn::kCpu> format;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTime;
        ogn::ArrayInput<const char,ogn::kCpu> interfaceIP;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> meta;
        ogn::ArrayInput<const char,ogn::kCpu> remoteIP;
        ogn::SimpleInput<const int,ogn::kCpu> remotePort;
        ogn::SimpleInput<const float,ogn::kCpu> signalScaler;
        ogn::SimpleInput<const double,ogn::kCpu> simTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
        ogn::ArrayInput<const char,ogn::kCpu> timestampMode;
        ogn::ArrayInput<const char,ogn::kCpu> vendor;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    TranscoderUltrasonicDatabase(NodeObj const& nodeObjParam)
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
    TranscoderUltrasonicDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : TranscoderUltrasonicDatabase(nodeObjParam)
    {}

    //Main constructor
    TranscoderUltrasonicDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::cudaStream.m_token, inputs::dumpPackets.m_token, inputs::fileFormat.m_token, inputs::fileName.m_token,
                    inputs::format.m_token, inputs::hydraTime.m_token, inputs::interfaceIP.m_token, inputs::meta.m_token,
                    inputs::remoteIP.m_token, inputs::remotePort.m_token, inputs::signalScaler.m_token, inputs::simTime.m_token,
                    inputs::src.m_token, inputs::timestampMode.m_token, inputs::vendor.m_token
                )
            , kAccordingToContextIndex);
            inputs.cudaStream.setContext(contextObj);
            inputs.cudaStream.setHandle(std::get<0>(inputDataHandles0));
            inputs.dumpPackets.setContext(contextObj);
            inputs.dumpPackets.setHandle(std::get<1>(inputDataHandles0));
            inputs.fileFormat.setContext(contextObj);
            inputs.fileFormat.setHandle(std::get<2>(inputDataHandles0));
            inputs.fileName.setContext(contextObj);
            inputs.fileName.setHandle(std::get<3>(inputDataHandles0));
            inputs.format.setContext(contextObj);
            inputs.format.setHandle(std::get<4>(inputDataHandles0));
            inputs.hydraTime.setContext(contextObj);
            inputs.hydraTime.setHandle(std::get<5>(inputDataHandles0));
            inputs.interfaceIP.setContext(contextObj);
            inputs.interfaceIP.setHandle(std::get<6>(inputDataHandles0));
            inputs.meta.setContext(contextObj);
            inputs.meta.setHandle(std::get<7>(inputDataHandles0));
            inputs.remoteIP.setContext(contextObj);
            inputs.remoteIP.setHandle(std::get<8>(inputDataHandles0));
            inputs.remotePort.setContext(contextObj);
            inputs.remotePort.setHandle(std::get<9>(inputDataHandles0));
            inputs.signalScaler.setContext(contextObj);
            inputs.signalScaler.setHandle(std::get<10>(inputDataHandles0));
            inputs.simTime.setContext(contextObj);
            inputs.simTime.setHandle(std::get<11>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<12>(inputDataHandles0));
            inputs.timestampMode.setContext(contextObj);
            inputs.timestampMode.setHandle(std::get<13>(inputDataHandles0));
            inputs.vendor.setContext(contextObj);
            inputs.vendor.setHandle(std::get<14>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.ultrasonic.TranscoderUltrasonic");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::cudaStream.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::dumpPackets.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::fileFormat.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::fileName.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::format.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::interfaceIP.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::meta.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::remoteIP.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::remotePort.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::signalScaler.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timestampMode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::vendor.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.ultrasonic");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Transcodes RTSensor buffer data to sensor specific formats and transmits it via udp");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda Stream Input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::dumpPackets.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Dump packets as dwBinFile");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::fileFormat.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "File format to dump");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"bin\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::fileName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "File name of the packets");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"uss.h5\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::format.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Output format");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "hydra timestamp input as double in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::interfaceIP.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "local interface to use");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"127.0.0.1\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::meta.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Meta Data");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::remoteIP.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Remote IP of UDP channel");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"127.0.0.1\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::remotePort.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Remote port of UDP channel");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "12001");
        attr = iNode->getAttributeByToken(nodeObj, inputs::signalScaler.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Signal scaling parameter");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "simTime timestamp input as double in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::timestampMode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "mode for the sent timestamp");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"VENDOR\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::vendor.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "USS model vendor");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"generic\"");
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
        sm_stateManagerTranscoderUltrasonic.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cudaStream.isValid()
            && inputs.dumpPackets.isValid()
            && inputs.fileFormat.isValid()
            && inputs.fileName.isValid()
            && inputs.format.isValid()
            && inputs.hydraTime.isValid()
            && inputs.interfaceIP.isValid()
            && inputs.meta.isValid()
            && inputs.remoteIP.isValid()
            && inputs.remotePort.isValid()
            && inputs.signalScaler.isValid()
            && inputs.simTime.isValid()
            && inputs.src.isValid()
            && inputs.timestampMode.isValid()
            && inputs.vendor.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cudaStream.invalidateCachedPointer();
            inputs.dumpPackets.invalidateCachedPointer();
            inputs.fileFormat.invalidateCachedPointer();
            inputs.fileName.invalidateCachedPointer();
            inputs.format.invalidateCachedPointer();
            inputs.hydraTime.invalidateCachedPointer();
            inputs.interfaceIP.invalidateCachedPointer();
            inputs.meta.invalidateCachedPointer();
            inputs.remoteIP.invalidateCachedPointer();
            inputs.remotePort.invalidateCachedPointer();
            inputs.signalScaler.invalidateCachedPointer();
            inputs.simTime.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            inputs.timestampMode.invalidateCachedPointer();
            inputs.vendor.invalidateCachedPointer();
            return;
        }
        inputs.fileFormat.invalidateCachedPointer();
        inputs.fileName.invalidateCachedPointer();
        inputs.format.invalidateCachedPointer();
        inputs.interfaceIP.invalidateCachedPointer();
        inputs.remoteIP.invalidateCachedPointer();
        inputs.timestampMode.invalidateCachedPointer();
        inputs.vendor.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cudaStream.m_token) {
                inputs.cudaStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::dumpPackets.m_token) {
                inputs.dumpPackets.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::fileFormat.m_token) {
                inputs.fileFormat.invalidateCachedPointer();
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
            if(attrib == inputs::hydraTime.m_token) {
                inputs.hydraTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::interfaceIP.m_token) {
                inputs.interfaceIP.invalidateCachedPointer();
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
            if(attrib == inputs::signalScaler.m_token) {
                inputs.signalScaler.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::simTime.m_token) {
                inputs.simTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::src.m_token) {
                inputs.src.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::timestampMode.m_token) {
                inputs.timestampMode.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::vendor.m_token) {
                inputs.vendor.invalidateCachedPointer();
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
            || !inputs.hydraTime.canVectorize()
            || !inputs.meta.canVectorize()
            || !inputs.remotePort.canVectorize()
            || !inputs.signalScaler.canVectorize()
            || !inputs.simTime.canVectorize()
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
        if(token == inputs::dumpPackets.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.dumpPackets.setHandle(hdl);
            return;
        }
        if(token == inputs::fileFormat.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.fileFormat.setHandle(hdl);
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
        if(token == inputs::hydraTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hydraTime.setHandle(hdl);
            return;
        }
        if(token == inputs::interfaceIP.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.interfaceIP.setHandle(hdl);
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
        if(token == inputs::signalScaler.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.signalScaler.setHandle(hdl);
            return;
        }
        if(token == inputs::simTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.simTime.setHandle(hdl);
            return;
        }
        if(token == inputs::src.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.src.setHandle(hdl);
            return;
        }
        if(token == inputs::timestampMode.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.timestampMode.setHandle(hdl);
            return;
        }
        if(token == inputs::vendor.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.vendor.setHandle(hdl);
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
ogn::StateManager TranscoderUltrasonicDatabase::sm_stateManagerTranscoderUltrasonic;
std::tuple<int, int, int> TranscoderUltrasonicDatabase::sm_generatorVersionTranscoderUltrasonic{std::make_tuple(1,79,2)};
std::tuple<int, int, int> TranscoderUltrasonicDatabase::sm_targetVersionTranscoderUltrasonic{std::make_tuple(2,184,5)};
}
using namespace ITranscoderUltrasonic;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<TranscoderUltrasonic, TranscoderUltrasonicDatabase> s_registration("omni.sensors.nv.ultrasonic.TranscoderUltrasonic", 1, "omni.sensors.nv.ultrasonic"); \
}
