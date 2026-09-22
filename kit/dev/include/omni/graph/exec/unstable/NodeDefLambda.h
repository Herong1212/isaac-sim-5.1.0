// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file NodeDefLambda.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::NodeDefLambda.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/NodeDef.h>

#include <functional>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Wrapper of a lambda function into an opaque node definition.
//!
//! This class is great for quick prototyping and nodes that won't be statically analyzed. It is recommended to convert
//! such nodes into real classes to avoid paying the price of std::function call from already virtual method and to
//! provide type information.
//!
//! See @rstref{Execution Concepts <ef_execution_concepts>} for an in-depth guide on how definitions are used during
//! execution.
//!
//! @thread_safety Since definitions can be shared by multiple nodes, and nodes can be executed in parallel,
//! implementations of this interface should expect its methods to be called in parallel.
// ef-docs node-def-lambda-begin
class NodeDefLambda : public NodeDef
{
public:
    //! Templated constructor for wrapper class
    //!
    //! The given definition name must not be @c nullptr.
    //!
    //! The given invokable object myst not be @c nullptr.
    //!
    //! The returned object will not be @c nullptr.
    //!
    //! @tparam Fn Invokable type (e.g. function, functor, lambda, etc) with the signature `Status(ExecutionTask&)`.
    //!
    //! @param definitionName Definition name is considered as a token that transformation passes can register against.
    //!
    //! @param fn Execute function body. Signature should be `Status(ExecutionTask&)`.
    //!
    //! @param schedInfo Fixed at runtime scheduling constraint.
    template <typename Fn>
    static omni::core::ObjectPtr<NodeDefLambda> create(const carb::cpp::string_view& definitionName,
                                                       Fn&& fn,
                                                       SchedulingInfo schedInfo) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(definitionName.data());
        return omni::core::steal(new NodeDefLambda(definitionName, std::forward<Fn>(fn), schedInfo));
    }

protected:
    //! Templated and protected constructor for wrapper class.
    //!
    //! Use the `create` factory method to construct objects of this class.
    template <typename Fn>
    NodeDefLambda(const carb::cpp::string_view& definitionName, Fn&& fn, SchedulingInfo schedInfo) noexcept
        : NodeDef(definitionName), m_fn(std::move(fn)), m_schedulingInfo(schedInfo)
    {
    }

    //! @copydoc omni::graph::exec::unstable::IDef::execute_abi
    Status execute_abi(ExecutionTask* info) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(info);
        return m_fn(*info);
    }

    //! @copydoc omni::graph::exec::unstable::IDef::getSchedulingInfo_abi
    SchedulingInfo getSchedulingInfo_abi(const ExecutionTask* info) noexcept override
    {
        return m_schedulingInfo;
    }

private:
    std::function<Status(ExecutionTask&)> m_fn; //!< Execute function body
    SchedulingInfo m_schedulingInfo; //!< Scheduling constraint
};
// ef-docs node-def-lambda-end

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
