// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/usd/UsdTypes.h>

#include <functional>

namespace rtx
{
namespace resourcemanager
{
class RpResource;
}
}

namespace omni
{
namespace usd
{

typedef size_t ViewPickingId;
typedef int32_t ViewportHandle;
static constexpr int32_t kInvalidViewportHandle = -1;

using OnPickingCompleteFn = std::function<void(const char* path, const carb::Double3* worldPos)>;

struct Picking
{
    int left;
    int top;
    int right;
    int bottom;

    enum class Mode
    {
        eNone,
        eResetAndSelect,
        eMergeSelection,
        eInvertSelection,
        eQuery, /// request that do not change selection
        eTrack, /// track mouse position, picking request is allowed.
        eTrackBlocking, /// track mouse position, picking request is blocked.
    } mode;

    ViewPickingId pickingId;
    bool queryAddsOutline; // Used only when mode == eQuery
    OnPickingCompleteFn onCompleteFn;
};

struct RenderVar
{
    const char* name;
    union {
        void* rawResource;
        rtx::resourcemanager::RpResource* rpResource;
    };
    bool isRpResource;
};

}
}
