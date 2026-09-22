// SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief Type definitions for *carb.input*.
#pragma once
#include "../Types.h"

namespace carb
{
namespace input
{

//! An opaque type representing an Input Device.
struct InputDevice DOXYGEN_EMPTY_CLASS;
//! An opaque type representing a Keyboard.
struct Keyboard DOXYGEN_EMPTY_CLASS;
//! An opaque type representing a Mouse.
struct Mouse DOXYGEN_EMPTY_CLASS;
//! An opaque type representing a Gamepad.
struct Gamepad DOXYGEN_EMPTY_CLASS;

/**
 * Type used as an identifier for all subscriptions.
 */
typedef uint32_t SubscriptionId;

//! An invalid \ref SubscriptionId with value 0.
constexpr SubscriptionId kInvalidSubscriptionId{};

/**
 * Subscription order.
 *
 * [0..N-1] requires to insert before the position from the beginning and shift tail on the right.
 * [-1..-N] requires to insert after the position relative from the end and shift head on the left.
 *
 * Please look at the examples below:
 *
 * Assume we initially have a queue of N subscribers  a b c .. y z:
 * +---+---+---+-- --+---+---+
 * | a | b | c |     | y | z | -----events--flow--->
 * +---+---+---+-- --+---+---+
 * | 0 | 1 | 2 |     |N-2|N-1| ---positive-order--->
 * +---+---+---+-- --+---+---+
 * | -N|   |   |     | -2| -1| <---negative-order---
 * +---+---+---+-- --+---+---+
 * first                  last
 *
 * After inserting subscriber e with the order 1:
 * +---+---+---+---+-- --+---+---+
 * | a | e | b | c |     | y | z |
 * +---+---+---+---+-- --+---+---+
 * | 0 | 1 | 2 | 3 |     |N-1| N |
 * +---+---+---+---+-- --+---+---+
 * first                      last
 *
 * After inserting subscriber f with the order -1:
 * +---+---+---+---+-- --+---+---+---+
 * | a | e | b | c |     | y | z | f |
 * +---+---+---+---+-- --+---+---+---+
 * | 0 | 1 | 2 | 3 |     |N-1| N |N+1|
 * +---+---+---+---+-- --+---+---+---+
 * | 0 | 1 | 2 | 3 |     |M-3|M-2|M-1|
 * +---+---+---+---+-- --+---+---+---+
 * first                          last
 *
 */
using SubscriptionOrder = int32_t;

//! Represents the 'first' subscription.
static constexpr SubscriptionOrder kSubscriptionOrderFirst = 0;
//! Represents the 'last' subscription.
static constexpr SubscriptionOrder kSubscriptionOrderLast = -1;
//! The 'default' subscription ordering, same as `kSubscriptionOrderLast`.
static constexpr SubscriptionOrder kSubscriptionOrderDefault = kSubscriptionOrderLast;

#ifndef DOXYGEN_BUILD
/**
 * Defines possible input event types.
 * \note This is reserved for future use.
 */
enum class EventType : uint32_t
{
    eUnknown
};
#endif

/**
 * Defines event type mask.
 * \note This is reserved for future use.
 */
typedef uint32_t EventTypeMask;
static constexpr EventTypeMask kEventTypeAll = EventTypeMask(-1); //!< Represents all event types.


/**
 * \defgroup ButtonFlags Button flags.
 * @{
 */
//! Type definition representing button flags.
typedef uint32_t ButtonFlags;
const uint32_t kButtonFlagTransitionUp = 1; //!< Button is transitioning from down to up.
const uint32_t kButtonFlagStateUp = (1 << 1); //!< Button is up.
const uint32_t kButtonFlagTransitionDown = (1 << 2); //!< Button is transitioning from up to down.
const uint32_t kButtonFlagStateDown = (1 << 3); //!< Button is down.
//! @}

/**
 * Defines possible device types.
 */
enum class DeviceType
{
    eKeyboard, //!< Keyboard device type.
    eMouse, //!< Mouse device type.
    eGamepad, //!< Gamepad device type.
    eCount, //!< Number of device types.
    eUnknown = eCount //!< Represents an unknown device.
};

/**
 * \defgroup KeyboardModifiers Defines keyboard modifiers.
 * @{
 */
//! Type definition representing keyboard modifier flags.
typedef uint32_t KeyboardModifierFlags;
const uint32_t kKeyboardModifierFlagShift = 1 << 0; //!< Shift key.
const uint32_t kKeyboardModifierFlagControl = 1 << 1; //!< Control key.
const uint32_t kKeyboardModifierFlagAlt = 1 << 2; //!< Alt key.
const uint32_t kKeyboardModifierFlagSuper = 1 << 3; //!< Super key.
const uint32_t kKeyboardModifierFlagCapsLock = 1 << 4; //!< Caps-lock key.
const uint32_t kKeyboardModifierFlagNumLock = 1 << 5; //!< Num-lock key.
/**
 * Defines total number of keyboard modifiers.
 */
const uint32_t kKeyboardModifierFlagCount = 6;
//! @}

/**
 * Defines keyboard event type.
 */
enum class KeyboardEventType
{
    eKeyPress, //!< Sent when key is pressed the first time.
    eKeyRepeat, //!< Sent after a platform-specific delay if key is held down.
    eKeyRelease, //!< Sent when the key is released.
    eChar, //!< Sent when a character is produced by the input actions, for example during key presses.

