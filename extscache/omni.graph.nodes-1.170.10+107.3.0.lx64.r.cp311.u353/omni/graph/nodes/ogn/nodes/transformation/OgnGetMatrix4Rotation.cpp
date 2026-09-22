// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnGetMatrix4RotationDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/vec.h>
#include <usdrt/gf/rotation.h>
// clang-format on

using omni::math::linalg::matrix3d;
using omni::math::linalg::matrix4d;
using omni::math::linalg::quat;
using omni::math::linalg::quatd;
using omni::math::linalg::vec3;
using omni::math::linalg::vec3d;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
// The rotation axes order could be different from the output order so we track both
struct RotationOrder
{
    vec3d axes[3];
    size_t outIndices[3];
};

const RotationOrder getRotationOrder(const NameToken orderToken)
{
    // The first 3 digits are the the axis order second 3 are the output order
    std::unordered_map<NameToken, RotationOrder> rotationOrders = {
        { OgnGetMatrix4RotationDatabase::tokens.XYZ, { { vec3d::ZAxis(), vec3d::YAxis(), vec3d::XAxis() }, { 2, 1, 0 } } },
        { OgnGetMatrix4RotationDatabase::tokens.XZY, { { vec3d::YAxis(), vec3d::ZAxis(), vec3d::XAxis() }, { 2, 0, 1 } } },
        { OgnGetMatrix4RotationDatabase::tokens.YXZ, { { vec3d::ZAxis(), vec3d::XAxis(), vec3d::YAxis() }, { 1, 2, 0 } } },
        { OgnGetMatrix4RotationDatabase::tokens.YZX, { { vec3d::XAxis(), vec3d::ZAxis(), vec3d::YAxis() }, { 0, 2, 1 } } },
        { OgnGetMatrix4RotationDatabase::tokens.ZXY, { { vec3d::YAxis(), vec3d::XAxis(), vec3d::ZAxis() }, { 1, 0, 2 } } },
        { OgnGetMatrix4RotationDatabase::tokens.ZYX, { { vec3d::XAxis(), vec3d::YAxis(), vec3d::ZAxis() }, { 0, 1, 2 } } },
    };
    if (auto search = rotationOrders.find(orderToken); search != rotationOrders.end())
        return search->second;
    else
        throw ogn::compute::InputError("Invalid rotation order. Must be XYZ, XZY, YXZ, YZX, ZXY or ZYX");
}

template <typename T>
void getEulerFromQuat(const T input[4], RotationOrder rotationOrder, T output[3])
{
    const auto& quaternion = quatd(*reinterpret_cast<const quat<T>*>(input));
    auto rotation = vec3<T>(
        usdrt::GfRotation(quaternion).Decompose(rotationOrder.axes[0], rotationOrder.axes[1], rotationOrder.axes[2]));
    output[0] = rotation[rotationOrder.outIndices[0]];
    output[1] = rotation[rotationOrder.outIndices[1]];
    output[2] = rotation[rotationOrder.outIndices[2]];
};

template <>
void getEulerFromQuat<pxr::GfHalf>(const pxr::GfHalf input[4], RotationOrder rotationOrder, pxr::GfHalf output[3])
{
    const auto& quaternion = quatd(*reinterpret_cast<const quat<pxr::GfHalf>*>(input));
    auto rotation = vec3<pxr::GfHalf>(vec3<float>(
        usdrt::GfRotation(quaternion).Decompose(rotationOrder.axes[0], rotationOrder.axes[1], rotationOrder.axes[2])));
    output[0] = rotation[rotationOrder.outIndices[0]];
    output[1] = rotation[rotationOrder.outIndices[1]];
    output[2] = rotation[rotationOrder.outIndices[2]];
};

