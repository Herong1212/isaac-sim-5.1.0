r"""Support for simplified access to data on nodes of type omni.replicator.core.OgnGetPrims

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

This node searches the stage by path and returns a list of prims.
"""

import numpy
import sys
import traceback
import usdrt

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnGetPrimsDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.OgnGetPrims

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.cachePrims
            inputs.execIn
            inputs.ignoreCase
            inputs.pathMatch
            inputs.pathPattern
            inputs.pathPatternExclusion
            inputs.primTypes
            inputs.primTypesExclusion
            inputs.semantics
            inputs.semanticsExclusion
        Outputs:
            outputs.execOut
            outputs.prims
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
        ('inputs:cachePrims', 'bool', 0, None, 'If set to True, the stage is parsed only once.', {ogn.MetadataKeys.DEFAULT: 'true'}, True, True, False, ''),
        ('inputs:execIn', 'execution', 0, None, 'exec', {}, True, None, False, ''),
        ('inputs:ignoreCase', 'bool', 0, None, 'If set to True, use case-insensitive matching.', {ogn.MetadataKeys.DEFAULT: 'true'}, True, True, False, ''),
        ('inputs:pathMatch', 'string', 0, None, 'The path substring to match', {}, True, "", False, ''),
        ('inputs:pathPattern', 'string', 0, None, 'The RegEx (Regular Expression) path pattern to match', {}, True, "", False, ''),
        ('inputs:pathPatternExclusion', 'string', 0, None, 'The RegEx (Regular Expression) path pattern to ignore', {}, True, "", False, ''),
        ('inputs:primTypes', 'token[]', 0, None, 'List of prim types to include', {}, True, [], False, ''),
        ('inputs:primTypesExclusion', 'token[]', 0, None, 'List of prim types to ignore', {}, True, [], False, ''),
        ('inputs:semantics', 'token[]', 0, None, 'Semantic type-value pairs of semantics to include', {}, True, [], False, ''),
        ('inputs:semanticsExclusion', 'token[]', 0, None, 'Semantic type-value pairs of semantics to ignore', {}, True, [], False, ''),
        ('outputs:execOut', 'execution', 0, None, 'exec', {}, True, None, False, ''),
        ('outputs:prims', 'target', 0, None, 'Prim paths from search result.', {}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.execIn = og.AttributeRole.EXECUTION
        role_data.inputs.pathMatch = og.AttributeRole.TEXT
        role_data.inputs.pathPattern = og.AttributeRole.TEXT
        role_data.inputs.pathPatternExclusion = og.AttributeRole.TEXT
        role_data.outputs.execOut = og.AttributeRole.EXECUTION
        role_data.outputs.prims = og.AttributeRole.TARGET
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"cachePrims", "execIn", "ignoreCase", "pathMatch", "pathPattern", "pathPatternExclusion", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.cachePrims, self._attributes.execIn, self._attributes.ignoreCase, self._attributes.pathMatch, self._attributes.pathPattern, self._attributes.pathPatternExclusion]
            self._batchedReadValues = [True, None, True, "", "", ""]

        @property
        def primTypes(self):
            data_view = og.AttributeValueHelper(self._attributes.primTypes)
            return data_view.get()

        @primTypes.setter
        def primTypes(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.primTypes)
            data_view = og.AttributeValueHelper(self._attributes.primTypes)
            data_view.set(value)
            self.primTypes_size = data_view.get_array_size()

        @property
        def primTypesExclusion(self):
            data_view = og.AttributeValueHelper(self._attributes.primTypesExclusion)
            return data_view.get()

        @primTypesExclusion.setter
        def primTypesExclusion(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.primTypesExclusion)
            data_view = og.AttributeValueHelper(self._attributes.primTypesExclusion)
            data_view.set(value)
            self.primTypesExclusion_size = data_view.get_array_size()

        @property
        def semantics(self):
            data_view = og.AttributeValueHelper(self._attributes.semantics)
            return data_view.get()

        @semantics.setter
        def semantics(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.semantics)
            data_view = og.AttributeValueHelper(self._attributes.semantics)
            data_view.set(value)
            self.semantics_size = data_view.get_array_size()

        @property
        def semanticsExclusion(self):
            data_view = og.AttributeValueHelper(self._attributes.semanticsExclusion)
            return data_view.get()

        @semanticsExclusion.setter
        def semanticsExclusion(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.semanticsExclusion)
            data_view = og.AttributeValueHelper(self._attributes.semanticsExclusion)
            data_view.set(value)
            self.semanticsExclusion_size = data_view.get_array_size()

        @property
        def cachePrims(self):
            return self._batchedReadValues[0]

        @cachePrims.setter
        def cachePrims(self, value):
            self._batchedReadValues[0] = value

        @property
        def execIn(self):
            return self._batchedReadValues[1]

        @execIn.setter
        def execIn(self, value):
            self._batchedReadValues[1] = value

        @property
        def ignoreCase(self):
            return self._batchedReadValues[2]

        @ignoreCase.setter
        def ignoreCase(self, value):
            self._batchedReadValues[2] = value

        @property
        def pathMatch(self):
            return self._batchedReadValues[3]

        @pathMatch.setter
        def pathMatch(self, value):
            self._batchedReadValues[3] = value

        @property
        def pathPattern(self):
            return self._batchedReadValues[4]

        @pathPattern.setter
        def pathPattern(self, value):
            self._batchedReadValues[4] = value

        @property
        def pathPatternExclusion(self):
            return self._batchedReadValues[5]

        @pathPatternExclusion.setter
        def pathPatternExclusion(self, value):
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
        LOCAL_PROPERTY_NAMES = {"execOut", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self.prims_size = None
            self._batchedWriteValues = { }

        @property
        def prims(self):
            data_view = og.AttributeValueHelper(self._attributes.prims)
            return data_view.get(reserved_element_count=self.prims_size)

        @prims.setter
        def prims(self, value):
            data_view = og.AttributeValueHelper(self._attributes.prims)
            data_view.set(value)
            self.prims_size = data_view.get_array_size()

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
        self.inputs = OgnGetPrimsDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnGetPrimsDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnGetPrimsDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnGetPrimsDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.OgnGetPrims'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnGetPrimsDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnGetPrimsDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnGetPrimsDatabase(node)

            try:
                compute_function = getattr(OgnGetPrimsDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnGetPrimsDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnGetPrimsDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnGetPrimsDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnGetPrimsDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnGetPrimsDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnGetPrimsDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnGetPrimsDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnGetPrimsDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnGetPrimsDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnGetPrimsDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnGetPrimsDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnGetPrimsDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Get Prims")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "Replicator:Core")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORY_DESCRIPTIONS, "Replicator:Core,Core Replicator nodes")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "This node searches the stage by path and returns a list of prims.")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                __hints = node_type.get_scheduling_hints()
                if __hints is not None:
                    __hints.compute_rule = og.eComputeRule.E_ON_REQUEST
                OgnGetPrimsDatabase.INTERFACE.add_to_node_type(node_type)
                node_type.set_has_state(True)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnGetPrimsDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnGetPrimsDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnGetPrimsDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.OgnGetPrims")
