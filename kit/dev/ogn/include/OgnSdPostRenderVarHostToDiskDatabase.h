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

namespace OgnSdPostRenderVarHostToDiskAttributes
{
namespace inputs
{
using detachResourceBeforeDispatch_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> detachResourceBeforeDispatch("inputs:detachResourceBeforeDispatch", "bool", kExtendedAttributeType_Regular, false);
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using outputBasename_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> outputBasename("inputs:outputBasename", "string", kExtendedAttributeType_Regular, "", 0);
using outputFolder_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> outputFolder("inputs:outputFolder", "string", kExtendedAttributeType_Regular, "/tmp/ovSdOut", 12);
using outputRationalRenderTime_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> outputRationalRenderTime("inputs:outputRationalRenderTime", "bool", kExtendedAttributeType_Regular, true);
using renderProductPath_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderProductPath("inputs:renderProductPath", "token", kExtendedAttributeType_Regular);
using renderVar_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderVar("inputs:renderVar", "token", kExtendedAttributeType_Regular);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using outputPath_t = char*&;
ogn::AttributeInitializer<char*, ogn::kOgnOutput> outputPath("outputs:outputPath", "string", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdPostRenderVarHostToDiskAttributes;
namespace IOgnSdPostRenderVarHostToDisk
{
// Dispatch the writting of a host renderVar to disk.
class OgnSdPostRenderVarHostToDiskDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdPostRenderVarHostToDisk.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdPostRenderVarHostToDisk.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdPostRenderVarHostToDisk.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdPostRenderVarHostToDisk.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdPostRenderVarHostToDisk;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdPostRenderVarHostToDisk;
    static std::tuple<int, int, int>sm_targetVersionOgnSdPostRenderVarHostToDisk;
    static constexpr size_t staticAttributeCount = 13;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : detachResourceBeforeDispatch{offset}
        , exec{offset,AttributeRole::eExecution}
        , gpu{offset}
        , outputBasename{offset,AttributeRole::eText}
        , outputFolder{offset,AttributeRole::eText}
        , outputRationalRenderTime{offset}
        , renderProductPath{offset}
        , renderVar{offset}
        , rp{offset}
        {}
        ogn::SimpleInput<const bool,ogn::kCpu> detachResourceBeforeDispatch;
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::ArrayInput<const char,ogn::kCpu> outputBasename;
        ogn::ArrayInput<const char,ogn::kCpu> outputFolder;
        ogn::SimpleInput<const bool,ogn::kCpu> outputRationalRenderTime;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderProductPath;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderVar;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , outputPath{offset,AttributeRole::eText}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::ArrayOutput<char,ogn::kCpu> outputPath;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdPostRenderVarHostToDiskDatabase(NodeObj const& nodeObjParam)
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
    OgnSdPostRenderVarHostToDiskDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdPostRenderVarHostToDiskDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdPostRenderVarHostToDiskDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::detachResourceBeforeDispatch.m_token, inputs::exec.m_token, inputs::gpu.m_token, inputs::outputBasename.m_token,
                    inputs::outputFolder.m_token, inputs::outputRationalRenderTime.m_token, inputs::renderProductPath.m_token, inputs::renderVar.m_token,
                    inputs::rp.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::outputPath.m_token
                )
            , kAccordingToContextIndex);
            inputs.detachResourceBeforeDispatch.setContext(contextObj);
            inputs.detachResourceBeforeDispatch.setHandle(std::get<0>(inputDataHandles0));
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<1>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<2>(inputDataHandles0));
            inputs.outputBasename.setContext(contextObj);
            inputs.outputBasename.setHandle(std::get<3>(inputDataHandles0));
            inputs.outputFolder.setContext(contextObj);
            inputs.outputFolder.setHandle(std::get<4>(inputDataHandles0));
            inputs.outputRationalRenderTime.setContext(contextObj);
            inputs.outputRationalRenderTime.setHandle(std::get<5>(inputDataHandles0));
            inputs.renderProductPath.setContext(contextObj);
            inputs.renderProductPath.setHandle(std::get<6>(inputDataHandles0));
            inputs.renderVar.setContext(contextObj);
            inputs.renderVar.setHandle(std::get<7>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<8>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.outputPath.setContext(contextObj);
            outputs.outputPath.setHandle(std::get<1>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdPostRenderVarHostToDisk");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::detachResourceBeforeDispatch.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::outputBasename.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::outputFolder.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::outputRationalRenderTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderProductPath.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderVar.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::outputPath.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,rendering");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Dispatch the writting of a host renderVar to disk.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::detachResourceBeforeDispatch.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Duplicate the resource before dispatching the copy");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::outputBasename.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Basename to write renderVar file. (use {renderVar} if empty)");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::outputFolder.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Folder to write renderVar file");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"/tmp/ovSdOut\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::outputRationalRenderTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Add rational render time to the basename");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "true");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderProductPath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Path of the render product prim");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderVar.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the renderVar to write to disk");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::outputPath.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Output path to be written");
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
        sm_stateManagerOgnSdPostRenderVarHostToDisk.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.detachResourceBeforeDispatch.isValid()
            && inputs.exec.isValid()
            && inputs.gpu.isValid()
            && inputs.outputBasename.isValid()
            && inputs.outputFolder.isValid()
            && inputs.outputRationalRenderTime.isValid()
            && inputs.renderProductPath.isValid()
            && inputs.renderVar.isValid()
            && inputs.rp.isValid()
            && outputs.exec.isValid()
            && outputs.outputPath.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.detachResourceBeforeDispatch.invalidateCachedPointer();
            inputs.exec.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.outputBasename.invalidateCachedPointer();
            inputs.outputFolder.invalidateCachedPointer();
            inputs.outputRationalRenderTime.invalidateCachedPointer();
            inputs.renderProductPath.invalidateCachedPointer();
            inputs.renderVar.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.outputPath.invalidateCachedPointer();
            return;
        }
        inputs.outputBasename.invalidateCachedPointer();
        inputs.outputFolder.invalidateCachedPointer();
        outputs.outputPath.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::detachResourceBeforeDispatch.m_token) {
                inputs.detachResourceBeforeDispatch.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::outputBasename.m_token) {
                inputs.outputBasename.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::outputFolder.m_token) {
                inputs.outputFolder.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::outputRationalRenderTime.m_token) {
                inputs.outputRationalRenderTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderProductPath.m_token) {
                inputs.renderProductPath.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderVar.m_token) {
                inputs.renderVar.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::outputPath.m_token) {
                outputs.outputPath.invalidateCachedPointer();
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
        if( !inputs.detachResourceBeforeDispatch.canVectorize()
            || !inputs.exec.canVectorize()
            || !inputs.gpu.canVectorize()
            || !inputs.outputRationalRenderTime.canVectorize()
            || !inputs.renderProductPath.canVectorize()
            || !inputs.renderVar.canVectorize()
            || !inputs.rp.canVectorize()
            || !outputs.exec.canVectorize()
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
        if(token == inputs::detachResourceBeforeDispatch.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.detachResourceBeforeDispatch.setHandle(hdl);
            return;
        }
        if(token == inputs::exec.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exec.setHandle(hdl);
            return;
        }
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::outputBasename.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.outputBasename.setHandle(hdl);
            return;
        }
        if(token == inputs::outputFolder.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.outputFolder.setHandle(hdl);
            return;
        }
        if(token == inputs::outputRationalRenderTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.outputRationalRenderTime.setHandle(hdl);
            return;
        }
        if(token == inputs::renderProductPath.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderProductPath.setHandle(hdl);
            return;
        }
        if(token == inputs::renderVar.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderVar.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::outputPath.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.outputPath.setHandle(hdl);
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
        auto variable = const_cast<OgnSdPostRenderVarHostToDiskDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostRenderVarHostToDiskDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostRenderVarHostToDiskDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostRenderVarHostToDiskDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdPostRenderVarHostToDiskDatabase::sm_stateManagerOgnSdPostRenderVarHostToDisk;
std::tuple<int, int, int> OgnSdPostRenderVarHostToDiskDatabase::sm_generatorVersionOgnSdPostRenderVarHostToDisk{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdPostRenderVarHostToDiskDatabase::sm_targetVersionOgnSdPostRenderVarHostToDisk{std::make_tuple(2,184,5)};
}
using namespace IOgnSdPostRenderVarHostToDisk;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdPostRenderVarHostToDisk, OgnSdPostRenderVarHostToDiskDatabase> s_registration("omni.syntheticdata.SdPostRenderVarHostToDisk", 1, "omni.syntheticdata"); \
}
