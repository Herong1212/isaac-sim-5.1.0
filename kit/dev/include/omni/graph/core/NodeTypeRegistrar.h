// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "iComputeGraph.h"

#include <type_traits>

//====================================================================================================
//
// Node type registration is handled through this set of classes. The implementation is geared towards simplifying
// the registration process as much as possible. All of this is support code for the macro "REGISTER_OGN_NODE()",
// which you place at the bottom of your .ogn file.
//
//====================================================================================================

namespace omni
{
namespace graph
{
namespace core
{
// If a node type version is not specified then it gets this value.
// Keep in sync with DEFAULT_NODE_TYPE_VERSION_DEFAULT in omni.graph.core/python/tests/omnigraph_test_utils.py
static constexpr int kDefaultNodeTypeVersion = 1;

// See this file for how to handle new methods added to the iNodeType interface.
#define NODE_TYPE_REGISTRY // For inclusion protection
#include "NodeTypeRegistryTemplates.h"

// Scoped node registration helper class. Used by the NodeTypeRegistrar to pass in node methods for the
// INodeType ABI, keeping the node type registered for the lifetime of the instantiated object. Only one
// registration object can exist per node type so copy methods are deleted in favour of their move equivalents.
class NodeTypeRegistration
{
public:
    // Direct access to the interface, for the manual registration modes
    const INodeType& nodeTypeInterface() const
    {
        return m_interface;
    }

    // Direct access to the version, for the manual registration modes
    const int nodeTypeVersion() const
    {
        return m_versionNumber;
    }

    // Move constructor allows passing of registration information through return values without double
    // register/unregister
    NodeTypeRegistration(NodeTypeRegistration&& rhs) noexcept
    {
        m_interface = rhs.m_interface;
        m_versionNumber = rhs.m_versionNumber;
        rhs.m_interface = INodeType{};
        rhs.m_versionNumber = kDefaultNodeTypeVersion;
    }
    // Move operator allows passing of registration information through return values without double register/unregister
    NodeTypeRegistration& operator=(NodeTypeRegistration&& rhs) noexcept
    {
        m_interface = rhs.m_interface;
        m_versionNumber = rhs.m_versionNumber;
        rhs.m_interface = INodeType{};
        rhs.m_versionNumber = kDefaultNodeTypeVersion;
        return *this;
    }
    // Only available constructor takes in the four methods required by the INodeType API and registers
    // the node type using that interface. Only the name function is remembered for later unregistration.
    NodeTypeRegistration(GetNodeTypeFunction nameFn,
                         ComputeFunction computeFn,
                         InitializeFunction initializeFn,
                         ReleaseFunction releaseFn,
                         InitializeTypeFunction initializeTypeFn,
                         UpdateNodeVersionFunction updateNodeVersionFn,
                         AddInputFunction addInputFn,
                         AddExtendedInputFunction addExtendedInputFn,
                         AddOutputFunction addOutputFn,
                         AddExtendedOutputFunction addExtendedOutputFn,
                         AddStateFunction addStateFn,
                         AddExtendedStateFunction addExtendedStateFn,
                         HasStateFunction hasStateFn,
                         RegisterTasksFunction registerTasksFn,
                         GetAllMetadataFunction getAllMetadataFn,
                         GetMetadataFunction getMetadataFn,
                         GetMetadataCountFunction getMetadataCountFn,
                         SetMetadataFunction setMetadataFn,
                         OnConnectionTypeResolveFunction onConnectionTypeResolveFn,
                         InspectFunction inspectFn,
                         ComputeVectorizedFunction computeVectorized,
                         InitInstanceFunction initInstance,
                         ReleaseInstanceFunction releaseInstance,
                         DefinedAtRuntimeFunction definedAtRuntime,
                         ComputeCudaFunction computeCuda,
                         InitializeNodesFunction initNodes,
                         int versionNumber)
    {
        m_versionNumber = versionNumber;

        m_interface.addInput = addInputFn;
        m_interface.addExtendedInput = addExtendedInputFn;
        m_interface.addOutput = addOutputFn;
        m_interface.addExtendedOutput = addExtendedOutputFn;
        m_interface.addState = addStateFn;
        m_interface.addExtendedState = addExtendedStateFn;
        m_interface.compute = computeFn;
        m_interface.getNodeType = nameFn;
        m_interface.hasState = hasStateFn;
        m_interface.initialize = initializeFn;
        m_interface.initializeType = initializeTypeFn;
        m_interface.registerTasks = registerTasksFn;
        m_interface.getAllMetadata = getAllMetadataFn;
        m_interface.getMetadata = getMetadataFn;
        m_interface.getMetadataCount = getMetadataCountFn;
        m_interface.setMetadata = setMetadataFn;
        m_interface.release = releaseFn;
        m_interface.updateNodeVersion = updateNodeVersionFn;
        m_interface.onConnectionTypeResolve = onConnectionTypeResolveFn;
        m_interface.inspect = inspectFn;
        m_interface.computeVectorized = computeVectorized;
        m_interface.initInstance = initInstance;
        m_interface.releaseInstance = releaseInstance;
        m_interface.getCarbABIVersion = []() { return INodeType::getInterfaceDesc().version; };
        m_interface.definedAtRuntime = definedAtRuntime;
        m_interface.computeCuda = computeCuda;
        m_interface.initializeNodes = initNodes;

        // deprecated
        m_interface._retired_0 = nullptr;
        m_interface._retired_1 = nullptr;
    }

