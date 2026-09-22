// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IGpuFoundation.h"

#include <carb/IObject.h>
#include <carb/Interface.h>
#include <carb/InterfaceUtils.h>
#include <carb/cpp/ZStringView.h>
#include <carb/extras/StringSafe.h>
#include <carb/tasking/TaskingTypes.h>

#include <omni/kit/IAppWindow.h>

namespace carb::events
{
class IEventStream;
}

namespace carb::graphics
{
enum class DescriptorType : int32_t;
struct Device;
class DeviceGroup;
struct CommandList;
struct CommandQueue;
struct DescriptorPool;
struct ResourceBindingSignature;
struct TextureDesc;
// TextureGpuData
struct Texture;
struct Descriptor;
struct DescriptorSet;
}

namespace carb::graphicsmux
{
class CommandList;
}

namespace carb::renderer
{
struct TextureHandle;
}


namespace gpu
{
enum class GfResult : int32_t;
}

namespace rtx::resourcemanager
{
class RpResource;
typedef uint32_t SyncScopeId;
}

namespace omni::kit::renderer
{

//! Renderer events. See Events.md for more info.
enum class RendererEventType
{
    ePreBeginFrame, //!< Pre Begin Frame event
    ePreBeginRenderPass, //!< Pre Begin Render Pass event
    eRenderFrame, //!< Render Frame event
    ePostEndRenderPass, //!< Post End Render Pass event
    ePostEndRenderFrame, //!< End Render Frame event
    ePostPresentFrameBuffer, //!< Post Present Frame Buffer event
    ePresentRenderFrame, //!< Present Render Frame event

    /// Count only
    eCount // MUST BE LAST
};

typedef int64_t CommandListHandle;

/**
 * Defines a simple interface for texture GPU resources
 */
class TextureGpuData : public carb::IObject
{
public:
    virtual carb::graphics::Texture* getGraphicsTexture() const = 0;
    virtual carb::graphics::Descriptor* getGraphicsDescriptor() const = 0;

    virtual carb::graphics::DescriptorSet* getGraphicsDescriptorSet() const = 0;

    virtual rtx::resourcemanager::RpResource* getManagedResource() const = 0;
    virtual uint32_t getBindlessDescriptorIndex() const = 0;
};

struct TextureGpuReference
{
    union {
        uint32_t gpuIndex;
        void* ptr;
    };
};

/**
 * @brief The data for all the viewports in GUI. We use it when present thread
 * is enabled to render viewport with more FPS that GUI.
 */
struct IRendererHydraViewportData
{
    using Clock = ::std::chrono::high_resolution_clock;
    using Duration = Clock::duration;
    using TimePoint = Clock::time_point;

    uint32_t viewportId;
    size_t subFrameCount;
    uint32_t subFrames[4];
    size_t currentSubFrame;
    TimePoint publishTime;
    Duration frameAverageTime;
};

/**
 * @brief Options for texture creation.
 */
struct IRendererTextureOptions
{
    uint32_t gpuDeviceMask = 0;        ///< Device mask to create texture on (0 for UI device only)
    uint32_t textureUsageFlags = 0;    ///< carb::graphics::TextureUsageFlags
    uint32_t resourceUsageFlags = 0;   ///< rtx::ResourceUsageFlags
    union
    {
        bool pooled;                   ///< Whether to create the RpResource as a pooled one
        uint32_t unusedExtPadding = 0; ///< Unused padding and expansion
    };
};

/**
 * Defines an interface for the small version of editor that provides simple GUI.
 */
class IRenderer
{
public:
    CARB_PLUGIN_INTERFACE("omni::kit::renderer::IRenderer", 1, 9);

    virtual void startup() = 0;
    virtual void shutdown() = 0;

