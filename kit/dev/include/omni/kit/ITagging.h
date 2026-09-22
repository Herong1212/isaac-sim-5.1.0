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

namespace carb
{
namespace datasource
{
struct IDataSource;
struct Connection;
}
}

namespace omni
{
namespace kit
{

const carb::events::EventType kEventGetTagsFinished = CARB_EVENTS_TYPE_FROM_STR("GET_TAGS_FINISHED");
const carb::events::EventType kEventTagQueryFinished = CARB_EVENTS_TYPE_FROM_STR("TAG_QUERY_FINISHED");
const carb::events::EventType kEventModifyTagFinished = CARB_EVENTS_TYPE_FROM_STR("MODIFY_TAG_FINISHED");
const carb::events::EventType kEventTagServiceConnected = CARB_EVENTS_TYPE_FROM_STR("TAG_SERVICE_CONNECTED");

/**
 * Defines a tagging interface to a running tagging server.
 */
struct ITagging
{
    CARB_PLUGIN_INTERFACE("omni::kit::ITagging", 2, 0);

    /**
     * Check connection to tagging service.
     *
     * @return true if connected to tagging service.
     */
    bool(CARB_ABI* isConnected)(const char* host_url);

    /**
     * Sends a list of urls as a single query to the tagging server. Results can be found by calling getTagsForUrl.
     * When the request returns, an event of type kEventGetTagsFinished will be dispatched.
     *
     * @param urls An array of usd file urls sent to the tagging server.
     * @param nUrls The number of urls.
     */
    void(CARB_ABI* getTags)(const char** urls, const size_t nUrls);

    /**
     * Sends a url & query as a recursive query to the tagging server. The query is a tag that will be matched
     * with all the usd files in the url. If url is a folder, then all files in that folder and subfolders will
     * be checked by the tagging service. Results can be found by calling getTagsForUrl.
     * When the request returns, an event of type kEventTagQueryFinished will be dispatched.
     *
     * @param query
     * @param url
     */
    void(CARB_ABI* queryTags)(const char* query, const char* url);

    /**
     * Returns the tags for the usd file at the given url. Use getTags or queryTags before calling this function.
     *
     * @param url to the usd file that may have tags.
     * @param nTags the number of tags as an output
     * @param filterExcluded true if we should compare system tags and remove excluded ones
     * @param resourceBusy set to true if we are blocked by another thread. This prevents ui blocking.
     * @return A list of tags as a pointer. This must be freed with clearTagsMemory()
     */
    char**(CARB_ABI* getTagsForUrl)(const char* url, size_t& nTags, bool filterExcluded, bool* resourceBusy);

    /**
     * See if url has the query after a recursive or normal search.
     *
     * @param url to the usd file that may have tags.
     * @param query The query we are searching for
     * @param resourceBusy set to true if we are blocked by another thread. This prevents ui blocking.
     * @return true if we have found the query at the given url
     */
    bool(CARB_ABI* urlHasTag)(const char* url, const char* query, bool* resourceBusy);

    /**
     * Frees the memory allocated in getTagsForUrl.
     *
     * @param tags pointer to tags that should be freed.
     * @param nTags the number of tags as an output
     */
    void(CARB_ABI* clearTagsMemory)(char** tags, size_t nTags);

    /**
     * Adds the tag to the usd file at url.
     * When the request returns, an event of type kEventModifyTagFinished will be dispatched.
     *
     * @param url to the usd file.
     * @param tag to add.
     */
    void(CARB_ABI* addTag)(const char* url, const char* tag);

    /**
     * Removes the old tag and adds the new one.
     * When the request returns, an event of type kEventModifyTagFinished will be dispatched.
     *
     * @param url to the usd file.
     * @param oldTag to remove.
     * @param newTag to add.
     */
    void(CARB_ABI* updateTag)(const char* url, const char* oldTag, const char* newTag);

    /**
     * Removes the tag from the usd file at url.
     * When the request returns, an event of type kEventModifyTagFinished will be dispatched.
     *
     * @param url to the usd file.
     * @param tag to remove.
     */
    void(CARB_ABI* removeTag)(const char* url, const char* tag);

    /**
     * Returns the event stream for tagging events.
     *
     * @return carb event stream for tagging.
     */
    carb::events::IEventStream*(CARB_ABI* getTagEventStream)();

    /**
     * Shuts down the plugin
     *
     */
    void(CARB_ABI* shutdown)();
};

}
}
