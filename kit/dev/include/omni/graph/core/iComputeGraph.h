// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/events/IEvents.h>
#include <carb/Defines.h>
#include <carb/Interface.h>
#include <omni/fabric/IToken.h>

#include <omni/graph/core/Type.h>
#include <omni/graph/core/Handle.h>
#include <omni/graph/core/Enums.h>
#include <omni/graph/core/ISchedulingHints2.h>
#include <omni/graph/core/ogn/Types.h>
#include <omni/graph/core/IVariable3.h>
#include <omni/graph/core/iAttributeData.h>
#include <omni/graph/core/IPrimView.h>
#include <omni/graph/core/INodeType.h>
#include <omni/graph/exec/unstable/Stamp.h>
#include <omni/graph/core/bundle/IBundle1.h>
#include <omni/inspect/IInspector.h>

#include <cstddef>

// Interfaces pulled out of this file but which are still referenced through it
#include "IGraphRegistry.h"

#ifdef __CUDA_ARCH__
#error iComputeGraph.h cannot be included from a .cu file due to a compiler problem. You probably want Handle.h.
#endif

namespace omni
{
namespace graph
{
namespace core
{

//! If 1 then extra logging is enabled (which affects performance)
#define COMPUTE_GRAPH_VERBOSE_LOGGING 0

// ==============================================================================================================
/** Encapsulates the information required to define a file format version number */
struct FileFormatVersion
{
    int majorVersion;  //!< Major version, for which changes mean incompatible formats
    int minorVersion;  //!< Minor version, for which changes mean compatible formats, possibly with auto-upgrades

    /**
     * @brief Equality operator for the file format version object
     *
     * @param rhs Version number to compare against
     * @return true The version number is not equal to @p rhs
     * @return false The version number is equal to @p rhs
     */
    bool operator==(const FileFormatVersion& rhs) const
    {
        return rhs.majorVersion == majorVersion && rhs.minorVersion == minorVersion;
    }

    /**
     * @brief Inequality operator for the file format version object
     *
     * @param rhs Version number to compare against
     * @return true The version number is not equal to @p rhs
     * @return false The version number is equal to @p rhs
     */
    bool operator!=(const FileFormatVersion& rhs) const
    {
        return !(*this==rhs);
    }

    /**
     * @brief Less-than operator for the file format version object
     *
     * @param rhs Version number to compare against
     * @return true The version number is less than @p rhs
     * @return false The version number is greater than or equal to @p rhs
     */
    bool operator<(const FileFormatVersion& rhs) const
    {
        return majorVersion < rhs.majorVersion || ((majorVersion == rhs.majorVersion) && (minorVersion < rhs.minorVersion));
    }

    /**
     * @brief Greater-than operator for the file format version object
     *
     * @param rhs Version number to compare against
     * @return true The version number is greater than @p rhs
     * @return false The version number is less than or equal to @p rhs
     */
    bool operator>(const FileFormatVersion& rhs) const
    {
        return majorVersion > rhs.majorVersion || ((majorVersion == rhs.majorVersion) && (minorVersion > rhs.minorVersion));
    }

    /**
     * @brief Greater-than or equal operator for the file format version object
     *
     * @param rhs Version number to compare against
     * @return true The version number is greater than or equal than @p rhs
     * @return false The version number is less than to @p rhs
     */
    bool operator>=(const FileFormatVersion& rhs) const
    {
        return !(*this < rhs);
    }

    /**
     * @brief Less-than or equal operator for the file format version object
     *
     * @param rhs Version number to compare against
     * @return true The version number is less than or equal than @p rhs
     * @return false The version number is greater than to @p rhs
     */
    bool operator<=(const FileFormatVersion& rhs) const
    {
        return !(*this > rhs);
    }
};

struct GraphObj;

// ==============================================================================================================
/** Callback object to instantiate for use as a callback when an older version of an OmniGraph file is read */
struct FileFormatUpgrade
{
    /**
     * Callback function definition. Parameters are
     *
     *   - oldVersion Version of the file being read
     *   - newVersion Current version of the file format
     *   - userData User data to pass to the callback
     */
    void(*fileFormatUpgradeCallback)(const FileFormatVersion& oldVersion,
                                     const FileFormatVersion& newVersion,
                                     GraphObj& graphObj,
                                     void* userData);

    /** User data to pass to the callback function */
    void* userData;

    /**
     * @brief Equality operator for the file format upgrade callback object
     *
     * @param rhs Callback object to compare against
     * @return true The callback object is equal to @p rhs
     * @return false The callback object is not equal to @p rhs
     */
    bool operator==(const FileFormatUpgrade& rhs) const
    {
        return rhs.fileFormatUpgradeCallback == fileFormatUpgradeCallback &&
               rhs.userData == userData;
    }

    /**
     * @brief Inequality operator for the file format upgrade callback object
     *
     * @param rhs Callback object to compare against
     * @return true The callback object is not equal to @p rhs
     * @return false The callback object is equal to @p rhs
     */
    bool operator!=(const FileFormatUpgrade& rhs) const
    {
        return !(*this == rhs);
    }
};

// ==============================================================================================================
/**
 * @brief Encapsulation of a callback that happens when a node's error status changes
 *
 */
struct ErrorStatusChangeCallback
{
    /**
     * Callback function definition. Parameters are
     *
     *   - nodeList List of nodes whose error status changed since the last compute
     *   - graphObj Graph to which the nodes belong
     *   - userData User data to pass to the callback
     */
    void (*errorStatusChangeCallback)(const std::vector<NodeObj>& nodeList, GraphObj& graphObj, void* userData);
    /** User data to pass to the callback function */
    void* userData;

    /**
     * @brief Equality operator for the error status change callback object
     *
     * @param rhs Callback object to compare against
     * @return true The callback object is equal to @p rhs
     * @return false The callback object is not equal to @p rhs
     */
    bool operator==(const ErrorStatusChangeCallback& rhs) const
    {
        return rhs.errorStatusChangeCallback == errorStatusChangeCallback &&
               rhs.userData == userData;
    }

    /**
     * @brief Inequality operator for the error status change callback object
     *
     * @param rhs Callback object to compare against
     * @return true The callback object is not equal to @p rhs
     * @return false The callback object is equal to @p rhs
     */
    bool operator!=(const ErrorStatusChangeCallback& rhs) const
    {
        return !(*this == rhs);
    }
};

// ==============================================================================================================
/** Information passed to define the opposite end of a connection */
struct ConnectionInfo
{
    AttributeObj attrObj;  //!< Attribute at the opposite end
    ConnectionType connectionType;  //!< Type of connection being made
};

// ==============================================================================================================
/** Callback object used when a connection is made or broken between two attributes */
struct ConnectionCallback
{
    /**
     * Callback function definition. Parameters are
     *
     *   - srcAttr Source end of the connection that changed
     *   - dstAttr Destination end of the connection that changed
     *   - userData User data to pass to the callback
     */
    void(*connectionCallback)(const AttributeObj& srcAttr, const AttributeObj& dstAttr, void* userData);

    /** User data to pass to the callback function */
    void* userData;

    /**
     * @brief Equality operator for the connection/disconnection callback object
     *
     * @param rhs Callback object to compare against
     * @return true The callback object is equal to @p rhs
     * @return false The callback object is not equal to @p rhs
     */
    bool operator==(const ConnectionCallback& rhs) const
    {
        return rhs.connectionCallback == connectionCallback &&
            rhs.userData == userData;
    }

    /**
     * @brief Inequality operator for the connection/disconnection callback object
     *
     * @param rhs Callback object to compare against
     * @return true The callback object is not equal to @p rhs
     * @return false The callback object is equal to @p rhs
     */
    bool operator!=(const ConnectionCallback& rhs) const
    {
        return !(*this == rhs);
    }
};

// ==============================================================================================================
/** Callback object used when a path has changed, requiring a path attribute update */
struct PathChangedCallback
{
    /**
     * Callback function definition. Parameters are
     *
     *   - paths Array of paths that have changed
     *   - numPaths Number of paths in the array
     *   - userData User data to pass to the callback
     */
    void(*pathChangedCallback)(const omni::fabric::PathC* paths, const size_t numPaths, void* userData);

    /** User data to pass to the callback function */
    void* userData;

    /**
     * @brief Equality operator for the path change callback object
     *
     * @param rhs Callback object to compare against
     * @return true The callback object is equal to @p rhs
     * @return false The callback object is not equal to @p rhs
     */
    bool operator==(const PathChangedCallback& rhs) const
    {
        return rhs.pathChangedCallback == pathChangedCallback &&
            rhs.userData == userData;
    }

    /**
     * @brief Inequality operator for the path change callback object
     *
     * @param rhs Callback object to compare against
     * @return true The callback object is not equal to @p rhs
     * @return false The callback object is equal to @p rhs
     */
    bool operator!=(const PathChangedCallback& rhs) const
    {
        return !(*this == rhs);
    }
};


namespace ogn
{
    class OmniGraphDatabase;
}
/**
 * A callback allocate, initialize, and returns an OGN database for a given node
 */
using CreateDbFunc = ogn::OmniGraphDatabase* (*)(GraphContextObj const*, NodeObj const*, size_t);


/**
 * Parameters for IGraph::CreateGraphAsNode
 */
struct CreateGraphAsNodeOptions
{
    static constexpr uint8_t kCurrentVersion = 2;  //!< Version number of this structure

    // VERSION 1 //

    //! The version of this structure.
    const uint8_t version{ CreateGraphAsNodeOptions::kCurrentVersion };

    //! The name of the node that wraps the graph
    const char* nodeName{ "" };

    //! The path to where the graph that the node will wrap will be added
    const char* graphPath{ "" };

    //! The evaluator to use for the new graph
    const char* evaluatorName{ "" };

    //! Whether this graph is a top level global graph
    bool isGlobalGraph{ true };

    //! Whether to back this graph by USD
    bool backByUSD{ true };

    //! What kind of FC backs this graph
    GraphBackingType backingType{ kGraphBackingType_FabricShared };

    //! What pipeline stage this graph occupies
    GraphPipelineStage pipelineStage{ kGraphPipelineStage_Simulation };

    //! The evaluation mode for the graph
    GraphEvaluationMode evaluationMode{ GraphEvaluationMode::Automatic };

    // VERSION 2 //

    //! Whether or not the graph is allowed to be auto instanced
    bool allowAutoInstancing{ true };
};


/**
 * @brief Possible values to be set for Attributes of type "execution"
 * @private Deprecated. See omni::graph::action::IActionGraph.
 */
enum ExecutionAttributeState : uint32_t
{
    kExecutionAttributeStateDisabled, //!< Output attribute connection is disabled
    kExecutionAttributeStateEnabled, //!< Output attribute connection is enabled
    //! Output attribute connection is enabled and the node is pushed to the evaluation stack
    kExecutionAttributeStateEnabledAndPush,
    //! Push this node as a latent event for the current entry point
    kExecutionAttributeStateLatentPush,
    // Output attribute connection is enabled and the latent state is finished for this node
    kExecutionAttributeStateLatentFinish
};

/**
 * Deprecated, do not use.
 */
#define RESOLVED_ATTRIBUTE_PREFIX ""

/**
 * The path used to identify the targeted prim, when graph instancing is used. At runtime this token will be
 * replaced with the absolute path to the targeted prim.
*/
static constexpr char kInstancingGraphTargetPath[] = "_OMNI_GRAPH_TARGET";

/**
 * The value of an uninitialized attribute for a type (eg: tuple_count, array_depth)
 */
constexpr uint8_t kUninitializedTypeCount = UINT8_MAX;

/**
 * Temp value representing an instance during a compute or a loop
 */
struct InstanceIndex
{
    /** Returns true if this InstanceIndex is equal to the @p other */
    bool const operator==(InstanceIndex const& other) const
    { return index == other.index; }
    /** Returns true if this InstanceIndex is not equal to the @p other */
    bool const operator!=(InstanceIndex const& other) const
    { return index != other.index; }
    /** Returns true if this InstanceIndex is less than the @p other */
    bool const operator<(InstanceIndex const& other) const
    { return index < other.index; }
    /** Returns true if this InstanceIndex is less than or equal to the @p other */
    bool const operator<=(InstanceIndex const& other) const
    { return index <= other.index; }
    /** Returns true if this InstanceIndex is greater than the @p other */
    bool const operator>(InstanceIndex const& other) const
    { return index > other.index; }
    /** Returns true if this InstanceIndex is greater than or equal to the @p other */
    bool const operator>=(InstanceIndex const& other) const
    { return index >= other.index; }
    /** Returns the sum of this instance index and that of the @p other */
    InstanceIndex operator+(InstanceIndex other) const
    { return { index + other.index }; }
    /** Returns the sum of this instance index and @p idx */
    InstanceIndex operator+(size_t idx) const
    { return { index + idx }; }
    /** Increments the instance index by the index amount contained in @p other */
    InstanceIndex& operator+=(InstanceIndex other)
    { index += other.index; return *this; }
    /** Increments the index value */
    InstanceIndex& operator++()
    { index++; return *this; }

