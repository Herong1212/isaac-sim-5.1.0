// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnTranslateToTargetDatabase.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/vec.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/math.h>
#include <omni/math/linalg/SafeCast.h>

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
namespace
{
constexpr double kUninitializedStartTime = -1.;
}

class OgnTranslateToTarget
{
    XformUtils::MoveState m_moveState;

public:
    static bool compute(OgnTranslateToTargetDatabase& db)
    {
        auto& nodeObj = db.abi_node();
        const auto& contextObj = db.abi_context();
        auto iContext = contextObj.iContext;

        double now = iContext->getTimeSinceStart(contextObj);

        auto& state = db.perInstanceState<OgnTranslateToTarget>();

        double& startTime = state.m_moveState.startTime;
        vec3d& startTranslation = state.m_moveState.startTranslation;

        if (db.inputs.stop() != kExecutionAttributeStateDisabled)
        {
            startTime = kUninitializedStartTime;
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

            // First frame of the maneuver.
            if (startTime <= kUninitializedStartTime || now < startTime)
            {
                try
                {
                    startTranslation =
                        tryGetPrimVec3dAttribute(contextObj, sourcePrimPath, XformUtils::TranslationAttrStr);
                }
                catch (std::runtime_error const& error)
                {
                    db.logError(error.what());
                    return false;
                }

                startTime = now;
                // Start sleeping
                db.outputs.finished() = kExecutionAttributeStateLatentPush;
                return true;
            }

            int exp = std::min(std::max(int(db.inputs.exponent()), 0), 10);
            float speed = std::max(0.f, float(db.inputs.speed()));

            matrix4d destWorldTransform, sourceParentTransform;

            // Convert dest prim transform to the source's parent frame
            if (XformUtils::useFabricSceneDelegate())
            {
                auto iHierarchy = XformUtils::getFabricHierarchy(contextObj);
                FIREWALL_RET_ERROR(db, !iHierarchy, false, "Failed to initialize omni.fabric.hierarchy"); // LCOV_EXCL_LINE
                destWorldTransform = iHierarchy->getWorldXform(fabric::asInt(destPrimPath));
                auto targetPrimParentPath = sourcePrimPath.GetParentPath();
                sourceParentTransform = iHierarchy->getWorldXform(fabric::asInt(targetPrimParentPath));
            }
            else
            {
                pxr::UsdPrim sourcePrim = getPrim(contextObj, sourcePrimPath);
                pxr::UsdPrim targetPrim = getPrim(contextObj, destPrimPath);
                pxr::UsdGeomXformCache xformCache;
                destWorldTransform = safeCastToOmni(xformCache.GetLocalToWorldTransform(targetPrim));
                sourceParentTransform = safeCastToOmni(xformCache.GetParentToWorldTransform(sourcePrim));
            }
            matrix4d destLocalTransform = destWorldTransform / sourceParentTransform;

            const vec3d targetTranslation = destLocalTransform.ExtractTranslation();

            // delta step
            float alpha = std::min(std::max(speed * float(now - startTime), 0.f), 1.f);
            // Ease out by applying a shifted exponential to the alpha
            float alpha2 = easeInOut<float>(0.f, 1.f, alpha, exp);

            vec3d translation = GfLerp(alpha2, startTranslation, targetTranslation);

            // Write back to the prim
            try
            {
                trySetPrimAttribute(contextObj, sourcePrimPath, XformUtils::TranslationAttrStr, translation);
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
            return true;
        }
    }
};
REGISTER_OGN_NODE()

} // action
} // graph
} // omni
