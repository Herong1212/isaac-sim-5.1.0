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
#include <omni/graph/image/unstable/ComputeParamsBuilder.h>

namespace OgnGpuInteropAdjustExposureAttributes
{
namespace inputs
{
using cudaMipmappedArray_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaMipmappedArray("inputs:cudaMipmappedArray", "uint64", kExtendedAttributeType_Regular, 0);
using exposure_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> exposure("inputs:exposure", "float", kExtendedAttributeType_Regular, 0.0f);
using format_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> format("inputs:format", "uint64", kExtendedAttributeType_Regular, 0);
using height_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> height("inputs:height", "uint", kExtendedAttributeType_Regular, 0);
using hydraTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTime("inputs:hydraTime", "double", kExtendedAttributeType_Regular, 0.0);
using mipCount_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> mipCount("inputs:mipCount", "uint", kExtendedAttributeType_Regular, 0);
using simTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTime("inputs:simTime", "double", kExtendedAttributeType_Regular, 0.0);
using stream_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> stream("inputs:stream", "uint64", kExtendedAttributeType_Regular, 0);
using width_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> width("inputs:width", "uint", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace OgnGpuInteropAdjustExposureAttributes;
namespace IOgnGpuInteropAdjustExposure
{
// RTX Renderer Postprocess Example: adjust the exposure of the rendered image. The
// node can be used in a post-render graph to change the brightness of the rendered
// image. As a CUDA interop node, the node is scheduled for execution as a CUDA command.
// If the input RenderVar is not a valid texture, the node does not produce a result.
class OgnGpuInteropAdjustExposureDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnGpuInteropAdjustExposure.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnGpuInteropAdjustExposure.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnGpuInteropAdjustExposure.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnGpuInteropAdjustExposure.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnGpuInteropAdjustExposure;
    static std::tuple<int, int, int>sm_generatorVersionOgnGpuInteropAdjustExposure;
    static std::tuple<int, int, int>sm_targetVersionOgnGpuInteropAdjustExposure;
    static constexpr size_t staticAttributeCount = 11;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : cudaMipmappedArray{offset}
        , exposure{offset}
        , format{offset}
        , height{offset}
        , hydraTime{offset}
        , mipCount{offset}
        , simTime{offset}
        , stream{offset}
        , width{offset}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaMipmappedArray;
        ogn::SimpleInput<const float,ogn::kCpu> exposure;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> format;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> height;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTime;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> mipCount;
        ogn::SimpleInput<const double,ogn::kCpu> simTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> stream;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> width;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnGpuInteropAdjustExposureDatabase(NodeObj const& nodeObjParam)
    : OmniGraphDatabase()
    , inputs{m_offset.index}
    {
        GraphContextObj const* contexts = nullptr;
        NodeObj const* nodes = nullptr;
        size_t handleCount = nodeObjParam.iNode->getAutoInstances(nodeObjParam, contexts, nodes);
        _ctor(contexts, nodes, handleCount);
        _init();
    }

    CARB_DEPRECATED("Passing the graph context to the temporary stack allocated database is not necessary anymore: you can safely remove this parameter")
    OgnGpuInteropAdjustExposureDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnGpuInteropAdjustExposureDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnGpuInteropAdjustExposureDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
    : OmniGraphDatabase()
    , inputs{m_offset.index}
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
                    inputs::cudaMipmappedArray.m_token, inputs::exposure.m_token, inputs::format.m_token, inputs::height.m_token,
                    inputs::hydraTime.m_token, inputs::mipCount.m_token, inputs::simTime.m_token, inputs::stream.m_token,
                    inputs::width.m_token
                )
            , kAccordingToContextIndex);
            inputs.cudaMipmappedArray.setContext(contextObj);
            inputs.cudaMipmappedArray.setHandle(std::get<0>(inputDataHandles0));
            inputs.exposure.setContext(contextObj);
            inputs.exposure.setHandle(std::get<1>(inputDataHandles0));
            inputs.format.setContext(contextObj);
            inputs.format.setHandle(std::get<2>(inputDataHandles0));
            inputs.height.setContext(contextObj);
            inputs.height.setHandle(std::get<3>(inputDataHandles0));
            inputs.hydraTime.setContext(contextObj);
            inputs.hydraTime.setHandle(std::get<4>(inputDataHandles0));
            inputs.mipCount.setContext(contextObj);
            inputs.mipCount.setHandle(std::get<5>(inputDataHandles0));
            inputs.simTime.setContext(contextObj);
            inputs.simTime.setHandle(std::get<6>(inputDataHandles0));
            inputs.stream.setContext(contextObj);
            inputs.stream.setHandle(std::get<7>(inputDataHandles0));
            inputs.width.setContext(contextObj);
            inputs.width.setHandle(std::get<8>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.graph.examples.cpp.GpuInteropAdjustExposure");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::cudaMipmappedArray.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exposure.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::format.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::height.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::mipCount.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::stream.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::width.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.graph.image.nodes");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataUiName, "GPU Interop Example: Adjust Render Exposure");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "examples,graph:postRender,rendering");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "RTX Renderer Postprocess Example: adjust the exposure of the rendered image. The node can be used in a post-render graph to change the brightness of the rendered image. As a CUDA interop node, the node is scheduled for execution as a CUDA command. If the input RenderVar is not a valid texture, the node does not produce a result.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaMipmappedArray.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The RenderVar data, defined as a CUDA Mipmapped Array.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "RenderVar Data");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exposure.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Exposure value (in stops). Positive values increase the brightness of the image, while negative values result in darker images. \nThe default exposure value of 0 results in an unmodified image. \nIncreasing the value by one unit, results in a doubling of the exposure and a brigher image; \ndecreasing the value by one unit results in a halving of the exposure, thus a darker image. ");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Exposure");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::format.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The texture format of the input image, matching the values of the enum carb::graphics::Format.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Texture Format");
        attr = iNode->getAttributeByToken(nodeObj, inputs::height.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The height of the input image.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Height");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The delta time of the renderer in stage.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Renderer Time");
        attr = iNode->getAttributeByToken(nodeObj, inputs::mipCount.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The number of levels of detail encoded in 'RenderVar Data'.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Mip Count");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The delta time of the simulation.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Simulation Time");
        attr = iNode->getAttributeByToken(nodeObj, inputs::stream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The CUDA Stream used to order the CUDA commands scheduled by this graph execution.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Stream");
        attr = iNode->getAttributeByToken(nodeObj, inputs::width.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The width of the input image.");
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
        sm_stateManagerOgnGpuInteropAdjustExposure.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cudaMipmappedArray.isValid()
            && inputs.exposure.isValid()
            && inputs.format.isValid()
            && inputs.height.isValid()
            && inputs.hydraTime.isValid()
            && inputs.mipCount.isValid()
            && inputs.simTime.isValid()
            && inputs.stream.isValid()
            && inputs.width.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cudaMipmappedArray.invalidateCachedPointer();
            inputs.exposure.invalidateCachedPointer();
            inputs.format.invalidateCachedPointer();
            inputs.height.invalidateCachedPointer();
            inputs.hydraTime.invalidateCachedPointer();
            inputs.mipCount.invalidateCachedPointer();
            inputs.simTime.invalidateCachedPointer();
            inputs.stream.invalidateCachedPointer();
            inputs.width.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cudaMipmappedArray.m_token) {
                inputs.cudaMipmappedArray.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::exposure.m_token) {
                inputs.exposure.invalidateCachedPointer();
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
            || !inputs.exposure.canVectorize()
            || !inputs.format.canVectorize()
            || !inputs.height.canVectorize()
            || !inputs.hydraTime.canVectorize()
            || !inputs.mipCount.canVectorize()
            || !inputs.simTime.canVectorize()
            || !inputs.stream.canVectorize()
            || !inputs.width.canVectorize()
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
        if(token == inputs::exposure.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exposure.setHandle(hdl);
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
        auto variable = const_cast<OgnGpuInteropAdjustExposureDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropAdjustExposureDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropAdjustExposureDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropAdjustExposureDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnGpuInteropAdjustExposureDatabase::sm_stateManagerOgnGpuInteropAdjustExposure;
std::tuple<int, int, int> OgnGpuInteropAdjustExposureDatabase::sm_generatorVersionOgnGpuInteropAdjustExposure{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnGpuInteropAdjustExposureDatabase::sm_targetVersionOgnGpuInteropAdjustExposure{std::make_tuple(2,184,5)};
}
using namespace IOgnGpuInteropAdjustExposure;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnGpuInteropAdjustExposure, OgnGpuInteropAdjustExposureDatabase> s_registration("omni.graph.examples.cpp.GpuInteropAdjustExposure", 2, "omni.graph.image.nodes"); \
}
