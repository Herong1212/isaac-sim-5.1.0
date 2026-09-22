// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include <carb/Types.h>

#include <list>
#include <string>

namespace omni
{
namespace geometry
{
struct Geometry
{
    CARB_PLUGIN_INTERFACE("omni::geometry::Geometry", 0, 1)
    /*
    ABI Definitions
    */

    bool(CARB_ABI* triangulate)(long int stageId, const char* inputPath, const char* outputPath);

    /**
     * @param stageId Identfier for stage to work in
     * @param layerPath The path of the layer in which to create the collision representation.  If NULL or zero-length,
     * the root layer is used
     * @param inputPath The path of the original graphics mesh
     * @param outputRoot The path of the new collision grouping
     * @param proxyName If not NULL or zero-length, the root name of the collision meshes
     * @param maxConvexHulls How many convex hulls can be used in the decomposition.  If set to 1, the convex hull of
     * the mesh vertices is used
     * @param maxNumVerticesPerCH Maximum number of vertices per convex hull
     * @param usePlaneShifting Whether or not to use plane shifting when building the hull
     * @param resolution Voxel resolution for VHACD when convex decomposition is performed (maxConvexHulls > 1)
     * @param visible Whether or not to make the collision hulls visible
     * @return number of convex hulls, return 0 in case of failure
     */
    int(CARB_ABI* createConvexHull)(long int stageId,
                                    const char* layerPath,
                                    const char* inputPath,
                                    const char* outputRoot,
                                    const char* proxyName,
                                    const int maxConvexHulls,
                                    const int maxNumVerticesPerCH,
                                    const bool usePlaneShifting,
                                    const int resolution,
                                    const bool visible);

    bool(CARB_ABI* createConvexHullFromSkeletalMesh)(long int stageId,
                                                     const char* inputMeshPath,
                                                     const char* proxyName,
                                                     const int maxConvexHulls,
                                                     const int maxNumVerticesPerCH,
                                                     const int resolution,
                                                     const bool makeConvexHullsVisible);

    // It applies for all proxy prims, such as triangle proxy prim as well as convex proxy prim
    bool(CARB_ABI* removeConvexHull)(long int stageId, const char* outputPath);

    // Return a UsdGeomCube at path outputPath
    bool(CARB_ABI* computeAABB)(long int stageId, const char* inputPath, const char* outputPath);

    // Return a UsdGeomSphere at path outputPath
    bool(CARB_ABI* computeBoundingSphere)(long int stageId, const char* inputPath, const char* outputPath);
};
}
}
