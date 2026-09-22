// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Framework.h>
#include <carb/logging/Log.h>

#include <omni/core/IObject.h>
#include <omni/core/OmniAttr.h>
#include <omni/graph/core/ogn/OmniGraphNodeABI.h>

#include <functional>
#include <string>
#include <unordered_map>
#include <vector>

// =================================================================================================================
// This file contains helpers for facilitating automatic OGN node registration/deregistration.
//
//    DECLARE_OGN_NODES()    Added to your PluginInterface.cpp declarations where a static initializer would go.
//    INITIALIZE_OGN_NODES() Added to your carbOnPluginStartup() or IExtensionHooks::onStartup_abi function.
//    RELEASE_OGN_NODES()    Added to your carbOnPluginShutdown() or IExtensionHooks::onShutdown_abi function.
//    REGISTER_OGN_NODE_INTERFACE(const char* const nodeTypeName, omni::core::ObjectPtr<CustomInterfaceImpl>)
//        Added to any .cpp in the plugin that defines the node in question (though placing
//        it with the node definition itself can be a nice way to organize everything).
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

namespace omni
{
namespace graph
{
namespace core
{
namespace ogn
{

// ==============================================================================================================
// This class has to be inlined or it would break ABI requirements. It is restricted to being instantiated and used
// within a single extension to enforce that.
class NodeTypeBootstrap
{
    const char* m_nodeTypeName{ nullptr };

public:
    explicit NodeTypeBootstrap(const char* nodeTypeName);

    virtual NodeTypeABI& getABI() = 0;

    void registerNodeType(IGraphRegistry& iGraphRegistry)
    {
        getABI().registerNodeType(iGraphRegistry);
    }
    void registerNodeType(IGraphRegistry& iGraphRegistry,
                          const std::vector<omni::core::ObjectPtr<unstable::INodeTypeCustomInterfaceBase>>& interfacePtrs)
    {
        getABI().registerNodeType(iGraphRegistry, interfacePtrs);
    }
    void deregisterNodeType(IGraphRegistry& iGraphRegistry)
    {
        getABI().deregisterNodeType(iGraphRegistry);
    }
    const char* const getNodeTypeName() const noexcept
    {
        return m_nodeTypeName;
    }
};

// ==============================================================================================================
//
// The registration/deregistration process code flow:
//
//    DECLARE_OGN_NODES() establishes a per-plugin manifest of registration records for its extension.
//    REGISTER_OGN_NODE(), added for each node type implementation, adds that node type's information to the manifest.
//    REGISTER_OGN_NODE_INTERFACE(const char* const nodeTypeName, omni::core::ObjectPtr<CustomInterfaceImpl>)
//        stores a generic, user-defined (and implemented) ONI object for the given node type name in the manifest.
//        Note that this macro assumes that the interface implementation has a static constructor of the form
//        `omni::core::ObjectPtr<CustomInterfaceImpl> create(void)`. For more generic interface registration, check
//        the INodeType::addInterface ABI method.
//    INITIALIZE_OGN_NODES() walks every node type in the manifest and registers it with OmniGraph. This step will also
//        process all ONI objects that were linked to specific node type names.
//    RELEASE_OGN_NODES() walks every node type in the manifest and deregisters it with OmniGraph.
//
// The code is set up to allow multiple calls to INITIALIZE_OGN_NODES()/RELEASE_OGN_NODES() within a plugin, however
// the typical case will only do those on startup and shutdown.
//
// ==============================================================================================================

// ==============================================================================================================
// This class has to be inlined or it would break ABI requirements. It is restricted to being instantiated and used
// within a single extension to enforce that.
template <typename NodeTypeClass, typename NodeTypeDataClass>
class NodeTypeBootstrapImpl : public NodeTypeBootstrap
{
    OmniGraphNode_ABI<NodeTypeClass, NodeTypeDataClass> m_nodeTypeABI;

public:
    NodeTypeBootstrapImpl(const char* nodeTypeName, int version, const char* extensionName)
        : NodeTypeBootstrap(nodeTypeName), m_nodeTypeABI(nodeTypeName, version, extensionName)
    {
    }

    NodeTypeABI& getABI()
    {
        return m_nodeTypeABI;
    }
};

// ==============================================================================================================
class NodeTypeManifest
{
    std::vector<NodeTypeBootstrap*> m_registrationList; //< List of node type information used for (de)registration.

    // A container of pointers to custom interface implementations that need to be registered against specific
    // node types (i.e., those node types are implementing some customized interfaces).
    std::unordered_map<std::string, std::vector<omni::core::ObjectPtr<unstable::INodeTypeCustomInterfaceBase>>>
        m_nodeTypeToInterfacePtrs;

