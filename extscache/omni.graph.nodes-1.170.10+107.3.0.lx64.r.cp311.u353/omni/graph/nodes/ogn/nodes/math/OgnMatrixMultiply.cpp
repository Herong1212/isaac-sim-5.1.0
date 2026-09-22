// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnMatrixMultiplyDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/vec.h>

using omni::math::linalg::base_matrix;
using omni::math::linalg::base_vec;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{

template <typename T, size_t N>
size_t tryComputeAssumingMatrix(OgnMatrixMultiplyDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        const auto& aMatrix = *reinterpret_cast<const base_matrix<T, N>*>(a);
        const auto& bMatrix = *reinterpret_cast<const base_matrix<T, N>*>(b);
        auto& resultMatrix = *reinterpret_cast<base_matrix<T, N>*>(result);
        resultMatrix = aMatrix * bMatrix;
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N * N]>(
               db.inputs.a(), db.inputs.b(), db.outputs.output(), functor, count) ?
               count :
               0;
}

template <typename T, size_t N>
size_t tryComputeAssumingMatrixVector(OgnMatrixMultiplyDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        const auto& aMatrix = *reinterpret_cast<const base_matrix<T, N>*>(a);
        const auto& bVec = *reinterpret_cast<const base_vec<T, N>*>(b);
        auto& resultVec = *reinterpret_cast<base_vec<T, N>*>(result);
        resultVec = aMatrix * bVec;
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N * N], T[N], T[N]>(
               db.inputs.a(), db.inputs.b(), db.outputs.output(), functor, count) ?
               count :
               0;
}

template <typename T, size_t N>
size_t tryComputeAssumingVectorMatrix(OgnMatrixMultiplyDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        const auto& aVec = *reinterpret_cast<const base_vec<T, N>*>(a);
        const auto& bMatrix = *reinterpret_cast<const base_matrix<T, N>*>(b);
        auto& resultVec = *reinterpret_cast<base_vec<T, N>*>(result);
        resultVec = aVec * bMatrix;
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N], T[N * N], T[N]>(
               db.inputs.a(), db.inputs.b(), db.outputs.output(), functor, count) ?
               count :
               0;
}

template <typename T, size_t N>
size_t tryComputeAssumingVector(OgnMatrixMultiplyDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        const auto& aVec = *reinterpret_cast<const base_vec<T, N>*>(a);
        const auto& bVec = *reinterpret_cast<const base_vec<T, N>*>(b);
        result = aVec * bVec;
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N], T[N], T>(
               db.inputs.a(), db.inputs.b(), db.outputs.output(), functor, count) ?
               count :
               0;
}

} // namespace

