// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/IFabric.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <omni/fabric/stage/PrimBucketList.h>
#include "Types.h"
#include <stack>

#include <iterator>

namespace omni
{
namespace fabric
{

struct IConnectivity;
class AddedPrimIndices;

//
// Connectivity is the main wrapper on top of the IConnectivity API
// to bring connections into a fabric cache between primitives.

struct Connectivity
{
    using Filter = connectivity::Filter;
    using Algorithm = connectivity::Algorithm;
    using EdgeType = connectivity::EdgeType;
    using EdgeId = connectivity::EdgeId;
    using BakeId = connectivity::BakeId;
    using SelectionId = connectivity::SelectionId;
    using VisitorFunctionPath_t = connectivity::VisitorFunctionPath_t;
    using VisitorFunctionRd_t = connectivity::VisitorFunctionRd_t;
    using VisitorFunctionWr_t = connectivity::VisitorFunctionWr_t;
    using TransformFunctionWr_t = connectivity::TransformFunctionWr_t;
    using ExtentFunctionWr_t = connectivity::ExtentFunctionWr_t;
    using NavigatorFunctionRd_t = connectivity::NavigatorFunctionRd_t;
    using NavigatorFunctionWr_t = connectivity::NavigatorFunctionWr_t;
    using NavigatorParametersRd_t = connectivity::NavigatorParametersRd_t;
    using NavigatorParametersWr_t = connectivity::NavigatorParametersWr_t;
    using PerformanceCounters = connectivity::PerformanceCounters;

    static constexpr const uint64_t kDefaultValue = connectivity::kParentEdgeType;
    static constexpr const uint64_t kDefaultDualValue = connectivity::kParentDualEdgeType;
    static constexpr const uint64_t kDefaultMask = connectivity::kDefaultEdgeMask;

    Connectivity(FabricId fabricId, IConnectivity* capi = nullptr);

    //! @fn void pushConnectionType(uint64_t value, uint64_t dualValue, uint64_t mask = 0xff)
    //! @brief Push a new context of a connection type.
    //! @param value The value stored at the half-edge
    //! @param dualValue The value stored at the dual half-edge
    //! @param mask The mask used to compare values using the following expression is_equal(v1, v2) := (v1 & mask) == (v2 & mask)
    //! @return False on a stack overflow
    //!
    //! @fn void pushConnectionType(const EdgeType type, const EdgeType dualType)
    //! @brief Push a new context of a connection type.
    //! @param typeName The connection type at the half-edge
    //! @param typeName The connection type at the dual half-edge
    //! @return False on a stack overflow
    //!
    //! @fn void pushConnectionType(const Token& typeName, const Token& dualTypeName)
    //! @brief Push a new context of a connection type.
    //! @param typeName The connection type name at the half-edge
    //! @param typeName The connection type name at the dual half-edge
    //! @return False on a stack overflow
    //!
    //! @fn void popConnectionType(unsigned n=1)
    //! @brief Restore a connection type context
    //! @param n Amount of contexts to pop
    //!
    //! @fn void swapConnectionType()
    //! @brief Swap the value and the dual value in the current connection type
    //!
    //! @fn void resetConnectionType()
    //! @brief Reset the stack and the context to default parent/child connection types
    //!
    //! @fn void currentConnectionTypeValue()
    //! @return The value of the current connection type
    //!
    //! @fn void currentConnectionTypeDualValue()
    //! @return The dual value of the current connection type
    //!
    //! @fn void currentConnectionTypeMask()
    //! @return The mask of the current connection type

    bool pushConnectionType(uint64_t value, uint64_t dualValue, uint64_t mask = 0xff);
    bool pushConnectionType(const EdgeType type, const EdgeType dualType);
    bool pushConnectionType(const Token& typeName, const Token& dualTypeName);
    void popConnectionType(unsigned n=1);
    void swapConnectionType();
    void resetConnectionType();
    uint64_t currentConnectionTypeValue() const;
    uint64_t currentConnectionTypeDualValue() const;
    uint64_t currentConnectionTypeMask() const;

    //! @fn EdgeType setType(FabricId fabricId, const Token& typeName)
    //! @brief Register the type of a named connection. A connection name could be be registered more than one time. Check the connectivity::StdEdgeType enum for a short list of the standard edge types always pre-registered.
    //! @param typeName The connection type name
    //! @return The numerical value of the associated connection type name
    //!
    //! @fn Token getTypeName(FabricId fabricId, EdgeType type)
    //! @brief Returns the connection name associated to the given type value.
    //! @param type The numerical value of a connection type
    //! @return The name of the associated connection type

    EdgeType setType(const Token& typeName);
    TokenC getTypeName(EdgeType type);

    //! @fn EdgeId connect(FabricId fabricId, const Path& src, const Path& dst)
    //! @brief Connect the src and dst prims using the current connection type informations (see the pushConnectionType function)
    //! @return The identifier of the half-edge src->dst
    //!
    //! @fn EdgeId connectIfNot(FabricId fabricId, const Path& src, const Path& dst)
    //! @brief Connect the src and dst prims, if not already connected, using the current connection type (see the pushConnectionType function)
    //! @param[out] outAlreadyConnected True if the 2 prims were already connected with the current connection type.
    //! @return The identifier of the half-edge src->dst

    EdgeId connect(const Path& src, const Path& dst);
    EdgeId connectIfNot(const Path& src, const Path& dst, bool* outAlreadyConnected=nullptr);

