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
#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>

namespace OgnTimestepSelectorAttributes
{
namespace inputs
{
using fps_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> fps("inputs:fps", "double", kExtendedAttributeType_Regular, 1.0);
using time_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> time("inputs:time", "double", kExtendedAttributeType_Regular, -1.0);
}
namespace outputs
{
using timestep_t = int&;
ogn::AttributeInitializer<int, ogn::kOgnOutput> timestep("outputs:timestep", "int", kExtendedAttributeType_Regular, -1);
}
namespace state
{
}
}
using namespace OgnTimestepSelectorAttributes;
namespace IOgnTimestepSelector
{
// Selects a timestep from time input
class OgnTimestepSelectorDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnTimestepSelector.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnTimestepSelector.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnTimestepSelector.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnTimestepSelector.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnTimestepSelector;
    static std::tuple<int, int, int>sm_generatorVersionOgnTimestepSelector;
    static std::tuple<int, int, int>sm_targetVersionOgnTimestepSelector;
    static constexpr size_t staticAttributeCount = 5;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : fps{offset}
        , time{offset}
        {}
        ogn::SimpleInput<const double,ogn::kCpu> fps;
        ogn::SimpleInput<const double,ogn::kCpu> time;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : timestep{offset}
        {}
        ogn::SimpleOutput<int,ogn::kCpu> timestep;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnTimestepSelectorDatabase(NodeObj const& nodeObjParam)
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
    OgnTimestepSelectorDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnTimestepSelectorDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnTimestepSelectorDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::fps.m_token, inputs::time.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::timestep.m_token
                )
            , kAccordingToContextIndex);
            inputs.fps.setContext(contextObj);
            inputs.fps.setHandle(std::get<0>(inputDataHandles0));
            inputs.time.setContext(contextObj);
            inputs.time.setHandle(std::get<1>(inputDataHandles0));
            outputs.timestep.setContext(contextObj);
            outputs.timestep.setHandle(std::get<0>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.index.compute.timestepSelector");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::fps.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::time.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::timestep.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.index.compute");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataUiName, "Timestep selector");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Selects a timestep from time input");
        auto __schedulingInfo = nodeTypeObj.iNodeType->getSchedulingHints(nodeTypeObj);
        CARB_ASSERT(__schedulingInfo, "Could not acquire the scheduling hints");
        if (__schedulingInfo)
        {
            __schedulingInfo->setThreadSafety(eThreadSafety::eSafe);
            auto __schedulingInfo2 = omni::core::cast<ISchedulingHints2>(__schedulingInfo).get();
            if (__schedulingInfo2)
            {
            }
        }
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::fps.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "FPS");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "FPS");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::time.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Time");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1.0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::timestep.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Timestep");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Timestep");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1");
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
        sm_stateManagerOgnTimestepSelector.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.fps.isValid()
            && inputs.time.isValid()
            && outputs.timestep.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.fps.invalidateCachedPointer();
            inputs.time.invalidateCachedPointer();
            outputs.timestep.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::fps.m_token) {
                inputs.fps.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::time.m_token) {
                inputs.time.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::timestep.m_token) {
                outputs.timestep.invalidateCachedPointer();
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
        if( !inputs.fps.canVectorize()
            || !inputs.time.canVectorize()
            || !outputs.timestep.canVectorize()
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
        if(token == inputs::fps.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.fps.setHandle(hdl);
            return;
        }
        if(token == inputs::time.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.time.setHandle(hdl);
            return;
        }
        if(token == outputs::timestep.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.timestep.setHandle(hdl);
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
ogn::StateManager OgnTimestepSelectorDatabase::sm_stateManagerOgnTimestepSelector;
std::tuple<int, int, int> OgnTimestepSelectorDatabase::sm_generatorVersionOgnTimestepSelector{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnTimestepSelectorDatabase::sm_targetVersionOgnTimestepSelector{std::make_tuple(2,184,5)};
}
using namespace IOgnTimestepSelector;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnTimestepSelector, OgnTimestepSelectorDatabase> s_registration("omni.index.compute.timestepSelector", 1, "omni.index.compute"); \
}