    // Must always be last
    eCount //!< The number of KeyboardEventType elements.
};


/**
 * Defines input code type.
 *
 */
typedef uint32_t InputType;

/**
 * Defines keyboard key codes
 *
 * The key code represents the physical key location in the standard US keyboard layout keyboard, if they exist
 * in the US keyboard.
 *
 * eUnknown is sent for key events that do not have a key code.
 */
enum class KeyboardInput : InputType
{
    eUnknown, //!< An unknown key event.
    eSpace,
    eApostrophe,
    eComma,
    eMinus,
    ePeriod,
    eSlash,
    eKey0,
    eKey1,
    eKey2,
    eKey3,
    eKey4,
    eKey5,
    eKey6,
    eKey7,
    eKey8,
    eKey9,
    eSemicolon,
    eEqual,
    eA,
    eB,
    eC,
    eD,
    eE,
    eF,
    eG,
    eH,
    eI,
    eJ,
    eK,
    eL,
    eM,
    eN,
    eO,
    eP,
    eQ,
    eR,
    eS,
    eT,
    eU,
    eV,
    eW,
    eX,
    eY,
    eZ,
    eLeftBracket,
    eBackslash,
    eRightBracket,
    eGraveAccent,
    eEscape,
    eTab,
    eEnter,
    eBackspace,
    eInsert,
    eDel,
    eRight,
    eLeft,
    eDown,
    eUp,
    ePageUp,
    ePageDown,
    eHome,
    eEnd,
    eCapsLock,
    eScrollLock,
    eNumLock,
    ePrintScreen,
    ePause,
    eF1,
    eF2,
    eF3,
    eF4,
    eF5,
    eF6,
    eF7,
    eF8,
    eF9,
    eF10,
    eF11,
    eF12,
    eNumpad0,
    eNumpad1,
    eNumpad2,
    eNumpad3,
    eNumpad4,
    eNumpad5,
    eNumpad6,
    eNumpad7,
    eNumpad8,
    eNumpad9,
    eNumpadDel,
    eNumpadDivide,
    eNumpadMultiply,
    eNumpadSubtract,
    eNumpadAdd,
    eNumpadEnter,
    eNumpadEqual,
    eLeftShift,
    eLeftControl,
    eLeftAlt,
    eLeftSuper,
    eRightShift,
    eRightControl,
    eRightAlt,
    eRightSuper,
    eMenu,

    eCount //!< Number of key entries
};

/**
 * UTF-8 RFC3629 - max 4 bytes per character
 */
const uint32_t kCharacterMaxNumBytes = 4;

/**
 * Defines a keyboard event.
 */
struct KeyboardEvent
{
    union
    {
        //! The \ref Keyboard handle that is sending this event.
        Keyboard* keyboard;
        //! The \ref InputDevice handle that is sending this event.
        InputDevice* device;
    };

    //! The \ref KeyboardEventType for this event.
    KeyboardEventType type;
    union
    {
        //! The \ref KeyboardInput key for this event, when `type` is not \ref KeyboardEventType::eChar.
        KeyboardInput key;
        //! The \ref InputType key for this event, when `type` is not \ref KeyboardEventType::eChar.
        InputType inputType;

        //! The UTF-8 character code, when `type` is \ref KeyboardEventType::eChar.
        char character[kCharacterMaxNumBytes];
    };

    //! The \ref KeyboardModifierFlags flags bitwise-or'd.
    KeyboardModifierFlags modifiers;
};

/**
 * Defines the mouse event types.
 */
enum class MouseEventType
{
    eLeftButtonDown,
    eLeftButtonUp,
    eMiddleButtonDown,
    eMiddleButtonUp,
    eRightButtonDown,
    eRightButtonUp,
    eMove,
    eScroll,

