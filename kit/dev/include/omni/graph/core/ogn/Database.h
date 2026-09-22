// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/InterfaceUtils.h>
#include <omni/fabric/IToken.h>
#include <carb/logging/Log.h>

#include <omni/graph/core/IAttributeType.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/StringUtils.h>
#include <omni/graph/core/ogn/RuntimeAttribute.h>
#include <omni/graph/core/ogn/SimpleRuntimeAttribute.h>
using omni::fabric::IToken;

// =================================================================================================================
// This file contains simple interface classes which wrap data in the OGN database for easier use.
//
//    OmniGraphDatabase  Base class for generated node database classes. Provides common functionality.
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

// Helper definitions for hardcoded metadata names.
// These should match the Python constants in the MetadataKey object found in the file
// source/extensions/omni.graph.tools/python/node_generator/keys.py
#define kOgnMetadataAllowMultiInputs "allowMultiInputs"
#define kOgnMetadataAllowedTokens "allowedTokens"
#define kOgnMetadataAllowedTokensRaw "__allowedTokens"
#define kOgnMetadataCategories "__categories"
#define kOgnMetadataCategoryDescriptions "__categoryDescriptions"
#define kOgnMetadataCudaPointers "__cudaPointers"
#define kOgnMetadataDefault "__default"
#define kOgnMetadataDescription "__description"
#define kOgnMetadataExclusions "__exclusions"
#define kOgnMetadataExtension "__extension"
#define kOgnMetadataHidden "hidden"
#define kOgnMetadataIconBackgroundColor "__iconBackgroundColor"
#define kOgnMetadataIconBorderColor "__iconBorderColor"
#define kOgnMetadataIconColor "__iconColor"
#define kOgnMetadataIconPath "__icon"
#define kOgnMetadataInternal "internal"
#define kOgnMetadataLanguage "__language"
#define kOgnMetadataMemoryType "__memoryType"
#define kOgnMetadataObjectId "__objectId"
#define kOgnMetadataOptional "__optional"
#define kOgnMetadataOutputOnly "outputOnly"
#define kOgnMetadataLiteralOnly "literalOnly"
#define kOgnMetadataTags "tags"
#define kOgnMetadataTokens "__tokens"
#define kOgnMetadataUiName "uiName"
#define kOgnMetadataUiType "uiType"
#define kOgnSingletonName "singleton"


namespace omni {
namespace graph {
namespace core {

class Node;

namespace ogn {
// The following type aliases are internal and are meant to be used as opaque types.
// The underlying type definition can change in future releases.
/** Type of accessor returned for simple input attributes */
using InputAttribute = ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu>;
/** Type of accessor returned for simple output attributes */
using OutputAttribute = ogn::RuntimeAttribute<ogn::kOgnOutput, ogn::kCpu>;
/** Type of accessor returned for simple state attributes */
using VariableAttribute = RuntimeAttribute<ogn::kOgnState, ogn::kCpu>;
/** Type of accessor returned for simple dynamic input attributes */
using DynamicInput = ogn::SimpleInput<const InputAttribute, ogn::kCpu>;
/** Type of accessor returned for simple dynamic output attributes */
using DynamicOutput = ogn::SimpleOutput<OutputAttribute, ogn::kCpu>;
/** Type of accessor returned for simple dynamic state attributes */
using DynamicState = ogn::SimpleState<VariableAttribute, ogn::kCpu>;

// ======================================================================
/**
 * Class defining the minimal amount of shared interface for the generated database interface classes.
 * This class should never be instatiated directly as it is not safe across ABI boundaries. Instead,
 * templated classes will derive from it to create new classes that live entirely on the plugin's side.
 * The template parameter NodeClassType is the node implementation class that makes use of the database.
 * This was necessary to avoid circular dependencies.
 */
class OmniGraphDatabase
{
protected:
    GraphContextObj const* m_graphContextHandles{ nullptr }; //!< ABI object referencing the OmniGraph
    NodeObj const* m_nodeHandles{ nullptr };  //!< List of node handles per-instance
    InstanceIndex m_offset{ 0 };//!< Instance offset in vectorized context
    size_t m_handleCounts{ 0 };  //!< Number of handles in m_nodeHandles

