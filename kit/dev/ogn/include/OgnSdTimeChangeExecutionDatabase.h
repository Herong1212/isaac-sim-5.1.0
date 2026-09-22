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

namespace OgnSdTimeChangeExecutionAttributes
{
namespace inputs
{
using errorOnFutureChange_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> errorOnFutureChange("inputs:errorOnFutureChange", "bool", kExtendedAttributeType_Regular, false);
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using lastUpdateTimeDenominator_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> lastUpdateTimeDenominator("inputs:lastUpdateTimeDenominator", "uint64", kExtendedAttributeType_Regular, 0);
using lastUpdateTimeNumerator_t = const int64_t&;
ogn::AttributeInitializer<const int64_t, ogn::kOgnInput> lastUpdateTimeNumerator("inputs:lastUpdateTimeNumerator", "int64", kExtendedAttributeType_Regular, 0);
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
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
using namespace OgnSdTimeChangeExecutionAttributes;
namespace IOgnSdTimeChangeExecution
{
// Set its execution output if the input rational time is more recent that the last
// registered time.
class OgnSdTimeChangeExecutionDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdTimeChangeExecution.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdTimeChangeExecution.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdTimeChangeExecution.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdTimeChangeExecution.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdTimeChangeExecution;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdTimeChangeExecution;
    static std::tuple<int, int, int>sm_targetVersionOgnSdTimeChangeExecution;
    static constexpr size_t staticAttributeCount = 8;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : errorOnFutureChange{offset}
        , exec{offset,AttributeRole::eExecution}
        , lastUpdateTimeDenominator{offset}
        , lastUpdateTimeNumerator{offset}
        , renderResults{offset}
        {}
        ogn::SimpleInput<const bool,ogn::kCpu> errorOnFutureChange;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> lastUpdateTimeDenominator;
        ogn::SimpleInput<const int64_t,ogn::kCpu> lastUpdateTimeNumerator;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdTimeChangeExecutionDatabase(NodeObj const& nodeObjParam)
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
    OgnSdTimeChangeExecutionDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdTimeChangeExecutionDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdTimeChangeExecutionDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::errorOnFutureChange.m_token, inputs::exec.m_token, inputs::lastUpdateTimeDenominator.m_token, inputs::lastUpdateTimeNumerator.m_token,
                    inputs::renderResults.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token
                )
            , kAccordingToContextIndex);
            inputs.errorOnFutureChange.setContext(contextObj);
            inputs.errorOnFutureChange.setHandle(std::get<0>(inputDataHandles0));
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<1>(inputDataHandles0));
            inputs.lastUpdateTimeDenominator.setContext(contextObj);
            inputs.lastUpdateTimeDenominator.setHandle(std::get<2>(inputDataHandles0));
            inputs.lastUpdateTimeNumerator.setContext(contextObj);
            inputs.lastUpdateTimeNumerator.setHandle(std::get<3>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<4>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdTimeChangeExecution");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::errorOnFutureChange.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::lastUpdateTimeDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::lastUpdateTimeNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,graph:action");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Set its execution output if the input rational time is more recent that the last registered time.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::errorOnFutureChange.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Print error if the last update is in the future.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::lastUpdateTimeDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time denominator of the last time change");
        attr = iNode->getAttributeByToken(nodeObj, inputs::lastUpdateTimeNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Time numerator of the last time change");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render results");
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
        sm_stateManagerOgnSdTimeChangeExecution.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.errorOnFutureChange.isValid()
            && inputs.exec.isValid()
            && inputs.lastUpdateTimeDenominator.isValid()
            && inputs.lastUpdateTimeNumerator.isValid()
            && inputs.renderResults.isValid()
            && outputs.exec.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.errorOnFutureChange.invalidateCachedPointer();
            inputs.exec.invalidateCachedPointer();
            inputs.lastUpdateTimeDenominator.invalidateCachedPointer();
            inputs.lastUpdateTimeNumerator.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::errorOnFutureChange.m_token) {
                inputs.errorOnFutureChange.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::lastUpdateTimeDenominator.m_token) {
                inputs.lastUpdateTimeDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::lastUpdateTimeNumerator.m_token) {
                inputs.lastUpdateTimeNumerator.invalidateCachedPointer();
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
        if( !inputs.errorOnFutureChange.canVectorize()
            || !inputs.exec.canVectorize()
            || !inputs.lastUpdateTimeDenominator.canVectorize()
            || !inputs.lastUpdateTimeNumerator.canVectorize()
            || !inputs.renderResults.canVectorize()
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
        if(token == inputs::errorOnFutureChange.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.errorOnFutureChange.setHandle(hdl);
            return;
        }
        if(token == inputs::exec.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exec.setHandle(hdl);
            return;
        }
        if(token == inputs::lastUpdateTimeDenominator.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.lastUpdateTimeDenominator.setHandle(hdl);
            return;
        }
        if(token == inputs::lastUpdateTimeNumerator.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.lastUpdateTimeNumerator.setHandle(hdl);
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
        auto variable = const_cast<OgnSdTimeChangeExecutionDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdTimeChangeExecutionDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdTimeChangeExecutionDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdTimeChangeExecutionDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdTimeChangeExecutionDatabase::sm_stateManagerOgnSdTimeChangeExecution;
std::tuple<int, int, int> OgnSdTimeChangeExecutionDatabase::sm_generatorVersionOgnSdTimeChangeExecution{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdTimeChangeExecutionDatabase::sm_targetVersionOgnSdTimeChangeExecution{std::make_tuple(2,184,5)};
}
using namespace IOgnSdTimeChangeExecution;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdTimeChangeExecution, OgnSdTimeChangeExecutionDatabase> s_registration("omni.syntheticdata.SdTimeChangeExecution", 1, "omni.syntheticdata"); \
}
