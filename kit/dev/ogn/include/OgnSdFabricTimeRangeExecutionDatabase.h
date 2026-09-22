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

namespace OgnSdFabricTimeRangeExecutionAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
using timeRangeBeginDenominatorToken_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> timeRangeBeginDenominatorToken("inputs:timeRangeBeginDenominatorToken", "token", kExtendedAttributeType_Regular);
using timeRangeBeginNumeratorToken_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> timeRangeBeginNumeratorToken("inputs:timeRangeBeginNumeratorToken", "token", kExtendedAttributeType_Regular);
using timeRangeEndDenominatorToken_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> timeRangeEndDenominatorToken("inputs:timeRangeEndDenominatorToken", "token", kExtendedAttributeType_Regular);
using timeRangeEndNumeratorToken_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> timeRangeEndNumeratorToken("inputs:timeRangeEndNumeratorToken", "token", kExtendedAttributeType_Regular);
using timeRangeName_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> timeRangeName("inputs:timeRangeName", "token", kExtendedAttributeType_Regular);
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using timeRangeBeginDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> timeRangeBeginDenominator("outputs:timeRangeBeginDenominator", "uint64", kExtendedAttributeType_Regular);
using timeRangeBeginNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> timeRangeBeginNumerator("outputs:timeRangeBeginNumerator", "int64", kExtendedAttributeType_Regular);
using timeRangeEndDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> timeRangeEndDenominator("outputs:timeRangeEndDenominator", "uint64", kExtendedAttributeType_Regular);
using timeRangeEndNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> timeRangeEndNumerator("outputs:timeRangeEndNumerator", "int64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdFabricTimeRangeExecutionAttributes;
namespace IOgnSdFabricTimeRangeExecution
{
// Read a rational time range from Fabric or RenderVars and signal its execution if
// the current time fall within this range. The range is [begin,end[, that is the end
// time does not belong to the range.
class OgnSdFabricTimeRangeExecutionDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdFabricTimeRangeExecution.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdFabricTimeRangeExecution.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdFabricTimeRangeExecution.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdFabricTimeRangeExecution.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdFabricTimeRangeExecution;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdFabricTimeRangeExecution;
    static std::tuple<int, int, int>sm_targetVersionOgnSdFabricTimeRangeExecution;
    static constexpr size_t staticAttributeCount = 15;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , gpu{offset}
        , renderResults{offset}
        , timeRangeBeginDenominatorToken{offset}
        , timeRangeBeginNumeratorToken{offset}
        , timeRangeEndDenominatorToken{offset}
        , timeRangeEndNumeratorToken{offset}
        , timeRangeName{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
        ogn::SimpleInput<const NameToken,ogn::kCpu> timeRangeBeginDenominatorToken;
        ogn::SimpleInput<const NameToken,ogn::kCpu> timeRangeBeginNumeratorToken;
        ogn::SimpleInput<const NameToken,ogn::kCpu> timeRangeEndDenominatorToken;
        ogn::SimpleInput<const NameToken,ogn::kCpu> timeRangeEndNumeratorToken;
        ogn::SimpleInput<const NameToken,ogn::kCpu> timeRangeName;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , timeRangeBeginDenominator{offset}
        , timeRangeBeginNumerator{offset}
        , timeRangeEndDenominator{offset}
        , timeRangeEndNumerator{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> timeRangeBeginDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> timeRangeBeginNumerator;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> timeRangeEndDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> timeRangeEndNumerator;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdFabricTimeRangeExecutionDatabase(NodeObj const& nodeObjParam)
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
    OgnSdFabricTimeRangeExecutionDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdFabricTimeRangeExecutionDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdFabricTimeRangeExecutionDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::exec.m_token, inputs::gpu.m_token, inputs::renderResults.m_token, inputs::timeRangeBeginDenominatorToken.m_token,
                    inputs::timeRangeBeginNumeratorToken.m_token, inputs::timeRangeEndDenominatorToken.m_token, inputs::timeRangeEndNumeratorToken.m_token, inputs::timeRangeName.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::timeRangeBeginDenominator.m_token, outputs::timeRangeBeginNumerator.m_token, outputs::timeRangeEndDenominator.m_token,
                    outputs::timeRangeEndNumerator.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<1>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<2>(inputDataHandles0));
            inputs.timeRangeBeginDenominatorToken.setContext(contextObj);
            inputs.timeRangeBeginDenominatorToken.setHandle(std::get<3>(inputDataHandles0));
            inputs.timeRangeBeginNumeratorToken.setContext(contextObj);
            inputs.timeRangeBeginNumeratorToken.setHandle(std::get<4>(inputDataHandles0));
            inputs.timeRangeEndDenominatorToken.setContext(contextObj);
            inputs.timeRangeEndDenominatorToken.setHandle(std::get<5>(inputDataHandles0));
            inputs.timeRangeEndNumeratorToken.setContext(contextObj);
            inputs.timeRangeEndNumeratorToken.setHandle(std::get<6>(inputDataHandles0));
            inputs.timeRangeName.setContext(contextObj);
            inputs.timeRangeName.setHandle(std::get<7>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.timeRangeBeginDenominator.setContext(contextObj);
            outputs.timeRangeBeginDenominator.setHandle(std::get<1>(outputDataHandles0));
            outputs.timeRangeBeginNumerator.setContext(contextObj);
            outputs.timeRangeBeginNumerator.setHandle(std::get<2>(outputDataHandles0));
            outputs.timeRangeEndDenominator.setContext(contextObj);
            outputs.timeRangeEndDenominator.setHandle(std::get<3>(outputDataHandles0));
            outputs.timeRangeEndNumerator.setContext(contextObj);
            outputs.timeRangeEndNumerator.setHandle(std::get<4>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdFabricTimeRangeExecution");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_timeRangeBeginDenominatorToken_token {"timeRangeStartDenominator"};
        inputs::timeRangeBeginDenominatorToken.setDefault(inputs_timeRangeBeginDenominatorToken_token.asTokenC());
        static omni::fabric::Token inputs_timeRangeBeginNumeratorToken_token {"timeRangeStartNumerator"};
        inputs::timeRangeBeginNumeratorToken.setDefault(inputs_timeRangeBeginNumeratorToken_token.asTokenC());
        static omni::fabric::Token inputs_timeRangeEndDenominatorToken_token {"timeRangeEndDenominator"};
        inputs::timeRangeEndDenominatorToken.setDefault(inputs_timeRangeEndDenominatorToken_token.asTokenC());
        static omni::fabric::Token inputs_timeRangeEndNumeratorToken_token {"timeRangeEndNumerator"};
        inputs::timeRangeEndNumeratorToken.setDefault(inputs_timeRangeEndNumeratorToken_token.asTokenC());
        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timeRangeBeginDenominatorToken.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timeRangeBeginNumeratorToken.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timeRangeEndDenominatorToken.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timeRangeEndNumeratorToken.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timeRangeName.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::timeRangeBeginDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::timeRangeBeginNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::timeRangeEndDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::timeRangeEndNumerator.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,graph:action");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Read a rational time range from Fabric or RenderVars and signal its execution if the current time fall within this range. The range is [begin,end[, that is the end time does not belong to the range.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations.");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render results");
        attr = iNode->getAttributeByToken(nodeObj, inputs::timeRangeBeginDenominatorToken.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Attribute name of the range begin time denominator");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"timeRangeStartDenominator\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::timeRangeBeginNumeratorToken.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Attribute name of the range begin time numerator");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"timeRangeStartNumerator\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::timeRangeEndDenominatorToken.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Attribute name of the range end time denominator");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"timeRangeEndDenominator\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::timeRangeEndNumeratorToken.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Attribute name of the range end time numerator");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"timeRangeEndNumerator\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::timeRangeName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time range name used to read from the Fabric or RenderVars.");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::timeRangeBeginDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time denominator of the last time range change (begin)");
        attr = iNode->getAttributeByToken(nodeObj, outputs::timeRangeBeginNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time numerator of the last time range change (begin)");
        attr = iNode->getAttributeByToken(nodeObj, outputs::timeRangeEndDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time denominator of the last time range change (end)");
        attr = iNode->getAttributeByToken(nodeObj, outputs::timeRangeEndNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time numerator of the last time range change (end)");
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
        sm_stateManagerOgnSdFabricTimeRangeExecution.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.gpu.isValid()
            && inputs.renderResults.isValid()
            && inputs.timeRangeBeginDenominatorToken.isValid()
            && inputs.timeRangeBeginNumeratorToken.isValid()
            && inputs.timeRangeEndDenominatorToken.isValid()
            && inputs.timeRangeEndNumeratorToken.isValid()
            && inputs.timeRangeName.isValid()
            && outputs.exec.isValid()
            && outputs.timeRangeBeginDenominator.isValid()
            && outputs.timeRangeBeginNumerator.isValid()
            && outputs.timeRangeEndDenominator.isValid()
            && outputs.timeRangeEndNumerator.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            inputs.timeRangeBeginDenominatorToken.invalidateCachedPointer();
            inputs.timeRangeBeginNumeratorToken.invalidateCachedPointer();
            inputs.timeRangeEndDenominatorToken.invalidateCachedPointer();
            inputs.timeRangeEndNumeratorToken.invalidateCachedPointer();
            inputs.timeRangeName.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.timeRangeBeginDenominator.invalidateCachedPointer();
            outputs.timeRangeBeginNumerator.invalidateCachedPointer();
            outputs.timeRangeEndDenominator.invalidateCachedPointer();
            outputs.timeRangeEndNumerator.invalidateCachedPointer();
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
            if(attrib == inputs::renderResults.m_token) {
                inputs.renderResults.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::timeRangeBeginDenominatorToken.m_token) {
                inputs.timeRangeBeginDenominatorToken.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::timeRangeBeginNumeratorToken.m_token) {
                inputs.timeRangeBeginNumeratorToken.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::timeRangeEndDenominatorToken.m_token) {
                inputs.timeRangeEndDenominatorToken.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::timeRangeEndNumeratorToken.m_token) {
                inputs.timeRangeEndNumeratorToken.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::timeRangeName.m_token) {
                inputs.timeRangeName.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::timeRangeBeginDenominator.m_token) {
                outputs.timeRangeBeginDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::timeRangeBeginNumerator.m_token) {
                outputs.timeRangeBeginNumerator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::timeRangeEndDenominator.m_token) {
                outputs.timeRangeEndDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::timeRangeEndNumerator.m_token) {
                outputs.timeRangeEndNumerator.invalidateCachedPointer();
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
            || !inputs.renderResults.canVectorize()
            || !inputs.timeRangeBeginDenominatorToken.canVectorize()
            || !inputs.timeRangeBeginNumeratorToken.canVectorize()
            || !inputs.timeRangeEndDenominatorToken.canVectorize()
            || !inputs.timeRangeEndNumeratorToken.canVectorize()
            || !inputs.timeRangeName.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.timeRangeBeginDenominator.canVectorize()
            || !outputs.timeRangeBeginNumerator.canVectorize()
            || !outputs.timeRangeEndDenominator.canVectorize()
            || !outputs.timeRangeEndNumerator.canVectorize()
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
        if(token == inputs::renderResults.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderResults.setHandle(hdl);
            return;
        }
        if(token == inputs::timeRangeBeginDenominatorToken.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.timeRangeBeginDenominatorToken.setHandle(hdl);
            return;
        }
        if(token == inputs::timeRangeBeginNumeratorToken.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.timeRangeBeginNumeratorToken.setHandle(hdl);
            return;
        }
        if(token == inputs::timeRangeEndDenominatorToken.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.timeRangeEndDenominatorToken.setHandle(hdl);
            return;
        }
        if(token == inputs::timeRangeEndNumeratorToken.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.timeRangeEndNumeratorToken.setHandle(hdl);
            return;
        }
        if(token == inputs::timeRangeName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.timeRangeName.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::timeRangeBeginDenominator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.timeRangeBeginDenominator.setHandle(hdl);
            return;
        }
        if(token == outputs::timeRangeBeginNumerator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.timeRangeBeginNumerator.setHandle(hdl);
            return;
        }
        if(token == outputs::timeRangeEndDenominator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.timeRangeEndDenominator.setHandle(hdl);
            return;
        }
        if(token == outputs::timeRangeEndNumerator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.timeRangeEndNumerator.setHandle(hdl);
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
        auto variable = const_cast<OgnSdFabricTimeRangeExecutionDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdFabricTimeRangeExecutionDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdFabricTimeRangeExecutionDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdFabricTimeRangeExecutionDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdFabricTimeRangeExecutionDatabase::sm_stateManagerOgnSdFabricTimeRangeExecution;
std::tuple<int, int, int> OgnSdFabricTimeRangeExecutionDatabase::sm_generatorVersionOgnSdFabricTimeRangeExecution{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdFabricTimeRangeExecutionDatabase::sm_targetVersionOgnSdFabricTimeRangeExecution{std::make_tuple(2,184,5)};
}
using namespace IOgnSdFabricTimeRangeExecution;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdFabricTimeRangeExecution, OgnSdFabricTimeRangeExecutionDatabase> s_registration("omni.syntheticdata.SdFabricTimeRangeExecution", 1, "omni.syntheticdata"); \
}
