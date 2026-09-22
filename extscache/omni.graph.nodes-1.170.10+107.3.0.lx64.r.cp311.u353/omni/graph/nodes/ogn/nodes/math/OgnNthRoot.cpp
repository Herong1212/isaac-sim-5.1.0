// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnNthRootDatabase.h>
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

/**
 * Helper functions to try doing an addition operation on two input attributes.
 *   We assume the runtime attributes have type T and the other one is double.
 *   The first input is either an array or a singular value, and the second input is a single double value
 *
 * @param db: database object
 * @return True if we can get a result properly, false if not
 */

/**
 * Used when input type is resolved as Half
 */
bool tryComputeAssumingType(OgnNthRootDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        double res;
        switch (b)
        {
        case 3:
            res = std::cbrt(a);
            break;
        case 2:
            res = std::sqrt(a);
            break;
        default:
            res = std::pow(static_cast<double>(static_cast<float>(a)), static_cast<double>(1.0 / static_cast<double>(b)));
            break;
        }
        result = static_cast<pxr::GfHalf>(static_cast<float>(res));
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<pxr::GfHalf, int, pxr::GfHalf>(
        db.inputs.value(), db.inputs.nthRoot(), db.outputs.result(), functor, count);
}

/**
 * Used when input type is resolved as non-int numeric type other than Half
 */
template <typename T>
bool tryComputeAssumingType(OgnNthRootDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        switch (b)
        {
        case 3:
            result = static_cast<T>(std::cbrt(a));
            break;
        case 2:
            result = static_cast<T>(std::sqrt(a));
            break;
        default:
            result = static_cast<T>(std::pow(a, 1.0 / static_cast<double>(b)));
            break;
        }
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, int, T>(
        db.inputs.value(), db.inputs.nthRoot(), db.outputs.result(), functor, count);
}

/**
 * Used when input type is resolved as int type
 */
template <typename T, typename M>
bool tryComputeAssumingType(OgnNthRootDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        switch (b)
        {
        case 3:
            result = static_cast<M>(std::cbrt(a));
            break;
        case 2:
            result = static_cast<M>(std::sqrt(a));
            break;
        default:
            result = static_cast<M>(std::pow(a, 1.0 / static_cast<double>(b)));
            break;
        }
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, int, M>(
        db.inputs.value(), db.inputs.nthRoot(), db.outputs.result(), functor, count);
}

/**
 * Used when input type is resolved as Half
 */
template <size_t N>
bool tryComputeAssumingType(OgnNthRootDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        double res;
        switch (b)
        {
        case 3:
            res = std::cbrt(a);
            break;
        case 2:
            res = std::sqrt(a);
            break;
        default:
            res = std::pow(static_cast<double>(static_cast<float>(a)), static_cast<double>(1.0 / static_cast<double>(b)));
            break;
        }
        result = static_cast<pxr::GfHalf>(static_cast<float>(res));
    };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, pxr::GfHalf, int, pxr::GfHalf>(
        db.inputs.value(), db.inputs.nthRoot(), db.outputs.result(), functor, count);
}

/**
 * Used when input type is resolved as any non-int numeric type other than Half
 */
template <typename T, size_t N>
bool tryComputeAssumingType(OgnNthRootDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        switch (b)
        {
        case 3:
            result = static_cast<T>(std::cbrt(a));
            break;
        case 2:
            result = static_cast<T>(std::sqrt(a));
            break;
        default:
            result = static_cast<T>(std::pow(a, 1.0 / static_cast<double>(b)));
            break;
        }
    };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T, int, T>(
        db.inputs.value(), db.inputs.nthRoot(), db.outputs.result(), functor, count);
}

/**
 * Used when input type is resolved as int type
 */
