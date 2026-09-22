# C++ Usage Examples


## Creating Actions

```
// Create an action that calls a C++ lambda function when executed.
omni::kit::actions::core::IAction::MetaData metaData;
metaData.displayName = "Quit";
metaData.description = "Quit the application.";
metaData.tag = "Application Actions";
m_quitAppAction =
    omni::kit::actions::core::LambdaAction::create(
        "omni.kit.app", "quit", &metaData,
        [this](const carb::variant::Variant& args = {}, const carb::dictionary::Item* kwargs = nullptr) {
            const int returnCode = args.getValueOr<int>(0);
            postQuit(returnCode);
            return carb::variant::Variant(true);
        }));
```


## Registering Actions

```
auto actionRegistry = carb::getCachedInterface<omni::kit::actions::core::IActionRegistry>();

// Create and register an action at the same time (the resulting action is returned, can be stored if needed).
actionRegistry->registerAction(
    "omni.kit.app", "quit",
    [](const carb::variant::Variant& args = {}, const carb::dictionary::Item* kwargs = nullptr) {
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            const int returnCode = args.getValueOr<int>(0);
            app->postQuit(returnCode);
        }
        return carb::variant::Variant();
    },
    "Quit", "Quit the application.", "Application Actions");

// Or register one that was already created explicitly.
actionRegistry->registerAction(m_quitAppAction);
```


## Discovering Actions

```
auto registry = carb::getCachedInterface<omni::kit::actions::core::IActionRegistry>();

// Retrieve an action that has been registered using the registering extension id and the action id.
carb::ObjectPtr<IAction> action = registry->getAction("omni.kit.app", "quit");

// Retrieve all actions that have been registered by a specific extension id.
std::vector<carb::ObjectPtr<IAction>> actions = registry->getAllActionsForExtension("omni.kit.app");

// Retrieve all actions that have been registered by any extension.
std::vector<carb::ObjectPtr<IAction>> actions = registry->getAllActions();
```

Note: These functions will return any action that has been registered from either Python or C++,
and you can interact with them without needing to know anything about where they were registered.


## Deregistering Actions

```
auto actionRegistry = carb::getCachedInterface<omni::kit::actions::core::IActionRegistry>();

// Deregister an action directly...
actionRegistry->deregisterAction(m_quitAppAction);

// or using the registering extension id and the action id...
actionRegistry->deregisterAction("omni.kit.app", "quit");

// or deregister all actions that were registered by an extension.
actionRegistry->deregisterAllActionsForExtension("omni.kit.app");
```

Note: Actions are ref counted and will be destroyed once nothing (including the action registry) is holding a
reference to it, which is what allows us to register an action without explicitly storing a reference to it,
and deregister an action that we haven’t stored a reference to (if anything else is holding a reference to
it then the action won’t be destroyed until all references are released, even though deregistering it from
the action registry means it will no longer be discoverable). By default, actions are invalidated (meaning
that executing them will do nothing) when they are deregistered (passing invalidate=false will skip this).


## Executing Actions

```
auto actionRegistry = carb::getCachedInterface<omni::kit::actions::core::IActionRegistry>();

// Execute an action after retrieving it from the action registry.
auto action = actionRegistry->getAction("omni.kit.app", "quit");
action->execute();

// Execute an action indirectly (retrieves it internally).
actionRegistry->executeAction("omni.kit.app", "quit");

// Execute an action that we stored previously.
m_quitAppAction->execute();
```


## Executing Actions With Arguments

```
// Create an action which accepts an argument and returns something...
auto testAction =
    carb::stealObject<omni::kit::actions::core::IAction>(new omni::kit::actions::core::LambdaAction(
        "omni.kit.actions.core_tests", "test_action", nullptr,
        [](const carb::variant::Variant& args = {}, const carb::dictionary::Item* kwargs = nullptr) {
            const int value = args.getValueOr<int>(0);
            return carb::variant::Variant(value * value);
        }));

// then execute it directly.
carb::variant::Variant valueSquared = testAction->execute(carb::variant::Variant(9));
CARB_ASSERT(valueSquared.getValueOr<int>(0) == 81);
```

Note: When executing an action that was created in Python from C++, the args and kwargs will be converted
(as best as possible) to their equivalent Python positional argument and keyword argument packs, and vice
versa when executing an action that was created in C++ from Python.


## Executing Actions With Keyword Arguments

```
// Create an action which accepts an argument and returns something...
auto testAction =
    carb::stealObject<omni::kit::actions::core::IAction>(new omni::kit::actions::core::LambdaAction(
        "omni.kit.actions.core_tests", "test_action", nullptr,
        [this](const carb::variant::Variant& args = {}, const carb::dictionary::Item* kwargs = nullptr) {
            int value = 0;
            if (kwargs)
            {
                auto iDictionary = carb::getCachedInterface<carb::dictionary::IDictionary>();
                const carb::dictionary::Item* kwarg = iDictionary->getItem(kwargs, "value");
                const carb::dictionary::ItemType paramType = iDictionary->getItemType(kwarg);
                value = paramType == carb::dictionary::ItemType::eInt ? iDictionary->getAsInt(kwarg) : 0;
            }
            return carb::variant::Variant(value * value);
        }));

// then execute it directly.
auto iDictionary = carb::getCachedInterface<carb::dictionary::IDictionary>();
carb::dictionary::Item* kwargs = iDictionary->createItem(nullptr, "", carb::dictionary::ItemType::eDictionary);
iDictionary->makeIntAtPath(kwargs, "value", 9);
carb::variant::Variant valueSquared = testAction->execute({}, kwargs);
iDictionary->destroyItem(kwargs);
CARB_ASSERT(valueSquared.getValueOr<int>(0) == 81);
```