    //! @fn EdgeId disconnect(const Path& path1, const Path& path2)
    //! @brief Disconnect two prims based on the end points and the value stored into the connection. The first occurrence found is removed.
    //! @param src The path of the source prim
    //! @param dst The path of the destination prim
    //! @return True if a connnection has been found and removed
    //!
    //! @fn EdgeId disconnectSource(const Path& src)
    //! @brief Disconnect two prims based on the source end point and the current connection type (see the pushConnectionType function). The first occurrence found is removed.
    //! @param src The path of the source prim
    //! @return True if a connnection has been found and removed

    bool disconnect(const Path& path1, const Path& path2);
    bool disconnectSource(const Path& src);

    //! @fn bool disconnectEdge(EdgeId eid)
    //! @brief Remove a connection of a given id
    //! @param eid the connection identifier
    //! @return True if the connection has been removed
    //!
    //! @fn bool disconnectEdges(SelectionId sid)
    //! @brief Remove a selection of connections.
    //! @param sid The selection identifier
    //! @return True if at least one connection has been removed

    bool disconnectEdge(EdgeId eid);
    bool disconnectEdges(SelectionId sid);

    //! @fn size_t sumDegree(const Path& path)
    //! @brief Calculates the degree (or valency) in the neighborhood of a prim considering all the outoing connections.
    //! @param path Path of the prim
    //! @return Amount of connections in the neighborhood of a prim
    //!
    //! @fn size_t countDegree(const Path& path)
    //! @brief Calculates the degree (or valency) in the neighborhood of a prim considering only the outgoing connections matching the current connection type (see the pushConnectionType function).
    //! @param path Path of the prim
    //! @param value Path of the prim
    //! @return Amount of connections in the neighborhood of a prim matching the given value

    size_t sumDegree(const Path& path);
    size_t countDegree(const Path& path);

    //! @fn EdgeId getFirstEdge(const Path& path)
    //! @brief Retrieves the first outgoing connection of a prim
    //! @param path Path of the prim
    //! @return Returns an edge identifier if the prim is connected or kInvalidEdgeId if not.
    //!
    //! @fn EdgeId findFirstEdge(const Path& path)
    //! @brief Finds the first connection from a path matching the current connection type (see the pushConnectionType function)
    //! @param path The path of the prim
    //! @return The identifier of the edge or kInvalidEdgeId
    //!
    //! @fn EdgeId findEdge(const Path& src, const Path& dst)
    //! @brief Finds the connection between two prims matching the current connection type (see the pushConnectionType function)
    //! @param src The path of the source prim
    //! @param dst The path of the target prim
    //! @return The identifier of the edge or kInvalidEdgeId

    EdgeId getFirstEdge(const Path& path);
    EdgeId findFirstEdge(const Path& path);
    EdgeId findEdge(const Path& src, const Path& dst);

    //! @fn bool isValid(EdgeId eid)
    //! @brief Checks if a connection is value
    //! @param eid Identifier of the connection
    //! @return True if the connection exists

    bool isValid(EdgeId eid);

    //! @fn Path getSource(EdgeId eid)
    //! @brief Retrieves the source endpoint of a connection
    //! @param eid The identifier of the connection
    //! @return Path of the prim or kUninitializedPath
    //!
    //! @fn Path getTarget(EdgeId eid)
    //! @brief Retrieves the destination endpoint of a connection
    //! @param eid The identifier of the connection
    //! @return Path of the prim or kUninitializedPath
    //!
    //! @fn EdgeId getDual(EdgeId eid)
    //! @brief Retrieves the dual connection of a connection
    //! @param eid The identifier of the connection
    //! @return The identifier of the dual connection
    //!
    //! @fn EdgeId getNext(EdgeId eid)
    //! @brief Retrieves the outgoing connection following a given connection in the neighborhood of a prim
    //! @param eid The identifier of the connection
    //! @return The identifier of the next outgoing connection
    //!
    //! @fn uint64_t getEdgeValue(EdgeId eid)
    //! @brief Retrieves the value stored into a connection
    //! @param eid The identifier of the connection
    //! @return The value stored into the connection
    //!
    //! @fn void setEdgeValue(EdgeId eid, uint64_t v)
    //! @brief Stores a value into a connection
    //! @param eid The identifier of the connection
    //! @param v The value to store

    PathC getSource(EdgeId eid);
    PathC getTarget(EdgeId eid);
    EdgeId getDual(EdgeId eid);
    EdgeId getNext(EdgeId eid);
    uint64_t getEdgeValue(EdgeId eid);
    void setEdgeValue(EdgeId eid, uint64_t v);

    //! @fn EdgeId getNextAtSource(EdgeId eid)
    //! @brief Retrieves the connection following a given connection in the neighborhood of the source endpoint
    //! @param eid The identifier of the connection
    //! @return The identifier of the next connection
    //!
    //! @fn EdgeId getNextAtTarget(EdgeId eid)
    //! @brief Retrieves the connection following a given connection in the neighborhood of the destination endpoint
    //! @param eid The identifier of the connection
    //! @return The identifier of the next connection
    //!
    //! @fn EdgeId getNextAtSourceWithin(EdgeId eid, SelectionId sid)
    //! @brief Retrieves the connection following a given connection in the neighborhood of the source endpoint and existing in a selection
    //! @param eid The identifier of the connection
    //! @param sid The selection identifier
    //! @return The identifier of the next connection
    //!
    //! @fn EdgeId getNextAtTargetWithin(EdgeId eid, SelectionId sid)
    //! @brief Retrieves the connection following a given connection in the neighborhood of the destination endpoint and existing in a selection
    //! @param eid The identifier of the connection
    //! @param sid The selection identifier
    //! @return The identifier of the next connection

