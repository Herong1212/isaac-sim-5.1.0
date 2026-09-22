// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IInvalidationForwarder.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IInvalidationForwarder.
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

class IInvalidationForwarder_abi;
class IInvalidationForwarder;
class ITopology;

//! Interface wrapping a function (possibly with storage) to forward topology invalidation notices.
//!
//! This interface is used by @ref omni::graph::exec::unstable::ITopology::addInvalidationForwarder(). Manual
//! instantiation of this interface can be avoided by simply calling @ref
//! omni::graph::exec::unstable::ITopology::addInvalidationForwarder() which will wrap the given invocable object in an
//! instance of this interface.
//!
//! See @rstref{Graph Invalidation <ef_graph_invalidation>} for details about how this interface is used during
//! invalidation.
//!
//! @thread_safety This callback may be invoked concurrently across multiple threads.
class IInvalidationForwarder_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                  OMNI_TYPE_ID("omni.graph.exec.unstable.IInvalidationForwarder")>
{
protected:
    //! Invokes the wrapped function.
    //!
    //! The given topology must not be @c nullptr.
    //!
    //! @thread_safety This method may be called concurrently across multiple threads.
    virtual void invoke_abi(OMNI_ATTR("not_null") ITopology* topology) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IInvalidationForwarder.
using InvalidationForwarderPtr = omni::core::ObjectPtr<IInvalidationForwarder>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IInvalidationForwarder.gen.h>

//! @copydoc omni::graph::exec::unstable::IInvalidationForwarder_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IInvalidationForwarder
    : public omni::core::Generated<omni::graph::exec::unstable::IInvalidationForwarder_abi>
{
};

#include <omni/graph/exec/unstable/ITopology.h>

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IInvalidationForwarder.gen.h>
