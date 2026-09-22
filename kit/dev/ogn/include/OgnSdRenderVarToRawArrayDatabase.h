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

namespace OgnSdRenderVarToRawArrayAttributes
{
namespace inputs
{
using cudaStream_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaStream("inputs:cudaStream", "uint64", kExtendedAttributeType_Regular, 0);
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using renderResults_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> renderResults("inputs:renderResults", "uint64", kExtendedAttributeType_Regular, 0);
using renderVar_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderVar("inputs:renderVar", "token", kExtendedAttributeType_Regular);
}
namespace outputs
{
using bufferSize_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> bufferSize("outputs:bufferSize", "uint64", kExtendedAttributeType_Regular);
using cudaStream_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> cudaStream("outputs:cudaStream", "uint64", kExtendedAttributeType_Regular);
using data_t_cpu = ogn::array<uint8_t>&;
using data_t_gpu = uint8_t**;
ogn::AttributeInitializer<uint8_t*, ogn::kOgnOutput> data("outputs:data", "uchar[]", kExtendedAttributeType_Regular, nullptr, 0);
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using format_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> format("outputs:format", "uint64", kExtendedAttributeType_Regular);
using height_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> height("outputs:height", "uint", kExtendedAttributeType_Regular);
using strides_t = pxr::GfVec2i&;
ogn::AttributeInitializer<pxr::GfVec2i, ogn::kOgnOutput> strides("outputs:strides", "int2", kExtendedAttributeType_Regular);
using width_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> width("outputs:width", "uint", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdRenderVarToRawArrayAttributes;
namespace IOgnSdRenderVarToRawArray
{
// Synthetic Data action node to copy the input rendervar into an output raw array
class OgnSdRenderVarToRawArrayDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdRenderVarToRawArray.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdRenderVarToRawArray.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdRenderVarToRawArray.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdRenderVarToRawArray.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdRenderVarToRawArray;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdRenderVarToRawArray;
    static std::tuple<int, int, int>sm_targetVersionOgnSdRenderVarToRawArray;
    static constexpr size_t staticAttributeCount = 14;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : cudaStream{offset}
        , exec{offset,AttributeRole::eExecution}
        , renderResults{offset}
        , renderVar{offset}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaStream;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> renderResults;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderVar;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : bufferSize{offset}
        , cudaStream{offset}
        , data{offset}
        , exec{offset,AttributeRole::eExecution}
        , format{offset}
        , height{offset}
        , strides{offset}
        , width{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> bufferSize;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> cudaStream;
        ogn::ArrayOutput<uint8_t,ogn::kAny,PtrToPtrKind::eCpuPtrToGpuPtr> data;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> format;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> height;
        ogn::SimpleOutput<pxr::GfVec2i,ogn::kCpu> strides;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> width;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdRenderVarToRawArrayDatabase(NodeObj const& nodeObjParam)
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
    OgnSdRenderVarToRawArrayDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdRenderVarToRawArrayDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdRenderVarToRawArrayDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::cudaStream.m_token, inputs::exec.m_token, inputs::renderResults.m_token, inputs::renderVar.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::bufferSize.m_token, outputs::cudaStream.m_token, outputs::exec.m_token, outputs::format.m_token,
                    outputs::height.m_token, outputs::strides.m_token, outputs::width.m_token
                )
            , kAccordingToContextIndex);
            inputs.cudaStream.setContext(contextObj);
            inputs.cudaStream.setHandle(std::get<0>(inputDataHandles0));
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<1>(inputDataHandles0));
            inputs.renderResults.setContext(contextObj);
            inputs.renderResults.setHandle(std::get<2>(inputDataHandles0));
            inputs.renderVar.setContext(contextObj);
            inputs.renderVar.setHandle(std::get<3>(inputDataHandles0));
            outputs.bufferSize.setContext(contextObj);
            outputs.bufferSize.setHandle(std::get<0>(outputDataHandles0));
            outputs.cudaStream.setContext(contextObj);
            outputs.cudaStream.setHandle(std::get<1>(outputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<2>(outputDataHandles0));
            outputs.format.setContext(contextObj);
            outputs.format.setHandle(std::get<3>(outputDataHandles0));
            outputs.height.setContext(contextObj);
            outputs.height.setHandle(std::get<4>(outputDataHandles0));
            outputs.strides.setContext(contextObj);
            outputs.strides.setHandle(std::get<5>(outputDataHandles0));
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
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::data.m_token
                )
            , kAccordingToContextIndex);
            outputs.data.setContext(contextObj);
            outputs.data.setHandle(std::get<0>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdRenderVarToRawArray");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::cudaStream.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderResults.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderVar.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::bufferSize.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::cudaStream.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::data.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::format.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::strides.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::width.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:action");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data action node to copy the input rendervar into an output raw array");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExclusions, "tests");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to the CUDA stream");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderResults.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Render results pointer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderVar.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the renderVar");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, outputs::bufferSize.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Size (in bytes) of the buffer (0 if the input is a texture)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cudaStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to the CUDA stream");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, outputs::data.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Buffer array data");
        attr.iAttribute->setMetadata(attr, kOgnMetadataMemoryType, "any");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Executes when the event is received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Received");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, outputs::format.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Format");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, outputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Height  (0 if the input is a buffer)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, outputs::strides.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Strides (in bytes) ([0,0] if the input is a buffer)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
        attr = iNode->getAttributeByToken(nodeObj, outputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Width  (0 if the input is a buffer)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataCudaPointers, "cpu");
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
        sm_stateManagerOgnSdRenderVarToRawArray.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cudaStream.isValid()
            && inputs.exec.isValid()
            && inputs.renderResults.isValid()
            && inputs.renderVar.isValid()
            && outputs.bufferSize.isValid()
            && outputs.cudaStream.isValid()
            && outputs.data.isValid()
            && outputs.exec.isValid()
            && outputs.format.isValid()
            && outputs.height.isValid()
            && outputs.strides.isValid()
            && outputs.width.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cudaStream.invalidateCachedPointer();
            inputs.exec.invalidateCachedPointer();
            inputs.renderResults.invalidateCachedPointer();
            inputs.renderVar.invalidateCachedPointer();
            outputs.bufferSize.invalidateCachedPointer();
            outputs.cudaStream.invalidateCachedPointer();
            outputs.data.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.format.invalidateCachedPointer();
            outputs.height.invalidateCachedPointer();
            outputs.strides.invalidateCachedPointer();
            outputs.width.invalidateCachedPointer();
            return;
        }
        outputs.data.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cudaStream.m_token) {
                inputs.cudaStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderResults.m_token) {
                inputs.renderResults.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderVar.m_token) {
                inputs.renderVar.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::bufferSize.m_token) {
                outputs.bufferSize.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cudaStream.m_token) {
                outputs.cudaStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::data.m_token) {
                outputs.data.invalidateCachedPointer();
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
            if(attrib == outputs::height.m_token) {
                outputs.height.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::strides.m_token) {
                outputs.strides.invalidateCachedPointer();
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
        if( !inputs.cudaStream.canVectorize()
            || !inputs.exec.canVectorize()
            || !inputs.renderResults.canVectorize()
            || !inputs.renderVar.canVectorize()
            || !outputs.bufferSize.canVectorize()
            || !outputs.cudaStream.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.format.canVectorize()
            || !outputs.height.canVectorize()
            || !outputs.strides.canVectorize()
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
        if(token == inputs::cudaStream.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cudaStream.setHandle(hdl);
            return;
        }
        if(token == inputs::exec.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exec.setHandle(hdl);
            return;
        }
        if(token == inputs::renderResults.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderResults.setHandle(hdl);
            return;
        }
        if(token == inputs::renderVar.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderVar.setHandle(hdl);
            return;
        }
        if(token == outputs::bufferSize.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.bufferSize.setHandle(hdl);
            return;
        }
        if(token == outputs::cudaStream.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cudaStream.setHandle(hdl);
            return;
        }
        if(token == outputs::data.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.data.setHandle(hdl);
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
        if(token == outputs::height.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.height.setHandle(hdl);
            return;
        }
        if(token == outputs::strides.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.strides.setHandle(hdl);
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
ogn::StateManager OgnSdRenderVarToRawArrayDatabase::sm_stateManagerOgnSdRenderVarToRawArray;
std::tuple<int, int, int> OgnSdRenderVarToRawArrayDatabase::sm_generatorVersionOgnSdRenderVarToRawArray{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdRenderVarToRawArrayDatabase::sm_targetVersionOgnSdRenderVarToRawArray{std::make_tuple(2,184,5)};
}
using namespace IOgnSdRenderVarToRawArray;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdRenderVarToRawArray, OgnSdRenderVarToRawArrayDatabase> s_registration("omni.syntheticdata.SdRenderVarToRawArray", 2, "omni.syntheticdata"); \
}
#else
#include <cuda_fp16.h>
#include <omni/graph/core/Handle.h>
#include <omni/graph/core/cuda/CUDAUtils.h>
#include <stdint.h>
namespace OgnSdRenderVarToRawArrayCudaTypes
{
namespace inputs
{
using cudaStream_t = const uint64_t;
using exec_t = const int;
using renderResults_t = const uint64_t;
using renderVar_t = const NameToken;
}
namespace outputs
{
using bufferSize_t = uint64_t;
using cudaStream_t = uint64_t;
using data_t = uint8_t**;
using exec_t = int;
using format_t = uint64_t;
using height_t = uint32_t;
using strides_t = int3;
using width_t = uint32_t;
}
namespace state
{
}
}
using namespace OgnSdRenderVarToRawArrayCudaTypes;
#endif
