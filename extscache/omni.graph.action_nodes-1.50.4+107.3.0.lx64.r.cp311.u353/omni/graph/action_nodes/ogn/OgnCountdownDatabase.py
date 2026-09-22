r"""Support for simplified access to data on nodes of type omni.graph.action.Countdown

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

This type of node will activate when 'Exec In' is first set and will remain active for a total of 'Duration' ticks, where
a 'tick' is an execution of the node. Every 'Period' ticks the output 'Tick' will activate and after the final tick 'Finished'
will activate.
For example if 'Duration' is set to 10 and 'Period' is set to 3 then after activation the 'Tick' signal will
activate after 3, 6, and 9 executions, and 'Finished' will activate after the 10th.
If 'Exec In' is activated again before
the current countdown has finished, the countdown will be reset to the start.
The first execution is considered number 0
and does not generate an activation signal.
"""

import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnCountdownDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.graph.action.Countdown

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.duration
            inputs.execIn
            inputs.period
        Outputs:
            outputs.alpha
            outputs.finished
            outputs.tick
            outputs.tickValue
        State:
            state.count
    """

    # Imprint the generator and target ABI versions in the file for JIT generation
    GENERATOR_VERSION = (1, 79, 2)
    TARGET_VERSION = (2, 184, 2)

    # This is an internal object that provides per-class storage of a per-node data dictionary
    PER_NODE_DATA = {}

    # This is an internal object that describes unchanging attributes in a generic way
    # The values in this list are in no particular order, as a per-attribute tuple
    #     Name, Type, ExtendedTypeIndex, UiName, Description, Metadata,
    #     Is_Required, DefaultValue, Is_Deprecated, DeprecationMsg
    # You should not need to access any of this data directly, use the defined database interfaces
    INTERFACE = og.Database._get_interface([
        ('inputs:duration', 'int', 0, None, 'The duration of the delay in ticks.', {ogn.MetadataKeys.DEFAULT: '5'}, True, 5, False, ''),
        ('inputs:execIn', 'execution', 0, None, 'Signal to the graph that this node is ready to be executed.', {}, True, None, False, ''),
        ('inputs:period', 'int', 0, None, 'The period of the pulse in ticks.', {ogn.MetadataKeys.DEFAULT: '1'}, True, 1, False, ''),
        ('outputs:alpha', 'float', 0, None, "On first execution this is set to 0, indicating that there is no progress on the countdown.\nFor every subsequent execution it is set to the normalized progress of the countdown as a value\nbetween 0 and 1 computed as 'Tick Value'/'Duration'. After the countdown is complete it keeps\na value of 1 until the next time the countdown is reset by activating 'Exec In'.", {}, True, None, False, ''),
        ('outputs:finished', 'execution', 0, None, "After 'Duration' ticks of this node have completed since 'Exec In' was activated\nsignal the graph that execution can continue downstream.", {}, True, None, False, ''),
        ('outputs:tick', 'execution', 0, None, "Every 'Period' ticks after 'Exec In' has been activated signal the graph\nthat execution can continue downstream.", {}, True, None, False, ''),
        ('outputs:tickValue', 'int', 0, None, "The current tick value, active in the range [1, 'Duration'].", {}, True, None, False, ''),
        ('state:count', 'int', 0, None, 'The number of ticks elapsed. The first tick is 0. A value of -1 means execution has not yet\nbeen activated.', {ogn.MetadataKeys.DEFAULT: '-1'}, True, -1, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.execIn = og.AttributeRole.EXECUTION
        role_data.outputs.finished = og.AttributeRole.EXECUTION
        role_data.outputs.tick = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"duration", "execIn", "period", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.duration, self._attributes.execIn, self._attributes.period]
            self._batchedReadValues = [5, None, 1]

        @property
        def duration(self):
            return self._batchedReadValues[0]

        @duration.setter
        def duration(self, value):
            self._batchedReadValues[0] = value

        @property
        def execIn(self):
            return self._batchedReadValues[1]

        @execIn.setter
        def execIn(self, value):
            self._batchedReadValues[1] = value

        @property
        def period(self):
            return self._batchedReadValues[2]

        @period.setter
        def period(self, value):
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
        LOCAL_PROPERTY_NAMES = {"alpha", "finished", "tick", "tickValue", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedWriteValues = { }

        @property
        def alpha(self):
            value = self._batchedWriteValues.get(self._attributes.alpha)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.alpha)
                return data_view.get()

        @alpha.setter
        def alpha(self, value):
            self._batchedWriteValues[self._attributes.alpha] = value

        @property
        def finished(self):
            value = self._batchedWriteValues.get(self._attributes.finished)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.finished)
                return data_view.get()

        @finished.setter
        def finished(self, value):
            self._batchedWriteValues[self._attributes.finished] = value

        @property
        def tick(self):
            value = self._batchedWriteValues.get(self._attributes.tick)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.tick)
                return data_view.get()

        @tick.setter
        def tick(self, value):
            self._batchedWriteValues[self._attributes.tick] = value

        @property
        def tickValue(self):
            value = self._batchedWriteValues.get(self._attributes.tickValue)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.tickValue)
                return data_view.get()

        @tickValue.setter
        def tickValue(self, value):
            self._batchedWriteValues[self._attributes.tickValue] = value

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

        @property
        def count(self):
            data_view = og.AttributeValueHelper(self._attributes.count)
            return data_view.get()

        @count.setter
        def count(self, value):
            data_view = og.AttributeValueHelper(self._attributes.count)
            data_view.set(value)

    def __init__(self, node):
        super().__init__(node)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT)
        self.inputs = OgnCountdownDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnCountdownDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnCountdownDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnCountdownDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.graph.action.Countdown'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnCountdownDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnCountdownDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnCountdownDatabase(node)

            try:
                compute_function = getattr(OgnCountdownDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnCountdownDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnCountdownDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnCountdownDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnCountdownDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnCountdownDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnCountdownDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnCountdownDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnCountdownDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnCountdownDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnCountdownDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnCountdownDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnCountdownDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.graph.action_nodes")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Countdown")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "graph:action,flowControl")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "This type of node will activate when 'Exec In' is first set and will remain active for a total of 'Duration' ticks, where a 'tick' is an execution of the node. Every 'Period' ticks the output 'Tick' will activate and after the final tick 'Finished' will activate.\nFor example if 'Duration' is set to 10 and 'Period' is set to 3 then after activation the 'Tick' signal will activate after 3, 6, and 9 executions, and 'Finished' will activate after the 10th.\nIf 'Exec In' is activated again before the current countdown has finished, the countdown will be reset to the start.\nThe first execution is considered number 0 and does not generate an activation signal.")
                node_type.set_metadata(ogn.MetadataKeys.EXCLUSIONS, "tests")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                OgnCountdownDatabase.INTERFACE.add_to_node_type(node_type)
                node_type.set_has_state(True)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnCountdownDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnCountdownDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnCountdownDatabase.abi, 2)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.graph.action.Countdown")
