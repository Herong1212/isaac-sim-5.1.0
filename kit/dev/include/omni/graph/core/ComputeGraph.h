// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "iComputeGraph.h"
#include "INodeCategories.h"
#include "INodeTypeForwarding2.h"
#include "unstable/INodeTypeForwarding.h"
#include "IBundleFactory.h"
#include "IDirtyID.h"
#include "IBundleChanges.h"
#include "IPrimView.h"
#include <omni/fabric/AttrNameAndType.h>

#include <carb/Interface.h>
#include <carb/tasking/TaskingTypes.h>

#include <omni/core/IObject.h>

namespace rtx
{
namespace resourcemanager
{
class RpResource;
typedef uint32_t SyncScopeId;
}
}

namespace carb
{
namespace graphics
{
struct Semaphore;
}
}

namespace gpu
{
namespace rendergraph
{
//! Declare the IRenderGraph interface definition
OMNI_DECLARE_INTERFACE(IRenderGraph);
using RenderGraph = omni::core::ObjectPtr<gpu::rendergraph::IRenderGraph>;
}
enum class GfResult: int32_t;
}

namespace omni
{
namespace usd
{
class IUsdMutex;
using PathH = uint64_t;
namespace hydra
{
struct ViewportHydraRenderResults;
}
}

namespace kit
{
struct StageUpdateSettings;
}

namespace graph
{
namespace core
{

/** used only by kit - do not use this interface in plugins */
struct ComputeGraph
{
    CARB_PLUGIN_INTERFACE("omni::graph::core::ComputeGraph", 2, 12)

    /**
     * Returns the number of global orchestration graphs for all stages of the graph pipelines
     *
     * Note: from version 2.3 on, the semantics of this call has changed, even if the interface has not.
     * There is now a orchestration graph which has nodes that each wrap either a graph or an extension to be run
     * This function will now return the number of such orchestration graphs.  The non-orchestration global graphs
     * can be retrieved by iterating over the nodes of the orchestration graph and calling getWrappedGraph
     *
     * @return the number of graphs in the system, regardless of pipeline stage
     */
    size_t(CARB_ABI* getGraphCount)();

    /**
     * Fills the buffer with global orchestration graph objects that occupy all pipeline stages
     *
     * Note: From version 2.3 on, see note above about the global orchestration graph with nodes that
     *       wrap previous global graphs
     *
     * @param[out] graphObjs The buffer of graphs to fill
     * @param[in] bufSize The size of the buffer in terms of the number of GraphObj it has room for
     * @return true on success, false on failure
     */

    bool(CARB_ABI* getGraphs)(GraphObj* contextBuf, size_t bufSize);

    /**
     * Returns the number of graph contexts for all pipeline stages
     *
     * Note: From version 2.3 on, see note above about the global orchestration graph with nodes that
     * wrap previous global graphs
     *
     * @return the number of graph contexts in the whole system, regardless of pipeline stage
     */
    size_t(CARB_ABI* getGraphContextCount)();

    /**
     * Fills the buffer with graph context objects that occupy all pipeline stages
     *
     * Note: From version 2.3 on, see note above about the global orchestration graph with nodes
     *       that wrap previous global graphs
     *
     * @param[out] contextBuf The buffer of graph contexts to fill
     * @param[in] bufSize The size of the buffer in terms of the number of GraphContextObj it has room for
     * @return true on success, false on failure
     */
    bool(CARB_ABI* getGraphContexts)(GraphContextObj* contextBuf, size_t bufSize);

    /**
     *  @deprecated All of this is automatically done by the framework
     */
    CARB_DEPRECATED("Not necessary: OG startup/shutdown is automatically managed by the framework")
    void(CARB_ABI* shutdownComputeGraph)();

    /**
     *  @deprecated All of this is automatically done by the framework
     */
    CARB_DEPRECATED("Not necessary: OG startup/shutdown is automatically managed by the framework")
    void(CARB_ABI* startupComputeGraph)();

    /**
     *  @deprecated All of this is automatically done by the framework
     *
     */
    CARB_DEPRECATED("Not necessary: OG attach/detach is automatically managed by the framework")
    void(CARB_ABI* attach)(long int stageId, double metersPerUnit, void* userData);

    /**
     *  @deprecated All of this is automatically done by the framework
     */
    CARB_DEPRECATED("Not necessary: OG attach/detach is automatically managed by the framework")
    void(CARB_ABI* detach)(void* userData);

    /**
     * @deprecated This version is deprecated and will be removed in a future version.
     */
    CARB_DEPRECATED("Not functional and will be removed in next major version - update is automatically managed by the framework")
    void(CARB_ABI* update)(float currentTime,
                           float elapsedSecs,
                           const omni::kit::StageUpdateSettings* updateSettings,
                           void* userData);

