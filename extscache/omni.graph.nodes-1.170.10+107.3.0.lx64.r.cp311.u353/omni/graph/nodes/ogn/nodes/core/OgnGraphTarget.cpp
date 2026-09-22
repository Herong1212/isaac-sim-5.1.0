// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <OgnGraphTargetDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnGraphTarget
{
public:
    static size_t computeVectorized(OgnGraphTargetDatabase& db, size_t count)
    {
        auto targets = db.getGraphTargets(count);
        auto paths = db.outputs.primPath.vectorized(count);
        memcpy(paths.data(), targets.data(), count * sizeof(NameToken));
        return count;
    }
};

REGISTER_OGN_NODE()
}
}
}
