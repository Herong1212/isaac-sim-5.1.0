// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnGetMatrix4ScaleDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/vec.h>

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
size_t tryComputeAssumingType(OgnGetMatrix4ScaleDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& output)
    {
        const auto& matrix = *reinterpret_cast<const T*>(input);
        output[0] = vec3d(matrix[0][0], matrix[0][1], matrix[0][2]).GetLength();
        output[1] = vec3d(matrix[1][0], matrix[1][1], matrix[1][2]).GetLength();
        output[2] = vec3d(matrix[2][0], matrix[2][1], matrix[2][2]).GetLength();
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<double[N * N], double[3]>(
               db.inputs.matrix(), db.outputs.scale(), functor, count) ?
               count :
               0;
}
}

class OgnGetMatrix4Scale
{
public:
    static size_t computeVectorized(OgnGetMatrix4ScaleDatabase& db, size_t count)
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
        const auto scale = node.iNode->getAttributeByToken(node, outputs::scale.token());

        auto matrixType = matrix.iAttribute->getResolvedType(matrix);

        std::array<AttributeObj, 2> attrs{ matrix, scale };
        std::array<uint8_t, 2> tupleCounts{ matrixType.componentCount, 3 };
        std::array<uint8_t, 2> arrayDepths{ matrixType.arrayDepth, matrixType.arrayDepth };
        std::array<AttributeRole, 2> rolesBuf{ matrixType.role, AttributeRole::eVector };
        node.iNode->resolvePartiallyCoupledAttributes(
            node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
    }
};

REGISTER_OGN_NODE()

}
}
}
