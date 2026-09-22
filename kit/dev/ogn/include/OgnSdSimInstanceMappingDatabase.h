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

namespace OgnSdSimInstanceMappingAttributes
{
namespace inputs
{
using needTransform_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> needTransform("inputs:needTransform", "bool", kExtendedAttributeType_Regular, true);
using semanticFilterPredicate_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> semanticFilterPredicate("inputs:semanticFilterPredicate", "token", kExtendedAttributeType_Regular);
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using semanticFilterPredicate_t = NameToken&;
ogn::AttributeInitializer<NameToken, ogn::kOgnOutput> semanticFilterPredicate("outputs:semanticFilterPredicate", "token", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdSimInstanceMappingAttributes;
namespace IOgnSdSimInstanceMapping
{
// Synthetic Data node to update and cache the instance mapping data
class OgnSdSimInstanceMappingDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdSimInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdSimInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdSimInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdSimInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdSimInstanceMapping;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdSimInstanceMapping;
    static std::tuple<int, int, int>sm_targetVersionOgnSdSimInstanceMapping;
    static constexpr size_t staticAttributeCount = 6;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : needTransform{offset}
        , semanticFilterPredicate{offset}
        {}
        ogn::SimpleInput<const bool,ogn::kCpu> needTransform;
        ogn::SimpleInput<const NameToken,ogn::kCpu> semanticFilterPredicate;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , semanticFilterPredicate{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<NameToken,ogn::kCpu> semanticFilterPredicate;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdSimInstanceMappingDatabase(NodeObj const& nodeObjParam)
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
    OgnSdSimInstanceMappingDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdSimInstanceMappingDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdSimInstanceMappingDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::needTransform.m_token, inputs::semanticFilterPredicate.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::semanticFilterPredicate.m_token
                )
            , kAccordingToContextIndex);
            inputs.needTransform.setContext(contextObj);
            inputs.needTransform.setHandle(std::get<0>(inputDataHandles0));
            inputs.semanticFilterPredicate.setContext(contextObj);
            inputs.semanticFilterPredicate.setHandle(std::get<1>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.semanticFilterPredicate.setContext(contextObj);
            outputs.semanticFilterPredicate.setHandle(std::get<1>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdSimInstanceMapping");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_semanticFilterPredicate_token {"*:*"};
        inputs::semanticFilterPredicate.setDefault(inputs_semanticFilterPredicate_token.asTokenC());
        inputs::needTransform.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticFilterPredicate.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticFilterPredicate.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:simulation,internal");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to update and cache the instance mapping data");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::needTransform.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If true compute the semantic entities world and object transforms");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "true");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticFilterPredicate.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The semantic filter predicate : a disjunctive normal form of semantic type and label");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"*:*\"");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticFilterPredicate.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The semantic filter predicate in normalized form");
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
        sm_stateManagerOgnSdSimInstanceMapping.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.needTransform.isValid()
            && inputs.semanticFilterPredicate.isValid()
            && outputs.exec.isValid()
            && outputs.semanticFilterPredicate.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.needTransform.invalidateCachedPointer();
            inputs.semanticFilterPredicate.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.semanticFilterPredicate.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::needTransform.m_token) {
                inputs.needTransform.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticFilterPredicate.m_token) {
                inputs.semanticFilterPredicate.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticFilterPredicate.m_token) {
                outputs.semanticFilterPredicate.invalidateCachedPointer();
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
        if( !inputs.needTransform.canVectorize()
            || !inputs.semanticFilterPredicate.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.semanticFilterPredicate.canVectorize()
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
        if(token == inputs::needTransform.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.needTransform.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticFilterPredicate.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticFilterPredicate.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticFilterPredicate.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticFilterPredicate.setHandle(hdl);
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
ogn::StateManager OgnSdSimInstanceMappingDatabase::sm_stateManagerOgnSdSimInstanceMapping;
std::tuple<int, int, int> OgnSdSimInstanceMappingDatabase::sm_generatorVersionOgnSdSimInstanceMapping{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdSimInstanceMappingDatabase::sm_targetVersionOgnSdSimInstanceMapping{std::make_tuple(2,184,5)};
}
using namespace IOgnSdSimInstanceMapping;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdSimInstanceMapping, OgnSdSimInstanceMappingDatabase> s_registration("omni.syntheticdata.SdSimInstanceMapping", 1, "omni.syntheticdata"); \
}
