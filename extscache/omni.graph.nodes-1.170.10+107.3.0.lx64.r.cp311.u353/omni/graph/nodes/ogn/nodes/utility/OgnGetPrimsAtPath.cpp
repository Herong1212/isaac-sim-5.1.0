// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnGetPrimsAtPathDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnGetPrimsAtPath
{
public:
    static bool computeVectorized(OgnGetPrimsAtPathDatabase& db, size_t count)
    {
        if (db.inputs.path().type().arrayDepth > 0)
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                auto& outPrims = db.outputs.prims(idx);
                const auto paths = *db.inputs.path(idx).template get<OgnToken[]>();
                outPrims.resize(paths.size());
                std::transform(paths.begin(), paths.end(), outPrims.begin(),
                               [&](const auto& p) {
                                   return (p != omni::fabric::kUninitializedToken) ? db.tokenToPath(p) :
                                                                                     omni::fabric::kUninitializedPath;
                               });
            }
        }
        else
        {
            const auto pathPtr = db.inputs.path().template get<OgnToken>();
            if (pathPtr)
            {
                auto path = pathPtr.vectorized(count);
                auto oldPath = db.state.path.vectorized(count);

                for (size_t idx = 0; idx < count; ++idx)
                {
                    auto outPrims = db.outputs.prims(idx);
                    if (oldPath[idx] != path[idx])
                    {
                        if (path[idx] != omni::fabric::kUninitializedToken)
                        {
                            outPrims.resize(1);
                            outPrims[0] = db.tokenToPath(path[idx]);
                        }
                        else
                        {
                            outPrims.resize(0);
                        }
                    }
                }
            }
        }
        return count;
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
