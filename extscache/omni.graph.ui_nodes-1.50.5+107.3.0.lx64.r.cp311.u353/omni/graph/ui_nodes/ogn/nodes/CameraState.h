// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <carb/Types.h>

#include <pxr/usd/usdGeom/camera.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{

class CameraState
{
    PXR_NS::UsdGeomCamera m_camera;
    const PXR_NS::UsdTimeCode m_timeCode;

public:
    CameraState(PXR_NS::UsdGeomCamera camera, const PXR_NS::UsdTimeCode* time = nullptr);
    ~CameraState() = default;

    void getCameraPosition(carb::Double3& position) const;
    void getCameraTarget(carb::Double3& target) const;

    bool setCameraPosition(const carb::Double3& position, bool rotate);
    bool setCameraTarget(const carb::Double3& target, bool rotate);
};

}
}
}
