// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IPass.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IPass.
#pragma once

#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/Types.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class IPass;
class IPass_abi;

//! @defgroup  groupOmniGraphExecPasses Passes
//!
//! @brief Interfaces, classes, and helpers related to graph transformation passes.
//!
//! Passes are user definable objects that populate, transform, and optimize the execution graph.
//!
//! Passes are registered using one of the @ref groupOmniGraphExecPassRegistration helpers.
//!
//! Passes are run during graph construction via a @ref omni::graph::exec::unstable::PassPipeline.
//!
//! See @rstref{Pass Concepts <ef_pass_concepts>} for an in-depth guide on how passes are used during graph
//! construction.

//! Base class for graph transformation passes.
//!
//! See @rstref{Pass Concepts <ef_pass_concepts>} for an in-depth guide on how passes are used during graph
//! construction.
//!
//! See @ref  groupOmniGraphExecPasses for more pass related functionality.
class IPass_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.exec.unstable.IPass")>
{
};

//! Smart pointer managing an instance of @ref omni::graph::exec::unstable::IPass.
using PassPtr = omni::core::ObjectPtr<IPass>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IPass.gen.h>

//! @copydoc omni::graph::exec::unstable::IPass_abi
//!
//! @ingroup  groupOmniGraphExecPasses groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IPass : public omni::core::Generated<omni::graph::exec::unstable::IPass_abi>
{
};

// additional headers needed for API implementation

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IPass.gen.h>
