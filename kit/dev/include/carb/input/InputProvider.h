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
//! \brief Definitions for the \ref carb::input::InputProvider sub-interface of \ref carb::input::IInput.
#pragma once
#include "../Defines.h"

#include "InputTypes.h"


namespace carb
{
namespace input
{

/**
 * Defines an input provider interface.
 * This interface is meant to be used only by the input providers. Hence it is in the separate file.
 * The examples of input providers could be windowing system or network input stream.
 */
struct InputProvider
{
    /**
     * Create a logical keyboard.
     *
     * @param name Logical keyboard name.
     * @return The keyboard created.
     */
    Keyboard*(CARB_ABI* createKeyboard)(const char* name);

    /**
     * Destroys the keyboard.
     *
     * This function will wait to return until all references to @p keyboard are released.
     * @param keyboard The logical keyboard.
     */
    void(CARB_ABI* destroyKeyboard)(Keyboard* keyboard);

    /**
     * Input "tick" for specific keyboard. Is meant to be called in the beginning of a new frame, right before sending
     * events. It saves old device state, allowing to differentiate pressed and released state of the buttons. @see
     * ButtonFlags.
     *
     * @param keyboard Logical keyboard to update.
     */
    void(CARB_ABI* updateKeyboard)(Keyboard* keyboard);

    /**
     * Sends keyboard event.
     *
     * @param evt Keyboard event.
     */
    void(CARB_ABI* bufferKeyboardEvent)(const KeyboardEvent& evt);

    /**
     * Create a logical mouse.
     *
     * @param name Logical mouse name.
     * @return The mouse created.
     */
    Mouse*(CARB_ABI* createMouse)(const char* name);

    /**
     * Destroys the mouse.
     *
     * This function will wait to return until all references to @p mouse are released.
     * @param mouse The logical mouse.
     */
    void(CARB_ABI* destroyMouse)(Mouse* mouse);

    /**
     * Input "tick" for specific mouse. Is meant to be called in the beginning of a new frame, right before sending
     * events. It saves old device state, allowing to differentiate pressed and released state of the buttons. @see
     * ButtonFlags.
     *
     * @param mouse Logical mouse to update.
     */
    void(CARB_ABI* updateMouse)(Mouse* mouse);

    /**
     * Sends mouse event.
     *
     * @param evt Mouse event.
     */
    void(CARB_ABI* bufferMouseEvent)(const MouseEvent& evt);

    /**
     * Create a logical gamepad.
     *
     * @param name Logical gamepad name.
     * @param guid Device GUID.
     * @return The gamepad created.
     */
    Gamepad*(CARB_ABI* createGamepad)(const char* name, const char* guid);

    /**
     * Broadcasts a gamepad connected event to all subscribers.
     *
     * Subscribers are registered with \ref IInput::subscribeToGamepadConnectionEvents().
     *
     * @param gamepad The logical gamepad.
     * @param connected Is the gamepad connected?.
     */
    void(CARB_ABI* setGamepadConnected)(Gamepad* gamepad, bool connected);

    /**
     * Destroys the gamepad.
     *
     * This function will wait to return until all references to @p gamepad are released.
     * @param gamepad The logical gamepad.
     */
    void(CARB_ABI* destroyGamepad)(Gamepad* gamepad);

    /**
     * Input "tick" for specific gamepad. Is meant to be called in the beginning of a new frame, right before sending
     * events. It saves old device state, allowing to differentiate pressed and released state of the buttons. @see
     * ButtonFlags.
     *
     * @param gamepad Logical gamepad to update.
     */
    void(CARB_ABI* updateGamepad)(Gamepad* gamepad);

    /**
     * Send gamepad event.
     *
     * @param evt Mouse event.
     */
    void(CARB_ABI* bufferGamepadEvent)(const GamepadEvent& evt);

    /**
     * Sends unified input event.
     *
     * @param evt A reference to unified input event description.
     */
    void(CARB_ABI* bufferInputEvent)(const InputEvent& evt);
};
} // namespace input
} // namespace carb
