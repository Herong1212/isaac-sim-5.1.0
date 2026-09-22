# Python Usage Examples

## Load an MDL module and listing it's materials
Here is a simple but complete example of how to access the materials defined in a given MDL module.
The `INeuray` and the `ITransaction` instances are provided by `omni.mdl.neuraylib`.
All other functionalities of the MDL SDK bindings can be used independent of Omniverse.

```python
import omni.mdl.pymdlsdk as pymdlsdk    # low-level MDL python binding that matches the native SDK
import omni.mdl.neuraylib               # interface the OV material backend

# acquire the neuraylib instance from OV
ov_neuraylib = omni.mdl.neuraylib.get_neuraylib()

# feed the neuray instance handle into the python binding
ov_neuray_handle = ov_neuraylib.getNeurayAPI()
neuray: pymdlsdk.INeuray = pymdlsdk.attach_ineuray(ov_neuray_handle)

# we need to load modules to Omniverse using the omni.mdl.neuraylib to allow proper tracking of loaded content,
# to enable reloads, and more Omniverse specific features
usd_identifier = "nvidia/support_definitions.mdl"
ov_module = ov_neuraylib.createMdlModule(usd_identifier)

if ov_module and ov_module.valid():
    # create a transaction after loading so we we can see the loaded module
    # we also request a handle from omni.mdl.neuraylib to initialize a pymdlsdk (Python Binding) transaction.
    ov_transaction_handle = ov_neuraylib.createReadingTransaction()
    transaction: pymdlsdk.ITransaction = pymdlsdk.attach_itransaction(ov_transaction_handle)

    # the MdlModule returned from omni.mdl.neuray provides the database name of the MDL module
    # after accessing it using a transaction, you have a IModule with all its MDL SDK functionality and API
    m: pymdlsdk.IModule = transaction.access_as(pymdlsdk.IModule, ovModule.dbName)

    # for example to access the containing material definitions:
    for i in range(m.get_material_count()):
        definition_db_name: str = m.get_material(i)
        definition: pymdlsdk.IFunction_definition = trans.access_as(pymdlsdk.IFunction_definition, definition_db_name)
        simple_name: str = definition.get_mdl_simple_name()
        print(f"found material: {simple_name}" )

    # MdlModules, MdlEntities, and MdlEntitySnapshots returned from omni.mdl.neuraylib need to be destroyed when not needed anymore
    ov_neuraylib.destroyMdlModule(ovModule)
```