    /**
     * @brief Common constructor for a node's database
     *
     * @param[in] graphContexts List of ABI objects referencing the graphs in which the node lives
     * @param[in] nodeObjects List of ABI objects referencing the instanced nodes to which this database belongs
     * @param[in] handleCount Number of node instances in @p nodeObjects
     */
    void _ctor(GraphContextObj const* graphContexts, NodeObj const* nodeObjects, size_t handleCount)
    {
        m_graphContextHandles = graphContexts;
        m_nodeHandles = nodeObjects;
        m_handleCounts = handleCount;
    }

    /**
     * @brief Simple construction passthrough to _ctor for backward compatibility
     */
    OmniGraphDatabase(GraphContextObj const* graphContexts, NodeObj const* nodeObjects, size_t handleCount)
    { _ctor(graphContexts, nodeObjects, handleCount); }

    /**
     * @brief Default constructor for a node's database
     */
    OmniGraphDatabase() = default;

public:

    /**
     * @brief Get the attribute Type from the OGN type name
     *
     * @param[in] typeNameToken Token with the string representation of the attribute type used by OGN
     * @returns Attribute type corresponding to the type name, invalid if the type name could not be parsed
     */
    Type typeFromName(NameToken typeNameToken) const
    {
        auto typeInterface = carb::getCachedInterface<omni::graph::core::IAttributeType>();
        if (!typeInterface)
        {
            CARB_LOG_ERROR_ONCE("Could not acquire the IAttributeType interface");
            return {};
        }
        auto typeName = tokenToString(typeNameToken);
        return typeInterface->typeFromOgnTypeName(typeName);
    }

    /**
     * @brief Access the token interface to convert a string to a token, for dealing with unique managed strings
     *
     * @param[in] tokenName Name of the string representing a token
     * @return Token corresponding to the unique string (for fast comparison)
     */
    NameToken stringToToken(const char* tokenName) const
    {
        auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
        if (!tokenInterface)
        {
            CARB_LOG_ERROR_ONCE("Failed to initialize node type - no token interface");
            return omni::fabric::kUninitializedToken;
        }
        return tokenInterface->getHandle(tokenName);
    }

    /**
     * @brief Access the token interface to convert a token to a string, for dealing with unique managed strings
     *
     * @param[in] token Name of the token representing a unique string
     * @return String corresponding to the token
     */
    const char* tokenToString(NameToken token) const
    {
        auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
        if (!tokenInterface)
        {
            CARB_LOG_ERROR_ONCE("Failed to initialize node type - no token interface");
            return nullptr;
        }
        return tokenInterface->getText(token);
    }

    /**
     * @brief Access the path interface to convert a string to a path
     *
     * @param[in] pathString Name of the string representing a token
     * @return Path corresponding to the string
     */
    TargetPath stringToPath(const char* pathString) const
    {
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
        if (!pathInterface)
        {
            CARB_LOG_ERROR_ONCE("Failed to initialize node type - no path interface");
            return omni::fabric::kUninitializedPath;
        }
        return pathInterface->getHandle(pathString);
    }

    /**
     * @brief Access the path interface to convert a path to a string
     *
     * @param[in] path Input path
     * @return String corresponding to the path
     */
    const char* pathToString(const TargetPath path) const
    {
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
        if (!pathInterface)
        {
            CARB_LOG_ERROR_ONCE("Failed to initialize node type - no path interface");
            return nullptr;
        }
        return pathInterface->getText(path);
    }

