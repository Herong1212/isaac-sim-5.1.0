// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/assets/IAssets.h>
#include <carb/filesystem/IFileSystem.h>
#include <carb/imaging/IImaging.h>
#include <carb/svg/Svg.h>
#include <carb/tokens/ITokens.h>
#include <carb/tokens/TokensUtils.h>

#include <omni/renderer/utils/AssetsManagement.h>

#include <cassert>
#include <unordered_set>

namespace omni
{
namespace ui
{

/**
 * @brief Helper class to store asset-related interfaces and entities.
 * The main entity is an asset pool, which is supposed to be single for the whole omni.ui.
 * As omni.ui do not have solid enter/exit pattern as e.g. Carbonite plugins do, reference
 * counting mechanism is implemented to make sure we don't leak resources.
 * Each time reference count is 0, the asset pool is released. When reference count goes
 * positive, asset pool is recreated.
 */
class AssetsState
{
public:
    carb::filesystem::IFileSystem* fs = nullptr;
    carb::tokens::ITokens* tokens = nullptr;
    carb::assets::IAssets* assets = nullptr;
    carb::imaging::IImaging* imaging = nullptr;
    carb::svg::Svg* svg = nullptr;

    omni::renderer::utils::AssetsManager* assetsManager = nullptr;
    carb::assets::Pool assetPool = carb::assets::kInvalidPool;

    bool isInitialized = false;
    bool releaseHookRegistered = false;

    AssetsState()
    {
        fs = carb::getCachedInterface<carb::filesystem::IFileSystem>();
        tokens = carb::getCachedInterface<carb::tokens::ITokens>();
        assets = carb::getCachedInterface<carb::assets::IAssets>();
        imaging = carb::getCachedInterface<carb::imaging::IImaging>();
        svg = carb::getCachedInterface<carb::svg::Svg>();
        carb::getFramework()->addReleaseHook(assets, sAssetsReleased, this);
        releaseHookRegistered = true;
    }
    ~AssetsState()
    {
        // As this object is expected to be static, we use regular assert
        assert(counter == 0);
        if (carb::getFramework())
        {
            if (releaseHookRegistered)
                carb::getFramework()->removeReleaseHook(assets, sAssetsReleased, this);
        }
    }

    static void sAssetsReleased(void*, void* user)
    {
        static_cast<AssetsState*>(user)->assetsReleased();
    }

    void assetsReleased()
    {
        fs = nullptr;
        tokens = nullptr;
        assets = nullptr;
        imaging = nullptr;
        svg = nullptr;
        assetPool = carb::assets::kInvalidPool;

        if (assetsManager)
        {
            assetsManager->notifyShutdown();
        }

        carb::getFramework()->removeReleaseHook(nullptr, sAssetsReleased, this);
        releaseHookRegistered = false;
    }

    carb::extras::Path getAssetPath(const std::string& sourceUrl)
    {
        carb::extras::Path imagePath;
        // TODO: should we support other kind of url for image provider?
        if (sourceUrl.find("://") != std::string::npos || sourceUrl.compare(0, 5, "file:") == 0 ||
            sourceUrl.compare(0, 2, "//") == 0 || sourceUrl[0] == '$')
        {
            // It's URL
            imagePath = sourceUrl;
        }
        else if (sourceUrl[0] == '/')
        {
            // If the first symbol is '/', it's direct path in Linux. Windows should accept it as path in the current
            // drive.
#if CARB_PLATFORM_WINDOWS
            // Get drive name from app directory and append imagePath.
            imagePath = carb::extras::Path{ "${drive}" }.join(sourceUrl);
#else
            imagePath = sourceUrl;
#endif
        }
        else if (sourceUrl.length() > 2 && sourceUrl[1] == ':')
        {
            // If the second symbol is ':', it's direct path in Windows.
#if CARB_PLATFORM_WINDOWS
            imagePath = sourceUrl;
#else
            // TODO: What should we do if we have Windows path on Linux? ATM the drive is removed from the path.
            imagePath = sourceUrl.substr(2);
#endif
        }
        else
        {
            // It's relative path. We consider it's relative to the application directory.
            imagePath = carb::extras::Path{ "${kit}" }.join(sourceUrl);
        }

        imagePath = carb::tokens::resolveString(tokens, { carb::cpp::unsafe_length, imagePath.getStringBuffer() });

        return imagePath;
    }

    void startup()
    {
        if (!isInitialized)
        {
            assetsManager = new omni::renderer::utils::AssetsManager;
            assetPool = assets->createPool("omni.ui ImageProviders");
            isInitialized = true;
        }
    }
    void shutdown()
    {
        if (isInitialized)
        {
            // The framework could be shutting down at this point. Re-acquire IAssets to see if it matches.
            if (carb::getFramework() && assets)
            {
                carb::AcquireInterfaceOptions aio{};
                aio.sizeofThis = sizeof(aio);
                aio.clientName = g_carbClientName;
                aio.desc = carb::assets::IAssets::getInterfaceDesc();
                aio.flags = (carb::AcquireInterfaceFlags)(carb::fAIFNoInitialize | carb::fAIFOptional);
                auto newAssets = (carb::assets::IAssets*)carb::getFramework()->internalAcquireInterface(aio);
                if (newAssets == assets)
                {
                    assets->destroyPool(assetPool);
                }
            }
            assetPool = carb::assets::kInvalidPool;
            delete assetsManager;
            assetsManager = nullptr;
            isInitialized = false;
        }
    }

    // We need this ref counting because omni.ui doesn't have clear shutdown routine,
    // and we need a way to free asset pool resources
    size_t counter = 0;
    void incPoolRef()
    {
        ++counter;
        if (assetPool == carb::assets::kInvalidPool)
        {
            startup();
        }
    }
    void decPoolRef()
    {
        if (counter > 0)
        {
            --counter;
            if (counter == 0)
            {
                shutdown();
            }
        }
        else
        {
            CARB_LOG_ERROR("Asset state manager: asymmetric ref counting detected!");
        }
    }
};

AssetsState& getAssetsState();

}
}
