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
#include <omni/graph/core/ogn/ArrayAttribute.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>
#include <omni/graph/image/unstable/ComputeParamsBuilder.h>

namespace OgnGpuInteropCudaEntryAttributes
{
namespace inputs
{
using sourceName_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> sourceName("inputs:sourceName", "string", kExtendedAttributeType_Regular, "ldrColor", 8);
}
namespace outputs
{
using bufferSize_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> bufferSize("outputs:bufferSize", "uint", kExtendedAttributeType_Regular);
using cudaMipmappedArray_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> cudaMipmappedArray("outputs:cudaMipmappedArray", "uint64", kExtendedAttributeType_Regular);
using externalTimeOfSimFrame_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> externalTimeOfSimFrame("outputs:externalTimeOfSimFrame", "int64", kExtendedAttributeType_Regular);
using format_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> format("outputs:format", "uint64", kExtendedAttributeType_Regular);
using frameId_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> frameId("outputs:frameId", "int64", kExtendedAttributeType_Regular);
using height_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> height("outputs:height", "uint", kExtendedAttributeType_Regular);
using hydraTime_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> hydraTime("outputs:hydraTime", "double", kExtendedAttributeType_Regular);
using isBuffer_t = bool&;
ogn::AttributeInitializer<bool, ogn::kOgnOutput> isBuffer("outputs:isBuffer", "bool", kExtendedAttributeType_Regular);
using mipCount_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> mipCount("outputs:mipCount", "uint", kExtendedAttributeType_Regular);
using rationalTimeOfSimDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> rationalTimeOfSimDenominator("outputs:rationalTimeOfSimDenominator", "uint64", kExtendedAttributeType_Regular);
using rationalTimeOfSimNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> rationalTimeOfSimNumerator("outputs:rationalTimeOfSimNumerator", "int64", kExtendedAttributeType_Regular);
using simTime_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> simTime("outputs:simTime", "double", kExtendedAttributeType_Regular);
using stream_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> stream("outputs:stream", "uint64", kExtendedAttributeType_Regular);
using width_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> width("outputs:width", "uint", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnGpuInteropCudaEntryAttributes;
namespace IOgnGpuInteropCudaEntry
{
// Entry node for post-processing hydra render results for a single view.  It outputs
// the properties of a RenderVar as attributes accessible to downstream nodes.  All
// downstream nodes are scheduled as CUDA commands.
class OgnGpuInteropCudaEntryDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnGpuInteropCudaEntry.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnGpuInteropCudaEntry.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnGpuInteropCudaEntry.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnGpuInteropCudaEntry.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnGpuInteropCudaEntry;
    static std::tuple<int, int, int>sm_generatorVersionOgnGpuInteropCudaEntry;
    static std::tuple<int, int, int>sm_targetVersionOgnGpuInteropCudaEntry;
    static constexpr size_t staticAttributeCount = 17;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : sourceName{offset,AttributeRole::eText}
        {}
        ogn::ArrayInput<const char,ogn::kCpu> sourceName;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : bufferSize{offset}
        , cudaMipmappedArray{offset}
        , externalTimeOfSimFrame{offset}
        , format{offset}
        , frameId{offset}
        , height{offset}
        , hydraTime{offset}
        , isBuffer{offset}
        , mipCount{offset}
        , rationalTimeOfSimDenominator{offset}
        , rationalTimeOfSimNumerator{offset}
        , simTime{offset}
        , stream{offset}
        , width{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> bufferSize;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> cudaMipmappedArray;
        ogn::SimpleOutput<int64_t,ogn::kCpu> externalTimeOfSimFrame;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> format;
        ogn::SimpleOutput<int64_t,ogn::kCpu> frameId;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> height;
        ogn::SimpleOutput<double,ogn::kCpu> hydraTime;
        ogn::SimpleOutput<bool,ogn::kCpu> isBuffer;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> mipCount;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> rationalTimeOfSimDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> rationalTimeOfSimNumerator;
        ogn::SimpleOutput<double,ogn::kCpu> simTime;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> stream;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> width;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnGpuInteropCudaEntryDatabase(NodeObj const& nodeObjParam)
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
    OgnGpuInteropCudaEntryDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnGpuInteropCudaEntryDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnGpuInteropCudaEntryDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::sourceName.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::bufferSize.m_token, outputs::cudaMipmappedArray.m_token, outputs::externalTimeOfSimFrame.m_token, outputs::format.m_token,
                    outputs::frameId.m_token, outputs::height.m_token, outputs::hydraTime.m_token, outputs::isBuffer.m_token,
                    outputs::mipCount.m_token, outputs::rationalTimeOfSimDenominator.m_token, outputs::rationalTimeOfSimNumerator.m_token, outputs::simTime.m_token,
                    outputs::stream.m_token, outputs::width.m_token
                )
            , kAccordingToContextIndex);
            inputs.sourceName.setContext(contextObj);
            inputs.sourceName.setHandle(std::get<0>(inputDataHandles0));
            outputs.bufferSize.setContext(contextObj);
            outputs.bufferSize.setHandle(std::get<0>(outputDataHandles0));
            outputs.cudaMipmappedArray.setContext(contextObj);
            outputs.cudaMipmappedArray.setHandle(std::get<1>(outputDataHandles0));
            outputs.externalTimeOfSimFrame.setContext(contextObj);
            outputs.externalTimeOfSimFrame.setHandle(std::get<2>(outputDataHandles0));
            outputs.format.setContext(contextObj);
            outputs.format.setHandle(std::get<3>(outputDataHandles0));
            outputs.frameId.setContext(contextObj);
            outputs.frameId.setHandle(std::get<4>(outputDataHandles0));
            outputs.height.setContext(contextObj);
            outputs.height.setHandle(std::get<5>(outputDataHandles0));
            outputs.hydraTime.setContext(contextObj);
            outputs.hydraTime.setHandle(std::get<6>(outputDataHandles0));
            outputs.isBuffer.setContext(contextObj);
            outputs.isBuffer.setHandle(std::get<7>(outputDataHandles0));
            outputs.mipCount.setContext(contextObj);
            outputs.mipCount.setHandle(std::get<8>(outputDataHandles0));
            outputs.rationalTimeOfSimDenominator.setContext(contextObj);
            outputs.rationalTimeOfSimDenominator.setHandle(std::get<9>(outputDataHandles0));
            outputs.rationalTimeOfSimNumerator.setContext(contextObj);
            outputs.rationalTimeOfSimNumerator.setHandle(std::get<10>(outputDataHandles0));
            outputs.simTime.setContext(contextObj);
            outputs.simTime.setHandle(std::get<11>(outputDataHandles0));
            outputs.stream.setContext(contextObj);
            outputs.stream.setHandle(std::get<12>(outputDataHandles0));
            outputs.width.setContext(contextObj);
            outputs.width.setHandle(std::get<13>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.graph.nodes.GpuInteropCudaEntry");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::sourceName.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::bufferSize.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cudaMipmappedArray.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::externalTimeOfSimFrame.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::format.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::frameId.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTime.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::isBuffer.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::mipCount.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rationalTimeOfSimDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rationalTimeOfSimNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::stream.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::width.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.graph.image.nodes");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataUiName, "GPU Interop: Cuda Entry");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,rendering");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Entry node for post-processing hydra render results for a single view.  It outputs the properties of a RenderVar as attributes accessible to downstream nodes.  All downstream nodes are scheduled as CUDA commands.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::sourceName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The name of the source RenderVar (AOV). The properties of this AOV are the output of this node.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Source Name");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"ldrColor\"");
        attr = iNode->getAttributeByToken(nodeObj, outputs::bufferSize.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Size of the buffer, if the selected RenderVar is a buffer, otherwise it represents the texture depth.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Buffer Size");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cudaMipmappedArray.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The RenderVar data, which is represented as a CUDA Mipmapped Array.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "RenderVar Data");
        attr = iNode->getAttributeByToken(nodeObj, outputs::externalTimeOfSimFrame.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The external time on the master node, matching the simulation frame used to render this frame. \nIt is only valid if the simulation and rendering are performed at the same, or different but constant rates.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "External Time Of Simulation Frame");
        attr = iNode->getAttributeByToken(nodeObj, outputs::format.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The texture format of the input image, matching the values of the enum carb::graphics::Format. \nIf the RenderVar is a buffer, the value is unknown.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Texture Format");
        attr = iNode->getAttributeByToken(nodeObj, outputs::frameId.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The frame number. \nIt is only valid if the simulation and rendering are performed at the same, or different but constant rates.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Frame ID");
        attr = iNode->getAttributeByToken(nodeObj, outputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The width of the selected texture RenderVar. \nIf the RenderVar is an arbitrary buffer, it is 0.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Height");
        attr = iNode->getAttributeByToken(nodeObj, outputs::hydraTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The time difference since the last rendered frame.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Renderer Time");
        attr = iNode->getAttributeByToken(nodeObj, outputs::isBuffer.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "True if the entry exposes an arbitrary buffer RenderVar as opposed to a texture RenderVar.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Is Buffer");
        attr = iNode->getAttributeByToken(nodeObj, outputs::mipCount.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The number of levels of detail encoded in 'RenderVar Data'. If the RenderVar is not a texture, the value is 0.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Mip Count");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rationalTimeOfSimDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The denominator of the simulation time expressed as rational time. \nIt is always valid and may be used to fetch data from Fabric during the node compute.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Rational Time Of Sim Denominator");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rationalTimeOfSimNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The numerator of the simulation time expressed as rational time. \nIt is always valid and may be used to fetch data from Fabric during the node compute.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Rational Time Of Sim Numerator");
        attr = iNode->getAttributeByToken(nodeObj, outputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The time difference since the last simulation frame.\nMay suffer from loss of precision and cannot be used as a deterministic identifier, \nfor example for fetching data from Fabric during the node compute - \nuse the Rational Time instead in that case.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Simulation Time");
        attr = iNode->getAttributeByToken(nodeObj, outputs::stream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The CUDA Stream used to order the CUDA commands scheduled by this graph execution.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Stream");
        attr = iNode->getAttributeByToken(nodeObj, outputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The width of the selected texture RenderVar. \nIf the RenderVar is an arbitrary buffer, it is 0.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Width");
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
        sm_stateManagerOgnGpuInteropCudaEntry.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.sourceName.isValid()
            && outputs.bufferSize.isValid()
            && outputs.cudaMipmappedArray.isValid()
            && outputs.externalTimeOfSimFrame.isValid()
            && outputs.format.isValid()
            && outputs.frameId.isValid()
            && outputs.height.isValid()
            && outputs.hydraTime.isValid()
            && outputs.isBuffer.isValid()
            && outputs.mipCount.isValid()
            && outputs.rationalTimeOfSimDenominator.isValid()
            && outputs.rationalTimeOfSimNumerator.isValid()
            && outputs.simTime.isValid()
            && outputs.stream.isValid()
            && outputs.width.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.sourceName.invalidateCachedPointer();
            outputs.bufferSize.invalidateCachedPointer();
            outputs.cudaMipmappedArray.invalidateCachedPointer();
            outputs.externalTimeOfSimFrame.invalidateCachedPointer();
            outputs.format.invalidateCachedPointer();
            outputs.frameId.invalidateCachedPointer();
            outputs.height.invalidateCachedPointer();
            outputs.hydraTime.invalidateCachedPointer();
            outputs.isBuffer.invalidateCachedPointer();
            outputs.mipCount.invalidateCachedPointer();
            outputs.rationalTimeOfSimDenominator.invalidateCachedPointer();
            outputs.rationalTimeOfSimNumerator.invalidateCachedPointer();
            outputs.simTime.invalidateCachedPointer();
            outputs.stream.invalidateCachedPointer();
            outputs.width.invalidateCachedPointer();
            return;
        }
        inputs.sourceName.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::sourceName.m_token) {
                inputs.sourceName.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::bufferSize.m_token) {
                outputs.bufferSize.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cudaMipmappedArray.m_token) {
                outputs.cudaMipmappedArray.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::externalTimeOfSimFrame.m_token) {
                outputs.externalTimeOfSimFrame.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::format.m_token) {
                outputs.format.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::frameId.m_token) {
                outputs.frameId.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::height.m_token) {
                outputs.height.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::hydraTime.m_token) {
                outputs.hydraTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::isBuffer.m_token) {
                outputs.isBuffer.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::mipCount.m_token) {
                outputs.mipCount.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::rationalTimeOfSimDenominator.m_token) {
                outputs.rationalTimeOfSimDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::rationalTimeOfSimNumerator.m_token) {
                outputs.rationalTimeOfSimNumerator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::simTime.m_token) {
                outputs.simTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::stream.m_token) {
                outputs.stream.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::width.m_token) {
                outputs.width.invalidateCachedPointer();
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
        if( !outputs.bufferSize.canVectorize()
            || !outputs.cudaMipmappedArray.canVectorize()
            || !outputs.externalTimeOfSimFrame.canVectorize()
            || !outputs.format.canVectorize()
            || !outputs.frameId.canVectorize()
            || !outputs.height.canVectorize()
            || !outputs.hydraTime.canVectorize()
            || !outputs.isBuffer.canVectorize()
            || !outputs.mipCount.canVectorize()
            || !outputs.rationalTimeOfSimDenominator.canVectorize()
            || !outputs.rationalTimeOfSimNumerator.canVectorize()
            || !outputs.simTime.canVectorize()
            || !outputs.stream.canVectorize()
            || !outputs.width.canVectorize()
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
        if(token == inputs::sourceName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sourceName.setHandle(hdl);
            return;
        }
        if(token == outputs::bufferSize.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.bufferSize.setHandle(hdl);
            return;
        }
        if(token == outputs::cudaMipmappedArray.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cudaMipmappedArray.setHandle(hdl);
            return;
        }
        if(token == outputs::externalTimeOfSimFrame.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.externalTimeOfSimFrame.setHandle(hdl);
            return;
        }
        if(token == outputs::format.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.format.setHandle(hdl);
            return;
        }
        if(token == outputs::frameId.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.frameId.setHandle(hdl);
            return;
        }
        if(token == outputs::height.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.height.setHandle(hdl);
            return;
        }
        if(token == outputs::hydraTime.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.hydraTime.setHandle(hdl);
            return;
        }
        if(token == outputs::isBuffer.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.isBuffer.setHandle(hdl);
            return;
        }
        if(token == outputs::mipCount.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.mipCount.setHandle(hdl);
            return;
        }
        if(token == outputs::rationalTimeOfSimDenominator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rationalTimeOfSimDenominator.setHandle(hdl);
            return;
        }
        if(token == outputs::rationalTimeOfSimNumerator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rationalTimeOfSimNumerator.setHandle(hdl);
            return;
        }
        if(token == outputs::simTime.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.simTime.setHandle(hdl);
            return;
        }
        if(token == outputs::stream.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.stream.setHandle(hdl);
            return;
        }
        if(token == outputs::width.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.width.setHandle(hdl);
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
        auto variable = const_cast<OgnGpuInteropCudaEntryDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropCudaEntryDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropCudaEntryDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropCudaEntryDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnGpuInteropCudaEntryDatabase::sm_stateManagerOgnGpuInteropCudaEntry;
std::tuple<int, int, int> OgnGpuInteropCudaEntryDatabase::sm_generatorVersionOgnGpuInteropCudaEntry{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnGpuInteropCudaEntryDatabase::sm_targetVersionOgnGpuInteropCudaEntry{std::make_tuple(2,184,5)};
}
using namespace IOgnGpuInteropCudaEntry;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnGpuInteropCudaEntry, OgnGpuInteropCudaEntryDatabase> s_registration("omni.graph.nodes.GpuInteropCudaEntry", 3, "omni.graph.image.nodes"); \
}
