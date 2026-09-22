// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#if (!defined(PXR_USD_SDF_PATH_H))
namespace pxr
{
class SdfPath;
};
#endif

#include "KitTypes.h"

#include <carb/Interface.h>
#include <carb/InterfaceUtils.h>
#include <memory>

namespace omni
{
namespace kit
{

struct StageUpdateNode;

struct StageUpdateSettings
{
    bool playSimulations;
    bool playComputegraph;
    bool isPlaying;
};

struct StageUpdateNodeDesc
{
    const char* displayName;

    void* userData;

    int order;

    /**
        Attach usd stage to physics.
        This function gets called when Kit loads a new usd file or create a new scene.
        To convert stageId to stage ref, use
         pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId))
    */
    void(CARB_ABI* onAttach)(long int stageId, double metersPerUnit, void* userData);

    // detach the stage
    void(CARB_ABI* onDetach)(void* userData);

    // simulation was paused
    void(CARB_ABI* onPause)(void* userData);

    // simulation was stopped(reset)
    void(CARB_ABI* onStop)(void* userData);

    // simulation was resumed
    void(CARB_ABI* onResume)(float currentTime, void* userData);

    // this gets called in every update cycle of Kit (typically at each render frame)
    void(CARB_ABI* onUpdate)(float currentTime, float elapsedSecs, const StageUpdateSettings* settings, void* userData);

    /*
        The following call backs are called when there is change in usd scene (e.g. user interaction, scripting, )
        Each plugin should query the usd stage based on provided prim path name and sync changes related to their data
    */
    // this gets called when a new Usd prim was added to the scene
    void(CARB_ABI* onPrimAdd)(const pxr::SdfPath& primPath, void* userData);

    // this gets called when some properties in the usd prim was changed (e.g. manipulator or script changes transform)
    void(CARB_ABI* onPrimOrPropertyChange)(const pxr::SdfPath& primOrPropertyPath, void* userData);

    // this gets called when the named usd prim was removed from the scene
    void(CARB_ABI* onPrimRemove)(const pxr::SdfPath& primPath, void* userData);

    /**
     * Temporary raycast handler.  This will become part of a more general user event handler.
     *
     * @param orig the ray origin.  Set to NULL to send a stop command for grabbing.
     * @param dir the ray direction (should be normalized).
     * @param input whether the input control is set or reset (e.g. mouse down).
     */
    void(CARB_ABI* onRaycast)(const float* orig, const float* dir, bool input, void* userData);
};

struct StageUpdateNodeDescV2 : public StageUpdateNodeDesc
{
    // simulation was resumed
    void(CARB_ABI* onResumeV2)(double currentTime, double absoluteSimTime, void* userData);

    // this gets called in every update cycle of Kit (typically at each render frame)
    void(CARB_ABI* onUpdateV2)(double currentTime,
                               float elapsedSecs,
                               double absoluteSimTime,
                               const StageUpdateSettings* settings,
                               void* userData);
};

struct StageUpdateNodeInfo
{
    const char* name;
    bool enabled;
    int order;
};

typedef void (*OnStageUpdateNodesChangeFn)(void* userData);

struct StageUpdate
{
    virtual StageUpdateNode* createStageUpdateNode(const StageUpdateNodeDesc& desc) = 0;

    virtual void destroyStageUpdateNode(StageUpdateNode* node) = 0;

    virtual size_t getStageUpdateNodeCount() const = 0;

    virtual void getStageUpdateNodes(StageUpdateNodeInfo* nodes) const = 0;

    virtual void setStageUpdateNodeOrder(size_t index, int order) = 0;

    virtual void setStageUpdateNodeEnabled(size_t index, bool enabled) = 0;

    virtual SubscriptionId subscribeToStageUpdateNodesChangeEvents(OnStageUpdateNodesChangeFn onChange,
                                                                      void* userData) = 0;

    virtual void unsubscribeToStageUpdateNodesChangeEvents(SubscriptionId subscriptionId) = 0;

    virtual void attach(long int stageId) = 0;

    virtual void detach() = 0;

    virtual void setPlaying(float currentTime, bool isPlaying, bool isStop /*= false*/) = 0;

    virtual void applyPendingEdit() = 0;

    virtual void update(float currentTime, float elapsedSecs, StageUpdateSettings& settings) = 0;

    virtual void handleAddedPrim(const pxr::SdfPath& primPath) = 0;

    virtual void handleChangedPrimOrProperty(const pxr::SdfPath& primOrPropertyPath, bool& isTransformDirty) = 0;

    virtual void handleRemovedPrim(const pxr::SdfPath& primPath) = 0;

