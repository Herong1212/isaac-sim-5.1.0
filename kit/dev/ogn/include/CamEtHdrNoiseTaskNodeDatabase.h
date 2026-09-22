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
#include <array>
#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/ArrayAttribute.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>
#include <omni/graph/core/tuple.h>

namespace CamEtHdrNoiseTaskNodeAttributes
{
namespace inputs
{
using gpu_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> gpu("inputs:gpu", "uint64", kExtendedAttributeType_Regular, 0);
using hdrCombinationData_t = const ogn::const_array<pxr::GfVec3f>&;
ogn::AttributeInitializer<const pxr::GfVec3f*, ogn::kOgnInput> hdrCombinationData("inputs:hdrCombinationData", "float3[]", kExtendedAttributeType_Regular, nullptr, 0);
using hydraTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> hydraTimeIn("inputs:hydraTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using realtime_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> realtime("inputs:realtime", "bool", kExtendedAttributeType_Regular, false);
using rp_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> rp("inputs:rp", "uint64", kExtendedAttributeType_Regular, 0);
using simTimeIn_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTimeIn("inputs:simTimeIn", "double", kExtendedAttributeType_Regular, 0.0);
using spatialNoiseFileExposureTime_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> spatialNoiseFileExposureTime("inputs:spatialNoiseFileExposureTime", "float", kExtendedAttributeType_Regular, 0.33f);
using spatialNoiseFileGain_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> spatialNoiseFileGain("inputs:spatialNoiseFileGain", "float", kExtendedAttributeType_Regular, 1.0f);
using spatialNoiseFilePedestal_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> spatialNoiseFilePedestal("inputs:spatialNoiseFilePedestal", "uint64", kExtendedAttributeType_Regular, 0);
using spatialNoiseFilename_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> spatialNoiseFilename("inputs:spatialNoiseFilename", "token", kExtendedAttributeType_Regular);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
using standardDeviationDarkShotNoise_t = const float&;
ogn::AttributeInitializer<const float, ogn::kOgnInput> standardDeviationDarkShotNoise("inputs:standardDeviationDarkShotNoise", "float", kExtendedAttributeType_Regular, 0.0f);
}
namespace outputs
{
using dest_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> dest("outputs:dest", "uint64", kExtendedAttributeType_Regular, 0);
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
using namespace CamEtHdrNoiseTaskNodeAttributes;
namespace ICamEtHdrNoiseTaskNode
{
// Adds Dark Noise (spatital and temporal) to the image.
class CamEtHdrNoiseTaskNodeDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerCamEtHdrNoiseTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerCamEtHdrNoiseTaskNode.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerCamEtHdrNoiseTaskNode.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerCamEtHdrNoiseTaskNode.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerCamEtHdrNoiseTaskNode;
    static std::tuple<int, int, int>sm_generatorVersionCamEtHdrNoiseTaskNode;
    static std::tuple<int, int, int>sm_targetVersionCamEtHdrNoiseTaskNode;
    static constexpr size_t staticAttributeCount = 19;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : gpu{offset}
        , hdrCombinationData{offset}
        , hydraTimeIn{offset}
        , realtime{offset}
        , rp{offset}
        , simTimeIn{offset}
        , spatialNoiseFileExposureTime{offset}
        , spatialNoiseFileGain{offset}
        , spatialNoiseFilePedestal{offset}
        , spatialNoiseFilename{offset}
        , src{offset}
        , standardDeviationDarkShotNoise{offset}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> gpu;
        ogn::ArrayInput<const pxr::GfVec3f,ogn::kCpu> hdrCombinationData;
        ogn::SimpleInput<const double,ogn::kCpu> hydraTimeIn;
        ogn::SimpleInput<const bool,ogn::kCpu> realtime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> rp;
        ogn::SimpleInput<const double,ogn::kCpu> simTimeIn;
        ogn::SimpleInput<const float,ogn::kCpu> spatialNoiseFileExposureTime;
        ogn::SimpleInput<const float,ogn::kCpu> spatialNoiseFileGain;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> spatialNoiseFilePedestal;
        ogn::SimpleInput<const NameToken,ogn::kCpu> spatialNoiseFilename;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
        ogn::SimpleInput<const float,ogn::kCpu> standardDeviationDarkShotNoise;
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
    CamEtHdrNoiseTaskNodeDatabase(NodeObj const& nodeObjParam)
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
    CamEtHdrNoiseTaskNodeDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : CamEtHdrNoiseTaskNodeDatabase(nodeObjParam)
    {}

