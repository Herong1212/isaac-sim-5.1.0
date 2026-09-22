# Overview

`omni.kit.converter.dgn_core` converts DGN files to USD using the ODA Kernel and Drawings SDKs. This is a core extension without a GUI that provides the fundamental DGN conversion functionality. It can be used directly through its Python API, or accessed through the GUI extension `omni.kit.converter.dgn` which provides a user interface for the conversion process.

Upon loading, it registers with the CAD Converter service (`omni.services.convert.cad`) if available, allowing other extensions to utilize its conversion capabilities.

The resulting USD file from the DGN Converter prepends names of DGN levels to prims. This allows for quick search by users to find geometry belonging to desired converted levels.

## DGN CONVERTER CONFIG FILE INPUTS:

Conversion options are configured by supplying a JSON file. Below are the available configuration options.

**_NOTE:_** Some converter options have been updated with new keys to replace legacy ones (often in Hungarian notation, e.g. `bInstancing`). Legacy keys are supported for backward compatibility but will be deprecated. This documentation uses the new keys and provides information about legacy keys in the description of each option.

### JSON Converter Settings:

**Format**: Each option is specified as a JSON key-value pair, e.g. `"option_name": default_value`

#### Converter Option: Tessellation Level of Detail (LOD)

**Description**: Tessellation levels of detail presets provide values to define DGN surface tolerance when `surfaceTolerance` is not provided. When both `tessLOD` and `surfaceTolerance` are defined, then this value is overridden by `surfaceTolerance` during conversion. If an invalid value was provided, then a value of 0.20 surface tolerance is used. The legacy key for this option is `iTessLOD`.

**Default Value**: 2
Value Ranges: [0, 4]
- 0 for 1.00 surface tolerance
- 1 for 0.75 surface tolerance
- 2 for 0.50 surface tolerance
- 3 for 0.25 surface tolerance
- 4 for 0.05 surface tolerance
**Data Format**: integer

**Config File Example**:
```json
"tessLOD" : 2
```

#### Converter Option: Surface Tolerance

**Description**: Sets the maximum distance (surface tolerance) between the tessellated mesh and the source surface. The smaller the value the more precise the tessellated mesh. The legacy key for this option is `dSurfaceTolerance`.
**Default Value**: 0.2
Value Ranges: [0,1]
**Data Format**: double

**Config File Example**:
```json
"surfaceTolerance" : 0.2
```

#### Converter Option: Use Materials

**Description**: If true converter creates materials with the color set as an attribute. If false converter will convert colors to USD `displayColor` primvars. The legacy key for this option is `bUseMaterials`.

**Default Value**: true
Value Ranges: true, false
**Data Format**: bool

**Config File Example**:
```json
"useMaterials" : true
```

#### Converter Option: Material Select

**Description**: If `useMaterials` is true, sets the material type for target renderer.

**Default Value**: 1
Value Ranges: [0, 2]
- 0: No materials
- 1: USD Preview Surface; default and compatible with Universal renderers
- 2: OmniPBR + USD Preview Surface; compatible with RTX and Universal renderers
**Data Format**: Integer

**Config File Example**:

```json
"materialType" : 1
```

#### Converter Option: Generate UVs

**Description**: If true, calls Scene Optimizer Service Kit extension to generate UVs if missing in source data.

