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

namespace CamPhotonEstimationTaskNodeAttributes
{
namespace inputs
{
using blueCorrection_t = const pxr::GfVec3f&;
ogn::AttributeInitializer<const pxr::GfVec3f, ogn::kOgnInput> blueCorrection("inputs:blueCorrection", "float3", kExtendedAttributeType_Regular, {0.0f,0.0f,0.0f});
using correctionsMultiplier_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> correctionsMultiplier("inputs:correctionsMultiplier", "float", kExtendedAttributeType_Regular, 0.3298769777f);
using exposureTime_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> exposureTime("inputs:exposureTime", "float", kExtendedAttributeType_Regular, 0.011f);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using greenCorrection_t = const pxr::GfVec3f&;
ogn::AttributeInitializer<const pxr::GfVec3f, ogn::kOgnInput> greenCorrection("inputs:greenCorrection", "float3", kExtendedAttributeType_Regular, {0.0f,0.0f,0.0f});
using hydraTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTimeIn("inputs:hydraTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using illuminantStandard_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> illuminantStandard("inputs:illuminantStandard", "token", kExtendedAttributeType_Regular);
using maxIllumination_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> maxIllumination("inputs:maxIllumination", "float", kExtendedAttributeType_Regular, 3000.0f);
using maxValueQECurve_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> maxValueQECurve("inputs:maxValueQECurve", "float", kExtendedAttributeType_Regular, 2.1f);
using pixelSize_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> pixelSize("inputs:pixelSize", "float", kExtendedAttributeType_Regular, 2.1f);
using redCorrection_t = const pxr::GfVec3f&;
ogn::AttributeInitializer<const pxr::GfVec3f, ogn::kOgnInput> redCorrection("inputs:redCorrection", "float3", kExtendedAttributeType_Regular, {0.0f,0.0f,0.0f});
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using simTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTimeIn("inputs:simTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using dest_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> dest("outputs:dest", "uint64", kExtendedAttributeType_Regular, 0);
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
using namespace CamPhotonEstimationTaskNodeAttributes;
namespace ICamPhotonEstimationTaskNode
{
// Translates the camera image to a RGB image for SiL FastPath.
class CamPhotonEstimationTaskNodeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerCamPhotonEstimationTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerCamPhotonEstimationTaskNode.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerCamPhotonEstimationTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerCamPhotonEstimationTaskNode.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerCamPhotonEstimationTaskNode;
    static std::tuple<int, int, int>sm_generatorVersionCamPhotonEstimationTaskNode;
    static std::tuple<int, int, int>sm_targetVersionCamPhotonEstimationTaskNode;
    static constexpr size_t staticAttributeCount = 21;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : blueCorrection{offset}
        , correctionsMultiplier{offset}
        , exposureTime{offset}
        , gpu{offset}
        , greenCorrection{offset}
        , hydraTimeIn{offset}
        , illuminantStandard{offset}
        , maxIllumination{offset}
        , maxValueQECurve{offset}
        , pixelSize{offset}
        , redCorrection{offset}
        , rp{offset}
        , simTimeIn{offset}
        , src{offset}
        {}
        ogn::SimpleInput<const pxr::GfVec3f,ogn::kCpu> blueCorrection;
        ogn::SimpleInput<const float,ogn::kCpu> correctionsMultiplier;
        ogn::SimpleInput<const float,ogn::kCpu> exposureTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const pxr::GfVec3f,ogn::kCpu> greenCorrection;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTimeIn;
        ogn::SimpleInput<const NameToken,ogn::kCpu> illuminantStandard;
        ogn::SimpleInput<const float,ogn::kCpu> maxIllumination;
        ogn::SimpleInput<const float,ogn::kCpu> maxValueQECurve;
        ogn::SimpleInput<const float,ogn::kCpu> pixelSize;
        ogn::SimpleInput<const pxr::GfVec3f,ogn::kCpu> redCorrection;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const double,ogn::kCpu> simTimeIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
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
    CamPhotonEstimationTaskNodeDatabase(NodeObj const& nodeObjParam)
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
    CamPhotonEstimationTaskNodeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : CamPhotonEstimationTaskNodeDatabase(nodeObjParam)
    {}

    //Main constructor
    CamPhotonEstimationTaskNodeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::blueCorrection.m_token, inputs::correctionsMultiplier.m_token, inputs::exposureTime.m_token, inputs::gpu.m_token,
                    inputs::greenCorrection.m_token, inputs::hydraTimeIn.m_token, inputs::illuminantStandard.m_token, inputs::maxIllumination.m_token,
                    inputs::maxValueQECurve.m_token, inputs::pixelSize.m_token, inputs::redCorrection.m_token, inputs::rp.m_token,
                    inputs::simTimeIn.m_token, inputs::src.m_token
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
            inputs.blueCorrection.setContext(contextObj);
            inputs.blueCorrection.setHandle(std::get<0>(inputDataHandles0));
            inputs.correctionsMultiplier.setContext(contextObj);
            inputs.correctionsMultiplier.setHandle(std::get<1>(inputDataHandles0));
            inputs.exposureTime.setContext(contextObj);
            inputs.exposureTime.setHandle(std::get<2>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<3>(inputDataHandles0));
            inputs.greenCorrection.setContext(contextObj);
            inputs.greenCorrection.setHandle(std::get<4>(inputDataHandles0));
            inputs.hydraTimeIn.setContext(contextObj);
            inputs.hydraTimeIn.setHandle(std::get<5>(inputDataHandles0));
            inputs.illuminantStandard.setContext(contextObj);
            inputs.illuminantStandard.setHandle(std::get<6>(inputDataHandles0));
            inputs.maxIllumination.setContext(contextObj);
            inputs.maxIllumination.setHandle(std::get<7>(inputDataHandles0));
            inputs.maxValueQECurve.setContext(contextObj);
            inputs.maxValueQECurve.setHandle(std::get<8>(inputDataHandles0));
            inputs.pixelSize.setContext(contextObj);
            inputs.pixelSize.setHandle(std::get<9>(inputDataHandles0));
            inputs.redCorrection.setContext(contextObj);
            inputs.redCorrection.setHandle(std::get<10>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<11>(inputDataHandles0));
            inputs.simTimeIn.setContext(contextObj);
            inputs.simTimeIn.setHandle(std::get<12>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<13>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.CamPhotonEstimationTaskNode");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_illuminantStandard_token {"D65"};
        inputs::illuminantStandard.setDefault(inputs_illuminantStandard_token.asTokenC());
        inputs::blueCorrection.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::correctionsMultiplier.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exposureTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::greenCorrection.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::illuminantStandard.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::maxIllumination.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::maxValueQECurve.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::pixelSize.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::redCorrection.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::dest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.camera");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Translates the camera image to a RGB image for SiL FastPath.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::blueCorrection.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Red Correction Matrix (R,G,B)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[0.0, 0.0, 0.0]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::correctionsMultiplier.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "multiplier to applied to all values for values which are missing in the preceding chain (e.g. fstops etc)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.3298769777");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exposureTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "exposure time in [s]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.011");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::greenCorrection.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Red Correction Matrix (R,G,B)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[0.0, 0.0, 0.0]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::illuminantStandard.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Defines the illlumination standard");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"D65\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::maxIllumination.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "maximal illumintation in the scene");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "3000.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::maxValueQECurve.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The maximal value in the quantum efficiency curve");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "2.1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::pixelSize.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "PixelSize in [um]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "2.1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::redCorrection.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Red Correction Matrix (R,G,B)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[0.0, 0.0, 0.0]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::dest.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Destination Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
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
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
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
        sm_stateManagerCamPhotonEstimationTaskNode.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.blueCorrection.isValid()
            && inputs.correctionsMultiplier.isValid()
            && inputs.exposureTime.isValid()
            && inputs.gpu.isValid()
            && inputs.greenCorrection.isValid()
            && inputs.hydraTimeIn.isValid()
            && inputs.illuminantStandard.isValid()
            && inputs.maxIllumination.isValid()
            && inputs.maxValueQECurve.isValid()
            && inputs.pixelSize.isValid()
            && inputs.redCorrection.isValid()
            && inputs.rp.isValid()
            && inputs.simTimeIn.isValid()
            && inputs.src.isValid()
            && outputs.dest.isValid()
            && outputs.gpu.isValid()
            && outputs.hydraTimeOut.isValid()
            && outputs.rp.isValid()
            && outputs.simTimeOut.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.blueCorrection.invalidateCachedPointer();
            inputs.correctionsMultiplier.invalidateCachedPointer();
            inputs.exposureTime.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.greenCorrection.invalidateCachedPointer();
            inputs.hydraTimeIn.invalidateCachedPointer();
            inputs.illuminantStandard.invalidateCachedPointer();
            inputs.maxIllumination.invalidateCachedPointer();
            inputs.maxValueQECurve.invalidateCachedPointer();
            inputs.pixelSize.invalidateCachedPointer();
            inputs.redCorrection.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.simTimeIn.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            outputs.dest.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.hydraTimeOut.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            outputs.simTimeOut.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::blueCorrection.m_token) {
                inputs.blueCorrection.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::correctionsMultiplier.m_token) {
                inputs.correctionsMultiplier.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::exposureTime.m_token) {
                inputs.exposureTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::greenCorrection.m_token) {
                inputs.greenCorrection.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hydraTimeIn.m_token) {
                inputs.hydraTimeIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::illuminantStandard.m_token) {
                inputs.illuminantStandard.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::maxIllumination.m_token) {
                inputs.maxIllumination.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::maxValueQECurve.m_token) {
                inputs.maxValueQECurve.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::pixelSize.m_token) {
                inputs.pixelSize.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::redCorrection.m_token) {
                inputs.redCorrection.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::simTimeIn.m_token) {
                inputs.simTimeIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::src.m_token) {
                inputs.src.invalidateCachedPointer();
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
        if( !inputs.blueCorrection.canVectorize()
            || !inputs.correctionsMultiplier.canVectorize()
            || !inputs.exposureTime.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.greenCorrection.canVectorize()
            || !inputs.hydraTimeIn.canVectorize()
            || !inputs.illuminantStandard.canVectorize()
            || !inputs.maxIllumination.canVectorize()
            || !inputs.maxValueQECurve.canVectorize()
            || !inputs.pixelSize.canVectorize()
            || !inputs.redCorrection.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.simTimeIn.canVectorize()
            || !inputs.src.canVectorize()
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
        if(token == inputs::blueCorrection.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.blueCorrection.setHandle(hdl);
            return;
        }
        if(token == inputs::correctionsMultiplier.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.correctionsMultiplier.setHandle(hdl);
            return;
        }
        if(token == inputs::exposureTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exposureTime.setHandle(hdl);
            return;
        }
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::greenCorrection.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.greenCorrection.setHandle(hdl);
            return;
        }
        if(token == inputs::hydraTimeIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hydraTimeIn.setHandle(hdl);
            return;
        }
        if(token == inputs::illuminantStandard.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.illuminantStandard.setHandle(hdl);
            return;
        }
        if(token == inputs::maxIllumination.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.maxIllumination.setHandle(hdl);
            return;
        }
        if(token == inputs::maxValueQECurve.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.maxValueQECurve.setHandle(hdl);
            return;
        }
        if(token == inputs::pixelSize.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.pixelSize.setHandle(hdl);
            return;
        }
        if(token == inputs::redCorrection.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.redCorrection.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == inputs::simTimeIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.simTimeIn.setHandle(hdl);
            return;
        }
        if(token == inputs::src.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.src.setHandle(hdl);
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
ogn::StateManager CamPhotonEstimationTaskNodeDatabase::sm_stateManagerCamPhotonEstimationTaskNode;
std::tuple<int, int, int> CamPhotonEstimationTaskNodeDatabase::sm_generatorVersionCamPhotonEstimationTaskNode{std::make_tuple(1,79,2)};
std::tuple<int, int, int> CamPhotonEstimationTaskNodeDatabase::sm_targetVersionCamPhotonEstimationTaskNode{std::make_tuple(2,184,5)};
}
using namespace ICamPhotonEstimationTaskNode;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<CamPhotonEstimationTaskNode, CamPhotonEstimationTaskNodeDatabase> s_registration("omni.sensors.nv.camera.CamPhotonEstimationTaskNode", 1, "omni.sensors.nv.camera"); \
}
