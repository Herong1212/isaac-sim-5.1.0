// Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Types.h"

#include <carb/Interface.h>
#include <carb/Types.h>

#include <typeinfo>

namespace omni
{
namespace anim
{
namespace graph
{
enum CharacterAnimatorHandle : uint32_t
{
    InvalidCharacterAnimatorHandleValue = static_cast<uint32_t>(-1)
};


/**
 * Defines an interface to control a character via Python.
 */
struct ICharacterAnimator
{
    CARB_PLUGIN_INTERFACE("omni::anim::graph::ICharacterAnimator", 0, 1)

    /**
     * Returns a active character at the specified USD Path.
     *
     * @param path The path to use for getting the character handle.
     * @return The character handle or CharacterAnimatorHandle::Invalid if not found.
     */
    const CharacterAnimatorHandle(CARB_ABI* getCharacterAnimator)(const char* path);

    /**
     * Sets the world transform (root).
     *
     * @param handle The character handle to use.
     * @param translation The root world translation to be applied.
     * @param rotation The root world rotation (quaternion) to be applied.
     */
    bool(CARB_ABI* setWorldTransform)(const CharacterAnimatorHandle handle,
        const carb::Float3& translation, const carb::Float4& rotation);

    /**
     * Gets the world transform (root).
     *
     * @param handle The character handle to use.*
     * @param translation The returned root world translation.
     * @param rotation The returned root world rotation (quaternion).
     */
    bool(CARB_ABI* getWorldTransform)(const CharacterAnimatorHandle handle,
        carb::Float3& translation, carb::Float4& rotation);

    /**
     * Gets the (world) joint transform.
     *
     * @param handle The character handle to use.
     * @param translation The returned world joint translation.
     * @param rotation The returned world joint rotation (quaternion)
     */
    bool(CARB_ABI* getJointTransform)(const CharacterAnimatorHandle handle, const char* jointToken,
        carb::Float3& translation, carb::Float4& rotation);


    /**
     * Gets the (local) joint transform.
     *
     * @param handle The character handle to use.
     * @param translation The returned local joint translations, needs to preallocate buffer.
     * @param rotation The returned local joint rotations (quaternions), needs to preallocate buffer
     */
    bool(CARB_ABI* getJointLocalTransforms)(const CharacterAnimatorHandle handle,
                                       span<carb::Float3> translations,
                                       span<carb::Float4> rotations);

    DirectModeAnimation (CARB_ABI* loadAnimation)(const char* usdPath);
    unsigned(CARB_ABI* playAnimation)(CharacterAnimatorHandle, const DirectModeAnimation&);
    bool (CARB_ABI* isAnimationPlaying)(CharacterAnimatorHandle, unsigned animID);
    float (CARB_ABI* animationDuration)(CharacterAnimatorHandle, unsigned animID);
    float (CARB_ABI* currentAnimationTime)(CharacterAnimatorHandle, unsigned animID);
    bool (CARB_ABI* seekAnimation)(CharacterAnimatorHandle, unsigned animID, float);
    bool (CARB_ABI* stopAnimation)(CharacterAnimatorHandle, unsigned animID);
    bool (CARB_ABI* deleteAnimation)(CharacterAnimatorHandle, unsigned animID);

    float (CARB_ABI* animationLayer)(CharacterAnimatorHandle, unsigned animID);
    bool (CARB_ABI* setAnimationLayer)(CharacterAnimatorHandle, unsigned animID, float);

    float (CARB_ABI* animationOpacity)(CharacterAnimatorHandle, unsigned animID);
    bool (CARB_ABI* setAnimationOpacity)(CharacterAnimatorHandle, unsigned animID, float);

    float (CARB_ABI* animationBlendIn)(CharacterAnimatorHandle, unsigned animID);
    bool (CARB_ABI* setAnimationBlendIn)(CharacterAnimatorHandle, unsigned animID, float);

    float (CARB_ABI* animationBlendOut)(CharacterAnimatorHandle, unsigned animID);
    bool (CARB_ABI* setAnimationBlendOut)(CharacterAnimatorHandle, unsigned animID, float);

    unsigned (CARB_ABI* animationOptions)(CharacterAnimatorHandle, unsigned animID);
    bool (CARB_ABI* turnAnimationOptionsOn)(CharacterAnimatorHandle, unsigned animID, unsigned);
    bool (CARB_ABI* turnAnimationOptionsOff)(CharacterAnimatorHandle, unsigned animID, unsigned);

    carb::events::IEventStreamPtr(CARB_ABI* getEventStream)(CharacterAnimatorHandle);
};
}
}
}
