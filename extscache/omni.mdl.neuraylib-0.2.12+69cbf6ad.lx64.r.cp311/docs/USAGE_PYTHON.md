# Python Usage Examples

## Load an MDL module

For loading modules, the wrappers in Omniverse have to be used in order to guarantee proper resource tracking.

```python
import omni.mdl.neuraylib

# acquire the neuraylib instance from OV
ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()

# address the MDL module using its USD identifier / source asset name
usd_identifier = "nvidia/support_definitions.mdl"
ov_module = ov_neuraylib.createMdlModule(usd_identifier)
if ov_module and ov_module.valid():
    print(f"dbScopeName: {ov_module.dbScopeName}")
    print(f"dbName: {ov_module.dbName}")
    # ...
    # use omni.mdl.pymdlsdk to get low-level access to the MDL module using its `dbName`
    # ...

    # release to Omniverse wrapper
    ov_neuraylib.destroyMdlModule(ov_module)
```

## Access an active material graph of the material back-end

The Neuraylib in Omniverse maps USD shader nodes to MDL function calls in order to provide implementations for them.
When the RTX renderer or NVIDIA Iray is active, or more specifically, an  `rtx.hydra` instance is active, this
mapping can be accessed for the active scene renderer.

```python
import omni.mdl.neuraylib

# acquire the neuraylib instance from OV
ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()

# access a USD shader nodes MDL representation. Note, this USD shader node has to exist in the scene
usd_prim_path: str = "/World/Looks/Material/Shader"
ov_entity = ov_neuraylib.createMdlEntity(usd_prim_path)

if ov_entity and ov_entity.valid():
    # create a snapshot from the entity, the actual MDL node exists only for snapshot of the current point in time
    ov_entity_snapshot = ov_neuraylib.createMdlEntitySnapshot(ov_entity)
    if ov_entity_snapshot and ov_entity_snapshot.valid():
        print(f"dbScopeName: {ov_entity_snapshot.dbScopeName}")
        print(f"dbName: {ov_entity_snapshot.dbName}")
        # ...
        # use omni.mdl.pymdlsdk to get low-level access to the MDL function call using its `dbName`
        # ...

        # destroy the MdlEntitySnapshot
        ov_neuraylib.destroyMdlEntitySnapshot(ov_entity_snapshot)
    else:
        # this means that there is a node for this entity but no function is selected yet
        # setting up the nodes function is done in rtx.hydra and not available in python

    # destroy the mdlEntity
    ov_neuraylib.destroyMdlEntity(ov_entity)
```

## Registration of MDL extension content

Omniverse Extensions can ship their own MDL modules that can be used in Omniverse and USD.
The only requirement for a user to access these modules is to enable the extension of interest.

The extension developer needs to register the content during startup and unregister during shutdown.
This allows extensions developers to:
* reference their own MDL materials in USD for rendering and parameter editing
* reference their own MDL materials in any MDL module using (absolute) fully qualified MDL names
<!-- *(not yet released)*
* register functions and materials as nodes in the Material Graph Editor for more complex authoring
* register materials in the `Create|Material` menu and in the context menu
-->

### Add content to MDL search paths

To be able to reference MDL modules that ship with an extension in USD, the content has to be referenced in an MDL search path.

Please Note: always put your content into proper packages to avoid collisions with other modules.
The MDL module space is similar to package names in python and java. They have to be unique.
A common pattern is to put the company in front, followed by a project or product name.

```python
import omni.mdl.neuraylib
from pathlib import Path

# fetch information about the current extension
ext_id = omni.kit.app.get_app().get_extension_manager().get_extension_id_by_module(__name__)
ext_dir = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id))
ext_name: str = omni.ext.get_extension_name(ext_id)

# assuming the content we are interested in is located in the extension subfolder called `data/mdl` subfolder.
ext_mdl_dir = ext_dir.joinpath('data', 'mdl')

# register the content
# NOTE keep the returned links in order to unregister on shutdown
linkedContentPaths: list[str] = omni.mdl.neuraylib.register_extension_content(ext_name, str(ext_content_mdl_dir))
```

Assuming the MDL module to reference is called `A.mdl`, that its path inside the extension folder is `data/mdl/my_company/my_project/P1/P2/A.mdl`, and that the module contains a material called `Main`, a corresponding reference in USD would be:

```python
def Shader "ShaderNode"
{
    uniform token info:implementationSource = "sourceAsset"
    uniform asset info:mdl:sourceAsset = @my_company/my_project/P1/P2/A.mdl@
    uniform token info:mdl:sourceAsset:subIdentifier = "Main"
    token outputs:out (
        renderType = "material"
    )
}
```

Referencing that content in an import statement of an arbitrary other MDL module is possible using it's fully qualified MDL name:
```python
import ::my_company::my_project::P1::P2::A::*;
```
or only the `Main` material:
```python
import ::my_company::my_project::P1::P2::A::main;
```

To clean up during the extension shutdown the content needs to be unregistered:

```python
import omni.mdl.neuraylib

# fetch information about the current extension
ext_id = omni.kit.app.get_app().get_extension_manager().get_extension_id_by_module(__name__)
ext_name: str = omni.ext.get_extension_name(ext_id)

# unregister the content
# to remove the extension content, usually done when unloading the extension
removed: bool = omni.mdl.neuraylib.unregister_extension_content(ext_name, linkedContentPaths)
```

<!-- *(not yet released)*
### Add nodes to the Material Graph Editor
t.b.d.

### Add entries to the Create|Material menus
t.b.d.
-->

## Enable MDL module resolution without the RTX renderer
Without the RTX renderer enabled, or more specifically, without `rtx.hydra`, neuray needs to be started manually in order to enable MDL module resolution in USD. During the neuray startup, the MDL search paths are registered at the USD Asset Resolver. When using the RTX renderer or NVIDIA Iray, this is done automatically.

```python
import omni.mdl.neuraylib

# this starts neuray if not running already
omni.mdl.neuraylib.ensure__running()
```
