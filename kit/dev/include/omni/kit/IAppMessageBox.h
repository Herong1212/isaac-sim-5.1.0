// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Message box interface for omni.kit.app
#pragma once

#include "../../carb/Interface.h"


namespace omni
{
namespace kit
{


//! Message box type.
//! @see IAppMessageBox::show()
enum class MessageBoxType
{
    eInfo, //!< Informational
    eWarning, //!< Warning
    eError, //!< Error
    eQuestion //!< Question
};

//! Buttons to place on the message box.
enum class MessageBoxButtons
{
    eOk, //!< Only an "Ok" button should be presented
    eOkCancel, //!< Both "Ok" and "Cancel" buttons should be presented
    eYesNo //!< Both "Yes" and "No" buttons should be presented
};

//! Message box user response.
enum class MessageBoxResponse
{
    eOk, //!< User pressed "Ok" button
    eCancel, //!< User pressed "Cancel" button
    eYes, //!< User pressed "Yes" button
    eNo, //!< User pressed "No" button
    eNone, //!< User pressed "Ok" button when that was the only choice
    eError //!< An error occurred
};

//! Interface for producing an OS-specific modal message box.
class IAppMessageBox
{
public:
    CARB_PLUGIN_INTERFACE("omni::kit::IAppMessageBox", 1, 1);

    /**
     * Shows an OS specific modal message box.
     *
     * @note This is a blocking call that will return user response to the message box. The thread that calls it will be
     *   blocked until the user presses a button.
     * @param message The message to display
     * @param title The title of the message box
     * @param type The \ref MessageBoxType to display
     * @param buttons The \ref MessageBoxButtons to present
     * @returns A \ref MessageBoxResponse value based on the button that the user pressed, or
     *   \ref MessageBoxResponse::eError if an error occurred.
     */
    virtual MessageBoxResponse show(const char* message,
                                    const char* title,
                                    MessageBoxType type,
                                    MessageBoxButtons buttons) = 0;
};


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                                Inline Functions                                                    //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


} // namespace kit
} // namespace omni
