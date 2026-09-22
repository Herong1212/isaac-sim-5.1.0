# Public API for module omni.kit.actions.core:

## Classes

- class Action
  - def __init__(self, extension_id: str, action_id: str, python_object: object, display_name: str = '', description: str = '', icon_url: str = '', tag: str = '')
  - def execute(self, *args, **kwargs) -> object
  - def invalidate(self)
  - [property] def description(self) -> str
  - [property] def display_name(self) -> str
  - [property] def extension_id(self) -> str
  - [property] def icon_url(self) -> str
  - [property] def id(self) -> str
  - [property] def parameters(self) -> dict
  - [property] def requires_parameters(self) -> bool
  - [property] def tag(self) -> str

- class IActionRegistry
  - static def deregister_action(*args, **kwargs) -> typing.Any
  - def deregister_all_actions_for_extension(self, extension_id: str, invalidate: bool = True)
  - def execute_action(self, extension_id: str, action_id: str, *args, **kwargs) -> object
  - static def get_action(*args, **kwargs) -> typing.Any
  - static def get_all_actions(*args, **kwargs) -> typing.Any
  - static def get_all_actions_for_extension(*args, **kwargs) -> typing.Any
  - static def register_action(*args, **kwargs) -> typing.Any

## Functions

- def get_action_registry() -> IActionRegistry
- def execute_action(extension_id: str, action_id: str, *args, **kwargs)
