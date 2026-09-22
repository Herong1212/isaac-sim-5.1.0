```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension

### `exts."omni.kit.manipulator.tool.snap".providerNames`
- **Default Value**: `{}`
- **Description**: Contains the list of provider names for snapping operations.

### `persistent.exts."omni.kit.manipulator.tool.snap".conformToTarget`
- **Default Value**: `false`
- **Description**: Determines whether snapped objects should conform to the target's orientation.

### `persistent.exts."omni.kit.manipulator.tool.snap".conformUpAxis`
- **Default Value**: `"Stage"`
- **Description**: Specifies the up axis used when conforming to the target's orientation.

### `persistent.exts."omni.kit.manipulator.tool.snap".explicitTransform.rotate`
- **Default Value**: `1.0`
- **Description**: The minimal increment value for rotate when "Explicit Transform" is enabled.

### `persistent.exts."omni.kit.manipulator.tool.snap".explicitTransform.scale`
- **Default Value**: `1.0`
- **Description**: The minimal increment value for scale when "Explicit Transform" is enabled.

### `persistent.exts."omni.kit.manipulator.tool.snap".explicitTransform.translate`
- **Default Value**: `1.0`
- **Description**: The minimal increment value for translate when "Explicit Transform" is enabled.

### `persistent.exts."omni.kit.manipulator.tool.snap".keepSpacing`
- **Default Value**: `true`
- **Description**: When multiple objects are selected, indicates if the original spacing between them should be maintained.

## Settings Used by the Extension but Provided by Another Extension

### `/app/viewport/snapEnabled`
- **Description**: Represents the state of snapping being enabled or disabled in the viewport.

### `/app/transform/operation`
- **Description**: Reflects the current transform operation active in the application (move, rotate, scale).

### `/app/viewport/grid/enabled`
- **Description**: Indicates whether the grid is enabled in the viewport, which affects the visibility of the snap to grid option.

### `/persistent/app/viewport/grid/scale`
- ***Description**: Viewport grid scale.