    // Must always be last
    eCount //!< The number of MouseEventType elements.
};

/**
 * Defines the mouse event.
 *
 * normalizedCoords - mouse coordinates only active in move events, normalized to [0.0, 1.0] relative to the
 *   associated window size.
 * unscaledCoords - mouse coordinates only active in move events, not normalized.
 * scrollDelta - scroll delta, only active in scroll events.
 */
struct MouseEvent
{
    union
    {
        //! The \ref Mouse handle that is sending this event.
        Mouse* mouse;
        //! The \ref InputDevice handle that is sending this event.
        InputDevice* device;
    };

    //! The \ref MouseEventType of this event.
    MouseEventType type;
    union
    {
        //! The coordinates, when `type` is not `MouseEventType::eScroll`.
        Float2 normalizedCoords;
        //! The scroll delta, when `type` is `MouseEventType::eScroll`.
        Float2 scrollDelta;
    };
    //! The \ref KeyboardModifierFlags flags  bitwise-or'd.
    KeyboardModifierFlags modifiers;
    //! Pixel coordinates.
    Float2 pixelCoords;
};

/**
 * Defines a mouse input.
 */
enum class MouseInput : InputType
{
    eLeftButton,
    eRightButton,
    eMiddleButton,
    eForwardButton,
    eBackButton,
    eScrollRight,
    eScrollLeft,
    eScrollUp,
    eScrollDown,
    eMoveRight,
    eMoveLeft,
    eMoveUp,
    eMoveDown,

    eCount //!< The number of MouseInput elements.
};

/**
 * Defines a gamepad input.
 *
 * Expected ABXY buttons layout:
 * ```text
 *   Y
 * X   B
 *   A
 * ```
 * eMenu1 - maps to View (XBone) / Share (PS4)
 * eMenu2 - maps to Menu (XBone) / Options (PS4)
 */
enum class GamepadInput : InputType
{
    eLeftStickRight,
    eLeftStickLeft,
    eLeftStickUp,
    eLeftStickDown,
    eRightStickRight,
    eRightStickLeft,
    eRightStickUp,
    eRightStickDown,
    eLeftTrigger,
    eRightTrigger,
    eA,
    eB,
    eX,
    eY,
    eLeftShoulder,
    eRightShoulder,
    eMenu1,
    eMenu2,
    eLeftStick,
    eRightStick,
    eDpadUp,
    eDpadRight,
    eDpadDown,
    eDpadLeft,

