// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include <carb/Interface.h>

#include <omni/graph/core/Enums.h>
#include <omni/graph/core/Handle.h>
#include <omni/graph/core/ISchedulingHints2.h>
#include <omni/graph/core/unstable/INodeTypeCustomInterfaceBase.h>

#include <vector>

namespace omni
{
namespace graph
{
namespace core
{
namespace ogn
{
class OmniGraphDatabase;
}

// ======================================================================
/** Each node type in a plugin must implement this interface */
struct INodeType
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::INodeType", 1, 19);

    /**
     * Return node type name - this is used by 'node:type' schema in Node prim.
     * For retrieving the node type name of a known NodeTypeObj use getTypeName().
     *
     * @return The node type name
     */
    const char*(CARB_ABI* getNodeType)();

    /**
     * Implementation of compute, see above GraphContext for functions to pull/push data with other nodes
     *
     * @param[in] context structure containing both the interface and underlying object
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @return true if compute is successful, false otherwise
     */
    bool(CARB_ABI* compute)(const GraphContextObj& context, const NodeObj& node);

    // functions below are optional

    /**
     * Called by the framework to give a chance to each node instance to define custom data
     * Single node instance version: Prefer the batch call 'initializeNodes' if possible
     * (one or the other will be called, not both)
     *
     * @param[in] context structure containing both the interface and underlying object
     * @param[in] node Reference to the NodeObj struct representing the node object pointer
     */
    void(CARB_ABI* initialize)(const GraphContextObj& context, const NodeObj& node);

    /**
     * Release memory created by initialize function above
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * pointer
     */
    void(CARB_ABI* release)(const NodeObj& node);

    /**
     * This allows each node to be upgraded/downgraded for each node instance
     *
     * @param[in] context structure containing both the interface and underlying object
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] oldVersion int specifying the old version (of the node)
     * @param[in] newVersion int specifying the new version (of the node type)
     * @return true if the node was modified, false otherwise
     */
    bool(CARB_ABI* updateNodeVersion)(const GraphContextObj& context, const NodeObj& node, int oldVersion, int newVersion);

    /**
     * This allows each node type to specify its inputs and outputs in order to build up a description
     * of the node type. This is done by calling the provided implementations of addInput and addOuput to
     * add the requisite inputs and outputs respectively.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     */
    void(CARB_ABI* initializeType)(const NodeTypeObj& nodeType);

    /**
     * Adds an input for the node type. This is intended to be called from initializeType when specifying
     * the inputs for the node type.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @param[in] name Name of the input
     * @param[in] typeName Typename of the input
     * @param[in] required Whether or not the input is required
     * @param[in] defaultValuePtr Pointer to the location containing the default value of the input
     * @param[in] defaultElemCountPtr Number of elements in the default value -- nullptr if the input is a scalar
     */
    void(CARB_ABI* addInput)(const NodeTypeObj& nodeType,
                             const char* name,
                             const char* typeName,
                             bool required,
                             const void* defaultValuePtr,
                             const size_t* defaultElemCountPtr);

    /**
     * Adds an output for the node type.  This is intended to be called from initializeType when specifying
     * the outputs for the node type.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @param[in] name Name of the output
     * @param[in] typeName Typename of the output
     * @param[in] required Whether or not the output is required
     * @param[in] defaultValuePtr Pointer to the location containing the default value of the output
     * @param[in] defaultElemCountPtr Number of elements in the default value -- nullptr if the output is a scalar
     */
    void(CARB_ABI* addOutput)(const NodeTypeObj& nodeType,
                              const char* name,
                              const char* typeName,
                              bool required,
                              const void* defaultValuePtr,
                              const size_t* defaultElemCountPtr);

    /**
     * Adds a state attribute for the node type. This is intended to be called from initializeType when specifying
     * the state information for the node type. State attributes differ from inputs and outputs in that they will
     * never leave the node (i.e. they cannot be connected). The node is responsible for ensuring that their contents
     * are consistent with the current evaluation.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @param[in] name Name of the input
     * @param[in] typeName Typename of the input
     * @param[in] required Whether or not the input is required
     * @param[in] defaultValuePtr Pointer to the location containing the default value of the input
     * @param[in] defaultElemCountPtr Number of elements in the default value -- nullptr if the input is a scalar
     */
    void(CARB_ABI* addState)(const NodeTypeObj& nodeType,
                             const char* name,
                             const char* typeName,
                             bool required,
                             const void* defaultValuePtr,
                             const size_t* defaultElemCountPtr);


