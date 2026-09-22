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
#include <array>
#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/ArrayAttribute.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>

namespace LidarPointAccumulatorAttributes
{
namespace inputs
{
using colorCode_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> colorCode("inputs:colorCode", "int", kExtendedAttributeType_Regular, 1);
using cudaStream_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaStream("inputs:cudaStream", "uint64", kExtendedAttributeType_Regular, 0);
using desiredCoordsType_t = const NameToken&;
ogn::AttributeInitializer<const NameToken, ogn::kOgnInput> desiredCoordsType("inputs:desiredCoordsType", "token", kExtendedAttributeType_Regular);
using exportBytePoints_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> exportBytePoints("inputs:exportBytePoints", "bool", kExtendedAttributeType_Regular, false);
using outputOnGPU_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> outputOnGPU("inputs:outputOnGPU", "bool", kExtendedAttributeType_Regular, false);
using publishVizPoints_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> publishVizPoints("inputs:publishVizPoints", "bool", kExtendedAttributeType_Regular, true);
using sendDataId_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> sendDataId("inputs:sendDataId", "int", kExtendedAttributeType_Regular, 0);
using sensorMount6DPose_t = const ogn::const_array<float>&;
ogn::AttributeInitializer<const float*, ogn::kOgnInput> sensorMount6DPose("inputs:sensorMount6DPose", "float[]", kExtendedAttributeType_Regular, nullptr, 0);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
using srcMeta_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> srcMeta("inputs:srcMeta", "uint64", kExtendedAttributeType_Regular, 0);
using targetPID_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> targetPID("inputs:targetPID", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
using cudaStream_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> cudaStream("outputs:cudaStream", "uint64", kExtendedAttributeType_Regular, 0);
using dest_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> dest("outputs:dest", "uint64", kExtendedAttributeType_Regular, 0);
using newData_t = bool&;
ogn::AttributeInitializer<bool, ogn::kOgnOutput> newData("outputs:newData", "bool", kExtendedAttributeType_Regular, false);
}
namespace state
{
}
}
using namespace LidarPointAccumulatorAttributes;
namespace ILidarPointAccumulator
{
// Gets pointcloud and writes it to csv file
class LidarPointAccumulatorDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    struct TokenManager
    {
        NameToken CARTESIAN;
        NameToken SPHERICAL;
    };
    static TokenManager tokens;
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerLidarPointAccumulator.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerLidarPointAccumulator.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerLidarPointAccumulator.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerLidarPointAccumulator.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerLidarPointAccumulator;
    static std::tuple<int, int, int>sm_generatorVersionLidarPointAccumulator;
    static std::tuple<int, int, int>sm_targetVersionLidarPointAccumulator;
    static constexpr size_t staticAttributeCount = 16;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : colorCode{offset}
        , cudaStream{offset}
        , desiredCoordsType{offset}
        , exportBytePoints{offset}
        , outputOnGPU{offset}
        , publishVizPoints{offset}
        , sendDataId{offset}
        , sensorMount6DPose{offset}
        , src{offset}
        , srcMeta{offset}
        , targetPID{offset}
        {}
        ogn::SimpleInput<const int,ogn::kCpu> colorCode;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaStream;
        ogn::SimpleInput<const NameToken,ogn::kCpu> desiredCoordsType;
        ogn::SimpleInput<const bool,ogn::kCpu> exportBytePoints;
        ogn::SimpleInput<const bool,ogn::kCpu> outputOnGPU;
        ogn::SimpleInput<const bool,ogn::kCpu> publishVizPoints;
        ogn::SimpleInput<const int,ogn::kCpu> sendDataId;
        ogn::ArrayInput<const float,ogn::kCpu> sensorMount6DPose;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> srcMeta;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> targetPID;
    } inputs;

    struct outputsT {
        outputsT(size_t const& offset)
        : cudaStream{offset}
        , dest{offset}
        , newData{offset}
        {}
        ogn::SimpleOutput<uint64_t,ogn::kCpu> cudaStream;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> dest;
        ogn::SimpleOutput<bool,ogn::kCpu> newData;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    LidarPointAccumulatorDatabase(NodeObj const& nodeObjParam)
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
    LidarPointAccumulatorDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : LidarPointAccumulatorDatabase(nodeObjParam)
    {}

