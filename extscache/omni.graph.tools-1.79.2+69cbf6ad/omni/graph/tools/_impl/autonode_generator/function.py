"""Support for the AutoNode decorator that turns a Python function into an OmniGraph node type definition

NodeTypeFromFunctionScan provides the bridge between the Python function and the OGN equivalent.
"""

import copy
import json
import logging
from collections import OrderedDict
from typing import _GenericAlias

from .ogn_types import TypeConversion
from .utils import GeneratedCode, as_class_name, python_name_to_ui_name
from .wrappers import AutoNodeDefinitionWrapper

EXEC_ATTRIBUTE_PREFIX = "exec"
NODE_DATA_LITERAL = "node_data"
_logger = logging.getLogger("AutoNode")


# ==============================================================================================================
class _AutoNodeGenericFunction:  # pragma: no cover    Unsupported code
    """
    OGN Python function runner
    TODO (oshapira): see if this is still necessary
    """

    def __init_subclass__(
        cls,
        function_name: str,
        unique_name: str,
        module_name: str,
        annotation: dict,
        autonode_data: dict,
        returns_tuple: bool,
        has_execution_pins: bool,
    ) -> None:
        cls.function_name = function_name
        cls.unique_name = unique_name
        cls.module_name = module_name
        cls.annotation = next(iter(json.loads(annotation).values()))
        cls.autonode_data = autonode_data
        cls.returns_tuple = returns_tuple
        cls.has_execution_pins = has_execution_pins

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def _generate_clean_compute(cls, code: GeneratedCode):
        """Generates the function call for the compute when no type conversions are required.
        Assumes the name of the function to call is "func_obj".
        Args:
            code: Generator to accept the compute code
        """
        output_prefix = "out_"

        def key_filter(x: str) -> bool:
            ret = not x.startswith("_")  # no private attributes
            ret &= not x.startswith(EXEC_ATTRIBUTE_PREFIX)  # no exec attributes
            return not ret

        # The outputs are all named "out_X" where X is the numerical index of the return values. For a single return
        # value it's out_0, otherwise it's the tuple index for multiple return values.
        output_list = [
            output
            for output in cls.annotation["outputs"]
            if output.startswith(output_prefix) and output[len(output_prefix) :].isnumeric()
        ]
        return_line = ""
        if len(output_list) == 1:
            return_line = "db.outputs.out_0"
        elif output_list:
            return_values = tuple(f"db.outputs_out_{key}" for key in range(len(output_list)))
            return_line = f"{return_values}"

        # The function call itself
        with code.indent(f"{return_line} = func_obj("):
            for key in cls.annotation["inputs"]:
                if key_filter(key):
                    continue
                code.line(f"db.inputs.{key}")
        code.line(")")

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def generate_compute(cls) -> tuple[str, set[str]]:
        """Generates a compute function for an instantiated class.
        This code generator aims to minimize the size of code that runs at every frame. This is the simplest form
        where the data types are all native OGN types:

        .. code-block:: python

            def compute(db) -> bool:
                func_obj = ogn.FunctionRegistry.get_function("omni.graph.core.an_float_test")
                (db.outputs.out_0,) = func_obj(db.inputs.value)
                return True

        Returns:
            Tuple of (code implementing the compute, imports required by the code)
        Raises:
            ParseError: If something in the definitions could not be converted into compute code
        """
        code = GeneratedCode()
        imports = {
            "import omni.graph.tools.ogn as ogn",
            "import omni.graph.core as og",
            f"from {cls.module_name} import {cls.function_name}",
        }

        code.line("@staticmethod")
        with code.indent("def compute(db) -> bool:"):
            with code.indent("try:"):
                code.line(f'func_obj = ogn.FunctionRegistry.get_function("{cls.unique_name}")')
                with code.indent("if func_obj is None:"):
                    code.line(
                        f"raise og.OmniGraphError(\"The function {cls.unique_name} that implements this node's"
                        ' compute() algorithm could not be found. Its extension may not be configured properly.")'
                    )

                # For now only the simplest cases are handled, where the inputs and outputs are all OGN types so no
                # conversion is required.
                cls._generate_clean_compute(code)

                if cls.has_execution_pins:
                    code.line("db.outputs.exec = True")

            with code.indent("except og.OmniGraphError as error:"):
                code.line("db.log_error(str(error))")
                code.line("return False")

            code.line("return True")

        _logger.info("Generated node type definition class %s", cls.unique_name)
        return (str(code), imports)

    # --------------------------------------------------------------------------------
    @classmethod
    def internal_state(cls):
        """Returns the internal state data on the generated AutoNode node type"""
        return None if cls.autonode_data is None else copy.copy(cls.autonode_data)


