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

namespace OgnIndexDistributedComputeTechniqueAttributes
{
namespace inputs
{
using active_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> active("inputs:active", "bool", kExtendedAttributeType_Regular, true);
using buffers_t = const ogn::const_array<uint64_t>&;
ogn::AttributeInitializer<const uint64_t*, ogn::kOgnInput> buffers("inputs:buffers", "uint64[]", kExtendedAttributeType_Regular, nullptr, 0);
using threading_t = const bool&;
ogn::AttributeInitializer<const bool, ogn::kOgnInput> threading("inputs:threading", "bool", kExtendedAttributeType_Regular, true);
using timestep_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> timestep("inputs:timestep", "int", kExtendedAttributeType_Regular, -1);
using verbose_t = const int&;
ogn::AttributeInitializer<const int, ogn::kOgnInput> verbose("inputs:verbose", "int", kExtendedAttributeType_Regular, 0);
}
namespace outputs
{
}
namespace state
{
}
}
using namespace OgnIndexDistributedComputeTechniqueAttributes;
namespace IOgnIndexDistributedComputeTechnique
{
// Integration with NVIDIA IndeX distributed compute technique
class OgnIndexDistributedComputeTechniqueDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnIndexDistributedComputeTechnique.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnIndexDistributedComputeTechnique.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnIndexDistributedComputeTechnique.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnIndexDistributedComputeTechnique.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnIndexDistributedComputeTechnique;
    static std::tuple<int, int, int>sm_generatorVersionOgnIndexDistributedComputeTechnique;
    static std::tuple<int, int, int>sm_targetVersionOgnIndexDistributedComputeTechnique;
    static constexpr size_t staticAttributeCount = 7;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    struct inputsT {
        inputsT(size_t const& offset)
        : active{offset}
        , buffers{offset}
        , threading{offset}
        , timestep{offset}
        , verbose{offset}
        {}
        ogn::SimpleInput<const bool,ogn::kCpu> active;
        ogn::ArrayInput<const uint64_t,ogn::kCpu> buffers;
        ogn::SimpleInput<const bool,ogn::kCpu> threading;
        ogn::SimpleInput<const int,ogn::kCpu> timestep;
        ogn::SimpleInput<const int,ogn::kCpu> verbose;
    } inputs;

    //Only use this constructor for temporary stack-allocated object:
    OgnIndexDistributedComputeTechniqueDatabase(NodeObj const& nodeObjParam)
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
    OgnIndexDistributedComputeTechniqueDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnIndexDistributedComputeTechniqueDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnIndexDistributedComputeTechniqueDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
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
                ConstAttributeDataHandle
                >(contextObj, nodeObj.nodeContextHandle, std::make_tuple(
                    inputs::active.m_token, inputs::buffers.m_token, inputs::threading.m_token, inputs::timestep.m_token,
                    inputs::verbose.m_token
                )
            , kAccordingToContextIndex);
            inputs.active.setContext(contextObj);
            inputs.active.setHandle(std::get<0>(inputDataHandles0));
            inputs.buffers.setContext(contextObj);
            inputs.buffers.setHandle(std::get<1>(inputDataHandles0));
            inputs.threading.setContext(contextObj);
            inputs.threading.setHandle(std::get<2>(inputDataHandles0));
            inputs.timestep.setContext(contextObj);
            inputs.timestep.setHandle(std::get<3>(inputDataHandles0));
            inputs.verbose.setContext(contextObj);
            inputs.verbose.setHandle(std::get<4>(inputDataHandles0));
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
            CARB_LOG_ERROR("IToken not found when initializing omni.index.compute.indexDistributedComputeTechnique");
            return;
        }
        auto& iToken{ *iTokenPtr };

        inputs::active.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::buffers.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::threading.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::timestep.initialize(iToken, *iNodeType, nodeTypeObj);
        inputs::verbose.initialize(iToken, *iNodeType, nodeTypeObj);


        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "omni.index.compute");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataUiName, "NVIDIA IndeX distributed compute technique");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Integration with NVIDIA IndeX distributed compute technique");
    }
    static void initialize(const GraphContextObj&, const NodeObj& nodeObj)
    {
        const INode* iNode = nodeObj.iNode;
        AttributeObj attr;
        attr = iNode->getAttributeByToken(nodeObj, inputs::active.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "If false then disable the node operation");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Active");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "true");
        attr = iNode->getAttributeByToken(nodeObj, inputs::buffers.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Input compute buffers");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Compute buffers");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "[]");
        attr = iNode->getAttributeByToken(nodeObj, inputs::threading.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Use multithreading");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Multithreading");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "true");
        attr = iNode->getAttributeByToken(nodeObj, inputs::timestep.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Active timestep");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Timestep");
        attr.iAttribute->setMetadata(attr, kOgnMetadataDefault, "-1");
        attr = iNode->getAttributeByToken(nodeObj, inputs::verbose.token());
        attr.iAttribute->setMetadata(attr, kOgnMetadataDescription, "Log verbose output");
        attr.iAttribute->setMetadata(attr, kOgnMetadataUiName, "Verbose");
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
        sm_stateManagerOgnIndexDistributedComputeTechnique.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        return validateNode()
            && inputs.active.isValid()
            && inputs.buffers.isValid()
            && inputs.threading.isValid()
            && inputs.timestep.isValid()
            && inputs.verbose.isValid()
        ;
    }
    void preCompute() {
        if(m_canCachePointers == false) {
            inputs.active.invalidateCachedPointer();
            inputs.buffers.invalidateCachedPointer();
            inputs.threading.invalidateCachedPointer();
            inputs.timestep.invalidateCachedPointer();
            inputs.verbose.invalidateCachedPointer();
            return;
        }
        inputs.buffers.invalidateCachedPointer();
        for(NameToken const& attrib : m_mappedAttributes) {
            if(attrib == inputs::active.m_token) {
                inputs.active.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::buffers.m_token) {
                inputs.buffers.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::threading.m_token) {
                inputs.threading.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::timestep.m_token) {
                inputs.timestep.invalidateCachedPointer();
                continue;
            }
            if(attrib == inputs::verbose.m_token) {
                inputs.verbose.invalidateCachedPointer();
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
        if( !inputs.active.canVectorize()
            || !inputs.threading.canVectorize()
            || !inputs.timestep.canVectorize()
            || !inputs.verbose.canVectorize()
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
        if(token == inputs::active.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.active.setHandle(hdl);
            return;
        }
        if(token == inputs::buffers.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.buffers.setHandle(hdl);
            return;
        }
        if(token == inputs::threading.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.threading.setHandle(hdl);
            return;
        }
        if(token == inputs::timestep.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.timestep.setHandle(hdl);
            return;
        }
        if(token == inputs::verbose.m_token) {
            ConstAttributeDataHandle hdl = attr.iAttribute->getConstAttributeDataHandle(attr, m_offset);
            inputs.verbose.setHandle(hdl);
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
ogn::StateManager OgnIndexDistributedComputeTechniqueDatabase::sm_stateManagerOgnIndexDistributedComputeTechnique;
std::tuple<int, int, int> OgnIndexDistributedComputeTechniqueDatabase::sm_generatorVersionOgnIndexDistributedComputeTechnique{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnIndexDistributedComputeTechniqueDatabase::sm_targetVersionOgnIndexDistributedComputeTechnique{std::make_tuple(2,184,5)};
}
using namespace IOgnIndexDistributedComputeTechnique;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnIndexDistributedComputeTechnique, OgnIndexDistributedComputeTechniqueDatabase> s_registration("omni.index.compute.indexDistributedComputeTechnique", 1, "omni.index.compute"); \
}
