// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnConstantTargetDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnConstantTarget
{
public:
    // LCOV_EXCL_START : NodeType has schedule hint 'pure'.
    static size_t computeVectorized(OgnConstantTargetDatabase& db, size_t count)
    {
        return count;
    }
    // LCOV_EXCL_STOP
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