    /**
     * Adds an extended input (not one of the usual data types) for the node type, for example, a union type.
     * This is intended to be called from initializeType when specifying the inputs for the node type.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @param[in] name Name of the input
     * @param[in] typeInfo A buffer holding extra information about the type
     * @param[in] required Whether or not the input is required
     * @param[in] extendedAttrType Whether the attribute is an extended type, like a union or any
     */
    void(CARB_ABI* addExtendedInput)(const NodeTypeObj& nodeType,
                                     const char* name,
                                     const char* typeInfo,
                                     bool required,
                                     ExtendedAttributeType extendedAttrType);

    /**
     * Adds an extended output (not one of the usual data types) for the node type, for example, a union type.
     * This is intended to be called from initializeType when specifying the inputs for the node type.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @param[in] name Name of the input
     * @param[in] typeInfo A buffer holding extra information about the type
     * @param[in] required Whether or not the input is required
     * @param[in] extendedAttrType Whether the attribute is an extended type, like a union or any
     */
    void(CARB_ABI* addExtendedOutput)(const NodeTypeObj& nodeType,
                                      const char* name,
                                      const char* typeInfo,
                                      bool required,
                                      ExtendedAttributeType extendedAttrType);

    /**
     * Adds an extended state (not one of the usual data types) for the node type, for example, a union type.
     * This is intended to be called from initializeType when specifying the inputs for the node type.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @param[in] name Name of the input
     * @param[in] typeInfo A buffer holding extra information about the type
     * @param[in] required Whether or not the input is required
     * @param[in] extendedAttrType Whether the attribute is an extended type, like a union or any
     */
    void(CARB_ABI* addExtendedState)(const NodeTypeObj& nodeType,
                                     const char* name,
                                     const char* typeInfo,
                                     bool required,
                                     ExtendedAttributeType extendedAttrType);


    /**
     * Return whether state information exists on the node. This is mainly used for determining how nodes can be
     * safely scheduled for execution.
     *
     * Internal state information is data maintained on the node that is unique to the node's evaluation instance.
     * As this is somewhat equivalent to member data it cannot be accessed in parallel on the same node. For example,
     * a node with internal state data cannot be scheduled as part of a parallel graph loop.
     *
     * @return True if this node type manages its own internal state information
     */
    bool(CARB_ABI* hasState)(const NodeTypeObj& nodeType);

    /**
     * Sets a flag that indications state information exists on the node. This is mainly used for determining how
     * nodes can be safely scheduled for execution.
     *
     * @param[in] nodeHasState New value for the flag indicating if the node has state information
     */
    void(CARB_ABI* setHasState)(const NodeTypeObj& nodeType, bool nodeHasState);

    /**
     * Returns the path to this node type object, so that nodes could be created under this path in the case
     * of compound nodes
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @return path to the nodeTypeObj
     */
    const char*(CARB_ABI* getPath)(const NodeTypeObj& nodeType);

    /**
     * Registers task functions that the node intends to schedule via Realm. This is called once for each node type
     * during the lifetime of the process after the Realm runtime has been initialized.
     *
     */
    void(CARB_ABI* registerTasks)();

    /**
     * Returns the set of all metadata on this node.
     *
     * The keyBuf and valueBuf arrays preallocated by the caller, and contain at least "getMetadataCount()"
     * entries in them.
     * All returned strings are owned by the node type and not to be destroyed.
     * The returned keyBuf and valueBuf must have exactly the same size with corresponding index values; that is
     * keyBuf[i] is the metadata name for the string in valueBuf[i].
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the current node type object
     * @param[out] keyBuf Buffer in which to put the list of metadata keys
     * @param[out] valueBuf Buffer in which to put the list of metadata values
     * @param[in] bufferSize the number of strings each of the two buffers is able to hold
     * @return Number of metadata items successfully populated
     */
    size_t(CARB_ABI* getAllMetadata)(const NodeTypeObj& nodeType,
                                     const char** keyBuf,
                                     const char** valueBuf,
                                     size_t bufferSize);

