// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief Utilities for \ref carb::input::IInput
#pragma once
#include "../logging/Log.h"
#include "IInput.h"
#include "../cpp/StringView.h"
#include "../extras/StringUtils.h"

#include <string>
#include <type_traits>


namespace carb
{
namespace input
{

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                                  Name Mapping                                                      //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#ifndef DOXYGEN_BUILD

static constexpr struct
{
    DeviceType ident;
    const char* name;
} g_deviceTypeToName[] = {
#    define CARBINPUT_DEVICETYPE_NAME(a, b) { (a), (b) },
#    include "detail/DeviceTypeName.h"
#    undef CARBINPUT_DEVICETYPE_NAME
};
static_assert(CARB_COUNTOF(g_deviceTypeToName) == unsigned(DeviceType::eCount), "Add missing entries");

static constexpr struct
{
    KeyboardInput ident;
    const char* name;
} kKeyboardInputCodeName[] = {
#    define CARBINPUT_KEYBOARDINPUT_NAME(a, b) { (a), (b) },
#    include "detail/KeyboardInputName.h"
#    undef CARBINPUT_KEYBOARDINPUT_NAME
};
static_assert(CARB_COUNTOF(kKeyboardInputCodeName) == unsigned(KeyboardInput::eCount), "Add missing entries");

static constexpr struct
{
    KeyboardModifierFlags ident;
    const char* name;
} kModifierFlagName[] = {
#    define CARBINPUT_KEYBOARDMODIFIERFLAG_NAME(a, b) { (a), (b) },
#    include "detail/KeyboardModifierFlagName.h"
#    undef CARBINPUT_KEYBOARDMODIFIERFLAG_NAME
};
static_assert(CARB_COUNTOF(kModifierFlagName) == kKeyboardModifierFlagCount, "Add missing entries");

static constexpr struct
{
    MouseInput ident;
    const char* name;
} kMouseInputCodeName[] = {
#    define CARBINPUT_MOUSEINPUT_NAME(a, b) { (a), (b) },
#    include "detail/MouseInputName.h"
#    undef CARBINPUT_MOUSEINPUT_NAME
};
static_assert(CARB_COUNTOF(kMouseInputCodeName) == unsigned(MouseInput::eCount), "Add missing entries");

static constexpr struct
{
    GamepadInput ident;
    const char* name;
} kGamepadInputCodeName[] = {
#    define CARBINPUT_GAMEPADINPUT_NAME(a, b) { (a), (b) },
#    include "detail/GamepadInputName.h"
#    undef CARBINPUT_GAMEPADINPUT_NAME
};
static_assert(CARB_COUNTOF(kGamepadInputCodeName) == unsigned(GamepadInput::eCount), "Add missing entries");

#endif

/**
 * Returns a string representation of the device type.
 * @see getDeviceTypeFromString()
 * @param deviceType \ref DeviceType
 * @returns A string representation of the device type, or "Unknown" if unknown.
 */
inline const char* getDeviceTypeString(DeviceType deviceType)
{
    // doxygen seems to incorrectly detect this macro as a 'member' of something (the function?!)
    // and warns about it even if it _is_ documented or marked as '@private'.  Similar patterns
    // with macros are also used elsewhere so it's not clear why these uses here are problematic.
    // The only way to avoid the warning seems to be with "#ifndef DOXYGEN_SHOULD_SKIP_THIS".
#ifndef DOXYGEN_SHOULD_SKIP_THIS
#    define CARBINPUT_DEVICETYPE_NAME(a, b)                                                                            \
        case (a):                                                                                                      \
            return (b);
#endif

    switch (deviceType)
    {
#include "detail/DeviceTypeName.h"
        default:
            return "Unknown";
    }

#undef CARBINPUT_DEVICETYPE_NAME
}

/**
 * Converts a device-type string to a \ref DeviceType.
 * @see getDeviceTypeString()
 * @param deviceTypeString The string to convert.
 * @returns A \ref DeviceType, or \ref DeviceType::eUnknown if the string is not known.
 */
inline DeviceType getDeviceTypeFromString(const char* deviceTypeString)
{
#ifndef DOXYGEN_SHOULD_SKIP_THIS
#    define CARBINPUT_DEVICETYPE_NAME(a, b)                                                                            \
        case carb::fnv1aHash(b):                                                                                       \
            return (a);
#endif

    switch (carb::hashString(deviceTypeString))
    {
#include "detail/DeviceTypeName.h"
        default:
            return DeviceType::eUnknown;
    }

#undef CARBINPUT_DEVICETYPE_NAME
}

/**
 * Returns a string representation of the keyboard input.
 * @see getKeyboardInputFromString()
 * @param key \ref KeyboardInput
 * @returns A string representation of the keyboard input, or an empty string if unknown.
 */
inline const char* getKeyboardInputString(KeyboardInput key)
{
#ifndef DOXYGEN_SHOULD_SKIP_THIS
#    define CARBINPUT_KEYBOARDINPUT_NAME(a, b)                                                                         \
        case (a):                                                                                                      \
            return (b);
#endif

    switch (key)
    {
#include "detail/KeyboardInputName.h"
        default:
            return "";
    }

#undef CARBINPUT_KEYBOARDINPUT_NAME
}

/**
 * Converts a keyboard input string to a \ref KeyboardInput.
 * @see getKeyboardInputString()
 * @param inputString The string to convert.
 * @returns A \ref KeyboardInput, or \ref KeyboardInput::eUnknown if the string is not known.
 */
inline KeyboardInput getKeyboardInputFromString(const char* inputString)
{
#ifndef DOXYGEN_SHOULD_SKIP_THIS
#    define CARBINPUT_KEYBOARDINPUT_NAME(a, b)                                                                         \
        case carb::fnv1aHash(b):                                                                                       \
            return (a);
#endif

    switch (carb::hashString(inputString))
    {
#include "detail/KeyboardInputName.h"
        default:
            return KeyboardInput::eUnknown;
    }

#undef CARBINPUT_KEYBOARDINPUT_NAME
}

/**
 * Returns a string representation of the keyboard modifier flag.
 * @note Exactly one \ref KeyboardModifierFlags must be specified in \p flag.
 * @see getModifierFlagFromString()
 * @param flag \ref KeyboardModifierFlags
 * @returns A string representation of the keyboard modifier flag, or an empty string if unknown.
 */
inline const char* getModifierFlagString(KeyboardModifierFlags flag)
{
#ifndef DOXYGEN_SHOULD_SKIP_THIS
#    define CARBINPUT_KEYBOARDMODIFIERFLAG_NAME(a, b)                                                                  \
        case (a):                                                                                                      \
            return (b);
#endif

    switch (flag)
    {
#include "detail/KeyboardModifierFlagName.h"
        default:
            return "";
    }

#undef CARBINPUT_KEYBOARDMODIFIERFLAG_NAME
}

/**
 * Converts a keyboard modifier flag string to a \ref KeyboardModifierFlags.
 * @see getModifierFlagString()
 * @param inputString The string to convert.
 * @returns A \ref KeyboardModifierFlags, or `0` if the string is not known.
 */
inline KeyboardModifierFlags getModifierFlagFromString(const char* inputString)
{
#ifndef DOXYGEN_SHOULD_SKIP_THIS
#    define CARBINPUT_KEYBOARDMODIFIERFLAG_NAME(a, b)                                                                  \
        case carb::fnv1aHash(b):                                                                                       \
            return (a);
#endif

    switch (carb::hashString(inputString))
    {
#include "detail/KeyboardModifierFlagName.h"
        default:
            return 0;
    }

#undef CARBINPUT_KEYBOARDMODIFIERFLAG_NAME
}

//! The separator used for device name components.
constexpr char kDeviceNameSeparator[] = "::";
//! The separator used for modifiers.
constexpr char kModifierSeparator[] = " + ";

/**
 * Returns a string of all modifier flags present.
 * @see getModifierFlagsFromString()
 * @param mod Zero or more \ref KeyboardModifierFlags bitwise-or'd together.
 * @returns A string representation of all modifier flags present, joined by \ref kModifierSeparator. If no modifier
 *   flags are present in \p mod, an empty string is returned.
 */
inline std::string getModifierFlagsString(KeyboardModifierFlags mod)
{
    std::string res = "";

    for (const auto& desc : kModifierFlagName)
    {
        const auto& flag = desc.ident;

        if ((mod & flag) != flag)
            continue;

        if (!res.empty())
            res += kModifierSeparator;

        res += desc.name;
    }

    return res;
}

/**
 * Returns \ref KeyboardModifierFlags composed of all the flags from a given string.
 * @see getModifierFlagsString()
 * @param modString A string as returned by \ref getModifierFlagsString().
 * @returns A \ref KeyboardModifierFlags with 0 or more bits set based on @p modString.
 */
inline KeyboardModifierFlags getModifierFlagsFromString(const char* modString)
{
    KeyboardModifierFlags res = KeyboardModifierFlags(0);

    constexpr static carb::cpp::string_view modifierSeparator(kModifierSeparator);

    std::string modifierNameString;
    const char* modifierName = modString;
    while (true)
    {
        const char* modifierNameEnd = strstr(modifierName, modifierSeparator.data());

        if (modifierNameEnd)
        {
            modifierNameString = std::string(modifierName, (std::string::size_type)(modifierNameEnd - modifierName));
        }
        else
        {
            modifierNameString = std::string(modifierName);
        }

        KeyboardModifierFlags mod = getModifierFlagFromString(modifierNameString.c_str());
        if (mod)
        {
            res = (KeyboardModifierFlags)((uint32_t)res | (uint32_t)mod);
        }
        else
        {
            CARB_LOG_VERBOSE("Unknown hotkey modifier encountered: %s in %s", modifierNameString.c_str(), modString);
        }

        if (!modifierNameEnd)
        {
            break;
        }
        modifierName = modifierNameEnd;
        modifierName += modifierSeparator.size();
    }

    return res;
}

/**
 * Returns a string representation of a mouse input enum value.
 * @see getMouseInputFromString()
 * @param key \ref MouseInput
 * @returns A string representation of the mouse input enum, or an empty string if unknown.
 */
inline const char* getMouseInputString(MouseInput key)
{
#ifndef DOXYGEN_SHOULD_SKIP_THIS
#    define CARBINPUT_MOUSEINPUT_NAME(a, b)                                                                            \
        case (a):                                                                                                      \
            return (b);
#endif

    switch (key)
    {
#include "detail/MouseInputName.h"
        default:
            return "";
    }

#undef CARBINPUT_MOUSEINPUT_NAME
}

/**
 * Converts a mouse input string to a \ref MouseInput.
 * @see getMouseInputString()
 * @param inputString The string to convert.
 * @returns A \ref MouseInput, or `MouseInput::eCount` if the string is not known.
 */
inline MouseInput getMouseInputFromString(const char* inputString)
{
#ifndef DOXYGEN_SHOULD_SKIP_THIS
#    define CARBINPUT_MOUSEINPUT_NAME(a, b)                                                                            \
        case carb::fnv1aHash(b):                                                                                       \
            return (a);
#endif

    switch (carb::hashString(inputString))
    {
#include "detail/MouseInputName.h"
        default:
            return MouseInput::eCount;
    }

#undef CARBINPUT_MOUSEINPUT_NAME
}

/**
 * Returns a string representation of a gamepad input enum value.
 * @see getGamepadInputFromString()
 * @param key \ref GamepadInput
 * @returns A string representation of the mouse input enum, or an empty string if unknown.
 */
inline const char* getGamepadInputString(GamepadInput key)
{
#ifndef DOXYGEN_SHOULD_SKIP_THIS
#    define CARBINPUT_GAMEPADINPUT_NAME(a, b)                                                                          \
        case (a):                                                                                                      \
            return (b);
#endif

    switch (key)
    {
#include "detail/GamepadInputName.h"
        default:
            return "";
    }

#undef CARBINPUT_GAMEPADINPUT_NAME
}

/**
 * Converts a gamepad input string to a \ref GamepadInput.
 * @see getGamepadInputString()
 * @param inputString The string to convert.
 * @returns A \ref GamepadInput, or `GamepadInput::eCount` if the string is not known.
 */
inline GamepadInput getGamepadInputFromString(const char* inputString)
{
#ifndef DOXYGEN_SHOULD_SKIP_THIS
#    define CARBINPUT_GAMEPADINPUT_NAME(a, b)                                                                          \
        case carb::fnv1aHash(b):                                                                                       \
            return (a);
#endif

    switch (carb::hashString(inputString))
    {
#include "detail/GamepadInputName.h"
        default:
            return GamepadInput::eCount;
    }

#undef CARBINPUT_GAMEPADINPUT_NAME
}

//! Previous button state.
enum class PreviousButtonState
{
    kUp, //!< Previous button state was "Up".
    kDown //!< Previous button state was "Down".
};

/**
 * Converts a button state to a \ref PreviousButtonState.
 * @param wasDown \c true if the down; \c false if up.
 * @returns a \ref PreviousButtonState conversion of the state.
 */
inline PreviousButtonState toPreviousButtonState(bool wasDown)
{
    return wasDown ? PreviousButtonState::kDown : PreviousButtonState::kUp;
}

//! Current button state.
enum class CurrentButtonState
{
    kUp, //!< Button is currently "Up".
    kDown //!< Button is currently "Down".
};

/**
 * Converts a button state to a \ref CurrentButtonState.
 * @param isDown \c true if the down; \c false if up.
 * @returns a \ref CurrentButtonState conversion of the state.
 */
inline CurrentButtonState toCurrentButtonState(bool isDown)
{
    return isDown ? CurrentButtonState::kDown : CurrentButtonState::kUp;
}

/**
 * Combines the previous and current button states into a \ref ButtonFlags.
 * @param previousButtonState \ref PreviousButtonState
 * @param currentButtonState \ref CurrentButtonState
 * @returns A \ref ButtonFlags representation of the previous and current button state.
 */
inline ButtonFlags toButtonFlags(PreviousButtonState previousButtonState, CurrentButtonState currentButtonState)
{
    ButtonFlags flags = 0;
    if (currentButtonState == CurrentButtonState::kDown)
    {
        flags = kButtonFlagStateDown;
        if (previousButtonState == PreviousButtonState::kUp)
            flags |= kButtonFlagTransitionDown;
    }
    else
    {
        flags = kButtonFlagStateUp;
        if (previousButtonState == PreviousButtonState::kDown)
            flags |= kButtonFlagTransitionUp;
    }
    return flags;
}

/**
 * Returns a device name.
 * @param deviceType \ref DeviceType
 * @param deviceId The identifier of the device.
 * @returns A device name composed of \ref getDeviceTypeString() for \p deviceType, with `[<deviceId>]` appended. If
 *   \p deviceType is not valid, an empty string is returned.
 */
inline std::string getDeviceNameString(DeviceType deviceType, const char* deviceId)
{
    if ((size_t)deviceType >= (size_t)DeviceType::eCount)
        return "";

    std::string result = getDeviceTypeString(deviceType);
    if (deviceId)
    {
        result = carb::extras::join("[", carb::cpp::string_view(carb::cpp::unsafe_length, deviceId), "]");
    }
    return result;
}

/**
 * Separates a device name into a device type and device ID.
 * @param deviceName Name as from \ref getDeviceNameString().
 * @param deviceType Parsed \ref DeviceType from \p deviceName. If not needed, this can be `nullptr`.
 * @param deviceId Parsed device ID from \p deviceName. If not needed, this can be `nullptr`.
 */
inline void parseDeviceNameString(const char* deviceName, DeviceType* deviceType, std::string* deviceId)
{
    if (!deviceName)
    {
        CARB_LOG_WARN("parseDeviceNameString: Empty device name");
        if (deviceType)
        {
            *deviceType = DeviceType::eCount;
        }
        return;
    }

    const char* deviceIdString = strstr(deviceName, "[");
    if (deviceType)
    {
        if (deviceIdString)
        {
            std::string deviceTypeString(deviceName, (std::string::size_type)(deviceIdString - deviceName));
            *deviceType = getDeviceTypeFromString(deviceTypeString.c_str());
        }
        else
        {
            *deviceType = getDeviceTypeFromString(deviceName);
        }
    }

    if (deviceId)
    {
        if (deviceIdString)
        {
            const char* deviceNameEnd = deviceIdString + strlen(deviceIdString);
            *deviceId = std::string(deviceIdString + 1, (std::string::size_type)(deviceNameEnd - deviceIdString - 2));
        }
        else
        {
            *deviceId = "";
        }
    }
}

/**
 * Parses components from a device input string.
 * @note Only one of \p keyboardInputOut, \p mouseInputOut or \p gamepadInputOut will be filled based on the
 *   \ref DeviceType.
 * @param deviceInputString A device input string.
 * @param deviceTypeOut The \ref DeviceType. If `nullptr`, parsing fails and `false` is returned.
 * @param keyboardInputOut (optional) Receives any \ref KeyboardInput parsed from \p deviceInputString.
 * @param mouseInputOut (optional) Receives any \ref MouseInput parsed from \p deviceInputString.
 * @param gamepadInputOut (optional) Receives any \ref GamepadInput parsed from \p deviceInputString.
 * @param deviceIdOut (optional) Receives the device identifier as per \ref parseDeviceNameString().
 * @returns \c true if parsing was successful; \c false if an error occurred.
 */
inline bool getDeviceInputFromString(const char* deviceInputString,
                                     DeviceType* deviceTypeOut,
                                     KeyboardInput* keyboardInputOut,
                                     MouseInput* mouseInputOut,
                                     GamepadInput* gamepadInputOut,
                                     std::string* deviceIdOut = nullptr)
{
    if (!deviceTypeOut)
        return false;

    const char* deviceInputStringTrimmed = deviceInputString;

    // Skip initial spaces
    while (*deviceInputStringTrimmed == ' ')
        ++deviceInputStringTrimmed;

    // Skip device name
    const char* inputNameString = strstr(deviceInputStringTrimmed, kDeviceNameSeparator);

    std::string deviceName;

    // No device name specified - fall back
    if (!inputNameString)
        inputNameString = deviceInputStringTrimmed;
    else
    {
        deviceName =
            std::string(deviceInputStringTrimmed, (std::string::size_type)(inputNameString - deviceInputStringTrimmed));

        constexpr static carb::cpp::string_view deviceNameSeparator(kDeviceNameSeparator);
        inputNameString += deviceNameSeparator.size();
    }

    parseDeviceNameString(deviceName.c_str(), deviceTypeOut, deviceIdOut);

    if ((*deviceTypeOut == DeviceType::eKeyboard) && keyboardInputOut)
    {
        KeyboardInput keyboardInput = getKeyboardInputFromString(inputNameString);
        *keyboardInputOut = keyboardInput;
        return (keyboardInput != KeyboardInput::eCount);
    }

    if ((*deviceTypeOut == DeviceType::eMouse) && mouseInputOut)
    {
        MouseInput mouseInput = getMouseInputFromString(inputNameString);
        *mouseInputOut = mouseInput;
        return (mouseInput != MouseInput::eCount);
    }

    if ((*deviceTypeOut == DeviceType::eGamepad) && gamepadInputOut)
    {
        GamepadInput gamepadInput = getGamepadInputFromString(inputNameString);
        *gamepadInputOut = gamepadInput;
        return (gamepadInput != GamepadInput::eCount);
    }

    return false;
}

/**
 * Translates a hot-key string to a \ref ActionMappingDesc.
 * @see getStringFromActionMappingDesc()
 * @param hotkeyString The hot-key string.
 * @param deviceId (optional) Receives the device identifier.
 * @returns An \ref ActionMappingDesc determined from the \p hotkeyString.
 */
inline ActionMappingDesc getActionMappingDescFromString(const char* hotkeyString, std::string* deviceId)
{
    constexpr static carb::cpp::string_view modifierSeparator(kModifierSeparator);

    ActionMappingDesc actionMappingDesc;
    actionMappingDesc.keyboard = nullptr;
    actionMappingDesc.mouse = nullptr;
    actionMappingDesc.gamepad = nullptr;
    actionMappingDesc.modifiers = (KeyboardModifierFlags)0;

    std::string modifierNameString;
    const char* modifierName = hotkeyString;
    while (true)
    {
        const char* modifierNameEnd = strstr(modifierName, modifierSeparator.data());

        if (modifierNameEnd)
        {
            modifierNameString = std::string(modifierName, (std::string::size_type)(modifierNameEnd - modifierName));
        }
        else
        {
            modifierNameString = std::string(modifierName);
        }

        KeyboardModifierFlags mod = getModifierFlagFromString(modifierNameString.c_str());
        if (mod)
        {
            actionMappingDesc.modifiers = (KeyboardModifierFlags)((uint32_t)actionMappingDesc.modifiers | (uint32_t)mod);
        }
        else
        {
            getDeviceInputFromString(modifierNameString.c_str(), &actionMappingDesc.deviceType,
                                     &actionMappingDesc.keyboardInput, &actionMappingDesc.mouseInput,
                                     &actionMappingDesc.gamepadInput, deviceId);
        }

        if (!modifierNameEnd)
        {
            break;
        }
        modifierName = modifierNameEnd;
        modifierName += modifierSeparator.size();
    }

    return actionMappingDesc;
}

/**
 * Builds a hot-key string from a \ref ActionMappingDesc.
 * @see getActionMappingDescFromString()
 * @param actionMappingDesc The \ref ActionMappingDesc.
 * @param deviceName An optional device name. If not provided, the device type from \p actionMappingDesc is used.
 * @returns A hot-key string.
 */
inline std::string getStringFromActionMappingDesc(const ActionMappingDesc& actionMappingDesc,
                                                  const char* deviceName = nullptr)
{
    std::string result = getModifierFlagsString(actionMappingDesc.modifiers);
    if (!result.empty())
    {
        result.append(kModifierSeparator);
    }

    if (deviceName)
    {
        result.append(deviceName);
    }
    else
    {
        result.append(getDeviceTypeString(actionMappingDesc.deviceType));
    }
    result.append(kDeviceNameSeparator);

    switch (actionMappingDesc.deviceType)
    {
        case DeviceType::eKeyboard:
        {
            result.append(getKeyboardInputString(actionMappingDesc.keyboardInput));
            break;
        }
        case DeviceType::eMouse:
        {
            result.append(getMouseInputString(actionMappingDesc.mouseInput));
            break;
        }
        case DeviceType::eGamepad:
        {
            result.append(getGamepadInputString(actionMappingDesc.gamepadInput));
            break;
        }
        default:
        {
            break;
        }
    }
    return result;
}

/**
 * Adds an action mapping if one does not already exist.
 * @see IInput::getActionMappingCount() IInput::addActionMapping()
 * @param input The \ref IInput interface.
 * @param actionMappingSet The \ref ActionMappingSet to add the default action mapping to.
 * @param actionName The name of the action.
 * @param desc The \ref ActionMappingDesc to set as default.
 * @returns \c true if no action mapping existed and a new one was added; \c false otherwise.
 */
inline bool setDefaultActionMapping(IInput* input,
                                    ActionMappingSetHandle actionMappingSet,
                                    const char* actionName,
                                    const ActionMappingDesc& desc)
{
    size_t actionMappingsCount = input->getActionMappingCount(actionMappingSet, actionName);
    if (actionMappingsCount > 0)
    {
        return false;
    }

    input->addActionMapping(actionMappingSet, actionName, desc);
    return true;
}

/**
 * Subscribes to the keyboard event stream.
 *
 * @param input The \ref IInput interface.
 * @param keyboard A \ref Keyboard handle, or \c nullptr if subscription to events from all keyboards is desired.
 * @param functor An invocable object to be called on each keyboard event. Prototype is `void(const KeyboardEvent&)`.
 * @returns \ref SubscriptionId.
 */
template <typename Functor>
inline SubscriptionId subscribeToKeyboardEvents(IInput* input, Keyboard* keyboard, Functor&& functor)
{
    return input->subscribeToKeyboardEvents(
        keyboard,
        [](const KeyboardEvent& evt, void* userData) -> bool { return (*static_cast<Functor*>(userData))(evt); },
        &functor);
}

/**
 * Subscribes to the mouse event stream.
 *
 * @param input The \ref IInput interface.
 * @param mouse A \ref Mouse handle, or \c nullptr if subscription to events from all mice is desired.
 * @param functor An invocable object to be called on each mouse event. Prototype is `void(const MouseEvent&)`.
 * @return \ref SubscriptionId.
 */
template <typename Functor>
inline SubscriptionId subscribeToMouseEvents(IInput* input, Mouse* mouse, Functor&& functor)
{
    return input->subscribeToMouseEvents(
        mouse, [](const MouseEvent& evt, void* userData) -> bool { return (*static_cast<Functor*>(userData))(evt); },
        &functor);
}

/**
 * Subscribes to the gamepad event stream.
 *
 * @param input The \ref IInput interface.
 * @param gamepad A \ref Gamepad handle, or \c nullptr if subscription to events from all gamepads is desired.
 * @param functor An invocable object to be called on each gamepad event. Prototype is `void(const GamepadEvent&)`.
 * @return \ref SubscriptionId.
 */
template <typename Functor>
inline SubscriptionId subscribeToGamepadEvents(IInput* input, Gamepad* gamepad, Functor&& functor)
{
    return input->subscribeToGamepadEvents(
        gamepad, [](const GamepadEvent& evt, void* userData) -> bool { return (*static_cast<Functor*>(userData))(evt); },
        &functor);
}

/**
 * Subscribes to the gamepad connection event stream.
 *
 * @note Once subscribed \p functor is called for all previously created gamepads.
 *
 * @param input The \ref IInput interface.
 * @param functor An invocable object to be called on each gamepad event. Prototype is
 *   `void(const GamepadConnectionEvent&)`.
 * @return \ref SubscriptionId.
 */
template <typename Functor>
inline SubscriptionId subscribeToGamepadConnectionEvents(IInput* input, Functor&& functor)
{
    return input->subscribeToGamepadConnectionEvents(
        [](const GamepadConnectionEvent& evt, void* userData) { (*static_cast<Functor*>(userData))(evt); }, &functor);
}

/**
 * Subscribes to the action event stream for a specified action.
 *
 * @param input The \ref IInput interface.
 * @param actionMappingSet The \ref ActionMappingSet to receive events for.
 * @param actionName The action name to receive events for.
 * @param functor An invocable object to be called on each event. Prototype is `void(const ActionEvent&)`.
 * @return \ref SubscriptionId.
 */
template <typename Functor>
inline SubscriptionId subscribeToActionEvents(IInput* input,
                                              ActionMappingSetHandle actionMappingSet,
                                              const char* actionName,
                                              Functor&& functor)
{
    return input->subscribeToActionEvents(
        actionMappingSet, actionName,
        [](const ActionEvent& evt, void* userData) -> bool { return (*static_cast<Functor*>(userData))(evt); }, &functor);
}

/**
 * Filter and modify input events in the event buffer.
 *
 * @param input The \ref IInput interface.
 * @param callable An invocable object to be called on each event. Prototype is `void(InputEvent&)`.
 */
template <typename Callable>
inline void filterBufferedEvents(IInput* input, Callable&& callable)
{
    using Func = std::decay_t<Callable>;
    input->filterBufferedEvents(
        [](InputEvent& evt, void* userData) { return (*static_cast<Func*>(userData))(evt); }, &callable);
}


} // namespace input
} // namespace carb
