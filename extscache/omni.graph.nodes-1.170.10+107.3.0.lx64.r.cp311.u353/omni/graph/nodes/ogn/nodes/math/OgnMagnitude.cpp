// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnMagnitudeDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>
#include <cmath>
#include <type_traits>

namespace omni
{
namespace graph
{
namespace nodes
{
// unnamed namespace to avoid multiple declaration when linking
namespace
{
template <typename T>
bool tryComputeAssumingType(OgnMagnitudeDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& magnitude)
    { magnitude = static_cast<T>(std::abs(static_cast<double>(input))); };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, T>(db.inputs.input(), db.outputs.magnitude(), functor, count) ?
               count :
               0;
}

template <>
bool tryComputeAssumingType<pxr::GfHalf>(OgnMagnitudeDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& magnitude)
    { magnitude = static_cast<pxr::GfHalf>(std::abs(static_cast<float>(input))); };
    return ogn::compute::tryComputeWithArrayBroadcasting<pxr::GfHalf, pxr::GfHalf>(
               db.inputs.input(), db.outputs.magnitude(), functor, count) ?
               count :
               0;
}

template <typename T, size_t N, std::enable_if_t<!std::is_same<T, int>::value && !std::is_same<T, pxr::GfHalf>::value, bool> = true>
bool tryComputeAssumingType(OgnMagnitudeDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& magnitude)
    {
        double acc = 0.0;
        for (size_t i = 0; i < N; ++i)
        {
            acc += static_cast<double>(input[i]) * static_cast<double>(input[i]);
        }
        acc = std::sqrt(acc);
        magnitude = static_cast<T>(acc);
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N], T>(
               db.inputs.input(), db.outputs.magnitude(), functor, count) ?
               count :
               0;
}

template <typename T, size_t N, std::enable_if_t<std::is_same<T, int>::value, bool> = true>
bool tryComputeAssumingType(OgnMagnitudeDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& magnitude)
    {
        double acc = 0.0;
        for (size_t i = 0; i < N; ++i)
        {
            acc += static_cast<double>(input[i]) * static_cast<double>(input[i]);
        }
        acc = std::sqrt(acc);
        magnitude = acc;
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<int[N], double>(
               db.inputs.input(), db.outputs.magnitude(), functor, count) ?
               count :
               0;
}

template <typename T, size_t N, std::enable_if_t<std::is_same<T, pxr::GfHalf>::value, bool> = true>
bool tryComputeAssumingType(OgnMagnitudeDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& magnitude)
    {
        float acc = 0.0f;
        for (size_t i = 0; i < N; ++i)
        {
            acc += static_cast<float>(input[i]) * static_cast<float>(input[i]);
        }
        acc = std::sqrt(acc);
        magnitude = static_cast<pxr::GfHalf>(acc);
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<pxr::GfHalf[N], pxr::GfHalf>(
               db.inputs.input(), db.outputs.magnitude(), functor, count) ?
               count :
               0;
}
} // namespace

class OgnMagnitude
{
public:
    static size_t computeVectorized(OgnMagnitudeDatabase& db, size_t count)
    {
        try
        {
            auto& type = db.inputs.input().type();

            // All possible types excluding ogn::string and bool
            switch (type.baseType)
            {
            case BaseDataType::eDouble:
                switch (type.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<double>(db, count);
                case 2:
                    return tryComputeAssumingType<double, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<double, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<double, 4>(db, count); // quaternion (XYZW), RGBA, etc
                case 9:
                    return tryComputeAssumingType<double, 9>(db, count); // Matrix3f type
                case 16:
                    return tryComputeAssumingType<double, 16>(db, count); // Matrix4f type
                }
                break;
            case BaseDataType::eFloat:
                switch (type.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<float>(db, count);
                case 2:
                    return tryComputeAssumingType<float, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<float, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<float, 4>(db, count); // quaternion (XYZW), RGBA, etc
                }
                break;
            case BaseDataType::eHalf:
                switch (type.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<pxr::GfHalf>(db, count);
                case 2:
                    return tryComputeAssumingType<pxr::GfHalf, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<pxr::GfHalf, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<pxr::GfHalf, 4>(db, count); // quaternion (XYZW), RGBA, etc
                }
                break;
            case BaseDataType::eInt:
                switch (type.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<int32_t>(db, count);
                case 2:
                    return tryComputeAssumingType<int32_t, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<int32_t, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<int32_t, 4>(db, count);
                }
                break;
            case BaseDataType::eUInt:
                switch (type.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<uint32_t>(db, count);
                }
                break;
            case BaseDataType::eInt64:
                switch (type.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<int64_t>(db, count);
                }
                break;
            case BaseDataType::eUInt64:
                switch (type.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<uint64_t>(db, count);
                }
                break;
            case BaseDataType::eUChar:
                switch (type.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<unsigned char>(db, count);
                }
                break;
            default:
                break;
            }
            throw ogn::compute::InputError("Failed to resolve input type");
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError("OgnMagnitude: %s", error.what());
        }
        return 0;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto input = node.iNode->getAttributeByToken(node, inputs::input.token());
        auto magnitude = node.iNode->getAttributeByToken(node, outputs::magnitude.token());
        auto inputType = input.iAttribute->getResolvedType(input);

        // Require input to be resolved before determining magnitude's type
        if (inputType.baseType != BaseDataType::eUnknown)
        {
            if (inputType.baseType == BaseDataType::eInt && inputType.componentCount > 1)
            {
                // int[N] => double
                auto newType = inputType;
                newType.baseType = BaseDataType::eDouble;
                newType.componentCount = 1;
                magnitude.iAttribute->setResolvedType(magnitude, newType);
            }
            else
            {
                // T => T
                // T[N] => T
                std::array<AttributeObj, 2> attrs{ input, magnitude };
                std::array<uint8_t, 2> tupleCounts{ inputType.componentCount, 1 };
                std::array<uint8_t, 2> arrayDepths{ inputType.arrayDepth, inputType.arrayDepth };
                std::array<AttributeRole, 2> rolesBuf{ inputType.role, AttributeRole::eUnknown };
                node.iNode->resolvePartiallyCoupledAttributes(
                    node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
            }
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
// end-compute-helpers
