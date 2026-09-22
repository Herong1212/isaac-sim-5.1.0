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
template <size_t N>
bool _tryCompute(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count)
{
    if (tryComputeAssumingType<double, double, N>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<double, float, N>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<double, pxr::GfHalf, N>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<double, int32_t, N>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<double, int64_t, N>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<double, unsigned char, N>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<double, uint32_t, N>(db, a, b, result, count))
        return true;
    if (tryComputeAssumingType<double, uint64_t, N>(db, a, b, result, count))
        return true;
    return false;
}

bool tryComputeMatrices(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count)
{
    // Matrix3f type
    if (_tryCompute<9>(db, a, b, result, count))
        return true;

    // Matrix4f type
    if (_tryCompute<16>(db, a, b, result, count))
        return true;

    return false;
}

} // namespace OGNDivideHelper
} // namespace nodes
} // namespace graph
} // namespace omni
