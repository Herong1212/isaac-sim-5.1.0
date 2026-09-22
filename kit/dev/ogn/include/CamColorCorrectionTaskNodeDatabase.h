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

namespace CamColorCorrectionTaskNodeAttributes
{
namespace inputs
{
using Bb_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> Bb("inputs:Bb", "float", kExtendedAttributeType_Regular, 1.0f);
using Bg_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> Bg("inputs:Bg", "float", kExtendedAttributeType_Regular, 0.0f);
using Br_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> Br("inputs:Br", "float", kExtendedAttributeType_Regular, 0.0f);
using Gb_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> Gb("inputs:Gb", "float", kExtendedAttributeType_Regular, 0.0f);
using Gg_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> Gg("inputs:Gg", "float", kExtendedAttributeType_Regular, 1.0f);
using Gr_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> Gr("inputs:Gr", "float", kExtendedAttributeType_Regular, 0.0f);
using Rb_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> Rb("inputs:Rb", "float", kExtendedAttributeType_Regular, 0.0f);
using Rg_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> Rg("inputs:Rg", "float", kExtendedAttributeType_Regular, 0.0f);
using Rr_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> Rr("inputs:Rr", "float", kExtendedAttributeType_Regular, 1.0f);
using applySaturation_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> applySaturation("inputs:applySaturation", "bool", kExtendedAttributeType_Regular, false);
using black_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> black("inputs:black", "float", kExtendedAttributeType_Regular, 0.0f);
using fullwell_black_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> fullwell_black("inputs:fullwell_black", "float", kExtendedAttributeType_Regular, 1.0f);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using hydraTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTimeIn("inputs:hydraTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using output_float16_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> output_float16("inputs:output_float16", "bool", kExtendedAttributeType_Regular, false);
using redBlueSwap_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> redBlueSwap("inputs:redBlueSwap", "bool", kExtendedAttributeType_Regular, false);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using simTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTimeIn("inputs:simTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
using useInteractiveMode_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> useInteractiveMode("inputs:useInteractiveMode", "bool", kExtendedAttributeType_Regular, false);
using whiteBalance_t = const pxr::GfVec3f&;
ogn::AttributeInitializer<const pxr::GfVec3f, ogn::kOgnInput> whiteBalance("inputs:whiteBalance", "float3", kExtendedAttributeType_Regular, {1.0f,1.0f,1.0f});
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
using namespace CamColorCorrectionTaskNodeAttributes;
namespace ICamColorCorrectionTaskNode
{
// Corrects the color mapping of a camera image.
class CamColorCorrectionTaskNodeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerCamColorCorrectionTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerCamColorCorrectionTaskNode.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerCamColorCorrectionTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerCamColorCorrectionTaskNode.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerCamColorCorrectionTaskNode;
    static std::tuple<int, int, int>sm_generatorVersionCamColorCorrectionTaskNode;
    static std::tuple<int, int, int>sm_targetVersionCamColorCorrectionTaskNode;
    static constexpr size_t staticAttributeCount = 28;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : Bb{offset}
        , Bg{offset}
        , Br{offset}
        , Gb{offset}
        , Gg{offset}
        , Gr{offset}
        , Rb{offset}
        , Rg{offset}
        , Rr{offset}
        , applySaturation{offset}
        , black{offset}
        , fullwell_black{offset}
        , gpu{offset}
        , hydraTimeIn{offset}
        , output_float16{offset}
        , redBlueSwap{offset}
        , rp{offset}
        , simTimeIn{offset}
        , src{offset}
        , useInteractiveMode{offset}
        , whiteBalance{offset}
        {}
        ogn::SimpleInput<const float,ogn::kCpu> Bb;
        ogn::SimpleInput<const float,ogn::kCpu> Bg;
        ogn::SimpleInput<const float,ogn::kCpu> Br;
        ogn::SimpleInput<const float,ogn::kCpu> Gb;
        ogn::SimpleInput<const float,ogn::kCpu> Gg;
        ogn::SimpleInput<const float,ogn::kCpu> Gr;
        ogn::SimpleInput<const float,ogn::kCpu> Rb;
        ogn::SimpleInput<const float,ogn::kCpu> Rg;
        ogn::SimpleInput<const float,ogn::kCpu> Rr;
        ogn::SimpleInput<const bool,ogn::kCpu> applySaturation;
        ogn::SimpleInput<const float,ogn::kCpu> black;
        ogn::SimpleInput<const float,ogn::kCpu> fullwell_black;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTimeIn;
        ogn::SimpleInput<const bool,ogn::kCpu> output_float16;
        ogn::SimpleInput<const bool,ogn::kCpu> redBlueSwap;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const double,ogn::kCpu> simTimeIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
        ogn::SimpleInput<const bool,ogn::kCpu> useInteractiveMode;
        ogn::SimpleInput<const pxr::GfVec3f,ogn::kCpu> whiteBalance;
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
    CamColorCorrectionTaskNodeDatabase(NodeObj const& nodeObjParam)
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
    CamColorCorrectionTaskNodeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : CamColorCorrectionTaskNodeDatabase(nodeObjParam)
    {}

    //Main constructor
    CamColorCorrectionTaskNodeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::Bb.m_token, inputs::Bg.m_token, inputs::Br.m_token, inputs::Gb.m_token,
                    inputs::Gg.m_token, inputs::Gr.m_token, inputs::Rb.m_token, inputs::Rg.m_token,
                    inputs::Rr.m_token, inputs::applySaturation.m_token, inputs::black.m_token, inputs::fullwell_black.m_token,
                    inputs::gpu.m_token, inputs::hydraTimeIn.m_token, inputs::output_float16.m_token, inputs::redBlueSwap.m_token,
                    inputs::rp.m_token, inputs::simTimeIn.m_token, inputs::src.m_token, inputs::useInteractiveMode.m_token,
                    inputs::whiteBalance.m_token
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
            inputs.Bb.setContext(contextObj);
            inputs.Bb.setHandle(std::get<0>(inputDataHandles0));
            inputs.Bg.setContext(contextObj);
            inputs.Bg.setHandle(std::get<1>(inputDataHandles0));
            inputs.Br.setContext(contextObj);
            inputs.Br.setHandle(std::get<2>(inputDataHandles0));
            inputs.Gb.setContext(contextObj);
            inputs.Gb.setHandle(std::get<3>(inputDataHandles0));
            inputs.Gg.setContext(contextObj);
            inputs.Gg.setHandle(std::get<4>(inputDataHandles0));
            inputs.Gr.setContext(contextObj);
            inputs.Gr.setHandle(std::get<5>(inputDataHandles0));
            inputs.Rb.setContext(contextObj);
            inputs.Rb.setHandle(std::get<6>(inputDataHandles0));
            inputs.Rg.setContext(contextObj);
            inputs.Rg.setHandle(std::get<7>(inputDataHandles0));
            inputs.Rr.setContext(contextObj);
            inputs.Rr.setHandle(std::get<8>(inputDataHandles0));
            inputs.applySaturation.setContext(contextObj);
            inputs.applySaturation.setHandle(std::get<9>(inputDataHandles0));
            inputs.black.setContext(contextObj);
            inputs.black.setHandle(std::get<10>(inputDataHandles0));
            inputs.fullwell_black.setContext(contextObj);
            inputs.fullwell_black.setHandle(std::get<11>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<12>(inputDataHandles0));
            inputs.hydraTimeIn.setContext(contextObj);
            inputs.hydraTimeIn.setHandle(std::get<13>(inputDataHandles0));
            inputs.output_float16.setContext(contextObj);
            inputs.output_float16.setHandle(std::get<14>(inputDataHandles0));
            inputs.redBlueSwap.setContext(contextObj);
            inputs.redBlueSwap.setHandle(std::get<15>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<16>(inputDataHandles0));
            inputs.simTimeIn.setContext(contextObj);
            inputs.simTimeIn.setHandle(std::get<17>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<18>(inputDataHandles0));
            inputs.useInteractiveMode.setContext(contextObj);
            inputs.useInteractiveMode.setHandle(std::get<19>(inputDataHandles0));
            inputs.whiteBalance.setContext(contextObj);
            inputs.whiteBalance.setHandle(std::get<20>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.ColorCorrectionTaskNode");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::Bb.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::Bg.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::Br.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::Gb.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::Gg.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::Gr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::Rb.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::Rg.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::Rr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::applySaturation.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::black.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::fullwell_black.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::output_float16.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::redBlueSwap.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::useInteractiveMode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::whiteBalance.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::dest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.camera");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Corrects the color mapping of a camera image.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::Bb.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Blue_blue");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::Bg.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Blue_green");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::Br.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Blue_red");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::Gb.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Green_blue");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::Gg.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Green_green");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::Gr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Green_red");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::Rb.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Red_blue");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::Rg.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Red_green");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::Rr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Red_red");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::applySaturation.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "indicates whether black and fullwell shall be applied");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::black.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Black floor level");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::fullwell_black.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "maximal allowed value of the input array until it saturates");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::output_float16.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "indicates whether the output should be float16");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::redBlueSwap.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "indicates whether the first and the third component shall be swapped");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::useInteractiveMode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "the CCM could be changed after the intialization (Linux only), uses cuda managed memory, only for sensor setup. Don't use in simulation scenarios");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::whiteBalance.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "white balance correction of the light source");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[1.0, 1.0, 1.0]");
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
        sm_stateManagerCamColorCorrectionTaskNode.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.Bb.isValid()
            && inputs.Bg.isValid()
            && inputs.Br.isValid()
            && inputs.Gb.isValid()
            && inputs.Gg.isValid()
            && inputs.Gr.isValid()
            && inputs.Rb.isValid()
            && inputs.Rg.isValid()
            && inputs.Rr.isValid()
            && inputs.applySaturation.isValid()
            && inputs.black.isValid()
            && inputs.fullwell_black.isValid()
            && inputs.gpu.isValid()
            && inputs.hydraTimeIn.isValid()
            && inputs.output_float16.isValid()
            && inputs.redBlueSwap.isValid()
            && inputs.rp.isValid()
            && inputs.simTimeIn.isValid()
            && inputs.src.isValid()
            && inputs.useInteractiveMode.isValid()
            && inputs.whiteBalance.isValid()
            && outputs.dest.isValid()
            && outputs.gpu.isValid()
            && outputs.hydraTimeOut.isValid()
            && outputs.rp.isValid()
            && outputs.simTimeOut.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.Bb.invalidateCachedPointer();
            inputs.Bg.invalidateCachedPointer();
            inputs.Br.invalidateCachedPointer();
            inputs.Gb.invalidateCachedPointer();
            inputs.Gg.invalidateCachedPointer();
            inputs.Gr.invalidateCachedPointer();
            inputs.Rb.invalidateCachedPointer();
            inputs.Rg.invalidateCachedPointer();
            inputs.Rr.invalidateCachedPointer();
            inputs.applySaturation.invalidateCachedPointer();
            inputs.black.invalidateCachedPointer();
            inputs.fullwell_black.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.hydraTimeIn.invalidateCachedPointer();
            inputs.output_float16.invalidateCachedPointer();
            inputs.redBlueSwap.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.simTimeIn.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            inputs.useInteractiveMode.invalidateCachedPointer();
            inputs.whiteBalance.invalidateCachedPointer();
            outputs.dest.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.hydraTimeOut.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            outputs.simTimeOut.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::Bb.m_token) {
                inputs.Bb.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::Bg.m_token) {
                inputs.Bg.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::Br.m_token) {
                inputs.Br.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::Gb.m_token) {
                inputs.Gb.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::Gg.m_token) {
                inputs.Gg.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::Gr.m_token) {
                inputs.Gr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::Rb.m_token) {
                inputs.Rb.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::Rg.m_token) {
                inputs.Rg.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::Rr.m_token) {
                inputs.Rr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::applySaturation.m_token) {
                inputs.applySaturation.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::black.m_token) {
                inputs.black.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::fullwell_black.m_token) {
                inputs.fullwell_black.invalidateCachedPointer();
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
            if(attrib == inputs::output_float16.m_token) {
                inputs.output_float16.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::redBlueSwap.m_token) {
                inputs.redBlueSwap.invalidateCachedPointer();
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
            if(attrib == inputs::useInteractiveMode.m_token) {
                inputs.useInteractiveMode.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::whiteBalance.m_token) {
                inputs.whiteBalance.invalidateCachedPointer();
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
        if( !inputs.Bb.canVectorize()
            || !inputs.Bg.canVectorize()
            || !inputs.Br.canVectorize()
            || !inputs.Gb.canVectorize()
            || !inputs.Gg.canVectorize()
            || !inputs.Gr.canVectorize()
            || !inputs.Rb.canVectorize()
            || !inputs.Rg.canVectorize()
            || !inputs.Rr.canVectorize()
            || !inputs.applySaturation.canVectorize()
            || !inputs.black.canVectorize()
            || !inputs.fullwell_black.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.hydraTimeIn.canVectorize()
            || !inputs.output_float16.canVectorize()
            || !inputs.redBlueSwap.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.simTimeIn.canVectorize()
            || !inputs.src.canVectorize()
            || !inputs.useInteractiveMode.canVectorize()
            || !inputs.whiteBalance.canVectorize()
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
        if(token == inputs::Bb.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.Bb.setHandle(hdl);
            return;
        }
        if(token == inputs::Bg.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.Bg.setHandle(hdl);
            return;
        }
        if(token == inputs::Br.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.Br.setHandle(hdl);
            return;
        }
        if(token == inputs::Gb.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.Gb.setHandle(hdl);
            return;
        }
        if(token == inputs::Gg.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.Gg.setHandle(hdl);
            return;
        }
        if(token == inputs::Gr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.Gr.setHandle(hdl);
            return;
        }
        if(token == inputs::Rb.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.Rb.setHandle(hdl);
            return;
        }
        if(token == inputs::Rg.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.Rg.setHandle(hdl);
            return;
        }
        if(token == inputs::Rr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.Rr.setHandle(hdl);
            return;
        }
        if(token == inputs::applySaturation.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.applySaturation.setHandle(hdl);
            return;
        }
        if(token == inputs::black.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.black.setHandle(hdl);
            return;
        }
        if(token == inputs::fullwell_black.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.fullwell_black.setHandle(hdl);
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
        if(token == inputs::output_float16.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.output_float16.setHandle(hdl);
            return;
        }
        if(token == inputs::redBlueSwap.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.redBlueSwap.setHandle(hdl);
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
        if(token == inputs::useInteractiveMode.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.useInteractiveMode.setHandle(hdl);
            return;
        }
        if(token == inputs::whiteBalance.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.whiteBalance.setHandle(hdl);
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
ogn::StateManager CamColorCorrectionTaskNodeDatabase::sm_stateManagerCamColorCorrectionTaskNode;
std::tuple<int, int, int> CamColorCorrectionTaskNodeDatabase::sm_generatorVersionCamColorCorrectionTaskNode{std::make_tuple(1,79,2)};
std::tuple<int, int, int> CamColorCorrectionTaskNodeDatabase::sm_targetVersionCamColorCorrectionTaskNode{std::make_tuple(2,184,5)};
}
using namespace ICamColorCorrectionTaskNode;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<CamColorCorrectionTaskNode, CamColorCorrectionTaskNodeDatabase> s_registration("omni.sensors.nv.camera.ColorCorrectionTaskNode", 1, "omni.sensors.nv.camera"); \
}
