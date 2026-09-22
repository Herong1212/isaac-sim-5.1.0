// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnScaleToSizeDatabase.h>
#include <omni/math/linalg/vec.h>
#include <omni/math/linalg/math.h>

#include "PrimCommon.h"
#include "XformUtils.h"

using omni::math::linalg::GfLerp;
using omni::math::linalg::vec3d;

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

struct ScaleMoveState : public XformUtils::MoveState
{
    vec3d targetScale;
};

class OgnScaleToSize
{
    ScaleMoveState m_moveState;

public:
    static bool compute(OgnScaleToSizeDatabase& db)
    {
        auto& nodeObj = db.abi_node();
        const auto& contextObj = db.abi_context();
        auto iContext = contextObj.iContext;

        double now = iContext->getTimeSinceStart(contextObj);
        auto& state = db.perInstanceState<OgnScaleToSize>();

        double& startTime = state.m_moveState.startTime;
        vec3d& startScale = state.m_moveState.startScale;
        vec3d& targetScale = state.m_moveState.targetScale;

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

            if (startTime <= kUninitializedStartTime || now < startTime)
            {
                // Set state variables
                try
                {
                    startScale = tryGetPrimVec3dAttribute(contextObj, primPath, XformUtils::ScaleAttrStr);
                }
                catch (std::runtime_error const& error)
                {
                    db.logError(error.what());
                    return false;
                }
                startTime = now;

                targetScale = db.inputs.target();

                // This is the first entry, start sleeping
                db.outputs.finished() = kExecutionAttributeStateLatentPush;

                return true;
            }

            int exp = std::min(std::max(int(db.inputs.exponent()), 0), 10);
            float speed = std::max(0.f, float(db.inputs.speed()));

            // delta step
            float alpha = std::min(std::max(speed * float(now - startTime), 0.f), 1.f);
            // Ease out by applying a shifted exponential to the alpha
            float alpha2 = easeInOut<float>(0.f, 1.f, alpha, exp);

            vec3d scale = GfLerp(alpha2, startScale, targetScale);
            // Write back to the prim
            try
            {
                trySetPrimAttribute(contextObj, primPath, XformUtils::ScaleAttrStr, scale);
            }
            catch (std::runtime_error const& error)
            {
                db.logError(error.what());
                return false;
            }

            if (alpha2 < 1)
            {
                // still waiting
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
