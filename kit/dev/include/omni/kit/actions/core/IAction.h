// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/IObject.h>
#include <carb/variant/IVariant.h>
#include <carb/dictionary/IDictionary.h>
#include <carb/variant/VariantUtils.h>

namespace omni
{
namespace kit
{
namespace actions
{
namespace core
{

/**
 * Pure virtual action interface.
 */
class IAction : public carb::IObject
{
public:
    /**
     * Function prototype to execute an action.
     *
     * @param args Variable positional argument (optional).
     *             Maybe a VariantArray with multiple args.
     * @param kwargs Variable keyword arguments (optional).
     *
     * @return An arbitrary variant object (could be empty).
     */
    using ExecuteFunctionType = carb::variant::Variant (*)(const carb::variant::Variant& /*args*/,
                                                           const carb::dictionary::Item* /*kwargs*/);

    /**
     * Called when something wants to execute this action.
     *
     * @param args Variable positional argument (optional).
     *             Maybe a VariantArray with multiple args.
     * @param kwargs Variable keyword arguments (optional).
     *
     * @return An arbitrary variant object (could be empty).
     */
    virtual carb::variant::Variant execute(const carb::variant::Variant& args = {},
                                           const carb::dictionary::Item* kwargs = nullptr) = 0;

    /**
     * Invalidate this action so that executing it will not do anything.
     * This can be called if it is no longer safe to execute the action,
     * and by default is called when deregistering an action (optional).
     */
    virtual void invalidate() = 0;

    /**
     * Is this an instance of the derived PythonAction class?
     *
     * @return True if this an instance of the derived PythonAction class, false otherwise.
     */
    virtual bool isPythonAction() const = 0;

    /**
     * Get the id of the source extension which registered this action.
     *
     * @return Id of the source extension which registered this action.
     */
    virtual const char* getExtensionId() const = 0;

    /**
     * Get the id of this action, unique to the extension that registered it.
     *
     * @return Id of this action, unique to the extension that registered it.
     */
    virtual const char* getActionId() const = 0;

    /**
     * Get the display name of this action.
     *
     * @return Display name of this action.
     */
    virtual const char* getDisplayName() const = 0;

    /**
     * Get the description of this action.
     *
     * @return Description of this action.
     */
    virtual const char* getDescription() const = 0;

    /**
     * Get the URL of the icon used to represent this action.
     *
     * @return URL of the icon used to represent this action.
     */
    virtual const char* getIconUrl() const = 0;

    /**
     * Get the tag that this action is grouped with.
     *
     * @return Tag that this action is grouped with.
     */
    virtual const char* getTag() const = 0;
};

using IActionPtr = carb::ObjectPtr<IAction>;

inline bool operator==(const carb::ObjectPtr<IAction>& left, const carb::ObjectPtr<IAction>& right) noexcept
{
    return (left.get() == right.get());
}
}
}
}
}
