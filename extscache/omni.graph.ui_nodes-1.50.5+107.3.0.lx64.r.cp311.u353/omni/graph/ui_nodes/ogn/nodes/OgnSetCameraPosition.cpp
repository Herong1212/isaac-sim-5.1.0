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

#include <OgnSetCameraPositionDatabase.h>

#include "CameraState.h"
#include "NodeUtils.h"
// clang-format on


namespace omni
{
namespace graph
{
namespace ui_nodes
{

class OgnSetCameraPosition
{
public:
    static bool compute(OgnSetCameraPositionDatabase& db)
    {
        PXR_NS::UsdPrim prim = getPrimFromPathOrRelationship(db, OgnSetCameraPositionAttributes::inputs::prim.m_token);
        if (!prim)
            return false;

        auto position = db.inputs.position();
        auto rotate = db.inputs.rotate();

        auto camera = PXR_NS::UsdGeomCamera(prim);
        if (!camera)
            return false;

        CameraState cameraState(std::move(camera));
        bool ok = cameraState.setCameraPosition({ position[0], position[1], position[2] }, rotate);
        if (!ok)
        {
            db.logError("Could not set position for camera %s", prim.GetPath().GetText());
        }

        db.outputs.execOut() = kExecutionAttributeStateEnabled;

        return true;
    }
};

REGISTER_OGN_NODE()
}
}
}
