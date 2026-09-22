// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnConstantPrimsDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnConstantPrims
{
public:
    static size_t computeVectorized(OgnConstantPrimsDatabase& db, size_t count)
    {
        return count;
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
