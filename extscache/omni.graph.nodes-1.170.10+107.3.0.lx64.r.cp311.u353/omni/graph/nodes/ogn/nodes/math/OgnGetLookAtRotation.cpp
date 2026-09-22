// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "UsdPCH.h"

#include <omni/math/linalg/SafeCast.h>
#include <omni/math/linalg/vec.h>

#include <OgnGetLookAtRotationDatabase.h>
// clang-format on

namespace omni
{
namespace graph
{
namespace action
{

class OgnGetLookAtRotation
{
    pxr::TfToken m_upAxisToken;

    static omni::math::linalg::vec3d getSceneUp(OgnGetLookAtRotationDatabase& db)
    {
        //  Default to the Y-axis if anything goes wrong.
        omni::math::linalg::vec3d up = omni::math::linalg::vec3d::YAxis();

        long stageId = db.abi_context().iContext->getStageId(db.abi_context());
        auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));

        if (stage)
        {
            auto& state = db.perInstanceState<OgnGetLookAtRotation>();
            pxr::VtValue value;

            if (stage->GetMetadata(state.m_upAxisToken, &value))
            {
                std::string upAxisStr = value.Cast<std::string>().Get<std::string>();

                if ((upAxisStr == "X") || (upAxisStr == "x"))
                {
                    up = omni::math::linalg::vec3d::XAxis();
                }
                else if ((upAxisStr == "Z") || (upAxisStr == "z"))
                {
                    up = omni::math::linalg::vec3d::ZAxis();
                }
            }
        }

        return up;
    }

public:
    OgnGetLookAtRotation()
    {
        // Cache the token.
        m_upAxisToken = pxr::TfToken("upAxis");
    }

    static bool compute(OgnGetLookAtRotationDatabase& db)
    {
        auto const start = db.inputs.start();
        auto const target = db.inputs.target();
        auto const forward = db.inputs.forward();
        auto up = db.inputs.up();

        // If 'up' is zero, use the scene's up.
        if (up.GetLengthSq() == 0.0)
        {
            up = getSceneUp(db);
        }

        omni::math::linalg::vec3d const aimVec = target - start;
        omni::math::linalg::vec3d const eyeU = aimVec.GetNormalized();
        omni::math::linalg::vec3d eyeV = up.GetNormalized();
        omni::math::linalg::vec3d const eyeW = (eyeU ^ eyeV).GetNormalized();
        // eyeW and eyeU are orthogonal unit vectors so eyeV will be one as well.
        eyeV = eyeW ^ eyeU;

        auto localMtx = omni::math::linalg::matrix4d().SetIdentity();
        omni::math::linalg::vec3d const eyeUL = forward.GetNormalized();
        omni::math::linalg::vec3d eyeVL = up.GetNormalized();
        omni::math::linalg::vec3d const eyeWL = (eyeUL ^ eyeVL).GetNormalized();
        // eyeWL and eyeUL are orthogonal unit vectors so eyeVL will be one as well.
        eyeVL = eyeWL ^ eyeUL;

        localMtx.SetRow3(0, eyeUL);
        localMtx.SetRow3(1, eyeVL);
        localMtx.SetRow3(2, eyeWL);

        // The actual aiming vectors
        auto newEyeMtx = omni::math::linalg::matrix4d().SetIdentity();
        newEyeMtx.SetRow3(0, eyeU);
        newEyeMtx.SetRow3(1, eyeV);
        newEyeMtx.SetRow3(2, eyeW);

        // Output
        omni::math::linalg::matrix4d aimMtx = localMtx.GetInverse() * newEyeMtx;
        aimMtx.SetRow3(3, start);

        omni::math::linalg::quatd orientation = aimMtx.ExtractRotation();
        pxr::GfRotation rotation(omni::math::linalg::safeCastToUSD(orientation));

        // extract the world space euler angles
        pxr::GfVec3d decomposed = rotation.Decompose(pxr::GfVec3d::ZAxis(), pxr::GfVec3d::YAxis(), pxr::GfVec3d::XAxis());
        pxr::GfVec3d rotateXYZ(decomposed[2], decomposed[1], decomposed[0]);

        db.outputs.rotateXYZ() = omni::math::linalg::safeCastToOmni(rotateXYZ);

        db.outputs.orientation() = orientation;

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
