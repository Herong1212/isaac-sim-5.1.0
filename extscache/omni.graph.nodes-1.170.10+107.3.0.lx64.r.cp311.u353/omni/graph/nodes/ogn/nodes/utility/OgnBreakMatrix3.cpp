// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnBreakMatrix3Database.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/vec.h>

using omni::math::linalg::matrix3;
using omni::math::linalg::vec3;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T>
size_t tryComputeAssumingType(OgnBreakMatrix3Database& db, size_t count)
{
    auto functor = [](auto const& input, auto& xOut, auto& yOut, auto& zOut)
    {
        const auto& matrix = *reinterpret_cast<const matrix3<T>*>(input);
        auto& x = *reinterpret_cast<vec3<T>*>(xOut);
        auto& y = *reinterpret_cast<vec3<T>*>(yOut);
        auto& z = *reinterpret_cast<vec3<T>*>(zOut);
        x = matrix.GetRow(0);
        y = matrix.GetRow(1);
        z = matrix.GetRow(2);
    };

    switch (db.inputs.matrix().type().arrayDepth)
    {
    case 0:
    {
        const auto input = db.inputs.matrix().template get<T[9]>();
        auto xOut = db.outputs.x().template get<T[3]>();
        auto yOut = db.outputs.y().template get<T[3]>();
        auto zOut = db.outputs.z().template get<T[3]>();
        if (input && xOut && yOut && zOut)
        {
            const auto inputVec = input.vectorized(count);
            const auto xOutVec = xOut.vectorized(count);
            const auto yOutVec = yOut.vectorized(count);
            const auto zOutVec = zOut.vectorized(count);
            if (!inputVec.empty() && !xOutVec.empty() && !yOutVec.empty() && !zOutVec.empty())
            {
                for (size_t idx = 0; idx < count; idx++)
                    functor(inputVec[idx], xOutVec[idx], yOutVec[idx], zOutVec[idx]);
            }
        }
        return count;
    }
    case 1:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<T[][9]>();
            auto xOut = db.outputs.x(idx).template get<T[][3]>();
            auto yOut = db.outputs.y(idx).template get<T[][3]>();
            auto zOut = db.outputs.z(idx).template get<T[][3]>();
            if (input && xOut && yOut && zOut)
            {
                xOut->resize(input->size());
                yOut->resize(input->size());
                zOut->resize(input->size());
                for (size_t i = 0; i < input->size(); i++)
                    functor((*input)[i], (*xOut)[i], (*yOut)[i], (*zOut)[i]);
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

class OgnBreakMatrix3
{
public:
    static size_t computeVectorized(OgnBreakMatrix3Database& db, size_t count)
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
        auto z = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::z.token());

        auto matrixType = matrix.iAttribute->getResolvedType(matrix);

        // Require inputs to be resolved before determining outputs' type
        if (matrixType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 4> attrs{ matrix, x, y, z };
            std::array<uint8_t, 4> tuples{ 9, 3, 3, 3 };
            std::array<uint8_t, 4> arrays{ matrixType.arrayDepth, matrixType.arrayDepth, matrixType.arrayDepth,
                                           matrixType.arrayDepth };
            std::array<AttributeRole, 4> roles{ matrixType.role, AttributeRole::eNone, AttributeRole::eNone,
                                                AttributeRole::eNone };
            nodeObj.iNode->resolvePartiallyCoupledAttributes(
                nodeObj, attrs.data(), tuples.data(), arrays.data(), roles.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE();

}
}
}