    virtual void handleRaycast(const float* orig, const float* dir, bool input) = 0;


    virtual StageUpdateNode* createStageUpdateNodeV2(const StageUpdateNodeDescV2& desc) = 0;

    virtual void setPlayingV2(double currentTime, double absoluteSimTime, bool isPlaying, bool isStop /*= false*/) = 0;

    virtual void updateV2(double currentTime, float elapsedSecs, double absoluteSimTime, StageUpdateSettings& settings) = 0;
};

using StageUpdatePtr = std::shared_ptr<StageUpdate>;

/**
 * Defines an interface for the editor stage update API part.
 */
struct IStageUpdate
{
    CARB_PLUGIN_INTERFACE("omni::kit::IStageUpdate", 1, 0);

    //------------------------
    // Deprecated interface
    //------------------------

    StageUpdateNode*(CARB_ABI* createStageUpdateNode)(const StageUpdateNodeDesc& desc);

    void(CARB_ABI* destroyStageUpdateNode)(StageUpdateNode* node);

    size_t(CARB_ABI* getStageUpdateNodeCount)();

    void(CARB_ABI* getStageUpdateNodes)(StageUpdateNodeInfo* nodes);

    void(CARB_ABI* setStageUpdateNodeOrder)(size_t index, int order);

    void(CARB_ABI* setStageUpdateNodeEnabled)(size_t index, bool enabled);

    SubscriptionId(CARB_ABI* subscribeToStageUpdateNodesChangeEvents)(OnStageUpdateNodesChangeFn onChange,
                                                                      void* userData);

    void(CARB_ABI* unsubscribeToStageUpdateNodesChangeEvents)(SubscriptionId subscriptionId);

    void(CARB_ABI* attach)(long int stageId);

    void(CARB_ABI* detach)();

    void(CARB_ABI* setPlaying)(float currentTime, bool isPlaying, bool isStop /*= false*/);

    void(CARB_ABI* applyPendingEdit)();

    void(CARB_ABI* update)(float currentTime, float elapsedSecs, StageUpdateSettings& settings);

    void(CARB_ABI* handleAddedPrim)(const pxr::SdfPath& primPath);

    void(CARB_ABI* handleChangedPrimOrProperty)(const pxr::SdfPath& primOrPropertyPath, bool& isTransformDirty);

    void(CARB_ABI* handleRemovedPrim)(const pxr::SdfPath& primPath);

    void(CARB_ABI* handleRaycast)(const float* orig, const float* dir, bool input);


    StageUpdateNode*(CARB_ABI* createStageUpdateNodeV2)(const StageUpdateNodeDescV2& desc);

    void(CARB_ABI* setPlayingV2)(double currentTime, double absoluteSimTime, bool isPlaying, bool isStop /*= false*/);

    void(CARB_ABI* updateV2)(double currentTime, float elapsedSecs, double absoluteSimTime, StageUpdateSettings& settings);

    //---------------
    // New interface
    //---------------

    /**
     * Gets the StageUpdate object with the given name. Creates a new one if it does not exist.
     * Pass nullptr to retrieve the default StageUpdate, which is the StageUpdate object of the default UsdContext.
     *
     * @param name Name of the StageUpdate object.
     *
     * @return The StageUpdate
     */
    StageUpdatePtr(CARB_ABI* getStageUpdateByName)(const char* name);
    inline StageUpdatePtr getStageUpdate(const char* name)
    {
        return getStageUpdateByName(name);
    }
    inline StageUpdatePtr getStageUpdate()
    {
        return getStageUpdateByName(nullptr);
    }

    /**
     * Destroys the StageUpdate with the given name if nothing references it. Does not release the default StageUpdate (name==null).
     *
     * @param name Name of the StageUpdate.
     *
     * @return True if a StageUpdate was deleted, false otherwise. The latter happens when the StageUpdate does not exist, it
     * is in use, or it is the StageUpdate of the default UsdContext.
     */
    bool(CARB_ABI* destroyStageUpdate)(const char* name);
};

/**
 * Gets the StageUpdate object with the given name via cached IStageUpdate interface. Creates a new one if it does not exist.
 * Pass nullptr to retrieve the default StageUpdate, which is the StageUpdate object of the default UsdContext.
 *
 * @param name Name of the StageUpdate object.
 *
 * @return The StageUpdate
 */
inline StageUpdatePtr getStageUpdate(const char* name = nullptr)
{
    auto iface = carb::getCachedInterface<omni::kit::IStageUpdate>();
    return iface == nullptr ? nullptr : iface->getStageUpdate(name);
}

}
}