    EdgeId getNextAtSource(EdgeId eid);
    EdgeId getNextAtTarget(EdgeId eid);
    EdgeId getNextAtSourceWithin(EdgeId eid, SelectionId sid);
    EdgeId getNextAtTargetWithin(EdgeId eid, SelectionId sid);

    //! @fn EdgeId findNextAtSource(EdgeId eid)
    //! @brief Finds the next connection in the neighborhood of the source endpoint matching the current connection selection
    //! @param eid Identifier of the connection to start with
    //! @return The identifier of the next connection
    //!
    //! @fn EdgeId findNextAtTarget(EdgeId eid)
    //! @brief Finds the next connection in the neighborhood of the target endpoint matching the current connection selection
    //! @param eid Identifier of the connection to start with
    //! @return The identifier of the next connection
    //!
    //! @fn EdgeId findNextAtSourceWithin(EdgeId eid, const SelectionId sid)
    //! @brief Finds the next connection in the neighborhood of the source endpoint matching the current connection selection and existing in a selection
    //! @param eid Identifier of the connection to start with
    //! @param sid Identifier of the selection
    //! @return The identifier of the next connection
    //!
    //! @fn EdgeId findNextAtTargetWithin(EdgeId eid, const SelectionId sid)
    //! @brief Finds the next connection in the neighborhood of the target endpoint matching the current connection selection and existing in a selection
    //! @param eid Identifier of the connection to start with
    //! @param sid Identifier of the selection
    //! @return The identifier of the next connection

    EdgeId findNextAtSource(EdgeId eid);
    EdgeId findNextAtTarget(EdgeId eid);
    EdgeId findNextAtSourceWithin(EdgeId eid, const SelectionId sid);
    EdgeId findNextAtTargetWithin(EdgeId eid, const SelectionId sid);

    //! @fn BakeId bakeBegin()
    //! @brief Begins a working session allowing the construction of selections of existing prims, attributes and connections
    //! @return The identifier of the baking session
    //!
    //! @fn SelectionId bakeSelectAttributes(BakeId bakeId, const Filter& any)
    //! @brief Builds a selection of attributes from a filter.
    //!        A baked selection needs to be exported (see bakeExport) to survive to the working session.
    //! @param bakeId Identifier of the working session
    //! @param any A component is selected if it matches at least one of the filtering parameters.
    //! @return The identifier of the constructed selection
    //!
    //! @fn SelectionId bakeSelectPrims(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none)
    //! @brief Builds a selection of prims matching a combination of 3-steps criteria. Primitives passing successfully the 3 steps are selected.
    //!        A baked selection needs to be exported (see bakeExport) to survive to the baking session.
    //! @param bakeId Identifier of the baking session
    //! @param all A component passes this filtering step if it matches all the parameters.
    //! @param any A component passes this filtering step if it matches any of the parameters.
    //! @param none A component passes this filtering step if it matches none of the parameters.
    //! @return The identifier of the constructed selection
    //!
    //! @fn SelectionId bakeSelectBuckets(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none)
    //! @brief Builds a selection of buckets matching a combination of 3-steps criteria. Buckets passing successfully the 3 steps are selected.
    //!        A baked selection needs to be exported (see bakeExport) to survive to the baking session.
    //! @param bakeId Identifier of the baking session
    //! @param all A component passes this filtering step if it matches all the parameters.
    //! @param any A component passes this filtering step if it matches any of the parameters.
    //! @param none A component passes this filtering step if it matches none of the parameters.
    //! @return The identifier of the constructed selection
    //!
    //! @fn SelectionId bakeSelectEdges(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none)
    //! @brief Builds a selection of edges matching a combination of 3-steps criteria. Edges passing successfully the 3 steps are selected.
    //!        A baked selection needs to be exported (see bakeExport) to survive to the baking session.
    //! @param bakeId Identifier of the baking session
    //! @param all A component passes this filtering step if it matches all the parameters.
    //! @param any A component passes this filtering step if it matches any of the parameters.
    //! @param none A component passes this filtering step if it matches none of the parameters.
    //! @return The identifier of the constructed selection
    //!
    //! @fn SelectionId bakeSelectNetwork(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none)
    //! @brief Builds a selection of edges matching a combination of 3-steps criteria. Edges passing successfully the 3 steps are selected as well as all the edges in the same network.
    //!        A baked selection needs to be exported (see bakeExport) to survive to the baking session.
    //! @param bakeId Identifier of the baking session
    //! @param all A component passes this filtering step if it matches all the parameters.
    //! @param any A component passes this filtering step if it matches any of the parameters.
    //! @param none A component passes this filtering step if it matches none of the parameters.
    //! @return The identifier of the constructed selection
    //!
    //! @fn SelectionId bakeUnion(SelectionId augend, SelectionId addend)
    //! @brief Builds a selection merging the components of 2 selections.
    //!        A baked selection needs to be exported (see bakeExport) to survive to the working session.
    //! @param augend Identifier of a selection
    //! @param addend Identifier of a selection
    //! @param Returns a selection with the components belonging to augend or addend
    //!
    //! @fn SelectionId bakeDifference(SelectionId minuend, SelectionId subtrahend)
    //! @brief Builds a selection corresponding to the difference of 2 selections.
    //!        A baked selection needs to be exported (see bakeExport) to survive to the working session.
    //! @param minuend Identifier of a selection
    //! @param subtrahend Identifier of a selection
    //! @param Returns a selection with the components belonging to minuend and not to subtrahend
    //!
    //! @fn SelectionId bakeIntersection(SelectionId intersecer, SelectionId intersecand)
    //! @brief Builds a selection corresponding to the intersection of 2 selections.
    //!        A baked selection needs to be exported (see bakeExport) to survive to the working session.
    //! @param intersecer Identifier of a selection
    //! @param intersecand Identifier of a selection
    //! @param Returns a selection with the components belonging to intersecer and intersecand
    //!
    //! @fn SelectionId bakeDisjunction(SelectionId disjuncer, SelectionId disjuncand)
    //! @brief Builds a selection corresponding to the disjunction of 2 selections.
    //!        A baked selection needs to be exported (see bakeExport) to survive to the working session.
    //! @param disjuncer Identifier of a selection
    //! @param disjuncand Identifier of a selection
    //! @param Returns a selection with the components belonging to disjuncer or disjuncer but not to both
    //!
    //! @fn void bakePack(SelectionId sid)
    //! @brief Optimizes the storage of a selection.
    //! @param sid Identifier of a selection
    //!
    //! @fn void bakeExport(SelectionId sid)
    //! @brief Exports a selection outside of the working session.
    //!        Not exported selections are automatically destroyed at the closing of the working session on a call to bakeEnd().
    //! @param sid Identifier of a selection
    //!
    //! @fn void bakeEnd(BakeId bakeId)
    //! @brief Close the working session and destroy all the non-exported selections.
    //! @param bakeId The identifier of the working session