    // Returns the interface to the registry, potentially using a supplied one (usually from omni.graph.core where
    // the usual method of getting a cached interface is not available)
    IGraphRegistry* getRegistryInterface(IGraphRegistry* potentialInterface, char const* processUsingIt) const
    {
        if (potentialInterface)
        {
            return potentialInterface;
        }
        auto iGraphRegistry = carb::getCachedInterface<omni::graph::core::IGraphRegistry>();
        if (iGraphRegistry)
        {
            return iGraphRegistry;
        }
        // No interface is okay when there is no registration list
        if (m_registrationList.empty())
        {
            return iGraphRegistry;
        }

        // This used to be an error, but it seems to get called on shutdown for some reason, where acquisition of
        // the registry interface is not possible, so log a message for history but do not fail, relying on the
        // caller to check for a nullptr return.
        CARB_LOG_INFO_ONCE("Failed to %s - could not acquire omni::graph::core::IGraphRegistry", processUsingIt);
        return nullptr;
    }


public:
    // Add a new node type record to the manifest. Should happen as a result of the REGISTER_OGN_NODE() macro.
    void addNodeTypeRecord(NodeTypeBootstrap* newRecord)
    {
        m_registrationList.push_back(newRecord);
    }

    // Add a new interface implementation for a specified node type name.
    void addInterface(const char* const nodeTypeName, unstable::INodeTypeCustomInterfaceBase* const interfaceRawPtr)
    {
        m_nodeTypeToInterfacePtrs.try_emplace(
            nodeTypeName, std::vector<omni::core::ObjectPtr<unstable::INodeTypeCustomInterfaceBase>>());

        // Note that the manifest will keep at least one reference to the interface implementation that's separate
        // from any references held by the corresponding NodeTypeDef; this should allow node type deregistrations
        // + re-registrations via the INITIALIZE_OGN_NODES and RELEASE_OGN_NODES to work correctly (in terms of
        // populating the NodeTypeDef with the necessary interface implementations) if those macros are invoked
        // multiple times from within a plugin.
        m_nodeTypeToInterfacePtrs.at(nodeTypeName).emplace_back(omni::core::steal(interfaceRawPtr));
    }

    void registerAll(IGraphRegistry* iGraphRegistry = nullptr)
    {
        iGraphRegistry = getRegistryInterface(iGraphRegistry, "register node types");
        if (iGraphRegistry)
        {
            for (const auto& registration : m_registrationList)
            {
                if (registration)
                {
                    if (m_nodeTypeToInterfacePtrs.find(registration->getNodeTypeName()) == m_nodeTypeToInterfacePtrs.end())
                    {
                        registration->registerNodeType(*iGraphRegistry);
                    }
                    else
                    {
                        registration->registerNodeType(
                            *iGraphRegistry, m_nodeTypeToInterfacePtrs.at(registration->getNodeTypeName()));
                    }
                }
                else
                {
                    CARB_LOG_ERROR_ONCE("Empty registration entry found when registering all node types");
                }
            }
        }
    }

