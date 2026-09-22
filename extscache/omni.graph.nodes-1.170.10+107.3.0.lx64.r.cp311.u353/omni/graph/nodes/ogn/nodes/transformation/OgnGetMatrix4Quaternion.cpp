// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnGetMatrix4QuaternionDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/vec.h>

#include "TransformCommon.h"

using omni::math::linalg::EulerRotationOrder;
using omni::math::linalg::matrix3d;
using omni::math::linalg::matrix4d;
using omni::math::linalg::quat;
using omni::math::linalg::quatd;
using omni::math::linalg::quath;
using omni::math::linalg::vec3;
using omni::math::linalg::vec3h;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T>
void getQuatFromEuler(const T input[3], EulerRotationOrder rotationOrder, T output[4])
{
    const auto& vector = *reinterpret_cast<const vec3<T>*>(input);
    auto& quaternion = *reinterpret_cast<quat<T>*>(output);
    quaternion =
        quat<T>(omni::math::linalg::eulerAnglesToQuaternion(GfDegreesToRadians(vector), rotationOrder).GetNormalized());
}

template <>
void getQuatFromEuler<pxr::GfHalf>(const pxr::GfHalf input[3], EulerRotationOrder rotationOrder, pxr::GfHalf output[4])
{
    const auto& vector = *reinterpret_cast<const vec3h*>(input);
    auto& quaternion = *reinterpret_cast<quath*>(output);
    quaternion =
        quath(omni::math::linalg::eulerAnglesToQuaternion(GfDegreesToRadians(vector), rotationOrder).GetNormalized());
}

template <typename T>
size_t tryComputeAssumingEuler(OgnGetMatrix4QuaternionDatabase& db, size_t count)
{
    switch (db.inputs.matrix().type().arrayDepth)
    {
    case 0:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<const T[3]>();
            const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
            auto output = db.outputs.quaternion(idx).template get<T[4]>();
            if (input && output)
                getQuatFromEuler<T>(*input, rotationOrder, *output);
        }
        return count;
    case 1:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<const T[][3]>();
            const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
            auto output = db.outputs.quaternion(idx).template get<T[][4]>();
            if (input && output)
            {
                output->resize(input->size());
                for (size_t i = 0; i < input->size(); i++)
                    getQuatFromEuler<T>((*input)[i], rotationOrder, (*output)[i]);
            }
        }
        return count;
    default:
        return 0;
    }
}

template <typename T, size_t N>
size_t tryComputeAssumingMatrix(OgnGetMatrix4QuaternionDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& output)
    {
        const auto& matrix = *reinterpret_cast<const T*>(input);
        auto& quaternion = *reinterpret_cast<quatd*>(output);
        quaternion = matrix.GetOrthonormalized().ExtractRotation();
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<double[N * N], double[4]>(
               db.inputs.matrix(), db.outputs.quaternion(), functor, count) ?
               count :
               0;
}

}

class OgnGetMatrix4Quaternion
{
public:
    static size_t computeVectorized(OgnGetMatrix4QuaternionDatabase& db, size_t count)
    {
        try
        {
            const auto& matrixType = db.inputs.matrix().type();
            switch (matrixType.baseType)
            {
            case BaseDataType::eDouble:
                switch (matrixType.componentCount)
                {
                case 3:
                    return tryComputeAssumingEuler<double>(db, count);
                case 9:
                    return tryComputeAssumingMatrix<matrix3d, 3>(db, count);
                case 16:
                    return tryComputeAssumingMatrix<matrix4d, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eFloat:
                switch (matrixType.componentCount)
                {
                case 3:
                    return tryComputeAssumingEuler<float>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eHalf:
                switch (matrixType.componentCount)
                {
                case 3:
                    return tryComputeAssumingEuler<pxr::GfHalf>(db, count);
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
        const auto quaternion = node.iNode->getAttributeByToken(node, outputs::quaternion.token());

        auto matrixType = matrix.iAttribute->getResolvedType(matrix);

        std::array<AttributeObj, 2> attrs{ matrix, quaternion };
        std::array<uint8_t, 2> tupleCounts{ matrixType.componentCount, 4 };
        std::array<uint8_t, 2> arrayDepths{ matrixType.arrayDepth, matrixType.arrayDepth };
        std::array<AttributeRole, 2> rolesBuf{ matrixType.role, AttributeRole::eQuaternion };
        node.iNode->resolvePartiallyCoupledAttributes(
            node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
    }
};

REGISTER_OGN_NODE()

}
}
}
