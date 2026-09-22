# Array Tool [omni.tools.array]

The Array Tool is used to create an array of objects in multiple dimensions. All USD Xformable types are supported - non-xformable types will not work (scopes, materials, etc.). The Array Tool defaults to creating instances, and therefore expects valid instanceable prims (Xforms) to be selected/provided. You can also switch to "Create Copies" if you do not want to create instances.

### CreateArrayCommand
Creates an Array of prims - undoable/redoable.

Can be used outside of the Array Tool extension.

Args:
* target_prims (list): The list of prims to array. Expects prims, not prim paths.
* array_values (dict): The values to use to construct the array. Expects a dictionary matching the one seen in ArrayParams().

Returns:
* Do() (tuple): (Created prim paths: list, Grouped prims path: list, Seleced prims path: list)


