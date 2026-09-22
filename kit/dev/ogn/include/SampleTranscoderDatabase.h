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

namespace SampleTranscoderAttributes
{
namespace inputs
{
using baseDirectory_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> baseDirectory("inputs:baseDirectory", "string", kExtendedAttributeType_Regular, "", 0);
using colorCode_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> colorCode("inputs:colorCode", "int", kExtendedAttributeType_Regular, 0);
using cudaStreamIn_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaStreamIn("inputs:cudaStreamIn", "uint64", kExtendedAttributeType_Regular, 0);
using dataId_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> dataId("inputs:dataId", "int", kExtendedAttributeType_Regular, 0);
using in_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> in("inputs:in", "uint64", kExtendedAttributeType_Regular, 0);
using sensorMount6DPose_t = const ogn::const_array<float>&;
ogn::AttributeInitializer<const float*, ogn::kOgnInput> sensorMount6DPose("inputs:sensorMount6DPose", "float[]", kExtendedAttributeType_Regular, nullptr, 0);
using vizPoints_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> vizPoints("inputs:vizPoints", "bool", kExtendedAttributeType_Regular, false);
using writeFiles_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> writeFiles("inputs:writeFiles", "bool", kExtendedAttributeType_Regular, true);
using writeToBinFile_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> writeToBinFile("inputs:writeToBinFile", "bool", kExtendedAttributeType_Regular, false);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace SampleTranscoderAttributes;
namespace ISampleTranscoder
{
// Receives Radar data and prepares a buffer for it from the buffer manager, and passes
// it to output
class SampleTranscoderDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerSampleTranscoder.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerSampleTranscoder.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerSampleTranscoder.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerSampleTranscoder.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerSampleTranscoder;
    static std::tuple<int, int, int>sm_generatorVersionSampleTranscoder;
    static std::tuple<int, int, int>sm_targetVersionSampleTranscoder;
    static constexpr size_t staticAttributeCount = 11;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : baseDirectory{offset,AttributeRole::eText}
        , colorCode{offset}
        , cudaStreamIn{offset}
        , dataId{offset}
        , in{offset}
        , sensorMount6DPose{offset}
        , vizPoints{offset}
        , writeFiles{offset}
        , writeToBinFile{offset}
        {}
        ogn::ArrayInput<const char,ogn::kCpu> baseDirectory;
        ogn::SimpleInput<const int,ogn::kCpu> colorCode;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaStreamIn;
        ogn::SimpleInput<const int,ogn::kCpu> dataId;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> in;
        ogn::ArrayInput<const float,ogn::kCpu> sensorMount6DPose;
        ogn::SimpleInput<const bool,ogn::kCpu> vizPoints;
        ogn::SimpleInput<const bool,ogn::kCpu> writeFiles;
        ogn::SimpleInput<const bool,ogn::kCpu> writeToBinFile;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    SampleTranscoderDatabase(NodeObj const& nodeObjParam)
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
    SampleTranscoderDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : SampleTranscoderDatabase(nodeObjParam)
    {}

