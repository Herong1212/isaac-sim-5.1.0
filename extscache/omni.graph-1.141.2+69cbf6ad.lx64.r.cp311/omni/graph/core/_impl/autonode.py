"""Runtime support for the AutoNode features, including the decorators that define node type implementations

Typical usage examples:

    # begin-autonode-examples
    import omni.graph.core as og
    import omni.graph.core.types as ot

    # Simple decorator with no configuration. When run from the script editor creates a node type definition
    # with the name "__autonode__.add_two" with two inputs named "inputs:a" and "inputs:b" of type integer and one
    # output named "outputs:out_0" of type integer. The node type description will be "Add two numbers together"
    # and the UI name will be "Add Two", being just the automatic capitalization of the function name.
    @og.create_node_type
    def add_two(a: ot.int, b: ot.int) -> ot.int:
       '''Add two numbers together'''
       return a + b

    # The same decorated function with an empty argument list, which will be exactly the same as the above
    @og.create_node_type()
    def add_two(a: ot.int, b: ot.int) -> ot.int:
       '''Add two numbers together'''
       return a + b

    # The same decorated function with an override of the unique name. The attributes and metadata will be the same
    # as above but the node type name will be "omni.math.add_two" while the UI name remains "Add Two".
    @og.create_node_type(unique_name="omni.math.add_two")
    def add_two(a: ot.int, b: ot.int) -> ot.int:
       '''Add two numbers together'''
       return a + b

    # The same decorated function with an override of the UI name. The unique name remains "__autonode__.add_two",
    # the attributes and description remain the same, but the UI name becomes "Add Two Integers"
    @og.create_node_type(ui_name="Add Two Integers")
    def add_two(a: ot.int, b: ot.int) -> ot.int:
       '''Add two numbers together'''
       return a + b

    # The same decorated function configured to participate in an Action Graph. All of the definitions remain with
    # the node type but two extra attributes are added, an input execution type named "inputs:execution" and an
    # output execution type named "outputs:execution".
    @og.create_node_type(add_execution_pins=True)
    def add_two(a: ot.int, b: ot.int) -> ot.int:
       '''Add two numbers together'''
       return a + b

    # The same decorated function configured to add metadata indicating that the node type belongs to the category
    # "math:operator"
    @og.create_node_type(categories=["math:operator"])
    def add_two(a: ot.int, b: ot.int) -> ot.int:
       '''Add two numbers together'''
       return a + b

    # end-autonode-examples

Note that at this time AutoNode cannot accept the extended data types "any" or "union" as there is no mechanism
for type resolution.
"""

import inspect
import logging
from functools import partial, wraps
from types import NoneType

import omni.ext
import omni.graph.core as og
import omni.graph.core.types as ot
import omni.graph.tools._internal as ogti
import omni.kit

from .unstable.attribute_spec import AttributeSpec
from .unstable.runtime_node_types import RUNTIME_MODULE_NAME, define_node_type, deregister_runtime_node_type


# ==============================================================================================================
class NodeTypeConstructionError(Exception):
    """Exception specific to caught errors in the node type construction process"""


# ==============================================================================================================
# Get the common logger used by all AutoNode features, both build time and runtime
_logger = logging.getLogger("AutoNode")


# Internal name for the automatically generated execution pins
_EXEC_PIN = "execute"


# ==============================================================================================================
def developer_mode_active(ext_name: str) -> tuple[bool, list[str]]:
    """Check to see if AutoNode developer mode is active on the given extension:
    Args:
        ext_name: Name of the extension to check
    Returns:
        (bool: is the extension in developer mode?, list[str]: List of import paths specified)
    """
    if not ogti.autonode_developer_mode():
        return False

    manager = omni.kit.app.get_app().get_extension_manager()
    # Disabled extensions are by definition not in developer mode
    ext_id = manager.get_enabled_extension_id(ext_name)
    if ext_id is None:
        return (False, [])

    ext_dict = manager.get_extension_dict(ext_id)
    try:
        autonode_config = ext_dict.get("omni", {}).get("graph", {}).get("autonode", {})
        if not autonode_config:
            return (False, [])
        return (autonode_config.get("developer_mode", False), autonode_config.get("import_paths", []))
    except AttributeError:
        return (False, [])


