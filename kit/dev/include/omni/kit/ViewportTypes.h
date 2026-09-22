// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/events/EventsUtils.h>

namespace carb
{
struct Double4x4
{
    double m[16];
};

namespace renderer
{
struct Renderer;
struct Context;
}

namespace scenerenderer
{
struct SceneRenderer;
struct Context;
}
}

namespace rtx
{
namespace resourcemanager
{
class RpResource;
}
}

namespace carb
{
namespace sensors
{
enum class SensorType;
}
namespace renderer
{
enum class FrameDataType;
}
}
namespace omni
{
namespace usd
{
using TokenH = uint64_t;
typedef int32_t ViewportHandle;

namespace hydra
{
enum class EngineCreationFlags : uint32_t;
}

}
namespace kit
{

typedef uint64_t SubscriptionId;
constexpr uint64_t kInvalidSubscriptionId = 0xFFFF'FFFF'FFFF'FFFFULL;

enum class ViewportMenuAlignment
{
    eTopLeft,
    eTopRight,
    eCount
};

typedef bool (*CheckCameraOverrideFn)(void* userdata);
typedef bool (*ApplyCameraOverrideFn)(carb::Double4x4& worldToView,
                                      carb::Double3& translate,
                                      carb::Double2& rotate,
                                      void* userdata);
typedef void (*ResetCameraOverrideFn)(void* userdata);

typedef void (*OnQueriedNextPickedWorldPositionFn)(const carb::Double3* worldPos, void* userData);

struct CameraOverrideDesc
{
    CheckCameraOverrideFn checkCameraOverrideActive;
    ApplyCameraOverrideFn applyCameraOverride;
    ResetCameraOverrideFn resetCameraOverride;
    void* userdata;
};

enum class ViewportPrimReferencePoint
{
    eBoundBoxCenter,
    eBoundBoxLeft,
    eBoundBoxRight,
    eBoundBoxTop,
    eBoundBoxBottom
};

struct DropHelper
{
    bool pickable;
    bool addOutline;
    void* userPointer;
    bool(CARB_ABI* onDropAccepted)(const char* url, void* userPointer);
    std::string(CARB_ABI* onDrop)(
        const char* url, const char* target, const char* viewport_name, const char* context_name, void* userPointer);
    void(CARB_ABI* onPick)(const char* url, const char* target, const char* context_name, void* userPointer);
};

struct DropHelperNode
{
    bool accepted;
    DropHelper dropHelper;
};

// a temporary set of overrides to make XR's life easier
// TODO - further cleanup
struct ViewportWindowXROverrideDesc
{
    bool disableGizmo;
    const char* resolutionString;
    const char** additionalMessages;
    size_t additionalMessagesCount;
    bool disableViewportResolutionOverride;
};

class IViewportWindow
{
public:
    /**
     * Setting path to retrieve viewport display options
     */
    static const char* const kViewportDisplayOptionsPath;

    /**
     * Defines viewport element visibility flags
     */
    using ShowFlags = uint32_t;
    static const ShowFlags kShowFlagNone = 0;
    static const ShowFlags kShowFlagFps = 1 << 0;
    static const ShowFlags kShowFlagAxis = 1 << 1;
    static const ShowFlags kShowFlagLayer = 1 << 2;
    static const ShowFlags kShowFlagResolution = 1 << 3;
    static const ShowFlags kShowFlagTimeline = 1 << 4;
    static const ShowFlags kShowFlagCamera = 1 << 5;
    static const ShowFlags kShowFlagGrid = 1 << 6;
    static const ShowFlags kShowFlagSelectionOutline = 1 << 7;
    static const ShowFlags kShowFlagLight = 1 << 8;
    static const ShowFlags kShowFlagSkeleton = 1 << 9;
    static const ShowFlags kShowFlagMesh = 1 << 10;
    static const ShowFlags kShowFlagPathTracingResults = 1 << 11;
    static const ShowFlags kShowFlagAudio = 1 << 12;
    static const ShowFlags kShowFlagDeviceMemory = 1 << 13;
    static const ShowFlags kShowFlagHostMemory = 1 << 14;

    static const ShowFlags kShowFlagAll = kShowFlagFps | kShowFlagAxis | kShowFlagLayer | kShowFlagResolution |
                                          kShowFlagPathTracingResults | kShowFlagTimeline | kShowFlagCamera |
                                          kShowFlagGrid | kShowFlagSelectionOutline | kShowFlagLight |
                                          kShowFlagSkeleton | kShowFlagMesh | kShowFlagAudio |
                                          kShowFlagDeviceMemory | kShowFlagHostMemory;

