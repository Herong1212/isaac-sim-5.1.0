// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <cstdint>

// File containing the enums used by OmniGraph. They are context-free and so can be included anywhere

namespace omni {
namespace graph {
namespace core {

// ==============================================================================================================
/** Type of connection between two attributes */
enum ConnectionType
{
    kConnectionType_Regular = 0,  //!< Normal attribute to attribute evaluation connection
    kConnectionType_DataOnly = 1,  //!< Data only connection, not implying evaluation
    kConnectionType_Execution = 2,  //!< Execution type connection, for execution type attributes
    kConnectionType_Bundle [[deprecated("Bundle connection type is deprecated. Use PureRelationship instead!")]] = 3,
    kConnectionType_PureRelationship = 4  //!< Only establish a relationship, no execution or data passed
};

// ==============================================================================================================
/** Extended type of an attribute */
enum ExtendedAttributeType
{
    kExtendedAttributeType_Regular = 0,  //!< No extended type, just a normal strongly typed attribute
    kExtendedAttributeType_Union = 1,   //!< An attribute that could be any one of a specific list of types
    kExtendedAttributeType_Any = 2   //!< An attribute that can be any legal type
};

// ==============================================================================================================
/** Port type of an attribute */
enum AttributePortType
{
    kAttributePortType_Input = 0,  //!< The attribute is an input
    kAttributePortType_Output = 1,  //!< The attribute is an output
    kAttributePortType_State = 2,   //!< The attribute holds state information
    kAttributePortType_Unknown = 3   //!< The port type is currently unknown
};

// ==============================================================================================================
/**
 * The kind of backing for the graph - can be one of FC shared, with history
 * or without history.  The shared FC means the orchestration graph (the graph
 * containing all other graphs as nodes) has a stage with history, and all
 * other global level graphs (which are nodes in this orchestration graph) share
 * this stage with history FC.  The shared FC also applies to subgraphs that share
 * the same FC as their parent graph.  The stage with history setting is self explanatory
 * but note there can only be 1 stage with history currently.  The stage without
 * history uses a separate FC to house the data for the graph
 * The "None" backing type are for orchestration graphs (graphs that hold other graphs
 * as nodes) that don't necessarily need a cache to hold "real" data`
 */
enum GraphBackingType
{
    kGraphBackingType_FabricShared = 0,   //!< Graph backing is a shared copy of Fabric
    kGraphBackingType_FabricWithHistory = 1,  //!< Use the Fabric instantiation that has history
    kGraphBackingType_FabricWithoutHistory = 2,  //!< Use the Fabric instantiation that has no retained history
    kGraphBackingType_Unknown = 3,  //!< Backing type is currently unknown
    kGraphBackingType_None = 4,  //!< There is no backing for the OmniGraph data

    kGraphBackingType_FlatCacheShared = 0,  //!< @private Deprecated, use kGraphBackingType_FabricShared
    kGraphBackingType_FlatCacheWithHistory = 1,  //!< @private Deprecated, use kGraphBackingType_FabricWithHistory
    kGraphBackingType_FlatCacheWithoutHistory = 2,  //!< @private Deprecated, use kGraphBackingType_FabricWithoutHistory
};

// ==============================================================================================================
/**
 * The pipeline stage defines where this graph is going to be used - as part of
 * simulation (before rendering), pre-rendering (after sim but before render), or
 * post-rendering.  Each pipeline stage will have a set of graphs that will
 * be run there.  We use larger numbers for the enums with spaces in between
 * so that other stages can be inserted in the future.  The custom pipeline stage
 * allows for graphs that can be run at any unknown time.
 */
enum GraphPipelineStage
{
    kGraphPipelineStage_Simulation = 10,  //!< The simulation phase, a.k.a. normal evaluation
    kGraphPipelineStage_PreRender = 20,  //!< The preRender phase, run just before Hydra takes over
    kGraphPipelineStage_PostRender = 30,  //!< The postRender phase, run after Hydra finishes
    kGraphPipelineStage_Unknown = 100,  //!< The phase is currently unknown
    kGraphPipelineStage_OnDemand = 200,  //!< The graph evaluates only on demand, not as part of the pipeline

    kGraphPipelineStage_Count = 4 //!< The number of existing pipelines
};

// ==============================================================================================================
/**
 * The graph evaluation mode specifies whether a graph is intended to self-evaluate,
 * or if represents an asset to by evaluated on behalf of a different Prim.
 */
enum class GraphEvaluationMode
{

    //! In Automatic mode, the graph is evaluated as Standalone, unless an OmniGraphAPI interface has a relationship to it,
    //! in which case it is evaluated as Instanced mode.
    Automatic = 0,
    //! In Standalone mode, the graph is evaluated once, with itself as the graph target
    Standalone = 1,
    //! In Instanced mode, the graph is evaluated once for each OmniGraphAPI interface with a relationship to the graph Prim
    //! Graphs that are used as assets should use this mode to prevent standalone execution.
    Instanced = 2
};

// ==============================================================================================================
/**
 * Enum class representing the return value of a function call
 *
 */
enum class FunctionResult : uint8_t
{
    Failure = 0,   //!< The function call failed.
    Success = 1,   //!< The function call succeeded.
    Deferred = 2   //!< The action invoked by the function call has been deferred
};

} // namespace core
} // namespace graph
} // namespace omni