# ==============================================================================================================
def _generate_node_type(
    compute_function: callable,
    *,
    module_name: str = None,
    unique_name: str = None,
    ui_name: str = None,
    add_execution_pins: bool = False,
    metadata: dict[str, str] = None,
):
    """Create a runtime node type definition from a function decorated by create_node_type.

    Args:
        compute_function: the function object to convert to a node type compute function.
        module_name: Name of the module to which the function belongs (required for registration)
        unique_name: Decoration parameter to override the default unique name
        ui_name: Decoration parameter to override the name that appears in the node type's menu and node display.
        add_execution_pins: Decoration parameter indicating that both input and output execution pins should be added
        so that this can be used as a trigger node type in an action graph.
        metadata: Decoration parameter containing a dictionary of extra metadata to apply to the node type.
        Special metadata of RUNTIME_MODULE_NAME:True invokes testing mode where the generated node type definition
        is not registered with OmniGraph.
    """
    _logger.info(
        "Attempting to generate OmniGraph node type in %s, name=%s, ui_name=%s, add_execution_pins=%s, metadata=%s",
        module_name,
        unique_name,
        ui_name,
        add_execution_pins,
        metadata,
    )

    if compute_function is None or not callable(compute_function):
        raise NodeTypeConstructionError("Cannot construct AutoNode type without a compute function")
    try:
        name = compute_function.__name__
        description = compute_function.__doc__ if compute_function.__doc__ else "[No description provided]"
    except AttributeError as error:
        raise NodeTypeConstructionError(
            f"AutoNode compute function {compute_function} must have a name and docstring"
        ) from error

    if not isinstance(ui_name, (NoneType, str)):
        raise NodeTypeConstructionError(f"ui_name must be None or a string, got {ui_name}")
    ui_name = f"{ogti.python_name_to_ui_name(name)} (AutoNode)" if ui_name is None else ui_name

    if not isinstance(metadata, (NoneType, dict)):
        raise NodeTypeConstructionError(f"metadata argument must be a dictionary of str:any, got {metadata}")
    metadata = metadata or {}
    if not all(isinstance(key, str) for key in metadata):
        raise NodeTypeConstructionError(f"metadata must be a dictionary of str:any, got {metadata}")
    testing_mode = metadata.get(RUNTIME_MODULE_NAME, False)
    # Testing mode calls this function directly, otherwise it goes through the decorator
    caller_depth = 1 if testing_mode else 2
    metadata = {key: str(value) for key, value in metadata.items() if key != RUNTIME_MODULE_NAME}

    if not isinstance(add_execution_pins, (NoneType, bool)):
        raise NodeTypeConstructionError(f"add_execution_pins must be a boolean, got {add_execution_pins}")
    add_execution_pins = bool(add_execution_pins)

    try:
        module = inspect.getmodule(inspect.stack()[caller_depth][0])
        module_name = module.__name__ if module else RUNTIME_MODULE_NAME
        if module_name == "__main__":
            module_name = RUNTIME_MODULE_NAME
        _logger.debug("AutoNode definition found at module %s", module_name)
    except (AttributeError, KeyError) as error:
        module_name = RUNTIME_MODULE_NAME
        _logger.debug("AutoNode module not found in generator, using default. (%s)", error)
    if module_name == RUNTIME_MODULE_NAME:
        ext_id = None
        ext_name = RUNTIME_MODULE_NAME
    else:
        ext_id = omni.kit.app.get_app().get_extension_manager().get_extension_id_by_module(module_name)
        if ext_id is None:
            # Some external module that belongs to no extension
            ext_name = RUNTIME_MODULE_NAME
        else:
            ext_name = omni.ext.get_extension_name(ext_id)
            if not ext_id or not ext_name:
                _logger.warning(
                    "Unable to find the extension owning module %s. Defaulting to unowned and adding the namespace"
                    " '%s' to guarantee uniqueness.",
                    module_name,
                    RUNTIME_MODULE_NAME,
                )
                ext_id = None
                ext_name = RUNTIME_MODULE_NAME

    if not isinstance(unique_name, (NoneType, str)):
        raise NodeTypeConstructionError(f"unique_name must be None or a string, got '{unique_name}'")
    unique_name = f"{ext_name}.{name}" if unique_name is None else unique_name

    _logger.debug("   Name = %s", name)
    _logger.debug("   Full Name = %s", unique_name)
    _logger.debug("   UI Name = %s", ui_name)
    _logger.debug("   Description = %s", description)
    _logger.debug("   Metadata = %s", metadata)
    _logger.debug("   Add Pins = %s", add_execution_pins)
    _logger.debug("   Ext ID = %s", ext_id)
    _logger.debug("   Ext Name = %s", ext_name)
    _logger.debug("   Testing = %s", testing_mode)

    inputs = []
    outputs = []
    annotations = inspect.get_annotations(compute_function)
    for attr_name, ann in annotations.items():
        if attr_name == "return":
            # Output of None, or no output, means no output attributes are required
            if ann is None:
                continue
            # Tuple output means there are multiple outputs
            if getattr(ann, "__origin__", None) == tuple:
                ann = ann.__args__
            else:
                ann = (ann,)
            for output_ann in ann:
                output_name = f"out_{len(outputs)}"
                type_name = ot.convert_type(output_ann, ot.DataTypeRepresentation.PYTHON, ot.DataTypeRepresentation.OGN)
                outputs.append(
                    AttributeSpec(name=output_name, port_type=og.AttributePortType.OUTPUT, type_name=type_name)
                )
        else:
            type_name = ot.convert_type(ann, ot.DataTypeRepresentation.PYTHON, ot.DataTypeRepresentation.OGN)
            # Process an input
            inputs.append(AttributeSpec(name=attr_name, port_type=og.AttributePortType.INPUT, type_name=type_name))
            # Flag the duplication of an execution input
            if type_name == "execution" and attr_name == _EXEC_PIN:
                raise NodeTypeConstructionError(
                    f"Specified 'add_execution_pins' but also had input named '{_EXEC_PIN}'."
                    " Either rename your input argument or remove the 'add_execution_pins' argument."
                )

    extra_inputs = []
    extra_outputs = []
    if add_execution_pins:
        _logger.info("Adding input and output execution pins named '%s'", _EXEC_PIN)
        extra_inputs.append(AttributeSpec(name=_EXEC_PIN, port_type=og.AttributePortType.INPUT, type_name="execution"))
        extra_outputs.append(
            AttributeSpec(name=_EXEC_PIN, port_type=og.AttributePortType.OUTPUT, type_name="execution")
        )

    _logger.info("INPUTS: %s", [input_spec.full_name() for input_spec in inputs + extra_inputs])
    _logger.info("OUTPUTS: %s", [output_spec.full_name() for output_spec in outputs + extra_outputs])

    def _runtime_methods():
        """Returns the dictionary of Name:Function of methods constructed to be overrides in the runtime node type"""

        def runtime_compute(context: og.GraphContext, node: og.Node):
            """Function called when a node of type defined from this generated type is asked to execute.
            This wraps a simple Python function call to expose it to OmniGraph as a node type for execution.
            This simple implementation assumes that looking up attributes by name at runtime is fast enough for
            the intended usage. Otherwise it is a good opportunity for optimization.
            Args:
                context: Graph context of the node
                node: Node being executed
            """
            input_values = []
            for attr in inputs:
                value = node.get_attribute(attr.full_name()).get() if attr.type_name != "bundle" else None
                match attr.type_name:
                    case "bundle":
                        input_values.append(
                            og.BundleContents(context, node, attr.full_name(), read_only=True, gpu_by_default=False)
                        )
                    # TODO: There is a problem with the matrix shape when getting values this way in that it returns the
                    #       values as a flat list. Reshape it so that it can be dealt with properly by the compute.
                    case "matrixd[2]":
                        input_values.append(value.transpose().reshape((2, 2)))
                    case "matrixd[2][]":
                        input_values.append(value.reshape((int(value.size / 4), 2, 2)).transpose(0, 2, 1))
                    case "matrixd[3]":
                        input_values.append(value.transpose().reshape((3, 3)))
                    case "matrixd[3][]":
                        input_values.append(value.reshape((int(value.size / 9), 3, 3)).transpose(0, 2, 1))
                    case "matrixd[4]":
                        input_values.append(value.transpose().reshape((4, 4)))
                    case "matrixd[4][]":
                        input_values.append(value.reshape((int(value.size / 16), 4, 4)).transpose(0, 2, 1))
                    case "frame[4]":
                        input_values.append(value.transpose().reshape((4, 4)))
                    case "frame[4][]":
                        input_values.append(value.reshape((int(value.size / 16), 4, 4)).transpose(0, 2, 1))
                    case _:
                        input_values.append(value)
            try:
                output_values = compute_function(*input_values)
                output_values = (output_values,) if len(outputs) == 1 else output_values
                for output_value, output in zip(output_values, outputs):
                    # Bundle outputs would have been set directly already
                    if output.type_name == "bundle":
                        continue
                    # TODO: There is a problem with the matrix shape when setting values this way in that they expect
                    #       values as a flat list. Reshape it so that it can be dealt with properly by the compute.
                    if (
                        output.type_name.startswith("matrix") or output.type_name.startswith("frame")
                    ) and not output.type_name.endswith("[]"):
                        node.get_attribute(output.full_name()).set(output_value.flatten())
                    else:
                        node.get_attribute(output.full_name()).set(output_value)
            except ValueError:
                return False
            except og.OmniGraphError as error:
                node.log_compute_message(og.Severity.ERROR, f"Compute failed: {error}")
                return False
            if add_execution_pins:
                node.get_attribute(f"outputs:{_EXEC_PIN}").set(og.ExecutionAttributeState.ENABLED)
            return True

        return {"compute": runtime_compute}

    method_overrides = _runtime_methods()

    # The testing will need to inspect the results without registration so return everything that was extracted
    # as a dictionary. More detailed testing will use registration and can inspect the results using the
    # runtime node type definition.
    if testing_mode:
        return {
            "name": name,
            "description": description,
            "ui_name": ui_name,
            "unique_name": unique_name,
            "module_name": module_name,
            "metadata": metadata,
            "extension": ext_name,
            "inputs": inputs + extra_inputs,
            "outputs": outputs + extra_outputs,
            "method_overrides": method_overrides,
        }

    # All of the information is now ready to define the node type
    definition = define_node_type(
        name=unique_name,
        version=1,
        description=description,
        extension=ext_name,
        attributes=inputs + outputs + extra_inputs + extra_outputs,
        ui_name=ui_name,
        metadata=metadata,
        method_overrides=method_overrides,
    )
    # AutoNode allows iteration of runtime node type definitions so first deregister any existing node types with
    # the same name
    deregister_runtime_node_type(unique_name)
    definition.register()

    return definition


