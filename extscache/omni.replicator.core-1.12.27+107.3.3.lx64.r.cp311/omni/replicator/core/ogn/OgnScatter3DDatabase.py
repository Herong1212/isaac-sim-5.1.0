r"""Support for simplified access to data on nodes of type omni.replicator.core.OgnScatter3D

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

This node generates random points within any 3D mesh.
"""

import numpy
import sys
import traceback
import usdrt

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnScatter3DDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.OgnScatter3D

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.checkForCollisions
            inputs.execIn
            inputs.maxSamp
            inputs.minSamp
            inputs.noCollPrims
            inputs.preventVolOverlap
            inputs.prims
            inputs.resolutionScaling
            inputs.seed
            inputs.vizSampledVoxels
            inputs.volumeExclPrims
            inputs.volumePrims
            inputs.voxelSize
        Outputs:
            outputs.execOut
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
        ('inputs:checkForCollisions', 'bool', 0, None, 'whether sampling procedure should ensure that no sampled prims overlap', {ogn.MetadataKeys.DEFAULT: 'false'}, True, False, False, ''),
        ('inputs:execIn', 'execution', 0, None, 'exec', {}, True, None, False, ''),
        ('inputs:maxSamp', 'float3', 0, None, 'maximum position in global space to sample from', {ogn.MetadataKeys.DEFAULT: '[3.4028235e+38, 3.4028235e+38, 3.4028235e+38]'}, True, [3.4028235e+38, 3.4028235e+38, 3.4028235e+38], False, ''),
        ('inputs:minSamp', 'float3', 0, None, 'minimum position in global space to sample from', {ogn.MetadataKeys.DEFAULT: '[-3.4028235e+38, -3.4028235e+38, -3.4028235e+38]'}, True, [-3.4028235e+38, -3.4028235e+38, -3.4028235e+38], False, ''),
        ('inputs:noCollPrims', 'target', 0, None, 'existing prim(s) to prevent collisions with - if any prims are passed they will be checked for collisions which may slow down compute, regardless if checkForCollisions is True/False', {}, True, None, False, ''),
        ('inputs:preventVolOverlap', 'bool', 0, None, 'If true, prevent double sampling even when multiple enclosing volumes overlap, so that the entire enclosed volume is sampled uniformly. If false, it allows overlapped sampling with higher density in overlapping areas.', {ogn.MetadataKeys.DEFAULT: 'true'}, True, True, False, ''),
        ('inputs:prims', 'target', 0, None, 'prim(s) to set location', {}, True, None, False, ''),
        ('inputs:resolutionScaling', 'float', 0, None, 'Amount the default voxel resolution used in sampling should be scaled. More complex meshes may require higher resolution. Default voxel resolution is 30 for the longest side of the mean sized volumePrim mesh provided.', {ogn.MetadataKeys.DEFAULT: '1.0'}, True, 1.0, False, ''),
        ('inputs:seed', 'int', 0, None, 'Random Number Generator seed. A value of less than 0 will indicate using the global seed.', {ogn.MetadataKeys.DEFAULT: '-1'}, True, -1, False, ''),
        ('inputs:vizSampledVoxels', 'bool', 0, None, 'Visualize the voxel space that input prim positions are sampled from', {ogn.MetadataKeys.DEFAULT: 'false'}, True, False, False, ''),
        ('inputs:volumeExclPrims', 'target', 0, None, 'prim(s) from which to exclude from sampling. similar effect to noCollPrims, but more efficient and less accurate', {}, True, None, False, ''),
        ('inputs:volumePrims', 'target', 0, None, 'prim(s) from which to sample', {}, True, None, False, ''),
        ('inputs:voxelSize', 'float', 0, None, 'Voxel size used to compute the resolution. If this is provided, then resolutionScaling is ignored, otherwise (if it is zero by default) resolutionScaling is used.', {ogn.MetadataKeys.DEFAULT: '0.0'}, True, 0.0, False, ''),
        ('outputs:execOut', 'execution', 0, None, 'exec', {}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.execIn = og.AttributeRole.EXECUTION
        role_data.inputs.noCollPrims = og.AttributeRole.TARGET
        role_data.inputs.prims = og.AttributeRole.TARGET
        role_data.inputs.volumeExclPrims = og.AttributeRole.TARGET
        role_data.inputs.volumePrims = og.AttributeRole.TARGET
        role_data.outputs.execOut = og.AttributeRole.EXECUTION
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"checkForCollisions", "execIn", "maxSamp", "minSamp", "preventVolOverlap", "resolutionScaling", "seed", "vizSampledVoxels", "voxelSize", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.checkForCollisions, self._attributes.execIn, self._attributes.maxSamp, self._attributes.minSamp, self._attributes.preventVolOverlap, self._attributes.resolutionScaling, self._attributes.seed, self._attributes.vizSampledVoxels, self._attributes.voxelSize]
            self._batchedReadValues = [False, None, [3.4028235e+38, 3.4028235e+38, 3.4028235e+38], [-3.4028235e+38, -3.4028235e+38, -3.4028235e+38], True, 1.0, -1, False, 0.0]

        @property
        def noCollPrims(self):
            data_view = og.AttributeValueHelper(self._attributes.noCollPrims)
            return data_view.get()

        @noCollPrims.setter
        def noCollPrims(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.noCollPrims)
            data_view = og.AttributeValueHelper(self._attributes.noCollPrims)
            data_view.set(value)
            self.noCollPrims_size = data_view.get_array_size()

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
        def volumeExclPrims(self):
            data_view = og.AttributeValueHelper(self._attributes.volumeExclPrims)
            return data_view.get()

        @volumeExclPrims.setter
        def volumeExclPrims(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.volumeExclPrims)
            data_view = og.AttributeValueHelper(self._attributes.volumeExclPrims)
            data_view.set(value)
            self.volumeExclPrims_size = data_view.get_array_size()

        @property
        def volumePrims(self):
            data_view = og.AttributeValueHelper(self._attributes.volumePrims)
            return data_view.get()

        @volumePrims.setter
        def volumePrims(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.volumePrims)
            data_view = og.AttributeValueHelper(self._attributes.volumePrims)
            data_view.set(value)
            self.volumePrims_size = data_view.get_array_size()

        @property
        def checkForCollisions(self):
            return self._batchedReadValues[0]

        @checkForCollisions.setter
        def checkForCollisions(self, value):
            self._batchedReadValues[0] = value

        @property
        def execIn(self):
            return self._batchedReadValues[1]

        @execIn.setter
        def execIn(self, value):
            self._batchedReadValues[1] = value

        @property
        def maxSamp(self):
            return self._batchedReadValues[2]

        @maxSamp.setter
        def maxSamp(self, value):
            self._batchedReadValues[2] = value

        @property
        def minSamp(self):
            return self._batchedReadValues[3]

        @minSamp.setter
        def minSamp(self, value):
            self._batchedReadValues[3] = value

        @property
        def preventVolOverlap(self):
            return self._batchedReadValues[4]

        @preventVolOverlap.setter
        def preventVolOverlap(self, value):
            self._batchedReadValues[4] = value

        @property
        def resolutionScaling(self):
            return self._batchedReadValues[5]

        @resolutionScaling.setter
        def resolutionScaling(self, value):
            self._batchedReadValues[5] = value

        @property
        def seed(self):
            return self._batchedReadValues[6]

        @seed.setter
        def seed(self, value):
            self._batchedReadValues[6] = value

        @property
        def vizSampledVoxels(self):
            return self._batchedReadValues[7]

        @vizSampledVoxels.setter
        def vizSampledVoxels(self, value):
            self._batchedReadValues[7] = value

        @property
        def voxelSize(self):
            return self._batchedReadValues[8]

        @voxelSize.setter
        def voxelSize(self, value):
            self._batchedReadValues[8] = value

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
            self._batchedWriteValues = { }

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
        self.inputs = OgnScatter3DDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnScatter3DDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnScatter3DDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnScatter3DDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.OgnScatter3D'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnScatter3DDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnScatter3DDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnScatter3DDatabase(node)

            try:
                compute_function = getattr(OgnScatter3DDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnScatter3DDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnScatter3DDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnScatter3DDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnScatter3DDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnScatter3DDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnScatter3DDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnScatter3DDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnScatter3DDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnScatter3DDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnScatter3DDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnScatter3DDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnScatter3DDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Scatter Node: 3D Scattering")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "Replicator:Core")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORY_DESCRIPTIONS, "Replicator:Core,Core Replicator nodes")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "This node generates random points within any 3D mesh.")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                __hints = node_type.get_scheduling_hints()
                if __hints is not None:
                    __hints.compute_rule = og.eComputeRule.E_ON_REQUEST
                OgnScatter3DDatabase.INTERFACE.add_to_node_type(node_type)
                node_type.set_has_state(True)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnScatter3DDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnScatter3DDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnScatter3DDatabase.abi, 1)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.OgnScatter3D")