    //Main constructor
    SampleTranscoderDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    inputs::baseDirectory.m_token, inputs::colorCode.m_token, inputs::cudaStreamIn.m_token, inputs::dataId.m_token,
                    inputs::in.m_token, inputs::sensorMount6DPose.m_token, inputs::vizPoints.m_token, inputs::writeFiles.m_token,
                    inputs::writeToBinFile.m_token
                )
            , kAccordingToContextIndex);
            inputs.baseDirectory.setContext(contextObj);
            inputs.baseDirectory.setHandle(std::get<0>(inputDataHandles0));
            inputs.colorCode.setContext(contextObj);
            inputs.colorCode.setHandle(std::get<1>(inputDataHandles0));
            inputs.cudaStreamIn.setContext(contextObj);
            inputs.cudaStreamIn.setHandle(std::get<2>(inputDataHandles0));
            inputs.dataId.setContext(contextObj);
            inputs.dataId.setHandle(std::get<3>(inputDataHandles0));
            inputs.in.setContext(contextObj);
            inputs.in.setHandle(std::get<4>(inputDataHandles0));
            inputs.sensorMount6DPose.setContext(contextObj);
            inputs.sensorMount6DPose.setHandle(std::get<5>(inputDataHandles0));
            inputs.vizPoints.setContext(contextObj);
            inputs.vizPoints.setHandle(std::get<6>(inputDataHandles0));
            inputs.writeFiles.setContext(contextObj);
            inputs.writeFiles.setHandle(std::get<7>(inputDataHandles0));
            inputs.writeToBinFile.setContext(contextObj);
            inputs.writeToBinFile.setHandle(std::get<8>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.samples.SampleTranscoder");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::baseDirectory.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::colorCode.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::cudaStreamIn.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::dataId.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::in.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::sensorMount6DPose.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::vizPoints.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::writeFiles.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::writeToBinFile.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.samples");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Receives Radar data and prepares a buffer for it from the buffer manager, and passes it to output");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::baseDirectory.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Base directory of files");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::colorCode.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "0 - range, 1 - intensity");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaStreamIn.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda Stream Input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::dataId.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Unique data id for visualizer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::in.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Source Buffer");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::sensorMount6DPose.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "sensor mounting pose in vehicle coordinates as (x, y, z, roll, pitch, yaw)");
        attr = iNode->getAttributeByToken(nodeObj, inputs::vizPoints.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Publishes Points");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::writeFiles.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Write CSV Files");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "true");
        attr = iNode->getAttributeByToken(nodeObj, inputs::writeToBinFile.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Record Sample Buffer as bianry file");
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
        sm_stateManagerSampleTranscoder.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.baseDirectory.isValid()
            && inputs.colorCode.isValid()
            && inputs.cudaStreamIn.isValid()
            && inputs.dataId.isValid()
            && inputs.in.isValid()
            && inputs.sensorMount6DPose.isValid()
            && inputs.vizPoints.isValid()
            && inputs.writeFiles.isValid()
            && inputs.writeToBinFile.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.baseDirectory.invalidateCachedPointer();
            inputs.colorCode.invalidateCachedPointer();
            inputs.cudaStreamIn.invalidateCachedPointer();
            inputs.dataId.invalidateCachedPointer();
            inputs.in.invalidateCachedPointer();
            inputs.sensorMount6DPose.invalidateCachedPointer();
            inputs.vizPoints.invalidateCachedPointer();
            inputs.writeFiles.invalidateCachedPointer();
            inputs.writeToBinFile.invalidateCachedPointer();
            return;
        }
        inputs.baseDirectory.invalidateCachedPointer();
        inputs.sensorMount6DPose.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::baseDirectory.m_token) {
                inputs.baseDirectory.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::colorCode.m_token) {
                inputs.colorCode.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::cudaStreamIn.m_token) {
                inputs.cudaStreamIn.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::dataId.m_token) {
                inputs.dataId.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::in.m_token) {
                inputs.in.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::sensorMount6DPose.m_token) {
                inputs.sensorMount6DPose.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::vizPoints.m_token) {
                inputs.vizPoints.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::writeFiles.m_token) {
                inputs.writeFiles.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::writeToBinFile.m_token) {
                inputs.writeToBinFile.invalidateCachedPointer();
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
            || !inputs.cudaStreamIn.canVectorize()
            || !inputs.dataId.canVectorize()
            || !inputs.in.canVectorize()
            || !inputs.vizPoints.canVectorize()
            || !inputs.writeFiles.canVectorize()
            || !inputs.writeToBinFile.canVectorize()
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
        if(token == inputs::baseDirectory.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.baseDirectory.setHandle(hdl);
            return;
        }
        if(token == inputs::colorCode.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.colorCode.setHandle(hdl);
            return;
        }
        if(token == inputs::cudaStreamIn.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cudaStreamIn.setHandle(hdl);
            return;
        }
        if(token == inputs::dataId.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.dataId.setHandle(hdl);
            return;
        }
        if(token == inputs::in.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.in.setHandle(hdl);
            return;
        }
        if(token == inputs::sensorMount6DPose.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.sensorMount6DPose.setHandle(hdl);
            return;
        }
        if(token == inputs::vizPoints.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.vizPoints.setHandle(hdl);
            return;
        }
        if(token == inputs::writeFiles.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.writeFiles.setHandle(hdl);
            return;
        }
        if(token == inputs::writeToBinFile.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.writeToBinFile.setHandle(hdl);
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
ogn::StateManager SampleTranscoderDatabase::sm_stateManagerSampleTranscoder;
std::tuple<int, int, int> SampleTranscoderDatabase::sm_generatorVersionSampleTranscoder{std::make_tuple(1,79,2)};
std::tuple<int, int, int> SampleTranscoderDatabase::sm_targetVersionSampleTranscoder{std::make_tuple(2,184,5)};
}
using namespace ISampleTranscoder;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<SampleTranscoder, SampleTranscoderDatabase> s_registration("omni.sensors.nv.samples.SampleTranscoder", 1, "omni.sensors.nv.samples"); \
}
