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

namespace OgnSdTestStageSynchronizationAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using randomMaxProcessingTimeUs_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> randomMaxProcessingTimeUs("inputs:randomMaxProcessingTimeUs", "uint", kExtendedAttributeType_Regular, 0);
using randomSeed_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> randomSeed("inputs:randomSeed", "uint", kExtendedAttributeType_Regular, 0);
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using swhFrameNumber_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> swhFrameNumber("inputs:swhFrameNumber", "uint64", kExtendedAttributeType_Regular, 0);
using tag_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> tag("inputs:tag", "token", kExtendedAttributeType_Regular);
using traceError_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> traceError("inputs:traceError", "bool", kExtendedAttributeType_Regular, false);
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using fabricSWHFrameNumber_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> fabricSWHFrameNumber("outputs:fabricSWHFrameNumber", "uint64", kExtendedAttributeType_Regular);
using swhFrameNumber_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> swhFrameNumber("outputs:swhFrameNumber", "uint64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdTestStageSynchronizationAttributes;
namespace IOgnSdTestStageSynchronization
{
// Synthetic Data node to test the pipeline stage synchronization
class OgnSdTestStageSynchronizationDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdTestStageSynchronization.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdTestStageSynchronization.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdTestStageSynchronization.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdTestStageSynchronization.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdTestStageSynchronization;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdTestStageSynchronization;
    static std::tuple<int, int, int>sm_targetVersionOgnSdTestStageSynchronization;
    static constexpr size_t staticAttributeCount = 14;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , gpu{offset}
        , randomMaxProcessingTimeUs{offset}
        , randomSeed{offset}
        , renderResults{offset}
        , rp{offset}
        , swhFrameNumber{offset}
        , tag{offset}
        , traceError{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> randomMaxProcessingTimeUs;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> randomSeed;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> swhFrameNumber;
        ogn::SimpleInput<const NameToken,ogn::kCpu> tag;
        ogn::SimpleInput<const bool,ogn::kCpu> traceError;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , fabricSWHFrameNumber{offset}
        , swhFrameNumber{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> fabricSWHFrameNumber;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> swhFrameNumber;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdTestStageSynchronizationDatabase(NodeObj const& nodeObjParam)
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
    OgnSdTestStageSynchronizationDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdTestStageSynchronizationDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdTestStageSynchronizationDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::exec.m_token, inputs::gpu.m_token, inputs::randomMaxProcessingTimeUs.m_token, inputs::randomSeed.m_token,
                    inputs::renderResults.m_token, inputs::rp.m_token, inputs::swhFrameNumber.m_token, inputs::tag.m_token,
                    inputs::traceError.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::fabricSWHFrameNumber.m_token, outputs::swhFrameNumber.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<1>(inputDataHandles0));
            inputs.randomMaxProcessingTimeUs.setContext(contextObj);
            inputs.randomMaxProcessingTimeUs.setHandle(std::get<2>(inputDataHandles0));
            inputs.randomSeed.setContext(contextObj);
            inputs.randomSeed.setHandle(std::get<3>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<4>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<5>(inputDataHandles0));
            inputs.swhFrameNumber.setContext(contextObj);
            inputs.swhFrameNumber.setHandle(std::get<6>(inputDataHandles0));
            inputs.tag.setContext(contextObj);
            inputs.tag.setHandle(std::get<7>(inputDataHandles0));
            inputs.traceError.setContext(contextObj);
            inputs.traceError.setHandle(std::get<8>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.fabricSWHFrameNumber.setContext(contextObj);
            outputs.fabricSWHFrameNumber.setHandle(std::get<1>(outputDataHandles0));
            outputs.swhFrameNumber.setContext(contextObj);
            outputs.swhFrameNumber.setHandle(std::get<2>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdTestStageSynchronization");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::randomMaxProcessingTimeUs.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::randomSeed.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::swhFrameNumber.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::tag.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::traceError.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::fabricSWHFrameNumber.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::swhFrameNumber.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:simulation,graph:postRender,graph:action,internal:test");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to test the pipeline stage synchronization");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExclusions, "tests");
        // LCOV_EXCL_STOP
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "OnDemand connection : trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "PostRender connection : pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::randomMaxProcessingTimeUs.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Maximum number of micro-seconds to randomly (uniformely) wait for in order to simulate varying workload");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::randomSeed.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Random seed for the randomization");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "OnDemand connection : pointer to render product results");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "PostRender connection : pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::swhFrameNumber.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Fabric frame number");
        attr = iNode->getAttributeByToken(nodeObj, inputs::tag.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "A tag to identify the node");
        attr = iNode->getAttributeByToken(nodeObj, inputs::traceError.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If true print an error message when the frame numbers are out-of-sync");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "OnDemand connection : trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::fabricSWHFrameNumber.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Fabric frame number from the fabric");
        attr = iNode->getAttributeByToken(nodeObj, outputs::swhFrameNumber.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Fabric frame number");
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
        sm_stateManagerOgnSdTestStageSynchronization.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        return validateNode()
            && inputs.exec.isValid()
            && inputs.gpu.isValid()
            && inputs.randomMaxProcessingTimeUs.isValid()
            && inputs.randomSeed.isValid()
            && inputs.renderResults.isValid()
            && inputs.rp.isValid()
            && inputs.swhFrameNumber.isValid()
            && inputs.tag.isValid()
            && inputs.traceError.isValid()
            && outputs.exec.isValid()
            && outputs.fabricSWHFrameNumber.isValid()
            && outputs.swhFrameNumber.isValid()
        ;
        // LCOV_EXCL_STOP
    }
    void preCompute() {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.randomMaxProcessingTimeUs.invalidateCachedPointer();
            inputs.randomSeed.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.swhFrameNumber.invalidateCachedPointer();
            inputs.tag.invalidateCachedPointer();
            inputs.traceError.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.fabricSWHFrameNumber.invalidateCachedPointer();
            outputs.swhFrameNumber.invalidateCachedPointer();
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
            if(attrib == inputs::randomMaxProcessingTimeUs.m_token) {
                inputs.randomMaxProcessingTimeUs.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::randomSeed.m_token) {
                inputs.randomSeed.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderResults.m_token) {
                inputs.renderResults.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::swhFrameNumber.m_token) {
                inputs.swhFrameNumber.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::tag.m_token) {
                inputs.tag.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::traceError.m_token) {
                inputs.traceError.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::fabricSWHFrameNumber.m_token) {
                outputs.fabricSWHFrameNumber.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::swhFrameNumber.m_token) {
                outputs.swhFrameNumber.invalidateCachedPointer();
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
            || !inputs.gpu.canVectorize()
            || !inputs.randomMaxProcessingTimeUs.canVectorize()
            || !inputs.randomSeed.canVectorize()
            || !inputs.renderResults.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.swhFrameNumber.canVectorize()
            || !inputs.tag.canVectorize()
            || !inputs.traceError.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.fabricSWHFrameNumber.canVectorize()
            || !outputs.swhFrameNumber.canVectorize()
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
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::randomMaxProcessingTimeUs.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.randomMaxProcessingTimeUs.setHandle(hdl);
            return;
        }
        if(token == inputs::randomSeed.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.randomSeed.setHandle(hdl);
            return;
        }
        if(token == inputs::renderResults.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderResults.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == inputs::swhFrameNumber.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.swhFrameNumber.setHandle(hdl);
            return;
        }
        if(token == inputs::tag.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.tag.setHandle(hdl);
            return;
        }
        if(token == inputs::traceError.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.traceError.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::fabricSWHFrameNumber.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.fabricSWHFrameNumber.setHandle(hdl);
            return;
        }
        if(token == outputs::swhFrameNumber.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.swhFrameNumber.setHandle(hdl);
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
        auto variable = const_cast<OgnSdTestStageSynchronizationDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdTestStageSynchronizationDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdTestStageSynchronizationDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdTestStageSynchronizationDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdTestStageSynchronizationDatabase::sm_stateManagerOgnSdTestStageSynchronization;
std::tuple<int, int, int> OgnSdTestStageSynchronizationDatabase::sm_generatorVersionOgnSdTestStageSynchronization{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdTestStageSynchronizationDatabase::sm_targetVersionOgnSdTestStageSynchronization{std::make_tuple(2,184,5)};
}
using namespace IOgnSdTestStageSynchronization;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdTestStageSynchronization, OgnSdTestStageSynchronizationDatabase> s_registration("omni.syntheticdata.SdTestStageSynchronization", 1, "omni.syntheticdata"); \
}
