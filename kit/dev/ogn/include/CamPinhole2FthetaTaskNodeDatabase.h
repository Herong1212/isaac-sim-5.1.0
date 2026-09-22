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

namespace CamPinhole2FthetaTaskNodeAttributes
{
namespace inputs
{
using LensDistCenterX_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> LensDistCenterX("inputs:LensDistCenterX", "float", kExtendedAttributeType_Regular, 0.0f);
using LensDistCenterY_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> LensDistCenterY("inputs:LensDistCenterY", "float", kExtendedAttributeType_Regular, 0.0f);
using LensDistortionP0_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> LensDistortionP0("inputs:LensDistortionP0", "float", kExtendedAttributeType_Regular, 0.0f);
using LensDistortionP1_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> LensDistortionP1("inputs:LensDistortionP1", "float", kExtendedAttributeType_Regular, 0.0f);
using LensDistortionP2_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> LensDistortionP2("inputs:LensDistortionP2", "float", kExtendedAttributeType_Regular, 0.0f);
using LensDistortionP3_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> LensDistortionP3("inputs:LensDistortionP3", "float", kExtendedAttributeType_Regular, 0.0f);
using LensDistortionP4_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> LensDistortionP4("inputs:LensDistortionP4", "float", kExtendedAttributeType_Regular, 0.0f);
using LensDistortionP5_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> LensDistortionP5("inputs:LensDistortionP5", "float", kExtendedAttributeType_Regular, 0.0f);
using SrcFOV_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> SrcFOV("inputs:SrcFOV", "uint", kExtendedAttributeType_Regular, 0);
using aov_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> aov("inputs:aov", "token", kExtendedAttributeType_Regular);
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
using namespace CamPinhole2FthetaTaskNodeAttributes;
namespace ICamPinhole2FthetaTaskNode
{
// Projects the data from a pinhole via the ftheta 5th order polynomial
class CamPinhole2FthetaTaskNodeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerCamPinhole2FthetaTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerCamPinhole2FthetaTaskNode.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerCamPinhole2FthetaTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerCamPinhole2FthetaTaskNode.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerCamPinhole2FthetaTaskNode;
    static std::tuple<int, int, int>sm_generatorVersionCamPinhole2FthetaTaskNode;
    static std::tuple<int, int, int>sm_targetVersionCamPinhole2FthetaTaskNode;
    static constexpr size_t staticAttributeCount = 21;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : LensDistCenterX{offset}
        , LensDistCenterY{offset}
        , LensDistortionP0{offset}
        , LensDistortionP1{offset}
        , LensDistortionP2{offset}
        , LensDistortionP3{offset}
        , LensDistortionP4{offset}
        , LensDistortionP5{offset}
        , SrcFOV{offset}
        , aov{offset}
        , gpu{offset}
        , hydraTime{offset}
        , rp{offset}
        , simTime{offset}
        {}
        ogn::SimpleInput<const float,ogn::kCpu> LensDistCenterX;
        ogn::SimpleInput<const float,ogn::kCpu> LensDistCenterY;
        ogn::SimpleInput<const float,ogn::kCpu> LensDistortionP0;
        ogn::SimpleInput<const float,ogn::kCpu> LensDistortionP1;
        ogn::SimpleInput<const float,ogn::kCpu> LensDistortionP2;
        ogn::SimpleInput<const float,ogn::kCpu> LensDistortionP3;
        ogn::SimpleInput<const float,ogn::kCpu> LensDistortionP4;
        ogn::SimpleInput<const float,ogn::kCpu> LensDistortionP5;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> SrcFOV;
        ogn::SimpleInput<const NameToken,ogn::kCpu> aov;
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
    CamPinhole2FthetaTaskNodeDatabase(NodeObj const& nodeObjParam)
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
    CamPinhole2FthetaTaskNodeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : CamPinhole2FthetaTaskNodeDatabase(nodeObjParam)
    {}

