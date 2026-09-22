// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once
#ifndef NODE_TYPE_REGISTRY
#    error This file can only be included indirectly from NodeTypeRegistrar.h
#endif


#include "iComputeGraph.h"

#include <type_traits>

//======================================================================
// Template metaprogramming that allows the node registration to figure out at compile time
// which functions a node has that can be registered. Functions come from the INodeType
// interface in iComputeGraph.h.
template <typename>
struct sfinae_true : std::true_type
{
};
template <typename>
struct sfinae_false : std::false_type
{
};

// Template collection to provide a pointer to the static method getNodeType() if it exists
// Usage: auto getNodeTypeFn = getNodeTypeFunction<NodeClass>();
using GetNodeTypeFunction = std::add_pointer<const char*()>::type;
template <typename NodeType>
constexpr auto _checkGetNodeTypeFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkGetNodeTypeFunction(int) -> sfinae_true<decltype(std::declval<const NodeType&>().getNodeType())>;
template <typename NodeType>
struct _hasGetNodeTypeFunction : decltype(_checkGetNodeTypeFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasGetNodeTypeFunction<NodeType>::value, bool>::type = 0>
static inline GetNodeTypeFunction getNodeTypeFunction()
{
    return &NodeType::getNodeType;
};
template <typename NodeType, typename std::enable_if<!_hasGetNodeTypeFunction<NodeType>::value, bool>::type = 0>
static inline GetNodeTypeFunction getNodeTypeFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method compute() if it exists
// Usage: auto computeFn = computeFunction<NodeClass>();
using ComputeFunction = std::add_pointer<bool(const GraphContextObj&, const NodeObj&)>::type;
template <typename NodeType>
constexpr auto _checkComputeFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkComputeFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().compute(std::declval<const GraphContextObj&>(),
                                                                    std::declval<const NodeObj&>()))>;
template <typename NodeType>
struct _hasComputeFunction : decltype(_checkComputeFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasComputeFunction<NodeType>::value, bool>::type = 0>
static inline ComputeFunction computeFunction()
{
    return &NodeType::compute;
};
template <typename NodeType, typename std::enable_if<!_hasComputeFunction<NodeType>::value, bool>::type = 0>
static inline ComputeFunction computeFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method initialize() if it exists
// Usage: auto initializeFn = initializeFunction<NodeClass>();
using InitializeFunction = std::add_pointer<void(const GraphContextObj&, const NodeObj&)>::type;
template <typename NodeType>
constexpr auto _checkInitializeFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkInitializeFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().initialize(std::declval<const GraphContextObj&>(),
                                                                       std::declval<const NodeObj&>()))>;
