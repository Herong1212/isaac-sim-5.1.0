```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Omni MDL extension provides access to MDL materials in Omniverse.  
The core features of this extensions are:
- Providing the `neuray` instance used in Omniverse for accessing the MDL SDK API
- Create database `scopes` and `transactions` for accessing the database content used by the renderer
- Create `MdlModule`, `MdlEntity`, and `MDLEntitySnapshots` that wrap the MDL module loading and the mapping from USD shade to MDL nodes

 The extension also provides access to more features around the MDL integration in Omniverse:
- Registration of MDL content shipped with extensions
- Initialization of neuray to enable MDL module resolution in USD in case the RTX renderer is not used

For examples, please see the [Python](USAGE_PYTHON) usage page.

## User Guide

- For more information about the MDL SDK Python API in Omniverse, please visit the documentation of [omni.mdl](https://docs.omniverse.nvidia.com/kit/docs/omni.mdl).
- For more MDL SDK examples, including Python examples, please consult the examples on [Github](https://github.com/NVIDIA/MDL-SDK/tree/master/examples).
- [](CHANGELOG)
