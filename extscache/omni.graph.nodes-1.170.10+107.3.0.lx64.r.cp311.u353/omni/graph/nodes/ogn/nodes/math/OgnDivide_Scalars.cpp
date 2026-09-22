// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnDivideHelper.h"

namespace omni
{
namespace graph
{
namespace nodes
{
namespace OGNDivideHelper
{
// AType is a scalar float or double
template <typename AType, typename BType>
bool tryComputeAssumingType(
    ogn::OmniGraphDatabase& db,
    InType const& a,
    InType const& b,
    ResType& result,
    size_t count,
    typename std::enable_if_t<!std::is_integral<AType>::value && !std::is_same<AType, pxr::GfHalf>::value, AType>* = 0)
{
    auto functor = [&](auto const& a, auto const& b, auto& result)
    {
        if (static_cast<double>(b) == 0.0)
        {
            db.logWarning("OgnDivide: Divide by zero encountered");
        }
        result = static_cast<AType>(static_cast<double>(a) / static_cast<double>(b));
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<AType, BType, AType>(a, b, result, functor, count);
}

// AType is a scalar half
template <typename AType, typename BType>
bool tryComputeAssumingType(ogn::OmniGraphDatabase& db,
                            InType const& a,
                            InType const& b,
                            ResType& result,
                            size_t count,
                            typename std::enable_if_t<std::is_same<AType, pxr::GfHalf>::value, AType>* = 0)
{
    auto functor = [&](auto const& a, auto const& b, auto& result)
    {
        if (static_cast<double>(b) == 0.0)
        {
            db.logWarning("OgnDivide: Divide by zero encountered");
        }
        result = static_cast<AType>(static_cast<float>(static_cast<double>(a) / static_cast<double>(b)));
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<AType, BType, AType>(a, b, result, functor, count);
}

// AType is a scalar integral => Force result to be a scalar double
template <typename AType, typename BType>
bool tryComputeAssumingType(ogn::OmniGraphDatabase& db,
                            InType const& a,
                            InType const& b,
                            ResType& result,
                            size_t count,
                            typename std::enable_if_t<std::is_integral<AType>::value, AType>* = 0)
{
    auto functor = [&](auto const& a, auto const& b, auto& result)
    {
        if (static_cast<double>(b) == 0.0)
        {
            db.logWarning("OgnDivide: Divide by zero encountered");
        }
        result = static_cast<double>(a) / static_cast<double>(b);
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<AType, BType, double>(a, b, result, functor, count);
}

bool tryComputeScalars(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count)
{
    if (tryComputeAssumingType<double, double>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<float, double>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<pxr::GfHalf, double>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int32_t, double>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int64_t, double>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<unsigned char, double>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint32_t, double>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint64_t, double>(db, a, b, result, count))
        return true;

    if (tryComputeAssumingType<double, float>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<float, float>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<pxr::GfHalf, float>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int32_t, float>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int64_t, float>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<unsigned char, float>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint32_t, float>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint64_t, float>(db, a, b, result, count))
        return true;

    if (tryComputeAssumingType<double, pxr::GfHalf>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<float, pxr::GfHalf>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<pxr::GfHalf, pxr::GfHalf>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int32_t, pxr::GfHalf>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int64_t, pxr::GfHalf>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<unsigned char, pxr::GfHalf>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint32_t, pxr::GfHalf>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint64_t, pxr::GfHalf>(db, a, b, result, count))
        return true;

    if (tryComputeAssumingType<double, int32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<float, int32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<pxr::GfHalf, int32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int32_t, int32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int64_t, int32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<unsigned char, int32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint32_t, int32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint64_t, int32_t>(db, a, b, result, count))
        return true;

    if (tryComputeAssumingType<double, int64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<float, int64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<pxr::GfHalf, int64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int32_t, int64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int64_t, int64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<unsigned char, int64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint32_t, int64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint64_t, int64_t>(db, a, b, result, count))
        return true;

    if (tryComputeAssumingType<double, unsigned char>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<float, unsigned char>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<pxr::GfHalf, unsigned char>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int32_t, unsigned char>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int64_t, unsigned char>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<unsigned char, unsigned char>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint32_t, unsigned char>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint64_t, unsigned char>(db, a, b, result, count))
        return true;

    if (tryComputeAssumingType<double, uint32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<float, uint32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<pxr::GfHalf, uint32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int32_t, uint32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int64_t, uint32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<unsigned char, uint32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint32_t, uint32_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint64_t, uint32_t>(db, a, b, result, count))
        return true;

    if (tryComputeAssumingType<double, uint64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<float, uint64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<pxr::GfHalf, uint64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int32_t, uint64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int64_t, uint64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<unsigned char, uint64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint32_t, uint64_t>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<uint64_t, uint64_t>(db, a, b, result, count))
        return true;

    return false;
}

} // namespace OGNDivideHelper
} // namespace nodes
} // namespace graph
} // namespace omni
