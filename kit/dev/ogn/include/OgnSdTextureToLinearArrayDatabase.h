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

namespace OgnSdTextureToLinearArrayAttributes
{
namespace inputs
{
using cudaMipmappedArray_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaMipmappedArray("inputs:cudaMipmappedArray", "uint64", kExtendedAttributeType_Regular, 0);
using format_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> format("inputs:format", "uint64", kExtendedAttributeType_Regular, 0);
using height_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> height("inputs:height", "uint", kExtendedAttributeType_Regular, 0);
using hydraTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTime("inputs:hydraTime", "double", kExtendedAttributeType_Regular, 0.0);
using mipCount_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> mipCount("inputs:mipCount", "uint", kExtendedAttributeType_Regular, 0);
using outputHeight_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> outputHeight("inputs:outputHeight", "uint", kExtendedAttributeType_Regular, 0);
using outputWidth_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> outputWidth("inputs:outputWidth", "uint", kExtendedAttributeType_Regular, 0);
using simTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTime("inputs:simTime", "double", kExtendedAttributeType_Regular, 0.0);
using stream_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> stream("inputs:stream", "uint64", kExtendedAttributeType_Regular, 0);
using width_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> width("inputs:width", "uint", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using data_t_cpu = ogn::array<pxr::GfVec4f>&;
using data_t = pxr::GfVec4f**;
ogn::AttributeInitializer<pxr::GfVec4f*, ogn::kOgnOutput> data("outputs:data", "float4[]", kExtendedAttributeType_Regular, nullptr, 0);
using height_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> height("outputs:height", "uint", kExtendedAttributeType_Regular);
using hydraTime_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> hydraTime("outputs:hydraTime", "double", kExtendedAttributeType_Regular);
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
using namespace OgnSdTextureToLinearArrayAttributes;
namespace IOgnSdTextureToLinearArray
{
// SyntheticData node to copy the input texture into a linear array buffer
class OgnSdTextureToLinearArrayDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdTextureToLinearArray.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdTextureToLinearArray.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdTextureToLinearArray.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdTextureToLinearArray.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdTextureToLinearArray;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdTextureToLinearArray;
    static std::tuple<int, int, int>sm_targetVersionOgnSdTextureToLinearArray;
    static constexpr size_t staticAttributeCount = 18;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : cudaMipmappedArray{offset}
        , format{offset}
        , height{offset}
        , hydraTime{offset}
        , mipCount{offset}
        , outputHeight{offset}
        , outputWidth{offset}
        , simTime{offset}
        , stream{offset}
        , width{offset}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaMipmappedArray;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> format;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> height;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTime;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> mipCount;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> outputHeight;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> outputWidth;
        ogn::SimpleInput<const double,ogn::kCpu> simTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> stream;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> width;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : data{offset}
        , height{offset}
        , hydraTime{offset}
        , simTime{offset}
        , stream{offset}
        , width{offset}
        {}
        ogn::ArrayOutput<pxr::GfVec4f,ogn::kCuda> data;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> height;
        ogn::SimpleOutput<double,ogn::kCpu> hydraTime;
        ogn::SimpleOutput<double,ogn::kCpu> simTime;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> stream;
        ogn::SimpleOutput<uint32_t,ogn::kCpu> width;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdTextureToLinearArrayDatabase(NodeObj const& nodeObjParam)
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
    OgnSdTextureToLinearArrayDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdTextureToLinearArrayDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdTextureToLinearArrayDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::cudaMipmappedArray.m_token, inputs::format.m_token, inputs::height.m_token, inputs::hydraTime.m_token,
                    inputs::mipCount.m_token, inputs::outputHeight.m_token, inputs::outputWidth.m_token, inputs::simTime.m_token,
                    inputs::stream.m_token, inputs::width.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::height.m_token, outputs::hydraTime.m_token, outputs::simTime.m_token, outputs::stream.m_token,
                    outputs::width.m_token
                )
            , kAccordingToContextIndex);
            inputs.cudaMipmappedArray.setContext(contextObj);
            inputs.cudaMipmappedArray.setHandle(std::get<0>(inputDataHandles0));
            inputs.format.setContext(contextObj);
            inputs.format.setHandle(std::get<1>(inputDataHandles0));
            inputs.height.setContext(contextObj);
            inputs.height.setHandle(std::get<2>(inputDataHandles0));
            inputs.hydraTime.setContext(contextObj);
            inputs.hydraTime.setHandle(std::get<3>(inputDataHandles0));
            inputs.mipCount.setContext(contextObj);
            inputs.mipCount.setHandle(std::get<4>(inputDataHandles0));
            inputs.outputHeight.setContext(contextObj);
            inputs.outputHeight.setHandle(std::get<5>(inputDataHandles0));
            inputs.outputWidth.setContext(contextObj);
            inputs.outputWidth.setHandle(std::get<6>(inputDataHandles0));
            inputs.simTime.setContext(contextObj);
            inputs.simTime.setHandle(std::get<7>(inputDataHandles0));
            inputs.stream.setContext(contextObj);
            inputs.stream.setHandle(std::get<8>(inputDataHandles0));
            inputs.width.setContext(contextObj);
            inputs.width.setHandle(std::get<9>(inputDataHandles0));
            outputs.height.setContext(contextObj);
            outputs.height.setHandle(std::get<0>(outputDataHandles0));
            outputs.hydraTime.setContext(contextObj);
            outputs.hydraTime.setHandle(std::get<1>(outputDataHandles0));
            outputs.simTime.setContext(contextObj);
            outputs.simTime.setHandle(std::get<2>(outputDataHandles0));
            outputs.stream.setContext(contextObj);
            outputs.stream.setHandle(std::get<3>(outputDataHandles0));
            outputs.width.setContext(contextObj);
            outputs.width.setHandle(std::get<4>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdTextureToLinearArray");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::cudaMipmappedArray.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::format.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::mipCount.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::outputHeight.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::outputWidth.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::stream.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::width.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::data.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTime.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::stream.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::width.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "internal");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "SyntheticData node to copy the input texture into a linear array buffer");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExclusions, "tests");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaMipmappedArray.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to the CUDA Mipmapped Array");
        attr = iNode->getAttributeByToken(nodeObj, inputs::format.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Format");
        attr = iNode->getAttributeByToken(nodeObj, inputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Height");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Hydra time in stage");
        attr = iNode->getAttributeByToken(nodeObj, inputs::mipCount.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Mip Count");
        attr = iNode->getAttributeByToken(nodeObj, inputs::outputHeight.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Requested output height");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::outputWidth.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Requested output width");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Simulation time");
        attr = iNode->getAttributeByToken(nodeObj, inputs::stream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to the CUDA Stream");
        attr = iNode->getAttributeByToken(nodeObj, inputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Width");
        attr = iNode->getAttributeByToken(nodeObj, outputs::data.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Buffer array data");
        attr.iAttribute->setMetadata(attr, kOgnMetadataMemoryType, "cuda");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[]");
        attr = iNode->getAttributeByToken(nodeObj, outputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Buffer array height");
        attr = iNode->getAttributeByToken(nodeObj, outputs::hydraTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Hydra time in stage");
        attr = iNode->getAttributeByToken(nodeObj, outputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Simulation time");
        attr = iNode->getAttributeByToken(nodeObj, outputs::stream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to the CUDA Stream");
        attr = iNode->getAttributeByToken(nodeObj, outputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Buffer array width");
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
        sm_stateManagerOgnSdTextureToLinearArray.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cudaMipmappedArray.isValid()
            && inputs.format.isValid()
            && inputs.height.isValid()
            && inputs.hydraTime.isValid()
            && inputs.mipCount.isValid()
            && inputs.outputHeight.isValid()
            && inputs.outputWidth.isValid()
            && inputs.simTime.isValid()
            && inputs.stream.isValid()
            && inputs.width.isValid()
            && outputs.data.isValid()
            && outputs.height.isValid()
            && outputs.hydraTime.isValid()
            && outputs.simTime.isValid()
            && outputs.stream.isValid()
            && outputs.width.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cudaMipmappedArray.invalidateCachedPointer();
            inputs.format.invalidateCachedPointer();
            inputs.height.invalidateCachedPointer();
            inputs.hydraTime.invalidateCachedPointer();
            inputs.mipCount.invalidateCachedPointer();
            inputs.outputHeight.invalidateCachedPointer();
            inputs.outputWidth.invalidateCachedPointer();
            inputs.simTime.invalidateCachedPointer();
            inputs.stream.invalidateCachedPointer();
            inputs.width.invalidateCachedPointer();
            outputs.data.invalidateCachedPointer();
            outputs.height.invalidateCachedPointer();
            outputs.hydraTime.invalidateCachedPointer();
            outputs.simTime.invalidateCachedPointer();
            outputs.stream.invalidateCachedPointer();
            outputs.width.invalidateCachedPointer();
            return;
        }
        outputs.data.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cudaMipmappedArray.m_token) {
                inputs.cudaMipmappedArray.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::format.m_token) {
                inputs.format.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::height.m_token) {
                inputs.height.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hydraTime.m_token) {
                inputs.hydraTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::mipCount.m_token) {
                inputs.mipCount.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::outputHeight.m_token) {
                inputs.outputHeight.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::outputWidth.m_token) {
                inputs.outputWidth.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::simTime.m_token) {
                inputs.simTime.invalidateCachedPointer();
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
            if(attrib == outputs::data.m_token) {
                outputs.data.invalidateCachedPointer();
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
        if( !inputs.cudaMipmappedArray.canVectorize()
            || !inputs.format.canVectorize()
            || !inputs.height.canVectorize()
            || !inputs.hydraTime.canVectorize()
            || !inputs.mipCount.canVectorize()
            || !inputs.outputHeight.canVectorize()
            || !inputs.outputWidth.canVectorize()
            || !inputs.simTime.canVectorize()
            || !inputs.stream.canVectorize()
            || !inputs.width.canVectorize()
            || !outputs.height.canVectorize()
            || !outputs.hydraTime.canVectorize()
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
        if(token == inputs::cudaMipmappedArray.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cudaMipmappedArray.setHandle(hdl);
            return;
        }
        if(token == inputs::format.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.format.setHandle(hdl);
            return;
        }
        if(token == inputs::height.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.height.setHandle(hdl);
            return;
        }
        if(token == inputs::hydraTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hydraTime.setHandle(hdl);
            return;
        }
        if(token == inputs::mipCount.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.mipCount.setHandle(hdl);
            return;
        }
        if(token == inputs::outputHeight.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.outputHeight.setHandle(hdl);
            return;
        }
        if(token == inputs::outputWidth.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.outputWidth.setHandle(hdl);
            return;
        }
        if(token == inputs::simTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.simTime.setHandle(hdl);
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
        if(token == outputs::data.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.data.setHandle(hdl);
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
};
ogn::StateManager OgnSdTextureToLinearArrayDatabase::sm_stateManagerOgnSdTextureToLinearArray;
std::tuple<int, int, int> OgnSdTextureToLinearArrayDatabase::sm_generatorVersionOgnSdTextureToLinearArray{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdTextureToLinearArrayDatabase::sm_targetVersionOgnSdTextureToLinearArray{std::make_tuple(2,184,5)};
}
using namespace IOgnSdTextureToLinearArray;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdTextureToLinearArray, OgnSdTextureToLinearArrayDatabase> s_registration("omni.syntheticdata.SdTextureToLinearArray", 1, "omni.syntheticdata"); \
}
#else
#include <cuda_fp16.h>
#include <omni/graph/core/cuda/CUDAUtils.h>
#include <stdint.h>
namespace OgnSdTextureToLinearArrayCudaTypes
{
namespace inputs
{
using cudaMipmappedArray_t = const uint64_t;
using format_t = const uint64_t;
using height_t = const uint32_t;
using hydraTime_t = const double;
using mipCount_t = const uint32_t;
using outputHeight_t = const uint32_t;
using outputWidth_t = const uint32_t;
using simTime_t = const double;
using stream_t = const uint64_t;
using width_t = const uint32_t;
}
namespace outputs
{
using data_t = float4**;
using height_t = uint32_t;
using hydraTime_t = double;
using simTime_t = double;
using stream_t = uint64_t;
using width_t = uint32_t;
}
namespace state
{
}
}
using namespace OgnSdTextureToLinearArrayCudaTypes;
#endif
