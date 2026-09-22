# Commands
Public command API for module **omni.kit.property.geometry**:

- [PrimVarCommand](#primvarcommand)
- [ToggleInstanceableCommand](#toggleinstanceablecommand)
- [TogglePrimVarCommand](#toggleprimvarcommand)


## PrimVarCommand
Set primvar undoable **Command**.

### Arguments
- prim_path(list): List of paths of prims.
- prim_name(str): Primvar name.
- prim_type
- value(any): New primvar value. If primvar doesn't exist, it will be created
- usd_context_name

### Usage

```python
import omni.usd
import omni.kit.commands
from pxr import Sdf, UsdGeom

# Get the current USD stage from the default USD context.
stage = omni.usd.get_context().get_stage()

# Define the list of prim paths that will be updated.
prim_paths = ["/World/Prim1", "/World/Prim2"]

# Define the primvar name, type and the new value.
primvar_name = "displayColor"
primvar_type = Sdf.ValueTypeNames.Color3f  # For a Color3f primvar
new_value = (1.0, 0.0, 0.0)  # Set the color to red

# Execute the PrimVarCommand to update or create the primvar on the specified prims.
omni.kit.commands.execute(
    "PrimVarCommand",
    prim_path=prim_paths,
    prim_name=primvar_name,
    prim_type=primvar_type,
    value=new_value,
)
```

## ToggleInstanceableCommand
Toggle instanceable undoable **Command**.

### Arguments
- prim_path(list): List of paths of prims.
- usd_context_name

### Usage

```python
import omni.usd
import omni.kit.commands

# Prepare the list of prim paths to toggle instanceable property
prim_paths = ["/World/PrimA", "/World/PrimB"]

# Execute the ToggleInstanceableCommand to toggle the instanceable state of each prim
omni.kit.commands.execute("ToggleInstanceableCommand", prim_path=prim_paths)
```

## TogglePrimVarCommand
Toggle primvar undoable **Command**.

### Arguments
- prim_path(list): List of paths of prims.
- prim_name(str): Primvar name.
- usd_context_name

### Usage

```python
import omni.usd
import omni.kit.commands

# Define the list of prim paths where the boolean primvar will be toggled.
prim_paths = ["/World/Prim1", "/World/Prim2"]

# Specify the name of the primvar to toggle.
primvar_name = "myBoolPrimVar"

# Execute the TogglePrimVarCommand to toggle the boolean primvar on the given prim paths.
omni.kit.commands.execute("TogglePrimVarCommand", prim_path=prim_paths, prim_name=primvar_name)
```

