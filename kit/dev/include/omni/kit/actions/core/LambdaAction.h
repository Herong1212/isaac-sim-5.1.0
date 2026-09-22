// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/kit/actions/core/Action.h>

#include <carb/thread/Mutex.h>

namespace omni
{
namespace kit
{
namespace actions
{
namespace core
{

/**
 * Concrete action class that can be used to create an action from C++ which calls a supplied lambda/function.
 */
class LambdaAction : public Action
{
public:
    /**
     * Factory.
     *
     * @param extensionId The id of the source extension registering the action.
     * @param actionId Id of the action, unique to the extension registering it.
     * @param metaData Pointer to a meta data struct associated with the action.
     * @param function The function object to call when the action is executed.
     *
     * @return The action that was created.
     */
    static carb::ObjectPtr<IAction> create(const char* extensionId,
                                           const char* actionId,
                                           const MetaData* metaData,
                                           ExecuteFunctionType function)
    {
        // Note: It is important to construct the handler using ObjectPtr<T>::InitPolicy::eSteal,
        // otherwise we end up incresing the reference count by one too many during construction,
        // resulting in a carb::ObjectPtr<IAction> whose object instance will never be destroyed.
        return carb::stealObject<IAction>(new LambdaAction(extensionId, actionId, metaData, function));
    }

    /**
     * Constructor.
     *
     * @param extensionId The id of the source extension registering the action.
     * @param actionId Id of the action, unique to the extension registering it.
     * @param metaData Pointer to a meta data struct associated with the action.
     * @param function The function object to call when the action is executed.
     */
    LambdaAction(const char* extensionId, const char* actionId, const MetaData* metaData, ExecuteFunctionType function)
        : Action(extensionId, actionId, metaData), m_function(function)
    {
    }

    /**
     * Destructor.
     */
    ~LambdaAction() override = default;

    /**
     * @ref IAction::execute
     */
    carb::variant::Variant execute(const carb::variant::Variant& args = {},
                                   const carb::dictionary::Item* kwargs = nullptr) override
    {
        std::lock_guard<carb::thread::mutex> lock(m_mutex);
        return m_function ? m_function(args, kwargs) : carb::variant::Variant();
    }

    /**
     * @ref IAction::invalidate
     */
    void invalidate() override
    {
        std::lock_guard<carb::thread::mutex> lock(m_mutex);
        m_function = nullptr;
    }

private:
    ExecuteFunctionType m_function; //!< The function object to call when the action is executed.
    carb::thread::mutex m_mutex; //!< Mutex to lock for thread safety when calling the function.
};

}
}
}
}
