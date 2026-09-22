# Usage Examples

## Register/Unregister Custom Data Accessor
```python
from omni.kit.manipulator.prim.core import get_prim_data_accessor_registry
from omni.kit.viewport.manipulator.transform import DataAccessor

# custom data accessor
class CustomDataAccessor(DataAccessor):
    def __init__(self, *args, **kwargs):
        super().__init__()
        print("CustomDataAccessor init")

    def get_sdf_path_type(self):
        import pxr
        return pxr.Sdf.Path

    @property
    def priority(self) -> int:
        return 1

    @property
    def priority_write(self) -> int:
        return 1

    def get_data_tag(self) -> str:
        return "USD"

    def destroy(self):
        print("CustomDataAccessor destroyed")

    def get_local_to_world_transform(self, obj):
        pass

    def get_parent_to_world_transform(self, obj):
        pass

    def clear_xform_cache(self):
        pass

    def update_xform_cache(self):
        pass

# get the singleton instance of the PrimDataAccessorRegistry
prim_data_accessor_registry = get_prim_data_accessor_registry()
# register custom data accessor
prim_data_accessor_registry.register_data_accessor(CustomDataAccessor, "CUSTOM")

# unregister custom data accessor
prim_data_accessor_registry.unregister_data_accessor("CUSTOM")
prim_data_accessor_registry = None
```


## Custom a Prim Transform Manipulator
```python
from omni.kit.manipulator.prim.core import PrimTransformManipulator, PrimTransformModel
from omni.kit.viewport.registry import RegisterScene


class CustomPrimTransformModel(PrimTransformModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_selection_changed(self, selection):
        """Handles updates to the selection of prims within the model."""
        print(f"changed prims : {selection}")

# Creates a custom manipulator only works on mesh prims
class CustomPrimTransformManipulator(PrimTransformManipulator):
    def __init__(self, usd_context_name: str = "", viewport_api=None):
        custom_model = CustomPrimTransformModel(usd_context_name, viewport_api)
        super().__init__(
            usd_context_name=usd_context_name,
            viewport_api=viewport_api,
            name="omni.kit.manipulator.test_mesh_prim",
            model=custom_model,
            size=0.5,
        )

    def on_selection_changed(self, stage, selection, *args, **kwargs) -> bool:
        if selection is None:
            self.model.on_selection_changed([])
            return False

        self.model.on_selection_changed(selection)
        for path in selection:
            prim = stage.GetPrimAtPath(path)
            if prim.IsA(UsdGeom.Mesh):
                return True

        return False

class CustomScene:
    def __init__(self, desc):
        usd_context_name = desc.get("usd_context_name")
        self.__transform_manip_override = CustomPrimTransformManipulator(
            usd_context_name=usd_context_name, viewport_api=desc.get("viewport_api")
        )

    def destroy(self):
        if self.__transform_manip_override:
            self.__transform_manip_override.destroy()
            self.__transform_manip_override = None

# register the custom scene to make the custom manipulator could works
scene = RegisterScene(CustomScene, "omni.kit.manipulator.custom")

# relase and destroy the custom scene
scene = None
```

## Custom Toolbar Button
```python
from omni.kit.manipulator.prim.core import get_toolbar_registry
from omni.kit.manipulator.transform.toolbar_tool import SimpleToolButton

#create custom tool
class CustomToolButton(SimpleToolButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("custom tool button init")

    @classmethod
    def can_build(cls, manipulator, operation) -> bool:
        return True


toolbar_registry = get_toolbar_registry()

# register custom tool
toolbar_registry.register_tool(CustomToolButton, "Custom tool button")

# unregister custom tool
toolbar_registry.unregister_tool("Custom tool button")
```

## Toggle Transform Manipulator Toolbar
```python
import carb.settings

# Get the settings interface
settings = carb.settings.get_settings()

# Toggle the visibility of the transform manipulator toolbar
toolbar_enabled = settings.get("/exts/omni.kit.manipulator.prim.core/tools/enabled")
settings.set("/exts/omni.kit.manipulator.prim.core/tools/enabled", not toolbar_enabled)
```
