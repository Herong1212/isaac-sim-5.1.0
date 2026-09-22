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

namespace VizTranscoderRadarAttributes
{
namespace inputs
{
using colorCode_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> colorCode("inputs:colorCode", "int", kExtendedAttributeType_Regular, 4);
using cudaStreamIn_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaStreamIn("inputs:cudaStreamIn", "uint64", kExtendedAttributeType_Regular, 0);
using hydraTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTime("inputs:hydraTime", "double", kExtendedAttributeType_Regular, 0.0);
using in_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> in("inputs:in", "uint64", kExtendedAttributeType_Regular, 0);
using lastNode_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> lastNode("inputs:lastNode", "bool", kExtendedAttributeType_Regular, false);
using maxNumScans_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> maxNumScans("inputs:maxNumScans", "int", kExtendedAttributeType_Regular, 2);
using meta_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> meta("inputs:meta", "uint64", kExtendedAttributeType_Regular, 0);
using sendDataId_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> sendDataId("inputs:sendDataId", "int", kExtendedAttributeType_Regular, 0);
using sensorMount6Dpose_t = const ogn::const_array<float>&;
ogn::AttributeInitializer<const float*, ogn::kOgnInput> sensorMount6Dpose("inputs:sensorMount6Dpose", "float[]", kExtendedAttributeType_Regular, nullptr, 0);
using simTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTime("inputs:simTime", "double", kExtendedAttributeType_Regular, 0.0);
using targetPID_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> targetPID("inputs:targetPID", "uint64", kExtendedAttributeType_Regular, 0);
using vlineScale_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> vlineScale("inputs:vlineScale", "float", kExtendedAttributeType_Regular, 1.0f);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace VizTranscoderRadarAttributes;
namespace IVizTranscoderRadar
{
// Receives Radar data and prepares a buffer for it from the buffer manager, and passes
// it to output
class VizTranscoderRadarDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerVizTranscoderRadar.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerVizTranscoderRadar.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerVizTranscoderRadar.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerVizTranscoderRadar.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerVizTranscoderRadar;
    static std::tuple<int, int, int>sm_generatorVersionVizTranscoderRadar;
    static std::tuple<int, int, int>sm_targetVersionVizTranscoderRadar;
    static constexpr size_t staticAttributeCount = 14;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : colorCode{offset}
        , cudaStreamIn{offset}
        , hydraTime{offset}
        , in{offset}
        , lastNode{offset}
        , maxNumScans{offset}
        , meta{offset}
        , sendDataId{offset}
        , sensorMount6Dpose{offset}
        , simTime{offset}
        , targetPID{offset}
        , vlineScale{offset}
        {}
        ogn::SimpleInput<const int,ogn::kCpu> colorCode;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaStreamIn;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> in;
        ogn::SimpleInput<const bool,ogn::kCpu> lastNode;
        ogn::SimpleInput<const int,ogn::kCpu> maxNumScans;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> meta;
        ogn::SimpleInput<const int,ogn::kCpu> sendDataId;
        ogn::ArrayInput<const float,ogn::kCpu> sensorMount6Dpose;
        ogn::SimpleInput<const double,ogn::kCpu> simTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> targetPID;
        ogn::SimpleInput<const float,ogn::kCpu> vlineScale;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    VizTranscoderRadarDatabase(NodeObj const& nodeObjParam)
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
    VizTranscoderRadarDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : VizTranscoderRadarDatabase(nodeObjParam)
    {}

