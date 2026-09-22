// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnGetGraphTargetIdDatabase.h>

namespace omni::graph::nodes
{

class OgnGetGraphTargetId
{
public:
    static size_t computeVectorized(OgnGetGraphTargetIdDatabase& db, size_t count)
    {
        auto targets = db.getGraphTargets(count);
        auto targetId = db.outputs.targetId.vectorized(count);
        std::transform(
            targets.begin(), targets.end(), targetId.begin(), [](auto const& t) { return omni::fabric::hash(t); });
        return count;
    }
};

REGISTER_OGN_NODE()
}