    // Node registrations must be unique
    NodeTypeRegistration() = delete;
    NodeTypeRegistration(const NodeTypeRegistration&) = delete;
    NodeTypeRegistration& operator=(const NodeTypeRegistration&) = delete;

private:
    INodeType m_interface = {}; // Interface created for this node type
    int m_versionNumber{ kDefaultNodeTypeVersion }; // Node type's registered version number
};

// Template class from which nodes can derive to automate their registration.
//
template <typename T>
class NodeTypeRegistrar
{
    static const char* s_nodeTypeName; // Name used if the node does not have a getNodeTypeName method
public:
    // Register the node type, returning a scoped registration object. Your node type will be registered and
    // available for the lifetime of the returned object.
    static NodeTypeRegistration registerNode(const char* name,
                                             int versionNumber,
                                             InitializeTypeFunction initializeTypeOverride)
    {
        s_nodeTypeName = name;
        auto nodeTypeNameGetter = getNodeTypeFunction<T>();
        if (!nodeTypeNameGetter)
        {
            nodeTypeNameGetter = &getNodeTypeName;
        }
        return std::move(NodeTypeRegistration(
            nodeTypeNameGetter, computeFunction<T>(), initializeFunction<T>(), releaseFunction<T>(),
            initializeTypeOverride ? initializeTypeOverride : initializeTypeFunction<T>(),
            updateNodeVersionFunction<T>(), addInputFunction<T>(), addExtendedInputFunction<T>(), addOutputFunction<T>(),
            addExtendedOutputFunction<T>(), addStateFunction<T>(), addExtendedStateFunction<T>(), hasStateFunction<T>(),
            registerTasksFunction<T>(), getAllMetadataFunction<T>(), getMetadataFunction<T>(),
            getMetadataCountFunction<T>(), setMetadataFunction<T>(), onConnectionTypeResolveFunction<T>(),
            inspectFunction<T>(), computeVectorizedFunction<T>(), initInstanceFunction<T>(),
            releaseInstanceFunction<T>(), definedAtRuntimeFunction<T>(), computeCudaFunction<T>(), initializeNodesFunction<T>(), versionNumber));
    }
    static const char* getNodeTypeName()
    {
        return s_nodeTypeName;
    }
};
// When the template instantiates the class it will also instantiate this static member
template <typename NodeType>
const char* NodeTypeRegistrar<NodeType>::s_nodeTypeName{ nullptr };

// Macro that simplifies the syntax of node registration, creating a scoped object for automatic register/unregister
// that can be accessed through the consistently named method "nodeTypeRegistrationMYNODENAME" to call its
// registerNodeType and unregisterNodeType methods at the appropriate time.
#define REGISTER_NODE_TYPE(NODE_CLASS, NODE_TYPE_NAME, NODE_TYPE_VERSION)                                              \
    const omni::graph::core::NodeTypeRegistration& nodeTypeRegistration##NODE_CLASS()                                  \
    {                                                                                                                  \
        static omni::graph::core::NodeTypeRegistration s_nodeRegistration{                                             \
            omni::graph::core::NodeTypeRegistrar<NODE_CLASS>::registerNode(NODE_TYPE_NAME, NODE_TYPE_VERSION, nullptr) \
        };                                                                                                             \
        return s_nodeRegistration;                                                                                     \
    }

}
}
}

#define REGISTER_NAMESPACED_NODE_TYPE(NODE_CLASS, NAMESPACE, NODE_TYPE_NAME, NODE_TYPE_VERSION)                        \
    const omni::graph::core::NodeTypeRegistration& nodeTypeRegistration##NODE_CLASS()                                  \
    {                                                                                                                  \
        static omni::graph::core::NodeTypeRegistration s_nodeRegistration{                                             \
            omni::graph::core::NodeTypeRegistrar<NAMESPACE ::NODE_CLASS>::registerNode(                                \
                NODE_TYPE_NAME, NODE_TYPE_VERSION, nullptr)                                                            \
        };                                                                                                             \
        return s_nodeRegistration;                                                                                     \
    }