    /**
     * @brief Access the path interface to convert a path to a token
     *
     * @param[in] path Input path
     * @return Token corresponding to the path
     */
    NameToken pathToToken(const TargetPath path) const
    {
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
        auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
        if (!pathInterface || !tokenInterface)
        {
            CARB_LOG_ERROR_ONCE("Failed to initialize node type - no path or token interface");
            return omni::fabric::kUninitializedToken;
        }
        return tokenInterface->getHandle(pathInterface->getText(path));
    }

    /**
     * @brief Access the path interface to convert a token to a path
     *
     * @param[in] pathString Token of the path
     * @return Path corresponding to the token
     */
    TargetPath tokenToPath(const NameToken pathString) const
    {
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
        auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
        if (!pathInterface || !tokenInterface)
        {
            CARB_LOG_ERROR_ONCE("Failed to initialize node type - no path or token interface");
            return omni::fabric::kUninitializedPath;
        }
        return pathInterface->getHandle(tokenInterface->getText(pathString));
    }

    /**
     * @brief Access the raw graph ABI object, for when you have to do something really unusual
     *
     * @return ABI object referencing the graph in which the node lives
     */
    const GraphContextObj& abi_context(InstanceIndex relativeIdx = { 0 }) const
    {
        InstanceIndex idx = m_offset + relativeIdx;
        if (idx.index < m_handleCounts)
            return m_graphContextHandles[idx.index];
        return m_graphContextHandles[0];
    }

    /**
     * @brief Access the raw node ABI object, for when you have to do something really unusual
     *
     * @return ABI object referencing the node to which this database belongs
     */
    const NodeObj& abi_node(InstanceIndex relativeIdx = { 0 }) const
    {
        InstanceIndex idx = m_offset + relativeIdx;
        if (idx.index < m_handleCounts)
            return m_nodeHandles[idx.index];
        return m_nodeHandles[0];
    }

    /**
     * @brief Retrieves the number of instances the owning graph has.
     * Be aware that depending on the context of execution and/or the current offset of the database,
     * that not all of the instances can be accessed.
     * For example:
     *   In a computeVectorized function, always rely on the 'count' parameter that is passed in.
     *   In a compute function, it is not safe to access anything else that the instance currently evaluating
     *
     * @return The number of instances (targets) associated to the graph. 0 if the graph is not instantiated.
     */
    size_t getGraphTotalInstanceCount() const
    {
        NodeObj const& nodeObj = abi_node();
        GraphObj graphObj = nodeObj.iNode->getGraph(nodeObj);
        return graphObj.iGraph->getInstanceCount(graphObj);
    }

    /**
     * @brief Access the user data, cast to the templated type.
     *
     * There is no guarantee that the existing user data is of the requested type - that is up to the
     * caller to ensure.
     *
     * @tparam UserDataType Type of the user data
     * @param[in] relativeIdx Instance index of the node to which the user data applies
     * @return Internal user data that was set elsewhere, cast to the templated type
     */
    template <typename UserDataType>
    UserDataType* userData(InstanceIndex relativeIdx = { 0 }) const
    {
        NodeObj const& obj = abi_node(relativeIdx);
        return reinterpret_cast<UserDataType*>(obj.iNode->getUserData(obj));
    }

    /**
     * @brief Log an evaluation error, warning, or message.
     * Takes a printf-style list of arguments indicating what happened during evaluation and logs the message.
     *
     * @tparam Args... Variable list of printf-like arguments to be formatted
     * @param[in] nodeObj Node reporting the error
     * @param[in] inst The graph instance for which this message should be logged
     * @param[in] sev Severity of the message to report
     * @param[in] fmt Formatting string
     * @param[in] args Variadic template arguments in the same form as printf arguments.
     */
    template <typename... Args>
    static void logMessage(NodeObj const& nodeObj, InstanceIndex inst, Severity sev, const char* fmt, Args&&... args)
    {
        if (sizeof...(args) == 0)
        {
            nodeObj.iNode->logComputeMessageOnInstance(nodeObj, inst, sev, fmt);
        }
        else
        {
            std::string msg = formatString(fmt, args...);
            nodeObj.iNode->logComputeMessageOnInstance(nodeObj, inst, sev, msg.c_str());
        }
    }