    size_t index{ 0 };  //!< Index value for the instance
};

/**
 * Some default instance value
 */
static constexpr InstanceIndex kAuthoringGraphIndex{ size_t(-1) };  //!< Special index for the authoring graph original
static constexpr InstanceIndex kAccordingToContextIndex{ size_t(-2) };   //!< Special index for a context
static constexpr InstanceIndex kInvalidInstanceIndex{ size_t(-3) };   //!< Special index indicating an invalid instance


// ======================================================================
/** Interface to provide functionality to access and modify properties of an OmniGraph attribute.
 */
struct IAttribute
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::IAttribute", 1, 15);

    /**
     * Returns the name of the attribute
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @return The name of the attribute
     */
    const char*(CARB_ABI* getName)(const AttributeObj& attr);

    /**
     * Returns the type name of the attribute
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @return The type name of the attribute
     */
    const char*(CARB_ABI* getTypeName)(const AttributeObj& attr);

    /**
     * Returns the extended type, if any, of the attribute.  Extended types are things like "union" and
     * "any" types that aren't in the explicit list of types in USD.  kExtendedAttributeType_Regular
     * means that the attribute is not one of these extended types.
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @return The extended type of the attribute
     */
    ExtendedAttributeType(CARB_ABI* getExtendedType)(const AttributeObj& attr);

    /**
     * Returns the resolved type an extended type like union actually turns out to be, by
     * inferring it from the connection. If the type is still not resolved, the BaseDataType of
     * the returned type will have eNone as its value.
     *
     * If the attribute type is just a Regular one then this method will return its permanent type.
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @return The resolved type of the attribute, based on the connection
     */
    Type(CARB_ABI* getResolvedType)(const AttributeObj& attr);

    /**
     * Returns whether the attribute is an array
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @return Whether or not the attribute is an array
     */
    bool(CARB_ABI* isArray)(const AttributeObj& attr);

    /**
     * Connects an attribute using a relationship to some other prim.  This could be for a bundle connection
     * or a pure relationship to a prim.  In the case of a pure relationship to a prim, some meta-data will
     * be added to mark the relationship as not being used for a bundle
     *
     * @param[in] attrObj The attr that represents the relationship
     * @param[in] pathToPrim The path to the prim to connect to
     * @param[in] modifyInUsd Whether the connection is also modified in the underlying USD representation
     * @param[in] isBundleConnection Whether the connection is to be used for bundles or just a pure relationship to a prim
     * @return true if connection is successful, false otherwise
     */
    bool(CARB_ABI* connectPrim)(const AttributeObj& attrObj, const char* pathToPrim, bool modifyInUsd, bool isBundleConnection);

    /**
     * Disconnects an attribute using a relationship to some other prim.  This could be for a bundle connection
     * or a pure relationship to a prim.
     *
     * @param[in] attrObj The attr that represents the relationship
     * @param[in] pathToPrim The path to the prim to disconnect
     * @param[in] modifyInUsd Whether the connection is also modified in the underlying USD representation
     * @param[in] isBundleConnection Whether the connection is to be used for bundles or just a pure relationship to a prim
     * @return true if disconnection is successful, false otherwise
     */
    bool(CARB_ABI* disconnectPrim)(const AttributeObj& attrObj, const char* pathToPrim, bool modifyInUsd, bool isBundleConnection);

    /**
     * Connects two attributes together to add an edge to the graph.  This is a legacy version of the
     * connection API.  Calling this is equivalent to setting kConnectionType_Regular type connections.
     * Please use connectAttrsEx to have fuller control over the kind of connections created.
     *
     * @param[in] srcAttr The attr that is the source of the directed connection
     * @param[in] destAttr The attr that is the destination of the directed connection
     * @param[in] modifyInUsd Whether the connection is also modified in the underlying USD representation
     * @return true if connection is successful, false otherwise
     */
    bool(CARB_ABI* connectAttrs)(const AttributeObj& srcAttr, const AttributeObj& destAttr, bool modifyInUsd);

    /**
     * Connects two attributes together to add an edge to the graph.  This is an extended version with
     * more information about the connection, such as the type of connection.
     *
     * @param[in] srcAttr The attr that is the source of the directed connection
     * @param[in] destAttrInfo A ConnectionInfo struct describing the connection
     * @param[in] modifyInUsd Whether the connection is also modified in the underlying USD representation
     * @return true if connection is successful, false otherwise
     */
    bool(CARB_ABI* connectAttrsEx)(const AttributeObj& srcAttr, const ConnectionInfo& destAttr, bool modifyInUsd);

    /**
     * Disconnects two attributes that are connected
     *
     * @param[in] srcAttr The attribute that is the source of the directed connection
     * @param[in] destAttr The attribute that is the destination of the directed connection
     * @param[in] modifyInUsd Whether the connection is also modified in the underlying USD representation
     * @return true if connection is successfully broken, false otherwise (if no connections existed)
     */
    bool(CARB_ABI* disconnectAttrs)(const AttributeObj& srcAttr, const AttributeObj& destAttr, bool modifyInUsd);

    /**
     * Queries whether two attributes are connected
     *
     * @param[in] srcAttr The attribute that is the source of the directed connection
     * @param[in] destAttr The attribute that is the destination of the directed connection
     * @return true if the two attributes are connected, false otherwise
     */
    bool(CARB_ABI* areAttrsConnected)(const AttributeObj& srcAttr, const AttributeObj& destAttr);

    /**
     * Queries whether two attributes are connection compatible
     *
     * @param[in] srcAttr The attribute that would be the source of the directed connection
     * @param[in] destAttr The attribute that would be the destination of the directed connection
     * @return true if the two attributes are compatible, false otherwise
     */
    bool(CARB_ABI* areAttrsCompatible)(const AttributeObj& srcAttr, const AttributeObj& destAttr);

    /**
     * Retrieves the number of upstream connections to the attribute of a node
     *
     * @param[in] attrObj The attribute object for which to retrieve the connection count
     * @return The number of upstream connections to that attribute
     */
    size_t(CARB_ABI* getUpstreamConnectionCount)(const AttributeObj& attrObj);

    /**
     * Retrieves the upstream connections of the attribute of a node
     *
     * @param[in] attrObj The attribute object for which to retrieve the connections
     * @param[out] attrsBuf Buffer to hold the return AttributeObj
     * @param[in] bufferSize the number of AttributeObj structures the buffer is able to hold
     * @return true on success, false on failure
     */
    bool(CARB_ABI* getUpstreamConnections)(const AttributeObj& attrObj, AttributeObj* attrsBuf, size_t bufferSize);

    /**
     * Retrieves the detailed upstream connection info of an attribute.  Includes information like type of
     * connections.
     *
     * @param[in] attrObj The attribute object for which to retrieve the connections
     * @param[out] connectionInfoBif Buffer to hold the return ConnectionInfo
     * @param[in] bufferSize the number of AttributeObj structures the buffer is able to hold
     * @return true on success, false on failure
     */
    bool(CARB_ABI* getUpstreamConnectionsInfo)(const AttributeObj& attrObj,
                                               ConnectionInfo* connectionInfoBuf,
                                               size_t bufferSize);

    /**
     * Retrieves the number of downstream connections to the attribute of a node
     *
     * @param[in] attrObj The attribute object for which to retrieve the connection count
     * @return The number of downstream connections to that attribute
     */
    size_t(CARB_ABI* getDownstreamConnectionCount)(const AttributeObj& attrObj);

    /**
     * Retrieves the down connections of the attribute of a node
     *
     * @param[in] attrObj The attribute object for which to retrieve the connections
     * @param[out] attrsBuf Buffer to hold the return AttributeObj
     * @param[in] bufferSize the number of AttributeObj structures the buffer is able to hold
     * @return true on success, false on failure
     */
    bool(CARB_ABI* getDownstreamConnections)(const AttributeObj& attrObj, AttributeObj* attrsBuf, size_t bufferSize);

    /**
     * Retrieves the detailed upstream connection info of an attribute.  Includes information like type of
     * connections.
     *
     * @param[in] attrObj The attribute object for which to retrieve the connections
     * @param[out] connectionInfoBif Buffer to hold the return ConnectionInfo
     * @param[in] bufferSize the number of AttributeObj structures the buffer is able to hold
     * @return true on success, false on failure
     */
    bool(CARB_ABI* getDownstreamConnectionsInfo)(const AttributeObj& attrObj,
                                                 ConnectionInfo* connectionInfoBuf,
                                                 size_t bufferSize);

    /**
     * Retrieves the node associated with this attribute
     *
     * @param[in] attrObj The attribute object for which to retrieve the node
     * @return The NodeObj representing the node. In case of failure, the node handle
     *         will be kInvalidNodeHandle
     */
    NodeObj(CARB_ABI* getNode)(const AttributeObj& attrObj);

    /**
     * Ensures the attribute's value is updated, before reading it.  For push graphs this does nothing, as the
     * push graph is always evaluating and considered up to date.
     * For pull graphs, this generates the true "pull" on the attribute, that will cause whatever is upstream
     * and is dirty to evaluate.
     *
     * @param[in] attrObj The attribute object for which to update the value for
     * @param[in] updateImmediately Whether to cause the graph to update immediately (synchronously)
     * @return Whether the update was successful
     */
    bool(CARB_ABI* updateAttributeValue)(const AttributeObj& attrObj, bool updateImmediately);

    /** @private Deprecated - do not use */
    AttributeDataHandle(CARB_ABI* deprecated_0)(const AttributeObj&);

    /** @private Deprecated - do not use */
    ConstAttributeDataHandle(CARB_ABI* deprecated_1)(const AttributeObj&);

    /**
     * Registers a callback to be invoked when the value of the current attribute changes
     *
     * An attribute only permits a single callback and when called, the previously set callback
     * is replaced. Passing nullptr as the callback will remove any existing callback.
     *
     * @param[in] thisAttribute Reference to the AttributeObj struct representing the current attribute object
     * @param[in] onValueChanged The callback to trigger.  Parameters are the attribute involved, and the new value
     * @param[in] triggerOnConnected Whether to trigger the callback on connected attributes.
     */
    void(CARB_ABI* registerValueChangedCallback)(const AttributeObj& attrObj,
                                                 void (*onValueChanged)(const AttributeObj& attr, const void* value),
                                                 bool triggerOnConnected);

    /**
     * Returns the set of all metadata on this attribute.
     *
     * The keyBuf and valueBuf arrays preallocated by the caller, and contain at least "getMetadataCount()"
     * entries in them.
     * All returned strings are owned by the node type and not to be destroyed.
     * The returned keyBuf and valueBuf must have exactly the same size with corresponding index values; that is
     * keyBuf[i] is the metadata name for the string in valueBuf[i].
     *
     * @param[in] thisAttribute Reference to the AttributeObj struct representing the current attribute object
     * @param[out] keyBuf Buffer in which to put the list of metadata keys
     * @param[out] valueBuf Buffer in which to put the list of metadata values
     * @param[in] bufferSize the number of strings each of the two buffers is able to hold
     * @return Number of metadata items successfully populated
     */
    size_t(CARB_ABI* getAllMetadata)(const AttributeObj& thisAttribute,
                                     const char** keyBuf,
                                     const char** valueBuf,
                                     size_t bufferSize);

    /**
     * Retrieves a metadata value from this attribute
     *
     * @param[in] thisAttribute Reference to the AttributeObj struct representing the current attribute object
     * @param[in] key The name of the metadata to be retrieved
     * @return The value of the metadata, or nullptr if the named metadata was not set on this attribute
     */
    const char*(CARB_ABI* getMetadata)(const AttributeObj& thisAttribute, const char* key);

    /**
     * Returns the number of metadata entries on this attribute
     *
     * @param[in] thisAttribute Reference to the AttributeObj struct representing the current attribute object
     * @return the number of metadata key/value pairs on this attribute
     */
    size_t(CARB_ABI* getMetadataCount)(const AttributeObj& thisAttribute);