    /**
     * Render events stream. Render events and pushed and popped every frame.
     */
    CARB_DEPRECATED("Use Events 2.0") virtual carb::events::IEventStream* getPreBeginFrameEventStream(IAppWindow* appWindow) = 0;
    CARB_DEPRECATED("Use Events 2.0") virtual carb::events::IEventStream* getPreBeginRenderPassEventStream(IAppWindow* appWindow) = 0;
    CARB_DEPRECATED("Use Events 2.0") virtual carb::events::IEventStream* getRenderFrameEventStream(IAppWindow* appWindow) = 0;
    CARB_DEPRECATED("Use Events 2.0") virtual carb::events::IEventStream* getPostEndRenderPassEventStream(IAppWindow* appWindow) = 0;
    CARB_DEPRECATED("Use Events 2.0") virtual carb::events::IEventStream* getPostEndRenderFrameEventStream(IAppWindow* appWindow) = 0;

    virtual carb::graphics::Device* getGraphicsDevice(IAppWindow* appWindow) = 0;
    virtual carb::graphics::DeviceGroup* getGraphicsDeviceGroup(IAppWindow* appWindow) = 0;
    virtual uint32_t getGraphicsDeviceIndex(IAppWindow* appWindow) = 0;
    virtual carb::Format getGraphicsSwapchainFormat(IAppWindow* appWindow) = 0;
    virtual carb::graphics::CommandQueue* getGraphicsCommandQueue(IAppWindow* appWindow) = 0;

    typedef void (*UploadCompleteCbDeprecated)(void* arg,
                                               void* textureHandle,
                                               carb::graphics::Descriptor* textureDescriptor,
                                               size_t width,
                                               size_t height,
                                               void* userData);
    struct UploadTextureDescDeprecated
    {
        const char* assetUri;
        UploadCompleteCbDeprecated callback;
        void* arg;
    };

    // TODO: remove these functions as they are merely wrappers around GPU data creation with integrated assets
    // management
    virtual void uploadTextureDeprecated(const UploadTextureDescDeprecated& desc, void* userData = nullptr) = 0;
    virtual void destroyTextureDeprecated(void* texture) = 0;
    virtual TextureGpuData* getTextureDataFromHandle(void* textureHandle) = 0;

    static constexpr uint32_t kMaxDescriptorSetCount = 8192;
    virtual carb::graphics::DescriptorPool* getDescriptorPool() = 0;

    /**
     * These functions are needed because carb::graphics doesn't have descriptor set deallocations, we have very
     * finite set of allocations - we have to track them to make sure we can emit a warning if we're reaching the limit.
     */
    virtual void notifyDescriptorPoolAllocation(carb::graphics::DescriptorType descriptorType) = 0;
    virtual int getFreeDescriptorPoolSlotCount(carb::graphics::DescriptorType descriptorType) = 0;

    /**
     * Functions that allocate id to use in shaders, given the created/imported GPU data.
     */
    virtual TextureGpuReference allocateReferenceForTexture(
        carb::graphics::ResourceBindingSignature* resourceBindingSignature) = 0;
    virtual TextureGpuReference allocateReferenceForDrawable(
        carb::graphics::ResourceBindingSignature* resourceBindingSignature) = 0;

    virtual TextureGpuReference updateReferenceFromTextureData(TextureGpuReference textureGpuReference,
                                                               TextureGpuData* textureGpuData) = 0;
    virtual TextureGpuReference updateReferenceFromDrawableData(TextureGpuReference* textureGpuReference,
                                                                TextureGpuData* drawableGpuData) = 0;

    /**
     * Functions to manipulate GPU data that was created outside of the renderer.
     */
    virtual TextureGpuData* createExternalTextureGpuData() = 0;
    virtual void updateExternalTextureGpuData(
        TextureGpuData* externalTextureGpuData,
        carb::graphics::Descriptor* externalDescriptor,
        uint32_t bindlessDescriptorIndex = CARB_UINT32_MAX) = 0;

    /**
     * Functions to create managed GPU data.
     */
    virtual TextureGpuData* createGpuResourcesForTexture(carb::Format format,
                                                         size_t mipMapCount,
                                                         size_t* mipWidths,
                                                         size_t* mipHeights,
                                                         const uint8_t** mipDatas,
                                                         size_t* mipStrides) = 0;
    virtual void updateGpuResourcesForTexture(TextureGpuData* textureGpuData,
                                              carb::Format format,
                                              size_t mipMapCount,
                                              size_t* mipWidths,
                                              size_t* mipHeights,
                                              const uint8_t** mipDatas,
                                              size_t* mipStrides) = 0;

