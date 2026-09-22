// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
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
#include <carb/profiler/Profile.h>

#include <omni/graph/core/ComputeGraph.h>
#include <omni/graph/core/IGraphRegistry.h>
#include <omni/graph/core/TemplateUtils.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/ogn/Database.h>
#include <omni/graph/core/unstable/INodeTypeCustomInterfaceBase.h>
#include <omni/graph/core/unstable/INodeTypeForwarding.h>

// =================================================================================================================
// This file contains simple interface classes which wrap data in the OGN database for easier use.
//
//    OmniGraphNode_ABI  Templated base class for generated OmniGraph node type definitions
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

// Uncomment the first line to see debug output, the second to see nothing
// #define OGN_DBG
#define OGN_DBG if (false)
#include <iostream>

namespace omni
{
namespace graph
{
namespace core
{
namespace ogn
{

// ======================================================================
// Function declarations for registering and deregistering node types. Used so that a node type
// can either use the static functions available within the core or the ABI functions outside of it.
using OmniGraphNodeRegisterFn = void (*)(const omni::graph::core::INodeType&, int);
using OmniGraphNodeDeregisterFn = void (*)(const char*);
using OmniGraphNodeRegisterAliasFn = void (*)(const omni::graph::core::INodeType&, const char*);


// ======================================================================
// The has_XXX templated types are a set of metaprograms that use type dispatching in conjunction with the
// is_detected template to resolve to a std::true_type when a class contains a certain function and std::false_type
// when it does not. This allows compile time choice of two overloaded versions of each of the ABI functions from
// the call_XXX() version of them.
//
// See the description of is_detected in TemplateUtils.h for more details on how the template match occurs.
//
// The functions defined are the ones that are used as part of the interface to the OmniGraph Node C ABI.
// The formatting is consistent to make it easier to recognize and add new types:
//    Line 1. The template declaration
//    Line 2. The typename declaration, with the expected return type of the function
//    Line 3. The function name declaration
//    Lines 4+. Declarations for each of the function parameters

// clang-format off
// ----------------------------------------------------------------------------------------------------
// static void addInput(const NodeTypeObj&, const char*, const char*, bool, const void*, const size_t*)
template <class NodeTypeClass>
using has_addInput = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().addInput(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char*>(),
        std::declval<const char*>(),
        std::declval<bool>(),
        std::declval<const void*>(),
        std::declval<const size_t*>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void addOutput(const NodeTypeObj&, const char*, const char*, bool, const void*, const size_t*)
template <class NodeTypeClass>
using has_addOutput = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().addOutput(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char*>(),
        std::declval<const char*>(),
        std::declval<bool>(),
        std::declval<const void*>(),
        std::declval<const size_t*>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void addState(const NodeTypeObj&, const char*, const char*, bool, const void*, const size_t*)
template <class NodeTypeClass>
using has_addState = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().addState(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char*>(),
        std::declval<const char*>(),
        std::declval<bool>(),
        std::declval<const void*>(),
        std::declval<const size_t*>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void addExtendedInput(const NodeTypeObj&, const char*, const char*, bool, ExtendedAttributeType)
template <class NodeTypeClass>
using has_addExtendedInput = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().addExtendedInput(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char*>(),
        std::declval<const char*>(),
        std::declval<bool>(),
        std::declval<ExtendedAttributeType>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void addExtendedOutput(const NodeTypeObj&, const char*, const char*, bool, ExtendedAttributeType)
template <class NodeTypeClass>
using has_addExtendedOutput = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().addExtendedOutput(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char*>(),
        std::declval<const char*>(),
        std::declval<bool>(),
        std::declval<ExtendedAttributeType>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void addExtendedState(const NodeTypeObj&, const char*, const char*, bool, ExtendedAttributeType)
template <class NodeTypeClass>
using has_addExtendedState = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().addExtendedState(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char*>(),
        std::declval<const char*>(),
        std::declval<bool>(),
        std::declval<ExtendedAttributeType>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static bool hasState()
template <class NodeTypeClass>
using has_hasState = typename std::is_same<bool,
    decltype(std::declval<const NodeTypeClass&>().hasState(
        std::declval<const NodeTypeObj&>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void setHasState(bool)
template <class NodeTypeClass>
using has_setHasState = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().setHasState(
        std::declval<const NodeTypeObj&>(),
        std::declval<bool>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static bool compute(const GraphContextObj&, const NodeObj&)
template <class NodeTypeClass>
using has_computeABI = typename std::is_same<bool,
    decltype(std::declval<const NodeTypeClass&>().compute(
        std::declval<const GraphContextObj&>(),
        std::declval<const NodeObj&>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static bool compute(NodeTypeDataClass&, size_t)
template <class NodeTypeClass, class NodeTypeDataClass>
using has_computeOGNT = typename std::is_same<bool,
    decltype(std::declval<NodeTypeClass&>().compute(
        std::declval<NodeTypeDataClass&>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static size_t computeVectorized(const GraphContextObj&, const NodeObj&, size_t)
template <class NodeTypeClass>
using has_computeVectorizedABI = typename std::is_same<size_t,
    decltype(std::declval<const NodeTypeClass&>().computeVectorized(
        std::declval<const GraphContextObj&>(),
        std::declval<const NodeObj&>(),
        std::declval<size_t>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static size_t computeVectorized(NodeTypeDataClass&, size_t)
template <class NodeTypeClass, class NodeTypeDataClass>
using has_computeVectorizedOGNT = typename std::is_same<size_t,
    decltype(std::declval<NodeTypeClass&>().computeVectorized(
        std::declval<NodeTypeDataClass&>(),
        std::declval<size_t>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static const char* getNodeType()
template <class NodeTypeClass>
using has_getNodeType = typename std::is_same<const char*,
    decltype(std::declval<const NodeTypeClass&>().getNodeType(
        ))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static const char* getTypeName(const NodeTypeObj&)
template <class NodeTypeClass>
using has_getTypeName = typename std::is_same<const char*,
    decltype(std::declval<const NodeTypeClass&>().getTypeName(
        std::declval<const NodeTypeObj&>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void initialize(const GraphContextObj&, const NodeObj&)
template <class NodeTypeClass>
using has_initialize = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().initialize(
        std::declval<const GraphContextObj&>(),
        std::declval<const NodeObj&>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void initializeType(const NodeTypeObj&)
template <class NodeTypeClass>
using has_initializeType = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().initializeType(
        std::declval<const NodeTypeObj&>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void registerTasks()
template <class NodeTypeClass>
using has_registerTasks = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().registerTasks(
        ))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void release(const NodeObj&)
template <class NodeTypeClass>
using has_release = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().release(
        std::declval<const NodeObj&>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void initInstance(const NodeObj&, GraphInstanceID)
template <class NodeTypeClass>
using has_initInstance = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().initInstance(
        std::declval<const NodeObj&>(),
        std::declval<GraphInstanceID>()
    ))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void releaseInstance(const NodeObj&, GraphInstanceID)
template <class NodeTypeClass>
using has_releaseInstance = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().releaseInstance(
        std::declval<const NodeObj&>(),
        std::declval<GraphInstanceID>()
    ))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static bool updateNodeVersion(const GraphContextObj&, const NodeObj&, int, int)
template <class NodeTypeClass>
using has_updateNodeVersion = typename std::is_same<bool,
    decltype(std::declval<const NodeTypeClass&>().updateNodeVersion(
        std::declval<const GraphContextObj&>(),
        std::declval<const NodeObj&>(),
        std::declval<int>(),
        std::declval<int>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static size_t getAllMetadata(const NodeTypeObj&, const char**, const char**, size_t)
template <class NodeTypeClass>
using has_getAllMetadata = typename std::is_same<size_t,
    decltype(std::declval<const NodeTypeClass&>().getAllMetadata(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char**>(),
        std::declval<const char**>(),
        std::declval<size_t>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static const char* getMetadata(const NodeTypeObj&, const char*)
template <class NodeTypeClass>
using has_getMetadata = typename std::is_same<const char*,
    decltype(std::declval<const NodeTypeClass&>().getMetadata(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char*>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static size_t getMetadataCount(const NodeTypeObj&)
template <class NodeTypeClass>
using has_getMetadataCount = typename std::is_same<size_t,
    decltype(std::declval<const NodeTypeClass&>().getMetadataCount(
        std::declval<const NodeTypeObj&>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void setMetadata(const NodeTypeObj&, const char*, const char*)
template <class NodeTypeClass>
using has_setMetadata = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().setMetadata(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char*>(),
        std::declval<const char*>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void addSubNodeType(const NodeTypeObj&, const char*, const NodeTypeObj&)
template <class NodeTypeClass>
using has_addSubNodeType = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().addSubNodeType(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char*>(),
        std::declval<const NodeTypeObj&>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static NodeTypeObj getSubNodeType(const NodeTypeObj&, const char*)
template <class NodeTypeClass>
using has_getSubNodeType = typename std::is_same<NodeTypeObj,
    decltype(std::declval<const NodeTypeClass&>().getSubNodeType(
        std::declval<const NodeTypeObj&>(),
        std::declval<const char*>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static NodeTypeObj createNodeType(const char*, int)
template <class NodeTypeClass>
using has_createNodeType = typename std::is_same<NodeTypeObj,
    decltype(std::declval<const NodeTypeClass&>().createNodeType(
        std::declval<const char*>(),
        std::declval<int>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static void onConnectionTypeResolve(const NodeTypeObj&)
template <class NodeTypeClass>
using has_onConnectionTypeResolve = typename std::is_same<void,
    decltype(std::declval<const NodeTypeClass&>().onConnectionTypeResolve(
        std::declval<const NodeObj&>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static bool inspect(const NodeTypeObj&, inspect::IInspector*)
template <class NodeTypeClass>
using has_inspect = typename std::is_same<bool,
    decltype(std::declval<const NodeTypeClass&>().inspect(
        std::declval<const NodeTypeObj&>(),
        std::declval<inspect::IInspector*>()))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static bool definedAtRuntime(const NodeTypeObj&)
template <class NodeTypeClass>
using has_definedAtRuntime = typename std::is_same<bool,
    decltype(std::declval<const NodeTypeClass&>().definedAtRuntime(
        std::declval<const NodeTypeObj&>()
        ))>::value_type;

// ----------------------------------------------------------------------------------------------------
// static bool computeCuda(NodeTypeDataClass&)
template <class NodeTypeClass, class NodeTypeDataClass>
using has_computeCudaT = typename std::is_same<bool,
    decltype(std::declval<NodeTypeClass&>().computeCuda(
        std::declval<NodeTypeDataClass&>()))>::value_type;

// clang-format on


// ==============================================================================================================
/**
 * @brief Common base class for all node type implementation definitions, so that they can be in a common container
 */
class NodeTypeABI
{
protected:
    // Remembering these values allow the node type to be registered and deregistered at will
    const char* m_nodeTypeName{ nullptr }; //!< Unique name of the node type
    int m_version{ 1 }; //!< Current version of the node type
    const char* m_extensionName{ nullptr }; //!< Extension to which this node type belongs

    /**
     * @brief Construct a new NodeTypeABI object
     *
     * @param nodeTypeName Unique name of the node type
     * @param version Version number of the node type
     * @param extensionName Extension to which this node type belongs
     */
    NodeTypeABI(const char* nodeTypeName, int version, const char* extensionName)
        : m_nodeTypeName{ nodeTypeName }, m_version(version), m_extensionName(extensionName)
    {
    }

public:
    // --------------------------------------------------------------------------------------------------------------
    /**
     * @brief Populate an INodeType interface with the functions that implement this particular templated node type
     *
     * @param[out] nodeTypeInterface Interface to be populated
     */
    virtual void populateNodeTypeInterface(INodeType& nodeTypeInterface) const = 0;

    // --------------------------------------------------------------------------------------------------------------
    /**
     * @brief Register the node type encapsulated in this description.
     */
    void registerNodeType(IGraphRegistry& iGraphRegistry)
    {
        INodeType iNodeType{};
        populateNodeTypeInterface(iNodeType);

        OGN_DBG std::cout << "DBG: ABI Registration of " << (m_nodeTypeName ? m_nodeTypeName : "UNKNOWN TYPE");
        OGN_DBG std::cout << ", version " << m_version;
        OGN_DBG std::cout << " from " << (m_extensionName ? m_extensionName : "UNKNOWN EXTENSION") << std::endl;

        iGraphRegistry.registerNodeTypeInterface(iNodeType, m_version, sizeof(INodeType));

        // One potential source of node type forwarding is if the node has overridden the getNodeType() method and
        // supplied a different name than the one generated through the .ogn file. Add that one here.
        if (iNodeType.getNodeType)
        {
            const char* overriddenTypeName = iNodeType.getNodeType();
            if (strcmp(overriddenTypeName, m_nodeTypeName) != 0)
            {
                auto iNodeTypeForwarding = carb::getCachedInterface<ComputeGraph>()->getNodeTypeForwardingInterfacePtr2();
                if (iNodeTypeForwarding)
                {
                    iNodeTypeForwarding->defineForward(
                        m_nodeTypeName, m_version, overriddenTypeName, m_version, m_extensionName);
                }
            }
        }
    }

    // --------------------------------------------------------------------------------------------------------------
    /**
     * @brief Register the node type encapsulated in this description along with the user-defined interfaces that it
     * implements.
     */
    void registerNodeType(IGraphRegistry& iGraphRegistry,
                          const std::vector<omni::core::ObjectPtr<unstable::INodeTypeCustomInterfaceBase>>& interfacePtrs)
    {
        // Register the node type as usual.
        registerNodeType(iGraphRegistry);

        // Register any custom interface implementations to the node type. Note that we do not detach the interface
        // pointer from the inputted ObjectPtrs; this is because we also want the node manifest (which calls this
        // method) to keep a reference to the interface implemenation to allow for node deregistration + reregistration
        // to occur from within a plugin (other than at plugin load and unload time, respectively).
        NodeTypeObj nodeTypeObj = iGraphRegistry.getRegisteredType(m_nodeTypeName);
        for (const auto& interfacePtr : interfacePtrs)
        {
            nodeTypeObj.iNodeType->addInterfaceImpl_abi(nodeTypeObj, interfacePtr.get());
        }
    }

    // --------------------------------------------------------------------------------------------------------------
    /**
     * @brief Deregister the node type encapsulated in this description.
     */
    void deregisterNodeType(IGraphRegistry& iGraphRegistry)
    {
        OGN_DBG std::cout << "DBG: ABI Deregistration of " << (m_nodeTypeName ? m_nodeTypeName : "UNKNOWN TYPE");
        OGN_DBG std::cout << ", version " << m_version;
        OGN_DBG std::cout << " from " << (m_extensionName ? m_extensionName : "UNKNOWN EXTENSION") << std::endl;
        iGraphRegistry.unregisterNodeType(m_nodeTypeName);
    }
};

// For safe profiler macros
#define NODE_PATH (node.isValid() ? node.iNode->getPrimPath(node) : "Unknown")

// ======================================================================
/**
 * @brief ABI proxy class for OGN generated nodes. It provides implementations for all of the
 * INodeType ABI functions which will call the actual node's versions of those functions
 * if the node defines them.
 *
 * This class uses a technique called "tag dispatching", which is a compile-time switch that decides
 * which version of a method will be called. By defining overloaded methods taking either the
 * `std::true_type` or `std::false_type` type as the first parameter, the version that is called can
 * be decided at compile time by using a template that instantiates one of the two.
 *
 * In this template class the methods "X()" use tag dispatching to decide which two versions of the `call_X()`
 * method to call. The version accepting `std::true_type` is called when an override of `X()` is detected and calls
 * the override directly. The version accepting std::false_type performs the default version of `X()`.
 *
 * Each of the INode ABI functions is implemented with these three functions. Here is an annotated example
 * of how this works for a fictional ABI method X that takes a single int argument:
 *
 * @code{.cpp}
 *      // By making this a template it can change types at compile-time
 *      template <class NodeTypeClass>
 *      // std::is_same will check to see if the named type matches the return type of the declared function
 *      using has_X = typename std::is_same<void,
 *          // decltype extracts the type of the declared entity
 *          // declval gives a compile-time stand-in for the declared entity
 *          // This statement says "get the type of the value returned by a NodeTypeClass function named X"
 *          decltype(std::declval<const NodeTypeClass&>().X(
 *          // This line adds the requirement that the function X takes an integer argument
 *          std::declval<int>())
 *          // The value_type trait gets the return type of the is_same template (std::true_type/std::false_type)
 *          )>::value_type;
 *      // These are two overloads of the same method
 *      // Since the last parameters are incompatible only one can be chosen
 *      void call_X(int value, std::true_type)  {}
 *      void call_X(int value, std::false_type) {}
 *      // This is the public method called from outside the class
 *      void X(int value) {
 *          // If NodeTypeClass::X exists then is_detected<> selects the std::true_type variation
 *          // for the first argument. Subsequent arguments are passed through from this method's arguments.
 *          call_X(is_detected<has_X, NodeTypeClass>(), value);
 *      }
 * @endcode
 *
 * For a full description of the SFINAE technique in general and the tag dispatching implementation see
 * https://www.bfilipek.com/2016/02/notes-on-c-sfinae.html#tag-dispatching
 *
 * The net result of this metaprogramming is that OmniGraphNode_ABI<MyNode, MyNodeDatabase> instantiates
 * an ABI-compatible class that calls overrides in MyNode where available and the default where not. This
 * is functionally equivalent to acquiring and extracting the Node ABI interface and calling the methods
 * on it. MyNodeDatabase is automatically generated by the .ogn processor and MyNode is the class the node
 * writer provides, giving them full control over the ABI implementation if they wish, and use of the
 * default implementation and generated helper classes if not.
 *
 * @tparam NodeTypeClass Class the user has defined for implementing the custom parts of the node type interface
 * @tparam NodeTypeDataClass Generated database class for @p NodeTypeClass
 */
template <typename NodeTypeClass, typename NodeTypeDataClass>
class OmniGraphNode_ABI : public NodeTypeABI
{
    static void call_addInput(std::true_type,
                              const NodeTypeObj& nodeType,
                              const char* name,
                              const char* typeName,
                              bool required,
                              const void* defaultValuePtr,
                              const size_t* defaultElemCountPtr) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(addInput " << name << ", " << typeName << ")" << std::endl;
        NodeTypeClass::addInput(nodeType, name, typeName, required, defaultValuePtr, defaultElemCountPtr);
    }
    static void call_addInput(std::false_type,
                              const NodeTypeObj& nodeType,
                              const char* name,
                              const char* typeName,
                              bool required,
                              const void* defaultValuePtr,
                              const size_t* defaultElemCountPtr) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(addInput " << name << ", " << typeName << ")" << std::endl;
        return;
    }

    // ----------------------------------------------------------------------
    static void call_addOutput(std::true_type,
                               const NodeTypeObj& nodeType,
                               const char* name,
                               const char* typeName,
                               bool required,
                               const void* defaultValuePtr,
                               const size_t* defaultElemCountPtr) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(addOutput " << name << ", " << typeName << ")" << std::endl;
        NodeTypeClass::addOutput(nodeType, name, typeName, required, defaultValuePtr, defaultElemCountPtr);
    }
    static void call_addOutput(std::false_type,
                               const NodeTypeObj& nodeType,
                               const char* name,
                               const char* typeName,
                               bool required,
                               const void* defaultValuePtr,
                               const size_t* defaultElemCountPtr) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(addOutput " << name << ", " << typeName << ")" << std::endl;
        return;
    }

    // ----------------------------------------------------------------------
    static void call_addState(std::true_type,
                              const NodeTypeObj& nodeType,
                              const char* name,
                              const char* typeName,
                              bool required,
                              const void* defaultValuePtr,
                              const size_t* defaultElemCountPtr) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(addState " << name << ", " << typeName << ")" << std::endl;
        NodeTypeClass::addState(nodeType, name, typeName, required, defaultValuePtr, defaultElemCountPtr);
    }
    static void call_addState(std::false_type,
                              const NodeTypeObj& nodeType,
                              const char* name,
                              const char* typeName,
                              bool required,
                              const void* defaultValuePtr,
                              const size_t* defaultElemCountPtr) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(addState " << name << ", " << typeName << ")" << std::endl;
        return;
    }

    // ----------------------------------------------------------------------
    static void call_addExtendedInput(std::true_type,
                                      const NodeTypeObj& nodeType,
                                      const char* name,
                                      const char* typeName,
                                      bool required,
                                      ExtendedAttributeType extendedType) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(addExtendedInput " << name << ", " << typeName << ")" << std::endl;
        NodeTypeClass::addExtendedInput(nodeType, name, typeName, required, extendedType);
    }
    static void call_addExtendedInput(std::false_type,
                                      const NodeTypeObj& nodeType,
                                      const char* name,
                                      const char* typeName,
                                      bool required,
                                      ExtendedAttributeType extendedType) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(addExtendedInput " << name << ", " << typeName << ")" << std::endl;
        return;
    }

    // ----------------------------------------------------------------------
    static void call_addExtendedOutput(std::true_type,
                                       const NodeTypeObj& nodeType,
                                       const char* name,
                                       const char* typeName,
                                       bool required,
                                       ExtendedAttributeType extendedType) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(addExtendedOutput " << name << ", " << typeName << ")" << std::endl;
        NodeTypeClass::addExtendedOutput(nodeType, name, typeName, required, extendedType);
    }
    static void call_addExtendedOutput(std::false_type,
                                       const NodeTypeObj& nodeType,
                                       const char* name,
                                       const char* typeName,
                                       bool required,
                                       ExtendedAttributeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(addExtendedOutput " << name << ", " << typeName << ")" << std::endl;
        return;
    }

    // ----------------------------------------------------------------------
    static void call_addExtendedState(std::true_type,
                                      const NodeTypeObj& nodeType,
                                      const char* name,
                                      const char* typeName,
                                      bool required,
                                      ExtendedAttributeType extendedType) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(addExtendedState " << name << ", " << typeName << ")" << std::endl;
        NodeTypeClass::addExtendedState(nodeType, name, typeName, required, extendedType);
    }
    static void call_addExtendedState(std::false_type,
                                      const NodeTypeObj& nodeType,
                                      const char* name,
                                      const char* typeName,
                                      bool required,
                                      ExtendedAttributeType extendedType) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(addExtendedState " << name << ", " << typeName << ")" << std::endl;
        return;
    }

    // ----------------------------------------------------------------------
    static bool call_hasState(std::true_type, const NodeTypeObj& nodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(hasState)" << std::endl;
        return NodeTypeClass::hasState(nodeType);
    }
    static bool call_hasState(std::false_type, const NodeTypeObj&) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(hasState)" << std::endl;
        return false;
    }

    // ----------------------------------------------------------------------
    static void call_setHasState(std::true_type, const NodeTypeObj& nodeType, bool hasState) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(setHasState)" << std::endl;
        NodeTypeClass::setHasState(nodeType, hasState);
    }
    static void call_setHasState(std::false_type, const NodeTypeObj&, bool) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(setHasState)" << std::endl;
    }

    // ----------------------------------------------------------------------
    template <typename FUNC>
    static bool call_computeCommonOGN(const GraphContextObj& context,
                                      const NodeObj& node,
                                      FUNC const& compute,
                                      size_t batchCount)
    {
        auto create = [](GraphContextObj const* contexts, NodeObj const* nodes, size_t count) -> ogn::OmniGraphDatabase*
        { return new NodeTypeDataClass(contexts, nodes, count); };

        NodeTypeDataClass* nodeDataPtr = reinterpret_cast<NodeTypeDataClass*>(
            node.iNode && node.iNode->getOgnDatabase ? node.iNode->getOgnDatabase(node, create) : nullptr);
        if (nodeDataPtr == nullptr || nodeDataPtr->validate() == false)
            return false;

        // Warn the node we're about to compute
        if (node.iNode->increaseComputeCount)
            node.iNode->increaseComputeCount(node, batchCount);

        // Call compute
        nodeDataPtr->preCompute();
        bool result = compute(*nodeDataPtr);

        return result;
    }

    // ----------------------------------------------------------------------
    template <typename T>
    using has_computeOGN = has_computeOGNT<T, NodeTypeDataClass>;

    template <typename T>
    using has_computeVectorizedOGN = has_computeVectorizedOGNT<T, NodeTypeDataClass>;

    template <typename T>
    using has_computeCuda = has_computeCudaT<T, NodeTypeDataClass>;

    using regOGN = is_detected<has_computeOGN, NodeTypeClass>;
    using regABI = is_detected<has_computeABI, NodeTypeClass>;
    using vecOGN = is_detected<has_computeVectorizedOGN, NodeTypeClass>;
    using vecABI = is_detected<has_computeVectorizedABI, NodeTypeClass>;

    using cudaABI = is_detected<has_computeCuda, NodeTypeClass>;

    // Nodes must have a valid compute method implemented.
    // Standard nodes need either a compute, or computeVectorized method - not both.
    // Pre or Post render graph nodes may implement
    // a standard compute / computeVectorized method, or computeCuda, or both.
    static_assert((!((regOGN() || regABI()) && (vecOGN() || vecABI()))
                    && (regOGN() || regABI() || vecOGN() || vecABI() || cudaABI())),
                  "Implements 'compute' or 'computeVectorized' (but not both)."
                  "Pre and Post render graph nodes may also implement computeCuda.");

    //===============
    template <typename UNUSED1, typename UNUSED2, typename UNUSED3>
    // regOGN, regABI, vecOGN, vecABI
    static bool call_compute(
        std::true_type, UNUSED1, UNUSED2, UNUSED3, const GraphContextObj& context, const NodeObj& node) noexcept
    {
        CARB_PROFILE_ZONE(carb::profiler::kCaptureMaskDefault, "[Compute][OGN] %s", NODE_PATH);
        return call_computeCommonOGN(context, node, NodeTypeClass::compute, 1);
    }
    //===============
    template <typename UNUSED1, typename UNUSED2>
    // regOGN, regABI, vecOGN, vecABI
    static bool call_compute(
        std::false_type, std::true_type, UNUSED1, UNUSED2, const GraphContextObj& context, const NodeObj& node) noexcept
    {
        CARB_PROFILE_ZONE(carb::profiler::kCaptureMaskDefault, "[Compute][ABI] %s", NODE_PATH);
        if (node.iNode->increaseComputeCount)
            node.iNode->increaseComputeCount(node, 1);
        return NodeTypeClass::compute(context, node);
    }

    //===============
    template <typename UNUSED1>
    // regOGN, regABI, vecOGN, vecABI
    static bool call_compute(std::false_type,
                             std::false_type,
                             std::true_type,
                             UNUSED1,
                             const GraphContextObj& context,
                             const NodeObj& node) noexcept
    {
        CARB_PROFILE_ZONE(carb::profiler::kCaptureMaskDefault, "[ComputeVectorized][OGN][x1] %s", NODE_PATH);
        auto adapter = [](NodeTypeDataClass& db) { return NodeTypeClass::computeVectorized(db, 1) != 0; };
        return call_computeCommonOGN(context, node, adapter, 1);
    }

    //===============
    // regOGN, regABI, vecOGN, vecABI
    static bool call_compute(std::false_type,
                             std::false_type,
                             std::false_type,
                             std::true_type,
                             const GraphContextObj& context,
                             const NodeObj& node) noexcept
    {
        CARB_PROFILE_ZONE(carb::profiler::kCaptureMaskDefault, "[ComputeVectorized][ABI][x1] %s", NODE_PATH);
        if (node.iNode->increaseComputeCount)
            node.iNode->increaseComputeCount(node, 1);
        return NodeTypeClass::computeVectorized(context, node, 1) != 0;
    }

    //===============
    static bool call_compute(
        std::false_type, std::false_type, std::false_type, std::false_type, const GraphContextObj&, const NodeObj&) noexcept
    {
        OGN_DBG std::cout << "DBG: No compute or computeVectorized method." << std::endl;
        return false;
    }

    // ----------------------------------------------------------------------
    //===============
    template <typename UNUSED1, typename UNUSED2, typename UNUSED3>
    // regOGN, regABI, vecOGN, vecABI
    static size_t call_computeVectorized(
        UNUSED1, UNUSED2, std::true_type, UNUSED3, const GraphContextObj& context, const NodeObj& node, size_t count) noexcept
    {
        // user has implemented the OGN version
        size_t ret = 0;
        auto adapter = [count, &ret, &node](NodeTypeDataClass& db)
        {
            db.resetToFirstInstance();
            if (db.canVectorize()) // auto conversion for instance might prevent vectorization
            {
                CARB_PROFILE_ZONE(
                    carb::profiler::kCaptureMaskDefault, "[ComputeVectorized][OGN][x%d] %s", (int)count, NODE_PATH);
                ret = NodeTypeClass::computeVectorized(db, count);
                return true;
            }

            CARB_PROFILE_ZONE(
                carb::profiler::kCaptureMaskDefault, "[ComputeVectorized][OGN][1 by 1][x%d] %s", (int)count, NODE_PATH);

            auto remaining = count;
            db.resetToFirstInstance();
            while (remaining--)
            {
                if (NodeTypeClass::computeVectorized(db, 1) != 0)
                    ++ret;
                db.moveToNextInstance();
            }
            db.resetToFirstInstance();
            return true;
        };
        call_computeCommonOGN(context, node, adapter, count);
        return ret;
    }

    //===============
    template <typename UNUSED1, typename UNUSED2>
    // regOGN, regABI, vecOGN, vecABI
    static size_t call_computeVectorized(UNUSED1,
                                         UNUSED2,
                                         std::false_type,
                                         std::true_type,
                                         const GraphContextObj& context,
                                         const NodeObj& node,
                                         size_t count) noexcept
    {
        CARB_PROFILE_ZONE(carb::profiler::kCaptureMaskDefault, "[ComputeVectorized][ABI][x%d] %s", (int)count, NODE_PATH);
        // user has implemented the ABI version
        if (node.iNode->increaseComputeCount)
            node.iNode->increaseComputeCount(node, count);
        return NodeTypeClass::computeVectorized(context, node, count);
    }

    //===============
    template <typename UNUSED1>
    // regOGN, regABI, vecOGN, vecABI
    static size_t call_computeVectorized(std::true_type,
                                         UNUSED1,
                                         std::false_type,
                                         std::false_type,
                                         const GraphContextObj& context,
                                         const NodeObj& node,
                                         size_t count) noexcept
    {
        // user has implemented the OGN version
        size_t ret = 0;
        auto adapter = [count, &ret, &node](NodeTypeDataClass& db)
        {
            CARB_PROFILE_ZONE(
                carb::profiler::kCaptureMaskDefault, "[Compute][OGN][1 by 1][x%d] %s", (int)count, NODE_PATH);
            auto remaining = count;
            db.resetToFirstInstance();
            while (remaining--)
            {
                if (NodeTypeClass::compute(db))
                    ret++;
                db.moveToNextInstance();
            }
            db.resetToFirstInstance();
            return true;
        };
        call_computeCommonOGN(context, node, adapter, count);
        return ret;
    }
    //===============
    // regOGN, regABI, vecOGN, vecABI
    static size_t call_computeVectorized(std::false_type,
                                         std::true_type,
                                         std::false_type,
                                         std::false_type,
                                         const GraphContextObj& context,
                                         const NodeObj& node,
                                         size_t count) noexcept
    {
        // unreachable
        CARB_LOG_FATAL("reaching abnormal code path in OmniGraphNodeABI");
        return 0;
    }

    //===============
    static size_t call_computeVectorized(std::false_type,
                                         std::false_type,
                                         std::false_type,
                                         std::false_type,
                                         const GraphContextObj&,
                                         const NodeObj&,
                                         size_t) noexcept
    {
        OGN_DBG std::cout << "DBG: No compute or computeVectorized method." << std::endl;
        return 0;
    }

    // ----------------------------------------------------------------------
    static const char* call_getNodeType(std::true_type) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(getNodeType)" << std::endl;
        return NodeTypeClass::getNodeType();
    }
    static const char* call_getNodeType(std::false_type) noexcept
    {
        // The node type name must always be available, usually as the one the .ogn file specified
        OGN_DBG std::cout << "DBG: Default(getNodeType)" << std::endl;
        return sm_nodeTypeName;
    }
    // ----------------------------------------------------------------------
    static const char* call_getTypeName(std::true_type, const NodeTypeObj& nodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(getTypeName)" << std::endl;
        return NodeTypeClass::getTypeName(nodeType);
    }
    static const char* call_getTypeName(std::false_type, const NodeTypeObj& nodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(getTypeName)" << std::endl;
        return sm_nodeTypeName;
    }
    // ----------------------------------------------------------------------
    // The generated database class may have overrides for the initialize() method if attribute metadata is present
    // so this function has two layers of calls.
    static void call_database_initialize(std::true_type, const GraphContextObj& context, const NodeObj& node) noexcept
    {
        OGN_DBG std::cout << "DBG: Database Override(initialize)" << std::endl;
        NodeTypeDataClass::initialize(context, node);
    }
    static void call_database_initialize(std::false_type, const GraphContextObj& context, const NodeObj& node) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(initialize)" << std::endl;
        return;
    }
    static void call_initialize(std::true_type, const GraphContextObj& context, const NodeObj& node) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(initialize)" << std::endl;
        call_database_initialize(is_detected<has_initialize, NodeTypeDataClass>(), context, node);
        NodeTypeClass::initialize(context, node);
    }
    static void call_initialize(std::false_type, const GraphContextObj& context, const NodeObj& node) noexcept
    {
        call_database_initialize(is_detected<has_initialize, NodeTypeDataClass>(), context, node);
        return;
    }
    // ----------------------------------------------------------------------
    static void call_initializeType(std::true_type, const NodeTypeObj& nodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(initializeType)" << std::endl;
        // Rely on the database to handle the case of state attributes, this is just for internal state data
        if (!std::is_empty<NodeTypeClass>::value)
        {
            nodeType.iNodeType->setHasState(nodeType, true);
        }
        NodeTypeDataClass::initializeType(nodeType);
        NodeTypeClass::initializeType(nodeType);
    }
    static void call_initializeType(std::false_type, const NodeTypeObj& nodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(initializeType)" << std::endl;
        // Rely on the database to handle the case of state attributes, this is just for internal state data
        if (!std::is_empty<NodeTypeClass>::value)
        {
            nodeType.iNodeType->setHasState(nodeType, true);
        }
        NodeTypeDataClass::initializeType(nodeType);
    }
    // ----------------------------------------------------------------------
    static void call_registerTasks(std::true_type) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(registerTasks)" << std::endl;
        NodeTypeClass::registerTasks();
    }
    static void call_registerTasks(std::false_type) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(registerTasks)" << std::endl;
        return;
    }
    // ----------------------------------------------------------------------
    static void call_release(std::true_type, const NodeObj& node) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(release)" << std::endl;
        NodeTypeClass::release(node);
    }
    static void call_release(std::false_type, const NodeObj& node) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(release)" << std::endl;
        return;
    }
    // ----------------------------------------------------------------------
    static void call_initInstance(std::true_type, const NodeObj& node, GraphInstanceID instanceID) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(initInstance)" << std::endl;
        NodeTypeClass::initInstance(node, instanceID);
    }
    static void call_initInstance(std::false_type, const NodeObj& /*node*/, GraphInstanceID /*instanceID*/) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(initInstance)" << std::endl;
        return;
    }
    // ----------------------------------------------------------------------
    static void call_releaseInstance(std::true_type, const NodeObj& node, GraphInstanceID instanceID) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(releaseInstance)" << std::endl;
        NodeTypeClass::releaseInstance(node, instanceID);
    }
    static void call_releaseInstance(std::false_type, const NodeObj& /*node*/, GraphInstanceID /*instanceID*/) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(releaseInstance)" << std::endl;
        return;
    }
    // ----------------------------------------------------------------------
    static bool call_updateNodeVersion(
        std::true_type, const GraphContextObj& context, const NodeObj& node, int oldVersion, int newVersion) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(updateNodeVersion)" << std::endl;
        return NodeTypeClass::updateNodeVersion(context, node, oldVersion, newVersion);
    }
    static bool call_updateNodeVersion(
        std::false_type, const GraphContextObj& context, const NodeObj& node, int oldVersion, int newVersion) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(updateNodeVersion)" << std::endl;
        return true;
    }
    // ----------------------------------------------------------------------
    static size_t call_getAllMetadata(
        std::true_type, const NodeTypeObj& nodeType, const char** keyBuf, const char** valueBuf, size_t bufSize) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(getAllMetadata)" << std::endl;
        return NodeTypeClass::getAllMetadata(nodeType, keyBuf, valueBuf, bufSize);
    }
    static size_t call_getAllMetadata(
        std::false_type, const NodeTypeObj& nodeType, const char** keyBuf, const char** valueBuf, size_t bufSize) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(getAllMetadata)" << std::endl;
        return 0;
    }
    // ----------------------------------------------------------------------
    static const char* call_getMetadata(std::true_type, const NodeTypeObj& nodeType, const char* key) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(getMetadata)" << std::endl;
        return NodeTypeClass::getMetadata(nodeType, key);
    }
    static const char* call_getMetadata(std::false_type, const NodeTypeObj& nodeType, const char* key) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(getMetadata)" << std::endl;
        return nullptr;
    }
    // ----------------------------------------------------------------------
    static size_t call_getMetadataCount(std::true_type, const NodeTypeObj& nodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(getMetadataCount)" << std::endl;
        return NodeTypeClass::getMetadataCount(nodeType);
    }
    static size_t call_getMetadataCount(std::false_type, const NodeTypeObj& nodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(getMetadataCount)" << std::endl;
        return 0;
    }
    // ----------------------------------------------------------------------
    static void call_setMetadata(std::true_type, const NodeTypeObj& nodeType, const char* key, const char* value) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(setMetadata)" << std::endl;
        NodeTypeClass::setMetadata(nodeType, key, value);
    }
    static void call_setMetadata(std::false_type, const NodeTypeObj& nodeType, const char* key, const char* value) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(setMetadata)" << std::endl;
    }

    // ----------------------------------------------------------------------
    static void call_addSubNodeType(std::true_type,
                                    const NodeTypeObj& nodeType,
                                    const char* subNodeTypeName,
                                    const NodeTypeObj& subNodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(addSubNodeType)" << std::endl;
        NodeTypeClass::addSubNodeType(nodeType, subNodeTypeName, subNodeType);
    }
    static void call_addSubNodeType(std::false_type,
                                    const NodeTypeObj& nodeType,
                                    const char* subNodeTypeName,
                                    const NodeTypeObj& subNodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(addSubNodeType)" << std::endl;
    }

    // ----------------------------------------------------------------------
    static NodeTypeObj call_getSubNodeType(std::true_type, const NodeTypeObj& nodeType, const char* subNodeTypeName) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(getSubNodeType)" << std::endl;
        return NodeTypeClass::getSubNodeType(nodeType, subNodeTypeName);
    }
    static NodeTypeObj call_getSubNodeType(std::false_type, const NodeTypeObj& nodeType, const char* subNodeTypeName) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(getSubNodeType)" << std::endl;
        return NodeTypeObj();
    }

    // ----------------------------------------------------------------------
    static NodeTypeObj call_createNodeType(std::true_type, const char* nodeTypeName, int version) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(createNodeType)" << std::endl;
        return NodeTypeClass::createNodeType(nodeTypeName, version);
    }
    static NodeTypeObj call_createNodeType(std::false_type, const char* nodeTypeName, int version) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(createNodeType)" << std::endl;
        return NodeTypeObj();
    }

