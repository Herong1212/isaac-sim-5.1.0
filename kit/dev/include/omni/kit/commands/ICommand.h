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
#include <carb/dictionary/IDictionary.h>

namespace omni
{
namespace kit
{
namespace commands
{

/**
 * Pure virtual command interface.
 */
class ICommand : public carb::IObject
{
public:
    /**
     * Factory function prototype to create a new command instance.
     *
     * @param extensionId The id of the source extension registering the command.
     * @param commandName The command name, unique to the extension registering it.
     * @param kwargs Arbitrary keyword arguments the command will be executed with.
     *
     * @return The command object that was created.
     */
    using CreateFunctionType = carb::ObjectPtr<ICommand> (*)(const char* /*extensionId*/,
                                                             const char* /*commandName*/,
                                                             const carb::dictionary::Item* /*kwargs*/);

    /**
     * Function prototype to populate keyword arguments expected by a command along with default values.
     *
     * @param defaultKwargs Dictionary item to fill with all keyword arguments that have default values.
     * @param optionalKwargs Dictionary item to fill with all other keyword arguments that are optional.
     * @param requiredKwargs Dictionary item to fill with all other keyword arguments that are required.
     */
    using PopulateKeywordArgsFunctionType = void (*)(carb::dictionary::Item* /*defaultKwargs*/,
                                                     carb::dictionary::Item* /*optionalKwargs*/,
                                                     carb::dictionary::Item* /*requiredKwargs*/);

    /**
     * Get the id of the source extension which registered this command.
     *
     * @return Id of the source extension which registered this command.
     */
    virtual const char* getExtensionId() const = 0;

    /**
     * Get the name of this command, unique to the extension that registered it.
     *
     * @return Name of this command, unique to the extension that registered it.
     */
    virtual const char* getName() const = 0;

    /**
     * Called when this command object is being executed,
     * either originally or in response to a redo request.
     */
    virtual void doCommand() = 0;

    /**
     * Called when this command object is being undone.
     */
    virtual void undoCommand() = 0;
};

using ICommandPtr = carb::ObjectPtr<ICommand>;

}
}
}
