// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnDistance3DDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>

#include <cmath>

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T>
size_t tryComputeAssumingType(OgnDistance3DDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    { result = sqrt((b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]) + (b[2] - a[2]) * (b[2] - a[2])); };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[3], T[3], T>(
               db.inputs.a(), db.inputs.b(), db.outputs.distance(), functor, count) ?
               count :
               0;
}

} // namespace

class OgnDistance3D
{
public:
    static size_t computeVectorized(OgnDistance3DDatabase& db, size_t count)
    {
        try
        {
            const auto& inputType = db.inputs.a().type();
            switch (inputType.baseType)
            {
            case BaseDataType::eDouble:
                return tryComputeAssumingType<double>(db, count);
            case BaseDataType::eFloat:
                return tryComputeAssumingType<float>(db, count);
            case BaseDataType::eHalf:
                return tryComputeAssumingType<pxr::GfHalf>(db, count);
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
        auto distance = node.iNode->getAttributeByToken(node, outputs::distance.token());

        auto aType = a.iAttribute->getResolvedType(a);
        auto bType = a.iAttribute->getResolvedType(b);

        if (aType.baseType != BaseDataType::eUnknown && bType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 3> attrs{ a, b, distance };
            std::array<uint8_t, 3> tupleCounts{ 3, 3, 1 };
            std::array<uint8_t, 3> arrayDepths{ aType.arrayDepth, bType.arrayDepth,
                                                std::max(aType.arrayDepth, bType.arrayDepth) };
            std::array<AttributeRole, 3> rolesBuf{ aType.role, bType.role, AttributeRole::eNone };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
