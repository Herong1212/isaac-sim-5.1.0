// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnConstantInt4Database.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnConstantInt4
{
public:
    // LCOV_EXCL_START : NodeType has schedule hint 'pure'.
    static size_t computeVectorized(OgnConstantInt4Database&, size_t count)
    {
        return count;
    }
    // LCOV_EXCL_STOP
};

REGISTER_OGN_NODE()

}
}
}
