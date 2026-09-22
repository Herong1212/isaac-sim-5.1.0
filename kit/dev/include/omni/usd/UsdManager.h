// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "HydraEngineTypes.h"

#include <carb/IObject.h>
#include <omni/usd/Api.h>

#include <memory.h>

namespace carb
{
namespace settings
{
struct ISettings;
}
}

namespace gpu
{
namespace foundation
{
struct GpuFoundation;
}
}

namespace carb
{
namespace renderer
{
struct Context;
struct Renderer;
}
}

namespace omni
{
namespace usd
{

class UsdContext;

namespace hydra
{

class IHydraEngineFactory;
using IHydraEngineFactoryPtr = carb::ObjectPtr<IHydraEngineFactory>;
class HydraEngineManager;
typedef struct OpaqueSharedHydraEngineContext* OpaqueSharedHydraEngineContextPtr;

}

class UsdManager
{
public:
    /**
     * Creates a UsdContext.
     *
     * @param name Name of the UsdContext to be created. The default context is named with empty string "".
     * @return Created UsdContext, or existing one if a context with same name is already created.
     */
    OMNI_USD_API static UsdContext* createContext(const std::string& name = "");

    /**
     * Destroys a UsdContext.
     *
     * @param name of the UsdContext to be destroyed. The default context is named with empty string "".
     * @return true if destroyed successfully, false if failed.
     */
    OMNI_USD_API static bool destroyContext(const std::string& name = "");

    /**
     * Gets a UsdContext.
     *
     * @param name of the UsdContext to get. The default context is named with empty string "".
     */
    OMNI_USD_API static UsdContext* getContext(const std::string& name = "");


    /*
     * Use by IHydraEngines at load/unload to register their factory class
     *
     */
    OMNI_USD_API static void registerHydraEngineFactory(const char* name,
                                                        omni::usd::hydra::IHydraEngineFactoryPtr factory);

    OMNI_USD_API static void unregisterHydraEngineFactory(const char* name);
   
    /**
     * Adds all loaded hydra engines to the USDContext. Used at startup
     *
     * All loaded hydra engines will share a single syncScope and run in a single rendering
     * thread when asyncRendering is enabled.
     *
     * Return type, first is the name of the engine, second is an opaque pointer to engine data
     *
     * Until legacy carb settings /renderer/active and /renderer/enabled are no longer used to
     * set the default hydra engine or override what extensions are "enabled", we need this function
     * to support legacy STARTUP behavior and it should be executed once AFTER all the extensions have loaded
     */
    OMNI_USD_API static std::vector<std::pair<std::string, hydra::OpaqueSharedHydraEngineContextPtr>> attachAllHydraEngines(
        UsdContext* context);

    /*
     * Advances all the hydra engines sync scopes rtx::kMaxFramesInFlight to trigger
     * deferred releases of all objects. Typically used to allow fully unloading
     * the USD Mesh data before loading another USD Stage
     */
    OMNI_USD_API static void advanceAllSyncScopes();

    /**
     * releaseAllHydraEngines() is designed to support the legacy Kit 1.0 Editor
     *
     * Unregisters all HydraEngineFactories and destroys any created OpaqueSharedHydraEngineContextPtr.
     *
     * @param context Optional, if valid, context releases all hydra engines prior to destroying any
     * @note Why context default value set to nullptr ? Implemented code will ignore any existing engine instance if it's null.
     *       This does not make any sense and if there should be some global shutdown function to clean up the engines
     *       it have to be explicit and not to rely on hidden default parameter.
     * OpaqueSharedHydraEngineContextPtr
     */
    OMNI_USD_API static void releaseAllHydraEngines(UsdContext* context = nullptr);

    /*
     * setSettingsPlugin() + setFoundationPlugins() are required initialization
     * methods of USDManager
     */
    OMNI_USD_API static void setSettingsPlugin(carb::settings::ISettings* settings);

    OMNI_USD_API static void setFoundationPlugins(gpu::foundation::GpuFoundation* gpuFoundation, uint32_t syncScope);

    // Until Kit redoes their implmentation of GpuFoundations integration, let's provide a global
    // getter for those that need GpuFoundations to be unblocked
    OMNI_USD_API static void getFoundationPlugins(gpu::foundation::GpuFoundation** outGpuFoundation);

    /**
     * @brief Called when from omni.usd extension shutdown
     *
     */
    OMNI_USD_API static void shutdownUsd();

    /**
     * Gets corresponding UsdContext of specified stage id.
     */
    OMNI_USD_API static UsdContext* getContextFromStageId(long int stageId);
            
    /**
     *  @note These APIs is replacing usage of name+index/opaque shared pointer based APIs.
     */

    /**
     *  @brief Create hydra engine instance with default configuration (from application provided settings).  
     *  @note Thread safe. If unused hydra engine instance exists with suitable configuration,
     *        will resue it instead of creating new one.  
     *  @param name [in] engine unique name.
     *  @param usdContextPtr [in] pointer to UsdContext instance.
     *  @return unique id of created hydra engine, will return sHydraEngineInvalidUniqueId value if failed.
     */
    OMNI_USD_API static hydra::HydraEngineUniqueId createHydraEngine(const char* name,
                                                                     UsdContext* usdContextPtr);

    /**
     *  @brief Create hydra engine instance with provided configuration. 
     *  @note Thread safe. If unused hydra engine instance exists with suitable configuration,
     *        will resue it instead of creating new one.  
     *  @param name [in] engine unique name.
     *  @param usdContextPtr [in] pointer to UsdContext instance.
     *  @param config [in] configuration for engine to be created, if invalid config provided will be created with default config. 
     *  @return unique id of created hydra engine, will return sHydraEngineInvalidUniqueId value if failed.
     */
    OMNI_USD_API static hydra::HydraEngineUniqueId createHydraEngineWithConfig(const char* name,
                                                                               UsdContext* usdContextPtr,
                                                                               hydra::HydraEngineCreationConfig const& config);

    /**
     *  @brief Destroy hydra engine with unique uid - releases runtime/gpu resources,
     *         removes it from the rendering threads. Thread safe.
     *  @note Will NOT destroy engine instance container and will leave it for future reuse.
     *        Destruction of the engine instance will happened on factory/context release.
     *        Viewports should be destroyed before calling this engine destruction API.
     *  @param uid [in] unique id of hydra engine instance.    
     *  @return true if succesfully destroyed engine, false otherwise.
     */
    OMNI_USD_API static bool destroyHydraEngine(hydra::HydraEngineUniqueId uid);
    
private:
    /**
     * Constructor.
     */
    UsdManager();

    /**
     * No copy.
     */
    UsdManager(const UsdManager&) = delete;

    /**
     * No assign.
     */
    UsdManager& operator=(const UsdManager&) = delete;

    /**
     * Destructor.
     */
    ~UsdManager();

    static UsdManager* instance();

    struct Impl;
    std::unique_ptr<Impl> m_impl;
};
}
}

namespace gpu
{
namespace realm
{

class Serializer;
class Deserializer;

template <typename T, typename Enabled>
struct TypeSerializer;

template <>
struct TypeSerializer<omni::usd::hydra::HydraEngineCreationConfig, void>
{    
    OMNI_USD_API void write(Serializer& serializer, const omni::usd::hydra::HydraEngineCreationConfig& engineCreationConfig);
    OMNI_USD_API void read(Deserializer& deserializer, omni::usd::hydra::HydraEngineCreationConfig& engineCreationConfig);
};

} // namespace realm
} // namespace gpu
