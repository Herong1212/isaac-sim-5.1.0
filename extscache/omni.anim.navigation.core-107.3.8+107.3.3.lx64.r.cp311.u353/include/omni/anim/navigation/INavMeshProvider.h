// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "INavMesh.h"

#include <carb/IObject.h>
#include <carb/Interface.h>
#include <carb/ObjectUtils.h>
#include <carb/Types.h>
#include <carb/logging/Log.h>


namespace omni
{
namespace anim
{
namespace navigation
{

/**
 * Defines an interface for accessing the baked NavMesh for perform
 */
class INavMeshProvider : public carb::IObject
{
public:

    struct AgentParams
    {
        float minHeight;
        float minRadius;
        float maxRadius;
        float maxStepHeight;
        float maxFloorSlopeInDegrees;
        float minIslandRadius;

        AgentParams():
            minHeight(1.0f),
            minRadius(0.1f),
            maxRadius(1.0f),
            maxStepHeight(0.4f),
            maxFloorSlopeInDegrees(45.0f),
            minIslandRadius(500.0f)
        {
        }

        AgentParams(float minHeight, float minRadius, float maxRadius, float maxStepHeight, float maxFloorSlopeInDegrees, float minIslandRadius):
            minHeight(minHeight),
            minRadius(minRadius),
            maxRadius(maxRadius),
            maxStepHeight(maxStepHeight),
            maxFloorSlopeInDegrees(maxFloorSlopeInDegrees),
            minIslandRadius(minIslandRadius)
        {
        }
    };

    /**
    * NavMesh progress callback function.
    *
    * @param progress The amount of progress between 0.0-1.0
    * @param userData The user data passed to create (below)
    */
    typedef bool (*OnProgressCallbackFn)(float progress, void* userData);

    /**
     * Creates a NavMesh by taking the triangle mesh geometry and baking it into a runtime representation used for pathfinding.
     *
     * @param params The user-specified parameters for the baking.
     * @param vertices The array of vertices. Should contain 3 * vertexCount elements (x, y, z).
     * @param upAxis The up axis (x=0, y=1, z=2).
     * @param vertexCount The number of vertices.
     * @param triangleIndices The array of vertex indices. Should contain 3 * triangleCount elements.
     * @param triangleAreas The area is an integer value. In the shortest path computation, each area has its own
     *  cost associated with it. The length of this array must be equal to the number of triangles.
     *  If the pointer is nullptr, the area of all treangles is set to 0.
     * @param triangleCount The number of triangles.
     * @param areaNames The array of area names. Should contain areaCount elements.
     * @param areaCosts The array of area costs. Should contain areaCount elements.
     * @param areaCount The number of areas passed.
     * @param includeVolumeBounds The clipping volume bounds to include geometry in the navigation mesh. The bounds are 6 float values per volume (min xyz, max xyz)
     * @param includeVolumeAreas The area index for each included volume.
     * @param includeVolumeCount The number of included volumes.
     * @param excludeVolumeBounds The clipping volume bounds to exclude geometry from the navigation mesh. The bounds are 6 float values per volume (min xyz, max xyz)
     * @param excludeVolumeCount The number of excluded volumes.
     * @param progressFn This is called when any progress is made and if callback return false, then the user has cancelled and should be returned nullptr.
     * @param userData The userData to passed to the progressFn callback.
     *
     * @return The NavMesh that was created, or nullptr on error.
     */
    virtual INavMeshPtr create(
        const AgentParams& params,
        int upAxis,
        const float* vertices, int vertexCount,
        const int* triangleIndices, const int* triangleAreas, int triangleCount,
        const char* const* areaNames, const float* areaCosts, int areaCount,
        const float* includeVolumeBounds, const int* includeVolumeAreas, int includeVolumeCount,
        const float* excludeVolumeBounds, int excludeVolumeCount,
        OnProgressCallbackFn progressFn, void* userData) const = 0;

    /**
     * Gets the size of memory needed to save the NavMesh to file.
     *
     * @see save()
     */
    virtual size_t getSize(const INavMeshPtr& navMesh) const = 0;

    /**
     * Saves this NavMesh to the data pointer specifed.
     *
     * @param navMesh The NavMesh to save to memory.
     * @param data The data to be written into up to the size specied.
     * @param size The size of the data passed for writting.
     *
     * @see getSize
     *
     * @return The size of the data written with saving.
     */
    virtual size_t save(const INavMeshPtr& navMesh, uint8_t* data, size_t size) const = 0;

    /**
     * Loads a previous baked and saved NavMesh.
     *
     * @param data The saved NavMesh data to be loaded.
     * @param size The size of the data being loaded.
     *
     * @return The NavMesh that was loaded.
     */
    virtual INavMeshPtr load(const uint8_t* data, size_t size) const = 0;

    /**
     * See INavigation::setRandomSeed
     */
    virtual void setRandomSeed(const char* randomizerId, uint32_t seed) = 0;
};

using INavMeshProviderPtr = carb::ObjectPtr<INavMeshProvider>;

}
}
}
