#pragma once

#ifndef __CUDACC__
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
#include <array>
#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/ArrayAttribute.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>
#include <omni/graph/core/tuple.h>

namespace OgnSdLinearArrayToTextureAttributes
{
namespace inputs
{
using data_t_cpu = const ogn::const_array<pxr::GfVec4f>&;
using data_t = const pxr::GfVec4f**;
ogn::AttributeInitializer<const pxr::GfVec4f*, ogn::kOgnInput> data("inputs:data", "float4[]", kExtendedAttributeType_Regular, nullptr, 0);
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using height_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> height("inputs:height", "uint", kExtendedAttributeType_Regular, 0);
using sdDisplayCudaMipmappedArray_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdDisplayCudaMipmappedArray("inputs:sdDisplayCudaMipmappedArray", "uint64", kExtendedAttributeType_Regular, 0);
using sdDisplayFormat_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdDisplayFormat("inputs:sdDisplayFormat", "uint64", kExtendedAttributeType_Regular, 0);
using sdDisplayHeight_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> sdDisplayHeight("inputs:sdDisplayHeight", "uint", kExtendedAttributeType_Regular, 0);
using sdDisplayStream_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdDisplayStream("inputs:sdDisplayStream", "uint64", kExtendedAttributeType_Regular, 0);
using sdDisplayWidth_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> sdDisplayWidth("inputs:sdDisplayWidth", "uint", kExtendedAttributeType_Regular, 0);
using stream_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> stream("inputs:stream", "uint64", kExtendedAttributeType_Regular, 0);
using width_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> width("inputs:width", "uint", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using cudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> cudaPtr("outputs:cudaPtr", "uint64", kExtendedAttributeType_Regular);
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using format_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> format("outputs:format", "uint64", kExtendedAttributeType_Regular);
using handlePtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> handlePtr("outputs:handlePtr", "uint64", kExtendedAttributeType_Regular);
using height_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> height("outputs:height", "uint", kExtendedAttributeType_Regular);
using stream_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> stream("outputs:stream", "uint64", kExtendedAttributeType_Regular);
using width_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> width("outputs:width", "uint", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdLinearArrayToTextureAttributes;
namespace IOgnSdLinearArrayToTexture
{
// Synthetic Data node to copy the input buffer array into a texture for visualization
class OgnSdLinearArrayToTextureDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdLinearArrayToTexture.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdLinearArrayToTexture.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdLinearArrayToTexture.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdLinearArrayToTexture.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdLinearArrayToTexture;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdLinearArrayToTexture;
    static std::tuple<int, int, int>sm_targetVersionOgnSdLinearArrayToTexture;
    static constexpr size_t staticAttributeCount = 19;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : data{offset}
        , exec{offset,AttributeRole::eExecution}
        , height{offset}
        , sdDisplayCudaMipmappedArray{offset}
        , sdDisplayFormat{offset}
        , sdDisplayHeight{offset}
        , sdDisplayStream{offset}
        , sdDisplayWidth{offset}
        , stream{offset}
        , width{offset}
        {}
        ogn::ArrayInput<const pxr::GfVec4f,ogn::kCuda> data;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> height;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdDisplayCudaMipmappedArray;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdDisplayFormat;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> sdDisplayHeight;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdDisplayStream;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> sdDisplayWidth;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> stream;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> width;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : cudaPtr{offset}
        , exec{offset,AttributeRole::eExecution}
        , format{offset}
        , handlePtr{offset}
        , height{offset}
        , stream{offset}
        , width{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> cudaPtr;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> format;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> handlePtr;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> height;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> stream;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> width;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdLinearArrayToTextureDatabase(NodeObj const& nodeObjParam)
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
    OgnSdLinearArrayToTextureDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdLinearArrayToTextureDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdLinearArrayToTextureDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::exec.m_token, inputs::height.m_token, inputs::sdDisplayCudaMipmappedArray.m_token, inputs::sdDisplayFormat.m_token,
                    inputs::sdDisplayHeight.m_token, inputs::sdDisplayStream.m_token, inputs::sdDisplayWidth.m_token, inputs::stream.m_token,
                    inputs::width.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::cudaPtr.m_token, outputs::exec.m_token, outputs::format.m_token, outputs::handlePtr.m_token,
                    outputs::height.m_token, outputs::stream.m_token, outputs::width.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.height.setContext(contextObj);
            inputs.height.setHandle(std::get<1>(inputDataHandles0));
            inputs.sdDisplayCudaMipmappedArray.setContext(contextObj);
            inputs.sdDisplayCudaMipmappedArray.setHandle(std::get<2>(inputDataHandles0));
            inputs.sdDisplayFormat.setContext(contextObj);
            inputs.sdDisplayFormat.setHandle(std::get<3>(inputDataHandles0));
            inputs.sdDisplayHeight.setContext(contextObj);
            inputs.sdDisplayHeight.setHandle(std::get<4>(inputDataHandles0));
            inputs.sdDisplayStream.setContext(contextObj);
            inputs.sdDisplayStream.setHandle(std::get<5>(inputDataHandles0));
            inputs.sdDisplayWidth.setContext(contextObj);
            inputs.sdDisplayWidth.setHandle(std::get<6>(inputDataHandles0));
            inputs.stream.setContext(contextObj);
            inputs.stream.setHandle(std::get<7>(inputDataHandles0));
            inputs.width.setContext(contextObj);
            inputs.width.setHandle(std::get<8>(inputDataHandles0));
            outputs.cudaPtr.setContext(contextObj);
            outputs.cudaPtr.setHandle(std::get<0>(outputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<1>(outputDataHandles0));
            outputs.format.setContext(contextObj);
            outputs.format.setHandle(std::get<2>(outputDataHandles0));
            outputs.handlePtr.setContext(contextObj);
            outputs.handlePtr.setHandle(std::get<3>(outputDataHandles0));
            outputs.height.setContext(contextObj);
            outputs.height.setHandle(std::get<4>(outputDataHandles0));
            outputs.stream.setContext(contextObj);
            outputs.stream.setHandle(std::get<5>(outputDataHandles0));
            outputs.width.setContext(contextObj);
            outputs.width.setHandle(std::get<6>(outputDataHandles0));
        }
        tryGetDynamicAttributes<AttributePortType::kAttributePortType_Input>(staticAttributeCount, m_dynamicInputs);
        tryGetDynamicAttributes<AttributePortType::kAttributePortType_Output>(staticAttributeCount, m_dynamicOutputs);
        tryGetDynamicAttributes<AttributePortType::kAttributePortType_State>(staticAttributeCount, m_dynamicStates);

        collectMappedAttributes(m_mappedAttributes);

        m_canCachePointers = contextObj.iContext->canCacheAttributePointers ?
                                 contextObj.iContext->canCacheAttributePointers(contextObj) : true;
        {
            auto inputDataHandles0 = getAttributesR<
                ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::data.m_token
                )
            , kAccordingToContextIndex);
            inputs.data.setContext(contextObj);
            inputs.data.setHandle(std::get<0>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdLinearArrayToTexture");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::data.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdDisplayCudaMipmappedArray.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdDisplayFormat.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdDisplayHeight.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdDisplayStream.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdDisplayWidth.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::stream.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::width.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::cudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::format.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::handlePtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::stream.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::width.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:action");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to copy the input buffer array into a texture for visualization");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExclusions, "tests");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::data.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Buffer array data");
        attr.iAttribute->setMetadata(attr, kOgnMetadataMemoryType, "cuda");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Buffer array height");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdDisplayCudaMipmappedArray.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Visualization texture CUDA mipmapped array pointer");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdDisplayFormat.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Visualization texture format");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdDisplayHeight.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Visualization texture Height");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdDisplayStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Visualization texture CUDA stream pointer");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdDisplayWidth.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Visualization texture width");
        attr = iNode->getAttributeByToken(nodeObj, inputs::stream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to the CUDA Stream");
        attr = iNode->getAttributeByToken(nodeObj, inputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Buffer array width");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture CUDA pointer");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes when the event is received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Received");
        attr = iNode->getAttributeByToken(nodeObj, outputs::format.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture format");
        attr = iNode->getAttributeByToken(nodeObj, outputs::handlePtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture handle reference");
        attr = iNode->getAttributeByToken(nodeObj, outputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture height");
        attr = iNode->getAttributeByToken(nodeObj, outputs::stream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Output texture CUDA stream pointer");
        attr = iNode->getAttributeByToken(nodeObj, outputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Display texture width");
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
        sm_stateManagerOgnSdLinearArrayToTexture.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.data.isValid()
            && inputs.exec.isValid()
            && inputs.height.isValid()
            && inputs.sdDisplayCudaMipmappedArray.isValid()
            && inputs.sdDisplayFormat.isValid()
            && inputs.sdDisplayHeight.isValid()
            && inputs.sdDisplayStream.isValid()
            && inputs.sdDisplayWidth.isValid()
            && inputs.stream.isValid()
            && inputs.width.isValid()
            && outputs.cudaPtr.isValid()
            && outputs.exec.isValid()
            && outputs.format.isValid()
            && outputs.handlePtr.isValid()
            && outputs.height.isValid()
            && outputs.stream.isValid()
            && outputs.width.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.data.invalidateCachedPointer();
            inputs.exec.invalidateCachedPointer();
            inputs.height.invalidateCachedPointer();
            inputs.sdDisplayCudaMipmappedArray.invalidateCachedPointer();
            inputs.sdDisplayFormat.invalidateCachedPointer();
            inputs.sdDisplayHeight.invalidateCachedPointer();
            inputs.sdDisplayStream.invalidateCachedPointer();
            inputs.sdDisplayWidth.invalidateCachedPointer();
            inputs.stream.invalidateCachedPointer();
            inputs.width.invalidateCachedPointer();
            outputs.cudaPtr.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.format.invalidateCachedPointer();
            outputs.handlePtr.invalidateCachedPointer();
            outputs.height.invalidateCachedPointer();
            outputs.stream.invalidateCachedPointer();
            outputs.width.invalidateCachedPointer();
            return;
        }
        inputs.data.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::data.m_token) {
                inputs.data.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::height.m_token) {
                inputs.height.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdDisplayCudaMipmappedArray.m_token) {
                inputs.sdDisplayCudaMipmappedArray.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdDisplayFormat.m_token) {
                inputs.sdDisplayFormat.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdDisplayHeight.m_token) {
                inputs.sdDisplayHeight.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdDisplayStream.m_token) {
                inputs.sdDisplayStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdDisplayWidth.m_token) {
                inputs.sdDisplayWidth.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::stream.m_token) {
                inputs.stream.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::width.m_token) {
                inputs.width.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cudaPtr.m_token) {
                outputs.cudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::format.m_token) {
                outputs.format.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::handlePtr.m_token) {
                outputs.handlePtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::height.m_token) {
                outputs.height.invalidateCachedPointer();
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
        if( !inputs.exec.canVectorize()
            || !inputs.height.canVectorize()
            || !inputs.sdDisplayCudaMipmappedArray.canVectorize()
            || !inputs.sdDisplayFormat.canVectorize()
            || !inputs.sdDisplayHeight.canVectorize()
            || !inputs.sdDisplayStream.canVectorize()
            || !inputs.sdDisplayWidth.canVectorize()
            || !inputs.stream.canVectorize()
            || !inputs.width.canVectorize()
            || !outputs.cudaPtr.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.format.canVectorize()
            || !outputs.handlePtr.canVectorize()
            || !outputs.height.canVectorize()
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
        if(token == inputs::data.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.data.setHandle(hdl);
            return;
        }
        if(token == inputs::exec.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exec.setHandle(hdl);
            return;
        }
        if(token == inputs::height.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.height.setHandle(hdl);
            return;
        }
        if(token == inputs::sdDisplayCudaMipmappedArray.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdDisplayCudaMipmappedArray.setHandle(hdl);
            return;
        }
        if(token == inputs::sdDisplayFormat.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdDisplayFormat.setHandle(hdl);
            return;
        }
        if(token == inputs::sdDisplayHeight.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdDisplayHeight.setHandle(hdl);
            return;
        }
        if(token == inputs::sdDisplayStream.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdDisplayStream.setHandle(hdl);
            return;
        }
        if(token == inputs::sdDisplayWidth.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdDisplayWidth.setHandle(hdl);
            return;
        }
        if(token == inputs::stream.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.stream.setHandle(hdl);
            return;
        }
        if(token == inputs::width.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.width.setHandle(hdl);
            return;
        }
        if(token == outputs::cudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::format.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.format.setHandle(hdl);
            return;
        }
        if(token == outputs::handlePtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.handlePtr.setHandle(hdl);
            return;
        }
        if(token == outputs::height.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.height.setHandle(hdl);
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
};
ogn::StateManager OgnSdLinearArrayToTextureDatabase::sm_stateManagerOgnSdLinearArrayToTexture;
std::tuple<int, int, int> OgnSdLinearArrayToTextureDatabase::sm_generatorVersionOgnSdLinearArrayToTexture{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdLinearArrayToTextureDatabase::sm_targetVersionOgnSdLinearArrayToTexture{std::make_tuple(2,184,5)};
}
using namespace IOgnSdLinearArrayToTexture;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdLinearArrayToTexture, OgnSdLinearArrayToTextureDatabase> s_registration("omni.syntheticdata.SdLinearArrayToTexture", 1, "omni.syntheticdata"); \
}
#else
#include <cuda_fp16.h>
#include <omni/graph/core/cuda/CUDAUtils.h>
#include <stdint.h>
namespace OgnSdLinearArrayToTextureCudaTypes
{
namespace inputs
{
using data_t = const float4**;
using exec_t = const int;
using height_t = const uint32_t;
using sdDisplayCudaMipmappedArray_t = const uint64_t;
using sdDisplayFormat_t = const uint64_t;
using sdDisplayHeight_t = const uint32_t;
using sdDisplayStream_t = const uint64_t;
using sdDisplayWidth_t = const uint32_t;
using stream_t = const uint64_t;
using width_t = const uint32_t;
}
namespace outputs
{
using cudaPtr_t = uint64_t;
using exec_t = int;
using format_t = uint64_t;
using handlePtr_t = uint64_t;
using height_t = uint32_t;
using stream_t = uint64_t;
using width_t = uint32_t;
}
namespace state
{
}
}
using namespace OgnSdLinearArrayToTextureCudaTypes;
#endif
