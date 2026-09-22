// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "OmniHydraTypes.h"

// Avoid including USD Headers as they come from UsdPCH.h included in .cpp files
PXR_NAMESPACE_OPEN_SCOPE
class SdfPath;
class GfMatrix4d;
class GfMatrix4f;
class GfVec3f;
template<typename> class VtArray;
typedef VtArray<GfVec3f> VtVec3fArray;
PXR_NAMESPACE_CLOSE_SCOPE


namespace omni
{
namespace usd
{
namespace hydra
{
struct IOmniHydra
{
    CARB_PLUGIN_INTERFACE("omni::hydra::IOmniHydra", 2, 0)

    /*
     * Transform Get/Set
     */

    // get world space transform in s,q,t format
    bool(CARB_ABI* GetWorldTransform)(pxr::SdfPath const& id, Transform& transform);

    // Set standard s,q,t transform to hydra.
    bool(CARB_ABI* SetWorldTransform)(pxr::SdfPath const& id, Transform const& transform);

    // get local space transform in 4x4 matrix
    bool(CARB_ABI* GetLocalMatrix)(pxr::SdfPath const& id, pxr::GfMatrix4d& matrix);

    // set local space transform in 4x4 matrix
    bool(CARB_ABI* SetLocalMatrix)(pxr::SdfPath const& id, pxr::GfMatrix4d const& matrix);

    // get world space transform in 4x4 matrix
    bool(CARB_ABI* GetWorldMatrix)(pxr::SdfPath const& id, pxr::GfMatrix4d& matrix);

    // set world space transform in 4x4 matrix
    bool(CARB_ABI* SetWorldMatrix)(pxr::SdfPath const& id, pxr::GfMatrix4d const& matrix);

    /*
     * Per vertex primvar buffers (points, normals, etc.)
     */

    // set points directly without triggering usd notice using generic buffer descriptor
    bool(CARB_ABI* SetPointsBuffer)(pxr::SdfPath const& id, BufferDesc const& bufferDesc);

    // set points directly without triggering usd notice using usd point array
    bool(CARB_ABI* SetPointsArray)(pxr::SdfPath const& id, pxr::VtVec3fArray const& pointsArray);

    /*
     * Instancer
     */
    // set transform of once instance by instance path + instance index
    bool(CARB_ABI* SetInstanceTransform)(const pxr::SdfPath& instancerPath,
                                         uint32_t instanceIndex,
                                         const Transform& transform);

    // Scatter the position data to corresponding instance position slots routed by the indexMap
    bool(CARB_ABI* SetInstancePosition)(const pxr::SdfPath& instancerPath,
                                        const carb::Double3* position,
                                        const uint32_t* indexMap,
                                        const uint32_t& instanceCount);

    // Legacy float support
    bool(CARB_ABI* SetInstancePositionF)(const pxr::SdfPath& instancerPath,
                                         const carb::Float3* position,
                                         const uint32_t* indexMap,
                                         const uint32_t& instanceCount);

    /*
     * Cached Paths
     */
    // get size of prim range at specified prim.
    size_t(CARB_ABI* GetPrimRangePathCount)(const pxr::SdfPath& primPath);

    // This includes paths for prim + all its descendents.
    void(CARB_ABI* GetPrimRangePaths)(const pxr::SdfPath& primPath, pxr::SdfPath* primRangePaths, size_t pathRangeSize);

    void(CARB_ABI* BlockUSDUpdate)(bool val);

    /*
     * Bypass RTX render's skel deformation (in favor of external deformer processing)
    */
    bool(CARB_ABI* GetBypassRenderSkelMeshProcessing)(pxr::SdfPath const& primPath, bool& bypass);

    bool(CARB_ABI* SetBypassRenderSkelMeshProcessing)(pxr::SdfPath const& primPath, bool const& bypass);

    bool(CARB_ABI* SetSkelMeshGraphCallbacks)(SkelMeshGraphCallback setupFunc);
};

} // namespace hydra
} // namespace usd
} // namespace omni
