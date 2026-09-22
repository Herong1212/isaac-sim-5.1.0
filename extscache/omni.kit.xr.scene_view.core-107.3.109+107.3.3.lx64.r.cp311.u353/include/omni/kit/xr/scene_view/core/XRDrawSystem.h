// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "Details.h"

#include <carb/events/IEvents.h>

#include <omni/ui/scene/AbstractDrawSystem.h>
#include <omni/ui/scene/DrawBuffer.h>
#include <pxr/usd/usd/stage.h>
#include <rtx/resourcemanager/ResourceManager.h>

#include <set>
#include <unordered_map>

namespace omni::usd
{
class UsdContext;
}

namespace omni::kit::xr
{
class XRSceneView;
}

OMNI_KIT_XR_SCENEVIEW_CORE_NAMESPACE_OPEN

class XRUiDrawItemBase;

/**
 * @brief Class used to interface between scene UI and the USD scene, converting from the generated
 * DrawBuffer into USD objects, and managing them as needed.
 */
class XRDrawSystem : public omni::ui::scene::AbstractDrawSystem
{
public:
    static std::string k_basePath;
    static std::string k_scenePathPrefix;

    static std::string k_polyPathPrefix;
    static std::string k_pointsPathPrefix;
    static std::string k_linesPathPrefix;
    static std::string k_textsPathPrefix;
    static std::string k_errorPathPrefix;

    static void initializePaths();

    XRDrawSystem(const std::string& basePath);
    ~XRDrawSystem() override;

    virtual void setup() override;
    virtual void beginFrame() override;
    virtual void render(const omni::ui::scene::DrawBuffer* const* buffers,
                        size_t bufferCount,
                        const omni::ui::scene::Matrix44& projection,
                        const omni::ui::scene::Matrix44& view,
                        float width,
                        float height,
                        float dpiScale) override;
    virtual void endFrame() override;
    virtual void destroy() override;

    void trackTextures(rtx::resourcemanager::RpResource* newTexture, rtx::resourcemanager::RpResource* oldTexture);

    const std::string& getRootPath() const
    {
        return m_rootPath;
    }

    // For systems which want to filter only the UI USD Prims...
    static const char* getUsdBasePath();

    // use this in actual classes to quickly check if FSD is enabled or not
    // TODO: OMPE-16574 -- Remove FSD checks once FSD replaces OmniHydra completely
    static bool usesFsd();

    // Update only the transforms of the XR Draw System
    void updateTransforms();

private:
    void _doSetup();
    void _doDestroy();

    class TextureTracker;
    std::shared_ptr<TextureTracker> m_textureTracker;

    std::vector<const omni::ui::scene::DrawBuffer*> _validateDrawBuffers(const omni::ui::scene::DrawBuffer* const* buffers,
                                                                         size_t bufferCount);
    void _initializeNewPrims(const std::vector<const omni::ui::scene::DrawBuffer*>& newPrimIds);
    void _updateAllPrims(const std::vector<const omni::ui::scene::DrawBuffer*>& newPrimIds);
    void _removeUnusedPrims();

    std::string m_rootPath;
    bool m_hasSetup = false;

    carb::events::ISubscriptionPtr m_stageUpdateSubscription;

    omni::usd::UsdContext* m_usdContext = nullptr;
    PXR_NS::UsdStageWeakPtr m_stage;
    PXR_NS::SdfLayerRefPtr m_sessionLayer;

    std::unordered_map<const omni::ui::scene::DrawBuffer*, std::unique_ptr<XRUiDrawItemBase>> m_trackedItems;
    std::unordered_map<const omni::ui::scene::DrawBuffer*, size_t> m_invisibleNewPrims; // map of primId to number of
                                                                                        // frames before it becomes
                                                                                        // visible
    std::set<const omni::ui::scene::DrawBuffer*> m_usedPrimIds;

    // Until FSD becomes the standard for everything, we need some support to check if it's
    // currently enabled in Kit or not.
    // TODO: OMPE-16574 -- Remove FSD checks once FSD replaces OmniHydra completely
    static bool s_usesFsd;
    static void onFsdEnabledSettingChanged(const carb::dictionary::Item* changedItem,
                                           carb::dictionary::ChangeEventType eventType,
                                           void*);
};

OMNI_KIT_XR_SCENEVIEW_CORE_NAMESPACE_CLOSE
