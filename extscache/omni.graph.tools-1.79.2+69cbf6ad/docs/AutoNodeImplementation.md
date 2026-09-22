# AutoNode Implementation

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

The {ref}`AutoNode user document <omnigraph_autonode>` shows how to make use of ``AutoNode`` features. This document
shows how these features are implemented under the covers.

There are two modes of operation of ``AutoNode``, [](#live-mode) and [](#developer-mode). The two have very different
use cases. If you just want to get started using ``AutoNode`` without any outside development then look into the
[](#live-mode) section. If you want to create ``AutoNode`` definitions you can bundle with your extension then jump
right to the [](#developer-mode) sections.

## Live Mode

"Live" in this context refers to the fact that the ``AutoNode`` definitions will be parsed and implemented directly
within the Python scripting environment. These are definitions you might type directly in to the script editor, or
run as part of an external script.

They are processed as part of the Python parsing, generate a .ogn definition internally, and from that generate
the node type definition and API, which are added directly to the extension's Python module. No files are saved
are loaded. All of the Python definition are processed in code.

```{mermaid}
flowchart TD
    A("@node_type") --> B(_generate_node_type)
    B --> C(FunctionRegistry)
```

```{note}
This section must be filled in with more details on live mode.
```

## Developer Mode

As the name might hint, this mode is mostly for use by developers. It provides the framework for defining ``AutoNode``
node types in a way that lets the node definitions persist in the extension. In the same way that a .ogn file will be
used to generate the database definition for the node implementation to use, an ``AutoNode`` definition will be used
to create the .ogn and .py files that implement a node based on a Python function or class.

```{mermaid}
flowchart TD
    A(Find Files) --> B(Read Files)
    B --> C(AST Parse Files)
    C --> D(Extract Decorated Functions)
    D --> E(Generate Node Type Definitions on Disk)
    E --> F(Run Node Type Generator)
```

### Locating The AutoNode Definitions

The ``AutoNode`` system must locate the definitions for parsing. It makes use of extension information and by
monitoring the state of extensions to optimize the number of places it will look for these definitions.

#### extension.toml Configuration

The first piece the developer must put in place is a few settings in their ``extension.toml`` configuration file.
A typical addition will look like this:

```{code-block} toml
[omni.graph.autonode]
developer_mode = true
import_paths = ["omni.graph.examples.python._impl.autonode"]
```

This is the content used by the ``omni.graph.examples.python`` extension to enable developer mode for a few
``AutoNode`` definitions it has.

The **[omni.graph.autonode]** line defines the dictionary entry to which these settings belong. It has to be exactly
as written since the ``AutoNode`` code looks for it by name.

**developer_mode = true** tells the system that ``AutoNode`` should enable developer mode for this extension to scan
for ``AutoNode`` definitions when the extension is enabled.

**import_paths = []** provides a list of specific Python import modules in which to look for ``AutoNode`` definitions.
It's more efficient to keep them isolated to a small module, but if you do not know where they will be implemented or
they can be implemented anywhere in your extension you can point this at the module(s) specified in your
``extension.toml``s **[[python.module]]** section.

#### Extension Monitoring

Once the ``AutoNode`` module has been initialized it creates a subscription to the extension enabled event in the
class {py:class}`omni.graph.core.autonode.AutoNodeExtensionWatcher`.

```{mermaid}
flowchart TD
    A[import omni.graph.core.autonode] -->|Instantiate| B(AutoNodeExtensionWatcher)
    B --> C[[Listen for Enabled]]
```

When an extension enabled event is encountered ``AutoNode`` reads the configuration information from the extension's
``extension.toml`` file to check if developer mode is enabled and find the list of modules in which it can find any
``AutoNode`` definitions. It then runs {py:func}`omni.graph.tools.ogn.build_autonode_from_folder` on each folder to
populate the ``AutoNode`` registry, which will be used to generate the node type definitions.

```{mermaid}
flowchart TD
    A[Listen for Enable] -->|"rebuild()"| B(Read Configuration)
    B --> C{For Each Module}
    C -->|Find Folder| D["build_autonode_from_folder()"]
    D --> C
```

{py:func}`omni.graph.tools.ogn.build_autonode_from_folder` generates the ``AutoNode`` node type definitions from the
descriptions it finds, and then optionally runs the OGN node generator on those definitions if it has been give a
directory in which to write those generated files.

#### Direct Invocation

In addition to the indirect extension monitoring that will automatically scan an extension for ``AutoNode``
definitions there is also a utility in ``ogn_helpers.lua`` named ``make_inline_generator_command()`` that can be
called as part of the build to accomplish the same goal. The difference is that the location of the module is assumed
to correspond to the extension, and there is only one, rather than being inferred from the extension configuration.

The above example could also have been implemented in the ``premake5.lua`` file of ``omni.graph.examples.python`` as
the function call:

```{code-block} lua
    make_inline_generator_command(ogn, "omni.graph.examples.python")
```

### Parsing The Definitions

After it has found the locations of all definitions {py:func}`omni.graph.tools.ogn.build_autonode_from_folder`
creates an {py:class}`omni.graph.tools._impl.autonode_generator.compiler.AutoNodeModule` object that will scan all
of the files in the module looking for ``AutoNode`` definitions.

```{mermaid}
flowchart TD
    A[Parse AST] --> B(Scan For Decorators)
    B --> |"Filter for OmniGraphNode"| C[Parse With AST]
    C --> D[Construct .ogn File]
    C --> E[Construct .py File]
    D --> F[Add Pairs To List]
    F --> G{"More Functions?"}
    E --> F
    G --> |Yes| C
    G --> |No| H[Return File Pairs]
```

For each file it uses the Python ``ast`` module to scan for decorators, gathering the annotation data for each
decorator it encounters as well as the object it decorates.

For each decorator that is part of ``AutoNode`` it uses the AST to create a wrapper around the function definition
of type {py:class}`omni.graph.tools._impl.autonode_generator.function.AOTAutoFunctionWrapper`. It extracts the
syntactic information from the function to create the corresponding .ogn and .py node type implementation files.

The wrapper has two functions ``get_ogn()`` and ``get_node_impl_source()`` tha accomplish this.

## Cleanup Needed

The two implementation trees, one in ``omni.graph`` and the other in ``omni.graph.tools`` have a lot of duplication
that should be resolved. The originals all live in ``omni.graph``.

### Support Files

These are the various files that mention or implement the AutoNode features.

```{code} text
omni.graph.tools/                          omni.graph/                       omni.graph.docs/
  python/                                    python/                           docs/
    generate_inline_nodes.py                   __init__.py                       CoreConcepts.md
    ogn.py                                     autonode.py                       Overview.md
    _impl/                                     _impl/                            dev/
      autonode_generator/                        bundles.py                        Versioning.md
        __init__.py                              autonode/                         WritingNodes.md
        compiler.py                                __init__.py
        function.py                                autonode.py
        main.py                                    core.py
        type_definitions.py                        enum_wrappers.py
        util.py                                    event.py
    tests/                                         function.py
      compiler/                                    property.py
        data/                                      type_definitions.py
          imported_module.py                       util.py
          test_module.py                     docs/
          test-subfolder/                      AutoNode.md
            test_subfolder_file.py             AutoNodeOperation.md
```

### Generated Files

Live mode has no generated files. For Developer mode in extension ``omni.mine`` with script ``an.py``
in Python module ``omni.mine.autonode`` containing ``OmniGraphNode`` decorations on functions ``node_a`` and ``node_b``
these are the potential files that will exist when those nodes are fully realized.

**BUILD** is the root of the build directory. **CACHE** is the root of the code generator's cache directory, which it
uses for storing nodes generated when the supplied generated code is out of date. Assumes version _1.2.3_ of OmniGraph
and version _2.3.4_ of ``omni.mine``.

```{code} text
BUILD/                                       CACHE/
  exts/                                        1.2.3/
    omni.mine/                                   omni.mine-2.3.4/
      ogn/                                         omni.mine/
        docs/                                        ogn/
          OgnNodeA.rst                                 __init__.py
          OgnNodeB.rst                                 OgnNodeADatabase.py
      omni/                                            OgnNodeBDatabase.py
        mine/                                          docs/
          autonode.py                                    OgnNodeA.rst
          ogn/                                           OgnNodeB.rst
            OgnNodeADatabase.py                        tests/
            OgnNodeBDatabase.py                          TestOgnNodeA.py
            _autonode/                                   TestOgnNodeB.py
              OgnNodeA.ogn                               usd/
              OgnNodeA.py                                  OgnNodeATemplate.usda
              OgnNodeB.ogn                                 OgnNodeBTemplate.usda
              OgnNodeB.py                              _autonode/
            tests/                                       OgnNodeA.ogn
              TestOgnNodeA.py                            OgnNodeA.py
              TestOgnNodeB.py                            OgnNodeB.ogn
              usd/                                       OgnNodeB.py
                OgnNodeATemplate.usda
                OgnNodeBTemplate.usda
```