    /**
     * Sets a metadata value on this attribute.
     *
     * Certain metadata keywords have special meaning internally:
     *     uiName: The name of the attribute in a longer, human-readable format
     *
     * Note: The main way for metadata to be set is through the .ogn format files. If you call this directly the
     *       metadata will not persist across sessions. If you wish to define metadata outside of the .ogn file
     *       the best method is to override the initializeType() method in your attribute definition and set it there.
     *
     * @param[in] attrObj Reference to the AttributeObj struct representing the current attribute object
     * @param[in] key The keyword, used as the name of the metadata
     * @param[in] value The value of the metadata. Metadata can be parsed later if non-string values are desired.
     */
    void(CARB_ABI* setMetadata)(const AttributeObj& attrObj, const char* key, const char* value);

    /**
     * Where we have dynamic scheduling, downstream nodes can have their execution disabled by turning on the flag
     * in the upstream attribute.  Note you also have to call setDynamicDownstreamControl on the node to enable
     * this feature.  See setDynamicDownstreamControl on INode for further information.
     *
     * @param[in] attrObj Reference to the AttributeObj struct representing the current attribute object
     * @return Whether downstream nodes connected to this attribute should be disabled from further work
     */
    bool (CARB_ABI* getDisableDynamicDownstreamWork)(const AttributeObj& attrObj);

    /**
     * Where we have dynamic scheduling, downstream nodes can have their execution disabled by turning on the flag
     * in the upstream attribute.  Note you also have to call setDynamicDownstreamControl on the node to enable
     * this feature.  This function allows you to set the flag on the attribute that will disable the downstream
     * node. See setDynamicDownstreamControl on INode for further information.
     *
     * @param[in] attrObj Reference to the AttributeObj struct representing the current attribute object
     * @param[in] value Whether to disable the downstream connected nodes or not.
     */
    void (CARB_ABI* setDisableDynamicDownstreamWork)(const AttributeObj& attrObj, bool value);

    /**
     * Sets the resolved type of an extended type.  This should be called by a node from the
     * *onConnectionTypeResolve()* callback when it determines that an extended-type attribute
     * can be resolved to a specific type.  For example a generic 2-input "Add" node could resolve input B and its
     * output attribute type to float when input A is connected to a float. Passing @ref omni::fabric::Type() will
     * reset the attribute type to "unresolved".
     *
     * @note This operation is asynchronous because it is considered as part of a whole-graph type resolution
     *       algorithm.  It also may not succeed because there could be constraints in the graph that
     *       prevent the type from being resolved as requested.
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @param[in] type The new type of the attribute
     */
    void(CARB_ABI* setResolvedType)(const AttributeObj& attr, const Type& type);

    /**
     * Retrieves the port type (such as input, output, state) associated with this attribute
     *
     * @param[in] attrObj The attribute object for which to retrieve the connections
     * @return the AttributePortType of this attribute
     */
    AttributePortType(CARB_ABI* getPortType)(const AttributeObj& attrObj);

    /**
     * Returns whether the attribute is a dynamic attribute (not in the node definition) or not
     *
     * @param[in] attrObj The attribute object for which to query
     * @return Whether the attribute is a dynamic one
     */
    bool(CARB_ABI* isDynamic)(const AttributeObj& attrObj);

    /**
     * Returns the full path to the attribute, including the node path
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @return The full path to the attribute
     */
    const char*(CARB_ABI* getPath)(const AttributeObj& attrObj);

    /**
     * @return The string representing the extended union types, nullptr if the attribute is not a union type
     */
    const char*(CARB_ABI* getUnionTypes)(const AttributeObj& attribute);

    /**
     * Returns whether the attribute is still valid or not
     *
     * @param[in] attrObj The attribute object for which to query
     * @return Whether the attribute is still valid
     */
    bool(CARB_ABI* isValid)(const AttributeObj& attrObj);

   /**
     * Return the attribute name with the port type prepended if it isn't already present.
     *
     * @param[in] name The attribute name, with or without the port prefix
     * @param[in] portType The port type of the attribute
     * @param[in] isBundle true if the attribute name is to be used in a bundle. Note that colon is an illegal character
     *                     in bundled attributes so an underscore is used instead.
     * @return The name with the proper prefix for the given port type
     */
    NameToken(CARB_ABI* ensurePortTypeInName)(NameToken name, AttributePortType portType, bool isBundle);

    /**
     * Parse the port type from the given attribute name if present. The port type is indicated by a prefix separated by
     * a colon or underscore in the case of bundled attributes.
     *
     * @param[in] name The attribute name
     * @return The port type indicated by the attribute prefix if present. AttributePortType::kAttributePortType_Unknown
     *         if there is no recognized prefix.
     */
    AttributePortType(CARB_ABI* getPortTypeFromName)(NameToken name);

    /**
     * Return the attribute name with the port type removed if it is present. For example "inputs:attr" becomes "attr"
     *
     * @param[in] name The attribute name, with or without the port prefix
     * @param[in] isBundle true if the attribute name is to be used in a bundle. Note that colon is an illegal character
     *                     in bundled attributes so an underscore is used instead.
     * @return The name with the port type prefix removed
     */
    NameToken(CARB_ABI* removePortTypeFromName)(NameToken name, bool isBundle);

    /**
     * Get the optional compute flag from the attribute. When true this flag indicates that the attribute does not
     * need to be valid in order for the compute() function to be called.
     * Note that "valid" does not necessarily mean the attribute data is up to date, it only means that everything
     * required to locate the attribute data is available and valid (otherwise outputs would always be invalid).
     *
     * @param[in] attrObj The attribute object being queried
     * @return True if the attribute is optional for compute
     */
    bool(CARB_ABI* getIsOptionalForCompute)(const AttributeObj& attrObj);

    /**
     * Set whether the attribute is optional for compute or not; mostly used by generated code.
     * This flag would be set on attributes that the compute() method may not look at. It would then be up to the
     * compute() method to check validity if it ends up requiring the attribute's value. You might use this when an
     * attribute value is not used in all compute paths, like a "choice" node that selects exactly one of its inputs
     * to send to the output - only the selected input would need to be valid for compute to succeed.
     *
     * @param[in] attrObj The attribute object being modified
     * @param[in] isOptional New value for the optional flag on the attribute
     */
    void(CARB_ABI* setIsOptionalForCompute)(const AttributeObj& attrObj, bool isOptional);


    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Deprecated - use setDefaultValue instead")
    AttributeDataHandle(CARB_ABI* getDefaultValueAttributeDataHandle)(const AttributeObj& attrObj);

    /**
     * Get the deprecated flag from the attribute. When true this flag indicates that the attribute has been
     * deprecated and will be removed in a future version of the node.
     *
     * @param[in] attrObj The attribute object being queried
     * @return True if the attribute is deprecated
     */
    bool(CARB_ABI* isDeprecated)(const AttributeObj& attrObj);

    /**
     * Return the deprecation message for an attribute.
     *
     * @param[in] attributeObj Attribute to which this function applies
     * @return String containing the attribute deprecation message (nullptr if the attribute is not deprecated)
     */
    char const*(CARB_ABI* deprecationMessage)(const AttributeObj& attributeObj);

    /**
     * Returns an AttributeDataHandle to access the data on this attribute.
     *
     * @param[in] attrObj The attribute object for which to retrieve the data accessor
     * @param[in] instanceIdx The instance index relative to the current active instance for which you want to retrieve the data.
     * @return The AttributeDataHandle associated with this attribute, to mutate data in the FC
     */
    AttributeDataHandle(CARB_ABI* getAttributeDataHandle)(const AttributeObj& attrObj, InstanceIndex instanceIdx);

    /**
     * Returns a ConstAttributeDataHandle to access the data on this attribute.
     *
     * @param[in] attrObj The attribute object for which to retrieve the data accessor
     * @param[in] instanceIdx The instance index relative to the current active instance for which you want to retrieve the data.
     * @return The ConstAttributeDataHandle associated with this attribute, to read data in the FC
     */
    ConstAttributeDataHandle(CARB_ABI* getConstAttributeDataHandle)(const AttributeObj& attrObj, InstanceIndex instanceIdx);

    /**
     * Returns whether or not this attribute is a runtime constant or not.
     * Runtime constant will keep the same value every frame, for every instances
     * This property can be taken advantage in vectorized compute
     *
     * @param[in] attrObj The attribute object to query
     *
     * @return true if the attribute is a runtime constant, false otherwise
     */
    bool(CARB_ABI* isRuntimeConstant)(const AttributeObj& attrObj);

    /**
     * Warn the framework that writing to the provided attributes is done, so it can trigger callbacks attached to them
     *
     * @param[in] attrObjs A pointer to an array of attribute objects for which to call change callbacks
     * @param[in] attrObjCount The number of object(s) in that array
     */
    void(CARB_ABI* writeComplete)(const AttributeObj* attrObjs, size_t attrObjCount);

    /**
     * Returns the name of the attribute as a token
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @return The name of the attribute as a token
     */
    NameToken(CARB_ABI* getNameToken)(const AttributeObj& attr);

    /**
     * Set the default value that needs to be used for this attribute
     * This function won't work on extended attributes
     * This function will write to USD if the owning graph is backed by USD
     * The new value will be immediately propagated to all existing instances
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @param[in] type The type of the value pointed by "value". The function will fail is this type is incompatible with the attribute
     * @param[in] value A pointer to a value of type "type". In case the type is an array, value should be a pointer to the base address of the storage
     * @param[in] size In case the pointed type is an array, the size of the pointed array. Parameter ignored otherwise.
     * @return Whether the value was successfully set or not
     */
    bool(CARB_ABI* setDefaultValue)(AttributeObj const& attr, Type type, void const* value, size_t size);

    /**
     * Maps a node attribute to an attribute on the owning graph target
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @param[in] targetAttribName The name of the attribute on the graph target to map to
     * @return Whether the attribute was successfully mapped or not. In certain cases, the
     *         mapping is deferred until instances are added to the graph, and the return
     *         value will reflect this.
     */
    FunctionResult(CARB_ABI* mapToTarget)(AttributeObj const& attr, NameToken targetAttribName);

    /**
     * Returns the attribute name on the graph target this node attribute maps to
     *
     * @param[in] attr Reference to the AttributeObj struct representing the attribute object
     * @return The target attribute name if mapped, invalid  token else (omni::fabric::kUninitializedToken)
     */
    NameToken(CARB_ABI* getTargetMapping)(AttributeObj const& attr);

    /**
    * Checks if this attribute is a pass through attribute.
    * Pass through attributes do not own any data.
    *
    * @param[in] attr Reference to the AttributeObj struct representing the attribute object
    * @return Returns true if this is a pass through attribute, otherwise returns false.
    */
    bool(CARB_ABI* isPassthrough)(AttributeObj const& attr);

    /**
    * Returns the attribute that will be the owner of the data for runtime
    * taking into account its connections.
    *
    * @param[in] attr Reference to the AttributeObj struct representing the attribute object
    * @return Returns the attribute that will be the owner of the data for runtime.
    */
    AttributeObj (CARB_ABI* getDataOwningAttribute)(AttributeObj const& attr);

    /**
     * Experimental feature that let you specify that a mapped attribute lives in another fabric cache
     * than the one used by the graph.
     *
     * This is mandatory that the graph targets are layed out in the exact same way in all fabrics caches
     * referenced by the graph (the main fabric as well as any others referenced through this call)
     *
     * @param[in] attr      Reference to the AttributeObj struct representing an already mapped attribute object
     * @param[in] fabricId  The Id representing the fabric cache backing the target data.
     *                      Passing kInvalidFabricId will restore the default backing.
     * @return              Returns true if the backing has been successfully changed, false otherwise and an error has been logged
     */
    bool (CARB_ABI* setFabricBackingForMappedAttribute)(AttributeObj const& attr, omni::fabric::FabricId fabricId);
};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IAttribute, setFabricBackingForMappedAttribute, 53)

// ======================================================================
/** Interface to a single node in a graph */
struct INode
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::INode", 4, 10);

    /**
     * Returns the number of attributes on this node
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @return the number of attributes on this node
     */
    size_t(CARB_ABI* getAttributeCount)(const NodeObj& node);