    /**
     * Setting path to retrieve gizmo options
     */
    static const char* const kViewportGizmoScalePath;
    static const char* const kViewportGizmoConstantScaleEnabledPath;
    static const char* const kViewportGizmoConstantScalePath;
    static const char* const kViewportGizmoBillboardStyleEnabledPath;

    typedef bool (*OnMenuDrawSubmenuFn)();


    /**
     * Destructor.
     */
    virtual ~IViewportWindow() = default;

    /**
     * Adds a menu item to the viewport, those are currently only Top Left aligned or Top Right aligned.
     * We currently only support Button type from the UI Toolkit
     * Because the caller of this function might not have access to the UI Class directly a void * is used
     * The function call does sanity check on the * and will handle wrong * properly.
     *
     * @param name is the name of the button.
     * @param button is a pointer to a Button class.
     * @param alignment is the alignment of the button either Left or Right.
     */
    virtual void addMenuButtonItem(const char* name, void* button, ViewportMenuAlignment alignment) = 0;

    /**
     * Removes the bottom from the menu, the name is the Key in the named array.
     *
     * @param name the name of the button to remove
     * @param alignment the alignment of the button, name are unique only per Menu
     */
    virtual void removeMenuButtonItem(const char* name, ViewportMenuAlignment alignment) = 0;

    /**
     * Adds a menu to the show/hide type submenu
     * @param name the name of the submenu
     * @param drawMenuCallback draw menu function pointer

     */
    virtual void addShowByTypeSubmenu(const char* name,
                                      OnMenuDrawSubmenuFn drawMenuCallback,
                                      OnMenuDrawSubmenuFn resetMenuCallback,
                                      OnMenuDrawSubmenuFn isResetMenuCallback) = 0;

    /**
     * Removes a menu to the show/hide type submenu
     * @param name the name of the submenu
     */
    virtual void removeShowByTypeSubmenu(const char* name) = 0;

    /**
     * Posts a toast message to viewport.
     *
     * @param message The message to be posted.
     */
    virtual void postToast(const char* message) = 0;

    /**
     * Request a picking query for the next frame.
     */
    virtual void requestPicking() = 0;

    /**
     * Enable picking.
     *
     * @param enable Enable/disable picking.
     */
    virtual void setEnabledPicking(bool enable) = 0;

    /**
     * Is picking enabled.
     *
     * @return True if picking is enabled.
     */
    virtual bool isEnabledPicking() const = 0;

    /**
     * Gets the EventStream for in-viewport draw event.
     *
     * @return EventStream for in-viewport draw event.
     */
    virtual carb::events::IEventStreamPtr getUiDrawEventStream() = 0;

    /**
     * Query the visibility of the window.
     *
     * @return visibility of the window.
     */
    virtual bool isVisible() const = 0;

    /**
     * Sets the visibility of the window.
     *
     * @param visible true to show the window, false to hide the window.
     */
    virtual void setVisible(bool visible) = 0;

    /**
     * Query the window name.
     *
     * @return the window name
     */
    virtual const char* getWindowName() = 0;

    /**
     * Sets the active camera in the viewport to a USD camera.
     *
     * @param path Path of the camera prim on the stage.
     */
    virtual void setActiveCamera(const char* path) = 0;

    /**
     * Gets the active camera in the viewport.
     *
     * @return Path of the camera prim on the stage.
     */
    virtual const char* getActiveCamera() const = 0;

    /**
     * Sends signal to the currently activecamera controller to focus on target (either selected scene primitive,
     * or the whole scene).
     */
    virtual void focusOnSelected() = 0;

    /**
     * Gets camera's target.
     *
     * @param path The path of the Camera prim.
     * @param target The target of the camera to be written to.
     * @return true on success, false if camera doesn't exist at path.
     */
    virtual bool getCameraTarget(const char* path, carb::Double3& target) const = 0;

    /**
     * Gets prim's clipping pos in current active camera.
     * It's calculated with prim_pos * view_matrix_of_camera * projection_matrix_of_camera.
     * The x or y pos of returned value is [-1, 1]. In xy plane, y is facing up and x is facing right,
     * which is unliking window coordinates that y is facing down and the range of xy is [0, 1]x[0, 1].
     * and the z pos is [0, 1], where z is in reverse form that 0 is the far plane, and 1 is the near plane.
     *
     * @param path The path of the prim.
     * @param pos The offset pos of the prim to be written to.
     * @param referencePoint The reference point of prim to be calculated for clipping pos.
     * By default, it's the center of the prim bound box.
     * @return true on success, false if prim doesn't exist at path. Or
     * prim's position is out of the active camera's view frustum.
     */
    virtual bool getPrimClippingPos(
        const char* path,
        carb::Double3& pos,
        ViewportPrimReferencePoint referencePoint = ViewportPrimReferencePoint::eBoundBoxCenter) const = 0;