template <typename T, size_t N, typename M>
bool tryComputeAssumingType(OgnNthRootDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        switch (b)
        {
        case 3:
            result = static_cast<M>(std::cbrt(a));
            break;
        case 2:
            result = static_cast<M>(std::sqrt(a));
            break;
        default:
            result = static_cast<M>(std::pow(a, 1.0 / static_cast<double>(b)));
            break;
        }
    };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T, int, M>(
        db.inputs.value(), db.inputs.nthRoot(), db.outputs.result(), functor, count);
}
} // namespace

class OgnNthRoot
{
public:
    static bool computeVectorized(OgnNthRootDatabase& db, size_t count)
    {

        try
        {
            const auto& vType = db.inputs.value().type();
            switch (vType.componentCount)
            {
            case 1:
                // All possible types excluding ogn::string and bool
                // scalars
                switch (vType.baseType)
                {
                case BaseDataType::eDouble:
                    return tryComputeAssumingType<double>(db, count);
                case BaseDataType::eHalf: // Specifically for pxr::GfHalf
                    return tryComputeAssumingType(db, count);
                case BaseDataType::eFloat:
                    return tryComputeAssumingType<float>(db, count);
                case BaseDataType::eInt:
                    return tryComputeAssumingType<int32_t, double>(db, count);
                case BaseDataType::eInt64:
                    return tryComputeAssumingType<int64_t, double>(db, count);
                case BaseDataType::eUChar:
                    return tryComputeAssumingType<unsigned char, double>(db, count);
                case BaseDataType::eUInt:
                    return tryComputeAssumingType<uint32_t, double>(db, count);
                case BaseDataType::eUInt64:
                    return tryComputeAssumingType<uint64_t, double>(db, count);
                default:
                    break;
                }
            case 2:
                switch (vType.baseType)
                {
                case BaseDataType::eInt:
                    return tryComputeAssumingType<int32_t, 2, double>(db, count);
                case BaseDataType::eDouble:
                    return tryComputeAssumingType<double, 2>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeAssumingType<float, 2>(db, count);
                case BaseDataType::eHalf:
                    return tryComputeAssumingType<2>(db, count);
                default:
                    break;
                }
            case 3:
                switch (vType.baseType)
                {
                case BaseDataType::eInt:
                    return tryComputeAssumingType<int32_t, 3, double>(db, count);
                case BaseDataType::eDouble:
                    return tryComputeAssumingType<double, 3>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeAssumingType<float, 3>(db, count);
                case BaseDataType::eHalf:
                    return tryComputeAssumingType<3>(db, count);
                default:
                    break;
                }
            case 4: // quaternion (IJKR), RGBA, etc
                switch (vType.baseType)
                {
                case BaseDataType::eInt:
                    return tryComputeAssumingType<int32_t, 4, double>(db, count);
                case BaseDataType::eDouble:
                    return tryComputeAssumingType<double, 4>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeAssumingType<float, 4>(db, count);
                case BaseDataType::eHalf:
                    return tryComputeAssumingType<4>(db, count);
                default:
                    break;
                }
            case 9: // Matrix3f type
                if (vType.baseType == BaseDataType::eDouble)
                {
                    return tryComputeAssumingType<double, 9>(db, count);
                }
            case 16: // Matrix4f type
                if (vType.baseType == BaseDataType::eDouble)
                {
                    return tryComputeAssumingType<double, 16>(db, count);
                }
            }
            throw ogn::compute::InputError("Failed to resolve input types");
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return false;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto value = node.iNode->getAttributeByToken(node, inputs::value.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto valueType = value.iAttribute->getResolvedType(value);
        Type newType(BaseDataType::eDouble, valueType.componentCount, valueType.arrayDepth, valueType.role);

        // Require inputs to be resolved before determining sum's type
        switch (valueType.baseType)
        {
        case BaseDataType::eUChar:
        case BaseDataType::eInt:
        case BaseDataType::eUInt:
        case BaseDataType::eInt64:
        case BaseDataType::eUInt64:
            result.iAttribute->setResolvedType(result, newType);
            break;
        case BaseDataType::eUnknown:
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
