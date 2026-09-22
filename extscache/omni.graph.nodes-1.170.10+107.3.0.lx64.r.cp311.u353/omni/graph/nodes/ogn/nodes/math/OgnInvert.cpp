// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnInvertDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
// Used for scalar inputs resolved for decimal types
template <typename T>
size_t tryComputeAssumingType(OgnInvertDatabase& db, size_t count)
{
    auto functor = [](auto const& value, auto& result) { result = value != 0 ? 1 / value : 0; };
    return ogn::compute::tryComputeWithArrayBroadcasting<T>(db.inputs.value(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// Used for scalar inputs resolved for integer types
template <typename T, typename M>
size_t tryComputeAssumingType(OgnInvertDatabase& db, size_t count)
{
    auto functor = [](auto const& value, auto& result) { result = value != 0 ? 1 / static_cast<M>(value) : 0; };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, M>(db.inputs.value(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// Used for tuple inputs resolved for decimal types
template <typename T, size_t N>
size_t tryComputeAssumingType(OgnInvertDatabase& db, size_t count)
{
    auto functor = [](auto const& value, auto& result) { result = value != 0 ? 1 / value : 0; };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T>(db.inputs.value(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// Used for tuple inputs resolved for integer types
template <typename T, size_t N, typename M>
size_t tryComputeAssumingType(OgnInvertDatabase& db, size_t count)
{
    auto functor = [](auto const& value, auto& result) { result = value != 0 ? 1 / static_cast<M>(value) : 0; };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T, M>(db.inputs.value(), db.outputs.result(), functor, count) ?
               count :
               0;
}
} // namespace

class OgnInvert
{
public:
    static size_t computeVectorized(OgnInvertDatabase& db, size_t count)
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
// end-compute-helpers