    // ----------------------------------------------------------------------
    static void call_database_onConnectionTypeResolve(std::true_type, const NodeObj& node) noexcept
    {
        OGN_DBG std::cout << "DBG: Database Override(onConnectionTypeResolve)" << std::endl;
        NodeTypeDataClass::onConnectionTypeResolve(node);
    }
    static void call_database_onConnectionTypeResolve(std::false_type, const NodeObj& node) noexcept
    {
        OGN_DBG std::cout << "DBG: Database Default(onConnectionTypeResolve)" << std::endl;
    }
    static void call_onConnectionTypeResolve(std::true_type, const NodeObj& node) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(onConnectionTypeResolve)" << std::endl;
        NodeTypeClass::onConnectionTypeResolve(node);
        call_database_onConnectionTypeResolve(is_detected<has_onConnectionTypeResolve, NodeTypeDataClass>(), node);
    }
    static void call_onConnectionTypeResolve(std::false_type, const NodeObj& node) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(onConnectionTypeResolve)" << std::endl;
        call_database_onConnectionTypeResolve(is_detected<has_onConnectionTypeResolve, NodeTypeDataClass>(), node);
    }
    // ----------------------------------------------------------------------
    static bool call_inspect(std::true_type, const NodeTypeObj& nodeType, inspect::IInspector* inspector) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(inspect)" << std::endl;
        return NodeTypeClass::inspect(nodeType, inspector);
    }
    static bool call_inspect(std::false_type, const NodeTypeObj& nodeType, inspect::IInspector* inspector) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(inspect)" << std::endl;
        return false;
    }
    // ----------------------------------------------------------------------
    static bool call_definedAtRuntime(std::true_type, const NodeTypeObj& nodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(definedAtRuntime)" << std::endl;
        return NodeTypeClass::definedAtRuntime(nodeType);
    }
    static bool call_definedAtRuntime(std::false_type, const NodeTypeObj& nodeType) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(definedAtRuntime)" << std::endl;
        return false;
    }
    // ----------------------------------------------------------------------
    static bool call_computeCuda(std::true_type, const NodeObj& nodeObj) noexcept
    {
        OGN_DBG std::cout << "DBG: Override(computeCuda)" << std::endl;

        auto create = [](GraphContextObj const* contexts, NodeObj const* nodes, size_t count) -> ogn::OmniGraphDatabase*
        { return new NodeTypeDataClass(contexts, nodes, count); };

        NodeTypeDataClass* nodeDataPtr = reinterpret_cast<NodeTypeDataClass*>(
            nodeObj.iNode && nodeObj.iNode->getOgnDatabase ? nodeObj.iNode->getOgnDatabase(nodeObj, create) : nullptr);
        if (nodeDataPtr == nullptr || nodeDataPtr->validate() == false)
        {
            CARB_LOG_ERROR("call_computeCuda: invalid node database");
            return false;
        }

        return NodeTypeClass::computeCuda(*nodeDataPtr);
    }
    static bool call_computeCuda(std::false_type, const NodeObj& nodeObj) noexcept
    {
        OGN_DBG std::cout << "DBG: Default(computeCuda)" << std::endl;
        return false;
    }