    /**
     * Returns the attributes on this node
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[out] attrsBuf Buffer to hold the return attribute objects
     * @param[in] bufferSize the number of AttributeObj structures the buffer is able to hold
     * @return true if successful, false otherwise
     */
    bool(CARB_ABI* getAttributes)(const NodeObj& node, AttributeObj* attrsBuf, size_t bufferSize);

    /**
     * Retrieves whether the attribute in question exists or not
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] attrName Name of the attribute on the node
     * @return true if the attribute exists on the node, false if not
     */
    bool(CARB_ABI* getAttributeExists)(const NodeObj& node, const char* attrName);

    /** @private Retired - do not use */
    void (CARB_ABI* retired_1)(NodeObj&);

    /**
     * Retrieves an attribute that points to the attribute on the current node.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] attrName Name of the attribute on the node
     * @return the attribute object requested
     */
    AttributeObj(CARB_ABI* getAttribute)(const NodeObj& node, const char* attrName);

    /**
     * Retrieves an attribute that points to the attribute on the current node.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] attrName Name of the attribute on the node
     * @return the attribute object requested
     */
    AttributeObj(CARB_ABI* getAttributeByToken)(const NodeObj& node, NameToken attrName);

    /**
     * Retrieves the prim path to the node
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @return the prim path to the node
     */
    const char*(CARB_ABI* getPrimPath)(const NodeObj& node);

    /**
     * Retrieves the user data set on the node
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     */
    void*(CARB_ABI* getUserData)(const NodeObj& node);

    /**
     * Retrieves the user data set on the node
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     */
    void(CARB_ABI* setUserData)(const NodeObj& node, void* userData);

    /** @private Retired - do not use */
    void (CARB_ABI* retired_2)(NodeObj&);

    /** @private Retired - do not use */
    bool (CARB_ABI* retired_3)(NodeObj&);

    /** @private Retired - do not use */
    void (CARB_ABI* retired_4)(NodeObj&);

    /**
     * Returns the graph that this node belongs to
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @return GraphObj structure containing the graph this node belongs to
     */
    GraphObj(CARB_ABI* getGraph)(const NodeObj& node);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Deprecated - use getNodeTypeObj")
    INodeType(CARB_ABI* getNodeType)(const NodeObj&);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Deprecated - use getNodeTypeObj().getTypeName()")
    const char*(CARB_ABI* getPythonNodeType)(const NodeObj&);

    /**
     * Returns the node is disabled
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @return true if disabled, false otherwise
     */
    bool(CARB_ABI* isDisabled)(const NodeObj& node);

    /**
     * Sets the disabled state on the node
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] disable Whether to disable the node
     */
    void(CARB_ABI* setDisabled)(const NodeObj& node, bool disable);

    /**
     * Lets the evaluation system know that the compute for this node is complete for this frame but not completed
     * overall.  For example, once an animation is triggered, we want the animation to play until completion - on
     * a particular frame, the animation for that frame may be complete, but we're not done until the overall
     * animation is completed.  This method is only meaningful for evaluators that implement standard flow graph
     * semantics.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     *
     */
    void(CARB_ABI* setComputeIncomplete)(const NodeObj& node);

    /**
     * Returns whether the node has an USD representation on the stage.
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @return true if the node is backed by USD, false otherwise
     */
    bool(CARB_ABI* isBackedByUsd)(const NodeObj& node);

    /**
     * Creates a dynamic attribute on the node.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] name Name of the attribute
     * @param[in] attributeType The Type of the attribute. Extended attributes are Token types.
     * @param[in] value Pointer to the location containing the initial value of the attribute
     * @param[in] elemCount Number of elements in the attribute -- nullptr if the attribute is a scalar
     * @param[in] portType Whether this attribute is an input, output, or state
     * @param[in] extendedAttrType The type of extended attribute to create, if any (see definition of
     *            ExtendedAttributeType)
     * @param[in] unionTypes In case the extendedAttrType is union, unionTypes is a comma separated
     *            string that lists the allowable concrete types in the union
     * @return true if the attribute was created, false otherwise
     */
    bool(CARB_ABI* createAttribute)(const NodeObj& node,
                                    const char* name,
                                    Type attributeType,
                                    const void* value,
                                    const size_t* elemCount,
                                    AttributePortType portType,
                                    ExtendedAttributeType extendedAttrType,
                                    const char* unionTypes);

    /**
     * Removes a dynamic attribute from the node
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] name Name of the attribute
     * @return true if the attribute was removed, false if the attribute was not found
     */
    bool(CARB_ABI* removeAttribute)(const NodeObj& node, const char* name);

    /** @private retired - do not use */
    void(CARB_ABI* retired_8)(const NodeObj&);

    /**
     * Registers a callback to be invoked when any attribute of the current node is connected
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] connectionCallback The struct containing the callback to trigger, and a piece of user data.
     * The parameters are the attributes of this and the other node being connected, and a void* of user data
     * @return true for success, false for failure
     */
    bool(CARB_ABI* registerConnectedCallback)(const NodeObj& node,
                                              ConnectionCallback connectionCallback);

    /**
     * Registers a callback to be invoked when any attribute of the current node is disconnected
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] connectionCallback The struct containing the callback to trigger, and a piece of user data.
     * The parameters are the attributes of this and the other node being disconnected, and a void* of user data
     * @return true for success, false for failure
     */
    bool(CARB_ABI* registerDisconnectedCallback)(const NodeObj& node,
                                                ConnectionCallback connectionCallback);

    /**
     * Deregisters the callback to be invoked when any attribute of the current node is connected
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] connectionCallback The struct containing the callback to trigger, and a piece of user data.
     */
    void(CARB_ABI* deregisterConnectedCallback)(const NodeObj& node, ConnectionCallback connectionCallback);

    /**
     * Deregisters the callback to be invoked when any attribute of the current node is disconnected
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] connectionCallback The struct containing the callback to trigger, and a piece of user data.
     */
    void(CARB_ABI* deregisterDisconnectedCallback)(const NodeObj& node, ConnectionCallback connectionCallback);

    /**
     * retired - do not use
     */
    bool(CARB_ABI* retired_6)(const NodeObj&);

    /**
     * retired - do not use
     */
    void(CARB_ABI* retired_7)(const NodeObj&, bool);

    /**
     * Returns the NodeTypeObj structure associated with this node.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @return NodeTypeObj encapsulating the node type from which this node was created
     */
    NodeTypeObj(CARB_ABI* getNodeTypeObj)(const NodeObj& node);

    /**
     * Resolves attribute types given a set of attributes which are fully type coupled.
     * For example if node 'Increment' has one input attribute 'a' and one output attribute 'b'
     * and the types of 'a' and 'b' should always match. If the input is resolved then this function will
     * resolve the output to the same type.
     * It will also take into consideration available conversions on the input side.
     * The type of the first (resolved) provided attribute will be used to resolve others or select appropriate conversions
     *
     * Note that input attribute types are never inferred from output attribute types.
     *
     * This function should only be called from the INodeType function `onConnectionTypeResolve`
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[out] attrsBuf Buffer that holds the attributes to be resolved as a coupled group
     * @param[in] bufferSize the number of AttributeObj structures the buffer is able to hold
     * @return true if successful, false otherwise, usually due to mismatched or missing resolved types
     */
    bool(CARB_ABI* resolveCoupledAttributes)(const NodeObj& node, AttributeObj* attrsBuf, size_t bufferSize);

    /**
     * Resolves attribute types given a set of attributes, that can have differing tuple counts and/or array depth,
     * and differing but convertible base data type.
     * The three input buffers are tied together, holding the attribute, the tuple
     * count, and the array depth of the types to be coupled.
     * This function will solve base type conversion by targeting the first provided type in the list,
     * for all other ones that require it.
     *
     * For example if node 'makeTuple2' has two input attributes 'a' and 'b' and one output 'c' and we want to resolve
     * any float connection to the types 'a':float, 'b':float, 'c':float[2] (convertible base types and different tuple counts)
     * then the input buffers would contain:
     *     attrsBuf = [a, b, c]
     *     tuplesBuf = [1, 1, 2]
     *     arrayDepthsBuf = [0, 0, 0]
     *     rolesBuf = [AttributeRole::eNone, AttributeRole::eNone, AttributeRole::eNone]
     *
     * This is worth noting that 'b' could be of any type convertible to float. But since the first provided
     * attribute is 'a', the type of 'a' will be used to propagate the type resolution.
     *
     * Note that input attribute types are never inferred from output attribute types.
     *
     * This function should only be called from the INodeType function `onConnectionTypeResolve`
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] attrsBuf Buffer that holds the attributes to be resolved as a coupled group
     * @param[in] tuplesBuf Buffer that holds the tuple count desired for each corresponding attribute. Any value
     *                      of kUninitializedTypeCount indicates the found tuple count is to be used when resolving.
     * @param[in] arrayDepthsBuf Buffer that holds the array depth desired for each corresponding attribute. Any value
     *                           of kUninitializedTypeCount indicates the found array depth is to be used when resolving.
     * @param[in] rolesBuf Buffer that holds the role desired for each corresponding attribute. Any value of
     *                     AttributeRole::eUnknown indicates the found role is to be used when resolving.
     * @param[in] bufferSize the number of AttributeObj structures the buffer is able to hold
     * @return true if successful, false otherwise, usually due to mismatched or missing resolved types
     */
    bool(CARB_ABI* resolvePartiallyCoupledAttributes)(const NodeObj& node,
                                                      const AttributeObj* attrsBuf,
                                                      const uint8_t* tuplesBuf,
                                                      const uint8_t* arrayDepthsBuf,
                                                      const AttributeRole* rolesBuf,
                                                      size_t bufferSize);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Use USD notice handling to monitor changes")
    bool(CARB_ABI* registerPathChangedCallback)(const NodeObj&, PathChangedCallback);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Use USD notice handling to monitor changes")
    void(CARB_ABI* deregisterPathChangedCallback)(const NodeObj& node, PathChangedCallback pathChangedCallback);

    /**
     * Returns the graph wrapped by this node, if any (as opposed to the graph this node belongs to)
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @return GraphObj structure containing the graph wrapped by this node
     */
    GraphObj(CARB_ABI* getWrappedGraph)(const NodeObj& node);

    /**
     * Returns the interface for the event stream generated by changes to this node.
     * @return The IEventStreamPtr that pumps events when node changes happen
     */
    carb::events::IEventStreamPtr(CARB_ABI* getEventStream)(const NodeObj& node);

    /**
     * Returns whether the NodeObj's handle is still valid
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @return true if valid, false otherwise
     */
    bool (CARB_ABI* isValid)(const NodeObj& node);

    /**
     * Requests that the given node be computed at the next graph evaluation. This is for use with nodes that are
     * marked as being RequestDrivenCompute.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @return true if the request was successful, false if there was an error
     */
    bool(CARB_ABI* requestCompute)(const NodeObj& node);

    /**
     * Returns a NodeObj for the given NodeHandle if the referenced node is valid.
     *
     * @param[in] nodeHandle The NodeHandle for the compute node
     * @return The NodeObj representing the node. In case of failure, the node handle
     *         will be kInvalidNodeHandle
     */
    NodeObj(CARB_ABI* getNodeFromHandle)(const NodeHandle nodeHandle);

    /**
     * Returns the number of instances on which computation has been invoked for this node since the
     * counter last rolled over to 0.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object.
     * @return The count.
     */
    size_t (CARB_ABI* getComputeCount)(const NodeObj& node);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Use increaseComputeCount instead")
    size_t (CARB_ABI* incrementComputeCount)(const NodeObj& node);


    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Use logComputeMessageOnInstance instead")
    bool (CARB_ABI* logComputeMessage)(const NodeObj& node, ogn::Severity severity, const char* message);

    /**
     * Returns the number of compute messages of the given severity logged for the node.
     *
     * Compute messages are cleared at the start of each evaluation, so the count will be
     * only for the most recent evaluation.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object.
     * @param[in] severity Severity level of the messages.
     * @return The number of compute messages of the specified severity.
     */
    size_t (CARB_ABI* getComputeMessageCount)(const NodeObj& node, ogn::Severity severity);

    /**
     * Returns a specified compute message of the given severity logged for the node.
     *
     * Use getComputeMessageCount() to determine the number of messages currently available.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object.
     * @param[in] severity Severity level of the message to return.
     * @param[in] index Index of the message to return, starting at 0.
     * @return The requested message or nullptr if 'index' was out of range.
     */
    const char* (CARB_ABI* getComputeMessage)(const NodeObj& node, ogn::Severity severity, size_t index);