    //Main constructor
    CamEtHdrNoiseTaskNodeDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::gpu.m_token, inputs::hdrCombinationData.m_token, inputs::hydraTimeIn.m_token, inputs::realtime.m_token,
                    inputs::rp.m_token, inputs::simTimeIn.m_token, inputs::spatialNoiseFileExposureTime.m_token, inputs::spatialNoiseFileGain.m_token,
                    inputs::spatialNoiseFilePedestal.m_token, inputs::spatialNoiseFilename.m_token, inputs::src.m_token, inputs::standardDeviationDarkShotNoise.m_token
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
            inputs.hdrCombinationData.setContext(contextObj);
            inputs.hdrCombinationData.setHandle(std::get<1>(inputDataHandles0));
            inputs.hydraTimeIn.setContext(contextObj);
            inputs.hydraTimeIn.setHandle(std::get<2>(inputDataHandles0));
            inputs.realtime.setContext(contextObj);
            inputs.realtime.setHandle(std::get<3>(inputDataHandles0));
            inputs.rp.setContext(contextObj);
            inputs.rp.setHandle(std::get<4>(inputDataHandles0));
            inputs.simTimeIn.setContext(contextObj);
            inputs.simTimeIn.setHandle(std::get<5>(inputDataHandles0));
            inputs.spatialNoiseFileExposureTime.setContext(contextObj);
            inputs.spatialNoiseFileExposureTime.setHandle(std::get<6>(inputDataHandles0));
            inputs.spatialNoiseFileGain.setContext(contextObj);
            inputs.spatialNoiseFileGain.setHandle(std::get<7>(inputDataHandles0));
            inputs.spatialNoiseFilePedestal.setContext(contextObj);
            inputs.spatialNoiseFilePedestal.setHandle(std::get<8>(inputDataHandles0));
            inputs.spatialNoiseFilename.setContext(contextObj);
            inputs.spatialNoiseFilename.setHandle(std::get<9>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<10>(inputDataHandles0));
            inputs.standardDeviationDarkShotNoise.setContext(contextObj);
            inputs.standardDeviationDarkShotNoise.setHandle(std::get<11>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.camera.CamEtHdrNoiseTask");
            return;
        }
        auto& iToken{ *iTokenPtr };

