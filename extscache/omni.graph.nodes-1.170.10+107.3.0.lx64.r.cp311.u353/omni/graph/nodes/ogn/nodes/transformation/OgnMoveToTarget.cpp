// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnMoveToTargetDatabase.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/vec.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/math.h>
#include <omni/math/linalg/SafeCast.h>

#include <cmath>

#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/usdGeom/xformCache.h>
#include <omni/graph/core/PostUsdInclude.h>

#include "CoverageUtils.h"
#include "PrimCommon.h"
#include "XformUtils.h"
// clang-format on

using namespace omni::math::linalg;

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnMoveToTarget
{
    XformUtils::MoveState m_moveState;

public:
    static bool compute(OgnMoveToTargetDatabase& db)
    {
        auto& nodeObj = db.abi_node();
        const auto& contextObj = db.abi_context();
        auto iContext = contextObj.iContext;

        double now = iContext->getTimeSinceStart(contextObj);

        auto& state = db.perInstanceState<OgnMoveToTarget>();

        double& startTime = state.m_moveState.startTime;
        pxr::TfToken& targetAttribName = state.m_moveState.targetAttribName;
        vec3d& startTranslation = state.m_moveState.startTranslation;
        quatd& startOrientation = state.m_moveState.startOrientation;
        vec3d& startEuler = state.m_moveState.startEuler;
        vec3d& startScale = state.m_moveState.startScale;
        XformUtils::RotationMode& rotationMode = state.m_moveState.rotationMode;

        if (db.inputs.stop() != kExecutionAttributeStateDisabled)
        {
            startTime = XformUtils::kUninitializedStartTime;
            db.outputs.finished() = kExecutionAttributeStateLatentFinish;
            return true;
        }

        try
        {
            auto sourcePrimPath =
                getPrimOrPath(contextObj, nodeObj, inputs::sourcePrim.token(), inputs::sourcePrimPath.token(),
                              inputs::useSourcePath.token(), db.getInstanceIndex());
            auto destPrimPath =
                getPrimOrPath(contextObj, nodeObj, inputs::targetPrim.token(), inputs::targetPrimPath.token(),
                              inputs::useTargetPath.token(), db.getInstanceIndex());

            if (sourcePrimPath.IsEmpty() || destPrimPath.IsEmpty())
                return true;

            matrix4d destWorldTransform, sourceParentTransform;

            if (XformUtils::useFabricSceneDelegate())
            {
                auto iHierarchy = XformUtils::getFabricHierarchy(contextObj);
                FIREWALL_RET_ERROR(db, !iHierarchy, false, "Failed to initialize omni.fabric.hierarchy"); // LCOV_EXCL_LINE
                destWorldTransform = iHierarchy->getWorldXform(fabric::asInt(destPrimPath));
                auto sourcePrimParentPath = sourcePrimPath.GetParentPath();
                sourceParentTransform = iHierarchy->getWorldXform(fabric::asInt(sourcePrimParentPath));
            }
            else
            {
                pxr::UsdPrim sourcePrim = getPrim(contextObj, sourcePrimPath);
                pxr::UsdPrim targetPrim = getPrim(contextObj, destPrimPath);
                pxr::UsdGeomXformCache xformCache;
                destWorldTransform = safeCastToOmni(xformCache.GetLocalToWorldTransform(targetPrim));
                sourceParentTransform = safeCastToOmni(xformCache.GetParentToWorldTransform(sourcePrim));
            }

            quatd destWorldOrient = extractRotationQuatd(destWorldTransform).GetNormalized();
            quatd sourceParentWorldOrient = extractRotationQuatd(sourceParentTransform).GetNormalized();
            bool hasRotations =
                (destWorldOrient != quatd::GetIdentity()) or (sourceParentWorldOrient != quatd::GetIdentity());

            // First frame of the maneuver.
            if (startTime <= XformUtils::kUninitializedStartTime || now < startTime)
            {
                std::tie(startOrientation, targetAttribName) =
                    XformUtils::extractPrimOrientOp(contextObj, sourcePrimPath);
                if (targetAttribName.IsEmpty())
                {
                    if (hasRotations)
                        throw std::runtime_error(
                            "MoveToTarget requires the source Prim to have xformOp:orient"
                            " when the destination Prim or source Prim parent has rotation, please Add");

                    std::tie(startEuler, targetAttribName) = XformUtils::extractPrimEulerOp(contextObj, sourcePrimPath);

                    if (not targetAttribName.IsEmpty())
                        rotationMode = XformUtils::RotationMode::eEuler;
                }
                else
                    rotationMode = XformUtils::RotationMode::eQuat;

                if (targetAttribName.IsEmpty())
                    throw std::runtime_error(
                        formatString("Could not find suitable XformOp on %s, please add", sourcePrimPath.GetText()));

                startTranslation = tryGetPrimVec3dAttribute(contextObj, sourcePrimPath, XformUtils::TranslationAttrStr);
                startScale = tryGetPrimVec3dAttribute(contextObj, sourcePrimPath, XformUtils::ScaleAttrStr);
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

            // Convert dest prim transform to the source's parent frame
            matrix4d destLocalTransform = destWorldTransform / sourceParentTransform;
            vec3d targetTranslation = destLocalTransform.ExtractTranslation();
            vec3d targetScale{ destLocalTransform.GetRow(0).GetLength(), destLocalTransform.GetRow(1).GetLength(),
                               destLocalTransform.GetRow(2).GetLength() };

            vec3d translation = GfLerp(alpha2, startTranslation, targetTranslation);
            vec3d scale = GfLerp(alpha2, startScale, targetScale);

            if (XformUtils::useFabricSceneDelegate())
            {
                quatd targetOrientation = extractRotationQuatd(destLocalTransform).GetNormalized();
                auto quat = GfSlerp(startOrientation, targetOrientation, alpha2).GetNormalized();
                matrix4d new_xform =
                    matrix4d().SetScale(scale) * matrix4d().SetRotate(quat) * matrix4d().SetTranslate(translation);
                trySetPrimAttribute(contextObj, sourcePrimPath, new_xform);
            }
            else
            {
                if (rotationMode == XformUtils::RotationMode::eQuat)
                {
                    quatd targetOrientation = extractRotationQuatd(destLocalTransform).GetNormalized();
                    auto quat = GfSlerp(startOrientation, targetOrientation, alpha2).GetNormalized();
                    // Write back to the prim
                    trySetPrimAttribute(contextObj, sourcePrimPath, targetAttribName.GetText(), quat);
                }
                else if (rotationMode == XformUtils::RotationMode::eEuler)
                {
                    // FIXME: We previously checked that there is no rotation on the target, so we just have to
                    // interpolate to identity.
                    vec3d const targetRot{};
                    auto rot = GfLerp(alpha2, startEuler, targetRot);

                    // Write back to the prim
                    trySetPrimAttribute(contextObj, sourcePrimPath, targetAttribName.GetText(), rot);
                }
                // Write back to the prim
                trySetPrimAttribute(contextObj, sourcePrimPath, XformUtils::TranslationAttrStr, translation);
                trySetPrimAttribute(contextObj, sourcePrimPath, XformUtils::ScaleAttrStr, scale);
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
            return false;
        }
    }
};
REGISTER_OGN_NODE()

} // action
} // graph
} // omni