template <typename T>
size_t tryComputeAssumingQuat(OgnGetMatrix4RotationDatabase& db, size_t count)
{
    switch (db.inputs.matrix().type().arrayDepth)
    {
    case 0:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<const T[4]>();
            const auto rotationOrder = getRotationOrder(db.inputs.rotationOrder(idx));
            auto output = db.outputs.rotation(idx).template get<T[3]>();
            if (input && output)
                getEulerFromQuat<T>(*input, rotationOrder, *output);
        }
        return count;
    case 1:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<const T[][4]>();
            const auto rotationOrder = getRotationOrder(db.inputs.rotationOrder(idx));
            auto output = db.outputs.rotation(idx).template get<T[][3]>();
            if (input && output)
            {
                output->resize(input->size());
                for (size_t i = 0; i < input->size(); i++)
                    getEulerFromQuat<T>((*input)[i], rotationOrder, (*output)[i]);
            }
        }
        return count;
    default:
        return 0;
    }
}

template <typename T, size_t N>
size_t tryComputeAssumingMatrix(OgnGetMatrix4RotationDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& rotationOrder, auto& output)
    {
        const auto& matrix = *reinterpret_cast<const T*>(input);
        auto rotation = matrix.GetOrthonormalized().template DecomposeRotation<usdrt::GfRotation>(
            rotationOrder.axes[0], rotationOrder.axes[1], rotationOrder.axes[2]);
        output[0] = rotation[rotationOrder.outIndices[0]];
        output[1] = rotation[rotationOrder.outIndices[1]];
        output[2] = rotation[rotationOrder.outIndices[2]];
    };

    switch (db.inputs.matrix().type().arrayDepth)
    {
    case 0:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<const double[N * N]>();
            const auto rotationOrder = getRotationOrder(db.inputs.rotationOrder(idx));
            auto output = db.outputs.rotation(idx).template get<double[3]>();
            if (input && output)
                functor(*input, rotationOrder, *output);
        }
        return count;
    case 1:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto input = db.inputs.matrix(idx).template get<const double[][N * N]>();
            const auto rotationOrder = getRotationOrder(db.inputs.rotationOrder(idx));
            auto output = db.outputs.rotation(idx).template get<double[][3]>();
            if (input && output)
            {
                output->resize(input->size());
                for (size_t i = 0; i < input->size(); i++)
                    functor((*input)[i], rotationOrder, (*output)[i]);
            }
        }
        return count;
    default:
        return 0;
    }
}

}

class OgnGetMatrix4Rotation
{
public:
    static size_t computeVectorized(OgnGetMatrix4RotationDatabase& db, size_t count)
    {
        try
        {
            const auto& matrixType = db.inputs.matrix().type();
            switch (matrixType.baseType)
            {
            case BaseDataType::eDouble:
                switch (matrixType.componentCount)
                {
                case 4:
                    return tryComputeAssumingQuat<double>(db, count);
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
                case 4:
                    return tryComputeAssumingQuat<float>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eHalf:
                switch (matrixType.componentCount)
                {
                case 4:
                    return tryComputeAssumingQuat<pxr::GfHalf>(db, count);
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
        const auto rotation = node.iNode->getAttributeByToken(node, outputs::rotation.token());

        auto matrixType = matrix.iAttribute->getResolvedType(matrix);

        std::array<AttributeObj, 2> attrs{ matrix, rotation };
        std::array<uint8_t, 2> tupleCounts{ matrixType.componentCount, 3 };
        std::array<uint8_t, 2> arrayDepths{ matrixType.arrayDepth, matrixType.arrayDepth };
        std::array<AttributeRole, 2> rolesBuf{ matrixType.role, AttributeRole::eVector };
        node.iNode->resolvePartiallyCoupledAttributes(
            node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
    }

    static bool updateNodeVersion(const GraphContextObj& context, const NodeObj& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            // The old node
            if (oldVersion < 2)
            {
                // The old behavior of the node was actually using ZYX rotation order rather than XYZ as intended
                const Token rotOrder("ZYX");
                nodeObj.iNode->createAttribute(nodeObj, "inputs:rotationOrder", Type(BaseDataType::eToken), &rotOrder,
                                               nullptr, kAttributePortType_Input, kExtendedAttributeType_Regular,
                                               nullptr);
            }
            return true;
        }
        return false;
    }
};

REGISTER_OGN_NODE()

}
}
}