    /**
     * Retrieves a metadata value from this node type
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the current node type object
     * @param[in] key The name of the metadata to be retrieved
     * @return The value of the metadata, or nullptr if the named metadata was not set on this node type
     */
    const char*(CARB_ABI* getMetadata)(const NodeTypeObj& nodeType, const char* key);

    /**
     * Returns the number of metadata entries on this node
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the current node type object
     * @return the number of metadata key/value pairs on this node
     */
    size_t(CARB_ABI* getMetadataCount)(const NodeTypeObj& nodeType);

    /**
     * Sets a metadata value on this node type.
     *
     * Certain metadata keywords have special meaning internally:
     *     _extension_: The name of the extension from which the node type was loaded
     *     uiName: The name of the node type in a longer, human-readable format
     *
     * Note: The main way for metadata to be set is through the .ogn format files. If you call this directly the
     *       metadata will not persist across sessions. If you wish to define metadata outside of the .ogn file
     *       the best method is to override the initializeType() method in your node definition and set it there.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the current node type object
     * @param[in] key The keyword, used as the name of the metadata
     * @param[in] value The value of the metadata. Metadata can be parsed later if non-string values are desired.
     * @return true if the keyword was successfully set
     */
    void(CARB_ABI* setMetadata)(const NodeTypeObj& nodeType, const char* key, const char* value);

    /**
     * Adds a sub-nodetype to an existing node type.  This is used for Python and Compounds, where there
     * is a global type that houses all the type information for all the nodes registered in the system.
     * Each of those specific node types is a sub-nodetype to the bigger container node type
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the current node type object
     * @param[in] subNodeTypeName Name of the sub-nodeType
     * @param[in] subNodeType Reference to the NodeTypeObj struct representing the sub-nodetype object
     */
    void(CARB_ABI* addSubNodeType)(const NodeTypeObj& nodeType,
                                   const char* subNodeTypeName,
                                   const NodeTypeObj& subNodeType);

    /**
     * Retrieves a sub-nodetype to an existing node type.  This is mainly used for Python nodes, where there is a
     * global PythonNode type that houses all the type information for all the python nodes registered in the
     * system.  Each of those specific python node types is a sub-nodetype to the bigger python node type
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the current node type object
     * @param[in] subNodeTypeName Name of the sub-nodeType
     * @return The NodeTypeObj of sub-nodetype
     */
    NodeTypeObj(CARB_ABI* getSubNodeType)(const NodeTypeObj& nodeType, const char* subNodeTypeName);

    /**
     * Creates a new nodeType, but without the interface portion.  It only contains the "handle" portion
     * of the NodeTypeObj - that is, a handle to an underlying object that can store the inputs/outputs of
     * a node type.  This is currently mainly used for Python types, where the functions are stored not in
     * INodeType struct as other types, but elsewhere.
     *
     * @param[in] the name of the new node type to be created.
     * @param[in] the version of the new node type to be created.
     * @return The NodeTypeObj created without the INodeType portion.
     */
    NodeTypeObj(CARB_ABI* createNodeType)(const char* nodeTypeName, int version);

    /**
     * retired
     */
    size_t(CARB_ABI* _retired_0)(const GraphContextObj&, const NodeObj&, void*, size_t);

    /**
     * retired
     */
    void(CARB_ABI* _retired_1)(const GraphContextObj&, const NodeObj&, void*, size_t, void*, size_t);

    /**
     * This function is called when an extended type attribute has been resolved due to a connection change.  The node
     * can then choose to call IAttribute::setResolvedType() on extended type attributes according to its
     * internal logic.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     */
    void(CARB_ABI* onConnectionTypeResolve)(const NodeObj& node);

    /**
     * Return whether this node type is a singleton (only 1 instance allowed per graph instance, and its subgraphs)
     *
     * A node type can be made to be singleton, in which case only 1 instance of that type of Node will be allowed
     * per graph.
     *
     * @return True if this node type is a singleton
     */
    bool(CARB_ABI* isSingleton)(const NodeTypeObj& nodeType);

