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

namespace OgnSdFrameIdentifierAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using durationDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> durationDenominator("outputs:durationDenominator", "uint64", kExtendedAttributeType_Regular, 0);
using durationNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> durationNumerator("outputs:durationNumerator", "int64", kExtendedAttributeType_Regular, 0);
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using externalTimeOfSimNs_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> externalTimeOfSimNs("outputs:externalTimeOfSimNs", "int64", kExtendedAttributeType_Regular, -1);
using frameNumber_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> frameNumber("outputs:frameNumber", "int64", kExtendedAttributeType_Regular, -1);
using rationalTimeOfSimDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> rationalTimeOfSimDenominator("outputs:rationalTimeOfSimDenominator", "uint64", kExtendedAttributeType_Regular, 0);
using rationalTimeOfSimNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> rationalTimeOfSimNumerator("outputs:rationalTimeOfSimNumerator", "int64", kExtendedAttributeType_Regular, 0);
using sampleTimeOffsetInSimFrames_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> sampleTimeOffsetInSimFrames("outputs:sampleTimeOffsetInSimFrames", "uint64", kExtendedAttributeType_Regular, 0);
using type_t = NameToken&;
ogn::AttributeInitializer<NameToken, ogn::kOgnOutput> type("outputs:type", "token", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdFrameIdentifierAttributes;
namespace IOgnSdFrameIdentifier
{
// Synthetic Data node to expose pipeline frame identifier.
class OgnSdFrameIdentifierDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken NoFrameNumber;
        NameToken FrameNumber;
        NameToken ConstantFramerateFrameNumber;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdFrameIdentifier.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdFrameIdentifier.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdFrameIdentifier.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdFrameIdentifier.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdFrameIdentifier;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdFrameIdentifier;
    static std::tuple<int, int, int>sm_targetVersionOgnSdFrameIdentifier;
    static constexpr size_t staticAttributeCount = 13;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , renderResults{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : durationDenominator{offset}
        , durationNumerator{offset}
        , exec{offset,AttributeRole::eExecution}
        , externalTimeOfSimNs{offset}
        , frameNumber{offset}
        , rationalTimeOfSimDenominator{offset}
        , rationalTimeOfSimNumerator{offset}
        , sampleTimeOffsetInSimFrames{offset}
        , type{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> durationDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> durationNumerator;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<int64_t,ogn::kCpu> externalTimeOfSimNs;
        ogn::SimpleOutput<int64_t,ogn::kCpu> frameNumber;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> rationalTimeOfSimDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> rationalTimeOfSimNumerator;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> sampleTimeOffsetInSimFrames;
        ogn::SimpleOutput<NameToken,ogn::kCpu> type;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdFrameIdentifierDatabase(NodeObj const& nodeObjParam)
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
    OgnSdFrameIdentifierDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdFrameIdentifierDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdFrameIdentifierDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::exec.m_token, inputs::renderResults.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::durationDenominator.m_token, outputs::durationNumerator.m_token, outputs::exec.m_token, outputs::externalTimeOfSimNs.m_token,
                    outputs::frameNumber.m_token, outputs::rationalTimeOfSimDenominator.m_token, outputs::rationalTimeOfSimNumerator.m_token, outputs::sampleTimeOffsetInSimFrames.m_token,
                    outputs::type.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<1>(inputDataHandles0));
            outputs.durationDenominator.setContext(contextObj);
            outputs.durationDenominator.setHandle(std::get<0>(outputDataHandles0));
            outputs.durationNumerator.setContext(contextObj);
            outputs.durationNumerator.setHandle(std::get<1>(outputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<2>(outputDataHandles0));
            outputs.externalTimeOfSimNs.setContext(contextObj);
            outputs.externalTimeOfSimNs.setHandle(std::get<3>(outputDataHandles0));
            outputs.frameNumber.setContext(contextObj);
            outputs.frameNumber.setHandle(std::get<4>(outputDataHandles0));
            outputs.rationalTimeOfSimDenominator.setContext(contextObj);
            outputs.rationalTimeOfSimDenominator.setHandle(std::get<5>(outputDataHandles0));
            outputs.rationalTimeOfSimNumerator.setContext(contextObj);
            outputs.rationalTimeOfSimNumerator.setHandle(std::get<6>(outputDataHandles0));
            outputs.sampleTimeOffsetInSimFrames.setContext(contextObj);
            outputs.sampleTimeOffsetInSimFrames.setHandle(std::get<7>(outputDataHandles0));
            outputs.type.setContext(contextObj);
            outputs.type.setHandle(std::get<8>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdFrameIdentifier");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdFrameIdentifierDatabase::tokens.NoFrameNumber = iToken.getHandle("NoFrameNumber");
        OgnSdFrameIdentifierDatabase::tokens.FrameNumber = iToken.getHandle("FrameNumber");
        OgnSdFrameIdentifierDatabase::tokens.ConstantFramerateFrameNumber = iToken.getHandle("ConstantFramerateFrameNumber");

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);

        static omni::fabric::Token outputs_type_token {"NoFrameNumber"};
        outputs::type.setDefault(outputs_type_token.asTokenC());
        outputs::durationDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::durationNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::externalTimeOfSimNs.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::frameNumber.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rationalTimeOfSimDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rationalTimeOfSimNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sampleTimeOffsetInSimFrames.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::type.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,graph:action");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to expose pipeline frame identifier.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render results");
        attr = iNode->getAttributeByToken(nodeObj, outputs::durationDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Duration denominator.\nOnly valid if eConstantFramerateFrameNumber");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::durationNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Duration numerator.\nOnly valid if eConstantFramerateFrameNumber.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes for each newFrame event received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Received");
        attr = iNode->getAttributeByToken(nodeObj, outputs::externalTimeOfSimNs.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "External time in Ns.\nOnly valid if eConstantFramerateFrameNumber.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1");
        attr = iNode->getAttributeByToken(nodeObj, outputs::frameNumber.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Frame number.\nValid if eFrameNumber or eConstantFramerateFrameNumber.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rationalTimeOfSimDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "rational time of simulation denominator.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rationalTimeOfSimNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "rational time of simulation numerator.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sampleTimeOffsetInSimFrames.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Sample time offset.\nOnly valid if eConstantFramerateFrameNumber.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::type.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Type of the frame identifier.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataAllowedTokens, "NoFrameNumber,FrameNumber,ConstantFramerateFrameNumber");
        attr.iAttribute->setMetadata(attr, kOgnMetadataAllowedTokensRaw, "[\"NoFrameNumber\", \"FrameNumber\", \"ConstantFramerateFrameNumber\"]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"NoFrameNumber\"");
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
        sm_stateManagerOgnSdFrameIdentifier.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.renderResults.isValid()
            && outputs.durationDenominator.isValid()
            && outputs.durationNumerator.isValid()
            && outputs.exec.isValid()
            && outputs.externalTimeOfSimNs.isValid()
            && outputs.frameNumber.isValid()
            && outputs.rationalTimeOfSimDenominator.isValid()
            && outputs.rationalTimeOfSimNumerator.isValid()
            && outputs.sampleTimeOffsetInSimFrames.isValid()
            && outputs.type.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            outputs.durationDenominator.invalidateCachedPointer();
            outputs.durationNumerator.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.externalTimeOfSimNs.invalidateCachedPointer();
            outputs.frameNumber.invalidateCachedPointer();
            outputs.rationalTimeOfSimDenominator.invalidateCachedPointer();
            outputs.rationalTimeOfSimNumerator.invalidateCachedPointer();
            outputs.sampleTimeOffsetInSimFrames.invalidateCachedPointer();
            outputs.type.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderResults.m_token) {
                inputs.renderResults.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::durationDenominator.m_token) {
                outputs.durationDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::durationNumerator.m_token) {
                outputs.durationNumerator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::externalTimeOfSimNs.m_token) {
                outputs.externalTimeOfSimNs.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::frameNumber.m_token) {
                outputs.frameNumber.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::rationalTimeOfSimDenominator.m_token) {
                outputs.rationalTimeOfSimDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::rationalTimeOfSimNumerator.m_token) {
                outputs.rationalTimeOfSimNumerator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sampleTimeOffsetInSimFrames.m_token) {
                outputs.sampleTimeOffsetInSimFrames.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::type.m_token) {
                outputs.type.invalidateCachedPointer();
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
            || !inputs.renderResults.canVectorize()
            || !outputs.durationDenominator.canVectorize()
            || !outputs.durationNumerator.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.externalTimeOfSimNs.canVectorize()
            || !outputs.frameNumber.canVectorize()
            || !outputs.rationalTimeOfSimDenominator.canVectorize()
            || !outputs.rationalTimeOfSimNumerator.canVectorize()
            || !outputs.sampleTimeOffsetInSimFrames.canVectorize()
            || !outputs.type.canVectorize()
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
        if(token == inputs::renderResults.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderResults.setHandle(hdl);
            return;
        }
        if(token == outputs::durationDenominator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.durationDenominator.setHandle(hdl);
            return;
        }
        if(token == outputs::durationNumerator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.durationNumerator.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::externalTimeOfSimNs.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.externalTimeOfSimNs.setHandle(hdl);
            return;
        }
        if(token == outputs::frameNumber.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.frameNumber.setHandle(hdl);
            return;
        }
        if(token == outputs::rationalTimeOfSimDenominator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rationalTimeOfSimDenominator.setHandle(hdl);
            return;
        }
        if(token == outputs::rationalTimeOfSimNumerator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rationalTimeOfSimNumerator.setHandle(hdl);
            return;
        }
        if(token == outputs::sampleTimeOffsetInSimFrames.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sampleTimeOffsetInSimFrames.setHandle(hdl);
            return;
        }
        if(token == outputs::type.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.type.setHandle(hdl);
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
        auto variable = const_cast<OgnSdFrameIdentifierDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdFrameIdentifierDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdFrameIdentifierDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdFrameIdentifierDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdFrameIdentifierDatabase::sm_stateManagerOgnSdFrameIdentifier;
std::tuple<int, int, int> OgnSdFrameIdentifierDatabase::sm_generatorVersionOgnSdFrameIdentifier{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdFrameIdentifierDatabase::sm_targetVersionOgnSdFrameIdentifier{std::make_tuple(2,184,5)};
OgnSdFrameIdentifierDatabase::TokenManager OgnSdFrameIdentifierDatabase::tokens;
}
using namespace IOgnSdFrameIdentifier;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdFrameIdentifier, OgnSdFrameIdentifierDatabase> s_registration("omni.syntheticdata.SdFrameIdentifier", 1, "omni.syntheticdata"); \
}
