// Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>
#include <carb/Types.h>

namespace omni
{
namespace anim
{
namespace retarget
{
/** Handle to an animation retarget controller. */
typedef void* ControllerHandle;

/**
 * Defines an interface for performating animation retargeting.
 *
 * This allows animations to be reused between characters that
 * use the same Skeleton asset but may have vastly different
 * proportions.
 *
 * This also support auto posing and auto tag retarget setup cababilities.
 *
 * You can create a retarget controller and then directly retarget
 * the source to target skeleton joints,
 *
 * The `autoPose` can be used to match the target skeleton pose to the source skeleton pose.
 *
 * The `autoTag` can be use to automatically setup retargeting based on auto mapping setup.
 *
 * You can register a joing keyword mapping first and attempt to run the auto rig process based
 * on the well know keywords for a given mapping you have for joint names to the defined retarget rig.
 *
 * Auto Mapping Tags:
 *
 * Required:
 *
 * Head, Left_Hand, Right_Hand, Left_Foot, Right_Foot
 *
 * Optional:
 *
 * Left_Shoulder, Left_Elbow, Right_Shoulder, Right_Elbow,
 * Left_Thigh, Left_Knee, Left_Toe, Right_Thigh, Right_Knee, Right_Toe,
 * Left_Thumb, Left_Index, Left_Middle, Left_Ring, Left_Pinky,
 * Right_Thumb, Right_Index, Right_Middle, Right_Ring, Right_Pinky
 *
 * https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_animation-retargeting.html
 */
struct IAnimRetarget
{
    CARB_PLUGIN_INTERFACE("omni::anim::retarget:IAnimRetarget", 1, 0)

    /**
     * Creates an animation retarget controller for the given target and target skeleton.
     *
     * @param sourceStagePath The optional source stage reference path. Can be `nullptr` if not used. Currently must be file path URL.
     * @param sourceSkeletonPrimPath The source skeleton USD Path. If empty the first skeleton found will be used.
     * @param targetSkeletonPrimPath The target skeleton USD Path.
     *
     * @return The handle to the animaton retarget controller.
     */
    ControllerHandle(CARB_ABI* createController)(const char* sourceStagePath,
                                                 const char* sourceSkeletonPrimPath,
                                                 const long int targetStageId,
                                                 const char* targetSkeletonPrimPath);

    /**
     * Destroys an animation retarget controller.
     *
     * @param handle The handle to a retarget controller to be destroyed.
     */
    void(CARB_ABI* destroyController)(ControllerHandle handle);

    /**
     * Returns the number of joints in the source skeleton.
     *
     * @param handle The handle to the animaton retarget controller to use.
     * @return The number of joints in the source skeleton.
     */
    size_t(CARB_ABI* getSourceJointCount)(ControllerHandle handle);

    /**
     * Returns the number of joints in the target skeleton.
     *
     * @param handle The handle to the animaton retarget controller to use.
     * @return The number of joints in the target skeleton.
     */
    size_t(CARB_ABI* getTargetJointCount)(ControllerHandle handle);

    /**
     * Retargets the source skeleton joint transforms based on the controller's
     * source and target skeletons, writes the result to the target joint transforms.
     *
     * @param handle The handle to the animaton retarget controller to use.
     * @param sourceJointTranslations The array of source skeleton joint translations.
     * @param sourceJointRotations The array of source skeleton joint rotations (quaternions).
     * @param sourceJointCount The number of source skeleton joints.
     * @param targetJointTranslations The array of target skeleton joint translations returned.
     * @param targetJointRotations The array of target skeleton joint rotations (quaternions) returned.
     * @param targetJointCount The number of target skeleton joints.
     */
    void(CARB_ABI* retarget)(ControllerHandle handle,
                             const carb::Float3* sourceJointTranslations,
                             const carb::Float4* sourceJointRotations,
                             size_t sourceJointCount,
                             carb::Float3* targetJointTranslations,
                             carb::Float4* targetJointRotations,
                             size_t targetJointCount);

    /**
     * Automatically poses the target skeleton joint transforms to match
     * the specified source skeleton joint transforms.
     *
     * @param handle The handle to the animaton retarget controller to use.
     * @param targetJointTranslations The target skeleton joint translations returned.
     * @param targetJointRotations The target skeleton joint rotatons(quaternions) returned.
     * @param targetRigointCount The number of target joints.
     */
    void(CARB_ABI* autoPose)(ControllerHandle handle,
                             carb::Float3* targetJointTranslations,
                             carb::Float4* targetJointRotations,
                             size_t targetJointCount);

    /**
     * Adds auto setup tag-to-joint_keywords to be used by `autoTag` and `autoFacing` functions.
     *
     * Use this method to help build up a set of keywords for the tags to automatically set up 
     * animation retargeting.
     *
     * Ex. tag="Left_Hand",  ["left", "l_", "_l", "lt", "hand", "wrist"]
     *
     * @param handle The handle to the animaton retarget controller to use.
     * @param tag The tag to use.
     * @param jointKeywords The array of keywords to use for the joint matching search. 
     * @param jointKeywordsCount The number of keywords. 
     */
    void(CARB_ABI* addAutoSetupKeywords)(ControllerHandle handle, const char* tag, const char** jointKeywords, size_t jointKeywordsCount);

    /**
     * Automatic sets up the upAxis and forwardAxis facing directions for the target skeleton based on auto setup.
     *
     * This is performed based on the auto-mapping definition.
     *
     * @see addAutoMappingEntry to configure the auto mapping
     *
     * @param handle The handle to the animaton retarget controller to use.
     * @param upAxis The up-axis that was automatically setup and returned.
     * @param forwardAxis The forward-axis that was automatically setup and returned.
     * @return true if setup was successful, false if not sucessful.
     */
    bool(CARB_ABI* autoFacing)(ControllerHandle handle, carb::Float3& upAxis, carb::Float3& forwardAxis);

    /**
     * Automatically sets up the tags and returns tag + joint mapping table for the target skeleton
     *
     * This is performed based on the auto-mapping definition.
     *
     * @param handle The handle to the animaton retarget controller to use.
     * @return true if setup was successful, false if not sucessful.
     */
    bool(CARB_ABI* autoTag)(ControllerHandle handle, size_t* tagCount);

    /**
     * Gets the auto tag-to-joint mapping that has been setup from auto rigging.
     *
     * @see addAutoMappingEntry to configure the auto mapping setup.
     * @see autoTag Call first to attempt to automatically configure the right from the tag-keyword
     *
     * @param handle The handle to the animaton retarget controller to use.
     * @param tags The tags that have been setup.
     * @param jointNames The names for the joints that have been setup in the auto mapping process.
     * @param tagCount Then number of tags/jointNames.
     */
    void(CARB_ABI* getAutoTags)(ControllerHandle handle, const char** tags, const char** jointNames, size_t tagCount);
};
}
}
}
