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
#include <omni/graph/core/GpuInteropEntryUserData.h>
#include <carb/cudainterop/CudaInterop.h>

namespace OgnRenderPreprocessEntryAttributes
{
namespace inputs
{
}
namespace outputs
{
using hydraTime_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> hydraTime("outputs:hydraTime", "double", kExtendedAttributeType_Regular);
using rationalTimeOfSimDenominator_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> rationalTimeOfSimDenominator("outputs:rationalTimeOfSimDenominator", "uint64", kExtendedAttributeType_Regular);
using rationalTimeOfSimNumerator_t = int64_t&;
ogn::AttributeInitializer<int64_t, ogn::kOgnOutput> rationalTimeOfSimNumerator("outputs:rationalTimeOfSimNumerator", "int64", kExtendedAttributeType_Regular);
using simTime_t = double&;
ogn::AttributeInitializer<double, ogn::kOgnOutput> simTime("outputs:simTime", "double", kExtendedAttributeType_Regular);
using stream_t = uint64_t&;
ogn::AttributeInitializer<uint64_t, ogn::kOgnOutput> stream("outputs:stream", "uint64", kExtendedAttributeType_Regular);
}
namespace state
{
}
}
using namespace OgnRenderPreprocessEntryAttributes;
namespace IOgnRenderPreprocessEntry
{
// Entry node for pre-processing hydra render results for a single view. All downstream
// nodes are scheduled as CUDA commands.
class OgnRenderPreprocessEntryDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnRenderPreprocessEntry.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnRenderPreprocessEntry.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnRenderPreprocessEntry.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnRenderPreprocessEntry.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnRenderPreprocessEntry;
    static std::tuple<int, int, int>sm_generatorVersionOgnRenderPreprocessEntry;
    static std::tuple<int, int, int>sm_targetVersionOgnRenderPreprocessEntry;
    static constexpr size_t staticAttributeCount = 7;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct outputsT {
        outputsT(size_t const& offset)
        : hydraTime{offset}
        , rationalTimeOfSimDenominator{offset}
        , rationalTimeOfSimNumerator{offset}
        , simTime{offset}
        , stream{offset}
        {}
        ogn::SimpleOutput<double,ogn::kCpu> hydraTime;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> rationalTimeOfSimDenominator;
        ogn::SimpleOutput<int64_t,ogn::kCpu> rationalTimeOfSimNumerator;
        ogn::SimpleOutput<double,ogn::kCpu> simTime;
        ogn::SimpleOutput<uint64_t,ogn::kCpu> stream;
    } outputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnRenderPreprocessEntryDatabase(NodeObj const& nodeObjParam)
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
    OgnRenderPreprocessEntryDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnRenderPreprocessEntryDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnRenderPreprocessEntryDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                    outputs::hydraTime.m_token, outputs::rationalTimeOfSimDenominator.m_token, outputs::rationalTimeOfSimNumerator.m_token, outputs::simTime.m_token,
                    outputs::stream.m_token
                )
            , kAccordingToContextIndex);
            outputs.hydraTime.setContext(contextObj);
            outputs.hydraTime.setHandle(std::get<0>(outputDataHandles0));
            outputs.rationalTimeOfSimDenominator.setContext(contextObj);
            outputs.rationalTimeOfSimDenominator.setHandle(std::get<1>(outputDataHandles0));
            outputs.rationalTimeOfSimNumerator.setContext(contextObj);
            outputs.rationalTimeOfSimNumerator.setHandle(std::get<2>(outputDataHandles0));
            outputs.simTime.setContext(contextObj);
            outputs.simTime.setHandle(std::get<3>(outputDataHandles0));
            outputs.stream.setContext(contextObj);
            outputs.stream.setHandle(std::get<4>(outputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.graph.nodes.RenderPreProcessEntry");
            return;
        }
        auto& iToken{ *iTokenPtr };


        outputs::hydraTime.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rationalTimeOfSimDenominator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::rationalTimeOfSimNumerator.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::simTime.initialize(iToken, *iNodeType, nodeTypeObj);
        outputs::stream.initialize(iToken, *iNodeType, nodeTypeObj);

        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.graph.image.nodes");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataUiName, "Render Preprocess Entry");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "graph:preRender,rendering");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Entry node for pre-processing hydra render results for a single view. All downstream nodes are scheduled as CUDA commands.");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, outputs::hydraTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The time difference since the last rendered frame.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Renderer Time");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rationalTimeOfSimDenominator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The denominator of the simulation time expressed as rational time. \nIt is always valid and may be used to fetch data from Fabric during the node compute.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Rational Time Of Sim Denominator");
        attr = iNode->getAttributeByToken(nodeObj, outputs::rationalTimeOfSimNumerator.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The numerator of the simulation time expressed as rational time. \nIt is always valid and may be used to fetch data from Fabric during the node compute.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Rational Time Of Sim Numerator");
        attr = iNode->getAttributeByToken(nodeObj, outputs::simTime.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The time difference since the last simulation frame.\nMay suffer from loss of precision and cannot be used as a deterministic identifier, \nfor example for fetching data from Fabric during the node compute - \nuse the Rational Time instead in that case.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Simulation Time");
        attr = iNode->getAttributeByToken(nodeObj, outputs::stream.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "The CUDA Stream used to order the CUDA commands scheduled by this graph execution.");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Stream");
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
        sm_stateManagerOgnRenderPreprocessEntry.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && outputs.hydraTime.isValid()
            && outputs.rationalTimeOfSimDenominator.isValid()
            && outputs.rationalTimeOfSimNumerator.isValid()
            && outputs.simTime.isValid()
            && outputs.stream.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            outputs.hydraTime.invalidateCachedPointer();
            outputs.rationalTimeOfSimDenominator.invalidateCachedPointer();
            outputs.rationalTimeOfSimNumerator.invalidateCachedPointer();
            outputs.simTime.invalidateCachedPointer();
            outputs.stream.invalidateCachedPointer();
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == outputs::hydraTime.m_token) {
                outputs.hydraTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::rationalTimeOfSimDenominator.m_token) {
                outputs.rationalTimeOfSimDenominator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::rationalTimeOfSimNumerator.m_token) {
                outputs.rationalTimeOfSimNumerator.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::simTime.m_token) {
                outputs.simTime.invalidateCachedPointer();
                continue;
            }
            if(attrib == outputs::stream.m_token) {
                outputs.stream.invalidateCachedPointer();
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
        if( !outputs.hydraTime.canVectorize()
            || !outputs.rationalTimeOfSimDenominator.canVectorize()
            || !outputs.rationalTimeOfSimNumerator.canVectorize()
            || !outputs.simTime.canVectorize()
            || !outputs.stream.canVectorize()
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
        if(token == outputs::hydraTime.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.hydraTime.setHandle(hdl);
            return;
        }
        if(token == outputs::rationalTimeOfSimDenominator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rationalTimeOfSimDenominator.setHandle(hdl);
            return;
        }
        if(token == outputs::rationalTimeOfSimNumerator.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.rationalTimeOfSimNumerator.setHandle(hdl);
            return;
        }
        if(token == outputs::simTime.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.simTime.setHandle(hdl);
            return;
        }
        if(token == outputs::stream.m_token) {
            AttributeDataHandle hdl = attr.iAttribute->getAttributeDataHandle(attr, m_offset);
            outputs.stream.setHandle(hdl);
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
    cudaStream_t getCudaStream(InstanceIndex relativeIdx = { 0 }) const {
        auto variable = const_cast<OgnRenderPreprocessEntryDatabase*>(this)->getVariable("__cudaStream", m_offset + relativeIdx);
        return variable.isValid() ? reinterpret_cast<cudaStream_t>(*variable.get<uint64_t>()) : cudaStream_t{};
    }
};
ogn::StateManager OgnRenderPreprocessEntryDatabase::sm_stateManagerOgnRenderPreprocessEntry;
std::tuple<int, int, int> OgnRenderPreprocessEntryDatabase::sm_generatorVersionOgnRenderPreprocessEntry{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnRenderPreprocessEntryDatabase::sm_targetVersionOgnRenderPreprocessEntry{std::make_tuple(2,184,5)};
}
using namespace IOgnRenderPreprocessEntry;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnRenderPreprocessEntry, OgnRenderPreprocessEntryDatabase> s_registration("omni.graph.nodes.RenderPreProcessEntry", 3, "omni.graph.image.nodes"); \
}
