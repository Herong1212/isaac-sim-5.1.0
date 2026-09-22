r"""Support for simplified access to data on nodes of type omni.graph.ui_nodes.SetViewportMode

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

Sets the mode of a specified viewport window to 'Scripted' mode or 'Default' mode when executed.
'Scripted' mode disables
default viewport interaction and enables placing UI elements over the viewport. 'Default' mode is the default state of the
viewport, and entering it will destroy any UI elements on the viewport.
Executing with 'Enable Viewport Mouse Events' set
to true in 'Scripted' mode is required to allow the specified viewport to be targeted by viewport mouse event nodes, including
'On Viewport Dragged' and 'Read Viewport Drag State'.
Executing with 'Enable Picking' set to true in 'Scripted' mode is required
to allow the specified viewport to be targeted by the 'On Picked' and 'Read Pick State' nodes.
"""

import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnSetViewportModeDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.graph.ui_nodes.SetViewportMode

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.enablePicking
            inputs.enableViewportMouseEvents
            inputs.execIn
            inputs.mode
            inputs.passClicksThru
            inputs.viewport
        Outputs:
            outputs.defaultMode
            outputs.scriptedMode
            outputs.widgetPath
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
        ('inputs:enablePicking', 'bool', 0, 'Enable Picking', "Enable/Disable picking prims in the specified viewport when in 'Scripted' mode", {ogn.MetadataKeys.DEFAULT: 'false'}, True, False, False, ''),
        ('inputs:enableViewportMouseEvents', 'bool', 0, 'Enable Viewport Mouse Events', "Enable/Disable viewport mouse events on the specified viewport when in 'Scripted' mode", {ogn.MetadataKeys.DEFAULT: 'false'}, True, False, False, ''),
        ('inputs:execIn', 'execution', 0, None, 'Signal to the graph that this node is ready to be executed.', {}, True, None, False, ''),
        ('inputs:mode', 'int', 0, 'Mode', "The mode to set the specified viewport to when this node is executed (0: 'Default', 1: 'Scripted')", {ogn.MetadataKeys.DEFAULT: '0'}, True, 0, False, ''),
        ('inputs:passClicksThru', 'bool', 0, 'Pass Clicks Thru', "Allow mouse clicks to affect the viewport while in 'Scripted' mode.\n\nIn 'Scripted' mode mouse clicks are prevented from reaching the viewport to avoid accidentally\nselecting prims or interacting with the viewport's own UI. Setting this attribute true will\nallow clicks to reach the viewport. This is in addition to interacting with the widgets created\nby UI nodes so if a button widget appears on top of some geometry in the viewport, clicking on\nthe button will not only trigger the button but could also select the geometry. To avoid this,\nput the button inside a Stack widget and use a WriteWidgetProperty node to set the Stack's\n'content_clipping' property to 1.", {ogn.MetadataKeys.DEFAULT: 'false'}, True, False, False, ''),
        ('inputs:viewport', 'token', 0, 'Viewport', 'Name of the viewport window to set the mode of', {ogn.MetadataKeys.DEFAULT: '"Viewport"'}, True, "Viewport", False, ''),
        ('outputs:defaultMode', 'execution', 0, 'Default Mode', "When this node is successfully executed with 'Mode' set to 'Default',\nsignal to the graph that execution can continue downstream on this path.", {}, True, None, False, ''),
        ('outputs:scriptedMode', 'execution', 0, 'Scripted Mode', "When this node is successfully executed with 'Mode' set to 'Scripted',\nsignal to the graph that execution can continue downstream on this path.", {}, True, None, False, ''),
        ('outputs:widgetPath', 'token', 0, 'Widget Path', "When the viewport enters 'Scripted' mode, a container widget is created under which other UI may be parented.\nThis attribute provides the absolute path to that widget, which can be used as the 'parentWidgetPath'\ninput to various UI nodes, such as Button. When the viewport exits 'Scripted' mode,\nthe container widget and all the UI within it will be destroyed.", {}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.execIn = og.AttributeRole.EXECUTION
        role_data.outputs.defaultMode = og.AttributeRole.EXECUTION
        role_data.outputs.scriptedMode = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"enablePicking", "enableViewportMouseEvents", "execIn", "mode", "passClicksThru", "viewport", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.enablePicking, self._attributes.enableViewportMouseEvents, self._attributes.execIn, self._attributes.mode, self._attributes.passClicksThru, self._attributes.viewport]
            self._batchedReadValues = [False, False, None, 0, False, "Viewport"]

        @property
        def enablePicking(self):
            return self._batchedReadValues[0]

        @enablePicking.setter
        def enablePicking(self, value):
            self._batchedReadValues[0] = value

        @property
        def enableViewportMouseEvents(self):
            return self._batchedReadValues[1]

        @enableViewportMouseEvents.setter
        def enableViewportMouseEvents(self, value):
            self._batchedReadValues[1] = value

        @property
        def execIn(self):
            return self._batchedReadValues[2]

        @execIn.setter
        def execIn(self, value):
            self._batchedReadValues[2] = value

        @property
        def mode(self):
            return self._batchedReadValues[3]

        @mode.setter
        def mode(self, value):
            self._batchedReadValues[3] = value

        @property
        def passClicksThru(self):
            return self._batchedReadValues[4]

        @passClicksThru.setter
        def passClicksThru(self, value):
            self._batchedReadValues[4] = value

        @property
        def viewport(self):
            return self._batchedReadValues[5]

        @viewport.setter
        def viewport(self, value):
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
        LOCAL_PROPERTY_NAMES = {"defaultMode", "scriptedMode", "widgetPath", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedWriteValues = { }

        @property
        def defaultMode(self):
            value = self._batchedWriteValues.get(self._attributes.defaultMode)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.defaultMode)
                return data_view.get()

        @defaultMode.setter
        def defaultMode(self, value):
            self._batchedWriteValues[self._attributes.defaultMode] = value

        @property
        def scriptedMode(self):
            value = self._batchedWriteValues.get(self._attributes.scriptedMode)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.scriptedMode)
                return data_view.get()

        @scriptedMode.setter
        def scriptedMode(self, value):
            self._batchedWriteValues[self._attributes.scriptedMode] = value

        @property
        def widgetPath(self):
            value = self._batchedWriteValues.get(self._attributes.widgetPath)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.widgetPath)
                return data_view.get()

        @widgetPath.setter
        def widgetPath(self, value):
            self._batchedWriteValues[self._attributes.widgetPath] = value

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
        self.inputs = OgnSetViewportModeDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnSetViewportModeDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnSetViewportModeDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnSetViewportModeDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.graph.ui_nodes.SetViewportMode'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnSetViewportModeDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnSetViewportModeDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnSetViewportModeDatabase(node)

            try:
                compute_function = getattr(OgnSetViewportModeDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnSetViewportModeDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnSetViewportModeDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnSetViewportModeDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnSetViewportModeDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnSetViewportModeDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnSetViewportModeDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnSetViewportModeDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnSetViewportModeDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnSetViewportModeDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnSetViewportModeDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnSetViewportModeDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnSetViewportModeDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.graph.ui_nodes")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Set Viewport Mode (BETA)")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "graph:action,ui")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "Sets the mode of a specified viewport window to 'Scripted' mode or 'Default' mode when executed.\n'Scripted' mode disables default viewport interaction and enables placing UI elements over the viewport. 'Default' mode is the default state of the viewport, and entering it will destroy any UI elements on the viewport.\nExecuting with 'Enable Viewport Mouse Events' set to true in 'Scripted' mode is required to allow the specified viewport to be targeted by viewport mouse event nodes, including 'On Viewport Dragged' and 'Read Viewport Drag State'.\nExecuting with 'Enable Picking' set to true in 'Scripted' mode is required to allow the specified viewport to be targeted by the 'On Picked' and 'Read Pick State' nodes.")
                node_type.set_metadata(ogn.MetadataKeys.EXCLUSIONS, "tests")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                OgnSetViewportModeDatabase.INTERFACE.add_to_node_type(node_type)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnSetViewportModeDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnSetViewportModeDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnSetViewportModeDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.graph.ui_nodes.SetViewportMode")