    /**
     * @brief Log an evaluation error.
     * Takes a printf-style list of arguments indicating what error during evaluation and logs the message.
     *
     * @tparam Args... Variable list of printf-like arguments to be formatted
     * @param[in] nodeObj Node reporting the error
     * @param[in] fmt Formatting string
     * @param[in] args Variadic template arguments in the same form as printf arguments.
     */
    template <typename... Args>
    static void logError(NodeObj const& nodeObj, const char* fmt, Args&&... args)
    { logMessage(nodeObj, kAccordingToContextIndex, Severity::eError, fmt, args...); }

    /**
     * @brief Log an evaluation error for a specific node instance.
     * Takes a printf-style list of arguments indicating what error during evaluation and logs the message.
     *
     * @tparam Args... Variable list of printf-like arguments to be formatted
     * @param[in] nodeObj Node reporting the error
     * @param[in] inst The graph instance for which this message should be logged
     * @param[in] fmt Formatting string
     * @param[in] args Variadic template arguments in the same form as printf arguments.
     */
    template <typename... Args>
    static void logError(NodeObj const& nodeObj, InstanceIndex inst, const char* fmt, Args&&... args)
    { logMessage(nodeObj, inst, Severity::eError, fmt, args...); }

    /**
     * @brief Log an evaluation warning.
     * Takes a printf-style list of arguments indicating what warning during evaluation and logs the message.
     *
     * @tparam Args... Variable list of printf-like arguments to be formatted
     * @param[in] nodeObj Node reporting the warning
     * @param[in] fmt Formatting string
     * @param[in] args Variadic template arguments in the same form as printf arguments.
     */
    template <typename... Args>
    static void logWarning(NodeObj const& nodeObj, const char* fmt, Args&&... args)
    { logMessage(nodeObj, kAccordingToContextIndex, Severity::eWarning, fmt, args...); }

    /**
     * @brief Log an evaluation warning for a specific node instance.
     * Takes a printf-style list of arguments indicating what warning during evaluation and logs the message.
     *
     * @tparam Args... Variable list of printf-like arguments to be formatted
     * @param[in] nodeObj Node reporting the warning
     * @param[in] inst The graph instance for which this message should be logged
     * @param[in] fmt Formatting string
     * @param[in] args Variadic template arguments in the same form as printf arguments.
     */
    template <typename... Args>
    static void logWarning(NodeObj const& nodeObj, InstanceIndex inst, const char* fmt, Args&&... args)
    { logMessage(nodeObj, inst, Severity::eWarning, fmt, args...); }

    /**
     * @brief Log an error using print-like formatting
     *
     * @tparam Args... Variable list of printf-like arguments to be formatted
     * @param[in] fmt Printf-like formatting string
     * @param[in] args Variable list of printf-like arguments to be formatted
     */
    template <typename... Args>
    void logError(const char* fmt, Args&&... args) { logError(abi_node(), m_offset, fmt, args...); }

    /**
     * @brief Log an error for a specific node instance using print-like formatting
     *
     * @tparam Args... Variable list of printf-like arguments to be formatted
     * @param[in] relativeIdx The graph instance for which this message should be logged
     * @param[in] fmt Printf-like formatting string
     * @param[in] args Variable list of printf-like arguments to be formatted
     */
    template <typename... Args>
    void logError(InstanceIndex relativeIdx, const char* fmt, Args&&... args) { logError(abi_node(relativeIdx), m_offset + relativeIdx, fmt, args...); }

