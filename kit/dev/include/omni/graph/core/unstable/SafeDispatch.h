// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file SafeDispatch.h
//!
//! @brief Declares a helper for OmniGraph types to run with serial initial frame. Also adds support for debugging
//!        options.
#pragma once

#include <omni/graph/exec/unstable/Executor.h>
#include <omni/kit/exec/core/unstable/IExecutionContext.h>
#include <omni/kit/exec/core/unstable/IExecutionGraphSettings.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

//! Class used to control globally how things should dispatch within OmniGraph
struct SafeDispatch
{
    //! Method called by executor to determine scheduling info
    static exec::unstable::SchedulingInfo getSchedulingInfo(const omni::graph::exec::unstable::ExecutionTask& task)
    {
        if (kit::exec::core::unstable::getExecutionGraphSettings()->shouldForceSerial())
            return exec::unstable::SchedulingInfo::eSchedulerBypass;
        else if (getNeedsIsolation(task))
            return exec::unstable::SchedulingInfo::eIsolate;
        else if (kit::exec::core::unstable::getExecutionGraphSettings()->shouldForceParallel())
            return graph::exec::unstable::SchedulingInfo::eParallel;
        else
            return graph::exec::unstable::DefaultSchedulingStrategy::getSchedulingInfo(task);
    }

    //! Is task forced to execute in isolation. Currently used to stabilize the graph before parallel execution.
    static bool getNeedsIsolation(const omni::graph::exec::unstable::ExecutionTask& task)
    {
        auto* context = exec::unstable::cast<kit::exec::core::unstable::IExecutionContext>(task.getContext());
        auto* nodeState = context->getStateInfo(task);

        const bool alreadyComputed = nodeState->getExecutionStamp().isValid();
        nodeState->setExecutionStamp(context->getExecutionStamp());

        return !alreadyComputed;
    }
};

} // namespace unstable
} // namespace core
} // namespace graph
} // namespace omni
