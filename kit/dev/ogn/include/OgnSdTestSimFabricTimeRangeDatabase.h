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

namespace OgnSdTestSimFabricTimeRangeAttributes
{
namespace inputs
{
using numberOfFrames_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> numberOfFrames("inputs:numberOfFrames", "uint64", kExtendedAttributeType_Regular, 0);
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
}
namespace state
{
}
}
using namespace OgnSdTestSimFabricTimeRangeAttributes;
namespace IOgnSdTestSimFabricTimeRange
{
// Testing node : on request write/update a Fabric time range of a given number of frames
// starting at the current simulation time.
class OgnSdTestSimFabricTimeRangeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken fc_exportToRingbuffer;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdTestSimFabricTimeRange.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdTestSimFabricTimeRange.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdTestSimFabricTimeRange.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdTestSimFabricTimeRange.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdTestSimFabricTimeRange;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdTestSimFabricTimeRange;
    static std::tuple<int, int, int>sm_targetVersionOgnSdTestSimFabricTimeRange;
    static constexpr size_t staticAttributeCount = 9;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : numberOfFrames{offset}
        , timeRangeBeginDenominatorToken{offset}
        , timeRangeBeginNumeratorToken{offset}
        , timeRangeEndDenominatorToken{offset}
        , timeRangeEndNumeratorToken{offset}
        , timeRangeName{offset}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> numberOfFrames;
        ogn::SimpleInput<const NameToken,ogn::kCpu> timeRangeBeginDenominatorToken;
        ogn::SimpleInput<const NameToken,ogn::kCpu> timeRangeBeginNumeratorToken;
        ogn::SimpleInput<const NameToken,ogn::kCpu> timeRangeEndDenominatorToken;
        ogn::SimpleInput<const NameToken,ogn::kCpu> timeRangeEndNumeratorToken;
        ogn::SimpleInput<const NameToken,ogn::kCpu> timeRangeName;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdTestSimFabricTimeRangeDatabase(NodeObj const& nodeObjParam)
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
    OgnSdTestSimFabricTimeRangeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdTestSimFabricTimeRangeDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdTestSimFabricTimeRangeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::numberOfFrames.m_token, inputs::timeRangeBeginDenominatorToken.m_token, inputs::timeRangeBeginNumeratorToken.m_token, inputs::timeRangeEndDenominatorToken.m_token,
                    inputs::timeRangeEndNumeratorToken.m_token, inputs::timeRangeName.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token
                )
            , kAccordingToContextIndex);
            inputs.numberOfFrames.setContext(contextObj);
            inputs.numberOfFrames.setHandle(std::get<0>(inputDataHandles0));
            inputs.timeRangeBeginDenominatorToken.setContext(contextObj);
            inputs.timeRangeBeginDenominatorToken.setHandle(std::get<1>(inputDataHandles0));
            inputs.timeRangeBeginNumeratorToken.setContext(contextObj);
            inputs.timeRangeBeginNumeratorToken.setHandle(std::get<2>(inputDataHandles0));
            inputs.timeRangeEndDenominatorToken.setContext(contextObj);
            inputs.timeRangeEndDenominatorToken.setHandle(std::get<3>(inputDataHandles0));
            inputs.timeRangeEndNumeratorToken.setContext(contextObj);
            inputs.timeRangeEndNumeratorToken.setHandle(std::get<4>(inputDataHandles0));
            inputs.timeRangeName.setContext(contextObj);
            inputs.timeRangeName.setHandle(std::get<5>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdTestSimFabricTimeRange");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdTestSimFabricTimeRangeDatabase::tokens.fc_exportToRingbuffer = iToken.getHandle("fc_exportToRingbuffer");

        static omni::fabric::Token inputs_timeRangeBeginDenominatorToken_token {"timeRangeStartDenominator"};
        inputs::timeRangeBeginDenominatorToken.setDefault(inputs_timeRangeBeginDenominatorToken_token.asTokenC());
        static omni::fabric::Token inputs_timeRangeBeginNumeratorToken_token {"timeRangeStartNumerator"};
        inputs::timeRangeBeginNumeratorToken.setDefault(inputs_timeRangeBeginNumeratorToken_token.asTokenC());
        static omni::fabric::Token inputs_timeRangeEndDenominatorToken_token {"timeRangeEndDenominator"};
        inputs::timeRangeEndDenominatorToken.setDefault(inputs_timeRangeEndDenominatorToken_token.asTokenC());
        static omni::fabric::Token inputs_timeRangeEndNumeratorToken_token {"timeRangeEndNumerator"};
        inputs::timeRangeEndNumeratorToken.setDefault(inputs_timeRangeEndNumeratorToken_token.asTokenC());
        static omni::fabric::Token inputs_timeRangeName_token {"TestSimFabricTimeRangeSD"};
        inputs::timeRangeName.setDefault(inputs_timeRangeName_token.asTokenC());
        inputs::numberOfFrames.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timeRangeBeginDenominatorToken.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timeRangeBeginNumeratorToken.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timeRangeEndDenominatorToken.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timeRangeEndNumeratorToken.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timeRangeName.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"fc_exportToRingbuffer\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:simulation,internal,event");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Testing node : on request write/update a Fabric time range of a given number of frames starting at the current simulation time.");
        auto __schedulingInfo = nodeTypeObj.iNodeType->getSchedulingHints(nodeTypeObj);
        CARB_ASSERT(__schedulingInfo, "Could not acquire the scheduling hints");
        if (__schedulingInfo)
        {
            __schedulingInfo->setComputeRule(eComputeRule::eOnRequest);
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
        attr = iNode->getAttributeByToken(nodeObj, inputs::numberOfFrames.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number of frames to writes.");
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
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time range name used to write to the Fabric.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"TestSimFabricTimeRangeSD\"");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
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
        sm_stateManagerOgnSdTestSimFabricTimeRange.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.numberOfFrames.isValid()
            && inputs.timeRangeBeginDenominatorToken.isValid()
            && inputs.timeRangeBeginNumeratorToken.isValid()
            && inputs.timeRangeEndDenominatorToken.isValid()
            && inputs.timeRangeEndNumeratorToken.isValid()
            && inputs.timeRangeName.isValid()
            && outputs.exec.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.numberOfFrames.invalidateCachedPointer();
            inputs.timeRangeBeginDenominatorToken.invalidateCachedPointer();
            inputs.timeRangeBeginNumeratorToken.invalidateCachedPointer();
            inputs.timeRangeEndDenominatorToken.invalidateCachedPointer();
            inputs.timeRangeEndNumeratorToken.invalidateCachedPointer();
            inputs.timeRangeName.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::numberOfFrames.m_token) {
                inputs.numberOfFrames.invalidateCachedPointer();
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
        if( !inputs.numberOfFrames.canVectorize()
            || !inputs.timeRangeBeginDenominatorToken.canVectorize()
            || !inputs.timeRangeBeginNumeratorToken.canVectorize()
            || !inputs.timeRangeEndDenominatorToken.canVectorize()
            || !inputs.timeRangeEndNumeratorToken.canVectorize()
            || !inputs.timeRangeName.canVectorize()
            || !outputs.exec.canVectorize()
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
        if(token == inputs::numberOfFrames.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.numberOfFrames.setHandle(hdl);
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
ogn::StateManager OgnSdTestSimFabricTimeRangeDatabase::sm_stateManagerOgnSdTestSimFabricTimeRange;
std::tuple<int, int, int> OgnSdTestSimFabricTimeRangeDatabase::sm_generatorVersionOgnSdTestSimFabricTimeRange{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdTestSimFabricTimeRangeDatabase::sm_targetVersionOgnSdTestSimFabricTimeRange{std::make_tuple(2,184,5)};
OgnSdTestSimFabricTimeRangeDatabase::TokenManager OgnSdTestSimFabricTimeRangeDatabase::tokens;
}
using namespace IOgnSdTestSimFabricTimeRange;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdTestSimFabricTimeRange, OgnSdTestSimFabricTimeRangeDatabase> s_registration("omni.syntheticdata.SdTestSimFabricTimeRange", 1, "omni.syntheticdata"); \
}
