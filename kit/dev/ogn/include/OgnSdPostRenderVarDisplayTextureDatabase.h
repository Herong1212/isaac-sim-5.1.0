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
#include <array>
#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/ArrayAttribute.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>
#include <omni/graph/core/tuple.h>
#include <omni/graph/image/unstable/ComputeParamsBuilder.h>

namespace OgnSdPostRenderVarDisplayTextureAttributes
{
namespace inputs
{
using cameraFisheyeParams_t = const ogn::const_array<float>&;
ogn::AttributeInitializer<const float*, ogn::kOgnInput> cameraFisheyeParams("inputs:cameraFisheyeParams", "float[]", kExtendedAttributeType_Regular, nullptr, 0);
using cameraModel_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> cameraModel("inputs:cameraModel", "int", kExtendedAttributeType_Regular, 0);
using cameraNearFar_t = const pxr::GfVec2f&;
ogn::AttributeInitializer<const pxr::GfVec2f, ogn::kOgnInput> cameraNearFar("inputs:cameraNearFar", "float2", kExtendedAttributeType_Regular, {0.0f,0.0f});
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using instanceMapSDCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> instanceMapSDCudaPtr("inputs:instanceMapSDCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using instanceMappingInfoSDPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> instanceMappingInfoSDPtr("inputs:instanceMappingInfoSDPtr", "uint64", kExtendedAttributeType_Regular, 0);
using metersPerSceneUnit_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> metersPerSceneUnit("inputs:metersPerSceneUnit", "float", kExtendedAttributeType_Regular, 0.0f);
using mode_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> mode("inputs:mode", "token", kExtendedAttributeType_Regular);
using parameters_t = const pxr::GfVec4f&;
ogn::AttributeInitializer<const pxr::GfVec4f, ogn::kOgnInput> parameters("inputs:parameters", "float4", kExtendedAttributeType_Regular, {0.0f,5.0f,0.33f,0.27f});
using renderVar_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderVar("inputs:renderVar", "token", kExtendedAttributeType_Regular);
using renderVarDisplay_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderVarDisplay("inputs:renderVarDisplay", "token", kExtendedAttributeType_Regular);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using sdDisplayHeight_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> sdDisplayHeight("inputs:sdDisplayHeight", "uint", kExtendedAttributeType_Regular, 0);
using sdDisplayWidth_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> sdDisplayWidth("inputs:sdDisplayWidth", "uint", kExtendedAttributeType_Regular, 0);
using sdSemBBox3dCamCornersCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdSemBBox3dCamCornersCudaPtr("inputs:sdSemBBox3dCamCornersCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using sdSemBBox3dCamExtentCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdSemBBox3dCamExtentCudaPtr("inputs:sdSemBBox3dCamExtentCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using sdSemBBoxExtentCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdSemBBoxExtentCudaPtr("inputs:sdSemBBoxExtentCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using sdSemBBoxInfosCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdSemBBoxInfosCudaPtr("inputs:sdSemBBoxInfosCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using semanticLabelTokenSDCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticLabelTokenSDCudaPtr("inputs:semanticLabelTokenSDCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using semanticMapSDCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticMapSDCudaPtr("inputs:semanticMapSDCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using semanticPrimTokenSDCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticPrimTokenSDCudaPtr("inputs:semanticPrimTokenSDCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using semanticWorldTransformSDCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticWorldTransformSDCudaPtr("inputs:semanticWorldTransformSDCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
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
using renderVarDisplay_t = NameToken&;
ogn::AttributeInitializer<NameToken, ogn::kOgnOutput> renderVarDisplay("outputs:renderVarDisplay", "token", kExtendedAttributeType_Regular);
using width_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> width("outputs:width", "uint", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdPostRenderVarDisplayTextureAttributes;
namespace IOgnSdPostRenderVarDisplayTexture
{
// Synthetic Data node to copy the input aov texture into the corresponding visualization
// texture
class OgnSdPostRenderVarDisplayTextureDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken LdrColorSD;
        NameToken Camera3dPositionSD;
        NameToken DistanceToImagePlaneSD;
        NameToken DistanceToCameraSD;
        NameToken InstanceSegmentationSD;
        NameToken SemanticSegmentationSD;
        NameToken NormalSD;
        NameToken TargetMotionSD;
        NameToken BoundingBox2DTightSD;
        NameToken BoundingBox2DLooseSD;
        NameToken BoundingBox3DSD;
        NameToken OcclusionSD;
        NameToken TruncationSD;
        NameToken CrossCorrespondenceSD;
        NameToken SemanticBoundingBox2DExtentTightSD;
        NameToken SemanticBoundingBox2DInfosTightSD;
        NameToken SemanticBoundingBox2DExtentLooseSD;
        NameToken SemanticBoundingBox2DInfosLooseSD;
        NameToken SemanticBoundingBox3DExtentSD;
        NameToken SemanticBoundingBox3DInfosSD;
        NameToken SemanticBoundingBox3DCamCornersSD;
        NameToken SemanticBoundingBox3DDisplayAxesSD;
        NameToken autoMode;
        NameToken colorMode;
        NameToken scaled3dVectorMode;
        NameToken clippedValueMode;
        NameToken normalized3dVectorMode;
        NameToken segmentationMapMode;
        NameToken instanceMapMode;
        NameToken semanticPathMode;
        NameToken semanticLabelMode;
        NameToken semanticBoundingBox2dMode;
        NameToken rawBoundingBox2dMode;
        NameToken semanticProjBoundingBox3dMode;
        NameToken semanticBoundingBox3dMode;
        NameToken rawBoundingBox3dMode;
        NameToken pinhole;
        NameToken perspective;
        NameToken orthographic;
        NameToken fisheyePolynomial;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdPostRenderVarDisplayTexture.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdPostRenderVarDisplayTexture.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdPostRenderVarDisplayTexture.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdPostRenderVarDisplayTexture.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdPostRenderVarDisplayTexture;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdPostRenderVarDisplayTexture;
    static std::tuple<int, int, int>sm_targetVersionOgnSdPostRenderVarDisplayTexture;
    static constexpr size_t staticAttributeCount = 31;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : cameraFisheyeParams{offset}
        , cameraModel{offset}
        , cameraNearFar{offset}
        , exec{offset,AttributeRole::eExecution}
        , gpu{offset}
        , instanceMapSDCudaPtr{offset}
        , instanceMappingInfoSDPtr{offset}
        , metersPerSceneUnit{offset}
        , mode{offset}
        , parameters{offset}
        , renderVar{offset}
        , renderVarDisplay{offset}
        , rp{offset}
        , sdDisplayHeight{offset}
        , sdDisplayWidth{offset}
        , sdSemBBox3dCamCornersCudaPtr{offset}
        , sdSemBBox3dCamExtentCudaPtr{offset}
        , sdSemBBoxExtentCudaPtr{offset}
        , sdSemBBoxInfosCudaPtr{offset}
        , semanticLabelTokenSDCudaPtr{offset}
        , semanticMapSDCudaPtr{offset}
        , semanticPrimTokenSDCudaPtr{offset}
        , semanticWorldTransformSDCudaPtr{offset}
        {}
        ogn::ArrayInput<const float,ogn::kCpu> cameraFisheyeParams;
        ogn::SimpleInput<const int,ogn::kCpu> cameraModel;
        ogn::SimpleInput<const pxr::GfVec2f,ogn::kCpu> cameraNearFar;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> instanceMapSDCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> instanceMappingInfoSDPtr;
        ogn::SimpleInput<const float,ogn::kCpu> metersPerSceneUnit;
        ogn::SimpleInput<const NameToken,ogn::kCpu> mode;
        ogn::SimpleInput<const pxr::GfVec4f,ogn::kCpu> parameters;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderVar;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderVarDisplay;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> sdDisplayHeight;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> sdDisplayWidth;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdSemBBox3dCamCornersCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdSemBBox3dCamExtentCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdSemBBoxExtentCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdSemBBoxInfosCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticLabelTokenSDCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticMapSDCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticPrimTokenSDCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticWorldTransformSDCudaPtr;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : cudaPtr{offset}
        , exec{offset,AttributeRole::eExecution}
        , format{offset}
        , height{offset}
        , renderVarDisplay{offset}
        , width{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> cudaPtr;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> format;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> height;
        ogn::SimpleOutput<NameToken,ogn::kCpu> renderVarDisplay;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> width;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdPostRenderVarDisplayTextureDatabase(NodeObj const& nodeObjParam)
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
    OgnSdPostRenderVarDisplayTextureDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdPostRenderVarDisplayTextureDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdPostRenderVarDisplayTextureDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::cameraFisheyeParams.m_token, inputs::cameraModel.m_token, inputs::cameraNearFar.m_token, inputs::exec.m_token,
                    inputs::gpu.m_token, inputs::instanceMapSDCudaPtr.m_token, inputs::instanceMappingInfoSDPtr.m_token, inputs::metersPerSceneUnit.m_token,
                    inputs::mode.m_token, inputs::parameters.m_token, inputs::renderVar.m_token, inputs::renderVarDisplay.m_token,
                    inputs::rp.m_token, inputs::sdDisplayHeight.m_token, inputs::sdDisplayWidth.m_token, inputs::sdSemBBox3dCamCornersCudaPtr.m_token,
                    inputs::sdSemBBox3dCamExtentCudaPtr.m_token, inputs::sdSemBBoxExtentCudaPtr.m_token, inputs::sdSemBBoxInfosCudaPtr.m_token, inputs::semanticLabelTokenSDCudaPtr.m_token,
                    inputs::semanticMapSDCudaPtr.m_token, inputs::semanticPrimTokenSDCudaPtr.m_token, inputs::semanticWorldTransformSDCudaPtr.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::cudaPtr.m_token, outputs::exec.m_token, outputs::format.m_token, outputs::height.m_token,
                    outputs::renderVarDisplay.m_token, outputs::width.m_token
                )
            , kAccordingToContextIndex);
            inputs.cameraFisheyeParams.setContext(contextObj);
            inputs.cameraFisheyeParams.setHandle(std::get<0>(inputDataHandles0));
            inputs.cameraModel.setContext(contextObj);
            inputs.cameraModel.setHandle(std::get<1>(inputDataHandles0));
            inputs.cameraNearFar.setContext(contextObj);
            inputs.cameraNearFar.setHandle(std::get<2>(inputDataHandles0));
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<3>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<4>(inputDataHandles0));
            inputs.instanceMapSDCudaPtr.setContext(contextObj);
            inputs.instanceMapSDCudaPtr.setHandle(std::get<5>(inputDataHandles0));
            inputs.instanceMappingInfoSDPtr.setContext(contextObj);
            inputs.instanceMappingInfoSDPtr.setHandle(std::get<6>(inputDataHandles0));
            inputs.metersPerSceneUnit.setContext(contextObj);
            inputs.metersPerSceneUnit.setHandle(std::get<7>(inputDataHandles0));
            inputs.mode.setContext(contextObj);
            inputs.mode.setHandle(std::get<8>(inputDataHandles0));
            inputs.parameters.setContext(contextObj);
            inputs.parameters.setHandle(std::get<9>(inputDataHandles0));
            inputs.renderVar.setContext(contextObj);
            inputs.renderVar.setHandle(std::get<10>(inputDataHandles0));
            inputs.renderVarDisplay.setContext(contextObj);
            inputs.renderVarDisplay.setHandle(std::get<11>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<12>(inputDataHandles0));
            inputs.sdDisplayHeight.setContext(contextObj);
            inputs.sdDisplayHeight.setHandle(std::get<13>(inputDataHandles0));
            inputs.sdDisplayWidth.setContext(contextObj);
            inputs.sdDisplayWidth.setHandle(std::get<14>(inputDataHandles0));
            inputs.sdSemBBox3dCamCornersCudaPtr.setContext(contextObj);
            inputs.sdSemBBox3dCamCornersCudaPtr.setHandle(std::get<15>(inputDataHandles0));
            inputs.sdSemBBox3dCamExtentCudaPtr.setContext(contextObj);
            inputs.sdSemBBox3dCamExtentCudaPtr.setHandle(std::get<16>(inputDataHandles0));
            inputs.sdSemBBoxExtentCudaPtr.setContext(contextObj);
            inputs.sdSemBBoxExtentCudaPtr.setHandle(std::get<17>(inputDataHandles0));
            inputs.sdSemBBoxInfosCudaPtr.setContext(contextObj);
            inputs.sdSemBBoxInfosCudaPtr.setHandle(std::get<18>(inputDataHandles0));
            inputs.semanticLabelTokenSDCudaPtr.setContext(contextObj);
            inputs.semanticLabelTokenSDCudaPtr.setHandle(std::get<19>(inputDataHandles0));
            inputs.semanticMapSDCudaPtr.setContext(contextObj);
            inputs.semanticMapSDCudaPtr.setHandle(std::get<20>(inputDataHandles0));
            inputs.semanticPrimTokenSDCudaPtr.setContext(contextObj);
            inputs.semanticPrimTokenSDCudaPtr.setHandle(std::get<21>(inputDataHandles0));
            inputs.semanticWorldTransformSDCudaPtr.setContext(contextObj);
            inputs.semanticWorldTransformSDCudaPtr.setHandle(std::get<22>(inputDataHandles0));
            outputs.cudaPtr.setContext(contextObj);
            outputs.cudaPtr.setHandle(std::get<0>(outputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<1>(outputDataHandles0));
            outputs.format.setContext(contextObj);
            outputs.format.setHandle(std::get<2>(outputDataHandles0));
            outputs.height.setContext(contextObj);
            outputs.height.setHandle(std::get<3>(outputDataHandles0));
            outputs.renderVarDisplay.setContext(contextObj);
            outputs.renderVarDisplay.setHandle(std::get<4>(outputDataHandles0));
            outputs.width.setContext(contextObj);
            outputs.width.setHandle(std::get<5>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdPostRenderVarDisplayTexture");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.LdrColorSD = iToken.getHandle("LdrColorSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.Camera3dPositionSD = iToken.getHandle("Camera3dPositionSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.DistanceToImagePlaneSD = iToken.getHandle("DistanceToImagePlaneSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.DistanceToCameraSD = iToken.getHandle("DistanceToCameraSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.InstanceSegmentationSD = iToken.getHandle("InstanceSegmentationSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.SemanticSegmentationSD = iToken.getHandle("SemanticSegmentationSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.NormalSD = iToken.getHandle("NormalSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.TargetMotionSD = iToken.getHandle("TargetMotionSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.BoundingBox2DTightSD = iToken.getHandle("BoundingBox2DTightSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.BoundingBox2DLooseSD = iToken.getHandle("BoundingBox2DLooseSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.BoundingBox3DSD = iToken.getHandle("BoundingBox3DSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.OcclusionSD = iToken.getHandle("OcclusionSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.TruncationSD = iToken.getHandle("TruncationSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.CrossCorrespondenceSD = iToken.getHandle("CrossCorrespondenceSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.SemanticBoundingBox2DExtentTightSD = iToken.getHandle("SemanticBoundingBox2DExtentTightSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.SemanticBoundingBox2DInfosTightSD = iToken.getHandle("SemanticBoundingBox2DInfosTightSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.SemanticBoundingBox2DExtentLooseSD = iToken.getHandle("SemanticBoundingBox2DExtentLooseSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.SemanticBoundingBox2DInfosLooseSD = iToken.getHandle("SemanticBoundingBox2DInfosLooseSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.SemanticBoundingBox3DExtentSD = iToken.getHandle("SemanticBoundingBox3DExtentSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.SemanticBoundingBox3DInfosSD = iToken.getHandle("SemanticBoundingBox3DInfosSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.SemanticBoundingBox3DCamCornersSD = iToken.getHandle("SemanticBoundingBox3DCamCornersSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.SemanticBoundingBox3DDisplayAxesSD = iToken.getHandle("SemanticBoundingBox3DDisplayAxesSD");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.autoMode = iToken.getHandle("autoMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.colorMode = iToken.getHandle("colorMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.scaled3dVectorMode = iToken.getHandle("scaled3dVectorMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.clippedValueMode = iToken.getHandle("clippedValueMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.normalized3dVectorMode = iToken.getHandle("normalized3dVectorMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.segmentationMapMode = iToken.getHandle("segmentationMapMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.instanceMapMode = iToken.getHandle("instanceMapMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.semanticPathMode = iToken.getHandle("semanticPathMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.semanticLabelMode = iToken.getHandle("semanticLabelMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.semanticBoundingBox2dMode = iToken.getHandle("semanticBoundingBox2dMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.rawBoundingBox2dMode = iToken.getHandle("rawBoundingBox2dMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.semanticProjBoundingBox3dMode = iToken.getHandle("semanticProjBoundingBox3dMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.semanticBoundingBox3dMode = iToken.getHandle("semanticBoundingBox3dMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.rawBoundingBox3dMode = iToken.getHandle("rawBoundingBox3dMode");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.pinhole = iToken.getHandle("pinhole");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.perspective = iToken.getHandle("perspective");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.orthographic = iToken.getHandle("orthographic");
        OgnSdPostRenderVarDisplayTextureDatabase::tokens.fisheyePolynomial = iToken.getHandle("fisheyePolynomial");

        static omni::fabric::Token inputs_mode_token {"autoMode"};
        inputs::mode.setDefault(inputs_mode_token.asTokenC());
        inputs::cameraFisheyeParams.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraModel.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraNearFar.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::instanceMapSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::instanceMappingInfoSDPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::metersPerSceneUnit.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::mode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::parameters.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderVar.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderVarDisplay.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdDisplayHeight.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdDisplayWidth.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdSemBBox3dCamCornersCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdSemBBox3dCamExtentCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdSemBBoxExtentCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdSemBBoxInfosCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticLabelTokenSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticMapSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticPrimTokenSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticWorldTransformSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::cudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::format.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::renderVarDisplay.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::width.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"LdrColorSD\", \"Camera3dPositionSD\", \"DistanceToImagePlaneSD\", \"DistanceToCameraSD\", \"InstanceSegmentationSD\", \"SemanticSegmentationSD\", \"NormalSD\", \"TargetMotionSD\", \"BoundingBox2DTightSD\", \"BoundingBox2DLooseSD\", \"BoundingBox3DSD\", \"OcclusionSD\", \"TruncationSD\", \"CrossCorrespondenceSD\", \"SemanticBoundingBox2DExtentTightSD\", \"SemanticBoundingBox2DInfosTightSD\", \"SemanticBoundingBox2DExtentLooseSD\", \"SemanticBoundingBox2DInfosLooseSD\", \"SemanticBoundingBox3DExtentSD\", \"SemanticBoundingBox3DInfosSD\", \"SemanticBoundingBox3DCamCornersSD\", \"SemanticBoundingBox3DDisplayAxesSD\", \"autoMode\", \"colorMode\", \"scaled3dVectorMode\", \"clippedValueMode\", \"normalized3dVectorMode\", \"segmentationMapMode\", \"instanceMapMode\", \"semanticPathMode\", \"semanticLabelMode\", \"semanticBoundingBox2dMode\", \"rawBoundingBox2dMode\", \"semanticProjBoundingBox3dMode\", \"semanticBoundingBox3dMode\", \"rawBoundingBox3dMode\", \"pinhole\", \"perspective\", \"orthographic\", \"fisheyePolynomial\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,rendering,internal");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to copy the input aov texture into the corresponding visualization texture");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraFisheyeParams.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera fisheye projection parameters");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraModel.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera model (pinhole or fisheye models)");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraNearFar.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera near/far clipping range");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::instanceMapSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint16_t buffer pointer of size numInstances containing the instance parent semantic index");
        attr = iNode->getAttributeByToken(nodeObj, inputs::instanceMappingInfoSDPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::metersPerSceneUnit.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Scene units to meters scale");
        attr = iNode->getAttributeByToken(nodeObj, inputs::mode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display mode");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"autoMode\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::parameters.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display parameters");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[0.0, 5.0, 0.33, 0.27]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderVar.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the input RenderVar to display");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderVarDisplay.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the output display RenderVar");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdDisplayHeight.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Visualization texture Height");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdDisplayWidth.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Visualization texture width");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdSemBBox3dCamCornersCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing the projection of the 3d bounding boxes on the camera plane represented as a float3=(u,v,z,a) for each bounding box corners");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdSemBBox3dCamExtentCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing the 2d extent of the 3d bounding boxes on the camera plane represented as a float6=(u_min,u_max,v_min,v_max,z_min,z_max)");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdSemBBoxExtentCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing the extent of the bounding boxes as a float4=(u_min,v_min,u_max,v_max) for 2D or a float6=(xmin,ymin,zmin,xmax,ymax,zmax) in object space for 3D");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdSemBBoxInfosCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing valid bounding boxes infos");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticLabelTokenSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint64_t buffer pointer of size numSemantics containing the semantic label token");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticMapSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint16_t buffer pointer of size numSemantics containing the semantic parent semantic index");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticPrimTokenSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint64_t buffer pointer of size numSemantics containing the semantic path token");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticWorldTransformSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda float44 buffer pointer of size numSemantics containing the world semantic transform");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture CUDA pointer");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::format.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture format");
        attr = iNode->getAttributeByToken(nodeObj, outputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture height");
        attr = iNode->getAttributeByToken(nodeObj, outputs::renderVarDisplay.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the output display RenderVar");
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
        sm_stateManagerOgnSdPostRenderVarDisplayTexture.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cameraFisheyeParams.isValid()
            && inputs.cameraModel.isValid()
            && inputs.cameraNearFar.isValid()
            && inputs.exec.isValid()
            && inputs.gpu.isValid()
            && inputs.instanceMapSDCudaPtr.isValid()
            && inputs.instanceMappingInfoSDPtr.isValid()
            && inputs.metersPerSceneUnit.isValid()
            && inputs.mode.isValid()
            && inputs.parameters.isValid()
            && inputs.renderVar.isValid()
            && inputs.renderVarDisplay.isValid()
            && inputs.rp.isValid()
            && inputs.sdDisplayHeight.isValid()
            && inputs.sdDisplayWidth.isValid()
            && inputs.sdSemBBox3dCamCornersCudaPtr.isValid()
            && inputs.sdSemBBox3dCamExtentCudaPtr.isValid()
            && inputs.sdSemBBoxExtentCudaPtr.isValid()
            && inputs.sdSemBBoxInfosCudaPtr.isValid()
            && inputs.semanticLabelTokenSDCudaPtr.isValid()
            && inputs.semanticMapSDCudaPtr.isValid()
            && inputs.semanticPrimTokenSDCudaPtr.isValid()
            && inputs.semanticWorldTransformSDCudaPtr.isValid()
            && outputs.cudaPtr.isValid()
            && outputs.exec.isValid()
            && outputs.format.isValid()
            && outputs.height.isValid()
            && outputs.renderVarDisplay.isValid()
            && outputs.width.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cameraFisheyeParams.invalidateCachedPointer();
            inputs.cameraModel.invalidateCachedPointer();
            inputs.cameraNearFar.invalidateCachedPointer();
            inputs.exec.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.instanceMapSDCudaPtr.invalidateCachedPointer();
            inputs.instanceMappingInfoSDPtr.invalidateCachedPointer();
            inputs.metersPerSceneUnit.invalidateCachedPointer();
            inputs.mode.invalidateCachedPointer();
            inputs.parameters.invalidateCachedPointer();
            inputs.renderVar.invalidateCachedPointer();
            inputs.renderVarDisplay.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.sdDisplayHeight.invalidateCachedPointer();
            inputs.sdDisplayWidth.invalidateCachedPointer();
            inputs.sdSemBBox3dCamCornersCudaPtr.invalidateCachedPointer();
            inputs.sdSemBBox3dCamExtentCudaPtr.invalidateCachedPointer();
            inputs.sdSemBBoxExtentCudaPtr.invalidateCachedPointer();
            inputs.sdSemBBoxInfosCudaPtr.invalidateCachedPointer();
            inputs.semanticLabelTokenSDCudaPtr.invalidateCachedPointer();
            inputs.semanticMapSDCudaPtr.invalidateCachedPointer();
            inputs.semanticPrimTokenSDCudaPtr.invalidateCachedPointer();
            inputs.semanticWorldTransformSDCudaPtr.invalidateCachedPointer();
            outputs.cudaPtr.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.format.invalidateCachedPointer();
            outputs.height.invalidateCachedPointer();
            outputs.renderVarDisplay.invalidateCachedPointer();
            outputs.width.invalidateCachedPointer();
            return;
        }
        inputs.cameraFisheyeParams.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cameraFisheyeParams.m_token) {
                inputs.cameraFisheyeParams.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cameraModel.m_token) {
                inputs.cameraModel.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cameraNearFar.m_token) {
                inputs.cameraNearFar.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::instanceMapSDCudaPtr.m_token) {
                inputs.instanceMapSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::instanceMappingInfoSDPtr.m_token) {
                inputs.instanceMappingInfoSDPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::metersPerSceneUnit.m_token) {
                inputs.metersPerSceneUnit.invalidateCachedPointer();
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
            if(attrib == inputs::renderVarDisplay.m_token) {
                inputs.renderVarDisplay.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdDisplayHeight.m_token) {
                inputs.sdDisplayHeight.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdDisplayWidth.m_token) {
                inputs.sdDisplayWidth.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdSemBBox3dCamCornersCudaPtr.m_token) {
                inputs.sdSemBBox3dCamCornersCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdSemBBox3dCamExtentCudaPtr.m_token) {
                inputs.sdSemBBox3dCamExtentCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdSemBBoxExtentCudaPtr.m_token) {
                inputs.sdSemBBoxExtentCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdSemBBoxInfosCudaPtr.m_token) {
                inputs.sdSemBBoxInfosCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticLabelTokenSDCudaPtr.m_token) {
                inputs.semanticLabelTokenSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticMapSDCudaPtr.m_token) {
                inputs.semanticMapSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticPrimTokenSDCudaPtr.m_token) {
                inputs.semanticPrimTokenSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticWorldTransformSDCudaPtr.m_token) {
                inputs.semanticWorldTransformSDCudaPtr.invalidateCachedPointer();
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
            if(attrib == outputs::renderVarDisplay.m_token) {
                outputs.renderVarDisplay.invalidateCachedPointer();
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
        if( !inputs.cameraModel.canVectorize()
            || !inputs.cameraNearFar.canVectorize()
            || !inputs.exec.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.instanceMapSDCudaPtr.canVectorize()
            || !inputs.instanceMappingInfoSDPtr.canVectorize()
            || !inputs.metersPerSceneUnit.canVectorize()
            || !inputs.mode.canVectorize()
            || !inputs.parameters.canVectorize()
            || !inputs.renderVar.canVectorize()
            || !inputs.renderVarDisplay.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.sdDisplayHeight.canVectorize()
            || !inputs.sdDisplayWidth.canVectorize()
            || !inputs.sdSemBBox3dCamCornersCudaPtr.canVectorize()
            || !inputs.sdSemBBox3dCamExtentCudaPtr.canVectorize()
            || !inputs.sdSemBBoxExtentCudaPtr.canVectorize()
            || !inputs.sdSemBBoxInfosCudaPtr.canVectorize()
            || !inputs.semanticLabelTokenSDCudaPtr.canVectorize()
            || !inputs.semanticMapSDCudaPtr.canVectorize()
            || !inputs.semanticPrimTokenSDCudaPtr.canVectorize()
            || !inputs.semanticWorldTransformSDCudaPtr.canVectorize()
            || !outputs.cudaPtr.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.format.canVectorize()
            || !outputs.height.canVectorize()
            || !outputs.renderVarDisplay.canVectorize()
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
        if(token == inputs::cameraFisheyeParams.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraFisheyeParams.setHandle(hdl);
            return;
        }
        if(token == inputs::cameraModel.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraModel.setHandle(hdl);
            return;
        }
        if(token == inputs::cameraNearFar.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraNearFar.setHandle(hdl);
            return;
        }
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
        if(token == inputs::instanceMapSDCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.instanceMapSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::instanceMappingInfoSDPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.instanceMappingInfoSDPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::metersPerSceneUnit.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.metersPerSceneUnit.setHandle(hdl);
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
        if(token == inputs::renderVarDisplay.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderVarDisplay.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == inputs::sdDisplayHeight.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdDisplayHeight.setHandle(hdl);
            return;
        }
        if(token == inputs::sdDisplayWidth.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdDisplayWidth.setHandle(hdl);
            return;
        }
        if(token == inputs::sdSemBBox3dCamCornersCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdSemBBox3dCamCornersCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::sdSemBBox3dCamExtentCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdSemBBox3dCamExtentCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::sdSemBBoxExtentCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdSemBBoxExtentCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::sdSemBBoxInfosCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdSemBBoxInfosCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticLabelTokenSDCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticLabelTokenSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticMapSDCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticMapSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticPrimTokenSDCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticPrimTokenSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticWorldTransformSDCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticWorldTransformSDCudaPtr.setHandle(hdl);
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
        if(token == outputs::renderVarDisplay.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.renderVarDisplay.setHandle(hdl);
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
    omni::graph::image::unstable::ComputeParamsBuilder<std::string> getCudaParamsBuilder(InstanceIndex relativeIdx = { 0 }) {
        auto variable = const_cast<OgnSdPostRenderVarDisplayTextureDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostRenderVarDisplayTextureDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostRenderVarDisplayTextureDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostRenderVarDisplayTextureDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdPostRenderVarDisplayTextureDatabase::sm_stateManagerOgnSdPostRenderVarDisplayTexture;
std::tuple<int, int, int> OgnSdPostRenderVarDisplayTextureDatabase::sm_generatorVersionOgnSdPostRenderVarDisplayTexture{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdPostRenderVarDisplayTextureDatabase::sm_targetVersionOgnSdPostRenderVarDisplayTexture{std::make_tuple(2,184,5)};
OgnSdPostRenderVarDisplayTextureDatabase::TokenManager OgnSdPostRenderVarDisplayTextureDatabase::tokens;
}
using namespace IOgnSdPostRenderVarDisplayTexture;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdPostRenderVarDisplayTexture, OgnSdPostRenderVarDisplayTextureDatabase> s_registration("omni.syntheticdata.SdPostRenderVarDisplayTexture", 1, "omni.syntheticdata"); \
}
