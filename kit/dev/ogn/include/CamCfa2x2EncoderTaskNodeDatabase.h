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

namespace CamCfa2x2EncoderTaskNodeAttributes
{
namespace inputs
{
using CFA_CF00_t = const pxr::GfVec3f&;
ogn::AttributeInitializer<const pxr::GfVec3f, ogn::kOgnInput> CFA_CF00("inputs:CFA_CF00", "float3", kExtendedAttributeType_Regular, {0.0f,0.0f,0.0f});
using CFA_CF01_t = const pxr::GfVec3f&;
ogn::AttributeInitializer<const pxr::GfVec3f, ogn::kOgnInput> CFA_CF01("inputs:CFA_CF01", "float3", kExtendedAttributeType_Regular, {0.0f,0.0f,0.0f});
using CFA_CF10_t = const pxr::GfVec3f&;
ogn::AttributeInitializer<const pxr::GfVec3f, ogn::kOgnInput> CFA_CF10("inputs:CFA_CF10", "float3", kExtendedAttributeType_Regular, {0.0f,0.0f,0.0f});
using CFA_CF11_t = const pxr::GfVec3f&;
ogn::AttributeInitializer<const pxr::GfVec3f, ogn::kOgnInput> CFA_CF11("inputs:CFA_CF11", "float3", kExtendedAttributeType_Regular, {0.0f,0.0f,0.0f});
using cfaSemantic_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> cfaSemantic("inputs:cfaSemantic", "token", kExtendedAttributeType_Regular);
using embeddedSrc_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> embeddedSrc("inputs:embeddedSrc", "uint64", kExtendedAttributeType_Regular, 0);
using flipHorizontal_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> flipHorizontal("inputs:flipHorizontal", "bool", kExtendedAttributeType_Regular, false);
using flipVertical_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> flipVertical("inputs:flipVertical", "bool", kExtendedAttributeType_Regular, false);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using hydraTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTimeIn("inputs:hydraTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using maximalValue_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> maximalValue("inputs:maximalValue", "uint64", kExtendedAttributeType_Regular, 16777215);
using outputDataTypeFormat_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> outputDataTypeFormat("inputs:outputDataTypeFormat", "token", kExtendedAttributeType_Regular);
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
using embeddedDest_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> embeddedDest("outputs:embeddedDest", "uint64", kExtendedAttributeType_Regular, 0);
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
using namespace CamCfa2x2EncoderTaskNodeAttributes;
namespace ICamCfa2x2EncoderTaskNode
{
// Translates the camera rgba image to a CFA image
class CamCfa2x2EncoderTaskNodeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerCamCfa2x2EncoderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerCamCfa2x2EncoderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerCamCfa2x2EncoderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerCamCfa2x2EncoderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerCamCfa2x2EncoderTaskNode;
    static std::tuple<int, int, int>sm_generatorVersionCamCfa2x2EncoderTaskNode;
    static std::tuple<int, int, int>sm_targetVersionCamCfa2x2EncoderTaskNode;
    static constexpr size_t staticAttributeCount = 23;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : CFA_CF00{offset}
        , CFA_CF01{offset}
        , CFA_CF10{offset}
        , CFA_CF11{offset}
        , cfaSemantic{offset}
        , embeddedSrc{offset}
        , flipHorizontal{offset}
        , flipVertical{offset}
        , gpu{offset}
        , hydraTimeIn{offset}
        , maximalValue{offset}
        , outputDataTypeFormat{offset}
        , rp{offset}
        , simTimeIn{offset}
        , src{offset}
        {}
        ogn::SimpleInput<const pxr::GfVec3f,ogn::kCpu> CFA_CF00;
        ogn::SimpleInput<const pxr::GfVec3f,ogn::kCpu> CFA_CF01;
        ogn::SimpleInput<const pxr::GfVec3f,ogn::kCpu> CFA_CF10;
        ogn::SimpleInput<const pxr::GfVec3f,ogn::kCpu> CFA_CF11;
        ogn::SimpleInput<const NameToken,ogn::kCpu> cfaSemantic;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> embeddedSrc;
        ogn::SimpleInput<const bool,ogn::kCpu> flipHorizontal;
        ogn::SimpleInput<const bool,ogn::kCpu> flipVertical;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTimeIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> maximalValue;
        ogn::SimpleInput<const NameToken,ogn::kCpu> outputDataTypeFormat;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const double,ogn::kCpu> simTimeIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : dest{offset}
        , embeddedDest{offset}
        , gpu{offset}
        , hydraTimeOut{offset}
        , rp{offset}
        , simTimeOut{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> dest;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> embeddedDest;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> gpu;
        ogn::SimpleOutput<double,ogn::kCpu> hydraTimeOut;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> rp;
        ogn::SimpleOutput<double,ogn::kCpu> simTimeOut;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    CamCfa2x2EncoderTaskNodeDatabase(NodeObj const& nodeObjParam)
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
    CamCfa2x2EncoderTaskNodeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : CamCfa2x2EncoderTaskNodeDatabase(nodeObjParam)
    {}

    //Main constructor
    CamCfa2x2EncoderTaskNodeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::CFA_CF00.m_token, inputs::CFA_CF01.m_token, inputs::CFA_CF10.m_token, inputs::CFA_CF11.m_token,
                    inputs::cfaSemantic.m_token, inputs::embeddedSrc.m_token, inputs::flipHorizontal.m_token, inputs::flipVertical.m_token,
                    inputs::gpu.m_token, inputs::hydraTimeIn.m_token, inputs::maximalValue.m_token, inputs::outputDataTypeFormat.m_token,
                    inputs::rp.m_token, inputs::simTimeIn.m_token, inputs::src.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::dest.m_token, outputs::embeddedDest.m_token, outputs::gpu.m_token, outputs::hydraTimeOut.m_token,
                    outputs::rp.m_token, outputs::simTimeOut.m_token
                )
            , kAccordingToContextIndex);
            inputs.CFA_CF00.setContext(contextObj);
            inputs.CFA_CF00.setHandle(std::get<0>(inputDataHandles0));
            inputs.CFA_CF01.setContext(contextObj);
            inputs.CFA_CF01.setHandle(std::get<1>(inputDataHandles0));
            inputs.CFA_CF10.setContext(contextObj);
            inputs.CFA_CF10.setHandle(std::get<2>(inputDataHandles0));
            inputs.CFA_CF11.setContext(contextObj);
            inputs.CFA_CF11.setHandle(std::get<3>(inputDataHandles0));
            inputs.cfaSemantic.setContext(contextObj);
            inputs.cfaSemantic.setHandle(std::get<4>(inputDataHandles0));
            inputs.embeddedSrc.setContext(contextObj);
            inputs.embeddedSrc.setHandle(std::get<5>(inputDataHandles0));
            inputs.flipHorizontal.setContext(contextObj);
            inputs.flipHorizontal.setHandle(std::get<6>(inputDataHandles0));
            inputs.flipVertical.setContext(contextObj);
            inputs.flipVertical.setHandle(std::get<7>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<8>(inputDataHandles0));
            inputs.hydraTimeIn.setContext(contextObj);
            inputs.hydraTimeIn.setHandle(std::get<9>(inputDataHandles0));
            inputs.maximalValue.setContext(contextObj);
            inputs.maximalValue.setHandle(std::get<10>(inputDataHandles0));
            inputs.outputDataTypeFormat.setContext(contextObj);
            inputs.outputDataTypeFormat.setHandle(std::get<11>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<12>(inputDataHandles0));
            inputs.simTimeIn.setContext(contextObj);
            inputs.simTimeIn.setHandle(std::get<13>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<14>(inputDataHandles0));
            outputs.dest.setContext(contextObj);
            outputs.dest.setHandle(std::get<0>(outputDataHandles0));
            outputs.embeddedDest.setContext(contextObj);
            outputs.embeddedDest.setHandle(std::get<1>(outputDataHandles0));
            outputs.gpu.setContext(contextObj);
            outputs.gpu.setHandle(std::get<2>(outputDataHandles0));
            outputs.hydraTimeOut.setContext(contextObj);
            outputs.hydraTimeOut.setHandle(std::get<3>(outputDataHandles0));
            outputs.rp.setContext(contextObj);
            outputs.rp.setHandle(std::get<4>(outputDataHandles0));
            outputs.simTimeOut.setContext(contextObj);
            outputs.simTimeOut.setHandle(std::get<5>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.CamCfa2x2EncoderTaskNode");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_cfaSemantic_token {"RGGB"};
        inputs::cfaSemantic.setDefault(inputs_cfaSemantic_token.asTokenC());
        static omni::fabric::Token inputs_outputDataTypeFormat_token {"UINT32"};
        inputs::outputDataTypeFormat.setDefault(inputs_outputDataTypeFormat_token.asTokenC());
        inputs::CFA_CF00.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::CFA_CF01.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::CFA_CF10.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::CFA_CF11.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cfaSemantic.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::embeddedSrc.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::flipHorizontal.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::flipVertical.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::maximalValue.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::outputDataTypeFormat.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::dest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::embeddedDest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.camera");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Translates the camera rgba image to a CFA image");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::CFA_CF00.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Top Left Pixel of 2x2 Color Filter Array");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[0.0, 0.0, 0.0]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::CFA_CF01.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Top Right Pixel of 2x2 Color Filter Array");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[0.0, 0.0, 0.0]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::CFA_CF10.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Bottom Left Pixel of 2x2 Color Filter Array");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[0.0, 0.0, 0.0]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::CFA_CF11.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Bottom Right Pixel of 2x2 Color Filter Array");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[0.0, 0.0, 0.0]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cfaSemantic.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Semantic of the Color Filter array: RGGB, GRBG, BGGR, RCCB, CRBC, BCCR, RCCC, CCCR or CRCC");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"RGGB\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::embeddedSrc.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Embedded Data Lines Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::flipHorizontal.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "horizonal mirroring");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::flipVertical.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "vertical mirroring");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::maximalValue.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "the maximal value of the internal processing (20bits : 1048575) (passthrough : 1) (default for 24 bits: 16777215)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "16777215");
        attr = iNode->getAttributeByToken(nodeObj, inputs::outputDataTypeFormat.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Data Type of the output format: [FLOAT32, UINT32]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"UINT32\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::dest.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Destination Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::embeddedDest.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Embedded Data Lines Destination Buffer");
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
        sm_stateManagerCamCfa2x2EncoderTaskNode.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.CFA_CF00.isValid()
            && inputs.CFA_CF01.isValid()
            && inputs.CFA_CF10.isValid()
            && inputs.CFA_CF11.isValid()
            && inputs.cfaSemantic.isValid()
            && inputs.embeddedSrc.isValid()
            && inputs.flipHorizontal.isValid()
            && inputs.flipVertical.isValid()
            && inputs.gpu.isValid()
            && inputs.hydraTimeIn.isValid()
            && inputs.maximalValue.isValid()
            && inputs.outputDataTypeFormat.isValid()
            && inputs.rp.isValid()
            && inputs.simTimeIn.isValid()
            && inputs.src.isValid()
            && outputs.dest.isValid()
            && outputs.embeddedDest.isValid()
            && outputs.gpu.isValid()
            && outputs.hydraTimeOut.isValid()
            && outputs.rp.isValid()
            && outputs.simTimeOut.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.CFA_CF00.invalidateCachedPointer();
            inputs.CFA_CF01.invalidateCachedPointer();
            inputs.CFA_CF10.invalidateCachedPointer();
            inputs.CFA_CF11.invalidateCachedPointer();
            inputs.cfaSemantic.invalidateCachedPointer();
            inputs.embeddedSrc.invalidateCachedPointer();
            inputs.flipHorizontal.invalidateCachedPointer();
            inputs.flipVertical.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.hydraTimeIn.invalidateCachedPointer();
            inputs.maximalValue.invalidateCachedPointer();
            inputs.outputDataTypeFormat.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.simTimeIn.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            outputs.dest.invalidateCachedPointer();
            outputs.embeddedDest.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.hydraTimeOut.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            outputs.simTimeOut.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::CFA_CF00.m_token) {
                inputs.CFA_CF00.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::CFA_CF01.m_token) {
                inputs.CFA_CF01.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::CFA_CF10.m_token) {
                inputs.CFA_CF10.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::CFA_CF11.m_token) {
                inputs.CFA_CF11.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cfaSemantic.m_token) {
                inputs.cfaSemantic.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::embeddedSrc.m_token) {
                inputs.embeddedSrc.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::flipHorizontal.m_token) {
                inputs.flipHorizontal.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::flipVertical.m_token) {
                inputs.flipVertical.invalidateCachedPointer();
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
            if(attrib == inputs::maximalValue.m_token) {
                inputs.maximalValue.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::outputDataTypeFormat.m_token) {
                inputs.outputDataTypeFormat.invalidateCachedPointer();
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
            if(attrib == outputs::embeddedDest.m_token) {
                outputs.embeddedDest.invalidateCachedPointer();
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
        if( !inputs.CFA_CF00.canVectorize()
            || !inputs.CFA_CF01.canVectorize()
            || !inputs.CFA_CF10.canVectorize()
            || !inputs.CFA_CF11.canVectorize()
            || !inputs.cfaSemantic.canVectorize()
            || !inputs.embeddedSrc.canVectorize()
            || !inputs.flipHorizontal.canVectorize()
            || !inputs.flipVertical.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.hydraTimeIn.canVectorize()
            || !inputs.maximalValue.canVectorize()
            || !inputs.outputDataTypeFormat.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.simTimeIn.canVectorize()
            || !inputs.src.canVectorize()
            || !outputs.dest.canVectorize()
            || !outputs.embeddedDest.canVectorize()
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
        if(token == inputs::CFA_CF00.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.CFA_CF00.setHandle(hdl);
            return;
        }
        if(token == inputs::CFA_CF01.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.CFA_CF01.setHandle(hdl);
            return;
        }
        if(token == inputs::CFA_CF10.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.CFA_CF10.setHandle(hdl);
            return;
        }
        if(token == inputs::CFA_CF11.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.CFA_CF11.setHandle(hdl);
            return;
        }
        if(token == inputs::cfaSemantic.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cfaSemantic.setHandle(hdl);
            return;
        }
        if(token == inputs::embeddedSrc.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.embeddedSrc.setHandle(hdl);
            return;
        }
        if(token == inputs::flipHorizontal.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.flipHorizontal.setHandle(hdl);
            return;
        }
        if(token == inputs::flipVertical.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.flipVertical.setHandle(hdl);
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
        if(token == inputs::maximalValue.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.maximalValue.setHandle(hdl);
            return;
        }
        if(token == inputs::outputDataTypeFormat.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.outputDataTypeFormat.setHandle(hdl);
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
        if(token == outputs::embeddedDest.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.embeddedDest.setHandle(hdl);
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
ogn::StateManager CamCfa2x2EncoderTaskNodeDatabase::sm_stateManagerCamCfa2x2EncoderTaskNode;
std::tuple<int, int, int> CamCfa2x2EncoderTaskNodeDatabase::sm_generatorVersionCamCfa2x2EncoderTaskNode{std::make_tuple(1,79,2)};
std::tuple<int, int, int> CamCfa2x2EncoderTaskNodeDatabase::sm_targetVersionCamCfa2x2EncoderTaskNode{std::make_tuple(2,184,5)};
}
using namespace ICamCfa2x2EncoderTaskNode;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<CamCfa2x2EncoderTaskNode, CamCfa2x2EncoderTaskNodeDatabase> s_registration("omni.sensors.nv.camera.CamCfa2x2EncoderTaskNode", 1, "omni.sensors.nv.camera"); \
}
