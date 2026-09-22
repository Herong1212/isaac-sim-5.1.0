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

namespace TranscoderLidarAttributes
{
namespace inputs
{
using cudaStream_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaStream("inputs:cudaStream", "uint64", kExtendedAttributeType_Regular, 0);
using decoderPath_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> decoderPath("inputs:decoderPath", "string", kExtendedAttributeType_Regular, "", 0);
using dumpPackets_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> dumpPackets("inputs:dumpPackets", "bool", kExtendedAttributeType_Regular, false);
using encoderType_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> encoderType("inputs:encoderType", "int", kExtendedAttributeType_Regular, 7);
using fileName_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> fileName("inputs:fileName", "string", kExtendedAttributeType_Regular, "lidar.h5", 8);
using groupName_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> groupName("inputs:groupName", "string", kExtendedAttributeType_Regular, "Lidar", 5);
using returnType_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> returnType("inputs:returnType", "int", kExtendedAttributeType_Regular, 3);
using sensorProfileName_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> sensorProfileName("inputs:sensorProfileName", "string", kExtendedAttributeType_Regular, "GENERIC", 7);
using simTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTime("inputs:simTime", "double", kExtendedAttributeType_Regular, 0.0);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
using srcMeta_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> srcMeta("inputs:srcMeta", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace TranscoderLidarAttributes;
namespace ITranscoderLidar
{
// Transcodes RTSensor buffer to Lidar packets
class TranscoderLidarDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerTranscoderLidar.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerTranscoderLidar.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerTranscoderLidar.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerTranscoderLidar.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerTranscoderLidar;
    static std::tuple<int, int, int>sm_generatorVersionTranscoderLidar;
    static std::tuple<int, int, int>sm_targetVersionTranscoderLidar;
    static constexpr size_t staticAttributeCount = 13;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : cudaStream{offset}
        , decoderPath{offset,AttributeRole::eText}
        , dumpPackets{offset}
        , encoderType{offset}
        , fileName{offset,AttributeRole::eText}
        , groupName{offset,AttributeRole::eText}
        , returnType{offset}
        , sensorProfileName{offset,AttributeRole::eText}
        , simTime{offset}
        , src{offset}
        , srcMeta{offset}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaStream;
        ogn::ArrayInput<const char,ogn::kCpu> decoderPath;
        ogn::SimpleInput<const bool,ogn::kCpu> dumpPackets;
        ogn::SimpleInput<const int,ogn::kCpu> encoderType;
        ogn::ArrayInput<const char,ogn::kCpu> fileName;
        ogn::ArrayInput<const char,ogn::kCpu> groupName;
        ogn::SimpleInput<const int,ogn::kCpu> returnType;
        ogn::ArrayInput<const char,ogn::kCpu> sensorProfileName;
        ogn::SimpleInput<const double,ogn::kCpu> simTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> srcMeta;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    TranscoderLidarDatabase(NodeObj const& nodeObjParam)
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
    TranscoderLidarDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : TranscoderLidarDatabase(nodeObjParam)
    {}

    //Main constructor
    TranscoderLidarDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::cudaStream.m_token, inputs::decoderPath.m_token, inputs::dumpPackets.m_token, inputs::encoderType.m_token,
                    inputs::fileName.m_token, inputs::groupName.m_token, inputs::returnType.m_token, inputs::sensorProfileName.m_token,
                    inputs::simTime.m_token, inputs::src.m_token, inputs::srcMeta.m_token
                )
            , kAccordingToContextIndex);
            inputs.cudaStream.setContext(contextObj);
            inputs.cudaStream.setHandle(std::get<0>(inputDataHandles0));
            inputs.decoderPath.setContext(contextObj);
            inputs.decoderPath.setHandle(std::get<1>(inputDataHandles0));
            inputs.dumpPackets.setContext(contextObj);
            inputs.dumpPackets.setHandle(std::get<2>(inputDataHandles0));
            inputs.encoderType.setContext(contextObj);
            inputs.encoderType.setHandle(std::get<3>(inputDataHandles0));
            inputs.fileName.setContext(contextObj);
            inputs.fileName.setHandle(std::get<4>(inputDataHandles0));
            inputs.groupName.setContext(contextObj);
            inputs.groupName.setHandle(std::get<5>(inputDataHandles0));
            inputs.returnType.setContext(contextObj);
            inputs.returnType.setHandle(std::get<6>(inputDataHandles0));
            inputs.sensorProfileName.setContext(contextObj);
            inputs.sensorProfileName.setHandle(std::get<7>(inputDataHandles0));
            inputs.simTime.setContext(contextObj);
            inputs.simTime.setHandle(std::get<8>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<9>(inputDataHandles0));
            inputs.srcMeta.setContext(contextObj);
            inputs.srcMeta.setHandle(std::get<10>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.lidar.TranscoderLidar");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::cudaStream.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::decoderPath.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::dumpPackets.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::encoderType.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::fileName.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::groupName.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::returnType.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sensorProfileName.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::srcMeta.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.lidar");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Transcodes RTSensor buffer to Lidar packets");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda Stream Input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::decoderPath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Optional, decoder path for file dumping");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::dumpPackets.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Dump packets as dwBinFile");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::encoderType.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Encoder Type -- needed if there are different versions of the sensor (e.g., NCD)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "7");
        attr = iNode->getAttributeByToken(nodeObj, inputs::fileName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "File name of the packets");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"lidar.h5\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::groupName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Sensor name to be put inside hdf5 file");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"Lidar\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::returnType.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Desired return type (0 - First, 1 - last, 2 - Strongest, 3 - MultipleReturns");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "3");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sensorProfileName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Filename of the sensor profile - has to be the same as in lidar model");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"GENERIC\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Simulation time given from PostProcessEntryNode");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "RtSensor buffer id");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::srcMeta.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Lidar Meta Data");
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
        sm_stateManagerTranscoderLidar.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cudaStream.isValid()
            && inputs.decoderPath.isValid()
            && inputs.dumpPackets.isValid()
            && inputs.encoderType.isValid()
            && inputs.fileName.isValid()
            && inputs.groupName.isValid()
            && inputs.returnType.isValid()
            && inputs.sensorProfileName.isValid()
            && inputs.simTime.isValid()
            && inputs.src.isValid()
            && inputs.srcMeta.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cudaStream.invalidateCachedPointer();
            inputs.decoderPath.invalidateCachedPointer();
            inputs.dumpPackets.invalidateCachedPointer();
            inputs.encoderType.invalidateCachedPointer();
            inputs.fileName.invalidateCachedPointer();
            inputs.groupName.invalidateCachedPointer();
            inputs.returnType.invalidateCachedPointer();
            inputs.sensorProfileName.invalidateCachedPointer();
            inputs.simTime.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            inputs.srcMeta.invalidateCachedPointer();
            return;
        }
        inputs.decoderPath.invalidateCachedPointer();
        inputs.fileName.invalidateCachedPointer();
        inputs.groupName.invalidateCachedPointer();
        inputs.sensorProfileName.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cudaStream.m_token) {
                inputs.cudaStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::decoderPath.m_token) {
                inputs.decoderPath.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::dumpPackets.m_token) {
                inputs.dumpPackets.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::encoderType.m_token) {
                inputs.encoderType.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::fileName.m_token) {
                inputs.fileName.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::groupName.m_token) {
                inputs.groupName.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::returnType.m_token) {
                inputs.returnType.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sensorProfileName.m_token) {
                inputs.sensorProfileName.invalidateCachedPointer();
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
            if(attrib == inputs::srcMeta.m_token) {
                inputs.srcMeta.invalidateCachedPointer();
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
            || !inputs.encoderType.canVectorize()
            || !inputs.returnType.canVectorize()
            || !inputs.simTime.canVectorize()
            || !inputs.src.canVectorize()
            || !inputs.srcMeta.canVectorize()
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
        if(token == inputs::dumpPackets.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.dumpPackets.setHandle(hdl);
            return;
        }
        if(token == inputs::encoderType.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.encoderType.setHandle(hdl);
            return;
        }
        if(token == inputs::fileName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.fileName.setHandle(hdl);
            return;
        }
        if(token == inputs::groupName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.groupName.setHandle(hdl);
            return;
        }
        if(token == inputs::returnType.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.returnType.setHandle(hdl);
            return;
        }
        if(token == inputs::sensorProfileName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sensorProfileName.setHandle(hdl);
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
        if(token == inputs::srcMeta.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.srcMeta.setHandle(hdl);
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
ogn::StateManager TranscoderLidarDatabase::sm_stateManagerTranscoderLidar;
std::tuple<int, int, int> TranscoderLidarDatabase::sm_generatorVersionTranscoderLidar{std::make_tuple(1,79,2)};
std::tuple<int, int, int> TranscoderLidarDatabase::sm_targetVersionTranscoderLidar{std::make_tuple(2,184,5)};
}
using namespace ITranscoderLidar;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<TranscoderLidar, TranscoderLidarDatabase> s_registration("omni.sensors.nv.lidar.TranscoderLidar", 1, "omni.sensors.nv.lidar"); \
}