    /**
     * @brief Log a warning using print-like formatting
     *
     * @tparam Args... Variable list of printf-like arguments to be formatted
     * @param[in] fmt Printf-like formatting string
     * @param[in] args Variable list of printf-like arguments to be formatted
     */
    template <typename... Args>
    void logWarning(const char* fmt, Args&&... args) { logWarning(abi_node(), m_offset, fmt, args...); }

    /**
     * @brief Log a warning for a specific node instance using print-like formatting
     *
     * @tparam Args... Variable list of printf-like arguments to be formatted
     * @param[in] relativeIdx The graph instance for which this message should be logged
     * @param[in] fmt Printf-like formatting string
     * @param[in] args Variable list of printf-like arguments to be formatted
     */
    template <typename... Args>
    void logWarning(InstanceIndex relativeIdx, const char* fmt, Args&&... args) { logWarning(abi_node(relativeIdx), m_offset + relativeIdx, fmt, args...); }

    /**
     * Retrieves an attribute representing the value of a variable. If the variable
     * with the given name does not exist in the graph, an invalid attribute is returned.
     *
     * @param[in] token: A token representing the variable name
     * @param[in] relativeIdx: The instance index/offset relative to the one currently pointed by the database
     * @return An attribute that allows access to the variable data.
     */
    VariableAttribute getVariable(NameToken token, InstanceIndex relativeIdx = { 0 })
    {
        return getVariable(tokenToString(token), relativeIdx);
    }

    /**
     * Retrieves an attribute representing the value of a variable. If the variable
     * with the given name does not exist in the graph, an invalid attribute is returned.
     *
     * @param[in] variableName: A string indicating the variable name
     * @param[in] relativeIdx: The instance index/offset relative to the one currently pointed by the database
     * @return An attribute that allows access to the variable data.
     */
    VariableAttribute getVariable(const char* variableName, InstanceIndex relativeIdx = { 0 })
    {
        NodeObj const& obj = abi_node(relativeIdx);
        GraphContextObj const& ctx = abi_context(relativeIdx);
        auto graphObj = obj.iNode->getGraph(obj);
        auto variable = graphObj.iGraph->findVariable(graphObj, variableName);
        if (!variable)
            return VariableAttribute();
        auto handle = ctx.iContext->getVariableDataHandle(ctx, variable, m_offset + relativeIdx);
        return VariableAttribute(ctx, handle);
    }

    /**
     * Retrieves the target of the executing graph.
     *
     * @param[in] relativeIdx: The instance index/offset relative to the one currently pointed by the database
     * @return A token representing the prim path of the graph target
     */
    NameToken getGraphTarget(InstanceIndex relativeIdx = { 0 }) const
    {
        GraphContextObj const& ctx = abi_context(relativeIdx);
        return ctx.iContext->getGraphTarget(ctx, relativeIdx+m_offset);
    }

    /**
     * Retrieves the targets of the executing graph.
     *
     * @param[in] count: The number of instances available for vectorized access
     * @return A span of token representing the prims path of the graph targets
     */
    gsl::span<NameToken const> getGraphTargets(size_t count) const
    {
        GraphContextObj const& ctx = abi_context();
        return { &ctx.iContext->getGraphTarget(ctx, m_offset), count };
    }

    /**
     * Retrieves the target of the executing graph.
     *
     * @param[in] relativeIdx: The instance index/offset relative to the one currently pointed by the database
     * @return A path representing the prim path of the graph target
     */
    TargetPath getGraphTargetAsPath(InstanceIndex relativeIdx = { 0 }) const
    {
        GraphContextObj const& ctx = abi_context(relativeIdx);
        return ctx.iContext->getGraphTargetAsPath(ctx, relativeIdx + m_offset);
    }

    /**
     * Retrieves the targets of the executing graph.
     *
     * @param[in] count: The number of instances available for vectorized access
     * @return A span of token representing the prims path of the graph targets
     */
    gsl::span<TargetPath const> getGraphTargetsAsPath(size_t count) const
    {
        GraphContextObj const& ctx = abi_context();
        return { &ctx.iContext->getGraphTargetAsPath(ctx, m_offset), count };
    }


