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

namespace OgnGpuInteropRenderProductEntryAttributes
{
namespace inputs
{
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> gpu("outputs:gpu", "uint64", kExtendedAttributeType_Regular);
using hydraTime_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> hydraTime("outputs:hydraTime", "double", kExtendedAttributeType_Regular);
using rp_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> rp("outputs:rp", "uint64", kExtendedAttributeType_Regular);
using simTime_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> simTime("outputs:simTime", "double", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnGpuInteropRenderProductEntryAttributes;
namespace IOgnGpuInteropRenderProductEntry
{
// Entry node for post-processing hydra render results for a single view.  Gives direct
// access to the RenderProduct and GPU interfaces.
class OgnGpuInteropRenderProductEntryDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnGpuInteropRenderProductEntry.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnGpuInteropRenderProductEntry.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnGpuInteropRenderProductEntry.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnGpuInteropRenderProductEntry.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnGpuInteropRenderProductEntry;
    static std::tuple<int, int, int>sm_generatorVersionOgnGpuInteropRenderProductEntry;
    static std::tuple<int, int, int>sm_targetVersionOgnGpuInteropRenderProductEntry;
    static constexpr size_t staticAttributeCount = 7;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , gpu{offset}
        , hydraTime{offset}
        , rp{offset}
        , simTime{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> gpu;
        ogn::SimpleOutput<double,ogn::kCpu> hydraTime;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> rp;
        ogn::SimpleOutput<double,ogn::kCpu> simTime;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnGpuInteropRenderProductEntryDatabase(NodeObj const& nodeObjParam)
    : OmniGraphDatabase()
    , outputs{m_offset.index}
    {
        GraphContextObj const* contexts = nullptr;
        NodeObj const* nodes = nullptr;
        size_t handleCount = nodeObjParam.iNode->getAutoInstances(nodeObjParam, contexts, nodes);
        _ctor(contexts, nodes, handleCount);
        _init();
    }

    CARB_DEPRECATED("Passing the graph context to the temporary stack allocated database is not necessary anymore: you can safely remove this parameter")
    OgnGpuInteropRenderProductEntryDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnGpuInteropRenderProductEntryDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnGpuInteropRenderProductEntryDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
    : OmniGraphDatabase()
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
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::gpu.m_token, outputs::hydraTime.m_token, outputs::rp.m_token,
                    outputs::simTime.m_token
                )
            , kAccordingToContextIndex);
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.gpu.setContext(contextObj);
            outputs.gpu.setHandle(std::get<1>(outputDataHandles0));
            outputs.hydraTime.setContext(contextObj);
            outputs.hydraTime.setHandle(std::get<2>(outputDataHandles0));
            outputs.rp.setContext(contextObj);
            outputs.rp.setHandle(std::get<3>(outputDataHandles0));
            outputs.simTime.setContext(contextObj);
            outputs.simTime.setHandle(std::get<4>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.graph.nodes.GpuInteropRenderProductEntry");
            return;
        }
        auto& iToken{ *iTokenPtr };


        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTime.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.graph.image.nodes");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataHidden, "true");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataUiName, "GPU Interop: Render Product Entry");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "internal,graph:postRender,rendering");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Entry node for post-processing hydra render results for a single view.  Gives direct access to the RenderProduct and GPU interfaces.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger for scheduling dependencies.");
        attr = iNode->getAttributeByToken(nodeObj, outputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The shared context containing GPU foundation interfaces.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "GPU Foundations");
        attr = iNode->getAttributeByToken(nodeObj, outputs::hydraTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The time difference since the last rendered frame.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Renderer Time");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The to render product for this view.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Render Product");
        attr = iNode->getAttributeByToken(nodeObj, outputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The time difference since the last simulation frame.\nMay suffer from loss of precision and cannot be used as a deterministic identifier, \nfor example for fetching data from Fabric during the node compute.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Simulation Time");
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
        sm_stateManagerOgnGpuInteropRenderProductEntry.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && outputs.exec.isValid()
            && outputs.gpu.isValid()
            && outputs.hydraTime.isValid()
            && outputs.rp.isValid()
            && outputs.simTime.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            outputs.exec.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.hydraTime.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            outputs.simTime.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::gpu.m_token) {
                outputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::hydraTime.m_token) {
                outputs.hydraTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::rp.m_token) {
                outputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::simTime.m_token) {
                outputs.simTime.invalidateCachedPointer();
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
        if( !outputs.exec.canVectorize()
            || !outputs.gpu.canVectorize()
            || !outputs.hydraTime.canVectorize()
            || !outputs.rp.canVectorize()
            || !outputs.simTime.canVectorize()
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
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::gpu.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.gpu.setHandle(hdl);
            return;
        }
        if(token == outputs::hydraTime.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.hydraTime.setHandle(hdl);
            return;
        }
        if(token == outputs::rp.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rp.setHandle(hdl);
            return;
        }
        if(token == outputs::simTime.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.simTime.setHandle(hdl);
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
        auto variable = const_cast<OgnGpuInteropRenderProductEntryDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropRenderProductEntryDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropRenderProductEntryDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnGpuInteropRenderProductEntryDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnGpuInteropRenderProductEntryDatabase::sm_stateManagerOgnGpuInteropRenderProductEntry;
std::tuple<int, int, int> OgnGpuInteropRenderProductEntryDatabase::sm_generatorVersionOgnGpuInteropRenderProductEntry{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnGpuInteropRenderProductEntryDatabase::sm_targetVersionOgnGpuInteropRenderProductEntry{std::make_tuple(2,184,5)};
}
using namespace IOgnGpuInteropRenderProductEntry;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnGpuInteropRenderProductEntry, OgnGpuInteropRenderProductEntryDatabase> s_registration("omni.graph.nodes.GpuInteropRenderProductEntry", 2, "omni.graph.image.nodes"); \
}
