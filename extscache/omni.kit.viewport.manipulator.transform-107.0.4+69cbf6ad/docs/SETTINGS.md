```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension

### persistent.exts."omni.kit.viewport.manipulator.transform".manipulator.intersectionThickness
   - **Default Value**: 10
   - **Description**: Defines the thickness of the intersection area for manipulators in the viewport.

### persistent.exts."omni.kit.viewport.manipulator.transform".manipulator.scaleMultiplier
   - **Default Value**: 1.4
   - **Description**: Sets the multiplier for scaling operations in the viewport manipulator.

### persistent.exts."omni.kit.viewport.manipulator.transform".manipulator.freeRotationEnabled
   - **Default Value**: True
   - **Description**: Enables or disables free rotation for the viewport manipulator.

### persistent.exts."omni.kit.viewport.manipulator.transform".manipulator.freeRotationType
   - **Default Value**: Clamped
   - **Description**: Specifies the type of free rotation for the viewport manipulator, such as 'Clamped'.

## Settings Used by the Extension but Provided by Another Extension

### /app/viewport/{self._stage_id}/manipulating
   - **Description**: Used to signal that user manipulation has started for the given stage in the viewport.

### TRANSFORM_GIZMO_TRANSLATE_DELTA_XYZ
   - **Description**: Stores the delta values for translation operations performed by the transform gizmo.

### TRANSFORM_GIZMO_ROTATE_DELTA_XYZW
   - **Description**: Stores the delta values for rotation operations performed by the transform gizmo.

### TRANSFORM_GIZMO_SCALE_DELTA_XYZ
   - **Description**: Stores the delta values for scaling operations performed by the transform gizmo.