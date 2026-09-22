// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "LayerTypes.h"

#include <carb/Interface.h>
#include <carb/dictionary/IDictionary.h>


#define LIVE_SYNCING_MAJOR_VER 1
#define LIVE_SYNCING_MINOR_VER 0


namespace omni
{
namespace kit
{
namespace usd
{
namespace layers
{

typedef void(*OnStageResultFn)(bool result, const char* err, void* userData);

/**
 * A Live Session is a concept that extends live workflow for USD layers.
 * Users who join the same Live Session can see live updates with each other.
 * A Live Session is physically defined as follows:
 * 1. It has an unique URL to identify the location.
 * 2. It has a toml file to include the session configuration.
 * 3. It includes a Live Session layer that has extension .live for users to cooperate together.
 * 4. It includes a channel for users to send instant messages.
 * 5. It's bound to a base layer. A base layer is a USD file that your Live Session will be based on.
 */
class LiveSession;

/**
 * LiveSyncing interfaces work to create/stop/manage Live Sessions. It supports to join a Live Session
 * for sublayer, or prim with references or payloads. If a layer is in the local sublayer list, and it's
 * added as reference or payload also. The Live Session can only be joined for the sublayer or reference/payload,
 * but cannot be joined for both. For layer that is added to multiple prims as reference/payload, it supports to
 * join the same Live Session for multiple prims that references the same layer.
 */
struct IWorkflowLiveSyncing
{
    CARB_PLUGIN_INTERFACE("omni::kit::usd::layers::IWorkflowLiveSyncing", 2, 2)

    /**
     * Gets the count of Live Sessions for a specific layer. The layer must be in the layer stack of current UsdContext
     * that layerInstance is bound to. It's possible that getTotalLiveSessions will return 0 even there are Live Sessions
     * on the server as Live Sessions' finding is asynchronous, and this function only returns the count that's discovered
     * currently.
     *
     * @param layerIdentifier The base layer of Live Sessions.
     */
    size_t(CARB_ABI* getTotalLiveSessions)(ILayersInstance* layerInstance, const char* layerIdentifier);

    /**
     * Gets the Live Session at index. The index must be less than the total Live Sessions got from getTotalLiveSessions.
     * Also, the index is not promised to be valid always as it's possible the Live Session is removed.

     * @param layerIdentifier The base layer of Live Sessions.
     * @param index The index to access. REMINDER: The same index may be changed to different Live Session as
     * it does not promise the list of Live Sessions will not be changed or re-ordered.
     */
    LiveSession*(CARB_ABI* getLiveSessionAtIndex)(ILayersInstance* layerInstance, const char* layerIdentifier, size_t index);

    /**
     * The name of this Live Session. It's possible that session is invalid and it will return empty.
     *
     * @param session The Live Session instance.
     */
    const char*(CARB_ABI* getLiveSessionName)(ILayersInstance* layerInstance, LiveSession* session);

    /**
     * The unique URL of this Live Session. It's possible that session is invalid and it will return empty.
     */
    const char*(CARB_ABI* getLiveSessionUrl)(ILayersInstance* layerInstance, LiveSession* session);

    /**
     * The owner name of this session. The owner of the session is the one that has the permission to merge session changes back to
     * base layers. It's possible that session is invalid and it will return empty. REMEMBER: You should not use this
     * function to check if the local instance is the session owner as it's possible multiple instances with the same user join
     * in the Live Session. But only one of them is the real session owner. This funciton is only to check the static ownership
     * that tells you whom the session belongs to. In order to tell the runtime ownership, you should see permissionToMergeSessionChanges.
     *
     * @param session The Live Session instance.
     */
    const char*(CARB_ABI* getLiveSessionOwner)(ILayersInstance* layersInstance, LiveSession* session);

