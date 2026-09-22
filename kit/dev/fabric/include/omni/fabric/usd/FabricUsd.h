// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/logging/Log.h>

#include <omni/fabric/core/Fabric.h>
#include <omni/fabric/core/FabricTypes.h>
#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/core/interface/IPath.h>
#include <omni/fabric/core/interface/IToken.h>
#include <omni/fabric/core/Type.h>

#include <omni/fabric/usd/IdTypes.h>

#include <omni/fabric/usd/interface/UsdIncludes.h>
#include <omni/fabric/usd/PathConversion.h>

#include <set>
#include <vector>

namespace omni
{
namespace fabric
{
void prefetchPrimToFabric(const Fabric& cache,
                          const pxr::SdfPath& dstPath,
                          const pxr::UsdPrim& prim,
                          const std::set<Token>& filter,
                          bool forceUpdate,
                          bool processConnections,
                          const pxr::UsdTimeCode& time

);

void prefetchPrimsToFabric(const Fabric& cache,
                           const std::vector<pxr::SdfPath>& dstPaths,
                           const std::vector<pxr::UsdPrim>& prims,
                           const std::set<Token>& filter,
                           bool forceUpdate,
                           bool processConnections,
                           const pxr::UsdTimeCode& time

);

void loadPrefetchedPrimData(const Fabric& cache, bool processConnections);

void exportUsdPrimData(const Fabric& cache);
void exportUsdPrimDataToStage(const Fabric& cache,
                              pxr::UsdStageRefPtr usdStage,
                              const double* timeCode,
                              const double* prevTimeCode);

void exportUsdPrimDataByBucket(const Fabric& cache, BucketSubset bucket, bool skipMeshPoints);
void exportUsdPrimDataByBucketToStage(const Fabric& cache,
                                      BucketSubset bucket,
                                      pxr::UsdStageRefPtr usdStage,
                                      bool skipMeshPoints,
                                      const double* timeCode,
                                      const double* prevTimeCode);


Type usdTypeToFabricType(pxr::SdfValueTypeName usdType);

pxr::SdfValueTypeName fabricTypetoUsdType(const Type& type);

size_t getUsdTypeCount();

void getAllUsdTypes(std::vector<Type>& types);


void setStageToWatchFabric(const Fabric& cache, UsdStageId stageId);
/** @brief Enable/Disable change notifications on USD changes.
 *
 * @enable[in] True/False enable notifications
 *
 */
void setEnableChangeNotifies(const Fabric& cache, bool enable);

/** @brief Return whether change notifications on USD changes is enabled.
 *
 * @return True if change notifications on USD changes is enabled, else False.
 *
 */
bool getEnableChangeNotifies(const Fabric& cache);

/** @brief copy data for a single prim from fabric to usd
 *
 * @fabricId[in] The fabric to copy from
 * @path[in] the prim to export
 */
void exportUsdPrimDataByPath(const Fabric& cache, const Path& path);

/** @brief make a bucket for a single USD prim in Fabric, but do not fetch
 *          its attributes
 *
 * @fabricId[in] The fabric to write to
 * @dstPath[in] The Fabric path to write to, typically the prim's USD path
 * @prim[in] The USD prim to read
 */
void prefetchPrimToFabricWithoutAttributes(const Fabric& cache, const pxr::SdfPath& dstPath, const pxr::UsdPrim& prim);

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
void minimalPopulateIfNecessary(const Fabric& cache);

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
void forceMinimalPopulate(const Fabric& cache);

/** @brief copy data for a BucketSubset to USD on a local layer
 *
 * @fabricId[in] The fabric to copy from
 * @bucket[in] the BucketSubset to export
 * @bucket[in] skipMeshPoints
 * @bucket[in] layerIdentifier. The layer identifier of target layer. The layer must be a local layer of USD stage
 * associated with fabricId. If set to kUninitializedToken, this function is same as exportUsdPrimDataByBucket, with
 * prim data exported to current edit target layer.
 */
void exportUsdPrimDataByBucketToLayer(const Fabric& cache,
                                      BucketSubset bucket,
                                      bool skipMeshPoints,
                                      const Token& layerIdentifier);

} // namespace fabric
} // namespace omni

#include <omni/fabric/usd/impl/FabricUsd.inl>