    /**
     * Sets camera's target.
     *
     * @param path The path of the Camera prim.
     * @param target The target of the camera to be set to.
     * @param rotate true to keep position but change orientation and radius (camera rotates to look at new target).
     *               false to keep orientation and radius but change position (camera moves to look at new target).
     * @return true on success, false if camera doesn't exist at path.
     */
    virtual bool setCameraTarget(const char* path, const carb::Double3& target, bool rotate) = 0;

    /**
     * Gets camera's position.
     *
     * @param path The path of the Camera prim.
     * @param position The position of the camera to be written to.
     * @return true on success, false if camera doesn't exist at path.
     */
    virtual bool getCameraPosition(const char* path, carb::Double3& position) const = 0;

    /**
     * Sets camera's position.
     *
     * @param path The path of the Camera prim.
     * @param position The position of the camera to be set to.
     * @param rotate true to keep position but change orientation and radius (camera moves to new position while still
     *                 looking at the same target).
     *               false to keep orientation and radius but change target (camera moves to new position while keeping
                       the relative position of target unchanged).
     * @return true on success, false if camera doesn't exist at path.
     */
    virtual bool setCameraPosition(const char* path, const carb::Double3& position, bool rotate) = 0;

    /**
     * Gets camera's forward vector.
     *
     * @param path The path of the Camera prim.
     * @param vector The forward vector of the camera to be written to.
     * @return true on success, false if camera doesn't exist at path.
     */
    virtual bool getCameraForward(const char* path, carb::Double3& vector) const = 0;

    /**
     * Gets camera's right vector.
     *
     * @param path The path of the Camera prim.
     * @param vector The right vector of the camera to be written to.
     * @return true on success, false if camera doesn't exist at path.
     */
    virtual bool getCameraRight(const char* path, carb::Double3& vector) const = 0;

    /**
     * Gets camera's up vector.
     *
     * @param path The path of the Camera prim.
     * @param vector The up vector of the camera to be written to.
     * @return true on success, false if camera doesn't exist at path.
     */
    virtual bool getCameraUp(const char* path, carb::Double3& vector) const = 0;

    /**
     * Gets camera move speed when pilot in viewport with camera control.
     *
     * @return camera move speed.
     */
    virtual double getCameraMoveVelocity() const = 0;

    /**
     * Sets camera move speed when pilot in viewport with camera control.
     *
     * @param velocity camera move speed.
     */
    virtual void setCameraMoveVelocity(double velocity) = 0;

    /**
     * Enables or disables gamepad for camera controller.
     *
     * @param enabled true to enable gamepad, false to disable.
     */
    virtual void setGamepadCameraControl(bool enabled) = 0;

    /**
     * Temporary workaround for fullscreen mode. DO NOT USE directly.
     */
    virtual void draw(const char* windowName, float elapsedTime) = 0;

    /**
     * Toggles Visibility settings. Lights/Camera/Skeleton/Grid/HUD etc.
     */
    virtual void toggleGlobalVisibilitySettings() = 0;

    /**
     * Gets the mouse event stream
     *
     * @returns The mouse event stream
     */
    virtual carb::events::IEventStream* getMouseEventStream() = 0;

    /**
     * Gets the viewport window rect
     *
     * @returns The viewport window rect
     */
    virtual carb::Float4 getViewportRect() const = 0;

    virtual carb::Int2 getViewportRenderResolution() const = 0;

    /**
     * Gets if camera is being manipulated.
     *
     * @returns true if camera is being manipulated.
     */
    virtual bool isManipulatingCamera() const = 0;

    /**
     * Gets if viewport is being focused.
     *
     * @returns true if viewport is being focused.
     */
    virtual bool isFocused() const = 0;

    /**
     * Allow camera motion to be overriden
     *
     * @returns a subscriptionId to remove override with
     */
    virtual SubscriptionId addCameraOverride(const CameraOverrideDesc& cameraOverride) = 0;

    /**
     * Remove override
     */
    virtual void removeCameraOverride(SubscriptionId subscription) = 0;

    /**
     * Sets the hydra engine to use for rendering
     *
     */
    virtual void setActiveHydraEngine(const char* hydraEngine) = 0;

    /**
     * Sets the tick rate for hydra engine used during rendering
     * -1 means unlimited
     */
    virtual void setHydraEngineTickRate(uint32_t tickRate) = 0;

    /**
     * Gets the render product prim path
     *
     */
    virtual const char* getRenderProductPrimPath() = 0;

    /**
     * Sets the render product prim path
     *
     */
    virtual void setRenderProductPrimPath(const char* path) = 0;

    /**
     * Enables an AOV on the viewport
     *
     * @param aov name of the AOV to add.
     * @param verifyAvailableBeforeAdd if true add the AOV only if it belong to the list of available AOVs.
     * @returns true if the AOV is added or already exists.
     */
    virtual bool addAOV(omni::usd::TokenH aov, bool verifyAvailableBeforeAdd) = 0;