    /**
     * Clears all compute messages logged for the node prior to its most recent evaluation.
     * Messages from its most recent evaluation are left untouched.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object.
     * @return The number of messages that were deleted.
     */
    size_t (CARB_ABI* clearOldComputeMessages)(const NodeObj& node);

    /**
    * Retrieve the OGN database for the current active instance of this node. The DB is maintained up2date internally by the framework.
     * If it does not exists the provided ognCreate callback will be invoked to instantiate it

     *
     * @param[in] node Reference to the NodeObj struct representing the node object.
     * @param[in] ognCreate A callback that allocates and returns the DB associated to the current active instance of this node. Ownership is transferred to the node
     */
    ogn::OmniGraphDatabase*(CARB_ABI* getOgnDatabase)(const NodeObj& node, CreateDbFunc ognCreate);

    /**
     * Returns whether this node is a compound node. A compound node is a node whose node type is defined by a subgraph instead
     * of a built-in type.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object.
     * @returns True if the provided node is a compound node, false otherwise
     */
    bool(CARB_ABI* isCompoundNode)(const NodeObj& node);

    /**
     * Retrieve a persistent ID for the current active graph associated to this node, optionally offsetted
     *
     * UPGRADE NOTE: if you end up here because of a compile error, the previously returned token is now wrapped into
     * the GraphInstanceID. Everything remains binary compatible, but code at call site needs to be adapted
     * by adding ".id" to the returned value.
     *
     * @param[in] node Handle representing the node object.
     * @param[in] instanceOffset: In vectorized context, the instance index relative to the currently targeted graph
     * @return A unique and process-persistent ID that represents the current active instance of this node
     */
    GraphInstanceID (CARB_ABI* getGraphInstanceID)(NodeHandle node, InstanceIndex instanceOffset);

    /**
     * Returns a Stamp that is incremented any time an input or state attribute is changed outside of graph evaluation.
     * For example, interactively or through a script.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object.
     * @returns The stamp value
     */
    exec::unstable::Stamp(CARB_ABI* getAttributeChangeStamp)(const NodeObj& node);

    /**
     * Returns a handle to the associated sub-graph, if the given node is a compound node.
     *
     * @param[in] node Handle representing the node object.
     * @return The GraphObj representing the graph. In case of failure, the graph handle
     *         will be kInvalidGraphHandle.
     */
    GraphObj (CARB_ABI* getCompoundGraphInstance)(const NodeObj& node);

    /**
     * Query all the node and context handles that the provided node emulate when used in an auto instancing scenario.
     *
     * @param[in] node Handle representing the "master" node object, the one that handle the execution.
     * @param[out] graphContexts A pointer reference that will be set to an array of all the emulated auto-instanced graph contexts
     * @param[out] nodeObjects A pointer reference that will be set to an array of all the emulated auto-instanced nodes
     * @return The number of elements in the returned arrays, 1 if there is not auto instancing associated to the provided node (itself)
     */
    size_t(CARB_ABI* getAutoInstances)(const NodeObj& node, GraphContextObj const*& graphContexts, NodeObj const*& nodeObjects);


    /** @private Retired - do not use */
    bool (CARB_ABI* retired_5)(const NodeObj& nodeObj);

    /**
     * Logs a compute message of a given severity for the node.
     *
     * This method is intended to be used from within the compute() method of a
     * node to alert the user to any problems or issues with the node's most recent
     * evaluation. They are accumulated until the start of the next compute,
     * at which point they are cleared.
     *
     * If duplicate messages are logged, with the same severity level, only one is
     * stored.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object.
     * @param[in] inst In vectorized context, the instance index relative to the currently targeted graph
     * @param[in] severity Severity level of the message.
     * @param[in] message The message.
     * @return Returns true if the message has already been logged, false otherwise.
     */
    bool(CARB_ABI* logComputeMessageOnInstance)(const NodeObj& node, InstanceIndex inst, ogn::Severity severity, const char* message);

    /**
     * Increase the node's compute counter by the provided amount.
     *
     * This method is provided primarily for debugging and experimental uses and
     * should not normally be used by end-users.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object
     * @param[in] count the number to be added to the compute count.
     * @return The new count.
     */
    size_t(CARB_ABI* increaseComputeCount)(const NodeObj& node, size_t count);

    /**
     * Returns the number of vectorized segments on which computation has been invoked on this node since the
     * counter last rolled over to 0.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object.
     * @return The count.
     */
    size_t(CARB_ABI* getComputeVectorizedCount)(const NodeObj& node);

    /**
     * Validates that a node can be evaluated. This is intended to be called prior to compute
     * to validate that the node does not contain any errors that should prevent computation, such as
     * invalid connections.
     *
     * @param[in] node Reference to the NodeObj struct representing the node object.
     * @return True if the node is eligible for validation, false if it contains an error that should prevent
     *         evaluation.
     */
    bool(CARB_ABI* validateCompute)(const NodeObj& node);

};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(INode, validateCompute, 54)


/**
 * Defines the node event types.
 */
enum class INodeEvent
{
    eCreateAttribute,      //!< Dynamic attribute added to a node
    eRemoveAttribute,      //!< Dynamic attribute removed from a node
    eAttributeTypeResolve  //!< Extended-type attribute resolution has changed
};

/**
 * Defines the graph event types
 */
enum class IGraphEvent
{
    eCreateVariable,     ///< Variable has been added to the graph
    eRemoveVariable,     ///< Variable has been removed from the graph
    eClosing,            ///< Stage is closing
    eComputeRequested,   ///< INode::requestCompute was called on a contained node
    eNodeAttributeChange,///< An input or state attribute changed outside of graph evaluation
    eVariableTypeChange  ///< A variable in the graph had its type changed
};

