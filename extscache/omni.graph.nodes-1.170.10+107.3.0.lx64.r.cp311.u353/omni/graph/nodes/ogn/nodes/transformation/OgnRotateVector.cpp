// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnRotateVectorDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/vec.h>
#include <omni/math/linalg/quat.h>
// clang-format on

#include "TransformCommon.h"

using ogn::compute::tryComputeWithArrayBroadcasting;
using omni::math::linalg::matrix3d;
using omni::math::linalg::matrix4d;
using omni::math::linalg::quat;
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
size_t tryComputeWithMatrix3(OgnRotateVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& rotation, auto& vector, auto& result)
    {
        auto& matrix = *reinterpret_cast<const matrix3d*>(rotation);
        auto sourceVec = vec3<double>(*reinterpret_cast<const vec3<T>*>(vector));
        auto& resultVec = *reinterpret_cast<vec3<T>*>(result);
        // left multiplication by row vector
        resultVec = vec3<T>(sourceVec * matrix);
    };
    return tryComputeWithArrayBroadcasting<double[9], T[3], T[3]>(
               db.inputs.rotation(), db.inputs.vector(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <typename T>
size_t tryComputeWithMatrix4(OgnRotateVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& rotation, auto& vector, auto& result)
    {
        auto& matrix = *reinterpret_cast<const matrix4d*>(rotation);
        auto sourceVec = vec3<double>(*reinterpret_cast<const vec3<T>*>(vector));
        auto& resultVec = *reinterpret_cast<vec3<T>*>(result);
        resultVec = vec3<T>(matrix.TransformDir(sourceVec));
    };
    return tryComputeWithArrayBroadcasting<double[16], T[3], T[3]>(
               db.inputs.rotation(), db.inputs.vector(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <typename T>
size_t tryComputeWithQuat(OgnRotateVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& rotation, auto& vector, auto& result)
    {
        auto& quaternion = *reinterpret_cast<const quat<T>*>(rotation);
        auto& sourceVec = *reinterpret_cast<const vec3<T>*>(vector);
        auto& resultVec = *reinterpret_cast<vec3<T>*>(result);
        resultVec = quaternion.Transform(sourceVec);
    };
    return tryComputeWithArrayBroadcasting<T[4], T[3], T[3]>(
               db.inputs.rotation(), db.inputs.vector(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <typename T>
size_t tryComputeWithEulerAngles(OgnRotateVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& rotation, auto& vector, auto& rotationOrder, auto& result)
    {
        auto eulerAngles = vec3<double>(*reinterpret_cast<const vec3<T>*>(rotation));
        auto sourceVec = vec3<double>(*reinterpret_cast<const vec3<T>*>(vector));
        auto& resultVec = *reinterpret_cast<vec3<T>*>(result);
        auto quaternion = omni::math::linalg::eulerAnglesToQuaternion(GfDegreesToRadians(eulerAngles), rotationOrder);
        resultVec = vec3<T>(quaternion.Transform(sourceVec));
    };

    const auto& rotationType = db.inputs.rotation().type();
    const auto& vectorType = db.inputs.vector().type();
    switch (rotationType.arrayDepth)
    {
    case 0:
        switch (vectorType.arrayDepth)
        {
        case 0:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto rotation = db.inputs.rotation(idx).template get<const T[3]>();
                const auto vector = db.inputs.vector(idx).template get<const T[3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
                auto output = db.outputs.result(idx).template get<T[3]>();
                functor(*rotation, *vector, rotationOrder, *output);
            }
            return count;
        case 1:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto rotation = db.inputs.rotation(idx).template get<const T[3]>();
                const auto vectors = db.inputs.vector(idx).template get<const T[][3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
                auto output = db.outputs.result(idx).template get<T[][3]>();
                output->resize(vectors->size());
                for (size_t i = 0; i < vectors.size(); i++)
                    functor(*rotation, (*vectors)[i], rotationOrder, (*output)[i]);
            }
            return count;
        // LCOV_EXCL_START
        default:
            throw ogn::compute::InputError("Failed to resolve input types");
            // LCOV_EXCL_STOP
        }
    case 1:
        switch (vectorType.arrayDepth)
        {
        case 0:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto rotations = db.inputs.rotation(idx).template get<const T[][3]>();
                const auto vector = db.inputs.vector(idx).template get<const T[3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
                auto output = db.outputs.result(idx).template get<T[][3]>();
                output->resize(rotations->size());
                for (size_t i = 0; i < rotations.size(); i++)
                    functor((*rotations)[i], *vector, rotationOrder, (*output)[i]);
            }
            return count;
        case 1:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto rotations = db.inputs.rotation(idx).template get<const T[][3]>();
                const auto vectors = db.inputs.vector(idx).template get<const T[][3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));

                if (rotations.size() != vectors.size())
                    throw ogn::compute::InputError(
                        "Unable to broadcast arrays of differing lengths: " + std::to_string(rotations.size()) +
                        "!=" + std::to_string(vectors.size()));

                auto output = db.outputs.result(idx).template get<T[][3]>();
                output->resize(rotations->size());
                for (size_t i = 0; i < rotations.size(); i++)
                    functor((*rotations)[i], (*vectors)[i], rotationOrder, (*output)[i]);
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

/* FIXME: GfHalf has no explicit conversion from double to half, so we need to convert to a float first */
template <>
size_t tryComputeWithMatrix3<pxr::GfHalf>(OgnRotateVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& rotation, auto& vector, auto& result)
    {
        auto& matrix = *reinterpret_cast<const matrix3d*>(rotation);
        auto sourceVec = vec3<double>(*reinterpret_cast<const vec3<pxr::GfHalf>*>(vector));
        auto& resultVec = *reinterpret_cast<vec3<pxr::GfHalf>*>(result);
        // left multiplication by row vector
        resultVec = vec3<pxr::GfHalf>(vec3<float>(sourceVec * matrix));
    };
    return tryComputeWithArrayBroadcasting<double[9], pxr::GfHalf[3], pxr::GfHalf[3]>(
               db.inputs.rotation(), db.inputs.vector(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <>
size_t tryComputeWithMatrix4<pxr::GfHalf>(OgnRotateVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& rotation, auto& vector, auto& result)
    {
        auto& matrix = *reinterpret_cast<const matrix4d*>(rotation);
        auto sourceVec = vec3<double>(*reinterpret_cast<const vec3<pxr::GfHalf>*>(vector));
        auto& resultVec = *reinterpret_cast<vec3<pxr::GfHalf>*>(result);
        resultVec = vec3<pxr::GfHalf>(vec3<float>(matrix.TransformDir(sourceVec)));
    };
    return tryComputeWithArrayBroadcasting<double[16], pxr::GfHalf[3], pxr::GfHalf[3]>(
               db.inputs.rotation(), db.inputs.vector(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <>
size_t tryComputeWithEulerAngles<pxr::GfHalf>(OgnRotateVectorDatabase& db, size_t count)
{
    auto functor = [&](auto& rotation, auto& vector, auto& rotationOrder, auto& result)
    {
        auto eulerAngles = vec3<double>(*reinterpret_cast<const vec3<pxr::GfHalf>*>(rotation));
        auto sourceVec = vec3<double>(*reinterpret_cast<const vec3<pxr::GfHalf>*>(vector));
        auto& resultVec = *reinterpret_cast<vec3<pxr::GfHalf>*>(result);
        auto quaternion = omni::math::linalg::eulerAnglesToQuaternion(GfDegreesToRadians(eulerAngles), rotationOrder);
        resultVec = vec3<pxr::GfHalf>(vec3<float>(quaternion.Transform(sourceVec)));
    };

    const auto& rotationType = db.inputs.rotation().type();
    const auto& vectorType = db.inputs.vector().type();
    switch (rotationType.arrayDepth)
    {
    case 0:
        switch (vectorType.arrayDepth)
        {
        case 0:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto rotation = db.inputs.rotation(idx).template get<const pxr::GfHalf[3]>();
                const auto vector = db.inputs.vector(idx).template get<const pxr::GfHalf[3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
                auto output = db.outputs.result(idx).template get<pxr::GfHalf[3]>();
                functor(*rotation, *vector, rotationOrder, *output);
            }
            return count;
        case 1:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto rotation = db.inputs.rotation(idx).template get<const pxr::GfHalf[3]>();
                const auto vectors = db.inputs.vector(idx).template get<const pxr::GfHalf[][3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
                auto output = db.outputs.result(idx).template get<pxr::GfHalf[][3]>();
                output->resize(vectors->size());
                for (size_t i = 0; i < vectors.size(); i++)
                    functor(*rotation, (*vectors)[i], rotationOrder, (*output)[i]);
            }
            return count;
        // LCOV_EXCL_START
        default:
            throw ogn::compute::InputError("Failed to resolve input types");
            // LCOV_EXCL_STOP
        }
    case 1:
        switch (vectorType.arrayDepth)
        {
        case 0:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto rotations = db.inputs.rotation(idx).template get<const pxr::GfHalf[][3]>();
                const auto vector = db.inputs.vector(idx).template get<const pxr::GfHalf[3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));
                auto output = db.outputs.result(idx).template get<pxr::GfHalf[][3]>();
                output->resize(rotations->size());
                for (size_t i = 0; i < rotations.size(); i++)
                    functor((*rotations)[i], *vector, rotationOrder, (*output)[i]);
            }
            return count;
        case 1:
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto rotations = db.inputs.rotation(idx).template get<const pxr::GfHalf[][3]>();
                const auto vectors = db.inputs.vector(idx).template get<const pxr::GfHalf[][3]>();
                const auto rotationOrder = getRotationOrder(db, db.inputs.rotationOrder(idx));

                if (rotations.size() != vectors.size())
                    throw ogn::compute::InputError(
                        "Unable to broadcast arrays of differing lengths: " + std::to_string(rotations.size()) +
                        "!=" + std::to_string(vectors.size()));

                auto output = db.outputs.result(idx).template get<pxr::GfHalf[][3]>();
                output->resize(rotations->size());
                for (size_t i = 0; i < rotations.size(); i++)
                    functor((*rotations)[i], (*vectors)[i], rotationOrder, (*output)[i]);
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
} // namespace

class OgnRotateVector
{
public:
    static size_t computeVectorized(OgnRotateVectorDatabase& db, size_t count)
    {
        // Compute the components, if the types are all resolved.
        try
        {
            auto& rotationType = db.inputs.rotation().type();
            auto& vectorType = db.inputs.vector().type();
            switch (rotationType.componentCount)
            {
            case 3:
                if (vectorType.baseType != rotationType.baseType)
                    throw ogn::compute::InputError("Rotation and vector types must match");

                switch (vectorType.baseType)
                {
                case BaseDataType::eDouble:
                    return tryComputeWithEulerAngles<double>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeWithEulerAngles<float>(db, count);
                case BaseDataType::eHalf:
                    return tryComputeWithEulerAngles<pxr::GfHalf>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case 4:
                if (vectorType.baseType != rotationType.baseType)
                    throw ogn::compute::InputError("Rotation and vector types must match");

                switch (vectorType.baseType)
                {
                case BaseDataType::eDouble:
                    return tryComputeWithQuat<double>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeWithQuat<float>(db, count);
                case BaseDataType::eHalf:
                    return tryComputeWithQuat<pxr::GfHalf>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case 9:
                switch (vectorType.baseType)
                {
                case BaseDataType::eDouble:
                    return tryComputeWithMatrix3<double>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeWithMatrix3<float>(db, count);
                case BaseDataType::eHalf:
                    return tryComputeWithMatrix3<pxr::GfHalf>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case 16:
                switch (vectorType.baseType)
                {
                case BaseDataType::eDouble:
                    return tryComputeWithMatrix4<double>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeWithMatrix4<float>(db, count);
                case BaseDataType::eHalf:
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
        auto rotation = node.iNode->getAttributeByToken(node, inputs::rotation.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto vectorType = vector.iAttribute->getResolvedType(vector);
        auto rotationType = rotation.iAttribute->getResolvedType(rotation);

        // Require vector, rotation to be resolved before determining result's type
        if (vectorType.baseType != BaseDataType::eUnknown && rotationType.baseType != BaseDataType::eUnknown)
        {
            Type resultType(vectorType.baseType, vectorType.componentCount,
                            std::max(vectorType.arrayDepth, rotationType.arrayDepth), vectorType.role);
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
