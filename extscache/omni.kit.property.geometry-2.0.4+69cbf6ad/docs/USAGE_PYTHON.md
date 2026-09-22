# Usage Examples

## Set Primvar Values on Selected Prims

```python
import omni.kit.commands
import omni.kit.property.geometry
import omni.usd

# Get the current USD context
usd_context = omni.usd.get_context()

# Get the path of the currently selected prim(s)
selection = usd_context.get_selection()
prim_paths = selection.get_selected_prim_paths()

if prim_paths:
    # Set a boolean primvar on the selected prims
    bool_primvar = omni.kit.property.geometry.PrimVarCommand(
        prim_path=prim_paths,
        prim_name="myBoolean",
        prim_type="Sdf.ValueTypeNames.Bool",
        value=True
    )
    omni.kit.commands.execute(bool_primvar)
    
    # Set a float primvar on the selected prims
    float_primvar = omni.kit.property.geometry.PrimVarCommand(
        prim_path=prim_paths,
        prim_name="myFloat",
        prim_type="Sdf.ValueTypeNames.Float",
        value=3.14
    )
    omni.kit.commands.execute(float_primvar)
```
---

## Toggle Boolean Primvar on Selected Prims

```python
import omni.kit.commands
import omni.kit.property.geometry
import omni.usd

# Get the current USD context
usd_context = omni.usd.get_context()

# Get the path of the currently selected prim(s)
selection = usd_context.get_selection()
prim_paths = selection.get_selected_prim_paths()

if prim_paths:
    # First, ensure we have a boolean primvar to toggle
    set_primvar = omni.kit.property.geometry.PrimVarCommand(
        prim_path=prim_paths,
        prim_name="visibility",
        prim_type="Sdf.ValueTypeNames.Bool",
        value=True
    )
    omni.kit.commands.execute(set_primvar)
    
    # Now toggle the boolean primvar (will become False)
    toggle_command = omni.kit.property.geometry.TogglePrimVarCommand(
        prim_path=prim_paths,
        prim_name="visibility"
    )
    omni.kit.commands.execute(toggle_command)
    
    # Toggle again (will become True)
    omni.kit.commands.execute(toggle_command)
```
---

## Toggle Instanceability on Selected Prims

```python
import omni.kit.commands
import omni.kit.property.geometry
import omni.usd

# Get the current USD context
usd_context = omni.usd.get_context()

# Get the path of the currently selected prim(s)
selection = usd_context.get_selection()
prim_paths = selection.get_selected_prim_paths()

if prim_paths:
    # Create and execute the command to toggle instanceability
    instanceable_command = omni.kit.property.geometry.ToggleInstanceableCommand(
        prim_path=prim_paths
    )
    omni.kit.commands.execute(instanceable_command)
    
    # Check if the prims are now instanceable
    stage = usd_context.get_stage()
    for path in prim_paths:
        prim = stage.GetPrimAtPath(path)
        if prim:
            print(f"Prim {path} instanceable: {prim.IsInstanceable()}")
```
---

## Access GeometryPropertyExtension Instance

```python
import omni.kit.property.geometry

# Get the current instance of the GeometryPropertyExtension
ext_instance = omni.kit.property.geometry.get_instance()

# Check if the extension is available
if ext_instance:
    # Register a custom visual attribute
    ext_instance.register_custom_visual_attribute(
        attribute_name="customAttr",
        display_name="My Custom Attribute",
        type_name="Sdf.ValueTypeNames.Bool",
        default_value=False,
        predicate=lambda x: True  # Always show this attribute
    )
    
    print("Custom attribute 'customAttr' registered")
    
    # Later, we can deregister it
    ext_instance.deregister_custom_visual_attribute("customAttr")
    print("Custom attribute 'customAttr' deregistered")
```
