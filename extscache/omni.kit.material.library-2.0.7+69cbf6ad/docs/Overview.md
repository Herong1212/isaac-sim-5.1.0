```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

omni.kit.material.library is library of python functions for materials. Provides simple interface with hydra and neuraylib low level extensions, for creating materials as prims, binding materials to "bindable" prims, material UI, material "Create" menus, material preferences and much more.

## Examples.

### Create a material.

```{code-block} python
import omni.kit.material.library

# Create a Shader
omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
                            mdl_name='OmniPBR.mdl',
                            mtl_name='OmniPBR'
)
```

### Create a material and bind to /World/Plane, method 1.

```{code-block} python
import omni.kit.material.library
from pxr import Usd

prim_path = "/World/Plane"
prim_name ="testplane"

# Create a Plane Prim
omni.kit.commands.execute('CreatePrimWithDefaultXform', prim_type='Plane', prim_path=prim_path )

# Select the Plane
omni.kit.commands.execute('SelectPrims', old_selected_paths=[''], new_selected_paths=[prim_path], expand_in_stage=True)

# Create a Shader
omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
                            mdl_name='OmniPBR.mdl',
                            mtl_name='OmniPBR',
                            prim_name=prim_name,
                            mtl_created_list=None,
                            bind_selected_prims=True                            
)
```

### Create a material and bind to /World/Plane, method 2

```{code-block} python
import omni.kit.material.library
from pxr import Usd, UsdShade

prim_path = "/World/Plane"
prim_name ="testplane"

# Create a Plane Prim
omni.kit.commands.execute('CreatePrimWithDefaultXform', prim_type='Plane', prim_path=prim_path )

# Select the Plane
omni.kit.commands.execute('SelectPrims', old_selected_paths=[''], new_selected_paths=[prim_path], expand_in_stage=True)

# Create a Shader
mtl_created_list = []
omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
                            mdl_name='OmniPBR.mdl',
                            mtl_name='OmniPBR',
                            mtl_created_list=mtl_created_list
)

# Bind material to prim
omni.kit.commands.execute("BindMaterial",
                          prim_path=[prim_path],
                          material_path=mtl_created_list[0],
                          strength=UsdShade.Tokens.weakerThanDescendants
)
```

### Create a material and modify created material.
- This can be a problem as just creating the material doesn't mean its Usd.Attribute's are immediately accessible. Created materials inputs/outputs then have to be "loaded" into Usd.Prim, so to work around this use on_created_fn callback.
- NOTE: Materials loaded via a .usd file will also not have the Usd.Attribute immediately accessible. Selecting the prim triggers `omni.usd.get_context().load_mdl_parameters_for_prim_async()` todo this.

```{code-block} python
import omni.kit.material.library
from pxr import Usd

# Created material callback
async def on_created(shader_prim: Usd.Prim):
    shader_prim.CreateAttribute("inputs:diffuse_texture").Set("./test.png")

# Create a Shader
omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
                            mdl_name='OmniPBR.mdl',
                            mtl_name='OmniPBR',
                            on_created_fn=lambda p: asyncio.ensure_future(on_created(p))
)
```

### Get SubIds from material
```{code-block} python
import asyncio
import carb
import omni.kit.material.library

async def get_subs_ids():
    mdl_path = carb.tokens.get_tokens_interface().resolve("${kit}/mdl/core/Base/OmniHairPresets.mdl")
    subid_list = await omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=mdl_path)
    print(f"subid_list:{subid_list}")

asyncio.ensure_future(get_subs_ids())
```

### Get SubIds from material using callback
```{code-block} python
import asyncio
import carb
import omni.kit.material.library

def have_subids(id_list):
    print(f"id_list:{id_list}")

mdl_path = carb.tokens.get_tokens_interface().resolve("${kit}/mdl/core/Base/OmniHairPresets.mdl")
asyncio.ensure_future(omni.kit.material.library.get_subidentifier_from_mdl(mdl_file=mdl_path, on_complete_fn=have_subids))
```
