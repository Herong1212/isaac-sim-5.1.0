// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include <omni/fabric/usd/interface/IFabricUsd.h>

namespace omni
{
namespace fabric
{

inline void prefetchPrimToFabric(const Fabric& cache,
                                 const pxr::SdfPath& dstPath,
                                 const pxr::UsdPrim& prim,
                                 const std::set<Token>& filter,
                                 bool forceUpdate,
                                 bool processConnections,
                                 const pxr::UsdTimeCode& time

)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    std::set<TokenC> tokens;
    for (auto it = filter.begin(); it != filter.end(); ++it)
    {
        tokens.insert(*it);
    }
    iFabricUsd->prefetchPrimToFabric(cache.getId(), dstPath, prim, tokens, forceUpdate, processConnections, time);
}

inline void prefetchPrimsToFabric(const Fabric& cache,
                                  const std::vector<pxr::SdfPath>& dstPaths,
                                  const std::vector<pxr::UsdPrim>& prims,
                                  const std::set<Token>& filter,
                                  bool forceUpdate,
                                  bool processConnections,
                                  const pxr::UsdTimeCode& time

)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    std::set<TokenC> tokens;
    for (auto it = filter.begin(); it != filter.end(); ++it)
    {
        tokens.insert(*it);
    }
    iFabricUsd->prefetchPrimsToFabric(cache.getId(), dstPaths, prims, tokens, forceUpdate, processConnections, time);
}

inline void loadPrefetchedPrimData(const Fabric& cache, bool processConnections)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->loadPrefetchedPrimData(cache.getId(), processConnections);
}

inline void exportUsdPrimData(const Fabric& cache)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->exportUsdPrimData(cache.getId());
}

inline void exportUsdPrimDataToStage(const Fabric& cache,
                                     pxr::UsdStageRefPtr usdStage,
                                     const double* timeCode,
                                     const double* prevTimeCode)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->exportUsdPrimDataToStage(cache.getId(), usdStage, timeCode, prevTimeCode);
}

inline void exportUsdPrimDataByBucket(const Fabric& cache, BucketSubset bucket, bool skipMeshPoints)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->exportUsdPrimDataByBucket(cache.getId(), bucket, skipMeshPoints);
}

inline void exportUsdPrimDataByBucketToStage(const Fabric& cache,
                                             BucketSubset bucket,
                                             pxr::UsdStageRefPtr usdStage,
                                             bool skipMeshPoints,
                                             const double* timeCode,
                                             const double* prevTimeCode)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->exportUsdPrimDataByBucketToStage(cache.getId(), bucket, usdStage, skipMeshPoints, timeCode, prevTimeCode);
}


inline Type usdTypeToFabricType(pxr::SdfValueTypeName usdType)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    return Type(iFabricUsd->usdTypeToFabricType(usdType));
}

inline pxr::SdfValueTypeName fabricTypetoUsdType(const Type& type)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    return iFabricUsd->fabricTypetoUsdType(TypeC(type));
}

inline size_t getUsdTypeCount()
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    return iFabricUsd->getUsdTypeCount();
}

inline void getAllUsdTypes(std::vector<Type>& types)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    size_t count = iFabricUsd->getUsdTypeCount();
    if (types.size() != count)
    {
        types.resize(count);
    }
    iFabricUsd->getAllUsdTypes((TypeC*)types.data(), types.size());
}

inline void setStageToWatchFabric(const Fabric& cache, UsdStageId stageId)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->setStageToWatchFabric(cache.getId(), stageId);
}

inline void setEnableChangeNotifies(const Fabric& cache, bool enable)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->setEnableChangeNotifies(cache.getId(), enable);
}

inline bool getEnableChangeNotifies(const Fabric& cache)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    return iFabricUsd->getEnableChangeNotifies(cache.getId());
}

inline void exportUsdPrimDataByPath(const Fabric& cache, const Path& path)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->exportUsdPrimDataByPath(cache.getId(), PathC(path));
}

inline void prefetchPrimToFabricWithoutAttributes(const Fabric& cache,
                                                  const pxr::SdfPath& dstPath,
                                                  const pxr::UsdPrim& prim)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->prefetchPrimToFabricWithoutAttributes(cache.getId(), dstPath, prim);
}

inline void minimalPopulateIfNecessary(const Fabric& cache)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->minimalPopulateIfNecessary(cache.getId());
}

inline void forceMinimalPopulate(const Fabric& cache)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->forceMinimalPopulate(cache.getId());
}

inline void exportUsdPrimDataByBucketToLayer(const Fabric& cache,
                                             BucketSubset bucket,
                                             bool skipMeshPoints,
                                             const Token& layerIdentifier)
{
    auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
    iFabricUsd->exportUsdPrimDataByBucketToLayer(cache.getId(), bucket, skipMeshPoints, layerIdentifier);
}

} // namespace fabric
} // namespace omni
