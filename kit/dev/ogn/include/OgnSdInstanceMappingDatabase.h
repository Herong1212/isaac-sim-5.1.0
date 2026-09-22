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

namespace OgnSdInstanceMappingAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using lazy_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> lazy("inputs:lazy", "bool", kExtendedAttributeType_Regular, true);
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using sdIMInstanceSemanticMap_t = ogn::array<uint8_t>&;
ogn::AttributeInitializer<uint8_t*, ogn::kOgnOutput> sdIMInstanceSemanticMap("outputs:sdIMInstanceSemanticMap", "uchar[]", kExtendedAttributeType_Regular, nullptr, 0);
using sdIMInstanceTokens_t = ogn::array<NameToken>&;
ogn::AttributeInitializer<NameToken*, ogn::kOgnOutput> sdIMInstanceTokens("outputs:sdIMInstanceTokens", "token[]", kExtendedAttributeType_Regular, nullptr, 0);
using sdIMLastUpdateTimeDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> sdIMLastUpdateTimeDenominator("outputs:sdIMLastUpdateTimeDenominator", "uint64", kExtendedAttributeType_Regular);
using sdIMLastUpdateTimeNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> sdIMLastUpdateTimeNumerator("outputs:sdIMLastUpdateTimeNumerator", "int64", kExtendedAttributeType_Regular);
using sdIMMaxSemanticHierarchyDepth_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> sdIMMaxSemanticHierarchyDepth("outputs:sdIMMaxSemanticHierarchyDepth", "uint", kExtendedAttributeType_Regular);
using sdIMMinInstanceIndex_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> sdIMMinInstanceIndex("outputs:sdIMMinInstanceIndex", "uint", kExtendedAttributeType_Regular);
using sdIMMinSemanticIndex_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> sdIMMinSemanticIndex("outputs:sdIMMinSemanticIndex", "uint", kExtendedAttributeType_Regular);
using sdIMNumInstances_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> sdIMNumInstances("outputs:sdIMNumInstances", "uint", kExtendedAttributeType_Regular);
using sdIMNumSemanticTokens_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> sdIMNumSemanticTokens("outputs:sdIMNumSemanticTokens", "uint", kExtendedAttributeType_Regular);
using sdIMNumSemantics_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> sdIMNumSemantics("outputs:sdIMNumSemantics", "uint", kExtendedAttributeType_Regular);
using sdIMSemanticLocalTransform_t = ogn::array<float>&;
ogn::AttributeInitializer<float*, ogn::kOgnOutput> sdIMSemanticLocalTransform("outputs:sdIMSemanticLocalTransform", "float[]", kExtendedAttributeType_Regular, nullptr, 0);
using sdIMSemanticTokenMap_t = ogn::array<NameToken>&;
ogn::AttributeInitializer<NameToken*, ogn::kOgnOutput> sdIMSemanticTokenMap("outputs:sdIMSemanticTokenMap", "token[]", kExtendedAttributeType_Regular, nullptr, 0);
using sdIMSemanticWorldTransform_t = ogn::array<float>&;
ogn::AttributeInitializer<float*, ogn::kOgnOutput> sdIMSemanticWorldTransform("outputs:sdIMSemanticWorldTransform", "float[]", kExtendedAttributeType_Regular, nullptr, 0);
}
namespace state
{
}
}
using namespace OgnSdInstanceMappingAttributes;
namespace IOgnSdInstanceMapping
{
// Synthetic Data node to expose the scene instances semantic hierarchy information
class OgnSdInstanceMappingDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken InstanceMappingInfoSDhost;
        NameToken InstanceMapSDhost;
        NameToken SemanticLabelTokenSDhost;
        NameToken InstancePrimTokenSDhost;
        NameToken SemanticLocalTransformSDhost;
        NameToken SemanticWorldTransformSDhost;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdInstanceMapping;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdInstanceMapping;
    static std::tuple<int, int, int>sm_targetVersionOgnSdInstanceMapping;
    static constexpr size_t staticAttributeCount = 19;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , lazy{offset}
        , renderResults{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const bool,ogn::kCpu> lazy;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , sdIMInstanceSemanticMap{offset}
        , sdIMInstanceTokens{offset}
        , sdIMLastUpdateTimeDenominator{offset}
        , sdIMLastUpdateTimeNumerator{offset}
        , sdIMMaxSemanticHierarchyDepth{offset}
        , sdIMMinInstanceIndex{offset}
        , sdIMMinSemanticIndex{offset}
        , sdIMNumInstances{offset}
        , sdIMNumSemanticTokens{offset}
        , sdIMNumSemantics{offset}
        , sdIMSemanticLocalTransform{offset}
        , sdIMSemanticTokenMap{offset}
        , sdIMSemanticWorldTransform{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::ArrayOutput<uint8_t,ogn::kCpu> sdIMInstanceSemanticMap;
        ogn::ArrayOutput<NameToken,ogn::kCpu> sdIMInstanceTokens;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> sdIMLastUpdateTimeDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> sdIMLastUpdateTimeNumerator;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> sdIMMaxSemanticHierarchyDepth;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> sdIMMinInstanceIndex;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> sdIMMinSemanticIndex;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> sdIMNumInstances;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> sdIMNumSemanticTokens;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> sdIMNumSemantics;
        ogn::ArrayOutput<float,ogn::kCpu> sdIMSemanticLocalTransform;
        ogn::ArrayOutput<NameToken,ogn::kCpu> sdIMSemanticTokenMap;
        ogn::ArrayOutput<float,ogn::kCpu> sdIMSemanticWorldTransform;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdInstanceMappingDatabase(NodeObj const& nodeObjParam)
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
    OgnSdInstanceMappingDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdInstanceMappingDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdInstanceMappingDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::exec.m_token, inputs::lazy.m_token, inputs::renderResults.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::sdIMInstanceSemanticMap.m_token, outputs::sdIMInstanceTokens.m_token, outputs::sdIMLastUpdateTimeDenominator.m_token,
                    outputs::sdIMLastUpdateTimeNumerator.m_token, outputs::sdIMMaxSemanticHierarchyDepth.m_token, outputs::sdIMMinInstanceIndex.m_token, outputs::sdIMMinSemanticIndex.m_token,
                    outputs::sdIMNumInstances.m_token, outputs::sdIMNumSemanticTokens.m_token, outputs::sdIMNumSemantics.m_token, outputs::sdIMSemanticLocalTransform.m_token,
                    outputs::sdIMSemanticTokenMap.m_token, outputs::sdIMSemanticWorldTransform.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.lazy.setContext(contextObj);
            inputs.lazy.setHandle(std::get<1>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<2>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.sdIMInstanceSemanticMap.setContext(contextObj);
            outputs.sdIMInstanceSemanticMap.setHandle(std::get<1>(outputDataHandles0));
            outputs.sdIMInstanceTokens.setContext(contextObj);
            outputs.sdIMInstanceTokens.setHandle(std::get<2>(outputDataHandles0));
            outputs.sdIMLastUpdateTimeDenominator.setContext(contextObj);
            outputs.sdIMLastUpdateTimeDenominator.setHandle(std::get<3>(outputDataHandles0));
            outputs.sdIMLastUpdateTimeNumerator.setContext(contextObj);
            outputs.sdIMLastUpdateTimeNumerator.setHandle(std::get<4>(outputDataHandles0));
            outputs.sdIMMaxSemanticHierarchyDepth.setContext(contextObj);
            outputs.sdIMMaxSemanticHierarchyDepth.setHandle(std::get<5>(outputDataHandles0));
            outputs.sdIMMinInstanceIndex.setContext(contextObj);
            outputs.sdIMMinInstanceIndex.setHandle(std::get<6>(outputDataHandles0));
            outputs.sdIMMinSemanticIndex.setContext(contextObj);
            outputs.sdIMMinSemanticIndex.setHandle(std::get<7>(outputDataHandles0));
            outputs.sdIMNumInstances.setContext(contextObj);
            outputs.sdIMNumInstances.setHandle(std::get<8>(outputDataHandles0));
            outputs.sdIMNumSemanticTokens.setContext(contextObj);
            outputs.sdIMNumSemanticTokens.setHandle(std::get<9>(outputDataHandles0));
            outputs.sdIMNumSemantics.setContext(contextObj);
            outputs.sdIMNumSemantics.setHandle(std::get<10>(outputDataHandles0));
            outputs.sdIMSemanticLocalTransform.setContext(contextObj);
            outputs.sdIMSemanticLocalTransform.setHandle(std::get<11>(outputDataHandles0));
            outputs.sdIMSemanticTokenMap.setContext(contextObj);
            outputs.sdIMSemanticTokenMap.setHandle(std::get<12>(outputDataHandles0));
            outputs.sdIMSemanticWorldTransform.setContext(contextObj);
            outputs.sdIMSemanticWorldTransform.setHandle(std::get<13>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdInstanceMapping");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdInstanceMappingDatabase::tokens.InstanceMappingInfoSDhost = iToken.getHandle("InstanceMappingInfoSDhost");
        OgnSdInstanceMappingDatabase::tokens.InstanceMapSDhost = iToken.getHandle("InstanceMapSDhost");
        OgnSdInstanceMappingDatabase::tokens.SemanticLabelTokenSDhost = iToken.getHandle("SemanticLabelTokenSDhost");
        OgnSdInstanceMappingDatabase::tokens.InstancePrimTokenSDhost = iToken.getHandle("InstancePrimTokenSDhost");
        OgnSdInstanceMappingDatabase::tokens.SemanticLocalTransformSDhost = iToken.getHandle("SemanticLocalTransformSDhost");
        OgnSdInstanceMappingDatabase::tokens.SemanticWorldTransformSDhost = iToken.getHandle("SemanticWorldTransformSDhost");

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::lazy.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMInstanceSemanticMap.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMInstanceTokens.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMLastUpdateTimeDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMLastUpdateTimeNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMMaxSemanticHierarchyDepth.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMMinInstanceIndex.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMMinSemanticIndex.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMNumInstances.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMNumSemanticTokens.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMNumSemantics.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMSemanticLocalTransform.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMSemanticTokenMap.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdIMSemanticWorldTransform.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"InstanceMappingInfoSDhost\", \"InstanceMapSDhost\", \"SemanticLabelTokenSDhost\", \"InstancePrimTokenSDhost\", \"SemanticLocalTransformSDhost\", \"SemanticWorldTransformSDhost\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:action");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to expose the scene instances semantic hierarchy information");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::lazy.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Compute outputs only when connected to a downstream node");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "true");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render results pointer");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes when the event is received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Received");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMInstanceSemanticMap.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Raw array of uint16_t of size sdIMNumInstances*sdIMMaxSemanticHierarchyDepth containing the mapping from the instances index to their inherited semantic entities");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMInstanceTokens.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Instance array containing the token for every instances");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMLastUpdateTimeDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time denominator of the last time the data has changed");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMLastUpdateTimeNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time numerator of the last time the data has changed");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMMaxSemanticHierarchyDepth.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Maximal number of semantic entities inherited by an instance");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMMinInstanceIndex.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Instance id of the first instance in the instance arrays");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMMinSemanticIndex.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Semantic id of the first semantic entity in the semantic arrays");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMNumInstances.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number of instances in the instance arrays");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMNumSemanticTokens.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number of semantics token including the semantic entity path, the semantic entity types and if the number of semantic types is greater than one a ");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMNumSemantics.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number of semantic entities in the semantic arrays");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMSemanticLocalTransform.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Semantic array of 4x4 float matrices containing the transform from world to local space for every semantic entity");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMSemanticTokenMap.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Semantic array of token of size numSemantics * numSemanticTypes containing the mapping from the semantic entities to the semantic entity path and semantic types");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdIMSemanticWorldTransform.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Semantic array of 4x4 float matrices containing the transform from local to world space for every semantic entity");
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
        sm_stateManagerOgnSdInstanceMapping.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.lazy.isValid()
            && inputs.renderResults.isValid()
            && outputs.exec.isValid()
            && outputs.sdIMInstanceSemanticMap.isValid()
            && outputs.sdIMInstanceTokens.isValid()
            && outputs.sdIMLastUpdateTimeDenominator.isValid()
            && outputs.sdIMLastUpdateTimeNumerator.isValid()
            && outputs.sdIMMaxSemanticHierarchyDepth.isValid()
            && outputs.sdIMMinInstanceIndex.isValid()
            && outputs.sdIMMinSemanticIndex.isValid()
            && outputs.sdIMNumInstances.isValid()
            && outputs.sdIMNumSemanticTokens.isValid()
            && outputs.sdIMNumSemantics.isValid()
            && outputs.sdIMSemanticLocalTransform.isValid()
            && outputs.sdIMSemanticTokenMap.isValid()
            && outputs.sdIMSemanticWorldTransform.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.lazy.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.sdIMInstanceSemanticMap.invalidateCachedPointer();
            outputs.sdIMInstanceTokens.invalidateCachedPointer();
            outputs.sdIMLastUpdateTimeDenominator.invalidateCachedPointer();
            outputs.sdIMLastUpdateTimeNumerator.invalidateCachedPointer();
            outputs.sdIMMaxSemanticHierarchyDepth.invalidateCachedPointer();
            outputs.sdIMMinInstanceIndex.invalidateCachedPointer();
            outputs.sdIMMinSemanticIndex.invalidateCachedPointer();
            outputs.sdIMNumInstances.invalidateCachedPointer();
            outputs.sdIMNumSemanticTokens.invalidateCachedPointer();
            outputs.sdIMNumSemantics.invalidateCachedPointer();
            outputs.sdIMSemanticLocalTransform.invalidateCachedPointer();
            outputs.sdIMSemanticTokenMap.invalidateCachedPointer();
            outputs.sdIMSemanticWorldTransform.invalidateCachedPointer();
            return;
        }
        outputs.sdIMInstanceSemanticMap.invalidateCachedPointer();
        outputs.sdIMInstanceTokens.invalidateCachedPointer();
        outputs.sdIMSemanticLocalTransform.invalidateCachedPointer();
        outputs.sdIMSemanticTokenMap.invalidateCachedPointer();
        outputs.sdIMSemanticWorldTransform.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::lazy.m_token) {
                inputs.lazy.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderResults.m_token) {
                inputs.renderResults.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMInstanceSemanticMap.m_token) {
                outputs.sdIMInstanceSemanticMap.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMInstanceTokens.m_token) {
                outputs.sdIMInstanceTokens.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMLastUpdateTimeDenominator.m_token) {
                outputs.sdIMLastUpdateTimeDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMLastUpdateTimeNumerator.m_token) {
                outputs.sdIMLastUpdateTimeNumerator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMMaxSemanticHierarchyDepth.m_token) {
                outputs.sdIMMaxSemanticHierarchyDepth.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMMinInstanceIndex.m_token) {
                outputs.sdIMMinInstanceIndex.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMMinSemanticIndex.m_token) {
                outputs.sdIMMinSemanticIndex.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMNumInstances.m_token) {
                outputs.sdIMNumInstances.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMNumSemanticTokens.m_token) {
                outputs.sdIMNumSemanticTokens.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMNumSemantics.m_token) {
                outputs.sdIMNumSemantics.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMSemanticLocalTransform.m_token) {
                outputs.sdIMSemanticLocalTransform.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMSemanticTokenMap.m_token) {
                outputs.sdIMSemanticTokenMap.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdIMSemanticWorldTransform.m_token) {
                outputs.sdIMSemanticWorldTransform.invalidateCachedPointer();
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
            || !inputs.lazy.canVectorize()
            || !inputs.renderResults.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.sdIMLastUpdateTimeDenominator.canVectorize()
            || !outputs.sdIMLastUpdateTimeNumerator.canVectorize()
            || !outputs.sdIMMaxSemanticHierarchyDepth.canVectorize()
            || !outputs.sdIMMinInstanceIndex.canVectorize()
            || !outputs.sdIMMinSemanticIndex.canVectorize()
            || !outputs.sdIMNumInstances.canVectorize()
            || !outputs.sdIMNumSemanticTokens.canVectorize()
            || !outputs.sdIMNumSemantics.canVectorize()
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
        if(token == inputs::lazy.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.lazy.setHandle(hdl);
            return;
        }
        if(token == inputs::renderResults.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderResults.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMInstanceSemanticMap.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMInstanceSemanticMap.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMInstanceTokens.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMInstanceTokens.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMLastUpdateTimeDenominator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMLastUpdateTimeDenominator.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMLastUpdateTimeNumerator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMLastUpdateTimeNumerator.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMMaxSemanticHierarchyDepth.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMMaxSemanticHierarchyDepth.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMMinInstanceIndex.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMMinInstanceIndex.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMMinSemanticIndex.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMMinSemanticIndex.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMNumInstances.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMNumInstances.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMNumSemanticTokens.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMNumSemanticTokens.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMNumSemantics.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMNumSemantics.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMSemanticLocalTransform.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMSemanticLocalTransform.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMSemanticTokenMap.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMSemanticTokenMap.setHandle(hdl);
            return;
        }
        if(token == outputs::sdIMSemanticWorldTransform.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdIMSemanticWorldTransform.setHandle(hdl);
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
ogn::StateManager OgnSdInstanceMappingDatabase::sm_stateManagerOgnSdInstanceMapping;
std::tuple<int, int, int> OgnSdInstanceMappingDatabase::sm_generatorVersionOgnSdInstanceMapping{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdInstanceMappingDatabase::sm_targetVersionOgnSdInstanceMapping{std::make_tuple(2,184,5)};
OgnSdInstanceMappingDatabase::TokenManager OgnSdInstanceMappingDatabase::tokens;
}
using namespace IOgnSdInstanceMapping;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdInstanceMapping, OgnSdInstanceMappingDatabase> s_registration("omni.syntheticdata.SdInstanceMapping", 2, "omni.syntheticdata"); \
}
