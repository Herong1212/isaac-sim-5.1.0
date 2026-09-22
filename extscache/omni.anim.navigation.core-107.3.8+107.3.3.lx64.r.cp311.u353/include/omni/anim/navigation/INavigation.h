// Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "INavMeshProvider.h"

#include <carb/IObject.h>
#include <carb/ObjectUtils.h>
#include <carb/Interface.h>
#include <carb/Types.h>
#include <carb/events/IEvents.h>
#include <carb/events/EventsUtils.h>

namespace omni
{
namespace anim
{
namespace navigation
{

/** Fires when the navmesh finishes updating (baking). Payload: "status" (bool), true on success, false for (failure or cancelation) */
const carb::events::EventType kEventTypeNavMeshUpdated = CARB_EVENTS_TYPE_FROM_STR("EVENT_TYPE_NAVMESH_UPDATED");
/** Fires during the progress of navmesh updating (baking) and fired at least once. Payload: "progress" (float), between 0 and 1. */
const carb::events::EventType kEventTypeNavMeshUpdating = CARB_EVENTS_TYPE_FROM_STR("EVENT_TYPE_NAVMESH_UPDATING");


/**
 * Defines a navigation interface for navigation path and meshes.
 */
struct INavigation
{
    CARB_PLUGIN_INTERFACE("omni::anim::navigation::INavigation", 4, 0)

    /**
     * Gets the events stream for the NavMesh processing.
     *
     * @return The events stream for the NavMesh processing.
     */
    carb::events::IEventStreamPtr(CARB_ABI* getNavMeshEventStream)();

    /**
     * Starts a task to bake a NavMesh for currently opened stage.
     *
     * @note The NavMesh will contain areas to match the areas currently defined in this INavigation object. Once baked, the NavMesh areas are not editable.
     * @note This will use a cached version if one is already baked and ready.
     *
     * @see omni::anim::navigation::INavigation::getNavMeshEventStream
     * @see omni::anim::navigation::kEventTypeNavMeshUpdated
     * @return true baking has started successfully, false if failed to start baking.
     */
    bool (CARB_ABI* startNavMeshBaking)();

    /**
     * Starts and waits for baking on a NavMesh for currently opened stage.
     *
     * @note The NavMesh will contain areas to match the areas currently defined in this INavigation object. Once baked, the NavMesh areas are not editable.
     * @note This will use a cached version if one is already baked and ready.
     * @return true if the navmesh baking is completed, false if failed.
     */
    bool (CARB_ABI* startNavMeshBakingAndWait)();

    /**
     * Cancels all pending NavMesh baking tasks.
     */
    void (CARB_ABI* cancelNavMeshBaking)();

    /**
     * Checks if the NavMesh is currently baking.
     *
     * @return true if the NavMesh is currently baking, false if not baking.
     */
    bool (CARB_ABI* isNavMeshBaking)();

    /**
     * Gets the baked NavMesh for the currently open stage.
     *
     * @see omni::anim::navigation::INavigation::getNavMeshEventStream
     * @see omni::anim::navigation::kEventTypeNavMeshUpdated
     *
     * @return The baked NavMesh or nullptr if not yet ready (baked or loaded).
     *
     * @note The returned INavMesh is immutable and thus it can be safely shared between threads.
     */
    INavMeshPtr (CARB_ABI* getNavMesh)();

    /**
     * Creates a new area.
     *
     * @return The index of the new area created.
     */
    int (CARB_ABI* createArea)();

    /**
     * Destroys the area at the specified index.
     *
     * @param areaIndex The index of the area to be removed.
     */
    void (CARB_ABI* destroyArea)(int areaIndex);

    /**
     * Returns the number of navigation areas defined in the stage.
     */
    int (CARB_ABI* getAreaCount)();

    /**
     * Finds an area by name.
     *
     * @param name The name of the area to search for.
     *
     * @return The index found for the specified name or -1 if no area found.
     */
    int (CARB_ABI* findArea)(const char* name);

    /**
     * Get the name of the area at the sepecified index.
     *
     * @param areaIndex The index of the area to access. Should be between 0 and getAreaCount() - 1.
     *
     * @return The area name or nullptr if areaIndex is out of bounds.
     */
    const char* (CARB_ABI* getAreaName)(int areaIndex);

    /**
     *  Sets the name of the area at the specified index.
     *
     * @param areaIndex The index of the area to access. Should be between 0 and getAreaCount() - 1.
     * @param name The new area name.
     *
     * @return true on success, false if areaIndex is out of bounds or if an area by the specified name already exists.
     */
    bool (CARB_ABI* setAreaName)(int areaIndex, const char* name);

    /**
     * Returns the area color given an area index.
     *
     * @param areaIndex The index of the area to access. Should be between 0 and getAreaCount() - 1.
     *
     * @return The color of the area or 0 if areaIndex is out of bounds.
     */
    uint32_t (CARB_ABI* getAreaColor)(int areaIndex);

    /**
     *  Sets the color of the area at the specified index.
     *
     * @param areaIndex The index of the area to access. Should be between 0 and getAreaCount() - 1.
     * @param color The color to set the area to.
     *
     * @return true on success, false if the specified areaIndex is out of bounds.
     */
    bool (CARB_ABI* setAreaColor)(int areaIndex, uint32_t color);

    /**
     *  Gets the default cost of the area at the specified index.
     *
     * @param areaIndex The index of the area to access. Should be between 0 and getAreaCount() - 1.
     *
     * @return The area default cost or -1 on error. Note that -1 is also a valid area cost, to specify that the area is inaccessible.
     */
    float (CARB_ABI* getAreaDefaultCost)(int areaIndex);

    /**
     *  Sets the default cost of the area at the specified index.
     *
     * @param areaIndex The index of the area to access. Should be between 0 and getAreaCount() - 1.
     * @param defaultCost The default cost to set the area to. Must be >= 0 or -1 to specify the area is inaccessible.
     *
     * @return true on success, false if the specified areaIndex is out of bounds.
     */
    bool (CARB_ABI* setAreaDefaultCost)(int areaIndex, float defaultCost);

    /**
     * Sets the random seed to allow for deterministic random outputs.
     *
     * @param randomizerId Identifies a randomizer to set the seed for. This allows each consumer of randomness
     * to get its own deterministic outcomes.
     * @param seed The seed to use for the randomizer.
     *
     * @See INavMesh::queryRandomPoint
     *
     * @return true on success, false on failure. The function fails if an INavMeshProvider has not been set.
     */
    bool (CARB_ABI* setRandomSeed)(const char* randomizerId, uint32_t seed);

    /**
     * Gets the directory that stores various cached Navigation files.
     *
     * @return The directory that stores various cached Navigation files.
     */
    const char* (CARB_ABI* getCacheDir)();

    /**
     * Clears the cached navmesh files in the cache dir.
     *
     * Use this function rather than deleting files directly as the naming conventions are subject to change.
     */
    void (CARB_ABI* clearCacheDir)();

    /**
     * Gets the NavMesh provider that is currently registered.
     *
     * @note you can use this to ensure a provider is registered.
     *
     * @return The NavMesh provider registered or nullptr if none is registered.
     */
    INavMeshProviderPtr (CARB_ABI* getNavMeshProvider)();
};

}
}
}
