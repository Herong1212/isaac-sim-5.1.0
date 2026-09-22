```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.widget.stage_icons` extension adds icons for some primitive types in the stage window.

## Important API List
The module consists of the following main components:
- **get_registered_icons**: This static method retrieves a list of currently registered icons for primitives.
- **register_icons**: Registers icons from SVG files found in the icons directory.
- **on_startup**: Initializes the icon registration process when the extension starts.
- **on_shutdown**: Deregisters all icons when the extension is shut down.

## User Guide
- [](CHANGELOG)
