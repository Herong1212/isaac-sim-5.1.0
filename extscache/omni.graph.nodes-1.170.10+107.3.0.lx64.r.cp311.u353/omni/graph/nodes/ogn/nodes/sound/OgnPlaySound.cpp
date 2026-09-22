// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <omni/usd/IStageAudio.h>
#include <omni/fabric/FabricUSD.h>

#include <OgnPlaySoundDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
/* We want this node to trigger the playing of the sound once the sound asset is loaded AND we want to pass the voice
 * pointer to the outputs. To have access to this pointer, we need the sound to be loaded before we exit the compute
 * function. Because the loading of the sound happens asynchronously, we need to wait. We use a promise to wait for the
 * sound to be loaded. The subscribeToAssetLoad function calls this afterSoundLoaded function when the sound is loaded.
 * This function sets the promise's value, which fulfills the promise, allowing the future.get() to return.
 */

// This is the callback function that is called when the sound is loaded. It sets the promise's value to true,
// triggering the future.get() to return.
void afterSoundLoaded(void* data)
{
    auto* promise = static_cast<std::promise<bool>*>(data);
    promise->set_value(true);
};
}

class OgnPlaySound
{
public:
    // In the initialize function, we register a callback to the prim attribute. This callback is called when the prim
    // value is changed, which we use to load the sound. We also call the onValueChanged function to load the sound that
    // is already set.
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        AttributeObj const attrObj = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::prim.m_token);
        attrObj.iAttribute->registerValueChangedCallback(attrObj, onValueChanged, true);
        onValueChanged(attrObj, nullptr);
    }

    // This function is called when the prim attribute is changed. It loads the sound.
    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        auto const nodeObj = attrObj.iAttribute->getNode(attrObj);
        OgnPlaySoundDatabase db(nodeObj);
        loadSound(db);
    }

    // This function loads the sound. It waits for the sound to be loaded before returning.
    static bool loadSound(OgnPlaySoundDatabase& db)
    {
        usd::audio::AudioManager* audioManager = getAudioManager(db);
        if (!audioManager)
            return false;

        char const* primPathText = getPrimPath(db);
        if (!primPathText)
            return false;

        waitWhileSoundLoads(db, audioManager, primPathText);
        return true;
    }

    // This function gets the audio manager. If it fails to get the audio manager, it logs an error and returns nullptr.
    static usd::audio::AudioManager* getAudioManager(OgnPlaySoundDatabase& db)
    {
        usd::audio::AudioManager* audioManager = usd::audio::getDefaultAudioManager();
        if (!audioManager)
        {
            db.logError("Unable to acquire Audio Manager!");
        }
        return audioManager;
    }

    // This function gets the prim path. If it fails to get the prim path, it logs an error and returns nullptr.
    static char const* getPrimPath(OgnPlaySoundDatabase& db)
    {
        fabric::PathC const primPath = db.inputs.prim.firstOrDefault();
        if (primPath == fabric::PathC())
        {
            db.outputs.soundId() = 0;
            return nullptr;
        }
        char const* primPathText = toSdfPath(primPath).GetText();
        return primPathText;
    }

    // This function waits for the sound to be loaded. It sets a promise and waits for the promise to be set, which
    // happens when the sound is loaded. It also checks the load status of the sound. If it fails to subscribe to the
    // sound load, it logs an error.
    static void waitWhileSoundLoads(OgnPlaySoundDatabase& db,
                                    usd::audio::AudioManager* audioManager,
                                    char const* primPathText)
    {
        std::promise<bool> promise;
        std::future<bool> result = promise.get_future();

        bool const subscribeStatus = subscribeToAssetLoad(audioManager, primPathText, afterSoundLoaded, (void*)&promise);

        if (subscribeStatus)
        {
            // Wait for the promise to be set, which happens when the sound is loaded.
            result.get();
            checkLoadStatus(db, audioManager, primPathText);
        }
        else
        {
            db.logError("Failed to subscribe to audio load!");
        }
    }

    // This function checks the load status of the sound. If the sound it not loaded, it logs an error or warning.
    static void checkLoadStatus(OgnPlaySoundDatabase& db, usd::audio::AudioManager* audioManager, char const* primPathText)
    {
        usd::audio::AssetLoadStatus const assetLoadStatus = getSoundAssetStatus(audioManager, primPathText);

        if (assetLoadStatus == usd::audio::AssetLoadStatus::eInProgress)
        {
            db.logWarning("Asset loading is in progress!");
        }
        else if (assetLoadStatus == usd::audio::AssetLoadStatus::eFailed)
        {
            db.logError("Asset has failed to load!");
        }
        else if (assetLoadStatus == usd::audio::AssetLoadStatus::eNotRegistered)
        {
            db.logError("Prim was not registered from hydra yet!");
        }
        else if (assetLoadStatus == usd::audio::AssetLoadStatus::eNoAssetPath)
        {
            db.logWarning("No asset path has been set for the prim.  No load has been queued!");
        }
    }

    // This function ensures that the sound is loaded and plays it if it is. It logs an error if the sound is not
    // loaded.
    static bool compute(OgnPlaySoundDatabase& db)
    {
        if (!loadSound(db))
            return false;

        if (!playSound(db))
            return false;

        return true;
    }

    // This function plays the sound. It logs an error if the sound is not played. It sets the outputs.soundId to the
    // voice pointer or nullptr if the sound is not played.
    static bool playSound(OgnPlaySoundDatabase& db)
    {
        usd::audio::AudioManager* audioManager = getAudioManager(db);
        if (!audioManager)
            return false;

        char const* primPathText = getPrimPath(db);
        if (!primPathText)
        {
            db.logError("No prim has been set.");
            db.outputs.soundId() = 0;
            return false;
        }

        carb::audio::Voice* voice = spawnVoice(audioManager, primPathText);
        if (!voice)
        {
            db.logError("Unable to create sound id!");
            db.outputs.soundId() = 0;
            return false;
        }

        db.outputs.soundId() = reinterpret_cast<uint64_t>(voice);
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
