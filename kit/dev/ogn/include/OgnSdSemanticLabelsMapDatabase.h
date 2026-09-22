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

namespace OgnSdSemanticLabelsMapAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using renderProductPath_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderProductPath("inputs:renderProductPath", "token", kExtendedAttributeType_Regular);
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
using semanticFilterName_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> semanticFilterName("inputs:semanticFilterName", "token", kExtendedAttributeType_Regular);
}
namespace outputs
{
using cudaDeviceIndex_t = int&;
ogn::AttributeInitializer<int, ogn::kOgnOutput> cudaDeviceIndex("outputs:cudaDeviceIndex", "int", kExtendedAttributeType_Regular, -1);
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using lastUpdateTimeDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> lastUpdateTimeDenominator("outputs:lastUpdateTimeDenominator", "uint64", kExtendedAttributeType_Regular);
using lastUpdateTimeNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> lastUpdateTimeNumerator("outputs:lastUpdateTimeNumerator", "int64", kExtendedAttributeType_Regular);
using minSemanticIndex_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> minSemanticIndex("outputs:minSemanticIndex", "uint", kExtendedAttributeType_Regular);
using numSemantics_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> numSemantics("outputs:numSemantics", "uint", kExtendedAttributeType_Regular);
using semanticFilterName_t = NameToken&;
ogn::AttributeInitializer<NameToken, ogn::kOgnOutput> semanticFilterName("outputs:semanticFilterName", "token", kExtendedAttributeType_Regular);
using semanticLabelTokenSDCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticLabelTokenSDCudaPtr("outputs:semanticLabelTokenSDCudaPtr", "uint64", kExtendedAttributeType_Regular);
using semanticLabelTokenSDHostPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> semanticLabelTokenSDHostPtr("outputs:semanticLabelTokenSDHostPtr", "uint64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdSemanticLabelsMapAttributes;
namespace IOgnSdSemanticLabelsMap
{
// Synthetic Data node to expose the semantic labels map of a given semantic filter
class OgnSdSemanticLabelsMapDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken InstanceMappingInfoSDhost;
        NameToken SemanticLabelTokenSD;
        NameToken SemanticLabelTokenSDhost;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdSemanticLabelsMap.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdSemanticLabelsMap.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdSemanticLabelsMap.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdSemanticLabelsMap.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdSemanticLabelsMap;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdSemanticLabelsMap;
    static std::tuple<int, int, int>sm_targetVersionOgnSdSemanticLabelsMap;
    static constexpr size_t staticAttributeCount = 16;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , gpu{offset}
        , renderProductPath{offset}
        , renderResults{offset}
        , semanticFilterName{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderProductPath;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
        ogn::SimpleInput<const NameToken,ogn::kCpu> semanticFilterName;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : cudaDeviceIndex{offset}
        , exec{offset,AttributeRole::eExecution}
        , lastUpdateTimeDenominator{offset}
        , lastUpdateTimeNumerator{offset}
        , minSemanticIndex{offset}
        , numSemantics{offset}
        , semanticFilterName{offset}
        , semanticLabelTokenSDCudaPtr{offset}
        , semanticLabelTokenSDHostPtr{offset}
        {}
        ogn::SimpleOutput<int,ogn::kCpu> cudaDeviceIndex;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> lastUpdateTimeDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> lastUpdateTimeNumerator;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> minSemanticIndex;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> numSemantics;
        ogn::SimpleOutput<NameToken,ogn::kCpu> semanticFilterName;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticLabelTokenSDCudaPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> semanticLabelTokenSDHostPtr;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdSemanticLabelsMapDatabase(NodeObj const& nodeObjParam)
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
    OgnSdSemanticLabelsMapDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdSemanticLabelsMapDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdSemanticLabelsMapDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::exec.m_token, inputs::gpu.m_token, inputs::renderProductPath.m_token, inputs::renderResults.m_token,
                    inputs::semanticFilterName.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::cudaDeviceIndex.m_token, outputs::exec.m_token, outputs::lastUpdateTimeDenominator.m_token, outputs::lastUpdateTimeNumerator.m_token,
                    outputs::minSemanticIndex.m_token, outputs::numSemantics.m_token, outputs::semanticFilterName.m_token, outputs::semanticLabelTokenSDCudaPtr.m_token,
                    outputs::semanticLabelTokenSDHostPtr.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<1>(inputDataHandles0));
            inputs.renderProductPath.setContext(contextObj);
            inputs.renderProductPath.setHandle(std::get<2>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<3>(inputDataHandles0));
            inputs.semanticFilterName.setContext(contextObj);
            inputs.semanticFilterName.setHandle(std::get<4>(inputDataHandles0));
            outputs.cudaDeviceIndex.setContext(contextObj);
            outputs.cudaDeviceIndex.setHandle(std::get<0>(outputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<1>(outputDataHandles0));
            outputs.lastUpdateTimeDenominator.setContext(contextObj);
            outputs.lastUpdateTimeDenominator.setHandle(std::get<2>(outputDataHandles0));
            outputs.lastUpdateTimeNumerator.setContext(contextObj);
            outputs.lastUpdateTimeNumerator.setHandle(std::get<3>(outputDataHandles0));
            outputs.minSemanticIndex.setContext(contextObj);
            outputs.minSemanticIndex.setHandle(std::get<4>(outputDataHandles0));
            outputs.numSemantics.setContext(contextObj);
            outputs.numSemantics.setHandle(std::get<5>(outputDataHandles0));
            outputs.semanticFilterName.setContext(contextObj);
            outputs.semanticFilterName.setHandle(std::get<6>(outputDataHandles0));
            outputs.semanticLabelTokenSDCudaPtr.setContext(contextObj);
            outputs.semanticLabelTokenSDCudaPtr.setHandle(std::get<7>(outputDataHandles0));
            outputs.semanticLabelTokenSDHostPtr.setContext(contextObj);
            outputs.semanticLabelTokenSDHostPtr.setHandle(std::get<8>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdSemanticLabelsMap");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdSemanticLabelsMapDatabase::tokens.InstanceMappingInfoSDhost = iToken.getHandle("InstanceMappingInfoSDhost");
        OgnSdSemanticLabelsMapDatabase::tokens.SemanticLabelTokenSD = iToken.getHandle("SemanticLabelTokenSD");
        OgnSdSemanticLabelsMapDatabase::tokens.SemanticLabelTokenSDhost = iToken.getHandle("SemanticLabelTokenSDhost");

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderProductPath.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticFilterName.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::cudaDeviceIndex.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::lastUpdateTimeDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::lastUpdateTimeNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::minSemanticIndex.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::numSemantics.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticFilterName.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticLabelTokenSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::semanticLabelTokenSDHostPtr.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"InstanceMappingInfoSDhost\", \"SemanticLabelTokenSD\", \"SemanticLabelTokenSDhost\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,graph:action");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to expose the semantic labels map of a given semantic filter");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations.");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderProductPath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "RenderProduct prim path");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render results");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticFilterName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the semantic filter to apply to the semanticLabelToken");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cudaDeviceIndex.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda index of the device the cuda buffer is residing in");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes for each newFrame event received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Received");
        attr = iNode->getAttributeByToken(nodeObj, outputs::lastUpdateTimeDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time denominator of the last time the data has changed");
        attr = iNode->getAttributeByToken(nodeObj, outputs::lastUpdateTimeNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time numerator of the last time the data has changed");
        attr = iNode->getAttributeByToken(nodeObj, outputs::minSemanticIndex.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Lower semantic id. Semantics ids are in [minSemanticIndex, minSemanticIndex+numSemantic-1]");
        attr = iNode->getAttributeByToken(nodeObj, outputs::numSemantics.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number of semantics in the scene");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticFilterName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the semantic filter to apply to the semanticLabelToken");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticLabelTokenSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "uint64_t cuda buffer pointer of size numSemantics containing the semantic label token");
        attr = iNode->getAttributeByToken(nodeObj, outputs::semanticLabelTokenSDHostPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "uint64_t host buffer pointer of size numSemantics containing the semantic label token");
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
        sm_stateManagerOgnSdSemanticLabelsMap.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.gpu.isValid()
            && inputs.renderProductPath.isValid()
            && inputs.renderResults.isValid()
            && inputs.semanticFilterName.isValid()
            && outputs.cudaDeviceIndex.isValid()
            && outputs.exec.isValid()
            && outputs.lastUpdateTimeDenominator.isValid()
            && outputs.lastUpdateTimeNumerator.isValid()
            && outputs.minSemanticIndex.isValid()
            && outputs.numSemantics.isValid()
            && outputs.semanticFilterName.isValid()
            && outputs.semanticLabelTokenSDCudaPtr.isValid()
            && outputs.semanticLabelTokenSDHostPtr.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.renderProductPath.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            inputs.semanticFilterName.invalidateCachedPointer();
            outputs.cudaDeviceIndex.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.lastUpdateTimeDenominator.invalidateCachedPointer();
            outputs.lastUpdateTimeNumerator.invalidateCachedPointer();
            outputs.minSemanticIndex.invalidateCachedPointer();
            outputs.numSemantics.invalidateCachedPointer();
            outputs.semanticFilterName.invalidateCachedPointer();
            outputs.semanticLabelTokenSDCudaPtr.invalidateCachedPointer();
            outputs.semanticLabelTokenSDHostPtr.invalidateCachedPointer();
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
            if(attrib == inputs::renderProductPath.m_token) {
                inputs.renderProductPath.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderResults.m_token) {
                inputs.renderResults.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticFilterName.m_token) {
                inputs.semanticFilterName.invalidateCachedPointer();
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
            if(attrib == outputs::lastUpdateTimeDenominator.m_token) {
                outputs.lastUpdateTimeDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::lastUpdateTimeNumerator.m_token) {
                outputs.lastUpdateTimeNumerator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::minSemanticIndex.m_token) {
                outputs.minSemanticIndex.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::numSemantics.m_token) {
                outputs.numSemantics.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticFilterName.m_token) {
                outputs.semanticFilterName.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticLabelTokenSDCudaPtr.m_token) {
                outputs.semanticLabelTokenSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::semanticLabelTokenSDHostPtr.m_token) {
                outputs.semanticLabelTokenSDHostPtr.invalidateCachedPointer();
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
            || !inputs.renderProductPath.canVectorize()
            || !inputs.renderResults.canVectorize()
            || !inputs.semanticFilterName.canVectorize()
            || !outputs.cudaDeviceIndex.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.lastUpdateTimeDenominator.canVectorize()
            || !outputs.lastUpdateTimeNumerator.canVectorize()
            || !outputs.minSemanticIndex.canVectorize()
            || !outputs.numSemantics.canVectorize()
            || !outputs.semanticFilterName.canVectorize()
            || !outputs.semanticLabelTokenSDCudaPtr.canVectorize()
            || !outputs.semanticLabelTokenSDHostPtr.canVectorize()
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
        if(token == inputs::renderProductPath.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderProductPath.setHandle(hdl);
            return;
        }
        if(token == inputs::renderResults.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderResults.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticFilterName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticFilterName.setHandle(hdl);
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
        if(token == outputs::minSemanticIndex.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.minSemanticIndex.setHandle(hdl);
            return;
        }
        if(token == outputs::numSemantics.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.numSemantics.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticFilterName.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticFilterName.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticLabelTokenSDCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticLabelTokenSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::semanticLabelTokenSDHostPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.semanticLabelTokenSDHostPtr.setHandle(hdl);
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
        auto variable = const_cast<OgnSdSemanticLabelsMapDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdSemanticLabelsMapDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdSemanticLabelsMapDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdSemanticLabelsMapDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdSemanticLabelsMapDatabase::sm_stateManagerOgnSdSemanticLabelsMap;
std::tuple<int, int, int> OgnSdSemanticLabelsMapDatabase::sm_generatorVersionOgnSdSemanticLabelsMap{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdSemanticLabelsMapDatabase::sm_targetVersionOgnSdSemanticLabelsMap{std::make_tuple(2,184,5)};
OgnSdSemanticLabelsMapDatabase::TokenManager OgnSdSemanticLabelsMapDatabase::tokens;
}
using namespace IOgnSdSemanticLabelsMap;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdSemanticLabelsMap, OgnSdSemanticLabelsMapDatabase> s_registration("omni.syntheticdata.SdSemanticLabelsMap", 1, "omni.syntheticdata"); \
}
