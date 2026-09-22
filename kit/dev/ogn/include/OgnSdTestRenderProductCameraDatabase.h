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

namespace OgnSdTestRenderProductCameraAttributes
{
namespace inputs
{
using cameraApertureOffset_t = const pxr::GfVec2f&;
ogn::AttributeInitializer<const pxr::GfVec2f, ogn::kOgnInput> cameraApertureOffset("inputs:cameraApertureOffset", "float2", kExtendedAttributeType_Regular, {0.0f,0.0f});
using cameraApertureSize_t = const pxr::GfVec2f&;
ogn::AttributeInitializer<const pxr::GfVec2f, ogn::kOgnInput> cameraApertureSize("inputs:cameraApertureSize", "float2", kExtendedAttributeType_Regular, {0.0f,0.0f});
using cameraFStop_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> cameraFStop("inputs:cameraFStop", "float", kExtendedAttributeType_Regular, 0.0f);
using cameraFisheyeParams_t = const ogn::const_array<float>&;
ogn::AttributeInitializer<const float*, ogn::kOgnInput> cameraFisheyeParams("inputs:cameraFisheyeParams", "float[]", kExtendedAttributeType_Regular, nullptr, 0);
using cameraFocalLength_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> cameraFocalLength("inputs:cameraFocalLength", "float", kExtendedAttributeType_Regular, 0.0f);
using cameraFocusDistance_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> cameraFocusDistance("inputs:cameraFocusDistance", "float", kExtendedAttributeType_Regular, 0.0f);
using cameraModel_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> cameraModel("inputs:cameraModel", "int", kExtendedAttributeType_Regular, 0);
using cameraNearFar_t = const pxr::GfVec2f&;
ogn::AttributeInitializer<const pxr::GfVec2f, ogn::kOgnInput> cameraNearFar("inputs:cameraNearFar", "float2", kExtendedAttributeType_Regular, {0.0f,0.0f});
using cameraProjection_t = const pxr::GfMatrix4d&;
ogn::AttributeInitializer<const pxr::GfMatrix4d, ogn::kOgnInput> cameraProjection("inputs:cameraProjection", "matrix4d", kExtendedAttributeType_Regular, {1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0});
using cameraViewTransform_t = const pxr::GfMatrix4d&;
ogn::AttributeInitializer<const pxr::GfMatrix4d, ogn::kOgnInput> cameraViewTransform("inputs:cameraViewTransform", "matrix4d", kExtendedAttributeType_Regular, {1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0});
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using height_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> height("inputs:height", "uint", kExtendedAttributeType_Regular, 0);
using metersPerSceneUnit_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> metersPerSceneUnit("inputs:metersPerSceneUnit", "float", kExtendedAttributeType_Regular, 0.0f);
using renderProductCameraPath_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderProductCameraPath("inputs:renderProductCameraPath", "token", kExtendedAttributeType_Regular);
using renderProductResolution_t = const pxr::GfVec2i&;
ogn::AttributeInitializer<const pxr::GfVec2i, ogn::kOgnInput> renderProductResolution("inputs:renderProductResolution", "int2", kExtendedAttributeType_Regular, {0,0});
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using stage_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> stage("inputs:stage", "token", kExtendedAttributeType_Regular);
using traceError_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> traceError("inputs:traceError", "bool", kExtendedAttributeType_Regular, false);
using width_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> width("inputs:width", "uint", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using test_t = bool&;
ogn::AttributeInitializer<bool, ogn::kOgnOutput> test("outputs:test", "bool", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdTestRenderProductCameraAttributes;
namespace IOgnSdTestRenderProductCamera
{
// Synthetic Data node to test the renderProduct camera pipeline
class OgnSdTestRenderProductCameraDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken simulation;
        NameToken postRender;
        NameToken onDemand;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdTestRenderProductCamera.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdTestRenderProductCamera.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdTestRenderProductCamera.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdTestRenderProductCamera.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdTestRenderProductCamera;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdTestRenderProductCamera;
    static std::tuple<int, int, int>sm_targetVersionOgnSdTestRenderProductCamera;
    static constexpr size_t staticAttributeCount = 23;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
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
        , height{offset}
        , metersPerSceneUnit{offset}
        , renderProductCameraPath{offset}
        , renderProductResolution{offset}
        , renderResults{offset}
        , rp{offset}
        , stage{offset}
        , traceError{offset}
        , width{offset}
        {}
        ogn::SimpleInput<const pxr::GfVec2f,ogn::kCpu> cameraApertureOffset;
        ogn::SimpleInput<const pxr::GfVec2f,ogn::kCpu> cameraApertureSize;
        ogn::SimpleInput<const float,ogn::kCpu> cameraFStop;
        ogn::ArrayInput<const float,ogn::kCpu> cameraFisheyeParams;
        ogn::SimpleInput<const float,ogn::kCpu> cameraFocalLength;
        ogn::SimpleInput<const float,ogn::kCpu> cameraFocusDistance;
        ogn::SimpleInput<const int,ogn::kCpu> cameraModel;
        ogn::SimpleInput<const pxr::GfVec2f,ogn::kCpu> cameraNearFar;
        ogn::SimpleInput<const pxr::GfMatrix4d,ogn::kCpu> cameraProjection;
        ogn::SimpleInput<const pxr::GfMatrix4d,ogn::kCpu> cameraViewTransform;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> height;
        ogn::SimpleInput<const float,ogn::kCpu> metersPerSceneUnit;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderProductCameraPath;
        ogn::SimpleInput<const pxr::GfVec2i,ogn::kCpu> renderProductResolution;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const NameToken,ogn::kCpu> stage;
        ogn::SimpleInput<const bool,ogn::kCpu> traceError;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> width;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : test{offset}
        {}
        ogn::SimpleOutput<bool,ogn::kCpu> test;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdTestRenderProductCameraDatabase(NodeObj const& nodeObjParam)
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
    OgnSdTestRenderProductCameraDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdTestRenderProductCameraDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdTestRenderProductCameraDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle,
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::cameraApertureOffset.m_token, inputs::cameraApertureSize.m_token, inputs::cameraFStop.m_token, inputs::cameraFisheyeParams.m_token,
                    inputs::cameraFocalLength.m_token, inputs::cameraFocusDistance.m_token, inputs::cameraModel.m_token, inputs::cameraNearFar.m_token,
                    inputs::cameraProjection.m_token, inputs::cameraViewTransform.m_token, inputs::exec.m_token, inputs::height.m_token,
                    inputs::metersPerSceneUnit.m_token, inputs::renderProductCameraPath.m_token, inputs::renderProductResolution.m_token, inputs::renderResults.m_token,
                    inputs::rp.m_token, inputs::stage.m_token, inputs::traceError.m_token, inputs::width.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::test.m_token
                )
            , kAccordingToContextIndex);
            inputs.cameraApertureOffset.setContext(contextObj);
            inputs.cameraApertureOffset.setHandle(std::get<0>(inputDataHandles0));
            inputs.cameraApertureSize.setContext(contextObj);
            inputs.cameraApertureSize.setHandle(std::get<1>(inputDataHandles0));
            inputs.cameraFStop.setContext(contextObj);
            inputs.cameraFStop.setHandle(std::get<2>(inputDataHandles0));
            inputs.cameraFisheyeParams.setContext(contextObj);
            inputs.cameraFisheyeParams.setHandle(std::get<3>(inputDataHandles0));
            inputs.cameraFocalLength.setContext(contextObj);
            inputs.cameraFocalLength.setHandle(std::get<4>(inputDataHandles0));
            inputs.cameraFocusDistance.setContext(contextObj);
            inputs.cameraFocusDistance.setHandle(std::get<5>(inputDataHandles0));
            inputs.cameraModel.setContext(contextObj);
            inputs.cameraModel.setHandle(std::get<6>(inputDataHandles0));
            inputs.cameraNearFar.setContext(contextObj);
            inputs.cameraNearFar.setHandle(std::get<7>(inputDataHandles0));
            inputs.cameraProjection.setContext(contextObj);
            inputs.cameraProjection.setHandle(std::get<8>(inputDataHandles0));
            inputs.cameraViewTransform.setContext(contextObj);
            inputs.cameraViewTransform.setHandle(std::get<9>(inputDataHandles0));
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<10>(inputDataHandles0));
            inputs.height.setContext(contextObj);
            inputs.height.setHandle(std::get<11>(inputDataHandles0));
            inputs.metersPerSceneUnit.setContext(contextObj);
            inputs.metersPerSceneUnit.setHandle(std::get<12>(inputDataHandles0));
            inputs.renderProductCameraPath.setContext(contextObj);
            inputs.renderProductCameraPath.setHandle(std::get<13>(inputDataHandles0));
            inputs.renderProductResolution.setContext(contextObj);
            inputs.renderProductResolution.setHandle(std::get<14>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<15>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<16>(inputDataHandles0));
            inputs.stage.setContext(contextObj);
            inputs.stage.setHandle(std::get<17>(inputDataHandles0));
            inputs.traceError.setContext(contextObj);
            inputs.traceError.setHandle(std::get<18>(inputDataHandles0));
            inputs.width.setContext(contextObj);
            inputs.width.setHandle(std::get<19>(inputDataHandles0));
            outputs.test.setContext(contextObj);
            outputs.test.setHandle(std::get<0>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdTestRenderProductCamera");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdTestRenderProductCameraDatabase::tokens.simulation = iToken.getHandle("simulation");
        OgnSdTestRenderProductCameraDatabase::tokens.postRender = iToken.getHandle("postRender");
        OgnSdTestRenderProductCameraDatabase::tokens.onDemand = iToken.getHandle("onDemand");

        inputs::cameraApertureOffset.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraApertureSize.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraFStop.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraFisheyeParams.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraFocalLength.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraFocusDistance.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraModel.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraNearFar.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraProjection.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraViewTransform.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::metersPerSceneUnit.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderProductCameraPath.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderProductResolution.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::stage.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::traceError.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::width.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::test.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"simulation\", \"postRender\", \"onDemand\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:simulation,graph:postRender,graph:action,internal:test");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to test the renderProduct camera pipeline");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExclusions, "tests");
        // LCOV_EXCL_STOP
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraApertureOffset.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera horizontal and vertical aperture offset");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraApertureSize.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera horizontal and vertical aperture");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraFStop.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera fStop");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraFisheyeParams.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera fisheye projection parameters");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraFocalLength.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera focal length");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraFocusDistance.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera focus distance");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraModel.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera model (pinhole or fisheye models)");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraNearFar.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera near/far clipping range");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraProjection.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera projection matrix");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cameraViewTransform.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Camera view matrix");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Height of the frame");
        attr = iNode->getAttributeByToken(nodeObj, inputs::metersPerSceneUnit.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Scene units to meters scale");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderProductCameraPath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "RenderProduct camera prim path");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderProductResolution.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "RenderProduct resolution");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "OnDemand connection : pointer to render product results");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "PostRender connection : pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::stage.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Stage in {simulation, postrender, ondemand}");
        attr = iNode->getAttributeByToken(nodeObj, inputs::traceError.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If true print an error message when the frame numbers are out-of-sync");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Width of the frame");
        attr = iNode->getAttributeByToken(nodeObj, outputs::test.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Test value : false if failed");
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
        sm_stateManagerOgnSdTestRenderProductCamera.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        return validateNode()
            && inputs.cameraApertureOffset.isValid()
            && inputs.cameraApertureSize.isValid()
            && inputs.cameraFStop.isValid()
            && inputs.cameraFisheyeParams.isValid()
            && inputs.cameraFocalLength.isValid()
            && inputs.cameraFocusDistance.isValid()
            && inputs.cameraModel.isValid()
            && inputs.cameraNearFar.isValid()
            && inputs.cameraProjection.isValid()
            && inputs.cameraViewTransform.isValid()
            && inputs.exec.isValid()
            && inputs.height.isValid()
            && inputs.metersPerSceneUnit.isValid()
            && inputs.renderProductCameraPath.isValid()
            && inputs.renderProductResolution.isValid()
            && inputs.renderResults.isValid()
            && inputs.rp.isValid()
            && inputs.stage.isValid()
            && inputs.traceError.isValid()
            && inputs.width.isValid()
            && outputs.test.isValid()
        ;
        // LCOV_EXCL_STOP
    }
    void preCompute() {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        if(m_canCachePointers == false) {
            inputs.cameraApertureOffset.invalidateCachedPointer();
            inputs.cameraApertureSize.invalidateCachedPointer();
            inputs.cameraFStop.invalidateCachedPointer();
            inputs.cameraFisheyeParams.invalidateCachedPointer();
            inputs.cameraFocalLength.invalidateCachedPointer();
            inputs.cameraFocusDistance.invalidateCachedPointer();
            inputs.cameraModel.invalidateCachedPointer();
            inputs.cameraNearFar.invalidateCachedPointer();
            inputs.cameraProjection.invalidateCachedPointer();
            inputs.cameraViewTransform.invalidateCachedPointer();
            inputs.exec.invalidateCachedPointer();
            inputs.height.invalidateCachedPointer();
            inputs.metersPerSceneUnit.invalidateCachedPointer();
            inputs.renderProductCameraPath.invalidateCachedPointer();
            inputs.renderProductResolution.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.stage.invalidateCachedPointer();
            inputs.traceError.invalidateCachedPointer();
            inputs.width.invalidateCachedPointer();
            outputs.test.invalidateCachedPointer();
            return;
        }
        inputs.cameraFisheyeParams.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cameraApertureOffset.m_token) {
                inputs.cameraApertureOffset.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cameraApertureSize.m_token) {
                inputs.cameraApertureSize.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cameraFStop.m_token) {
                inputs.cameraFStop.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cameraFisheyeParams.m_token) {
                inputs.cameraFisheyeParams.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cameraFocalLength.m_token) {
                inputs.cameraFocalLength.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cameraFocusDistance.m_token) {
                inputs.cameraFocusDistance.invalidateCachedPointer();
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
            if(attrib == inputs::cameraProjection.m_token) {
                inputs.cameraProjection.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cameraViewTransform.m_token) {
                inputs.cameraViewTransform.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::height.m_token) {
                inputs.height.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::metersPerSceneUnit.m_token) {
                inputs.metersPerSceneUnit.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderProductCameraPath.m_token) {
                inputs.renderProductCameraPath.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderProductResolution.m_token) {
                inputs.renderProductResolution.invalidateCachedPointer();
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
            if(attrib == inputs::stage.m_token) {
                inputs.stage.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::traceError.m_token) {
                inputs.traceError.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::width.m_token) {
                inputs.width.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::test.m_token) {
                outputs.test.invalidateCachedPointer();
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
        if( !inputs.cameraApertureOffset.canVectorize()
            || !inputs.cameraApertureSize.canVectorize()
            || !inputs.cameraFStop.canVectorize()
            || !inputs.cameraFocalLength.canVectorize()
            || !inputs.cameraFocusDistance.canVectorize()
            || !inputs.cameraModel.canVectorize()
            || !inputs.cameraNearFar.canVectorize()
            || !inputs.cameraProjection.canVectorize()
            || !inputs.cameraViewTransform.canVectorize()
            || !inputs.exec.canVectorize()
            || !inputs.height.canVectorize()
            || !inputs.metersPerSceneUnit.canVectorize()
            || !inputs.renderProductCameraPath.canVectorize()
            || !inputs.renderProductResolution.canVectorize()
            || !inputs.renderResults.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.stage.canVectorize()
            || !inputs.traceError.canVectorize()
            || !inputs.width.canVectorize()
            || !outputs.test.canVectorize()
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
        if(token == inputs::cameraApertureOffset.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraApertureOffset.setHandle(hdl);
            return;
        }
        if(token == inputs::cameraApertureSize.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraApertureSize.setHandle(hdl);
            return;
        }
        if(token == inputs::cameraFStop.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraFStop.setHandle(hdl);
            return;
        }
        if(token == inputs::cameraFisheyeParams.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraFisheyeParams.setHandle(hdl);
            return;
        }
        if(token == inputs::cameraFocalLength.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraFocalLength.setHandle(hdl);
            return;
        }
        if(token == inputs::cameraFocusDistance.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraFocusDistance.setHandle(hdl);
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
        if(token == inputs::cameraProjection.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraProjection.setHandle(hdl);
            return;
        }
        if(token == inputs::cameraViewTransform.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cameraViewTransform.setHandle(hdl);
            return;
        }
        if(token == inputs::exec.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exec.setHandle(hdl);
            return;
        }
        if(token == inputs::height.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.height.setHandle(hdl);
            return;
        }
        if(token == inputs::metersPerSceneUnit.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.metersPerSceneUnit.setHandle(hdl);
            return;
        }
        if(token == inputs::renderProductCameraPath.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderProductCameraPath.setHandle(hdl);
            return;
        }
        if(token == inputs::renderProductResolution.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderProductResolution.setHandle(hdl);
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
        if(token == inputs::stage.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.stage.setHandle(hdl);
            return;
        }
        if(token == inputs::traceError.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.traceError.setHandle(hdl);
            return;
        }
        if(token == inputs::width.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.width.setHandle(hdl);
            return;
        }
        if(token == outputs::test.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.test.setHandle(hdl);
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
        auto variable = const_cast<OgnSdTestRenderProductCameraDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdTestRenderProductCameraDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdTestRenderProductCameraDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdTestRenderProductCameraDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdTestRenderProductCameraDatabase::sm_stateManagerOgnSdTestRenderProductCamera;
std::tuple<int, int, int> OgnSdTestRenderProductCameraDatabase::sm_generatorVersionOgnSdTestRenderProductCamera{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdTestRenderProductCameraDatabase::sm_targetVersionOgnSdTestRenderProductCamera{std::make_tuple(2,184,5)};
OgnSdTestRenderProductCameraDatabase::TokenManager OgnSdTestRenderProductCameraDatabase::tokens;
}
using namespace IOgnSdTestRenderProductCamera;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdTestRenderProductCamera, OgnSdTestRenderProductCameraDatabase> s_registration("omni.syntheticdata.SdTestRenderProductCamera", 1, "omni.syntheticdata"); \
}
