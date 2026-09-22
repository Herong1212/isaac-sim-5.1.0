// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <carb/logging/Log.h>

namespace omni
{
namespace graph
{
namespace nodes
{

template <typename T, typename F>
static size_t tryComputeOperator(F&& f, T t, size_t count)
{
    try
    {
        return f(t, count);
    }
    // LCOV_EXCL_START
    catch (std::exception& error)
    {
        t.logError("Could not perform function: %s", error.what());
    }
    return 0;
    // LCOV_EXCL_STOP
}
}
}
}