# ==============================================================================================================
class NodeTypeFromFunctionScan(AutoNodeDefinitionWrapper):  # pragma: no cover    Unsupported code
    """Class to wrap python functions and classmethods. Contains methods for creating an OGN annotation from a python
    function, and methods for applying values to the function. Takes as input the encoded function definitions, such
    as the ones extracted from the AST of raw text code int compiler.py.

    Attributes:
        _returns_tuple:
        _argument_cache:
        _has_node_data_signature:
        _node_impl: Wrapper object with the node implementation definition for the AutoNode node type

        class_name: Name of the class defining the AutoNode node type
        python_name: Name of the function defining the AutoNode node type
        name: UI name of the node type
        add_execution_pins: Should the node type automatically add input and output execution pins so that it can
                            be used as part of an Action Graph?
        unique_name: Fully namespaced unique name of the AutoNode node type
        module_name: Generated qualified name of the function to provide it with a unique Python module
        descriptor: Contents of the OGN for the AutoNode node type
    """

    def __init__(
        self,
        func_descriptor: str,
        func_name: str,
        func_signature: str,
        func_docstring: str,
        *,
        add_execution_pins: bool,
        ui_name: str,
        unique_name: str,
        module_name: str,
        tags: list[str],
        annotation: dict = None,
    ) -> None:
        """Set up the AutoNode type definition from a function definition

        Args:
            func_descriptor: Identifier to the user of this function
            func_name: Name of the function
            func_signature: A fixed key dictionary containing the unpacked information about the function where
                **parameters**: *List of inputs to the function and their types*
                **return_annotation**: *Unpacked type of the function's return value for use as output attribute*
            func_docstring: Documentation of the function, pulled from its __doc__ value
            *: Forces the following arguments to have a keyword, so they cannot be added positionally
            add_execution_pins: If True, automatically generate input and output execution pins for the Action Graph
            ui_name: User visible name of the generated node type
            unique_name: Unique (namespaced) name of the generated node type
            module_name: Unique generated Python module name in which the generated node type will live
            tags: Set of tags to attach to the node type definition
            annotation: Overrides to the type annotations, usually required to differentiate CPython types like
                double/float/half which only exist in Python as "float". The value is a dictionary where the keyword
                "return" provides the type annotation for the output of the node type and any other keywords correspond
                to the type annotation of the named input. e.g. f(a:int) -> float -> {"return": "float", "a": "int"}
        """
        super().__init__()
        self._returns_tuple = False
        self._argument_cache: dict = {}
        self._has_node_data_signature = False
        self._node_impl = None

        self.python_name = func_name
        self.name = ui_name or f"{python_name_to_ui_name(self.python_name)} (AutoNode)"

        self.add_execution_pins = add_execution_pins or False
        if unique_name is None:
            raise NameError(f"{func_descriptor} does not have a specified unique name")

        self.unique_name = unique_name
        self.module_name = module_name
        self.class_name = as_class_name(func_name)

        self.descriptor = {}
        self.descriptor["uiName"] = self.name
        self.descriptor["version"] = 1
        self.descriptor["language"] = "Python"
        self.descriptor["tags"] = tags or []

        docstring = func_docstring or "[no documentation]"
        self.descriptor["description"] = f"{docstring}. (Autogenerated.)"

        self.descriptor["inputs"] = OrderedDict(
            {
                "__an_function_name__": {
                    "uiName": "Function Name",
                    "type": "string",
                    "description": "Name of the function from which this node type was generated",
                    "metadata": {"hidden": 1},
                    "default": f"{self.module_name}.{func_name}",
                }
            }
        )

        if self.add_execution_pins:
            self.descriptor["tags"].append("action")
            self.descriptor["inputs"][EXEC_ATTRIBUTE_PREFIX] = {
                "uiName": "Exec",
                "description": "exec input",
                "type": "execution",
            }

        if annotation is not None:
            # If the annotation shim exists, use it:
            for key in annotation:
                if key == "return":
                    self._set_output_type(annotation[key])
                elif key != "self":
                    self._add_input(key, annotation[key])
                else:
                    # FIXME (OS): func.__class__ will not contain the whole type
                    # in the case pybind is used
                    raise NotImplementedError()
                    # self._add_input(key, func.__class__)
        else:
            # fall back to inspection otherwise
            sig = func_signature
            params = sig["parameters"]
            for name, the_annotation in params.items():
                if name == NODE_DATA_LITERAL:  # This node holds state
                    self._has_node_data_signature = True
                elif name != "self":
                    self._add_input(name, the_annotation)
                else:
                    raise NotImplementedError()
                    # self._add_input(item.name, func.__class__)
            self._set_output_type(sig["return_annotation"])

    # --------------------------------------------------------------------------------
    @staticmethod
    def get_type_signature(type_desc: type, docstring: str) -> dict:
        """Constructs an OGN type signature from the incoming type. If the type can be converted to a native OGN type,
        the method attempts to do this automatically.

        Args:
            type_desc: A type object corresponding to the attribute type
            docstring: Description of the attribute whose signature is being created

        Returns:
            dict: OGN properties of the type description, including the type name, default value, and metadata
        """
        if type_desc is None:
            return None
        conversion = TypeConversion.from_type(type_desc)
        ret = {"description": docstring}
        if conversion is not None:
            ret["type"] = conversion.ogn_type
            if conversion.default is not None:
                ret["default"] = conversion.default
        else:
            try:
                type_name = type_desc.__name__
            except AttributeError:
                type_name = str(type_desc)
            ret["type"] = "objectId"
            ret["metadata"] = {"python_type_desc": type_name}
        return ret

    # --------------------------------------------------------------------------------
    def _add_input(self, name: str, type_desc: type):
        """Adds an input to the function wrpper

        Args:
            name: a string to name the input in the node's public interface
            type_desc: a type for the function's public interface
        """
        self.descriptor["inputs"][name] = NodeTypeFromFunctionScan.get_type_signature(
            type_desc, f"Function input {name}"
        )
        self.descriptor["inputs"].move_to_end(name)

    # --------------------------------------------------------------------------------
    def _set_output_type(self, type_desc: type):
        """Sets the function's output signature. Adds an "exec" port if the function is marked as "add_execution_pins"
        If the function returns a 'Tuple' type, the Tuple is unpacked to individual node outputs,
        labeled 'out_0', 'out_1', etc.

        Args:
            type_desc: a return type
        """
        outputs = OrderedDict()
        if self.add_execution_pins:
            outputs[EXEC_ATTRIBUTE_PREFIX] = {"type": "execution", "description": "Execution output"}
        if type_desc is None:
            self.descriptor["outputs"] = outputs
            return

        # Handle case where tuples are returned
        if isinstance(type_desc, _GenericAlias) and type_desc.__origin__ == tuple:
            self._returns_tuple = True

        if self._returns_tuple:
            for num, tuple_type_desc in enumerate(reversed(type_desc.__args__)):
                name = f"out_{num}"
                outputs[name] = NodeTypeFromFunctionScan.get_type_signature(tuple_type_desc, f"Function output {num}")
                outputs.move_to_end(name)
        else:
            outputs["out_0"] = NodeTypeFromFunctionScan.get_type_signature(type_desc, "Function output")
            outputs.move_to_end("out_0")

        self.descriptor["outputs"] = outputs

    # --------------------------------------------------------------------------------
    def get_ogn(self) -> str:
        """Gets the OGN function representation

        Returns:
            str: A JSON String with the representation
        """
        d = {self.python_name: self.descriptor}
        return json.dumps(d, indent=2)

    # --------------------------------------------------------------------------------
    def get_node_impl_source(self) -> str:
        """Get the source of this OGN object's node type implementation

        Returns:
            str: Code that implements the compute of an AutoNode definition
        """

        class NodeImpl(
            _AutoNodeGenericFunction,
            function_name=self.python_name,
            unique_name=self.get_unique_name(),
            module_name=self.get_module_name(),
            annotation=self.get_ogn(),
            # FIXME (OS): Change to actual type
            autonode_data={} if self._has_node_data_signature else None,
            returns_tuple=self._returns_tuple,
            has_execution_pins=self.add_execution_pins,
        ):
            pass

        compute_impl, imports = NodeImpl.generate_compute()
        code = GeneratedCode()
        for import_line in imports:
            code.line(import_line)
        code.line("")
        code.line("")
        with code.indent(f"class {self.class_name}:"):
            code.block(str(compute_impl))

        return str(code)

    # --------------------------------------------------------------------------------
    def get_node_impl(self) -> type:
        """Lazy fetch of the node implementation class

        Returns:
            NodeImpl: Wrapper class containing the implementation of the AutoNode
        """
        if self._node_impl is None:

            class NodeImpl(
                _AutoNodeGenericFunction,
                function_name=self.python_name,
                unique_name=self.get_unique_name(),
                module_name=self.get_module_name(),
                annotation=self.get_ogn(),
                # FIXME (OS): Change to actual type
                autonode_data={} if self._has_node_data_signature else None,
                returns_tuple=self._returns_tuple,
            ):
                pass

            self._node_impl = NodeImpl

        return self._node_impl

    # --------------------------------------------------------------------------------------------------------------
    def get_unique_name(self) -> str:
        """Returns the unique name of the AutoNode generated node type"""
        return self.unique_name

    # --------------------------------------------------------------------------------------------------------------
    def get_module_name(self) -> str:
        """Returns the local (module) name of the AutoNode generated node type"""
        return self.module_name
