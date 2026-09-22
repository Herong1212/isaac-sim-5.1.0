// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

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
 * Defines a controller controller for agents and obstacles that navigate on the NavMesh.
 * Agents are able to set their goal position and the controller will attempt to find a target path and next position.
 */
class INavController : public carb::IObject
{
public:
    /**
     * Parameters for the controller.
     */
    struct ControllerParams
    {
        /**
         * The distance an agent is pushed away from obstacles.
         * The distance is defined relative to the sampling distance.
         */
        float obstaclePadding = 0.1f;
        /**
         * The distance an agent is allowed to push into obstacles if two or more obstacles are near.
         * The distance is defined relative to the sampling distance.
         */
        float passagePadding = 1.0f;
        /**
         * The distance an agent is pushed away from other agents.
         * The distance is defined relative to the sampling distance.
         */
        float agentPadding = 0.5f;
        /**
         * The minimum velocity an agent must have for the agent padding to be applied.
         * Agents that are close to the goal position or in congested areas that get slowed down
         * have no padding applied and are allowed to get closer to other agents.
         */
        float agentPaddingMinVelocity = 0.1f;
    };


    /**
     * Parameters for the debug lines.
     */
    struct DebugParams
    {
        /**If true, the bounds of the obstacles are created. */
        bool getObstacleBounds = false;
        /** If true, edges of the navigation mesh that are blocked by obstacles are created. */
        bool getObstructedNavMeshEdges = false;
        /** If true, the distance field of the obstacles is created. */
        bool getObstacleDistanceField = false;
        /** If true, the distance field of the navigation mesh is created. */
        bool getBorderDistanceField = false;
        /** If true, the distance field of the navigation mesh is created. */
        bool getAreaDistanceField = false;
        /** If true, the clearance field of the navigation mesh is created. */
        bool getClearanceField = false;
        /** If true, the lines from the query point to all visible obstacles and agents are created. */
        bool getVisibilityLines = false;
        /** If true, the agents are created. */
        bool getAgents = false;
        /** If true, lines to the goals of the agents are created. */
        bool getAgentGoals = false;
        /** If true, the paths of the agents are created. */
        bool getAgentPaths = false;
        /**
         * If >= 0, the area distance field for the area costs of this agent is returned.
         * If < 0, the area distance field for the costs set by setAreaCosts() is returned.
         * If no call has been made to setAreaCosts(), the area distance field of the navigation mesh is returned.
         */
        int agentId = -1;
    };


    /**
     * Sets the area costs for the controller.
     *
     * This allows a controller to override all the area costs from the default navmesh area costs.
     *
     * @param areaCosts The area costs to set.
     * @param areaCostsCount The number of area costs to set.
     */
    virtual void setAreaCosts(const float* areaCosts, int areaCostsCount) = 0;

    /**
     * Creates agents. Agents can be simulated to move to their updated goal positions.
     *
     * @param agentIds The agentIds to be created.
     * @param agentCount The number of agents.
     * @param positions The positions of each agent.
     * @param velocities The velocities of the agents.
     * @param radii The radius of each agent.
     * @param heights The height of each agent.
     *
     * @return true if all agents have been created. false if some agents already exist.
     */
    virtual bool createAgents(const int* agentIds, int agentCount,
                              const carb::Float3* positions,
                              const float* velocities,
                              const float* radii,
                              const float* heights) = 0;

   /**
    * Destroys agents.
    *
    * @param agentIds The agentIds to be destroyed.
    * @param agentCount The number of agents to be destroyed.
    *
    * @return true if all agents were destroyed. false if some agents do not exist.
    */
    virtual bool destroyAgents(const int* agentIds, int agentCount) = 0;

