// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnOrthonormalizeDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/matrix.h>

using omni::math::linalg::matrix3d;
using omni::math::linalg::matrix4d;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T, size_t N>
size_t tryComputeAssumingType(OgnOrthonormalizeDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& output)
    {
        const auto matrix = *reinterpret_cast<const T*>(input);
        auto& result = *reinterpret_cast<T*>(output);
        result = matrix.GetOrthonormalized();
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<double[N * N]>(
               db.inputs.matrix(), db.outputs.result(), functor, count) ?
               count :
               0;
}
}

class OgnOrthonormalize
{
public:
    static size_t computeVectorized(OgnOrthonormalizeDatabase& db, size_t count)
    {
        const auto& matrixType = db.inputs.matrix().type();
        try
        {
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
        auto input = node.iNode->getAttributeByToken(node, inputs::matrix.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto inputType = input.iAttribute->getResolvedType(input);

        // Require inputs to be resolved before determining output's type
        if (inputType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 2> attrs{ input, result };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