    /**
     * Move to next instance in a vectorized context.
     *
     */
    inline void moveToNextInstance()
    {
        ++m_offset.index;
    }
    /**
     * Move to next instance in a vectorized context.
     *
     */
    inline void resetToFirstInstance()
    {
        m_offset = { 0 };
    }

    /**
     * Get the current instance index, relative to the the one pointed by the context
     *
     */
    inline const InstanceIndex& getInstanceIndex() const
    {
        return m_offset;
    }

protected:

    /**
     * Gets the dynamic attributes of the specified type, if any are registered with the node.
     *
     * @param[in] staticAttributeCount: The number of attributes that are statically defined in the ogn node definition.
     * @param[out] dynamicAttributes: The buffer for the collected dynamic attributes.
     * @return Returns true if any dynamic attributes of the requested type are found, otherwise returns false.
     */
    template <AttributePortType portType, typename TAttribute>
    bool tryGetDynamicAttributes(size_t staticAttributeCount, std::vector<TAttribute>& dynamicAttributes)
    {
        NodeObj const& obj = abi_node();
        GraphContextObj const& ctx = abi_context();
        auto totalAttributeCount = obj.iNode->getAttributeCount(obj);
        if (totalAttributeCount > staticAttributeCount)
        {
            dynamicAttributes.reserve(totalAttributeCount - staticAttributeCount);
            std::vector<AttributeObj> allAttributes(totalAttributeCount);
            obj.iNode->getAttributes(obj, allAttributes.data(), totalAttributeCount);

            bool foundAny = false;
            for (auto const& __a : allAttributes)
            {
                if (__a.iAttribute->isDynamic(__a) && __a.iAttribute->getPortType(__a) == portType)
                {
                    foundAny = true;
                    auto __h = __a.iAttribute->getAttributeDataHandle(__a, kAccordingToContextIndex);
                    dynamicAttributes.emplace_back(m_offset.index);
                    dynamicAttributes.back()().reset(ctx, __h, __a);
                }
            }

            return foundAny;
        }

        return false;
    }

    /**
     * @brief Populate an array of dynamic attributes from the node
     *
     * @tparam portType Port type from which the dynamic attributes will be pulled
     * @param staticAttributeCount Number of static attributes on the node
     * @param dynamicAttributes Array of dynamic attributes, to be populated on return
     * @return true Dynamic attributes were found and populated
     * @return false No dynamic attributes were found
     */
    template <AttributePortType portType>
    bool tryGetDynamicAttributes(size_t staticAttributeCount, std::vector<DynamicInput>& dynamicAttributes)
    {
        NodeObj const& obj = abi_node();
        GraphContextObj const& ctx = abi_context();
        auto totalAttributeCount = obj.iNode->getAttributeCount(obj);
        if (totalAttributeCount > staticAttributeCount)
        {
            dynamicAttributes.reserve(totalAttributeCount - staticAttributeCount);
            std::vector<AttributeObj> allAttributes(totalAttributeCount);
            obj.iNode->getAttributes(obj, allAttributes.data(), totalAttributeCount);

            bool foundAny = false;
            for (auto const& __a : allAttributes)
            {
                if (__a.iAttribute->isDynamic(__a) &&
                    __a.iAttribute->getPortType(__a) == portType)
                {
                    foundAny = true;
                    auto __h = __a.iAttribute->getAttributeDataHandle(__a, kAccordingToContextIndex);
                    dynamicAttributes.emplace_back(m_offset.index);
                    const_cast<typename std::remove_const_t<ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu>&>>(dynamicAttributes.back()())
                        .reset(ctx, __h, __a);
                }
            }

            return foundAny;
        }

        return false;
    }

