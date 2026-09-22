# Overview

`omni.kit.converter.hoops_core` converts CAD files to USD using the HOOPS Exchange SDK. This is a core extension without a GUI that provides the fundamental CAD conversion functionality. It can be used directly through its Python API, or accessed through the GUI extension `omni.kit.converter.hoops` which provides a user interface for the conversion process.

Upon loading, it registers with the CAD Converter service (`omni.services.convert.cad`) if available, allowing other extensions to utilize its conversion capabilities.

## CAD CONVERTER CONFIG FILE INPUTS:

### JSON Converter Settings:

**_NOTE:_** Some converter options have been updated with new keys to replace legacy ones (often in Hungarian notation, e.g. `bInstancing`). Legacy keys are supported for backward compatibility but will be deprecated. This documentation uses the new keys and provides information about legacy keys in the description of each option.

**Format**: "setting name" : default value

#### Converter Option: Instancing

Description: If true the USD model uses instancing by creating USD References. If false, then there is no instancing at all. The legacy key for this option is `bInstancing`.

Default Value: true
Value Ranges: true, false
Data Format: bool

Config File Example:
```json
"instancing" : true
```

#### Converter Option: Convert Hidden

Description: If true, export hidden elements but set their converted USD prims visibility to "invisible". Otherwise, skip hidden elements. The legacy key for this option is `bConvertHidden`.

Default Value: true
Value Ranges: true, false
Data Format: bool

Config File Example:
```json
"convertHidden" : true
```

#### Converter Option: Global Xforms

Description: When bInstancing is set to false, this flag controls whether globalXforms are composited. If false local transforms are applied. The legacy key for this option is `bGlobalXforms`.

Default Value: false
Value Ranges: true, false
Data Format: bool

```json
"globalXforms" : false
```

#### Converter Option: Tessellation Level of Detail (LOD)

Description: Tessellation levels of detail presets provide values to define ChordHeightRatio and AngleToleranceDeg; 0 is the lowest level (ExtraLow) while 4 is the highest level (ExtraHigh). The legacy key for this option is `iTessLOD`.

Default Value: 2
Value Ranges: [0, 4]
- 0: `tessLOD0` = ExtraLow, ChordHeightRatio=50, AngleToleranceDeg=40,
- 1: `tessLOD1` = Low, ChordHeightRatio=600, AngleToleranceDeg=40,
- 2: `tessLOD2` = Medium, ChordHeightRatio=2000, AngleToleranceDeg=40,
- 3: `tessLOD3` = High, ChordHeightRatio=5000, AngleToleranceDeg=30,
- 4: `tessLOD4` = ExtraHigh, ChordHeightRatio=10000, AngleToleranceDeg=20.
Data Format: integer

```json
"tessLOD" : 2
```

#### Converter Option: Accurate Surface Curvatures

Description: If true, respect surface curvature to control triangles elongation directions. The legacy key for this option is `bAccurateSurfaceCurvatures`.

Default Value: true
Value Ranges: true, false
Data Format: bool

```json
"accurateSurfaceCurvatures" : true
```

#### Converter Option: Accurate Tessellation

Description: If false, tessellate for visualization. If true, tessellate for analysis.

Default Value: false
Value Ranges: true, false
Data Format: bool

```json
"accurateTessellation": false
```


#### Converter Option: Generate UVs

Description: If true, calls Scene Optimizer Service Kit extension to generate UVs if missing in source data.