// ======================================================================
/** Interface to an OmniGraph, several of which may be present in a scene */
struct IGraph
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::IGraph", 3, 16);

    /**
     * Returns the number of nodes in the graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return The number of nodes in the graph
     */
    size_t(CARB_ABI* getNodeCount)(const GraphObj& graphObj);

    /**
     * Get the nodes in the graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[out] nodesBuf Buffer to hold the return NodeObjs
     * @param[in] bufferSize the number of NodeObj structures the buffer is able to hold
     * @return true on success, false on failure
     */
    bool(CARB_ABI* getNodes)(const GraphObj& graphObj, NodeObj* nodesBuf, size_t bufferSize);

    /**
     * Returns the number of subgraphs in the graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return The number of subgraphs in the graph
     */
    size_t(CARB_ABI* getSubgraphCount)(const GraphObj& graphObj);

    /**
     * Get the subgraphs in the graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[out] graphsBuf Buffer to hold the return GraphObjs
     * @param[in] bufferSize the number of GraphObjs structures the buffer is able to hold
     * @return true on success, false on failure
     */
    bool(CARB_ABI* getSubgraphs)(const GraphObj& graphObj, GraphObj* graphsBuf, size_t bufferSize);

    /**
     * Get a particular subgraph in the graph given its path
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] subgraphPath the path to the subgraph in question
     * @return The GraphObj representing the graph.  In case of failure, the graph handle
     *         will be kInvalidGraphHandle
     */
    GraphObj(CARB_ABI* getSubgraph)(const GraphObj& graphObj, const char* subgraphPath);

    /**
     * Returns the path to the graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return The path to the graph (may be empty)
     */
    const char*(CARB_ABI* getPathToGraph)(const GraphObj& graphObj);

    /**
     * Returns whether the current graph is disabled
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return true if the current graph is disabled false otherwise
     */
    bool(CARB_ABI* isDisabled)(const GraphObj& graphObj);

    /**
     * Sets the disabled state of the graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] disable Whether or not to disable the current graph
     */
    void(CARB_ABI* setDisabled)(const GraphObj& graphObj, bool disable);

    /**
     * Get the default graph context associated with the graph.  Each graph has a default
     * context - it's usually one that gives you evaluation of the graph on the current
     * time, for example.
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return The GraphContextObj representing the default graph context associated with
     *         the node.
     */
    GraphContextObj(CARB_ABI* getDefaultGraphContext)(const GraphObj& graphObj);

    /**
     * Get a particular node in the graph given its path
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] nodePath the path to the node in question
     * @return The NodeObj representing the node.  In case of failure, the node handle
     *         will be kInvalidNodeHandle
     */
    NodeObj(CARB_ABI* getNode)(const GraphObj& graphObj, const char* nodePath);

    /**
     * Create a node in the graph at a given path with a given type
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] nodePath the path to where the node will be added
     * @param[in] nodeType the type name of the node to add
     * @param[in] createUsd Whether to create USD backing for the node being created
     * @return The NodeObj representing the node. In case of failure, the node handle
     *         will be kInvalidNodeHandle
     */
    NodeObj(CARB_ABI* createNode)(GraphObj& graphObj, const char* nodePath, const char* nodeType, bool createUsd);

    /**
     * Destroy the node in the graph at a given path
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] nodePath the path of the node to destroy
     * @param[in] destroyUsd Whether to destroy USD backing for the node being destroyed
     * @return True, if the node was successfully destroyed. False otherwise.
     */
    bool(CARB_ABI* destroyNode)(GraphObj& graphObj, const char* nodePath, bool destroyUsd);

    /**
     * Rename the node in the graph at a given path
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] nodePath the path of the node to rename
     * @param[in] newPath the new path of the node
     * @return True, if the node was successfully renamed. False otherwise.
     */
    bool(CARB_ABI* renameNode)(GraphObj& graphObj, const char* oldPath, const char* newPath);

    /**
     * Create a subgraph in the graph at a given path with a given type
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] subgraphPath the path to where the subgraph will be added
     * @param[in] evaluator the evaluator type to use for the subgraph being created
     * @param[in] createUsd whether to create USD backing for the subgraph being created
     * @return The GraphObj representing the subgraph. In case of failure, the graph handle
     *         will be kInvalidGraphHandle
     */
    GraphObj(CARB_ABI* createSubgraph)(GraphObj& graphObj, const char* subgraphPath, const char* evaluator, bool createUsd);

    /**
     * reload the graph settings based on ComputeGraphSettings
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     */
    void(CARB_ABI* reloadGraphSettings)(GraphObj& graphObj);

    /**
     * Rename the subgraph in the graph at a given path
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] subgraphPath the path of the subgraph to rename
     * @param[in] newPath the new path of the subgraph
     * @return True, if the subgraph was successfully renamed. False otherwise.
     */
    bool(CARB_ABI* renameSubgraph)(GraphObj& graphObj, const char* oldPath, const char* newPath);

    /**
     * Notifies the graph that some attribute has changed on a node.  This will trigger
     * updates from things like lazy evaluation graphs, for example.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] Reference to the AttributeObj struct representing the attribute object
     */
    void(CARB_ABI* onAttributeChanged)(const GraphObj& graphObj, const AttributeObj& attrObj);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Will be removed in next major version, please use IGraph::inspect instead")
    void(CARB_ABI* printDiagnostic)(const GraphObj&);

    /**
     * Register a callback to be invoked when a legacy file with an older file format version
     * is detected.  This callback is invoked before stage attach happens.
     *
     * @param[in] fileFormatUpgrade - structure containing the callback and a piece of user data to
     * be passed back to the callback when invoked.
     */
    void (CARB_ABI* registerPreLoadFileFormatUpgradeCallback)(FileFormatUpgrade fileFormatUpgrade);

    /**
     * Register a callback to be invoked when a legacy file with an older file format version
     * is detected.  This callback is invoked after stage attach happens.
     *
     * @param[in] fileFormatUpgrade - structure containing the callback and a piece of user data to
     * be passed back to the callback when invoked.
     */
    void (CARB_ABI* registerPostLoadFileFormatUpgradeCallback)(FileFormatUpgrade fileFormatUpgrade);

    /**
     * Deregisters the pre-load callback to be invoked when a legacy file with an older
     * file format version is detected.
     *
     * @param[in] fileFormatUpgrade - structure containing the callback and a piece of user data to
     * be passed back to the callback when invoked.
     *
     */
    void (CARB_ABI* deregisterPreLoadFileFormatUpgradeCallback)(FileFormatUpgrade fileFormatUpgrade);

    /**
     * Deregisters the post-load callback to be invoked when a legacy file with an older
     * file format version is detected.
     *
     * @param[in] fileFormatUpgrade - structure containing the callback and a piece of user data to
     * be passed back to the callback when invoked.
     */
    void (CARB_ABI* deregisterPostLoadFileFormatUpgradeCallback)(FileFormatUpgrade fileFormatUpgrade);

    /**
     * Returns whether USD notice handling is enabled for the graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return true if the current graph has USD notice handling enabled
     */
    bool(CARB_ABI* usdNoticeHandlingEnabled)(const GraphObj& graphObj);

    /**
     * Sets whether the USD notice handling is enabled for this graph.  This is an
     * advanced operation - do not use this method unless you know what you're doing.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] enable Whether or not to enable USD notice handling for this graph
     */
    void(CARB_ABI* setUSDNoticeHandlingEnabled)(const GraphObj& graphObj, bool enable);

    /**
     * Runs the inspector on the data in the given graph.
     *
     * @param[in] graphObj The graph on which the inspector runs
     * @param[in] inspector The inspector class
     * @return true if the inspection ran successfully, false if the inspection type is not supported
     */
    bool(CARB_ABI* inspect)(const GraphObj& graphObj, inspect::IInspector* inspector);

    /**
     * Create a new graph, wrapped as a node, at the given location.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] nodeName the name of the node that wraps the graph
     * @param[in] graphPath the path to where the graph that the node will wrap will be added
     * @param[in] evaluatorName the evaluator to use for the new graph
     * @param[in] isGlobalGraph Whether this graph is a top level global graph
     * @param[in] backByUSD Whether to back this graph by USD
     * @param[in] backingType What kind of FC backs this graph
     * @param[in] graphPipelineStage What pipeline stage this graph occupies
     * @return The NodeObj representing the node that wraps the graph. The newly created graph can be
     *         retrieved from the node.  In case of failure, the NodeObj will contain kInvalidNodeHandle
     */
    NodeObj(CARB_ABI* createGraphAsNode)(GraphObj& graphObj,
                                         const char* nodeName,
                                         const char* graphPath,
                                         const char* evaluatorName,
                                         bool isGlobalGraph,
                                         bool backByUSD,
                                         GraphBackingType backingType,
                                         GraphPipelineStage graphPipelineStage);

    /**
     * Reloads the graph from the stage by deleting the current graph and creating a new one to attach
     * to the stage.  Note: this is a complete reset - any stateful nodes will lose their state.
     *
     * @param[in] graphObj The graph to reload
     */
    void(CARB_ABI* reloadFromStage)(const GraphObj& graphObj);

    /**
     * Returns the Fabric backing type for this graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return Fabric backing type.  See GraphBackingType definition for details.
     */
    GraphBackingType(CARB_ABI* getGraphBackingType)(const GraphObj& graphObj);

    /**
     * Returns the graph pipeline stage (eg. simulation, pre-render, post-render) for this graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return Graph pipeline stage.  See GraphPipelineStage definition for details.
     */
    GraphPipelineStage(CARB_ABI* getPipelineStage)(const GraphObj& graphObj);

     /**
     * Returns whether the GraphObj's handle is still valid
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return true if valid, false otherwise
     */
    bool(CARB_ABI* isValid)(const GraphObj& graphObj);

    /**
     * Returns the FabricId for this Graph. This id can be used with the Fabric API, but should only
     * be required for advanced use cases.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[out] fabricId The output user id
     * @return true on success, false on failure
     */
    bool(CARB_ABI* getFabricId)(const GraphObj& graphObj, omni::fabric::FabricId& fabricId);

    /**
     * Warning: this is an advanced function - do not call unless you know exactly what is involved here.
     *
     * This allows a graph to be "ticked" independently of the normal graph evaluation process, where
     * graphs are ordered into different pipeline stages (simulation, pre-render, post-render), and all
     * graphs of each stage are evaluated according to the order described in the orchestration graph in
     * each stage.
     *
     * Instead, this function allows graphs in the custom pipeline stage to be evaluated on its own.
     * If this function is being called from a different thread, it is the caller's responsibility to ensure
     * that the Fabric backing the graph is independent (stage without history), otherwise data races
     * will ensue.  If this function is being called from the simulation / main thread, the the Fabric
     * backing the graph may be a shared one.
     *
     * It is illegal to call this function for any graph other than those setup with the custom pipeline
     * stage.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     */
    void (CARB_ABI* evaluate)(const GraphObj& graphObj);

    /**
     * Returns the parent of this graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return The parent graph (may be invalid)
     */
    GraphObj(CARB_ABI* getParentGraph)(const GraphObj& graphObj);

    /**
    * Returns whether the path points to a top level graph prim.
    *
    * @param[in] path to the prim in question
    * @return True if the path points to a prim that is a top level graph
    */
    bool(CARB_ABI* isGlobalGraphPrim)(const char* path);

    /**
     * Registers a callback to be invoked at the end of graph evaluation for all of the nodes
     * whose error status changed during that evaluation.
     *
     * This is provided primarily for UI purposes. E.g. highlighting nodes with compute errors
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] errorStatusChangeCallback - structure containing the callback and a piece of user data to
     * be passed back to the callback when invoked.
     */
    void (CARB_ABI* registerErrorStatusChangeCallback)(const GraphObj& graphObj, ErrorStatusChangeCallback errorStatusChangeCallback);

    /**
     * Deregisters a callback to be invoked at the end of graph evaluation for all of the nodes
     * whose error status changed during that evaluation.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] errorStatusChangeCallback - structure containing the callback and a piece of user data to
     * be passed back to the callback when invoked.
     *
     */
    void (CARB_ABI* deregisterErrorStatusChangeCallback)(const GraphObj& graphObj, ErrorStatusChangeCallback errorStatusChangeCallback);

    /** @private deprecated - do not use */
    CARB_DEPRECATED("Will be retired in next major version: this call is not necessary anymore and can be safely removed")
    void(CARB_ABI* nodeErrorStatusChanged)(const GraphObj& graphObj, const NodeObj& nodeObj);

    /**
     * Returns the number of variables in the graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return The number of variables in the graph.
     */
    size_t(CARB_ABI* getVariableCount)(const GraphObj& graphObj);

    /**
     * Get the variables defined in the graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[out] variableBuf Buffer to hold the returned IVariable objects
     * @param[in] bufferSize The number of IVariable objects the buffer is able to hold
     * @return true on success, false on failure
     */
    bool(CARB_ABI* getVariables)(const GraphObj& graphObj, IVariablePtr* variableBuf, size_t bufferSize);

    /**
     * Create a new variable on the graph with the given name. The name must be unique
     * among variables on the graph, even if the type is different.
     *
     * The variable is backed by USD.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] name The name to give the variable.
     * @param[in] variableType The data type used to create the variable.
     * @return The newly created variable, or null if the variable could not be created.
     */
    IVariablePtr(CARB_ABI* createVariable)(const GraphObj& graphObj, const char* name, Type variableType);

    /**
     * Removes the given variable from the graph.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] variable The variable to remove from the graph.
     * @return True if the variable was successfully removed, false otherwise.
     */
    bool(CARB_ABI* removeVariable)(const GraphObj& graphObj, const IVariablePtr& variable);

    /**
     * Retrieves a variable with the given name.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] name The name of the variable to search for.
     * @return The variable with the given name on the graph, or null if the variable does
     *         not exist.
     */
    IVariablePtr(CARB_ABI* findVariable)(const GraphObj& graphObj, const char* name);

    /**
     * Change the pipeline stage (eg. simulation, pre-render, post-render) that this graph is in
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] newPipelineStage The new pipeline stage that this graph will be moved into
     */
    void (CARB_ABI* changePipelineStage)(const GraphObj& graphObj, GraphPipelineStage newPipelineStage);

    /**
     * Returns the interface for the event stream generated by changes to this graph.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return The IEventStreamPtr that pumps events when graph changes happen
     */
    carb::events::IEventStreamPtr(CARB_ABI* getEventStream)(const GraphObj& graphObj);


    /**
     * Returns the evaluation mode of the graph. The evaluation mode determines how the graph
     * will be evaluated standalone or when referenced from an OmniGraphAPI component.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return The evaluation mode of the graph
     */
    GraphEvaluationMode(CARB_ABI* getEvaluationMode)(const GraphObj& graphObj);

    /**
     * Sets the evaluation mode of the graph. The evaluation mode determines if the graph
     * will be evaluated standalone or when referenced from an OmniGraphAPI component.
     *
     * @param[in] graphObj Reference to the graph object
     * @param[in] evaluationMode the evaluation mode of the graph to set
     */
    void(CARB_ABI* setEvaluationMode)(const GraphObj& graphObj, GraphEvaluationMode evaluationMode);

    /**
     * Create a new graph, wrapped as a node, at the given location.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] options Options relating to creating a graph as a node.
     * @return The NodeObj representing the node that wraps the graph. The newly created graph can be
     *         retrieved from the node.  In case of failure, the NodeObj will contain kInvalidNodeHandle
     */
    NodeObj(CARB_ABI* createGraphAsNodeV2)(GraphObj& graphObj, const CreateGraphAsNodeOptions& options);

    /**
     * Returns the name of the evaluator for the specified graph
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @return The name of the evaluator, or the empty string if it isn't set.
     */
    const char*(CARB_ABI* getEvaluatorName)(const GraphObj& graphObj);

    /**
     * Returns whether this graph is a compound graph instance. A compound graph is a subgraph that
     * is parented to a compound node
     *
     * @return True if this graph is a compound graph, false otherwise.
     */
    bool(CARB_ABI* isCompoundGraph)(const GraphObj& graphObj);

    /**
     * Returns the number of instance currently allocated for this graph
     *
     * @return The number of instances registered in the graph, 0 if the graph is standalone
     */
    size_t(CARB_ABI* getInstanceCount)(const GraphObj& graphObj);

    /**
     * Returns whether this graph is an auto instance. An auto instance is a graph that got merged as an instance
     * with all other similar graphs in the stage.
     *
     * @return True if this graph is an auto instance, false otherwise.
     */
    bool(CARB_ABI* isAutoInstanced)(const GraphObj& graphObj);

    /**
     * Set whether or not this graph can be candidate for auto-instance merging (true by default)
     *
     * @return The old value of the allowed flag
     */
    bool(CARB_ABI* setAutoInstancingAllowed)(const GraphObj& graphObj, bool allowed);

    /**
     * Returns the compound node for which this graph is the compound subgraph of.
     *
     * @return If this graph is a compound graph, the owning compound node. Otherwise, an invalid node is returned.
     */
    NodeObj(CARB_ABI* getOwningCompoundNode)(const GraphObj& graphObj);

    /**
     * Apply a prim view to a graph. A view is a way to dynamically and automatically manage the list of instances for a graph
     *
     * @return Whether the view has been successfully applied (could fail if graph already have instances for example)
     */
    bool(CARB_ABI* setPrimView)(const GraphObj& graphObj, IPrimViewPtr view);

    /**
     * Returns whether or not a graph meets all the required condition in order to run
     * For example, a graph cannot run if it is disabled, or has invalid/unresolved mappings.
     */
    bool(CARB_ABI* canEvaluate)(const GraphObj& graphObj);

    /**
     * Returns the file format version for any new OmniGraphs created.
     *
     * @returns The file format structure containing the current major and minor version.
     */
    FileFormatVersion(CARB_ABI* getCurrentFileFormatVersion)();

    /**
     * Create a new variable on the graph with the given name. The name must be unique
     * among variables on the graph, even if the type is different.
     *
     * Runtime variables are not backed by USD attributes and are not persistent.
     *
     * @param[in] graphObj Reference to the GraphObj struct representing the graph object
     * @param[in] name The name to give the variable.
     * @param[in] variableType The data type used to create the variable.
     * @param[in] value A pointer to a value of type "variableType". In case the type is an array, value should be a pointer to the base address of the storage.
     * @param[in] size In case the pointed type is an array, the size of the pointed array. Parameter ignored otherwise.
     * @return The newly created variable, or null if the variable could not be created.
     */
    IVariablePtr(CARB_ABI* createRuntimeVariable)(const GraphObj& graphObj, const char* name, Type variableType, void const* value, size_t size);
};

// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IGraph, createRuntimeVariable, 56)

using DataAccessFlags = uint32_t; //!< Data type for specifying read/write access abilities

static constexpr DataAccessFlags kReadAndWrite = 0; //!< Data is accessible for both read and write
static constexpr DataAccessFlags kReadOnly = 1; //!< Data is only accessible for reading
static constexpr DataAccessFlags kWriteOnly = 2; //!< Data is only accessible for writing