    /**
     * Updates the node database when a dynamic attribute is created.
     *
     * @tparam TAttribute The type of the dynamic attribute that was created (DynamicInput/DynamicOutput/DynamicState)
     * @param[out] dynamicAttributes: The dynamic attributes buffer.
     * @param[in] attribute: The newly created attribute.
     */
    template<typename TAttribute>
    void onDynamicAttributeCreated(std::vector<TAttribute>& dynamicAttributes, AttributeObj const& attribute)
    {
        auto handle = attribute.iAttribute->getAttributeDataHandle(attribute, kAccordingToContextIndex);
        dynamicAttributes.emplace_back(m_offset.index);
        dynamicAttributes.back()().reset(abi_context(), handle, attribute);
    }

    /**
     * Updates the node database when a dynamic input is created.
     *
     * @param[out] dynamicInputs: The dynamic attributes buffer.
     * @param[in] attribute: The newly created attribute.
     */
    void onDynamicInputsCreated(std::vector<DynamicInput>& dynamicInputs, AttributeObj const& attribute)
    {
        auto handle = attribute.iAttribute->getAttributeDataHandle(attribute, kAccordingToContextIndex);
        dynamicInputs.emplace_back(m_offset.index);
        const_cast<typename std::remove_const_t<ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu>&>>(
            dynamicInputs.back()())
            .reset(abi_context(), handle, attribute);
    }

    /**
     * Updates the node database when a dynamic attribute is removed.
     *
     * @tparam TAttribute The type of the dynamic attribute that was created (DynamicInput/DynamicOutput/DynamicState)
     * @param[out] dynamicAttributes: The dynamic attributes buffer.
     * @param[in] attribute: The dynamic attribute about to be removed.
     */
    template<typename TAttribute>
    void onDynamicAttributeRemoved(std::vector<TAttribute>& dynamicAttributes, AttributeObj const& attribute)
    {
        auto const attrName = attribute.iAttribute->getNameToken(attribute);
        for (auto it = dynamicAttributes.begin(); it != dynamicAttributes.end(); ++it)
        {
            if ((*it)().name() == attrName)
            {
                dynamicAttributes.erase(it);
                return;
            }
        }
    }

    /**
     * Updates the node database when a dynamic attribute is created or removed.
     *
     * @param[out] inputs: The buffer of input dynamic attributes.
     * @param[out] outputs: The buffer of output dynamic attributes.
     * @param[out] states: The buffer of state dynamic attributes.
     * @param[in] attribute: The attribute added or removed.
     * @param[in] isAttributeCreated: If true, the input attribute is newly created, otherwise it will be removed.
     */
    void onDynamicAttributeCreatedOrRemoved(std::vector<DynamicInput>& inputs,
                                            std::vector<DynamicOutput>& outputs,
                                            std::vector<DynamicState>& states,
                                            AttributeObj const& attribute,
                                            bool isAttributeCreated)
    {
        if (! attribute.iAttribute) return;
        switch (attribute.iAttribute->getPortType(attribute))
        {
        case AttributePortType::kAttributePortType_Input:
        {
            if (isAttributeCreated)
            {
                onDynamicInputsCreated(inputs, attribute);
            }
            else
            {
                onDynamicAttributeRemoved(inputs, attribute);
            }
            break;
        }
        case AttributePortType::kAttributePortType_Output:
        {
            if (isAttributeCreated)
            {
                onDynamicAttributeCreated(outputs, attribute);
            }
            else
            {
                onDynamicAttributeRemoved(outputs, attribute);
            }
            break;
        }
        case AttributePortType::kAttributePortType_State:
        {
            if (isAttributeCreated)
            {
                onDynamicAttributeCreated(states, attribute);
            }
            else
            {
                onDynamicAttributeRemoved(states, attribute);
            }
            break;
        }
        default:
            break;
        }
    }

