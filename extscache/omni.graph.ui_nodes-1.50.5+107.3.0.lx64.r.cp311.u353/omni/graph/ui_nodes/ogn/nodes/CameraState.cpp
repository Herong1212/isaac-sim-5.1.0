// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "CameraState.h"

#include <carb/settings/ISettings.h>

// clang-format off
#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/sdf/valueTypeName.h>
#include <omni/graph/core/PostUsdInclude.h>
// clang-format on

#include <omni/timeline/ITimeline.h>
#include <omni/usd/UsdUtils.h>


using namespace omni::graph::ui_nodes;

static const PXR_NS::TfToken kCenterOfInterest("omni:kit:centerOfInterest");

static bool checkPositionAndTarget(const PXR_NS::GfVec3d& position, const PXR_NS::GfVec3d& target)
{
    // If position and target are coincident, fail
    if ((position - target).GetLengthSq() <= std::numeric_limits<double>::epsilon())
    {
        return false;
    }
    return true;
}

static PXR_NS::GfVec3d getCameraUp(PXR_NS::UsdStageRefPtr stage)
{
    PXR_NS::TfToken upAxis = PXR_NS::UsdGeomGetStageUpAxis(stage);
    if (upAxis == PXR_NS::UsdGeomTokens->x)
    {
        return { 1, 0, 0 };
    }
    if (upAxis == PXR_NS::UsdGeomTokens->z)
    {
        return { 0, 0, 1 };
    }
    return { 0, 1, 0 };
}

CameraState::CameraState(PXR_NS::UsdGeomCamera camera, const PXR_NS::UsdTimeCode* time)
    : m_camera(std::move(camera)),
      m_timeCode(time ? *time :
                        omni::timeline::getTimeline()->getCurrentTime() *
                            m_camera.GetPrim().GetStage()->GetTimeCodesPerSecond())
{
}

void CameraState::getCameraPosition(carb::Double3& position) const
{
    PXR_NS::GfMatrix4d worldXform = m_camera.ComputeLocalToWorldTransform(m_timeCode).RemoveScaleShear();
    PXR_NS::GfVec3d worldPos = worldXform.Transform(PXR_NS::GfVec3d(0, 0, 0));
    position = { worldPos[0], worldPos[1], worldPos[2] };
}

static PXR_NS::UsdAttribute createCoiAttr(const PXR_NS::UsdPrim& cameraPrim)
{
    return cameraPrim.CreateAttribute(
        kCenterOfInterest, PXR_NS::SdfValueTypeNames->Vector3d, true, PXR_NS::SdfVariabilityUniform);
}

void CameraState::getCameraTarget(carb::Double3& target) const
{
    PXR_NS::GfVec3d localCenterOfInterest;
    PXR_NS::UsdAttribute coiAttr = m_camera.GetPrim().GetAttribute(kCenterOfInterest);
    if (!coiAttr || !coiAttr.Get(&localCenterOfInterest, m_timeCode))
    {
        localCenterOfInterest = { 0, 0, -1 };
    }

    PXR_NS::GfMatrix4d worldXform = m_camera.ComputeLocalToWorldTransform(m_timeCode).RemoveScaleShear();
    PXR_NS::GfVec3d worldCenterOfInterest = worldXform.Transform(localCenterOfInterest);
    target = { worldCenterOfInterest[0], worldCenterOfInterest[1], worldCenterOfInterest[2] };
}

