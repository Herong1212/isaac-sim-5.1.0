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

namespace CamDefaultEmbeddedLinesTaskNodeAttributes
{
namespace inputs
{
using EmbeddedLineEncoder_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> EmbeddedLineEncoder("inputs:EmbeddedLineEncoder", "token", kExtendedAttributeType_Regular);
using embedFrameID_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> embedFrameID("inputs:embedFrameID", "bool", kExtendedAttributeType_Regular, false);
using embedFrameIDOffset_t = const int64_t&;
ogn::AttributeInitializer<const int64_t, ogn::kOgnInput> embedFrameIDOffset("inputs:embedFrameIDOffset", "int64", kExtendedAttributeType_Regular, 0);
using embedTimecode_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> embedTimecode("inputs:embedTimecode", "bool", kExtendedAttributeType_Regular, false);
using embeddedBottomLines_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> embeddedBottomLines("inputs:embeddedBottomLines", "int", kExtendedAttributeType_Regular, 0);
using embeddedDataFilepath_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> embeddedDataFilepath("inputs:embeddedDataFilepath", "token", kExtendedAttributeType_Regular);
using embeddedTimecodeOffset_t = const int64_t&;
ogn::AttributeInitializer<const int64_t, ogn::kOgnInput> embeddedTimecodeOffset("inputs:embeddedTimecodeOffset", "int64", kExtendedAttributeType_Regular, 0);
using embeddedTopLines_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> embeddedTopLines("inputs:embeddedTopLines", "int", kExtendedAttributeType_Regular, 0);
using externalTimeOfSimFrameIn_t = const int64_t&;
ogn::AttributeInitializer<const int64_t, ogn::kOgnInput> externalTimeOfSimFrameIn("inputs:externalTimeOfSimFrameIn", "int64", kExtendedAttributeType_Regular, 0);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using hydraTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTimeIn("inputs:hydraTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using rawEncoding_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> rawEncoding("inputs:rawEncoding", "token", kExtendedAttributeType_Regular);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using simTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTimeIn("inputs:simTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
using timecodeIn_t = const int64_t&;
ogn::AttributeInitializer<const int64_t, ogn::kOgnInput> timecodeIn("inputs:timecodeIn", "int64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using dest_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> dest("outputs:dest", "uint64", kExtendedAttributeType_Regular);
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
using namespace CamDefaultEmbeddedLinesTaskNodeAttributes;
namespace ICamDefaultEmbeddedLinesTaskNode
{
// Loads a preset of embedded line registers
class CamDefaultEmbeddedLinesTaskNodeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerCamDefaultEmbeddedLinesTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerCamDefaultEmbeddedLinesTaskNode.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerCamDefaultEmbeddedLinesTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerCamDefaultEmbeddedLinesTaskNode.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerCamDefaultEmbeddedLinesTaskNode;
    static std::tuple<int, int, int>sm_generatorVersionCamDefaultEmbeddedLinesTaskNode;
    static std::tuple<int, int, int>sm_targetVersionCamDefaultEmbeddedLinesTaskNode;
    static constexpr size_t staticAttributeCount = 24;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : EmbeddedLineEncoder{offset}
        , embedFrameID{offset}
        , embedFrameIDOffset{offset}
        , embedTimecode{offset}
        , embeddedBottomLines{offset}
        , embeddedDataFilepath{offset}
        , embeddedTimecodeOffset{offset}
        , embeddedTopLines{offset}
        , externalTimeOfSimFrameIn{offset}
        , gpu{offset}
        , hydraTimeIn{offset}
        , rawEncoding{offset}
        , rp{offset}
        , simTimeIn{offset}
        , src{offset}
        , timecodeIn{offset}
        {}
        ogn::SimpleInput<const NameToken,ogn::kCpu> EmbeddedLineEncoder;
        ogn::SimpleInput<const bool,ogn::kCpu> embedFrameID;
        ogn::SimpleInput<const int64_t,ogn::kCpu> embedFrameIDOffset;
        ogn::SimpleInput<const bool,ogn::kCpu> embedTimecode;
        ogn::SimpleInput<const int,ogn::kCpu> embeddedBottomLines;
        ogn::SimpleInput<const NameToken,ogn::kCpu> embeddedDataFilepath;
        ogn::SimpleInput<const int64_t,ogn::kCpu> embeddedTimecodeOffset;
        ogn::SimpleInput<const int,ogn::kCpu> embeddedTopLines;
        ogn::SimpleInput<const int64_t,ogn::kCpu> externalTimeOfSimFrameIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTimeIn;
        ogn::SimpleInput<const NameToken,ogn::kCpu> rawEncoding;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const double,ogn::kCpu> simTimeIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
        ogn::SimpleInput<const int64_t,ogn::kCpu> timecodeIn;
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
    CamDefaultEmbeddedLinesTaskNodeDatabase(NodeObj const& nodeObjParam)
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
    CamDefaultEmbeddedLinesTaskNodeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : CamDefaultEmbeddedLinesTaskNodeDatabase(nodeObjParam)
    {}

    //Main constructor
    CamDefaultEmbeddedLinesTaskNodeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::EmbeddedLineEncoder.m_token, inputs::embedFrameID.m_token, inputs::embedFrameIDOffset.m_token, inputs::embedTimecode.m_token,
                    inputs::embeddedBottomLines.m_token, inputs::embeddedDataFilepath.m_token, inputs::embeddedTimecodeOffset.m_token, inputs::embeddedTopLines.m_token,
                    inputs::externalTimeOfSimFrameIn.m_token, inputs::gpu.m_token, inputs::hydraTimeIn.m_token, inputs::rawEncoding.m_token,
                    inputs::rp.m_token, inputs::simTimeIn.m_token, inputs::src.m_token, inputs::timecodeIn.m_token
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
            inputs.EmbeddedLineEncoder.setContext(contextObj);
            inputs.EmbeddedLineEncoder.setHandle(std::get<0>(inputDataHandles0));
            inputs.embedFrameID.setContext(contextObj);
            inputs.embedFrameID.setHandle(std::get<1>(inputDataHandles0));
            inputs.embedFrameIDOffset.setContext(contextObj);
            inputs.embedFrameIDOffset.setHandle(std::get<2>(inputDataHandles0));
            inputs.embedTimecode.setContext(contextObj);
            inputs.embedTimecode.setHandle(std::get<3>(inputDataHandles0));
            inputs.embeddedBottomLines.setContext(contextObj);
            inputs.embeddedBottomLines.setHandle(std::get<4>(inputDataHandles0));
            inputs.embeddedDataFilepath.setContext(contextObj);
            inputs.embeddedDataFilepath.setHandle(std::get<5>(inputDataHandles0));
            inputs.embeddedTimecodeOffset.setContext(contextObj);
            inputs.embeddedTimecodeOffset.setHandle(std::get<6>(inputDataHandles0));
            inputs.embeddedTopLines.setContext(contextObj);
            inputs.embeddedTopLines.setHandle(std::get<7>(inputDataHandles0));
            inputs.externalTimeOfSimFrameIn.setContext(contextObj);
            inputs.externalTimeOfSimFrameIn.setHandle(std::get<8>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<9>(inputDataHandles0));
            inputs.hydraTimeIn.setContext(contextObj);
            inputs.hydraTimeIn.setHandle(std::get<10>(inputDataHandles0));
            inputs.rawEncoding.setContext(contextObj);
            inputs.rawEncoding.setHandle(std::get<11>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<12>(inputDataHandles0));
            inputs.simTimeIn.setContext(contextObj);
            inputs.simTimeIn.setHandle(std::get<13>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<14>(inputDataHandles0));
            inputs.timecodeIn.setContext(contextObj);
            inputs.timecodeIn.setHandle(std::get<15>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.CamDefaultEmbeddedLinesTask");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_EmbeddedLineEncoder_token {"NONE"};
        inputs::EmbeddedLineEncoder.setDefault(inputs_EmbeddedLineEncoder_token.asTokenC());
        static omni::fabric::Token inputs_embeddedDataFilepath_token {"/tmp/AR0231_daylight.raw"};
        inputs::embeddedDataFilepath.setDefault(inputs_embeddedDataFilepath_token.asTokenC());
        static omni::fabric::Token inputs_rawEncoding_token {"RAW12"};
        inputs::rawEncoding.setDefault(inputs_rawEncoding_token.asTokenC());
        inputs::EmbeddedLineEncoder.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::embedFrameID.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::embedFrameIDOffset.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::embedTimecode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::embeddedBottomLines.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::embeddedDataFilepath.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::embeddedTimecodeOffset.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::embeddedTopLines.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::externalTimeOfSimFrameIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rawEncoding.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timecodeIn.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::dest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::embeddedDest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.camera");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Loads a preset of embedded line registers");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::EmbeddedLineEncoder.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Encoder for the embedded Lines : Values: NONE, IMX390_DEFAULT, IMX728_DEFAULT, IMX623_DEFAULT, AR820_DEFAULT, defaults to NONE");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"NONE\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::embedFrameID.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "boolean, whether frame ID shall be embedded into the embedded lines (overwrites camera type default)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::embedFrameIDOffset.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "offset of the frame ID");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::embedTimecode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "boolean, whether timecode shall be embedded into the embedded lines  (overwrites camera type default)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::embeddedBottomLines.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "number of embedded bottom lines");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::embeddedDataFilepath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "File path to the embedded line data file");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"/tmp/AR0231_daylight.raw\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::embeddedTimecodeOffset.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "offset of the timecode in [us]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::embeddedTopLines.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "number of embedded top lines");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::externalTimeOfSimFrameIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "externalTimeOfSimFrameIn input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rawEncoding.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Raw Encoding of the embedded registers RAW12, RAW16, RAW20, RAW24");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"RAW12\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::timecodeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::dest.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Destination Buffer");
        attr = iNode->getAttributeByToken(nodeObj, outputs::embeddedDest.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Embedded Data Lines Destination Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundationsOut");
        attr = iNode->getAttributeByToken(nodeObj, outputs::hydraTimeOut.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp output in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
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
        sm_stateManagerCamDefaultEmbeddedLinesTaskNode.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.EmbeddedLineEncoder.isValid()
            && inputs.embedFrameID.isValid()
            && inputs.embedFrameIDOffset.isValid()
            && inputs.embedTimecode.isValid()
            && inputs.embeddedBottomLines.isValid()
            && inputs.embeddedDataFilepath.isValid()
            && inputs.embeddedTimecodeOffset.isValid()
            && inputs.embeddedTopLines.isValid()
            && inputs.externalTimeOfSimFrameIn.isValid()
            && inputs.gpu.isValid()
            && inputs.hydraTimeIn.isValid()
            && inputs.rawEncoding.isValid()
            && inputs.rp.isValid()
            && inputs.simTimeIn.isValid()
            && inputs.src.isValid()
            && inputs.timecodeIn.isValid()
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
            inputs.EmbeddedLineEncoder.invalidateCachedPointer();
            inputs.embedFrameID.invalidateCachedPointer();
            inputs.embedFrameIDOffset.invalidateCachedPointer();
            inputs.embedTimecode.invalidateCachedPointer();
            inputs.embeddedBottomLines.invalidateCachedPointer();
            inputs.embeddedDataFilepath.invalidateCachedPointer();
            inputs.embeddedTimecodeOffset.invalidateCachedPointer();
            inputs.embeddedTopLines.invalidateCachedPointer();
            inputs.externalTimeOfSimFrameIn.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.hydraTimeIn.invalidateCachedPointer();
            inputs.rawEncoding.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.simTimeIn.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            inputs.timecodeIn.invalidateCachedPointer();
            outputs.dest.invalidateCachedPointer();
            outputs.embeddedDest.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.hydraTimeOut.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            outputs.simTimeOut.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::EmbeddedLineEncoder.m_token) {
                inputs.EmbeddedLineEncoder.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::embedFrameID.m_token) {
                inputs.embedFrameID.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::embedFrameIDOffset.m_token) {
                inputs.embedFrameIDOffset.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::embedTimecode.m_token) {
                inputs.embedTimecode.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::embeddedBottomLines.m_token) {
                inputs.embeddedBottomLines.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::embeddedDataFilepath.m_token) {
                inputs.embeddedDataFilepath.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::embeddedTimecodeOffset.m_token) {
                inputs.embeddedTimecodeOffset.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::embeddedTopLines.m_token) {
                inputs.embeddedTopLines.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::externalTimeOfSimFrameIn.m_token) {
                inputs.externalTimeOfSimFrameIn.invalidateCachedPointer();
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
            if(attrib == inputs::rawEncoding.m_token) {
                inputs.rawEncoding.invalidateCachedPointer();
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
            if(attrib == inputs::timecodeIn.m_token) {
                inputs.timecodeIn.invalidateCachedPointer();
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
        if( !inputs.EmbeddedLineEncoder.canVectorize()
            || !inputs.embedFrameID.canVectorize()
            || !inputs.embedFrameIDOffset.canVectorize()
            || !inputs.embedTimecode.canVectorize()
            || !inputs.embeddedBottomLines.canVectorize()
            || !inputs.embeddedDataFilepath.canVectorize()
            || !inputs.embeddedTimecodeOffset.canVectorize()
            || !inputs.embeddedTopLines.canVectorize()
            || !inputs.externalTimeOfSimFrameIn.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.hydraTimeIn.canVectorize()
            || !inputs.rawEncoding.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.simTimeIn.canVectorize()
            || !inputs.src.canVectorize()
            || !inputs.timecodeIn.canVectorize()
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
        if(token == inputs::EmbeddedLineEncoder.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.EmbeddedLineEncoder.setHandle(hdl);
            return;
        }
        if(token == inputs::embedFrameID.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.embedFrameID.setHandle(hdl);
            return;
        }
        if(token == inputs::embedFrameIDOffset.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.embedFrameIDOffset.setHandle(hdl);
            return;
        }
        if(token == inputs::embedTimecode.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.embedTimecode.setHandle(hdl);
            return;
        }
        if(token == inputs::embeddedBottomLines.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.embeddedBottomLines.setHandle(hdl);
            return;
        }
        if(token == inputs::embeddedDataFilepath.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.embeddedDataFilepath.setHandle(hdl);
            return;
        }
        if(token == inputs::embeddedTimecodeOffset.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.embeddedTimecodeOffset.setHandle(hdl);
            return;
        }
        if(token == inputs::embeddedTopLines.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.embeddedTopLines.setHandle(hdl);
            return;
        }
        if(token == inputs::externalTimeOfSimFrameIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.externalTimeOfSimFrameIn.setHandle(hdl);
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
        if(token == inputs::rawEncoding.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rawEncoding.setHandle(hdl);
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
        if(token == inputs::timecodeIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.timecodeIn.setHandle(hdl);
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
ogn::StateManager CamDefaultEmbeddedLinesTaskNodeDatabase::sm_stateManagerCamDefaultEmbeddedLinesTaskNode;
std::tuple<int, int, int> CamDefaultEmbeddedLinesTaskNodeDatabase::sm_generatorVersionCamDefaultEmbeddedLinesTaskNode{std::make_tuple(1,79,2)};
std::tuple<int, int, int> CamDefaultEmbeddedLinesTaskNodeDatabase::sm_targetVersionCamDefaultEmbeddedLinesTaskNode{std::make_tuple(2,184,5)};
}
using namespace ICamDefaultEmbeddedLinesTaskNode;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<CamDefaultEmbeddedLinesTaskNode, CamDefaultEmbeddedLinesTaskNodeDatabase> s_registration("omni.sensors.nv.camera.CamDefaultEmbeddedLinesTask", 1, "omni.sensors.nv.camera"); \
}
