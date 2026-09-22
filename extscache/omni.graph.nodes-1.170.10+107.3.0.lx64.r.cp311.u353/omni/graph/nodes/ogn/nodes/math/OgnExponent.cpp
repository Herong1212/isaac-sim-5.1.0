// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnExponentDatabase.h>
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
//
bool tryComputeAssumingScalarHalf(OgnExponentDatabase& db, size_t count)
{
    auto functor = [](auto const& base, auto const& exp, auto& result)
    {
        result =
            static_cast<pxr::GfHalf>(static_cast<float>(std::pow(static_cast<double>(static_cast<float>(base)), exp)));
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<pxr::GfHalf, int, pxr::GfHalf>(
               db.inputs.base(), db.inputs.exponent(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <typename T, typename M>
bool tryComputeAssumingScalarType(OgnExponentDatabase& db, size_t count)
{
    auto functor = [](auto const& base, auto const& exp, auto& result) { result = static_cast<M>(std::pow(base, exp)); };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, int, M>(
               db.inputs.base(), db.inputs.exponent(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <size_t N>
bool tryComputeAssumingTupleHalf(OgnExponentDatabase& db, size_t count)
{
    auto functor = [](auto const& base, auto const& exp, auto& result)
    {
        result =
            static_cast<pxr::GfHalf>(static_cast<float>(std::pow(static_cast<double>(static_cast<float>(base)), exp)));
    };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, pxr::GfHalf, int, pxr::GfHalf>(
               db.inputs.base(), db.inputs.exponent(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <typename T, size_t N, typename M>
bool tryComputeAssumingTupleType(OgnExponentDatabase& db, size_t count)
{
    auto functor = [](auto const& base, auto const& exp, auto& result) { result = static_cast<M>(std::pow(base, exp)); };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T, int, M>(
               db.inputs.base(), db.inputs.exponent(), db.outputs.result(), functor, count) ?
               count :
               0;
}
} // unnamed namespace

class OgnExponent
{
public:
    static size_t computeVectorized(OgnExponentDatabase& db, size_t count)
    {
        try
        {
            const auto& bType = db.inputs.base().type();
            switch (bType.componentCount)
            {
            case 1:
                switch (bType.baseType)
                {
                case BaseDataType::eInt:
                    return tryComputeAssumingScalarType<int32_t, double>(db, count);
                case BaseDataType::eInt64:
                    return tryComputeAssumingScalarType<int64_t, double>(db, count);
                case BaseDataType::eUInt:
                    return tryComputeAssumingScalarType<uint32_t, double>(db, count);
                case BaseDataType::eUInt64:
                    return tryComputeAssumingScalarType<uint64_t, double>(db, count);
                case BaseDataType::eUChar:
                    return tryComputeAssumingScalarType<unsigned char, double>(db, count);
                case BaseDataType::eHalf:
                    return tryComputeAssumingScalarHalf(db, count);
                case BaseDataType::eDouble:
                    return tryComputeAssumingScalarType<double, double>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeAssumingScalarType<float, float>(db, count);
                default:
                    break;
                }
            case 2:
                switch (bType.baseType)
                {
                case BaseDataType::eInt:
                    return tryComputeAssumingTupleType<int32_t, 2, double>(db, count);
                case BaseDataType::eDouble:
                    return tryComputeAssumingTupleType<double, 2, double>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeAssumingTupleType<float, 2, float>(db, count);
                case BaseDataType::eHalf:
                    return tryComputeAssumingTupleHalf<2>(db, count);
                default:
                    break;
                }
            case 3:
                switch (bType.baseType)
                {
                case BaseDataType::eInt:
                    return tryComputeAssumingTupleType<int32_t, 3, double>(db, count);
                case BaseDataType::eDouble:
                    return tryComputeAssumingTupleType<double, 3, double>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeAssumingTupleType<float, 3, float>(db, count);
                case BaseDataType::eHalf:
                    return tryComputeAssumingTupleHalf<3>(db, count);
                default:
                    break;
                }
            case 4:
                switch (bType.baseType)
                {
                case BaseDataType::eInt:
                    return tryComputeAssumingTupleType<int32_t, 4, double>(db, count);
                case BaseDataType::eDouble:
                    return tryComputeAssumingTupleType<double, 4, double>(db, count);
                case BaseDataType::eFloat:
                    return tryComputeAssumingTupleType<float, 4, float>(db, count);
                case BaseDataType::eHalf:
                    return tryComputeAssumingTupleHalf<4>(db, count);
                default:
                    break;
                }
            case 9:
                if (bType.baseType == BaseDataType::eDouble)
                {
                    return tryComputeAssumingTupleType<double, 9, double>(db, count);
                }
            case 16:
                if (bType.baseType == BaseDataType::eDouble)
                {
                    return tryComputeAssumingTupleType<double, 16, double>(db, count);
                }
            }
            throw ogn::compute::InputError("Failed to resolve input types");
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto base = node.iNode->getAttributeByToken(node, inputs::base.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto bType = base.iAttribute->getResolvedType(base);
        Type newType(BaseDataType::eDouble, bType.componentCount, bType.arrayDepth, bType.role);

        if (bType.baseType != BaseDataType::eUnknown)
        {
            switch (bType.baseType)
            {
            case BaseDataType::eUChar:
            case BaseDataType::eInt:
            case BaseDataType::eUInt:
            case BaseDataType::eInt64:
            case BaseDataType::eUInt64:
                result.iAttribute->setResolvedType(result, newType);
                break;
            default:
                std::array<AttributeObj, 2> attrs{ base, result };
                node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
                break;
            }
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
