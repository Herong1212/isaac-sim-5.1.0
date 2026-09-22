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
//! @brief Interface definition for IRunLoopRunner for *omni.kit.app*
#pragma once
#include "../../carb/IObject.h"
#include "../../carb/Interface.h"


namespace omni
{

namespace kit
{

class RunLoop;

/**
 * Interface to implement by custom run loop runners.
 *
 * \ref IApp calls the functions on this interface if one was set with \ref IApp::setRunLoopRunner().
 */
class IRunLoopRunner : public carb::IObject
{
public:
    /**
     * Called once before starting application update.
     *
     * This is called by \ref IApp::startup(), and is called **after** the initial Run Loop notifications are given via
     * \ref onAddRunLoop().
     * @warning This function is **not** called by \ref IApp::setRunLoopRunner().
     */
    virtual void startup() = 0;

    /**
     * Called each time a new run loop is created.
     *
     * This function can be called both prior to startup() (by \ref IApp::startup()), and whenever a new Run Loop is
     * created by \ref IApp::getRunLoop().
     *
     * @thread_safety May be called from different threads simultaneously.
     * @param name The run loop name; will not be `nullptr`
     * @param loop The \ref RunLoop instance being added
     */
    virtual void onAddRunLoop(const char* name, RunLoop* loop) = 0;

    /**
     * Called when IApp wants to remove a run loop.
     *
     * @param name The name of the run loop; will not be `nullptr`
     * @param loop The \ref RunLoop instance, owned by \ref IApp
     * @param block if `true`, this function should not return until the Run Loop has completed
     */
    virtual void onRemoveRunLoop(const char* name, RunLoop* loop, bool block) = 0;

    /**
     * Called by each application update.
     *
     * Called by \ref IApp::update() before any work is done.
     */
    virtual void update() = 0;

    /**
     * Called to notify of shut down.
     * @warning This function is only called on the previous instance when \ref IApp::setRunLoopRunner() is called to
     *   switch to a different \ref IRunLoopRunner instance (or `nullptr`).
     */
    virtual void shutdown() = 0;
};

//! RAII pointer type for \ref IRunLoopRunner
using IRunLoopRunnerPtr = carb::ObjectPtr<IRunLoopRunner>;


} // namespace kit
} // namespace omni
