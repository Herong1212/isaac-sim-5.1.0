// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/kit/actions/core/IAction.h>

#include <carb/Interface.h>

#include <vector>

namespace omni
{
namespace kit
{
namespace actions
{
namespace core
{

/**
 * Defines the interface for the ActionRegistry.
 */
class IActionRegistry
{
public:
    /// @private
    CARB_PLUGIN_INTERFACE("omni::kit::actions::core::IActionRegistry", 1, 0);

    /**
     * Register an action.
     *
     * @param action The action to register.
     */
    virtual void registerAction(carb::ObjectPtr<IAction>& action) = 0;

    /**
     * Create and register an action that calls a function object when executed.
     *
     * @param extensionId The id of the source extension registering the action.
     * @param actionId Id of the action, unique to the extension registering it.
     * @param function The function object to call when the action is executed.
     * @param displayName The name of the action for display purposes.
     * @param description A brief description of what the action does.
     * @param iconUrl The URL of an image which represents the action.
     * @param tag Arbitrary tag used to group sets of related actions.
     *
     * @return The action that was created.
     */
    virtual carb::ObjectPtr<IAction> registerAction(const char* extensionId,
                                                    const char* actionId,
                                                    IAction::ExecuteFunctionType function,
                                                    const char* displayName = "",
                                                    const char* description = "",
                                                    const char* iconUrl = "",
                                                    const char* tag = "") = 0;

    /**
     * Deregister an action.
     *
     * @param action The action to deregister.
     * @param invalidate Should the action be invalidated so executing does nothing?
     */
    virtual void deregisterAction(carb::ObjectPtr<IAction>& action, bool invalidate = true) = 0;

    /**
     * Find and deregister an action.
     *
     * @param extensionId The id of the source extension that registered the action.
     * @param actionId Id of the action, unique to the extension that registered it.
     * @param invalidate Should the action be invalidated so executing does nothing?
     *
     * @return The action if it exists and was deregistered, an empty ObjectPtr otherwise.
     */
    virtual carb::ObjectPtr<IAction> deregisterAction(const char* extensionId,
                                                      const char* actionId,
                                                      bool invalidate = true) = 0;

    /**
     * Deregister all actions that were registered by the specified extension.
     *
     * @param extensionId The id of the source extension that registered the actions.
     * @param invalidate Should the actions be invalidated so executing does nothing?
     */
    virtual void deregisterAllActionsForExtension(const char* extensionId, bool invalidate = true) = 0;

    /**
     * Find and execute an action.
     *
     * @param extensionId The id of the source extension that registered the action.
     * @param actionId Id of the action, unique to the extension that registered it.
     * @param args Variable positional argument (optional).
     *             Maybe a VariantArray with multiple args.
     * @param kwargs Variable keyword arguments (optional).
     *
     * @return An arbitrary variant object (could be empty).
     */
    virtual carb::variant::Variant executeAction(const char* extensionId,
                                                 const char* actionId,
                                                 const carb::variant::Variant& args = {},
                                                 const carb::dictionary::Item* kwargs = nullptr) const = 0;

    /**
     * Get an action.
     *
     * @param extensionId The id of the source extension that registered the action.
     * @param actionId Id of the action, unique to the extension that registered it.
     *
     * @return The action if it exists, an empty ObjectPtr otherwise.
     */
    virtual carb::ObjectPtr<IAction> getAction(const char* extensionId, const char* actionId) const = 0;

    /**
     * Get the total number of registered actions.
     *
     * @return Total number of registered actions.
     */
    virtual size_t getActionCount() const = 0;

    /**
     * Callback function used by @ref IActionRegistry::walkAllActions.
     *
     * @param action The current action being visited by @ref IActionRegistry::walkAllActions.
     * @param context Any user defined data that was passed to @ref IActionRegistry::walkAllActions.
     *
     * @return True if we should continue walking through all registered actions, false otherwise.
    */
    using WalkActionsCallbackFn = bool(*)(carb::ObjectPtr<IAction> action, void* context);

    /**
     * Walks through all registered actions and calls a callback function for each.
     *
     * @param callbackFn The callback function to call for each registered action,
     * until all actions have been visited or the callback function returns false.
     * @param context User defined data that will be passed to callback function.
     *
     * @return The number of actions that were visited.
     */
    virtual size_t walkAllActions(WalkActionsCallbackFn callbackFn, void* context) const = 0;

    /**
     * Walks through all actions that were registered by the specified extension.
     *
     * @param callbackFn The callback function to call for each registered action,
     * until all actions have been visited or the callback function returns false.
     * @param context User defined data that will be passed to callback function.
     * @param extensionId The id of the extension which registered the actions.
     *
     * @return The number of actions that were visited.
     */
    virtual size_t walkAllActionsRegisteredByExtension(WalkActionsCallbackFn callbackFn,
                                                       void* context,
                                                       const char* extensionId) const = 0;

    /**
     * Get all registered actions.
     *
     * @return All registered actions.
     */
    std::vector<carb::ObjectPtr<IAction>> getAllActions() const
    {
        std::vector<carb::ObjectPtr<IAction>> actions;
        const size_t numActionsWalked = walkAllActions(
            [](carb::ObjectPtr<IAction> action, void* context) {
                auto actionsPtr = static_cast<std::vector<carb::ObjectPtr<IAction>>*>(context);
                actionsPtr->push_back(action);
                return true;
            },
            &actions);

        CARB_ASSERT(numActionsWalked == actions.size());
        CARB_UNUSED(numActionsWalked);
        return actions;
    }

    /**
     * Get all actions that were registered by the specified extension.
     *
     * @param extensionId Id of the extension which registered the actions.
     *
     * @return All actions that were registered by the specified extension.
     */
    std::vector<carb::ObjectPtr<IAction>> getAllActionsForExtension(const char* extensionId) const
    {
        std::vector<carb::ObjectPtr<IAction>> actions;
        const size_t numActionsWalked = walkAllActionsRegisteredByExtension(
            [](carb::ObjectPtr<IAction> action, void* context) {
                auto actionsPtr = static_cast<std::vector<carb::ObjectPtr<IAction>>*>(context);
                actionsPtr->push_back(action);
                return true;
            },
            &actions, extensionId);

        CARB_ASSERT(numActionsWalked == actions.size());
        CARB_UNUSED(numActionsWalked);
        return actions;
    }
};

}
}
}
}
