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

namespace OgnGpuInteropCpuToDiskAttributes
{
namespace inputs
{
using active_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> active("inputs:active", "bool", kExtendedAttributeType_Regular, false);
using aovCpu_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> aovCpu("inputs:aovCpu", "string", kExtendedAttributeType_Regular, "", 0);
using aovGpu_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> aovGpu("inputs:aovGpu", "string", kExtendedAttributeType_Regular, "", 0);
using autoFileNumber_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> autoFileNumber("inputs:autoFileNumber", "int", kExtendedAttributeType_Regular, -1);
using fileName_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> fileName("inputs:fileName", "string", kExtendedAttributeType_Regular, "", 0);
using fileNumber_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> fileNumber("inputs:fileNumber", "int", kExtendedAttributeType_Regular, -1);
using fileType_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> fileType("inputs:fileType", "string", kExtendedAttributeType_Regular, "png", 3);
using frameCount_t = const int64_t&;
ogn::AttributeInitializer<const int64_t, ogn::kOgnInput> frameCount("inputs:frameCount", "int64", kExtendedAttributeType_Regular, -1);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using maxInflightWrites_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> maxInflightWrites("inputs:maxInflightWrites", "int", kExtendedAttributeType_Regular, 2);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using saveFlags_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> saveFlags("inputs:saveFlags", "uint64", kExtendedAttributeType_Regular, 0);
using saveLocation_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> saveLocation("inputs:saveLocation", "string", kExtendedAttributeType_Regular, "", 0);
using skipInactive_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> skipInactive("inputs:skipInactive", "bool", kExtendedAttributeType_Regular, false);
using startFrame_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> startFrame("inputs:startFrame", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using gpu_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> gpu("outputs:gpu", "uint64", kExtendedAttributeType_Regular);
using rp_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> rp("outputs:rp", "uint64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnGpuInteropCpuToDiskAttributes;
namespace IOgnGpuInteropCpuToDisk
{
// Saves the specified CPU buffer to disk.  The node assumes that the RenderVar (AOV)
// has already been copied to the host (CPU) memory.
class OgnGpuInteropCpuToDiskDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnGpuInteropCpuToDisk.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnGpuInteropCpuToDisk.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnGpuInteropCpuToDisk.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnGpuInteropCpuToDisk.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnGpuInteropCpuToDisk;
    static std::tuple<int, int, int>sm_generatorVersionOgnGpuInteropCpuToDisk;
    static std::tuple<int, int, int>sm_targetVersionOgnGpuInteropCpuToDisk;
    static constexpr size_t staticAttributeCount = 19;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : active{offset}
        , aovCpu{offset,AttributeRole::eText}
        , aovGpu{offset,AttributeRole::eText}
        , autoFileNumber{offset}
        , fileName{offset,AttributeRole::eText}
        , fileNumber{offset}
        , fileType{offset,AttributeRole::eText}
        , frameCount{offset}
        , gpu{offset}
        , maxInflightWrites{offset}
        , rp{offset}
        , saveFlags{offset}
        , saveLocation{offset,AttributeRole::eText}
        , skipInactive{offset}
        , startFrame{offset}
        {}
        ogn::SimpleInput<const bool,ogn::kCpu> active;
        ogn::ArrayInput<const char,ogn::kCpu> aovCpu;
        ogn::ArrayInput<const char,ogn::kCpu> aovGpu;
        ogn::SimpleInput<const int,ogn::kCpu> autoFileNumber;
        ogn::ArrayInput<const char,ogn::kCpu> fileName;
        bool has_fileName() const { return fileName.isValid(); };
        ogn::SimpleInput<const int,ogn::kCpu> fileNumber;
        ogn::ArrayInput<const char,ogn::kCpu> fileType;
        ogn::SimpleInput<const int64_t,ogn::kCpu> frameCount;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const int,ogn::kCpu> maxInflightWrites;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> saveFlags;
        ogn::ArrayInput<const char,ogn::kCpu> saveLocation;
        ogn::SimpleInput<const bool,ogn::kCpu> skipInactive;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> startFrame;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : gpu{offset}
        , rp{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> gpu;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> rp;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnGpuInteropCpuToDiskDatabase(NodeObj const& nodeObjParam)
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
    OgnGpuInteropCpuToDiskDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnGpuInteropCpuToDiskDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnGpuInteropCpuToDiskDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::active.m_token, inputs::aovCpu.m_token, inputs::aovGpu.m_token, inputs::autoFileNumber.m_token,
                    inputs::fileName.m_token, inputs::fileNumber.m_token, inputs::fileType.m_token, inputs::frameCount.m_token,
                    inputs::gpu.m_token, inputs::maxInflightWrites.m_token, inputs::rp.m_token, inputs::saveFlags.m_token,
                    inputs::saveLocation.m_token, inputs::skipInactive.m_token, inputs::startFrame.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::gpu.m_token, outputs::rp.m_token
                )
            , kAccordingToContextIndex);
            inputs.active.setContext(contextObj);
            inputs.active.setHandle(std::get<0>(inputDataHandles0));
            inputs.aovCpu.setContext(contextObj);
            inputs.aovCpu.setHandle(std::get<1>(inputDataHandles0));
            inputs.aovGpu.setContext(contextObj);
            inputs.aovGpu.setHandle(std::get<2>(inputDataHandles0));
            inputs.autoFileNumber.setContext(contextObj);
            inputs.autoFileNumber.setHandle(std::get<3>(inputDataHandles0));
            inputs.fileName.setContext(contextObj);
            inputs.fileName.setHandle(std::get<4>(inputDataHandles0));
            inputs.fileNumber.setContext(contextObj);
            inputs.fileNumber.setHandle(std::get<5>(inputDataHandles0));
            inputs.fileType.setContext(contextObj);
            inputs.fileType.setHandle(std::get<6>(inputDataHandles0));
            inputs.frameCount.setContext(contextObj);
            inputs.frameCount.setHandle(std::get<7>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<8>(inputDataHandles0));
            inputs.maxInflightWrites.setContext(contextObj);
            inputs.maxInflightWrites.setHandle(std::get<9>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<10>(inputDataHandles0));
            inputs.saveFlags.setContext(contextObj);
            inputs.saveFlags.setHandle(std::get<11>(inputDataHandles0));
            inputs.saveLocation.setContext(contextObj);
            inputs.saveLocation.setHandle(std::get<12>(inputDataHandles0));
            inputs.skipInactive.setContext(contextObj);
            inputs.skipInactive.setHandle(std::get<13>(inputDataHandles0));
            inputs.startFrame.setContext(contextObj);
            inputs.startFrame.setHandle(std::get<14>(inputDataHandles0));
            outputs.gpu.setContext(contextObj);
            outputs.gpu.setHandle(std::get<0>(outputDataHandles0));
            outputs.rp.setContext(contextObj);
            outputs.rp.setHandle(std::get<1>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.graph.examples.cpp.GpuInteropCpuToDisk");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::active.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::aovCpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::aovGpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::autoFileNumber.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::fileName.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::fileNumber.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::fileType.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::frameCount.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::maxInflightWrites.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::saveFlags.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::saveLocation.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::skipInactive.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::startFrame.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.graph.image.nodes");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataUiName, "GPU Interop: Cpu To Disk");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,rendering");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Saves the specified CPU buffer to disk.  The node assumes that the RenderVar (AOV) has already been copied to the host (CPU) memory.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::active.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If true, the node computes once, then resets to false. \nIt is useful to use in runtime scripts or tests, where a single frame should be captured at a time.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Active Reset");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::aovCpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of AOV representing the CPU buffer of GPU resource. \nIt is assumed that the CPU RenderVar is a copy of the GPU data.\nIf the CPU AOV is invalid, the node does not output anything.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "AOV CPU");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::aovGpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of AOV representing the GPU resource, used for querying format and properties.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "AOV GPU");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::autoFileNumber.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If non zero, this number will be the starting number for export. Each invocation of this node increases the number by 1.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Auto File Number");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::fileName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Optional, name given to the output file. If specified the output filename will be 'File Name_{aovGpu}.{fileType}'.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "File Name");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr.iAttribute->setIsOptionalForCompute(attr, true);
        attr = iNode->getAttributeByToken(nodeObj, inputs::fileNumber.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number that will be appended to the exported filename. If -1 then the render product's frame number will be used.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "File Number");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::fileType.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The file type of the saved images. The valid types are bmp, png and exr.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "File Type");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"png\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::frameCount.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Number of frames to capture. If set to -1, the node execution never stops.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Frame Count");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The shared context containing GPU foundation interfaces.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "GPU Foundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::maxInflightWrites.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Specifies the maximum allowed concurrent asynchronous file write operations dispatched by the node, \npreventing potential blocking on file I/O for the Render thread. \nThis attribute controls the number of writes before waiting to dispatch a new I/O command.\nIf the number of concurrent writes is reached, the Render Thread waits for the existing write commands to complete \nbefore dispatching new commands.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Max Concurrent Writes");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "2");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The render product for this view.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Render Product");
        attr = iNode->getAttributeByToken(nodeObj, inputs::saveFlags.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Flags that will be passed to carb::imaging::IImaging for file saving.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Save Flags");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::saveLocation.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The path to save AOVs as AOV_FrameNumber.{exr,png}");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Save Location");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::skipInactive.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If true, the node will early out if 'isactive' is false. \nIf false, the node will be triggered even if 'active' is False but only \nif the frame number of the render product is smaller than 'startFrame', \nand if the 'frameCount' is larger or equal to the internal capture count.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Skip Inactive Nodes");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::startFrame.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Frame number to begin saving to disk.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Start Frame");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The shared context containing GPU foundation interfaces.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "GPU Foundations");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The render product for this view.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Render Product");
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
        sm_stateManagerOgnGpuInteropCpuToDisk.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.active.isValid()
            && inputs.aovCpu.isValid()
            && inputs.aovGpu.isValid()
            && inputs.autoFileNumber.isValid()
            && inputs.fileNumber.isValid()
            && inputs.fileType.isValid()
            && inputs.frameCount.isValid()
            && inputs.gpu.isValid()
            && inputs.maxInflightWrites.isValid()
            && inputs.rp.isValid()
            && inputs.saveFlags.isValid()
            && inputs.saveLocation.isValid()
            && inputs.skipInactive.isValid()
            && inputs.startFrame.isValid()
            && outputs.gpu.isValid()
            && outputs.rp.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.active.invalidateCachedPointer();
            inputs.aovCpu.invalidateCachedPointer();
            inputs.aovGpu.invalidateCachedPointer();
            inputs.autoFileNumber.invalidateCachedPointer();
            inputs.fileName.invalidateCachedPointer();
            inputs.fileNumber.invalidateCachedPointer();
            inputs.fileType.invalidateCachedPointer();
            inputs.frameCount.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.maxInflightWrites.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.saveFlags.invalidateCachedPointer();
            inputs.saveLocation.invalidateCachedPointer();
            inputs.skipInactive.invalidateCachedPointer();
            inputs.startFrame.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            return;
        }
        inputs.aovCpu.invalidateCachedPointer();
        inputs.aovGpu.invalidateCachedPointer();
        inputs.fileName.invalidateCachedPointer();
        inputs.fileType.invalidateCachedPointer();
        inputs.saveLocation.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::active.m_token) {
                inputs.active.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::aovCpu.m_token) {
                inputs.aovCpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::aovGpu.m_token) {
                inputs.aovGpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::autoFileNumber.m_token) {
                inputs.autoFileNumber.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::fileName.m_token) {
                inputs.fileName.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::fileNumber.m_token) {
                inputs.fileNumber.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::fileType.m_token) {
                inputs.fileType.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::frameCount.m_token) {
                inputs.frameCount.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::maxInflightWrites.m_token) {
                inputs.maxInflightWrites.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::saveFlags.m_token) {
                inputs.saveFlags.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::saveLocation.m_token) {
                inputs.saveLocation.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::skipInactive.m_token) {
                inputs.skipInactive.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::startFrame.m_token) {
                inputs.startFrame.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::gpu.m_token) {
                outputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::rp.m_token) {
                outputs.rp.invalidateCachedPointer();
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
        if( !inputs.active.canVectorize()
            || !inputs.autoFileNumber.canVectorize()
            || !inputs.fileNumber.canVectorize()
            || !inputs.frameCount.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.maxInflightWrites.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.saveFlags.canVectorize()
            || !inputs.skipInactive.canVectorize()
            || !inputs.startFrame.canVectorize()
            || !outputs.gpu.canVectorize()
            || !outputs.rp.canVectorize()
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
        if(token == inputs::active.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.active.setHandle(hdl);
            return;
        }
        if(token == inputs::aovCpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.aovCpu.setHandle(hdl);
            return;
        }
        if(token == inputs::aovGpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.aovGpu.setHandle(hdl);
            return;
        }
        if(token == inputs::autoFileNumber.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.autoFileNumber.setHandle(hdl);
            return;
        }
        if(token == inputs::fileName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.fileName.setHandle(hdl);
            return;
        }
        if(token == inputs::fileNumber.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.fileNumber.setHandle(hdl);
            return;
        }
        if(token == inputs::fileType.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.fileType.setHandle(hdl);
            return;
        }
        if(token == inputs::frameCount.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.frameCount.setHandle(hdl);
            return;
        }
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::maxInflightWrites.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.maxInflightWrites.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == inputs::saveFlags.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.saveFlags.setHandle(hdl);
            return;
        }
        if(token == inputs::saveLocation.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.saveLocation.setHandle(hdl);
            return;
        }
        if(token == inputs::skipInactive.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.skipInactive.setHandle(hdl);
            return;
        }
        if(token == inputs::startFrame.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.startFrame.setHandle(hdl);
            return;
        }
        if(token == outputs::gpu.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.gpu.setHandle(hdl);
            return;
        }
        if(token == outputs::rp.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rp.setHandle(hdl);
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
        auto variable = const_cast<OgnGpuInteropCpuToDiskDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropCpuToDiskDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropCpuToDiskDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropCpuToDiskDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnGpuInteropCpuToDiskDatabase::sm_stateManagerOgnGpuInteropCpuToDisk;
std::tuple<int, int, int> OgnGpuInteropCpuToDiskDatabase::sm_generatorVersionOgnGpuInteropCpuToDisk{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnGpuInteropCpuToDiskDatabase::sm_targetVersionOgnGpuInteropCpuToDisk{std::make_tuple(2,184,5)};
}
using namespace IOgnGpuInteropCpuToDisk;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnGpuInteropCpuToDisk, OgnGpuInteropCpuToDiskDatabase> s_registration("omni.graph.examples.cpp.GpuInteropCpuToDisk", 2, "omni.graph.image.nodes"); \
}
