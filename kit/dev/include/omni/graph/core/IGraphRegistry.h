// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once
#include <carb/Interface.h>
#include <carb/events/IEvents.h>

#include <omni/graph/core/Handle.h>
#include <omni/inspect/IInspector.h>

namespace omni
{
namespace graph
{
namespace core
{

/**
 * An event that occurs on the graph registry
 */
enum class IGraphRegistryEvent
{
    //! Node type has been added to the registry. Event payloads are:
    //! "node_type" (std::string): Name of new node type
    eNodeTypeAdded,
    //! Node type has been removed from the registry. Event payloads are:
    //! "node_type" (std::string): Name of removed node type
    eNodeTypeRemoved,
    //! Node type has had its namespace changed. Event payloads are:
    //! "node_type" (std::string): New namespace
    //! "prev_type" (std::string): Previous namespace
    eNodeTypeNamespaceChanged,
    //! Node type has had its category changed. Event payloads are:
    //! "node_type" (std::string): Node type whose category changed
    //! "prev_value" (std::string): Previous category value
    eNodeTypeCategoryChanged,
    //! A stage is being attached. Event payloads are:
    //! "has_og_prims_on_stage" (bool): Is true if the stage that is being loaded contains OmniGraph nodes, otherwise is
    //! false.
    eStagePreAttach,
};

// ======================================================================
//! Interface that manages the registration and deregistration of node types
struct IGraphRegistry
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::IGraphRegistry", 1, 5);

    /**
     * Returns the number of registered node types in the graph. This includes C++ types only.
     *
     * @return The number of node type objects.
     */
    size_t(CARB_ABI* getRegisteredTypesCount)();

    /**
     * Gets the list of the registered types in the graph. This includes C++ types only.
     *
     * @param[out] typesBuf Buffer to hold the return array of node type objects
     * @param[in] bufferSize The number of NodeTypeObj structures the buffer is able to hold
     * @return true on success, false on failure.
     */
    bool(CARB_ABI* getRegisteredTypes)(NodeTypeObj* typesBuf, size_t bufferSize);

    /**
     * Gets the version of the registered node type. This includes both C++ and Python types.
     *
     * @param[in] nodeType The name of the node type in question.
     * @return The version number of the currently registered type. If the type is not found
     *         returns the default version number, which is 0.
     */
    int(CARB_ABI* getNodeTypeVersion)(const char* nodeType);

    /**
     * Registers a node type as defined above with the system
     * Deprecated. Use registerNodeTypeInterface instead.
     *
     * @param[in] desc Reference to the node type interface (the underlying object is not yet available here).
     * @param[in] version Version of the node interface to be registered.
     */
    CARB_DEPRECATED("Will be removed in next major version, use IGraphRegistry::registerNodeTypeInterface instead")
    void(CARB_ABI* registerNodeType)(const INodeType& desc, int version);

    /**
     * Unregisters a node type interface as defined above with the system.
     *
     * @param[in] nodeType Name of the node type to be unregistered.
     */
    void(CARB_ABI* unregisterNodeType)(const char* nodeType);

    /**
     * Registers an alias by which a node type can be referred to. Useful for backward compatibility in files.
     *
     * @param[in] desc Reference to the node type interface.
     * @param[in] alias Alternate name that can be used to refer to the node type when creating.
     */
    CARB_DEPRECATED("Will be removed in next major version, use INodeTypeForwarding2 instead")
    void(CARB_ABI* registerNodeTypeAlias)(const INodeType& desc, const char* alias);

    /**
     * Runs the inspector on the contents of the graph registry.
     *
     * @param[in] inspector The inspector class.
     * @return true if the inspection ran successfully, false if the inspection type is not supported.
     */
    bool(CARB_ABI* inspect)(inspect::IInspector* inspector);

    /**
     * Gets the node type information corresponding to the node type name. This includes aliases.
     *
     * @param[in] nodeTypeName the name of the node type one wishes to acquire
     * @return The node type object corresponding to the inputted name if such a node type has
     *         been registered, an empty/invalid node type object if no such name has been registered.
     */
    NodeTypeObj(CARB_ABI* getRegisteredType)(const char* nodeTypeName);

    /**
     * Returns the interface for the event stream for the changes on the graph registry.
     *
     * The events that are raised are specified by IGraphRegistryEvent.
     *
     * @return The event stream interface that pumps events.
     */
    carb::events::IEventStreamPtr(CARB_ABI* getEventStream)();

    /**
     * Registers a node type as defined above with the system
     *
     * @param[in] desc Reference to the node type interface (the underlying object is not yet available here)
     * @param[in] version Version of the node interface to be registered
     * @param[in] nodeTypeStructSize The size of the INodeType struct being passed. Use sizeof(INodeType).
     *
     */
    void(CARB_ABI* registerNodeTypeInterface)(const INodeType& desc, int version, size_t nodeTypeStructSize);
};

// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IGraphRegistry, registerNodeTypeInterface, 9)

} // namespace core
} // namespace graph
} // namespace omni
