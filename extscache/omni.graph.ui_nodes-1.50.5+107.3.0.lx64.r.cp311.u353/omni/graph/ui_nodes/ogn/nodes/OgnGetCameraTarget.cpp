// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include <OgnGetCameraTargetDatabase.h>

#include "CameraState.h"
#include "NodeUtils.h"
// clang-format on


namespace omni
{
namespace graph
{
namespace ui_nodes
{

class OgnGetCameraTarget
{
public:
    static bool compute(OgnGetCameraTargetDatabase& db)
    {
        PXR_NS::UsdPrim prim = getPrimFromPathOrRelationship(db, OgnGetCameraTargetAttributes::inputs::prim.m_token);
        if (!prim)
            return false;

        auto camera = PXR_NS::UsdGeomCamera(prim);
        if (!camera)
            return true;

        CameraState cameraState(std::move(camera));

        carb::Double3 target;
        cameraState.getCameraTarget(target);

        carb::Double3& targetAttrib = reinterpret_cast<carb::Double3&>(db.outputs.target());
        targetAttrib = target;

        return true;
    }
};

REGISTER_OGN_NODE()
}
}
}
