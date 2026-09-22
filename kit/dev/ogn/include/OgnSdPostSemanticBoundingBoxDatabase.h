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

namespace OgnSdPostSemanticBoundingBoxAttributes
{
namespace inputs
{
using exec_t = const uint32_t&;
ogn::AttributeInitializer<const uint32_t, ogn::kOgnInput> exec("inputs:exec", "execution", kExtendedAttributeType_Regular);
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using instanceMapSDCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> instanceMapSDCudaPtr("inputs:instanceMapSDCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using instanceMappingInfoSDPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> instanceMappingInfoSDPtr("inputs:instanceMappingInfoSDPtr", "uint64", kExtendedAttributeType_Regular, 0);
using renderProductResolution_t = const pxr::GfVec2i&;
ogn::AttributeInitializer<const pxr::GfVec2i, ogn::kOgnInput> renderProductResolution("inputs:renderProductResolution", "int2", kExtendedAttributeType_Regular, {0,0});
using renderVar_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> renderVar("inputs:renderVar", "token", kExtendedAttributeType_Regular);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using semanticLocalTransformSDCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticLocalTransformSDCudaPtr("inputs:semanticLocalTransformSDCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
using semanticMapSDCudaPtr_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> semanticMapSDCudaPtr("inputs:semanticMapSDCudaPtr", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using exec_t = uint32_t&;
ogn::AttributeInitializer<uint32_t, ogn::kOgnOutput> exec("outputs:exec", "execution", kExtendedAttributeType_Regular);
using sdSemBBoxExtentCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> sdSemBBoxExtentCudaPtr("outputs:sdSemBBoxExtentCudaPtr", "uint64", kExtendedAttributeType_Regular);
using sdSemBBoxInfosCudaPtr_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> sdSemBBoxInfosCudaPtr("outputs:sdSemBBoxInfosCudaPtr", "uint64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnSdPostSemanticBoundingBoxAttributes;
namespace IOgnSdPostSemanticBoundingBox
{
// Synthetic Data node to compute the bounding boxes of the scene semantic entities.
class OgnSdPostSemanticBoundingBoxDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken BoundingBox2DLooseSD;
        NameToken BoundingBox2DTightSD;
        NameToken SemanticBoundingBox2DExtentLooseSD;
        NameToken SemanticBoundingBox2DInfosLooseSD;
        NameToken SemanticBoundingBox2DExtentTightSD;
        NameToken SemanticBoundingBox2DInfosTightSD;
        NameToken BoundingBox3DSD;
        NameToken SemanticBoundingBox3DExtentSD;
        NameToken SemanticBoundingBox3DInfosSD;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnSdPostSemanticBoundingBox.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnSdPostSemanticBoundingBox.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnSdPostSemanticBoundingBox.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnSdPostSemanticBoundingBox.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnSdPostSemanticBoundingBox;
    static std::tuple<int, int, int>sm_generatorVersionOgnSdPostSemanticBoundingBox;
    static std::tuple<int, int, int>sm_targetVersionOgnSdPostSemanticBoundingBox;
    static constexpr size_t staticAttributeCount = 14;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , gpu{offset}
        , instanceMapSDCudaPtr{offset}
        , instanceMappingInfoSDPtr{offset}
        , renderProductResolution{offset}
        , renderVar{offset}
        , rp{offset}
        , semanticLocalTransformSDCudaPtr{offset}
        , semanticMapSDCudaPtr{offset}
        {}
        ogn::SimpleInput<const uint32_t,ogn::kCpu> exec;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> instanceMapSDCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> instanceMappingInfoSDPtr;
        ogn::SimpleInput<const pxr::GfVec2i,ogn::kCpu> renderProductResolution;
        ogn::SimpleInput<const NameToken,ogn::kCpu> renderVar;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticLocalTransformSDCudaPtr;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> semanticMapSDCudaPtr;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : exec{offset,AttributeRole::eExecution}
        , sdSemBBoxExtentCudaPtr{offset}
        , sdSemBBoxInfosCudaPtr{offset}
        {}
        ogn::SimpleOutput<uint32_t,ogn::kCpu> exec;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> sdSemBBoxExtentCudaPtr;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> sdSemBBoxInfosCudaPtr;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnSdPostSemanticBoundingBoxDatabase(NodeObj const& nodeObjParam)
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
    OgnSdPostSemanticBoundingBoxDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnSdPostSemanticBoundingBoxDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnSdPostSemanticBoundingBoxDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::exec.m_token, inputs::gpu.m_token, inputs::instanceMapSDCudaPtr.m_token, inputs::instanceMappingInfoSDPtr.m_token,
                    inputs::renderProductResolution.m_token, inputs::renderVar.m_token, inputs::rp.m_token, inputs::semanticLocalTransformSDCudaPtr.m_token,
                    inputs::semanticMapSDCudaPtr.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::exec.m_token, outputs::sdSemBBoxExtentCudaPtr.m_token, outputs::sdSemBBoxInfosCudaPtr.m_token
                )
            , kAccordingToContextIndex);
            inputs.exec.setContext(contextObj);
            inputs.exec.setHandle(std::get<0>(inputDataHandles0));
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<1>(inputDataHandles0));
            inputs.instanceMapSDCudaPtr.setContext(contextObj);
            inputs.instanceMapSDCudaPtr.setHandle(std::get<2>(inputDataHandles0));
            inputs.instanceMappingInfoSDPtr.setContext(contextObj);
            inputs.instanceMappingInfoSDPtr.setHandle(std::get<3>(inputDataHandles0));
            inputs.renderProductResolution.setContext(contextObj);
            inputs.renderProductResolution.setHandle(std::get<4>(inputDataHandles0));
            inputs.renderVar.setContext(contextObj);
            inputs.renderVar.setHandle(std::get<5>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<6>(inputDataHandles0));
            inputs.semanticLocalTransformSDCudaPtr.setContext(contextObj);
            inputs.semanticLocalTransformSDCudaPtr.setHandle(std::get<7>(inputDataHandles0));
            inputs.semanticMapSDCudaPtr.setContext(contextObj);
            inputs.semanticMapSDCudaPtr.setHandle(std::get<8>(inputDataHandles0));
            outputs.exec.setContext(contextObj);
            outputs.exec.setHandle(std::get<0>(outputDataHandles0));
            outputs.sdSemBBoxExtentCudaPtr.setContext(contextObj);
            outputs.sdSemBBoxExtentCudaPtr.setHandle(std::get<1>(outputDataHandles0));
            outputs.sdSemBBoxInfosCudaPtr.setContext(contextObj);
            outputs.sdSemBBoxInfosCudaPtr.setHandle(std::get<2>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.syntheticdata.SdPostSemanticBoundingBox");
            return;
        }
        auto& iToken{ *iTokenPtr };
        OgnSdPostSemanticBoundingBoxDatabase::tokens.BoundingBox2DLooseSD = iToken.getHandle("BoundingBox2DLooseSD");
        OgnSdPostSemanticBoundingBoxDatabase::tokens.BoundingBox2DTightSD = iToken.getHandle("BoundingBox2DTightSD");
        OgnSdPostSemanticBoundingBoxDatabase::tokens.SemanticBoundingBox2DExtentLooseSD = iToken.getHandle("SemanticBoundingBox2DExtentLooseSD");
        OgnSdPostSemanticBoundingBoxDatabase::tokens.SemanticBoundingBox2DInfosLooseSD = iToken.getHandle("SemanticBoundingBox2DInfosLooseSD");
        OgnSdPostSemanticBoundingBoxDatabase::tokens.SemanticBoundingBox2DExtentTightSD = iToken.getHandle("SemanticBoundingBox2DExtentTightSD");
        OgnSdPostSemanticBoundingBoxDatabase::tokens.SemanticBoundingBox2DInfosTightSD = iToken.getHandle("SemanticBoundingBox2DInfosTightSD");
        OgnSdPostSemanticBoundingBoxDatabase::tokens.BoundingBox3DSD = iToken.getHandle("BoundingBox3DSD");
        OgnSdPostSemanticBoundingBoxDatabase::tokens.SemanticBoundingBox3DExtentSD = iToken.getHandle("SemanticBoundingBox3DExtentSD");
        OgnSdPostSemanticBoundingBoxDatabase::tokens.SemanticBoundingBox3DInfosSD = iToken.getHandle("SemanticBoundingBox3DInfosSD");

        inputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::instanceMapSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::instanceMappingInfoSDPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderProductResolution.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::renderVar.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticLocalTransformSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::semanticMapSDCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::exec.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdSemBBoxExtentCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::sdSemBBoxInfosCudaPtr.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.syntheticdata");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataTokens, "[\"BoundingBox2DLooseSD\", \"BoundingBox2DTightSD\", \"SemanticBoundingBox2DExtentLooseSD\", \"SemanticBoundingBox2DInfosLooseSD\", \"SemanticBoundingBox2DExtentTightSD\", \"SemanticBoundingBox2DInfosTightSD\", \"BoundingBox3DSD\", \"SemanticBoundingBox3DExtentSD\", \"SemanticBoundingBox3DInfosSD\"]");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:postRender,rendering");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Synthetic Data node to compute the bounding boxes of the scene semantic entities.");
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
        attr = iNode->getAttributeByToken(nodeObj, inputs::instanceMapSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint16_t buffer pointer of size numInstances containing the instance parent semantic index");
        attr = iNode->getAttributeByToken(nodeObj, inputs::instanceMappingInfoSDPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "uint buffer pointer containing the following information : [numInstances, minInstanceId, numSemantics, minSemanticId, numProtoSemantic]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderProductResolution.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "RenderProduct resolution");
        attr = iNode->getAttributeByToken(nodeObj, inputs::renderVar.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Name of the BoundingBox RenderVar to process");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticLocalTransformSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda float44 buffer pointer of size numSemantics containing the local semantic transform");
        attr = iNode->getAttributeByToken(nodeObj, inputs::semanticMapSDCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "cuda uint16_t buffer pointer of size numSemantics containing the semantic parent semantic index");
        attr = iNode->getAttributeByToken(nodeObj, outputs::exec.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Trigger");
        attr = iNode->getAttributeByToken(nodeObj, outputs::sdSemBBoxExtentCudaPtr.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda buffer containing the extent of the bounding boxes as a float4=(u_min,v_min,u_max,v_max) for 2D or a float6=(xmin,ymin,zmin,xmax,ymax,zmax) in object space for 3D");
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
        sm_stateManagerOgnSdPostSemanticBoundingBox.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.exec.isValid()
            && inputs.gpu.isValid()
            && inputs.instanceMapSDCudaPtr.isValid()
            && inputs.instanceMappingInfoSDPtr.isValid()
            && inputs.renderProductResolution.isValid()
            && inputs.renderVar.isValid()
            && inputs.rp.isValid()
            && inputs.semanticLocalTransformSDCudaPtr.isValid()
            && inputs.semanticMapSDCudaPtr.isValid()
            && outputs.exec.isValid()
            && outputs.sdSemBBoxExtentCudaPtr.isValid()
            && outputs.sdSemBBoxInfosCudaPtr.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.exec.invalidateCachedPointer();
            inputs.gpu.invalidateCachedPointer();
            inputs.instanceMapSDCudaPtr.invalidateCachedPointer();
            inputs.instanceMappingInfoSDPtr.invalidateCachedPointer();
            inputs.renderProductResolution.invalidateCachedPointer();
            inputs.renderVar.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.semanticLocalTransformSDCudaPtr.invalidateCachedPointer();
            inputs.semanticMapSDCudaPtr.invalidateCachedPointer();
            outputs.exec.invalidateCachedPointer();
            outputs.sdSemBBoxExtentCudaPtr.invalidateCachedPointer();
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
            if(attrib == inputs::instanceMapSDCudaPtr.m_token) {
                inputs.instanceMapSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::instanceMappingInfoSDPtr.m_token) {
                inputs.instanceMappingInfoSDPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::renderProductResolution.m_token) {
                inputs.renderProductResolution.invalidateCachedPointer();
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
            if(attrib == inputs::semanticLocalTransformSDCudaPtr.m_token) {
                inputs.semanticLocalTransformSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::semanticMapSDCudaPtr.m_token) {
                inputs.semanticMapSDCudaPtr.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::exec.m_token) {
                outputs.exec.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::sdSemBBoxExtentCudaPtr.m_token) {
                outputs.sdSemBBoxExtentCudaPtr.invalidateCachedPointer();
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
            || !inputs.instanceMapSDCudaPtr.canVectorize()
            || !inputs.instanceMappingInfoSDPtr.canVectorize()
            || !inputs.renderProductResolution.canVectorize()
            || !inputs.renderVar.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.semanticLocalTransformSDCudaPtr.canVectorize()
            || !inputs.semanticMapSDCudaPtr.canVectorize()
            || !outputs.exec.canVectorize()
            || !outputs.sdSemBBoxExtentCudaPtr.canVectorize()
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
        if(token == inputs::instanceMapSDCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.instanceMapSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::instanceMappingInfoSDPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.instanceMappingInfoSDPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::renderProductResolution.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.renderProductResolution.setHandle(hdl);
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
        if(token == inputs::semanticLocalTransformSDCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticLocalTransformSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == inputs::semanticMapSDCudaPtr.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.semanticMapSDCudaPtr.setHandle(hdl);
            return;
        }
        if(token == outputs::exec.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.exec.setHandle(hdl);
            return;
        }
        if(token == outputs::sdSemBBoxExtentCudaPtr.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.sdSemBBoxExtentCudaPtr.setHandle(hdl);
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
        auto variable = const_cast<OgnSdPostSemanticBoundingBoxDatabase*>(this)->getVariable("__rpInteropState", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostSemanticBoundingBoxDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostSemanticBoundingBoxDatabase*>(this)->getVariable("__computeParams", m_offset + relativeIdx);
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
        auto variable = const_cast<OgnSdPostSemanticBoundingBoxDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnSdPostSemanticBoundingBoxDatabase::sm_stateManagerOgnSdPostSemanticBoundingBox;
std::tuple<int, int, int> OgnSdPostSemanticBoundingBoxDatabase::sm_generatorVersionOgnSdPostSemanticBoundingBox{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnSdPostSemanticBoundingBoxDatabase::sm_targetVersionOgnSdPostSemanticBoundingBox{std::make_tuple(2,184,5)};
OgnSdPostSemanticBoundingBoxDatabase::TokenManager OgnSdPostSemanticBoundingBoxDatabase::tokens;
}
using namespace IOgnSdPostSemanticBoundingBox;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnSdPostSemanticBoundingBox, OgnSdPostSemanticBoundingBoxDatabase> s_registration("omni.syntheticdata.SdPostSemanticBoundingBox", 1, "omni.syntheticdata"); \
}
