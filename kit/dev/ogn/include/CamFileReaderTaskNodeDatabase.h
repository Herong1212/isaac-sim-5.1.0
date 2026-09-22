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

namespace CamFileReaderTaskNodeAttributes
{
namespace inputs
{
using AOVTrigger_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> AOVTrigger("inputs:AOVTrigger", "token", kExtendedAttributeType_Regular);
using fileDataType_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> fileDataType("inputs:fileDataType", "token", kExtendedAttributeType_Regular);
using filename_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> filename("inputs:filename", "token", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using height_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> height("inputs:height", "int", kExtendedAttributeType_Regular, 1208);
using hydraTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTimeIn("inputs:hydraTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using loop_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> loop("inputs:loop", "bool", kExtendedAttributeType_Regular, false);
using pixelPattern_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> pixelPattern("inputs:pixelPattern", "token", kExtendedAttributeType_Regular);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using simTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTimeIn("inputs:simTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using skipBack_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> skipBack("inputs:skipBack", "uint64", kExtendedAttributeType_Regular, 0);
using skipFront_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> skipFront("inputs:skipFront", "uint64", kExtendedAttributeType_Regular, 0);
using start_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> start("inputs:start", "bool", kExtendedAttributeType_Regular, false);
using width_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> width("inputs:width", "int", kExtendedAttributeType_Regular, 1920);
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
using namespace CamFileReaderTaskNodeAttributes;
namespace ICamFileReaderTaskNode
{
// Reads a camera raw file
class CamFileReaderTaskNodeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerCamFileReaderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerCamFileReaderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerCamFileReaderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerCamFileReaderTaskNode.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerCamFileReaderTaskNode;
    static std::tuple<int, int, int>sm_generatorVersionCamFileReaderTaskNode;
    static std::tuple<int, int, int>sm_targetVersionCamFileReaderTaskNode;
    static constexpr size_t staticAttributeCount = 21;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : AOVTrigger{offset}
        , fileDataType{offset}
        , filename{offset}
        , gpu{offset}
        , height{offset}
        , hydraTimeIn{offset}
        , loop{offset}
        , pixelPattern{offset}
        , rp{offset}
        , simTimeIn{offset}
        , skipBack{offset}
        , skipFront{offset}
        , start{offset}
        , width{offset}
        {}
        ogn::SimpleInput<const NameToken,ogn::kCpu> AOVTrigger;
        ogn::SimpleInput<const NameToken,ogn::kCpu> fileDataType;
        ogn::SimpleInput<const NameToken,ogn::kCpu> filename;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const int,ogn::kCpu> height;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTimeIn;
        ogn::SimpleInput<const bool,ogn::kCpu> loop;
        ogn::SimpleInput<const NameToken,ogn::kCpu> pixelPattern;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const double,ogn::kCpu> simTimeIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> skipBack;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> skipFront;
        ogn::SimpleInput<const bool,ogn::kCpu> start;
        ogn::SimpleInput<const int,ogn::kCpu> width;
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
    CamFileReaderTaskNodeDatabase(NodeObj const& nodeObjParam)
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
    CamFileReaderTaskNodeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : CamFileReaderTaskNodeDatabase(nodeObjParam)
    {}

    //Main constructor
    CamFileReaderTaskNodeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::AOVTrigger.m_token, inputs::fileDataType.m_token, inputs::filename.m_token, inputs::gpu.m_token,
                    inputs::height.m_token, inputs::hydraTimeIn.m_token, inputs::loop.m_token, inputs::pixelPattern.m_token,
                    inputs::rp.m_token, inputs::simTimeIn.m_token, inputs::skipBack.m_token, inputs::skipFront.m_token,
                    inputs::start.m_token, inputs::width.m_token
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
            inputs.AOVTrigger.setContext(contextObj);
            inputs.AOVTrigger.setHandle(std::get<0>(inputDataHandles0));
            inputs.fileDataType.setContext(contextObj);
            inputs.fileDataType.setHandle(std::get<1>(inputDataHandles0));
            inputs.filename.setContext(contextObj);
            inputs.filename.setHandle(std::get<2>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<3>(inputDataHandles0));
            inputs.height.setContext(contextObj);
            inputs.height.setHandle(std::get<4>(inputDataHandles0));
            inputs.hydraTimeIn.setContext(contextObj);
            inputs.hydraTimeIn.setHandle(std::get<5>(inputDataHandles0));
            inputs.loop.setContext(contextObj);
            inputs.loop.setHandle(std::get<6>(inputDataHandles0));
            inputs.pixelPattern.setContext(contextObj);
            inputs.pixelPattern.setHandle(std::get<7>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<8>(inputDataHandles0));
            inputs.simTimeIn.setContext(contextObj);
            inputs.simTimeIn.setHandle(std::get<9>(inputDataHandles0));
            inputs.skipBack.setContext(contextObj);
            inputs.skipBack.setHandle(std::get<10>(inputDataHandles0));
            inputs.skipFront.setContext(contextObj);
            inputs.skipFront.setHandle(std::get<11>(inputDataHandles0));
            inputs.start.setContext(contextObj);
            inputs.start.setHandle(std::get<12>(inputDataHandles0));
            inputs.width.setContext(contextObj);
            inputs.width.setHandle(std::get<13>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.CamFileReaderTaskNode");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_AOVTrigger_token {"LDR"};
        inputs::AOVTrigger.setDefault(inputs_AOVTrigger_token.asTokenC());
        static omni::fabric::Token inputs_fileDataType_token {"UINT8"};
        inputs::fileDataType.setDefault(inputs_fileDataType_token.asTokenC());
        static omni::fabric::Token inputs_filename_token {"/tmp/new.raw"};
        inputs::filename.setDefault(inputs_filename_token.asTokenC());
        static omni::fabric::Token inputs_pixelPattern_token {"RGBA"};
        inputs::pixelPattern.setDefault(inputs_pixelPattern_token.asTokenC());
        inputs::AOVTrigger.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::fileDataType.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::filename.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::loop.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::pixelPattern.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::skipBack.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::skipFront.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::start.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::width.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::dest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.camera");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Reads a camera raw file");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::AOVTrigger.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The renderproduct which triggers the reader");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"LDR\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::fileDataType.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Data type of the RGB: Could be UINT8, UINT16, UINT32, FLOAT16 or FLOAT32");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"UINT8\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::filename.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "File path to the video raw file");
        attr.iAttribute->setMetadata(attr, kOgnMetadataMemoryType, "cpu");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"/tmp/new.raw\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Image Height");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1208");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::loop.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Indicates whether the input file shall be loop infinitely");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::pixelPattern.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pixel pattern of the input file: RGBA or CFA");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"RGBA\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::skipBack.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Bytes to skip after each frame");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::skipFront.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Bytes to skip before each frame");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::start.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "start");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Image Width");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1920");
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
        sm_stateManagerCamFileReaderTaskNode.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.AOVTrigger.isValid()
            && inputs.fileDataType.isValid()
            && inputs.filename.isValid()
            && inputs.gpu.isValid()
            && inputs.height.isValid()
            && inputs.hydraTimeIn.isValid()
            && inputs.loop.isValid()
            && inputs.pixelPattern.isValid()
            && inputs.rp.isValid()
            && inputs.simTimeIn.isValid()
            && inputs.skipBack.isValid()
            && inputs.skipFront.isValid()
            && inputs.start.isValid()
            && inputs.width.isValid()
            && outputs.dest.isValid()
            && outputs.gpu.isValid()
            && outputs.hydraTimeOut.isValid()
            && outputs.rp.isValid()
            && outputs.simTimeOut.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.AOVTrigger.invalidateCachedPointer();
            inputs.fileDataType.invalidateCachedPointer();
            inputs.filename.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.height.invalidateCachedPointer();
            inputs.hydraTimeIn.invalidateCachedPointer();
            inputs.loop.invalidateCachedPointer();
            inputs.pixelPattern.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.simTimeIn.invalidateCachedPointer();
            inputs.skipBack.invalidateCachedPointer();
            inputs.skipFront.invalidateCachedPointer();
            inputs.start.invalidateCachedPointer();
            inputs.width.invalidateCachedPointer();
            outputs.dest.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.hydraTimeOut.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            outputs.simTimeOut.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::AOVTrigger.m_token) {
                inputs.AOVTrigger.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::fileDataType.m_token) {
                inputs.fileDataType.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::filename.m_token) {
                inputs.filename.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::height.m_token) {
                inputs.height.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hydraTimeIn.m_token) {
                inputs.hydraTimeIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::loop.m_token) {
                inputs.loop.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::pixelPattern.m_token) {
                inputs.pixelPattern.invalidateCachedPointer();
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
            if(attrib == inputs::skipBack.m_token) {
                inputs.skipBack.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::skipFront.m_token) {
                inputs.skipFront.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::start.m_token) {
                inputs.start.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::width.m_token) {
                inputs.width.invalidateCachedPointer();
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
        if( !inputs.AOVTrigger.canVectorize()
            || !inputs.fileDataType.canVectorize()
            || !inputs.filename.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.height.canVectorize()
            || !inputs.hydraTimeIn.canVectorize()
            || !inputs.loop.canVectorize()
            || !inputs.pixelPattern.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.simTimeIn.canVectorize()
            || !inputs.skipBack.canVectorize()
            || !inputs.skipFront.canVectorize()
            || !inputs.start.canVectorize()
            || !inputs.width.canVectorize()
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
        if(token == inputs::AOVTrigger.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.AOVTrigger.setHandle(hdl);
            return;
        }
        if(token == inputs::fileDataType.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.fileDataType.setHandle(hdl);
            return;
        }
        if(token == inputs::filename.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.filename.setHandle(hdl);
            return;
        }
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::height.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.height.setHandle(hdl);
            return;
        }
        if(token == inputs::hydraTimeIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hydraTimeIn.setHandle(hdl);
            return;
        }
        if(token == inputs::loop.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.loop.setHandle(hdl);
            return;
        }
        if(token == inputs::pixelPattern.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.pixelPattern.setHandle(hdl);
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
        if(token == inputs::skipBack.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.skipBack.setHandle(hdl);
            return;
        }
        if(token == inputs::skipFront.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.skipFront.setHandle(hdl);
            return;
        }
        if(token == inputs::start.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.start.setHandle(hdl);
            return;
        }
        if(token == inputs::width.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.width.setHandle(hdl);
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
ogn::StateManager CamFileReaderTaskNodeDatabase::sm_stateManagerCamFileReaderTaskNode;
std::tuple<int, int, int> CamFileReaderTaskNodeDatabase::sm_generatorVersionCamFileReaderTaskNode{std::make_tuple(1,79,2)};
std::tuple<int, int, int> CamFileReaderTaskNodeDatabase::sm_targetVersionCamFileReaderTaskNode{std::make_tuple(2,184,5)};
}
using namespace ICamFileReaderTaskNode;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<CamFileReaderTaskNode, CamFileReaderTaskNodeDatabase> s_registration("omni.sensors.nv.camera.CamFileReaderTaskNode", 1, "omni.sensors.nv.camera"); \
}
