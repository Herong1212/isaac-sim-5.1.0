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

namespace VizTranscoderRadarCfarAttributes
{
namespace inputs
{
using colorCode_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> colorCode("inputs:colorCode", "int", kExtendedAttributeType_Regular, 1);
using cudaStreamIn_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaStreamIn("inputs:cudaStreamIn", "uint64", kExtendedAttributeType_Regular, 0);
using in_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> in("inputs:in", "uint64", kExtendedAttributeType_Regular, 0);
using maxVal_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> maxVal("inputs:maxVal", "float", kExtendedAttributeType_Regular, 1.0f);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace VizTranscoderRadarCfarAttributes;
namespace IVizTranscoderRadarCfar
{
// Receives Radar cfar and sends it for visualization
class VizTranscoderRadarCfarDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerVizTranscoderRadarCfar.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerVizTranscoderRadarCfar.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerVizTranscoderRadarCfar.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerVizTranscoderRadarCfar.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerVizTranscoderRadarCfar;
    static std::tuple<int, int, int>sm_generatorVersionVizTranscoderRadarCfar;
    static std::tuple<int, int, int>sm_targetVersionVizTranscoderRadarCfar;
    static constexpr size_t staticAttributeCount = 6;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : colorCode{offset}
        , cudaStreamIn{offset}
        , in{offset}
        , maxVal{offset}
        {}
        ogn::SimpleInput<const int,ogn::kCpu> colorCode;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaStreamIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> in;
        ogn::SimpleInput<const float,ogn::kCpu> maxVal;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    VizTranscoderRadarCfarDatabase(NodeObj const& nodeObjParam)
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
    VizTranscoderRadarCfarDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : VizTranscoderRadarCfarDatabase(nodeObjParam)
    {}

    //Main constructor
    VizTranscoderRadarCfarDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::colorCode.m_token, inputs::cudaStreamIn.m_token, inputs::in.m_token, inputs::maxVal.m_token
                )
            , kAccordingToContextIndex);
            inputs.colorCode.setContext(contextObj);
            inputs.colorCode.setHandle(std::get<0>(inputDataHandles0));
            inputs.cudaStreamIn.setContext(contextObj);
            inputs.cudaStreamIn.setHandle(std::get<1>(inputDataHandles0));
            inputs.in.setContext(contextObj);
            inputs.in.setHandle(std::get<2>(inputDataHandles0));
            inputs.maxVal.setContext(contextObj);
            inputs.maxVal.setHandle(std::get<3>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.radar.VizTranscoderRadarCfar");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::colorCode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cudaStreamIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::in.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::maxVal.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.radar");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Receives Radar cfar and sends it for visualization");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::colorCode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "0 - constant, 1 - HSV");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaStreamIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda Stream Input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::in.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::maxVal.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "max Cfar value");
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
        sm_stateManagerVizTranscoderRadarCfar.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.colorCode.isValid()
            && inputs.cudaStreamIn.isValid()
            && inputs.in.isValid()
            && inputs.maxVal.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.colorCode.invalidateCachedPointer();
            inputs.cudaStreamIn.invalidateCachedPointer();
            inputs.in.invalidateCachedPointer();
            inputs.maxVal.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::colorCode.m_token) {
                inputs.colorCode.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cudaStreamIn.m_token) {
                inputs.cudaStreamIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::in.m_token) {
                inputs.in.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::maxVal.m_token) {
                inputs.maxVal.invalidateCachedPointer();
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
            || !inputs.in.canVectorize()
            || !inputs.maxVal.canVectorize()
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
        if(token == inputs::in.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.in.setHandle(hdl);
            return;
        }
        if(token == inputs::maxVal.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.maxVal.setHandle(hdl);
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
ogn::StateManager VizTranscoderRadarCfarDatabase::sm_stateManagerVizTranscoderRadarCfar;
std::tuple<int, int, int> VizTranscoderRadarCfarDatabase::sm_generatorVersionVizTranscoderRadarCfar{std::make_tuple(1,79,2)};
std::tuple<int, int, int> VizTranscoderRadarCfarDatabase::sm_targetVersionVizTranscoderRadarCfar{std::make_tuple(2,184,5)};
}
using namespace IVizTranscoderRadarCfar;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<VizTranscoderRadarCfar, VizTranscoderRadarCfarDatabase> s_registration("omni.sensors.nv.radar.VizTranscoderRadarCfar", 1, "omni.sensors.nv.radar"); \
}
