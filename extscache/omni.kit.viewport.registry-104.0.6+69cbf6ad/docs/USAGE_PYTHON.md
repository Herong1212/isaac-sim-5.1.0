```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Usage Examples

## Adding and Removing Notifiers to Registry
```python
from omni.kit.viewport.registry import RegisterScene

# Define a notifier callback function
def scene_type_notification(factory, loading):
    if loading:
        print(f"Scene factory {factory.factory_id} loaded")
    else:
        print(f"Scene factory {factory.factory_id} unloaded")

# Add notifier to RegisterScene
RegisterScene.add_notifier(scene_type_notification)

# ... Perform operations that trigger the notifier ...

# Remove notifier from RegisterScene
RegisterScene.remove_notifier(scene_type_notification)
```

## Registering and Deregistering Factories with Auto Destruct
```python
from omni.kit.viewport.registry import RegisterScene

# Define a factory class
class SceneFactory:
    def __init__(self, id_str):
        self.factory_id = id_str

# Define a notifier callback function
def scene_type_notification(factory, loading):
    if loading:
        print(f"Scene factory {factory.factory_id} loaded")
    else:
        print(f"Scene factory {factory.factory_id} unloaded")

# Add notifier to RegisterScene
RegisterScene.add_notifier(scene_type_notification)

# Register a factory and immediately lose the reference to it
# to simulate auto-destruct behavior (factory goes out of scope)
factory_id = "my_scene_factory"
scene_registration = RegisterScene(SceneFactory, factory_id)
del scene_registration

# Since the factory registration object is deleted, the factory is automatically deregistered
```

## Factory Registration and Ordered Retrieval
```python
from omni.kit.viewport.registry import RegisterScene

# Define a factory class
class SceneFactory:
    def __init__(self, id_str):
        self.factory_id = id_str

# Register multiple factories
scene_factories = [RegisterScene(SceneFactory, f"factory_{i}") for i in range(5)]

# Define a custom order for the factories
custom_order = ["factory_2", "factory_0", "factory_4"]

# Retrieve the factories in the specified custom order, excluding unknown and appending unknown
ordered_factories = RegisterScene.ordered_factories(custom_order, append_unkown=True, ignore_unknown=[])

# Print the ordered factory IDs
for factory_id, factory in ordered_factories:
    if factory is not None:
        print(f"Ordered factory: {factory_id}")

# Deregister factories by destroying the registration objects
for registration in scene_factories:
    registration.destroy()
```

## Excluding Specific Factories from Ordered Retrieval
```python
from omni.kit.viewport.registry import RegisterScene

# Define a factory class
class SceneFactory:
    def __init__(self, id_str):
        self.factory_id = id_str

# Register multiple factories
scene_factories = [RegisterScene(SceneFactory, f"factory_{i}") for i in range(5)]

# Define a custom order for the factories
custom_order = ["factory_2", "factory_0", "factory_4"]

# Define factories to ignore
factories_to_ignore = ["factory_1", "factory_3"]

# Retrieve the factories in the specified custom order, excluding the ignored ones
ordered_factories = RegisterScene.ordered_factories(custom_order, append_unkown=True, ignore_unknown=factories_to_ignore)

# Print the ordered factory IDs, excluding the ignored ones
for factory_id, factory in ordered_factories:
    if factory is not None and factory_id not in factories_to_ignore:
        print(f"Ordered factory: {factory_id}")
```