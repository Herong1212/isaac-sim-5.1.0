r"""Support for simplified access to data on nodes of type omni.replicator.core.OgnCameraRelativePosition

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

Convert camera relative position to world position.
"""

import numpy
import sys
import traceback
import usdrt

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnCameraRelativePositionDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.OgnCameraRelativePosition

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.cameraPrim
            inputs.distance
            inputs.execIn
            inputs.height
            inputs.horizontalLocation
            inputs.numSamples
            inputs.verticalLocation
            inputs.width
        Outputs:
            outputs.execOut
            outputs.samples
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
        ('inputs:cameraPrim', 'target', 0, None, 'Prims will be positioned relative to this camera', {}, True, None, False, ''),
        ('inputs:distance', 'float[]', 0, None, 'Distance from the prim(s) to the camera', {}, True, [], False, ''),
        ('inputs:execIn', 'execution', 0, None, 'exec', {}, True, None, False, ''),
        ('inputs:height', 'int', 0, None, 'Height of the render product', {}, True, 0, False, ''),
        ('inputs:horizontalLocation', 'float[]', 0, None, 'Horizontal location in the camera frame, which is in the range of [-1, 1]', {}, True, [], False, ''),
        ('inputs:numSamples', 'int', 0, None, 'Number of samples', {}, True, 0, False, ''),
        ('inputs:verticalLocation', 'float[]', 0, None, 'Vertical location in the camera frame, which is in the range of [-1, 1]', {}, True, [], False, ''),
        ('inputs:width', 'int', 0, None, 'Width of the render product', {}, True, 0, False, ''),
        ('outputs:execOut', 'execution', 0, None, 'exec', {}, True, None, False, ''),
        ('outputs:samples', 'double3[]', 0, None, 'New positions of each prim in the world space', {}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.cameraPrim = og.AttributeRole.TARGET
        role_data.inputs.execIn = og.AttributeRole.EXECUTION
        role_data.outputs.execOut = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"execIn", "height", "numSamples", "width", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.execIn, self._attributes.height, self._attributes.numSamples, self._attributes.width]
            self._batchedReadValues = [None, 0, 0, 0]

        @property
        def cameraPrim(self):
            data_view = og.AttributeValueHelper(self._attributes.cameraPrim)
            return data_view.get()

        @cameraPrim.setter
        def cameraPrim(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.cameraPrim)
            data_view = og.AttributeValueHelper(self._attributes.cameraPrim)
            data_view.set(value)
            self.cameraPrim_size = data_view.get_array_size()

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
        def horizontalLocation(self):
            data_view = og.AttributeValueHelper(self._attributes.horizontalLocation)
            return data_view.get()

        @horizontalLocation.setter
        def horizontalLocation(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.horizontalLocation)
            data_view = og.AttributeValueHelper(self._attributes.horizontalLocation)
            data_view.set(value)
            self.horizontalLocation_size = data_view.get_array_size()

        @property
        def verticalLocation(self):
            data_view = og.AttributeValueHelper(self._attributes.verticalLocation)
            return data_view.get()

        @verticalLocation.setter
        def verticalLocation(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.verticalLocation)
            data_view = og.AttributeValueHelper(self._attributes.verticalLocation)
            data_view.set(value)
            self.verticalLocation_size = data_view.get_array_size()

        @property
        def execIn(self):
            return self._batchedReadValues[0]

        @execIn.setter
        def execIn(self, value):
            self._batchedReadValues[0] = value

        @property
        def height(self):
            return self._batchedReadValues[1]

        @height.setter
        def height(self, value):
            self._batchedReadValues[1] = value

        @property
        def numSamples(self):
            return self._batchedReadValues[2]

        @numSamples.setter
        def numSamples(self, value):
            self._batchedReadValues[2] = value

        @property
        def width(self):
            return self._batchedReadValues[3]

        @width.setter
        def width(self, value):
            self._batchedReadValues[3] = value

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
        LOCAL_PROPERTY_NAMES = {"execOut", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self.samples_size = None
            self._batchedWriteValues = { }

        @property
        def samples(self):
            data_view = og.AttributeValueHelper(self._attributes.samples)
            return data_view.get(reserved_element_count=self.samples_size)

        @samples.setter
        def samples(self, value):
            data_view = og.AttributeValueHelper(self._attributes.samples)
            data_view.set(value)
            self.samples_size = data_view.get_array_size()

        @property
        def execOut(self):
            value = self._batchedWriteValues.get(self._attributes.execOut)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.execOut)
                return data_view.get()

        @execOut.setter
        def execOut(self, value):
            self._batchedWriteValues[self._attributes.execOut] = value

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
        self.inputs = OgnCameraRelativePositionDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnCameraRelativePositionDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnCameraRelativePositionDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.OgnCameraRelativePosition'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnCameraRelativePositionDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnCameraRelativePositionDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnCameraRelativePositionDatabase(node)

            try:
                compute_function = getattr(OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnCameraRelativePositionDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnCameraRelativePositionDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnCameraRelativePositionDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnCameraRelativePositionDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnCameraRelativePositionDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Camera Relative Position")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "Replicator:Core")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORY_DESCRIPTIONS, "Replicator:Core,Core Replicator nodes")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "Convert camera relative position to world position.")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                __hints = node_type.get_scheduling_hints()
                if __hints is not None:
                    __hints.compute_rule = og.eComputeRule.E_ON_REQUEST
                OgnCameraRelativePositionDatabase.INTERFACE.add_to_node_type(node_type)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnCameraRelativePositionDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnCameraRelativePositionDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.OgnCameraRelativePosition")
