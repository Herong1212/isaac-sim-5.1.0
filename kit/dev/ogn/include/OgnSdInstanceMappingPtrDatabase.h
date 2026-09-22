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

namespace OgnSdInstanceMappingPtrAttributes
{
namespace inputs
{
using cudaPtr_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> cudaPtr("inputs:cudaPtr", "bool", kExtendedAttributeType_Regular, false);
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
using semanticFilerTokens_t = const ogn::const_array<NameToken>&;
ogn::AttributeInitializer<const NameToken*, ogn::kOgnInput> semanticFilerTokens("inputs:semanticFilerTokens", "token[]", kExtendedAttributeType_Regular, nullptr, 0);
}
namespace outputs
{
using cudaDeviceIndex_t = int&;
ogn::AttributeInitializer<int, ogn::kOgnOutput> cudaDeviceIndex("outputs:cudaDeviceIndex", "int", kExtendedAttributeType_Regular, -1);
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using instanceMapPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> instanceMapPtr("outputs:instanceMapPtr", "uint64", kExtendedAttributeType_Regular);
using instancePrimPathPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> instancePrimPathPtr("outputs:instancePrimPathPtr", "uint64", kExtendedAttributeType_Regular);
using lastUpdateTimeDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> lastUpdateTimeDenominator("outputs:lastUpdateTimeDenominator", "uint64", kExtendedAttributeType_Regular);
using lastUpdateTimeNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> lastUpdateTimeNumerator("outputs:lastUpdateTimeNumerator", "int64", kExtendedAttributeType_Regular);
using minInstanceIndex_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> minInstanceIndex("outputs:minInstanceIndex", "uint", kExtendedAttributeType_Regular);
using minSemanticIndex_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> minSemanticIndex("outputs:minSemanticIndex", "uint", kExtendedAttributeType_Regular);
using numInstances_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> numInstances("outputs:numInstances", "uint", kExtendedAttributeType_Regular);
using numSemantics_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> numSemantics("outputs:numSemantics", "uint", kExtendedAttributeType_Regular);
using semanticLabelTokenPtrs_t = ogn::array<uint64_t>&;
ogn::AttributeInitializer<uint64_t*, ogn::kOgnOutput> semanticLabelTokenPtrs("outputs:semanticLabelTokenPtrs", "uint64[]", kExtendedAttributeType_Regular, nullptr, 0);
using semanticLocalTransformPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticLocalTransformPtr("outputs:semanticLocalTransformPtr", "uint64", kExtendedAttributeType_Regular);
using semanticMapPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticMapPtr("outputs:semanticMapPtr", "uint64", kExtendedAttributeType_Regular);
using semanticPrimPathPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticPrimPathPtr("outputs:semanticPrimPathPtr", "uint64", kExtendedAttributeType_Regular);
using semanticWorldTransformPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticWorldTransformPtr("outputs:semanticWorldTransformPtr", "uint64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdInstanceMappingPtrAttributes;
namespace IOgnSdInstanceMappingPtr
{
// Synthetic Data node to expose the scene instances semantic hierarchy information
class OgnSdInstanceMappingPtrDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken InstanceMappingInfoSDhost;
        NameToken InstancePrimTokenSDhost;
        NameToken InstancePrimTokenSD;
        NameToken SemanticPrimTokenSDhost;
        NameToken SemanticPrimTokenSD;
        NameToken InstanceMapSDhost;
        NameToken InstanceMapSD;
        NameToken SemanticMapSDhost;
        NameToken SemanticMapSD;
        NameToken SemanticWorldTransformSDhost;
        NameToken SemanticWorldTransformSD;
        NameToken SemanticLocalTransformSDhost;
        NameToken SemanticLocalTransformSD;
        NameToken SemanticLabelTokenSDhost;
        NameToken SemanticLabelTokenSD;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdInstanceMappingPtr.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdInstanceMappingPtr.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdInstanceMappingPtr.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdInstanceMappingPtr.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdInstanceMappingPtr;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdInstanceMappingPtr;
    static std::tuple<int, int, int>sm_targetVersionOgnSdInstanceMappingPtr;
    static constexpr size_t staticAttributeCount = 21;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : cudaPtr{offset}
        , exec{offset,AttributeRole::eExecution}
        , renderResults{offset}
        , semanticFilerTokens{offset}
        {}
        ogn::SimpleInput<const bool,ogn::kCpu> cudaPtr;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
        ogn::ArrayInput<const NameToken,ogn::kCpu> semanticFilerTokens;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : cudaDeviceIndex{offset}
        , exec{offset,AttributeRole::eExecution}
        , instanceMapPtr{offset}
        , instancePrimPathPtr{offset}
        , lastUpdateTimeDenominator{offset}
        , lastUpdateTimeNumerator{offset}
        , minInstanceIndex{offset}
        , minSemanticIndex{offset}
        , numInstances{offset}
        , numSemantics{offset}
        , semanticLabelTokenPtrs{offset}
        , semanticLocalTransformPtr{offset}
        , semanticMapPtr{offset}
        , semanticPrimPathPtr{offset}
        , semanticWorldTransformPtr{offset}
        {}
        ogn::SimpleOutput<int,ogn::kCpu> cudaDeviceIndex;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> instanceMapPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> instancePrimPathPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> lastUpdateTimeDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> lastUpdateTimeNumerator;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> minInstanceIndex;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> minSemanticIndex;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> numInstances;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> numSemantics;
        ogn::ArrayOutput<uint64_t,ogn::kCpu> semanticLabelTokenPtrs;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticLocalTransformPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticMapPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticPrimPathPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticWorldTransformPtr;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdInstanceMappingPtrDatabase(NodeObj const& nodeObjParam)
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
    OgnSdInstanceMappingPtrDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdInstanceMappingPtrDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdInstanceMappingPtrDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::cudaPtr.m_token, inputs::exec.m_token, inputs::renderResults.m_token, inputs::semanticFilerTokens.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::cudaDeviceIndex.m_token, outputs::exec.m_token, outputs::instanceMapPtr.m_token, outputs::instancePrimPathPtr.m_token,
                    outputs::lastUpdateTimeDenominator.m_token, outputs::lastUpdateTimeNumerator.m_token, outputs::minInstanceIndex.m_token, outputs::minSemanticIndex.m_token,
                    outputs::numInstances.m_token, outputs::numSemantics.m_token, outputs::semanticLabelTokenPtrs.m_token, outputs::semanticLocalTransformPtr.m_token,
                    outputs::semanticMapPtr.m_token, outputs::semanticPrimPathPtr.m_token, outputs::semanticWorldTransformPtr.m_token
                )
            , kAccordingToContextIndex);
            inputs.cudaPtr.setContext(contextObj);
            inputs.cudaPtr.setHandle(std::get<0>(inputDataHandles0));
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<1>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<2>(inputDataHandles0));
            inputs.semanticFilerTokens.setContext(contextObj);
            inputs.semanticFilerTokens.setHandle(std::get<3>(inputDataHandles0));
            outputs.cudaDeviceIndex.setContext(contextObj);
            outputs.cudaDeviceIndex.setHandle(std::get<0>(outputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<1>(outputDataHandles0));
            outputs.instanceMapPtr.setContext(contextObj);
            outputs.instanceMapPtr.setHandle(std::get<2>(outputDataHandles0));
            outputs.instancePrimPathPtr.setContext(contextObj);
            outputs.instancePrimPathPtr.setHandle(std::get<3>(outputDataHandles0));
            outputs.lastUpdateTimeDenominator.setContext(contextObj);
            outputs.lastUpdateTimeDenominator.setHandle(std::get<4>(outputDataHandles0));
            outputs.lastUpdateTimeNumerator.setContext(contextObj);
            outputs.lastUpdateTimeNumerator.setHandle(std::get<5>(outputDataHandles0));
            outputs.minInstanceIndex.setContext(contextObj);
            outputs.minInstanceIndex.setHandle(std::get<6>(outputDataHandles0));
            outputs.minSemanticIndex.setContext(contextObj);
            outputs.minSemanticIndex.setHandle(std::get<7>(outputDataHandles0));
            outputs.numInstances.setContext(contextObj);
            outputs.numInstances.setHandle(std::get<8>(outputDataHandles0));
            outputs.numSemantics.setContext(contextObj);
            outputs.numSemantics.setHandle(std::get<9>(outputDataHandles0));
            outputs.semanticLabelTokenPtrs.setContext(contextObj);
            outputs.semanticLabelTokenPtrs.setHandle(std::get<10>(outputDataHandles0));
            outputs.semanticLocalTransformPtr.setContext(contextObj);
            outputs.semanticLocalTransformPtr.setHandle(std::get<11>(outputDataHandles0));
            outputs.semanticMapPtr.setContext(contextObj);
            outputs.semanticMapPtr.setHandle(std::get<12>(outputDataHandles0));
            outputs.semanticPrimPathPtr.setContext(contextObj);
            outputs.semanticPrimPathPtr.setHandle(std::get<13>(outputDataHandles0));
            outputs.semanticWorldTransformPtr.setContext(contextObj);
            outputs.semanticWorldTransformPtr.setHandle(std::get<14>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdInstanceMappingPtr");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdInstanceMappingPtrDatabase::tokens.InstanceMappingInfoSDhost = iToken.getHandle("InstanceMappingInfoSDhost");
        OgnSdInstanceMappingPtrDatabase::tokens.InstancePrimTokenSDhost = iToken.getHandle("InstancePrimTokenSDhost");
        OgnSdInstanceMappingPtrDatabase::tokens.InstancePrimTokenSD = iToken.getHandle("InstancePrimTokenSD");
        OgnSdInstanceMappingPtrDatabase::tokens.SemanticPrimTokenSDhost = iToken.getHandle("SemanticPrimTokenSDhost");
        OgnSdInstanceMappingPtrDatabase::tokens.SemanticPrimTokenSD = iToken.getHandle("SemanticPrimTokenSD");
        OgnSdInstanceMappingPtrDatabase::tokens.InstanceMapSDhost = iToken.getHandle("InstanceMapSDhost");
        OgnSdInstanceMappingPtrDatabase::tokens.InstanceMapSD = iToken.getHandle("InstanceMapSD");
        OgnSdInstanceMappingPtrDatabase::tokens.SemanticMapSDhost = iToken.getHandle("SemanticMapSDhost");
        OgnSdInstanceMappingPtrDatabase::tokens.SemanticMapSD = iToken.getHandle("SemanticMapSD");
        OgnSdInstanceMappingPtrDatabase::tokens.SemanticWorldTransformSDhost = iToken.getHandle("SemanticWorldTransformSDhost");
        OgnSdInstanceMappingPtrDatabase::tokens.SemanticWorldTransformSD = iToken.getHandle("SemanticWorldTransformSD");
        OgnSdInstanceMappingPtrDatabase::tokens.SemanticLocalTransformSDhost = iToken.getHandle("SemanticLocalTransformSDhost");
        OgnSdInstanceMappingPtrDatabase::tokens.SemanticLocalTransformSD = iToken.getHandle("SemanticLocalTransformSD");
        OgnSdInstanceMappingPtrDatabase::tokens.SemanticLabelTokenSDhost = iToken.getHandle("SemanticLabelTokenSDhost");
        OgnSdInstanceMappingPtrDatabase::tokens.SemanticLabelTokenSD = iToken.getHandle("SemanticLabelTokenSD");

        inputs::cudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticFilerTokens.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::cudaDeviceIndex.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::instanceMapPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::instancePrimPathPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::lastUpdateTimeDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::lastUpdateTimeNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::minInstanceIndex.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::minSemanticIndex.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::numInstances.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::numSemantics.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticLabelTokenPtrs.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticLocalTransformPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticMapPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticPrimPathPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticWorldTransformPtr.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"InstanceMappingInfoSDhost\", \"InstancePrimTokenSDhost\", \"InstancePrimTokenSD\", \"SemanticPrimTokenSDhost\", \"SemanticPrimTokenSD\", \"InstanceMapSDhost\", \"InstanceMapSD\", \"SemanticMapSDhost\", \"SemanticMapSD\", \"SemanticWorldTransformSDhost\", \"SemanticWorldTransformSD\", \"SemanticLocalTransformSDhost\", \"SemanticLocalTransformSD\", \"SemanticLabelTokenSDhost\", \"SemanticLabelTokenSD\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:action");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to expose the scene instances semantic hierarchy information");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If true, return cuda device pointer instead of host pointer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render results pointer");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticFilerTokens.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Tokens identifying the semantic filters applied to the output semantic labels. Each token should correspond to an activated SdSemanticFilter node");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[]");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cudaDeviceIndex.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If the data is on the device it is the cuda index of this device otherwise it is set to -1");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes when the event is received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Received");
        attr = iNode->getAttributeByToken(nodeObj, outputs::instanceMapPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numInstances uint16_t containing the semantic index of the instance prim first semantic prim parent");
        attr = iNode->getAttributeByToken(nodeObj, outputs::instancePrimPathPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numInstances uint64_t containing the prim path tokens for every instance prims");
        attr = iNode->getAttributeByToken(nodeObj, outputs::lastUpdateTimeDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time denominator of the last time the data has changed");
        attr = iNode->getAttributeByToken(nodeObj, outputs::lastUpdateTimeNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time numerator of the last time the data has changed");
        attr = iNode->getAttributeByToken(nodeObj, outputs::minInstanceIndex.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Instance index of the first instance prim in the instance arrays");
        attr = iNode->getAttributeByToken(nodeObj, outputs::minSemanticIndex.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Semantic index of the first semantic prim in the semantic arrays");
        attr = iNode->getAttributeByToken(nodeObj, outputs::numInstances.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number of instances prim in the instance arrays");
        attr = iNode->getAttributeByToken(nodeObj, outputs::numSemantics.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number of semantic prim in the semantic arrays");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticLabelTokenPtrs.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array containing for every input semantic filters the corresponding array pointer of numSemantics uint64_t representing the semantic label of the semantic prim");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticLocalTransformPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numSemantics 4x4 float matrices containing the transform from world to object space for every semantic prims");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticMapPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numSemantics uint16_t containing the semantic index of the semantic prim first semantic prim parent");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticPrimPathPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numSemantics uint32_t containing the prim part of the prim path tokens for every semantic prims");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticWorldTransformPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array pointer of numSemantics 4x4 float matrices containing the transform from local to world space for every semantic entity");
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
        sm_stateManagerOgnSdInstanceMappingPtr.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cudaPtr.isValid()
            && inputs.exec.isValid()
            && inputs.renderResults.isValid()
            && inputs.semanticFilerTokens.isValid()
            && outputs.cudaDeviceIndex.isValid()
            && outputs.exec.isValid()
            && outputs.instanceMapPtr.isValid()
            && outputs.instancePrimPathPtr.isValid()
            && outputs.lastUpdateTimeDenominator.isValid()
            && outputs.lastUpdateTimeNumerator.isValid()
            && outputs.minInstanceIndex.isValid()
            && outputs.minSemanticIndex.isValid()
            && outputs.numInstances.isValid()
            && outputs.numSemantics.isValid()
            && outputs.semanticLabelTokenPtrs.isValid()
            && outputs.semanticLocalTransformPtr.isValid()
            && outputs.semanticMapPtr.isValid()
            && outputs.semanticPrimPathPtr.isValid()
            && outputs.semanticWorldTransformPtr.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cudaPtr.invalidateCachedPointer();
            inputs.exec.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            inputs.semanticFilerTokens.invalidateCachedPointer();
            outputs.cudaDeviceIndex.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.instanceMapPtr.invalidateCachedPointer();
            outputs.instancePrimPathPtr.invalidateCachedPointer();
            outputs.lastUpdateTimeDenominator.invalidateCachedPointer();
            outputs.lastUpdateTimeNumerator.invalidateCachedPointer();
            outputs.minInstanceIndex.invalidateCachedPointer();
            outputs.minSemanticIndex.invalidateCachedPointer();
            outputs.numInstances.invalidateCachedPointer();
            outputs.numSemantics.invalidateCachedPointer();
            outputs.semanticLabelTokenPtrs.invalidateCachedPointer();
            outputs.semanticLocalTransformPtr.invalidateCachedPointer();
            outputs.semanticMapPtr.invalidateCachedPointer();
            outputs.semanticPrimPathPtr.invalidateCachedPointer();
            outputs.semanticWorldTransformPtr.invalidateCachedPointer();
            return;
        }
        inputs.semanticFilerTokens.invalidateCachedPointer();
        outputs.semanticLabelTokenPtrs.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cudaPtr.m_token) {
                inputs.cudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderResults.m_token) {
                inputs.renderResults.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticFilerTokens.m_token) {
                inputs.semanticFilerTokens.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cudaDeviceIndex.m_token) {
                outputs.cudaDeviceIndex.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::instanceMapPtr.m_token) {
                outputs.instanceMapPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::instancePrimPathPtr.m_token) {
                outputs.instancePrimPathPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::lastUpdateTimeDenominator.m_token) {
                outputs.lastUpdateTimeDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::lastUpdateTimeNumerator.m_token) {
                outputs.lastUpdateTimeNumerator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::minInstanceIndex.m_token) {
                outputs.minInstanceIndex.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::minSemanticIndex.m_token) {
                outputs.minSemanticIndex.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::numInstances.m_token) {
                outputs.numInstances.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::numSemantics.m_token) {
                outputs.numSemantics.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticLabelTokenPtrs.m_token) {
                outputs.semanticLabelTokenPtrs.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticLocalTransformPtr.m_token) {
                outputs.semanticLocalTransformPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticMapPtr.m_token) {
                outputs.semanticMapPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticPrimPathPtr.m_token) {
                outputs.semanticPrimPathPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticWorldTransformPtr.m_token) {
                outputs.semanticWorldTransformPtr.invalidateCachedPointer();
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
        if( !inputs.cudaPtr.canVectorize()
            || !inputs.exec.canVectorize()
            || !inputs.renderResults.canVectorize()
            || !outputs.cudaDeviceIndex.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.instanceMapPtr.canVectorize()
            || !outputs.instancePrimPathPtr.canVectorize()
            || !outputs.lastUpdateTimeDenominator.canVectorize()
            || !outputs.lastUpdateTimeNumerator.canVectorize()
            || !outputs.minInstanceIndex.canVectorize()
            || !outputs.minSemanticIndex.canVectorize()
            || !outputs.numInstances.canVectorize()
            || !outputs.numSemantics.canVectorize()
            || !outputs.semanticLocalTransformPtr.canVectorize()
            || !outputs.semanticMapPtr.canVectorize()
            || !outputs.semanticPrimPathPtr.canVectorize()
            || !outputs.semanticWorldTransformPtr.canVectorize()
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
        if(token == inputs::cudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::exec.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exec.setHandle(hdl);
            return;
        }
        if(token == inputs::renderResults.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderResults.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticFilerTokens.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticFilerTokens.setHandle(hdl);
            return;
        }
        if(token == outputs::cudaDeviceIndex.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cudaDeviceIndex.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::instanceMapPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.instanceMapPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::instancePrimPathPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.instancePrimPathPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::lastUpdateTimeDenominator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.lastUpdateTimeDenominator.setHandle(hdl);
            return;
        }
        if(token == outputs::lastUpdateTimeNumerator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.lastUpdateTimeNumerator.setHandle(hdl);
            return;
        }
        if(token == outputs::minInstanceIndex.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.minInstanceIndex.setHandle(hdl);
            return;
        }
        if(token == outputs::minSemanticIndex.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.minSemanticIndex.setHandle(hdl);
            return;
        }
        if(token == outputs::numInstances.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.numInstances.setHandle(hdl);
            return;
        }
        if(token == outputs::numSemantics.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.numSemantics.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticLabelTokenPtrs.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticLabelTokenPtrs.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticLocalTransformPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticLocalTransformPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticMapPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticMapPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticPrimPathPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticPrimPathPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticWorldTransformPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticWorldTransformPtr.setHandle(hdl);
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
ogn::StateManager OgnSdInstanceMappingPtrDatabase::sm_stateManagerOgnSdInstanceMappingPtr;
std::tuple<int, int, int> OgnSdInstanceMappingPtrDatabase::sm_generatorVersionOgnSdInstanceMappingPtr{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdInstanceMappingPtrDatabase::sm_targetVersionOgnSdInstanceMappingPtr{std::make_tuple(2,184,5)};
OgnSdInstanceMappingPtrDatabase::TokenManager OgnSdInstanceMappingPtrDatabase::tokens;
}
using namespace IOgnSdInstanceMappingPtr;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdInstanceMappingPtr, OgnSdInstanceMappingPtrDatabase> s_registration("omni.syntheticdata.SdInstanceMappingPtr", 2, "omni.syntheticdata"); \
}
