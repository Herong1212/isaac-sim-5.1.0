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
//! @brief Provides a base class for a filter for log channel patterns.
#pragma once

#include "../core/IObject.h"
#include "../str/IReadOnlyCString.h"
#include "ILog.h"
#include "../extras/OutArrayUtils.h"

namespace omni
{
//! Namespace for logging functionality.
namespace log
{

class ILogChannelFilter_abi;
class ILogChannelFilter;
//! Read-only object to encapsulate a channel filter's pattern and effects.
//!
//! A channel filter is a pattern matcher.  If a channel's name matches the pattern, the filter can set both the
//! channel's enabled flag and/or level.
class OMNI_ATTR("no_gil") ILogChannelFilter_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.log.ILogChannelFilter")>
{
protected:
    //! Returns the channels pattern.  The returned memory is valid for the lifetime of this object.
    //!
    //! This method is thread safe.
    virtual OMNI_ATTR("c_str, not_null") const char* getFilter_abi() noexcept = 0;

    //! Returns the desired enabled state for this filter.
    //!
    //! All parameters must not be nullptr.
    //!
    //! If `isUsed` is false after calling this method, `isEnabled` and `behavior` should not be used.
    //!
    //! This method is thread safe.
    virtual OMNI_ATTR("no_gil") void getEnabled_abi(OMNI_ATTR("out, not_null") bool* isEnabled,
                                                    OMNI_ATTR("out, not_null") SettingBehavior* behavior,
                                                    OMNI_ATTR("out, not_null") bool* isUsed) noexcept = 0;

    //! Returns the desired level for this filter.
    //!
    //! All parameters must not be nullptr.
    //!
    //! If `isUsed` is false after calling this method, `level` and `behavior` should not be used.
    //!
    //! This method is thread safe.
    virtual OMNI_ATTR("no_gil") void getLevel_abi(OMNI_ATTR("out, not_null") Level* level,
                                                  OMNI_ATTR("out, not_null") SettingBehavior* behavior,
                                                  OMNI_ATTR("out, not_null") bool* isUsed) noexcept = 0;

    //! Given a channel name, returns if the channel name matches the filter's pattern.
    //!
    //! The matching algorithm used is implementation specific (e.g. regex, glob, etc).
    //!
    //! This method is thread safe.
    virtual OMNI_ATTR("no_gil") bool isMatch_abi(OMNI_ATTR("c_str, not_null") const char* channel) noexcept = 0;
};

} // namespace log
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "ILogChannelFilter.gen.h"

//! \copydoc omni::log::ILogChannelFilter_abi
class omni::log::ILogChannelFilter : public omni::core::Generated<omni::log::ILogChannelFilter_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "ILogChannelFilter.gen.h"
