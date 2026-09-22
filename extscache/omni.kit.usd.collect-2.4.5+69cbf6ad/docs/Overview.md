```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

{py:mod}`omni.kit.usd.collect` provides the core API for collecting a USD file with all of its dependencies that are scattered around different locations.

```python
from omni.kit.usd.collect import Collector

...
collector = Collector(usd_path, target_folder)
success, target_root_usd = await collector.collect()
```

Here it instantiates a {py:class}`omni.kit.usd.collect.Collector` to collect USD file from `usd_path` to target location `target_folder` with default parameters. You can check {py:func}`omni.kit.usd.collect.Collector.__init__` for more customizations to instantiate a Collector.

## Differences between Flat Collection and Non-Flat Collection
Collector supports to organize a final collection in two different folder structures: flat or non-flat. By default,
collector collects all assets with non-flat structure, that collected files are organized in the same folder structure
as the source files. In flat mode, folder structure will not be kept and all dependencies will be put into specified folders.
Also, you can specify the policy about how to group textures (see {py:class}`omni.kit.usd.collect.FlatCollectionTextureOptions` for more details). Currently there are 3 available options:

| Options | Description |
| ------- | ----------- |
| Group by MDL | Textures will be grouped by their parent MDL file name. |
| Group by USD | Textures will be grouped by their parent USD file name. |
| Flat | All textures will be collected under the same hierarchy under "textures" folder. Note that there might be potential danger of textures overwriting each other, if they have the same names but belong to different assets/mdls. |

## Default Prim Only Mode
User can also specify the option to enable "Default Prim Only" mode. In this mode, collector will prune USD files according to the given policy (see the `Keyword Args` section of {py:func}`omni.kit.usd.collect.Collector.__init__`). So prim except
default prim will be removed to speed up collection. If USD file has no default prim set, it does nothing to the USD file.

REMINDER: This is an advanced mode that may remove valid data of your stage, and if you have references with explicit prim
set, and the prim is not the default prim from the reference file. It may create stale reference if you apply this mode to
all USD layers since non-default prims will be removed.

## Limitations
There is no USDZ support currently until Kit resolves MDL loading issue inside USDZ file.