    /**
     * Runs the inspector on the data in the given node type.
     *
     * @param[in] nodeTypeObj The node type on which the inspector runs
     * @param[in] inspector The inspector class
     * @return true if the inspection ran successfully, false if the inspection type is not supported
     */
    bool(CARB_ABI* inspect)(const NodeTypeObj& nodeTypeObj, inspect::IInspector* inspector);

    /**
     * Returns the number of subnode types on this node type.
     *
     * @param[in] nodeType Reference to node type object for which subnode types are to be found
     * @return the number of subnode types owned by this node type
     */
    size_t(CARB_ABI* getSubNodeTypeCount)(const NodeTypeObj& nodeType);

    /**
     * Returns the set of all subnode types of this node type.
     *
     * The subNodeTypeBuf array must be preallocated by the caller, and contain at least "bufferSize" entries.
     * The contents of both buffers are owned by the interface and should not be freed by the caller.
     *
     * @param[in] nodeType Reference to node type object for which subnode types are to be found
     * @param[out] subNodeTypeNameBuf Buffer in which to put the list of subnode type names
     * @param[out] subNodeTypeBuf Buffer in which to put the list of subnode type definitions
     * @param[in] bufferSize the number of strings each of the two buffers is able to hold
     * @return Number of subnode types successfully populated
     */
    size_t(CARB_ABI* getAllSubNodeTypes)(const NodeTypeObj& nodeType,
                                         const char** subNodeTypeNameBuf,
                                         NodeTypeObj* subNodeTypeBuf,
                                         size_t bufferSize);

    /**
     * Removes a sub-nodetype from an existing node type.  This is mainly used for Python nodes, where there is a
     * global PythonNode type that houses all the type information for all the python nodes registered in the
     * system.  Each of those specific python node types is a sub-nodetype to the bigger python node type. When a
     * Python module is unloaded it should be removing any sub-nodetypes it has added.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @param[in] subNodeTypeName Name of the sub-nodeType to be removed
     * @return True if the removal succeeded, false if not (most likely because the sub-nodetype did not exist)
     */
    bool(CARB_ABI* removeSubNodeType)(const NodeTypeObj& nodeType, const char* subNodeTypeName);

    /**
     * Get the currently defined scheduling hints for this node type.
     * Call the inline function unless you want to manage your own reference counts.

     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @return Scheduling hints pertaining to scheduling for this node type.
     */
    ISchedulingHints*(CARB_ABI* getSchedulingHints)(const NodeTypeObj& nodeType);

    /**
     * Get a pointer to the currently defined scheduling hints for this node type.
     * This version lets you manage your own reference counts.

     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @return Scheduling hints pertaining to scheduling for this node type.
     */
    inline omni::core::ObjectPtr<ISchedulingHints> getSchedulingHintsPtr(const NodeTypeObj& nodeType) const
    {
        return omni::core::steal(getSchedulingHints(nodeType));
    }

    /**
     * Set the scheduling hints for this node type.
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @param[in] newSchedulingHints Scheduling hints pertaining to scheduling for this node type.
     */
    void(CARB_ABI* setSchedulingHints)(const NodeTypeObj& nodeType, ISchedulingHints* newSchedulingHints);

    /**
     * Returns the name of the node type
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the node type object
     * @return The name of the node type
     */
    const char*(CARB_ABI* getTypeName)(const NodeTypeObj& nodeType);

    /**
     * Destroys a node type object, including any sub-nodetype objects attached to it.
     *
     * @param[in] The nodeType to destroy
     * @return true if the node type is destroyed, false otherwise
     */
    bool(CARB_ABI* destroyNodeType)(const NodeTypeObj& nodeType);

    /**
     * Retrieves a sub-nodetype to an existing node type by it's SdfPath. This is mainly used for compound
     * nodes where subnode types that are stored have a backing Prim on the stage.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the current node type object
     * @param[in] pathToSubNodeType Stage path to the subnode type
     * @return The NodeTypeObj of sub-nodetype
     */
    NodeTypeObj(CARB_ABI* getSubNodeTypeByPath)(const NodeTypeObj& nodeType, const char* pathToSubNodeType);