public:
    // ----------------------------------------------------------------------
    // These are the ABI implementations, which call the right version of the above call_DBG: functions
    // based on whether the node class has custom implementations of the ABI functions or not.

    /**
     * Implementation of omni::graph::core::INodeType::addInput to use as part of a node type definition
     */
    static void addInput(const NodeTypeObj& nodeType,
                         const char* name,
                         const char* typeName,
                         bool required,
                         const void* defaultValuePtr,
                         const size_t* defaultElemCountPtr) noexcept
    {
        return call_addInput(is_detected<has_addInput, NodeTypeClass>(), nodeType, name, typeName, required,
                             defaultValuePtr, defaultElemCountPtr);
    }
    /**
     * Implementation of omni::graph::core::INodeType::addOutput to use as part of a node type definition
     */
    static void addOutput(const NodeTypeObj& nodeType,
                          const char* name,
                          const char* typeName,
                          bool required,
                          const void* defaultValuePtr,
                          const size_t* defaultElemCountPtr) noexcept
    {
        return call_addOutput(is_detected<has_addOutput, NodeTypeClass>(), nodeType, name, typeName, required,
                              defaultValuePtr, defaultElemCountPtr);
    }
    /**
     * Implementation of omni::graph::core::INodeType::addState to use as part of a node type definition
     */
    static void addState(const NodeTypeObj& nodeType,
                         const char* name,
                         const char* typeName,
                         bool required,
                         const void* defaultValuePtr,
                         const size_t* defaultElemCountPtr) noexcept
    {
        return call_addState(is_detected<has_addState, NodeTypeClass>(), nodeType, name, typeName, required,
                             defaultValuePtr, defaultElemCountPtr);
    }
    /**
     * Implementation of omni::graph::core::INodeType::addExtendedInput to use as part of a node type definition
     */
    static void addExtendedInput(const NodeTypeObj& nodeType,
                                 const char* name,
                                 const char* typeName,
                                 bool required,
                                 ExtendedAttributeType extendedType) noexcept
    {
        return call_addExtendedInput(
            is_detected<has_addExtendedInput, NodeTypeClass>(), nodeType, name, typeName, required, extendedType);
    }
    /**
     * Implementation of omni::graph::core::INodeType::addExtendedOutput to use as part of a node type definition
     */
    static void addExtendedOutput(const NodeTypeObj& nodeType,
                                  const char* name,
                                  const char* typeName,
                                  bool required,
                                  ExtendedAttributeType extendedType) noexcept
    {
        return call_addExtendedOutput(
            is_detected<has_addExtendedOutput, NodeTypeClass>(), nodeType, name, typeName, required, extendedType);
    }
    /**
     * Implementation of omni::graph::core::INodeType::addExtendedState to use as part of a node type definition
     */
    static void addExtendedState(const NodeTypeObj& nodeType,
                                 const char* name,
                                 const char* typeName,
                                 bool required,
                                 ExtendedAttributeType extendedType) noexcept
    {
        return call_addExtendedState(
            is_detected<has_addExtendedState, NodeTypeClass>(), nodeType, name, typeName, required, extendedType);
    }
    /**
     * Implementation of omni::graph::core::INodeType::hasState to use as part of a node type definition
     */
    static bool hasState(const NodeTypeObj& nodeType) noexcept
    {
        return call_hasState(is_detected<has_hasState, NodeTypeClass>(), nodeType);
    }
    /**
     * Implementation of omni::graph::core::INodeType::setHasState to use as part of a node type definition
     */
    static void setHasState(const NodeTypeObj& nodeType, bool hasState) noexcept
    {
        call_setHasState(is_detected<has_setHasState, NodeTypeClass>(), nodeType, hasState);
    }
    // If the compute ABI function is overridden the user loses all of the nice setup
    // we've done with the data class, however we won't disallow it as there may be reasons
    // for doing it that aren't currently apparent.
    /**
     * Implementation of omni::graph::core::INodeType::compute to use as part of a node type definition
     */
    static bool compute(const GraphContextObj& context, const NodeObj& node) noexcept
    {
        return call_compute(regOGN(), regABI(), vecOGN(), vecABI(), context, node);
    }

    /**
     * Implementation of omni::graph::core::INodeType::computeVectorized to use as part of a node type definition
     */
    static size_t computeVectorized(const GraphContextObj& context, const NodeObj& node, size_t count) noexcept
    {
        return call_computeVectorized(regOGN(), regABI(), vecOGN(), vecABI(), context, node, count);
    }

    /**
     * Implementation of omni::graph::core::INodeType::getNodeType to use as part of a node type definition
     */
    static const char* getNodeType()
    {
        return call_getNodeType(is_detected<has_getNodeType, NodeTypeClass>());
    }
    /**
     * Implementation of omni::graph::core::INodeType::getTypeName to use as part of a node type definition
     */
    static const char* getTypeName(const NodeTypeObj& nodeType)
    {
        return call_getTypeName(is_detected<has_getTypeName, NodeTypeClass>(), nodeType);
    }
    /**
     * Implementation of omni::graph::core::INodeType::initialize to use as part of a node type definition
     */
    static void initialize(const GraphContextObj& context, const NodeObj& node) noexcept
    {
        call_initialize(is_detected<has_initialize, NodeTypeClass>(), context, node);
    }
    /**
     * Implementation of omni::graph::core::INodeType::initializeType to use as part of a node type definition
     */
    static void initializeType(const NodeTypeObj& nodeType) noexcept
    {
        call_initializeType(is_detected<has_initializeType, NodeTypeClass>(), nodeType);
    }
    /**
     * Implementation of omni::graph::core::INodeType::registerTasks to use as part of a node type definition
     */
    static void registerTasks() noexcept
    {
        call_registerTasks(is_detected<has_registerTasks, NodeTypeClass>());
    }
    /**
     * Implementation of omni::graph::core::INodeType::release to use as part of a node type definition
     */
    static void release(const NodeObj& node) noexcept
    {
        call_release(is_detected<has_release, NodeTypeClass>(), node);
        // Release any data associated to the authoring graph
        NodeTypeDataClass::release(node, node.iNode->getGraphInstanceID(node.nodeHandle, kAuthoringGraphIndex));
    }
    /**
     * Implementation of omni::graph::core::INodeType::releaseInstace to use as part of a node type definition
     */
    static void initInstance(const NodeObj& node, GraphInstanceID instanceId) noexcept
    {
        call_initInstance(is_detected<has_initInstance, NodeTypeClass>(), node, instanceId);
    }
    /**
     * Implementation of omni::graph::core::INodeType::releaseInstace to use as part of a node type definition
     */
    static void releaseInstance(const NodeObj& node, GraphInstanceID instanceId) noexcept
    {
        call_releaseInstance(is_detected<has_releaseInstance, NodeTypeClass>(), node, instanceId);
        // Release any user data after the callback
        NodeTypeDataClass::release(node, instanceId);
    }
    /**
     * Implementation of omni::graph::core::INodeType::destroyDB to use as part of a node type definition
     */
    static void destroyDB(const NodeObj& node, ogn::OmniGraphDatabase* db)
    {
        delete static_cast<NodeTypeDataClass*>(db);
    }
    /**
     * Implementation of omni::graph::core::INodeType::notifyTypeResolution to use as part of a node type definition
     */
    static void notifyTypeResolution(AttributeObj const& attrib, ogn::OmniGraphDatabase* db)
    {
        static_cast<NodeTypeDataClass*>(db)->onTypeResolutionChanged(attrib);
    }
    /**
     * Implementation of omni::graph::core::INodeType::notifyDynamicAttributeChanged to use as part of a node type
     * definition
     */
    static void notifyDynamicAttributeChanged(ogn::OmniGraphDatabase* db, AttributeObj const& attr, bool isAttributeCreated)
    {
        static_cast<NodeTypeDataClass*>(db)->onDynamicAttributesChanged(attr, isAttributeCreated);
    }
    /**
     * Implementation of omni::graph::core::INodeType::notifyDataLocationChanged to use as part of a node type
     * definition
     */
    static void notifyDataLocationChanged(ogn::OmniGraphDatabase* db, AttributeObj const& attr)
    {
        static_cast<NodeTypeDataClass*>(db)->onDataLocationChanged(attr);
    }
    /**
     * Implementation of omni::graph::core::INodeType::udpateNodeVersion to use as part of a node type definition
     */
    static bool updateNodeVersion(const GraphContextObj& context, const NodeObj& node, int oldVersion, int newVersion) noexcept
    {
        return call_updateNodeVersion(
            is_detected<has_updateNodeVersion, NodeTypeClass>(), context, node, oldVersion, newVersion);
    }
    /**
     * Implementation of omni::graph::core::INodeType::getAllMetadata to use as part of a node type definition
     */
    static size_t getAllMetadata(const NodeTypeObj& nodeType, const char** keyBuf, const char** valueBuf, size_t bufSize) noexcept
    {
        return call_getAllMetadata(is_detected<has_getAllMetadata, NodeTypeClass>(), nodeType, keyBuf, valueBuf, bufSize);
    }
    /**
     * Implementation of omni::graph::core::INodeType::getMetadata to use as part of a node type definition
     */
    static const char* getMetadata(const NodeTypeObj& nodeType, const char* key) noexcept
    {
        return call_getMetadata(is_detected<has_getMetadata, NodeTypeClass>(), nodeType, key);
    }
    /**
     * Implementation of omni::graph::core::INodeType::getMetadataCount to use as part of a node type definition
     */
    static size_t getMetadataCount(const NodeTypeObj& nodeType) noexcept
    {
        return call_getMetadataCount(is_detected<has_getMetadataCount, NodeTypeClass>(), nodeType);
    }
    /**
     * Implementation of omni::graph::core::INodeType::setMetadata to use as part of a node type definition
     */
    static void setMetadata(const NodeTypeObj& nodeType, const char* key, const char* value) noexcept
    {
        call_setMetadata(is_detected<has_setMetadata, NodeTypeClass>(), nodeType, key, value);
    }
    /**
     * Implementation of omni::graph::core::INodeType::addSubNodeType to use as part of a node type definition
     */
    static void addSubNodeType(const NodeTypeObj& nodeType, const char* subNodeTypeName, const NodeTypeObj& subNodeType)
    {
        call_addSubNodeType(is_detected<has_addSubNodeType, NodeTypeClass>(), nodeType, subNodeTypeName, subNodeType);
    }
    /**
     * Implementation of omni::graph::core::INodeType::getSubNodeType to use as part of a node type definition
     */
    static NodeTypeObj getSubNodeType(const NodeTypeObj& nodeType, const char* subNodeTypeName)
    {
        return call_getSubNodeType(is_detected<has_getSubNodeType, NodeTypeClass>(), nodeType, subNodeTypeName);
    }
    /**
     * Implementation of omni::graph::core::INodeType::createNodeType to use as part of a node type definition
     */
    static NodeTypeObj createNodeType(const char* nodeTypeName, int version)
    {
        return call_createNodeType(is_detected<has_createNodeType, NodeTypeClass>(), nodeTypeName, version);
    }
    /**
     * Implementation of omni::graph::core::INodeType::onConnectionTypeResolve to use as part of a node type definition
     */
    static void onConnectionTypeResolve(const NodeObj& node)
    {
        call_onConnectionTypeResolve(is_detected<has_onConnectionTypeResolve, NodeTypeClass>(), node);
    }
    /**
     * Implementation of omni::graph::core::INodeType::inspect to use as part of a node type definition
     */
    static bool inspect(const NodeTypeObj& nodeType, inspect::IInspector* inspector)
    {
        return call_inspect(is_detected<has_inspect, NodeTypeClass>(), nodeType, inspector);
    }
    /**
     * Default implementation of omni::graph::core::INodeType::definedAtRuntime to use as part of a node type definition
     */
    static bool definedAtRuntime(const NodeTypeObj& nodeType)
    {
        return call_definedAtRuntime(is_detected<has_definedAtRuntime, NodeTypeClass>(), nodeType);
    }

    /**
    * Implementation of omni::graph::core::INodeType::computeCuda to use as part of a node type definition.
    *
    * This ABI is supported for pre and post render graph nodes which are executed as cuda commands.
    * The computeCuda ABI is ignored by the framework and will not produce any output
    * when the nodes which implement it are executed outside of the context of
    * a pre or post render graph.
    *
    * @param[in] node The node object on which computeCuda is called.
    * @return Returns true if the node compute was successful, otherwise returns false.
    */
    static bool computeCuda(const NodeObj& node)
    {
        return call_computeCuda(is_detected<has_computeCuda, NodeTypeClass>(), node);
    }

