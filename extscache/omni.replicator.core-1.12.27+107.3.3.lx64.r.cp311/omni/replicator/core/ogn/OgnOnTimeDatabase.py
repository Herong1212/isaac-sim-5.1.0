r"""Support for simplified access to data on nodes of type omni.replicator.core.OgnOnTime

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

Triggers at the specified time interval. Note that the graph will run asynchronously to the new frame event
"""

import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnOnTimeDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.OgnOnTime

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.interval
            inputs.maxExecs
            inputs.resetPhysics
            inputs.rtSubframes
            inputs.run
            inputs.triggerOnLastFrame
        Outputs:
            outputs.execCounts
            outputs.execOut
            outputs.referenceTimeDenominator
            outputs.referenceTimeNumerator
            outputs.time
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
        ('inputs:interval', 'float', 0, None, 'Trigger interval, in seconds.', {ogn.MetadataKeys.DEFAULT: '1'}, True, 1, False, ''),
        ('inputs:maxExecs', 'uint', 0, None, 'Number of sequences triggered before stopping. If 0, continue indefinitely.', {ogn.MetadataKeys.DEFAULT: '0'}, True, 0, False, ''),
        ('inputs:resetPhysics', 'bool', 0, None, 'If True, reset physics simulation on trigger.', {ogn.MetadataKeys.DEFAULT: 'true'}, True, True, False, ''),
        ('inputs:rtSubframes', 'uint64', 0, None, 'Determines how many subframes to render in RealTime render mode on each trigger\nto reduce artifacts caused by sudden scene changes.', {ogn.MetadataKeys.DEFAULT: '16'}, True, 16, False, ''),
        ('inputs:run', 'bool', 0, None, 'Run', {}, True, False, False, ''),
        ('inputs:triggerOnLastFrame', 'bool', 0, None, 'If True, trigger on the frame before the interval time is reached.', {ogn.MetadataKeys.DEFAULT: 'false'}, True, False, False, ''),
        ('outputs:execCounts', 'int', 0, None, 'The number of times the trigger has executed.', {}, True, None, False, ''),
        ('outputs:execOut', 'execution', 0, None, 'Output Execution', {}, True, None, False, ''),
        ('outputs:referenceTimeDenominator', 'uint64', 0, None, 'Reference time represented as a rational number : denominator', {}, True, None, False, ''),
        ('outputs:referenceTimeNumerator', 'int64', 0, None, 'Reference time represented as a rational number : numerator', {}, True, None, False, ''),
        ('outputs:time', 'int', 0, None, 'The current physx simulation time.', {}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.outputs.execOut = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"interval", "maxExecs", "resetPhysics", "rtSubframes", "run", "triggerOnLastFrame", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.interval, self._attributes.maxExecs, self._attributes.resetPhysics, self._attributes.rtSubframes, self._attributes.run, self._attributes.triggerOnLastFrame]
            self._batchedReadValues = [1, 0, True, 16, False, False]

        @property
        def interval(self):
            return self._batchedReadValues[0]

        @interval.setter
        def interval(self, value):
            self._batchedReadValues[0] = value

        @property
        def maxExecs(self):
            return self._batchedReadValues[1]

        @maxExecs.setter
        def maxExecs(self, value):
            self._batchedReadValues[1] = value

        @property
        def resetPhysics(self):
            return self._batchedReadValues[2]

        @resetPhysics.setter
        def resetPhysics(self, value):
            self._batchedReadValues[2] = value

        @property
        def rtSubframes(self):
            return self._batchedReadValues[3]

        @rtSubframes.setter
        def rtSubframes(self, value):
            self._batchedReadValues[3] = value

        @property
        def run(self):
            return self._batchedReadValues[4]

        @run.setter
        def run(self, value):
            self._batchedReadValues[4] = value

        @property
        def triggerOnLastFrame(self):
            return self._batchedReadValues[5]

        @triggerOnLastFrame.setter
        def triggerOnLastFrame(self, value):
            self._batchedReadValues[5] = value

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
        LOCAL_PROPERTY_NAMES = {"execCounts", "execOut", "referenceTimeDenominator", "referenceTimeNumerator", "time", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedWriteValues = { }

        @property
        def execCounts(self):
            value = self._batchedWriteValues.get(self._attributes.execCounts)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.execCounts)
                return data_view.get()

        @execCounts.setter
        def execCounts(self, value):
            self._batchedWriteValues[self._attributes.execCounts] = value

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

        @property
        def referenceTimeDenominator(self):
            value = self._batchedWriteValues.get(self._attributes.referenceTimeDenominator)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.referenceTimeDenominator)
                return data_view.get()

        @referenceTimeDenominator.setter
        def referenceTimeDenominator(self, value):
            self._batchedWriteValues[self._attributes.referenceTimeDenominator] = value

        @property
        def referenceTimeNumerator(self):
            value = self._batchedWriteValues.get(self._attributes.referenceTimeNumerator)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.referenceTimeNumerator)
                return data_view.get()

        @referenceTimeNumerator.setter
        def referenceTimeNumerator(self, value):
            self._batchedWriteValues[self._attributes.referenceTimeNumerator] = value

        @property
        def time(self):
            value = self._batchedWriteValues.get(self._attributes.time)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.time)
                return data_view.get()

        @time.setter
        def time(self, value):
            self._batchedWriteValues[self._attributes.time] = value

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
        self.inputs = OgnOnTimeDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnOnTimeDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnOnTimeDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnOnTimeDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.OgnOnTime'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnOnTimeDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnOnTimeDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnOnTimeDatabase(node)

            try:
                compute_function = getattr(OgnOnTimeDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnOnTimeDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnOnTimeDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnOnTimeDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnOnTimeDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnOnTimeDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnOnTimeDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnOnTimeDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnOnTimeDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnOnTimeDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnOnTimeDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnOnTimeDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnOnTimeDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "On Time")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "Replicator:Core")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORY_DESCRIPTIONS, "Replicator:Core,Core Replicator nodes")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "Triggers at the specified time interval. Note that the graph will run asynchronously to the new frame event")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                __hints = node_type.get_scheduling_hints()
                if __hints is not None:
                    __hints.compute_rule = og.eComputeRule.E_ON_REQUEST
                OgnOnTimeDatabase.INTERFACE.add_to_node_type(node_type)
                node_type.set_has_state(True)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnOnTimeDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnOnTimeDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnOnTimeDatabase.abi, 3)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.OgnOnTime")
