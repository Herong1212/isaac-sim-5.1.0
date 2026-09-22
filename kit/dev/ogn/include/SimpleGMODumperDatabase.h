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

namespace SimpleGMODumperAttributes
{
namespace inputs
{
using cudaStream_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> cudaStream("inputs:cudaStream", "uint64", kExtendedAttributeType_Regular, 0);
using dumpPackets_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> dumpPackets("inputs:dumpPackets", "bool", kExtendedAttributeType_Regular, false);
using fileName_t = const char*&;
ogn::AttributeInitializer<const char*, ogn::kOgnInput> fileName("inputs:fileName", "string", kExtendedAttributeType_Regular, "lidar.h5", 8);
using isRadar_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> isRadar("inputs:isRadar", "bool", kExtendedAttributeType_Regular, false);
using simTime_t = const double&;
ogn::AttributeInitializer<const double, ogn::kOgnInput> simTime("inputs:simTime", "double", kExtendedAttributeType_Regular, 0.0);
using src_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> src("inputs:src", "uint64", kExtendedAttributeType_Regular, 0);
using srcMeta_t = const uint64_t&;
ogn::AttributeInitializer<const uint64_t, ogn::kOgnInput> srcMeta("inputs:srcMeta", "uint64", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace SimpleGMODumperAttributes;
namespace ISimpleGMODumper
{
// Dumps GMO buffer to bin file
class SimpleGMODumperDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerSimpleGMODumper.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerSimpleGMODumper.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerSimpleGMODumper.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerSimpleGMODumper.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerSimpleGMODumper;
    static std::tuple<int, int, int>sm_generatorVersionSimpleGMODumper;
    static std::tuple<int, int, int>sm_targetVersionSimpleGMODumper;
    static constexpr size_t staticAttributeCount = 9;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : cudaStream{offset}
        , dumpPackets{offset}
        , fileName{offset,AttributeRole::eText}
        , isRadar{offset}
        , simTime{offset}
        , src{offset}
        , srcMeta{offset}
        {}
        ogn::SimpleInput<const uint64_t,ogn::kCpu> cudaStream;
        ogn::SimpleInput<const bool,ogn::kCpu> dumpPackets;
        ogn::ArrayInput<const char,ogn::kCpu> fileName;
        ogn::SimpleInput<const bool,ogn::kCpu> isRadar;
        ogn::SimpleInput<const double,ogn::kCpu> simTime;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> src;
        ogn::SimpleInput<const uint64_t,ogn::kCpu> srcMeta;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    SimpleGMODumperDatabase(NodeObj const& nodeObjParam)
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
    SimpleGMODumperDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : SimpleGMODumperDatabase(nodeObjParam)
    {}

    //Main constructor
    SimpleGMODumperDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle, ConstAttributeDataHandle, ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::cudaStream.m_token, inputs::dumpPackets.m_token, inputs::fileName.m_token, inputs::isRadar.m_token,
                    inputs::simTime.m_token, inputs::src.m_token, inputs::srcMeta.m_token
                )
            , kAccordingToContextIndex);
            inputs.cudaStream.setContext(contextObj);
            inputs.cudaStream.setHandle(std::get<0>(inputDataHandles0));
            inputs.dumpPackets.setContext(contextObj);
            inputs.dumpPackets.setHandle(std::get<1>(inputDataHandles0));
            inputs.fileName.setContext(contextObj);
            inputs.fileName.setHandle(std::get<2>(inputDataHandles0));
            inputs.isRadar.setContext(contextObj);
            inputs.isRadar.setHandle(std::get<3>(inputDataHandles0));
            inputs.simTime.setContext(contextObj);
            inputs.simTime.setHandle(std::get<4>(inputDataHandles0));
            inputs.src.setContext(contextObj);
            inputs.src.setHandle(std::get<5>(inputDataHandles0));
            inputs.srcMeta.setContext(contextObj);
            inputs.srcMeta.setHandle(std::get<6>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.sensors.nv.common.SimpleGMODumper");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::cudaStream.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::dumpPackets.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::fileName.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::isRadar.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::src.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::srcMeta.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.sensors.nv.common");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Dumps GMO buffer to bin file");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::cudaStream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Cuda Stream Input");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::dumpPackets.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Dump packets as dwBinFile");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::fileName.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "File name of the packets");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "\"lidar.h5\"");
        attr = iNode->getAttributeByToken(nodeObj, inputs::isRadar.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "True for radar sensor");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "false");
        attr = iNode->getAttributeByToken(nodeObj, inputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Simulation time given from PostProcessEntryNode");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::src.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "RtSensor buffer id");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
        attr = iNode->getAttributeByToken(nodeObj, inputs::srcMeta.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Lidar Meta Data");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "0");
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
        sm_stateManagerSimpleGMODumper.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.cudaStream.isValid()
            && inputs.dumpPackets.isValid()
            && inputs.fileName.isValid()
            && inputs.isRadar.isValid()
            && inputs.simTime.isValid()
            && inputs.src.isValid()
            && inputs.srcMeta.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.cudaStream.invalidateCachedPointer();
            inputs.dumpPackets.invalidateCachedPointer();
            inputs.fileName.invalidateCachedPointer();
            inputs.isRadar.invalidateCachedPointer();
            inputs.simTime.invalidateCachedPointer();
            inputs.src.invalidateCachedPointer();
            inputs.srcMeta.invalidateCachedPointer();
            return;
        }
        inputs.fileName.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::cudaStream.m_token) {
                inputs.cudaStream.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::dumpPackets.m_token) {
                inputs.dumpPackets.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::fileName.m_token) {
                inputs.fileName.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::isRadar.m_token) {
                inputs.isRadar.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::simTime.m_token) {
                inputs.simTime.invalidateCachedPointer();
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
        if( !inputs.cudaStream.canVectorize()
            || !inputs.dumpPackets.canVectorize()
            || !inputs.isRadar.canVectorize()
            || !inputs.simTime.canVectorize()
            || !inputs.src.canVectorize()
            || !inputs.srcMeta.canVectorize()
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
        if(token == inputs::cudaStream.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.cudaStream.setHandle(hdl);
            return;
        }
        if(token == inputs::dumpPackets.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.dumpPackets.setHandle(hdl);
            return;
        }
        if(token == inputs::fileName.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.fileName.setHandle(hdl);
            return;
        }
        if(token == inputs::isRadar.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.isRadar.setHandle(hdl);
            return;
        }
        if(token == inputs::simTime.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.simTime.setHandle(hdl);
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
ogn::StateManager SimpleGMODumperDatabase::sm_stateManagerSimpleGMODumper;
std::tuple<int, int, int> SimpleGMODumperDatabase::sm_generatorVersionSimpleGMODumper{std::make_tuple(1,79,2)};
std::tuple<int, int, int> SimpleGMODumperDatabase::sm_targetVersionSimpleGMODumper{std::make_tuple(2,184,5)};
}
using namespace ISimpleGMODumper;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<SimpleGMODumper, SimpleGMODumperDatabase> s_registration("omni.sensors.nv.common.SimpleGMODumper", 1, "omni.sensors.nv.common"); \
}