public:
    /**
     * @brief Constructor with the basic information that is needed to identify a node type
     *
     * @param nodeTypeName Unique name of the node type
     * @param nodeTypeVersion Version of the node type being defined
     * @param nodeTypeExtension Extension owning the node type
     */
    OmniGraphNode_ABI(const char* nodeTypeName, int nodeTypeVersion, const char* nodeTypeExtension)
        : NodeTypeABI(nodeTypeName, nodeTypeVersion, nodeTypeExtension)
    {
        sm_nodeTypeName = nodeTypeName;
    }

    /**
     * @brief Populate an INodeType interface with the functions that implement this particular templated node type
     *
     * @param[out] nodeTypeInterface Interface to be populated
     */
    void populateNodeTypeInterface(INodeType& nodeTypeInterface) const override
    {
        // Any functions required in order for the interface to work are left as nullptr when
        // there is no implementation of them overridden by the node so that the defaults can be used.
        nodeTypeInterface.addInput = is_detected<has_addInput, NodeTypeClass>::value ? addInput : nullptr;
        nodeTypeInterface.addOutput = is_detected<has_addOutput, NodeTypeClass>::value ? addOutput : nullptr;
        nodeTypeInterface.addState = is_detected<has_addState, NodeTypeClass>::value ? addState : nullptr;
        nodeTypeInterface.addExtendedInput =
            is_detected<has_addExtendedInput, NodeTypeClass>::value ? addExtendedInput : nullptr;
        nodeTypeInterface.addExtendedOutput =
            is_detected<has_addExtendedOutput, NodeTypeClass>::value ? addExtendedOutput : nullptr;
        nodeTypeInterface.addExtendedState =
            is_detected<has_addExtendedState, NodeTypeClass>::value ? addExtendedState : nullptr;
        nodeTypeInterface.hasState = is_detected<has_hasState, NodeTypeClass>::value ? hasState : nullptr;
        nodeTypeInterface.setHasState = is_detected<has_setHasState, NodeTypeClass>::value ? setHasState : nullptr;
        nodeTypeInterface.getNodeType = getNodeType;
        nodeTypeInterface.getTypeName = getTypeName;
        nodeTypeInterface.initialize = initialize;
        nodeTypeInterface.initializeType = initializeType;
        nodeTypeInterface.registerTasks = registerTasks;
        nodeTypeInterface.release = release;
        nodeTypeInterface.updateNodeVersion = updateNodeVersion;
        nodeTypeInterface.getAllMetadata =
            is_detected<has_getAllMetadata, NodeTypeClass>::value ? getAllMetadata : nullptr;
        nodeTypeInterface.getMetadata = is_detected<has_getMetadata, NodeTypeClass>::value ? getMetadata : nullptr;
        nodeTypeInterface.getMetadataCount =
            is_detected<has_getMetadataCount, NodeTypeClass>::value ? getMetadataCount : nullptr;
        nodeTypeInterface.setMetadata = is_detected<has_setMetadata, NodeTypeClass>::value ? setMetadata : nullptr;
        nodeTypeInterface.addSubNodeType =
            is_detected<has_addSubNodeType, NodeTypeClass>::value ? addSubNodeType : nullptr;
        nodeTypeInterface.getSubNodeType =
            is_detected<has_getSubNodeType, NodeTypeClass>::value ? getSubNodeType : nullptr;
        nodeTypeInterface.createNodeType =
            is_detected<has_createNodeType, NodeTypeClass>::value ? createNodeType : nullptr;
        nodeTypeInterface.onConnectionTypeResolve = onConnectionTypeResolve;
        nodeTypeInterface.inspect = is_detected<has_inspect, NodeTypeClass>::value ? inspect : nullptr;

        nodeTypeInterface.compute = regOGN() || regABI() || vecOGN() || vecABI() ? compute : nullptr;
        nodeTypeInterface.computeVectorized = regOGN() || vecOGN() || vecABI() ? computeVectorized : nullptr;
        nodeTypeInterface.initInstance = initInstance;
        nodeTypeInterface.releaseInstance = releaseInstance;
        nodeTypeInterface.destroyDB = destroyDB;
        nodeTypeInterface.notifyTypeResolution = notifyTypeResolution;
        nodeTypeInterface.notifyDynamicAttributeChanged = notifyDynamicAttributeChanged;
        nodeTypeInterface.getCarbABIVersion = []() { return INodeType::getInterfaceDesc().version; };
        nodeTypeInterface.notifyDataLocationChanged = notifyDataLocationChanged;
        nodeTypeInterface.definedAtRuntime = definedAtRuntime;
        nodeTypeInterface.computeCuda = cudaABI() ? computeCuda : nullptr;

        // retired
        nodeTypeInterface._retired_0 = nullptr;
        nodeTypeInterface._retired_1 = nullptr;
    }

    static const char* sm_nodeTypeName; //!< Name of node type, to allow passing a static function to ABI
};
template <typename NodeTypeClass, typename NodeTypeDataClass>
const char* OmniGraphNode_ABI<NodeTypeClass, NodeTypeDataClass>::sm_nodeTypeName{ nullptr };

} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
