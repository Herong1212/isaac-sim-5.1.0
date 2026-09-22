r"""Support for simplified access to data on nodes of type omni.graph.ui_nodes.LockViewportRender

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

Locks and unlocks viewport render. Viewport render is frozen at the frame when it is locked, while computation and UI update
are still executed as normal. It fades out back to the current frame when it is unlocked, two output execution attributes
- fadeStarted and fadeComplete - will be triggered separately during the fading progress. The node manages the lock state
for its target viewport and takes action according to the lock state when an input execution attribute is triggered. A node
is able to unlock the target viewort only if it has locked the target viewport.
"""

import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnLockViewportRenderDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.graph.ui_nodes.LockViewportRender

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.fadeTime
            inputs.lock
            inputs.unlock
            inputs.viewport
        Outputs:
            outputs.fadeComplete
            outputs.fadeStarted
            outputs.locked
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
        ('inputs:fadeTime', 'double', 0, 'Fade Time', 'The duration of fading in time (seconds) when being unlocked', {ogn.MetadataKeys.DEFAULT: '1.0'}, True, 1.0, False, ''),
        ('inputs:lock', 'execution', 0, None, 'Signal to the graph that this node is ready to be executed for locking the viewport render.', {}, True, None, False, ''),
        ('inputs:unlock', 'execution', 0, None, 'Signal to the graph that this node is ready to be executed for unlocking the viewport render.', {}, True, None, False, ''),
        ('inputs:viewport', 'token', 0, 'Viewport', 'Name of the viewport, or empty for the default viewport', {ogn.MetadataKeys.DEFAULT: '""'}, True, "", False, ''),
        ('outputs:fadeComplete', 'execution', 0, None, 'When fading is complete, signal to the graph that execution can continue downstream on this path.', {}, True, None, False, ''),
        ('outputs:fadeStarted', 'execution', 0, None, 'When fading is started, signal to the graph that execution can continue downstream on this path.', {}, True, None, False, ''),
        ('outputs:locked', 'execution', 0, None, 'When viewport render is locked, signal to the graph that execution can continue downstream on this path.', {}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.lock = og.AttributeRole.EXECUTION
        role_data.inputs.unlock = og.AttributeRole.EXECUTION
        role_data.outputs.fadeComplete = og.AttributeRole.EXECUTION
        role_data.outputs.fadeStarted = og.AttributeRole.EXECUTION
        role_data.outputs.locked = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"fadeTime", "lock", "unlock", "viewport", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.fadeTime, self._attributes.lock, self._attributes.unlock, self._attributes.viewport]
            self._batchedReadValues = [1.0, None, None, ""]

        @property
        def fadeTime(self):
            return self._batchedReadValues[0]

        @fadeTime.setter
        def fadeTime(self, value):
            self._batchedReadValues[0] = value

        @property
        def lock(self):
            return self._batchedReadValues[1]

        @lock.setter
        def lock(self, value):
            self._batchedReadValues[1] = value

        @property
        def unlock(self):
            return self._batchedReadValues[2]

        @unlock.setter
        def unlock(self, value):
            self._batchedReadValues[2] = value

        @property
        def viewport(self):
            return self._batchedReadValues[3]

        @viewport.setter
        def viewport(self, value):
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
        LOCAL_PROPERTY_NAMES = {"fadeComplete", "fadeStarted", "locked", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedWriteValues = { }

        @property
        def fadeComplete(self):
            value = self._batchedWriteValues.get(self._attributes.fadeComplete)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.fadeComplete)
                return data_view.get()

        @fadeComplete.setter
        def fadeComplete(self, value):
            self._batchedWriteValues[self._attributes.fadeComplete] = value

        @property
        def fadeStarted(self):
            value = self._batchedWriteValues.get(self._attributes.fadeStarted)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.fadeStarted)
                return data_view.get()

        @fadeStarted.setter
        def fadeStarted(self, value):
            self._batchedWriteValues[self._attributes.fadeStarted] = value

        @property
        def locked(self):
            value = self._batchedWriteValues.get(self._attributes.locked)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.locked)
                return data_view.get()

        @locked.setter
        def locked(self, value):
            self._batchedWriteValues[self._attributes.locked] = value

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
        self.inputs = OgnLockViewportRenderDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnLockViewportRenderDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnLockViewportRenderDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnLockViewportRenderDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.graph.ui_nodes.LockViewportRender'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnLockViewportRenderDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnLockViewportRenderDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnLockViewportRenderDatabase(node)

            try:
                compute_function = getattr(OgnLockViewportRenderDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnLockViewportRenderDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnLockViewportRenderDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnLockViewportRenderDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnLockViewportRenderDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnLockViewportRenderDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnLockViewportRenderDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnLockViewportRenderDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnLockViewportRenderDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnLockViewportRenderDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnLockViewportRenderDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnLockViewportRenderDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnLockViewportRenderDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.graph.ui_nodes")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Lock Viewport Render")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "graph:action,viewport")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "Locks and unlocks viewport render. Viewport render is frozen at the frame when it is locked, while computation and UI update are still executed as normal. It fades out back to the current frame when it is unlocked, two output execution attributes - fadeStarted and fadeComplete - will be triggered separately during the fading progress. The node manages the lock state for its target viewport and takes action according to the lock state when an input execution attribute is triggered. A node is able to unlock the target viewort only if it has locked the target viewport.")
                node_type.set_metadata(ogn.MetadataKeys.EXCLUSIONS, "tests")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                OgnLockViewportRenderDatabase.INTERFACE.add_to_node_type(node_type)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnLockViewportRenderDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnLockViewportRenderDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnLockViewportRenderDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.graph.ui_nodes.LockViewportRender")
