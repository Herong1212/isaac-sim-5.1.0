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

namespace OgnSdPostSemantic3dBoundingBoxCameraProjectionAttributes
{
namespace inputs
{
using cameraFisheyeParams_t = const ogn::const_array<float>&;
ogn::AttributeInitializer<const float*, ogn::kOgnInput> cameraFisheyeParams("inputs:cameraFisheyeParams", "float[]", kExtendedAttributeType_Regular, nullptr, 0);
using cameraModel_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> cameraModel("inputs:cameraModel", "int", kExtendedAttributeType_Regular, 0);
using cameraNearFar_t = const pxr::GfVec2f&;
ogn::AttributeInitializer<const pxr::GfVec2f, ogn::kOgnInput> cameraNearFar("inputs:cameraNearFar", "float2", kExtendedAttributeType_Regular, {1.0f,10000000.0f});
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using instanceMappingInfoSDPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> instanceMappingInfoSDPtr("inputs:instanceMappingInfoSDPtr", "uint64", kExtendedAttributeType_Regular, 0);
using metersPerSceneUnit_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> metersPerSceneUnit("inputs:metersPerSceneUnit", "float", kExtendedAttributeType_Regular, 0.01f);
using renderProductResolution_t = const pxr::GfVec2i&;
ogn::AttributeInitializer<const pxr::GfVec2i, ogn::kOgnInput> renderProductResolution("inputs:renderProductResolution", "int2", kExtendedAttributeType_Regular, {65536,65536});
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using sdSemBBoxExtentCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdSemBBoxExtentCudaPtr("inputs:sdSemBBoxExtentCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using sdSemBBoxInfosCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdSemBBoxInfosCudaPtr("inputs:sdSemBBoxInfosCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using semanticWorldTransformSDCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticWorldTransformSDCudaPtr("inputs:semanticWorldTransformSDCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using sdSemBBox3dCamCornersCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> sdSemBBox3dCamCornersCudaPtr("outputs:sdSemBBox3dCamCornersCudaPtr", "uint64", kExtendedAttributeType_Regular);
using sdSemBBox3dCamExtentCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> sdSemBBox3dCamExtentCudaPtr("outputs:sdSemBBox3dCamExtentCudaPtr", "uint64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdPostSemantic3dBoundingBoxCameraProjectionAttributes;
namespace IOgnSdPostSemantic3dBoundingBoxCameraProjection
{
// Synthetic Data node to project 3d bounding boxes data in camera space.
class OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken SemanticBoundingBox3DInfosSD;
        NameToken SemanticBoundingBox3DCamCornersSD;
        NameToken SemanticBoundingBox3DCamExtentSD;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdPostSemantic3dBoundingBoxCameraProjection.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdPostSemantic3dBoundingBoxCameraProjection.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdPostSemantic3dBoundingBoxCameraProjection.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdPostSemantic3dBoundingBoxCameraProjection.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdPostSemantic3dBoundingBoxCameraProjection;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdPostSemantic3dBoundingBoxCameraProjection;
    static std::tuple<int, int, int>sm_targetVersionOgnSdPostSemantic3dBoundingBoxCameraProjection;
    static constexpr size_t staticAttributeCount = 17;
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
        , instanceMappingInfoSDPtr{offset}
        , metersPerSceneUnit{offset}
        , renderProductResolution{offset}
        , rp{offset}
        , sdSemBBoxExtentCudaPtr{offset}
        , sdSemBBoxInfosCudaPtr{offset}
        , semanticWorldTransformSDCudaPtr{offset}
        {}
        ogn::ArrayInput<const float,ogn::kCpu> cameraFisheyeParams;
        ogn::SimpleInput<const int,ogn::kCpu> cameraModel;
        ogn::SimpleInput<const pxr::GfVec2f,ogn::kCpu> cameraNearFar;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> instanceMappingInfoSDPtr;
        ogn::SimpleInput<const float,ogn::kCpu> metersPerSceneUnit;
        ogn::SimpleInput<const pxr::GfVec2i,ogn::kCpu> renderProductResolution;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdSemBBoxExtentCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdSemBBoxInfosCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticWorldTransformSDCudaPtr;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , sdSemBBox3dCamCornersCudaPtr{offset}
        , sdSemBBox3dCamExtentCudaPtr{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> sdSemBBox3dCamCornersCudaPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> sdSemBBox3dCamExtentCudaPtr;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase(NodeObj const& nodeObjParam)
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
    OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::cameraFisheyeParams.m_token, inputs::cameraModel.m_token, inputs::cameraNearFar.m_token, inputs::exec.m_token,
                    inputs::gpu.m_token, inputs::instanceMappingInfoSDPtr.m_token, inputs::metersPerSceneUnit.m_token, inputs::renderProductResolution.m_token,
                    inputs::rp.m_token, inputs::sdSemBBoxExtentCudaPtr.m_token, inputs::sdSemBBoxInfosCudaPtr.m_token, inputs::semanticWorldTransformSDCudaPtr.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::sdSemBBox3dCamCornersCudaPtr.m_token, outputs::sdSemBBox3dCamExtentCudaPtr.m_token
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
            inputs.instanceMappingInfoSDPtr.setContext(contextObj);
            inputs.instanceMappingInfoSDPtr.setHandle(std::get<5>(inputDataHandles0));
            inputs.metersPerSceneUnit.setContext(contextObj);
            inputs.metersPerSceneUnit.setHandle(std::get<6>(inputDataHandles0));
            inputs.renderProductResolution.setContext(contextObj);
            inputs.renderProductResolution.setHandle(std::get<7>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<8>(inputDataHandles0));
            inputs.sdSemBBoxExtentCudaPtr.setContext(contextObj);
            inputs.sdSemBBoxExtentCudaPtr.setHandle(std::get<9>(inputDataHandles0));
            inputs.sdSemBBoxInfosCudaPtr.setContext(contextObj);
            inputs.sdSemBBoxInfosCudaPtr.setHandle(std::get<10>(inputDataHandles0));
            inputs.semanticWorldTransformSDCudaPtr.setContext(contextObj);
            inputs.semanticWorldTransformSDCudaPtr.setHandle(std::get<11>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.sdSemBBox3dCamCornersCudaPtr.setContext(contextObj);
            outputs.sdSemBBox3dCamCornersCudaPtr.setHandle(std::get<1>(outputDataHandles0));
            outputs.sdSemBBox3dCamExtentCudaPtr.setContext(contextObj);
            outputs.sdSemBBox3dCamExtentCudaPtr.setHandle(std::get<2>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdPostSemantic3dBoundingBoxCameraProjection");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase::tokens.SemanticBoundingBox3DInfosSD = iToken.getHandle("SemanticBoundingBox3DInfosSD");
        OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase::tokens.SemanticBoundingBox3DCamCornersSD = iToken.getHandle("SemanticBoundingBox3DCamCornersSD");
        OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase::tokens.SemanticBoundingBox3DCamExtentSD = iToken.getHandle("SemanticBoundingBox3DCamExtentSD");

        inputs::cameraFisheyeParams.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraModel.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cameraNearFar.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::instanceMappingInfoSDPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::metersPerSceneUnit.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderProductResolution.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdSemBBoxExtentCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdSemBBoxInfosCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticWorldTransformSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdSemBBox3dCamCornersCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdSemBBox3dCamExtentCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"SemanticBoundingBox3DInfosSD\", \"SemanticBoundingBox3DCamCornersSD\", \"SemanticBoundingBox3DCamExtentSD\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,rendering");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to project 3d bounding boxes data in camera space.");
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
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[1.0, 10000000.0]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::instanceMappingInfoSDPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::metersPerSceneUnit.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Scene units to meters scale");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.01");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderProductResolution.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "RenderProduct resolution");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[65536, 65536]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdSemBBoxExtentCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing the extent of the bounding boxes as a float4=(u_min,v_min,u_max,v_max) for 2D or a float6=(xmin,ymin,zmin,xmax,ymax,zmax) in object space for 3D");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdSemBBoxInfosCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing valid bounding boxes infos");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticWorldTransformSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda float44 buffer pointer of size numSemantics containing the world semantic transform");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdSemBBox3dCamCornersCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing the projection of the 3d bounding boxes on the camera plane represented as a float4=(u,v,z,a) for each bounding box corners");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdSemBBox3dCamExtentCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing the 2d extent of the 3d bounding boxes on the camera plane represented as a float6=(u_min,u_max,v_min,v_max,z_min,z_max)");
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
        sm_stateManagerOgnSdPostSemantic3dBoundingBoxCameraProjection.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cameraFisheyeParams.isValid()
            && inputs.cameraModel.isValid()
            && inputs.cameraNearFar.isValid()
            && inputs.exec.isValid()
            && inputs.gpu.isValid()
            && inputs.instanceMappingInfoSDPtr.isValid()
            && inputs.metersPerSceneUnit.isValid()
            && inputs.renderProductResolution.isValid()
            && inputs.rp.isValid()
            && inputs.sdSemBBoxExtentCudaPtr.isValid()
            && inputs.sdSemBBoxInfosCudaPtr.isValid()
            && inputs.semanticWorldTransformSDCudaPtr.isValid()
            && outputs.exec.isValid()
            && outputs.sdSemBBox3dCamCornersCudaPtr.isValid()
            && outputs.sdSemBBox3dCamExtentCudaPtr.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cameraFisheyeParams.invalidateCachedPointer();
            inputs.cameraModel.invalidateCachedPointer();
            inputs.cameraNearFar.invalidateCachedPointer();
            inputs.exec.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.instanceMappingInfoSDPtr.invalidateCachedPointer();
            inputs.metersPerSceneUnit.invalidateCachedPointer();
            inputs.renderProductResolution.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.sdSemBBoxExtentCudaPtr.invalidateCachedPointer();
            inputs.sdSemBBoxInfosCudaPtr.invalidateCachedPointer();
            inputs.semanticWorldTransformSDCudaPtr.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.sdSemBBox3dCamCornersCudaPtr.invalidateCachedPointer();
            outputs.sdSemBBox3dCamExtentCudaPtr.invalidateCachedPointer();
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
            if(attrib == inputs::instanceMappingInfoSDPtr.m_token) {
                inputs.instanceMappingInfoSDPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::metersPerSceneUnit.m_token) {
                inputs.metersPerSceneUnit.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderProductResolution.m_token) {
                inputs.renderProductResolution.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
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
            if(attrib == inputs::semanticWorldTransformSDCudaPtr.m_token) {
                inputs.semanticWorldTransformSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdSemBBox3dCamCornersCudaPtr.m_token) {
                outputs.sdSemBBox3dCamCornersCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdSemBBox3dCamExtentCudaPtr.m_token) {
                outputs.sdSemBBox3dCamExtentCudaPtr.invalidateCachedPointer();
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
            || !inputs.instanceMappingInfoSDPtr.canVectorize()
            || !inputs.metersPerSceneUnit.canVectorize()
            || !inputs.renderProductResolution.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.sdSemBBoxExtentCudaPtr.canVectorize()
            || !inputs.sdSemBBoxInfosCudaPtr.canVectorize()
            || !inputs.semanticWorldTransformSDCudaPtr.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.sdSemBBox3dCamCornersCudaPtr.canVectorize()
            || !outputs.sdSemBBox3dCamExtentCudaPtr.canVectorize()
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
        if(token == inputs::renderProductResolution.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderProductResolution.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
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
        if(token == inputs::semanticWorldTransformSDCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticWorldTransformSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::sdSemBBox3dCamCornersCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdSemBBox3dCamCornersCudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::sdSemBBox3dCamExtentCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdSemBBox3dCamExtentCudaPtr.setHandle(hdl);
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
        auto variable = const_cast<OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase::sm_stateManagerOgnSdPostSemantic3dBoundingBoxCameraProjection;
std::tuple<int, int, int> OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase::sm_generatorVersionOgnSdPostSemantic3dBoundingBoxCameraProjection{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase::sm_targetVersionOgnSdPostSemantic3dBoundingBoxCameraProjection{std::make_tuple(2,184,5)};
OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase::TokenManager OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase::tokens;
}
using namespace IOgnSdPostSemantic3dBoundingBoxCameraProjection;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdPostSemantic3dBoundingBoxCameraProjection, OgnSdPostSemantic3dBoundingBoxCameraProjectionDatabase> s_registration("omni.syntheticdata.SdPostSemantic3dBoundingBoxCameraProjection", 1, "omni.syntheticdata"); \
}