See [Scene Optimizer Service documentation](https://docs.omniverse.nvidia.com/kit/docs/omni.services.scene.optimizer/latest/overview.html) for details.

**Default Value**: true
Value Ranges: true, false
**Data Format**: bool

**Config File Example**:
```json
"bOptimize" : true
```

#### Converter Option: Instancing

**Description**: If true the USD model uses instancing by creating USD References. If false, then there is no instancing at all. The legacy key for this option is `bInstancing`.

**Default Value**: true
Value Ranges: true, false
**Data Format**: bool

**Config File Example**:
```json
"instancing" : true
```

#### Converter Option: Instancing Style

**Description**: Style of instancing to use in USD when handling Shared Cell References. Creates references to a prototype prim, allowing multiple instances to share geometry and materials. This reduces memory usage and improves performance compared to duplicating geometry. See [Scenegraph Instancing](https://docs.omniverse.nvidia.com/dang/latest/guide/usd/instancing.html#scenegraph-instancing) documentation for more details.

**Default Value**: 1
Value Ranges: [0, 1]
  0: No instancing
  1: Scenegraph Instancing is enabled
**Data Format**: integer

**Config File Example**:
```json
"instancingStyle" : 1
```

#### Converter Option: Convert Hidden

**Description**: If true, export hidden DGN elements but set their converted USD prims visibility to "invisible". Otherwise, skip hidden elements. The legacy key for this option is `bConvertHidden`.

**Default Value**: true
Value Ranges: true, false
**Data Format**: bool

**Config File Example**:
```json
"convertHidden" : true
```

#### Converter Option: Convert Curves

**Description**: If true, convert DGN curve elements (Lines, Linestrings, Arcs, Ellipses, etc.) into USD Basis Curves; else, ignore these elements. The legacy key for this option is `bConvertCurves`.

**Default Value**: false
Value Ranges: true, false
**Data Format**: bool

**Config File Example**:
```json
"convertCurves" : true
```

#### Converter Option: Apply Global Origin

**Description**: This flag controls whether the global origin of Models are applied as transforms. If false the value is stored as an attribute but the Model has no transform applied.

**Default Value**: false
Value Ranges: true, false
**Data Format**: bool

```json
"applyGlobalOrigin" : false
```

#### Converter Option: Hide Levels by List

**Description**: If true, set converted USD prims' visibilities to invisible if their respective DGN elements belonged to the list of hidden levels (see option hiddenLevels); otherwise, do not set their visiblities to invisible. The legacy key for this option is `bHideLevelsByList`.

**Default Value**: true
Value Ranges: true, false
**Data Format**: bool

**Config File Example**:
```json
"hideLevelsByList" : true
```

#### Converter Option: Hidden Levels List

**Description**: String array of level patterns for resolving DGN levels to hide after conversion; level names can include wildcard characters (\"\*\") to complete the rest of the level name during conversion wildcard characters can be placed at the beginning (\"\*ault\"), ending (\"Def\*\"), or both (\"\*fau\*\"). If the user provides patterns that do not match any levels in the DGN file, then no converted USD prims will be hidden based on their level. If the user provides \"\*\", then all levels will be hidden. Searches are case sensitive (i.e., if a level is named "Default" but a pattern "default" is provided, then there is no match.).

**Default Value**: [] (empty array)
Value Ranges: empty or populated array of strings
**Data Format**: array of strings

**Config File Example**:
```json
"hiddenLevels": ["default", "hiddenLevel1", "hiddenLevel_2"]
```

#### Converter Option: Convert Levels

**Description**: If true, only convert DGN elements belonging to the levels matching the entries under levelNamePatterns; else, ignore DGN elements belonging to the matching levels.

**Default Value**: true
Value Ranges: true, false
**Data Format**: bool

**Config File Example**:
```json
"bConvertLevels" : true
```

#### Converter Option: Level Name Patterns

**Description**: String array of level names patterns for resolving DGN levels to convert; level names can include wildcard characters (\"\*\") to complete the rest of the level name during conversion wildcard characters can be placed at the beginning (\"\*ault\"), ending (\"Def\*\"), or both (\"\*fau\*\"). If the user provides patterns that do not match any levels in the DGN file, then the file is not converted. If the user provides \"\*\", then all levels will be converted. Searches are case sensitive (i.e., if a level is named "Default" but a pattern "default" is provided, then there is no match.).

**Default Value**: [] (empty array)
Value Ranges: empty or populated array of strings
**Data Format**: array of strings

**Config File Example**:
```json
"levelNamePatterns" : [
  "Default",
  "*vertedLevel",
  "ConvertedLev*",
  "*vertedLev*",
  "ConvertedLevel_X"
]
```

**_NOTE:_** **Level Filter Style**, **Level Includes**, and **Level Excludes** options are meant to replace `bConvertLevels` and `levelNamePatterns`. **You must switch to these Converter Options to handle filtered levels.**

#### Converter Option: Level Filter Style

**Description**: Styles to used to handle filtered levels.

**Default value**: 0
Value Ranges: [0, 3]
  0: eNone - Apply no filtering
  1: eOmit - Do not convert the filtered element or its descendants
  2: eDeactivate - Convert all elements and deactivate the ones that were filtered
  3: eHide - Convert all elements and hide the ones that were filtered
**Data Format**: integer

**Config File Example**:
```json
"levelFilterStyle" : 0
```

#### Converter Option: Level Includes

**Description**: List of level names to include during filtering. Level names can include wildcard characters (\"\*\") to complete the rest of the level name during conversion wildcard characters can be placed at the beginning (\"\*ault\"), ending (\"Def\*\"), or both (\"\*fau\*\"). If the user provides patterns that do not match any levels in the DGN file, then the file is not converted. If the user provides \"\*\", then all levels will be converted. Searches are case sensitive (i.e., if a level is named "Default" but a pattern "default" is provided, then there is no match.).

**Default Value**: [] (empty array)
Value Ranges: empty or populated array of strings
**Data Format**: array of strings

**Config File Example**:
```json
"levelIncludes" : [
  "Default",
  "3D*"
]
```

#### Converter Option: Level Excludes

**Description**: List of level names to exclude during filtering. Level names can include wildcard characters (\"\*\") to complete the rest of the level name during conversion wildcard characters can be placed at the beginning (\"\*ault\"), ending (\"Def\*\"), or both (\"\*fau\*\"). If the user provides patterns that do not match any levels in the DGN file, then the file is not converted. If the user provides \"\*\", then all levels will be converted. Searches are case sensitive (i.e., if a level is named "Default" but a pattern "default" is provided, then there is no match.)

**Default Value**: [] (empty array)
Value Ranges: empty or populated array of strings
**Data Format**: array of strings

**Config File Example**:
```json
"levelExcludes" : [
  "Default",
  "3D*"
]
```


#### Converter Option: Merge Meshes

**Description**: If true, meshes that share the same level, color, and element type are merged for optimization; else, mesh merging is skipped. The legacy key for this option is `bMergeMeshes`.

**Default Value**: true
Value Ranges: true, false
**Data Format**: bool

**Config File Example**:
```json
"mergeMeshes" : true
```

#### Converter Option: Converted Levels

**Description**: String array of level names patterns for resolving DGN levels to convert; level names can include wildcard characters (\"\*\") to complete the rest of the level name during conversion wildcard characters can be placed at the beginning (\"\*ault\"), ending (\"Def\*\"), or both (\"\*fau\*\"). If the user provides patterns that do not match any levels in the DGN file, then the file is not converted. If the user provides \"\*\", then all levels will be converted. Searches are case sensitive (i.e., if a model is named "Default" but a pattern "default" is provided, then there is no match.).

**Default Value**: [] (empty array)
Value Ranges: empty or populated array of strings
**Data Format**: array of strings

**Config File Example**:
```json
  "modelNamePatterns": ["model1", "model2", "model3", "model_X"]
```

#### Converter Option: Import Attributes by List

**Description**: Flag to export DGN custom properties and convert to DGN attributes. the "prefix" key is used to create a namespace for the USD attribute (e.g., for organization, avoiding attribute name overlaps) resulting in the naming convention of "{prefix}:{converted_name}"; if "prefix" is not provided, then the default value is "omni:connect:dgn:{property_class}:{converted_name}". The legacy key for this option is `bImportAttributesByList`.

**Default Value**: true
Value Ranges: true, false
**Data Format**: bool

**Config File Example**:
```json
"importAttributesByList" : true
```

#### Converter Option: Attributes

**Description**: Array of attribute objects that contain the name of the custom DGN property (`name`), the prefix of (`prefix`) and the desired name (`converted_name`) for the converted USD attributed. The value of `name` is used to find matching DGN properties and convert them into USD attributes for converted elements. The name of the USD attribute is a concatenation of `prefix` and `converted_name`, separated by a colon (':'). The value of `prefix` can be a user-defined value (e.g., `"myPrefix:myAttribute1_foobar"`), an empty string resulting in an un-namespaced attribute (e.g., `"myAttribute2_foobar"`), or no prefix at all resulting in the use of the DGN Converter's default prefix which is `"omni:connect:dgn:{DGN property class name}"` (e.g., `"omni:connect:dgn:dgn_class:myAttribute3_foobar"`).

**Default Value**: [] (empty array)
Value Ranges: empty or populated array of JSON objects containing strings
**Data Format**: array of JSON objects containing strings

#### Converter Option: Merged Attributes

**Description**: The style in which the values of attributes that differ between merged elements are stored.

**Default Value**: 2

Value Ranges: [0, 2]
  0 : eNone - Discard the attributes
  1 : ePrimvar - Store them as a face varying primvar (not implemented)
  2 : eSubset - Store them on metadata subset Prims

**Data Format**:

**Config File Example**:
```json
  "attributes": [
    {
      "name": "myAttribute1",
      "prefix": "myPrefix",
      "converted_name": "myAttribute1_foobar"
    },
    {
      "name": "myAttribute2",
      "prefix": "",
      "converted_name": "myAttribute2_foobar"
    },
    {
      "name": "myAttribute3",
      "converted_name": "myAttribute3_foobar"
    }
  ],
```

#### Converter Option: Progress Logging

**Description**: If true, then conversion progress will be reported. The legacy key for this option is `bProgressLogging`.

**Default Value**: false
Value Ranges: true, false
**Data Format**: bool

**Config File Example**:
```json
"progressLogging" : false
```

#### Converter Option: Override Up-Axis

**Description**: Override the up-axis of the converted USD's stage to Y-up, Z-up, or default to the converter's up-axis setting.

**Default Value**: 0
Value Ranges: [0, 2]
- 0 to default to converter's up-axis
- 1 to override to Y-up
- 2 to override to Z-up
**Data Format**: integer

**Config File Example**:
```json
"iUpAxis" : 0
```

#### Converter Option: Meters Per Unit

**Description**: Set the meters per unit converted USD's stage metric. If set to 0.0, the converted USD will retain the meters per unit from conversion.

**Default Value**: 1.0
Value Ranges: Positive numbers
**Data Format**: double

**Config File Example**:
```json
"dMetersPerUnit" : 1.0
```

#### Converter Option: Scene Optimizer Config

**Description**: (Experimental feature) Provide a path to a saved Scene Optimizer JSON configuration file or a JSON formatted string for executing a predefined optimization process stack.

See [Scene Optimizer Service documentation](https://docs.omniverse.nvidia.com/kit/docs/omni.services.scene.optimizer/latest/overview.html) for details.

**Default Value**: ""
**Data Format**: string

**Config File Example**:
```json
"sOptimizeConfig" : "converter_config_example.json"
```

### Complete Example `converter_config_example.json`:

```json
{
    "applyGlobalOrigin": false,
    "attributes": [
        {
            "name": "foo1",
            "prefix": "prefix",
            "converted_name": "foobar1"
        },
        {
            "name": "foo2",
            "prefix": "",
            "converted_name": "foobar2"
        },
        {
            "name": "foo3",
            "converted_name": "foobar3"
        }
    ],
    "convertCurves": false,
    "convertHidden": false,
    "hiddenLevels": [
        "level_foo",
        "*vel_foo",
        "level_bar*",
        "*vel_bar*"
    ],
    "hideLevelsByList": true,
    "importAttributesByList": true,
    "instancing": true,
    "instancingStyle": 1,
    "levelExcludes": [],
    "levelFilterStyle": 0,
    "levelIncludes": [
        "Default",
        "level_foo",
        "*vel_foo",
        "level_ba*",
        "*vel_ba*"
    ],
    "materialType": 1,
    "mergeMeshes": true,
    "mergedAttributeStyle": 2,
    "modelNamePatterns": [
        "Default",
        "model_foo",
        "*del_foo",
        "model_ba*",
        "*del_ba*"
    ],
    "progressLogging": true,
    "surfaceTolerance": 0.2,
    "tessLOD": 2,
    "useMaterials": true,
    "sOptimizeConfig": "",
    "bOptimize": true,
    "iUpAxis": 0,
    "dMetersPerUnit": 0.0
}
```