    BakeId bakeBegin();
    SelectionId bakeSelectAttributes(BakeId bakeId, const Filter& any);
    SelectionId bakeSelectPrims(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none);
    SelectionId bakeSelectBuckets(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none);
    SelectionId bakeSelectEdges(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none);
    SelectionId bakeSelectNetwork(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none);
    SelectionId bakeUnion(SelectionId augend, SelectionId addend); // augend + addend
    SelectionId bakeDifference(SelectionId minuend, SelectionId subtrahend); // minuend − subtrahend
    SelectionId bakeIntersection(SelectionId intersecer, SelectionId intersecand); // intersecer ^ intersecand
    SelectionId bakeDisjunction(SelectionId disjuncer, SelectionId disjuncand); // disjunctive union
    void bakePack(SelectionId sid);
    void bakeExport(SelectionId sid);
    void bakeEnd(BakeId bakeId);

    //! @fn size_t retain(SelectionId sid)
    //! @brief Increment the internal reference counter of a selection
    //! @param sid Identifier of the selection
    //! @return The new value of the reference counter. This value is > 1
    //!
    //! @fn size_t release(SelectionId sid)
    //! @brief Decrements the internal reference counter of a selection
    //! @param sid Identifier of the selection
    //! @return The new value of the reference counter. A value of 0 indicates the selection has be destroyed.
    //!
    //! @fn bool isUndefined(SelectionId sid)
    //! @brief Checks if the content of a given selection is still valid or became undefined following data changes in the associated cache.
    //! @param sid Identifier of the selection
    //! @return True is the content of the selection is invalid and should be updated.
    //!
    //! @fn size_t getMemUsage(SelectionId sid)
    //! @brief Calculate the total memory footprint of a selection in bytes. This amount includes the memory used for caching, if existing.
    //! @param sid Identifier of the selection
    //! @return The memory usage in bytes.
    //!
    //! @fn void invalidate(SelectionId sid)
    //! @brief Manually invalidate the selection.
    //! @param sid Identifier of the selection
    //!
    //! @fn void invalidateAll()
    //! @brief Manually invalidate all selections

    size_t retain(SelectionId sid);
    size_t release(SelectionId sid);
    bool isUndefined(SelectionId sid);
    size_t getMemUsage(SelectionId sid);
    void invalidate(SelectionId sid);
    void invalidateAll();

    //! @fn bool pathExistsIn(SelectionId sid, const Path& path)
    //! @brief Checks if a prim exists in a selection
    //! @param sid Identifier of the selection
    //! @param path Path of the prim
    //! @return True if the prim belongs to the selection
    //!
    //! @fn bool edgeExistsIn(SelectionId sid, EdgeId eid)
    //! @brief Checks if a connection exists in a selection
    //! @param sid Identifier of the selection
    //! @param eid Identifier of the connection
    //! @return True if the connection belongs to the selection

    bool pathExistsIn(SelectionId sid, const Path& path);
    bool edgeExistsIn(SelectionId sid, EdgeId eid);

    //! @fn void includeEdge(SelectionId sid, EdgeId eid)
    //! @brief Add a connection to a selection if the connection is not already in the selection
    //! @param sid Identifier of the selection
    //! @param eid Identifier of the connection
    //!
    //! @fn void excludeEdge(SelectionId sid, EdgeId eid)
    //! @brief Remove a connection to a selection
    //! @param sid Identifier of the selection
    //! @param eid Identifier of the connection

