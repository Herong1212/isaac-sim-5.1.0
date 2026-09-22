```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Omni Kit Actions Core extension is a framework for creating, registering, and discovering actions. Actions are programmable objects that can encapsulate anything which occurs in a fire and forget manner. An action can be created in one extension and then executed from anywhere else in the application; for example, a user could execute the same action via a UI Menu, Hot Key, or Gesture.

```{mermaid}
graph TD
  subgraph Interactions[Interactions]
    Interaction1(UI Menu)
    Interaction2(Hot Key)
    Interaction3(Gesture)
    Interaction4(Voice)
  end
  Extension[Extension] -->|Register| Action[Action]
  Interaction1 -->|Execute| Action[Action]
  Interaction2 -->|Execute| Action[Action]
  Interaction3 -->|Execute| Action[Action]
  Interaction4 -->|Execute| Action[Action]
```

## Actions

Actions can be:
- Created, registered, discovered, and executed from any extension in C++, Python, or a mix of the two.
- Created with associated metadata to aid in their discoverability and/or display in a UI.
- Executed in a 'fire and forget' manner.
- Executed using arbitrary parameters.

Actions are not stateful (although their end result may not manifest immediately), therefore they do not support undo/redo functionality.

## Action Registry

The Action Registry maintains a collection of all registered actions and allows any extension to:
- Register new actions.
- Deregister existing actions.
- Discover registered actions.

 Here is an example of registering an action from Python that creates a new file when it is executed:

```
action_registry = omni.kit.actions.core.get_action_registry()
actions_tag = "File Actions"

action_registry.register_action(
    extension_id,
    "new",
    omni.kit.window.file.new,
    display_name="File->New",
    description="Create a new USD stage.",
    tag=actions_tag,
)
```

For more examples, please consult the [Python](USAGE_PYTHON) and [C++](USAGE_CPP) usage pages.

## User Guide

- [](USAGE_PYTHON)
- [](USAGE_CPP)
- [](CHANGELOG)

