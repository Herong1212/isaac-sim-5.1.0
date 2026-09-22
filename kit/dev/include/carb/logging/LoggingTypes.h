// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Type definitions for carb.logging
#pragma once

#include <cstddef>

namespace carb
{
namespace logging
{

//! Enumerations of output stream types
enum class OutputStream
{
    eDefault, //!< Default selection, stdout for \ref kLevelWarn and below, stderr for \ref kLevelError and above.
    eStderr, //!< Force all output to stderr.
};

//! Can be used by setFileConfiguration
const char* const kKeepSameFile = (const char*)size_t(-1);

/**
 * Describes the configuration for logging to a file for setFileConfiguration
 *
 * @note Do not rearrange below members as it disrupts @rstref{ABI compatibility <abi-compatibility>}. Add members at
 * the bottom.
 */
struct LogFileConfiguration
{
    /// Size of the struct used for versioning. Adding members to this struct will change the size and therefore act as
    /// a version for the struct.
    size_t size{ sizeof(LogFileConfiguration) };

    /// Indicates whether opening the file should append to it. If false, file is overwritten.
    ///
    /// @note Setting (boolean): "/log/fileAppend"
    /// @note Default = false
    bool append{ false };
};

//! StandardLogger2 output types
enum class OutputType
{
    eFile, //!< Output to log file.
    eDebugConsole, //!< Output to debug console.
    eStandardStream, //!< Output to standard stream (i.e. stdout/stderr).

    eCount //!< Number of OutputTypes
};

} // namespace logging
} // namespace carb
