// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <algorithm>
#include <OgnInterpolateToDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>

#include <omni/math/linalg/quat.h>

#include "XformUtils.h"

using omni::math::linalg::GfSlerp;
using omni::math::linalg::quatd;

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{

template <typename T>
bool tryComputeAssumingType(OgnInterpolateToDatabase& db, double alpha, size_t count)
{
    auto functor = [&](auto const& a, auto const& b, auto& result)
    {
        // Linear interpolation between a and b, alpha in [0, 1]
        result = a + (b - a) * (float)alpha;
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T>(
        db.inputs.current(), db.inputs.target(), db.outputs.result(), functor, count);
}
template <typename T, size_t N>
bool tryComputeAssumingType(OgnInterpolateToDatabase& db, double alpha, size_t count)
{
    auto functor = [&](auto const& a, auto const& b, auto& result)
    {
        // Linear interpolation between a and b, alpha in [0, 1]
        for (size_t i = 0; i < N; i++)
        {
            result[i] = a[i] + (b[i] - a[i]) * (float)alpha;
        }
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N]>(
        db.inputs.current(), db.inputs.target(), db.outputs.result(), functor, count);
}
template <>
bool tryComputeAssumingType<double, 4>(OgnInterpolateToDatabase& db, double alpha, size_t count)
{
    auto currentAttribute =
        db.abi_node().iNode->getAttribute(db.abi_node(), OgnInterpolateToAttributes::inputs::current.m_name);
    auto currentRole = currentAttribute.iAttribute->getResolvedType(currentAttribute).role;
    if (currentRole == AttributeRole::eQuaternion)
    {
        auto functor = [&](auto const& a, auto const& b, auto& result)
        {
            // Note that in Fabric, quaternions are stored as XYZW, but quatd constructor requires WXYZ
            auto q = GfSlerp(quatd(a[3], a[0], a[1], a[2]), quatd(b[3], b[0], b[1], b[2]), alpha);
            result[0] = q.GetImaginary()[0];
            result[1] = q.GetImaginary()[1];
            result[2] = q.GetImaginary()[2];
            result[3] = q.GetReal();
        };
        return ogn::compute::tryComputeWithArrayBroadcasting<double[4]>(
            db.inputs.current(), db.inputs.target(), db.outputs.result(), functor, count);
    }
    else
    {
        auto functor = [&](auto const& a, auto const& b, auto& result)
        {
            // Linear interpolation between a and b, alpha in [0, 1]
            for (size_t i = 0; i < 4; i++)
            {
                result[i] = a[i] + (b[i] - a[i]) * (float)alpha;
            }
        };
        return ogn::compute::tryComputeWithArrayBroadcasting<double[4]>(
            db.inputs.current(), db.inputs.target(), db.outputs.result(), functor, count);
    }
}
template <>
bool tryComputeAssumingType<float, 4>(OgnInterpolateToDatabase& db, double alpha, size_t count)
{
    auto currentAttribute =
        db.abi_node().iNode->getAttribute(db.abi_node(), OgnInterpolateToAttributes::inputs::current.m_name);
    auto currentRole = currentAttribute.iAttribute->getResolvedType(currentAttribute).role;
    if (currentRole == AttributeRole::eQuaternion)
    {
        auto functor = [&](auto const& a, auto const& b, auto& result)
        {
            // Note that in Fabric, quaternions are stored as XYZW, but quatd constructor requires WXYZ
            auto q = GfSlerp(quatd(a[3], a[0], a[1], a[2]), quatd(b[3], b[0], b[1], b[2]), alpha);
            result[0] = (float)q.GetImaginary()[0];
            result[1] = (float)q.GetImaginary()[1];
            result[2] = (float)q.GetImaginary()[2];
            result[3] = (float)q.GetReal();
        };
        return ogn::compute::tryComputeWithArrayBroadcasting<float[4]>(
            db.inputs.current(), db.inputs.target(), db.outputs.result(), functor, count);
    }
    else
    {
        auto functor = [&](auto const& a, auto const& b, auto& result)
        {
            // Linear interpolation between a and b, alpha in [0, 1]
            for (size_t i = 0; i < 4; i++)
            {
                result[i] = a[i] + (b[i] - a[i]) * (float)alpha;
            }
        };
        return ogn::compute::tryComputeWithArrayBroadcasting<float[4]>(
            db.inputs.current(), db.inputs.target(), db.outputs.result(), functor, count);
    };
}
template <>
bool tryComputeAssumingType<pxr::GfHalf, 4>(OgnInterpolateToDatabase& db, double alpha, size_t count)
{
    auto currentAttribute =
        db.abi_node().iNode->getAttribute(db.abi_node(), OgnInterpolateToAttributes::inputs::current.m_name);
    auto currentRole = currentAttribute.iAttribute->getResolvedType(currentAttribute).role;
    if (currentRole == AttributeRole::eQuaternion)
    {
        auto functor = [&](auto const& a, auto const& b, auto& result)
        {
            // Note that in Fabric, quaternions are stored as XYZW, but quatd constructor requires WXYZ
            auto q = GfSlerp(quatd(a[3], a[0], a[1], a[2]), quatd(b[3], b[0], b[1], b[2]), alpha);
            result[0] = (float)q.GetImaginary()[0];
            result[1] = (float)q.GetImaginary()[1];
            result[2] = (float)q.GetImaginary()[2];
            result[3] = (float)q.GetReal();
        };
        return ogn::compute::tryComputeWithArrayBroadcasting<pxr::GfHalf[4]>(
            db.inputs.current(), db.inputs.target(), db.outputs.result(), functor, count);
    }
    else
    {
        auto functor = [&](auto const& a, auto const& b, auto& result)
        {
            // Linear interpolation between a and b, alpha in [0, 1]
            for (size_t i = 0; i < 4; i++)
            {
                result[i] = a[i] + (b[i] - a[i]) * (float)alpha;
            }
        };
        return ogn::compute::tryComputeWithArrayBroadcasting<pxr::GfHalf[4]>(
            db.inputs.current(), db.inputs.target(), db.outputs.result(), functor, count);
    };
}
} // namespace

class OgnInterpolateTo
{
public:
    static bool computeVectorized(OgnInterpolateToDatabase& db, size_t count)
    {
        int exp = std::min(std::max(int(db.inputs.exponent()), 0), 10);
        float speed = std::max(0.f, float(db.inputs.speed()));
        float deltaSeconds = std::max(0.f, float(db.inputs.deltaSeconds()));
        // delta step
        float alpha = std::min(std::max(speed * deltaSeconds, 0.f), 1.f);
        // Ease out by applying a shifted exponential to the alpha
        double alpha2 = 1.f - exponent(1.f - alpha, exp);

        auto& inputType = db.inputs.current().type();
        auto& tgtType = db.inputs.target().type();
        // Compute the components, if the types are all resolved.
        try
        {
            if (inputType.componentCount != tgtType.componentCount)
                throw ogn::compute::InputError("Mismatched tuple counts: " + std::to_string(inputType.componentCount) +
                                               " and " + std::to_string(tgtType.componentCount));

            switch (inputType.baseType)
            {
            case BaseDataType::eDouble:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<double>(db, alpha2, count);
                case 2:
                    return tryComputeAssumingType<double, 2>(db, alpha2, count);
                case 3:
                    return tryComputeAssumingType<double, 3>(db, alpha2, count);
                case 4:
                    return tryComputeAssumingType<double, 4>(db, alpha2, count);
                case 9:
                    return tryComputeAssumingType<double, 9>(db, alpha2, count);
                case 16:
                    return tryComputeAssumingType<double, 16>(db, alpha2, count);
                default:
                    break;
                }
            case BaseDataType::eFloat:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<float>(db, alpha2, count);
                case 2:
                    return tryComputeAssumingType<float, 2>(db, alpha2, count);
                case 3:
                    return tryComputeAssumingType<float, 3>(db, alpha2, count);
                case 4:
                    return tryComputeAssumingType<float, 4>(db, alpha2, count);
                default:
                    break;
                }
            case BaseDataType::eHalf:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<pxr::GfHalf>(db, alpha2, count);
                case 2:
                    return tryComputeAssumingType<pxr::GfHalf, 2>(db, alpha2, count);
                case 3:
                    return tryComputeAssumingType<pxr::GfHalf, 3>(db, alpha2, count);
                case 4:
                    return tryComputeAssumingType<pxr::GfHalf, 4>(db, alpha2, count);
                default:
                    break;
                }
            default:
                break;
            }

            throw ogn::compute::InputError("Failed to resolve input types");
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError("OgnInterpolateTo: %s", error.what());
        }
        return false;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto current = node.iNode->getAttributeByToken(node, inputs::current.token());
        auto target = node.iNode->getAttributeByToken(node, inputs::target.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto currentType = current.iAttribute->getResolvedType(current);
        auto targetType = target.iAttribute->getResolvedType(target);

        // Require current, target, and alpha to be resolved before determining result's type
        if (currentType.baseType != BaseDataType::eUnknown && targetType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 3> attrs{ current, target, result };
            std::array<uint8_t, 3> tupleCounts{ currentType.componentCount, targetType.componentCount,
                                                std::max(currentType.componentCount, targetType.componentCount) };
            std::array<uint8_t, 3> arrayDepths{ currentType.arrayDepth, targetType.arrayDepth,
                                                std::max(currentType.arrayDepth, targetType.arrayDepth) };
            std::array<AttributeRole, 3> rolesBuf{ currentType.role, targetType.role, AttributeRole::eUnknown };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
