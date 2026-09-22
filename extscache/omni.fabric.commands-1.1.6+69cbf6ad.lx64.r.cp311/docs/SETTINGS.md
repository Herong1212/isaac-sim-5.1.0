```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension

### `"omni.fabric.commands.setting.nestedGprimsAuthoring"`
- Default Value: `false`
- Description: Determines if nested geometric primitives (gprims) are allowed in the stage hierarchy.

### `"omni.fabric.commands.setting.primCreationWithDefaultXformOps"`
- Default Value: `true`
- Description: Specifies whether to create default transform operations for primitives upon creation.

## Settings Used by the Extension but Provided by Another Extension

### `"/persistent/app/stage/nestedGprimsAuthoring"`
- Used Value: `get` or `set`
- Description: Toggles the ability to author nested geometric primitives (gprims) in the stage.

### `"/persistent/app/primCreation/PrimCreationWithDefaultXformOps"`
- Used Value: `get`
- Description: Indicates whether primitives are created with default transform operations.