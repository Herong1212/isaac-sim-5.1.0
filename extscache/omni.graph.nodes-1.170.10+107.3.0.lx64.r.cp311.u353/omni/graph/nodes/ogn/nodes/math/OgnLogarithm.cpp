// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnLogarithmDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>
#include <math.h>

namespace omni
{
namespace graph
{
namespace nodes
{

// unnamed namespace to avoid multiple declaration when linking
namespace
{
// Used for scalar inputs resolved for decimal types other than Half
template <typename T>
size_t tryComputeAssumingType(OgnLogarithmDatabase& db, size_t count)
{
    auto functor = [&](auto const& value, auto const& base, auto& result)
    {
        if (base <= 0 || base == 1.0 || value <= 0)
            throw ogn::compute::InputError("Domain error, base & value must be > 0 & base != 1.");

        result = std::log(value) / std::log(static_cast<T>(base));
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, double, T>(
               db.inputs.value(), db.inputs.base(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// Used for scalar inputs resolved as Half
template <>
size_t tryComputeAssumingType<pxr::GfHalf>(OgnLogarithmDatabase& db, size_t count)
{
    auto functor = [&](auto const& value, auto const& base, auto& result)
    {
        if (base <= 0 || base == 1.0 || value <= 0)
            throw ogn::compute::InputError("Domain error, base & value must be > 0 & base != 1.");

        result = std::log(value) / std::log(static_cast<pxr::GfHalf>(static_cast<float>(base)));
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<pxr::GfHalf, double, pxr::GfHalf>(
               db.inputs.value(), db.inputs.base(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// Used for scalar inputs resolved for integer types
template <typename T, typename M>
size_t tryComputeAssumingType(OgnLogarithmDatabase& db, size_t count)
{
    auto functor = [&](auto const& value, auto const& base, auto& result)
    {
        if (base <= 0 || base == 1.0 || value <= 0)
            throw ogn::compute::InputError("Domain error, base & value must be > 0 & base != 1.");

        result = static_cast<M>(std::log(value) / std::log(static_cast<T>(base)));
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, double, M>(
               db.inputs.value(), db.inputs.base(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// Used for tuple inputs resolved for decimal types other than Half
template <typename T, size_t N, std::enable_if_t<!std::is_same<T, pxr::GfHalf>::value, bool> = true>
size_t tryComputeAssumingType(OgnLogarithmDatabase& db, size_t count)
{
    auto functor = [&](auto const& value, auto const& base, auto& result)
    {
        if (base <= 0 || base == 1.0 || value <= 0)
            throw ogn::compute::InputError("Domain error, base & value must be > 0 & base != 1.");

        result = std::log(value) / std::log(static_cast<T>(base));
    };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T, double, T>(
               db.inputs.value(), db.inputs.base(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// // Used for tuple inputs resolved as Half
template <typename T, size_t N, std::enable_if_t<std::is_same<T, pxr::GfHalf>::value, bool> = true>
size_t tryComputeAssumingType(OgnLogarithmDatabase& db, size_t count)
{
    auto functor = [&](auto const& value, auto const& base, auto& result)
    {
        if (base <= 0 || base == 1.0 || value <= 0)
            throw ogn::compute::InputError("Domain error, base & value must be > 0 & base != 1.");

        result = std::log(value) / std::log(static_cast<pxr::GfHalf>(static_cast<float>(base)));
    };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T, double, T>(
               db.inputs.value(), db.inputs.base(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// Used for tuple inputs resolved for integer types
template <typename T, size_t N, typename M>
size_t tryComputeAssumingType(OgnLogarithmDatabase& db, size_t count)
{
    auto functor = [&](auto const& value, auto const& base, auto& result)
    {
        if (base <= 0 || base == 1.0 || value <= 0)
            throw ogn::compute::InputError("Domain error, base & value must be > 0 & base != 1.");

        result = static_cast<M>(std::log(value) / std::log(static_cast<T>(base)));
    };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T, double, M>(
               db.inputs.value(), db.inputs.base(), db.outputs.result(), functor, count) ?
               count :
               0;
}
} // unnamed namespace

class OgnLogarithm
{
public:
    static size_t computeVectorized(OgnLogarithmDatabase& db, size_t count)
    {
        try
        {
            const auto& inputType = db.inputs.value().type();
            switch (inputType.baseType)
            {
            case BaseDataType::eDouble:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<double>(db, count);
                case 2:
                    return tryComputeAssumingType<double, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<double, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<double, 4>(db, count);
                case 9:
                    return tryComputeAssumingType<double, 9>(db, count);
                case 16:
                    return tryComputeAssumingType<double, 16>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eFloat:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<float>(db, count);
                case 2:
                    return tryComputeAssumingType<float, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<float, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<float, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eHalf:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<pxr::GfHalf>(db, count);
                case 2:
                    return tryComputeAssumingType<pxr::GfHalf, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<pxr::GfHalf, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<pxr::GfHalf, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<int, double>(db, count);
                case 2:
                    return tryComputeAssumingType<int, 2, double>(db, count);
                case 3:
                    return tryComputeAssumingType<int, 3, double>(db, count);
                case 4:
                    return tryComputeAssumingType<int, 4, double>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt64:
                return tryComputeAssumingType<int64_t, double>(db, count);
            case BaseDataType::eUChar:
                return tryComputeAssumingType<uchar, double>(db, count);
            case BaseDataType::eUInt:
                return tryComputeAssumingType<uint32_t, double>(db, count);
            case BaseDataType::eUInt64:
                return tryComputeAssumingType<uint64_t, double>(db, count);
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
        auto value = node.iNode->getAttributeByToken(node, inputs::value.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto valueType = value.iAttribute->getResolvedType(value);

        switch (valueType.baseType)
        {
        case BaseDataType::eInt:
        case BaseDataType::eInt64:
        case BaseDataType::eUChar:
        case BaseDataType::eUInt:
        case BaseDataType::eUInt64:
            result.iAttribute->setResolvedType(
                result, Type(BaseDataType::eDouble, valueType.componentCount, valueType.arrayDepth, valueType.role));
            break;
        case BaseDataType::eUnknown:
            result.iAttribute->setResolvedType(result, Type(BaseDataType::eUnknown));
            break;
        default:
            std::array<AttributeObj, 2> attrs{ value, result };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
            break;
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