    /**
     * Called at database initialization to collect all attributes that are mapped.
     *
     * @param[out] mappedAttributes: The buffer of mapped attributes.
     */
    void collectMappedAttributes(std::vector<NameToken>& mappedAttributes)
    {
        NodeObj const& obj = abi_node();
        auto totalAttributeCount = obj.iNode->getAttributeCount(obj);
        std::vector<AttributeObj> allAttributes(totalAttributeCount);
        obj.iNode->getAttributes(obj, allAttributes.data(), totalAttributeCount);
        for (auto const& __a : allAttributes)
        {
            NameToken mapping = __a.iAttribute->getTargetMapping(__a);
            if (mapping != fabric::kUninitializedToken)
                mappedAttributes.push_back(__a.iAttribute->getNameToken(__a));
        }
        //keep sorted
        std::sort(mappedAttributes.begin(), mappedAttributes.end());
    }

    /**
     * Called by the database in order to update its mapped attribute array
     * when one of its attribute has changed its mapping state.
     *
     * @param[in/out] mappedAttributes: The buffer of mapped attributes.
     * @param[out] attr: The attribute that has changed its mapping "state"
     */
    void updateMappedAttributes(std::vector<NameToken>& mappedAttributes, AttributeObj const& attr)
    {
        bool const isMapped = attr.iAttribute->getTargetMapping(attr) != fabric::kUninitializedToken;
        NameToken const token = attr.iAttribute->getNameToken(attr);
        if (isMapped)
        {
            //might be a change of mapping, make sure it is not already here
            auto found = std::lower_bound(mappedAttributes.begin(), mappedAttributes.end(), token);
            if (found == mappedAttributes.end() || *found != token)
                mappedAttributes.insert(found, token);
        }
        else
        {
            // not mapped anymore: remove from list
            auto found = std::lower_bound(mappedAttributes.begin(), mappedAttributes.end(), token);
            if (found != mappedAttributes.end() && *found == token)
                mappedAttributes.erase(found);
        }
    }

    /**
     * Called by the auto-generated databases classes to validate that it
     * is safe for a node to have compute or computeVectorized called on it.
     */
    bool validateNode() const
    {
        NodeObj const& nodeObj = abi_node();
        return nodeObj.iNode->validateCompute(nodeObj);
    }
};

/**
 * Creates an input RuntimeAttribute from an output RuntimeAttribute.
 *
 * When nodes have to chain the result of multiple computations, for example when
 * accumulating a value in a loop, it is often necessary to treat the output attribute
 * as an input in the next iteration of the loop. Because the runtime attributes are strongly typed
 * and different depending if they are inputs or outputs, they cannot be used interchangeably as arguments
 * to functions which compute one iteration of a computation.
 *
 * This helper function creates an input RuntimeAttribute from the same handle as the original output attribute.
 * The raw data pointer of the original attribute and the newly constructed input attribute are the same.
 *
 * @tparam MemoryType The location of the memory expected for the attribute
 * @param[in] db: The node database.
 * @param[in] output: The original output RuntimeAttribute.
 * @param[in] outputToken: The original output RuntimeAttribute name token.
 *
 * @return Returns a RuntimeAttribute with the template type ogn::kOgnInput and the same handle as the original output attribute.
 */
template <eMemoryType MemoryType>
static inline ogn::RuntimeAttribute<ogn::kOgnInput, MemoryType> constructInputFromOutput(
    OmniGraphDatabase const& db,
    ogn::RuntimeAttribute<ogn::kOgnOutput, MemoryType> const& output,
    NameToken outputToken)
{
    auto const& nodeObj = db.abi_node();
    auto const& context = db.abi_context();
    auto const& resultAttribute = nodeObj.iNode->getAttributeByToken(nodeObj, outputToken);
    auto handle = resultAttribute.iAttribute->getConstAttributeDataHandle(resultAttribute, db.getInstanceIndex());

    return ogn::RuntimeAttribute<ogn::kOgnInput, MemoryType>(context, handle, output.type());
}

} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
