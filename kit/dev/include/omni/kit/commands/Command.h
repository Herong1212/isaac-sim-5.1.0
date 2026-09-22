// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/kit/commands/ICommand.h>

#include <carb/ObjectUtils.h>

#include <omni/String.h>

namespace omni
{
namespace kit
{
namespace commands
{

/**
 * Abstract command base class providing the core functionaly common to all commands.
 */
class Command : public ICommand
{
public:
    /**
     * Constructor.
     *
     * @param extensionId The id of the source extension registering the command.
     * @param commandName The command name, unique to the registering extension.
     */
    Command(const char* extensionId, const char* commandName)
        : m_extensionId(extensionId ? extensionId : ""), m_commandName(commandName ? commandName : "")
    {
    }

    /**
     * Destructor.
     */
    ~Command() override = default;

    /**
     * @ref ICommand::getExtensionId
     */
    const char* getExtensionId() const override
    {
        return m_extensionId.c_str();
    }

    /**
     * @ref ICommand::getName
     */
    const char* getName() const override
    {
        return m_commandName.c_str();
    }

protected:
    omni::string m_extensionId; //!< The id of the source extension that registered the command.
    omni::string m_commandName; //!< Name of the command, unique to the registering extension.

private:
    CARB_IOBJECT_IMPL
};

}
}
}
