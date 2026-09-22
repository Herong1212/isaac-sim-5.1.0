# Python Usage Examples


## Creating Actions

```
def new():
    # Code to create a new USD stage.

# Create an action that calls a Python function when executed.
self.action_new = omni.kit.actions.core.Action(
    "omni.kit.window.file",
    "new",
    new,
    display_name="File->New",
    description="Create a new USD stage."
)

# Create an action that calls a Python lambda when executed.
self.action_save = omni.kit.actions.core.Action(
    "omni.kit.window.file",
    "save",
    lambda: some.other.file.save(),
    display_name="File->Save",
    description="Save the currently opened USD stage to file."
)
```


## Registering Actions

```
# Create and register an action at the same time (the resulting action is returned, can be stored if needed).
omni.kit.actions.core.get_action_registry().register_action(
    "omni.kit.window.file",
    "new",
    new,
    display_name="File->New",
    description="Create a new USD stage."
)

# Or create and store an action...
self.action_save = omni.kit.actions.core.Action(
    "omni.kit.window.file",
    "save",
    lambda: some.other.file.save(),
    display_name="File->Save",
    description="Save the currently opened USD stage to file."
)

# ...then register it explicitly.
omni.kit.actions.core.get_action_registry().register_action(self.action_save)
```


## Discovering Actions

```
action_registry = omni.kit.actions.core.get_action_registry()

# Retrieve an action that has been registered using the registering extension id and the action id.
action = action_registry.get_action("omni.kit.window.file", "new")

# Retrieve all actions that have been registered by a specific extension id.
actions = action_registry.get_all_actions_for_extension("omni.kit.window.file")

# Retrieve all actions that have been registered by any extension.
all_actions = action_registry.get_all_actions()
```

Note: These functions will return any action that has been registered from either Python or C++,
and you can interact with them without needing to know anything about where they were registered.


## Deregistering Actions

```
action_registry = omni.kit.actions.core.get_action_registry()

# Deregister an action directly...
action_registry.deregister_action(self.action_save)

# or using the registering extension id and the action id...
action_registry.deregister_action("omni.kit.window.file", "new")

# or deregister all actions that were registered by an extension.
action_registry.deregister_all_actions_for_extension("omni.kit.window.file")
```

Note: Actions are ref counted and will be destroyed once nothing (including the action registry) is holding a
reference to it, which is what allows us to register an action without explicitly storing a reference to it,
and deregister an action that we haven’t stored a reference to (if anything else is holding a reference to
it then the action won’t be destroyed until all references are released, even though deregistering it from
the action registry means it will no longer be discoverable). By default, actions are invalidated (meaning
that executing them will do nothing) when they are deregistered (passing invalidate=false will skip this).


## Executing Actions

```
action_registry = omni.kit.actions.core.get_action_registry()

# Execute an action after retrieving it from the action registry.
action = action_registry.get_action("omni.kit.window.file", "new")
action.execute()

# Execute an action indirectly (retrieves it internally).
omni.kit.actions.core.execute_action("omni.kit.window.file", "new")

# Execute an action that we stored previously.
self.action_save.execute()

# Execute an action that returns something.
test_action = omni.kit.actions.core.Action("omni.kit.actions.core_tests", "test_action", lambda x: x*x)
value_squared = test_action.execute(9)
self.assertEqual(value_squared, 81)
```


## Executing Actions With Arguments

```
# Create an action which accepts an argument...
self.action_open = omni.kit.actions.core.get_action_registry().register_action(
    "omni.kit.window.file",
    "open",
    lambda stage_url: some.other.file.open(stage_url),
    display_name="File->Open",
    description="Open an existing USD stage."
)

# and execute it directly...
self.action_open.execute("omniverse:://url/of/stage/to/open")

# or indirectly.
omni.kit.actions.core.execute_action("omni.kit.window.file", "open", "omniverse:://url/of/stage/to/open")
```


## Executing Actions With Keyword Arguments

```
def open(stage_url, save_existing=True, log_string=""):
    if save_existing:
        some.other.file.save()
    some.other.file.open(stage_url, log_string)

# Define an action which accepts multiple arguments...
self.action_open = omni.kit.actions.core.get_action_registry().register_action(
    "omni.kit.window.file",
    "open",
    open,
    display_name="File->Open"
)

# and execute it using positional args...
self.action_open.execute("url_of_stage_to_open", False, "Opening new stage!")

# keyword args...
self.action_open.execute(stage_url="url_of_stage_to_open", log_string="Opening new stage!")

# or a combination of both.
self.action_open.execute("url_of_stage_to_open", log_string="Opening new stage!")
```


## Executing Actions With Variable Arguments

```
def test_function(*args, **kwargs):
    # Parse args and/or kwargs then do things with them!

# Define an action which accepts variable and keyword arguments...
self.action_test = omni.kit.actions.core.get_action_registry().register_action(
    "omni.kit.actions.core_tests",
    "test_action",
    test_function
)

# and execute it using whatever you want directly...
self.action_test.execute()
self.action_test.execute(False)
self.action_test.execute(9)
self.action_test.execute("Ninety-Nine")
self.action_test.execute("Some String", True, 99)
self.action_test.execute(keyword_arg_name="Some Other String", other_keyword_arg_name=9)
self.action_test.execute("Positional Arg Value", 9, keyword_arg_name="Keyword Arg Value")

# or indirectly.
omni.kit.actions.core.execute_action("omni.kit.actions.core_tests", "test_action", 9, keyword_arg=True)
```


