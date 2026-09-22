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
enum CharacterHandle : uint32_t
{
    Invalid = static_cast<uint32_t>(-1)
};

/**
 * Defines an interface to control a character.
 *
 * A characer is active  component created on a UsdSkelRoot prim
 * by applying an animation graph to the UsdSkelRoot.
 *
 * The animation graph has a Skeleton bound for authoring.
 * The animation graph is created from various user defined animation clips,
 * blend trees, state machines/states, transitions and condition nodes.
 *
 * The variables exposed on the animation graph help the user to control
 * the outputs poses that are evaluated. To apply changes to the variables
 * to control the pose outcome.
 *
 * This interface also offers access to get and set the root world transform
 * and to get local joint transforms.
 *
 * All methods must be only called when the timeline is animating/playing.
 */
struct ICharacter
{
    CARB_PLUGIN_INTERFACE("omni::anim::graph::ICharacter", 1, 2)

    /**
     * Returns the number of active characters (SkelRoot) in the stage.
     *
     * @return The number of active characters (SkelRoot) in the stage.
     */
    size_t(CARB_ABI* getCharacterCount)();

    /**
     * Gets the array of active characters in the stage.
     *
     * @param characters The array of active characters to be populated in the array.
     * @param size Then number of active characters you have allocated for return array.
     * @see getCharacterCount
     */
    bool(CARB_ABI* getCharacters)(CharacterHandle* characters, size_t size);

    /**
     * Returns a active character at the specified USD Path.
     *
     * @param path The path to use for getting the character handle.
     * @return The character handle or CharacterHandle::Invalid if not found.
     */
    const CharacterHandle(CARB_ABI* getCharacter)(const char* path);

    /**
     * Returns the type information for the variable that is found on the AnimationGraph assigned
     * to the specified character.
     *
     * @param handle The character handle to use.
     * @param name The variable name to use.
     */
    const std::type_info&(CARB_ABI* getVariableType)(const CharacterHandle handle, const char* name);

    /**
     * Sets the variable value for the specified variable name.
     *
     * @tparam T The template type of variable to set be applied for.
     * @param handle The character handle to use.
     * @param name  The variable name to use.
     * @param value The value to be set.
     * @return true if successfully applied, false it failed and not applied.
     * @see getVariableType
     */
    template <typename T>
    bool setVariable(const CharacterHandle handle, const char* name, T value);

    /**
     * Set the Variable Array values for the specified variable name.
     *
     * @tparam T The template type of variable to set be applied for.
     * @param handle The character handle to use.
     * @param name  The variable name to use.
     * @param values The span of values to be set.
     * @return true if successfully applied, false it failed and not applied.
     * @see getVariableType
     * @see span
     */
    template <typename T>
    bool setVariableArray(const CharacterHandle handle, const char* name, const span<T>& values);

    /** Alternative to @see ICharacter::setVariable<const char*> */
    bool(CARB_ABI* setVariableString)(const CharacterHandle handle, const char* name, const char* value);

    /** Alternative to @see ICharacter::setVariable<const span<const char*>&> */
    bool(CARB_ABI* setVariableStringArray)(const CharacterHandle handle, const char* name, const span<const char*>& values);

    /** Alternative to @see ICharacter::setVariable<bool> */
    bool(CARB_ABI* setVariableBool)(const CharacterHandle handle, const char* name, bool value);

    /** Alternative to @see ICharacter::setVariable<const span<bool>&> */
    bool(CARB_ABI* setVariableBoolArray)(const CharacterHandle handle, const char* name, const span<bool>& values);

    /** Alternative to @see ICharacter::setVariable<int32_t> */
    bool(CARB_ABI* setVariableInt)(const CharacterHandle handle, const char* name, int32_t value);

    /** Alternative to @see ICharacter::setVariable<const span<int32_t>&> */
    bool(CARB_ABI* setVariableIntArray)(const CharacterHandle handle, const char* name, const span<int32_t>& values);

