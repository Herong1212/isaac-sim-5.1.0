// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnMoveToTransformDatabase.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/vec.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/math.h>
#include <omni/math/linalg/SafeCast.h>

#include <cmath>

#include "PrimCommon.h"
#include "XformUtils.h"

using namespace omni::math::linalg;

namespace omni
{
namespace graph
{
namespace nodes
{
namespace
{
constexpr double kUninitializedStartTime = -1.;
}

struct MoveMoveState : public XformUtils::MoveState
{
    matrix4d targetTransform;
};

class OgnMoveToTransform
{
public:
    MoveMoveState m_moveState;

    static bool compute(OgnMoveToTransformDatabase& db)
    {
        auto& nodeObj = db.abi_node();
        const auto& contextObj = db.abi_context();
        auto iContext = contextObj.iContext;

        double now = iContext->getTimeSinceStart(contextObj);

        auto& state = db.perInstanceState<OgnMoveToTransform>();
        double& startTime = state.m_moveState.startTime;
        pxr::TfToken& targetAttribName = state.m_moveState.targetAttribName;
        quatd& startOrientation = state.m_moveState.startOrientation;
        vec3d& startTranslation = state.m_moveState.startTranslation;
        matrix4d& targetTransform = state.m_moveState.targetTransform;
        vec3d& startScale = state.m_moveState.startScale;
        XformUtils::RotationMode& rotationMode = state.m_moveState.rotationMode;

        if (db.inputs.stop() != kExecutionAttributeStateDisabled)
        {
            startTime = kUninitializedStartTime;
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
            if (startTime <= kUninitializedStartTime || now < startTime)
            {
                try
                {
                    std::tie(startOrientation, targetAttribName) = XformUtils::extractPrimOrientOp(contextObj, primPath);
                    if (targetAttribName.IsEmpty())
                        throw std::runtime_error(
                            "MoveToTransform requires the source Prim to have xformOp:orient, please add");

                    rotationMode = XformUtils::RotationMode::eQuat;

                    startTranslation = tryGetPrimVec3dAttribute(contextObj, primPath, XformUtils::TranslationAttrStr);
                    startScale = tryGetPrimVec3dAttribute(contextObj, primPath, XformUtils::ScaleAttrStr);
                }
                catch (std::runtime_error const& error)
                {
                    db.logError(error.what());
                    return false;
                }

                startTime = now;
                targetTransform = db.inputs.target();
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
                vec3d targetTranslation = targetTransform.ExtractTranslation();
                vec3d targetScale{ targetTransform.GetRow(0).GetLength(), targetTransform.GetRow(1).GetLength(),
                                   targetTransform.GetRow(2).GetLength() };


                vec3d translation = GfLerp(alpha2, startTranslation, targetTranslation);
                vec3d scale = GfLerp(alpha2, startScale, targetScale);

                if (XformUtils::useFabricSceneDelegate())
                {
                    quatd targetOrientation = extractRotationQuatd(targetTransform).GetNormalized();
                    auto quat = GfSlerp(startOrientation, targetOrientation, alpha2).GetNormalized();
                    matrix4d new_xform =
                        matrix4d().SetScale(scale) * matrix4d().SetRotate(quat) * matrix4d().SetTranslate(translation);
                    trySetPrimAttribute(contextObj, primPath, new_xform);
                }
                else
                {
                    if (rotationMode == XformUtils::RotationMode::eQuat)
                    {
                        quatd targetOrientation = extractRotationQuatd(targetTransform).GetNormalized();
                        quatd quat = GfSlerp(startOrientation, targetOrientation, alpha2).GetNormalized();
                        // Write back to the prim
                        trySetPrimAttribute(contextObj, primPath, targetAttribName.GetText(), quat);
                    }

                    // Write back to the prim
                    trySetPrimAttribute(contextObj, primPath, XformUtils::TranslationAttrStr, translation);
                    trySetPrimAttribute(contextObj, primPath, XformUtils::ScaleAttrStr, scale);
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
                startTime = kUninitializedStartTime;
                db.outputs.finished() = kExecutionAttributeStateLatentFinish;
                return true;
            }
        }
        catch (const std::exception& e)
        {
            db.logError(e.what());
            return false;
        }
    }
};
REGISTER_OGN_NODE()

} // action
} // graph
} // omni
