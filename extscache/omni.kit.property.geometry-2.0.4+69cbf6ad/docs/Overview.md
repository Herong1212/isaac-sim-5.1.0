```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

**omni.kit.property.geometry** is an extension designed to provide interactive controls for viewing and editing geometry property values directly within a USD stage. It offers undoable commands to update prim attributes and toggle key properties such as primvars and instanceable states, streamlining the process of modifying geometry properties. The extension also integrates with property widgets and menu entries to give users easy access to visual attribute adjustments.

```{image} ../../../../source/extensions/omni.kit.property.geometry/data/preview.png
---
align: center
---
```


## Concepts

- **Primvars and Attributes:** The extension focuses on managing prim attribute values (primvars) by allowing users to set or toggle them via dedicated commands.
- **Undoable Commands:** Commands like [PrimVarCommand](omni.kit.property.geometry/omni.kit.property.geometry.PrimVarCommand), [TogglePrimVarCommand](omni.kit.property.geometry/omni.kit.property.geometry.TogglePrimVarCommand), and [ToggleInstanceableCommand](omni.kit.property.geometry/omni.kit.property.geometry.ToggleInstanceableCommand) encapsulate property changes such that every operation supports undo/redo functionality.
- **Extension Instance:** The [get_instance](omni.kit.property.geometry/omni.kit.property.geometry.get_instance) API provides a mechanism to retrieve the current extension instance, ensuring a single point of control for geometry property operations.

## Functionality

- **Command-based Updates:** The provided commands update property values on selected prims. For instance, [PrimVarCommand](omni.kit.property.geometry/omni.kit.property.geometry.PrimVarCommand) sets a new value (or creates a primvar if missing) while preserving original states for undo functionality.
- **Toggle Operations:** [TogglePrimVarCommand](omni.kit.property.geometry/omni.kit.property.geometry.TogglePrimVarCommand) and [ToggleInstanceableCommand](omni.kit.property.geometry/omni.kit.property.geometry.ToggleInstanceableCommand) allow users to switch boolean properties and instanceable flags with a simple command interface.
- **Custom Visual Attributes:** The extension supports registering and deregistering custom visual attributes that adapt the display and management of geometry properties, enhancing interactivity within the property widget.

## Usage Examples

A typical use case involves retrieving the extension instance and executing a command to modify prims:

```python
from omni.kit.property.geometry import get_instance, PrimVarCommand

# Retrieve the current extension instance
extension_instance = get_instance()
if extension_instance is not None:
    # Example: update a primvar for a list of prims
    prims = ["/World/Prim1", "/World/Prim2"]
    command = PrimVarCommand(prim_path=prims, prim_name="displayColor", prim_type="Sdf.ValueTypeNames.Color3f", value=(1.0, 0.5, 0.0))
    command.do()
```

## Relationships

- **Dependencies:** This extension relies on other key modules including **omni.usd** for stage interactions, **omni.ui** for UI elements, **omni.kit.window.property** for property widget integration, and **omni.kit.property.usd** for USD-based property handling.
- **Integration:** It seamlessly interfaces with other Omniverse Kit SDK components to ensure that changes made via the commands are reflected within the broader USD workflow and visual properties management.

## Considerations

- The commands assume that prim selections and property types are correctly validated before execution. Users should ensure that the provided prim paths and attribute types match the expected format.
- Custom visual attribute functions allow dynamic updates, but care should be taken to maintain consistency between the displayed values and the underlying USD stage state.
- The extension is designed for interactive property management; therefore, it integrates closely with the UI and command systems to provide real-time feedback and undo capabilities.