// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/IObject.h>
#include <carb/Interface.h>
#include <carb/ObjectUtils.h>
#include <carb/Types.h>

namespace omni
{
namespace anim
{
namespace navigation
{
/**
 * Defines a navigation path on the NavMesh.
 */
class INavMeshPath : public carb::IObject
{
public:
    /**
     * Gets the number of points on the path.
     *
     * @return number of points on the path
     */
    virtual size_t getPointCount() const = 0;

    /**
     * Gets a pointer to the path point array.
     *
     * @return pointer to the path point array.
     */
    virtual const carb::Float3* getPoints() const = 0;

    /**
     * Computes the distance along the path that is closest to the given reference position.
     *
     * @param position Position for which the closest point on the path should be calculated.
     * @param outPathPosition The position of the closest point on the path, or nullptr if not needed.
     * @param outPathTangent The tangent of the closest point on the path, or nullptr if not needed.
     *
     * @return the distance to the closest point on the path, or -1 if path is empty.
     */
    virtual float closestDistance(const carb::Float3& position, carb::Float3* outPathPosition, carb::Float3* outPathTangent) const = 0;

    /**
     * Computes the length of the path.
     */
    virtual float length() const = 0;

    /**
     * Evaluetes the position that corresponds to the given distance along the path.
     *
     * @param distance Distance for which the corresponding position is to be evaluated.
     */
    virtual carb::Float3 evaluatePosition(float distance) const = 0;

    /**
     * Evaluetes the tangent that corresponds to the given distance along the path.
     *
     * @param distance Distance for which the corresponding tangent is to be evaluated.
     */
    virtual carb::Float3 evaluateTangent(float distance) const = 0;

    /**
     * Gets a pointer to the smooth path point array.
     *
     * @return pointer to the smooth path point array.
     */
    virtual carb::ObjectPtr<INavMeshPath> smooth() const = 0;
};

using INavMeshPathPtr = carb::ObjectPtr<INavMeshPath>;
}
}
}