   /**
    * Updates the agents transforms, velocities and goal positions.
    *
    * @param agentIds The ids of the a to transform.
    * @param agentCount The number of agents.
    * @param positions The optional updated positions of the agents.
    * @param velocities The optional updated velocities of the agents. If nullptr, the velocities are not updated.
    * @param radii The optional radii to use for the agents. For agent interaction, you may want to reduce or increase the agent radii.
    * @param heights The optional heights to use for the agents. For agent interaction, you may want to reduce or increase the agent heights.
    * @param goalPositions The optional target goal positions of the agents.
    * @param areaCosts The optional overridden set of areas costs to compute the shortest path from, or nullptr to use default area costs.
    *
    * @return true if some agents were updated. false if all transforms are the same as before.
    */
    virtual bool updateAgents(const int* agentIds, int agentCount,
            const carb::Float3* positions = nullptr,
            const float* velocities = nullptr,
            const float* radii = nullptr,
            const float* heights = nullptr,
            const carb::Float3* goalPositions = nullptr,
            const float* areaCosts = nullptr) = 0;

   /**
    * Sets the ignored obstacles for an agent.
    *
    * @param agentId The id of the agent to set the ignored obstacles for.
    * @param obstacleIds The ids of the obstacles to ignore.
    * @param obstacleCount The number of obstacles to ignore.
    */
    virtual void setAgentIgnoredObstacle(int agentId, const int* obstacleIds, int obstacleCount) = 0;

   /**
    * Gets the agents in the stage that are near to a specified position.
    *
    * @param position The position to check from.
    * @param maxDistance The maximal distance to check for agents.
    * @param agentIds A buffer to receive the ids of the agents.
    *
    * @return The number of agents returned.
    */
    virtual int getAgentsNearby(const carb::Float3& position, float maxDistance, Int32Array& agentIds) const = 0;

   /**
    * Simulates the agents requesting to find their next shortest position on this navmesh reach their goals
    * whilst avoiding other agents and obstacles.
    *
    * @param time The delta time (in seconds).
    * @param debugLines If not nullptr, the debug lines are filled with path computation information such as the
    * triangles visited by the A* algorithm as in the findShortestPath methods
    */
    virtual void simulateAgents(float time, DebugLines* debugLines = nullptr) = 0;

   /**
    * Saves the current simulation state of the agents.
    *
    **/
    virtual void saveSimulationState() = 0;

    /**
    * Restores the simulation state of the agents.
    **/
    virtual void restoreSimulationState() = 0;

   /**
    * Gets the simulation results of the agents next positions to move to.
    *
    * @param agentIds The agentIds to get the simulation results for.
    * @param agentCount The number of agents.
    * @param nextPositions The array of next positions to move to.
    */
    virtual void getSimulatedAgents(const int* agentIds, int agentCount, Vec3Array& nextPositions) const = 0;

   /**
    * Gets the current path of agent
    *
    * @param agentId The ID of the agent
    */
    virtual omni::anim::navigation::INavMeshPathPtr getAgentPath(int agentId) const = 0;

   /**
    * Creates obstacles for dynamic meshes.
    *
    * @note vertices must not be shared between obstacles.
    *
    * @param obstacleIds The ids of the obstacles.
    * @param obstacleCount The number of obstacles to create.
    * @param transforms The transforms of the obstacles. 16 floats per transform.
    * @param vertexOffsets The first vertex of each obstacle in the vertices array.
    * @param triangleOffsets The first triangle of each obstacle in the triangleIds array.
    * @param vertices The vertices of the union of all obstacles.
    * @param vertexCount The number of vertices in the union of all obstacles.
    * @param triangleIds The triangle indices of the union of all obstacles.
    * @param triangleCount The number of triangles in the union of all obstacles.
    *
    * @return true if all obstacles have been created. false if some obstacles already exist.
    */
    virtual bool createObstacles(const int* obstacleIds, int obstacleCount, const float** transforms,
                                 const int* vertexOffsets, const int* triangleOffsets,
                                 const carb::Float3* vertices, int vertexCount,
                                 const int* triangleIds, int triangleCount) = 0;
   /**
    * Destroys obstacles.
    *
    * @param obstacleIds The ids of the obstacles to destroy.
    * @param obstacleCount The number of obstacle ids to destroy.
    *
    * @return true if all obstacles were destroyed. false if some obstacles do not exist.
    */
    virtual bool destroyObstacles(const int* obstacleIds, int obstacleCount) = 0;

