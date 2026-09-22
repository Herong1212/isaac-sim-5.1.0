// SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief carb.logging StandardLogger definitions
#pragma once

#include "Logger.h"
#include "StandardLogger2.h"

namespace carb
{
namespace logging
{

/**
 * The default logger provided by the Framework. It is quite flexible and you can use multiple
 * instances if you want different configurations for different output destinations. It can
 * also be safely called from multiple threads.
 *
 * @see ILogging::getDefaultLogger
 * @see ILogging::createStandardLogger
 * @see ILogging::destroyStandardLogger
 */
#if CARB_PLATFORM_WINDOWS && !defined(DOXYGEN_BUILD) && CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 1)
struct CARB_DEPRECATED("Use StandardLogger2 instead") StandardLogger : public Logger
#else // Linux is very warning-heavy about [[deprecated]]
struct StandardLogger : public Logger
#endif
{
    //! \copydoc StandardLogger2::setFilenameIncluded
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`. May not be
    //! `nullptr`.
    void(CARB_ABI* setFilenameIncluded)(StandardLogger* instance, bool included);

    //! \copydoc StandardLogger2::setLineNumberIncluded
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setLineNumberIncluded)(StandardLogger* instance, bool included);

    //! \copydoc StandardLogger2::setFunctionNameIncluded
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setFunctionNameIncluded)(StandardLogger* instance, bool included);

    //! \copydoc StandardLogger2::setTimestampIncluded
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setTimestampIncluded)(StandardLogger* instance, bool included);

    //! \copydoc StandardLogger2::setThreadIdIncluded
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setThreadIdIncluded)(StandardLogger* instance, bool included);

    //! \copydoc StandardLogger2::setSourceIncluded
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setSourceIncluded)(StandardLogger* instance, bool included);

    //! \copydoc StandardLogger2::setStandardStreamOutput
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setStandardStreamOutput)(StandardLogger* instance, bool enabled);

    //! \copydoc StandardLogger2::setDebugConsoleOutput
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setDebugConsoleOutput)(StandardLogger* instance, bool enabled);

    //! \copydoc StandardLogger2::setFileOutput
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setFileOutput)(StandardLogger* instance, const char* filePath);

    //! \copydoc StandardLogger2::setFileOuputFlushLevel
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setFileOuputFlushLevel)(StandardLogger* instance, int32_t level);

    //! \copydoc StandardLogger2::setFlushStandardStreamOutput
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setFlushStandardStreamOutput)(StandardLogger* instance, bool enabled);

    //! \copydoc StandardLogger2::setElapsedTimeUnits
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setElapsedTimeUnits)(StandardLogger* instance, const char* units);

    //! \copydoc StandardLogger2::setProcessIdIncluded
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setProcessIdIncluded)(StandardLogger* instance, bool enabled);

    //! \copydoc StandardLogger2::setMultiProcessGroupId
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setMultiProcessGroupId)(StandardLogger* instance, int32_t id);

    //! \copydoc StandardLogger2::setColorOutputIncluded
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setColorOutputIncluded)(StandardLogger* instance, bool enabled);

    //! \copydoc StandardLogger2::setOutputStream
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setOutputStream)(StandardLogger* instance, OutputStream outputStream);

    //! \copydoc StandardLogger2::setStandardStreamOutputLevelThreshold
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setStandardStreamOutputLevelThreshold)(StandardLogger* instance, int32_t level);

    //! \copydoc StandardLogger2::setDebugConsoleOutputLevelThreshold
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setDebugConsoleOutputLevelThreshold)(StandardLogger* instance, int32_t level);

    //! \copydoc StandardLogger2::setFileOutputLevelThreshold
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setFileOutputLevelThreshold)(StandardLogger* instance, int32_t level);

    //! \copydoc StandardLogger2::setFileConfiguration
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setFileConfiguration)(StandardLogger* instance,
                                         const char* filePath,
                                         const LogFileConfiguration* config);

    //! \copydoc StandardLogger2::getFileConfiguration
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    size_t(CARB_ABI* getFileConfiguration)(StandardLogger* instance,
                                           char* buffer,
                                           size_t bufferSize,
                                           LogFileConfiguration* config);

    //! \copydoc StandardLogger2::pauseFileLogging
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* pauseFileLogging)(StandardLogger* instance);

    //! \copydoc StandardLogger2::resumeFileLogging
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* resumeFileLogging)(StandardLogger* instance);

    //! \copydoc StandardLogger2::setForceAnsiColor
    //! \param instance The instance of the StandardLogger interface being used. May not be `nullptr`.
    void(CARB_ABI* setForceAnsiColor)(StandardLogger* instance, bool forceAnsiColor);

    // NOTE: This interface, because it is inherited from, is CLOSED and may not have any additional functions added
    // without an ILogging major version increase. See StandardLogger2 for adding additional functionality.
};

} // namespace logging
} // namespace carb
