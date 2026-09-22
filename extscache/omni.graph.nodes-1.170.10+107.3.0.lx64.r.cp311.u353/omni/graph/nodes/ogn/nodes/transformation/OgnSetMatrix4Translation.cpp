// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnSetMatrix4TranslationDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
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
size_t tryComputeAssumingType(OgnSetMatrix4TranslationDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto const& translation, auto& result)
    {
        auto& resultMat = *reinterpret_cast<matrix4d*>(result);
        memcpy(resultMat.data(), input, sizeof(double) * 16);
        resultMat.SetTranslateOnly({ translation[0], translation[1], translation[2] });
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<double[16], double[3], double[16]>(
               db.inputs.matrix(), db.inputs.translation(), db.outputs.matrix(), functor, count) ?
               count :
               0;
}
} // namespace

class OgnSetMatrix4Translation
{
public:
    static size_t computeVectorized(OgnSetMatrix4TranslationDatabase& db, size_t count)
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
        const auto translate = node.iNode->getAttributeByToken(node, inputs::translation.token());
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
