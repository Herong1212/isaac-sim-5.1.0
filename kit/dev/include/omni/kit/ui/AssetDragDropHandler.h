// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/datasource/DataSourceUtils.h>
#include <carb/extras/Path.h>
#include <carb/imgui/ImGui.h>
#include <carb/logging/Log.h>

#include <omniAudioSchema/sound.h>
#include <omni/kit/IViewport.h>
#include <omni/kit/PythonInterOpHelper.h>
#include <omni/timeline/ITimeline.h>
#include <omni/ui/Widget.h>
#include <omni/usd/AssetUtils.h>
#include <omni/usd/Selection.h>

// clang-format off
#include <omni/usd/UsdContextIncludes.h>
#include <omni/usd/UsdContext.h>
// clang-format on

#include <functional>
#include <regex>

namespace carb
{
namespace datasource
{
struct IDataSource;
struct Connection;
}
namespace imgui
{
struct ImGui;
}
}

namespace omni
{
namespace kit
{
namespace ui
{

static constexpr char kAssetDragDropPayloadId[] = "AssetDragDropPayloadId";

/**
 * Defines a class to handle asset drag and drop action.
 */
class AssetDragDropHandler
{
public:
    /**
     * Defines the payload of a drag
     */
    struct Payload
    {
        static constexpr size_t kStringBufferSize = 260;

        char path[kStringBufferSize]; ///! Absolute path to the asset.
        char dataSourcePath[kStringBufferSize]; ///! DataSource path to the asset.
        carb::datasource::IDataSource* dataSource; ///! DataSource of the asset.
        carb::datasource::Connection* connection; ///! Connection of the asset.
    };

    enum class AssetType
    {
        eUnknown,
        eUsd,
        eMdl,
        eAudio,
        ePrim,
    };

    using AssetDropHandlerFn = std::function<std::vector<PXR_NS::UsdPrim>(
        AssetDragDropHandler*, carb::imgui::ImGui* imgui, const char* payloadId, const carb::imgui::Payload* payload, void* userData)>;
    using AssetPeekHandlerFn = std::function<void(
        AssetDragDropHandler*, carb::imgui::ImGui* imgui, const carb::imgui::Payload* payload, const carb::Float4& rect)>;

    /**
     * Constructor.
     *
     * @param canPeek If this AssetDragDropHandler support @ref peek operation.
     * not be bound to any Prim.
     */
    AssetDragDropHandler(bool canPeek) : kCanPeek(canPeek)
    {
    }

    /**
     * Handles asset drag option.
     *
     * @param imgui The imgui instance.
     * @param payload The payload of the drag. Payload will be copied internally.
     * @param tooltip Tool tip to show while dragging.
     * @param flags DragDropFlags to control drag behaviors.
     */
    void drag(carb::imgui::ImGui* imgui, const Payload& payload, const char* tooltip, carb::imgui::DragDropFlags flags = 0)
    {
        if (imgui->beginDragDropSource(flags))
        {
            imgui->setDragDropPayload(
                kAssetDragDropPayloadId, &payload, sizeof(payload), carb::imgui::Condition::eAlways);
            imgui->text(tooltip);
            imgui->endDragDropSource();
        }
    }

    /**
     * Handles asset drop option.
     *
     * @param imgui The imgui instance.
     */
    std::vector<PXR_NS::UsdPrim> drop(carb::imgui::ImGui* imgui,
                         const char* payloadId = kAssetDragDropPayloadId,
                         const AssetDropHandlerFn& dropHandler = nullptr,
                         void* userData = nullptr)
    {
        std::vector<PXR_NS::UsdPrim> prims;
        if (imgui->beginDragDropTarget())
        {
            if (const carb::imgui::Payload* payload = imgui->acceptDragDropPayload(payloadId, 0))
            {
                if (dropHandler)
                    prims = dropHandler(this, imgui, payloadId, payload, userData);
                else
                    prims = defaultDropHandler(this, imgui, payloadId, payload, userData);
            }
            imgui->endDragDropTarget();
        }
        return prims;
    }

    /**
     * Peeks into current payload without releasing mouse button.
     *
     * @param imgui The imgui instance.
     */
    void peek(carb::imgui::ImGui* imgui, const carb::Float4& rect, const AssetPeekHandlerFn& peekHandler)
    {
        const carb::imgui::Payload* payload = imgui->getDragDropPayload();
        if (!payload)
        {
            stopPeek();
            return;
        }

        if (!payload->isDataType(kAssetDragDropPayloadId) &&
            !payload->isDataType(OMNIUI_NS::Widget::getDragDropPayloadId()))
        {
            return;
        }

        // Set mouse cursor shape to indicate drag
        imgui->setMouseCursor(carb::imgui::MouseCursor::eHand);

        if (!kCanPeek)
        {
            return;
        }

        peekHandler(this, imgui, payload, rect);
    }

