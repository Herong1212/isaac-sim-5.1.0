```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension
### ext."omni.kit.property.usd".enableAdapter
   - **Default Value**: False
   - **Description**: Enables the use of property adapters from omni.kit.property.adapter.* extensions for custom UI widgets. This allows property widget to support different datastores other than USD. If set to false, only USD will be supported.

### exts."omni.kit.property.usd".show_prefs
   - **Default Value**: True
   - **Description**: Controls whether preferences for USD properties are shown in the application settings.

### exts."omni.kit.property.usd".allow_rename_prims
   - **Default Value**: True
   - **Description**: Allows renaming of USD prims from the property interface.

### persistent.exts."omni.kit.property.usd".references_hide_max
   - **Default Value**: 5
   - **Description**: The maximum number of references to display before collapsing the references view.

### persistent.exts."omni.kit.property.usd".references_check_missing
   - **Default Value**: True
   - **Description**: Checks for missing references in USD properties.

### persistent.exts."omni.kit.property.usd".update_on_press_enter
   - **Default Value**: True
   - **Description**: Updates property fields only when the Enter key is pressed.

### persistent.exts."omni.kit.property.usd".raw_widget_multi_selection_limit
   - **Default Value**: 1
   - **Description**: The limit for multi-selection in raw USD property widgets.

### persistent.exts."omni.kit.property.usd".large_selection
   - **Default Value**: 100
   - **Description**: Defines what count is considered a large selection for USD properties.

## omni.kit.property.usd version 4.3.0 and above

### exts."omni.kit.property.usd".showSchemaAPI
   - **Default Value**: True
   - **Description**: show schema API in property window

### exts."omni.kit.property.usd".removeSchemaAPI
   - **Default Value**: True
   - **Description**: Allow removing of schema API's from property window
   - **Note**: If this is False the schema API's will still be shown but are not removable
   - **Note**: exts."omni.kit.property.usd".showSchemaAPI must be True

