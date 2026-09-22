// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnIncrementDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>

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
bool tryComputeAssumingType(OgnIncrementDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result) { result = a + static_cast<float>(b); };
    return ogn::compute::tryComputeWithArrayBroadcasting<pxr::GfHalf, double, pxr::GfHalf>(
        db.inputs.value(), db.inputs.increment(), db.outputs.result(), functor, count);
}
/**
 * Used when input type is resolved as any numeric type other than Half
 */
template <typename T>
bool tryComputeAssumingType(OgnIncrementDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result) { result = a + static_cast<T>(b); };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, double, T>(
        db.inputs.value(), db.inputs.increment(), db.outputs.result(), functor, count);
}
/**
 * Used when input type is resolved as Half
 */
template <size_t N>
bool tryComputeAssumingType(OgnIncrementDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result) { result = a + static_cast<float>(b); };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, pxr::GfHalf, double, pxr::GfHalf>(
        db.inputs.value(), db.inputs.increment(), db.outputs.result(), functor, count);
}
/**
 * Used when input type is resolved as any numeric type other than Half
 */
template <typename T, size_t N>
bool tryComputeAssumingType(OgnIncrementDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result) { result = a + static_cast<T>(b); };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T, double, T>(
        db.inputs.value(), db.inputs.increment(), db.outputs.result(), functor, count);
}
} // namespace

class OgnIncrement
{
public:
    static size_t computeVectorized(OgnIncrementDatabase& db, size_t count)
    {
        auto& inputType = db.inputs.value().type();
        // Compute the components, if the types are all resolved.
        try
        {
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
                default:
                    break;
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
                default:
                    break;
                }
            case BaseDataType::eHalf:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType(db, count);
                case 2:
                    return tryComputeAssumingType<2>(db, count);
                case 3:
                    return tryComputeAssumingType<3>(db, count);
                case 4:
                    return tryComputeAssumingType<4>(db, count);
                default:
                    break;
                }
            case BaseDataType::eInt:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<int32_t>(db, count);
                case 2:
                    return tryComputeAssumingType<int32_t, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<int32_t, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<int32_t, 4>(db, count);
                default:
                    break;
                };
            case BaseDataType::eInt64:
                return tryComputeAssumingType<int64_t>(db, count);
            case BaseDataType::eUChar:
                return tryComputeAssumingType<unsigned char>(db, count);
            case BaseDataType::eUInt:
                return tryComputeAssumingType<uint32_t>(db, count);
            case BaseDataType::eUInt64:
                return tryComputeAssumingType<uint64_t>(db, count);
            default:
                break;
            }

            db.logWarning("Failed to resolve input types");
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto value = node.iNode->getAttributeByToken(node, inputs::value.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto valueType = value.iAttribute->getResolvedType(value);

        // Require inputs to be resolved before determining sum's type
        if (valueType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 2> attrs{ value, result };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