    /**
     * Determines if the node type is a compound node type. A compound node type is a node type that references
     * an OmniGraph to define the computation.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the current node type object
     * @return True if the node type is a compound node, false otherwise
     */
    bool(CARB_ABI* isCompoundNodeType)(const NodeTypeObj& nodeType);

    /**
     * Implementation of computeVectorized, see above GraphContext for functions to pull/push data with other nodes
     *
     * @param[in] context structure containing both the interface and underlying object
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] count The number of vectorized instances available for compute
     * @return true if compute is successful, false otherwise
     */
    size_t(CARB_ABI* computeVectorized)(const GraphContextObj& context, const NodeObj& node, size_t count);

    /**
     * Called whenever a graph instance is being removed form the stage.
     * This is an opportunity to release any memory allocated specifically for this instance
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] instanceID The instanceID as would be returned by INode::getGraphInstanceID
     */
    void(CARB_ABI* releaseInstance)(const NodeObj& node, GraphInstanceID instanceID);

    /**
     * Called by the framework when an OGN database previously created by the provided callback in INode::getOgnDatabase
     * needs to be destroyed
     *
     * @param[in] node Reference to the NodeObj struct representing the node object previously used to create the DB
     * @param[in] db An OGN database previously created by provided callback in INode::getOgnDatabase
     */
    void(CARB_ABI* destroyDB)(const NodeObj& node, ogn::OmniGraphDatabase* db);

    /**
     * Called by the framework in order to notify an OGN database previously created by the provided callback in
     * INode::getOgnDatabase that a type resolution event has happened on an attribute
     *
     * @param[in] attrib Reference to the AttributeObj struct representing the attribute object that just (un)resolved
     * its type
     * @param[in] db An OGN database previously created by provided callback in INode::getOgnDatabase
     */
    void(CARB_ABI* notifyTypeResolution)(AttributeObj const& attrib, ogn::OmniGraphDatabase* db);

    /**
     * Called by the framework in order to notify an OGN database that some dynamic attributes been added or removed.
     *
     * @param[in] db An OGN database previously created by provided callback in INode::getOgnDatabase
     * @param[in] attrib The attribute that is created or removed
     * @param[in] isAttributeCreated If true, the attribute is newly created, otherwise it is going to be removed
     */
    void(CARB_ABI* notifyDynamicAttributeChanged)(ogn::OmniGraphDatabase* db,
                                                  AttributeObj const& attrib,
                                                  bool isAttributeCreated);

    /**
     * Returns the ABI version against which the extension has been built
     */
    carb::Version(CARB_ABI* getCarbABIVersion)();

    /**
     * Called by the framework in order to notify an OGN database that an attribute is now stored at a different
     * location. (ie. its attribute data handle has changed)
     *
     * @param[in] db An OGN database previously created by provided callback in INode::getOgnDatabase
     * @param[in] attrib The attribute that has been relocated
     */
    void(CARB_ABI* notifyDataLocationChanged)(ogn::OmniGraphDatabase* db, AttributeObj const& attrib);

    /**
     * Called whenever a graph instance is being added to the stage.
     * This is an opportunity to allocate/init any memory specifically for this instance
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] instanceID The instanceID as would be returned by INode::getGraphInstanceID
     */
    void(CARB_ABI* initInstance)(const NodeObj& node, GraphInstanceID instanceID);

    /**
     * @brief Check to see when the node type was defined.
     * The difference is important because node types defined at runtime will not have prebuilt generated code, tests,
     * documentation, or structural definitions and require different handling for presentation to the user.
     *
     * @param[in] nodeType Reference to the NodeTypeObj struct representing the current node type object.
     * @return true if the node type was defined at runtime rather than at build time.
     */
    bool(CARB_ABI* definedAtRuntime)(const NodeTypeObj& nodeType);