    void includeEdge(SelectionId sid, EdgeId eid);
    void excludeEdge(SelectionId sid, EdgeId eid);

    //! @fn size_t countPrims(SelectionId sid)
    //! @brief Count the amount of prims in a given selection
    //! @param sid Identifier of the selection
    //! @return The amount of prims in the selection
    //!
    //! @fn size_t countAttributes(SelectionId sid)
    //! @brief Count the amount of attributes in a given selection
    //! @param sid Identifier of the selection
    //! @param path Root prim to start the visit from
    //! @return The amount of attributes in the selection
    //!
    //! @fn size_t countBuckets(SelectionId sid)
    //! @brief Count the amount of buckets in a given selection
    //! @param sid Identifier of the selection
    //! @return The amount of buckets in the selection
    //!
    //! @fn size_t countEdges(SelectionId sid)
    //! @brief Count the amount of edges in a given selection
    //! @param sid Identifier of the selection
    //! @return The amount of edges in the selection

    size_t countPrims(SelectionId sid);
    size_t countAttributes(SelectionId sid);
    size_t countBuckets(SelectionId sid);
    size_t countEdges(SelectionId sid);

    //! @fn PathC findRoot(const Path& prim)
    //! @brief Find the top level root prim of a prim
    //!
    //! @fn size_t findEdgesToRoot(Span<Edge> edges, const Path& prim)
    //! @brief Find all edges composing the path from a prim to its top level root prim
    //!
    //! @fn size_t findPrimsToRoot(Span<PathC> ancestors, const Path& prim)
    //! @brief Find all the ancestors of a prim
    //!
    //! @fn size_t removeDescendants(Span<PathC> outReducedList, Span<const Path> inList)
    //! @brief Remove the prims which have an ancestor in the same list. This is a reduction operation
    //!
    //! @fn size_t reduceChangeList(Span<PathC> outReducedList, ListenerId listener, Span<const PathC> inExcludeList, Span<const PathC> inIncludeList, size_t max_amount)
    //! @brief Combine multiple lists of prims in a single one and reduce it to a maximum amount.
    //! @param outReducedList The output reduced list with no more elements than the size of this list.
    //! @param listener Implicit base working list of modified prims
    //! @param inExcludeList List of prims to exclude from the base working list
    //! @param inIncludeList List of prims to include into the base working list
    //! @return The amount of effective elements stored in the output list outReducedList.

    PathC findRoot(const Path& prim);
    size_t findEdgesToRoot(Span<EdgeId> edges, const Path& prim);
    size_t findPrimsToRoot(Span<PathC> ancestors, const Path& prim);
    size_t removeDescendants(Span<PathC> outReducedList, Span<const Path> inList);
    size_t reduceChangeList(Span<PathC> outReducedList, ListenerId listener, Span<const PathC> inExcludeList, Span<const PathC> inIncludeList);

