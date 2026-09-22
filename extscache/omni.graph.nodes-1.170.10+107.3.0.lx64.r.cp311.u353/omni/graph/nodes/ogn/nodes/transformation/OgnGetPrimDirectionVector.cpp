// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnGetPrimDirectionVectorDatabase.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/vec.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/SafeCast.h>

#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/usdGeom/xformCache.h>
#include <omni/graph/core/PostUsdInclude.h>

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

class OgnGetPrimDirectionVector
{
public:
    static bool compute(OgnGetPrimDirectionVectorDatabase& db)
    {
        auto& nodeObj = db.abi_node();
        const auto& contextObj = db.abi_context();
        try
        {
            // Retrieve the prim path string in one of two ways
            bool usePath = db.inputs.usePath();
            std::string primPathStr;

            if (usePath)
            {
                // Use the absolute path
                NameToken primPath = db.inputs.primPath();
                primPathStr = db.tokenToString(primPath);
                if (primPathStr.empty())
                {
                    db.logWarning("No prim path specified");
                    return false;
                }
            }
            else
            {
                // Read the path from the relationship input on this compute node
                auto primPath = getRelationshipPrimPath(contextObj, nodeObj,
                                                        OgnGetPrimDirectionVectorAttributes::inputs::prim.m_token,
                                                        db.getInstanceIndex());
                primPathStr = primPath.GetText();
            }

            // Retrieve a reference to the prim
            pxr::UsdPrim prim = getPrim(contextObj, pxr::SdfPath(primPathStr));

            // Extract the rotation from the local to world transformation matrix
            pxr::UsdGeomXformCache xformCache;
            matrix4d localWorldTransform = safeCastToOmni(xformCache.GetLocalToWorldTransform(prim));
            quatd rotation = extractRotationQuatd(localWorldTransform).GetNormalized();

            // Apply the rotation to (0,1,0) to get the up vector
            vec3<double> upVector = rotation.Transform(vec3<double>::YAxis());
            db.outputs.upVector() = upVector;

            db.outputs.downVector() = -upVector;

            // Apply the rotation to (0,0,-1) to get the forward vector
            vec3<double> forwardVector = rotation.Transform(-vec3<double>::ZAxis());
            db.outputs.forwardVector() = forwardVector;

            db.outputs.backwardVector() = -forwardVector;

            // Apply the rotation to (1,0,0) to get the right vector
            vec3<double> rightVector = rotation.Transform(vec3<double>::XAxis());
            db.outputs.rightVector() = rightVector;

            db.outputs.leftVector() = -rightVector;

            return true;
        }
        catch (const std::exception& e)
        {
            db.logError(e.what());
            return false;
        }
    }
};
REGISTER_OGN_NODE()

} // nodes
} // graph
} // omni
