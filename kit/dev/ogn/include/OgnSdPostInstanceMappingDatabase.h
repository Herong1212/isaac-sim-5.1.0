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
#include <omni/graph/image/unstable/ComputeParamsBuilder.h>

namespace OgnSdPostInstanceMappingAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using semanticFilterName_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> semanticFilterName("inputs:semanticFilterName", "token", kExtendedAttributeType_Regular);
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using instanceMapSDCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> instanceMapSDCudaPtr("outputs:instanceMapSDCudaPtr", "uint64", kExtendedAttributeType_Regular);
using instanceMappingInfoSDPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> instanceMappingInfoSDPtr("outputs:instanceMappingInfoSDPtr", "uint64", kExtendedAttributeType_Regular);
using instancePrimTokenSDCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> instancePrimTokenSDCudaPtr("outputs:instancePrimTokenSDCudaPtr", "uint64", kExtendedAttributeType_Regular);
using lastUpdateTimeDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> lastUpdateTimeDenominator("outputs:lastUpdateTimeDenominator", "uint64", kExtendedAttributeType_Regular);
using lastUpdateTimeNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> lastUpdateTimeNumerator("outputs:lastUpdateTimeNumerator", "int64", kExtendedAttributeType_Regular);
using semanticLabelTokenSDCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticLabelTokenSDCudaPtr("outputs:semanticLabelTokenSDCudaPtr", "uint64", kExtendedAttributeType_Regular);
using semanticLocalTransformSDCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticLocalTransformSDCudaPtr("outputs:semanticLocalTransformSDCudaPtr", "uint64", kExtendedAttributeType_Regular);
using semanticMapSDCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticMapSDCudaPtr("outputs:semanticMapSDCudaPtr", "uint64", kExtendedAttributeType_Regular);
using semanticPrimTokenSDCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticPrimTokenSDCudaPtr("outputs:semanticPrimTokenSDCudaPtr", "uint64", kExtendedAttributeType_Regular);
using semanticWorldTransformSDCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticWorldTransformSDCudaPtr("outputs:semanticWorldTransformSDCudaPtr", "uint64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdPostInstanceMappingAttributes;
namespace IOgnSdPostInstanceMapping
{
// Synthetic Data node to compute and store scene instances semantic hierarchy information
class OgnSdPostInstanceMappingDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken InstanceMappingInfoSDhost;
        NameToken SemanticMapSD;
        NameToken SemanticMapSDhost;
        NameToken SemanticPrimTokenSD;
        NameToken SemanticPrimTokenSDhost;
        NameToken InstanceMapSD;
        NameToken InstanceMapSDhost;
        NameToken InstancePrimTokenSD;
        NameToken InstancePrimTokenSDhost;
        NameToken SemanticLabelTokenSD;
        NameToken SemanticLabelTokenSDhost;
        NameToken SemanticLocalTransformSD;
        NameToken SemanticLocalTransformSDhost;
        NameToken SemanticWorldTransformSD;
        NameToken SemanticWorldTransformSDhost;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdPostInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdPostInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdPostInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdPostInstanceMapping.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdPostInstanceMapping;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdPostInstanceMapping;
    static std::tuple<int, int, int>sm_targetVersionOgnSdPostInstanceMapping;
    static constexpr size_t staticAttributeCount = 17;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , gpu{offset}
        , rp{offset}
        , semanticFilterName{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const NameToken,ogn::kCpu> semanticFilterName;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , instanceMapSDCudaPtr{offset}
        , instanceMappingInfoSDPtr{offset}
        , instancePrimTokenSDCudaPtr{offset}
        , lastUpdateTimeDenominator{offset}
        , lastUpdateTimeNumerator{offset}
        , semanticLabelTokenSDCudaPtr{offset}
        , semanticLocalTransformSDCudaPtr{offset}
        , semanticMapSDCudaPtr{offset}
        , semanticPrimTokenSDCudaPtr{offset}
        , semanticWorldTransformSDCudaPtr{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> instanceMapSDCudaPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> instanceMappingInfoSDPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> instancePrimTokenSDCudaPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> lastUpdateTimeDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> lastUpdateTimeNumerator;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticLabelTokenSDCudaPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticLocalTransformSDCudaPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticMapSDCudaPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticPrimTokenSDCudaPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticWorldTransformSDCudaPtr;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdPostInstanceMappingDatabase(NodeObj const& nodeObjParam)
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
    OgnSdPostInstanceMappingDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdPostInstanceMappingDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdPostInstanceMappingDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::exec.m_token, inputs::gpu.m_token, inputs::rp.m_token, inputs::semanticFilterName.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::instanceMapSDCudaPtr.m_token, outputs::instanceMappingInfoSDPtr.m_token, outputs::instancePrimTokenSDCudaPtr.m_token,
                    outputs::lastUpdateTimeDenominator.m_token, outputs::lastUpdateTimeNumerator.m_token, outputs::semanticLabelTokenSDCudaPtr.m_token, outputs::semanticLocalTransformSDCudaPtr.m_token,
                    outputs::semanticMapSDCudaPtr.m_token, outputs::semanticPrimTokenSDCudaPtr.m_token, outputs::semanticWorldTransformSDCudaPtr.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<1>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<2>(inputDataHandles0));
            inputs.semanticFilterName.setContext(contextObj);
            inputs.semanticFilterName.setHandle(std::get<3>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.instanceMapSDCudaPtr.setContext(contextObj);
            outputs.instanceMapSDCudaPtr.setHandle(std::get<1>(outputDataHandles0));
            outputs.instanceMappingInfoSDPtr.setContext(contextObj);
            outputs.instanceMappingInfoSDPtr.setHandle(std::get<2>(outputDataHandles0));
            outputs.instancePrimTokenSDCudaPtr.setContext(contextObj);
            outputs.instancePrimTokenSDCudaPtr.setHandle(std::get<3>(outputDataHandles0));
            outputs.lastUpdateTimeDenominator.setContext(contextObj);
            outputs.lastUpdateTimeDenominator.setHandle(std::get<4>(outputDataHandles0));
            outputs.lastUpdateTimeNumerator.setContext(contextObj);
            outputs.lastUpdateTimeNumerator.setHandle(std::get<5>(outputDataHandles0));
            outputs.semanticLabelTokenSDCudaPtr.setContext(contextObj);
            outputs.semanticLabelTokenSDCudaPtr.setHandle(std::get<6>(outputDataHandles0));
            outputs.semanticLocalTransformSDCudaPtr.setContext(contextObj);
            outputs.semanticLocalTransformSDCudaPtr.setHandle(std::get<7>(outputDataHandles0));
            outputs.semanticMapSDCudaPtr.setContext(contextObj);
            outputs.semanticMapSDCudaPtr.setHandle(std::get<8>(outputDataHandles0));
            outputs.semanticPrimTokenSDCudaPtr.setContext(contextObj);
            outputs.semanticPrimTokenSDCudaPtr.setHandle(std::get<9>(outputDataHandles0));
            outputs.semanticWorldTransformSDCudaPtr.setContext(contextObj);
            outputs.semanticWorldTransformSDCudaPtr.setHandle(std::get<10>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdPostInstanceMapping");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdPostInstanceMappingDatabase::tokens.InstanceMappingInfoSDhost = iToken.getHandle("InstanceMappingInfoSDhost");
        OgnSdPostInstanceMappingDatabase::tokens.SemanticMapSD = iToken.getHandle("SemanticMapSD");
        OgnSdPostInstanceMappingDatabase::tokens.SemanticMapSDhost = iToken.getHandle("SemanticMapSDhost");
        OgnSdPostInstanceMappingDatabase::tokens.SemanticPrimTokenSD = iToken.getHandle("SemanticPrimTokenSD");
        OgnSdPostInstanceMappingDatabase::tokens.SemanticPrimTokenSDhost = iToken.getHandle("SemanticPrimTokenSDhost");
        OgnSdPostInstanceMappingDatabase::tokens.InstanceMapSD = iToken.getHandle("InstanceMapSD");
        OgnSdPostInstanceMappingDatabase::tokens.InstanceMapSDhost = iToken.getHandle("InstanceMapSDhost");
        OgnSdPostInstanceMappingDatabase::tokens.InstancePrimTokenSD = iToken.getHandle("InstancePrimTokenSD");
        OgnSdPostInstanceMappingDatabase::tokens.InstancePrimTokenSDhost = iToken.getHandle("InstancePrimTokenSDhost");
        OgnSdPostInstanceMappingDatabase::tokens.SemanticLabelTokenSD = iToken.getHandle("SemanticLabelTokenSD");
        OgnSdPostInstanceMappingDatabase::tokens.SemanticLabelTokenSDhost = iToken.getHandle("SemanticLabelTokenSDhost");
        OgnSdPostInstanceMappingDatabase::tokens.SemanticLocalTransformSD = iToken.getHandle("SemanticLocalTransformSD");
        OgnSdPostInstanceMappingDatabase::tokens.SemanticLocalTransformSDhost = iToken.getHandle("SemanticLocalTransformSDhost");
        OgnSdPostInstanceMappingDatabase::tokens.SemanticWorldTransformSD = iToken.getHandle("SemanticWorldTransformSD");
        OgnSdPostInstanceMappingDatabase::tokens.SemanticWorldTransformSDhost = iToken.getHandle("SemanticWorldTransformSDhost");

        static omni::fabric::Token inputs_semanticFilterName_token {"default"};
        inputs::semanticFilterName.setDefault(inputs_semanticFilterName_token.asTokenC());
        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticFilterName.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::instanceMapSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::instanceMappingInfoSDPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::instancePrimTokenSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::lastUpdateTimeDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::lastUpdateTimeNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticLabelTokenSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticLocalTransformSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticMapSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticPrimTokenSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticWorldTransformSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"InstanceMappingInfoSDhost\", \"SemanticMapSD\", \"SemanticMapSDhost\", \"SemanticPrimTokenSD\", \"SemanticPrimTokenSDhost\", \"InstanceMapSD\", \"InstanceMapSDhost\", \"InstancePrimTokenSD\", \"InstancePrimTokenSDhost\", \"SemanticLabelTokenSD\", \"SemanticLabelTokenSDhost\", \"SemanticLocalTransformSD\", \"SemanticLocalTransformSDhost\", \"SemanticWorldTransformSD\", \"SemanticWorldTransformSDhost\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,rendering");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to compute and store scene instances semantic hierarchy information");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticFilterName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the semantic filter to apply to the semanticLabelToken");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"default\"");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::instanceMapSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint16_t buffer pointer of size numInstances containing the instance parent semantic index");
        attr = iNode->getAttributeByToken(nodeObj, outputs::instanceMappingInfoSDPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "uint buffer pointer containing the following information :\n[ numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic,\n  lastUpdateTimeNumeratorHigh, lastUpdateTimeNumeratorLow, , lastUpdateTimeDenominatorHigh, lastUpdateTimeDenominatorLow ]");
        attr = iNode->getAttributeByToken(nodeObj, outputs::instancePrimTokenSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint64_t buffer pointer of size numInstances containing the instance path token");
        attr = iNode->getAttributeByToken(nodeObj, outputs::lastUpdateTimeDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time denominator of the last time the data has changed");
        attr = iNode->getAttributeByToken(nodeObj, outputs::lastUpdateTimeNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time numerator of the last time the data has changed");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticLabelTokenSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint64_t buffer pointer of size numSemantics containing the semantic label token");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticLocalTransformSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda float44 buffer pointer of size numSemantics containing the local semantic transform");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticMapSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint16_t buffer pointer of size numSemantics containing the semantic parent semantic index");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticPrimTokenSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint32_t buffer pointer of size numSemantics containing the prim part of the semantic path token");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticWorldTransformSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda float44 buffer pointer of size numSemantics containing the world semantic transform");
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
        sm_stateManagerOgnSdPostInstanceMapping.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.gpu.isValid()
            && inputs.rp.isValid()
            && inputs.semanticFilterName.isValid()
            && outputs.exec.isValid()
            && outputs.instanceMapSDCudaPtr.isValid()
            && outputs.instanceMappingInfoSDPtr.isValid()
            && outputs.instancePrimTokenSDCudaPtr.isValid()
            && outputs.lastUpdateTimeDenominator.isValid()
            && outputs.lastUpdateTimeNumerator.isValid()
            && outputs.semanticLabelTokenSDCudaPtr.isValid()
            && outputs.semanticLocalTransformSDCudaPtr.isValid()
            && outputs.semanticMapSDCudaPtr.isValid()
            && outputs.semanticPrimTokenSDCudaPtr.isValid()
            && outputs.semanticWorldTransformSDCudaPtr.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.semanticFilterName.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.instanceMapSDCudaPtr.invalidateCachedPointer();
            outputs.instanceMappingInfoSDPtr.invalidateCachedPointer();
            outputs.instancePrimTokenSDCudaPtr.invalidateCachedPointer();
            outputs.lastUpdateTimeDenominator.invalidateCachedPointer();
            outputs.lastUpdateTimeNumerator.invalidateCachedPointer();
            outputs.semanticLabelTokenSDCudaPtr.invalidateCachedPointer();
            outputs.semanticLocalTransformSDCudaPtr.invalidateCachedPointer();
            outputs.semanticMapSDCudaPtr.invalidateCachedPointer();
            outputs.semanticPrimTokenSDCudaPtr.invalidateCachedPointer();
            outputs.semanticWorldTransformSDCudaPtr.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticFilterName.m_token) {
                inputs.semanticFilterName.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::instanceMapSDCudaPtr.m_token) {
                outputs.instanceMapSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::instanceMappingInfoSDPtr.m_token) {
                outputs.instanceMappingInfoSDPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::instancePrimTokenSDCudaPtr.m_token) {
                outputs.instancePrimTokenSDCudaPtr.invalidateCachedPointer();
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
            if(attrib == outputs::semanticLabelTokenSDCudaPtr.m_token) {
                outputs.semanticLabelTokenSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticLocalTransformSDCudaPtr.m_token) {
                outputs.semanticLocalTransformSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticMapSDCudaPtr.m_token) {
                outputs.semanticMapSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticPrimTokenSDCudaPtr.m_token) {
                outputs.semanticPrimTokenSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticWorldTransformSDCudaPtr.m_token) {
                outputs.semanticWorldTransformSDCudaPtr.invalidateCachedPointer();
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
            || !inputs.gpu.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.semanticFilterName.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.instanceMapSDCudaPtr.canVectorize()
            || !outputs.instanceMappingInfoSDPtr.canVectorize()
            || !outputs.instancePrimTokenSDCudaPtr.canVectorize()
            || !outputs.lastUpdateTimeDenominator.canVectorize()
            || !outputs.lastUpdateTimeNumerator.canVectorize()
            || !outputs.semanticLabelTokenSDCudaPtr.canVectorize()
            || !outputs.semanticLocalTransformSDCudaPtr.canVectorize()
            || !outputs.semanticMapSDCudaPtr.canVectorize()
            || !outputs.semanticPrimTokenSDCudaPtr.canVectorize()
            || !outputs.semanticWorldTransformSDCudaPtr.canVectorize()
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
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticFilterName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticFilterName.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::instanceMapSDCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.instanceMapSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::instanceMappingInfoSDPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.instanceMappingInfoSDPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::instancePrimTokenSDCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.instancePrimTokenSDCudaPtr.setHandle(hdl);
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
        if(token == outputs::semanticLabelTokenSDCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticLabelTokenSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticLocalTransformSDCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticLocalTransformSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticMapSDCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticMapSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticPrimTokenSDCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticPrimTokenSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticWorldTransformSDCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticWorldTransformSDCudaPtr.setHandle(hdl);
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
    omni::graph::image::unstable::ComputeParamsBuilder<std::string> getCudaParamsBuilder(InstanceIndex relativeIdx = { 0 }) {
        auto variable = const_cast<OgnSdPostInstanceMappingDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostInstanceMappingDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostInstanceMappingDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostInstanceMappingDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdPostInstanceMappingDatabase::sm_stateManagerOgnSdPostInstanceMapping;
std::tuple<int, int, int> OgnSdPostInstanceMappingDatabase::sm_generatorVersionOgnSdPostInstanceMapping{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdPostInstanceMappingDatabase::sm_targetVersionOgnSdPostInstanceMapping{std::make_tuple(2,184,5)};
OgnSdPostInstanceMappingDatabase::TokenManager OgnSdPostInstanceMappingDatabase::tokens;
}
using namespace IOgnSdPostInstanceMapping;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdPostInstanceMapping, OgnSdPostInstanceMappingDatabase> s_registration("omni.syntheticdata.SdPostInstanceMapping", 2, "omni.syntheticdata"); \
}
