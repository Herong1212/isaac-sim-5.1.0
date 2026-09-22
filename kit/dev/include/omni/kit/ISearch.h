// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>
#include <carb/events/IEvents.h>

namespace omni
{
namespace kit
{

const carb::events::EventType kEventSearchFinished = CARB_EVENTS_TYPE_FROM_STR("SEARCH_FINISHED");

/**
 * Defines an interface for the search service plugin.
 *
 * This plugin handles communication between the content window and the search service python client.
 */
struct ISearch
{
    CARB_PLUGIN_INTERFACE("omni::kit::search::ISearch", 1, 0);

    /**
     * Attempt to discover the search service
     *
     * @param url host url
     */
    void(CARB_ABI* tryConnection)(const char* url);

    /**
     * Return true if we have discovered the search service at this host url
     *
     * @param url host url
     * @return True if found
     */
    bool(CARB_ABI* isConnected)(const char* url);

    /**
     * Set connection status (called from python)
     *
     * @param hostName host Name (not full url)
     * @param isConnected true if connected, false if not
     */
    void(CARB_ABI* setConnection)(const char* hostName, bool isConnected);

    /**
     * Perform a recursive file and tag search
     *
     * @param query The search query.
     * @param parent The parent url to search, including the host name.
     */
    void(CARB_ABI* recursiveSearch)(const char* query, const char* parent);

    /**
     * Status of search plugin connection. Returns true if connection attempt is pending.
     *
     * @param url The host url
     * @return False if search is ready or unavailable. True if a connection attempt is pending.
     */
    bool(CARB_ABI* connectionPending)(const char* url);

    /**
     * Status of search
     *
     * @return True if search is ongoing.
     */
    bool(CARB_ABI* isSearching)();

    /**
     * Set status of search (called from python)
     *
     * @param isSearching True if searching.
     */
    void(CARB_ABI* setSearching)(bool isSearching);

    /**
     * Add a search result to the internal cache.
     *
     * @param query The search query
     * @param result The path to a file matching the query
     * @param path The parent url
     */
    void(CARB_ABI* addResult)(const char* query, const char* result, const char* path);

    /**
     * Get all the results from a query from the cache. Call clearMemory afterwards to cleanup.
     *
     * @param query The search query
     * @param path The parent url
     * @param nResults output: number of results.
     * @return list of result paths
     */
    char**(CARB_ABI* populateResults)(const char* query, const char* path, size_t* nResults);

    /**
     * clear memory from populateResults
     *
     * @param results Memory to clear
     * @param nResults Number of results from populateResults
     */
    void(CARB_ABI* clearMemory)(char** results, size_t nResults);

    /**
     * Search events occur when the search is finished.
     *
     * @return Search event stream
     */
    carb::events::IEventStream*(CARB_ABI* getSearchEventStream)();

    /**
     * Shutdown the plugin
     *
     */
    void(CARB_ABI* shutdown)();
};
}
}
