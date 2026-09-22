"""Support for generating a pythonic interface class for OmniGraph Nodes.

Exports:
    generate_python: Create a NODE.ogn.py file containing a pythonic interface for the node data
"""

import json
import re
from contextlib import suppress
from pathlib import Path
from typing import List, Optional

from .attributes.AttributeManager import AttributeManager
from .attributes.naming import INPUT_NS, OUTPUT_NS, PORT_NAMES, STATE_NS
from .keys import CudaPointerValues, LanguageTypeValues, MemoryTypeValues, MetadataKeyOutput, MetadataKeys
from .nodes import NodeInterfaceGenerator
from .utils import GeneratorConfiguration, logger, shorten_string_lines_to

__all__ = ["generate_python"]


class NodePythonGenerator(NodeInterfaceGenerator):
    """Manage the functions required to generate a Python interface for a node"""

    def __init__(self, configuration: GeneratorConfiguration):  # noqa: PLW0246
        """Set up the generator and output the Python interface code for the node

        Just passes the initialization on to the parent class. See the argument and exception descriptions there.
        """
        super().__init__(configuration)

    # ----------------------------------------------------------------------
    def interface_file_name(self) -> str:
        """Return the path to the name of the Python file"""
        return self.base_name + "Database.py"

    # ----------------------------------------------------------------------
    def database_class_name(self) -> str:
        """Return the name of the generated database class, which is what will be passed to the compute method"""
        return f"{self.base_name}Database"

    # ----------------------------------------------------------------------
    def _value_class_name(self, namespace: str) -> str:
        """Return the name of the internal class that holds attributes in the given namespace"""
        return f"ValuesFor{namespace.capitalize()}"

    # ----------------------------------------------------------------------
    def _pre_class_spacing(self):
        """Writes out spacing before class names - follows Flake8 in verbose mode, nothing otherwise"""
        self.out.write()
        self.out.write()

    # ----------------------------------------------------------------------
    def _pre_function_spacing(self):
        """Writes out spacing before function definitions - follows Flake8 in verbose mode, nothing otherwise"""
        self.out.write()

    # ----------------------------------------------------------------------
    def _filter_out_batched_attributes(self, attribute_list: List[AttributeManager], namespace: str):
        """
        Args:
            attribute_list: List of attributes belonging to the generated class
            namespace: Namespace of attributes in the list. Assumption is that all attributes have the same answer.

        Returns:
            Two lists of attributes: batched attributes and the filtered list without batched attributes"""
        if namespace == STATE_NS or self.node_interface.language != LanguageTypeValues.PYTHON:
            return [], attribute_list

        batched_attribute_list = []
        filtered_attribute_list = []

        for attribute in attribute_list:
            # batching of attributes is not supported for runtime types
            # batching of array attributes wouldn't be the most efficient. best is to acquire the right size
            # numpy.array once and work with it directly currently only limited to CPU memory
            if (
                attribute.ogn_base_type() not in ["bundle", "target", "any", "union"]
                and attribute.array_depth == 0
                and attribute.memory_storage() == MemoryTypeValues.CPU
            ):
                batched_attribute_list.append(attribute)
            else:
                filtered_attribute_list.append(attribute)

        return batched_attribute_list, filtered_attribute_list

    # ----------------------------------------------------------------------
    def _generate_attribute_class(self, attribute_list: List[AttributeManager], namespace: str) -> Optional[str]:
        """Output a nested class that provides database access for the node's input or output attributes.

        Args:
            attribute_list: List of attributes belonging to the generated class
            namespace: Namespace of attributes in the list. Assumption is that all attributes have the same answer.
                       Passed explicitly to allow for the possibility of an empty list.

        Returns:
            The name of the class that was generated (None if not generated)

        The attribute classes have two members per attribute:
            attr_PROPERTY: Holds a reference to the node's Attribute member for this attribute
            PROPERTY: A property through which the attribute values are accessed
        """
        # This method is called with all attributes in the same namespace so it's safe to use the first one
        # to extract the common definition.

        attribute_class = self._value_class_name(namespace)
        is_read_only = namespace == INPUT_NS
        # For correct syntax the namespace name must be singular
        namespace_for_comment = namespace[:-1] if namespace.endswith("s") else namespace

        self._pre_function_spacing()
        if self.out.indent(f"class {attribute_class}(og.DynamicAttributeAccess):"):
            batched_attribute_list, filtered_attribute_list = self._filter_out_batched_attributes(
                attribute_list, namespace
            )
            has_batched_attributes = len(batched_attribute_list) > 0
            if has_batched_attributes:
                local_property_list = [attribute.python_property_name() for attribute in batched_attribute_list]
                if namespace == INPUT_NS:
                    local_property_list += ["_setting_locked", "_batchedReadAttributes", "_batchedReadValues"]
                elif namespace == OUTPUT_NS:
                    local_property_list += ["_batchedWriteValues"]
                batched_str = "{" + ", ".join(f'"{attribute}"' for attribute in local_property_list) + "}"
                self.out.write(f"LOCAL_PROPERTY_NAMES = {batched_str}")
            elif namespace != STATE_NS:
                self.out.write("LOCAL_PROPERTY_NAMES = { }")

            self.out.write(
                f'"""Helper class that creates natural hierarchical access to {namespace_for_comment} attributes"""'
            )
            if self.out.indent(
                "def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):"
            ):
                self.out.write('"""Initialize simplified access for the attribute data"""')
                self.out.write("context = node.get_graph().get_default_graph_context()")
                self.out.write("super().__init__(context, node, attributes, dynamic_attributes)")
                has_bundles = False
                gpu_bundles = []
                gpu_ptr_kinds = {}
                for attribute in attribute_list:
                    if attribute.ogn_base_type() == "bundle":
                        has_bundles = True
                        if attribute.memory_type != MemoryTypeValues.CPU:
                            gpu_bundles.append(attribute.usd_name())
                            with suppress(KeyError):
                                gpu_ptr_kinds[attribute.usd_name()] = CudaPointerValues.PYTHON[
                                    self.node_interface.cuda_pointer_type
                                ]
                if has_bundles:
                    gpu_ptr_str = "{" + ",".join(f'"{key}": {value}' for key, value in gpu_ptr_kinds.items()) + "}"
                    self.out.write(
                        f"self.__bundles = og.BundleContainer(context, node, attributes, {gpu_bundles},"
                        f" read_only={is_read_only}, gpu_ptr_kinds={gpu_ptr_str})"
                    )

                # Output arrays will need a size since that has to be set when the user gets their values.
                # This puts the onus on the caller to set the size before calling get(). For safety, the sizes
                # are initialized to None so that failure to set values can generate a sensible error message.
                if not is_read_only:
                    for attribute in attribute_list:
                        if attribute.fabric_needs_counter():
                            default_size = "None" if attribute.default is None else len(attribute.default)
                            self.out.write(f"self.{attribute.python_property_name()}_size = {default_size}")

                # Initialize storage for batched values
                if namespace == INPUT_NS:
                    batched_str = (
                        "["
                        + ", ".join(f"self.{attribute.python_attribute_name()}" for attribute in batched_attribute_list)
                        + "]"
                    )
                    self.out.write(f"self._batchedReadAttributes = {batched_str}")
                    batched_values = []
                    for attribute in batched_attribute_list:
                        value = attribute.python_value_as_repr(attribute.default)
                        batched_values.append(value)
                    batched_str = ", ".join(str(value) for value in batched_values)
                    self.out.write(f"self._batchedReadValues = [{batched_str}]")
                elif namespace == OUTPUT_NS:
                    self.out.write("self._batchedWriteValues = { }")

                self.out.exdent()
            for attribute in filtered_attribute_list:
                # Emit the getters and setters for the attributes.
                attribute.generate_python_property_code(self.out)

            for index, attribute in enumerate(batched_attribute_list):
                # Emit the getters and setters for batched read or write
                attribute.generate_python_batched_property_code(index, self.out)

            if has_batched_attributes:
                # Override any dynamic getters and setters for batched attributes to remove the overhead
                self.out.write()
                if self.out.indent("def __getattr__(self, item: str):"):
                    if self.out.indent("if item in self.LOCAL_PROPERTY_NAMES:"):
                        self.out.write("return object.__getattribute__(self, item)")
                        self.out.exdent()
                    if self.out.indent("else:"):
                        self.out.write("return super().__getattr__(item)")
                        self.out.exdent()
                    self.out.exdent()
                self.out.write()
                if self.out.indent("def __setattr__(self, item: str, new_value):"):
                    if self.out.indent("if item in self.LOCAL_PROPERTY_NAMES:"):
                        self.out.write("object.__setattr__(self, item, new_value)")
                        self.out.exdent()
                    if self.out.indent("else:"):
                        self.out.write("super().__setattr__(item, new_value)")
                        self.out.exdent()
                    self.out.exdent()

            if namespace == INPUT_NS:
                self.out.write()
                if self.out.indent("def _prefetch(self):"):
                    self.out.write("readAttributes = self._batchedReadAttributes")
                    self.out.write("newValues = _og._prefetch_input_attributes_data(readAttributes)")
                    if self.out.indent("if len(readAttributes) == len(newValues):"):
                        self.out.write("self._batchedReadValues = newValues")
                        self.out.exdent()
                    self.out.exdent()
            elif namespace == OUTPUT_NS:
                self.out.write()
                if self.out.indent("def _commit(self):"):
                    self.out.write("_og._commit_output_attributes_data(self._batchedWriteValues)")
                    self.out.write("self._batchedWriteValues = { }")
                    self.out.exdent()

            self.out.exdent()

        return attribute_class

    # ----------------------------------------------------------------------
    def _generate_shared_node_type_initialize(self):
        """
        Output the code to set up any shared node type information, like adding attributes and setting metadata.
        Assumes this is part of a method where the variable "node_type" contains the node type object to initialize
        """
        # Set the metadata for this node type
        self.out.write(f"node_type.set_metadata(ogn.MetadataKeys.EXTENSION, {json.dumps(self.extension)})")
        for key, value in self.node_interface.metadata.items():
            python_key = MetadataKeyOutput.python_name_from_key(key)
            if python_key is None:
                python_key = json.dumps(key)
            # Handle lists as a comma-separated string
            if isinstance(value, list):
                value = '"' + ",".join([x.replace('"', '\\"') for x in value]) + '"'
            else:
                value = json.dumps(value)
            self.out.write(f"node_type.set_metadata({python_key}, {value})")
        if self.node_interface.memory_type != MemoryTypeValues.CPU:
            self.out.write(f'node_type.set_metadata(ogn.MetadataKeys.MEMORY_TYPE, "{self.node_interface.memory_type}")')

        # The icon path is relative to the extension path, which is only known at runtime, so build it up then.
        # To the user it will appear as an absolute path, which they can modify if they wish to.
        if self.node_interface.icon_path is not None:
            icon_path = json.dumps(self.node_interface.icon_path)
            # If the path is absolute then it does not need to be resolved at runtime
            if Path(self.node_interface.icon_path).is_absolute():
                self.out.write(f"node_type.set_metadata(ogn.MetadataKeys.ICON_PATH, {icon_path})")
            else:
                self.out.write(f'icon_path = carb.tokens.get_tokens_interface().resolve("${{{self.extension}}}")')
                # Using os.path.join here causes problems due to the backslash path separator on Windows. The components
                # both have forward slashes by design so just insert the missing one.
                self.out.write(f"icon_path = icon_path + '/' + {icon_path}")
                self.out.write("node_type.set_metadata(ogn.MetadataKeys.ICON_PATH, icon_path)")

        # If any of the scheduling hints flags have been defined then set them here
        if self.node_interface.scheduling_hints is not None:
            self.node_interface.scheduling_hints.emit_python(self.out)

        # Generate the initialization of attributes, including setting defaults and adding them to the node type
        if self.node_interface.has_attributes():
            self.out.write(f"{self.database_class_name()}.INTERFACE.add_to_node_type(node_type)")
        if self.node_interface.all_state_attributes() or self.node_interface.has_state:
            self.out.write("node_type.set_has_state(True)")

    # ----------------------------------------------------------------------
    def _generate_node_registration(self):
        """
        Output the definition of the node type's registration support method
        By having the node type class object be a static class member a circular import can be avoided.
        The node implementation will call OgnTheNodeDatabase.register(OgnTheNode) to handle registration and the
        automatic override of any ABI methods that OgnTheNode might implement.
        """
        db_class_name = self.database_class_name()
        self._pre_function_spacing()
        self.out.write("NODE_TYPE_CLASS = None")

        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def register(node_type_class):"):
            self.out.write(f"{db_class_name}.NODE_TYPE_CLASS = node_type_class")
            self.out.write(f"og.register_node_type({db_class_name}.abi, {self.node_interface.version})")
            self.out.exdent()
        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def deregister():"):
            self.out.write(f'og.deregister_node_type("{self.node_interface.name}")')
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_abi_get_node_type(self):
        """Output the abi implementation of the get_node_type method"""
        db_class_name = self.database_class_name()
        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def get_node_type():"):
            self.out.write(f"get_node_type_function = getattr({db_class_name}.NODE_TYPE_CLASS, 'get_node_type', None)")
            # Any overrides will be counted as part of the implementation so skip the coverage here to avoid
            # false positives when the functions do not exist.
            if self.out.indent("if callable(get_node_type_function):  # pragma: no cover"):
                self.out.write("return get_node_type_function()")
                self.out.exdent(f"return '{self.node_interface.name}'")
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_abi_compute(self):
        """Output the abi implementation of the compute method"""
        db_class_name = self.database_class_name()

        def __generate_attribute_validate(attribute_list: List[AttributeManager]):
            """Write out any code that verifies the validity of attributes before trying to compute"""
            for attribute in attribute_list:
                attribute.generate_python_validation(self.out)

        def __generate_database_validate():
            if self.out.indent("def database_valid():"):
                __generate_attribute_validate(self.node_interface.all_input_attributes())
                __generate_attribute_validate(self.node_interface.all_output_attributes())
                __generate_attribute_validate(self.node_interface.all_state_attributes())
                self.out.write("return True")
                self.out.exdent()

        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def compute(context, node):"):
            __generate_database_validate()

            # Construct the database that accesses the Fabric data in a Pythonic way
            if self.out.indent("try:"):
                self.out.write(f"per_node_data = {db_class_name}.PER_NODE_DATA[node.node_id()]")
                self.out.write("db = per_node_data.get('_db')")
                if self.out.indent("if db is None:"):
                    self.out.write(f"db = {db_class_name}(node)")
                    self.out.write("per_node_data['_db'] = db")
                    self.out.exdent()

                # Remove database if validation fails. Database removal allows internal pointers and handles to be reconstructed.
                if self.out.indent("if not database_valid():"):
                    self.out.write("per_node_data['_db'] = None")
                    self.out.write("return False")
                    self.out.exdent()

                self.out.exdent()
            # Currently with hot reload we are not getting PER_NODE_DATA initialized. Just generate the db on the fly.
            if self.out.indent("except:"):
                self.out.write(f"db = {db_class_name}(node)")
                self.out.exdent()

            self.out.write()
            if self.out.indent("try:"):
                # The ABI compute method has the same name as the generated compute method to be called, so use
                # the fact that the ABI method has more parameters to figure out which one the node has defined.
                self.out.write(f"compute_function = getattr({db_class_name}.NODE_TYPE_CLASS, 'compute', None)")
                # Any overrides will be counted as part of the implementation so skip the coverage here to avoid
                # false positives when the functions do not exist.
                if self.out.indent(
                    "if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover"
                ):
                    self.out.write("return compute_function(context, node)")
                    self.out.exdent()

                self.out.write()
                # Fetch input attributes registered for batch read
                self.out.write("db.inputs._prefetch()")

                # Special flag that prevents inputs from being modified inside a compute method, which avoids
                # synchronization problems. In C++ this is enforced by returning const values; this is equivalent.
                # Suppress the error that occurs if no inputs were generated.
                self.out.write("db.inputs._setting_locked = True")

                # If the node attempted to write a const value the compute will throw AttributeError saying why
                if self.out.indent("with og.in_compute():"):
                    self.out.write(f"return {db_class_name}.NODE_TYPE_CLASS.compute(db)")
                    self.out.exdent()
                self.out.exdent()
            # For this error only the name of the attribute is returned, to minimize duplication of strings
            # Any exceptions raised as part of the implementation will be counted at the raise location so skip the
            # coverage here that handles it to avoid false positives when exceptions are never raised.
            if self.out.indent("except Exception as error:  # pragma: no cover"):
                self.out.write('stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))')
                self.out.write(
                    "db.log_error(f'Assertion raised in compute - {error}\\n{stack_trace}', add_context=False)"
                )
                self.out.exdent()
            if self.out.indent("finally:"):
                self.out.write("db.inputs._setting_locked = False")
                # Commit output attributes registered for batch write
                self.out.write("db.outputs._commit()")
                self.out.exdent()
            self.out.write("return False")
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_abi_initialize(self):
        """Output the abi implementation of the initialize method"""
        db_class_name = self.database_class_name()
        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def initialize(context, node):"):
            # Give the database a chance to cache away any node-specific data that will not change each evaluation
            self.out.write(f"{db_class_name}._initialize_per_node_data(node)")

            self.out.write(f"initialize_function = getattr({db_class_name}.NODE_TYPE_CLASS, 'initialize', None)")
            # Any overrides will be counted as part of the implementation so skip the coverage here to avoid
            # false positives when the functions do not exist.
            if self.out.indent("if callable(initialize_function):  # pragma: no cover"):
                self.out.write("initialize_function(context, node)")
                self.out.exdent()

            self.out.write()
            self.out.write(f"per_node_data = {db_class_name}.PER_NODE_DATA[node.node_id()]")
            self.out.write()
            if self.out.indent("def on_connection_or_disconnection(*args):"):
                self.out.write("per_node_data['_db'] = None")
                self.out.exdent()

            self.out.write()
            self.out.write("node.register_on_connected_callback(on_connection_or_disconnection)")
            self.out.write("node.register_on_disconnected_callback(on_connection_or_disconnection)")
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_abi_initialize_nodes(self):
        """Output the abi implementation of the initialize method"""
        db_class_name = self.database_class_name()
        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def initialize_nodes(context, nodes):"):
            if self.out.indent("for n in nodes:"):
                self.out.write(f"{db_class_name}.abi.initialize(context, n)")
                self.out.exdent()
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_abi_release(self):
        """Output the abi implementation of the release method"""
        db_class_name = self.database_class_name()
        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def release(node):"):
            self.out.write(f"release_function = getattr({db_class_name}.NODE_TYPE_CLASS, 'release', None)")
            # Any overrides will be counted as part of the implementation so skip the coverage here to avoid
            # false positives when the functions do not exist.
            if self.out.indent("if callable(release_function):  # pragma: no cover"):
                self.out.write("release_function(node)")
                self.out.exdent()

            # Release any node-specific data that was cached during the initialize function
            self.out.write(f"{db_class_name}._release_per_node_data(node)")

            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_abi_init_instance(self):
        """Output the abi implementation of the init instance method"""
        db_class_name = self.database_class_name()
        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def init_instance(node, graph_instance_id):"):
            self.out.write(f"init_instance_function = getattr({db_class_name}.NODE_TYPE_CLASS, 'init_instance', None)")
            # Any overrides will be counted as part of the implementation so skip the coverage here to avoid
            # false positives when the functions do not exist.
            if self.out.indent("if callable(init_instance_function):  # pragma: no cover"):
                self.out.write("init_instance_function(node, graph_instance_id)")
                self.out.exdent()
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_abi_release_instance(self):
        """Output the abi implementation of the release instance method"""
        db_class_name = self.database_class_name()
        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def release_instance(node, graph_instance_id):"):
            self.out.write(
                f"release_instance_function = getattr({db_class_name}.NODE_TYPE_CLASS, 'release_instance', None)"
            )
            # Any overrides will be counted as part of the implementation so skip the coverage here to avoid
            # false positives when the functions do not exist.
            if self.out.indent("if callable(release_instance_function):  # pragma: no cover"):
                self.out.write("release_instance_function(node, graph_instance_id)")
                self.out.exdent()
            self.out.write(f"{db_class_name}._release_per_node_instance_data(node, graph_instance_id)")
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_abi_update_node_version(self):
        """Output the abi implementation of the update_node_version method"""
        db_class_name = self.database_class_name()
        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def update_node_version(context, node, old_version, new_version):"):
            self.out.write(
                f"update_node_version_function = getattr({db_class_name}.NODE_TYPE_CLASS, 'update_node_version', None)"
            )
            # Any overrides will be counted as part of the implementation so skip the coverage here to avoid
            # false positives when the functions do not exist.
            if self.out.indent("if callable(update_node_version_function):  # pragma: no cover"):
                self.out.write("return update_node_version_function(context, node, old_version, new_version)")
                self.out.exdent("return False")
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_abi_initialize_type(self):
        """Output the abi implementation of the intialize_type method"""
        db_class_name = self.database_class_name()
        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def initialize_type(node_type):"):
            self.out.write(
                f"initialize_type_function = getattr({db_class_name}.NODE_TYPE_CLASS, 'initialize_type', None)"
            )
            self.out.write("needs_initializing = True")
            # Any overrides will be counted as part of the implementation so skip the coverage here to avoid
            # false positives when the functions do not exist.
            if self.out.indent("if callable(initialize_type_function):  # pragma: no cover"):
                self.out.write("needs_initializing = initialize_type_function(node_type)")
                self.out.exdent()

            # By returning a bool the initialize_type override can request attribute additions from the parent
            # rather than a full override.
            if self.out.indent("if needs_initializing:"):
                self._generate_shared_node_type_initialize()
                self.out.exdent()

            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_abi_on_connection_type_resolve(self):
        """Output the abi implementation of the on_connection_type_resolve method"""
        db_class_name = self.database_class_name()
        self._pre_function_spacing()
        self.out.write("@staticmethod")
        if self.out.indent("def on_connection_type_resolve(node):"):
            self.out.write(
                "on_connection_type_resolve_function = "
                f"getattr({db_class_name}.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)"
            )
            # Any overrides will be counted as part of the implementation so skip the coverage here to avoid
            # false positives when the functions do not exist.
            if self.out.indent("if callable(on_connection_type_resolve_function):  # pragma: no cover"):
                self.out.write("on_connection_type_resolve_function(node)")
                self.out.exdent()
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_database_abi(self):
        """Output a registration method and subclass that handles ABI access for the Python node"""

        self._pre_function_spacing()
        if self.out.indent("class abi:"):
            self.out.write('"""Class defining the ABI interface for the node type"""')

            self._generate_abi_get_node_type()
            self._generate_abi_compute()
            self._generate_abi_initialize()
            self._generate_abi_initialize_nodes()
            self._generate_abi_release()
            self._generate_abi_init_instance()
            self._generate_abi_release_instance()
            self._generate_abi_update_node_version()
            self._generate_abi_initialize_type()
            self._generate_abi_on_connection_type_resolve()
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_token_help(self):
        """Generate the help information showing how to access any hardcoded tokens in the file"""
        if not self.node_interface.tokens:
            return
        self.out.write()
        if self.out.indent("Predefined Tokens:"):
            for token_name, _ in self.node_interface.tokens.items():
                self.out.write(f"tokens.{token_name}")
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_tokens(self):
        """Generate the code required to define and initialize any hardcoded tokens in the file"""
        if not self.node_interface.tokens:
            return
        self._pre_function_spacing()
        if self.out.indent("class tokens:"):
            for token_name, token_value in self.node_interface.tokens.items():
                value = json.dumps(token_value)
                self.out.write(f"{token_name} = {value}")
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_attribute_definitions(self):
        """Output the database class member that describes unchanging attribute data"""

        self._pre_function_spacing()
        self.out.write("# This is an internal object that provides per-class storage of a per-node data dictionary")
        self.out.write("PER_NODE_DATA = {}")

        all_attributes = self.node_interface.all_attributes()

        self._pre_function_spacing()
        self.out.write("# This is an internal object that describes unchanging attributes in a generic way")
        self.out.write("# The values in this list are in no particular order, as a per-attribute tuple")
        self.out.write("#     Name, Type, ExtendedTypeIndex, UiName, Description, Metadata,")
        self.out.write("#     Is_Required, DefaultValue, Is_Deprecated, DeprecationMsg")
        self.out.write("# You should not need to access any of this data directly, use the defined database interfaces")
        if self.out.indent("INTERFACE = og.Database._get_interface(["):
            empty_list = [None, None, None, None, None, None, None, None, None, None]
            placeholder = "___PLACEHOLDER___"
            for attribute in all_attributes:
                attribute_data = empty_list[:]
                attribute_data[0] = attribute.name
                (extended_type, type_info) = attribute.python_extended_type()
                attribute_data[1] = attribute.create_type_name() if type_info is None else type_info
                attribute_data[2] = extended_type
                with suppress(KeyError):
                    attribute_data[3] = attribute.metadata[MetadataKeys.UI_NAME]
                with suppress(KeyError):
                    attribute_data[4] = attribute.metadata[MetadataKeys.DESCRIPTION]
                metadata = {}
                for key, value in attribute.metadata.items():
                    if key not in [MetadataKeys.UI_NAME, MetadataKeys.DESCRIPTION]:
                        python_key = MetadataKeyOutput.python_name_from_key(key)
                        if python_key is None:
                            python_key = key
                        metadata[python_key] = value
                attribute_data[5] = metadata
                attribute_data[6] = attribute.is_required
                attribute_data[7] = placeholder
                attribute_data[8] = attribute.is_deprecated
                attribute_data[9] = attribute.deprecation_msg if attribute.is_deprecated else ""
                # Default values could have weird escape requirements that are lost in rendering tuple strings so
                # do a replacement after the fact to make sure they are correct.
                raw_output = f"{tuple(attribute_data)},"
                default_value = attribute.python_value_as_repr(attribute.default)
                raw_output = raw_output.replace(f"'{placeholder}'", default_value)
                # ogn.MetadataKeys is an object name so make sure it is not quoted
                raw_output = re.sub(r'"(ogn.MetadataKeys[^"]*)"', r"\1", raw_output)
                raw_output = re.sub(r"'(ogn.MetadataKeys[^']*)'", r"\1", raw_output)
                self.out.write(raw_output)
            self.out.exdent("])")

    # ----------------------------------------------------------------------
    def _generate_role_definition_method(self):
        """Output the method responsible for initialize the role-based data, if any attributes have roles to set"""
        # Find attributes with non-default roles for output.
        # Dictionary is {NAMESPACED_ATTRIBUTE, ROLE_NAME}
        roles_to_output = {}
        for attribute in self.node_interface.all_attributes():
            role = attribute.python_role_name()
            if role:
                roles_to_output[f"{attribute.namespace}.{attribute.python_property_name()}"] = role

        # Rely on the base class method if no roles were found
        if not roles_to_output:
            return

        self._pre_function_spacing()
        self.out.write("@classmethod")
        if self.out.indent("def _populate_role_data(cls):"):
            self.out.write('"""Populate a role structure with the non-default roles on this node type"""')
            self.out.write("role_data = super()._populate_role_data()")
            for attribute_name, role in roles_to_output.items():
                self.out.write(f"role_data.{attribute_name} = {role}")
            self.out.write("return role_data")
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_attribute_access_help(self):
        """Output the help information describing attribute properties available on this node type"""
        if not self.node_interface.has_attributes():
            return

        def __generate_attribute_access_help(attribute_list: List[AttributeManager]):
            """Output the documentation for a single section of attributes (input/output/state)"""
            if not attribute_list:
                return
            # All attributes are in the same namespace so use the first one to extract its name
            if self.out.indent(f"{attribute_list[0].namespace.capitalize()}:"):
                for attribute in attribute_list:
                    self.out.write(f"{attribute.namespace}.{attribute.python_property_name()}")
                self.out.exdent()

        self.out.write()
        if self.out.indent("Attribute Value Properties:"):
            __generate_attribute_access_help(self.node_interface.all_input_attributes())
            __generate_attribute_access_help(self.node_interface.all_output_attributes())
            __generate_attribute_access_help(self.node_interface.all_state_attributes())
            self.out.exdent()

    # ----------------------------------------------------------------------
    def _generate_database_class(self):
        """Output a class that provides database access for the node's compute method.

        The class has nested class members called "inputs", "outputs", and "state" that make access to attribute values
        more natural:

                inputValue = Node.inputs.InputAttribute
                Node.outputs.OutputAttribute = inputValue * 2
        """
        db_class_name = self.database_class_name()
        self._pre_class_spacing()
        class_definition = f"class {db_class_name}(og.Database):"
        # For internal test nodes we do not care if the database contents are tested so exclude them explicitly
        if self.node_interface.exclude_from_coverage:
            class_definition += "  # pragma: no cover"
        if self.out.indent(class_definition):
            self.out.write(
                f'"""Helper class providing simplified access to data on nodes of type {self.node_interface.name}'
            )
            self.out.write()
            if self.out.indent("Class Members:"):
                self.out.write("node: Node being evaluated")
                self.out.exdent()
            self._generate_attribute_access_help()
            self._generate_token_help()
            self.out.write('"""')

            self._pre_function_spacing()
            self.out.write("# Imprint the generator and target ABI versions in the file for JIT generation")
            self.out.write(f"GENERATOR_VERSION = {self.generator_version}")
            self.out.write(f"TARGET_VERSION = {self.target_version}")

            self._generate_attribute_definitions()
            self._generate_tokens()
            self._generate_role_definition_method()
            input_class_name = self._generate_attribute_class(
                self.node_interface.all_input_attributes(), namespace=INPUT_NS
            )
            output_class_name = self._generate_attribute_class(
                self.node_interface.all_output_attributes(), namespace=OUTPUT_NS
            )
            state_class_name = self._generate_attribute_class(
                self.node_interface.all_state_attributes(), namespace=STATE_NS
            )
            self._pre_function_spacing()
            if self.out.indent("def __init__(self, node):"):
                self.out.write("super().__init__(node)")
                for value_class_name, namespace in [
                    (input_class_name, INPUT_NS),
                    (output_class_name, OUTPUT_NS),
                    (state_class_name, STATE_NS),
                ]:
                    if value_class_name is not None:
                        self.out.write(
                            f"dynamic_attributes = self.dynamic_attribute_data(node, {PORT_NAMES[namespace]})"
                        )
                        self.out.write(
                            f"self.{namespace} = {db_class_name}.{value_class_name}"
                            f"(node, self.attributes.{namespace}, dynamic_attributes)"
                        )
                self.out.exdent()

            # When the node is written in Python there are some helper methods to add
            if self.node_interface.language == LanguageTypeValues.PYTHON:
                self._generate_database_abi()

            # By having the node type class object be a static class member a circular import can be avoided.
            # The node implementation will call OgnTheNodeDatabase.register(OgnTheNode) to handle registration and the
            # automatic override of any ABI methods that OgnTheNode might implement.
            self._generate_node_registration()

            # End of the database
            self.out.exdent()

    # ----------------------------------------------------------------------
    def generate_node_interface(self):
        """Output a Python script containing interface and database support for an OmniGraph node

        Raises:
            NodeGenerationError: When there is a failure in the generation of the Python class
        """
        self.out.write(f'r"""Support for simplified access to data on nodes of type {self.node_interface.name}')
        self.out.write()
        self.out.write(r" __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___")
        self.out.write(r"/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__")
        self.out.write(r"\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___")
        self.out.write()
        self.out.write(r" __   __     .  .  __  ___     .  .  __   __     ___")
        self.out.write(r"|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /")
        self.out.write(r"|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |")
        self.out.write()

        for line in shorten_string_lines_to(self.node_interface.description, 120):
            self.out.write(line)
        self.out.write('"""')
        self.out.write()
        imports_og = [
            "import omni.graph.core as og",
            "import omni.graph.core._omni_graph_core as _og",
            "import omni.graph.tools.ogn as ogn",
        ]
        imports_standard = []
        # Relative icon path resolution requires access to the token interface in Carbonite
        if self.node_interface.icon_path is not None and not Path(self.node_interface.icon_path).is_absolute():
            imports_standard.append("import carb")

        # Python-implemented nodes need access to stack information for compute error reporting
        if self.node_interface.language == LanguageTypeValues.PYTHON:
            imports_standard.append("import sys")
            imports_standard.append("import traceback")

        # Imports required by the attributes
        for attribute in self.node_interface.all_attributes():
            attribute.add_python_imports()
            imports_standard += attribute.imports_standard
            imports_og += attribute.imports_og

        # Sort the imports in the standard order so that the emitted code is consistent
        for import_statement in sorted(set(imports_standard)):
            self.out.write(import_statement)
        self.out.write()
        for import_statement in sorted(set(imports_og)):
            self.out.write(import_statement)
        self.out.write()

        # Both Python and C++ nodes benefit from the use of the Pythonic database class
        self._generate_database_class()


# ======================================================================
def generate_python(configuration: GeneratorConfiguration) -> Optional[str]:
    """Create support files for the pythonic interface to a node

    Args:
        configuration: Information defining how and where the documentation will be generated

    Returns:
        String containing the generated Python database definition or None if its generation was not enabled

    Raises:
        NodeGenerationError: When there is a failure in the generation of the Python database
    """
    if not configuration.node_interface.can_generate("python"):
        return None

    logger.info("Generating Python Database")
    generator = NodePythonGenerator(configuration)
    generator.generate_interface()
    return str(generator.out)
