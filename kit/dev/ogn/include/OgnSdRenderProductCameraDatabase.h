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

namespace OgnSdRenderProductCameraAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using renderProductPath_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderProductPath("inputs:renderProductPath", "token", kExtendedAttributeType_Regular);
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using cameraApertureOffset_t = pxr::GfVec2f&;
ogn::AttributeInitializer<pxr::GfVec2f, ogn::kOgnOutput> cameraApertureOffset("outputs:cameraApertureOffset", "float2", kExtendedAttributeType_Regular);
using cameraApertureSize_t = pxr::GfVec2f&;
ogn::AttributeInitializer<pxr::GfVec2f, ogn::kOgnOutput> cameraApertureSize("outputs:cameraApertureSize", "float2", kExtendedAttributeType_Regular);
using cameraFStop_t = float&;
ogn::AttributeInitializer<float, ogn::kOgnOutput> cameraFStop("outputs:cameraFStop", "float", kExtendedAttributeType_Regular);
using cameraFisheyeParams_t = ogn::array<float>&;
ogn::AttributeInitializer<float*, ogn::kOgnOutput> cameraFisheyeParams("outputs:cameraFisheyeParams", "float[]", kExtendedAttributeType_Regular, nullptr, 0);
using cameraFocalLength_t = float&;
ogn::AttributeInitializer<float, ogn::kOgnOutput> cameraFocalLength("outputs:cameraFocalLength", "float", kExtendedAttributeType_Regular);
using cameraFocusDistance_t = float&;
ogn::AttributeInitializer<float, ogn::kOgnOutput> cameraFocusDistance("outputs:cameraFocusDistance", "float", kExtendedAttributeType_Regular);
using cameraModel_t = int&;
ogn::AttributeInitializer<int, ogn::kOgnOutput> cameraModel("outputs:cameraModel", "int", kExtendedAttributeType_Regular);
using cameraNearFar_t = pxr::GfVec2f&;
ogn::AttributeInitializer<pxr::GfVec2f, ogn::kOgnOutput> cameraNearFar("outputs:cameraNearFar", "float2", kExtendedAttributeType_Regular);
using cameraProjection_t = pxr::GfMatrix4d&;
ogn::AttributeInitializer<pxr::GfMatrix4d, ogn::kOgnOutput> cameraProjection("outputs:cameraProjection", "matrix4d", kExtendedAttributeType_Regular);
using cameraViewTransform_t = pxr::GfMatrix4d&;
ogn::AttributeInitializer<pxr::GfMatrix4d, ogn::kOgnOutput> cameraViewTransform("outputs:cameraViewTransform", "matrix4d", kExtendedAttributeType_Regular);
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using metersPerSceneUnit_t = float&;
ogn::AttributeInitializer<float, ogn::kOgnOutput> metersPerSceneUnit("outputs:metersPerSceneUnit", "float", kExtendedAttributeType_Regular);
using renderProductResolution_t = pxr::GfVec2i&;
ogn::AttributeInitializer<pxr::GfVec2i, ogn::kOgnOutput> renderProductResolution("outputs:renderProductResolution", "int2", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdRenderProductCameraAttributes;
namespace IOgnSdRenderProductCamera
{
// Synthetic Data node to expose the camera data
class OgnSdRenderProductCameraDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken RenderProductCameraSD;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdRenderProductCamera.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdRenderProductCamera.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdRenderProductCamera.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdRenderProductCamera.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdRenderProductCamera;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdRenderProductCamera;
    static std::tuple<int, int, int>sm_targetVersionOgnSdRenderProductCamera;
    static constexpr size_t staticAttributeCount = 19;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , gpu{offset}
        , renderProductPath{offset}
        , renderResults{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderProductPath;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : cameraApertureOffset{offset}
        , cameraApertureSize{offset}
        , cameraFStop{offset}
        , cameraFisheyeParams{offset}
        , cameraFocalLength{offset}
        , cameraFocusDistance{offset}
        , cameraModel{offset}
        , cameraNearFar{offset}
        , cameraProjection{offset,AttributeRole::eMatrix}
        , cameraViewTransform{offset,AttributeRole::eMatrix}
        , exec{offset,AttributeRole::eExecution}
        , metersPerSceneUnit{offset}
        , renderProductResolution{offset}
        {}
        ogn::SimpleOutput<pxr::GfVec2f,ogn::kCpu> cameraApertureOffset;
        ogn::SimpleOutput<pxr::GfVec2f,ogn::kCpu> cameraApertureSize;
        ogn::SimpleOutput<float,ogn::kCpu> cameraFStop;
        ogn::ArrayOutput<float,ogn::kCpu> cameraFisheyeParams;
        ogn::SimpleOutput<float,ogn::kCpu> cameraFocalLength;
        ogn::SimpleOutput<float,ogn::kCpu> cameraFocusDistance;
        ogn::SimpleOutput<int,ogn::kCpu> cameraModel;
        ogn::SimpleOutput<pxr::GfVec2f,ogn::kCpu> cameraNearFar;
        ogn::SimpleOutput<pxr::GfMatrix4d,ogn::kCpu> cameraProjection;
        ogn::SimpleOutput<pxr::GfMatrix4d,ogn::kCpu> cameraViewTransform;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<float,ogn::kCpu> metersPerSceneUnit;
        ogn::SimpleOutput<pxr::GfVec2i,ogn::kCpu> renderProductResolution;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdRenderProductCameraDatabase(NodeObj const& nodeObjParam)
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
    OgnSdRenderProductCameraDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdRenderProductCameraDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdRenderProductCameraDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::exec.m_token, inputs::gpu.m_token, inputs::renderProductPath.m_token, inputs::renderResults.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::cameraApertureOffset.m_token, outputs::cameraApertureSize.m_token, outputs::cameraFStop.m_token, outputs::cameraFisheyeParams.m_token,
                    outputs::cameraFocalLength.m_token, outputs::cameraFocusDistance.m_token, outputs::cameraModel.m_token, outputs::cameraNearFar.m_token,
                    outputs::cameraProjection.m_token, outputs::cameraViewTransform.m_token, outputs::exec.m_token, outputs::metersPerSceneUnit.m_token,
                    outputs::renderProductResolution.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<1>(inputDataHandles0));
            inputs.renderProductPath.setContext(contextObj);
            inputs.renderProductPath.setHandle(std::get<2>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<3>(inputDataHandles0));
            outputs.cameraApertureOffset.setContext(contextObj);
            outputs.cameraApertureOffset.setHandle(std::get<0>(outputDataHandles0));
            outputs.cameraApertureSize.setContext(contextObj);
            outputs.cameraApertureSize.setHandle(std::get<1>(outputDataHandles0));
            outputs.cameraFStop.setContext(contextObj);
            outputs.cameraFStop.setHandle(std::get<2>(outputDataHandles0));
            outputs.cameraFisheyeParams.setContext(contextObj);
            outputs.cameraFisheyeParams.setHandle(std::get<3>(outputDataHandles0));
            outputs.cameraFocalLength.setContext(contextObj);
            outputs.cameraFocalLength.setHandle(std::get<4>(outputDataHandles0));
            outputs.cameraFocusDistance.setContext(contextObj);
            outputs.cameraFocusDistance.setHandle(std::get<5>(outputDataHandles0));
            outputs.cameraModel.setContext(contextObj);
            outputs.cameraModel.setHandle(std::get<6>(outputDataHandles0));
            outputs.cameraNearFar.setContext(contextObj);
            outputs.cameraNearFar.setHandle(std::get<7>(outputDataHandles0));
            outputs.cameraProjection.setContext(contextObj);
            outputs.cameraProjection.setHandle(std::get<8>(outputDataHandles0));
            outputs.cameraViewTransform.setContext(contextObj);
            outputs.cameraViewTransform.setHandle(std::get<9>(outputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<10>(outputDataHandles0));
            outputs.metersPerSceneUnit.setContext(contextObj);
            outputs.metersPerSceneUnit.setHandle(std::get<11>(outputDataHandles0));
            outputs.renderProductResolution.setContext(contextObj);
            outputs.renderProductResolution.setHandle(std::get<12>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdRenderProductCamera");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdRenderProductCameraDatabase::tokens.RenderProductCameraSD = iToken.getHandle("RenderProductCameraSD");

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderProductPath.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::cameraApertureOffset.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cameraApertureSize.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cameraFStop.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cameraFisheyeParams.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cameraFocalLength.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cameraFocusDistance.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cameraModel.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cameraNearFar.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cameraProjection.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cameraViewTransform.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::metersPerSceneUnit.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::renderProductResolution.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"RenderProductCameraSD\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,graph:action");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to expose the camera data");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations.");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderProductPath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "RenderProduct prim path");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render results");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cameraApertureOffset.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera horizontal and vertical aperture offset");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cameraApertureSize.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera horizontal and vertical aperture");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cameraFStop.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera fStop");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cameraFisheyeParams.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera fisheye projection parameters");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cameraFocalLength.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera focal length");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cameraFocusDistance.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera focus distance");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cameraModel.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera model (pinhole or fisheye models)");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cameraNearFar.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera near/far clipping range");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cameraProjection.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera projection matrix");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cameraViewTransform.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera view matrix");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes for each newFrame event received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Received");
        attr = iNode->getAttributeByToken(nodeObj, outputs::metersPerSceneUnit.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Scene units to meters scale");
        attr = iNode->getAttributeByToken(nodeObj, outputs::renderProductResolution.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "RenderProduct resolution");
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
        sm_stateManagerOgnSdRenderProductCamera.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.gpu.isValid()
            && inputs.renderProductPath.isValid()
            && inputs.renderResults.isValid()
            && outputs.cameraApertureOffset.isValid()
            && outputs.cameraApertureSize.isValid()
            && outputs.cameraFStop.isValid()
            && outputs.cameraFisheyeParams.isValid()
            && outputs.cameraFocalLength.isValid()
            && outputs.cameraFocusDistance.isValid()
            && outputs.cameraModel.isValid()
            && outputs.cameraNearFar.isValid()
            && outputs.cameraProjection.isValid()
            && outputs.cameraViewTransform.isValid()
            && outputs.exec.isValid()
            && outputs.metersPerSceneUnit.isValid()
            && outputs.renderProductResolution.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.renderProductPath.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            outputs.cameraApertureOffset.invalidateCachedPointer();
            outputs.cameraApertureSize.invalidateCachedPointer();
            outputs.cameraFStop.invalidateCachedPointer();
            outputs.cameraFisheyeParams.invalidateCachedPointer();
            outputs.cameraFocalLength.invalidateCachedPointer();
            outputs.cameraFocusDistance.invalidateCachedPointer();
            outputs.cameraModel.invalidateCachedPointer();
            outputs.cameraNearFar.invalidateCachedPointer();
            outputs.cameraProjection.invalidateCachedPointer();
            outputs.cameraViewTransform.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.metersPerSceneUnit.invalidateCachedPointer();
            outputs.renderProductResolution.invalidateCachedPointer();
            return;
        }
        outputs.cameraFisheyeParams.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderProductPath.m_token) {
                inputs.renderProductPath.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderResults.m_token) {
                inputs.renderResults.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cameraApertureOffset.m_token) {
                outputs.cameraApertureOffset.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cameraApertureSize.m_token) {
                outputs.cameraApertureSize.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cameraFStop.m_token) {
                outputs.cameraFStop.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cameraFisheyeParams.m_token) {
                outputs.cameraFisheyeParams.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cameraFocalLength.m_token) {
                outputs.cameraFocalLength.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cameraFocusDistance.m_token) {
                outputs.cameraFocusDistance.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cameraModel.m_token) {
                outputs.cameraModel.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cameraNearFar.m_token) {
                outputs.cameraNearFar.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cameraProjection.m_token) {
                outputs.cameraProjection.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cameraViewTransform.m_token) {
                outputs.cameraViewTransform.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::metersPerSceneUnit.m_token) {
                outputs.metersPerSceneUnit.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::renderProductResolution.m_token) {
                outputs.renderProductResolution.invalidateCachedPointer();
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
            || !inputs.renderProductPath.canVectorize()
            || !inputs.renderResults.canVectorize()
            || !outputs.cameraApertureOffset.canVectorize()
            || !outputs.cameraApertureSize.canVectorize()
            || !outputs.cameraFStop.canVectorize()
            || !outputs.cameraFocalLength.canVectorize()
            || !outputs.cameraFocusDistance.canVectorize()
            || !outputs.cameraModel.canVectorize()
            || !outputs.cameraNearFar.canVectorize()
            || !outputs.cameraProjection.canVectorize()
            || !outputs.cameraViewTransform.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.metersPerSceneUnit.canVectorize()
            || !outputs.renderProductResolution.canVectorize()
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
        if(token == inputs::renderProductPath.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderProductPath.setHandle(hdl);
            return;
        }
        if(token == inputs::renderResults.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderResults.setHandle(hdl);
            return;
        }
        if(token == outputs::cameraApertureOffset.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cameraApertureOffset.setHandle(hdl);
            return;
        }
        if(token == outputs::cameraApertureSize.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cameraApertureSize.setHandle(hdl);
            return;
        }
        if(token == outputs::cameraFStop.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cameraFStop.setHandle(hdl);
            return;
        }
        if(token == outputs::cameraFisheyeParams.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cameraFisheyeParams.setHandle(hdl);
            return;
        }
        if(token == outputs::cameraFocalLength.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cameraFocalLength.setHandle(hdl);
            return;
        }
        if(token == outputs::cameraFocusDistance.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cameraFocusDistance.setHandle(hdl);
            return;
        }
        if(token == outputs::cameraModel.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cameraModel.setHandle(hdl);
            return;
        }
        if(token == outputs::cameraNearFar.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cameraNearFar.setHandle(hdl);
            return;
        }
        if(token == outputs::cameraProjection.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cameraProjection.setHandle(hdl);
            return;
        }
        if(token == outputs::cameraViewTransform.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cameraViewTransform.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::metersPerSceneUnit.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.metersPerSceneUnit.setHandle(hdl);
            return;
        }
        if(token == outputs::renderProductResolution.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.renderProductResolution.setHandle(hdl);
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
        auto variable = const_cast<OgnSdRenderProductCameraDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdRenderProductCameraDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdRenderProductCameraDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdRenderProductCameraDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdRenderProductCameraDatabase::sm_stateManagerOgnSdRenderProductCamera;
std::tuple<int, int, int> OgnSdRenderProductCameraDatabase::sm_generatorVersionOgnSdRenderProductCamera{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdRenderProductCameraDatabase::sm_targetVersionOgnSdRenderProductCamera{std::make_tuple(2,184,5)};
OgnSdRenderProductCameraDatabase::TokenManager OgnSdRenderProductCameraDatabase::tokens;
}
using namespace IOgnSdRenderProductCamera;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdRenderProductCamera, OgnSdRenderProductCameraDatabase> s_registration("omni.syntheticdata.SdRenderProductCamera", 2, "omni.syntheticdata"); \
}
