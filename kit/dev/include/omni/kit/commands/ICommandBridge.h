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

#include <carb/dictionary/IDictionary.h>
#include <carb/Interface.h>

namespace omni
{
namespace kit
{
namespace commands
{

/**
 * Defines the interface for the CommandBridge. Commands were originally
 * written in (and only available to use from) Python, so this interface
 * acts as a bridge allowing them to be registered and executed from C++
 */
class ICommandBridge
{
public:
    CARB_PLUGIN_INTERFACE("omni::kit::commands::ICommandBridge", 1, 0);

    using RegisterFunctionType = void (*)(const char*,
                                          const char*,
                                          const carb::dictionary::Item*,
                                          const carb::dictionary::Item*,
                                          const carb::dictionary::Item*);
    using DeregisterFunctionType = void (*)(const char*, const char*);
    using ExecuteFunctionType = bool (*)(const char*, const char*, const carb::dictionary::Item*);
    using UndoFunctionType = bool (*)();
    using RedoFunctionType = bool (*)();
    using RepeatFunctionType = bool (*)();
    using VoidFunctionType = void (*)();

    /**
     * Enable the command bridge so that new command types can be registered and deregistered from C++,
     * and so that existing command types can be executed in Python (where commands are held) from C++.
     *
     * @param registerFunction Function responsible for registering new C++ command types with Python.
     * @param deregisterFunction Function responsible for deregistering C++ command types from Python.
     * @param executeFunction Function responsible for executing existing commands in Python from C++.
     * @param undoFunction Function responsible for calling undo on past commands in Python from C++.
     * @param redoFunction Function responsible for calling redo on past commands in Python from C++.
     * @param repeatFunction Function responsible for calling repeat on past commands in Python from C++.
     * @param beginUndoGroupFunction Function responsible for opening an undo group in Python from C++.
     * @param endUndoGroupFunction Function responsible for closing an undo group in Python from C++.
     * @param beginUndoDisabledFunction Function responsible for disabling undo in Python from C++.
     * @param endUndoDisabledFunction Function responsible for re-enabling undo in Python from C++.
     */
    virtual void enableBridge(RegisterFunctionType registerFunction,
                              DeregisterFunctionType deregisterFunction,
                              ExecuteFunctionType executeFunction,
                              UndoFunctionType undoFunction,
                              RedoFunctionType redoFunction,
                              RepeatFunctionType repeatFunction,
                              VoidFunctionType beginUndoGroupFunction,
                              VoidFunctionType endUndoGroupFunction,
                              VoidFunctionType beginUndoDisabledFunction,
                              VoidFunctionType endUndoDisabledFunction) = 0;

    /**
     * Disable the command bridge so that new command types can no longer be registered and deregistered from C++,
     * and so that existing command types can no longer be executed in Python (where commands are held) from C++.
     * Calling this will also cause any remaining command types previously registered in C++ to be deregistered.
     */
    virtual void disableBridge() = 0;

    /**
     * Bridge function to call from C++ to register a C++ command type with Python.
     *
     * @param extensionId The id of the source extension registering the command.
     * @param commandName The command name, unique to the registering extension.
     * @param factory Factory function used to create instances of the command.
     * @param populateKeywordArgs Function called to populate the keyword args.
     */
    virtual void registerCommand(const char* extensionId,
                                 const char* commandName,
                                 ICommand::CreateFunctionType factory,
                                 ICommand::PopulateKeywordArgsFunctionType populateKeywordArgs) = 0;

    /**
     * Bridge function to call from C++ to deregister a C++ command type from Python.
     *
     * @param extensionId The id of the source extension that registered the command.
     * @param commandName Command name, unique to the extension that registered it.
     */
    virtual void deregisterCommand(const char* extensionId, const char* commandName) = 0;

    /**
     * Deregister all C++ command types that were registered by the specified extension.
     *
     * @param extensionId The id of the source extension that registered the commands.
     */
    virtual void deregisterAllCommandsForExtension(const char* extensionId) = 0;

    /**
     * Bridge function to call from C++ to execute any existing command type in Python.
     *
     * @param commandName Command name, unique to the extension that registered it.
     * @param kwargs Arbitrary keyword arguments the command will be executed with.
     *
     * @return True if the command object was created and executed, false otherwise.
     */
    virtual bool executeCommand(const char* commandName, const carb::dictionary::Item* kwargs = nullptr) const = 0;

    /**
     * Bridge function to call from C++ to execute any existing command type in Python.
     *
     * @param extensionId The id of the source extension that registered the command.
     * @param commandName Command name, unique to the extension that registered it.
     * @param kwargs Arbitrary keyword arguments the command will be executed with.
     *
     * @return True if the command object was created and executed, false otherwise.
     */
    virtual bool executeCommand(const char* extensionId,
                                const char* commandName,
                                const carb::dictionary::Item* kwargs = nullptr) const = 0;

    /**
     * Bridge function to call from Python to create a new instance of a C++ command.
     *
     * @param extensionId The id of the source extension that registered the command.
     * @param commandName The command name, unique to the extension that registered it.
     * @param kwargs Arbitrary keyword arguments that the command will be executed with.
     *
     * @return A command object if it was created, or an empty ObjectPtr otherwise.
     */
    virtual carb::ObjectPtr<ICommand> createCommandObject(const char* extensionId,
                                                          const char* commandName,
                                                          const carb::dictionary::Item* kwargs = nullptr) const = 0;

    /**
     * Bridge function to call from C++ to undo the last command that was executed.
     *
     * @return True if the last command was successfully undone, false otherwise.
     */
    virtual bool undoCommand() const = 0;

    /**
     * Bridge function to call from C++ to redo the last command that was undone.
     *
     * @return True if the last command was successfully redone, false otherwise.
     */
    virtual bool redoCommand() const = 0;

    /**
     * Bridge function to call from C++ to repeat the last command that was executed or redone.
     *
     * @return True if the last command was successfully repeated, false otherwise.
     */
    virtual bool repeatCommand() const = 0;

    /**
     * Bridge function to call from C++ to begin a new group of commands to be undone together.
     */
    virtual void beginUndoGroup() const = 0;

    /**
     * Bridge function to call from C++ to end a new group of commands to be undone together.
     */
    virtual void endUndoGroup() const = 0;

    /**
     * Bridge function to call from C++ to begin disabling undo for subsequent commands.
     */
    virtual void beginUndoDisabled() const = 0;

    /**
     * Bridge function to call from C++ to end disabling undo for subsequent commands.
     */
    virtual void endUndoDisabled() const = 0;

    /**
     * RAII class used to begin and end a new undo group within a specific scope.
     */
    class ScopedUndoGroup
    {
    public:
        ScopedUndoGroup()
        {
            if (ICommandBridge* commandBridge = carb::getCachedInterface<ICommandBridge>())
            {
                commandBridge->beginUndoGroup();
            }
        }

        ~ScopedUndoGroup()
        {
            if (ICommandBridge* commandBridge = carb::getCachedInterface<ICommandBridge>())
            {
                commandBridge->endUndoGroup();
            }
        }
    };

    /**
     * RAII class used to begin and end disabling undo within a specific scope.
     */
    class ScopedUndoDisabled
    {
    public:
        ScopedUndoDisabled()
        {
            if (ICommandBridge* commandBridge = carb::getCachedInterface<ICommandBridge>())
            {
                commandBridge->beginUndoDisabled();
            }
        }

        ~ScopedUndoDisabled()
        {
            if (ICommandBridge* commandBridge = carb::getCachedInterface<ICommandBridge>())
            {
                commandBridge->endUndoDisabled();
            }
        }
    };
};

}
}
}
