# Project Collector [omni.kit.usd.collect]

This extension provides functionality to collect a USD project by resolving, re-pathing and gathering all dependencies, so project can be movable and sharable conveniently.

## Collector Options Explained
`USD Only`: If this option is enabled, it will only collect USD files and other other dependencies are ignored (like material files and textures.)

`Material Only`: If this options is enabled, it will only collect all material related dependencies including textures, and USD files will be ignored.

`Flat Collection`: By default, it will collect USD project by keeping the directory structure. If this option is enabled, the directory structure will not be kept and all dependencies will be put into specified folders.

`Flat Collection Texture Options`: When collecting in Flat mode, users can specify the grouping for texture files via this option; Currently there are 3 available options:
| Options | Description |
| ------- | ----------- |
| Group by MDL | Textures will be grouped by their parent MDL file name. |
| Group by USD | Textures will be grouped by their parent USD file name. | 
| Flat | All textures will be collected under the same hierarchy under "textures" folder. Note that there might be potential danger of textures overwriting each other, if they have the same names but belong to different assets/mdls. |

## Limitations
There is no USDZ support currently until Kit resolves MDL loading issue inside USDZ file. 