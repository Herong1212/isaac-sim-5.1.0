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

namespace CamYCbCrEncoderTaskNodeAttributes
{
namespace inputs
{
using CbCoefficentsB_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> CbCoefficentsB("inputs:CbCoefficentsB", "float", kExtendedAttributeType_Regular, 0.0f);
using CbCoefficentsG_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> CbCoefficentsG("inputs:CbCoefficentsG", "float", kExtendedAttributeType_Regular, 0.0f);
using CbCoefficentsR_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> CbCoefficentsR("inputs:CbCoefficentsR", "float", kExtendedAttributeType_Regular, 0.0f);
using CrCoefficentsB_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> CrCoefficentsB("inputs:CrCoefficentsB", "float", kExtendedAttributeType_Regular, 0.0f);
using CrCoefficentsG_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> CrCoefficentsG("inputs:CrCoefficentsG", "float", kExtendedAttributeType_Regular, 0.0f);
using CrCoefficentsR_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> CrCoefficentsR("inputs:CrCoefficentsR", "float", kExtendedAttributeType_Regular, 0.0f);
using YCbCrEncodingFormat_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> YCbCrEncodingFormat("inputs:YCbCrEncodingFormat", "token", kExtendedAttributeType_Regular);
using YCbCrEncodingStandard_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> YCbCrEncodingStandard("inputs:YCbCrEncodingStandard", "token", kExtendedAttributeType_Regular);
using YCoefficentsB_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> YCoefficentsB("inputs:YCoefficentsB", "float", kExtendedAttributeType_Regular, 0.0f);
using YCoefficentsG_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> YCoefficentsG("inputs:YCoefficentsG", "float", kExtendedAttributeType_Regular, 0.0f);
using YCoefficentsR_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> YCoefficentsR("inputs:YCoefficentsR", "float", kExtendedAttributeType_Regular, 0.0f);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using hydraTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTimeIn("inputs:hydraTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using offsetCb_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> offsetCb("inputs:offsetCb", "float", kExtendedAttributeType_Regular, 0.0f);
using offsetCr_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> offsetCr("inputs:offsetCr", "float", kExtendedAttributeType_Regular, 0.0f);
using offsetY_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> offsetY("inputs:offsetY", "float", kExtendedAttributeType_Regular, 0.0f);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using simTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTimeIn("inputs:simTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
using yuvDataType_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> yuvDataType("inputs:yuvDataType", "token", kExtendedAttributeType_Regular);
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
using namespace CamYCbCrEncoderTaskNodeAttributes;
namespace ICamYCbCrEncoderTaskNode
{
// Translates the camera rgba image to a YCbCr image for SiL FastPath.
class CamYCbCrEncoderTaskNodeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerCamYCbCrEncoderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerCamYCbCrEncoderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerCamYCbCrEncoderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerCamYCbCrEncoderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerCamYCbCrEncoderTaskNode;
    static std::tuple<int, int, int>sm_generatorVersionCamYCbCrEncoderTaskNode;
    static std::tuple<int, int, int>sm_targetVersionCamYCbCrEncoderTaskNode;
    static constexpr size_t staticAttributeCount = 27;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : CbCoefficentsB{offset}
        , CbCoefficentsG{offset}
        , CbCoefficentsR{offset}
        , CrCoefficentsB{offset}
        , CrCoefficentsG{offset}
        , CrCoefficentsR{offset}
        , YCbCrEncodingFormat{offset}
        , YCbCrEncodingStandard{offset}
        , YCoefficentsB{offset}
        , YCoefficentsG{offset}
        , YCoefficentsR{offset}
        , gpu{offset}
        , hydraTimeIn{offset}
        , offsetCb{offset}
        , offsetCr{offset}
        , offsetY{offset}
        , rp{offset}
        , simTimeIn{offset}
        , src{offset}
        , yuvDataType{offset}
        {}
        ogn::SimpleInput<const float,ogn::kCpu> CbCoefficentsB;
        ogn::SimpleInput<const float,ogn::kCpu> CbCoefficentsG;
        ogn::SimpleInput<const float,ogn::kCpu> CbCoefficentsR;
        ogn::SimpleInput<const float,ogn::kCpu> CrCoefficentsB;
        ogn::SimpleInput<const float,ogn::kCpu> CrCoefficentsG;
        ogn::SimpleInput<const float,ogn::kCpu> CrCoefficentsR;
        ogn::SimpleInput<const NameToken,ogn::kCpu> YCbCrEncodingFormat;
        ogn::SimpleInput<const NameToken,ogn::kCpu> YCbCrEncodingStandard;
        ogn::SimpleInput<const float,ogn::kCpu> YCoefficentsB;
        ogn::SimpleInput<const float,ogn::kCpu> YCoefficentsG;
        ogn::SimpleInput<const float,ogn::kCpu> YCoefficentsR;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTimeIn;
        ogn::SimpleInput<const float,ogn::kCpu> offsetCb;
        ogn::SimpleInput<const float,ogn::kCpu> offsetCr;
        ogn::SimpleInput<const float,ogn::kCpu> offsetY;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const double,ogn::kCpu> simTimeIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
        ogn::SimpleInput<const NameToken,ogn::kCpu> yuvDataType;
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
    CamYCbCrEncoderTaskNodeDatabase(NodeObj const& nodeObjParam)
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
    CamYCbCrEncoderTaskNodeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : CamYCbCrEncoderTaskNodeDatabase(nodeObjParam)
    {}

    //Main constructor
    CamYCbCrEncoderTaskNodeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::CbCoefficentsB.m_token, inputs::CbCoefficentsG.m_token, inputs::CbCoefficentsR.m_token, inputs::CrCoefficentsB.m_token,
                    inputs::CrCoefficentsG.m_token, inputs::CrCoefficentsR.m_token, inputs::YCbCrEncodingFormat.m_token, inputs::YCbCrEncodingStandard.m_token,
                    inputs::YCoefficentsB.m_token, inputs::YCoefficentsG.m_token, inputs::YCoefficentsR.m_token, inputs::gpu.m_token,
                    inputs::hydraTimeIn.m_token, inputs::offsetCb.m_token, inputs::offsetCr.m_token, inputs::offsetY.m_token,
                    inputs::rp.m_token, inputs::simTimeIn.m_token, inputs::src.m_token, inputs::yuvDataType.m_token
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
            inputs.CbCoefficentsB.setContext(contextObj);
            inputs.CbCoefficentsB.setHandle(std::get<0>(inputDataHandles0));
            inputs.CbCoefficentsG.setContext(contextObj);
            inputs.CbCoefficentsG.setHandle(std::get<1>(inputDataHandles0));
            inputs.CbCoefficentsR.setContext(contextObj);
            inputs.CbCoefficentsR.setHandle(std::get<2>(inputDataHandles0));
            inputs.CrCoefficentsB.setContext(contextObj);
            inputs.CrCoefficentsB.setHandle(std::get<3>(inputDataHandles0));
            inputs.CrCoefficentsG.setContext(contextObj);
            inputs.CrCoefficentsG.setHandle(std::get<4>(inputDataHandles0));
            inputs.CrCoefficentsR.setContext(contextObj);
            inputs.CrCoefficentsR.setHandle(std::get<5>(inputDataHandles0));
            inputs.YCbCrEncodingFormat.setContext(contextObj);
            inputs.YCbCrEncodingFormat.setHandle(std::get<6>(inputDataHandles0));
            inputs.YCbCrEncodingStandard.setContext(contextObj);
            inputs.YCbCrEncodingStandard.setHandle(std::get<7>(inputDataHandles0));
            inputs.YCoefficentsB.setContext(contextObj);
            inputs.YCoefficentsB.setHandle(std::get<8>(inputDataHandles0));
            inputs.YCoefficentsG.setContext(contextObj);
            inputs.YCoefficentsG.setHandle(std::get<9>(inputDataHandles0));
            inputs.YCoefficentsR.setContext(contextObj);
            inputs.YCoefficentsR.setHandle(std::get<10>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<11>(inputDataHandles0));
            inputs.hydraTimeIn.setContext(contextObj);
            inputs.hydraTimeIn.setHandle(std::get<12>(inputDataHandles0));
            inputs.offsetCb.setContext(contextObj);
            inputs.offsetCb.setHandle(std::get<13>(inputDataHandles0));
            inputs.offsetCr.setContext(contextObj);
            inputs.offsetCr.setHandle(std::get<14>(inputDataHandles0));
            inputs.offsetY.setContext(contextObj);
            inputs.offsetY.setHandle(std::get<15>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<16>(inputDataHandles0));
            inputs.simTimeIn.setContext(contextObj);
            inputs.simTimeIn.setHandle(std::get<17>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<18>(inputDataHandles0));
            inputs.yuvDataType.setContext(contextObj);
            inputs.yuvDataType.setHandle(std::get<19>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.CamYCbCrEncoderTaskNode");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_YCbCrEncodingFormat_token {"YUV420"};
        inputs::YCbCrEncodingFormat.setDefault(inputs_YCbCrEncodingFormat_token.asTokenC());
        static omni::fabric::Token inputs_YCbCrEncodingStandard_token {"JPEG"};
        inputs::YCbCrEncodingStandard.setDefault(inputs_YCbCrEncodingStandard_token.asTokenC());
        static omni::fabric::Token inputs_yuvDataType_token {"UINT8"};
        inputs::yuvDataType.setDefault(inputs_yuvDataType_token.asTokenC());
        inputs::CbCoefficentsB.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::CbCoefficentsG.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::CbCoefficentsR.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::CrCoefficentsB.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::CrCoefficentsG.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::CrCoefficentsR.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::YCbCrEncodingFormat.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::YCbCrEncodingStandard.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::YCoefficentsB.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::YCoefficentsG.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::YCoefficentsR.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::offsetCb.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::offsetCr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::offsetY.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::yuvDataType.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::dest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.camera");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Translates the camera rgba image to a YCbCr image for SiL FastPath.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::CbCoefficentsB.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "B component weight to calc Cb for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::CbCoefficentsG.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "G component weight to calc Cb for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::CbCoefficentsR.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "R component weight to calc Cb for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::CrCoefficentsB.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "B component weight to calc Cr for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::CrCoefficentsG.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "G component weight to calc Cr for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::CrCoefficentsR.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "R component weight to calc Cr for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::YCbCrEncodingFormat.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Format of the YCbCr: Could be YUV444,YUV422 or YUV420 ");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"YUV420\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::YCbCrEncodingStandard.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Standard of the RGB->YCbCr transcoding: Could be BT.601, BT.709, BT.2020, JPEG or custom ");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"JPEG\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::YCoefficentsB.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "B component weight to calc Y for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::YCoefficentsG.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "G component weight to calc Y for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::YCoefficentsR.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "R component weight to calc Y for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::offsetCb.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cb offset for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::offsetCr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cr offset for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::offsetY.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Y offset for custom YcbCr calculation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::yuvDataType.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "YUV output data type UINT8 or FLOAT16");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"UINT8\"");
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
        sm_stateManagerCamYCbCrEncoderTaskNode.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.CbCoefficentsB.isValid()
            && inputs.CbCoefficentsG.isValid()
            && inputs.CbCoefficentsR.isValid()
            && inputs.CrCoefficentsB.isValid()
            && inputs.CrCoefficentsG.isValid()
            && inputs.CrCoefficentsR.isValid()
            && inputs.YCbCrEncodingFormat.isValid()
            && inputs.YCbCrEncodingStandard.isValid()
            && inputs.YCoefficentsB.isValid()
            && inputs.YCoefficentsG.isValid()
            && inputs.YCoefficentsR.isValid()
            && inputs.gpu.isValid()
            && inputs.hydraTimeIn.isValid()
            && inputs.offsetCb.isValid()
            && inputs.offsetCr.isValid()
            && inputs.offsetY.isValid()
            && inputs.rp.isValid()
            && inputs.simTimeIn.isValid()
            && inputs.src.isValid()
            && inputs.yuvDataType.isValid()
            && outputs.dest.isValid()
            && outputs.gpu.isValid()
            && outputs.hydraTimeOut.isValid()
            && outputs.rp.isValid()
            && outputs.simTimeOut.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.CbCoefficentsB.invalidateCachedPointer();
            inputs.CbCoefficentsG.invalidateCachedPointer();
            inputs.CbCoefficentsR.invalidateCachedPointer();
            inputs.CrCoefficentsB.invalidateCachedPointer();
            inputs.CrCoefficentsG.invalidateCachedPointer();
            inputs.CrCoefficentsR.invalidateCachedPointer();
            inputs.YCbCrEncodingFormat.invalidateCachedPointer();
            inputs.YCbCrEncodingStandard.invalidateCachedPointer();
            inputs.YCoefficentsB.invalidateCachedPointer();
            inputs.YCoefficentsG.invalidateCachedPointer();
            inputs.YCoefficentsR.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.hydraTimeIn.invalidateCachedPointer();
            inputs.offsetCb.invalidateCachedPointer();
            inputs.offsetCr.invalidateCachedPointer();
            inputs.offsetY.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.simTimeIn.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            inputs.yuvDataType.invalidateCachedPointer();
            outputs.dest.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.hydraTimeOut.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            outputs.simTimeOut.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::CbCoefficentsB.m_token) {
                inputs.CbCoefficentsB.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::CbCoefficentsG.m_token) {
                inputs.CbCoefficentsG.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::CbCoefficentsR.m_token) {
                inputs.CbCoefficentsR.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::CrCoefficentsB.m_token) {
                inputs.CrCoefficentsB.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::CrCoefficentsG.m_token) {
                inputs.CrCoefficentsG.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::CrCoefficentsR.m_token) {
                inputs.CrCoefficentsR.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::YCbCrEncodingFormat.m_token) {
                inputs.YCbCrEncodingFormat.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::YCbCrEncodingStandard.m_token) {
                inputs.YCbCrEncodingStandard.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::YCoefficentsB.m_token) {
                inputs.YCoefficentsB.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::YCoefficentsG.m_token) {
                inputs.YCoefficentsG.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::YCoefficentsR.m_token) {
                inputs.YCoefficentsR.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hydraTimeIn.m_token) {
                inputs.hydraTimeIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::offsetCb.m_token) {
                inputs.offsetCb.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::offsetCr.m_token) {
                inputs.offsetCr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::offsetY.m_token) {
                inputs.offsetY.invalidateCachedPointer();
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
            if(attrib == inputs::yuvDataType.m_token) {
                inputs.yuvDataType.invalidateCachedPointer();
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
        if( !inputs.CbCoefficentsB.canVectorize()
            || !inputs.CbCoefficentsG.canVectorize()
            || !inputs.CbCoefficentsR.canVectorize()
            || !inputs.CrCoefficentsB.canVectorize()
            || !inputs.CrCoefficentsG.canVectorize()
            || !inputs.CrCoefficentsR.canVectorize()
            || !inputs.YCbCrEncodingFormat.canVectorize()
            || !inputs.YCbCrEncodingStandard.canVectorize()
            || !inputs.YCoefficentsB.canVectorize()
            || !inputs.YCoefficentsG.canVectorize()
            || !inputs.YCoefficentsR.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.hydraTimeIn.canVectorize()
            || !inputs.offsetCb.canVectorize()
            || !inputs.offsetCr.canVectorize()
            || !inputs.offsetY.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.simTimeIn.canVectorize()
            || !inputs.src.canVectorize()
            || !inputs.yuvDataType.canVectorize()
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
        if(token == inputs::CbCoefficentsB.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.CbCoefficentsB.setHandle(hdl);
            return;
        }
        if(token == inputs::CbCoefficentsG.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.CbCoefficentsG.setHandle(hdl);
            return;
        }
        if(token == inputs::CbCoefficentsR.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.CbCoefficentsR.setHandle(hdl);
            return;
        }
        if(token == inputs::CrCoefficentsB.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.CrCoefficentsB.setHandle(hdl);
            return;
        }
        if(token == inputs::CrCoefficentsG.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.CrCoefficentsG.setHandle(hdl);
            return;
        }
        if(token == inputs::CrCoefficentsR.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.CrCoefficentsR.setHandle(hdl);
            return;
        }
        if(token == inputs::YCbCrEncodingFormat.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.YCbCrEncodingFormat.setHandle(hdl);
            return;
        }
        if(token == inputs::YCbCrEncodingStandard.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.YCbCrEncodingStandard.setHandle(hdl);
            return;
        }
        if(token == inputs::YCoefficentsB.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.YCoefficentsB.setHandle(hdl);
            return;
        }
        if(token == inputs::YCoefficentsG.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.YCoefficentsG.setHandle(hdl);
            return;
        }
        if(token == inputs::YCoefficentsR.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.YCoefficentsR.setHandle(hdl);
            return;
        }
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::hydraTimeIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hydraTimeIn.setHandle(hdl);
            return;
        }
        if(token == inputs::offsetCb.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.offsetCb.setHandle(hdl);
            return;
        }
        if(token == inputs::offsetCr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.offsetCr.setHandle(hdl);
            return;
        }
        if(token == inputs::offsetY.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.offsetY.setHandle(hdl);
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
        if(token == inputs::yuvDataType.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.yuvDataType.setHandle(hdl);
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
ogn::StateManager CamYCbCrEncoderTaskNodeDatabase::sm_stateManagerCamYCbCrEncoderTaskNode;
std::tuple<int, int, int> CamYCbCrEncoderTaskNodeDatabase::sm_generatorVersionCamYCbCrEncoderTaskNode{std::make_tuple(1,79,2)};
std::tuple<int, int, int> CamYCbCrEncoderTaskNodeDatabase::sm_targetVersionCamYCbCrEncoderTaskNode{std::make_tuple(2,184,5)};
}
using namespace ICamYCbCrEncoderTaskNode;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<CamYCbCrEncoderTaskNode, CamYCbCrEncoderTaskNodeDatabase> s_registration("omni.sensors.nv.camera.CamYCbCrEncoderTaskNode", 1, "omni.sensors.nv.camera"); \
}
