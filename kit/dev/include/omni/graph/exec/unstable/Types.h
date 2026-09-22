// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Types.h
//!
//! @brief Defines typedefs used by interfaces.
//!
//! Because interface bindings are inlined and sometimes coupled, you sometimes need to break out typedefs into their
//! own file so that you can get the include order correct in interface .h files.
#pragma once

#include <omni/graph/exec/unstable/EnumBitops.h>

#include <cstdint>
#include <limits>

namespace omni
{
namespace graph
{

//! Omniverse Execution Framework (EF)
//!
//! Namespace for the Execution Framework.
//!
//! See @rstref{Execution Framework Overview <ef_framework>} for to begin learning about the Execution Framework.
//!
//! The Execution Framework has no dependencies on OmniGraph and is designed to be front-end agnostic. It could very
//! much live in its own namespace, but we decided to make it part of @ref omni::graph namespace. There is no useful
//! runtime without an authoring front-end and we consider OmniGraph as the front-end to runtime execution. EF sits at
//! the backend, orchestrating execution of computation defined by one or many front-ends.
namespace exec
{

//! Unstable features currently in development.  Do not depend on any API or ABI in this namespace, as it will change
//! without notice.
namespace unstable
{

//! Each node in an @ref ITopology is given a unique index (via @ref ITopology::acquireNodeIndex()).
using NodeIndexInTopology = uint64_t;

//! Type which store a unique identifier for a node or definition.
using NameHash = uint64_t;

//! Hash of each node's topology index in a path.
using ExecutionPathHash = uint64_t;

//! Key for a piece of data attached to a node.
using NodeDataKey = uint64_t;

//! Pass priority used by @ref IPassPipeline to resolve conflicts between passes.
//!
//! See @ref  groupOmniGraphExecPasses for more pass related functionality.
using PassPriority = uint32_t;

//! Constant to denote an @ref INode has not been assigned an index in an @ref ITopology.
constexpr const uint64_t kInvalidNodeIndexInTopology = std::numeric_limits<uint64_t>::max();
static_assert(std::numeric_limits<uint64_t>::max() == 0xFFFFFFFFFFFFFFFF, "unexpected uin64_t max value");

//! Grouping type for different passes.
//!
//! Graph transformation pass is registered with a given type and type can't be changed after.
//!
//! See @ref  groupOmniGraphExecPasses for more pass related functionality.
//!
//! @note   We are not yet using all these states...expect changes.
//!
//! @ingroup groupOmniGraphExecPassRegistration
enum class PassType
{
    ePopulate, //!< open-up graph types
    ePartitioning, //!< change granularity of executions (including executors)
    eGlobal, //!< pass is running over entire graph. no other passes can run now
    eTypeInference, //!< resolve types
    eOverrideExecution, //!< override compute methods, executors, etc
    eScheduling, //!< memory access, pipeline stages, etc
    eCount //!< total number of known pass types
};

//! Current execution status of pass pipeline a @ref omni::graph::exec::unstable::IPassPipeline.
//!
//! See @ref  groupOmniGraphExecPasses for more pass related functionality.
enum class PassPipelineStatus : uint32_t
{
    eNone = 0, //!< Pipeline is not executing.
    eExecuting = 1 << 0, //!< Pipeline is running
    eTopologyChangesAllowed = 1 << 1, //!< Pipeline is allowing mutating changes to topology
};

//! Enable bitwise operations on PassPipelineStatus state.
template <>
struct EnumBitops<PassPipelineStatus> : EnumBitops<>::allow_bitops
{
};

//! Result of waiting for the result of a @ref omni::graph::exec::unstable::IBackgroundResult.
enum class BackgroundResultStatus
{
    eReady, //!< The result is ready.
    eTimeout, //!< The result did not become ready int he specified wait time.
};

//! Type specific function for deleting context specific execution data associated with a node.
//!
//! The function is expected to know the type given as the first arg and handle the deletion of the type in an
//! appropriate manner.  Usually, this means casting the `void*` pointer to the proper type and calling `delete`.
using NodeDataDeleterFn = void(void*);

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