template <typename NodeType>
struct _hasInitializeFunction : decltype(_checkInitializeFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasInitializeFunction<NodeType>::value, bool>::type = 0>
static inline InitializeFunction initializeFunction()
{
    return &NodeType::initialize;
};
template <typename NodeType, typename std::enable_if<!_hasInitializeFunction<NodeType>::value, bool>::type = 0>
static inline InitializeFunction initializeFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method release() if it exists
// Usage: auto releaseFn = releaseFunction<NodeClass>();
using ReleaseFunction = std::add_pointer<void(const NodeObj&)>::type;
template <typename NodeType>
constexpr auto _checkReleaseFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkReleaseFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().release(std::declval<const NodeObj&>()))>;
template <typename NodeType>
struct _hasReleaseFunction : decltype(_checkReleaseFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasReleaseFunction<NodeType>::value, bool>::type = 0>
static inline ReleaseFunction releaseFunction()
{
    return &NodeType::release;
};
template <typename NodeType, typename std::enable_if<!_hasReleaseFunction<NodeType>::value, bool>::type = 0>
static inline ReleaseFunction releaseFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method initializeType() if it exists
// Usage: auto initializeTypeFn = initializeTypeFunction<NodeClass>();
using InitializeTypeFunction = std::add_pointer<void(const NodeTypeObj&)>::type;
template <typename NodeType>
constexpr auto _checkInitializeTypeFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkInitializeTypeFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().initializeType(std::declval<const NodeTypeObj&>()))>;
template <typename NodeType>
struct _hasInitializeTypeFunction : decltype(_checkInitializeTypeFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasInitializeTypeFunction<NodeType>::value, bool>::type = 0>
static inline InitializeTypeFunction initializeTypeFunction()
{
    return &NodeType::initializeType;
};
template <typename NodeType, typename std::enable_if<!_hasInitializeTypeFunction<NodeType>::value, bool>::type = 0>
static inline InitializeTypeFunction initializeTypeFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method updateNodeVersion() if it exists
// Usage: auto updateNodeVersionFn = updateNodeVersionFunction<NodeClass>();
using UpdateNodeVersionFunction = std::add_pointer<bool(const GraphContextObj&, const NodeObj&, int, int)>::type;
template <typename NodeType>
constexpr auto _checkUpdateNodeVersionFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkUpdateNodeVersionFunction(int) -> sfinae_true<decltype(std::declval<const NodeType&>().updateNodeVersion(
    std::declval<const GraphContextObj&>(), std::declval<const NodeObj&>(), std::declval<int>(), std::declval<int>()))>;
template <typename NodeType>
struct _hasUpdateNodeVersionFunction : decltype(_checkUpdateNodeVersionFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasUpdateNodeVersionFunction<NodeType>::value, bool>::type = 0>
static inline UpdateNodeVersionFunction updateNodeVersionFunction()
{
    return &NodeType::updateNodeVersion;
};
template <typename NodeType, typename std::enable_if<!_hasUpdateNodeVersionFunction<NodeType>::value, bool>::type = 0>
static inline UpdateNodeVersionFunction updateNodeVersionFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method addInput() if it exists
// Usage: auto addInputFn = addInputFunction<NodeClass>();
using AddInputFunction =
    std::add_pointer<void(const NodeTypeObj&, const char*, const char*, bool, const void*, const size_t*)>::type;
template <typename NodeType>
constexpr auto _checkAddInputFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkAddInputFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().addInput(std::declval<const NodeTypeObj&>(),
                                                                     std::declval<const char*>(),
                                                                     std::declval<const char*>(),
                                                                     std::declval<bool>(),
                                                                     std::declval<const void*>(),
                                                                     std::declval<const size_t*>()))>;
template <typename NodeType>
struct _hasAddInputFunction : decltype(_checkAddInputFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasAddInputFunction<NodeType>::value, bool>::type = 0>
static inline AddInputFunction addInputFunction()
{
    return &NodeType::addInput;
};
template <typename NodeType, typename std::enable_if<!_hasAddInputFunction<NodeType>::value, bool>::type = 0>
static inline AddInputFunction addInputFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method addExtendedInput() if it exists
// Usage: auto addExtendedInputFn = addExtendedInputFunction<NodeClass>();
using AddExtendedInputFunction =
    std::add_pointer<void(const NodeTypeObj&, const char*, const char*, bool, ExtendedAttributeType)>::type;
template <typename NodeType>
constexpr auto _checkAddExtendedInputFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkAddExtendedInputFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().addExtendedInput(std::declval<const NodeTypeObj&>(),
                                                                             std::declval<const char*>(),
                                                                             std::declval<const char*>(),
                                                                             std::declval<bool>(),
                                                                             std::declval<ExtendedAttributeType>()))>;
template <typename NodeType>
struct _hasAddExtendedInputFunction : decltype(_checkAddExtendedInputFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasAddExtendedInputFunction<NodeType>::value, bool>::type = 0>
static inline AddExtendedInputFunction addExtendedInputFunction()
{
    return &NodeType::addExtendedInput;
};
template <typename NodeType, typename std::enable_if<!_hasAddExtendedInputFunction<NodeType>::value, bool>::type = 0>
static inline AddExtendedInputFunction addExtendedInputFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method addOutput() if it exists
// Usage: auto addOutputFn = addOutputFunction<NodeClass>();
using AddOutputFunction =
    std::add_pointer<void(const NodeTypeObj&, const char*, const char*, bool, const void*, const size_t*)>::type;
template <typename NodeType>
constexpr auto _checkAddOutputFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkAddOutputFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().addOutput(std::declval<const NodeTypeObj&>(),
                                                                      std::declval<const char*>(),
                                                                      std::declval<const char*>(),
                                                                      std::declval<bool>(),
                                                                      std::declval<const void*>(),
                                                                      std::declval<const size_t*>()))>;
template <typename NodeType>
struct _hasAddOutputFunction : decltype(_checkAddOutputFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasAddOutputFunction<NodeType>::value, bool>::type = 0>
static inline AddOutputFunction addOutputFunction()
{
    return &NodeType::addOutput;
};
template <typename NodeType, typename std::enable_if<!_hasAddOutputFunction<NodeType>::value, bool>::type = 0>
static inline AddOutputFunction addOutputFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method addExtendedOutput() if it exists
// Usage: auto addExtendedOutputFn = addExtendedOutputFunction<NodeClass>();
using AddExtendedOutputFunction =
    std::add_pointer<void(const NodeTypeObj&, const char*, const char*, bool, ExtendedAttributeType)>::type;
template <typename NodeType>
constexpr auto _checkAddExtendedOutputFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkAddExtendedOutputFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().addExtendedOutput(std::declval<const NodeTypeObj&>(),
                                                                              std::declval<const char*>(),
                                                                              std::declval<const char*>(),
                                                                              std::declval<bool>(),
                                                                              std::declval<ExtendedAttributeType>()))>;
template <typename NodeType>
struct _hasAddExtendedOutputFunction : decltype(_checkAddExtendedOutputFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasAddExtendedOutputFunction<NodeType>::value, bool>::type = 0>
static inline AddExtendedOutputFunction addExtendedOutputFunction()
{
    return &NodeType::addExtendedOutput;
};
template <typename NodeType, typename std::enable_if<!_hasAddExtendedOutputFunction<NodeType>::value, bool>::type = 0>
static inline AddExtendedOutputFunction addExtendedOutputFunction()
{
    return nullptr;
};


// Template collection to provide a pointer to the static method addState() if it exists
// Usage: auto addStateFn = addStateFunction<NodeClass>();
using AddStateFunction =
    std::add_pointer<void(const NodeTypeObj&, const char*, const char*, bool, const void*, const size_t*)>::type;
template <typename NodeType>
constexpr auto _checkAddStateFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkAddStateFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().addState(std::declval<const NodeTypeObj&>(),
                                                                     std::declval<const char*>(),
                                                                     std::declval<const char*>(),
                                                                     std::declval<bool>(),
                                                                     std::declval<const void*>(),
                                                                     std::declval<const size_t*>()))>;
template <typename NodeType>
struct _hasAddStateFunction : decltype(_checkAddStateFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasAddStateFunction<NodeType>::value, bool>::type = 0>
static inline AddStateFunction addStateFunction()
{
    return &NodeType::addState;
};
template <typename NodeType, typename std::enable_if<!_hasAddStateFunction<NodeType>::value, bool>::type = 0>
static inline AddStateFunction addStateFunction()
{
    return nullptr;
};


// Template collection to provide a pointer to the static method addExtendedState() if it exists
// Usage: auto addExtendedStateFn = addExtendedStateFunction<NodeClass>();
using AddExtendedStateFunction =
    std::add_pointer<void(const NodeTypeObj&, const char*, const char*, bool, ExtendedAttributeType)>::type;
template <typename NodeType>
constexpr auto _checkAddExtendedStateFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkAddExtendedStateFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().addExtendedState(std::declval<const NodeTypeObj&>(),
                                                                             std::declval<const char*>(),
                                                                             std::declval<const char*>(),
                                                                             std::declval<bool>(),
                                                                             std::declval<ExtendedAttributeType>()))>;
template <typename NodeType>
struct _hasAddExtendedStateFunction : decltype(_checkAddExtendedStateFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasAddExtendedStateFunction<NodeType>::value, bool>::type = 0>
static inline AddExtendedStateFunction addExtendedStateFunction()
{
    return &NodeType::addExtendedState;
};
template <typename NodeType, typename std::enable_if<!_hasAddExtendedStateFunction<NodeType>::value, bool>::type = 0>
static inline AddExtendedStateFunction addExtendedStateFunction()
{
    return nullptr;
};


// Template collection to provide a pointer to the static method hasState() if it exists
// Usage: auto hasStateFn = hasStateFunction<NodeClass>();
using HasStateFunction = std::add_pointer<bool(const NodeTypeObj&)>::type;
template <typename NodeType>
constexpr auto _checkHasStateFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkHasStateFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().hasState(std::declval<const NodeTypeObj&>()))>;
template <typename NodeType>
struct _hasHasStateFunction : decltype(_checkHasStateFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasHasStateFunction<NodeType>::value, bool>::type = 0>
static inline HasStateFunction hasStateFunction()
{
    return &NodeType::hasState;
};
template <typename NodeType, typename std::enable_if<!_hasHasStateFunction<NodeType>::value, bool>::type = 0>
static inline HasStateFunction hasStateFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method registerTasks() if it exists
// Usage: auto registerTasksFn = registerTasksFunction<NodeClass>();
using RegisterTasksFunction = std::add_pointer<void()>::type;
template <typename NodeType>
constexpr auto _checkRegisterTasksFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkRegisterTasksFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().registerTasks())>;
template <typename NodeType>
struct _hasRegisterTasksFunction : decltype(_checkRegisterTasksFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasRegisterTasksFunction<NodeType>::value, bool>::type = 0>
static inline RegisterTasksFunction registerTasksFunction()
{
    return &NodeType::registerTasks;
};
template <typename NodeType, typename std::enable_if<!_hasRegisterTasksFunction<NodeType>::value, bool>::type = 0>
static inline RegisterTasksFunction registerTasksFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method getAllMetadata() if it exists
// Usage: auto getAllMetadataFn = getAllMetadataFunction<NodeClass>();
using GetAllMetadataFunction =
    std::add_pointer<size_t(const NodeTypeObj& nodeType, const char**, const char**, size_t)>::type;
template <typename NodeType>
constexpr auto _checkGetAllMetadataFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkGetAllMetadataFunction(int) -> sfinae_true<decltype(std::declval<const NodeType&>().getAllMetadata(
    std::declval<const NodeTypeObj&>(), std::declval<const char**>(), std::declval<const char**>(), std::declval<size_t>()))>;
template <typename NodeType>
struct _hasGetAllMetadataFunction : decltype(_checkGetAllMetadataFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasGetAllMetadataFunction<NodeType>::value, bool>::type = 0>
static inline GetAllMetadataFunction getAllMetadataFunction()
{
    return &NodeType::getAllMetadata;
};
template <typename NodeType, typename std::enable_if<!_hasGetAllMetadataFunction<NodeType>::value, bool>::type = 0>
static inline GetAllMetadataFunction getAllMetadataFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method getMetadata() if it exists
// Usage: auto getMetadataFn = getMetadataFunction<NodeClass>();
using GetMetadataFunction = std::add_pointer<const char*(const NodeTypeObj& nodeType, const char*)>::type;
template <typename NodeType>
constexpr auto _checkGetMetadataFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkGetMetadataFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().getMetadata(std::declval<const NodeTypeObj&>(),
                                                                        std::declval<const char*>()))>;
template <typename NodeType>
struct _hasGetMetadataFunction : decltype(_checkGetMetadataFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasGetMetadataFunction<NodeType>::value, bool>::type = 0>
static inline GetMetadataFunction getMetadataFunction()
{
    return &NodeType::getMetadata;
};
template <typename NodeType, typename std::enable_if<!_hasGetMetadataFunction<NodeType>::value, bool>::type = 0>
static inline GetMetadataFunction getMetadataFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method getMetadataCount() if it exists
// Usage: auto getMetadataCountFn = getMetadataCountFunction<NodeClass>();
using GetMetadataCountFunction = std::add_pointer<size_t(const NodeTypeObj& nodeType)>::type;
template <typename NodeType>
constexpr auto _checkGetMetadataCountFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkGetMetadataCountFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().getMetadataCount(std::declval<const NodeTypeObj&>()))>;
template <typename NodeType>
struct _hasGetMetadataCountFunction : decltype(_checkGetMetadataCountFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasGetMetadataCountFunction<NodeType>::value, bool>::type = 0>
static inline GetMetadataCountFunction getMetadataCountFunction()
{
    return &NodeType::getMetadataCount;
};
template <typename NodeType, typename std::enable_if<!_hasGetMetadataCountFunction<NodeType>::value, bool>::type = 0>
static inline GetMetadataCountFunction getMetadataCountFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method setMetadata() if it exists
// Usage: auto setMetadataFn = setMetadataFunction<NodeClass>();
using SetMetadataFunction = std::add_pointer<void(const NodeTypeObj& nodeType, const char*, const char*)>::type;
template <typename NodeType>
constexpr auto _checkSetMetadataFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkSetMetadataFunction(int) -> sfinae_true<decltype(std::declval<const NodeType&>().setMetadata(
    std::declval<const NodeTypeObj&>(), std::declval<const char*>(), std::declval<const char*>()))>;
template <typename NodeType>
struct _hasSetMetadataFunction : decltype(_checkSetMetadataFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasSetMetadataFunction<NodeType>::value, bool>::type = 0>
static inline SetMetadataFunction setMetadataFunction()
{
    return &NodeType::setMetadata;
};
template <typename NodeType, typename std::enable_if<!_hasSetMetadataFunction<NodeType>::value, bool>::type = 0>
static inline SetMetadataFunction setMetadataFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method onConnectionMade() if it exists
// Usage: auto onConnectionTypeResolveFn = onConnectionTypeResolve<NodeClass>();
using OnConnectionTypeResolveFunction = std::add_pointer<void(const NodeObj&)>::type;
template <typename NodeType>
constexpr auto _checkOnConnectionTypeResolveFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkOnConnectionTypeResolveFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().onConnectionTypeResolve(std::declval<const NodeObj&>()))>;
template <typename NodeType>
struct _hasOnConnectionTypeResolveFunction : decltype(_checkOnConnectionTypeResolveFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasOnConnectionTypeResolveFunction<NodeType>::value, bool>::type = 0>
static inline OnConnectionTypeResolveFunction onConnectionTypeResolveFunction()
{
    return &NodeType::onConnectionTypeResolve;
};
template <typename NodeType, typename std::enable_if<!_hasOnConnectionTypeResolveFunction<NodeType>::value, bool>::type = 0>
static inline OnConnectionTypeResolveFunction onConnectionTypeResolveFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method inspect() if it exists
// Usage: auto inspectFn = inspectFunction<NodeClass>();
using InspectFunction = std::add_pointer<bool(const NodeTypeObj& nodeType, inspect::IInspector*)>::type;
template <typename NodeType>
constexpr auto _checkInspectFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkInspectFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().inspect(std::declval<const NodeTypeObj&>(),
                                                                    std::declval<inspect::IInspector*>()))>;
template <typename NodeType>
struct _hasInspectFunction : decltype(_checkInspectFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasInspectFunction<NodeType>::value, bool>::type = 0>
static inline InspectFunction inspectFunction()
{
    return &NodeType::inspect;
};
template <typename NodeType, typename std::enable_if<!_hasInspectFunction<NodeType>::value, bool>::type = 0>
static inline InspectFunction inspectFunction()
{
    return nullptr;
};


// Template collection to provide a pointer to the static method computeVectorized() if it exists
// Usage: auto computeVectorizedFn = computeVectorizedFunction<NodeClass>();
using ComputeVectorizedFunction = std::add_pointer<size_t(const GraphContextObj&, const NodeObj&, size_t)>::type;
template <typename NodeType>
constexpr auto _checkComputeVectorizedFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkComputeVectorizedFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().computeVectorized(
        std::declval<const GraphContextObj&>(), std::declval<const NodeObj&>(), std::declval<size_t>()))>;
template <typename NodeType>
struct _hasComputeVectorizedFunction : decltype(_checkComputeVectorizedFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasComputeVectorizedFunction<NodeType>::value, bool>::type = 0>
static inline ComputeVectorizedFunction computeVectorizedFunction()
{
    return &NodeType::computeVectorized;
};
template <typename NodeType, typename std::enable_if<!_hasComputeVectorizedFunction<NodeType>::value, bool>::type = 0>
static inline ComputeVectorizedFunction computeVectorizedFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method initInstance() if it exists
// Usage: auto initInstanceFn = initInstanceFunction<NodeClass>();
using InitInstanceFunction = std::add_pointer<void(const NodeObj&, GraphInstanceID)>::type;
template <typename NodeType>
constexpr auto _checkInitInstanceFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkInitInstanceFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().initInstance(std::declval<const NodeObj&>(),
                                                                         std::declval<GraphInstanceID>()))>;
template <typename NodeType>
struct _hasInitInstanceFunction : decltype(_checkInitInstanceFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasInitInstanceFunction<NodeType>::value, bool>::type = 0>
static inline InitInstanceFunction initInstanceFunction()
{
    return &NodeType::initInstance;
};
template <typename NodeType, typename std::enable_if<!_hasInitInstanceFunction<NodeType>::value, bool>::type = 0>
static inline InitInstanceFunction initInstanceFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method releaseInstance() if it exists
// Usage: auto releaseInstanceFn = releaseInstanceFunction<NodeClass>();
using ReleaseInstanceFunction = std::add_pointer<void(const NodeObj&, GraphInstanceID)>::type;
template <typename NodeType>
constexpr auto _checkReleaseInstanceFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkReleaseInstanceFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().releaseInstance(std::declval<const NodeObj&>(),
                                                                            std::declval<GraphInstanceID>()))>;
template <typename NodeType>
struct _hasReleaseInstanceFunction : decltype(_checkReleaseInstanceFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasReleaseInstanceFunction<NodeType>::value, bool>::type = 0>
static inline ReleaseInstanceFunction releaseInstanceFunction()
{
    return &NodeType::releaseInstance;
};
template <typename NodeType, typename std::enable_if<!_hasReleaseInstanceFunction<NodeType>::value, bool>::type = 0>
static inline ReleaseInstanceFunction releaseInstanceFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method definedAtRuntime() if it exists
// Usage: auto definedAtRuntimeFn = definedAtRuntimeFunction<NodeClass>();
using DefinedAtRuntimeFunction = std::add_pointer<bool(const NodeTypeObj&)>::type;
template <typename NodeType>
constexpr auto _checkDefinedAtRuntimeFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkDefinedAtRuntimeFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().definedAtRuntime(std::declval<const NodeTypeObj&>()))>;
template <typename NodeType>
struct _hasDefinedAtRuntimeFunction : decltype(_checkDefinedAtRuntimeFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasDefinedAtRuntimeFunction<NodeType>::value, bool>::type = 0>
static inline DefinedAtRuntimeFunction definedAtRuntimeFunction()
{
    return &NodeType::definedAtRuntime;
};
template <typename NodeType, typename std::enable_if<!_hasDefinedAtRuntimeFunction<NodeType>::value, bool>::type = 0>
static inline DefinedAtRuntimeFunction definedAtRuntimeFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method bool computeCuda(const NodeObj&) if it exists
// Usage: auto computeCudaFn = computeCudaFunction<NodeClass>();
using ComputeCudaFunction = std::add_pointer<bool(const NodeObj&)>::type;
template <typename NodeType>
constexpr auto _checkComputeCudaFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkComputeCudaFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().computeCuda(std::declval<const NodeObj&>()))>;
template <typename NodeType>
struct _hasComputeCudaFunction : decltype(_checkComputeCudaFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasComputeCudaFunction<NodeType>::value, bool>::type = 0>
static inline ComputeCudaFunction computeCudaFunction()
{
    return &NodeType::computeCuda;
};
template <typename NodeType, typename std::enable_if<!_hasComputeCudaFunction<NodeType>::value, bool>::type = 0>
static inline ComputeCudaFunction computeCudaFunction()
{
    return nullptr;
};

// Template collection to provide a pointer to the static method initializeNodes() if it exists
// Usage: auto InitializeNodesFunction = initializeNodesFunction<NodeClass>();
using InitializeNodesFunction = std::add_pointer<void(const GraphContextObj&, const NodeObj*, size_t)>::type;
template <typename NodeType>
constexpr auto _checkInitializeNodesFunction(long) -> sfinae_false<NodeType>;
template <typename NodeType>
constexpr auto _checkInitializeNodesFunction(int)
    -> sfinae_true<decltype(std::declval<const NodeType&>().initializeNodes(
        std::declval<const GraphContextObj&>(), std::declval<const NodeObj*>(), std::declval<size_t>()))>;
template <typename NodeType>
struct _hasInitializeNodesFunction : decltype(_checkInitializeNodesFunction<NodeType>(0))
{
};
template <typename NodeType, typename std::enable_if<_hasInitializeNodesFunction<NodeType>::value, bool>::type = 0>
static inline InitializeNodesFunction initializeNodesFunction()
{
    return &NodeType::initializeNodes;
};
template <typename NodeType, typename std::enable_if<!_hasInitializeNodesFunction<NodeType>::value, bool>::type = 0>
static inline InitializeNodesFunction initializeNodesFunction()
{
    return nullptr;
};
