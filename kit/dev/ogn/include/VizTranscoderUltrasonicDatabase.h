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
#include <omni/graph/core/ogn/SimpleAttribute.h>

namespace VizTranscoderUltrasonicAttributes
{
namespace inputs
{
using averagePeriod_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> averagePeriod("inputs:averagePeriod", "int", kExtendedAttributeType_Regular, 4);
using cudaStreamIn_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaStreamIn("inputs:cudaStreamIn", "uint64", kExtendedAttributeType_Regular, 0);
using hydraTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTime("inputs:hydraTime", "double", kExtendedAttributeType_Regular, 0.0);
using in_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> in("inputs:in", "uint64", kExtendedAttributeType_Regular, 0);
using meta_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> meta("inputs:meta", "uint64", kExtendedAttributeType_Regular, 0);
using sendDataId_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> sendDataId("inputs:sendDataId", "int", kExtendedAttributeType_Regular, 0);
using simTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTime("inputs:simTime", "double", kExtendedAttributeType_Regular, 0.0);
using targetPID_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> targetPID("inputs:targetPID", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace VizTranscoderUltrasonicAttributes;
namespace IVizTranscoderUltrasonic
{
// Receives Radar data and prepares a buffer for it from the buffer manager, and passes
// it to output
class VizTranscoderUltrasonicDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerVizTranscoderUltrasonic.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerVizTranscoderUltrasonic.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerVizTranscoderUltrasonic.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerVizTranscoderUltrasonic.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerVizTranscoderUltrasonic;
    static std::tuple<int, int, int>sm_generatorVersionVizTranscoderUltrasonic;
    static std::tuple<int, int, int>sm_targetVersionVizTranscoderUltrasonic;
    static constexpr size_t staticAttributeCount = 10;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : averagePeriod{offset}
        , cudaStreamIn{offset}
        , hydraTime{offset}
        , in{offset}
        , meta{offset}
        , sendDataId{offset}
        , simTime{offset}
        , targetPID{offset}
        {}
        ogn::SimpleInput<const int,ogn::kCpu> averagePeriod;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaStreamIn;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> in;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> meta;
        ogn::SimpleInput<const int,ogn::kCpu> sendDataId;
        ogn::SimpleInput<const double,ogn::kCpu> simTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> targetPID;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    VizTranscoderUltrasonicDatabase(NodeObj const& nodeObjParam)
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
    VizTranscoderUltrasonicDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : VizTranscoderUltrasonicDatabase(nodeObjParam)
    {}

    //Main constructor
    VizTranscoderUltrasonicDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::averagePeriod.m_token, inputs::cudaStreamIn.m_token, inputs::hydraTime.m_token, inputs::in.m_token,
                    inputs::meta.m_token, inputs::sendDataId.m_token, inputs::simTime.m_token, inputs::targetPID.m_token
                )
            , kAccordingToContextIndex);
            inputs.averagePeriod.setContext(contextObj);
            inputs.averagePeriod.setHandle(std::get<0>(inputDataHandles0));
            inputs.cudaStreamIn.setContext(contextObj);
            inputs.cudaStreamIn.setHandle(std::get<1>(inputDataHandles0));
            inputs.hydraTime.setContext(contextObj);
            inputs.hydraTime.setHandle(std::get<2>(inputDataHandles0));
            inputs.in.setContext(contextObj);
            inputs.in.setHandle(std::get<3>(inputDataHandles0));
            inputs.meta.setContext(contextObj);
            inputs.meta.setHandle(std::get<4>(inputDataHandles0));
            inputs.sendDataId.setContext(contextObj);
            inputs.sendDataId.setHandle(std::get<5>(inputDataHandles0));
            inputs.simTime.setContext(contextObj);
            inputs.simTime.setHandle(std::get<6>(inputDataHandles0));
            inputs.targetPID.setContext(contextObj);
            inputs.targetPID.setHandle(std::get<7>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.ultrasonic.VizTranscoderUltrasonic");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::averagePeriod.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cudaStreamIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::in.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::meta.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sendDataId.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::targetPID.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.ultrasonic");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Receives Radar data and prepares a buffer for it from the buffer manager, and passes it to output");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::averagePeriod.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "number of frames to average signal over");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "4");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaStreamIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda Stream Input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "hydra timestamp input as double in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::in.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::meta.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Meta Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sendDataId.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Send data buffer id to distinguish data on receiver side");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "simTime timestamp input as double in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::targetPID.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Target process ID to send data stream to");
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
        sm_stateManagerVizTranscoderUltrasonic.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.averagePeriod.isValid()
            && inputs.cudaStreamIn.isValid()
            && inputs.hydraTime.isValid()
            && inputs.in.isValid()
            && inputs.meta.isValid()
            && inputs.sendDataId.isValid()
            && inputs.simTime.isValid()
            && inputs.targetPID.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.averagePeriod.invalidateCachedPointer();
            inputs.cudaStreamIn.invalidateCachedPointer();
            inputs.hydraTime.invalidateCachedPointer();
            inputs.in.invalidateCachedPointer();
            inputs.meta.invalidateCachedPointer();
            inputs.sendDataId.invalidateCachedPointer();
            inputs.simTime.invalidateCachedPointer();
            inputs.targetPID.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::averagePeriod.m_token) {
                inputs.averagePeriod.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cudaStreamIn.m_token) {
                inputs.cudaStreamIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hydraTime.m_token) {
                inputs.hydraTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::in.m_token) {
                inputs.in.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::meta.m_token) {
                inputs.meta.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sendDataId.m_token) {
                inputs.sendDataId.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::simTime.m_token) {
                inputs.simTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::targetPID.m_token) {
                inputs.targetPID.invalidateCachedPointer();
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
        if( !inputs.averagePeriod.canVectorize()
            || !inputs.cudaStreamIn.canVectorize()
            || !inputs.hydraTime.canVectorize()
            || !inputs.in.canVectorize()
            || !inputs.meta.canVectorize()
            || !inputs.sendDataId.canVectorize()
            || !inputs.simTime.canVectorize()
            || !inputs.targetPID.canVectorize()
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
        if(token == inputs::averagePeriod.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.averagePeriod.setHandle(hdl);
            return;
        }
        if(token == inputs::cudaStreamIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cudaStreamIn.setHandle(hdl);
            return;
        }
        if(token == inputs::hydraTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hydraTime.setHandle(hdl);
            return;
        }
        if(token == inputs::in.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.in.setHandle(hdl);
            return;
        }
        if(token == inputs::meta.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.meta.setHandle(hdl);
            return;
        }
        if(token == inputs::sendDataId.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sendDataId.setHandle(hdl);
            return;
        }
        if(token == inputs::simTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.simTime.setHandle(hdl);
            return;
        }
        if(token == inputs::targetPID.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.targetPID.setHandle(hdl);
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
ogn::StateManager VizTranscoderUltrasonicDatabase::sm_stateManagerVizTranscoderUltrasonic;
std::tuple<int, int, int> VizTranscoderUltrasonicDatabase::sm_generatorVersionVizTranscoderUltrasonic{std::make_tuple(1,79,2)};
std::tuple<int, int, int> VizTranscoderUltrasonicDatabase::sm_targetVersionVizTranscoderUltrasonic{std::make_tuple(2,184,5)};
}
using namespace IVizTranscoderUltrasonic;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<VizTranscoderUltrasonic, VizTranscoderUltrasonicDatabase> s_registration("omni.sensors.nv.ultrasonic.VizTranscoderUltrasonic", 1, "omni.sensors.nv.ultrasonic"); \
}
