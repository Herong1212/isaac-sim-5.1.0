r"""Support for simplified access to data on nodes of type omni.replicator.core.OgnOrbit

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

Compute prim position in the form of an orbit around a central point.
"""

import numpy
import sys
import traceback
import usdrt

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnOrbitDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.OgnOrbit

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.azimuth
            inputs.barycentreCoordinates
            inputs.barycentreMode
            inputs.barycentrePrim
            inputs.distance
            inputs.elevation
            inputs.exec
            inputs.prims
        Outputs:
            outputs.exec
            outputs.values

    Predefined Tokens:
        tokens.Prim
        tokens.Coordinates
    """

    # Imprint the generator and target ABI versions in the file for JIT generation
    GENERATOR_VERSION = (1, 79, 2)
    TARGET_VERSION = (2, 184, 5)

    # This is an internal object that provides per-class storage of a per-node data dictionary
    PER_NODE_DATA = {}

    # This is an internal object that describes unchanging attributes in a generic way
    # The values in this list are in no particular order, as a per-attribute tuple
    #     Name, Type, ExtendedTypeIndex, UiName, Description, Metadata,
    #     Is_Required, DefaultValue, Is_Deprecated, DeprecationMsg
    # You should not need to access any of this data directly, use the defined database interfaces
    INTERFACE = og.Database._get_interface([
        ('inputs:azimuth', 'float[]', 0, None, 'Horizontal angle in degrees.', {}, True, [], False, ''),
        ('inputs:barycentreCoordinates', 'float3', 0, None, 'The barycentre position expressed in (x, y, z) coordinates.', {}, True, [0.0, 0.0, 0.0], False, ''),
        ('inputs:barycentreMode', 'token', 0, None, 'Determine whether to use barycentrePrim or barycentreCoordinates as the orbit barycentre.', {'displayGroup': 'parameters', ogn.MetadataKeys.LITERAL_ONLY: '1', ogn.MetadataKeys.ALLOWED_TOKENS: 'Prim,Coordinates', ogn.MetadataKeys.ALLOWED_TOKENS_RAW: '["Prim", "Coordinates"]'}, True, "", False, ''),
        ('inputs:barycentrePrim', 'target', 0, None, 'The barycentre prim that the prims will orbit around', {}, True, None, False, ''),
        ('inputs:distance', 'float[]', 0, None, 'Distance from barycentre.', {}, True, [], False, ''),
        ('inputs:elevation', 'float[]', 0, None, 'Vertical angle in degrees.', {}, True, [], False, ''),
        ('inputs:exec', 'execution', 0, None, 'exec', {}, True, None, False, ''),
        ('inputs:prims', 'target', 0, None, 'The prims orbit position is to be computed', {}, True, None, False, ''),
        ('outputs:exec', 'execution', 0, None, 'exec', {}, True, None, False, ''),
        ('outputs:values', 'double3[]', 0, None, 'Position values of prims orbiting around a barycentre point.', {}, True, None, False, ''),
    ])

    class tokens:
        Prim = "Prim"
        Coordinates = "Coordinates"

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.barycentrePrim = og.AttributeRole.TARGET
        role_data.inputs.exec = og.AttributeRole.EXECUTION
        role_data.inputs.prims = og.AttributeRole.TARGET
        role_data.outputs.exec = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"barycentreCoordinates", "barycentreMode", "exec", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.barycentreCoordinates, self._attributes.barycentreMode, self._attributes.exec]
            self._batchedReadValues = [[0.0, 0.0, 0.0], "", None]

        @property
        def azimuth(self):
            data_view = og.AttributeValueHelper(self._attributes.azimuth)
            return data_view.get()

        @azimuth.setter
        def azimuth(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.azimuth)
            data_view = og.AttributeValueHelper(self._attributes.azimuth)
            data_view.set(value)
            self.azimuth_size = data_view.get_array_size()

        @property
        def barycentrePrim(self):
            data_view = og.AttributeValueHelper(self._attributes.barycentrePrim)
            return data_view.get()

        @barycentrePrim.setter
        def barycentrePrim(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.barycentrePrim)
            data_view = og.AttributeValueHelper(self._attributes.barycentrePrim)
            data_view.set(value)
            self.barycentrePrim_size = data_view.get_array_size()

        @property
        def distance(self):
            data_view = og.AttributeValueHelper(self._attributes.distance)
            return data_view.get()

        @distance.setter
        def distance(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.distance)
            data_view = og.AttributeValueHelper(self._attributes.distance)
            data_view.set(value)
            self.distance_size = data_view.get_array_size()

        @property
        def elevation(self):
            data_view = og.AttributeValueHelper(self._attributes.elevation)
            return data_view.get()

        @elevation.setter
        def elevation(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.elevation)
            data_view = og.AttributeValueHelper(self._attributes.elevation)
            data_view.set(value)
            self.elevation_size = data_view.get_array_size()

        @property
        def prims(self):
            data_view = og.AttributeValueHelper(self._attributes.prims)
            return data_view.get()

        @prims.setter
        def prims(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.prims)
            data_view = og.AttributeValueHelper(self._attributes.prims)
            data_view.set(value)
            self.prims_size = data_view.get_array_size()

        @property
        def barycentreCoordinates(self):
            return self._batchedReadValues[0]

        @barycentreCoordinates.setter
        def barycentreCoordinates(self, value):
            self._batchedReadValues[0] = value

        @property
        def barycentreMode(self):
            return self._batchedReadValues[1]

        @barycentreMode.setter
        def barycentreMode(self, value):
            self._batchedReadValues[1] = value

        @property
        def exec(self):
            return self._batchedReadValues[2]

        @exec.setter
        def exec(self, value):
            self._batchedReadValues[2] = value

        def __getattr__(self, item: str):
            if item in self.LOCAL_PROPERTY_NAMES:
                return object.__getattribute__(self, item)
            else:
                return super().__getattr__(item)

        def __setattr__(self, item: str, new_value):
            if item in self.LOCAL_PROPERTY_NAMES:
                object.__setattr__(self, item, new_value)
            else:
                super().__setattr__(item, new_value)

        def _prefetch(self):
            readAttributes = self._batchedReadAttributes
            newValues = _og._prefetch_input_attributes_data(readAttributes)
            if len(readAttributes) == len(newValues):
                self._batchedReadValues = newValues

    class ValuesForOutputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"exec", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self.values_size = None
            self._batchedWriteValues = { }

        @property
        def values(self):
            data_view = og.AttributeValueHelper(self._attributes.values)
            return data_view.get(reserved_element_count=self.values_size)

        @values.setter
        def values(self, value):
            data_view = og.AttributeValueHelper(self._attributes.values)
            data_view.set(value)
            self.values_size = data_view.get_array_size()

        @property
        def exec(self):
            value = self._batchedWriteValues.get(self._attributes.exec)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.exec)
                return data_view.get()

        @exec.setter
        def exec(self, value):
            self._batchedWriteValues[self._attributes.exec] = value

        def __getattr__(self, item: str):
            if item in self.LOCAL_PROPERTY_NAMES:
                return object.__getattribute__(self, item)
            else:
                return super().__getattr__(item)

        def __setattr__(self, item: str, new_value):
            if item in self.LOCAL_PROPERTY_NAMES:
                object.__setattr__(self, item, new_value)
            else:
                super().__setattr__(item, new_value)

        def _commit(self):
            _og._commit_output_attributes_data(self._batchedWriteValues)
            self._batchedWriteValues = { }

    class ValuesForState(og.DynamicAttributeAccess):
        """Helper class that creates natural hierarchical access to state attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)

    def __init__(self, node):
        super().__init__(node)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT)
        self.inputs = OgnOrbitDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnOrbitDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnOrbitDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnOrbitDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.OgnOrbit'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnOrbitDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnOrbitDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnOrbitDatabase(node)

            try:
                compute_function = getattr(OgnOrbitDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnOrbitDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnOrbitDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnOrbitDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnOrbitDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnOrbitDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnOrbitDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnOrbitDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnOrbitDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnOrbitDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnOrbitDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnOrbitDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnOrbitDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Compute Orbit Position")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "Replicator")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORY_DESCRIPTIONS, "Replicator,Orbit")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "Compute prim position in the form of an orbit around a central point.")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                OgnOrbitDatabase.INTERFACE.add_to_node_type(node_type)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnOrbitDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnOrbitDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnOrbitDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.OgnOrbit")
