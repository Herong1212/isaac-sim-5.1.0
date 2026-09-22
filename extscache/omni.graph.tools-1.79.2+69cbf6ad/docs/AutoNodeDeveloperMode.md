(omnigraph_autonode_developer_mode)=

# AutoNode - Developer Mode

  <!--
  _______ ____  _____   ____
 |__   __/ __ \|  __ \ / __ \
    | | | |  | | |  | | |  | |
    | | | |  | | |  | | |  | |
    | | | |__| | |__| | |__| |
    |_|  \____/|_____/ \____/

 The documentation for AutoNode will be filled out once the functionality is all in place as it keeps changing
 during development. The feature is hidden behind a setting and this documentation is only visible in internal
 builds.
 -->


```{warning}
This feature is currently only a prototype. While in development it must be enabled explicitly by defining the Carbonite
setting both `/omnigraph/autonode/enabled` and `/omnigraph/autonode/developer` to 1, e.g. by using the command line
option **--/omnigraph/autonode/developer=1 --/omnigraph/autonode/enabled=1**.
Interfaces, behavior, and documentation for this feature are subject to change without notice.
```

Developer mode is used when you wish to publish your AutoNode node type definitions so that they can be used by other
extensions and saved in USD files. To enable developer mode in your extension you must add an entry into your
`extension.toml` file that defines the node type definition location(s). This one shows that AutoNode definitions
can be found in the `autonode/` subdirectory of the extension's Python module. If there is more than one import path
then all of them will be checked.

```{code-block} toml
[omni.graph.autonode]
developer_mode = true
import_paths = ["autonode"]
```

In this example the code that defines your AutoNode node type definitions are found in the Python import module
`omni.my.extension.autonode`.

```{tip}
Directories are recursively searched so for good performance you should keep all of
your AutoNode definitions confined to a single file where possible.
```

A more targeted approach is to put all of the `AutoNode` definitions in leaf level files and add the paths to those
files directly in the `extension.toml` definition.

```{code-block} toml
[omni.graph.autonode]
developer_mode = true
import_paths = [
    "core/autonode_definitions.py",
    "geometry/autonode_definitions.py",
    "math/autonode_definitions.py",
    "rendering/autonode_definitions.py",
    "utility/autonode_definitions.py",
]
```

```{note}
Omitting the `import_paths` or having an entry in it that is an empty string `import_paths = [""]` indicates that
the entire Python module directory is to be searched for AutoNode definitions.
```

If you have a build for your extension (i.e. a `premake5.lua` file) then you must add a flag to your ogn project
definition to enable generation of AutoNode node types as part of your build. Otherwise the node type definitions
will be generated at runtime and you will not have tests or documentation for the node type available for shipping
with your extension.

```{code-block} lua
local ogn = get_ogn_project_information(ext, "omni/my/extension")
ogn.enable_autonode = true
```