    virtual void resetGpuResourcesForTexture(TextureGpuData* textureGpuData) = 0;
    virtual void destroyGpuResourcesForTexture(TextureGpuData* textureGpuData) = 0;

    /**
     * Functions to extract command lists from handles.
     */
    virtual carb::graphics::CommandList* getGraphicsCommandList(CommandListHandle commandListHandle) = 0;
    virtual carb::graphicsmux::CommandList* getGraphicsMuxCommandList(CommandListHandle commandListHandle) = 0;

    virtual uint32_t getCurrentBackBufferIndex(IAppWindow* appWindow) = 0;
    virtual uint32_t getBackBufferCount(IAppWindow* appWindow) = 0;
    virtual size_t getFrameCount(IAppWindow* appWindow) = 0;

    /**
     * Framebuffer information.
     */
    virtual carb::graphics::Texture* getFramebufferTexture(IAppWindow* appWindow) = 0;
    virtual uint32_t getFramebufferWidth(IAppWindow* appWindow) = 0;
    virtual uint32_t getFramebufferHeight(IAppWindow* appWindow) = 0;
    virtual carb::Format getFramebufferFormat(IAppWindow* appWindow) = 0;
    virtual CommandListHandle getFrameCommandList(IAppWindow* appWindow) = 0;

    virtual TextureGpuReference getInvalidTextureReference() = 0;

    static inline IGpuFoundation* getGpuFoundation();

    virtual bool attachAppWindow(IAppWindow* appWindow) = 0;
    virtual void detachAppWindow(IAppWindow* appWindow) = 0;
    virtual bool isAppWindowAttached(IAppWindow* appWindow) = 0;

    virtual void waitIdle(IAppWindow* appWindow) = 0;
    virtual void forceRenderFrame(float dt) = 0;

    virtual rtx::resourcemanager::SyncScopeId getSyncScopeId() = 0;

    /**
     * Get a reference to the current ResourceManager and it's Context.
     * IAppWindow* can currently be null.
     */
    struct ResourceManagerState
    {
        rtx::resourcemanager::ResourceManager* manager;
        rtx::resourcemanager::Context* context;
    };
    virtual ResourceManagerState getResourceManagerState(IAppWindow* appWindow) = 0;

    virtual void setClearColor(IAppWindow* appWindow, const carb::Float4& clearColor) = 0;
    virtual carb::Float4 getClearColor(IAppWindow* appWindow) = 0;


    virtual bool setRenderQueue(IAppWindow* appWindow, size_t renderQueueIdx) = 0;
    virtual size_t getRenderQueue(IAppWindow* appWindow) = 0;

    /**
     * Functions that deallocate id to use in shaders, given the created/imported GPU data.
     */
    virtual void deallocateReferenceForTexture(
        carb::graphics::ResourceBindingSignature* resourceBindingSignature, const TextureGpuReference& textureGpuReference) = 0;
    virtual void deallocateReferenceForDrawable(
        carb::graphics::ResourceBindingSignature* resourceBindingSignature, const TextureGpuReference& textureGpuReference) = 0;

    /**
     * Present thread streams.
     *
     * Called from the separate thread (present thread) to render the saved UI
     * with bigger framerate than it's generated.
     */
    CARB_DEPRECATED("Use Events 2.0") virtual carb::events::IEventStream* getPresentRenderFrameEventStream(IAppWindow* appWindow) = 0;

    /**
     * @brief Should be called when the new viewport frame is ready
     *
     * @param dt time to render this frame in ns
     * @param viewportId the id of the viewport that should be replaced to the
     *                   given textureId
     * @param subFrameCount the number of subframes
     * @param subFrames the viewport subframes
     */
    virtual void notifyRenderingIsReady(float dtNs,
                                        uint32_t viewportId,
                                        size_t subFrameCount,
                                        const uint32_t* subFrames) = 0;

