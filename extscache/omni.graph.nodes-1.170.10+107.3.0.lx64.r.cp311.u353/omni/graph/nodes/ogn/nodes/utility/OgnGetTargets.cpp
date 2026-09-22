// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnGetTargetsDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include "ArrayCommon.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnGetTargets
{
public:
    static size_t computeVectorized(OgnGetTargetsDatabase& db, size_t count)
    {
        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto& targets = db.inputs.targets(idx);
                auto& outTargets = db.outputs.targets(idx);

                if (!targets.empty())
                {
                    const size_t inSize = targets.size();
                    const size_t index = tryWrapIndex(db.inputs.index(idx), inSize);
                    const size_t count = db.inputs.count(idx) < 0 ? inSize : db.inputs.count(idx);
                    const size_t outSize = std::min(count, (inSize - index));
                    outTargets.resize(outSize);
                    std::copy(targets.begin() + index, targets.begin() + index + outSize, outTargets.begin());
                }
                else
                    outTargets.resize(0);
            }
            return count;
        }
        // LCOV_EXCL_START
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
        // LCOV_EXCL_STOP
    }
};


REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
