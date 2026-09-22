// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnSetMatrix4ScaleDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>

using omni::math::linalg::matrix3d;
using omni::math::linalg::matrix4d;
using omni::math::linalg::vec3d;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T, size_t N>
size_t tryComputeAssumingType(OgnSetMatrix4ScaleDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto const& scale, auto& result)
    {
        const auto& scaleVec = *reinterpret_cast<const vec3d*>(scale);
        auto& resultMat = *reinterpret_cast<T*>(result);
        memcpy(resultMat.data(), input, sizeof(double) * (N * N));
        resultMat[0][0] = scaleVec[0];
        resultMat[1][1] = scaleVec[1];
        resultMat[2][2] = scaleVec[2];
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<double[N * N], double[3], double[N * N]>(
               db.inputs.matrix(), db.inputs.scale(), db.outputs.matrix(), functor, count) ?
               count :
               0;
}
} // namespace

class OgnSetMatrix4Scale
{
public:
    static size_t computeVectorized(OgnSetMatrix4ScaleDatabase& db, size_t count)
    {
        try
        {
            const auto& matrixType = db.inputs.matrix().type();
            switch (matrixType.componentCount)
            {
            case 9:
                return tryComputeAssumingType<matrix3d, 3>(db, count);
            case 16:
                return tryComputeAssumingType<matrix4d, 4>(db, count);
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
        const auto translate = node.iNode->getAttributeByToken(node, inputs::scale.token());
        const auto result = node.iNode->getAttributeByToken(node, outputs::matrix.token());

        auto matrixType = matrix.iAttribute->getResolvedType(matrix);
        auto translateType = translate.iAttribute->getResolvedType(translate);

        // Require matrix, quaternion, and condition to be resolved before determining result's type
        if (matrixType.baseType != BaseDataType::eUnknown && translateType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 3> attrs{ matrix, translate, result };
            std::array<uint8_t, 3> tupleCounts{ matrixType.componentCount, translateType.componentCount,
                                                matrixType.componentCount };
            std::array<uint8_t, 3> arrayDepths{ matrixType.arrayDepth, translateType.arrayDepth,
                                                std::max(matrixType.arrayDepth, translateType.arrayDepth) };
            std::array<AttributeRole, 3> rolesBuf{ matrixType.role, translateType.role, AttributeRole::eUnknown };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

}
}
}
