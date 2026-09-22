// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnBreakMatrix2Database.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/vec.h>

using omni::math::linalg::matrix2;
using omni::math::linalg::vec2;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T>
size_t tryComputeAssumingType(OgnBreakMatrix2Database& db, size_t count)
{
    auto functor = [](auto const& input, auto& xOut, auto& yOut)
    {
        const auto& matrix = *reinterpret_cast<const matrix2<T>*>(input);
        auto& x = *reinterpret_cast<vec2<T>*>(xOut);
        auto& y = *reinterpret_cast<vec2<T>*>(yOut);
        x = matrix.GetRow(0);
        y = matrix.GetRow(1);
    };

    switch (db.inputs.matrix().type().arrayDepth)
    {
    case 0:
    {
        const auto input = db.inputs.matrix().template get<T[4]>();
        auto xOut = db.outputs.x().template get<T[2]>();
        auto yOut = db.outputs.y().template get<T[2]>();
        if (input && xOut && yOut)
        {
            const auto inputVec = input.vectorized(count);
            const auto xOutVec = xOut.vectorized(count);
            const auto yOutVec = yOut.vectorized(count);
            if (!inputVec.empty() && !xOutVec.empty() && !yOutVec.empty())
            {
                for (size_t idx = 0; idx < count; idx++)
                    functor(inputVec[idx], xOutVec[idx], yOutVec[idx]);
            }
        }
        return count;
    }
    case 1:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<T[][4]>();
            auto xOut = db.outputs.x(idx).template get<T[][2]>();
            auto yOut = db.outputs.y(idx).template get<T[][2]>();
            if (input && xOut && yOut)
            {
                xOut->resize(input->size());
                yOut->resize(input->size());
                for (size_t i = 0; i < input->size(); i++)
                    functor((*input)[i], (*xOut)[i], (*yOut)[i]);
            }
        }
        return count;
    // LCOV_EXCL_START
    default:
        throw ogn::compute::InputError("Failed to resolve input types");
        // LCOV_EXCL_STOP
    }
}
} // namespace

class OgnBreakMatrix2
{
public:
    static size_t computeVectorized(OgnBreakMatrix2Database& db, size_t count)
    {
        try
        {
            const auto& inputType = db.inputs.matrix().type();
            switch (inputType.baseType)
            {
            case BaseDataType::eDouble:
                return tryComputeAssumingType<double>(db, count);
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

    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
        auto matrix = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::matrix.token());
        auto x = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::x.token());
        auto y = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::y.token());

        auto matrixType = matrix.iAttribute->getResolvedType(matrix);

        // Require inputs to be resolved before determining outputs' type
        if (matrixType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 3> attrs{ matrix, x, y };
            std::array<uint8_t, 3> tuples{ 4, 2, 2 };
            std::array<uint8_t, 3> arrays{ matrixType.arrayDepth, matrixType.arrayDepth, matrixType.arrayDepth };
            std::array<AttributeRole, 3> roles{ matrixType.role, AttributeRole::eNone, AttributeRole::eNone };
            nodeObj.iNode->resolvePartiallyCoupledAttributes(
                nodeObj, attrs.data(), tuples.data(), arrays.data(), roles.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE();

}
}
}
