# Python Extension for MDL <--> USD conversions [omni.mdl.usd_converter]

This is an extension for MDL to USD and for USD to MDL conversions.

## Interfaces

### mdl_to_usd(moduleName: str, searchPath: str = None, targetFolder: str = MDL_AUTOGEN_PATH, targetFilename: str = None, output: mdl_usd.OutputType = mdl_usd.OutputType.SHADER, nestedShaders: bool = False)

- moduleName: Module to convert (example: `nvidia/core_definitions.mdl`)
- searchPath: MDL search path to be able to load MDL modules referenced by usdPrim (default = not set)
- targetFolder: Destination folder for USD stage (default = `${data}/shadergraphs/mdl_usd`)
- targetFilename: Destination stage filename, extension `.usd` or `.usda` can be omitted (default is module name, example: `core_definitions.usda`)
- output: What to output:
a shader: omni.mdl.usd_converter.mdl_usd.OutputType.SHADER
a material: omni.mdl.usd_converter.mdl_usd.OutputType.MATERIAL
material and geometry: omni.mdl.usd_converter.mdl_usd.OutputType.MATERIAL_AND_GEOMETRY
- nestedShaders: Do we want nested shaders or flat (default = False)

### usd_to_mdl(path: str, prim: mdl_usd.Usd.Prim, forceNotOV: bool = False)

- path: Output filename to save the new module to (need to end with .mdl, example: "c:/temp/new_module.mdl")
- prim: The Usd.Prim to convert
- forceNotOV: If set to True do not use the OV NeurayLib for conversion. Use specific code. (default = False)

## Examples

### MDL -> USD conversion

```
omni.mdl.usd_converter.mdl_to_usd("nvidia/core_definitions.mdl")
```

Convert core_definitions module to USD. Save the result of the conversion in the folder `${data}/shadergraphs/mdl_usd`.

```
omni.mdl.usd_converter.mdl_to_usd(
	moduleName = "nvidia/core_definitions.mdl",
	targetFolder = "C:/ProgramData/NVIDIA Corporation/mdl")
```

Convert core_definitions module to USD. Save the result of the conversion in the folder `C:/ProgramData/NVIDIA Corporation/mdl`.

```
omni.mdl.usd_converter.mdl_to_usd(
	moduleName = "nvidia/core_definitions.mdl",
	targetFolder = "C:/ProgramData/NVIDIA Corporation/mdl",
	targetFilename = "stage.usda")
```

Convert core_definitions module to USD. Save the result of the conversion in the folder `C:/ProgramData/NVIDIA Corporation/mdl` under the name `stage.usda`.