    /**
     * @deprecated This version is deprecated and will be removed in a future version.
     * Use updateSimStepWithUsd() instead.
     */
    void(CARB_ABI* updateSimStep)(int64_t timeNS, carb::tasking::Counter*);

    /**
     * @brief Enable of disable the attachment of OmniGraph to the Kit update loop
     *
     * Currently there is a dependency in SimStageWithHistory on OG, so we cannot shutdown the graph
     * when it needs to be ticked from external process, such as DS2's ISimStep.
     * Using this method we can block (or unblock) OG from reacting to Kit's update loop.
     *
     * @param[in] state Whether the Kit update loop should be respected or not
     */
    void(CARB_ABI* considerKitUpdateLoop)(bool state);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Will be removed in next major version, do not use (currently no-ops)")
    void(CARB_ABI* postRenderBegin)(rtx::resourcemanager::SyncScopeId syncScope,
                                    gpu::rendergraph::RenderGraph renderGraph);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Will be removed in next major version, do not use (currently no-ops)")
    void(CARB_ABI* postRenderUpdate)(rtx::resourcemanager::SyncScopeId syncScope,
                                     omni::usd::hydra::ViewportHydraRenderResults* renderResults,
                                     omni::usd::PathH renderProductPrimPath,
                                     double simTime,
                                     double hydraTime);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Will be removed in next major version, do not use (currently no-ops)")
    gpu::GfResult(CARB_ABI* postRenderEnd)(rtx::resourcemanager::SyncScopeId syncScope);

    /**
     * Returns the number of global orchestration graphs given a particular graph pipeline stage.
     *
     * @param[in] pipelineStage The stage of the pipeline (simulation, pre-render, post-render)
     * @return the number of graphs in that pipeline stage
     */
    size_t(CARB_ABI* getGraphCountInPipelineStage)(GraphPipelineStage pipelineStage);

    /**
     * Fills the buffer with global orchestration graph objects that occupy a particular pipeline stage
     *
     * @param[out] graphObjs The buffer of graphs to fill
     * @param[in] bufSize The size of the buffer in terms of the number of GraphObj it has room for
     * @param[in] pipelineStage The stage of the pipeline (simulation, pre-render, post-render)
     * @return true on success, false on failure
     */
    bool(CARB_ABI* getGraphsInPipelineStage)(GraphObj* graphObjs, size_t bufSize, GraphPipelineStage pipelineStage);

    /**
     * @brief This update function is used by DriveSim's ISimStep interface to tick the graph
     *
     * @param[in] timeNS Simulation time, in nanoseconds
     * @param[in] counter Tasking counter
     * @param[in] disableUsdUpdates Turn off USD updates while the simulation step is happening
     */
    void(CARB_ABI* updateSimStepUsd)(int64_t timeNS, carb::tasking::Counter* counter, bool disableUsdUpdates);

    /**
     * @brief Gets the interface object handling the node categories
     *
     * @return Raw object that implements the node category interface
     */
    INodeCategories*(CARB_ABI* getNodeCategoriesInterface)();

    /**
     * @brief Gets an ONI object for the interface handling the node categories
     *
     * @return Shared object that implements the node category interface
     */
    inline omni::core::ObjectPtr<INodeCategories> getNodeCategoriesInterfacePtr() const
    {
        return omni::core::steal(getNodeCategoriesInterface());
    }

    /**
     * @brief Sets the test failure state. This is for test failures that cannot be caught by conventional means.
     *
     * @param[in] hasFailed If true then increment the test failure count, otherwise reset it to 0.
     */
    void (CARB_ABI* setTestFailure)(bool hasFailed);

    /**
     * @return Returns the current test failure count since it was last cleared.
     */
    size_t (CARB_ABI* testFailureCount)();

    /**
     * @brief Gets an ONI object for the interface handling the bundle factory
     *
     * @return Shared object that implements the bundle factory interface
     */
    IBundleFactory*(CARB_ABI* getBundleFactoryInterface)();

    /**
     * @brief Gets an ONI object for the interface handling the bundle factory
     *
     * @return Shared object that implements the bundle factory interface
     */
    inline omni::core::ObjectPtr<IBundleFactory> getBundleFactoryInterfacePtr() const
    {
        return omni::core::steal(getBundleFactoryInterface());
    }

    /**
     * @deprecated This version is deprecated and will be removed in a future version.
     */
    CARB_DEPRECATED("Not functional and will be removed in next major version - update is automatically managed by the framework")
    void(CARB_ABI* updateV2)(double currentTime,
                             float elapsedSecs,
                             double absoluteSimTime,
                             const omni::kit::StageUpdateSettings* updateSettings,
                             void* userData);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Will be removed in next major version, do not use (currently no-ops)")
    void(CARB_ABI* preRenderBegin)(gpu::rendergraph::RenderGraph renderGraph);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Will be removed in next major version, do not use (currently no-ops)")
    void(CARB_ABI* preRenderUpdate)(double simTime,
                                    double hydraTime,
                                    omni::usd::IUsdMutex& mutex);

