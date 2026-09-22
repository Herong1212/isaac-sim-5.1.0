// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnRotateToOrientationDatabase.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/vec.h>
#include <omni/math/linalg/matrix.h>

#include "PrimCommon.h"
#include "XformUtils.h"

using namespace omni::math::linalg;

namespace omni
{
namespace graph
{
namespace nodes
{

struct RotateMoveState : public XformUtils::MoveState
{
    vec3d targetEuler;
};

class OgnRotateToOrientation
{
public:
    RotateMoveState m_moveState;

    static bool compute(OgnRotateToOrientationDatabase& db)
    {
        auto& nodeObj = db.abi_node();
        const auto& contextObj = db.abi_context();
        auto iContext = contextObj.iContext;

        double now = iContext->getTimeSinceStart(contextObj);

        auto& state = db.perInstanceState<OgnRotateToOrientation>();
        double& startTime = state.m_moveState.startTime;
        pxr::TfToken& targetAttribName = state.m_moveState.targetAttribName;
        quatd& startOrientation = state.m_moveState.startOrientation;
        vec3d& startEuler = state.m_moveState.startEuler;
        vec3d& targetEuler = state.m_moveState.targetEuler;
        XformUtils::RotationMode& rotationMode = state.m_moveState.rotationMode;

        if (db.inputs.stop() != kExecutionAttributeStateDisabled)
        {
            startTime = XformUtils::kUninitializedStartTime;
            db.outputs.finished() = kExecutionAttributeStateLatentFinish;
            return true;
        }

        try
        {
            auto primPath = getPrimOrPath(contextObj, nodeObj, inputs::prim.token(), inputs::primPath.token(),
                                          inputs::usePath.token(), db.getInstanceIndex());

            if (primPath.IsEmpty())
                return true;

            // First frame of the maneuver.
            if (startTime <= XformUtils::kUninitializedStartTime || now < startTime)
            {
                try
                {
                    std::tie(startOrientation, targetAttribName) = XformUtils::extractPrimOrientOp(contextObj, primPath);
                    if (not targetAttribName.IsEmpty())
                        rotationMode = XformUtils::RotationMode::eQuat;
                    else
                    {
                        std::tie(startEuler, targetAttribName) = XformUtils::extractPrimEulerOp(contextObj, primPath);
                        if (not targetAttribName.IsEmpty())
                            rotationMode = XformUtils::RotationMode::eEuler;
                    }

                    if (targetAttribName.IsEmpty())
                        throw std::runtime_error(
                            formatString("Could not find suitable XformOp on %s, please add", primPath.GetText()));
                }
                catch (std::runtime_error const& error)
                {
                    db.logError(error.what());
                    return false;
                }

                // Copy the target in case it changes during the movement
                targetEuler = db.inputs.target();

                startTime = now;
                // Start sleeping
                db.outputs.finished() = kExecutionAttributeStateLatentPush;
                return true;
            }

            int exp = std::min(std::max(int(db.inputs.exponent()), 0), 10);
            float speed = std::max(0.f, float(db.inputs.speed()));

            // delta step
            float alpha = std::min(std::max(speed * float(now - startTime), 0.f), 1.f);
            // Ease out by applying a shifted exponential to the alpha
            float alpha2 = easeInOut<float>(0.f, 1.f, alpha, exp);

            try
            {
                if (rotationMode == XformUtils::RotationMode::eQuat)
                {
                    quatd const& targetOrientation =
                        eulerAnglesToQuaternion(GfDegreesToRadians(targetEuler), EulerRotationOrder::XYZ);
                    auto const quat = GfSlerp(startOrientation, targetOrientation, alpha2).GetNormalized();
                    // Write back to the prim
                    trySetPrimAttribute(contextObj, primPath, targetAttribName.GetText(), quat);
                }
                else if (rotationMode == XformUtils::RotationMode::eEuler)
                {
                    vec3d rot = lerp(startEuler, targetEuler, alpha2);
                    // Write back to the prim
                    trySetPrimAttribute(contextObj, primPath, targetAttribName.GetText(), rot);
                }
            }
            catch (std::runtime_error const& error)
            {
                db.logError(error.what());
                return false;
            }

            if (alpha2 < 1)
            {
                // still waiting, output is disabled
                db.outputs.finished() = kExecutionAttributeStateDisabled;
                return true;
            }
            else
            {
                // Completed the maneuver
                startTime = XformUtils::kUninitializedStartTime;
                db.outputs.finished() = kExecutionAttributeStateLatentFinish;
                return true;
            }
        }
        catch (const std::exception& e)
        {
            db.logError(e.what());
            return true;
        }
    }
};
REGISTER_OGN_NODE()

} // action
} // graph
} // omni
