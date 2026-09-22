// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#ifndef USD_UTILS_INCLUDES
#    error "Please include UtilsIncludes.h before including this header or in pre-compiled header."
#endif

#include <carb/datasource/IDataSource.h>

#include <omniAudioSchema/sound.h>
#include <omni/usd/UsdUtils.h>

#include <condition_variable>

namespace omni
{
namespace usd
{
class AssetUtils
{
public:
    /**
     * Imports an external file in to the stage.
     *
     * @param stage The stage to import file into.
     * @param importUrl The URL of the imported file.
     * @param path The path to create the imported prim at.
     * @param dataSourcePath The path of the file in its dataSource (Only needed for MDL).
     * @param dataSource DataSource associated with this file (Only needed for MDL).
     * @param connection Connection associated with this file (Only needed for MDL).
     */
    static pxr::UsdPrim createPrimFromAssetPath(pxr::UsdStageWeakPtr stage,
                                                const char* importUrl,
                                                const char* primPath,
                                                const char* dataSourcePath = "",
                                                carb::datasource::IDataSource* dataSource = nullptr,
                                                carb::datasource::Connection* connection = nullptr)
    {
        pxr::UsdPrim prim;
        std::string newPrimPath = omni::usd::UsdUtils::findNextNoneExisitingNodePath(stage, primPath, true);

        // MDL file
        static const std::regex kMdlFile("^.*\\.mdl(?:\\?.*)?$", std::regex_constants::icase | std::regex_constants::optimize);
        // the supported audio formats
        static const std::regex kAudioFile(
            "^.*\\.(?:wav|wave|ogg|oga|flac|fla|mp3|m4a|spx|opus)(?:\\?.*)?$", std::regex_constants::icase | std::regex_constants::optimize);

        std::string relativeUrl = importUrl;
        omni::usd::UsdUtils::makePathRelativeToLayer(stage->GetEditTarget().GetLayer(), relativeUrl);

        if (std::regex_search(importUrl, kMdlFile))
        {
            CARB_ASSERT(dataSource && connection);
            prim = createMdlMaterial(
                stage, pxr::SdfPath(newPrimPath), relativeUrl.c_str(), dataSourcePath, "", dataSource, connection);
        }
        else if (std::regex_search(importUrl, kAudioFile))
        {
            auto sound = pxr::OmniAudioSchemaOmniSound::Define(stage, pxr::SdfPath(newPrimPath));
            if (sound)
            {
                sound.CreateFilePathAttr(pxr::VtValue(pxr::SdfAssetPath(relativeUrl.c_str())));
                prim = sound.GetPrim();
            }
            else
                CARB_LOG_ERROR("failed to define an OmniAudioSchemaOmniSound");
        }
        return prim;
    }