    /** Alternative to @see ICharacter::setVariable<float> */
    bool(CARB_ABI* setVariableFloat)(const CharacterHandle handle, const char* name, float value);

    /** Alternative to @see ICharacter::setVariable<const span<float>&> */
    bool(CARB_ABI* setVariableFloatArray)(const CharacterHandle handle, const char* name, const span<float>& values);

    /** Alternative to @see ICharacter::setVariable<const carb::Float3&> */
    bool(CARB_ABI* setVariableFloat3)(const CharacterHandle handle, const char* name, const carb::Float3& value);

    /** Alternative to @see ICharacter::setVariable<const span<carb::Float3>&> */
    bool(CARB_ABI* setVariableFloat3Array)(const CharacterHandle handle, const char* name, const span<carb::Float3>& values);

    /** Alternative to @see ICharacter::setVariable<const carb::Float4&> */
    bool(CARB_ABI* setVariableFloat4)(const CharacterHandle handle, const char* name, const carb::Float4& value);

    /** Alternative to @see ICharacter::setVariable<const span<carb::Float4>&> */
    bool(CARB_ABI* setVariableFloat4Array)(const CharacterHandle handle, const char* name, const span<carb::Float4>& values);

 /**
     * Gets the variable value for the specified variable name.
     *
     * @tparam T The template type of variable to set be applied for.
     * @param handle The character handle to use.
     * @param name  The variable name to use.
     * @param value The value to be returned.
     * @return true if successfully applied, false it failed and not applied.
     * @see getVariableType
     */
    template <typename T>
    bool getVariable(const CharacterHandle handle, const char* name, T value);

    /**
     * Get the variable array values for the specified variable name.
     *
     * @tparam T The template type of variable to set be applied for.
     * @param handle The character handle to use.
     * @param name  The variable name to use.
     * @param values The span of values to be returned.
     * @return true if successfully applied, false it failed and not applied.
     * @see getVariableType
     * @see span
     */
    template <typename T>
    bool getVariableArray(const CharacterHandle handle, const char* name, span<T>& values);

    /** Alternative to @see ICharacter::getVariable<const char*&> */
    bool(CARB_ABI* getVariableString)(const CharacterHandle handle, const char* name, const char*& value);

    /** Alternative to @see ICharacter::getVariable<span<const char*>&> */
    bool(CARB_ABI* getVariableStringArray)(const CharacterHandle handle, const char* name, span<const char*>& values);

    /** Alternative to @see ICharacter::getVariable<bool&> */
    bool(CARB_ABI* getVariableBool)(const CharacterHandle handle, const char* name, bool& value);

    /** Alternative to @see ICharacter::getVariable<span<span<bool>&> */
    bool(CARB_ABI* getVariableBoolArray)(const CharacterHandle handle, const char* name, span<bool>& values);

    /** Alternative to @see ICharacter::getVariable<int32_t&> */
    bool(CARB_ABI* getVariableInt)(const CharacterHandle handle, const char* name, int32_t& value);

    /** Alternative to @see ICharacter::getVariable<span<span<int32_t>&> */
    bool(CARB_ABI* getVariableIntArray)(const CharacterHandle handle, const char* name, span<int32_t>& values);

    /** Alternative to @see ICharacter::getVariable<float&> */
    bool(CARB_ABI* getVariableFloat)(const CharacterHandle handle, const char* name, float& value);

    /** Alternative to @see ICharacter::getVariable<span<span<float>&> */
    bool(CARB_ABI* getVariableFloatArray)(const CharacterHandle handle, const char* name, span<float>& values);

    /** Alternative to @see ICharacter::getVariable<carb::Float3&> */
    bool(CARB_ABI* getVariableFloat3)(const CharacterHandle handle, const char* name, carb::Float3& value);

    /** Alternative to @see ICharacter::getVariable<span<span<carb::Float3>&> */
    bool(CARB_ABI* getVariableFloat3Array)(const CharacterHandle handle, const char* name, span<carb::Float3>& values);