    eCount //!< The number of GamepadInput elements.
};

/**
 * Defines a gamepad event.
 */
struct GamepadEvent
{
    union
    {
        //! The \ref Gamepad handle that is sending this event.
        Gamepad* gamepad;
        //! The \ref InputDevice handle that is sending this event.
        InputDevice* device;
    };
    union
    {
        //! The \ref GamepadInput button or axis for this event.
        GamepadInput input;
        //! The \ref InputType button or axis for this event.
        InputType inputType;
    };
    //! The value of the button or axis for this event. Buttons will have either 0.0 or 1.0, whereas axes may have any
    //! value `[0.0, 1.0]`
    float value;
};

/**
 * Defines the gamepad connection event types.
 */
enum class GamepadConnectionEventType
{
    eCreated, //!< A Gamepad handle was created by \ref InputProvider::createGamepad().
    eConnected, //!< A Gamepad was set to connected by \ref InputProvider::setGamepadConnected().
    eDisconnected, //!< A Gamepad was set to disconnected by \ref InputProvider::setGamepadConnected().
    eDestroyed //!< A Gamepad handle was destroyed by \ref InputProvider::destroyGamepad().
};

/**
 * Defines the gamepad connection event.
 */
struct GamepadConnectionEvent
{
    union
    {
        //! The \ref Gamepad handle that is sending this event.
        Gamepad* gamepad;
        //! The \ref InputDevice handle that is sending this event.
        InputDevice* device;
    };
    //! The \ref GamepadConnectionEventType type of connection event.
    GamepadConnectionEventType type;
};

/**
 * Defines the unified input event.
 */
struct InputEvent
{
    //! The \ref DeviceType that dictates which member is valid.
    DeviceType deviceType;
    union
    {
        //! The \ref KeyboardEvent structure that is in use when `deviceType` is \ref DeviceType::eKeyboard.
        KeyboardEvent keyboardEvent;
        //! The \ref MouseEvent structure that is in use when `deviceType` is \ref DeviceType::eMouse.
        MouseEvent mouseEvent;
        //! The \ref GamepadEvent structure that is in use when `deviceType` is \ref DeviceType::eGamepad.
        GamepadEvent gamepadEvent;
        //! The \ref InputDevice handle that is sending the event; corresponds to the `device` member of all of the
        //! event structures.
        InputDevice* device;
    };
};


/**
 * Defines action mapping description.
 */
struct ActionMappingDesc
{
    //! The \ref DeviceType for the action mapping; dictates which members below should be used.
    DeviceType deviceType;
    union
    {
        //! The \ref Keyboard handle for this action mapping, when `deviceType` is \ref DeviceType::eKeyboard.
        Keyboard* keyboard;
        //! The \ref Mouse handle for this action mapping, when `deviceType` is \ref DeviceType::eMouse.
        Mouse* mouse;
        //! The \ref Gamepad handle for this action mapping, when `deviceType` is \ref DeviceType::eGamepad.
        Gamepad* gamepad;
        //! The \ref InputDevice handle for this action mapping.
        InputDevice* device;
    };
    union
    {
        //! The \ref KeyboardInput key for this action mapping, when `deviceType` is \ref DeviceType::eKeyboard.
        KeyboardInput keyboardInput;
        //! The \ref MouseInput button for this action mapping, when `deviceType` is \ref DeviceType::eMouse.
        MouseInput mouseInput;
        //! The \ref GamepadInput button or axis for this action mapping, when `deviceType` is
        //! \ref DeviceType::eGamepad.
        GamepadInput gamepadInput;
        //! The non-enumeration \ref InputType representing the key/button/axis.
        InputType inputType;
    };
    //! \ref KeyboardModifierFlags values bitwise-or'd determining which modifiers are used by this action mapping.
    KeyboardModifierFlags modifiers;
};

/**
 * Defines an action event.
 */
struct ActionEvent
{
    //! The action name.
    const char* action;
    //! The action value.
    float value;
    //! The \ref ButtonFlags for this action event.
    ButtonFlags flags;
};

/**
 * Function type that describes keyboard event callback.
 *
 * @param evt The event description.
 * @param userData Pointer to the user data.
 * @return Whether event should be processed by subsequent event subscribers.
 */
typedef bool (*OnActionEventFn)(const ActionEvent& evt, void* userData);

/**
 * Function type that describes keyboard event callback.
 *
 * @param evt The event description.
 * @param userData Pointer to the user data.
 * @return Whether event should be processed by subsequent event subscribers.
 */
typedef bool (*OnKeyboardEventFn)(const KeyboardEvent& evt, void* userData);

/**
 * Function type that describes mouse event callback.
 *
 * @param evt The event description.
 * @param userData Pointer to the user data.
 * @return Whether event should be processed by subsequent event subscribers.
 */
typedef bool (*OnMouseEventFn)(const MouseEvent& evt, void* userData);

/**
 * Function type that describes gamepad event callback.
 *
 * @param evt The event description.
 * @param userData Pointer to the user data.
 * @return Whether event should be processed by subsequent event subscribers.
 */
typedef bool (*OnGamepadEventFn)(const GamepadEvent& evt, void* userData);

/**
 * Function type that describes gamepad connection event callback.
 *
 * @param evt The event description.
 * @param userData Pointer to the user data.
 * @return Whether event should not be processed anymore by subsequent event subscribers.
 */
typedef void (*OnGamepadConnectionEventFn)(const GamepadConnectionEvent& evt, void* userData);

/**
 * Function type that describes input event callback.
 *
 * @param evt The event description.
 * @param userData Pointer to the user data.
 * @return Whether event should be processed by subsequent event subscribers.
 */
typedef bool (*OnInputEventFn)(const InputEvent& evt, void* userData);

/**
 * The result returned by InputEventFilterFn.
 */
enum class FilterResult : uint8_t
{
    //! The event should be retained and sent later when IInput::distributeBufferedEvents() is called.
    eRetain = 0,

    //! The event has been fully processed by InputEventFilterFn and should NOT be sent later when
    //! IInput::distributeBufferedEvents() is called.
    eConsume = 1,
};

/**
 * Callback function type for filtering events.
 *
 * @see IInput::filterBufferedEvents() for more information.
 *
 * @param evt A reference to the unified event description. The event may be modified.
 * @param userData A pointer to the user data passed to IInput::filterBufferedEvents().
 * @return The FilterResult indicating what should happen with the event.
 */
typedef FilterResult (*InputEventFilterFn)(InputEvent& evt, void* userData);

//! A value that means any available device.
const char* const kAnyDevice = nullptr;

} // namespace input
} // namespace carb
