#pragma once

#include <omni/graph/core/ogn/UsdTypes.h>
using namespace pxr;

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
#include <omni/graph/core/tuple.h>
#include <omni/graph/image/unstable/ComputeParamsBuilder.h>

namespace OgnSdPostCompRenderVarTexturesAttributes
{
namespace inputs
{
using cudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaPtr("inputs:cudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using format_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> format("inputs:format", "uint64", kExtendedAttributeType_Regular, 0);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using height_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> height("inputs:height", "uint", kExtendedAttributeType_Regular, 0);
using mode_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> mode("inputs:mode", "token", kExtendedAttributeType_Regular);
using parameters_t = const pxr::GfVec3f&;
ogn::AttributeInitializer<const pxr::GfVec3f, ogn::kOgnInput> parameters("inputs:parameters", "float3", kExtendedAttributeType_Regular, {0.0f,0.0f,0.0f});
using renderVar_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderVar("inputs:renderVar", "token", kExtendedAttributeType_Regular);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using width_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> width("inputs:width", "uint", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace OgnSdPostCompRenderVarTexturesAttributes;
namespace IOgnSdPostCompRenderVarTextures
{
// Synthetic Data node to compose a front renderVar texture into a back renderVar texture
class OgnSdPostCompRenderVarTexturesDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken line;
        NameToken grid;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdPostCompRenderVarTextures.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdPostCompRenderVarTextures.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdPostCompRenderVarTextures.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdPostCompRenderVarTextures.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdPostCompRenderVarTextures;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdPostCompRenderVarTextures;
    static std::tuple<int, int, int>sm_targetVersionOgnSdPostCompRenderVarTextures;
    static constexpr size_t staticAttributeCount = 11;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : cudaPtr{offset}
        , format{offset}
        , gpu{offset}
        , height{offset}
        , mode{offset}
        , parameters{offset}
        , renderVar{offset}
        , rp{offset}
        , width{offset}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> format;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> height;
        ogn::SimpleInput<const NameToken,ogn::kCpu> mode;
        ogn::SimpleInput<const pxr::GfVec3f,ogn::kCpu> parameters;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderVar;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> width;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdPostCompRenderVarTexturesDatabase(NodeObj const& nodeObjParam)
    : OmniGraphDatabase()
    , inputs{m_offset.index}
    {
        GraphContextObj const* contexts = nullptr;
        NodeObj const* nodes = nullptr;
        size_t handleCount = nodeObjParam.iNode->getAutoInstances(nodeObjParam, contexts, nodes);
        _ctor(contexts, nodes, handleCount);
        _init();
    }

    CARB_DEPRECATED("Passing the graph context to the temporary stack allocated database is not necessary anymore: you can safely remove this parameter")
    OgnSdPostCompRenderVarTexturesDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdPostCompRenderVarTexturesDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdPostCompRenderVarTexturesDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
    : OmniGraphDatabase()
    , inputs{m_offset.index}
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::cudaPtr.m_token, inputs::format.m_token, inputs::gpu.m_token, inputs::height.m_token,
                    inputs::mode.m_token, inputs::parameters.m_token, inputs::renderVar.m_token, inputs::rp.m_token,
                    inputs::width.m_token
                )
            , kAccordingToContextIndex);
            inputs.cudaPtr.setContext(contextObj);
            inputs.cudaPtr.setHandle(std::get<0>(inputDataHandles0));
            inputs.format.setContext(contextObj);
            inputs.format.setHandle(std::get<1>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<2>(inputDataHandles0));
            inputs.height.setContext(contextObj);
            inputs.height.setHandle(std::get<3>(inputDataHandles0));
            inputs.mode.setContext(contextObj);
            inputs.mode.setHandle(std::get<4>(inputDataHandles0));
            inputs.parameters.setContext(contextObj);
            inputs.parameters.setHandle(std::get<5>(inputDataHandles0));
            inputs.renderVar.setContext(contextObj);
            inputs.renderVar.setHandle(std::get<6>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<7>(inputDataHandles0));
            inputs.width.setContext(contextObj);
            inputs.width.setHandle(std::get<8>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdPostCompRenderVarTextures");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdPostCompRenderVarTexturesDatabase::tokens.line = iToken.getHandle("line");
        OgnSdPostCompRenderVarTexturesDatabase::tokens.grid = iToken.getHandle("grid");

        static omni::fabric::Token inputs_mode_token {"line"};
        inputs::mode.setDefault(inputs_mode_token.asTokenC());
        static omni::fabric::Token inputs_renderVar_token {"LdrColor"};
        inputs::renderVar.setDefault(inputs_renderVar_token.asTokenC());
        inputs::cudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::format.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::mode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::parameters.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderVar.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::width.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"line\", \"grid\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,rendering,internal");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to compose a front renderVar texture into a back renderVar texture");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Front texture CUDA pointer");
        attr = iNode->getAttributeByToken(nodeObj, inputs::format.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Front texture format");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Front texture height");
        attr = iNode->getAttributeByToken(nodeObj, inputs::mode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Mode : grid, line");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"line\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::parameters.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Parameters");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[0, 0, 0]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderVar.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the back RenderVar");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"LdrColor\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Front texture width");
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
        sm_stateManagerOgnSdPostCompRenderVarTextures.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cudaPtr.isValid()
            && inputs.format.isValid()
            && inputs.gpu.isValid()
            && inputs.height.isValid()
            && inputs.mode.isValid()
            && inputs.parameters.isValid()
            && inputs.renderVar.isValid()
            && inputs.rp.isValid()
            && inputs.width.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cudaPtr.invalidateCachedPointer();
            inputs.format.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.height.invalidateCachedPointer();
            inputs.mode.invalidateCachedPointer();
            inputs.parameters.invalidateCachedPointer();
            inputs.renderVar.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.width.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cudaPtr.m_token) {
                inputs.cudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::format.m_token) {
                inputs.format.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::height.m_token) {
                inputs.height.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::mode.m_token) {
                inputs.mode.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::parameters.m_token) {
                inputs.parameters.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderVar.m_token) {
                inputs.renderVar.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::width.m_token) {
                inputs.width.invalidateCachedPointer();
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
        if( !inputs.cudaPtr.canVectorize()
            || !inputs.format.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.height.canVectorize()
            || !inputs.mode.canVectorize()
            || !inputs.parameters.canVectorize()
            || !inputs.renderVar.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.width.canVectorize()
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
        if(token == inputs::cudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::format.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.format.setHandle(hdl);
            return;
        }
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::height.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.height.setHandle(hdl);
            return;
        }
        if(token == inputs::mode.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.mode.setHandle(hdl);
            return;
        }
        if(token == inputs::parameters.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.parameters.setHandle(hdl);
            return;
        }
        if(token == inputs::renderVar.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderVar.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == inputs::width.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.width.setHandle(hdl);
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
        auto variable = const_cast<OgnSdPostCompRenderVarTexturesDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostCompRenderVarTexturesDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostCompRenderVarTexturesDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostCompRenderVarTexturesDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdPostCompRenderVarTexturesDatabase::sm_stateManagerOgnSdPostCompRenderVarTextures;
std::tuple<int, int, int> OgnSdPostCompRenderVarTexturesDatabase::sm_generatorVersionOgnSdPostCompRenderVarTextures{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdPostCompRenderVarTexturesDatabase::sm_targetVersionOgnSdPostCompRenderVarTextures{std::make_tuple(2,184,5)};
OgnSdPostCompRenderVarTexturesDatabase::TokenManager OgnSdPostCompRenderVarTexturesDatabase::tokens;
}
using namespace IOgnSdPostCompRenderVarTextures;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdPostCompRenderVarTextures, OgnSdPostCompRenderVarTexturesDatabase> s_registration("omni.syntheticdata.SdPostCompRenderVarTextures", 1, "omni.syntheticdata"); \
}