    /**
     * Disables an AOV on the viewport
     *
     * @returns true if the AOV is removed.
     */
    virtual bool removeAOV(omni::usd::TokenH aov) = 0;

    /**
     * Returns all the AOVs output by the viewport
     *
     * @returns true if the AOV is removed.
     */
    virtual const omni::usd::TokenH* getAOVs(uint32_t& outNumAovs) = 0;

    /**
     * Sets the window size
     */
    virtual void setWindowSize(uint32_t w, uint32_t h) = 0;

    /**
     * Sets the window position
     */
    virtual void setWindowPosition(uint32_t x, uint32_t y) = 0;

    /**
     * Sets the texture resolution. This overrides window size when viewport resolution is selected
     * Pass -1,-1 to undo override
     */
    virtual void setTextureResolution(int32_t x, int32_t y) = 0;

    /**
     * @returns current viewport's resource specified by the AOV (null if non-existent)
     */
    virtual rtx::resourcemanager::RpResource* getDrawableResource(omni::usd::TokenH aov) = 0;

    /**
     * @returns whether the AOV is available on the current viewport
     */
    virtual bool isDrawableAvailable(omni::usd::TokenH aov) = 0;

    /**
     * @returns fps of  viewport's drawable
     */
    virtual float getFps() = 0;

    /**
     * @ Calls the callback on next mouse click and passes the world position under mouse.
     *
     * @param fn callback function when world position is fetched after mouse click. The position can be nullptr if
     * clicked on black background.
     * @param userData user data to be passed back to fn when callback is triggered.
     */
    virtual void queryNextPickedWorldPosition(OnQueriedNextPickedWorldPositionFn fn, void* userData) = 0;

    /**
     * Returns the current frame data based on the requested feature, such as profiler data.
     * If frame is not finished processing the data, the result of the previous frame is returned.
     * For multi-GPU, query the device count and then set deviceIndex to the desired device index.
     *
     * @param dataType    Specified the requested data type to return.
     * @param deviceIndex The index of GPU device to get the frame data from. Set to zero in Single-GPU mode.
     *                    You may query the number of devices with FrameDataType::eGpuProfilerDeviceCount.
     *                    deviceIndex is ignored when the type is set to eGpuProfilerDeviceCount.
     * @param data        A pointer to the returned data. Returns nullptr for failures or eGpuProfilerDeviceCount.
     *                    You may pass nullptr if you only need dataSize.
     * @param dataSize    The size of the returned data in bytes, the number of structures, or device count based on
     *                    the dataType. For strings, it includes the null-termination.
     */
    virtual void getFrameData(carb::renderer::FrameDataType dataType,
                              uint32_t deviceIndex,
                              void** data,
                              size_t* dataSize) = 0;

    /**
     * Checks if mouse is hovering over the viewport's content region, without being occluded by other UI elements.
     */
    virtual bool isContentRegionHovered() const = 0;

    /**
     * Gets the hydra engine that is used for rendering.
     */
    virtual const char* getActiveHydraEngine() = 0;

    /* menu UI */
    virtual void showHideWindow(bool visible) = 0;

    virtual omni::usd::ViewportHandle getId() const = 0;

    /**
     * Get the picked world pos since last requested picking.
     *
     * @param outWorldPos picked world pos to be filled.
     *
     * @returns false if no picked pos is available.
     */
    virtual bool getPickedWorldPos(carb::Double3& outWorldPos) = 0;

    virtual bool getPickedGeometryHit(carb::Double3& outWorldPos, carb::Float3& outNormal) = 0;


    virtual uint32_t getAvailableAovCount() const = 0;

    virtual void getAvailableAovs(const char* outAovs[]) const = 0;

    virtual const char* getUsdContextName() const = 0;
    virtual void disableSelectionRect(bool enablePicking) = 0;

    // A shim for XR until better paths for messages is ready
    virtual void setXROverrideDesc(ViewportWindowXROverrideDesc xrOverrideDesc) = 0;

    /**
     * @returns scene renderer.
     */
    virtual carb::scenerenderer::SceneRenderer* getSceneRenderer() = 0;

    /**
     * @ returns scene renderer context.
     */
    virtual carb::scenerenderer::Context* getSceneRendererContext() = 0;

    /**
     * Sets the hydra engine flags for the hydra engine used to render this viewport
     */
    virtual void setHydraEngineFlags(omni::usd::hydra::EngineCreationFlags flags) = 0;

    /**
     * Sets the deviceMask for hydra engine used during rendering.
     */
    virtual void setHydraEngineDeviceMask(uint32_t deviceMask) = 0;
};
}
}
