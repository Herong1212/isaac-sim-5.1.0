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

namespace OgnSdOnNewFrameAttributes
{
namespace inputs
{
}
namespace outputs
{
using cudaStream_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> cudaStream("outputs:cudaStream", "uint64", kExtendedAttributeType_Regular);
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using referenceTimeDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> referenceTimeDenominator("outputs:referenceTimeDenominator", "uint64", kExtendedAttributeType_Regular);
using referenceTimeNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> referenceTimeNumerator("outputs:referenceTimeNumerator", "int64", kExtendedAttributeType_Regular);
using renderProductDataPtrs_t = ogn::array<uint64_t>&;
ogn::AttributeInitializer<uint64_t*, ogn::kOgnOutput> renderProductDataPtrs("outputs:renderProductDataPtrs", "uint64[]", kExtendedAttributeType_Regular, nullptr, 0);
using renderProductPaths_t = ogn::array<NameToken>&;
ogn::AttributeInitializer<NameToken*, ogn::kOgnOutput> renderProductPaths("outputs:renderProductPaths", "token[]", kExtendedAttributeType_Regular, nullptr, 0);
}
namespace state
{
}
}
using namespace OgnSdOnNewFrameAttributes;
namespace IOgnSdOnNewFrame
{
// Synthetic Data postprocess node to execute pipeline after the NewFrame event has
// been received
class OgnSdOnNewFrameDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdOnNewFrame.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdOnNewFrame.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdOnNewFrame.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdOnNewFrame.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdOnNewFrame;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdOnNewFrame;
    static std::tuple<int, int, int>sm_targetVersionOgnSdOnNewFrame;
    static constexpr size_t staticAttributeCount = 8;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct outputsT {
        outputsT(size_t const& offset)
        : cudaStream{offset}
        , exec{offset,AttributeRole::eExecution}
        , referenceTimeDenominator{offset}
        , referenceTimeNumerator{offset}
        , renderProductDataPtrs{offset}
        , renderProductPaths{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> cudaStream;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> referenceTimeDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> referenceTimeNumerator;
        ogn::ArrayOutput<uint64_t,ogn::kCpu> renderProductDataPtrs;
        ogn::ArrayOutput<NameToken,ogn::kCpu> renderProductPaths;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdOnNewFrameDatabase(NodeObj const& nodeObjParam)
    : OmniGraphDatabase()
    , outputs{m_offset.index}
    {
        GraphContextObj const* contexts = nullptr;
        NodeObj const* nodes = nullptr;
        size_t handleCount = nodeObjParam.iNode->getAutoInstances(nodeObjParam, contexts, nodes);
        _ctor(contexts, nodes, handleCount);
        _init();
    }

    CARB_DEPRECATED("Passing the graph context to the temporary stack allocated database is not necessary anymore: you can safely remove this parameter")
    OgnSdOnNewFrameDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdOnNewFrameDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdOnNewFrameDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
    : OmniGraphDatabase()
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
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::cudaStream.m_token, outputs::exec.m_token, outputs::referenceTimeDenominator.m_token, outputs::referenceTimeNumerator.m_token,
                    outputs::renderProductDataPtrs.m_token, outputs::renderProductPaths.m_token
                )
            , kAccordingToContextIndex);
            outputs.cudaStream.setContext(contextObj);
            outputs.cudaStream.setHandle(std::get<0>(outputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<1>(outputDataHandles0));
            outputs.referenceTimeDenominator.setContext(contextObj);
            outputs.referenceTimeDenominator.setHandle(std::get<2>(outputDataHandles0));
            outputs.referenceTimeNumerator.setContext(contextObj);
            outputs.referenceTimeNumerator.setHandle(std::get<3>(outputDataHandles0));
            outputs.renderProductDataPtrs.setContext(contextObj);
            outputs.renderProductDataPtrs.setHandle(std::get<4>(outputDataHandles0));
            outputs.renderProductPaths.setContext(contextObj);
            outputs.renderProductPaths.setHandle(std::get<5>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdOnNewFrame");
            return;
        }
        auto& iToken{ *iTokenPtr };


        outputs::cudaStream.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::referenceTimeDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::referenceTimeNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::renderProductDataPtrs.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::renderProductPaths.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:action,flowControl");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data postprocess node to execute pipeline after the NewFrame event has been received");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, outputs::cudaStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda stream");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes for each newFrame event received");
        attr = iNode->getAttributeByToken(nodeObj, outputs::referenceTimeDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Reference time represented as a rational number : denominator");
        attr = iNode->getAttributeByToken(nodeObj, outputs::referenceTimeNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Reference time represented as a rational number : numerator");
        attr = iNode->getAttributeByToken(nodeObj, outputs::renderProductDataPtrs.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "HydraRenderProduct data pointer.");
        attr = iNode->getAttributeByToken(nodeObj, outputs::renderProductPaths.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render product path tokens.");
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
        sm_stateManagerOgnSdOnNewFrame.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && outputs.cudaStream.isValid()
            && outputs.exec.isValid()
            && outputs.referenceTimeDenominator.isValid()
            && outputs.referenceTimeNumerator.isValid()
            && outputs.renderProductDataPtrs.isValid()
            && outputs.renderProductPaths.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            outputs.cudaStream.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.referenceTimeDenominator.invalidateCachedPointer();
            outputs.referenceTimeNumerator.invalidateCachedPointer();
            outputs.renderProductDataPtrs.invalidateCachedPointer();
            outputs.renderProductPaths.invalidateCachedPointer();
            return;
        }
        outputs.renderProductDataPtrs.invalidateCachedPointer();
        outputs.renderProductPaths.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == outputs::cudaStream.m_token) {
                outputs.cudaStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::referenceTimeDenominator.m_token) {
                outputs.referenceTimeDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::referenceTimeNumerator.m_token) {
                outputs.referenceTimeNumerator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::renderProductDataPtrs.m_token) {
                outputs.renderProductDataPtrs.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::renderProductPaths.m_token) {
                outputs.renderProductPaths.invalidateCachedPointer();
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
        if( !outputs.cudaStream.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.referenceTimeDenominator.canVectorize()
            || !outputs.referenceTimeNumerator.canVectorize()
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
        if(token == outputs::cudaStream.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cudaStream.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::referenceTimeDenominator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.referenceTimeDenominator.setHandle(hdl);
            return;
        }
        if(token == outputs::referenceTimeNumerator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.referenceTimeNumerator.setHandle(hdl);
            return;
        }
        if(token == outputs::renderProductDataPtrs.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.renderProductDataPtrs.setHandle(hdl);
            return;
        }
        if(token == outputs::renderProductPaths.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.renderProductPaths.setHandle(hdl);
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
ogn::StateManager OgnSdOnNewFrameDatabase::sm_stateManagerOgnSdOnNewFrame;
std::tuple<int, int, int> OgnSdOnNewFrameDatabase::sm_generatorVersionOgnSdOnNewFrame{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdOnNewFrameDatabase::sm_targetVersionOgnSdOnNewFrame{std::make_tuple(2,184,5)};
}
using namespace IOgnSdOnNewFrame;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdOnNewFrame, OgnSdOnNewFrameDatabase> s_registration("omni.syntheticdata.SdOnNewFrame", 1, "omni.syntheticdata"); \
}
