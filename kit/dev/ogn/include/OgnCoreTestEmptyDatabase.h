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
#include <carb/tokens/TokensUtils.h>

namespace OgnCoreTestEmptyAttributes
{
namespace inputs
{
}
namespace outputs
{
}
namespace state
{
}
}
using namespace OgnCoreTestEmptyAttributes;
namespace IOgnCoreTestEmpty
{
// Test node for omni.graph.core that does nothing and has no attributes. The version
// number is deliberately non-default so that testing can verify it. It also puts the
// icon in a non-standard location to test that feature.
class OgnCoreTestEmptyDatabase : public omni::graph::core::ogn::OmniGraphDatabase
{
public:
    template <typename StateInformation>
    CARB_DEPRECATED("sInternalState is deprecated. Use sSharedState or sPerInstanceState instead")
    static StateInformation& sInternalState(const NodeObj& nodeObj, InstanceIndex index = {kAuthoringGraphIndex}) {
        return sm_stateManagerOgnCoreTestEmpty.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sSharedState(const NodeObj& nodeObj) {
        return sm_stateManagerOgnCoreTestEmpty.getState<StateInformation>(nodeObj.nodeHandle, kAuthoringGraphIndex);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, InstanceIndex index) {
        return sm_stateManagerOgnCoreTestEmpty.getState<StateInformation>(nodeObj.nodeHandle, index);
    }
    template <typename StateInformation>
    static StateInformation& sPerInstanceState(const NodeObj& nodeObj, GraphInstanceID instanceId) {
        return sm_stateManagerOgnCoreTestEmpty.getState<StateInformation>(nodeObj.nodeHandle, instanceId);
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
    static ogn::StateManager sm_stateManagerOgnCoreTestEmpty;
    static std::tuple<int, int, int>sm_generatorVersionOgnCoreTestEmpty;
    static std::tuple<int, int, int>sm_targetVersionOgnCoreTestEmpty;
    static constexpr size_t staticAttributeCount = 2;
    std::vector<ogn::DynamicInput> m_dynamicInputs;
    std::vector<ogn::DynamicOutput> m_dynamicOutputs;
    std::vector<ogn::DynamicState> m_dynamicStates;
    std::vector<NameToken> m_mappedAttributes;
    bool m_canCachePointers{true};

    //Only use this constructor for temporary stack-allocated object:
    OgnCoreTestEmptyDatabase(NodeObj const& nodeObjParam)
    : OmniGraphDatabase()
    {
        GraphContextObj const* contexts = nullptr;
        NodeObj const* nodes = nullptr;
        size_t handleCount = nodeObjParam.iNode->getAutoInstances(nodeObjParam, contexts, nodes);
        _ctor(contexts, nodes, handleCount);
        _init();
    }

    CARB_DEPRECATED("Passing the graph context to the temporary stack allocated database is not necessary anymore: you can safely remove this parameter")
    OgnCoreTestEmptyDatabase(GraphContextObj const&, NodeObj const& nodeObjParam)
    : OgnCoreTestEmptyDatabase(nodeObjParam)
    {}

    //Main constructor
    OgnCoreTestEmptyDatabase(GraphContextObj const* contextObjParam, NodeObj const* nodeObjParam, size_t handleCount)
    : OmniGraphDatabase()
    {
        _ctor(contextObjParam, nodeObjParam, handleCount);
        _init();
    }

private:
    void _init() {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        // LCOV_EXCL_STOP
    }

public:
    static void initializeType(const NodeTypeObj& nodeTypeObj)
    {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        const INodeType* iNodeType = nodeTypeObj.iNodeType;



        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExtension, "test.omni.graph.core");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataUiName, "Core Test: Empty");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataCategories, "internal:test");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataDescription, "Test node for omni.graph.core that does nothing and has no attributes. The version number is deliberately non-default so that testing can verify it. It also puts the icon in a non-standard location to test that feature.");
        iNodeType->setMetadata(nodeTypeObj, kOgnMetadataExclusions, "tests,usd,python,docs");
        auto iTokens = carb::getCachedInterface<carb::tokens::ITokens>();
        if( ! iTokens ) {
            CARB_LOG_ERROR("Extension path not available - ITokens not found when initializing test.omni.graph.core.Empty");
        }
        else
        {
            std::string iconPath = carb::tokens::resolveString(iTokens, "${test.omni.graph.core}");
            iconPath.append("/");
            iconPath.append("ogn/icons/test.omni.graph.core.Empty.svg");
            iNodeType->setMetadata(nodeTypeObj, kOgnMetadataIconPath, iconPath.c_str());
        }
        // LCOV_EXCL_STOP
    }
    std::vector<ogn::DynamicInput> const& getDynamicInputs() const
    {
        return m_dynamicInputs;  // LCOV_EXCL_LINE
    }
    gsl::span<ogn::DynamicOutput> getDynamicOutputs()
    {
        return m_dynamicOutputs;  // LCOV_EXCL_LINE
    }
    gsl::span<ogn::DynamicState> getDynamicStates()
    {
        return m_dynamicStates;  // LCOV_EXCL_LINE
    }
    static void release(const NodeObj& nodeObj, GraphInstanceID instanceID)
    {
        sm_stateManagerOgnCoreTestEmpty.removeState(nodeObj.nodeHandle, instanceID);
    }
    bool validate() const {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        return validateNode()
        ;
        // LCOV_EXCL_STOP
    }
    void preCompute() {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        if(m_canCachePointers == false) {
            return;
        }
        for(NameToken const& attrib : m_mappedAttributes) {
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
        // LCOV_EXCL_STOP
    }
    bool canVectorize() const {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
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
        // LCOV_EXCL_STOP
    }
    void onTypeResolutionChanged(AttributeObj const& attr) {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
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
        // LCOV_EXCL_STOP
    }
    void onDynamicAttributesChanged(AttributeObj const& attribute, bool isAttributeCreated) {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        onDynamicAttributeCreatedOrRemoved(m_dynamicInputs, m_dynamicOutputs, m_dynamicStates, attribute, isAttributeCreated);
        // LCOV_EXCL_STOP
    }
    void onDataLocationChanged(AttributeObj const& attr) {
        // LCOV_EXCL_START : internal:test nodes are excluded from coverage
        if (! attr.isValid()) return;
        updateMappedAttributes(m_mappedAttributes, attr);
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
        // LCOV_EXCL_STOP
    }
};
ogn::StateManager OgnCoreTestEmptyDatabase::sm_stateManagerOgnCoreTestEmpty;
std::tuple<int, int, int> OgnCoreTestEmptyDatabase::sm_generatorVersionOgnCoreTestEmpty{std::make_tuple(1,79,2)};
std::tuple<int, int, int> OgnCoreTestEmptyDatabase::sm_targetVersionOgnCoreTestEmpty{std::make_tuple(2,184,5)};
}
using namespace IOgnCoreTestEmpty;
#define REGISTER_OGN_NODE() \
namespace { \
    ogn::NodeTypeBootstrapImpl<OgnCoreTestEmpty, OgnCoreTestEmptyDatabase> s_registration("test.omni.graph.core.Empty", 7, "test.omni.graph.core"); \
}
