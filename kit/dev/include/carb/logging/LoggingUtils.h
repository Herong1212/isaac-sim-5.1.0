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
//! @brief Utilities for carb.logging
#pragma once

#include "Log.h"

#if CARB_ASSERT_ENABLED
#    include "../thread/Util.h"
#endif

namespace carb
{
namespace logging
{

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 1)
/**
 * A class that pauses logging to a file when constructed and resumes logging to a file when destroyed.
 */
class ScopedFilePause
{
public:
    /**
     * RAII Constructor.
     *
     * @param inst The StandardLogger to pause file logging for.
     */
    CARB_DEPRECATED("Use StandardLogger2 instead")
    ScopedFilePause(StandardLogger* inst) : ScopedFilePause(g_carbLogging->getStandardLogger2(inst))
    {
    }

    /**
     * RAII Constructor.
     *
     * @param inst The \ref StandardLogger2 to pause file logging for.
     */
    ScopedFilePause(StandardLogger2* inst) : m_inst(inst)
    {
        if (m_inst)
        {
            m_inst->addRef();
            m_inst->pauseFileLogging();
        }
    }

    /**
     * RAII Destructor.
     *
     * Restarts file logging on the StandardLogger that was given to the constructor.
     */
    ~ScopedFilePause()
    {
        if (m_inst)
        {
            m_inst->resumeFileLogging();
            m_inst->release();
        }
    }

    CARB_PREVENT_COPY_AND_MOVE(ScopedFilePause);

private:
    StandardLogger2* m_inst;
};
#else
class ScopedFilePause
{
public:
    ScopedFilePause(StandardLogger* inst) : m_inst(inst)
    {
        if (m_inst)
        {
            m_inst->pauseFileLogging(m_inst);
        }
    }
    ~ScopedFilePause()
    {
        if (m_inst)
        {
            m_inst->resumeFileLogging(m_inst);
        }
    }

    CARB_PREVENT_COPY_AND_MOVE(ScopedFilePause);

private:
    StandardLogger* m_inst;
};
#endif

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 1)
/**
 * A RAII object for overriding a thread's log level for a given type in \ref StandardLogger while in scope.
 *
 * When this object is constructed, \ref StandardLogger2::setLevelThresholdThreadOverride() is called as long as the
 * given logger object is not `nullptr`. Upon destruction, \ref StandardLogger2::clearLevelThresholdThreadOverride() is
 * called.
 */
class ScopedLevelThreadOverride
{
public:
    /**
     * Converting constructor for StandardLogger.
     * @warning It is not recommended to use this from within a \a carb.tasking task across context switches.
     * @param logger The \ref StandardLogger instance to override. If `nullptr` no action is taken.
     * @param type The \ref OutputType to override.
     * @param level The overriding \ref loglevel.
     */
    CARB_DEPRECATED("Use StandardLogger2 instead")
    ScopedLevelThreadOverride(StandardLogger* logger, OutputType type, int32_t level)
        : ScopedLevelThreadOverride(g_carbLogging->getStandardLogger2(logger), type, level)
    {
    }

    /**
     * Constructor for overriding a log level for the calling thread.
     * @warning It is not recommended to use this from within a \a carb.tasking task across context switches.
     * @param logger The \ref StandardLogger2 instance to override. If `nullptr` no action is taken.
     * @param type The \ref OutputType to override.
     * @param level The overriding \ref loglevel.
     */
    ScopedLevelThreadOverride(StandardLogger2* logger, OutputType type, int32_t level)
        : m_logger(logger),
          m_type(type)
#    if CARB_ASSERT_ENABLED
          ,
          m_threadId(carb::this_thread::getId())
#    endif
    {
        if (m_logger)
        {
            m_logger->addRef();
            m_logger->setLevelThresholdThreadOverride(m_type, level);
        }
    }

    /**
     * Destructor which clears the override for the current thread.
     */
    ~ScopedLevelThreadOverride()
    {
        // Make sure we are on the same thread
        CARB_ASSERT(m_threadId == carb::this_thread::getId());
        if (m_logger)
        {
            m_logger->clearLevelThresholdThreadOverride(m_type);
            m_logger->release();
        }
    }

    CARB_PREVENT_COPY_AND_MOVE(ScopedLevelThreadOverride);

private:
    StandardLogger2* m_logger;
    OutputType m_type;
#    if CARB_ASSERT_ENABLED
    thread::ThreadId m_threadId;
#    endif
};
#endif

} // namespace logging
} // namespace carb