    /**
     * The communication channel of this session. Channel is a concept in Nucleus to pub/sub transient messages
     * so all clients connected to it can communicate with each other. It's possible that session is invalid and it will return empty.
     *
     * @param session The Live Session instance.
     */
    const char*(CARB_ABI* getLiveSessionChannelUrl)(ILayersInstance* layerInstance, LiveSession* session);

    /**
     * A session consists a root layer that's suffixed with .live extension. All live edits are done inside that
     * .live layer during a Live Session. It's possible that session is invalid and it will return empty.
     *
     * @param session The Live Session instance.
     */
    const char*(CARB_ABI* getLiveSessionRootIdentifier)(ILayersInstance* layerInstance, LiveSession* session);

    /**
     * The base layer identifier for this Live Session. It's possible that session is invalid and it will return empty.
     *
     * @param session The Live Session instance.
     */
    const char*(CARB_ABI* getLiveSessionBaseLayerIdentifier)(ILayersInstance* layerInstance, LiveSession* session);

    /**
     * Whether the local user has the permission to merge the Live Session or not. It's possible that the local user is
     * the owner of the Live Session but it returns false as if there are multiple instances with the same user join
     * the same session, only one of them has the merge permission to satisfy the requirement of unique ownership.
     * If the session is not joined, it will return the static ownership based on the owner name.
     *
     * @param session The Live Session instance.
     */
    bool(CARB_ABI* permissionToMergeSessionChanges)(ILayersInstance* layersInstance, LiveSession* session);

    /**
     * If the session is valid. A valid session means it's not removed from disk. It's possible that this session
     * is removed during runtime. This function can be used to check if it's still valid before accessing it.
     *
     * @param session The Live Session instance.
     */
    bool(CARB_ABI* isValidLiveSession)(ILayersInstance* layersInstance, LiveSession* session);

    /**
     * Creates a Live Session for specific sublayer.
     *
     * @param layerIdentifier The base layer.
     * @param sessionName The name of the Live Session. Name can only be alphanumerical characters with hyphens and underscores,
     * and should be prefixed with letter.
     * @see ILayersInstance::get_last_error_type() for more error details if it returns nullptr.
     */
    LiveSession*(CARB_ABI* createLiveSession)(ILayersInstance* layersInstance, const char* layerIdentifier, const char* sessionName);

    /**
     * Joins the Live Session. The base layer of the Live Session must be in the local layer stack of current stage.
     *
     * @param session The Live Session instance.
     * @see ILayersInstance::get_last_error_type() for more error details if it returns false.
     */
    bool(CARB_ABI* joinLiveSession)(ILayersInstance* layersInstance, LiveSession* session);

    /**
     * Joins Live Session by url for specified sublayer. The url must point to a valid Live Session for this layer or it can be created if it does not exist.
     *
     * @param layerIdentifier The base layer identifier of a sublayer.
     * @param liveSessionUrl The Live Session URL to join.
     * @param createIfNotExisted If it's true, it will create the Live Session under the URL specified if no Live Session is found.
     * @see ILayersInstance::get_last_error_type() for more error details if it returns false.
     */
    bool(CARB_ABI* joinLiveSessionByURL)(ILayersInstance* layersInstance, const char* layerIdentifier, const char* liveSessionUrl, bool createIfNotExisted);

    /**
     * Stops the Live Session of base layer if it's in Live Session already. If this layer is added as reference/payload to multiple prims, and some of
     * them are in the Live Session of this layer, it will stop the Live Session for all the prims that reference this layer and in the Live Session.
     * @see stopLiveSessionForPrim to stop Live Session for specific prim.
     *
     * @param layerIdentifier The base layer.
     */
    void(CARB_ABI* stopLiveSession)(ILayersInstance* layersInstance, const char* layerIdentifier);

    /**
     * Stops all Live Sessions in this stage for all layers.
     */
    void(CARB_ABI* stopAllLiveSessions)(ILayersInstance* layersInstance);

    /**
     * If the current stage has any active Live Sessions for all used layers.
     */
    bool(CARB_ABI* isStageInLiveSession)(ILayersInstance* layersInstance);

