// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/core/API.h>

namespace omni
{
namespace fabric
{

struct IConnectivity
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IConnectivity", 1, 7);

    using Algorithm = connectivity::Algorithm;
    using Filter = connectivity::Filter;
    using EdgeType = connectivity::EdgeType;
    using EdgeId = connectivity::EdgeId;
    using BakeId = connectivity::BakeId;
    using SelectionId = connectivity::SelectionId;
    using VisitorFunctionPath_t = connectivity::VisitorFunctionPath_t;
    using VisitorFunctionRd_t = connectivity::VisitorFunctionRd_t;
    using VisitorFunctionWr_t = connectivity::VisitorFunctionWr_t;
    using TransformFunctionWr_t = connectivity::TransformFunctionWr_t;
    using ExtentFunctionWr_t = connectivity::ExtentFunctionWr_t;
    using NavigatorParametersRd_t = connectivity::NavigatorParametersRd_t;
    using NavigatorParametersWr_t = connectivity::NavigatorParametersWr_t;

    EdgeType(CARB_ABI* setType)(FabricId fabricId, const TokenC& typeName);
    TokenC(CARB_ABI* getTypeName)(FabricId fabricId, EdgeType type);

    EdgeId(CARB_ABI* connect)(FabricId fabricId, const PathC& src, const PathC& dst, uint64_t value, uint64_t dualValue);
    EdgeId(CARB_ABI* connectIfNot)(FabricId fabricId, const PathC& src, const PathC& dst, uint64_t value, uint64_t dualValue, bool* outAlreadyConnected);

    bool(CARB_ABI* disconnect)(FabricId fabricId, const PathC& path1, const PathC& path2, uint64_t value);
    bool(CARB_ABI* disconnectSource)(FabricId fabricId, const PathC& src, const uint64_t value);
    bool(CARB_ABI* disconnectEdge)(FabricId fabricId, EdgeId eid);
    bool(CARB_ABI* disconnectEdges)(SelectionId sid);

    size_t(CARB_ABI* countDegree)(FabricId fabricId, const PathC& path, uint64_t value);
    size_t(CARB_ABI* sumDegree)(FabricId fabricId, const PathC& path);

    EdgeId(CARB_ABI* getFirstEdge)(FabricId fabricId, const PathC& path);
    EdgeId(CARB_ABI* findFirstEdge)(FabricId fabricId, const PathC& path, uint64_t value);
    EdgeId(CARB_ABI* findEdge)(FabricId fabricId, const PathC& src, const PathC& dst, uint64_t value);

    bool(CARB_ABI* isValid)(FabricId fabricId, EdgeId eid);
    PathC(CARB_ABI* getSource)(FabricId fabricId, EdgeId eid);
    PathC(CARB_ABI* getTarget)(FabricId fabricId, EdgeId eid);
    EdgeId(CARB_ABI* getDual)(FabricId fabricId, EdgeId eid);
    EdgeId(CARB_ABI* getNext)(FabricId fabricId, EdgeId eid);
    uint64_t(CARB_ABI* getEdgeValue)(FabricId fabricId, EdgeId eid);
    void(CARB_ABI* setEdgeValue)(FabricId fabricId, EdgeId eid, uint64_t value);

    EdgeId(CARB_ABI* getNextAtSource)(FabricId fabricId, EdgeId eid);
    EdgeId(CARB_ABI* getNextAtTarget)(FabricId fabricId, EdgeId eid);
    EdgeId(CARB_ABI* getNextAtSourceWithin)(FabricId fabricId, EdgeId eid, SelectionId sid);
    EdgeId(CARB_ABI* getNextAtTargetWithin)(FabricId fabricId, EdgeId eid, SelectionId sid);

    EdgeId(CARB_ABI* findNextAtSource)(FabricId fabricId, EdgeId eid, uint64_t value);
    EdgeId(CARB_ABI* findNextAtTarget)(FabricId fabricId, EdgeId eid, uint64_t value);
    EdgeId(CARB_ABI* findNextAtSourceWithin)(FabricId fabricId, EdgeId eid, uint64_t value, const SelectionId sid);
    EdgeId(CARB_ABI* findNextAtTargetWithin)(FabricId fabricId, EdgeId eid, uint64_t value, const SelectionId sid);

    BakeId (CARB_ABI* bakeBegin)(FabricId fabricId);
    SelectionId(CARB_ABI* bakeSelect_deprecated)(BakeId bakeId, const Filter& filter, const PathC& root);
    SelectionId(CARB_ABI* bakeSelectBucket_deprecated)(BakeId bakeId, const BucketId& filter);
    SelectionId(CARB_ABI* bakeSubselect_deprecated)(SelectionId sid, const Filter& filter, const PathC& root);
    SelectionId(CARB_ABI* bakeUnion)(SelectionId augend, SelectionId addend); // augend + addend
    SelectionId(CARB_ABI* bakeDifference)(SelectionId minuend, SelectionId subtrahend); // minuend − subtrahend
    SelectionId(CARB_ABI* bakeIntersection)(SelectionId intersecer, SelectionId intersecand); // intersecer ^ intersecand
    SelectionId(CARB_ABI* bakeDisjunction)(SelectionId disjuncer, SelectionId disjuncand); // disjunctive union
    void(CARB_ABI* bakePack)(SelectionId sid);
    void(CARB_ABI* bakeExport)(SelectionId sid);
    void(CARB_ABI* bakeEnd)(BakeId bakeId);

    size_t(CARB_ABI* retain)(SelectionId sid);
    size_t(CARB_ABI* release)(SelectionId sid);
    bool(CARB_ABI* isUndefined)(SelectionId sid);