    /**
     * Checks if the payload wants to query Prim or position under mouse position.
     *
     * @param imgui The imgui instance.
     * @param[out] addOutline Whether to add outline for queried Prim.
     * @return true if payload wants to query Prim under mouse position.
     */
    bool needsQuery(carb::imgui::ImGui* imgui, bool& addOutline) const
    {
        auto stage = omni::usd::UsdContext::getContext()->getStage();
        if (!stage)
        {
            return false;
        }

        addOutline = false;
        if (const carb::imgui::Payload* payload = imgui->getDragDropPayload())
        {
            if (strcmp(payload->dataType, kAssetDragDropPayloadId) != 0 &&
                strcmp(payload->dataType, OMNIUI_NS::Widget::getDragDropPayloadId()) != 0)
            {
                return false;
            }

            const char* url = reinterpret_cast<const char*>(payload->data);
            std::vector<std::string> assetUrls = splitMultiline(url);
            for (const auto& assetUrl : assetUrls)
            {
                auto assetType = getAssetType(assetUrl);
                if (assetType == AssetType::eMdl)
                {
                    addOutline = true;
                    return true;
                }
                else if (assetType == AssetType::eUsd)
                {
                    return true;
                }
                else if (assetType == AssetType::ePrim && PXR_NS::SdfPath::IsValidPathString(assetUrl))
                {
                    // If it's a material, then highlight outline of the object under the mouse cursor.
                    auto prim = stage->GetPrimAtPath(PXR_NS::SdfPath{ assetUrl });
                    if (prim)
                    {
                        bool isMaterial = prim.IsA<PXR_NS::UsdShadeMaterial>();
                        addOutline = isMaterial;
                        return isMaterial;
                    }
                }
            }
        }
        return false;
    }

    /**
     * Checks if peeking is in progress.
     */
    bool isPeeking() const
    {
        return m_peeking;
    }

    /**
     * @brief Checks if it's necessary to draw the full preview when peeking
     */
    bool hasPreview() const
    {
        return m_preview;
    }

    /**
     * Sets peeking state.
     *
     * @param peeking true to start peeking, false to stop peeking
     * @param preview true if it's necessary to draw the full preview of the
     *                layer. false if it's necessary to draw the cross.
     */
    void setPeeking(bool peeking, bool preview = false)
    {
        if (m_peeking == peeking)
        {
            return;
        }

        if (!peeking)
        {
            stopPeek();
        }
        else
        {
            PythonInterOpHelper::beginUndoGroup();
            m_peeking = peeking;
            m_preview = preview;
            m_hasUndoGroup = true;
        }
    }

    /**
     * Sets the peeking prims.
     *
     * @param prims the peeking preview prims.
     */
    void setPeekingPrims(const std::vector<PXR_NS::UsdPrim>& prims)
    {
        m_peekingPrims = prims;
    }

    /**
     * Gets the peeking prims.
     */
    std::vector<PXR_NS::UsdPrim> getPeekingPrims() const
    {
        return m_peekingPrims;
    }

    /**
     * Gets asset type from url.
     *
     * @param url the url of the asset to be checked.
     */
    static AssetType getAssetType(const std::string& url)
    {
        static const std::regex kMdlFile(
            "^.*\\.mdl(\\?.*)?$", std::regex_constants::icase | std::regex_constants::optimize);
        static const std::regex kAudioFile("^.*\\.(wav|wave|ogg|oga|flac|fla|mp3|m4a|spx|opus)(\\?.*)?$",
                                           std::regex_constants::icase | std::regex_constants::optimize);

        // Check for mdl first, because mdl may also be considered a readable
        // SdfFileFormat - ie, UsdStage::IsSupportedFile might return true
        if (std::regex_search(url, kMdlFile))
        {
            return AssetType::eMdl;
        }
        bool canBeOpened = PXR_NS::UsdStage::IsSupportedFile(url);
        if (canBeOpened)
        {
            return AssetType::eUsd;
        }
        if (std::regex_search(url, kAudioFile))
        {
            return AssetType::eAudio;
        }
        if (PXR_NS::SdfPath::IsValidPathString(url))
        {
            return AssetType::ePrim;
        }
        return AssetType::eUnknown;
    }

    /**
     * @brief Splits the given line to multilines.
     */
    static std::vector<std::string> splitMultiline(const char* input)
    {
        std::vector<std::string> result;
        const char* iterator = input;
        while (iterator && *iterator != '\0')
        {
            const char* foundLineBreak = strchr(iterator, '\n');
            if (foundLineBreak)
            {
                result.emplace_back(iterator, foundLineBreak - iterator);
            }
            else
            {
                result.emplace_back(iterator);
            }

            if (foundLineBreak)
            {
                iterator = foundLineBreak + 1;
            }
            else
            {
                iterator = nullptr;
            }
        }

        return result;
    }