    /**
     * Registers an arbitrary, user-defined ONI implementation against a specified node type. Note that all ONIs which
     * a node type wishes to implement must be derived from @ref
     * omni::graph::core::unstable::INodeTypeCustomInterfaceBase. Also note that no restrictions are placed on the type
     * or number of interfaces that node may wish to implement, e.g. if we have some ONI called IMyInterface and create
     * two different derived implementation classes called MyInterfaceImpl0 and MyInterfaceImpl1, both will be
     * registrable to the OG node. This behavior is purposefully left to be as generic as possible.
     *
     * @param[in] nodeTypeObj Reference to the NodeTypeObj struct representing the current node type object.
     * @param[in] interfacePtr A pointer to an instance of the implemented ONI.
     *
     * @thread_safety This method is not thread safe.
     */
    void(CARB_ABI* addInterfaceImpl_abi)(const NodeTypeObj& nodeTypeObj,
                                         unstable::INodeTypeCustomInterfaceBase* const interfacePtr);

    /**
     * A templated, API version of @ref omni::graph::core::INodeType::addInterfaceImpl that automatically performs the
     * necessary casting of the passed-in pointer into an omni::graph::core::unstable::INodeTypeCustomInterfaceBase*
     * before processing.
     *
     * @param[in] nodeTypeObj Reference to the NodeTypeObj struct representing the current node type object.
     * @tparam[in] interfacePtr A templated pointer to an instance of the implemented ONI.
     *
     * @thread_safety This method is not thread safe.
     */
    template <typename T>
    inline void addInterfaceImpl(const NodeTypeObj& nodeTypeObj, T* const interfacePtr) const
    {
        if (unstable::INodeTypeCustomInterfaceBase* const basePtr =
                exec::unstable::cast<unstable::INodeTypeCustomInterfaceBase>(interfacePtr))
        {
            nodeTypeObj.iNodeType->addInterfaceImpl_abi(nodeTypeObj, basePtr);
        }
        else
        {
            CARB_LOG_ERROR(
                "The passed-in interface pointer does not derive from omni::graph::core::unstable::INodeTypeCustomInterfaceBase");
        }
    }

    /**
     * Get the number of interfaces that have been registered against the given node type.
     * @param[in] nodeTypeObj Reference to the NodeTypeObj struct representing the current node type object.
     *
     * @thread_safety This method is thread safe.
     */
    const size_t(CARB_ABI* getInterfaceCount)(const NodeTypeObj& nodeTypeObj);

    /**
     * Acquire pointers to all ONIs that the current node type implements.
     *
     * @param[in] nodeTypeObj Reference to the NodeTypeObj struct representing the current node type object.
     * @param[out] interfaceRawPtrs Buffer in which to place the list of implemented interface pointers.
     * @param[out] bufferSize The number of interfaces that this node type implements.
     *
     * @thread_safety This method is thread safe.
     */
    void(CARB_ABI* getAllInterfaces_abi)(const NodeTypeObj& nodeTypeObj,
                                         unstable::INodeTypeCustomInterfaceBase** const buffer,
                                         const size_t bufferSize);

    /**
     * A templated, API version of @ref omni::graph::core::INodeType::getAllInterfaces that returns a vector of
     * automatically-cast pointers to registered implementation objects that implement the template-specified ONI.
     *
     * @param[in] nodeTypeObj Reference to the NodeTypeObj struct representing the current node type object.
     * @return A vector of pointers (cast to the templated type) to any registered objects that fulfill the requirements
     *         laid out above.
     *
     * @thread_safety This method is thread safe.
     */
    template <typename T>
    inline std::vector<T*> getAllInterfaces(const NodeTypeObj& nodeTypeObj) const
    {
        // Acquire all custom interfaces that have been registered to the current node type.
        std::vector<unstable::INodeTypeCustomInterfaceBase*> interfaceRawPtrs;
        interfaceRawPtrs.resize(nodeTypeObj.iNodeType->getInterfaceCount(nodeTypeObj));
        nodeTypeObj.iNodeType->getAllInterfaces_abi(nodeTypeObj, interfaceRawPtrs.data(), interfaceRawPtrs.size());

        // Check if the current node type implements the requested ONI.
        std::vector<T*> castedInterfaceRawPtrs;
        for (const auto interfaceRawPtr : interfaceRawPtrs)
        {
            if (T* requestedInterface = exec::unstable::cast<T>(interfaceRawPtr))
            {
                castedInterfaceRawPtrs.emplace_back(requestedInterface);
            }
        }

        return castedInterfaceRawPtrs;
    }