    /** @private Deprecated - do not use */
    CARB_DEPRECATED("Will be removed in next major version, do not use (currently no-ops)")
    void(CARB_ABI* preRenderEnd)();

    /**
     * Flushes any pending USD changes from the fabric scene delegate.
     */
    void(CARB_ABI* flushUsd)();

    /**
     * @brief Gets the interface object handling the node type forwarding
     * @deprecated This version is not the most recent one - use getNodeTypeForwardingInterface2() instead.
     * @return Shared object that implements the node type forwarding interface
     */
    unstable::INodeTypeForwarding*(CARB_ABI* getNodeTypeForwardingInterface)();
    inline omni::core::ObjectPtr<unstable::INodeTypeForwarding> getNodeTypeForwardingInterfacePtr() const
    {
        return omni::core::steal(getNodeTypeForwardingInterface());
    }

    /**
     * @brief Gets the interface object handling the latest Dirty ID interface
     *
     * @return Shared object that implements the IDirtyID2 interface
     */
    unstable::IDirtyID2*(CARB_ABI* getDirtyIDInterface)(GraphContextObj const& context);
    omni::core::ObjectPtr<unstable::IDirtyID2> getDirtyIDInterfacePtr(GraphContextObj const& context) const
    {
        return omni::core::steal(getDirtyIDInterface(context));
    }

    /**
     * @brief Gets the interface object handling the latest bundle changes interface
     *
     * @return Shared object that implements the IBundleChanges interface
     */
    IBundleChanges*(CARB_ABI* getBundleChangesInterface)(GraphContextObj const& context);
    omni::core::ObjectPtr<IBundleChanges> getBundleChangesInterfacePtr(GraphContextObj const& context) const
    {
        return omni::core::steal(getBundleChangesInterface(context));
    }

    /**
     * @brief Gets the latest interface object handling the node type forwarding
     *
     * @return Shared object that implements the node type forwarding interface
     */
    INodeTypeForwarding2*(CARB_ABI* getNodeTypeForwardingInterface2)();
    inline omni::core::ObjectPtr<INodeTypeForwarding2> getNodeTypeForwardingInterfacePtr2() const
    {
        return omni::core::steal(getNodeTypeForwardingInterface2());
    }

    /**
     * Create a prim view object from a list of prims. Returns a PrimView object that represents a simple
     * set of primitives. The PrimView object returned does not sort the primitives into buckets, and
     * is thus less efficient to use than createPrimViewFromQuery.
     *
     * @param[in] prims     The list of prims to include in the PrimView
     * @param[in] primCount The number of prims referenced by the primCount argument
     *
     * @return A Prim View object that represents the list of provided prims.
     */
    IPrimViewPtr(CARB_ABI* createPrimViewFromPrimList)(omni::fabric::PathC const* const prims, size_t primCount);

    /**
     * Create a prim view from a list of attributes. The resulting object represents a view on the prims that
     * match the given arguments.
     *
     * @param[in] includeAttributes The list of attribute that indicates what attributes are required to exist on
     *                              the Prims in the query.
     *                              Can be nullptr to indicate all Prims are to be included.
     * @param[in] includeAttributeCount The number of attributes referenced by the includeAttribute argument
     * @param[in] excludeAttributes The list of attributes that indicate what attributes cannot on exist on Prims
     *                              that are returned by the query. Can be nullptr to indicate no arguments are
     *                              excluded.
     * @param[in] excludeAttributecount The number of attributes referenced by the excludeAttribute argument.
     * @return A Prim View object that represents the result of query.
     */
    IPrimViewPtr(CARB_ABI* createPrimViewFromQuery)(omni::fabric::AttrNameAndType const* const includeAttributes,
                                                    size_t includeAttributeCount,
                                                    omni::fabric::AttrNameAndType const* const excludeAttributes,
                                                    size_t excludeAttributeCount);

    /**
     * Returns the CUDA device used by OmniGraph.
     */
    int(CARB_ABI* getComputeCudaDevice)();

    /**
     * Reset any fabric caching made by all graphs currently allocated
     * This function is not thread safe and must be called from a safe synched location
     * It should be called after the underlying fabric is changed without OG knowing about it,
     *  such as with a snapshot restoration 
     */
    void(CARB_ABI* resetGraphsCaching)();

    /**
     * Allows or not OG to cache pointers to main fabric storage
     * returns whether it succeed to apply the change
     * 
     * When using the "main stage" fabric (default), OG caches pointers from frame to frame to increase its performance.
     * While enabled by default in situation where it is known to be safe, this ABI let the user decide
     * to disable altogether this caching.
     */
    bool(CARB_ABI* enableMainFabricCaching)(bool enable);

};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(ComputeGraph, enableMainFabricCaching, 34)

}
}
}
