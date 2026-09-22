// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IExecutionContext.h
//!
//! @brief Defines @ref omni::kit::exec::core::unstable::IExecutionContext.
#pragma once

#include <omni/graph/exec/unstable/IExecutionContext.h>

namespace omni
{
namespace kit
{

struct StageUpdateSettings;

namespace exec
{
namespace core
{
namespace unstable
{

//! ABI-safe struct containing time information for graph execution.
struct ExecutionContextTime
{
    double currentTime; //!< Current execution time (within application timeline)
    double absoluteSimTime; //!< Absolute simulation time (from start of simulation)
    float elapsedSecs; //!< Time elapsed since last execution
    bool timeChanged; //!< Is this execution triggered by a time change
    char _padding; //!< Padding
    char _padding1; //!< Padding
    char _padding2; //!< Padding
};

#ifndef DOXYGEN_BUILD // macros called in namespaces seem to upset doxygen
OMNI_STATIC_ASSERT_CAN_BE_PASSED_BY_VALUE_IN_ABI(ExecutionContextTime);
static_assert(CARB_OFFSETOF2(ExecutionContextTime, currentTime) == 0, "unexpected offset");
static_assert(CARB_OFFSETOF2(ExecutionContextTime, absoluteSimTime) == 8, "unexpected offset");
static_assert(CARB_OFFSETOF2(ExecutionContextTime, elapsedSecs) == 16, "unexpected offset");
static_assert(CARB_OFFSETOF2(ExecutionContextTime, timeChanged) == 20, "unexpected offset");
static_assert(24 == sizeof(ExecutionContextTime), "unexpected size");
#endif

// forward declarations needed by interface declaration
class IExecutionContext;
class IExecutionContext_abi;

//! @ref omni::kit::exec::core::unstable::IExecutionContext inherits all of the functionality of @ref
//! omni::graph::exec::unstable::IExecutionContext but adds information related to Kit.
class IExecutionContext_abi : public omni::core::Inherits<omni::graph::exec::unstable::IExecutionContext,
                                                          OMNI_TYPE_ID("omni.kit.exec.core.unstable.IExecutionContext")>
{
protected:
    //! Returns Kit's timing parameters for the current execution.
    //!
    //! Always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null") const ExecutionContextTime* getTime_abi() noexcept = 0;

    //! Returns Kit's update settings for the current execution.
    //!
    //! Always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null") const omni::kit::StageUpdateSettings* getUpdateSettings_abi() noexcept = 0;
};

} // namespace unstable
} // namespace core
} // namespace exec
} // namespace kit
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "IExecutionContext.gen.h"

#include <omni/graph/exec/unstable/ExecutionPath.h>
#include <omni/graph/exec/unstable/INode.h>
#include <omni/graph/exec/unstable/Status.h>

//! @copydoc omni::kit::exec::core::unstable::IExecutionContext_abi
class omni::kit::exec::core::unstable::IExecutionContext
    : public omni::core::Generated<omni::kit::exec::core::unstable::IExecutionContext_abi>
{
private:
    using omni::graph::exec::unstable::IExecutionContext::execute;
    using omni::graph::exec::unstable::IExecutionContext::executeNode;

    //! Hide and reimplement this public API method to prevent omni::kit::exec::core::unstable::IExecutionContext
    //! objects from directly calling it; prefer using the ExecutionController class for controlling evaluation at the
    //! kit integration level.
    omni::graph::exec::unstable::Status execute() noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(false);
        return omni::graph::exec::unstable::Status::eFailure;
    }

    //! Hide and reimplement this public API method to prevent omni::kit::exec::core::unstable::IExecutionContext
    //! objects from directly calling it; prefer using the ExecutionController class for controlling evaluation at the
    //! kit integration level.
    omni::graph::exec::unstable::Status execute(const omni::graph::exec::unstable::ExecutionPath& path,
                                                omni::core::ObjectParam<omni::graph::exec::unstable::INode> node) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(false);
        return omni::graph::exec::unstable::Status::eFailure;
    }

    //! Hide and reimplement this public API method to prevent omni::kit::exec::core::unstable::IExecutionContext
    //! objects from directly calling it; prefer using the ExecutionController class for controlling evaluation at the
    //! kit integration level.
    omni::graph::exec::unstable::Status executeNode(const omni::graph::exec::unstable::ExecutionPath& upstreamPath,
                                                    omni::core::ObjectParam<omni::graph::exec::unstable::INode> node) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(false);
        return omni::graph::exec::unstable::Status::eFailure;
    }
};

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "IExecutionContext.gen.h"
