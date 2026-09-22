// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/events/IEvents.h>

namespace omni
{
namespace kit
{
namespace usd
{
namespace layers
{

/**
 * Regards of edit mode, it's extended by Kit to support customized workflow.
 * USD supports to switch edit target so that all authoring will take place in
 * that layer. When it's working with multiple sublayers, this kind of freedom
 * may cause experience issues. The user has to be aware the changes he/she made are
 * not overrided in any stronger layer. We extend a new mode called "auto authoring"
 * is to improve this. In this mode, all changes will firstly go into a middle delegate
 * layer and it will distribute them into their corresponding layers where it has the strongest
 * opinions. So it cannot switch edit target freely, and user does not need to be
 * aware of existence of multi-sublayers and how USD will compose the changes.
 * Besides, there is one more extended mode called "spec linking", which is based on
 * auto authoring. In this mode, user can customize the target layer of specific specs.
 */
enum class LayerEditMode
{
    eNormal, // Normal USD mode that user can freely switch edit target and creates deltas.
    eAutoAuthoring, // Auto authoring mode that user cannot switch authoring layer freely. And all
                    // deltas will be merged to its original layer where the prim specs have strongest opinions.
                    // @see IWorkflowAutoAuthoring for interfaces about auto authoring.
    eSpecsLinking, // Spec linking mode will support to link specified spec changes into specific layers,
                   // including forwarding changes of whole prim, or specific group of attributes.
};

enum class LayerEventType
{
    eInfoChanged, // Layer info changed, which includes:
                  // PXR_NS::UsdGeomTokens->upAxis          PXR_NS::UsdGeomTokens->metersPerUnit
                  // PXR_NS::SdfFieldKeys->StartTimeCode    PXR_NS::SdfFieldKeys->EndTimeCode
                  // PXR_NS::SdfFieldKeys->FramesPerSecond  PXR_NS::SdfFieldKeys->TimeCodesPerSecond
                  // PXR_NS::SdfFieldKeys->SubLayerOffsets  PXR_NS::SdfFieldKeys->Comment
                  // PXR_NS::SdfFieldKeys->Documentation

    eMutenessScopeChanged, // For vallina USD, muteness is only local and not persistent. Omniverse extends
                           // it so it could be persistent and sharable with other users. The muteness scope
                           // is a concept about this that supports to switch between local and global scope.
                           // In local scope, muteness will not be persistent In contract, global scope will
                           // save muteness across sessions. This event is to notify change of muteness scope.

    eMutenessStateChanged, // Change of muteness state.

    eLockStateChanged, // Change of lock state. Lock is a customized concept in Omniverse that supports to
                       // lock a layer it's not editable and savable.

    eDirtyStateChanged, // Change of dirtiness state.

    eOutdateStateChanged, // Change of outdate state. This is only emitted for layer in Nucleus when layer content
                          // is out of sync with server one.

    ePrimSpecsChanged, // Change of layer. It will be emitted along with changed paths of prim specs.

    eSublayersChanged, // Change of sublayers.

    eSpecsLockingChanged, // Change of lock states of specs. It will be emitted along with the changed paths.

    eSpecsLinkingChanged, // Change of linking states of specs. It will be emitted along with the changed paths.

    eEditTargetChanged, // Change of edit target.

    eEditModeChanged, // Change of edit mode. @see LayerEditMode for details.

    eDefaultLayerChanged, // Change default layer. Default layer is an extended concept that's only available in auto
                          // authornig mode. It's to host all newly created prims from auto authoring layer.

    eLiveSessionStateChanged, // Live session started or stopped

    eLiveSessionListChanged, // List of live sessions refreshed, which may because of a session is created or removed.

    eLiveSessionUserJoined, // User joined.

    eLiveSessionUserLeft, // User left.

    eLiveSessionMergeStarted, // Starting to merge live session.

    eLiveSessionMergeEnded,   // Finished to merge live session.

    eUsedLayersChanged,      // Used layers changed in stage. Used layers includes all sublayers, references, payloads or any external layers loaded into stage.
                            // If eSublayersChanged is sent, this event will be sent also.

    eLiveSessionJoining,     // The event will be sent before Live Session is joined.

    eLayerFilePermissionChanged, // The event will be sent when file write/read permission is changed.
};

enum class LayerErrorType
{
    eSuccess,

    eReadOnly,                      // Destination folder or file is read-only
    eNotFound,                      // File/folder/live session is not found, or layer is not in the local layer stack.
    eAlreadyExists,                 // File/folder/layer/live session already existes.
    eInvalidStage,                  // No stage is attached to the UsdContext.
    eInvalidParam,                  // Invalid param passed to API.

    eLiveSessionInvalid,            // The live session does not match the base layer. Or The live session exists,
                                    // but it is broken on disk, for example, toml file is corrupted.
    eLiveSessionVersionMismatch,
    eLiveSessionBaseLayerMismatch,  // The base layer of thie live session does not match the specified one.
                                    // It's normally because user wants to join session of layer B for layer A.
    eLiveSessionAlreadyJoined,
    eLiveSessionNoMergePermission,
    eLiveSessionNotSupported,       // Live session is not supported for the layer if layer is not in Nucleus or already has .live as extension.
                                    // Or it's reported for joining a live session for a reference or payload prim if prim is invalid, or it has
                                    // no references or payloads.
    eLiveSessionNotJoined,

    eUnkonwn
};

class ILayersInstance : public carb::IObject
{
public:
    virtual carb::events::IEventStream* getEventStream() const = 0;

    virtual LayerEditMode getEditMode() const = 0;

    virtual void setEditMode(LayerEditMode editMode) = 0;

    virtual LayerErrorType getLastErrorType() const = 0;

    virtual const char* getLastErrorString() const = 0;
};

}
}
}
}
