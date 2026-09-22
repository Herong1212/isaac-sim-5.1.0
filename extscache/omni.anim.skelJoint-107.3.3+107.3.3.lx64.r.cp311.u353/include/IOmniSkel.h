// Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IOmniSkelTypes.h"

#include <carb/Interface.h>
#include <carb/Types.h>

namespace omni
{
namespace skel
{

/**
 * Defines an interface for omniskel.
 */
struct IOmniSkel
{
    CARB_PLUGIN_INTERFACE("omni::skel", 1, 1);

    /**
     * @brief generate omni skeleton.
     *
     */
    bool(CARB_ABI* generateOmniSkeleton)(const char* usdSkeletonPath, const char* defaultRotationOrder, double timeCode, const char* usdContextName);


    /**
     * @brief switch to animation transform mode for a skeleton.
     *
     */
    bool(CARB_ABI* switchToAnimationTransformMode)(const char* usdSkeletonPath, const char* usdContextName);

    /**
     * @reset to binding for a skeleton.
     *
     */
    bool(CARB_ABI* resetToBinding)(const char* usdSkeletonPath, const char* usdContextName);

    /**
     * @brief switch to retarget transform mode for a skeleton.
     *
     */
    bool(CARB_ABI* switchToRetargetingTransformMode)(const char* usdSkeletonPath, const char* usdContextName);

    /**
     * @reset to apply current joints retarget pose to retargetTransform on skeleton's controlRigAPI
     *
     */
    bool(CARB_ABI* applyJointRetargetPoseToSkeleton)(const char* usdSkeletonPath, const char* usdContextName);

    /**
     * @brief switch to rest transform mode for a skeleton.
     *
     */
    bool(CARB_ABI* switchToRestTransformMode)(const char* usdSkeletonPath, const char* usdContextName);

    /**
     * @reset to apply current joints rest pose to retargetTransform on skeleton's controlRigAPI
     *
     */
    bool(CARB_ABI* applyJointRestPoseToSkeleton)(const char* usdSkeletonPath, const char* usdContextName);

    ///**
    // * @brief Returns the session layer identifier of OmniSkel.
    // *
    // */
    // const char*(CARB_ABI* getOmniSkelSessionLayerIdentifier)(const char* usdContextName);

    /**
     * @brief Adds Omni Skeleton support to a given context. No need to call this for the default context.
     *
     */
    void(CARB_ABI* addOmniSkel)(const char* usdContextName);

    /**
     * @brief Removes Omni Skeleton support from a given context. Has no effect on the default context.
     *
     */
    void(CARB_ABI* removeOmniSkel)(const char* usdContextName);

    /**
     * @brief Deprecated. Adds Omni Skeleton support to a given context. No need to call this for the default context.
     *
     * @param usdContextName Name of the USD context, the newly created OmniSkel will be tied to this context.
     * @param fabricUseType Sets Fabric write setting for the OmniSkel of the given context.
     *
     */
    void(CARB_ABI* addOmniSkelCustom)(const char* usdContextName, FabricUseType fabricUseType);
};
}
}