    bool(CARB_ABI* pathExistsIn)(SelectionId sid, const PathC& path);
    FABRIC_ABI_DUMMY(1)
    bool(CARB_ABI* edgeExistsIn)(SelectionId sid, EdgeId eid);

    void(CARB_ABI* includeEdge)(SelectionId sid, EdgeId eid);
    void(CARB_ABI* excludeEdge)(SelectionId sid, EdgeId eid);

    size_t(CARB_ABI* visitRd)(SelectionId attributes, const PathC& root, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionRd_t visitor, void* userData);
    size_t(CARB_ABI* visitWr)(SelectionId attributes, const PathC& root, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionWr_t visitor, void* userData);
    size_t(CARB_ABI* visitPaths)(FabricId fabricId, VisitorFunctionPath_t visitor, void* userData);

    size_t(CARB_ABI* navigateRd)(const NavigatorParametersRd_t& parameters, size_t value, size_t dualValue, size_t valueMask);
    size_t(CARB_ABI* navigateWr)(const NavigatorParametersWr_t& parameters, size_t value, size_t dualValue, size_t valueMask);

    size_t(CARB_ABI* visitMappingRd)(SelectionId attributes, SelectionId domain, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionRd_t visitor, Algorithm algo, void* userData);
    size_t(CARB_ABI* visitMappingWr)(SelectionId attributes, SelectionId domain, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionWr_t visitor, Algorithm algo, void* userData);

    SelectionId(CARB_ABI* bakeSelectAttributes)(BakeId bakeId, const Filter& filter);
    SelectionId(CARB_ABI* bakeSelectPrims)(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none);
    SelectionId(CARB_ABI* bakeSelectBuckets)(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none);
    SelectionId(CARB_ABI* bakeSelectEdges)(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none);
    SelectionId(CARB_ABI* bakeSelectNetwork)(BakeId bakeId, const Filter& all, const Filter& any, const Filter& none);

    size_t(CARB_ABI* countPrims)(SelectionId sid);
    size_t(CARB_ABI* countAttributes)(SelectionId sid);
    size_t(CARB_ABI* countBuckets)(SelectionId sid);
    size_t(CARB_ABI* countEdges)(SelectionId sid);

    // 0.4
    size_t(CARB_ABI* findEdgesToRoot)(FabricId fabricId, Span<EdgeId> outEdges, const PathC& prim, size_t upValue, size_t valueMask);
    size_t(CARB_ABI* findPrimsToRoot)(FabricId fabricId, Span<PathC> outPaths, const PathC& prim, size_t upValue, size_t valueMask);
    PathC(CARB_ABI* findRoot)(FabricId fabricId, const PathC& prim, size_t upValue, size_t valueMask);
    size_t(CARB_ABI* removeDescendants)(FabricId fabricId, Span<PathC> outReducedList, Span<const PathC> inList, size_t upValue, size_t valueMask);
    size_t(CARB_ABI* getMemUsage)(SelectionId sid);
    void(CARB_ABI* invalidate)(SelectionId sid);
    connectivity::PerformanceCounters*(CARB_ABI* runtimePerfCounters)(FabricId fabricId);
    void(CARB_ABI* runtimeClearQueryCache)(FabricId fabricId);
    size_t(CARB_ABI* runtimeReserveQueryCache)(FabricId fabricId, size_t capacity);

    size_t(CARB_ABI* visitParallelRd)(SelectionId attributes, const PathC& root, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionRd_t visitor, void* userData);
    size_t(CARB_ABI* visitParallelWr)(SelectionId attributes, const PathC& root, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionWr_t visitor, void* userData);

    // 1.5
    size_t(CARB_ABI* visitFromRd)(SelectionId attributes, const PathC& root, const PathC& start, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionRd_t visitor, void* userData);
    size_t(CARB_ABI* visitFromWr)(SelectionId attributes, const PathC& root, const PathC& start, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionWr_t visitor, void* userData);
    size_t(CARB_ABI* rvisitFromRd)(SelectionId attributes, const PathC& root, const PathC& start, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionRd_t visitor, void* userData);
    size_t(CARB_ABI* rvisitFromWr)(SelectionId attributes, const PathC& root, const PathC& start, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionWr_t visitor, void* userData);
    size_t(CARB_ABI* visitParallelFromRd)(SelectionId attributes, const PathC& root, const PathC& start, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionRd_t visitor, void* userData);
    size_t(CARB_ABI* visitParallelFromWr)(SelectionId attributes, const PathC& root, const PathC& start, size_t value, size_t dualValue, size_t valueMask, VisitorFunctionWr_t visitor, void* userData);
    size_t(CARB_ABI* reduceChangeList)(FabricId fabricId, Span<PathC> outReducedList, ListenerId listener, Span<const PathC> inExcludeList, Span<const PathC> inIncludeList, size_t upValue, size_t valueMask);
    size_t(CARB_ABI* transformFromWr)(SelectionId attributes, const PathC& root, const Span<const PathC> starts, size_t value, size_t dualValue, size_t valueMask, TransformFunctionWr_t visitor, void* userData);
    size_t(CARB_ABI* extentFromWr)(SelectionId attributes, const PathC& root, const Span<const PathC> starts, size_t value, size_t dualValue, size_t valueMask, ExtentFunctionWr_t visitor, void* userData);

    // 1.6
    void(CARB_ABI* invalidateAll)(FabricId fabricId);

    // 1.7
    size_t(CARB_ABI* getDataRevision)(FabricId fabricId);
    size_t(CARB_ABI* getDataId)(FabricId fabricId);
};

} // namespace fabric
} // namespace omni
