// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnStartsWithDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>

#include <algorithm>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnStartsWith
{
public:
    static size_t computeVectorized(OgnStartsWithDatabase& db, size_t count)
    {
        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                auto const& prefix = db.inputs.prefix(idx);
                auto const& value = db.inputs.value(idx);
                auto iters = std::mismatch(prefix.begin(), prefix.end(), value.begin(), value.end());
                db.outputs.isPrefix(idx) = (iters.first == prefix.end());
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
