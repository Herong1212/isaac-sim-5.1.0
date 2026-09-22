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
#include <omni/graph/image/unstable/ComputeParamsBuilder.h>

namespace OgnSdTestInstanceMappingAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using instanceMapPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> instanceMapPtr("inputs:instanceMapPtr", "uint64", kExtendedAttributeType_Regular, 0);
using instancePrimPathPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> instancePrimPathPtr("inputs:instancePrimPathPtr", "uint64", kExtendedAttributeType_Regular, 0);
using minInstanceIndex_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> minInstanceIndex("inputs:minInstanceIndex", "uint", kExtendedAttributeType_Regular, 0);
using minSemanticIndex_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> minSemanticIndex("inputs:minSemanticIndex", "uint", kExtendedAttributeType_Regular, 0);
using numInstances_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> numInstances("inputs:numInstances", "uint", kExtendedAttributeType_Regular, 0);
using numSemantics_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> numSemantics("inputs:numSemantics", "uint", kExtendedAttributeType_Regular, 0);
using semanticLabelTokenPtrs_t = const ogn::const_array<uint64_t>&;
ogn::AttributeInitializer<const uint64_t*, ogn::kOgnInput> semanticLabelTokenPtrs("inputs:semanticLabelTokenPtrs", "uint64[]", kExtendedAttributeType_Regular, nullptr, 0);
using semanticLocalTransformPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticLocalTransformPtr("inputs:semanticLocalTransformPtr", "uint64", kExtendedAttributeType_Regular, 0);
using semanticMapPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticMapPtr("inputs:semanticMapPtr", "uint64", kExtendedAttributeType_Regular, 0);
using semanticPrimPathPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticPrimPathPtr("inputs:semanticPrimPathPtr", "uint64", kExtendedAttributeType_Regular, 0);
using semanticWorldTransformPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticWorldTransformPtr("inputs:semanticWorldTransformPtr", "uint64", kExtendedAttributeType_Regular, 0);
using stage_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> stage("inputs:stage", "token", kExtendedAttributeType_Regular);
using swhFrameNumber_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> swhFrameNumber("inputs:swhFrameNumber", "uint64", kExtendedAttributeType_Regular, 0);
using testCaseIndex_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> testCaseIndex("inputs:testCaseIndex", "int", kExtendedAttributeType_Regular, -1);
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using semanticFilterPredicate_t = NameToken&;
ogn::AttributeInitializer<NameToken, ogn::kOgnOutput> semanticFilterPredicate("outputs:semanticFilterPredicate", "token", kExtendedAttributeType_Regular);
using success_t = bool&;
ogn::AttributeInitializer<bool, ogn::kOgnOutput> success("outputs:success", "bool", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdTestInstanceMappingAttributes;
namespace IOgnSdTestInstanceMapping
{
// Synthetic Data node to test the instance mapping pipeline
class OgnSdTestInstanceMappingDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken simulation;
        NameToken postRender;
        NameToken onDemand;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdTestInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdTestInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdTestInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdTestInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdTestInstanceMapping;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdTestInstanceMapping;
    static std::tuple<int, int, int>sm_targetVersionOgnSdTestInstanceMapping;
    static constexpr size_t staticAttributeCount = 20;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , instanceMapPtr{offset}
        , instancePrimPathPtr{offset}
        , minInstanceIndex{offset}
        , minSemanticIndex{offset}
        , numInstances{offset}
        , numSemantics{offset}
        , semanticLabelTokenPtrs{offset}
        , semanticLocalTransformPtr{offset}
        , semanticMapPtr{offset}
        , semanticPrimPathPtr{offset}
        , semanticWorldTransformPtr{offset}
        , stage{offset}
        , swhFrameNumber{offset}
        , testCaseIndex{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> instanceMapPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> instancePrimPathPtr;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> minInstanceIndex;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> minSemanticIndex;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> numInstances;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> numSemantics;
        ogn::ArrayInput<const uint64_t,ogn::kCpu> semanticLabelTokenPtrs;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticLocalTransformPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticMapPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticPrimPathPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticWorldTransformPtr;
        ogn::SimpleInput<const NameToken,ogn::kCpu> stage;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> swhFrameNumber;
        ogn::SimpleInput<const int,ogn::kCpu> testCaseIndex;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , semanticFilterPredicate{offset}
        , success{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<NameToken,ogn::kCpu> semanticFilterPredicate;
        ogn::SimpleOutput<bool,ogn::kCpu> success;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdTestInstanceMappingDatabase(NodeObj const& nodeObjParam)
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
    OgnSdTestInstanceMappingDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdTestInstanceMappingDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdTestInstanceMappingDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
    : OmniGraphDatabase()
    , inputs{m_offset.index}
    , outputs{m_offset.index}
    {
        _ctor(contextObjParam, nodeObjParam, handleCount);
        _init();
    }

private:
    void _init() {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        GraphContextObj const& contextObj = abi_context();
        NodeObj const& nodeObj = abi_node();
        {
            auto inputDataHandles0 = getAttributesR<
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::exec.m_token, inputs::instanceMapPtr.m_token, inputs::instancePrimPathPtr.m_token, inputs::minInstanceIndex.m_token,
                    inputs::minSemanticIndex.m_token, inputs::numInstances.m_token, inputs::numSemantics.m_token, inputs::semanticLabelTokenPtrs.m_token,
                    inputs::semanticLocalTransformPtr.m_token, inputs::semanticMapPtr.m_token, inputs::semanticPrimPathPtr.m_token, inputs::semanticWorldTransformPtr.m_token,
                    inputs::stage.m_token, inputs::swhFrameNumber.m_token, inputs::testCaseIndex.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::semanticFilterPredicate.m_token, outputs::success.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.instanceMapPtr.setContext(contextObj);
            inputs.instanceMapPtr.setHandle(std::get<1>(inputDataHandles0));
            inputs.instancePrimPathPtr.setContext(contextObj);
            inputs.instancePrimPathPtr.setHandle(std::get<2>(inputDataHandles0));
            inputs.minInstanceIndex.setContext(contextObj);
            inputs.minInstanceIndex.setHandle(std::get<3>(inputDataHandles0));
            inputs.minSemanticIndex.setContext(contextObj);
            inputs.minSemanticIndex.setHandle(std::get<4>(inputDataHandles0));
            inputs.numInstances.setContext(contextObj);
            inputs.numInstances.setHandle(std::get<5>(inputDataHandles0));
            inputs.numSemantics.setContext(contextObj);
            inputs.numSemantics.setHandle(std::get<6>(inputDataHandles0));
            inputs.semanticLabelTokenPtrs.setContext(contextObj);
            inputs.semanticLabelTokenPtrs.setHandle(std::get<7>(inputDataHandles0));
            inputs.semanticLocalTransformPtr.setContext(contextObj);
            inputs.semanticLocalTransformPtr.setHandle(std::get<8>(inputDataHandles0));
            inputs.semanticMapPtr.setContext(contextObj);
            inputs.semanticMapPtr.setHandle(std::get<9>(inputDataHandles0));
            inputs.semanticPrimPathPtr.setContext(contextObj);
            inputs.semanticPrimPathPtr.setHandle(std::get<10>(inputDataHandles0));
            inputs.semanticWorldTransformPtr.setContext(contextObj);
            inputs.semanticWorldTransformPtr.setHandle(std::get<11>(inputDataHandles0));
            inputs.stage.setContext(contextObj);
            inputs.stage.setHandle(std::get<12>(inputDataHandles0));
            inputs.swhFrameNumber.setContext(contextObj);
            inputs.swhFrameNumber.setHandle(std::get<13>(inputDataHandles0));
            inputs.testCaseIndex.setContext(contextObj);
            inputs.testCaseIndex.setHandle(std::get<14>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.semanticFilterPredicate.setContext(contextObj);
            outputs.semanticFilterPredicate.setHandle(std::get<1>(outputDataHandles0));
            outputs.success.setContext(contextObj);
            outputs.success.setHandle(std::get<2>(outputDataHandles0));
        }
        tryGetDynamicAttributes<AttributePortType::kAttributePortType_Input>(staticAttributeCount, m_dynamicInputs);
        tryGetDynamicAttributes<AttributePortType::kAttributePortType_Output>(staticAttributeCount, m_dynamicOutputs);
        tryGetDynamicAttributes<AttributePortType::kAttributePortType_State>(staticAttributeCount, m_dynamicStates);

        collectMappedAttributes(m_mappedAttributes);

        m_canCachePointers = contextObj.iContext->canCacheAttributePointers ?
                                 contextObj.iContext->canCacheAttributePointers(contextObj) : true;
        // LCOV_EXCL_STOP
    }

public:
    static void initializeType(const NodeTypeObj& nodeTypeObj)
    {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        const INodeType* iNodeType = nodeTypeObj.iNodeType;
        auto iTokenPtr = carb::getCachedInterface<omni::fabric::IToken>();
        if( ! iTokenPtr ) {
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdTestInstanceMapping");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdTestInstanceMappingDatabase::tokens.simulation = iToken.getHandle("simulation");
        OgnSdTestInstanceMappingDatabase::tokens.postRender = iToken.getHandle("postRender");
        OgnSdTestInstanceMappingDatabase::tokens.onDemand = iToken.getHandle("onDemand");

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::instanceMapPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::instancePrimPathPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::minInstanceIndex.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::minSemanticIndex.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::numInstances.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::numSemantics.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticLabelTokenPtrs.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticLocalTransformPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticMapPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticPrimPathPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticWorldTransformPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::stage.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::swhFrameNumber.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::testCaseIndex.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticFilterPredicate.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::success.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"simulation\", \"postRender\", \"onDemand\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:simulation,graph:postRender,graph:action,internal:test");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to test the instance mapping pipeline");
        // LCOV_EXCL_STOP
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::instanceMapPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numInstances uint16_t containing the semantic index of the instance prim first semantic prim parent");
        attr = iNode->getAttributeByToken(nodeObj, inputs::instancePrimPathPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numInstances uint64_t containing the prim path tokens for every instance prims");
        attr = iNode->getAttributeByToken(nodeObj, inputs::minInstanceIndex.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Instance index of the first instance prim in the instance arrays");
        attr = iNode->getAttributeByToken(nodeObj, inputs::minSemanticIndex.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Semantic index of the first semantic prim in the semantic arrays");
        attr = iNode->getAttributeByToken(nodeObj, inputs::numInstances.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number of instances prim in the instance arrays");
        attr = iNode->getAttributeByToken(nodeObj, inputs::numSemantics.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number of semantic prim in the semantic arrays");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticLabelTokenPtrs.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array containing for every input semantic filters the corresponding array pointer of numSemantics uint64_t representing the semantic label of the semantic prim");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticLocalTransformPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numSemantics 4x4 float matrices containing the transform from world to object space for every semantic prims");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticMapPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numSemantics uint16_t containing the semantic index of the semantic prim first semantic prim parent");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticPrimPathPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numSemantics uint32_t containing the prim part of the prim path tokens for every semantic prims");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticWorldTransformPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numSemantics 4x4 float matrices containing the transform from local to world space for every semantic entity");
        attr = iNode->getAttributeByToken(nodeObj, inputs::stage.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Stage in {simulation, postrender, ondemand}");
        attr = iNode->getAttributeByToken(nodeObj, inputs::swhFrameNumber.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Fabric frame number");
        attr = iNode->getAttributeByToken(nodeObj, inputs::testCaseIndex.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Test case index");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes when the event is received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Received");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticFilterPredicate.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The semantic filter predicate : a disjunctive normal form of semantic type and label");
        attr = iNode->getAttributeByToken(nodeObj, outputs::success.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Test value : false if failed");
        // LCOV_EXCL_STOP
    }
    std::vector<ogn::DynamicInput> const& getDynamicInputs() const
    {
        return m_dynamicInputs;  // LCOV_EXCL_LINE
    }
    gsl::span<ogn::DynamicOutput> getDynamicOutputs()
    {
        return m_dynamicOutputs;  // LCOV_EXCL_LINE
    }
    gsl::span<ogn::DynamicState> getDynamicStates()
    {
        return m_dynamicStates;  // LCOV_EXCL_LINE
    }
    static void release(const NodeObj& nodeObj, GraphInstanceID instanceID)
    {
        sm_stateManagerOgnSdTestInstanceMapping.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        return validateNode()
            && inputs.exec.isValid()
            && inputs.instanceMapPtr.isValid()
            && inputs.instancePrimPathPtr.isValid()
            && inputs.minInstanceIndex.isValid()
            && inputs.minSemanticIndex.isValid()
            && inputs.numInstances.isValid()
            && inputs.numSemantics.isValid()
            && inputs.semanticLabelTokenPtrs.isValid()
            && inputs.semanticLocalTransformPtr.isValid()
            && inputs.semanticMapPtr.isValid()
            && inputs.semanticPrimPathPtr.isValid()
            && inputs.semanticWorldTransformPtr.isValid()
            && inputs.stage.isValid()
            && inputs.swhFrameNumber.isValid()
            && inputs.testCaseIndex.isValid()
            && outputs.exec.isValid()
            && outputs.semanticFilterPredicate.isValid()
            && outputs.success.isValid()
        ;
        // LCOV_EXCL_STOP
    }
    void preCompute() {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.instanceMapPtr.invalidateCachedPointer();
            inputs.instancePrimPathPtr.invalidateCachedPointer();
            inputs.minInstanceIndex.invalidateCachedPointer();
            inputs.minSemanticIndex.invalidateCachedPointer();
            inputs.numInstances.invalidateCachedPointer();
            inputs.numSemantics.invalidateCachedPointer();
            inputs.semanticLabelTokenPtrs.invalidateCachedPointer();
            inputs.semanticLocalTransformPtr.invalidateCachedPointer();
            inputs.semanticMapPtr.invalidateCachedPointer();
            inputs.semanticPrimPathPtr.invalidateCachedPointer();
            inputs.semanticWorldTransformPtr.invalidateCachedPointer();
            inputs.stage.invalidateCachedPointer();
            inputs.swhFrameNumber.invalidateCachedPointer();
            inputs.testCaseIndex.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.semanticFilterPredicate.invalidateCachedPointer();
            outputs.success.invalidateCachedPointer();
            return;
        }
        inputs.semanticLabelTokenPtrs.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::instanceMapPtr.m_token) {
                inputs.instanceMapPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::instancePrimPathPtr.m_token) {
                inputs.instancePrimPathPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::minInstanceIndex.m_token) {
                inputs.minInstanceIndex.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::minSemanticIndex.m_token) {
                inputs.minSemanticIndex.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::numInstances.m_token) {
                inputs.numInstances.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::numSemantics.m_token) {
                inputs.numSemantics.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticLabelTokenPtrs.m_token) {
                inputs.semanticLabelTokenPtrs.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticLocalTransformPtr.m_token) {
                inputs.semanticLocalTransformPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticMapPtr.m_token) {
                inputs.semanticMapPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticPrimPathPtr.m_token) {
                inputs.semanticPrimPathPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticWorldTransformPtr.m_token) {
                inputs.semanticWorldTransformPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::stage.m_token) {
                inputs.stage.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::swhFrameNumber.m_token) {
                inputs.swhFrameNumber.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::testCaseIndex.m_token) {
                inputs.testCaseIndex.invalidateCachedPointer();
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
            if(attrib == outputs::success.m_token) {
                outputs.success.invalidateCachedPointer();
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
        // LCOV_EXCL_STOP
    }
    bool canVectorize() const {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        if( !inputs.exec.canVectorize()
            || !inputs.instanceMapPtr.canVectorize()
            || !inputs.instancePrimPathPtr.canVectorize()
            || !inputs.minInstanceIndex.canVectorize()
            || !inputs.minSemanticIndex.canVectorize()
            || !inputs.numInstances.canVectorize()
            || !inputs.numSemantics.canVectorize()
            || !inputs.semanticLocalTransformPtr.canVectorize()
            || !inputs.semanticMapPtr.canVectorize()
            || !inputs.semanticPrimPathPtr.canVectorize()
            || !inputs.semanticWorldTransformPtr.canVectorize()
            || !inputs.stage.canVectorize()
            || !inputs.swhFrameNumber.canVectorize()
            || !inputs.testCaseIndex.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.semanticFilterPredicate.canVectorize()
            || !outputs.success.canVectorize()
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
        // LCOV_EXCL_STOP
    }
    void onTypeResolutionChanged(AttributeObj const& attr) {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
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
        // LCOV_EXCL_STOP
    }
    void onDynamicAttributesChanged(AttributeObj const& attribute, bool isAttributeCreated) {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        onDynamicAttributeCreatedOrRemoved(m_dynamicInputs, m_dynamicOutputs, m_dynamicStates, attribute, isAttributeCreated);
        // LCOV_EXCL_STOP
    }
    void onDataLocationChanged(AttributeObj const& attr) {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        if (! attr.isValid()) return;
        updateMappedAttributes(m_mappedAttributes, attr);
        NameToken token = attr.iAttribute->getNameToken(attr);
        if(token == inputs::exec.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exec.setHandle(hdl);
            return;
        }
        if(token == inputs::instanceMapPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.instanceMapPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::instancePrimPathPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.instancePrimPathPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::minInstanceIndex.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.minInstanceIndex.setHandle(hdl);
            return;
        }
        if(token == inputs::minSemanticIndex.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.minSemanticIndex.setHandle(hdl);
            return;
        }
        if(token == inputs::numInstances.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.numInstances.setHandle(hdl);
            return;
        }
        if(token == inputs::numSemantics.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.numSemantics.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticLabelTokenPtrs.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticLabelTokenPtrs.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticLocalTransformPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticLocalTransformPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticMapPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticMapPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticPrimPathPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticPrimPathPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticWorldTransformPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticWorldTransformPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::stage.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.stage.setHandle(hdl);
            return;
        }
        if(token == inputs::swhFrameNumber.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.swhFrameNumber.setHandle(hdl);
            return;
        }
        if(token == inputs::testCaseIndex.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.testCaseIndex.setHandle(hdl);
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
        if(token == outputs::success.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.success.setHandle(hdl);
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
        // LCOV_EXCL_STOP
    }
    omni::graph::image::unstable::ComputeParamsBuilder<std::string> getCudaParamsBuilder(InstanceIndex relativeIdx = { 0 }) {
        auto variable = const_cast<OgnSdTestInstanceMappingDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
        if (CARB_UNLIKELY(!variable.isValid() || 0 == *variable.get<uint64_t>())) {
            auto nodeObj = abi_node(relativeIdx);
            auto graphObj = nodeObj.iNode->getGraph(nodeObj);
            auto pipeline = graphObj.iGraph->getPipelineStage(graphObj);
            if (pipeline != kGraphPipelineStage_PostRender) {
                CARB_LOG_ERROR("%s: The node %s is trying to get a ComputeParamsBuilder outside of a post render graph. Nodes using this API are only supported in post render graphs.", __func__, nodeObj.iNode->getPrimPath(nodeObj));
            }
            // LCOV_EXCL_START : this error condition is a manifestation of an error in the execution framework and not expected to happen in user code
            else {
                CARB_LOG_ERROR("%s: Invalid GPU data for node %s", __func__, nodeObj.iNode->getPrimPath(nodeObj));
            }
            // LCOV_EXCL_STOP
            return omni::graph::image::unstable::ComputeParamsBuilder<std::string>{ nullptr, nullptr, *this };
        }
        auto internalData = reinterpret_cast<GpuInteropRpEntryUserData*>(*variable.get<uint64_t>());
        return omni::graph::image::unstable::ComputeParamsBuilder<std::string>{ internalData->gpu, internalData->rp, *this };
    }
    void setCudaParams(omni::graph::image::unstable::ComputeParams<std::string>&& params, InstanceIndex relativeIdx = { 0 }) {
        auto variable = const_cast<OgnSdTestInstanceMappingDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
        if (CARB_UNLIKELY(!(variable.isValid() && *variable.get<uint64_t>()))) {
            auto nodeObj = abi_node(relativeIdx);
            auto graphObj = nodeObj.iNode->getGraph(nodeObj);
            auto pipeline = graphObj.iGraph->getPipelineStage(graphObj);
            if (pipeline != kGraphPipelineStage_PostRender) {
                CARB_LOG_ERROR("%s: Invalid ComputeParams instance for node %s. Nodes using this API are only supported in post render graphs.", __func__, nodeObj.iNode->getPrimPath(nodeObj));
            }
            // LCOV_EXCL_START : this error condition is a manifestation of an error in the execution framework and not expected to happen in user code
            else {
                CARB_LOG_ERROR("%s: Invalid ComputeParams instance for node %s.", __func__, nodeObj.iNode->getPrimPath(nodeObj));
            }
            // LCOV_EXCL_STOP
            return;
        }
        auto paramsPtr = reinterpret_cast<omni::graph::image::unstable::ComputeParams<std::string>*>(*variable.get<uint64_t>());
        *paramsPtr = std::forward<omni::graph::image::unstable::ComputeParams<std::string>>(params);
    }
    omni::graph::image::unstable::ComputeParams<std::string> const& getCudaParams(InstanceIndex relativeIdx = { 0 }) const {
        static omni::graph::image::unstable::ComputeParams<std::string> defaultParams{};
        auto variable = const_cast<OgnSdTestInstanceMappingDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
        if (CARB_UNLIKELY(!(variable.isValid() && *variable.get<uint64_t>()))) {
            auto nodeObj = abi_node(relativeIdx);
            auto graphObj = nodeObj.iNode->getGraph(nodeObj);
            auto pipeline = graphObj.iGraph->getPipelineStage(graphObj);
            if (pipeline != kGraphPipelineStage_PostRender) {
                CARB_LOG_ERROR("%s: Invalid ComputeParams instance for node %s. Nodes using this API are only supported in post render graphs.", __func__, nodeObj.iNode->getPrimPath(nodeObj));
            }
            // LCOV_EXCL_START : this error condition is a manifestation of an error in the execution framework and not expected to happen in user code
            else {
                CARB_LOG_ERROR("%s: Invalid ComputeParams instance for node %s.", __func__, nodeObj.iNode->getPrimPath(nodeObj));
            }
            // LCOV_EXCL_STOP
            return defaultParams;
        }
        return *reinterpret_cast<omni::graph::image::unstable::ComputeParams<std::string>*>(*variable.get<uint64_t>());
    }
    cudaStream_t getCudaStream(InstanceIndex relativeIdx = { 0 }) const {
        auto variable = const_cast<OgnSdTestInstanceMappingDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdTestInstanceMappingDatabase::sm_stateManagerOgnSdTestInstanceMapping;
std::tuple<int, int, int> OgnSdTestInstanceMappingDatabase::sm_generatorVersionOgnSdTestInstanceMapping{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdTestInstanceMappingDatabase::sm_targetVersionOgnSdTestInstanceMapping{std::make_tuple(2,184,5)};
OgnSdTestInstanceMappingDatabase::TokenManager OgnSdTestInstanceMappingDatabase::tokens;
}
using namespace IOgnSdTestInstanceMapping;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdTestInstanceMapping, OgnSdTestInstanceMappingDatabase> s_registration("omni.syntheticdata.SdTestInstanceMapping", 1, "omni.syntheticdata"); \
}
