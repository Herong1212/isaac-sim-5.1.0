// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file INodeGraphDefDebug.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::INodeGraphDefDebug.
#pragma once

#include <omni/graph/exec/unstable/IBase.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class INodeGraphDefDebug;
class INodeGraphDefDebug_abi;

//! Interface containing debugging methods for @ref omni::graph::exec::unstable::INodeGraphDef.
//!
//! Implementation of this interface is optional.
class INodeGraphDefDebug_abi : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                                           OMNI_TYPE_ID("omni.graph.exec.unstable.INodeGraphDefDebug")>
{
protected:
    //! Returns the current execution count.  A value of 0 means the graph is not executing.
    //!
    //! @thread_safety This method is thread safe.
    virtual uint64_t getExecutionCount_abi() noexcept = 0;

    //! Increments the execution count.
    //!
    //! Prefer using @ref omni::graph::exec::unstable::ScopedExecutionDebug rather than directly calling this method.
    //!
    //! @thread_safety This method is thread safe.
    virtual void incrementExecutionCount_abi() noexcept = 0;

    //! Decrements the execution count.
    //!
    //! Prefer using @ref omni::graph::exec::unstable::ScopedExecutionDebug rather than directly calling this method.
    //!
    //! The caller must not decrement the execution count below zero.
    //!
    //! @thread_safety This method is thread safe.
    virtual void decrementExecutionCount_abi() noexcept = 0;
};

//! Smart pointer managing an instance of @ref INodeGraphDefDebug.
using NodeGraphDefDebugPtr = omni::core::ObjectPtr<INodeGraphDefDebug>;

class ScopedExecutionDebug;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/INodeGraphDefDebug.gen.h>

//! @copydoc omni::graph::exec::unstable::INodeGraphDefDebug_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::INodeGraphDefDebug
    : public omni::core::Generated<omni::graph::exec::unstable::INodeGraphDefDebug_abi>
{
public:
    //! Returns @c true if the graph's execution count is greater than 0.
    inline bool isExecuting() noexcept
    {
        return (getExecutionCount() > 0);
    }
};

//! Scoped object used mark that a given @ref INodeGraphDef is currently executing.
//!
//! Since @ref INodeGraphDef objects can be shared across nodes, it is safe to create multiple instances of this object
//! with the same @ref INodeGraphDef.
class omni::graph::exec::unstable::ScopedExecutionDebug
{
public:
    //! Marks the given @ref INodeGraphDef as executing.
    //!
    //! The given graph definition may be @c nullptr.
    ScopedExecutionDebug(omni::core::ObjectParam<IBase> nodeGraphDef)
        : m_nodeGraphDef(omni::graph::exec::unstable::cast<INodeGraphDefDebug>(nodeGraphDef))
    {
        if (m_nodeGraphDef)
        {
            m_nodeGraphDef->incrementExecutionCount();
        }
    }

    //! Decrements the given @ref INodeGraphDef's execution tracker.
    ~ScopedExecutionDebug()
    {
        if (m_nodeGraphDef)
        {
            m_nodeGraphDef->decrementExecutionCount();
        }
    }

private:
    INodeGraphDefDebug* m_nodeGraphDef;
};

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/INodeGraphDefDebug.gen.h>
