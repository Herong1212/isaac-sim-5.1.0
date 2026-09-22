// Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
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
namespace graph
{

/**
 * Animation Graph compile error codes.
 */
enum CompileErrorCode : uint32_t
{
    eNoError,
    eNodeMissingAttribute,
    eNodeInvalidAttribute,
    eNodeMissingDefaultState,
    eNodeMissingTransition,
    eRigDuplicateJoint,
    eRigMissingJoint,
    eRigMissingJointParent,
    eRigDuplicateBlendShape,
    eRetargetSolverMissingTag,
    eRetargetSolverInvalidChain,
    eMissingDependencies,
    eMissingEffectorNodes,
    eCount // Keep this as last error.
};

/**
 * Animation Graph compile event types.
 */
enum CompileEventType
{
    eCompileStart,
    eCompileStop,
    eCompileError,
};

/**
 * Animation Graph compile events
 */
struct CompileEvent
{
    CompileEventType type;
    const char* assetPath;
    uint32_t errorCode;
    uint32_t argument;
};

/**
 * Compile Event callback function.
 */
typedef void (*OnCompileEventFn)(const char* graphPath, const CompileEvent& evt, void* userData);


/**
 * Defines an interface to support manual processing of animation graph system.
 */
struct IAnimGraph
{
    CARB_PLUGIN_INTERFACE("omni::anim::graph::IAnimGraph", 1, 1)

    /**
     * Initializes the animation system. By default this is handled
     * automatically and calling this function will fail. This behavior
     * can be changed by enabling "/animGraph/manualUpdate".
     */
    bool(CARB_ABI* initialize)(long int stageId);

    /**
     * Shuts down the animation system. By default this is handled
     * automatically. This behavior can be changed
     * by enabling "/animGraph/manualUpdate".
     */
    void(CARB_ABI* shutdown)();

    /**
     * Execute the per-frame update for the animation system.
     * By default this is handled automatically as part of the stage
     * update and calling this function will fail.
     *
     * This behavior can be changed by enabling "/animGraph/manualUpdate".
     *
     * @param deltaTimeInSeconds The delta time to update with (in seconds).
     */
    bool(CARB_ABI* update)(float deltaTimeInSeconds);

    /**
     * Subscribes to animation graph compile events.
     *
     * @param fn The callback function to be called on compile events.
     * @param userData The userData to be passed back on any compile event.
     * @return The subsciption identifier.
     */
    uint32_t(CARB_ABI* subscribeToCompileEvents)(OnCompileEventFn fn, void* userData);

    /**
     * Unsubscribes to animation graph compile events.
     *
     * @param subscriptionId The subscription identier to unsubscribe with.
     */
    void(CARB_ABI* unsubscribeToCompileEvents)(uint32_t subscriptionId);
};
}
}
}