    //Main constructor
    VizTranscoderRadarDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::colorCode.m_token, inputs::cudaStreamIn.m_token, inputs::hydraTime.m_token, inputs::in.m_token,
                    inputs::lastNode.m_token, inputs::maxNumScans.m_token, inputs::meta.m_token, inputs::sendDataId.m_token,
                    inputs::sensorMount6Dpose.m_token, inputs::simTime.m_token, inputs::targetPID.m_token, inputs::vlineScale.m_token
                )
            , kAccordingToContextIndex);
            inputs.colorCode.setContext(contextObj);
            inputs.colorCode.setHandle(std::get<0>(inputDataHandles0));
            inputs.cudaStreamIn.setContext(contextObj);
            inputs.cudaStreamIn.setHandle(std::get<1>(inputDataHandles0));
            inputs.hydraTime.setContext(contextObj);
            inputs.hydraTime.setHandle(std::get<2>(inputDataHandles0));
            inputs.in.setContext(contextObj);
            inputs.in.setHandle(std::get<3>(inputDataHandles0));
            inputs.lastNode.setContext(contextObj);
            inputs.lastNode.setHandle(std::get<4>(inputDataHandles0));
            inputs.maxNumScans.setContext(contextObj);
            inputs.maxNumScans.setHandle(std::get<5>(inputDataHandles0));
            inputs.meta.setContext(contextObj);
            inputs.meta.setHandle(std::get<6>(inputDataHandles0));
            inputs.sendDataId.setContext(contextObj);
            inputs.sendDataId.setHandle(std::get<7>(inputDataHandles0));
            inputs.sensorMount6Dpose.setContext(contextObj);
            inputs.sensorMount6Dpose.setHandle(std::get<8>(inputDataHandles0));
            inputs.simTime.setContext(contextObj);
            inputs.simTime.setHandle(std::get<9>(inputDataHandles0));
            inputs.targetPID.setContext(contextObj);
            inputs.targetPID.setHandle(std::get<10>(inputDataHandles0));
            inputs.vlineScale.setContext(contextObj);
            inputs.vlineScale.setHandle(std::get<11>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.radar.VizTranscoderRadar");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::colorCode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cudaStreamIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::in.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::lastNode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::maxNumScans.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::meta.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sendDataId.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sensorMount6Dpose.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::targetPID.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::vlineScale.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.radar");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Receives Radar data and prepares a buffer for it from the buffer manager, and passes it to output");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::colorCode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "0 - constant, 1 - range, 2 - doppler, 3 - azimuth, 4 - elevation, 5 - rcs, 6 - semantic, 7 - material, 8 - instance");
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
        attr = iNode->getAttributeByToken(nodeObj, inputs::lastNode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "true if the viz transcoder is last node in pipeline and needs to signal async work termination");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::maxNumScans.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "max number of scans to accumulate");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "2");
        attr = iNode->getAttributeByToken(nodeObj, inputs::meta.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Meta Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sendDataId.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Send data buffer id to distinguish data on receiver side");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sensorMount6Dpose.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "sensor mounting pose in vehicle coordinates as (x, y, z, roll, pitch, yaw)");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "simTime timestamp input as double in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::targetPID.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Target process ID to send data stream to");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::vlineScale.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "scale of velocity lines");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1.0");
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
        sm_stateManagerVizTranscoderRadar.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.colorCode.isValid()
            && inputs.cudaStreamIn.isValid()
            && inputs.hydraTime.isValid()
            && inputs.in.isValid()
            && inputs.lastNode.isValid()
            && inputs.maxNumScans.isValid()
            && inputs.meta.isValid()
            && inputs.sendDataId.isValid()
            && inputs.sensorMount6Dpose.isValid()
            && inputs.simTime.isValid()
            && inputs.targetPID.isValid()
            && inputs.vlineScale.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.colorCode.invalidateCachedPointer();
            inputs.cudaStreamIn.invalidateCachedPointer();
            inputs.hydraTime.invalidateCachedPointer();
            inputs.in.invalidateCachedPointer();
            inputs.lastNode.invalidateCachedPointer();
            inputs.maxNumScans.invalidateCachedPointer();
            inputs.meta.invalidateCachedPointer();
            inputs.sendDataId.invalidateCachedPointer();
            inputs.sensorMount6Dpose.invalidateCachedPointer();
            inputs.simTime.invalidateCachedPointer();
            inputs.targetPID.invalidateCachedPointer();
            inputs.vlineScale.invalidateCachedPointer();
            return;
        }
        inputs.sensorMount6Dpose.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::colorCode.m_token) {
                inputs.colorCode.invalidateCachedPointer();
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
            if(attrib == inputs::lastNode.m_token) {
                inputs.lastNode.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::maxNumScans.m_token) {
                inputs.maxNumScans.invalidateCachedPointer();
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
            if(attrib == inputs::sensorMount6Dpose.m_token) {
                inputs.sensorMount6Dpose.invalidateCachedPointer();
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
            if(attrib == inputs::vlineScale.m_token) {
                inputs.vlineScale.invalidateCachedPointer();
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
        if( !inputs.colorCode.canVectorize()
            || !inputs.cudaStreamIn.canVectorize()
            || !inputs.hydraTime.canVectorize()
            || !inputs.in.canVectorize()
            || !inputs.lastNode.canVectorize()
            || !inputs.maxNumScans.canVectorize()
            || !inputs.meta.canVectorize()
            || !inputs.sendDataId.canVectorize()
            || !inputs.simTime.canVectorize()
            || !inputs.targetPID.canVectorize()
            || !inputs.vlineScale.canVectorize()
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
        if(token == inputs::colorCode.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.colorCode.setHandle(hdl);
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
        if(token == inputs::lastNode.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.lastNode.setHandle(hdl);
            return;
        }
        if(token == inputs::maxNumScans.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.maxNumScans.setHandle(hdl);
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
        if(token == inputs::sensorMount6Dpose.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sensorMount6Dpose.setHandle(hdl);
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
        if(token == inputs::vlineScale.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.vlineScale.setHandle(hdl);
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
ogn::StateManager VizTranscoderRadarDatabase::sm_stateManagerVizTranscoderRadar;
std::tuple<int, int, int> VizTranscoderRadarDatabase::sm_generatorVersionVizTranscoderRadar{std::make_tuple(1,79,2)};
std::tuple<int, int, int> VizTranscoderRadarDatabase::sm_targetVersionVizTranscoderRadar{std::make_tuple(2,184,5)};
}
using namespace IVizTranscoderRadar;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<VizTranscoderRadar, VizTranscoderRadarDatabase> s_registration("omni.sensors.nv.radar.VizTranscoderRadar", 1, "omni.sensors.nv.radar"); \
}
