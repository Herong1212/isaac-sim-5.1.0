// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "INavController.h"
#include "INavMeshPath.h"
#include "Types.h"

#include <carb/IObject.h>
#include <carb/Interface.h>
#include <carb/ObjectUtils.h>
#include <carb/Types.h>


namespace omni
{
namespace anim
{
namespace navigation
{

/**
 * Defines an interface for accessing the baked NavMesh for perform queries for pathfinding.
 *
 * The NavMesh will be baked into a PXR_NS::UsdGeomMesh in the session layer and build any runtime data need.
 */
class INavMesh : public carb::IObject
{
public:
   /**
     * Queries to find a shortest path on the NavMesh between a start and end position.
     *
     * @param startPos The starting position of the path.
     * @param endPos The ending position of the path.
     * @param areaCosts The optional overridden set of areas costs to compute the shortest path from, or nullptr to use default area costs.
     * @param agentRadius The radius of the agent that is calling this to navigates the path queried.
     * @param agentHeight The height of the agent that is calling this to navigates the path queried.
     * @param straighten true to straight the shorted path found for A* or false to not.
     * @param prevNavMeshPath The previous path to use for A* pathfinding. This is used to avoid recomputing the full path again.
     *
     * @return An INavMeshPathPtr object containing the points along the path. nullptr if no NavMesh is available,
     * startPos/endPos are not on the NavMesh or a path between them cannot be established.
     */
    virtual INavMeshPathPtr queryShortestPath(const carb::Float3& startPos, const carb::Float3& endPos,
                                              const float* areaCosts = nullptr,
                                              float agentRadius = 0.0f, float agentHeight = 0.0f,
                                              bool straighten = true,
                                              INavMeshPathPtr prevNavMeshPath = nullptr) const = 0;

    /**
     * Queries to find the closest point on the NavMesh to the specified target.
     *
     * @param target The target position to be closest to.
     * @param point The closest point found to the target position.
     * @param areaIndices The optional an array of area indices to use for the closest point within or nullptr to use all areas.
     * @param areaCount The element count in the areaIndices array. Must not exceed INavMesh::getAreaCount().
     * @param agentRadius The radius of the agent that is calling this to navigates the path queried.
     * @param agentHeight The height of the agent that is calling this to navigates the path queried.
     * @param searchIslandId The id of the island to search for the closest point. If -1, to find the closest point on any island.
     * @param foundIslandId The id of the island that the closest point is found on.
     *
     * @return true if a closest point could be found, false on error.
     */
    virtual bool queryClosestPoint(const carb::Float3& target, carb::Float3* point,
                                   const int* areaIndices = nullptr, int areaCount = 0,
                                   float agentRadius = 0.0f, float agentHeight = 0.0f,
                                   int searchIslandId = -1,  int* foundIslandId = nullptr) const = 0;

    /**
     * Queries to find a random point on the NavMesh.
     *
     * @param randomizerId Identifies a randomizer to set the seed for. This allows each consumer of randomness
     * to get its own deterministic randomizer. See INavigation::setRandomSeed.
     * @param point The random point to be output as a result.
     * @param areaProbabilities The optional indexed array of weighted probabilities to randomize for each area.
     * @param agentRadius The radius of the agent that is calling this to navigates the path queried.
     * @param agentHeight The height of the agent that is calling this to navigates the path queried.
     *
     * @return true if a random point could be found, false on error.
     */
    virtual bool queryRandomPoint(const char* randomizerId, carb::Float3* point,
                                  const float* areaProbabilities,
                                  float agentRadius = 0.0f, float agentHeight = 0.0f) const = 0;

    /**
     * Gets the minimum height of the navigation agent.
     * This represents the vertical space an agent occupies when navigating the mesh.
     * @return The minimum height of the agent in world units.
     */
    virtual float getAgentMinHeight() const = 0;

    /**
     * Gets the minimum radius of the navigation agent based on the baked navmesh.
     *
     * This represents the horizontal space an agent occupies when navigating the mesh.
     * @return The minimum radius of the agent in world units.
     */
    virtual float getAgentMinRadius() const = 0;

    /**
     * Gets the maximum radius of the navigation agent based on the baked navmesh.
     *
     * This represents the horizontal space an agent occupies when navigating the mesh.
     * @return The maximum radius of the agent in world units.
     */
    virtual float getAgentMaxRadius() const = 0;