    /**
     * Functions to create managed GPU data with optional multiGpu and GPU source support.
     *
     * @param multiGpu data will be uploaded or copied to all GPUs in device group
     * @param fromGpu data is a gpu memory address, not host memory
     */
    virtual TextureGpuData* createGpuResourcesForTexture(carb::Format format,
                                                         size_t mipMapCount,
                                                         size_t* mipWidths,
                                                         size_t* mipHeights,
                                                         const uint8_t** mipDatas,
                                                         size_t* mipStrides,
                                                         bool multiGpu,
                                                         bool cudaBytes) = 0;
    virtual void updateGpuResourcesForTexture(TextureGpuData* textureGpuData,
                                              carb::Format format,
                                              size_t mipMapCount,
                                              size_t* mipWidths,
                                              size_t* mipHeights,
                                              const uint8_t** mipDatas,
                                              size_t* mipStrides,
                                              bool cudaBytes) = 0;

    /**
     * Add a callback to be run in the IRenderer / Graphics initialization
     *
     * @param eventHandler An IEventListener to be called during IRenderer/Graphics setup.
     * This handler is currently invoked with a null carb::event::IEvent pointer.
     *
     */
    virtual void addToInitPipeline(carb::events::IEventListenerPtr eventHandler) = 0;

    /**
     * Block current thread until renderer (& GPU Foundation) is fully setup
     *
     */
    virtual void waitForInit() = 0;

    /**
     * @brief Called immediately after the renderer presents the current frame
     * to the frame buffer. This function allows the developer to perform any
     * additional operations or processing on the frame after it has been
     * presented, such as sending the frame data to a CUDA memory frame for
     * further processing. Additionally, the callback can be used to trigger any
     * additional actions that need to be taken after the frame has been
     * presented, such as updating a status or sending a notification.
     */
    CARB_DEPRECATED("Use Events 2.0") virtual carb::events::IEventStream* getPostPresentFrameBufferEventStream(IAppWindow* appWindow) = 0;

    /**
     * @brief Frozen window is skipped from the run loop and it's not updated.
     */
    virtual void freezeAppWindow(IAppWindow* appWindow, bool freeze) = 0;

    /*
     * @brief State of the present thread
     *
     * @return true The present thread is enabled
     * @return false The present thread is disabled
     */
    virtual bool isPresentThreadEnabled() const = 0;

    /**
     * @brief Create or update a GPU resource.
     *
     * @param format The format of the texture being created
     * @param mipMapResolutions An array of resolutions to use for mip-mapped data
     * @param mipMapDatas An array of bytes to upload, for each mip-level
     * @param mipMapStrides An array of strides on the bytes to upload, for each mip-level
     * @param mipMapCount The number of elements in the mipResolutions, mipDatas, and mipStrides arguments
     * @param multiGpu Data will be uploaded or copied to all GPUs in device group
     * @param createShared Whether to create the texture as shareable for later use in CUDA or OpenGL
     * @param cudaBytes Whether the pointers in mipDatas refer to CPU memory or CUDA memory
     * @param deviceMask The devices to create the texture for
     */
    virtual TextureGpuData* createGpuResourcesForTexture(carb::Format format,
                                                         const carb::Uint2* mipMapResolutions,
                                                         const uint8_t* const* mipMapDatas,
                                                         const size_t* mipMapStrides,
                                                         size_t mipMapCount,
                                                         const IRendererTextureOptions& options = {}) = 0;


    virtual void updateGpuResourcesForTexture(TextureGpuData* textureGpuData,
                                              carb::Format format,
                                              const carb::Uint2* mipMapResolutions,
                                              const uint8_t* const* mipMapDatas,
                                              const size_t* mipMapStrides,
                                              size_t mipMapCount,
                                              const IRendererTextureOptions& options = {}) = 0;

