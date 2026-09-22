// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <pxr/imaging/hd/changeTracker.h>
#include <pxr/imaging/hd/camera.h>
#include <pxr/base/vt/value.h>
#include <pxr/base/tf/token.h>

#include <map>

namespace usdrt
{
namespace hydra
{

enum HdOmniSensorDirtyBits : PXR_NS::HdDirtyBits
{
    OmniSensorDirtyClean = 0,
    OmniSensorDirtyAttributes = 1 << 0,
    OmniSensorDirtyTransform = 1 << 1,
    OmniSensorDirtyVisibility = 1 << 2,
    OmniSensorDirtyAll = OmniSensorDirtyAttributes | OmniSensorDirtyTransform | OmniSensorDirtyVisibility,
};

enum HdOmniLensDistortionDirtyBits : PXR_NS::HdDirtyBits
{
    OmniLensDistortionDirtyAttributes = PXR_NS::HdCamera::DirtyWindowPolicy << 1
};

using CameraAttributesMap = std::map<PXR_NS::TfToken, PXR_NS::VtValue>;

} // namespace hydra
} // namespace usdrt