   /**
    * Updates the obstacle transforms for the specified obstacles.
    *
    * @param obstacleIds The ids of the obstacles to transform.
    * @param obstacleCount The number of obstacle ids.
    * @param transforms The new transforms of the obstacles.
    *
    * @return true if some obstacles were updated. false if all transforms are the same as before.
    */
    virtual bool updateObstacles(const int* obstacleIds, int obstacleCount, const float** transforms) = 0;

   /**
    * Gets the obstacles in the stage that are near to a specified position.
    *
    * @param position The position to check from.
    * @param maxDistance The maximal distance to check for obstacles.
    * @param obstacleIds A buffer to receive the ids of the obstacles.
    *
    * @return The number of obstacles returned.
    */
    virtual int getObstaclesNearby(const carb::Float3& position, float maxDistance,
                                   Int32Array& obstacleIds) const = 0;


    /**
     * Queries to find a shortest path on the NavMesh between a start and end position.
     *
     * @param startPos The starting position of the path.
     * @param endPos The ending position of the path.
     * @param areaCosts The optional overridden full set of areas costs to compute the shortest path from, or nullptr to use default area costs.
     * @param agentRadius The radius of the agent that is calling this to navigates the path queried.
     * @param agentHeight The height of the agent that is calling this to navigates the path queried.
     * @param agentId The id of the agent that is calling this to navigates the path queried.
     * @param straighten true to straight the shorted path found for A* or false to not.
     * @param prevNavMeshPath The previous path to use for A* pathfinding. This is used to avoid recomputing the path.
     *
     * @return An INavMeshPathPtr object containing the points along the path. nullptr if no NavMesh is available,
     * startPos/endPos are not on the NavMesh or a path between them cannot be established.
     */
    virtual INavMeshPathPtr queryShortestPath(const carb::Float3& startPos, const carb::Float3& endPos,
                                              float agentRadius = 0.0f, float agentHeight = 0.0f, int agentId = -1,
                                              bool straighten = true, INavMeshPathPtr prevNavMeshPath = nullptr) const = 0;

    /**
    * Queries to find the closest point on the NavMesh to the specified target.
    *
    * @param target The target position to be closest to.
    * @param point The closest point found to the target position.
    * @param areaIndices The optional set of area indices to use for the closest point within or nullptr to use all areas.
    * @param areaCount The number of area indices in the areaIndices array to use. Must not exceed INavMesh::getAreaCount().
    * @param agentRadius The radius of the agent that is calling this to navigates the path queried.
    * @param agentHeight The height of the agent that is calling this to navigates the path queried.
    * @param agentId The id of the agent that is calling this to navigates the path queried.
    * @param searchIslandId The id of the island to search for the closest point. If -1, to find the closest point on any island.
    * @param foundIslandId The id of the island that the closest point is found on.
    *
    * @return true if a closest point could be found, false on error.
    */
    virtual bool queryClosestPoint(const carb::Float3& target, carb::Float3* point,
                                   const int* areaIndices = nullptr, int areaCount = 0,
                                   float agentRadius = 0.0f, float agentHeight = 0.0f, int agentId = -1,
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
    * @param agentId The id of the agent that is calling this to navigates the path queried.
    *
    * @return true if a randopm point could be found, false on error.
    */
    virtual bool queryRandomPoint(const char* randomizerId, carb::Float3* point,
                                  const float* areaProbabilities,
                                  float agentRadius = 0.0f, float agentHeight = 0.0f, int agentId = -1) const = 0;

    /**
     * Creates debug lines for obstacles that can be retreived via the method getObstaclesDebugLines.
     * The lines are cleared before each call that modifies obstacles and updated by the call.
     *
     * @param params The debug parameters.
     * @param debugLines The debug lines returned.
     * @param agentMaxRadius The maximum radius around each agent to create debug lines for. Use 0.0f to not filter by agent radius.
     */
    virtual void createDebugLines(const DebugParams& params, DebugLines& debugLines, float agentMaxRadius = 0.0f) = 0;

};

using INavControllerPtr = carb::ObjectPtr<INavController>;
}
}
}