    /**
     * If a base layer is in any Live Sessions. It includes both Live Sessions for sublayer or reference/payload prims.
     * @see isLayerInPrimLiveSession to check if a layer is in any Live Sessions that are bound to reference/payload prims.
     *
     * @param layerIdentifier The base layer.
     */
    bool(CARB_ABI* isLayerInLiveSession)(ILayersInstance* layersInstance, const char* layerIdentifier);

    /**
     * Gets the current Live Session of the base layer. A layer can only have one Live Session enabled at a time.
     *
     * @param layerIdentifier The base layer.
     */
    LiveSession*(CARB_ABI* getCurrentLiveSession)(ILayersInstance* layersInstance, const char* layerIdentifier);

    /**
     * Checks if this layer is a Live Session layer. A Live Session layer must be managed by a session, and with extension .live.
     *
     * @param layerIdentifier The base layer.
     */
    bool(CARB_ABI* isLiveSessionLayer)(ILayersInstance* layersInstance, const char* layerIdentifier);

    /**
     * Merge changes of the Live Session to base layer specified by layerIdentifier. If layer is not in the Live Session currently,
     * it will return false directly. Live Session for prim is not supported to be merged.
     *
     * @param layerIdentifier The base layer to merge.
     * @param stopSession If it needs to stop the Live Session after merging.
     * @see ILayersInstance::get_last_error_type() for more error details if it returns false.
     */
    bool(CARB_ABI* mergeLiveSessionChanges)(ILayersInstance* layersInstance, const char* layerIdentifier, bool stopSession);

    /**
     * Merge changes of the Live Session to target layer specified by targetLayerIdentifier. If base layer is not in the Live Session currently,
     * it will return false directly. Live Session for prim is not supported to be merged.
     *
     * @param layersInstance Layer instance.
     * @param layerIdentifier The base layer of the Live Session.
     * @param targetLayerIdentifier Target layer identifier.
     * @param stopSession If it's to stop Live Session after merge.
     * @param clearTargetLayer If it's to clear target layer before merge.
     * @see ILayersInstance::get_last_error_type() for more error details if it returns false.
     */
    bool(CARB_ABI* mergeLiveSessionChangesToSpecificLayer)(ILayersInstance* layersInstance,
                                                const char* layerIdentifier,
                                                const char* targetLayerIdentifier,
                                                bool stopSession, bool clearTargetLayer);

    /**
     * Given the layer identifier of a .live layer, it's to find its corresponding session.
     *
     * @param liveLayerIdentifier The live layer of the Live Session.
     */
    LiveSession*(CARB_ABI* getLiveSessionForLiveLayer)(ILayersInstance* layersInstance, const char* liveLayerIdentifier);

    /**
     * Gets the Live Session by url. It can only find the Live Session that belongs to one of the sublayer in the current stage.
     *
     * @param liveSessionURL The URL of the Live Session.
     */
    LiveSession*(CARB_ABI* getLiveSessionByURL)(ILayersInstance* layersInstance, const char* liveSessionURL);

    /**
     * Gets the logged-in user name for this layer. The layer must be in the used layers of current opened stage, from Nucleus,
     * and not a live layer. As client library supports multiple Nucleus servers, the logged-in user for each layer may be different.
     *
     * @param layerIdentifier The base layer.
     */
    const char*(CARB_ABI* getLoggedInUserNameForLayer)(ILayersInstance* layersInstance, const char* layerIdentifier);

    /**
     * Gets the logged-in user id for this layer. The layer must be in the used layers of current opened stage, from Nucleus,
     * and not a live layer. As client library supports multiple Nucleus servers, the logged-in user for each layer may be different.
     *
     * @param layerIdentifier The base layer.
     */
    const char*(CARB_ABI* getLoggedInUserIdForLayer)(ILayersInstance* layersInstance, const char* layerIdentifier);

