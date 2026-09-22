// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnMakeMatrix3Database.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>

using omni::math::linalg::matrix3;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T>
size_t tryComputeAssumingType(OgnMakeMatrix3Database& db, size_t count)
{
    auto functor = [](auto const& x, auto const& y, auto const& z, auto& output)
    {
        auto& matrix = *reinterpret_cast<matrix3<T>*>(output);
        matrix = matrix.Set(x[0], x[1], x[2], y[0], y[1], y[2], z[0], z[1], z[2]);
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[3], T[3], T[3], T[9]>(
               db.inputs.x(), db.inputs.y(), db.inputs.z(), db.outputs.matrix(), functor, count) ?
               count :
               0;
}
} // namespace

class OgnMakeMatrix3
{
public:
    static size_t computeVectorized(OgnMakeMatrix3Database& db, size_t count)
    {

        try
        {
            const auto& outputType = db.outputs.matrix().type();
            switch (outputType.baseType)
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
        auto x = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::x.token());
        auto y = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::y.token());
        auto z = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::z.token());
        auto matrix = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::matrix.token());

        auto xType = x.iAttribute->getResolvedType(x);
        auto yType = y.iAttribute->getResolvedType(y);
        auto zType = z.iAttribute->getResolvedType(z);

        // If one of the inputs is resolved we can resolve the other because they should match
        std::array<AttributeObj, 3> attrs{ x, y, z };
        if (nodeObj.iNode->resolveCoupledAttributes(nodeObj, attrs.data(), attrs.size()))
        {
            xType = x.iAttribute->getResolvedType(x);
            yType = y.iAttribute->getResolvedType(y);
            zType = z.iAttribute->getResolvedType(z);
        }

        // Require inputs to be resolved before determining outputs' type
        if (xType.baseType != BaseDataType::eUnknown && yType.baseType != BaseDataType::eUnknown &&
            zType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 4> attrs{ x, y, z, matrix };
            std::array<uint8_t, 4> tuples{ 3, 3, 3, 9 };
            std::array<uint8_t, 4> arrays{ xType.arrayDepth, yType.arrayDepth, zType.arrayDepth,
                                           std::max(xType.arrayDepth, std::max(yType.arrayDepth, zType.arrayDepth)) };
            std::array<AttributeRole, 4> roles{ xType.role, yType.role, zType.role, AttributeRole::eMatrix };
            nodeObj.iNode->resolvePartiallyCoupledAttributes(
                nodeObj, attrs.data(), tuples.data(), arrays.data(), roles.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE();

}
}
}
