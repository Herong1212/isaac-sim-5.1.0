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
bool tryComputeTuple4(ogn::OmniGraphDatabase& db, InType const& a, InType const& b, ResType& result, size_t count)
{
    return _tryComputeTuple<4>(db, a, b, result, count);
}

} // namespace OGNDivideHelper
} // namespace nodes
} // namespace graph
} // namespace omni
