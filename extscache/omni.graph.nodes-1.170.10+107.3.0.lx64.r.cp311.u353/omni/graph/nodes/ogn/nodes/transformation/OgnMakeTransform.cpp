// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnMakeTransformDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/matrix.h>

#include "TransformCommon.h"

using omni::math::linalg::matrix4d;
using omni::math::linalg::quatd;

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnMakeTransform
{
public:
    static size_t computeVectorized(OgnMakeTransformDatabase& db, size_t count)
    {
        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto& translation = db.inputs.translation(idx);
                const auto& orientation = db.inputs.rotationXYZ(idx);
                const auto& rotationOrder = db.inputs.rotationOrder(idx);
                const auto& scale = db.inputs.scale(idx);

                const quatd q = omni::math::linalg::eulerAnglesToQuaternion(
                                    GfDegreesToRadians(orientation), getRotationOrder(db, rotationOrder))
                                    .GetNormalized();
                db.outputs.transform(idx) =
                    matrix4d().SetScale(scale) * matrix4d().SetRotate(q) * matrix4d().SetTranslate(translation);
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
