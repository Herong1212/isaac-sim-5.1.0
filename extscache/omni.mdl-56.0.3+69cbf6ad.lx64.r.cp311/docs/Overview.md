```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Omni MDL extension provides access to the MDL SDK Python bindings.
This low-level binding is automatically generated from the C++ API using SWIG.
With only a limited number of exceptions, it offers the same functionality as the native API using a nearly identical set of functions and classes.
For detailed API documentation, examples, and the source code, please consult:
- [NVIDIA Ray Tracing Documentation](https://raytracing-docs.nvidia.com/mdl/index.html)
- [NVIDIA MDL Github](https://github.com/NVIDIA/MDL-SDK)

## MDL in Omniverse

The MDL SDK relies on the neuray API which is shared with the NVIDIA Iray renderer.
At its core, there is a database that stores the MDL modules, their definitions, and calls.
Calls are instantiated function definitions along with their parameters.
Since parameters can reference other calls, they describe entire material graphs that correspond to the USD materials composed of USD shader nodes.
This means that MDL provides the implementation of the abstract material description in USD.

The binding itself is independent of Omniverse and Kit.
To be able to work on the same database as Omniverse, another extension, called [omni.mdl.neuraylib](https://docs.omniverse.nvidia.com/kit/docs/omni.mdl.neuraylib), is used.

Getting an `INeuray` instance is the first step for all MDL SDK development:

```python
import omni.mdl.pymdlsdk as pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.neuraylib               # interface the OV material backend

# acquire the neuraylib instance from OV
ov_neuray_lib = omni.mdl.neuraylib.get_neuraylib()

# feed the neuray instance handle into the python binding
ov_neuray_handle = ov_neuray_lib.getNeurayAPI()
neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(ov_neuray_handle)
```

For accessing the materials used by the active renderer, an `ITransaction` is needed.
Instead of creating the transaction directly using the `IDatabase` component, call the `omni.mdl.neuraylib` functions for proper interop with Omniverse. 

```python
# acquire the neuraylib instance from OV
ov_neuray_lib = omni.mdl.neuraylib.get_neuraylib()

# create a transaction after loading so we we can see the loaded module
# we also request a handle from omni.mdl.neuraylib to initialize an omni.mdl (Python Binding) transaction.
ov_transaction_handle = ov_neuray_lib.createReadingTransaction()
transaction: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ov_transaction_handle)

```

For a more complete example, please see the [Python](USAGE_PYTHON) usage page.

## User Guide

- For more examples on the integration in Omniverse, please visit the documentation of [omni.mdl.neuraylib](https://docs.omniverse.nvidia.com/kit/docs/omni.mdl.neuraylib).
- For more MDL SDK examples, including Python examples, please consult the examples on [Github](https://github.com/NVIDIA/MDL-SDK/tree/master/examples).
- [](CHANGELOG)
