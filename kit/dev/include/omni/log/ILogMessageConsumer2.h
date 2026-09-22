// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Omni log consumer definitions.
#pragma once

#include "ILog.h"

#include "../../carb/logging/Logger.h"

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 3) || defined(OMNI_BIND)

namespace omni
{
namespace log
{

class ILogMessageConsumer2_abi;
class ILogMessageConsumer2;

//! Consumes (listens for) log messages.
//!
//! @ref omni::log::ILogMessageConsumer2 is usually associated with an @ref omni::log::ILog instance.  Add a consumer
//! to an @ref omni::log::ILog object with @ref omni::log::ILog::addMessageConsumer().
class OMNI_ATTR("no_gil") ILogMessageConsumer2_abi
    : public omni::core::Inherits<ILogMessageConsumer_abi, OMNI_TYPE_ID("omni.log.ILogMessageConsumer2")>
{
protected:
    //! Receives a log message.
    //!
    //! Logging a message from this method results in undefined behavior.
    //!
    //! Accessing the owning @ref omni::log::ILog from this method will lead to undefined behavior.
    //!
    //! The memory pointed to by the provided pointers will remain valid only during the duration of this call.
    //!
    //! @note As ILogMessageConsumer2 inherits from ILogMessageConsumer, both onMessage functions must be implemented,
    //! but the logging subsystem will only call this onMessage signature for ILogMessageConsumer2.
    //!
    //! @thread_safety This method must be thread safe as the attached @ref omni::log::ILog may send messages to this
    //! object in parallel.
    virtual OMNI_ATTR("no_gil") void onMessage_abi(const carb::logging::LogMessage& msg) noexcept = 0;

    // Silence Clang warning about hiding overloaded virtual function
    using ILogMessageConsumer_abi::onMessage_abi;
};

} // namespace log
} // namespace omni

#    define OMNI_BIND_INCLUDE_INTERFACE_DECL
#    include "ILogMessageConsumer2.gen.h"

//! @copydoc omni::log::ILogMessageConsumer2_abi
class omni::log::ILogMessageConsumer2 : public omni::core::Generated<omni::log::ILogMessageConsumer2_abi>
{
};

#    define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#    include "ILogMessageConsumer2.gen.h"

#endif
