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

namespace OgnSdRenderVarDisplayTextureAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
using renderVarDisplay_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderVarDisplay("inputs:renderVarDisplay", "token", kExtendedAttributeType_Regular);
}
namespace outputs
{
using cudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> cudaPtr("outputs:cudaPtr", "uint64", kExtendedAttributeType_Regular);
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using format_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> format("outputs:format", "uint64", kExtendedAttributeType_Regular);
using height_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> height("outputs:height", "uint", kExtendedAttributeType_Regular);
using referenceTimeDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> referenceTimeDenominator("outputs:referenceTimeDenominator", "uint64", kExtendedAttributeType_Regular);
using referenceTimeNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> referenceTimeNumerator("outputs:referenceTimeNumerator", "int64", kExtendedAttributeType_Regular);
using rpResourcePtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> rpResourcePtr("outputs:rpResourcePtr", "uint64", kExtendedAttributeType_Regular);
using width_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> width("outputs:width", "uint", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdRenderVarDisplayTextureAttributes;
namespace IOgnSdRenderVarDisplayTexture
{
// Synthetic Data node to expose texture resource of a visualization render variable
class OgnSdRenderVarDisplayTextureDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdRenderVarDisplayTexture.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdRenderVarDisplayTexture.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdRenderVarDisplayTexture.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdRenderVarDisplayTexture.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdRenderVarDisplayTexture;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdRenderVarDisplayTexture;
    static std::tuple<int, int, int>sm_targetVersionOgnSdRenderVarDisplayTexture;
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
        , renderVarDisplay{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderVarDisplay;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : cudaPtr{offset}
        , exec{offset,AttributeRole::eExecution}
        , format{offset}
        , height{offset}
        , referenceTimeDenominator{offset}
        , referenceTimeNumerator{offset}
        , rpResourcePtr{offset}
        , width{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> cudaPtr;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> format;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> height;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> referenceTimeDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> referenceTimeNumerator;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> rpResourcePtr;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> width;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdRenderVarDisplayTextureDatabase(NodeObj const& nodeObjParam)
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
    OgnSdRenderVarDisplayTextureDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdRenderVarDisplayTextureDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdRenderVarDisplayTextureDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::exec.m_token, inputs::renderResults.m_token, inputs::renderVarDisplay.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::cudaPtr.m_token, outputs::exec.m_token, outputs::format.m_token, outputs::height.m_token,
                    outputs::referenceTimeDenominator.m_token, outputs::referenceTimeNumerator.m_token, outputs::rpResourcePtr.m_token, outputs::width.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<1>(inputDataHandles0));
            inputs.renderVarDisplay.setContext(contextObj);
            inputs.renderVarDisplay.setHandle(std::get<2>(inputDataHandles0));
            outputs.cudaPtr.setContext(contextObj);
            outputs.cudaPtr.setHandle(std::get<0>(outputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<1>(outputDataHandles0));
            outputs.format.setContext(contextObj);
            outputs.format.setHandle(std::get<2>(outputDataHandles0));
            outputs.height.setContext(contextObj);
            outputs.height.setHandle(std::get<3>(outputDataHandles0));
            outputs.referenceTimeDenominator.setContext(contextObj);
            outputs.referenceTimeDenominator.setHandle(std::get<4>(outputDataHandles0));
            outputs.referenceTimeNumerator.setContext(contextObj);
            outputs.referenceTimeNumerator.setHandle(std::get<5>(outputDataHandles0));
            outputs.rpResourcePtr.setContext(contextObj);
            outputs.rpResourcePtr.setHandle(std::get<6>(outputDataHandles0));
            outputs.width.setContext(contextObj);
            outputs.width.setHandle(std::get<7>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdRenderVarDisplayTexture");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderVarDisplay.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::cudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::format.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::referenceTimeDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::referenceTimeNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rpResourcePtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::width.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:action,rendering,internal");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to expose texture resource of a visualization render variable");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render results pointer");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderVarDisplay.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the renderVar");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture CUDA pointer");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::format.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture format");
        attr = iNode->getAttributeByToken(nodeObj, outputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture height");
        attr = iNode->getAttributeByToken(nodeObj, outputs::referenceTimeDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Reference time represented as a rational number : denominator");
        attr = iNode->getAttributeByToken(nodeObj, outputs::referenceTimeNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Reference time represented as a rational number : numerator");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rpResourcePtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture RpResource pointer");
        attr = iNode->getAttributeByToken(nodeObj, outputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture width");
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
        sm_stateManagerOgnSdRenderVarDisplayTexture.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.renderResults.isValid()
            && inputs.renderVarDisplay.isValid()
            && outputs.cudaPtr.isValid()
            && outputs.exec.isValid()
            && outputs.format.isValid()
            && outputs.height.isValid()
            && outputs.referenceTimeDenominator.isValid()
            && outputs.referenceTimeNumerator.isValid()
            && outputs.rpResourcePtr.isValid()
            && outputs.width.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            inputs.renderVarDisplay.invalidateCachedPointer();
            outputs.cudaPtr.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.format.invalidateCachedPointer();
            outputs.height.invalidateCachedPointer();
            outputs.referenceTimeDenominator.invalidateCachedPointer();
            outputs.referenceTimeNumerator.invalidateCachedPointer();
            outputs.rpResourcePtr.invalidateCachedPointer();
            outputs.width.invalidateCachedPointer();
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
            if(attrib == inputs::renderVarDisplay.m_token) {
                inputs.renderVarDisplay.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cudaPtr.m_token) {
                outputs.cudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::format.m_token) {
                outputs.format.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::height.m_token) {
                outputs.height.invalidateCachedPointer();
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
            if(attrib == outputs::rpResourcePtr.m_token) {
                outputs.rpResourcePtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::width.m_token) {
                outputs.width.invalidateCachedPointer();
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
            || !inputs.renderVarDisplay.canVectorize()
            || !outputs.cudaPtr.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.format.canVectorize()
            || !outputs.height.canVectorize()
            || !outputs.referenceTimeDenominator.canVectorize()
            || !outputs.referenceTimeNumerator.canVectorize()
            || !outputs.rpResourcePtr.canVectorize()
            || !outputs.width.canVectorize()
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
        if(token == inputs::renderVarDisplay.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderVarDisplay.setHandle(hdl);
            return;
        }
        if(token == outputs::cudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::format.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.format.setHandle(hdl);
            return;
        }
        if(token == outputs::height.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.height.setHandle(hdl);
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
        if(token == outputs::rpResourcePtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rpResourcePtr.setHandle(hdl);
            return;
        }
        if(token == outputs::width.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.width.setHandle(hdl);
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
ogn::StateManager OgnSdRenderVarDisplayTextureDatabase::sm_stateManagerOgnSdRenderVarDisplayTexture;
std::tuple<int, int, int> OgnSdRenderVarDisplayTextureDatabase::sm_generatorVersionOgnSdRenderVarDisplayTexture{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdRenderVarDisplayTextureDatabase::sm_targetVersionOgnSdRenderVarDisplayTexture{std::make_tuple(2,184,5)};
}
using namespace IOgnSdRenderVarDisplayTexture;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdRenderVarDisplayTexture, OgnSdRenderVarDisplayTextureDatabase> s_registration("omni.syntheticdata.SdRenderVarDisplayTexture", 2, "omni.syntheticdata"); \
}
