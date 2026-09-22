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

namespace OgnSdSemanticFilterAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using hierarchicalLabels_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> hierarchicalLabels("inputs:hierarchicalLabels", "bool", kExtendedAttributeType_Regular, false);
using matchingLabels_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> matchingLabels("inputs:matchingLabels", "bool", kExtendedAttributeType_Regular, true);
using name_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> name("inputs:name", "token", kExtendedAttributeType_Regular);
using predicate_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> predicate("inputs:predicate", "token", kExtendedAttributeType_Regular);
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using name_t = NameToken&;
ogn::AttributeInitializer<NameToken, ogn::kOgnOutput> name("outputs:name", "token", kExtendedAttributeType_Regular);
using predicate_t = NameToken&;
ogn::AttributeInitializer<NameToken, ogn::kOgnOutput> predicate("outputs:predicate", "token", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdSemanticFilterAttributes;
namespace IOgnSdSemanticFilter
{
// Synthetic Data node to declare a semantic filter.
class OgnSdSemanticFilterDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdSemanticFilter.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdSemanticFilter.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdSemanticFilter.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdSemanticFilter.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdSemanticFilter;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdSemanticFilter;
    static std::tuple<int, int, int>sm_targetVersionOgnSdSemanticFilter;
    static constexpr size_t staticAttributeCount = 10;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , hierarchicalLabels{offset}
        , matchingLabels{offset}
        , name{offset}
        , predicate{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const bool,ogn::kCpu> hierarchicalLabels;
        ogn::SimpleInput<const bool,ogn::kCpu> matchingLabels;
        ogn::SimpleInput<const NameToken,ogn::kCpu> name;
        ogn::SimpleInput<const NameToken,ogn::kCpu> predicate;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , name{offset}
        , predicate{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<NameToken,ogn::kCpu> name;
        ogn::SimpleOutput<NameToken,ogn::kCpu> predicate;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdSemanticFilterDatabase(NodeObj const& nodeObjParam)
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
    OgnSdSemanticFilterDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdSemanticFilterDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdSemanticFilterDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::exec.m_token, inputs::hierarchicalLabels.m_token, inputs::matchingLabels.m_token, inputs::name.m_token,
                    inputs::predicate.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::name.m_token, outputs::predicate.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.hierarchicalLabels.setContext(contextObj);
            inputs.hierarchicalLabels.setHandle(std::get<1>(inputDataHandles0));
            inputs.matchingLabels.setContext(contextObj);
            inputs.matchingLabels.setHandle(std::get<2>(inputDataHandles0));
            inputs.name.setContext(contextObj);
            inputs.name.setHandle(std::get<3>(inputDataHandles0));
            inputs.predicate.setContext(contextObj);
            inputs.predicate.setHandle(std::get<4>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.name.setContext(contextObj);
            outputs.name.setHandle(std::get<1>(outputDataHandles0));
            outputs.predicate.setContext(contextObj);
            outputs.predicate.setHandle(std::get<2>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdSemanticFilter");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hierarchicalLabels.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::matchingLabels.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::name.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::predicate.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::name.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::predicate.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:simulation");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to declare a semantic filter.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Dependency");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hierarchicalLabels.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If true the filter consider all labels in the semantic hierarchy above the prims");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::matchingLabels.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If true output only the labels matching the filter (if false keep all labels of the matching prims)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "true");
        attr = iNode->getAttributeByToken(nodeObj, inputs::name.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Filter unique identifier [if empty, use the normalized predicate as an identifier]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::predicate.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The semantic filter specification : a disjunctive normal form of semantic type and label");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::name.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The semantic filter name identifier");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, outputs::predicate.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The semantic filter predicate in normalized form");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
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
        sm_stateManagerOgnSdSemanticFilter.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.hierarchicalLabels.isValid()
            && inputs.matchingLabels.isValid()
            && inputs.name.isValid()
            && inputs.predicate.isValid()
            && outputs.exec.isValid()
            && outputs.name.isValid()
            && outputs.predicate.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.hierarchicalLabels.invalidateCachedPointer();
            inputs.matchingLabels.invalidateCachedPointer();
            inputs.name.invalidateCachedPointer();
            inputs.predicate.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.name.invalidateCachedPointer();
            outputs.predicate.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hierarchicalLabels.m_token) {
                inputs.hierarchicalLabels.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::matchingLabels.m_token) {
                inputs.matchingLabels.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::name.m_token) {
                inputs.name.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::predicate.m_token) {
                inputs.predicate.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::name.m_token) {
                outputs.name.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::predicate.m_token) {
                outputs.predicate.invalidateCachedPointer();
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
        if( !inputs.exec.canVectorize()
            || !inputs.hierarchicalLabels.canVectorize()
            || !inputs.matchingLabels.canVectorize()
            || !inputs.name.canVectorize()
            || !inputs.predicate.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.name.canVectorize()
            || !outputs.predicate.canVectorize()
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
        if(token == inputs::exec.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exec.setHandle(hdl);
            return;
        }
        if(token == inputs::hierarchicalLabels.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hierarchicalLabels.setHandle(hdl);
            return;
        }
        if(token == inputs::matchingLabels.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.matchingLabels.setHandle(hdl);
            return;
        }
        if(token == inputs::name.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.name.setHandle(hdl);
            return;
        }
        if(token == inputs::predicate.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.predicate.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::name.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.name.setHandle(hdl);
            return;
        }
        if(token == outputs::predicate.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.predicate.setHandle(hdl);
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
ogn::StateManager OgnSdSemanticFilterDatabase::sm_stateManagerOgnSdSemanticFilter;
std::tuple<int, int, int> OgnSdSemanticFilterDatabase::sm_generatorVersionOgnSdSemanticFilter{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdSemanticFilterDatabase::sm_targetVersionOgnSdSemanticFilter{std::make_tuple(2,184,5)};
}
using namespace IOgnSdSemanticFilter;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdSemanticFilter, OgnSdSemanticFilterDatabase> s_registration("omni.syntheticdata.SdSemanticFilter", 1, "omni.syntheticdata"); \
}
