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

namespace VizTranscoderCameraAttributes
{
namespace inputs
{
using channelName_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> channelName("inputs:channelName", "token", kExtendedAttributeType_Regular);
using frameId_t = const int64_t&;
ogn::AttributeInitializer<const int64_t, ogn::kOgnInput> frameId("inputs:frameId", "int64", kExtendedAttributeType_Regular, 0);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using hydraTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTimeIn("inputs:hydraTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using sendDataId_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> sendDataId("inputs:sendDataId", "int", kExtendedAttributeType_Regular, 100);
using simTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTimeIn("inputs:simTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
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
using namespace VizTranscoderCameraAttributes;
namespace IVizTranscoderCamera
{
// Camera to Visualizer Sink Node
class VizTranscoderCameraDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerVizTranscoderCamera.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerVizTranscoderCamera.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerVizTranscoderCamera.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerVizTranscoderCamera.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerVizTranscoderCamera;
    static std::tuple<int, int, int>sm_generatorVersionVizTranscoderCamera;
    static std::tuple<int, int, int>sm_targetVersionVizTranscoderCamera;
    static constexpr size_t staticAttributeCount = 10;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : channelName{offset}
        , frameId{offset}
        , gpu{offset}
        , hydraTimeIn{offset}
        , rp{offset}
        , sendDataId{offset}
        , simTimeIn{offset}
        , src{offset}
        {}
        ogn::SimpleInput<const NameToken,ogn::kCpu> channelName;
        ogn::SimpleInput<const int64_t,ogn::kCpu> frameId;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTimeIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const int,ogn::kCpu> sendDataId;
        ogn::SimpleInput<const double,ogn::kCpu> simTimeIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    VizTranscoderCameraDatabase(NodeObj const& nodeObjParam)
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
    VizTranscoderCameraDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : VizTranscoderCameraDatabase(nodeObjParam)
    {}

    //Main constructor
    VizTranscoderCameraDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::channelName.m_token, inputs::frameId.m_token, inputs::gpu.m_token, inputs::hydraTimeIn.m_token,
                    inputs::rp.m_token, inputs::sendDataId.m_token, inputs::simTimeIn.m_token, inputs::src.m_token
                )
            , kAccordingToContextIndex);
            inputs.channelName.setContext(contextObj);
            inputs.channelName.setHandle(std::get<0>(inputDataHandles0));
            inputs.frameId.setContext(contextObj);
            inputs.frameId.setHandle(std::get<1>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<2>(inputDataHandles0));
            inputs.hydraTimeIn.setContext(contextObj);
            inputs.hydraTimeIn.setHandle(std::get<3>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<4>(inputDataHandles0));
            inputs.sendDataId.setContext(contextObj);
            inputs.sendDataId.setHandle(std::get<5>(inputDataHandles0));
            inputs.simTimeIn.setContext(contextObj);
            inputs.simTimeIn.setHandle(std::get<6>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<7>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.VizTranscoderCamera");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::channelName.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::frameId.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sendDataId.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.camera");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Camera to Visualizer Sink Node");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::channelName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "sink channel name");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::frameId.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Frame identifier");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sendDataId.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Send data id to distinguish point clouds on the receiver side");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "100");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
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
        sm_stateManagerVizTranscoderCamera.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.channelName.isValid()
            && inputs.frameId.isValid()
            && inputs.gpu.isValid()
            && inputs.hydraTimeIn.isValid()
            && inputs.rp.isValid()
            && inputs.sendDataId.isValid()
            && inputs.simTimeIn.isValid()
            && inputs.src.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.channelName.invalidateCachedPointer();
            inputs.frameId.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.hydraTimeIn.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.sendDataId.invalidateCachedPointer();
            inputs.simTimeIn.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::channelName.m_token) {
                inputs.channelName.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::frameId.m_token) {
                inputs.frameId.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hydraTimeIn.m_token) {
                inputs.hydraTimeIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sendDataId.m_token) {
                inputs.sendDataId.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::simTimeIn.m_token) {
                inputs.simTimeIn.invalidateCachedPointer();
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
        if( !inputs.channelName.canVectorize()
            || !inputs.frameId.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.hydraTimeIn.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.sendDataId.canVectorize()
            || !inputs.simTimeIn.canVectorize()
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
        if(token == inputs::channelName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.channelName.setHandle(hdl);
            return;
        }
        if(token == inputs::frameId.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.frameId.setHandle(hdl);
            return;
        }
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::hydraTimeIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hydraTimeIn.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == inputs::sendDataId.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sendDataId.setHandle(hdl);
            return;
        }
        if(token == inputs::simTimeIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.simTimeIn.setHandle(hdl);
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
ogn::StateManager VizTranscoderCameraDatabase::sm_stateManagerVizTranscoderCamera;
std::tuple<int, int, int> VizTranscoderCameraDatabase::sm_generatorVersionVizTranscoderCamera{std::make_tuple(1,79,2)};
std::tuple<int, int, int> VizTranscoderCameraDatabase::sm_targetVersionVizTranscoderCamera{std::make_tuple(2,184,5)};
}
using namespace IVizTranscoderCamera;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<VizTranscoderCamera, VizTranscoderCameraDatabase> s_registration("omni.sensors.nv.camera.VizTranscoderCamera", 1, "omni.sensors.nv.camera"); \
}
