// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnMakeTransformLookAtDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnMakeTransformLookAt
{
public:
    static size_t computeVectorized(OgnMakeTransformLookAtDatabase& db, size_t count)
    {
        try
        {
            for (size_t idx = 0; idx < count; idx++)
            {
                const auto& eyeInput = db.inputs.eye(idx);
                const auto& centerInput = db.inputs.center(idx);
                const auto& upInput = db.inputs.up(idx);
                auto& output = db.outputs.transform(idx);
                output.SetLookAt(centerInput, eyeInput, upInput);
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

}
}
}
