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

namespace CamTextureReadTaskNodeAttributes
{
namespace inputs
{
using aov_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> aov("inputs:aov", "token", kExtendedAttributeType_Regular);
using degreesX_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> degreesX("inputs:degreesX", "float", kExtendedAttributeType_Regular, 0.0f);
using degreesY_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> degreesY("inputs:degreesY", "float", kExtendedAttributeType_Regular, 0.0f);
using degreesZ_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> degreesZ("inputs:degreesZ", "float", kExtendedAttributeType_Regular, 0.0f);
using disparityBaselineMM_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> disparityBaselineMM("inputs:disparityBaselineMM", "float", kExtendedAttributeType_Regular, 55.0f);
using disparityFarthestDistanceError_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> disparityFarthestDistanceError("inputs:disparityFarthestDistanceError", "float", kExtendedAttributeType_Regular, 0.14f);
using disparityFarthestRangeMM_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> disparityFarthestRangeMM("inputs:disparityFarthestRangeMM", "float", kExtendedAttributeType_Regular, 4000.0f);
using disparityHorizontalFovDeg_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> disparityHorizontalFovDeg("inputs:disparityHorizontalFovDeg", "float", kExtendedAttributeType_Regular, 65.0f);
using disparityNearestDistanceError_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> disparityNearestDistanceError("inputs:disparityNearestDistanceError", "float", kExtendedAttributeType_Regular, 0.02f);
using disparityNearestRangeMM_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> disparityNearestRangeMM("inputs:disparityNearestRangeMM", "float", kExtendedAttributeType_Regular, 300.0f);
using enableSyntheticDisparitySim_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> enableSyntheticDisparitySim("inputs:enableSyntheticDisparitySim", "bool", kExtendedAttributeType_Regular, false);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using hydraTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTime("inputs:hydraTime", "double", kExtendedAttributeType_Regular, 0.0);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using simTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTime("inputs:simTime", "double", kExtendedAttributeType_Regular, 0.0);
}
namespace outputs
{
using dest_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> dest("outputs:dest", "uint64", kExtendedAttributeType_Regular);
using gpu_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> gpu("outputs:gpu", "uint64", kExtendedAttributeType_Regular);
using hydraTimeOut_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> hydraTimeOut("outputs:hydraTimeOut", "double", kExtendedAttributeType_Regular, 0.0);
using rp_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> rp("outputs:rp", "uint64", kExtendedAttributeType_Regular);
using simTimeOut_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> simTimeOut("outputs:simTimeOut", "double", kExtendedAttributeType_Regular, 0.0);
}
namespace state
{
}
}
using namespace CamTextureReadTaskNodeAttributes;
namespace ICamTextureReadTaskNode
{
// Translates data from a render node to the camera pipeline
class CamTextureReadTaskNodeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerCamTextureReadTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerCamTextureReadTaskNode.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerCamTextureReadTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerCamTextureReadTaskNode.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerCamTextureReadTaskNode;
    static std::tuple<int, int, int>sm_generatorVersionCamTextureReadTaskNode;
    static std::tuple<int, int, int>sm_targetVersionCamTextureReadTaskNode;
    static constexpr size_t staticAttributeCount = 22;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : aov{offset}
        , degreesX{offset}
        , degreesY{offset}
        , degreesZ{offset}
        , disparityBaselineMM{offset}
        , disparityFarthestDistanceError{offset}
        , disparityFarthestRangeMM{offset}
        , disparityHorizontalFovDeg{offset}
        , disparityNearestDistanceError{offset}
        , disparityNearestRangeMM{offset}
        , enableSyntheticDisparitySim{offset}
        , gpu{offset}
        , hydraTime{offset}
        , rp{offset}
        , simTime{offset}
        {}
        ogn::SimpleInput<const NameToken,ogn::kCpu> aov;
        ogn::SimpleInput<const float,ogn::kCpu> degreesX;
        ogn::SimpleInput<const float,ogn::kCpu> degreesY;
        ogn::SimpleInput<const float,ogn::kCpu> degreesZ;
        ogn::SimpleInput<const float,ogn::kCpu> disparityBaselineMM;
        ogn::SimpleInput<const float,ogn::kCpu> disparityFarthestDistanceError;
        ogn::SimpleInput<const float,ogn::kCpu> disparityFarthestRangeMM;
        ogn::SimpleInput<const float,ogn::kCpu> disparityHorizontalFovDeg;
        ogn::SimpleInput<const float,ogn::kCpu> disparityNearestDistanceError;
        ogn::SimpleInput<const float,ogn::kCpu> disparityNearestRangeMM;
        ogn::SimpleInput<const bool,ogn::kCpu> enableSyntheticDisparitySim;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const double,ogn::kCpu> simTime;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : dest{offset}
        , gpu{offset}
        , hydraTimeOut{offset}
        , rp{offset}
        , simTimeOut{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> dest;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> gpu;
        ogn::SimpleOutput<double,ogn::kCpu> hydraTimeOut;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> rp;
        ogn::SimpleOutput<double,ogn::kCpu> simTimeOut;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    CamTextureReadTaskNodeDatabase(NodeObj const& nodeObjParam)
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
    CamTextureReadTaskNodeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : CamTextureReadTaskNodeDatabase(nodeObjParam)
    {}

    //Main constructor
    CamTextureReadTaskNodeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::aov.m_token, inputs::degreesX.m_token, inputs::degreesY.m_token, inputs::degreesZ.m_token,
                    inputs::disparityBaselineMM.m_token, inputs::disparityFarthestDistanceError.m_token, inputs::disparityFarthestRangeMM.m_token, inputs::disparityHorizontalFovDeg.m_token,
                    inputs::disparityNearestDistanceError.m_token, inputs::disparityNearestRangeMM.m_token, inputs::enableSyntheticDisparitySim.m_token, inputs::gpu.m_token,
                    inputs::hydraTime.m_token, inputs::rp.m_token, inputs::simTime.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::dest.m_token, outputs::gpu.m_token, outputs::hydraTimeOut.m_token, outputs::rp.m_token,
                    outputs::simTimeOut.m_token
                )
            , kAccordingToContextIndex);
            inputs.aov.setContext(contextObj);
            inputs.aov.setHandle(std::get<0>(inputDataHandles0));
            inputs.degreesX.setContext(contextObj);
            inputs.degreesX.setHandle(std::get<1>(inputDataHandles0));
            inputs.degreesY.setContext(contextObj);
            inputs.degreesY.setHandle(std::get<2>(inputDataHandles0));
            inputs.degreesZ.setContext(contextObj);
            inputs.degreesZ.setHandle(std::get<3>(inputDataHandles0));
            inputs.disparityBaselineMM.setContext(contextObj);
            inputs.disparityBaselineMM.setHandle(std::get<4>(inputDataHandles0));
            inputs.disparityFarthestDistanceError.setContext(contextObj);
            inputs.disparityFarthestDistanceError.setHandle(std::get<5>(inputDataHandles0));
            inputs.disparityFarthestRangeMM.setContext(contextObj);
            inputs.disparityFarthestRangeMM.setHandle(std::get<6>(inputDataHandles0));
            inputs.disparityHorizontalFovDeg.setContext(contextObj);
            inputs.disparityHorizontalFovDeg.setHandle(std::get<7>(inputDataHandles0));
            inputs.disparityNearestDistanceError.setContext(contextObj);
            inputs.disparityNearestDistanceError.setHandle(std::get<8>(inputDataHandles0));
            inputs.disparityNearestRangeMM.setContext(contextObj);
            inputs.disparityNearestRangeMM.setHandle(std::get<9>(inputDataHandles0));
            inputs.enableSyntheticDisparitySim.setContext(contextObj);
            inputs.enableSyntheticDisparitySim.setHandle(std::get<10>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<11>(inputDataHandles0));
            inputs.hydraTime.setContext(contextObj);
            inputs.hydraTime.setHandle(std::get<12>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<13>(inputDataHandles0));
            inputs.simTime.setContext(contextObj);
            inputs.simTime.setHandle(std::get<14>(inputDataHandles0));
            outputs.dest.setContext(contextObj);
            outputs.dest.setHandle(std::get<0>(outputDataHandles0));
            outputs.gpu.setContext(contextObj);
            outputs.gpu.setHandle(std::get<1>(outputDataHandles0));
            outputs.hydraTimeOut.setContext(contextObj);
            outputs.hydraTimeOut.setHandle(std::get<2>(outputDataHandles0));
            outputs.rp.setContext(contextObj);
            outputs.rp.setHandle(std::get<3>(outputDataHandles0));
            outputs.simTimeOut.setContext(contextObj);
            outputs.simTimeOut.setHandle(std::get<4>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.CamTextureReadTaskNode");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_aov_token {"LDR"};
        inputs::aov.setDefault(inputs_aov_token.asTokenC());
        inputs::aov.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::degreesX.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::degreesY.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::degreesZ.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::disparityBaselineMM.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::disparityFarthestDistanceError.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::disparityFarthestRangeMM.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::disparityHorizontalFovDeg.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::disparityNearestDistanceError.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::disparityNearestRangeMM.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::enableSyntheticDisparitySim.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::dest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.camera");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Translates data from a render node to the camera pipeline");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::aov.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "AOV used as source (LDR, HDR, DEPTH)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Render Product/Arbitrary Output Variable (AOV)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"LDR\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::degreesX.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Degrees to tilt on the X axis");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "degreesX");
        attr = iNode->getAttributeByToken(nodeObj, inputs::degreesY.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Degrees to tilt on the Y axis");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "degreesY");
        attr = iNode->getAttributeByToken(nodeObj, inputs::degreesZ.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Degrees to tilt on the Z axis");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "degreesZ");
        attr = iNode->getAttributeByToken(nodeObj, inputs::disparityBaselineMM.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Baseline distance between depth imagers in millimeters.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "disparityBaselineMM");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "55.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::disparityFarthestDistanceError.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Percent error in depth measurement at the farthest sensor range.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "disparityFarthestDistanceError");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.14");
        attr = iNode->getAttributeByToken(nodeObj, inputs::disparityFarthestRangeMM.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Maximum visible distance for the depth sensor in millimeters.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "disparityFarthestRangeMM");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "4000.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::disparityHorizontalFovDeg.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Horizontal field of view in degrees.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "disparityHorizontalFovDeg");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "65.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::disparityNearestDistanceError.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Percent error in depth measurement at the nearest sensor range.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "disparityNearestDistanceError");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.02");
        attr = iNode->getAttributeByToken(nodeObj, inputs::disparityNearestRangeMM.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Minimum visible distance for the depth sensor in millimeters.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "disparityNearestRangeMM");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "300.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::enableSyntheticDisparitySim.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Enable disparity simulation when reading synthetic depth buffer.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "enableSyntheticDisparitySim");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "hydra timestamp input as double in [s]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "simTime timestamp input as double in [s]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::dest.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Destination Buffer");
        attr = iNode->getAttributeByToken(nodeObj, outputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundationsOut");
        attr = iNode->getAttributeByToken(nodeObj, outputs::hydraTimeOut.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp output in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProductOut");
        attr = iNode->getAttributeByToken(nodeObj, outputs::simTimeOut.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp output in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
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
        sm_stateManagerCamTextureReadTaskNode.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.aov.isValid()
            && inputs.degreesX.isValid()
            && inputs.degreesY.isValid()
            && inputs.degreesZ.isValid()
            && inputs.disparityBaselineMM.isValid()
            && inputs.disparityFarthestDistanceError.isValid()
            && inputs.disparityFarthestRangeMM.isValid()
            && inputs.disparityHorizontalFovDeg.isValid()
            && inputs.disparityNearestDistanceError.isValid()
            && inputs.disparityNearestRangeMM.isValid()
            && inputs.enableSyntheticDisparitySim.isValid()
            && inputs.gpu.isValid()
            && inputs.hydraTime.isValid()
            && inputs.rp.isValid()
            && inputs.simTime.isValid()
            && outputs.dest.isValid()
            && outputs.gpu.isValid()
            && outputs.hydraTimeOut.isValid()
            && outputs.rp.isValid()
            && outputs.simTimeOut.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.aov.invalidateCachedPointer();
            inputs.degreesX.invalidateCachedPointer();
            inputs.degreesY.invalidateCachedPointer();
            inputs.degreesZ.invalidateCachedPointer();
            inputs.disparityBaselineMM.invalidateCachedPointer();
            inputs.disparityFarthestDistanceError.invalidateCachedPointer();
            inputs.disparityFarthestRangeMM.invalidateCachedPointer();
            inputs.disparityHorizontalFovDeg.invalidateCachedPointer();
            inputs.disparityNearestDistanceError.invalidateCachedPointer();
            inputs.disparityNearestRangeMM.invalidateCachedPointer();
            inputs.enableSyntheticDisparitySim.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.hydraTime.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.simTime.invalidateCachedPointer();
            outputs.dest.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.hydraTimeOut.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            outputs.simTimeOut.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::aov.m_token) {
                inputs.aov.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::degreesX.m_token) {
                inputs.degreesX.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::degreesY.m_token) {
                inputs.degreesY.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::degreesZ.m_token) {
                inputs.degreesZ.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::disparityBaselineMM.m_token) {
                inputs.disparityBaselineMM.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::disparityFarthestDistanceError.m_token) {
                inputs.disparityFarthestDistanceError.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::disparityFarthestRangeMM.m_token) {
                inputs.disparityFarthestRangeMM.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::disparityHorizontalFovDeg.m_token) {
                inputs.disparityHorizontalFovDeg.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::disparityNearestDistanceError.m_token) {
                inputs.disparityNearestDistanceError.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::disparityNearestRangeMM.m_token) {
                inputs.disparityNearestRangeMM.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::enableSyntheticDisparitySim.m_token) {
                inputs.enableSyntheticDisparitySim.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hydraTime.m_token) {
                inputs.hydraTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::simTime.m_token) {
                inputs.simTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::dest.m_token) {
                outputs.dest.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::gpu.m_token) {
                outputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::hydraTimeOut.m_token) {
                outputs.hydraTimeOut.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::rp.m_token) {
                outputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::simTimeOut.m_token) {
                outputs.simTimeOut.invalidateCachedPointer();
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
        if( !inputs.aov.canVectorize()
            || !inputs.degreesX.canVectorize()
            || !inputs.degreesY.canVectorize()
            || !inputs.degreesZ.canVectorize()
            || !inputs.disparityBaselineMM.canVectorize()
            || !inputs.disparityFarthestDistanceError.canVectorize()
            || !inputs.disparityFarthestRangeMM.canVectorize()
            || !inputs.disparityHorizontalFovDeg.canVectorize()
            || !inputs.disparityNearestDistanceError.canVectorize()
            || !inputs.disparityNearestRangeMM.canVectorize()
            || !inputs.enableSyntheticDisparitySim.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.hydraTime.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.simTime.canVectorize()
            || !outputs.dest.canVectorize()
            || !outputs.gpu.canVectorize()
            || !outputs.hydraTimeOut.canVectorize()
            || !outputs.rp.canVectorize()
            || !outputs.simTimeOut.canVectorize()
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
        if(token == inputs::aov.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.aov.setHandle(hdl);
            return;
        }
        if(token == inputs::degreesX.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.degreesX.setHandle(hdl);
            return;
        }
        if(token == inputs::degreesY.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.degreesY.setHandle(hdl);
            return;
        }
        if(token == inputs::degreesZ.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.degreesZ.setHandle(hdl);
            return;
        }
        if(token == inputs::disparityBaselineMM.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.disparityBaselineMM.setHandle(hdl);
            return;
        }
        if(token == inputs::disparityFarthestDistanceError.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.disparityFarthestDistanceError.setHandle(hdl);
            return;
        }
        if(token == inputs::disparityFarthestRangeMM.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.disparityFarthestRangeMM.setHandle(hdl);
            return;
        }
        if(token == inputs::disparityHorizontalFovDeg.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.disparityHorizontalFovDeg.setHandle(hdl);
            return;
        }
        if(token == inputs::disparityNearestDistanceError.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.disparityNearestDistanceError.setHandle(hdl);
            return;
        }
        if(token == inputs::disparityNearestRangeMM.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.disparityNearestRangeMM.setHandle(hdl);
            return;
        }
        if(token == inputs::enableSyntheticDisparitySim.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.enableSyntheticDisparitySim.setHandle(hdl);
            return;
        }
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::hydraTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hydraTime.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == inputs::simTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.simTime.setHandle(hdl);
            return;
        }
        if(token == outputs::dest.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.dest.setHandle(hdl);
            return;
        }
        if(token == outputs::gpu.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.gpu.setHandle(hdl);
            return;
        }
        if(token == outputs::hydraTimeOut.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.hydraTimeOut.setHandle(hdl);
            return;
        }
        if(token == outputs::rp.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rp.setHandle(hdl);
            return;
        }
        if(token == outputs::simTimeOut.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.simTimeOut.setHandle(hdl);
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
ogn::StateManager CamTextureReadTaskNodeDatabase::sm_stateManagerCamTextureReadTaskNode;
std::tuple<int, int, int> CamTextureReadTaskNodeDatabase::sm_generatorVersionCamTextureReadTaskNode{std::make_tuple(1,79,2)};
std::tuple<int, int, int> CamTextureReadTaskNodeDatabase::sm_targetVersionCamTextureReadTaskNode{std::make_tuple(2,184,5)};
}
using namespace ICamTextureReadTaskNode;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<CamTextureReadTaskNode, CamTextureReadTaskNodeDatabase> s_registration("omni.sensors.nv.camera.CamTextureReadTaskNode", 1, "omni.sensors.nv.camera"); \
}