    static std::vector<std::string> filterAssetPaths(const std::vector<std::string>& assetPaths, AssetType type)
    {
        std::vector<std::string> filteredAssetPaths;
        for (const std::string& assetPath : assetPaths)
        {
            if (getAssetType(assetPath) == type)
            {
                filteredAssetPaths.push_back(assetPath);
            }
        }

        return filteredAssetPaths;
    }

private:
    void stopPeek()
    {
        if (m_peeking)
        {
            m_peeking = false;
            for (auto& prim : m_peekingPrims)
            {
                if (prim.IsValid())
                {
                    omni::usd::UsdUtils::removePrim(prim);
                }
            }

            if (m_hasUndoGroup)
            {
                m_hasUndoGroup = false;
                PythonInterOpHelper::endUndoGroup();

                // Need to pop the previous undo group because peek is canceled and nothing done in between should be
                // undoable.
                PythonInterOpHelper::popLastUndoGroup();
            }
        }
    }

    static std::vector<PXR_NS::UsdPrim> defaultDropHandler(AssetDragDropHandler* handler,
        carb::imgui::ImGui* imgui,
        const char* payloadId,
        const carb::imgui::Payload* payload,
        void* userData)
    {
        std::vector<PXR_NS::UsdPrim> assetPrims;

        const char* url = "";
        const char* dataSourcePath = "";
        carb::datasource::IDataSource* dataSource = nullptr;
        carb::datasource::Connection* connection = nullptr;

        // From old content window ? FIXME: Do we need old content window support?
        // Old content window supports single drag and drop only.
        bool oldContentWindow = strcmp(payloadId, kAssetDragDropPayloadId) == 0;
        if (oldContentWindow)
        {
            const Payload* payloadData = reinterpret_cast<const Payload*>(payload->data);
            url = payloadData->path;
            dataSourcePath = payloadData->dataSourcePath;
            dataSource = payloadData->dataSource;
            connection = payloadData->connection;
        }
        else // From new content window
        {
            url = reinterpret_cast<const char*>(payload->data);
        }

        auto stage = omni::usd::UsdContext::getContext()->getStage();
        std::vector<std::string> assets = stage && url ? splitMultiline(url) : std::vector<std::string>{};
        auto usdAssets = filterAssetPaths(assets, AssetType::eUsd);
        auto mdlAssets = filterAssetPaths(assets, AssetType::eMdl);
        auto audioAssets = filterAssetPaths(assets, AssetType::eAudio);
        auto unknownAssets = filterAssetPaths(assets, AssetType::eUnknown);

        if (usdAssets.size() > 0 || mdlAssets.size() > 0 || audioAssets.size() > 0)
        {
            if (!handler->m_hasUndoGroup)
            {
                PythonInterOpHelper::beginUndoGroup();
                handler->m_hasUndoGroup = true;
            }
        }

        // If it can peek, we just directly use the existing peekingPrims.
        if (handler->kCanPeek && handler->hasPreview())
        {
            if (handler->m_peeking)
            {
                handler->m_peeking = false;

                PXR_NS::SdfPathVector selectedPrimPaths;

                for (auto& assetPrim : handler->m_peekingPrims)
                {
                    if (!assetPrim.IsValid())
                    {
                        continue;
                    }

                    PXR_NS::SdfPath path = assetPrim.GetPath();
                    selectedPrimPaths.push_back(path);
                    auto* isettings = carb::getCachedInterface<carb::settings::ISettings>();

                    // OM-38909: Since we're about to set the selection to this prim, make it un-pickable for snapping
                    static constexpr char kSnapEnabledSetting[] = "/app/viewport/snapEnabled";
                    static constexpr char kSnapToSurfaceSetting[] = PERSISTENT_SETTINGS_PREFIX "/app/viewport/snapToSurface";
                    const bool snapToSurface = isettings->getAsBool(kSnapEnabledSetting) && isettings->getAsBool(kSnapToSurfaceSetting);
                    omni::usd::UsdContext::getContext()->setPickable(path.GetText(), !snapToSurface);
                    if (assetPrim.IsA<PXR_NS::UsdGeomXform>())
                    {
                        assetPrim.SetInstanceable(isettings->getAsBool(PERSISTENT_SETTINGS_PREFIX "/app/stage/instanceableOnCreatingReference"));
                    }
                    assetPrims.push_back(assetPrim);
                }

                omni::usd::UsdContext::getContext()->getSelection()->setSelectedPrimPathsV2(selectedPrimPaths);
            }
        }

        for (const auto& asset : usdAssets)
        {
            std::string relativeUrl = asset;
            omni::usd::UsdUtils::makePathRelativeToLayer(stage->GetEditTarget().GetLayer(), relativeUrl);

            // If it cannot peek, we'll create all prims.
            if (!handler->kCanPeek || !handler->hasPreview())
            {
                carb::extras::Path urlPath(asset);
                std::string warningMsg;

                std::string newPrimPath = omni::usd::UsdUtils::findNextNoneExisitingNodePath(
                    stage, "/" + pxr::TfMakeValidIdentifier(urlPath.getStem().getString()), true);

                PythonInterOpHelper::runCreateReferenceCommand(relativeUrl, newPrimPath, true);
                auto assetPrim = stage->GetPrimAtPath(PXR_NS::SdfPath(newPrimPath));
                if (assetPrim)
                {
                    assetPrims.push_back(assetPrim);
                }
            }
        }

        const std::string targetPrim = (const char*)userData;
        if (mdlAssets.size() > 1 && !targetPrim.empty())
        {
            PythonInterOpHelper::postNotification("Multiple materials assignment is not supported.", true, false);
            CARB_LOG_WARN("Multiple materials assignment to prim %s is not supported.", targetPrim.c_str());
        }
        else
        {
            bool fallbackDataSource = false;
            if (mdlAssets.size() > 0 && !dataSource)
            {
                dataSource = carb::getFramework()->acquireInterface<carb::datasource::IDataSource>(
                    "carb.datasource-omniclient.plugin");
                connection = carb::datasource::connectAndWait({ "", nullptr, nullptr, false }, dataSource);
                fallbackDataSource = true;
            }

            for (const auto& asset : mdlAssets)
            {
                std::string relativeUrl = asset;
                omni::usd::UsdUtils::makePathRelativeToLayer(stage->GetEditTarget().GetLayer(), relativeUrl);

                carb::extras::Path urlPath(asset);
                if (!omni::usd::UsdUtils::hasPrimAtPath(stage, "/Looks"))
                {
                    std::string looksPath = omni::usd::UsdUtils::findNextNoneExisitingNodePath(stage, "/Looks", true);
                    PythonInterOpHelper::runCreatePrimCommand(looksPath.c_str(), "Scope", false);
                }

                if (!oldContentWindow)
                {
                    dataSourcePath = asset.c_str();
                }

                const std::string mtlName =
                    omni::usd::AssetUtils::findMaterialNameFromMdlContent(dataSource, connection, urlPath.getString().c_str(), dataSourcePath);

                if (!mtlName.empty())
                {
                    const std::string mtlPrimPath = omni::usd::UsdUtils::findNextNoneExisitingNodePath(
                        stage, "/Looks/" + PXR_NS::TfMakeValidIdentifier(mtlName), true);
                    PythonInterOpHelper::runCreateMdlMaterialPrimCommand(
                        url, mtlName, mtlPrimPath, targetPrim);
                    // when drag onto prim, material prim will not have been created yet so matrial assignment is done
                    // by runCreateMdlMaterialPrimCommand
                    auto assetPrim = stage->GetPrimAtPath(PXR_NS::SdfPath(mtlPrimPath));
                    if (assetPrim)
                    {
                        assetPrims.push_back(assetPrim);
                    }
                }
            }

            if (fallbackDataSource)
            {
                dataSource->disconnect(connection);
            }

        }
        
        for (const auto& asset : audioAssets)
        {
            std::string relativeUrl = asset;
            omni::usd::UsdUtils::makePathRelativeToLayer(stage->GetEditTarget().GetLayer(), relativeUrl);

            carb::extras::Path urlPath(asset);
            std::string path = omni::usd::UsdUtils::findNextNoneExisitingNodePath(
                stage, std::string("/") + PXR_NS::TfMakeValidIdentifier(std::string(urlPath.getStem())), true);
            PythonInterOpHelper::runCreateAudioPrimFromAssetPathCommand(relativeUrl, path);
            auto assetPrim = stage->GetPrimAtPath(PXR_NS::SdfPath(path));
            if (assetPrim)
            {
                assetPrims.push_back(assetPrim);
            }
        }

        for (const auto& asset : unknownAssets)
        {
            if (!payload->isDataType(OMNIUI_NS::Widget::getDragDropPayloadId()))
            {
                carb::getCachedInterface<omni::kit::IViewport>()->getViewportWindow(nullptr)->postToast("unsupported file format");
                CARB_LOG_WARN("Unsupported file %s", asset.c_str());
                break;
            }
        }

        if (handler->m_hasUndoGroup)
        {
            handler->m_hasUndoGroup = false;
            PythonInterOpHelper::endUndoGroup();
        }

        return assetPrims;
    }

    const bool kCanPeek;
    bool m_peeking = false;
    // true when it's necessary to draw the full preview when peeking
    bool m_preview = false;
    bool m_hasUndoGroup = false;
    std::vector<PXR_NS::UsdPrim> m_peekingPrims;
};
}
}
}
