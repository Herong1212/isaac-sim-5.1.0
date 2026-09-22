// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnGetMatrix4RotationMatrixDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/vec.h>

#include "TransformCommon.h"

using omni::math::linalg::matrix3d;
using omni::math::linalg::matrix4d;
using omni::math::linalg::quatd;
using omni::math::linalg::vec3d;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
size_t tryComputeAssumingEuler(OgnGetMatrix4RotationMatrixDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& rotationOrder, auto& output)
    {
        const auto& vector = *reinterpret_cast<const vec3d*>(input);
        auto& rotation = *reinterpret_cast<matrix3d*>(output);
        rotation = matrix3d(
            omni::math::linalg::eulerAnglesToQuaternion(GfDegreesToRadians(vector), rotationOrder).GetNormalized());
    };

    switch (db.inputs.matrix().type().arrayDepth)
    {
    case 0:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<const double[3]>();
            const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
            auto output = db.outputs.rotation(idx).template get<double[9]>();
            if (input && output)
                functor(*input, rotationOrder, *output);
        }
        return count;
    case 1:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<const double[][3]>();
            const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
            auto output = db.outputs.rotation(idx).template get<double[][9]>();
            if (input && output)
            {
                output->resize(input->size());
                for (size_t i = 0; i < input->size(); i++)
                    functor((*input)[i], rotationOrder, (*output)[i]);
            }
        }
        return count;
    default:
        return 0;
    }
}

size_t tryComputeAssumingQuat(OgnGetMatrix4RotationMatrixDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& output)
    {
        const auto& quaternion = *reinterpret_cast<const quatd*>(input);
        auto& rotation = *reinterpret_cast<matrix3d*>(output);
        rotation = matrix3d(quaternion);
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<double[4], double[9]>(
               db.inputs.matrix(), db.outputs.rotation(), functor, count) ?
               count :
               0;
}

size_t tryComputeAssumingMatrix(OgnGetMatrix4RotationMatrixDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& output)
    {
        const auto& matrix = *reinterpret_cast<const matrix4d*>(input);
        auto& rotation = *reinterpret_cast<matrix3d*>(output);
        rotation = matrix.GetOrthonormalized().ExtractRotationMatrix();
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<double[16], double[9]>(
               db.inputs.matrix(), db.outputs.rotation(), functor, count) ?
               count :
               0;
}
}

class OgnGetMatrix4RotationMatrix
{
public:
    static size_t computeVectorized(OgnGetMatrix4RotationMatrixDatabase& db, size_t count)
    {
        try
        {
            const auto& matrixType = db.inputs.matrix().type();
            switch (matrixType.componentCount)
            {
            case 3:
                return tryComputeAssumingEuler(db, count);
            case 4:
                return tryComputeAssumingQuat(db, count);
            case 16:
                return tryComputeAssumingMatrix(db, count);
            // LCOV_EXCL_START
            default:
                throw ogn::compute::InputError("Failed to resolve input types");
                // LCOV_EXCL_STOP
            }
        }
        // LCOV_EXCL_START
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
        // LCOV_EXCL_STOP
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        const auto matrix = node.iNode->getAttributeByToken(node, inputs::matrix.token());
        const auto rotation = node.iNode->getAttributeByToken(node, outputs::rotation.token());

        auto matrixType = matrix.iAttribute->getResolvedType(matrix);

        std::array<AttributeObj, 2> attrs{ matrix, rotation };
        std::array<uint8_t, 2> tupleCounts{ 16, 9 };
        std::array<uint8_t, 2> arrayDepths{ matrixType.arrayDepth, matrixType.arrayDepth };
        std::array<AttributeRole, 2> rolesBuf{ matrixType.role, AttributeRole::eMatrix };
        node.iNode->resolvePartiallyCoupledAttributes(
            node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
    }
};

REGISTER_OGN_NODE()

}
}
}
