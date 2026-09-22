// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "omni/graph/core/Handle.h"

namespace omni
{
namespace graph
{

namespace core
{
struct NodeObj;
}

namespace nodes
{

extern void resolveBooleanOpAttributes(const core::NodeObj&,
                                       const core::NameToken aToken,
                                       const core::NameToken bToken,
                                       const core::NameToken resultToken);

extern void resolveBooleanOpDynamicAttributes(const core::NodeObj& node, const core::NameToken resultToken);

} // namespace nodes
} // namespace graph
} // namespace omni
