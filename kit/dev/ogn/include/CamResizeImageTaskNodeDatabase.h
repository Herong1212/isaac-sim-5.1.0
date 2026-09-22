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

namespace CamResizeImageTaskNodeAttributes
{
namespace inputs
{
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using hydraTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTimeIn("inputs:hydraTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using interpolationMethod_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> interpolationMethod("inputs:interpolationMethod", "token", kExtendedAttributeType_Regular);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using simTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTimeIn("inputs:simTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
using srcSubRegionHeight_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> srcSubRegionHeight("inputs:srcSubRegionHeight", "uint64", kExtendedAttributeType_Regular, 1);
using srcSubRegionMinX_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> srcSubRegionMinX("inputs:srcSubRegionMinX", "uint64", kExtendedAttributeType_Regular, 0);
using srcSubRegionMinY_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> srcSubRegionMinY("inputs:srcSubRegionMinY", "uint64", kExtendedAttributeType_Regular, 0);
using srcSubRegionWidth_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> srcSubRegionWidth("inputs:srcSubRegionWidth", "uint64", kExtendedAttributeType_Regular, 1);
using targetHeight_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> targetHeight("inputs:targetHeight", "uint64", kExtendedAttributeType_Regular, 1);
using targetWidth_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> targetWidth("inputs:targetWidth", "uint64", kExtendedAttributeType_Regular, 1);
using useSubRegion_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> useSubRegion("inputs:useSubRegion", "bool", kExtendedAttributeType_Regular, false);
}
namespace outputs
{
using dest_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> dest("outputs:dest", "uint64", kExtendedAttributeType_Regular);
using gpu_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> gpu("outputs:gpu", "uint64", kExtendedAttributeType_Regular);
using hydraTimeOut_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> hydraTimeOut("outputs:hydraTimeOut", "double", kExtendedAttributeType_Regular, 0.0);
using rp_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> rp("outputs:rp", "uint64", kExtendedAttributeType_Regular);
using simTimeOut_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> simTimeOut("outputs:simTimeOut", "double", kExtendedAttributeType_Regular, 0.0);
}
namespace state
{
}
}
using namespace CamResizeImageTaskNodeAttributes;
namespace ICamResizeImageTaskNode
{
// Resizes an RGBA image
class CamResizeImageTaskNodeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerCamResizeImageTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerCamResizeImageTaskNode.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerCamResizeImageTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerCamResizeImageTaskNode.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerCamResizeImageTaskNode;
    static std::tuple<int, int, int>sm_generatorVersionCamResizeImageTaskNode;
    static std::tuple<int, int, int>sm_targetVersionCamResizeImageTaskNode;
    static constexpr size_t staticAttributeCount = 20;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : gpu{offset}
        , hydraTimeIn{offset}
        , interpolationMethod{offset}
        , rp{offset}
        , simTimeIn{offset}
        , src{offset}
        , srcSubRegionHeight{offset}
        , srcSubRegionMinX{offset}
        , srcSubRegionMinY{offset}
        , srcSubRegionWidth{offset}
        , targetHeight{offset}
        , targetWidth{offset}
        , useSubRegion{offset}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTimeIn;
        ogn::SimpleInput<const NameToken,ogn::kCpu> interpolationMethod;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const double,ogn::kCpu> simTimeIn;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> srcSubRegionHeight;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> srcSubRegionMinX;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> srcSubRegionMinY;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> srcSubRegionWidth;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> targetHeight;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> targetWidth;
        ogn::SimpleInput<const bool,ogn::kCpu> useSubRegion;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : dest{offset}
        , gpu{offset}
        , hydraTimeOut{offset}
        , rp{offset}
        , simTimeOut{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> dest;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> gpu;
        ogn::SimpleOutput<double,ogn::kCpu> hydraTimeOut;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> rp;
        ogn::SimpleOutput<double,ogn::kCpu> simTimeOut;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    CamResizeImageTaskNodeDatabase(NodeObj const& nodeObjParam)
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
    CamResizeImageTaskNodeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : CamResizeImageTaskNodeDatabase(nodeObjParam)
    {}

    //Main constructor
    CamResizeImageTaskNodeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::gpu.m_token, inputs::hydraTimeIn.m_token, inputs::interpolationMethod.m_token, inputs::rp.m_token,
                    inputs::simTimeIn.m_token, inputs::src.m_token, inputs::srcSubRegionHeight.m_token, inputs::srcSubRegionMinX.m_token,
                    inputs::srcSubRegionMinY.m_token, inputs::srcSubRegionWidth.m_token, inputs::targetHeight.m_token, inputs::targetWidth.m_token,
                    inputs::useSubRegion.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle, AttributeDataHandle,
                AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::dest.m_token, outputs::gpu.m_token, outputs::hydraTimeOut.m_token, outputs::rp.m_token,
                    outputs::simTimeOut.m_token
                )
            , kAccordingToContextIndex);
            inputs.gpu.setContext(contextObj);
            inputs.gpu.setHandle(std::get<0>(inputDataHandles0));
            inputs.hydraTimeIn.setContext(contextObj);
            inputs.hydraTimeIn.setHandle(std::get<1>(inputDataHandles0));
            inputs.interpolationMethod.setContext(contextObj);
            inputs.interpolationMethod.setHandle(std::get<2>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<3>(inputDataHandles0));
            inputs.simTimeIn.setContext(contextObj);
            inputs.simTimeIn.setHandle(std::get<4>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<5>(inputDataHandles0));
            inputs.srcSubRegionHeight.setContext(contextObj);
            inputs.srcSubRegionHeight.setHandle(std::get<6>(inputDataHandles0));
            inputs.srcSubRegionMinX.setContext(contextObj);
            inputs.srcSubRegionMinX.setHandle(std::get<7>(inputDataHandles0));
            inputs.srcSubRegionMinY.setContext(contextObj);
            inputs.srcSubRegionMinY.setHandle(std::get<8>(inputDataHandles0));
            inputs.srcSubRegionWidth.setContext(contextObj);
            inputs.srcSubRegionWidth.setHandle(std::get<9>(inputDataHandles0));
            inputs.targetHeight.setContext(contextObj);
            inputs.targetHeight.setHandle(std::get<10>(inputDataHandles0));
            inputs.targetWidth.setContext(contextObj);
            inputs.targetWidth.setHandle(std::get<11>(inputDataHandles0));
            inputs.useSubRegion.setContext(contextObj);
            inputs.useSubRegion.setHandle(std::get<12>(inputDataHandles0));
            outputs.dest.setContext(contextObj);
            outputs.dest.setHandle(std::get<0>(outputDataHandles0));
            outputs.gpu.setContext(contextObj);
            outputs.gpu.setHandle(std::get<1>(outputDataHandles0));
            outputs.hydraTimeOut.setContext(contextObj);
            outputs.hydraTimeOut.setHandle(std::get<2>(outputDataHandles0));
            outputs.rp.setContext(contextObj);
            outputs.rp.setHandle(std::get<3>(outputDataHandles0));
            outputs.simTimeOut.setContext(contextObj);
            outputs.simTimeOut.setHandle(std::get<4>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.CamResizeImageTaskNode");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_interpolationMethod_token {"LANCZOS"};
        inputs::interpolationMethod.setDefault(inputs_interpolationMethod_token.asTokenC());
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::interpolationMethod.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::srcSubRegionHeight.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::srcSubRegionMinX.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::srcSubRegionMinY.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::srcSubRegionWidth.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::targetHeight.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::targetWidth.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::useSubRegion.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::dest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.camera");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Resizes an RGBA image");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::interpolationMethod.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Method applied to do Interpolation: NEAREST_NEIGHBOUR, LINEAR, CUBIC, SUPERSAMPLING or LANCZOS ");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"LANCZOS\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::srcSubRegionHeight.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Height of the subRegion of the source");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::srcSubRegionMinX.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The left upper corner coordinate in x");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::srcSubRegionMinY.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The left upper corner coordinate in y");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::srcSubRegionWidth.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Width of the subRegion of the source");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::targetHeight.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "width of the target image");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::targetWidth.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "width of the target image");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::useSubRegion.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Indicates whether a subRegion (ROI) shall be extracted instead of the whole image");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, outputs::dest.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Destination Buffer");
        attr = iNode->getAttributeByToken(nodeObj, outputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundationsOut");
        attr = iNode->getAttributeByToken(nodeObj, outputs::hydraTimeOut.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp output in [s]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProductOut");
        attr = iNode->getAttributeByToken(nodeObj, outputs::simTimeOut.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp output in [s]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
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
        sm_stateManagerCamResizeImageTaskNode.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.gpu.isValid()
            && inputs.hydraTimeIn.isValid()
            && inputs.interpolationMethod.isValid()
            && inputs.rp.isValid()
            && inputs.simTimeIn.isValid()
            && inputs.src.isValid()
            && inputs.srcSubRegionHeight.isValid()
            && inputs.srcSubRegionMinX.isValid()
            && inputs.srcSubRegionMinY.isValid()
            && inputs.srcSubRegionWidth.isValid()
            && inputs.targetHeight.isValid()
            && inputs.targetWidth.isValid()
            && inputs.useSubRegion.isValid()
            && outputs.dest.isValid()
            && outputs.gpu.isValid()
            && outputs.hydraTimeOut.isValid()
            && outputs.rp.isValid()
            && outputs.simTimeOut.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.gpu.invalidateCachedPointer();
            inputs.hydraTimeIn.invalidateCachedPointer();
            inputs.interpolationMethod.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.simTimeIn.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            inputs.srcSubRegionHeight.invalidateCachedPointer();
            inputs.srcSubRegionMinX.invalidateCachedPointer();
            inputs.srcSubRegionMinY.invalidateCachedPointer();
            inputs.srcSubRegionWidth.invalidateCachedPointer();
            inputs.targetHeight.invalidateCachedPointer();
            inputs.targetWidth.invalidateCachedPointer();
            inputs.useSubRegion.invalidateCachedPointer();
            outputs.dest.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.hydraTimeOut.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            outputs.simTimeOut.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hydraTimeIn.m_token) {
                inputs.hydraTimeIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::interpolationMethod.m_token) {
                inputs.interpolationMethod.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::rp.m_token) {
                inputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::simTimeIn.m_token) {
                inputs.simTimeIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::src.m_token) {
                inputs.src.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::srcSubRegionHeight.m_token) {
                inputs.srcSubRegionHeight.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::srcSubRegionMinX.m_token) {
                inputs.srcSubRegionMinX.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::srcSubRegionMinY.m_token) {
                inputs.srcSubRegionMinY.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::srcSubRegionWidth.m_token) {
                inputs.srcSubRegionWidth.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::targetHeight.m_token) {
                inputs.targetHeight.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::targetWidth.m_token) {
                inputs.targetWidth.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::useSubRegion.m_token) {
                inputs.useSubRegion.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::dest.m_token) {
                outputs.dest.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::gpu.m_token) {
                outputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::hydraTimeOut.m_token) {
                outputs.hydraTimeOut.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::rp.m_token) {
                outputs.rp.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::simTimeOut.m_token) {
                outputs.simTimeOut.invalidateCachedPointer();
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
        if( !inputs.gpu.canVectorize()
            || !inputs.hydraTimeIn.canVectorize()
            || !inputs.interpolationMethod.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.simTimeIn.canVectorize()
            || !inputs.src.canVectorize()
            || !inputs.srcSubRegionHeight.canVectorize()
            || !inputs.srcSubRegionMinX.canVectorize()
            || !inputs.srcSubRegionMinY.canVectorize()
            || !inputs.srcSubRegionWidth.canVectorize()
            || !inputs.targetHeight.canVectorize()
            || !inputs.targetWidth.canVectorize()
            || !inputs.useSubRegion.canVectorize()
            || !outputs.dest.canVectorize()
            || !outputs.gpu.canVectorize()
            || !outputs.hydraTimeOut.canVectorize()
            || !outputs.rp.canVectorize()
            || !outputs.simTimeOut.canVectorize()
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
        if(token == inputs::gpu.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.gpu.setHandle(hdl);
            return;
        }
        if(token == inputs::hydraTimeIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hydraTimeIn.setHandle(hdl);
            return;
        }
        if(token == inputs::interpolationMethod.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.interpolationMethod.setHandle(hdl);
            return;
        }
        if(token == inputs::rp.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.rp.setHandle(hdl);
            return;
        }
        if(token == inputs::simTimeIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.simTimeIn.setHandle(hdl);
            return;
        }
        if(token == inputs::src.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.src.setHandle(hdl);
            return;
        }
        if(token == inputs::srcSubRegionHeight.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.srcSubRegionHeight.setHandle(hdl);
            return;
        }
        if(token == inputs::srcSubRegionMinX.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.srcSubRegionMinX.setHandle(hdl);
            return;
        }
        if(token == inputs::srcSubRegionMinY.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.srcSubRegionMinY.setHandle(hdl);
            return;
        }
        if(token == inputs::srcSubRegionWidth.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.srcSubRegionWidth.setHandle(hdl);
            return;
        }
        if(token == inputs::targetHeight.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.targetHeight.setHandle(hdl);
            return;
        }
        if(token == inputs::targetWidth.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.targetWidth.setHandle(hdl);
            return;
        }
        if(token == inputs::useSubRegion.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.useSubRegion.setHandle(hdl);
            return;
        }
        if(token == outputs::dest.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.dest.setHandle(hdl);
            return;
        }
        if(token == outputs::gpu.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.gpu.setHandle(hdl);
            return;
        }
        if(token == outputs::hydraTimeOut.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.hydraTimeOut.setHandle(hdl);
            return;
        }
        if(token == outputs::rp.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rp.setHandle(hdl);
            return;
        }
        if(token == outputs::simTimeOut.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.simTimeOut.setHandle(hdl);
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
ogn::StateManager CamResizeImageTaskNodeDatabase::sm_stateManagerCamResizeImageTaskNode;
std::tuple<int, int, int> CamResizeImageTaskNodeDatabase::sm_generatorVersionCamResizeImageTaskNode{std::make_tuple(1,79,2)};
std::tuple<int, int, int> CamResizeImageTaskNodeDatabase::sm_targetVersionCamResizeImageTaskNode{std::make_tuple(2,184,5)};
}
using namespace ICamResizeImageTaskNode;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<CamResizeImageTaskNode, CamResizeImageTaskNodeDatabase> s_registration("omni.sensors.nv.camera.CamResizeImageTaskNode", 1, "omni.sensors.nv.camera"); \
}