    static pxr::UsdPrim createMdlMaterial(pxr::UsdStageWeakPtr stage,
                                          const pxr::SdfPath& primPath,
                                          const char* mdlPath,
                                          const char* mdlDataSourcePath,
                                          const char* mdlMaterialName = "",
                                          carb::datasource::IDataSource* dataSource = nullptr,
                                          carb::datasource::Connection* connection = nullptr)
    {
        // How do we get the material name:
        // - If user provides one via mdlMaterialName, use it.
        // - If user doesn't provide mdlMaterialName, but provides dataSource and connection, we do a regex search on
        //   the MDL file's content and extract the first material name.
        // - If user provides nothing, or previous step fails, we take the MDL filename as the material name.
        std::string materialName = (mdlMaterialName == nullptr) ? "" : mdlMaterialName;
        if (materialName.empty() && dataSource && connection)
        {
            materialName = findMaterialNameFromMdlContent(dataSource, connection, mdlPath, mdlDataSourcePath);
        }

        if (materialName.empty())
        {
            carb::extras::Path mdlCarbPath(mdlPath);
            materialName = mdlCarbPath.getStem();
        }

        if (materialName.empty())
        {
            CARB_LOG_ERROR("Failed to find material name for MDL file %s", mdlPath);
        }

        auto materialPrim = pxr::UsdShadeMaterial::Define(stage, primPath);
        if (materialPrim)
        {
            pxr::SdfPath shaderPrimPath = primPath.AppendPath(pxr::SdfPath("Shader"));
            auto shaderPrim = pxr::UsdShadeShader::Define(stage, shaderPrimPath);
            if (shaderPrim)
            {
                carb::settings::ISettings* settings = carb::getFramework()->acquireInterface<carb::settings::ISettings>();
                bool authorOldMdlSchema = settings->getAsBool(omni::usd::kAuthorOldMdlSchemaSettingPath);
                if (authorOldMdlSchema)
                {
                    materialPrim.CreateSurfaceOutput().ConnectToSource(
                        shaderPrim.CreateOutput(pxr::TfToken("out"), pxr::SdfValueTypeNames->Token));

                    shaderPrim.CreateIdAttr(pxr::VtValue(pxr::TfToken("mdlMaterial")));
                    shaderPrim.GetPrim()
                        .CreateAttribute(pxr::TfToken("module"), pxr::SdfValueTypeNames->Asset)
                        .Set(pxr::SdfAssetPath(mdlPath));

                    shaderPrim.GetPrim().CreateAttribute(pxr::TfToken("name"), pxr::SdfValueTypeNames->String).Set(materialName);
                }
                else
                {
                    pxr::TfToken mdlToken("mdl");
                    auto shaderOut = shaderPrim.CreateOutput(pxr::TfToken("out"), pxr::SdfValueTypeNames->Token);
                    materialPrim.CreateSurfaceOutput(mdlToken).ConnectToSource(shaderOut);
                    materialPrim.CreateVolumeOutput(mdlToken).ConnectToSource(shaderOut);
                    materialPrim.CreateDisplacementOutput(mdlToken).ConnectToSource(shaderOut);

                    shaderPrim.GetImplementationSourceAttr().Set(pxr::UsdShadeTokens->sourceAsset);
                    shaderPrim.SetSourceAsset(pxr::SdfAssetPath(mdlPath), mdlToken);

                    shaderPrim.SetSourceAssetSubIdentifier(pxr::TfToken(materialName), mdlToken);
                }
            }
        }
        return materialPrim.GetPrim();
    }

    static std::string findMaterialNameFromMdlContent(carb::datasource::IDataSource* dataSource,
                                                      carb::datasource::Connection* connection,
                                                      const char* mdlPath,
                                                      const char* mdlDataSourcePath)
    {
        std::string materialName;

        struct ReadArgs
        {
            std::string mdlContent;
            std::atomic<bool> readDone{ false };
            std::condition_variable readDoneCondition;
            std::mutex readDoneMutex;
        } readArgs;

        dataSource->readData(connection, mdlDataSourcePath, std::malloc,
                             [](carb::datasource::Response response, const char* path, uint8_t* payload,
                                size_t payloadSize, void* userData) {
                                 ReadArgs* readArgs = reinterpret_cast<ReadArgs*>(userData);
                                 if (response == carb::datasource::Response::eOk)
                                 {
                                     readArgs->mdlContent = std::string(payload, payload + payloadSize);
                                 }

                                 std::free(payload);

                                 std::unique_lock<std::mutex> lock(readArgs->readDoneMutex);
                                 readArgs->readDone.store(true, std::memory_order_relaxed);
                                 readArgs->readDoneCondition.notify_all();
                             },
                             &readArgs);

        {
            std::unique_lock<std::mutex> lock(readArgs.readDoneMutex);
            readArgs.readDoneCondition.wait(
                lock, [&readArgs] { return readArgs.readDone.load(std::memory_order_relaxed); });
        }

        if (readArgs.mdlContent.length() == 0)
        {
            CARB_LOG_ERROR("Failed to load %s when creating MDL material from it", mdlPath);
            return "";
        }

        // Do a regex search on the content of MDL file to get first valid material name to use
        const static std::regex kExportedMaterialRegex(
            "export\\s+material\\s+([^\\s]+)\\s*\\(", std::regex_constants::optimize);

        std::smatch match;
        if (std::regex_search(readArgs.mdlContent, match, kExportedMaterialRegex))
        {
            if (match.size() >= 2)
            {
                materialName = match[1];
            }
            else
            {
                CARB_LOG_WARN("Could not extract material name from %s. Fallback to filename.", mdlPath);
            }
        }

        return materialName;
    }
};
}
}