    /** Alternative to @see ICharacter::getVariable<carb::Float4&> */
    bool(CARB_ABI* getVariableFloat4)(const CharacterHandle handle, const char* name, carb::Float4& value);

    /** Alternative to @see ICharacter::getVariable<span<span<carb::Float4>&> */
    bool(CARB_ABI* getVariableFloat4Array)(const CharacterHandle handle, const char* name, span<carb::Float4>& values);

    /**
     * Determines if a node in the AnimationGraph assigned to a character is currently active.
     *
     * Typcically used from tooling solutions.
     *
     * @param handle The character handle to use.
     * @param handle The animation graph nodeName to check.
     */
    bool(CARB_ABI* isNodeActive)(const CharacterHandle handle, const char* nodeName);

    /**
     * Sets the world transform (root).
     *
     * @param handle The character handle to use.
     * @param translation The root world translation to be applied.
     * @param rotation The root world rotation (quaternion) to be applied.
     */
    bool(CARB_ABI* setWorldTransform)(const CharacterHandle handle,
        const carb::Float3& translation, const carb::Float4& rotation);

    /**
     * Gets the world transform (root).
     *
     * @param handle The character handle to use.*
     * @param translation The returned root world translation.
     * @param rotation The returned root world rotation (quaternion).
     */
    bool(CARB_ABI* getWorldTransform)(const CharacterHandle handle,
        carb::Float3& translation, carb::Float4& rotation);

    /**
     * Gets the (world) joint transform.
     *
     * @param handle The character handle to use.
     * @param translation The returned world joint translation.
     * @param rotation The returned world joint rotation (quaternion)
     */
    bool(CARB_ABI* getJointTransform)(const CharacterHandle handle, const char* jointToken,
        carb::Float3& translation, carb::Float4& rotation);


    /**
     * Gets the (local) joint transform.
     *
     * @param handle The character handle to use.
     * @param translation The returned local joint translations, needs to preallocate buffer.
     * @param rotation The returned local joint rotations (quaternions), needs to preallocate buffer
     */
    bool(CARB_ABI* getJointLocalTransforms)(const CharacterHandle handle,
                                       span<carb::Float3> translations,
                                       span<carb::Float4> rotations);

    /**
     * Returns the number of joints.
     * *
     * @param handle The character handle to use.
     * @return The number of joints.
     */
    size_t(CARB_ABI* getJointCount)(const CharacterHandle handle);

    /**
     * Returns the number of blend shapes.
     * *
     * @param handle The character handle to use.
     * @return The number of blend shapes.
     */
    size_t(CARB_ABI* getBlendShapeCount)(const CharacterHandle handle);

    /**
     * Gets the blend shape weights.
     *
     * @param handle The character handle to use.
     * @param weights The returned blend shape weight, needs to preallocate buffer.
     */
    bool(CARB_ABI* getBlendShapeWeights)(const CharacterHandle handle, span<float> weights);

    /**
     * Gets the weight of blend shape.
     *
     * @param handle The character handle to use.
     * @param nameToken The name of blend shape.
     */
    float(CARB_ABI* getBlendShapeWeight)(const CharacterHandle handle, const char* nameToken);

    /**
     * Manually updates (ticks) the character which update the pose based on animation graph processing.
     *
     * @param handle The character handle to use.
     * @param deltaTimeInSeconds The delta time to update with (in seconds).
     */
    void(CARB_ABI* update)(const CharacterHandle handle, float deltaTimeInSeconds);
};

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Inline template implementations for setVariable<T>,  and setVariableArray<T>
template <>
inline bool ICharacter::setVariable(const CharacterHandle handle, const char* name, const char* value)
{
    return setVariableString(handle, name, value);
}

template <>
inline bool ICharacter::setVariableArray(const CharacterHandle handle, const char* name, const span<const char*>& values)
{
    return setVariableStringArray(handle, name, values);
}

