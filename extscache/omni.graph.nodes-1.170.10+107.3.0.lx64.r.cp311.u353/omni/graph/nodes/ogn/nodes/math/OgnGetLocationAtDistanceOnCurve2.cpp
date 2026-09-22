// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnGetLocationAtDistanceOnCurve2Database.h>

#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/vec.h>

#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/base/gf/rotation.h>
#include <omni/graph/core/PostUsdInclude.h>
#include <omni/math/linalg/SafeCast.h>

#include <cmath>
#include "XformUtils.h"
// clang-format on

using omni::math::linalg::matrix4d;
using omni::math::linalg::quatd;
using omni::math::linalg::quatf;
using omni::math::linalg::vec3d;

// return the named unit vector X,Y or Z
static vec3d axisToVec(NameToken axisToken, OgnGetLocationAtDistanceOnCurve2Database::TokenManager& tokens)
{
    if (axisToken == tokens.y || axisToken == tokens.Y)
        return vec3d::YAxis();
    if (axisToken == tokens.z || axisToken == tokens.Z)
        return vec3d::ZAxis();
    return vec3d::XAxis();
}

class OgnGetLocationAtDistanceOnCurve2
{
public:
    static bool computeVectorized(OgnGetLocationAtDistanceOnCurve2Database& db, size_t count)
    {
        /* This is a simple closed poly-line interpolation to find p, the point on the curve
            1. find the total length of the curve
            2. find the start and end cvs of the line segment which contains p
            3. calculate the position on that line segment, and the rotation
        */
        bool ok = false;

        const auto& curve_cvs_in = db.inputs.curve();
        auto locations = db.outputs.location.vectorized(count);
        auto rotations = db.outputs.rotateXYZ.vectorized(count);
        auto orientations = db.outputs.orientation.vectorized(count);
        const auto distances = db.inputs.distance.vectorized(count);

        double curve_length = 0; // The total curve length
        std::vector<double> accumulated_lengths; // the length of the curve at each the end of each segment
        std::vector<double> segment_lengths; // the length of each segment

        size_t num_cvs = curve_cvs_in.size();

        if (num_cvs == 0)
            return false;

        if (num_cvs == 1)
        {
            std::fill(locations.begin(), locations.end(), curve_cvs_in[0]);
            std::fill(rotations.begin(), rotations.end(), vec3d(0, 0, 0));
            return true;
        }

        std::vector<vec3d> curve_cvs;
        {
            CARB_PROFILE_ZONE(carb::profiler::kCaptureMaskDefault, "PreprocessCurve");
            curve_cvs.resize(curve_cvs_in.size() + 1);
            std::copy(curve_cvs_in.begin(), curve_cvs_in.end(), curve_cvs.begin());

            // add a cv to make a closed curve
            curve_cvs[curve_cvs_in.size()] = curve_cvs_in[0];

            // calculate the total curve length and the length at the end of each segment
            const vec3d* p_a = curve_cvs.data();

            for (size_t i = 1; i < curve_cvs.size(); ++i)
            {
                const vec3d& p_b = curve_cvs[i];
                double segment_length = (p_b - *p_a).GetLength();
                segment_lengths.push_back(segment_length);
                curve_length += segment_length;
                accumulated_lengths.push_back(curve_length);
                p_a = &p_b;
            }
        }

        const vec3d forwardAxis = axisToVec(db.inputs.forwardAxis(), db.tokens);
        const vec3d upAxis = axisToVec(db.inputs.upAxis(), db.tokens);

        // Calculate eye frame
        auto eyeUL = forwardAxis;
        auto eyeVL = upAxis;
        auto eyeWL = (eyeUL ^ eyeVL).GetNormalized();
        eyeVL = eyeWL ^ eyeUL;

        // local transform from forward axis
        matrix4d localMat, localMatInv;
        localMat.SetIdentity();
        localMat.SetRow3(0, eyeUL);
        localMat.SetRow3(1, eyeVL);
        localMat.SetRow3(2, eyeWL);
        localMatInv = localMat.GetInverse();

        auto distanceIter = distances.begin();
        auto locationIter = locations.begin();
        auto rotationIter = rotations.begin();
        auto orientationIter = orientations.begin();

        {
            CARB_PROFILE_ZONE(carb::profiler::kCaptureMaskDefault, "ScanCurve");
            for (; distanceIter != distances.end(); ++distanceIter, ++locationIter, ++rotationIter, ++orientationIter)
            {
                // wrap distance to range [0, 1.0]
                double normalized_distance = std::fmod(*distanceIter, 1.0);

                // the distance along the curve in world space
                double distance = curve_length * normalized_distance;

                // Find the location and direction
                double remaining_dist = 0;

                for (size_t i = 0; i < accumulated_lengths.size(); ++i)
                {
                    double segment_length = accumulated_lengths[i];
                    if (segment_length >= distance)
                    {
                        if (i > 0)
                            remaining_dist = distance - accumulated_lengths[i - 1];
                        else
                            remaining_dist = distance;

                        const auto& start_cv = curve_cvs[i];
                        const auto& end_cv = curve_cvs[i + 1];
                        const auto aimVec = end_cv - start_cv;
                        const auto segment_unit_vec = aimVec / segment_lengths[i];
                        const auto point_on_segment = start_cv + segment_unit_vec * remaining_dist;
                        *locationIter = point_on_segment;

                        // calculate the rotation
                        vec3d eyeU = segment_unit_vec;
                        vec3d eyeV = upAxis;
                        auto eyeW = (eyeU ^ eyeV).GetNormalized();
                        eyeV = eyeW ^ eyeU;

                        matrix4d eyeMtx;
                        eyeMtx.SetIdentity();
                        eyeMtx.SetTranslateOnly(point_on_segment);
                        // eye aiming
                        eyeMtx.SetRow3(0, eyeU);
                        eyeMtx.SetRow3(1, eyeV);
                        eyeMtx.SetRow3(2, eyeW);

                        matrix4d orientMtx = localMatInv * eyeMtx;

                        const quatd q = omni::graph::nodes::extractRotationQuatd(orientMtx);

                        const pxr::GfRotation rotation(omni::math::linalg::safeCastToUSD(q));
                        const auto eulerRotations =
                            rotation.Decompose(pxr::GfVec3d::ZAxis(), pxr::GfVec3d::YAxis(), pxr::GfVec3d::XAxis());
                        pxr::GfVec3d eulerRotationsXYZ(eulerRotations[2], eulerRotations[1], eulerRotations[0]);
                        *rotationIter = omni::math::linalg::safeCastToOmni(eulerRotationsXYZ);

                        *orientationIter = quatf(q);
                        ok = true;
                        break;
                    }
                }
            }
        }
        return ok;
    }
};

REGISTER_OGN_NODE()
