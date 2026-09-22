// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnTransformVectorDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/vec.h>

using ogn::compute::tryComputeWithArrayBroadcasting;
using omni::math::linalg::matrix3d;
using omni::math::linalg::matrix4d;
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
size_t tryComputeWithMatrix3(OgnTransformVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& matrix, auto& vector, auto& result)
    {
        auto& transformMat = *reinterpret_cast<const matrix3d*>(matrix);
        auto sourceVec = vec3<double>(*reinterpret_cast<const vec3<T>*>(vector));
        auto& resultVec = *reinterpret_cast<vec3<T>*>(result);
        // left multiplication by row vector
        resultVec = vec3<T>(sourceVec * transformMat);
    };
    return tryComputeWithArrayBroadcasting<double[9], T[3], T[3]>(
               db.inputs.matrix(), db.inputs.vector(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <typename T>
size_t tryComputeWithMatrix4(OgnTransformVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& matrix, auto& vector, auto& result)
    {
        auto& transformMat = *reinterpret_cast<const matrix4d*>(matrix);
        auto sourceVec = vec3<double>(*reinterpret_cast<const vec3<T>*>(vector));
        auto& resultVec = *reinterpret_cast<vec3<T>*>(result);
        resultVec = vec3<T>(transformMat.Transform(sourceVec));
    };
    return tryComputeWithArrayBroadcasting<double[16], T[3], T[3]>(
               db.inputs.matrix(), db.inputs.vector(), db.outputs.result(), functor, count) ?
               count :
               0;
}

/* FIXME: GfHalf has no explicit conversion from double to half, so we need to convert to a float first */
template <>
size_t tryComputeWithMatrix3<pxr::GfHalf>(OgnTransformVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& matrix, auto& vector, auto& result)
    {
        auto& transformMat = *reinterpret_cast<const matrix3d*>(matrix);
        auto sourceVec = vec3<double>(*reinterpret_cast<const vec3<pxr::GfHalf>*>(vector));
        auto& resultVec = *reinterpret_cast<vec3<pxr::GfHalf>*>(result);
        // left multiplication by row vector
        resultVec = vec3<pxr::GfHalf>(vec3<float>(sourceVec * transformMat));
    };
    return tryComputeWithArrayBroadcasting<double[9], pxr::GfHalf[3], pxr::GfHalf[3]>(
               db.inputs.matrix(), db.inputs.vector(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <>
size_t tryComputeWithMatrix4<pxr::GfHalf>(OgnTransformVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& matrix, auto& vector, auto& result)
    {
        auto& transformMat = *reinterpret_cast<const matrix4d*>(matrix);
        auto sourceVec = vec3<double>(*reinterpret_cast<const vec3<pxr::GfHalf>*>(vector));
        auto& resultVec = *reinterpret_cast<vec3<pxr::GfHalf>*>(result);
        resultVec = vec3<pxr::GfHalf>(vec3<float>(transformMat.Transform(sourceVec)));
    };
    return tryComputeWithArrayBroadcasting<double[16], pxr::GfHalf[3], pxr::GfHalf[3]>(
               db.inputs.matrix(), db.inputs.vector(), db.outputs.result(), functor, count) ?
               count :
               0;
}
} // namespace

class OgnTransformVector
{
public:
    static size_t computeVectorized(OgnTransformVectorDatabase& db, size_t count)
    {
        // Compute the components, if the types are all resolved.
        try
        {
            auto& vectorType = db.inputs.vector().type();
            auto& matrixType = db.inputs.matrix().type();
            switch (vectorType.baseType)
            {
            case BaseDataType::eDouble:
                switch (matrixType.componentCount)
                {
                case 9:
                    return tryComputeWithMatrix3<double>(db, count);
                case 16:
                    return tryComputeWithMatrix4<double>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eFloat:
                switch (matrixType.componentCount)
                {
                case 9:
                    return tryComputeWithMatrix3<float>(db, count);
                case 16:
                    return tryComputeWithMatrix4<float>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eHalf:
                switch (matrixType.componentCount)
                {
                case 9:
                    return tryComputeWithMatrix3<pxr::GfHalf>(db, count);
                case 16:
                    return tryComputeWithMatrix4<pxr::GfHalf>(db, count);
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
        auto vector = node.iNode->getAttributeByToken(node, inputs::vector.token());
        auto matrix = node.iNode->getAttributeByToken(node, inputs::matrix.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto vectorType = vector.iAttribute->getResolvedType(vector);
        auto matrixType = matrix.iAttribute->getResolvedType(matrix);

        // Require vector, matrix to be resolved before determining result's type
        if (vectorType.baseType != BaseDataType::eUnknown && matrixType.baseType != BaseDataType::eUnknown)
        {
            Type resultType(vectorType.baseType, vectorType.componentCount,
                            std::max(vectorType.arrayDepth, matrixType.arrayDepth), vectorType.role);
            result.iAttribute->setResolvedType(result, resultType);
        }
        else
            result.iAttribute->setResolvedType(result, Type(BaseDataType::eUnknown));
    }
};

REGISTER_OGN_NODE()

}
}
}
