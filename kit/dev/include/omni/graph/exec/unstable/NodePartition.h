// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file NodePartition.h
//!
//! @brief Defines omni::graph::exec::unstable::NodePartition.
#pragma once

#include <omni/graph/exec/unstable/Span.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations
class INode;

//! Type definition used to pass node partitions in the ABI.
using NodePartition = omni::graph::exec::unstable::Span<INode* const>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
