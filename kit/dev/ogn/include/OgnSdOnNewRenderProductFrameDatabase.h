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

namespace OgnSdOnNewRenderProductFrameAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using renderProductDataPtrs_t = const ogn::const_array<uint64_t>&;
ogn::AttributeInitializer<const uint64_t*, ogn::kOgnInput> renderProductDataPtrs("inputs:renderProductDataPtrs", "uint64[]", kExtendedAttributeType_Regular, nullptr, 0);
using renderProductPath_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderProductPath("inputs:renderProductPath", "token", kExtendedAttributeType_Regular);
using renderProductPaths_t = const ogn::const_array<NameToken>&;
ogn::AttributeInitializer<const NameToken*, ogn::kOgnInput> renderProductPaths("inputs:renderProductPaths", "token[]", kExtendedAttributeType_Regular, nullptr, 0);
}
namespace outputs
{
using cudaStream_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> cudaStream("outputs:cudaStream", "uint64", kExtendedAttributeType_Regular);
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using renderProductPath_t = NameToken&;
ogn::AttributeInitializer<NameToken, ogn::kOgnOutput> renderProductPath("outputs:renderProductPath", "token", kExtendedAttributeType_Regular);
using renderResults_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> renderResults("outputs:renderResults", "uint64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdOnNewRenderProductFrameAttributes;
namespace IOgnSdOnNewRenderProductFrame
{
// Synthetic Data postprocess node to execute pipeline after the NewFrame event has
// been received on the given renderProduct
class OgnSdOnNewRenderProductFrameDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdOnNewRenderProductFrame.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdOnNewRenderProductFrame.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdOnNewRenderProductFrame.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdOnNewRenderProductFrame.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdOnNewRenderProductFrame;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdOnNewRenderProductFrame;
    static std::tuple<int, int, int>sm_targetVersionOgnSdOnNewRenderProductFrame;
    static constexpr size_t staticAttributeCount = 10;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , renderProductDataPtrs{offset}
        , renderProductPath{offset}
        , renderProductPaths{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::ArrayInput<const uint64_t,ogn::kCpu> renderProductDataPtrs;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderProductPath;
        ogn::ArrayInput<const NameToken,ogn::kCpu> renderProductPaths;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : cudaStream{offset}
        , exec{offset,AttributeRole::eExecution}
        , renderProductPath{offset}
        , renderResults{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> cudaStream;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<NameToken,ogn::kCpu> renderProductPath;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> renderResults;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdOnNewRenderProductFrameDatabase(NodeObj const& nodeObjParam)
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
    OgnSdOnNewRenderProductFrameDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdOnNewRenderProductFrameDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdOnNewRenderProductFrameDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::exec.m_token, inputs::renderProductDataPtrs.m_token, inputs::renderProductPath.m_token, inputs::renderProductPaths.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::cudaStream.m_token, outputs::exec.m_token, outputs::renderProductPath.m_token, outputs::renderResults.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.renderProductDataPtrs.setContext(contextObj);
            inputs.renderProductDataPtrs.setHandle(std::get<1>(inputDataHandles0));
            inputs.renderProductPath.setContext(contextObj);
            inputs.renderProductPath.setHandle(std::get<2>(inputDataHandles0));
            inputs.renderProductPaths.setContext(contextObj);
            inputs.renderProductPaths.setHandle(std::get<3>(inputDataHandles0));
            outputs.cudaStream.setContext(contextObj);
            outputs.cudaStream.setHandle(std::get<0>(outputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<1>(outputDataHandles0));
            outputs.renderProductPath.setContext(contextObj);
            outputs.renderProductPath.setHandle(std::get<2>(outputDataHandles0));
            outputs.renderResults.setContext(contextObj);
            outputs.renderResults.setHandle(std::get<3>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdOnNewRenderProductFrame");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderProductDataPtrs.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderProductPath.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderProductPaths.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::cudaStream.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::renderProductPath.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:action,flowControl");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data postprocess node to execute pipeline after the NewFrame event has been received on the given renderProduct");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes for each newFrame event received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Received");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderProductDataPtrs.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "HydraRenderProduct data pointers.");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderProductPath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Path of the renderProduct to wait for being rendered");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderProductPaths.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render product path tokens.");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cudaStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda stream");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes for each newFrame event received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Received");
        attr = iNode->getAttributeByToken(nodeObj, outputs::renderProductPath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Path of the renderProduct to wait for being rendered");
        attr = iNode->getAttributeByToken(nodeObj, outputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render results");
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
        sm_stateManagerOgnSdOnNewRenderProductFrame.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.renderProductDataPtrs.isValid()
            && inputs.renderProductPath.isValid()
            && inputs.renderProductPaths.isValid()
            && outputs.cudaStream.isValid()
            && outputs.exec.isValid()
            && outputs.renderProductPath.isValid()
            && outputs.renderResults.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.renderProductDataPtrs.invalidateCachedPointer();
            inputs.renderProductPath.invalidateCachedPointer();
            inputs.renderProductPaths.invalidateCachedPointer();
            outputs.cudaStream.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.renderProductPath.invalidateCachedPointer();
            outputs.renderResults.invalidateCachedPointer();
            return;
        }
        inputs.renderProductDataPtrs.invalidateCachedPointer();
        inputs.renderProductPaths.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderProductDataPtrs.m_token) {
                inputs.renderProductDataPtrs.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderProductPath.m_token) {
                inputs.renderProductPath.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderProductPaths.m_token) {
                inputs.renderProductPaths.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cudaStream.m_token) {
                outputs.cudaStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::renderProductPath.m_token) {
                outputs.renderProductPath.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::renderResults.m_token) {
                outputs.renderResults.invalidateCachedPointer();
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
            || !inputs.renderProductPath.canVectorize()
            || !outputs.cudaStream.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.renderProductPath.canVectorize()
            || !outputs.renderResults.canVectorize()
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
        if(token == inputs::renderProductDataPtrs.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderProductDataPtrs.setHandle(hdl);
            return;
        }
        if(token == inputs::renderProductPath.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderProductPath.setHandle(hdl);
            return;
        }
        if(token == inputs::renderProductPaths.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderProductPaths.setHandle(hdl);
            return;
        }
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
        if(token == outputs::renderProductPath.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.renderProductPath.setHandle(hdl);
            return;
        }
        if(token == outputs::renderResults.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.renderResults.setHandle(hdl);
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
ogn::StateManager OgnSdOnNewRenderProductFrameDatabase::sm_stateManagerOgnSdOnNewRenderProductFrame;
std::tuple<int, int, int> OgnSdOnNewRenderProductFrameDatabase::sm_generatorVersionOgnSdOnNewRenderProductFrame{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdOnNewRenderProductFrameDatabase::sm_targetVersionOgnSdOnNewRenderProductFrame{std::make_tuple(2,184,5)};
}
using namespace IOgnSdOnNewRenderProductFrame;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdOnNewRenderProductFrame, OgnSdOnNewRenderProductFrameDatabase> s_registration("omni.syntheticdata.SdOnNewRenderProductFrame", 1, "omni.syntheticdata"); \
}
