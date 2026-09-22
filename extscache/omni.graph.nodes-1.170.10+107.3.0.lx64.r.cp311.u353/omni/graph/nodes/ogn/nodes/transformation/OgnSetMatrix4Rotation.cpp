// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnSetMatrix4RotationDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/vec.h>

#include <cmath>

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

const vec3d getAxis(OgnSetMatrix4RotationDatabase& db, size_t idx)
{
    std::unordered_map<NameToken, vec3d> axes = { { omni::fabric::kUninitializedToken, vec3d::YAxis() },
                                                  { OgnSetMatrix4RotationDatabase::tokens.X, vec3d::XAxis() },
                                                  { OgnSetMatrix4RotationDatabase::tokens.Y, vec3d::YAxis() },
                                                  { OgnSetMatrix4RotationDatabase::tokens.Z, vec3d::ZAxis() },
                                                  { OgnSetMatrix4RotationDatabase::tokens.Custom,
                                                    vec3d(db.inputs.rotationAxis(idx)) } };
    if (auto search = axes.find(db.inputs.fixedRotationAxis(idx)); search != axes.end())
        return search->second;
    else
        throw ogn::compute::InputError("fixedRotationAxis must be one of X, Y, Z or Custom.");
}

size_t tryComputeAssumingAxis(OgnSetMatrix4RotationDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto const& angle, auto const& axis, auto& output)
    {
        auto& matrix = *reinterpret_cast<matrix4d*>(output);
        memcpy(matrix.data(), input, sizeof(double) * 16);

        // 0.5 is because quaternions cover the space of rotations twice
        double c = std::cos(0.5f * GfDegreesToRadians(angle));
        double s = std::sin(0.5f * GfDegreesToRadians(angle));
        matrix.SetRotateOnly(quatd(c, s * axis.GetNormalized()));
    };

    const auto& matrixType = db.inputs.matrix().type();
    const auto& rotType = db.inputs.rotationAngle().type();
    switch (matrixType.arrayDepth)
    {
    case 0:
        switch (rotType.arrayDepth)
        {
        case 0:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto matrix = db.inputs.matrix(idx).template get<const double[16]>();
                const auto rotationAngle = db.inputs.rotationAngle().template get<const double>();
                const auto axis = getAxis(db, idx);
                auto output = db.outputs.matrix(idx).template get<double[16]>();
                functor(*matrix, *rotationAngle, axis, *output);
            }
            return count;
        case 1:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto matrix = db.inputs.matrix(idx).template get<const double[16]>();
                const auto rotationAngles = db.inputs.rotationAngle().template get<const double[]>();
                const auto axis = getAxis(db, idx);
                auto output = db.outputs.matrix(idx).template get<double[][16]>();
                output->resize(rotationAngles->size());
                for (size_t i = 0; i < rotationAngles.size(); i++)
                    functor(*matrix, (*rotationAngles)[i], axis, (*output)[i]);
            }
            return count;
        // LCOV_EXCL_START
        default:
            throw ogn::compute::InputError("Failed to resolve input types");
            // LCOV_EXCL_STOP
        }
    case 1:
        switch (rotType.arrayDepth)
        {
        case 0:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto matrices = db.inputs.matrix(idx).template get<const double[][16]>();
                const auto rotationAngle = db.inputs.rotationAngle(idx).template get<const double>();
                const auto axis = getAxis(db, idx);
                auto output = db.outputs.matrix(idx).template get<double[][16]>();
                output->resize(matrices->size());
                for (size_t i = 0; i < matrices.size(); i++)
                    functor((*matrices)[i], *rotationAngle, axis, (*output)[i]);
            }
            return count;
        case 1:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto matrices = db.inputs.matrix(idx).template get<const double[][16]>();
                const auto rotationAngles = db.inputs.rotationAngle(idx).template get<const double[]>();
                const auto axis = getAxis(db, idx);

                if (matrices.size() != rotationAngles.size())
                    throw ogn::compute::InputError(
                        "Unable to broadcast arrays of differing lengths: " + std::to_string(matrices.size()) +
                        "!=" + std::to_string(rotationAngles.size()));

                auto output = db.outputs.matrix(idx).template get<double[][16]>();
                output->resize(matrices->size());
                for (size_t i = 0; i < matrices.size(); i++)
                    functor((*matrices)[i], (*rotationAngles)[i], axis, (*output)[i]);
            }
            return count;
        // LCOV_EXCL_START
        default:
            throw ogn::compute::InputError("Failed to resolve input types");
            // LCOV_EXCL_STOP
        }
    // LCOV_EXCL_START
    default:
        throw ogn::compute::InputError("Failed to resolve input types");
        // LCOV_EXCL_STOP
    }
    return 0;
}