    /**
     * Ensures that the resource exists on the target display device, potentially performing an asynchronous GPU copy.
     * @return The pointer to the resource on the target display device. If the resource is already on the target
     * device, then this pointer will be the same as the input. This function will return nullptr on failure.
     * @param resource The resource to potentially copy to the target display device
     * @param timeout The timeout (in milliseconds) for the copy operation. The future will return eTimeout if the
     * timeout is exceeded.
     * @param dstRsrc Optional: If not nullptr, the resource on the target device.
     * @param outTextureHandle Optional: If not nullptr, the GPU handle for the resource on the target device.
     * @param outTextureDesc Optional: If not nullptr, the TextureDesc of the returned RpResource will be returned in
     * @param resourceId A unique id that allows reusing internal memory for the MGPU transfer.
     * outTextureDesc.
     * @param outFuture Optional: If not nullptr, the receiver for a future that can be waited on for the completion of
     * the potential GPU copy.
     */
    virtual rtx::resourcemanager::RpResource* ensureRpResourceOnTargetDevice(
        rtx::resourcemanager::RpResource* resource,
        uint32_t timeout,
        rtx::resourcemanager::RpResource* dstRsrc,
        carb::renderer::TextureHandle* outTextureHandle,
        const carb::graphics::TextureDesc** outTextureDesc,
        carb::tasking::SharedFuture<gpu::GfResult>* outFuture,
        uint32_t resourceId) = 0;

    /**
     * @brief Draw-frozen window is not skipped from the run loop and but the
     * draw list of this window is not updated.
     */
    virtual void drawFreezeAppWindow(IAppWindow* appWindow, bool freeze) = 0;