template <>
inline bool ICharacter::setVariable(const CharacterHandle handle, const char* name, bool value)
{
    return setVariableBool(handle, name, value);
}

template <>
inline bool ICharacter::setVariableArray(const CharacterHandle handle, const char* name, const span<bool>& values)
{
    return setVariableBoolArray(handle, name, values);
}

template <>
inline bool ICharacter::setVariable(const CharacterHandle handle, const char* name, int32_t value)
{
    return setVariableInt(handle, name, value);
}

template <>
inline bool ICharacter::setVariableArray(const CharacterHandle handle, const char* name, const span<int32_t>& values)
{
    return setVariableIntArray(handle, name, values);
}

template <>
inline bool ICharacter::setVariable(const CharacterHandle handle, const char* name, float value)
{
    return setVariableFloat(handle, name, value);
}

template <>
inline bool ICharacter::setVariableArray(const CharacterHandle handle, const char* name, const span<float>& values)
{
    return setVariableFloatArray(handle, name, values);
}

template <>
inline bool ICharacter::setVariable(const CharacterHandle handle, const char* name, const carb::Float3& value)
{
    return setVariableFloat3(handle, name, value);
}

template <>
inline bool ICharacter::setVariableArray(const CharacterHandle handle, const char* name, const span<carb::Float3>& values)
{
    return setVariableFloat3Array(handle, name, values);
}

template <>
inline bool ICharacter::setVariable(const CharacterHandle handle, const char* name, const carb::Float4& value)
{
    return setVariableFloat4(handle, name, value);
}

template <>
inline bool ICharacter::setVariableArray(const CharacterHandle handle, const char* name, const span<carb::Float4>& values)
{
    return setVariableFloat4Array(handle, name, values);
}

// Inline template implementations for getVariable<T>,  and getVariableArray<T>
template <>
inline bool ICharacter::getVariable(const CharacterHandle handle, const char* name, const char*& value)
{
    return getVariableString(handle, name, value);
}

template <>
inline bool ICharacter::getVariableArray(const CharacterHandle handle, const char* name, span<const char*>& values)
{
    return getVariableStringArray(handle, name, values);
}

template <>
inline bool ICharacter::getVariable(const CharacterHandle handle, const char* name, bool& value)
{
    return getVariableBool(handle, name, value);
}

template <>
inline bool ICharacter::getVariableArray(const CharacterHandle handle, const char* name, span<bool>& values)
{
    return getVariableBoolArray(handle, name, values);
}

template <>
inline bool ICharacter::getVariable(const CharacterHandle handle, const char* name, int32_t& value)
{
    return getVariableInt(handle, name, value);
}

template <>
inline bool ICharacter::getVariableArray(const CharacterHandle handle, const char* name, span<int32_t>& values)
{
    return getVariableIntArray(handle, name, values);
}

template <>
inline bool ICharacter::getVariable(const CharacterHandle handle, const char* name, float& value)
{
    return getVariableFloat(handle, name, value);
}

template <>
inline bool ICharacter::getVariableArray(const CharacterHandle handle, const char* name, span<float>& values)
{
    return getVariableFloatArray(handle, name, values);
}

template <>
inline bool ICharacter::getVariable(const CharacterHandle handle, const char* name, carb::Float3& value)
{
    return getVariableFloat3(handle, name, value);
}

template <>
inline bool ICharacter::getVariableArray(const CharacterHandle handle, const char* name, span<carb::Float3>& values)
{
    return getVariableFloat3Array(handle, name, values);
}

template <>
inline bool ICharacter::getVariable(const CharacterHandle handle, const char* name, carb::Float4& value)
{
    return getVariableFloat4(handle, name, value);
}

template <>
inline bool ICharacter::getVariableArray(const CharacterHandle handle, const char* name, span<carb::Float4>& values)
{
    return getVariableFloat4Array(handle, name, values);
}
}
}
}