        static omni::fabric::Token inputs_spatialNoiseFilename_token {"/temp/noise_ar0820.raw"};
        inputs::spatialNoiseFilename.setDefault(inputs_spatialNoiseFilename_token.asTokenC());
        inputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hdrCombinationData.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::hydraTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::realtime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTimeIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::spatialNoiseFileExposureTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::spatialNoiseFileGain.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::spatialNoiseFilePedestal.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::spatialNoiseFilename.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::standardDeviationDarkShotNoise.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::dest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::gpu.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::hydraTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rp.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTimeOut.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.camera");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Adds Dark Noise (spatital and temporal) to the image.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::gpu.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to shared context containing gpu foundations");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "gpuFoundations");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hdrCombinationData.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Array of (gain, exposure time, max linear value) of the HDR regions");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::hydraTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::realtime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "determines how the random values are generated (true= random per image (not yet implemented), false = random per pixel");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::rp.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Pointer to render product for this view");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "renderProduct");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTimeIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "timecode/timestamp input in [ns]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::spatialNoiseFileExposureTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The exposure time in [s] ");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.33");
        attr = iNode->getAttributeByToken(nodeObj, inputs::spatialNoiseFileGain.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The total gain applied of the noise file");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1.0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::spatialNoiseFilePedestal.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The pedestal used");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::spatialNoiseFilename.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "File path to a UINT16 spatial noise file");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"/temp/noise_ar0820.raw\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::standardDeviationDarkShotNoise.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The temporal standard deviation of dark shot noise (0.0 to disable dark shot noise) ");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0.0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::dest.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Destination Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
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
        sm_stateManagerCamEtHdrNoiseTaskNode.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.gpu.isValid()
            && inputs.hdrCombinationData.isValid()
            && inputs.hydraTimeIn.isValid()
            && inputs.realtime.isValid()
            && inputs.rp.isValid()
            && inputs.simTimeIn.isValid()
            && inputs.spatialNoiseFileExposureTime.isValid()
            && inputs.spatialNoiseFileGain.isValid()
            && inputs.spatialNoiseFilePedestal.isValid()
            && inputs.spatialNoiseFilename.isValid()
            && inputs.src.isValid()
            && inputs.standardDeviationDarkShotNoise.isValid()
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
            inputs.hdrCombinationData.invalidateCachedPointer();
            inputs.hydraTimeIn.invalidateCachedPointer();
            inputs.realtime.invalidateCachedPointer();
            inputs.rp.invalidateCachedPointer();
            inputs.simTimeIn.invalidateCachedPointer();
            inputs.spatialNoiseFileExposureTime.invalidateCachedPointer();
            inputs.spatialNoiseFileGain.invalidateCachedPointer();
            inputs.spatialNoiseFilePedestal.invalidateCachedPointer();
            inputs.spatialNoiseFilename.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            inputs.standardDeviationDarkShotNoise.invalidateCachedPointer();
            outputs.dest.invalidateCachedPointer();
            outputs.gpu.invalidateCachedPointer();
            outputs.hydraTimeOut.invalidateCachedPointer();
            outputs.rp.invalidateCachedPointer();
            outputs.simTimeOut.invalidateCachedPointer();
            return;
        }
        inputs.hdrCombinationData.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::gpu.m_token) {
                inputs.gpu.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hdrCombinationData.m_token) {
                inputs.hdrCombinationData.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::hydraTimeIn.m_token) {
                inputs.hydraTimeIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::realtime.m_token) {
                inputs.realtime.invalidateCachedPointer();
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
            if(attrib == inputs::spatialNoiseFileExposureTime.m_token) {
                inputs.spatialNoiseFileExposureTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::spatialNoiseFileGain.m_token) {
                inputs.spatialNoiseFileGain.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::spatialNoiseFilePedestal.m_token) {
                inputs.spatialNoiseFilePedestal.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::spatialNoiseFilename.m_token) {
                inputs.spatialNoiseFilename.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::src.m_token) {
                inputs.src.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::standardDeviationDarkShotNoise.m_token) {
                inputs.standardDeviationDarkShotNoise.invalidateCachedPointer();
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
            || !inputs.realtime.canVectorize()
            || !inputs.rp.canVectorize()
            || !inputs.simTimeIn.canVectorize()
            || !inputs.spatialNoiseFileExposureTime.canVectorize()
            || !inputs.spatialNoiseFileGain.canVectorize()
            || !inputs.spatialNoiseFilePedestal.canVectorize()
            || !inputs.spatialNoiseFilename.canVectorize()
            || !inputs.src.canVectorize()
            || !inputs.standardDeviationDarkShotNoise.canVectorize()
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
        if(token == inputs::hdrCombinationData.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hdrCombinationData.setHandle(hdl);
            return;
        }
        if(token == inputs::hydraTimeIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.hydraTimeIn.setHandle(hdl);
            return;
        }
        if(token == inputs::realtime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.realtime.setHandle(hdl);
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
        if(token == inputs::spatialNoiseFileExposureTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.spatialNoiseFileExposureTime.setHandle(hdl);
            return;
        }
        if(token == inputs::spatialNoiseFileGain.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.spatialNoiseFileGain.setHandle(hdl);
            return;
        }
        if(token == inputs::spatialNoiseFilePedestal.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.spatialNoiseFilePedestal.setHandle(hdl);
            return;
        }
        if(token == inputs::spatialNoiseFilename.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.spatialNoiseFilename.setHandle(hdl);
            return;
        }
        if(token == inputs::src.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.src.setHandle(hdl);
            return;
        }
        if(token == inputs::standardDeviationDarkShotNoise.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.standardDeviationDarkShotNoise.setHandle(hdl);
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
ogn::StateManager CamEtHdrNoiseTaskNodeDatabase::sm_stateManagerCamEtHdrNoiseTaskNode;
std::tuple<int, int, int> CamEtHdrNoiseTaskNodeDatabase::sm_generatorVersionCamEtHdrNoiseTaskNode{std::make_tuple(1,79,2)};
std::tuple<int, int, int> CamEtHdrNoiseTaskNodeDatabase::sm_targetVersionCamEtHdrNoiseTaskNode{std::make_tuple(2,184,5)};
}
using namespace ICamEtHdrNoiseTaskNode;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<CamEtHdrNoiseTaskNode, CamEtHdrNoiseTaskNodeDatabase> s_registration("omni.sensors.nv.camera.CamEtHdrNoiseTask", 1, "omni.sensors.nv.camera"); \
}
