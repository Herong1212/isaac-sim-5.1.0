// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnEndsWithDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>

#include <algorithm>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnEndsWith
{
public:
    static bool computeVectorized(OgnEndsWithDatabase& db, size_t count)
    {
        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                auto const& suffix = db.inputs.suffix(idx);
                auto const& value = db.inputs.value(idx);
                auto iters = std::mismatch(suffix.rbegin(), suffix.rend(), value.rbegin(), value.rend());
                db.outputs.isSuffix(idx) = (iters.first == suffix.rend());
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


REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