    //Main constructor
    LidarPointAccumulatorDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::colorCode.m_token, inputs::cudaStream.m_token, inputs::desiredCoordsType.m_token, inputs::exportBytePoints.m_token,
                    inputs::outputOnGPU.m_token, inputs::publishVizPoints.m_token, inputs::sendDataId.m_token, inputs::sensorMount6DPose.m_token,
                    inputs::src.m_token, inputs::srcMeta.m_token, inputs::targetPID.m_token
                )
            , kAccordingToContextIndex);
            auto outputDataHandles0 = getAttributesW<
                AttributeDataHandle, AttributeDataHandle, AttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    outputs::cudaStream.m_token, outputs::dest.m_token, outputs::newData.m_token
                )
            , kAccordingToContextIndex);
            inputs.colorCode.setContext(contextObj);
            inputs.colorCode.setHandle(std::get<0>(inputDataHandles0));
            inputs.cudaStream.setContext(contextObj);
            inputs.cudaStream.setHandle(std::get<1>(inputDataHandles0));
            inputs.desiredCoordsType.setContext(contextObj);
            inputs.desiredCoordsType.setHandle(std::get<2>(inputDataHandles0));
            inputs.exportBytePoints.setContext(contextObj);
            inputs.exportBytePoints.setHandle(std::get<3>(inputDataHandles0));
            inputs.outputOnGPU.setContext(contextObj);
            inputs.outputOnGPU.setHandle(std::get<4>(inputDataHandles0));
            inputs.publishVizPoints.setContext(contextObj);
            inputs.publishVizPoints.setHandle(std::get<5>(inputDataHandles0));
            inputs.sendDataId.setContext(contextObj);
            inputs.sendDataId.setHandle(std::get<6>(inputDataHandles0));
            inputs.sensorMount6DPose.setContext(contextObj);
            inputs.sensorMount6DPose.setHandle(std::get<7>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<8>(inputDataHandles0));
            inputs.srcMeta.setContext(contextObj);
            inputs.srcMeta.setHandle(std::get<9>(inputDataHandles0));
            inputs.targetPID.setContext(contextObj);
            inputs.targetPID.setHandle(std::get<10>(inputDataHandles0));
            outputs.cudaStream.setContext(contextObj);
            outputs.cudaStream.setHandle(std::get<0>(outputDataHandles0));
            outputs.dest.setContext(contextObj);
            outputs.dest.setHandle(std::get<1>(outputDataHandles0));
            outputs.newData.setContext(contextObj);
            outputs.newData.setHandle(std::get<2>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.lidar.LidarPointAccumulator");
            return;
        }
        auto& iToken{ *iTokenPtr };
        LidarPointAccumulatorDatabase::tokens.CARTESIAN = iToken.getHandle("CARTESIAN");
        LidarPointAccumulatorDatabase::tokens.SPHERICAL = iToken.getHandle("SPHERICAL");

        static omni::fabric::Token inputs_desiredCoordsType_token {"CARTESIAN"};
        inputs::desiredCoordsType.setDefault(inputs_desiredCoordsType_token.asTokenC());
        inputs::colorCode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cudaStream.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::desiredCoordsType.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::exportBytePoints.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::outputOnGPU.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::publishVizPoints.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sendDataId.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sensorMount6DPose.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::srcMeta.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::targetPID.initialize(iToken, *iNodeType, nodeTypeObj);

        outputs::cudaStream.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::dest.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::newData.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.lidar");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Gets pointcloud and writes it to csv file");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::colorCode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "0 - constant, 1 - intensity, 2 - height, 3 - range, 4 - objectId, 5 - echoId, 6 - materialId");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda Stream Input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::desiredCoordsType.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Desired output coords type");
        attr.iAttribute->setMetadata(attr, kOgnMetadataAllowedTokens, "CARTESIAN,SPHERICAL");
        attr.iAttribute->setMetadata(attr, kOgnMetadataAllowedTokensRaw, "[\"CARTESIAN\", \"SPHERICAL\"]");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"CARTESIAN\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::exportBytePoints.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Export lidar points");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::outputOnGPU.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Output on GPU");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::publishVizPoints.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Export viz points");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "true");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sendDataId.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Send data id to distinguish point clouds on the receiver side");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sensorMount6DPose.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "[x,y,z,r,p,y]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Input buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::srcMeta.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Input meta data buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::targetPID.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Target process ID to send data stream to");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::cudaStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda Stream Input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::dest.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Output buffer of accumulated GenericModelOutput");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, outputs::newData.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "True if new data is published");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
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
        sm_stateManagerLidarPointAccumulator.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.colorCode.isValid()
            && inputs.cudaStream.isValid()
            && inputs.desiredCoordsType.isValid()
            && inputs.exportBytePoints.isValid()
            && inputs.outputOnGPU.isValid()
            && inputs.publishVizPoints.isValid()
            && inputs.sendDataId.isValid()
            && inputs.sensorMount6DPose.isValid()
            && inputs.src.isValid()
            && inputs.srcMeta.isValid()
            && inputs.targetPID.isValid()
            && outputs.cudaStream.isValid()
            && outputs.dest.isValid()
            && outputs.newData.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.colorCode.invalidateCachedPointer();
            inputs.cudaStream.invalidateCachedPointer();
            inputs.desiredCoordsType.invalidateCachedPointer();
            inputs.exportBytePoints.invalidateCachedPointer();
            inputs.outputOnGPU.invalidateCachedPointer();
            inputs.publishVizPoints.invalidateCachedPointer();
            inputs.sendDataId.invalidateCachedPointer();
            inputs.sensorMount6DPose.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            inputs.srcMeta.invalidateCachedPointer();
            inputs.targetPID.invalidateCachedPointer();
            outputs.cudaStream.invalidateCachedPointer();
            outputs.dest.invalidateCachedPointer();
            outputs.newData.invalidateCachedPointer();
            return;
        }
        inputs.sensorMount6DPose.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::colorCode.m_token) {
                inputs.colorCode.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cudaStream.m_token) {
                inputs.cudaStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::desiredCoordsType.m_token) {
                inputs.desiredCoordsType.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::exportBytePoints.m_token) {
                inputs.exportBytePoints.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::outputOnGPU.m_token) {
                inputs.outputOnGPU.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::publishVizPoints.m_token) {
                inputs.publishVizPoints.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sendDataId.m_token) {
                inputs.sendDataId.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sensorMount6DPose.m_token) {
                inputs.sensorMount6DPose.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::src.m_token) {
                inputs.src.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::srcMeta.m_token) {
                inputs.srcMeta.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::targetPID.m_token) {
                inputs.targetPID.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::cudaStream.m_token) {
                outputs.cudaStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::dest.m_token) {
                outputs.dest.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::newData.m_token) {
                outputs.newData.invalidateCachedPointer();
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
        if( !inputs.colorCode.canVectorize()
            || !inputs.cudaStream.canVectorize()
            || !inputs.desiredCoordsType.canVectorize()
            || !inputs.exportBytePoints.canVectorize()
            || !inputs.outputOnGPU.canVectorize()
            || !inputs.publishVizPoints.canVectorize()
            || !inputs.sendDataId.canVectorize()
            || !inputs.src.canVectorize()
            || !inputs.srcMeta.canVectorize()
            || !inputs.targetPID.canVectorize()
            || !outputs.cudaStream.canVectorize()
            || !outputs.dest.canVectorize()
            || !outputs.newData.canVectorize()
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
        if(token == inputs::colorCode.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.colorCode.setHandle(hdl);
            return;
        }
        if(token == inputs::cudaStream.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cudaStream.setHandle(hdl);
            return;
        }
        if(token == inputs::desiredCoordsType.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.desiredCoordsType.setHandle(hdl);
            return;
        }
        if(token == inputs::exportBytePoints.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.exportBytePoints.setHandle(hdl);
            return;
        }
        if(token == inputs::outputOnGPU.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.outputOnGPU.setHandle(hdl);
            return;
        }
        if(token == inputs::publishVizPoints.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.publishVizPoints.setHandle(hdl);
            return;
        }
        if(token == inputs::sendDataId.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sendDataId.setHandle(hdl);
            return;
        }
        if(token == inputs::sensorMount6DPose.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sensorMount6DPose.setHandle(hdl);
            return;
        }
        if(token == inputs::src.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.src.setHandle(hdl);
            return;
        }
        if(token == inputs::srcMeta.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.srcMeta.setHandle(hdl);
            return;
        }
        if(token == inputs::targetPID.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.targetPID.setHandle(hdl);
            return;
        }
        if(token == outputs::cudaStream.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.cudaStream.setHandle(hdl);
            return;
        }
        if(token == outputs::dest.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.dest.setHandle(hdl);
            return;
        }
        if(token == outputs::newData.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.newData.setHandle(hdl);
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
ogn::StateManager LidarPointAccumulatorDatabase::sm_stateManagerLidarPointAccumulator;
std::tuple<int, int, int> LidarPointAccumulatorDatabase::sm_generatorVersionLidarPointAccumulator{std::make_tuple(1,79,2)};
std::tuple<int, int, int> LidarPointAccumulatorDatabase::sm_targetVersionLidarPointAccumulator{std::make_tuple(2,184,5)};
LidarPointAccumulatorDatabase::TokenManager LidarPointAccumulatorDatabase::tokens;
}
using namespace ILidarPointAccumulator;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<LidarPointAccumulator, LidarPointAccumulatorDatabase> s_registration("omni.sensors.nv.lidar.LidarPointAccumulator", 1, "omni.sensors.nv.lidar"); \
}
