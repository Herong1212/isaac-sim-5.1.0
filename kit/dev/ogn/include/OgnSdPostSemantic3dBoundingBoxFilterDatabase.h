#pragma once

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
#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>
#include <omni/graph/core/tuple.h>
#include <omni/graph/image/unstable/ComputeParamsBuilder.h>

namespace OgnSdPostSemantic3dBoundingBoxFilterAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using instanceMappingInfoSDPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> instanceMappingInfoSDPtr("inputs:instanceMappingInfoSDPtr", "uint64", kExtendedAttributeType_Regular, 0);
using metersPerSceneUnit_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> metersPerSceneUnit("inputs:metersPerSceneUnit", "float", kExtendedAttributeType_Regular, 0.01f);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using sdSemBBox3dCamCornersCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdSemBBox3dCamCornersCudaPtr("inputs:sdSemBBox3dCamCornersCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using sdSemBBoxInfosCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> sdSemBBoxInfosCudaPtr("inputs:sdSemBBoxInfosCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using viewportNearFar_t = const pxr::GfVec2f&;
ogn::AttributeInitializer<const pxr::GfVec2f, ogn::kOgnInput> viewportNearFar("inputs:viewportNearFar", "float2", kExtendedAttributeType_Regular, {0.0f,-1.0f});
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using sdSemBBoxInfosCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> sdSemBBoxInfosCudaPtr("outputs:sdSemBBoxInfosCudaPtr", "uint64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdPostSemantic3dBoundingBoxFilterAttributes;
namespace IOgnSdPostSemantic3dBoundingBoxFilter
{
// Synthetic Data node to cull the semantic 3d bounding boxes.
class OgnSdPostSemantic3dBoundingBoxFilterDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken SemanticBoundingBox3DInfosSD;
        NameToken SemanticBoundingBox3DFilterInfosSD;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdPostSemantic3dBoundingBoxFilter.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdPostSemantic3dBoundingBoxFilter.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdPostSemantic3dBoundingBoxFilter.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdPostSemantic3dBoundingBoxFilter.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdPostSemantic3dBoundingBoxFilter;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdPostSemantic3dBoundingBoxFilter;
    static std::tuple<int, int, int>sm_targetVersionOgnSdPostSemantic3dBoundingBoxFilter;
    static constexpr size_t staticAttributeCount = 12;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , gpu{offset}
        , instanceMappingInfoSDPtr{offset}
        , metersPerSceneUnit{offset}
        , rp{offset}
        , sdSemBBox3dCamCornersCudaPtr{offset}
        , sdSemBBoxInfosCudaPtr{offset}
        , viewportNearFar{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> instanceMappingInfoSDPtr;
        ogn::SimpleInput<const float,ogn::kCpu> metersPerSceneUnit;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdSemBBox3dCamCornersCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> sdSemBBoxInfosCudaPtr;
        ogn::SimpleInput<const pxr::GfVec2f,ogn::kCpu> viewportNearFar;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , sdSemBBoxInfosCudaPtr{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> sdSemBBoxInfosCudaPtr;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdPostSemantic3dBoundingBoxFilterDatabase(NodeObj const& nodeObjParam)
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
    OgnSdPostSemantic3dBoundingBoxFilterDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdPostSemantic3dBoundingBoxFilterDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdPostSemantic3dBoundingBoxFilterDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::exec.m_token, inputs::gpu.m_token, inputs::instanceMappingInfoSDPtr.m_token, inputs::metersPerSceneUnit.m_token,
                    inputs::rp.m_token, inputs::sdSemBBox3dCamCornersCudaPtr.m_token, inputs::sdSemBBoxInfosCudaPtr.m_token, inputs::viewportNearFar.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::sdSemBBoxInfosCudaPtr.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<1>(inputDataHandles0));
            inputs.instanceMappingInfoSDPtr.setContext(contextObj);
            inputs.instanceMappingInfoSDPtr.setHandle(std::get<2>(inputDataHandles0));
            inputs.metersPerSceneUnit.setContext(contextObj);
            inputs.metersPerSceneUnit.setHandle(std::get<3>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<4>(inputDataHandles0));
            inputs.sdSemBBox3dCamCornersCudaPtr.setContext(contextObj);
            inputs.sdSemBBox3dCamCornersCudaPtr.setHandle(std::get<5>(inputDataHandles0));
            inputs.sdSemBBoxInfosCudaPtr.setContext(contextObj);
            inputs.sdSemBBoxInfosCudaPtr.setHandle(std::get<6>(inputDataHandles0));
            inputs.viewportNearFar.setContext(contextObj);
            inputs.viewportNearFar.setHandle(std::get<7>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.sdSemBBoxInfosCudaPtr.setContext(contextObj);
            outputs.sdSemBBoxInfosCudaPtr.setHandle(std::get<1>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdPostSemantic3dBoundingBoxFilter");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdPostSemantic3dBoundingBoxFilterDatabase::tokens.SemanticBoundingBox3DInfosSD = iToken.getHandle("SemanticBoundingBox3DInfosSD");
        OgnSdPostSemantic3dBoundingBoxFilterDatabase::tokens.SemanticBoundingBox3DFilterInfosSD = iToken.getHandle("SemanticBoundingBox3DFilterInfosSD");

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::instanceMappingInfoSDPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::metersPerSceneUnit.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdSemBBox3dCamCornersCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sdSemBBoxInfosCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::viewportNearFar.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdSemBBoxInfosCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"SemanticBoundingBox3DInfosSD\", \"SemanticBoundingBox3DFilterInfosSD\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,rendering");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to cull the semantic 3d bounding boxes.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::instanceMappingInfoSDPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::metersPerSceneUnit.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Scene units to meters scale");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.01");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdSemBBox3dCamCornersCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing the projection of the 3d bounding boxes on the camera plane represented as a float3=(u,v,z,a) for each bounding box corners");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sdSemBBoxInfosCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing valid bounding boxes infos");
        attr = iNode->getAttributeByToken(nodeObj, inputs::viewportNearFar.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "near and far plane (in scene units) used to clip the 3d bounding boxes.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[0.0, -1.0]");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdSemBBoxInfosCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing valid bounding boxes infos");
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
        sm_stateManagerOgnSdPostSemantic3dBoundingBoxFilter.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.gpu.isValid()
            && inputs.instanceMappingInfoSDPtr.isValid()
            && inputs.metersPerSceneUnit.isValid()
            && inputs.rp.isValid()
            && inputs.sdSemBBox3dCamCornersCudaPtr.isValid()
            && inputs.sdSemBBoxInfosCudaPtr.isValid()
            && inputs.viewportNearFar.isValid()
            && outputs.exec.isValid()
            && outputs.sdSemBBoxInfosCudaPtr.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.instanceMappingInfoSDPtr.invalidateCachedPointer();
            inputs.metersPerSceneUnit.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.sdSemBBox3dCamCornersCudaPtr.invalidateCachedPointer();
            inputs.sdSemBBoxInfosCudaPtr.invalidateCachedPointer();
            inputs.viewportNearFar.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.sdSemBBoxInfosCudaPtr.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::exec.m_token) {
                inputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::instanceMappingInfoSDPtr.m_token) {
                inputs.instanceMappingInfoSDPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::metersPerSceneUnit.m_token) {
                inputs.metersPerSceneUnit.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdSemBBox3dCamCornersCudaPtr.m_token) {
                inputs.sdSemBBox3dCamCornersCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sdSemBBoxInfosCudaPtr.m_token) {
                inputs.sdSemBBoxInfosCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::viewportNearFar.m_token) {
                inputs.viewportNearFar.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdSemBBoxInfosCudaPtr.m_token) {
                outputs.sdSemBBoxInfosCudaPtr.invalidateCachedPointer();
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
            || !inputs.gpu.canVectorize()
            || !inputs.instanceMappingInfoSDPtr.canVectorize()
            || !inputs.metersPerSceneUnit.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.sdSemBBox3dCamCornersCudaPtr.canVectorize()
            || !inputs.sdSemBBoxInfosCudaPtr.canVectorize()
            || !inputs.viewportNearFar.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.sdSemBBoxInfosCudaPtr.canVectorize()
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
        if(token == inputs::instanceMappingInfoSDPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.instanceMappingInfoSDPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::metersPerSceneUnit.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.metersPerSceneUnit.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == inputs::sdSemBBox3dCamCornersCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdSemBBox3dCamCornersCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::sdSemBBoxInfosCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sdSemBBoxInfosCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::viewportNearFar.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.viewportNearFar.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::sdSemBBoxInfosCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdSemBBoxInfosCudaPtr.setHandle(hdl);
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
        auto variable = const_cast<OgnSdPostSemantic3dBoundingBoxFilterDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostSemantic3dBoundingBoxFilterDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostSemantic3dBoundingBoxFilterDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostSemantic3dBoundingBoxFilterDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdPostSemantic3dBoundingBoxFilterDatabase::sm_stateManagerOgnSdPostSemantic3dBoundingBoxFilter;
std::tuple<int, int, int> OgnSdPostSemantic3dBoundingBoxFilterDatabase::sm_generatorVersionOgnSdPostSemantic3dBoundingBoxFilter{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdPostSemantic3dBoundingBoxFilterDatabase::sm_targetVersionOgnSdPostSemantic3dBoundingBoxFilter{std::make_tuple(2,184,5)};
OgnSdPostSemantic3dBoundingBoxFilterDatabase::TokenManager OgnSdPostSemantic3dBoundingBoxFilterDatabase::tokens;
}
using namespace IOgnSdPostSemantic3dBoundingBoxFilter;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdPostSemantic3dBoundingBoxFilter, OgnSdPostSemantic3dBoundingBoxFilterDatabase> s_registration("omni.syntheticdata.SdPostSemantic3dBoundingBoxFilter", 1, "omni.syntheticdata"); \
}