See [Scene Optimizer Service documentation](https://docs.omniverse.nvidia.com/kit/docs/omni.services.scene.optimizer/latest/overview.html) for details.

Default Value: true
Value Ranges: true, false
Data Format: bool

Config File Example:
```json
"bOptimize" : true
```

#### Converter Option: Dedup Mesh Vertices

Description: If true, weld mesh elements in appropriate groups. The legacy key for this option is `bDedup`.

Default Value: true
Value Ranges: true, false
Data Format: bool

Config File Example:
```json
"dedup" : true
```

#### Converter Option: Use Materials

Description: If true converter creates materials with the color set as an attribute. If false converter will convert colors to USD `displayColor` primvars. The legacy key for this option is `bUseMaterials`.

Default Value: true
Value Ranges: true, false
Data Format: bool

Config File Example:
```json
"useMaterials" : true
```

#### Converter Option: Material Select

Description: If `useMaterials` is true, sets the material type for target renderer.

Default Value: 1
Value Ranges: [0, 2]
- 0: No materials
- 1: USD Preview Surface; default and compatible with Universal renderers
- 2: OmniPBR + USD Preview Surface; compatible with RTX and Universal renderers
Data Format: Integer

Config File Example:

```json
"materialType" : 1
```

#### Converter Option: Use Normals

Description: If true then we pass normals to USD. if false, then we do not. The legacy key for this option is `bUseNormals`.

Default Value: true
Value Ranges: true, false
Data Format: bool

Config File Example:
```json
"useNormals" : true
```

#### Converter Option: Report Progress

Description: If true then we report import/export progress. The legacy key for this option is `bReportProgress`.

Default Value: true
Value Ranges: true, false
Data Format: bool

Config File Example:
```json
"reportProgress" : true
```

#### Converter Option: Report Progress Frequency

Description: When progress reporting is enabled, this option controls how frequently (in Hz) progress updates are reported during conversion.

Default Value: 4.0
Value Ranges: [1.0, 10.0]
Data Format: double

```json
"reportProgressFreq": 4.0
```

#### Converter Option: Convert Curves

Description: If true, convert curve elements into USD Basis Curves; else, ignore these elements. The legacy key for this option is `bConvertCurves`.

Default Value: false
Value Ranges: true, false
Data Format: bool

```json
"convertCurves" : false
```

#### Converter Option: Convert Metadata

Description: If true then metadata, including PMI, are imported as USD Attributes; else, metadata are ignored. The legacy key for this option is `bConvertMetadata`.

Default Value: false
Value Ranges: true, false
Data Format: bool

```json
"convertMetadata" : false
```

#### Converter Option: Override Up-Axis

Description: Override the up-axis of the converted USD's stage to Y-up, Z-up, or default to the converter's up-axis setting.

Default Value: 0
Value Ranges: [0, 2]
- 0 to default to converter's up-axis
- 1 to override to Y-up
- 2 to override to Z-up
Data Format: integer

Config File Example:
```json
"iUpAxis" : 0
```

#### Converter Option: Meters Per Unit

Description: Set the meters per unit converted USD's stage metric. If set to 0.0, the converted USD will retain the meters per unit from conversion.

Default Value: 1.0
Value Ranges: Positive numbers
Data Format: double

Config File Example:
```json
"dMetersPerUnit" : 1.0
```

#### Converter Option: Scene Optimizer Config

Description: (Experimental feature) Provide a path to a saved Scene Optimizer JSON configuration file or a JSON formatted string for executing a predefined optimization process stack.

See [Scene Optimizer Service documentation](https://docs.omniverse.nvidia.com/kit/docs/omni.services.scene.optimizer/latest/overview.html) for details.

Default Value: ""
Data Format: string

Config File Example:
```json
"sOptimizeConfig" : "converter_config_example.json"
```

### Full `converter_config_example.json`:

```json
{
    "accurateSurfaceCurvatures": true,
    "accurateTessellation": false,
    "convertCurves": false,
    "convertHidden": false,
    "convertMetadata": false,
    "dedup": true,
    "globalXforms": false,
    "instancing": true,
    "materialType": 1,
    "reportProgress": true,
    "reportProgressFreq": 4,
    "tessLOD": 2,
    "useMaterials": true,
    "useNormals": true,
    "sOptimizeConfig": "",
    "bOptimize": true,
    "iUpAxis": 0,
    "dMetersPerUnit": 0.0
}
```

## Known Issues

- Please refer to [Known Issues](Known_Issues.md#known-issues) for more information.

## Licensing Terms of Use and Third-Party Notices
The `omni.kit.converter.hoops_core` and related CAD converter Extensions are Omniverse Core Extensions.
Do not redistribute or sublicense without express permission or agreement.
Please read the [Omniverse License Agreements](https://docs.omniverse.nvidia.com/extensions/latest/common/NVIDIA_Omniverse_License_Agreement.html) and the [Third_Party_Notices.md](Third_Party_Notices.md) for detailed license information.