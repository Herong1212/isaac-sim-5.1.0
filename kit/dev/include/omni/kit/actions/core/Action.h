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

#include <carb/ObjectUtils.h>

#include <omni/String.h>

namespace omni
{
namespace kit
{
namespace actions
{
namespace core
{

/**
 * Abstract action base class providing the core functionaly common to all actions.
 */
class Action : public IAction
{
public:
    /**
     * Struct containing all optional data that can be associated with any action.
     */
    struct MetaData
    {
        omni::string displayName; //!< The name of the action for display purposes.
        omni::string description; //!< A brief description of what the action does.
        omni::string iconUrl; //!< The URL of an image which represents the action.
        omni::string tag; //!< Arbitrary tag used to group sets of related actions.
    };

    /**
     * Constructor.
     *
     * @param extensionId The id of the source extension registering the action.
     * @param actionId Id of the action, unique to the extension registering it.
     * @param metaData Pointer to a meta data struct associated with the action.
     */
    Action(const char* extensionId, const char* actionId, const MetaData* metaData = nullptr)
        : m_extensionId(extensionId ? extensionId : ""), m_actionId(actionId ? actionId : "")
    {
        if (metaData)
        {
            m_metaData = *metaData;
        }
    }

    /**
     * Destructor.
     */
    ~Action() override = default;

    /**
     * @ref IAction::isPythonAction
     */
    bool isPythonAction() const override
    {
        return false;
    }

    /**
     * @ref IAction::getExtensionId
     */
    const char* getExtensionId() const override
    {
        return m_extensionId.c_str();
    }

    /**
     * @ref IAction::getActionId
     */
    const char* getActionId() const override
    {
        return m_actionId.c_str();
    }

    /**
     * @ref IAction::getDisplayName
     */
    const char* getDisplayName() const override
    {
        return m_metaData.displayName.c_str();
    }

    /**
     * @ref IAction::getDescription
     */
    const char* getDescription() const override
    {
        return m_metaData.description.c_str();
    }

    /**
     * @ref IAction::getIconUrl
     */
    const char* getIconUrl() const override
    {
        return m_metaData.iconUrl.c_str();
    }

    /**
     * @ref IAction::getTag
     */
    const char* getTag() const override
    {
        return m_metaData.tag.c_str();
    }

protected:
    omni::string m_extensionId; //!< The id of the source extension that registered the action.
    omni::string m_actionId; //!< Id of the action, unique to the extension that registered it.
    MetaData m_metaData; //!< Struct containing all the meta data associated with this action.

private:
    CARB_IOBJECT_IMPL
};

}
}
}
}