    /**
     * @brief Ensures that the resource exists on the target display device, potentially performing an asynchronous GPU copy.
     * @return The pointer to the resource on the target display device. If the resource is already on the target
     * device, then this pointer will be the same as the input. This function will return nullptr on failure.
     * @param resource The resource to potentially copy to the target display device
     * @param timeout The timeout (in milliseconds) for the copy operation. The future will return eTimeout if the
     * timeout is exceeded.
     * @param textureOptions: IRendererTextureOptions to ensure in resource conforms to.
     * @param dstRsrc Optional: If not nullptr, the resource on the target device.
     * @param outTextureHandle Optional: If not nullptr, the GPU handle for the resource on the target device.
     * @param outTextureDesc Optional: If not nullptr, the TextureDesc of the returned RpResource will be returned in
     * outTextureDesc.
     * @param outFuture Optional: If not nullptr, the receiver for a future that can be waited on for the completion of
     * the potential GPU copy.
     */
    virtual rtx::resourcemanager::RpResource* ensureRpResourceTextureOptions(
        rtx::resourcemanager::RpResource* resource,
        uint32_t timeout,
        const IRendererTextureOptions& textureOptions,
        rtx::resourcemanager::RpResource* dstRsrc,
        carb::renderer::TextureHandle* outTextureHandle,
        const carb::graphics::TextureDesc** outTextureDesc,
        carb::tasking::SharedFuture<gpu::GfResult>* outFuture,
        uint32_t resourceId) = 0;
};

/**
 * Retrieves the name for a given RendererEventType.
 * @param event The RendererEventType
 * @param window The IAppWindow instance for the event name. May be `nullptr` to use the default window.
 * @returns a `carb::RString` event name for the given event and the window in the format
 *   `omni.kit.renderer:renderer:<window pointer>:<event name>` where the `<window pointer>` may be empty if @p window
 *   is `nullptr` or as formatted by printf's `%p` format specifier.
 */
inline carb::RString getRendererEventName(RendererEventType event, IAppWindow* window) noexcept
{
    // clang-format off
    static carb::RString mapping[] = {
        carb::RString("omni.kit.renderer:renderer::pre_begin_frame"),
        carb::RString("omni.kit.renderer:renderer::pre_begin_render_pass"),
        carb::RString("omni.kit.renderer:renderer::render_frame"),
        carb::RString("omni.kit.renderer:renderer::post_end_render_pass"),
        carb::RString("omni.kit.renderer:renderer::post_end_render_frame"),
        carb::RString("omni.kit.renderer:renderer::post_present_frame_buffer"),
        carb::RString("omni.kit.renderer:renderer::present_render_frame"),
    };
    // clang-format on
    static_assert(CARB_COUNTOF(mapping) == size_t(RendererEventType::eCount), "Add missing entry");
    CARB_ASSERT(size_t(event) < CARB_COUNTOF(mapping));
    
    auto name = mapping[size_t(event)];

    // Default/empty window: just return the base event
    if (!window)
        return name;
    
    constexpr static carb::cpp::zstring_view kPrefix("omni.kit.renderer:renderer:");
    // we reserve 16 characters for the hex value of the pointer, which is only correct for 64-bit values
    static_assert((8 * sizeof(window)) == 64);
    auto const kBufSize = name.length() + 16 + 1;

    // Allocate a stack buffer and format the string into it
    auto buf = CARB_STACK_ALLOC(char, kBufSize);
    memcpy(buf, kPrefix.c_str(), kPrefix.length());
    auto const len = carb::extras::formatString(buf + kPrefix.length(), kBufSize - kPrefix.length(), "%p", window);
    CARB_ASSERT(len > 0 && len <= 16);
    memcpy(buf + kPrefix.length() + len, name.c_str() + kPrefix.length(), name.length() - kPrefix.length());
    buf[len + name.length()] = '\0';

    return carb::RString(buf, len + name.length());
}

/**
 * Parses the RendererEventType from a renderer event RString.
 * @param event The event name, typically generated from \ref getRendererEventName().
 * @param ppOut Optional, may be `nullptr`. If non-`nullptr` and `nullopt` is not returned, will be set to the
 *   IAppWindow instance that sent the given message. NOTE: It may not be safe to access this pointer without verifying
 *   validity through other means. If non-`nullptr` and `nullopt` is returned, it will be set to `nullptr`.
 * @returns A valid `optional` containing the determined `RendererEventType` if parsing is successful. Otherwise,
 *   `carb::cpp::nullopt` is returned to indicate that the given event name is not a valid renderer event name.
 */
inline carb::cpp::optional<RendererEventType> getRendererEventType(carb::RString event, IAppWindow** ppOut = nullptr) noexcept
{
    if (ppOut)
        *ppOut = nullptr;

    constexpr static carb::cpp::string_view kPrefix("omni.kit.renderer:renderer:");
    auto sv = carb::cpp::zstring_view(event);
    if (!sv.starts_with(kPrefix))
        return carb::cpp::nullopt;
    
    auto colon = sv.find(':', kPrefix.length());
    if (colon == sv.npos)
        return carb::cpp::nullopt;
    
    if (ppOut)
    {
        CARB_IGNOREWARNING_MSC_WITH_PUSH(4996) // deprecation warning
        sscanf(sv.c_str() + kPrefix.length(), "%p", ppOut);
        CARB_IGNOREWARNING_MSC_POP
    }

    auto name = sv.substr(colon + 1);
    switch (carb::hashBuffer(name.data(), name.length()))
    {
    case CARB_HASH_STRING("pre_begin_frame"): return RendererEventType::ePreBeginFrame;
    case CARB_HASH_STRING("pre_begin_render_pass"): return RendererEventType::ePreBeginRenderPass;
    case CARB_HASH_STRING("render_frame"): return RendererEventType::eRenderFrame;        
    case CARB_HASH_STRING("post_end_render_pass"): return RendererEventType::ePostEndRenderPass;        
    case CARB_HASH_STRING("post_end_render_frame"): return RendererEventType::ePostEndRenderFrame;        
    case CARB_HASH_STRING("post_present_frame_buffer"): return RendererEventType::ePostPresentFrameBuffer;        
    case CARB_HASH_STRING("present_render_frame"): return RendererEventType::ePresentRenderFrame;
    default: break;
    }
    static_assert(size_t(RendererEventType::eCount) == 7, "add missing entry");
    return carb::cpp::nullopt;
}

inline IGpuFoundation* IRenderer::getGpuFoundation()
{
    return carb::getCachedInterface<IGpuFoundation>();
}

}
