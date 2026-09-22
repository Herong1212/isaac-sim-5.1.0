// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/ogn/UsdTypes.h>
#include <omni/graph/core/ogn/Database.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>


namespace omni
{
namespace graph
{
namespace nodes
{
namespace OGNDivideHelper
{
using InType = ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu>;
using ResType = ogn::RuntimeAttribute<ogn::kOgnOutput, ogn::kCpu>;

// Allow (AType[N] / BType) and (AType[N] / BType[N]) but not (AType / BType[N])
template <typename AType, typename BType, typename CType, size_t N, typename Functor>
bool tryComputeWithLimitedTupleBroadcasting(InType const& a, InType const& b, ResType& result, Functor functor, size_t count)
{
    if (ogn::compute::tryComputeWithArrayBroadcasting<AType[N], BType[N], CType[N]>(
            a, b, result,
            [&](auto const& a, auto const& b, auto& result)
            {
                for (size_t i = 0; i < N; i++)
                    functor(a[i], b[i], result[i]);
            },
            count))
        return true;
    else if (ogn::compute::tryComputeWithArrayBroadcasting<AType[N], BType, CType[N]>(
                 a, b, result,
                 [&](auto const& a, auto const& b, auto& result)
                 {
                     for (size_t i = 0; i < N; i++)
                         functor(a[i], b, result[i]);
                 },
                 count))
        return true;
    return false;
}

// AType is a vector of float's or double's
template <typename AType, typename BType, size_t N>
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
    return tryComputeWithLimitedTupleBroadcasting<AType, BType, AType, N>(a, b, result, functor, count);
}

// AType is a vector of half's
template <typename AType, typename BType, size_t N>
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
    return tryComputeWithLimitedTupleBroadcasting<AType, BType, AType, N>(a, b, result, functor, count);
}

// AType is a vector of integrals => Force result to be a vector of doubles
template <typename AType, typename BType, size_t N>
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
    return tryComputeWithLimitedTupleBroadcasting<AType, BType, double, N>(a, b, result, functor, count);
}

template <typename T, size_t N>
bool _tryComputeAssuming(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count)
{
    if (tryComputeAssumingType<double, T, N>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<float, T, N>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<pxr::GfHalf, T, N>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<int32_t, T, N>(db, a, b, result, count))
        return true;
    return false;
}

template <size_t N>
bool _tryComputeTuple(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count)
{
    if (_tryComputeAssuming<double, N>(db, a, b, result, count))
        return true;
    if (_tryComputeAssuming<float, N>(db, a, b, result, count))
        return true;
    if (_tryComputeAssuming<pxr::GfHalf, N>(db, a, b, result, count))
        return true;
    if (_tryComputeAssuming<int32_t, N>(db, a, b, result, count))
        return true;
    if (_tryComputeAssuming<int64_t, N>(db, a, b, result, count))
        return true;
    if (_tryComputeAssuming<unsigned char, N>(db, a, b, result, count))
        return true;
    if (_tryComputeAssuming<uint32_t, N>(db, a, b, result, count))
        return true;
    if (_tryComputeAssuming<uint64_t, N>(db, a, b, result, count))
        return true;
    return false;
}

bool tryComputeScalars(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count);
bool tryComputeTuple2(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count);
bool tryComputeTuple3(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count);
bool tryComputeTuple4(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count);
bool tryComputeMatrices(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count);


} // namespace OGNDivideHelper
} // namespace nodes
} // namespace graph
} // namespace omni
