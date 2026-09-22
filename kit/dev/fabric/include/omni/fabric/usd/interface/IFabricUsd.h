// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>
#include <carb/logging/Log.h>

#include <omni/fabric/FabricTypes.h>
#include <omni/fabric/IdTypes.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <omni/fabric/Type.h>

#include <omni/fabric/usd/PathConversion.h>
#include <omni/fabric/usd/interface/UsdIncludes.h>

#include <set>
#include <vector>

namespace omni
{
namespace fabric
{

// This api is a set of helper functions for working with fabric and usd. It is not
// intended to be C abi stable.
struct IFabricUsd
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IFabricUsd", 0, 2);

    void(CARB_ABI* prefetchPrimToFabric)(FabricId fabricId,
                                         const pxr::SdfPath& dstPath,
                                         const pxr::UsdPrim& prim,
                                         const std::set<TokenC>& filter,
                                         bool forceUpdate,
                                         bool processConnections,
                                         const pxr::UsdTimeCode& time

    );

    void(CARB_ABI* prefetchPrimsToFabric)(FabricId fabricId,
                                          const std::vector<pxr::SdfPath>& dstPaths,
                                          const std::vector<pxr::UsdPrim>& prims,
                                          const std::set<TokenC>& filter,
                                          bool forceUpdate,
                                          bool processConnections,
                                          const pxr::UsdTimeCode& time

    );

    void(CARB_ABI* loadPrefetchedPrimData)(FabricId fabricId, bool processConnections);

    void(CARB_ABI* exportUsdPrimData)(FabricId fabricId);
    void(CARB_ABI* exportUsdPrimDataToStage)(FabricId fabricId,
                                             pxr::UsdStageRefPtr usdStage,
                                             const double* timeCode,
                                             const double* prevTimeCode);

    void(CARB_ABI* exportUsdPrimDataByBucket)(FabricId fabricId, BucketSubset bucket, bool skipMeshPoints);
    void(CARB_ABI* exportUsdPrimDataByBucketToStage)(FabricId fabricId,
                                                     BucketSubset bucket,
                                                     pxr::UsdStageRefPtr usdStage,
                                                     bool skipMeshPoints,
                                                     const double* timeCode,
                                                     const double* prevTimeCode);


    TypeC(CARB_ABI* usdTypeToFabricType)(pxr::SdfValueTypeName usdType);

    pxr::SdfValueTypeName(CARB_ABI* fabricTypetoUsdType)(TypeC typeC);

    size_t(CARB_ABI* getUsdTypeCount)();

    void(CARB_ABI* getAllUsdTypes)(TypeC* outArray, size_t outArraySize);


    void(CARB_ABI* setStageToWatchFabric)(FabricId fabricId, UsdStageId stageId);
    /** @brief Enable/Disable change notifications on USD changes.
     *
     * @enable[in] True/False enable notifications
     *
     */
    void(CARB_ABI* setEnableChangeNotifies)(FabricId fabricId, bool enable);

    /** @brief Return whether change notifications on USD changes is enabled.
     *
     * @return True if change notifications on USD changes is enabled, else False.
     *
     */
    bool(CARB_ABI* getEnableChangeNotifies)(FabricId fabricId);

    /** @brief copy data for a single prim from fabric to usd
     *
     * @fabricId[in] The fabric to copy from
     * @path[in] the prim to export
     */
    void(CARB_ABI* exportUsdPrimDataByPath)(FabricId fabricId, const PathC path);

    /** @brief make a bucket for a single USD prim in Fabric, but do not fetch
     *          its attributes
     *
     * @fabricId[in] The fabric to write to
     * @dstPath[in] The Fabric path to write to, typically the prim's USD path
     * @prim[in] The USD prim to read
     */
    void(CARB_ABI* prefetchPrimToFabricWithoutAttributes)(FabricId fabricId,
                                                          const pxr::SdfPath& dstPath,
                                                          const pxr::UsdPrim& prim);

    /** @brief make buckets for all prims on a USD stage, but only if this
     *          hasn't been done before.
     *
     * This is used to lazily create an index of all prims on a stage, without
     * the time or memory cost of fetching all the attribute values. The user
     * can then use findPrims to, for example, find all the prims of a
     * particular type.
     *
     * If a SimStageWithHistory hasn't been created for this stage then a
     * warning will be printed and no population will be done.
     *
     * @stageId[in] The UsdStage to fetch to Fabric
     */
    void(CARB_ABI* minimalPopulateIfNecessary)(FabricId fabricId);

    /** @brief copy data for a BucketSubset to USD on a local layer
     *
     * @fabricId[in] The fabric to copy from
     * @bucket[in] the BucketSubset to export
     * @bucket[in] skipMeshPoints
     * @bucket[in] layerIdentifier. The layer identifier of target layer. The layer must be a local layer of USD stage
     * associated with fabricId. If set to kUninitializedToken, this function is same as exportUsdPrimDataByBucket, with
     * prim data exported to current edit target layer.
     */
    void(CARB_ABI* exportUsdPrimDataByBucketToLayer)(FabricId fabricId,
                                                     BucketSubset bucket,
                                                     bool skipMeshPoints,
                                                     TokenC layerIdentifier);

    /** @brief make buckets for all prims on a USD stage, even
     *         if this operation has already been done before
     *
     * This is used to lazily create an index of all prims on a stage, without
     * the time or memory cost of fetching all the attribute values. The user
     * can then use findPrims to, for example, find all the prims of a
     * particular type.
     *
     * If a SimStageWithHistory hasn't been created for this stage then a
     * warning will be printed and no population will be done.
     *
     * The 'force' version of this API allows developers to "catch up"
     * if Fabric notifications were disabled while populating a USD stage
     *
     * @fabricId[in] The Fabric to populate
     */
    void(CARB_ABI* forceMinimalPopulate)(FabricId fabricId);
};

} // namespace fabric
} // namespace omni
