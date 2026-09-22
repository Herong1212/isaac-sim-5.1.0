```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`,{ref}`changelog_omni_syntheticdata`
```

(ext_omni_syntheticdata)=

# omni.syntheticdata

## Introduction

This extension provides low level OmniGraph nodes for preparing synthetic data AOVs and annotator outputs for the higher
level Omniverse Replicator extension. End user applications should use the Replicator APIs, rather than using this
extension directly.

The extension also includes support for older deprecated Omniverse Synthetic Data APIs. If you are currently using
these older APIs, we suggest reviewing the newer Replicator APIs and switching to these.

A preview visualization component is also included - this is accessible from the viewport synthetic data icon when
the extension is installed.

```{toctree}
:maxdepth: 1
:caption: OmniGraph Nodes In This Extension
:glob:

GeneratedNodeDocumentation/*
```
