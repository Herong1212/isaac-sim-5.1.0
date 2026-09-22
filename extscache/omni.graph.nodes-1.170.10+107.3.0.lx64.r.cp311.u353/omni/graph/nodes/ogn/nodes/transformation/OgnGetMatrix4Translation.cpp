// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnGetMatrix4TranslationDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/vec.h>
#include <omni/math/linalg/matrix.h>

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
size_t tryComputeAssumingType(OgnGetMatrix4TranslationDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& output)
    {
        const auto& matrix = *reinterpret_cast<const matrix4d*>(input);
        auto& translation = *reinterpret_cast<vec3d*>(output);
        translation = matrix.ExtractTranslation();
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<double[16], double[3]>(
               db.inputs.matrix(), db.outputs.translation(), functor, count) ?
               count :
               0;
}
}

class OgnGetMatrix4Translation
{
public:
    static size_t computeVectorized(OgnGetMatrix4TranslationDatabase& db, size_t count)
    {
        try
        {
            const auto& matrixType = db.inputs.matrix().type();
            switch (matrixType.componentCount)
            {
            case 16:
                return tryComputeAssumingType(db, count);
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
        const auto translation = node.iNode->getAttributeByToken(node, outputs::translation.token());

        auto matrixType = matrix.iAttribute->getResolvedType(matrix);

        std::array<AttributeObj, 2> attrs{ matrix, translation };
        std::array<uint8_t, 2> tupleCounts{ 16, 3 };
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