size_t tryComputeAssumingEuler(OgnSetMatrix4RotationDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto const& rotation, auto& rotationOrder, auto& output)
    {
        const auto& vector = *reinterpret_cast<const vec3d*>(rotation);
        auto& matrix = *reinterpret_cast<matrix4d*>(output);
        memcpy(matrix.data(), input, sizeof(double) * 16);
        matrix.SetRotateOnly(
            omni::math::linalg::eulerAnglesToQuaternion(GfDegreesToRadians(vector), rotationOrder).GetNormalized());
    };

    const auto& matrixType = db.inputs.matrix().type();
    const auto& rotType = db.inputs.rotationAngle().type();
    switch (matrixType.arrayDepth)
    {
    case 0:
        switch (rotType.arrayDepth)
        {
        case 0:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto matrix = db.inputs.matrix(idx).template get<const double[16]>();
                const auto rotationAngle = db.inputs.rotationAngle(idx).template get<const double[3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
                auto output = db.outputs.matrix(idx).template get<double[16]>();
                functor(*matrix, *rotationAngle, rotationOrder, *output);
            }
            return count;
        case 1:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto matrix = db.inputs.matrix(idx).template get<const double[16]>();
                const auto rotationAngles = db.inputs.rotationAngle(idx).template get<const double[][3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
                auto output = db.outputs.matrix(idx).template get<double[][16]>();
                output->resize(rotationAngles->size());
                for (size_t i = 0; i < rotationAngles.size(); i++)
                    functor(*matrix, (*rotationAngles)[i], rotationOrder, (*output)[i]);
            }
            return count;
        // LCOV_EXCL_START
        default:
            throw ogn::compute::InputError("Failed to resolve input types");
            // LCOV_EXCL_STOP
        }
    case 1:
        switch (rotType.arrayDepth)
        {
        case 0:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto matrices = db.inputs.matrix(idx).template get<const double[][16]>();
                const auto rotationAngle = db.inputs.rotationAngle(idx).template get<const double[3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
                auto output = db.outputs.matrix(idx).template get<double[][16]>();
                output->resize(matrices->size());
                for (size_t i = 0; i < matrices.size(); i++)
                    functor((*matrices)[i], *rotationAngle, rotationOrder, (*output)[i]);
            }
            return count;
        case 1:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto matrices = db.inputs.matrix(idx).template get<const double[][16]>();
                const auto rotationAngles = db.inputs.rotationAngle(idx).template get<const double[][3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));

                if (matrices.size() != rotationAngles.size())
                    throw ogn::compute::InputError(
                        "Unable to broadcast arrays of differing lengths: " + std::to_string(matrices.size()) +
                        "!=" + std::to_string(rotationAngles.size()));

                auto output = db.outputs.matrix(idx).template get<double[][16]>();
                output->resize(matrices->size());
                for (size_t i = 0; i < matrices.size(); i++)
                    functor((*matrices)[i], (*rotationAngles)[i], rotationOrder, (*output)[i]);
            }
            return count;
        // LCOV_EXCL_START
        default:
            throw ogn::compute::InputError("Failed to resolve input types");
            // LCOV_EXCL_STOP
        }
    // LCOV_EXCL_START
    default:
        throw ogn::compute::InputError("Failed to resolve input types");
        // LCOV_EXCL_STOP
    }
    return 0;
}

size_t tryComputeAssumingQuat(OgnSetMatrix4RotationDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto const& quaternion, auto& output)
    {
        auto& matrix = *reinterpret_cast<matrix4d*>(output);
        memcpy(matrix.data(), input, sizeof(double) * 16);
        matrix.SetRotateOnly(quatd(quaternion[3], quaternion[0], quaternion[1], quaternion[2]));
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<double[16], double[4], double[16]>(
               db.inputs.matrix(), db.inputs.rotationAngle(), db.outputs.matrix(), functor, count) ?
               count :
               0;
}

size_t tryComputeAssumingMatrix(OgnSetMatrix4RotationDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto const& rotation, auto& output)
    {
        const auto& rotMatrix = *reinterpret_cast<const matrix3d*>(rotation);
        auto& matrix = *reinterpret_cast<matrix4d*>(output);
        memcpy(matrix.data(), input, sizeof(double) * 16);
        matrix.SetRotateOnly(rotMatrix);
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<double[16], double[9], double[16]>(
               db.inputs.matrix(), db.inputs.rotationAngle(), db.outputs.matrix(), functor, count) ?
               count :
               0;
}

} // namespace

class OgnSetMatrix4Rotation
{
public:
    static size_t computeVectorized(OgnSetMatrix4RotationDatabase& db, size_t count)
    {
        try
        {
            const auto& rotType = db.inputs.rotationAngle().type();
            switch (rotType.componentCount)
            {
            case 1:
                return tryComputeAssumingAxis(db, count);
            case 3:
                return tryComputeAssumingEuler(db, count);
            case 4:
                return tryComputeAssumingQuat(db, count);
            case 9:
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
        const auto rotAngle = node.iNode->getAttributeByToken(node, inputs::rotationAngle.token());
        const auto result = node.iNode->getAttributeByToken(node, outputs::matrix.token());

        auto matrixType = matrix.iAttribute->getResolvedType(matrix);
        auto rotAngleType = rotAngle.iAttribute->getResolvedType(rotAngle);

        // Require matrix, quaternion, and condition to be resolved before determining result's type
        if (matrixType.baseType != BaseDataType::eUnknown && rotAngleType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 3> attrs{ matrix, rotAngle, result };
            std::array<uint8_t, 3> tupleCounts{ matrixType.componentCount, rotAngleType.componentCount,
                                                matrixType.componentCount };
            std::array<uint8_t, 3> arrayDepths{ matrixType.arrayDepth, rotAngleType.arrayDepth,
                                                std::max(matrixType.arrayDepth, rotAngleType.arrayDepth) };
            std::array<AttributeRole, 3> rolesBuf{ matrixType.role, rotAngleType.role, AttributeRole::eUnknown };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

}
}
}