    /**
     * A convenience API method for returning a single automatically-cast interface pointer to some ONI implementation
     * that's been registered against the node type. Useful if the user knowns in advance that only one such
     * implementation has been registered against the node type.
     *
     * @param[in] nodeTypeObj Reference to the NodeTypeObj struct representing the current node type object.
     * @return An automatically-casted pointer to a template-specified interface if the node type implements
     * said interface and only contains one such implementation, otherwise @p nullptr.
     *
     * @thread_safety This method is thread safe.
     */
    template <typename T>
    inline T* getInterface(const NodeTypeObj& nodeTypeObj) const
    {
        std::vector<T*> vectorOfCastedInterfaceRawPtrs = getAllInterfaces<T>(nodeTypeObj);
        if (vectorOfCastedInterfaceRawPtrs.empty())
        {
            return nullptr;
        }
        else if (vectorOfCastedInterfaceRawPtrs.size() == 1)
        {
            return vectorOfCastedInterfaceRawPtrs[0];
        }
        else
        {
            CARB_LOG_WARN(
                "Ambiguity: Node type object \"%s\" contains multiple registered implementations for the requested interface; returning nullptr",
                nodeTypeObj.iNodeType->getNodeType());
            return nullptr;
        }
    }

    /*
     * @brief Computation method supported for pre and post render graph nodes.
     *
     * The method is invoked by the Execution Framework for nodes that are executed as part of
     * pre or post render graphs, as CUDA commands.
     * The computeCuda ABI is ignored by the framework and will not produce any output
     * when the nodes which implement it are executed outside of the context of
     * a pre or post render graph.
     *
     * @param[in] nodeObj Reference to the NodeObj struct representing the node object.
     * @return Returns true if the node computation is successful, otherwise returns false.
     */
    bool(CARB_ABI* computeCuda)(const NodeObj& nodeObj);
    
    /**
     * Called by the framework to give a chance to each node instance to define custom data.
     * This batch call passes in all node instances created in a given graph at once, and  if setup,
     * it will be preferred to the single instance version "initialize"
     * 
     * If not setup, "initialize" will be called once for each instance of node of this type)
     *
     * @param[in] context structure containing both the interface and underlying object
     * @param[in] nodes Pointer to a list of NodeObj structs representing all nodes of that type in the graph
     * @param[in] count The number of instances in the nodes list
     */
    void(CARB_ABI* initializeNodes)(const GraphContextObj& context, const NodeObj* nodes, size_t count);

    //////////////////////////////////////////////////////////////////////////////////////
    // REMINDER REMINDER REMINDER REMINDER REMINDER REMINDER
    //////////////////////////////////////////////////////////////////////////////////////
    // Any change made in this ABI should come with a change in either (or both of):
    // - OmniGraphNode_ABI::populateNodeTypeInterface()
    // - NodeTypeRegistration::NodeTypeRegistration()

    //////////////////////////////////////////////////////////////////////////////////////
    // WARNING WARNING WARNING WARNING WARNING WARNING WARNING
    //////////////////////////////////////////////////////////////////////////////////////
    // COMPATIBILITY CONSIDERATIONS WHEN ADDING AN ENTRY
    //
    // If the change breaks forward compatibility (most likely when adding an entry here),
    // any extensions built with this SDK that embeds node(s) will need to
    // enforce its minimum dependency version to the new omni.graph.core.
    //
    // At the time of writing, the following dependencies will need upgrade for the official omni graph extensions:
    // Property to change : [dependencies] "omni.graph.core" =  = { version = "x.y.z"} )
    //  - omni.graph.action_nodes/config/extension.toml
    //  - omni.graph.examples.cpp/config/extension.toml
    //  - omni.graph.nodes/config/extension.toml
    //  - omni.graph.rtxtest/config/extension.toml
    //  - omni.graph.test/config/extension.toml
    //  - omni.graph.tutorials/config/extension.toml
    //  - omni.graph.ui_nodes/config/extension.toml
};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(INodeType, initializeNodes, 50) // Check the reminder above

} // namespace core
} // namespace graph
} // namespace omni