class OgnMatrixMultiply
{
public:
    static size_t computeVectorized(OgnMatrixMultiplyDatabase& db, size_t count)
    {
        try
        {
            const auto& aType = db.inputs.a().type();
            const auto& bType = db.inputs.b().type();
            switch (aType.baseType)
            {
            case BaseDataType::eDouble:
                switch (aType.componentCount)
                {
                case 2:
                    switch (bType.componentCount)
                    {
                    case 2:
                        return tryComputeAssumingVector<double, 2>(db, count); // vec2d * vec2d
                    case 4:
                        if (bType.isMatrixType())
                            return tryComputeAssumingVectorMatrix<double, 2>(db, count); // vec2d * matrix2d
                        throw ogn::compute::InputError("Failed to resolve input types"); // LCOV_EXCL_LINE
                    // LCOV_EXCL_START
                    default:
                        throw ogn::compute::InputError("Failed to resolve input types");
                        // LCOV_EXCL_STOP
                    }
                case 3:
                    switch (bType.componentCount)
                    {
                    case 3:
                        return tryComputeAssumingVector<double, 3>(db, count); // vec3d * vec3d
                    case 9:
                        return tryComputeAssumingVectorMatrix<double, 3>(db, count); // vec3d * matrix3d
                    // LCOV_EXCL_START
                    default:
                        throw ogn::compute::InputError("Failed to resolve input types");
                        // LCOV_EXCL_STOP
                    }
                case 4:
                    switch (bType.componentCount)
                    {
                    case 2:
                        return tryComputeAssumingMatrixVector<double, 2>(db, count); // matrix2d * vec2d
                    case 4:
                        if (aType.isMatrixType() && bType.isMatrixType())
                            return tryComputeAssumingMatrix<double, 2>(db, count); // matrix2d * matrix2d
                        else if (!aType.isMatrixType() && !bType.isMatrixType())
                            return tryComputeAssumingVector<double, 4>(db, count); // vec4d * vec4d
                        throw ogn::compute::InputError("Failed to resolve input types"); // LCOV_EXCL_LINE
                    case 16:
                        return tryComputeAssumingVectorMatrix<double, 4>(db, count); // vec4d * matrix4d
                    // LCOV_EXCL_START
                    default:
                        throw ogn::compute::InputError("Failed to resolve input types");
                        // LCOV_EXCL_STOP
                    }
                case 9:
                    switch (bType.componentCount)
                    {
                    case 3:
                        return tryComputeAssumingMatrixVector<double, 3>(db, count); // matrix3d * vec3d
                    case 9:
                        return tryComputeAssumingMatrix<double, 3>(db, count); // matrix3d * matrix3d
                    // LCOV_EXCL_START
                    default:
                        throw ogn::compute::InputError("Failed to resolve input types");
                        // LCOV_EXCL_STOP
                    }
                case 16:
                    switch (bType.componentCount)
                    {
                    case 4:
                        if (!bType.isMatrixType())
                            return tryComputeAssumingMatrixVector<double, 4>(db, count); // matrix4d * vec4d
                        throw ogn::compute::InputError("Failed to resolve input types"); // LCOV_EXCL_LINE
                    case 16:
                        return tryComputeAssumingMatrix<double, 4>(db, count); // matrix4d * matrix4d
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
            case BaseDataType::eFloat:
                switch (aType.componentCount)
                {
                case 2:
                    return tryComputeAssumingVector<float, 2>(db, count); // vec2f * vec2f
                case 3:
                    return tryComputeAssumingVector<float, 3>(db, count); // vec3f * vec3f
                case 4:
                    return tryComputeAssumingVector<float, 4>(db, count); // vec4f * vec4f
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eHalf:
                switch (aType.componentCount)
                {
                case 2:
                    return tryComputeAssumingVector<pxr::GfHalf, 2>(db, count); // vec2h * vec2h
                case 3:
                    return tryComputeAssumingVector<pxr::GfHalf, 3>(db, count); // vec3h * vec3h
                case 4:
                    return tryComputeAssumingVector<pxr::GfHalf, 4>(db, count); // vec4h * vec4h
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
        auto a = node.iNode->getAttributeByToken(node, inputs::a.token());
        auto b = node.iNode->getAttributeByToken(node, inputs::b.token());
        auto output = node.iNode->getAttributeByToken(node, outputs::output.token());

        auto aType = a.iAttribute->getResolvedType(a);
        auto bType = b.iAttribute->getResolvedType(b);

        // Require inputs to be resolved before determining output's type
        if (aType.baseType != BaseDataType::eUnknown && bType.baseType != BaseDataType::eUnknown)
        {
            auto biggerDim = std::max(aType.componentCount, bType.componentCount);
            auto smallerDim = std::min(aType.componentCount, bType.componentCount);

            if ((aType.isMatrixType() != bType.isMatrixType() && biggerDim != smallerDim * smallerDim) ||
                (aType.isMatrixType() == bType.isMatrixType() && aType.componentCount != bType.componentCount))
            {
                node.iNode->logComputeMessageOnInstance(
                    node, kAuthoringGraphIndex, ogn::Severity::eError,
                    formatString("[%s] Inputs are not compatible with tuple counts %d (%s) and %d (%s)",
                                 node.iNode->getPrimPath(node), aType.componentCount, getAttributeRoleName(aType.role),
                                 bType.componentCount, getAttributeRoleName(bType.role))
                        .c_str());
                return;
            }

            // Vector4 * Matrix4 = Vector4, Matrix4 * Vector4 = Vector4 and etc.
            auto tupleCount = smallerDim;
            auto role = aType.isMatrixType() ? bType.role : aType.role;
            if (!aType.isMatrixType() && !bType.isMatrixType())
            {
                // equivalent to dot product of two vectors
                tupleCount = 1;
                role = AttributeRole::eNone;
            }
            std::array<AttributeObj, 3> attrs{ a, b, output };
            std::array<uint8_t, 3> tupleCounts{ aType.componentCount, bType.componentCount, tupleCount };
            std::array<uint8_t, 3> arrayDepths{ aType.arrayDepth, bType.arrayDepth,
                                                std::max(aType.arrayDepth, bType.arrayDepth) };
            std::array<AttributeRole, 3> rolesBuf{ aType.role, bType.role, role };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