    //! @fn size_t visitPaths(VisitorFunctionRd_t visitor, void* userData)
    //! @brief Visits all the paths of the prims
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited primitives
    //!
    //! @fn size_t visitRd(SelectionId attributes, const Path& tree, VisitorFunctionRd_t visitor, void* userData)
    //! @brief Visits the connections composing a tree of prims while exposing a selection of attributes for reading only.
    //!        A visiting traversal is a limited optimized traversal implementing a fast pre-visit DFS.
    //!        See the navigation traversal offering more control at the cost of a reduced execution speed.
    //! @param attributes Selection of attributes to expose
    //! @param tree Path to the top root prim defining a tree. The whole tree will be cached for optimal performances.
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t visitWr(SelectionId attributes, const Path& tree, VisitorFunctionWr_t visitor, void* userData)
    //! @brief Visits the connections composing a tree of prims while exposing a selection of attributes for reading and writing.
    //!        A visiting traversal is a limited optimized traversal implementing a fast pre-visit DFS.
    //!        See the navigation traversal offering more control at the cost of a reduced execution speed.
    //! @param attributes Selection of attributes to expose
    //! @param tree Path to the top root prim defining a tree. The whole tree will be cached for optimal performances.
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t visitParallelRd(SelectionId attributes, const Path& tree, VisitorFunctionRd_t visitor, void* userData)
    //! @brief Visits the connections similarly to the visitRd call except that the visitor function is executed in parallel on multiple cores.
    //! @param attributes Selection of attributes to expose
    //! @param tree Path to the top root prim defining a tree. The whole tree will be cached for optimal performances.
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t visitParallelWr(SelectionId attributes, const Path& tree, VisitorFunctionWr_t visitor, void* userData)
    //! @brief Visits the connections similarly to the visitWr call except that the visitor function is executed in parallel on multiple cores.
    //! @param attributes Selection of attributes to expose
    //! @param tree Path to the top root prim defining a tree. The whole tree will be cached for optimal performances.
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t visitFromRd(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionRd_t visitor, void* userData)
    //! @brief Visits the connections composing a tree of prims while exposing a selection of attributes for reading only.
    //!        A visiting traversal is a limited optimized traversal implementing a fast pre-visit DFS.
    //!        See the navigation traversal offering more control at the cost of a reduced execution speed.
    //! @param attributes Selection of attributes to expose
    //! @param tree Path to the top root prim defining a tree. The whole tree will be cached for optimal performances.
    //! @param start Prim to start the visit from. The start prim could be the root prim or a child.
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t visitFromWr(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionWr_t visitor, void* userData)
    //! @brief Visits the connections composing a tree of prims while exposing a selection of attributes for reading and writing.
    //!        A visiting traversal is a limited optimized traversal implementing a fast pre-visit DFS.
    //!        See the navigation traversal offering more control at the cost of a reduced execution speed.
    //! @param attributes Selection of attributes to expose
    //! @param tree Path to the top root prim defining a tree. The whole tree will be cached for optimal performances.
    //! @param start Prim to start the visit from. The start prim could be the root prim or a child.
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t rvisitFromRd(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionRd_t visitor, void* userData)
    //! @brief Reversed-order visit of the connections composing a tree of prims while exposing a selection of attributes for reading only.
    //!        A reversed visiting traversal is a limited optimized traversal implementing a fast post-visit DFS.
    //!        See the navigation traversal offering more control at the cost of a reduced execution speed.
    //! @param attributes Selection of attributes to expose
    //! @param tree Path to the top root prim defining a tree. The whole tree will be cached for optimal performances.
    //! @param start Prim to start the visit from. The start prim could be the root prim or a child.
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t rvisitFromWr(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionWr_t visitor, void* userData)
    //! @brief Reversed-order visit of the connections composing a tree of prims while exposing a selection of attributes for reading and writing.
    //!        A reversed visiting traversal is a limited optimized traversal implementing a fast post-visit DFS.
    //!        See the navigation traversal offering more control at the cost of a reduced execution speed.
    //! @param attributes Selection of attributes to expose
    //! @param tree Path to the top root prim defining a tree. The whole tree will be cached for optimal performances.
    //! @param start Prim to start the visit from. The start prim could be the root prim or a child.
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t visitParallelFromRd(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionRd_t visitor, void* userData)
    //! @brief Visits the connections similarly to the visitRd call except that the visitor function is executed in parallel on multiple cores.
    //! @param attributes Selection of attributes to expose
    //! @param tree Path to the top root prim defining a tree. The whole tree will be cached for optimal performances.
    //! @param start Prim to start the visit from. The start prim could be the root prim or a child.
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t visitParallelFromWr(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionWr_t visitor, void* userData)
    //! @brief Visits the connections similarly to the visitWr call except that the visitor function is executed in parallel on multiple cores.
    //! @param attributes Selection of attributes to expose
    //! @param tree Path to the top root prim defining a tree. The whole tree will be cached for optimal performances.
    //! @param start Prim to start the visit from. The start prim could be the root prim or a child.
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t visitMappingRd(SelectionId attributes, SelectionId domain, VisitorFunctionRd_t visitor, void* userData)
    //! @brief Visit the connections mapping a domain of prims to a range of other prims.
    //! @param attributes Selection of read-only attributes to expose
    //! @param domain Set of prims defining the source domain of the mapping
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t visitMappingWr(SelectionId attributes, SelectionId domain, VisitorFunctionWr_t visitor, void* userData)
    //! @brief Visit the connections mapping a domain of prims to a range of other prims.
    //! @param attributes Selection of writable attributes to expose
    //! @param domain Set of prims defining the source domain of the mapping
    //! @param visitor User functor used to access the components
    //! @param userData User parameter passed to the functor
    //! @return Amount of visited connections
    //!
    //! @fn size_t navigateRd(const NavigatorParametersRd_t& params)
    //! @brief Navigates the connections composing a tree of prims while accessing for reading only the source and target attributes.
    //!        A navigation offers more control than a simple visit, at the cost of a bit slower traversal.
    //! @param NavigatorParametersRd_t The navigation parameters.
    //! @return Amount of visited connections
    //!
    //! @fn size_t navigateWr(const NavigatorParametersWr_t& params)
    //! @brief Navigates the connections composing a tree of prims while accessing the source and target attributes.
    //!        A navigation offers more control than a simple visit, at the cost of a bit slower traversal.
    //! @param NavigatorParametersRd_t The navigation parameters.
    //! @return Amount of visited connections

    size_t visitPaths(VisitorFunctionPath_t visitor, void* userData = nullptr);
    size_t visitRd(SelectionId attributes, const Path& tree, VisitorFunctionRd_t visitor, void* userData = nullptr);
    size_t visitWr(SelectionId attributes, const Path& tree, VisitorFunctionWr_t visitor, void* userData = nullptr);
    size_t visitParallelRd(SelectionId attributes, const Path& tree, VisitorFunctionRd_t visitor, void* userData = nullptr);
    size_t visitParallelWr(SelectionId attributes, const Path& tree, VisitorFunctionWr_t visitor, void* userData = nullptr);
    //
    size_t visitFromRd(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionRd_t visitor, void* userData = nullptr);
    size_t visitFromWr(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionWr_t visitor, void* userData = nullptr);
    size_t rvisitFromRd(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionRd_t visitor, void* userData = nullptr);
    size_t rvisitFromWr(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionWr_t visitor, void* userData = nullptr);
    size_t visitParallelFromRd(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionRd_t visitor, void* userData = nullptr);
    size_t visitParallelFromWr(SelectionId attributes, const Path& tree, const Path& start, VisitorFunctionWr_t visitor, void* userData = nullptr);
    size_t transformFromWr(SelectionId attributes, const Path& tree, const Span<const Path> starts, TransformFunctionWr_t visitor, void* userData = nullptr);
    size_t extentFromWr(SelectionId attributes, const Path& tree, const Span<const Path> starts, ExtentFunctionWr_t visitor, void* userData = nullptr);
    //
    size_t visitMappingRd(SelectionId attributes, SelectionId domain, VisitorFunctionRd_t visitor, Algorithm algorith=Algorithm::DefaultMapping, void* userData = nullptr);
    size_t visitMappingWr(SelectionId attributes, SelectionId domain, VisitorFunctionWr_t visitor, Algorithm algorith=Algorithm::DefaultMapping, void* userData = nullptr);
    size_t navigateWr(const NavigatorParametersWr_t& params);
    size_t navigateRd(const NavigatorParametersRd_t& params);