    //Main constructor
    CamPinhole2FthetaTaskNodeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::LensDistCenterX.m_token, inputs::LensDistCenterY.m_token, inputs::LensDistortionP0.m_token, inputs::LensDistortionP1.m_token,
                    inputs::LensDistortionP2.m_token, inputs::LensDistortionP3.m_token, inputs::LensDistortionP4.m_token, inputs::LensDistortionP5.m_token,
                    inputs::SrcFOV.m_token, inputs::aov.m_token, inputs::gpu.m_token, inputs::hydraTime.m_token,
                    inputs::rp.m_token, inputs::simTime.m_token
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
            inputs.LensDistCenterX.setContext(contextObj);
            inputs.LensDistCenterX.setHandle(std::get<0>(inputDataHandles0));
            inputs.LensDistCenterY.setContext(contextObj);
            inputs.LensDistCenterY.setHandle(std::get<1>(inputDataHandles0));
            inputs.LensDistortionP0.setContext(contextObj);
            inputs.LensDistortionP0.setHandle(std::get<2>(inputDataHandles0));
            inputs.LensDistortionP1.setContext(contextObj);
            inputs.LensDistortionP1.setHandle(std::get<3>(inputDataHandles0));
            inputs.LensDistortionP2.setContext(contextObj);
            inputs.LensDistortionP2.setHandle(std::get<4>(inputDataHandles0));
            inputs.LensDistortionP3.setContext(contextObj);
            inputs.LensDistortionP3.setHandle(std::get<5>(inputDataHandles0));
            inputs.LensDistortionP4.setContext(contextObj);
            inputs.LensDistortionP4.setHandle(std::get<6>(inputDataHandles0));
            inputs.LensDistortionP5.setContext(contextObj);
            inputs.LensDistortionP5.setHandle(std::get<7>(inputDataHandles0));
            inputs.SrcFOV.setContext(contextObj);
            inputs.SrcFOV.setHandle(std::get<8>(inputDataHandles0));
            inputs.aov.setContext(contextObj);
            inputs.aov.setHandle(std::get<9>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<10>(inputDataHandles0));
            inputs.hydraTime.setContext(contextObj);
            inputs.hydraTime.setHandle(std::get<11>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<12>(inputDataHandles0));
            inputs.simTime.setContext(contextObj);
            inputs.simTime.setHandle(std::get<13>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.CamPinhole2FthetaTaskNode");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_aov_token {"LDR"};
        inputs::aov.setDefault(inputs_aov_token.asTokenC());
        inputs::LensDistCenterX.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::LensDistCenterY.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::LensDistortionP0.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::LensDistortionP1.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::LensDistortionP2.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::LensDistortionP3.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::LensDistortionP4.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::LensDistortionP5.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::SrcFOV.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::aov.initialize(iToken, *iNodeType, nodeTypeObj);
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
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Projects the data from a pinhole via the ftheta 5th order polynomial");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::LensDistCenterX.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Distortion Center X Axis");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::LensDistCenterY.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Distortion Center Y Axis");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::LensDistortionP0.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Distortion Coefficent offset (In DW calibration always 0.0)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::LensDistortionP1.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Distortion Coefficent linear");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::LensDistortionP2.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Distortion Coefficent square");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::LensDistortionP3.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Distortion Coefficent cubic");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::LensDistortionP4.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Distortion Coefficent power 4");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::LensDistortionP5.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Distortion Coefficent power 5");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::SrcFOV.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Field of View which is projected to the image plane");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::aov.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "AOV used as source (LDR, HDR, DEPTH)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Render Product/Arbitrary Output Variable (AOV)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"LDR\"");
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
        sm_stateManagerCamPinhole2FthetaTaskNode.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.LensDistCenterX.isValid()
            && inputs.LensDistCenterY.isValid()
            && inputs.LensDistortionP0.isValid()
            && inputs.LensDistortionP1.isValid()
            && inputs.LensDistortionP2.isValid()
            && inputs.LensDistortionP3.isValid()
            && inputs.LensDistortionP4.isValid()
            && inputs.LensDistortionP5.isValid()
            && inputs.SrcFOV.isValid()
            && inputs.aov.isValid()
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
            inputs.LensDistCenterX.invalidateCachedPointer();
            inputs.LensDistCenterY.invalidateCachedPointer();
            inputs.LensDistortionP0.invalidateCachedPointer();
            inputs.LensDistortionP1.invalidateCachedPointer();
            inputs.LensDistortionP2.invalidateCachedPointer();
            inputs.LensDistortionP3.invalidateCachedPointer();
            inputs.LensDistortionP4.invalidateCachedPointer();
            inputs.LensDistortionP5.invalidateCachedPointer();
            inputs.SrcFOV.invalidateCachedPointer();
            inputs.aov.invalidateCachedPointer();
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
            if(attrib == inputs::LensDistCenterX.m_token) {
                inputs.LensDistCenterX.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::LensDistCenterY.m_token) {
                inputs.LensDistCenterY.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::LensDistortionP0.m_token) {
                inputs.LensDistortionP0.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::LensDistortionP1.m_token) {
                inputs.LensDistortionP1.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::LensDistortionP2.m_token) {
                inputs.LensDistortionP2.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::LensDistortionP3.m_token) {
                inputs.LensDistortionP3.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::LensDistortionP4.m_token) {
                inputs.LensDistortionP4.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::LensDistortionP5.m_token) {
                inputs.LensDistortionP5.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::SrcFOV.m_token) {
                inputs.SrcFOV.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::aov.m_token) {
                inputs.aov.invalidateCachedPointer();
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
        if( !inputs.LensDistCenterX.canVectorize()
            || !inputs.LensDistCenterY.canVectorize()
            || !inputs.LensDistortionP0.canVectorize()
            || !inputs.LensDistortionP1.canVectorize()
            || !inputs.LensDistortionP2.canVectorize()
            || !inputs.LensDistortionP3.canVectorize()
            || !inputs.LensDistortionP4.canVectorize()
            || !inputs.LensDistortionP5.canVectorize()
            || !inputs.SrcFOV.canVectorize()
            || !inputs.aov.canVectorize()
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
        if(token == inputs::LensDistCenterX.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.LensDistCenterX.setHandle(hdl);
            return;
        }
        if(token == inputs::LensDistCenterY.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.LensDistCenterY.setHandle(hdl);
            return;
        }
        if(token == inputs::LensDistortionP0.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.LensDistortionP0.setHandle(hdl);
            return;
        }
        if(token == inputs::LensDistortionP1.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.LensDistortionP1.setHandle(hdl);
            return;
        }
        if(token == inputs::LensDistortionP2.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.LensDistortionP2.setHandle(hdl);
            return;
        }
        if(token == inputs::LensDistortionP3.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.LensDistortionP3.setHandle(hdl);
            return;
        }
        if(token == inputs::LensDistortionP4.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.LensDistortionP4.setHandle(hdl);
            return;
        }
        if(token == inputs::LensDistortionP5.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.LensDistortionP5.setHandle(hdl);
            return;
        }
        if(token == inputs::SrcFOV.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.SrcFOV.setHandle(hdl);
            return;
        }
        if(token == inputs::aov.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.aov.setHandle(hdl);
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
ogn::StateManager CamPinhole2FthetaTaskNodeDatabase::sm_stateManagerCamPinhole2FthetaTaskNode;
std::tuple<int, int, int> CamPinhole2FthetaTaskNodeDatabase::sm_generatorVersionCamPinhole2FthetaTaskNode{std::make_tuple(1,79,2)};
std::tuple<int, int, int> CamPinhole2FthetaTaskNodeDatabase::sm_targetVersionCamPinhole2FthetaTaskNode{std::make_tuple(2,184,5)};
}
using namespace ICamPinhole2FthetaTaskNode;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<CamPinhole2FthetaTaskNode, CamPinhole2FthetaTaskNodeDatabase> s_registration("omni.sensors.nv.camera.CamPinhole2FthetaTaskNode", 1, "omni.sensors.nv.camera"); \
}