// ======================================================================
/** Use this interface to pull data for compute node, and also push data to compute graph/cache */
struct IGraphContext
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::IGraphContext", 3, 9);

    /**
     * Returns the stage id the context is currently attached to
     * @param[in] context structure containing both the interface and underlying object
     * @return the USD stage id
     */
    long int(CARB_ABI* getStageId)(const GraphContextObj& contextObj);

    //---------------------------------------------------------------------------------------------
    // wrappers for fabric

    /** @private Retired - do not use */
    void (CARB_ABI* retired_1)();

    /** @private Retired - do not use */
    void (CARB_ABI* retired_2)();

    /** @private Deprecated - do not use */
    size_t*(CARB_ABI* deprecated_12)(const GraphContextObj&, const AttributeObj&, DataAccessFlags);

    /** @private Deprecated - do not use */
    size_t*(CARB_ABI* deprecated_13)(const GraphContextObj&, const AttributeObj&, DataAccessFlags);

    /** @private Retired - do not use */
    void (CARB_ABI* retired_3)();

    /** @private Retired - do not use */
    void (CARB_ABI* retired_4)();

    /** @private Retired - do not use */
    void (CARB_ABI* retired_5)();

    /** @private Retired - do not use */
    void (CARB_ABI* retired_6)();

    /** @private Retired - do not use */
    void (CARB_ABI* retired_7)();

    /** @private Retired - do not use */
    void (CARB_ABI* retired_8)();

    /**
     * Returns the graph associated with this context
     * @param[in] context structure containing both the interface and underlying object
     * @return GraphObj structure containing the graph
     */
    GraphObj(CARB_ABI* getGraph)(const GraphContextObj& context);

    /**
     * Returns the time between last evaluation of the graph and "now"
     * @param[in] context structure containing both the interface and underlying object
     * @return the elapsed time
     */
    float(CARB_ABI* getElapsedTime)(const GraphContextObj& contextObj);

    /**
     * Returns the global playback time
     * @param[in] context structure containing both the interface and underlying object
     * @return the global playback time in seconds
     */
    float(CARB_ABI* getTime)(const GraphContextObj& contextObj);

    /**
     * Returns the time between last evaluation of the graph and "now", in NS.
     * Note this will only return valid values if the update loop is using the
     * void updateSimStep(int64_t timeNS, carb::tasking::Counter* counter, bool) interface
     * As of this writing, this is limited to the DS project
     *
     * @param[in] context structure containing both the interface and underlying object
     * @return the elapsed time in nano seconds
     */
    int64_t(CARB_ABI* getElapsedTimeNS)(const GraphContextObj& contextObj);

    /**
     * Returns the global time in NS.
     * Note this will only return valid values if the update loop is using the
     * void updateSimStep(int64_t timeNS, carb::tasking::Counter* counter, bool) interface
     * As of this writing, this is limited to the DS project
     *
     * @param[in] context structure containing both the interface and underlying object
     * @return the global time in nano seconds
     */
    int64_t(CARB_ABI* getTimeNS)(const GraphContextObj& contextObj);

    /**
     * Given an attribute, retrieves the default attribute value in system memory
     *
     * @param[in] context structure containing both the interface and underlying object
     * @param[in] attrObj The attribute object for which to retrieve the default value
     * @return the const void pointer to the data
     */
    const void*(CARB_ABI* getDefault)(const GraphContextObj& context, const AttributeObj& attrObj);

    /** @private Deprecated - do not use */
    ConstBundleHandle(CARB_ABI* deprecated_4)(const GraphContextObj&, NodeContextHandle, NameToken);

    /** @private Deprecated - do not use */
    size_t (CARB_ABI* deprecated_5)(const GraphContextObj&, NodeContextHandle, NameToken);

    /** @private Deprecated - do not use */
    void (CARB_ABI* deprecated_6)(const GraphContextObj&,NodeContextHandle,NameToken,ConstBundleHandle*);

    /** @private Deprecated - do not use */
    BundleHandle (CARB_ABI* deprecated_3)(const GraphContextObj& , NodeContextHandle, NameToken);

    /** @private Deprecated - do not use */
    void(CARB_ABI* deprecated_7)(
        ConstAttributeDataHandle*, const GraphContextObj&, NodeContextHandle, const NameToken*, size_t);

    /** @private Deprecated - do not use */
    void(CARB_ABI* deprecated_8)(AttributeDataHandle*, const GraphContextObj&, NodeContextHandle, const NameToken*, size_t);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Deprecated - Use INode::getAttributeCount")
    size_t (CARB_ABI* getAttributesCount)(const GraphContextObj& contextObj, NodeContextHandle node);

    /** @private Deprecated - do not use */
    void(CARB_ABI* deprecated_9)(ConstAttributeDataHandle*, const GraphContextObj&, NodeContextHandle, size_t);

    /** @private Deprecated - do not use */
    void(CARB_ABI* deprecated_10)(AttributeDataHandle*, const GraphContextObj&, NodeContextHandle, size_t);

    /** @private Deprecated - do not use */
    BundleHandle(CARB_ABI* deprecated_11)(const GraphContextObj&, NodeContextHandle, NameToken, ConstBundleHandle);

    /** @private Deprecated - do not use */
    [[deprecated("Use copyBundleContentsInto")]] void (CARB_ABI* copyPrimContentsInto)(const GraphContextObj& contextObj,
                                 BundleHandle destBundleHandle,
                                 ConstBundleHandle sourceBundleHandle);

    /** @private Retired - do not use */
    void(CARB_ABI* retired_10)();

    /** @private Deprecated - do not use */
    [[deprecated("Use clearBundleContents")]] void(CARB_ABI* clearPrimContents)(const GraphContextObj& contextObj, BundleHandle bundleHandle);

    /** @private Retired - do not use */
    void(CARB_ABI* retired_9)();

    /**
     * Returns the global playback time in frames
     * @param[in] context structure containing both the interface and underlying object
     * @return the global playback time in frames
     */
    float(CARB_ABI* getFrame)(const GraphContextObj& contextObj);

    /**
     * Returns the state of global playback
     * @param[in] context structure containing both the interface and underlying object
     * @return true if playback has started, false is playback is stopped
     */
    bool(CARB_ABI* getIsPlaying)(const GraphContextObj& contextObj);

    /**
     * Runs the inspector on the data in the given graph context.
     *
     * @param[in] contextObj The graph context on which the inspector runs
     * @param[in] inspector The inspector class
     * @return true if the inspection ran successfully, false if the inspection type is not supported
     */
    bool(CARB_ABI* inspect)(const GraphContextObj& contextObj, inspect::IInspector* inspector);

    /**
     * Returns the time since the App started
     * @param[in] context structure containing both the interface and underlying object
     * @return the global time since the app started in seconds
     */
    double(CARB_ABI* getTimeSinceStart)(const GraphContextObj& contextObj);

    /**
     * Returns whether the graph context object is still valid or not
     *
     * @param[in] contextObj The context object for which to query
     * @return Whether the context is still valid
     */
    bool(CARB_ABI* isValid)(const GraphContextObj& contextObj);

    /** @private Deprecated - do not use */
    AttributeDataHandle (CARB_ABI* deprecated_0)(const GraphContextObj&, const IVariablePtr&);

    /** @private Deprecated - do not use */
    ConstAttributeDataHandle(CARB_ABI* deprecated_1)(const GraphContextObj&, const IVariablePtr&);

    /**
     * Returns the accumulated total of elapsed times between rendered frames
     * @param[in] contextObj structure containing both the interface and underlying object
     * @return the accumulated total of elapsed times between rendered frames
     */
    double(CARB_ABI* getAbsoluteSimTime)(const GraphContextObj& contextObj);

    /** @private Deprecated - do not use */
    NameToken(CARB_ABI* deprecated_2)(const GraphContextObj&);


    /** Deprecated - do not use - removal scheduled for 106 **/
    [[deprecated("Use registerForUSDWriteBacks")]]
    void(CARB_ABI* registerForUSDWriteBack)(const GraphContextObj& contextObj, BundleHandle bundle, NameToken attrib);

    /**
     * Given a variable and an instance path, returns a handle to access its data.
     *
     * @param[in] contextObj The context object used to find the variable data
     * @param[in] variable The variable to retrieve the data from
     * @param[in] Path to the prim holding an instance of this graph
     *
     * @returns An attribute data handle that can be used to access the variable data.
     *          If the given prim does not contain an instance of the graph, the data handle
     *          returned will be invalid.
     */
    AttributeDataHandle(CARB_ABI* getVariableInstanceDataHandle)(const GraphContextObj& contextObj,
                                                                 const IVariablePtr& variable,
                                                                 const char* instancePrimPath);

    /**
     * Given a variable and an instance path, returns a constant handle to access its data as readonly.
     *
     * @param[in] contextObj The context object used to find the variable data
     * @param[in] variable The variable to retrieve the data from
     * @param[in] Path to the prim holding an instance of this graph
     *
     * @returns An constant attribute data handle that can be used to access the variable data.
     *          If the given prim does not contain an instance of the graph, the data handle
     *          returned will be invalid.
     */
     ConstAttributeDataHandle(CARB_ABI* getVariableInstanceConstDataHandle)(const GraphContextObj& contextObj,
                                                                            const IVariablePtr& variable,
                                                                            const char* instancePrimPath);
    /**
     * Get the Prim path of the graph target.
     *
     * The graph target is defined as the parent Prim of the compute graph, except during
     * instancing - where OmniGraph executes a graph once for each Prim. In the case
     * of instancing, the graph target will change at each execution to be the path of the instance.
     * If this is called outside of graph execution, the path of the graph Prim is returned, or an empty
     * token if the graph does not have a Prim associated with it.
     *
     * @param[in] contextObj The context object used to find the data.
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     *
     * @returns a token representing the path of the graph target primitive.
     */
     NameToken const&(CARB_ABI* getGraphTarget)(const GraphContextObj& contextObj, InstanceIndex instanceIndex);

    /**
     * Given a variable, returns a handle to access its data.
     *
     * @param[in] contextObj The context object used to find the variable data
     * @param[in] variable The variable to retrieve the data from
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     *
     * @returns An attribute data handle that can be used to access the variable data.
     */
    AttributeDataHandle(CARB_ABI* getVariableDataHandle)(const GraphContextObj& contextObj,
                                                         const IVariablePtr& variable,
                                                          InstanceIndex instanceIndex);

    /**
     * Given a variable, returns a constant handle to access its data as readonly.
     *
     * @param[in] contextObj The context object used to find the variable data
     * @param[in] variable The variable to retrieve the data from
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     *
     * @returns A constant attribute data handle that can be used to access the variable data.
     */
    ConstAttributeDataHandle(CARB_ABI* getVariableConstDataHandle)(const GraphContextObj& contextObj,
                                                                   const IVariablePtr& variable,
                                                                   InstanceIndex instanceIndex);
    /** @private Deprecated - do not use */
    [[deprecated("Use getOutputBundle!")]] BundleHandle(CARB_ABI* getOutputPrim)(const GraphContextObj& contextObj,
                                        NodeContextHandle node,
                                        NameToken bundleName,
                                        InstanceIndex instanceIndex);

    /** @private Deprecated - do not use */
    [[deprecated("Use getInputTarget!")]] ConstBundleHandle(CARB_ABI* getInputPrim)(const GraphContextObj& contextObj,
                                            NodeContextHandle node,
                                            NameToken bundleName,
                                            InstanceIndex instanceIndex);

    /** @private Deprecated - do not use */
    [[deprecated("Use getInputTargetCount!")]] size_t(CARB_ABI* getInputPrimCount)(const GraphContextObj& contextObj,
                                        NodeContextHandle node,
                                        NameToken relName,
                                        InstanceIndex instanceIndex);

    /** @private Deprecated - do not use */
    [[deprecated("Use getInputTargets!")]] void(CARB_ABI* getInputPrims)(const GraphContextObj& contextObj,
                                  NodeContextHandle node,
                                  NameToken relName,
                                  ConstBundleHandle* bundleHandles,
                                  InstanceIndex instanceIndex);

    /**
     * Requests some input attributes of the specified compute node in the specified context.
     *
     * If no input attribute with the given name exists on the node, the returned handle
     * will return false from its isValid() function.
     *
     *
     * @param[in/out] attrsOut A pre-allocated array that will be filled with the requested handles
     * @param[in] contextObj The context object used to find the  data
     * @param[in] node The node object to retrieve the data from
     * @param[in] attrNames An array of names of attributes on the given node to retrieve a data handle for
     * @param[in] count The size of the provided arrays (attrName and attrsOut)
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     */
    void(CARB_ABI* getAttributesByNameR)(ConstAttributeDataHandle* attrsOut,
                                         const GraphContextObj& contextObj,
                                         NodeContextHandle node,
                                         const NameToken* attrNames,
                                         size_t count,
                                         InstanceIndex instanceIndex);

    /**
     * Requests some output attributes of the specified compute node in the specified context.
     *
     * If no input attribute with the given name exists on the node, the returned handle
     * will return false from its isValid() function.
     *
     *
     * @param[in/out] attrsOut A pre-allocated array that will be filled with the requested handles
     * @param[in] contextObj The context object used to find the  data
     * @param[in] node The node object to retrieve the data from
     * @param[in] attrNames An array of names of attributes on the given node to retrieve a data handle for
     * @param[in] count The size of the provided arrays (attrName and attrsOut)
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     */
    void(CARB_ABI* getAttributesByNameW)(AttributeDataHandle* attrsOut,
                                         const GraphContextObj& contextObj,
                                         NodeContextHandle node,
                                         const NameToken* attrNames,
                                         size_t count,
                                         InstanceIndex instanceIndex);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Deprecated - use getAttributesByNameR instead")
    void(CARB_ABI* getAttributesR)(ConstAttributeDataHandle* attrsOut,
                                   const GraphContextObj& contextObj,
                                   NodeContextHandle node,
                                   size_t count,
                                   InstanceIndex instanceIndex);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Deprecated - use getAttributesByNameW instead")
    void(CARB_ABI* getAttributesW)(AttributeDataHandle* attrsOut,
                                   const GraphContextObj& contextObj,
                                   NodeContextHandle node,
                                   size_t count,
                                   InstanceIndex instanceIndex);

    /** @private Deprecated - do not use */
    [[deprecated("use copyBundleContentsIntoOutput")]] BundleHandle(CARB_ABI* copyPrimContentsIntoOutput)(
        const GraphContextObj& contextObj,
        NodeContextHandle node,
        NameToken outBundleName,
        ConstBundleHandle sourceBundleHandle,
        InstanceIndex instanceIndex);

    /**
     * Given an attribute of array type, return a pointer to the number of elements in the array
     * If flags is kWriteOnly or kReadAndWrite then writing to the dereferenced pointer resizes the
     * array the next time it is accessed on CPU or GPU
     *
     * @param[in] context structure containing both the interface and underlying object
     * @param[in] attrObj The attribute object for which to retrieve the array size
     * @param[in] flags The data access flags indicating whether the array size is to be R, W, or RW
     * @return the pointer to the array size
     */
    size_t*(CARB_ABI* getArrayAttributeSize)(const GraphContextObj& context,
                                             const AttributeObj& attrObj,
                                             DataAccessFlags flags,
                                             InstanceIndex instanceIndex);

    /**
     * Given an attribute of array type, return a GPU pointer to the number of elements in the array
     * Flags must be kReadOnly, because currently we don't allow GPU code to resize GPU arrays
     * This restriction may be relaxed in the future
     * If you want to resize a GPU array you can do it on the CPU using getArrayAttributeSize
     *
     * @param[in] context structure containing both the interface and underlying object
     * @param[in] attrObj The attribute object for which to retrieve the array size
     * @param[in] flags The data access flags indicating whether the array size is to be R, W, or RW
     * @return the pointer to the array size
     */
    size_t*(CARB_ABI* getArrayAttributeSizeGPU)(const GraphContextObj& context,
                                                const AttributeObj& attrObj,
                                                DataAccessFlags flags,
                                                InstanceIndex instanceIndex);

    /**
     * Requests an output bundle of the specified compute node in the specified context.
     *
     * If no output bundle with the given name exists on the node, the returned handle
     * will return false from its isValid() function.
     *
     * @param[in] contextObj The context object used to find the  data
     * @param[in] node The node object to retrieve the data from
     * @param[in] outputName The name of the attribute on the given node that represent the output bundle
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     *
     * @returns A handle to the requested prim
     */
    BundleHandle(CARB_ABI* getOutputBundle)(const GraphContextObj& contextObj,
                                            NodeContextHandle node,
                                            NameToken outputName,
                                            InstanceIndex instanceIndex);

    /**
     * Requests an input target path of the specified compute node in the specified context.
     *
     * If no input target path with the given name exists on the node, the returned path
     * will return uninitialized path.
     *
     * @param[in] contextObj The context object used to find the  data
     * @param[in] node The node object to retrieve the data from
     * @param[in] inputName The name of the attribute on the given node that represent the input bundle
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     *
     * @returns A path to the requested target
     */
    omni::fabric::PathC(CARB_ABI* getInputTarget)(const GraphContextObj& contextObj,
                                                  NodeContextHandle node,
                                                  NameToken inputName,
                                                  InstanceIndex instanceIndex);

    /**
     * Requests the number of input targets in the relationship with the given name on the
     * specified compute node in the specified context.
     *
     * This returns 0 if no relationship with the given name exists on the node
     * or the relationship is empty.
     *
     * @param[in] contextObj The context object used to find the data
     * @param[in] node The node object to retrieve the data from
     * @param[in] inputName The name of the relationship attribute on the given node that represent the input targets
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     *
     * @returns The number of input targets under the provided relationship
     */
    size_t(CARB_ABI* getInputTargetCount)(const GraphContextObj& contextObj,
                                          NodeContextHandle node,
                                          NameToken inputName,
                                          InstanceIndex instanceIndex);

    /**
     * Fills in the provided targets array with paths to all of the input targets(bundles or primitives)
     * in the relationship with the given name on the specified compute node in the specified context.
     *
     * The caller *must* first call getInputTargetCount to ensure that the targets array will be
     * sufficiently large to receive all of the paths.
     *
     * @param[in] contextObj The context object used to find the data
     * @param[in] node The node object to retrieve the data from
     * @param[in] inputName The name of the relationship attribute on the given node that represent the input targets
     * @param[in,out] targets A pre-sized array that will be filled with the requested paths
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     */
    void(CARB_ABI* getInputTargets)(const GraphContextObj& contextObj,
                                    NodeContextHandle node,
                                    NameToken inputName,
                                    omni::fabric::PathC* targets,
                                    InstanceIndex instanceIndex);

    /**
     * Creates copies of all attributes from sourceBundleHandle in the output bundle
     * with the specified name on the specified node.
     *
     * This function is equivalent to:
     *      BundleHandle retBundle = iContext.getOutputBundle(context, node, outBundleName);
     *      iContext.copyBundleContentsInto(context, retBundle, sourceBundleHandle);
     *      return retBundle;
     * but with a single function pointer call, instead of two.
     *
     * @param[in] contextObj The context object used to find the data
     * @param[in] node The node object to retrieve the data from
     * @param[in] outBundleName The name of the attribute on the given node that represent the output bundle to write to
     * @param[in] sourceBundleHandle A handle to a bundle to copy content from
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     *
     * @returns An handle to the targeted output bundle
     */
    BundleHandle(CARB_ABI* copyBundleContentsIntoOutput)(const GraphContextObj& contextObj,
                                                         NodeContextHandle node,
                                                         NameToken outBundleName,
                                                         ConstBundleHandle sourceBundleHandle,
                                                         InstanceIndex instanceIndex);

    /**
     * Creates copies of all attributes from sourceBundleHandle in the bundle corresponding with destBundleHandle.
     *
     * @param contextObj The context object used to find the data
     * @param destBundleHandle A handle to a bundle to copy content to
     * @param sourceBundleHandle A handle to a bundle to copy content from
     */
    void(CARB_ABI* copyBundleContentsInto)(const GraphContextObj& contextObj,
                                           BundleHandle destBundleHandle,
                                           ConstBundleHandle sourceBundleHandle);

    /**
     * Removes all attributes from the prim corresponding with bundleHandle,
     * but keeps the bundle itself.
     *
     * @param contextObj The context object used to find the data
     * @param bundleHandle A handle to a bundle to clear content from
     */
    void(CARB_ABI* clearBundleContents)(const GraphContextObj& contextObj, BundleHandle bundleHandle);

    /**
     * Register provided attributes for USD write back at the end of the current frame
     *
     *
     * @param[in] contextObj The context object used to find the data.
     * @param[in] handles An array of handles of the attributes that should be written back to usd
     * @param[in] count The size of the provided array
     */
    void(CARB_ABI* registerForUSDWriteBacks)(const GraphContextObj& contextObj, AttributeDataHandle const* handles, size_t count);

    /**
     * Register provided attributes for USD write back at the end of the current frame to a specific layer
     *
     *
     * @param[in] contextObj The context object used to find the data.
     * @param[in] handles An array of handles of the attributes that should be written back to usd
     * @param[in] count The size of the provided array
     * @param[in] layerIdentifier The unique name for the layer to be written
     */
    void(CARB_ABI* registerForUSDWriteBacksToLayer)(const GraphContextObj& contextObj,
                                                    AttributeDataHandle const* handles,
                                                    size_t count,
                                                    NameToken layerIdentifier);

    /**
     * Returns whether or not the graph associated with this context meets all the required condition that allows a
     * user side system (such as OGN databases) to cache its node's attribute pointers returned by the ABIs from frame to frame.
     * Note that when allowed to cache pointers, nodes using such system also need to listen to the various callbacks
     * that can be implemented on the node-type-definition in order to be warned when those pointers needs to be discarded.
     */
    bool(CARB_ABI* canCacheAttributePointers)(const GraphContextObj& graphObj);

    /**
     * Get the Prim path of the graph target.
     *
     * The graph target is defined as the parent Prim of the compute graph, except during
     * instancing - where OmniGraph executes a graph once for each Prim. In the case
     * of instancing, the graph target will change at each execution to be the path of the instance.
     * If this is called outside of graph execution, the path of the graph Prim is returned, or an empty
     * path if the graph does not have a Prim associated with it.
     *
     * @param[in] contextObj The context object used to find the data.
     * @param[in] instanceIndex In vectorized context, the instance index relative to the currently targeted graph
     *
     * @returns a path representing the path of the graph target primitive.
     */
    TargetPath const&(CARB_ABI* getGraphTargetAsPath)(const GraphContextObj& contextObj, InstanceIndex instanceIndex);

    /**
     * Creates copies of all attributes from sourceBundleHandle in the bundle corresponding with destBundleHandle.
     *
     * @param dstFabricId The fabric ID where to copy the data
     * @param destBundleHandle A handle to a bundle to copy content to
     * @param srcFabricId The fabric ID where to locate source data
     * @param sourceBundleHandle A handle to a bundle to copy content from
     */
    void(CARB_ABI* copyBundleContentsIntoWithFabric)(omni::fabric::FabricId dstFabricId,
                                           BundleHandle destBundleHandle,
                                           omni::fabric::FabricId srcFabricId,
                                           ConstBundleHandle sourceBundleHandle);
};

// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IGraphContext, copyBundleContentsIntoWithFabric, 68)

// ==============================================================================================================
//! @private Retired feature - use EF in order to customize execution flow in OG
struct IScheduleNode
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::IScheduleNode", 2, 0);

    /** @private Retired - do not use */
    NodeObj(CARB_ABI* retired)(void*);
};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IScheduleNode, retired, 0)


// ==============================================================================================================
//! @private Retired prototype
struct IDataStealingPrototype
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::IDataStealingPrototype", 1, 1);

    /** @private Retired - do not use */
    bool(CARB_ABI* __retired_0)(const GraphContextObj&,ConstAttributeDataHandle,ConstAttributeDataHandle);
    /** @private Retired - do not use */
    AttributeDataHandle(CARB_ABI* __retired_1)(const GraphContextObj&,ConstAttributeDataHandle );
    /** @private Retired - do not use */
    bool(CARB_ABI* __retired_2)(const GraphContextObj&,ConstBundleHandle,ConstBundleHandle);
    /** @private Retired - do not use */
    BundleHandle(CARB_ABI* __retired_3)(const GraphContextObj&, ConstBundleHandle);
    bool(CARB_ABI* enabled)(const GraphContextObj&);//always false
    /** @private Retired - do not use */
    void(CARB_ABI* __retired_4)(const GraphContextObj&, bool);
};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IDataStealingPrototype, __retired_4, 5)


} // namespace core
} // namespace graph
} // namespace omni
