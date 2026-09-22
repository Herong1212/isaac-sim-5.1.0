```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## "/exts/omni.kit.material.library/lib_paths"
- default is
```
[
    "${kit}/mdl/core/Base",
    "${kit}/mdl/core/Volume"
]
```
- material paths to build UI list from.
- Can be updated with omni.kit.material.library.add_to_mtl_lib / omni.kit.material.library.remove_from_mtl_lib functions.

## "/exts/omni.kit.material.library/ui_hidden_list"
- default is
```
[
    "${kit}/mdl/core/Base/OmniPBR_Opacity.mdl",
    "${kit}/mdl/core/Base/OmniPBR_ClearCoat_Opacity.mdl",
    "${kit}/mdl/core/Base/OmniGlass_Opacity.mdl",
    "${kit}/mdl/core/Base/SimPBR_Model.mdl"
]
```
- list of materials not to add to UI list.

## "/exts/omni.kit.material.library/ui_show_list"
- default is []
- when set, the UI "Create" material menus will only list materials listed. EG ["OmniPBR*", "OmniSurface*"].
- NOTE: This uses fnmatch, so wild-cards can be used.

## "/exts/omni.kit.material.library/show_ui_groups"
- default is true
- show/hide material groups in "Create" material menus.

## "/exts/omni.kit.material.library/cache_mdl"
- default true
- material cache enable/disable. Avoids loading all materials from lib_paths every launch.

## "/exts/omni.kit.material.library/cache_version"
- default "1.2"
- current cache version number, this can get incremented when cache file changes.

## "/persistent/app/stage/materialStrength"
- default "weakerThanDescendants"
- default material strength of new material binding.

## "/exts/omni.kit.material.library/original_svg_color"
- default is false.
- deprecated & doesn't do anything.