# ==============================================================================================================
# begin-create-node-type
def create_node_type(
    func: callable = None,
    *,
    unique_name: str = None,
    ui_name: str = None,
    add_execution_pins: bool = False,
    metadata: dict[str, str] = None,
) -> callable:
    """Decorator to transform a Python function into an OmniGraph node type definition.
    The decorator is configured to allow use with and without parameters. When used without parameters all of the
    default values for the parameters are assumed.

    If the function is called from the __main__ context, as it would if it were executed from the script editor or
    from a file, then the decorator is assumed to be creating a short-lived node type definition and the default
    module name "__autonode__" is applied to indicate this. Any attempts to save a scene containing these short-term
    node types will be flagged as a warning.

    Examples:
        >>> import omni.graph.core as og
        >>> @og.create_node_type
        >>> def double_float(a: ogdt.Float) -> ogdt.Float:
        >>>     return a * 2.0
        >>>
        >>> @og.create_node_type(add_execution_pins=True)
        >>> def double_float(a: ogdt.Float) -> ogdt.Float:
        >>>     return a * 2.0

    Args:
        func: the function object being wrapped. Should be a pure python function object or any other callable which
        has an `__annotations__` property. If "None" then the decorator was called using the parameterized form
        "@create_node_type(...)" instead of "@create_node_type" and the function will be inferred in other ways.
        unique_name: Override the default unique name, which is the function name in the module namespace
        ui_name: Name that appears in the node type's menu and node display.
        add_execution_pins: Include both input and output execution pins so that this can be used as a trigger node
        type in an action graph.
        metadata: Dictionary of extra metadata to apply to the node type
    Returns:
        Decorated version of the function that will create the node type definition
    """
    # end-create-node-type
    # Get the keyword arguments for passing along, skipping the positional argument
    kwargs = {kw: value for kw, value in locals().items() if kw != "func"}

    # Detect when the decorator is called as "@create_node_type" instead of "@create_node_type(..)"
    no_parameters = func is not None

    def _return_as_is(*log_args) -> callable:
        """Returns a reference to the decorated function with an added error message
        Args:
            log_args: List of arguments to pass to the logging function when the undecorated function is called
        """

        # Return an appropriate decorator that just passes through the function
        if no_parameters:
            _logger.debug(*log_args)
            return func

        def call_autonode_function(func):
            @wraps(func)
            def autonode_disabled(*args, **kwargs):
                func(*args, **kwargs)

            return autonode_disabled()

        _logger.debug(*log_args)
        return call_autonode_function

    # Get the caller for extraction of the module information. The module will tell us where the function is defined,
    # though not necessarily where it's imported from. That's okay because this is for internal use so it's better to
    # have the exact information than the user-friendly version (plus the latter can change for different imports).
    calling_frame = inspect.stack()[1][0]

    try:
        module = inspect.getmodule(calling_frame)
        kwargs["module_name"] = module.__name__ if module else RUNTIME_MODULE_NAME
        if kwargs["module_name"] == "__main__":
            kwargs["module_name"] = RUNTIME_MODULE_NAME
        _logger.debug("AutoNode definition found at module %s", kwargs["module_name"])
    except (AttributeError, KeyError) as error:
        kwargs["module_name"] = RUNTIME_MODULE_NAME
        _logger.debug("AutoNode module not found, using default. (%s)", error)

    _logger.debug("No parameter decorator = %s with args (%s, %s)", no_parameters, func, kwargs)

    # Two variations of return values depending on whether the decorator had arguments or not.
    # When no arguments were present then the args list contains just the name of the function being decorated.
    if no_parameters:
        return _generate_node_type(func, **kwargs)

    # When arguments are present the return value must be wrapped as the decorator isn't passed the function directly.
    def inner_decorator(wrapped_func, **kwargs):
        _generate_node_type(wrapped_func, **kwargs)
        return wrapped_func

    # Using partial here forces an early binding that makes the call at import time instead of only when running
    # the function, which is needed in order to add the function to the registry.
    return partial(inner_decorator, **kwargs)