bool CameraState::setCameraPosition(const carb::Double3& worldPosition, bool rotate)
{
    PXR_NS::GfMatrix4d worldXform = m_camera.ComputeLocalToWorldTransform(m_timeCode).RemoveScaleShear();
    PXR_NS::GfMatrix4d parentXform = m_camera.ComputeParentToWorldTransform(m_timeCode);
    PXR_NS::GfMatrix4d invParentXform = parentXform.GetInverse();
    PXR_NS::GfMatrix4d initialLocalXform = worldXform * invParentXform;
    PXR_NS::GfVec3d posInParent =
        invParentXform.Transform(PXR_NS::GfVec3d(worldPosition.x, worldPosition.y, worldPosition.z));
    PXR_NS::UsdPrim camPrim = m_camera.GetPrim();

    PXR_NS::UsdAttribute coiAttr;
    PXR_NS::GfVec3d prevLocalCenterOfInterest;
    PXR_NS::GfMatrix4d newLocalXform;
    if (rotate)
    {
        const PXR_NS::GfVec3d camUp = getCameraUp(camPrim.GetStage());

        coiAttr = camPrim.GetAttribute(kCenterOfInterest);
        if (!coiAttr || !coiAttr.Get(&prevLocalCenterOfInterest, m_timeCode))
        {
            prevLocalCenterOfInterest = { 0, 0, -1 };
            // Try to create the centerOfInterest attribute for set below
            coiAttr = createCoiAttr(camPrim);
        }

        PXR_NS::GfVec3d coiInParent = invParentXform.Transform(worldXform.Transform(prevLocalCenterOfInterest));
        if (!checkPositionAndTarget(posInParent, coiInParent))
        {
            return false;
        }
        newLocalXform = PXR_NS::GfMatrix4d(1).SetLookAt(posInParent, coiInParent, camUp).GetInverse();
    }
    else
    {
        newLocalXform = initialLocalXform;
    }

    newLocalXform.SetTranslateOnly(posInParent);
    omni::usd::UsdUtils::setLocalTransformMatrix(camPrim, newLocalXform, m_timeCode);

    if (coiAttr)
    {
        PXR_NS::GfVec3d prevWorldCOI = worldXform.Transform(prevLocalCenterOfInterest);
        PXR_NS::GfVec3d newLocalCOI = (newLocalXform * parentXform).GetInverse().Transform(prevWorldCOI);
        omni::usd::UsdUtils::setAttribute(coiAttr, newLocalCOI, m_timeCode);
    }

    return true;
}

bool CameraState::setCameraTarget(const carb::Double3& worldTarget, bool rotate)
{
    PXR_NS::UsdPrim camPrim = m_camera.GetPrim();

    PXR_NS::GfMatrix4d worldXform = m_camera.ComputeLocalToWorldTransform(m_timeCode).RemoveScaleShear();
    PXR_NS::GfMatrix4d parentXform = m_camera.ComputeParentToWorldTransform(m_timeCode);
    PXR_NS::GfMatrix4d invParentXform = parentXform.GetInverse();
    PXR_NS::GfMatrix4d initialLocalXform = worldXform * invParentXform;
    PXR_NS::GfVec3d gfWorldTarget(worldTarget.x, worldTarget.y, worldTarget.z);

    PXR_NS::GfVec3d prevLocalCenterOfInterest;
    PXR_NS::UsdAttribute coiAttr = camPrim.GetAttribute(kCenterOfInterest);
    if (!coiAttr || !coiAttr.Get(&prevLocalCenterOfInterest, m_timeCode))
    {
        prevLocalCenterOfInterest = { 0, 0, -1 };
        if (rotate)
        {
            // Try to create the centerOfInterest attribute for set below
            coiAttr = createCoiAttr(camPrim);
        }
    }

    PXR_NS::GfVec3d posInParent = invParentXform.Transform(initialLocalXform.Transform(PXR_NS::GfVec3d(0, 0, 0)));
    PXR_NS::GfMatrix4d newLocalXform;
    PXR_NS::GfVec3d newLocalCenterOfInterest;
    if (rotate)
    {
        // Rotate camera to look at new target, leaving it where it is
        PXR_NS::GfVec3d camUp = getCameraUp(camPrim.GetStage());
        PXR_NS::GfVec3d coiInParent = invParentXform.Transform(gfWorldTarget);
        if (!checkPositionAndTarget(posInParent, coiInParent))
        {
            return false;
        }
        newLocalXform = PXR_NS::GfMatrix4d(1).SetLookAt(posInParent, coiInParent, camUp).GetInverse();
        newLocalCenterOfInterest = (newLocalXform * parentXform).GetInverse().Transform(gfWorldTarget);
    }
    else
    {
        // Camera keeps orientation and distance relative to target
        // Calculate movement of center-of-interest in parent's space
        PXR_NS::GfVec3d targetMove = invParentXform.Transform(gfWorldTarget) -
                                     invParentXform.Transform(worldXform.Transform(prevLocalCenterOfInterest));
        // Copy the camera's local transform
        newLocalXform = initialLocalXform;
        // And move it by the delta
        newLocalXform.SetTranslateOnly(posInParent + targetMove);
    }

    if (rotate)
    {
        omni::usd::UsdUtils::setAttribute(coiAttr, newLocalCenterOfInterest, m_timeCode);
    }
    omni::usd::UsdUtils::setLocalTransformMatrix(camPrim, newLocalXform, m_timeCode);

    return true;
}