    /**
     * Opens stage with specified Live Session asynchronously.
     *
     * @param stageUrl The stageUrl to open.
     * @param sessionName The session to open.
     * @param stageResultFn Callback of stage open. This function will call omni::usd::UsdContext::openStage
     *
     * @return false if no session name is provided or other open issues.
     */
    bool(CARB_ABI* openStageWithLiveSession)(
        ILayersInstance* layersInstance, const char* stageUrl, const char* sessionName, OnStageResultFn stageResultFn, void* userData);

    /**
     * Joins the Live Session for prim. The prim must include references or payloads. If it includes multiple references or payloads, an index
     * is provided to decide which reference or payload layer to join the Live Session.

     * @param layersInstance Layer instance.
     * @param session The Live Session to join. It must be the Live Session of the references or payloads of the specified prim.
     * @param primPath The prim to join the Live Session.
     * @see ILayersInstance::get_last_error_type() for more error details if it returns false.
     */
    bool(CARB_ABI* joinLiveSessionForPrim)(ILayersInstance* layersInstance, LiveSession* session, const char* primPath);

    /**
     * Finds the Live Session by name. It will return the first one that matches the name.
     * @param layerIdentifier The base layer to find the Live Session.
     * @param sessionName The name to search.
     */
    LiveSession*(CARB_ABI* findLiveSessionByName)(ILayersInstance* layersInstance, const char* layerIdentifier, const char* sessionName);

    /**
     * Whether the prim is in any Live Sessions or not.
     *
     * @param primPath The prim path to check.
     * @param layerIdentifier The optional layer identifier to check. If it's not specified, it will return true if it's in any Live Sessions.
     * Otherwise, it will only return true if the prim is in the Live Session specified by the layer identifier.
     * @param fromReferenceOrPayloadOnly If it's true, it will check only references and payloads to see if the same
     * Live Session is enabled already in any references or payloads. Otherwise, it checks both the prim specificed by primPath and its references
     * and payloads. This is normally used to check if the Live Session can be stopped as prim that is in a Live Session may not own the Live Session,
     * which is owned by its references or payloads, so it cannot stop the Live Session with the prim.
     */
    bool(CARB_ABI* isPrimInLiveSession)(ILayersInstance* layersInstance, const char* primPath, const char* layerIdentifier, bool fromReferenceOrPayloadOnly);

    /**
     * Whether the layer is in the Live Session that's bound to any prims.
     */
    bool(CARB_ABI* isLayerInPrimLiveSession)(ILayersInstance* layersInstance, const char* layerIdentifier);

    /**
     * Returns all prim paths that this Live Session is currently bound to, or nullptr if no prims are in this Live Session.
     *
     * @param session The session handle.
     */
    carb::dictionary::Item*(CARB_ABI* getLiveSessionPrimPaths)(ILayersInstance* layersInstance, LiveSession* session);

    /**
     * Stops all the Live Sessions that the prim joins to, or the specified Live Session if layerIdentifier is provided.
     */
    void(CARB_ABI* stopLiveSessionForPrim)(ILayersInstance* layersInstance, const char* primPath, const char* layerIdentifier);

    /**
     * It provides option to cancel joining to a Live Session if layer is in joining state.
     * This function only works when it's called during handling eLiveSessionJoining event as all interfaces
     * to join a Live Session is synchronous currently.
     * TODO: Supports asynchronous interface to join a session to avoid blocking main thread.
     */
    LiveSession*(CARB_ABI* tryCancellingLiveSessionJoin)(ILayersInstance* layersInstance, const char* layerIdentifier);

    /**
     * Nanoseconds since the Unix epoch (1 January 1970) of the last time the file was modified. This time is not real time
     * in the filesystem. Joining a session will modify its modified time also.
     *
     * @param session The Live Session instance.
     */
    uint64_t (CARB_ABI* getLiveSessionLastModifiedTimeNs)(ILayersInstance* layerInstance, LiveSession* session);
};

}
}
}
}