    void deregisterAll(IGraphRegistry* iGraphRegistry = nullptr)
    {
        iGraphRegistry = getRegistryInterface(iGraphRegistry, "register node types");
        if (iGraphRegistry)
        {
            for (const auto& registration : m_registrationList)
            {
                if (registration)
                {
                    registration->deregisterNodeType(*iGraphRegistry);
                }
                else
                {
                    CARB_LOG_ERROR_ONCE("Empty registration entry found when deregistering all node types");
                }
            }
        }
    }
};


} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni

// ======================================================================
/**
 * In order to support delayed registration per-plugin each plugin must contain a list of
 * registration functions to be called on startup. To that end the first macro is instantiated
 * in the plugin interface file at the file-static level and the second is instantiated
 * inside the carbOnPluginStartup function. No instantiation is needed in the carbOnPluginShutdown
 * function as the registration object will take care of cleanup. The access is made through
 * a function call with a static member to prevent static initialization ordering problems.
 */
extern omni::graph::core::ogn::NodeTypeManifest& __nodeTypeManifest();

// This has to be separate from the class declaration since it would otherwise create a circular dependency between
// NodeTypeManifest and NodeTypeBootstrap
inline omni::graph::core::ogn::NodeTypeBootstrap::NodeTypeBootstrap(const char* nodeTypeName)
    : m_nodeTypeName(nodeTypeName)
{
    __nodeTypeManifest().addNodeTypeRecord(this);
}

// This is included in the plugin definition file in the file-static declaration code block
#define DECLARE_OGN_NODES()                                                                                            \
    omni::graph::core::ogn::NodeTypeManifest& __nodeTypeManifest()                                                     \
    {                                                                                                                  \
        static omni::graph::core::ogn::NodeTypeManifest _nodeTypeManifest;                                             \
        return _nodeTypeManifest;                                                                                      \
    }

// This is added to the plugin startup to register all (C++) node types owned by the plugin
#define INITIALIZE_OGN_NODES() __nodeTypeManifest().registerAll();

// This should be added to the plugin shutdown to ensure that all node types owned by the plugin are cleanly shut down
#define RELEASE_OGN_NODES() __nodeTypeManifest().deregisterAll();

#define OMNI_GRAPH_CORE_OGN_CONCAT_(a_, b_) a_##b_
#define OMNI_GRAPH_CORE_OGN_CONCAT(a_, b_) OMNI_GRAPH_CORE_OGN_CONCAT_(a_, b_)
#define REGISTER_OGN_NODE_INTERFACE_(var_, class_, nodeTypeName, ...)                                                    \
    static auto var_ = [](omni::graph::core::ogn::NodeTypeManifest& nodeTypeManifest) -> int                             \
    {                                                                                                                    \
        if (omni::graph::core::unstable::INodeTypeCustomInterfaceBase* const basePtr =                                   \
                omni::graph::exec::unstable::cast<omni::graph::core::unstable::INodeTypeCustomInterfaceBase>(            \
                    new class_(nodeTypeName, ##__VA_ARGS__)))                                                            \
        {                                                                                                                \
            nodeTypeManifest.addInterface(nodeTypeName, basePtr);                                                        \
        }                                                                                                                \
        else                                                                                                             \
        {                                                                                                                \
            CARB_LOG_ERROR(                                                                                              \
                "Class \"%s\" does not derive from omni::graph::core::unstable::INodeTypeCustomInterfaceBase", #class_); \
        }                                                                                                                \
        return 0;                                                                                                        \
    }(__nodeTypeManifest());
#define REGISTER_OGN_NODE_INTERFACE(class_, nodeTypeName, ...)                                                           \
    REGISTER_OGN_NODE_INTERFACE_(OMNI_GRAPH_CORE_OGN_CONCAT(sInterface, __LINE__), class_, nodeTypeName, ##__VA_ARGS__)


// ==============================================================================================================
/* Everything below here was used on previous versions of generated code and should no longer be accessed. They only
   continue to exist here on the off chance that somebody was using them directly.
  _____   ______  _____   _____   ______  _____         _______  ______  _____
 |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
 | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
 | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
 | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
 |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/
*/
namespace omni
{
namespace graph
{
namespace core
{
namespace ogn
{

// ======================================================================
// Define the type used for remembering the function to call for a delayed registration of a node type
using DelayedRegistrationFn =
    std::function<const char*(OmniGraphNodeRegisterFn&, OmniGraphNodeDeregisterFn&, OmniGraphNodeRegisterAliasFn&)>;
using DelayRegistrationFn = std::function<void(DelayedRegistrationFn)>;

// ======================================================================
/**
 * Template for a class that manages registration of a node defined outside the omni.graph.core extension
 * The OmniGraph interface is assumed to be available as any extension registering nodes must have a dependency on it.
 * One of these objects must be statically instantiated for the node type registration to be properly managed.
 */
template <typename NodeTypeClass, typename NodeTypeDataClass>
class RegisterNode : OmniGraphNode_ABI<NodeTypeClass, NodeTypeDataClass>
{
public:
    /**
     * Construct a registration object and register it for delayed registration when the plugin starts up
     *
     * @param[in] nodeTypeName Name of the node type being registered
     * @param[in] nodeTypeVersion Version of the node type being registered
     * @param[in] extensionName Name of the extension owning this node type
     * @param[in] delayRegistration Function to call to queue up a delayed registration in the plugin start-up code
     */
    RegisterNode<NodeTypeClass, NodeTypeDataClass>(const char* nodeTypeName,
                                                   int nodeTypeVersion,
                                                   const char* extensionName,
                                                   DelayRegistrationFn delayRegistration)
        : OmniGraphNode_ABI<NodeTypeClass, NodeTypeDataClass>()
    {
        // std::cout << "DBG: Delayed registration of " << nodeTypeName << " from " << extensionName << std::endl;
        using std::placeholders::_1;
        using std::placeholders::_2;
        using std::placeholders::_3;
        delayRegistration(std::bind(&RegisterNode<NodeTypeClass, NodeTypeDataClass>::performRegistration, this,
                                    nodeTypeName, nodeTypeVersion, extensionName, _1, _2, _3));
    }

    /**
     * A binding of this function for every node type is added to a delayed registration list, which will be processed
     * when the plugin starts up.
     *
     * @param[in] nodeTypeName Name of the node type being registered
     * @param[in] nodeTypeVersion Version of the node type being registered
     * @param[in] extensionName Name of the extension owning this node type
     * @param[in] registerFn Function to call to register the node type with the OmniGraph
     * @param[in] deregisterFn Function to call to deregister the node type with the OmniGraph
     * @param[in] registerAliasFn Function to call to register an alternate name for the node type
     * @return The name of the node type as registered
     */
    const char* performRegistration(const char* nodeTypeName,
                                    int nodeTypeVersion,
                                    const char* extensionName,
                                    OmniGraphNodeRegisterFn& registerFn,
                                    OmniGraphNodeDeregisterFn& deregisterFn,
                                    OmniGraphNodeRegisterAliasFn& registerAliasFn)
    {
        // std::cout << "--- Registered " << nodeTypeName << " from " << extensionName << std::endl;
        OmniGraphNode_ABI<NodeTypeClass, NodeTypeDataClass>::doRegister(
            nodeTypeName, nodeTypeVersion, extensionName, registerFn, deregisterFn, registerAliasFn);
        return nodeTypeName;
    }
};

} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
