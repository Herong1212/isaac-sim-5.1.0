// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

// ====================================================================================================
/*   _____          _   _       _     _    _
    |  __ \        | \ | |     | |   | |  | |
    | |  | | ___   |  \| | ___ | |_  | |  | |___  ___
    | |  | |/ _ \  | . ` |/ _ \| __| | |  | / __|/ _ \
    | |__| | (_) | | |\  | (_) | |_  | |__| \__ \  __/
    |_____/ \___/  |_| \_|\___/ \__|  \____/|___/\___|

This is a temporary interface that can change at any time.
*/
// ====================================================================================================

#include <carb/Interface.h>

#include <cstdint>

namespace omni
{
namespace graph
{
namespace core
{
using DirtyIDType = uint64_t;
constexpr DirtyIDType kInvalidDirtyID = ~static_cast<DirtyIDType>(0);

struct IDirtyID
{
    CARB_PLUGIN_INTERFACE("omni::graph::core::IDirtyID", 1, 0)

    /**
     * @return The next dirty ID, atomically incrementing the counter inside.
     */
    DirtyIDType(CARB_ABI* getNextDirtyID)() = nullptr;
};

template <typename PREVIOUS_T>
bool checkDirtyIDChanged(PREVIOUS_T& previousID, DirtyIDType newID)
{
    if (newID != previousID)
    {
        previousID = newID;
        return true;
    }
    // Equal, but if they're invalid, still treat them as changed
    return (newID == kInvalidDirtyID);
}

}
}
}