    //! @fn PerformanceCounters* runtimePerfCounters()
    //! @brief Return a table of internal performance counters
    //! @return Pointer on the counters table
    //!
    //! @fn void runtimeClearQueryCache()
    //! @brief Clean up an internal cache dedicated to speed up some queries to the connectivity API.
    //!
    //! @fn size_t runtimeReserveQueryCache(size_t capacity)
    //! @brief Change the capacity of the cache of queries.
    //! @param capacity The requested new cache capacity.
    //! @return The capacity of the cache after the request. The cache can only grow in capacity.
    //!         Requesting a capacity smaller than the current one has no effect.
    //!         By requesting a new capacity of 0, one can probe the current capacity of the cache.

    PerformanceCounters* runtimePerfCounters();
    void runtimeClearQueryCache();
    size_t runtimeReserveQueryCache(size_t capacity);

    //! @fn size_t getDataRevision()
    //! @brief Return the revision number incremented with changes on connectivity information.
    //! @return The revision number. This number overflows on size_t limit. Check for equality only.
    //!
    //! @fn size_t getDataId()
    //! @brief Connectivity instances with same IDs are shared.
    //! @return A comparable number identifying the connectivity data in memory.

    size_t getDataRevision();
    size_t getDataId();

protected:
    IConnectivity* capi = nullptr;
    FabricId fabricId = kInvalidFabricId;
    uint64_t value[4] = { kDefaultValue };
    uint64_t dualValue[4] = { kDefaultDualValue };
    uint64_t mask[4] = { kDefaultMask };
    unsigned top = 0;
};

//
// USDHierarchy is a specialized wrapper on top of the IConnectivity API
// dealing only with default parent/child relationship as defined
// by the connection type (connectivity::kParentEdgeType, connectivity::kChildEdgeType)

struct USDHierarchy
{
    using EdgeId = connectivity::EdgeId;
    USDHierarchy() {};
    USDHierarchy(FabricId fabricId, IConnectivity* capi = nullptr);

    //! @fn EdgeId connectToParent(const Path& child, const Path& parent)
    //! @brief Connect a prim to a parent using a default connection name
    //! @param child Path of the child prim
    //! @param parent Path of the parent prim
    //! @return Identifier of the connection
    //!
    //! @fn EdgeId connectToCanonicalParent(const Path& child)
    //! @brief Connect a prim to its canonical parent retrieved using USD Path.GetParent()
    //! @param child Path of the child prim
    //! @return Identifier of the connection
    //!
    //! @fn size_t connectAllToCanonicalParent()
    //! @brief Connect all the prims to their respective cannonical parents
    //! @param[out] outAmountVisited Stores the amount of visited primitives
    //! @param[out] outAmountConnected Stores the amount of connected primitives
    //! @return Amount of new connections
    //!
    //! @fn size_t connectAllToCanonicalParent(const AddedPrimIndices& addedPrims)
    //! @brief Connect the prims of a given set to their respective cannonical parents
    //! @param[out] outAmountVisited Stores the amount of visited primitives
    //! @param[out] outAmountConnected Stores the amount of connected primitives
    //! @return Amount of new connections
    //!
    //! @fn bool disconnectFromParent(const Path& child)
    //! @brief Disconnect a prim to its parent according to a default connection name.
    //! @param child Path of the child prim
    //! @return True if the existing connection has been removed

    EdgeId connectToParent(const Path& child, const Path& parent);
    EdgeId connectToCanonicalParent(const Path& child);
    void connectAllToCanonicalParent(size_t* outAmountVisited=nullptr, size_t* outAmountConnected = nullptr);
    void connectAllToCanonicalParent(ChangedPrimBucketList& changedList, size_t* outAmountVisited = nullptr, size_t* outAmountConnected = nullptr);
    bool disconnectFromParent(const Path& child);

    //! @fn Path getParent(const Path& path)
    //! @brief Returns the canonical parent of a prim
    //! @param path Path of a prim
    //! @return Path of the parent.
    //!
    //! @fn Path getTopParent(const Path& path)
    //! @brief Returns the top canonical parent of a prim
    //! @param path Path of a prim
    //! @return Path of the top parent.
    //!
    //! @fn Path getFirstChild(const Path& path)
    //! @brief Returns the first child of a prim
    //! @param path Path of a prim
    //! @return Path of the first child.
    //!
    //! @fn Path getNextSibling(const Path& path)
    //! @brief Returns the next sibling of a prim
    //! @param path Path of a prim
    //! @return Path of the next sibling. The next sibling of the last child if the first child.