    /**
     * Gets the maximum step height the agent can climb based on the baked navmesh.
     *
     * This determines how high of a ledge or step the agent can traverse.
     * @return The maximum step height in world units.
     */
    virtual float getAgentMaxStepHeight() const = 0;

    /**
     * Gets the maximum slope angle the agent can traverse based on the baked navmesh.
     *
     * This determines how steep of an incline the agent can climb.
     * @return The maximum slope angle in degrees.
     */
    virtual float getAgentMaxSlope() const = 0;

    /**
     * Gets the minimum radius of the island based on the baked navmesh.
     *
     * This represents the minimum radius of the island that the agent can navigate.
     * @return The minimum radius of the island in world units.
     */
    virtual float getAgentMinIslandRadius() const = 0;

    /**
     * Gets the number of areas defined in the navmesh.
     *
     * @return The number of areas in the NavMesh.
     */
    virtual int getAreaCount() const = 0;

    /**
     * Gets the area name for the given index defined in the navmesh.
     *
     * @param areaIndex The index of the area to access. Should be between 0 and getAreaCount() - 1.
     *
     * @return The area name or nullptr on error.
     */
    virtual const char* getAreaName(int areaIndex) const = 0;

    /**
     * Gets the area cost for the given index defined in the navmesh.
     *
     * @param areaIndex The index of the area to access. Should be between 0 and getAreaCount() - 1.
     *
     * @return The area cost or 0.0f on error.
     */
    virtual float getAreaCost(int areaIndex) const = 0;

    /**
     * Gets the number of mesh triangles needed to visualize the navmesh surface.
     *
     * @param areaIndex The index of the area to access. Should be between 0 and getAreaCount() - 1.
     *
     * @return The triangle count or -1 on error.
     */
    virtual int getDrawTriangleCount(int areaIndex) const = 0;

    /**
     * Gets mesh triangles for visualization of the navmesh surface.
     *
     * @param areaIndex The index of the area to access. Should be between 0 and getAreaCount() - 1.
     * @param vertices (out) pointer to the first vertex. See vertexStride.
     * @param vertexStride vertices in the output are assumed to be vertexStride bytes apart. If vertices points an array of sequential carb::Float3 objects, pass sizeof(carb::Float3) for vertexStride.
     * @param triangleCount The number of triangles. Note that the vertices array must have space for 3 * triangleCount vertices.
     *
     * @see getDrawTriangleCount
     */
    virtual int getDrawTriangles(int areaIndex, carb::Float3* vertices, int vertexStride, int triangleCount) const = 0;

    /**
     * Gets the number of lines needed for visualizing the navmesh outline.
     *
     * @param borderOnly true if only the border lines be drawn, false if detailed edges also
     *
     * @return The number of lines.
     */
    virtual int getDrawLineCount(bool borderOnly) const = 0;

    /**
     * Gets the lines for visualization of the navmesh outline.
     *
     * @see getDrawLineCount
     *
     * @param borderOnly true if only the border lines be drawn, false if detailed edges
     * @param firstPoints Points the carb::Float3 object where the first point of the first line will be written.
     * The carb::Float3 object that will take the first point of the second line is expected to be at
     * firstPointsStride offset (in bytes) from the address of the first point of the first line, and so on.
     * @param firstPointsStride See firstPoints.
     * @param secondPoints By analogy, see firstPoints.
     * @param secondPointsStride By analogy, see firstPointStride.
     * @param lineCount The number lines. Must be equal to the value returned by getDrawLineCount.
     *
     * @return The number of lines.
     */
    virtual int getDrawLines(bool borderOnly,
        carb::Float3* firstPoints, int firstPointsStride,
        carb::Float3* secondPoints, int secondPointsStride,
        int lineCount) const = 0;

    /**
     * Gets a signature to define and encoded hash representation of the mesh data that was baked.
     *
     * @note You can use this to compare within some tolerance the equality of 2 navmesh that have been generated.
     * @return A signature to define and encoded hash representation of the mesh data that was baked.
     */
    virtual uint32_t getMeshSignature() const = 0;

    /**
     * Creates a controller for agents and obstacles that navigate on the NavMesh.
     *
     * @param params The parameters for the controller.
     * @return A pointer to the created controller.
     */
    virtual INavControllerPtr createController(const omni::anim::navigation::INavController::ControllerParams& params) const = 0;
};

using INavMeshPtr = carb::ObjectPtr<INavMesh>;

}
}
}