    PathC getParent(const Path& path);
    PathC getTopParent(const Path& path);
    PathC getFirstChild(const Path& path);
    PathC getNextSibling(const Path& path);

    //! @fn FabricId getFabricId()
    //! @brief Returns the fabric id associated with the hierarchy
    //! @return Fabric id of the hierarchy
    FabricId getFabricId();

    /// @brief SubTreeRange emulates the pxr::SubTreeRange class to iterate over a subtree of a prims.
    class SubTreeRange
    {
    public:
        SubTreeRange(USDHierarchy& hier, PathC root) : hier(hier), root(root)
        {
        }

        class Iterator : public std::iterator<std::input_iterator_tag, PathC>
        {
        public:
            Iterator(USDHierarchy& hier, PathC root) : hier(hier)
            {
                if (root != kUninitializedPath)
                {
                    stack.push(root);
                    ++(*this); // Initialize to the first valid node
                }
            }

            Iterator& operator++()
            {
                if (stack.empty())
                {
                    currentPath = kUninitializedPath;
                    return *this;
                }

                currentPath = stack.top();
                stack.pop();

                const PathC firstChild = hier.getFirstChild(currentPath);
                PathC child = firstChild;
                while (child != kUninitializedPath)
                {
                    stack.push(child);
                    child = hier.getNextSibling(child);
                    if (child == firstChild)
                    {
                        break;
                    }
                }

                return *this;
            }

            PathC operator*() const
            {
                return currentPath;
            }

            bool operator!=(const Iterator& other) const
            {
                return currentPath != other.currentPath;
            }

        private:
            USDHierarchy& hier;
            std::stack<PathC> stack;
            PathC currentPath = kUninitializedPath;
        };

        Iterator begin() const
        {
            return Iterator(hier, root);
        }

        Iterator end() const
        {
            return Iterator(hier, kUninitializedPath);
        }

    private:
        USDHierarchy& hier;
        PathC root = kUninitializedPath;
    };

protected:
    IConnectivity* capi = nullptr;
    FabricId fabricId = kInvalidFabricId;
};

//
// USDHierarchyRange is an iteratable wrapper for USDHierarchy to Depth-First traverse a USD Hierarchy rooted at a given
// prim. Based on UsdPrimRange.
// @note This is the simplest, but is not the most efficient traversal Connectivity offers.

struct USDHierarchyRange
{
public:
    USDHierarchyRange(){};
    USDHierarchyRange(USDHierarchy& hier, const PathC& startPath);

    struct iterator;
    using const_iterator = iterator;

    //! @fn PathC getNextPrim(const Path& path)
    //! @brief Returns the next prim path "to the right" of this one.  That is, this
    //! prim's next sibling if it has one, otherwise the next sibling of the
    //! nearest ancestor with a sibling, if there is one, otherwise null.
    //! This is used to determine the "end" of our iterator.
    //! @param path Path of a prim
    //! @return Path of the next sibling.
    PathC getNextPrim(const Path& path);


    iterator begin();
    iterator end();

private:
    // data members fixed for the life of the range
    PathC m_beginPath;
    PathC m_endPath;
    USDHierarchy m_hier;
};

//
// USDHierarchyRange::iterator
// Iterator class to Depth-First traverse a USD Hierarchy rooted at a given prim. Based on UsdPrimRange::iterator.
// @note This iterator is the simplest, but is not the most efficient traversal Connectivity offers.
struct USDHierarchyRange::iterator
{
public:
    using iterator_category = std::forward_iterator_tag;
    using difference_type = std::ptrdiff_t;
    using value_type = PathC;
    using pointer = PathC;
    using reference = PathC;

    iterator(USDHierarchyRange& hierRange, USDHierarchy& hier, PathC path)
        : m_primPath(path), m_hierRange(hierRange), m_hier(hier), m_depth(0)
    {
    }

    iterator() : m_primPath(kUninitializedPath){};

    //! @fn void PruneChildren();
    //! @brief Behave as if the current prim has no children when next advanced.
    void PruneChildren();
    reference operator*();
    pointer operator->();

    // Prefix increment
    iterator& operator++();
    // Postfix increment
    iterator operator++(int);

    friend bool operator==(const iterator& a, const iterator& b);
    friend bool operator!=(const iterator& a, const iterator& b);

private:
    friend struct USDHierarchyRange;

    PathC m_primPath;
    USDHierarchyRange m_hierRange;
    USDHierarchy m_hier;
    bool m_pruneChildrenFlag = false;
    unsigned int m_depth = 0;

    //! @fn void increment()
    //! @brief increments the iterator by one.
    void increment();

    //! @fn bool moveToChild
    //! @brief Search for the first direct child of \p m_primPath up to \end.
    //! If found, move m_primPath to the child and return true. If no children found,
    //! leave the iterator unchanged and return false. Based on Usd_MoveToChild.
    bool moveToChild();

    //! @fn bool moveToNextSiblingOrParent()
    //! @brief Search for the next sibling up to \p end. If no such sibling exists,
    //! move to the parent and return true (to indicate we have not yet found an unvisited prim).
    //! If we move to a sibling, or reach the end, return false. This is based on Usd_MoveToNextSiblingOrParent.
    //! @return Return true if iterator moved to the parent, and false otherwise.
    bool moveToNextSiblingOrParent();
};

} // namespace fabric
} // namespace omni

#include "Connectivity.inl"
