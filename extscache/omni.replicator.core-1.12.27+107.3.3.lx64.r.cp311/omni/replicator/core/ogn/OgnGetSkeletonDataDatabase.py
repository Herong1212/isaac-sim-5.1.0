r"""Support for simplified access to data on nodes of type omni.replicator.core.OgnGetSkeletonData

 __   ___ .  .  ___  __       ___  ___  __      __   __   __   ___
/ _` |__  |\ | |__  |__)  /\   |  |__  |  \    /  ` /  \ |  \ |__
\__| |___ | \| |___ |  \ /--\  |  |___ |__/    \__, \__/ |__/ |___

 __   __     .  .  __  ___     .  .  __   __     ___
|  \ /  \    |\ | /  \  |      |\/| /  \ |  \ | |__  \ /
|__/ \__/    | \| \__/  |      |  | \__/ |__/ | |     |

This node retrieves skeleton data given skeleton prims and camera paramters
"""

import numpy
import sys
import traceback

import omni.graph.core as og
import omni.graph.core._omni_graph_core as _og
import omni.graph.tools.ogn as ogn



class OgnGetSkeletonDataDatabase(og.Database):
    """Helper class providing simplified access to data on nodes of type omni.replicator.core.OgnGetSkeletonData

    Class Members:
        node: Node being evaluated

    Attribute Value Properties:
        Inputs:
            inputs.cameraAperture
            inputs.cameraFisheyeMaxFOV
            inputs.cameraFisheyeNominalHeight
            inputs.cameraFisheyeNominalWidth
            inputs.cameraFisheyeOpticalCentre
            inputs.cameraFisheyePolynomial
            inputs.cameraFocalLength
            inputs.cameraModel
            inputs.cameraNearFar
            inputs.cameraProjection
            inputs.cameraViewTransform
            inputs.exec
            inputs.fabricJoints
            inputs.fabricPrims
            inputs.instanceSegmentationCudaDeviceIndex
            inputs.instanceSegmentationHeight
            inputs.instanceSegmentationIds
            inputs.instanceSegmentationLabels
            inputs.instanceSegmentationPtr
            inputs.instanceSegmentationSemantics
            inputs.instanceSegmentationStrides
            inputs.instanceSegmentationWidth
            inputs.jointWorldOrientations
            inputs.jointWorldPositions
            inputs.jointWorldScales
            inputs.primWorldOrientations
            inputs.primWorldPositions
            inputs.primWorldScales
            inputs.prims
            inputs.renderProductPath
            inputs.useSkelJoints
        Outputs:
            outputs.animationVariant
            outputs.assetPath
            outputs.exec
            outputs.globalTranslations
            outputs.globalTranslationsSizes
            outputs.inView
            outputs.jointOcclusions
            outputs.jointOcclusionsSizes
            outputs.localRotations
            outputs.localRotationsSizes
            outputs.numSkeletons
            outputs.occlusionTypes
            outputs.occlusionTypesSizes
            outputs.restGlobalTranslations
            outputs.restGlobalTranslationsSizes
            outputs.restLocalRotations
            outputs.restLocalRotationsSizes
            outputs.restLocalTranslations
            outputs.restLocalTranslationsSizes
            outputs.skelName
            outputs.skelPath
            outputs.skeletonData
            outputs.skeletonJoints
            outputs.skeletonParents
            outputs.skeletonParentsSizes
            outputs.translations2d
            outputs.translations2dSizes
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
        ('inputs:cameraAperture', 'float2', 0, None, 'Camera horizontal and vertical aperture', {}, True, [0.0, 0.0], False, ''),
        ('inputs:cameraFisheyeMaxFOV', 'float', 0, None, 'Camera fisheye maximum field of view', {}, True, 0.0, False, ''),
        ('inputs:cameraFisheyeNominalHeight', 'int', 0, None, 'Camera fisheye nominal height', {}, True, 0, False, ''),
        ('inputs:cameraFisheyeNominalWidth', 'int', 0, None, 'Camera fisheye nominal width', {}, True, 0, False, ''),
        ('inputs:cameraFisheyeOpticalCentre', 'float2', 0, None, 'Camera fisheye optical centre', {}, True, [0.0, 0.0], False, ''),
        ('inputs:cameraFisheyePolynomial', 'float[]', 0, None, 'Camera fisheye polynomial', {}, True, [], False, ''),
        ('inputs:cameraFocalLength', 'float', 0, None, 'Camera focal length', {}, True, 0.0, False, ''),
        ('inputs:cameraModel', 'token', 0, None, 'Camera model (pinhole or fisheye models)', {}, True, "", False, ''),
        ('inputs:cameraNearFar', 'float2', 0, None, 'Camera near/far clipping range', {}, True, [0.0, 0.0], False, ''),
        ('inputs:cameraProjection', 'matrix4d', 0, None, 'Camera projection matrix', {}, True, [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], False, ''),
        ('inputs:cameraViewTransform', 'matrix4d', 0, None, 'Camera view matrix', {}, True, [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], False, ''),
        ('inputs:exec', 'execution', 0, None, 'exec', {}, True, None, False, ''),
        ('inputs:fabricJoints', 'token[]', 0, None, 'list of fabric joint prim paths', {}, True, [], False, ''),
        ('inputs:fabricPrims', 'token[]', 0, None, 'list of fabric skeleton root prim paths', {}, True, [], False, ''),
        ('inputs:instanceSegmentationCudaDeviceIndex', 'int', 0, None, 'Index of the device where the data lives (-1 for host data)', {ogn.MetadataKeys.DEFAULT: '-1'}, True, -1, False, ''),
        ('inputs:instanceSegmentationHeight', 'uint', 0, None, 'Instance Segmentation buffer height', {ogn.MetadataKeys.DEFAULT: '0'}, True, 0, False, ''),
        ('inputs:instanceSegmentationIds', 'uint[]', 0, None, 'Mapping from id to semantic labels.', {}, True, [], False, ''),
        ('inputs:instanceSegmentationLabels', 'token[]', 0, None, 'Mapping from id to prim paths.', {}, True, [], False, ''),
        ('inputs:instanceSegmentationPtr', 'uint64', 0, None, 'Pointer to the raw instance segmentation data (host pointer)', {ogn.MetadataKeys.DEFAULT: '0'}, True, 0, False, ''),
        ('inputs:instanceSegmentationSemantics', 'token[]', 0, None, 'Mapping from id to semantic labels.', {}, True, [], False, ''),
        ('inputs:instanceSegmentationStrides', 'int2', 0, None, 'Strides (in bytes) for instance segmentation.', {}, True, [0, 0], False, ''),
        ('inputs:instanceSegmentationWidth', 'uint', 0, None, 'Instance Segmentation buffer width', {ogn.MetadataKeys.DEFAULT: '0'}, True, 0, False, ''),
        ('inputs:jointWorldOrientations', 'float4[]', 0, None, 'World rotations for skeleton prims from fabric', {ogn.MetadataKeys.DEFAULT: '[]'}, True, [], False, ''),
        ('inputs:jointWorldPositions', 'double3[]', 0, None, 'World translations for skeleton prims from fabric', {ogn.MetadataKeys.DEFAULT: '[]'}, True, [], False, ''),
        ('inputs:jointWorldScales', 'float3[]', 0, None, 'World scales for skeleton prims from fabric', {ogn.MetadataKeys.DEFAULT: '[]'}, True, [], False, ''),
        ('inputs:primWorldOrientations', 'float4[]', 0, None, 'World rotations for skeleton prims from fabric', {ogn.MetadataKeys.DEFAULT: '[]'}, True, [], False, ''),
        ('inputs:primWorldPositions', 'double3[]', 0, None, 'World translations for skeleton prims from fabric', {ogn.MetadataKeys.DEFAULT: '[]'}, True, [], False, ''),
        ('inputs:primWorldScales', 'float3[]', 0, None, 'World scales for skeleton prims from fabric', {ogn.MetadataKeys.DEFAULT: '[]'}, True, [], False, ''),
        ('inputs:prims', 'token[]', 0, None, 'list of skeleton prim paths', {}, True, [], False, ''),
        ('inputs:renderProductPath', 'token', 0, None, 'Path of the render product to use for 2d projections', {}, True, "", False, ''),
        ('inputs:useSkelJoints', 'bool', 0, None, 'Get skeleton joint information using the skelJoints information', {}, True, False, False, ''),
        ('outputs:animationVariant', 'token[]', 0, None, 'The name of the animation variant assigned.', {}, True, None, False, ''),
        ('outputs:assetPath', 'token[]', 0, None, 'The referenced asset path.', {}, True, None, False, ''),
        ('outputs:exec', 'execution', 0, None, 'exec', {}, True, None, False, ''),
        ('outputs:globalTranslations', 'float3[]', 0, None, 'The skeleton joint translations in global space.', {}, True, None, False, ''),
        ('outputs:globalTranslationsSizes', 'int[]', 0, None, 'The size of each skeleton globalTranslations array.', {}, True, None, False, ''),
        ('outputs:inView', 'bool[]', 0, None, 'Whether the skeleton is in the camera view.', {}, True, None, False, ''),
        ('outputs:jointOcclusions', 'bool[]', 0, None, 'Whether the joint is occluded.', {}, True, None, False, ''),
        ('outputs:jointOcclusionsSizes', 'int[]', 0, None, 'The size of each skeleton jointOcclusions array.', {}, True, None, False, ''),
        ('outputs:localRotations', 'float4[]', 0, None, 'The skeleton joint rotations in local space.', {}, True, None, False, ''),
        ('outputs:localRotationsSizes', 'int[]', 0, None, 'The size of each skeleton localRotations array.', {}, True, None, False, ''),
        ('outputs:numSkeletons', 'int', 0, None, 'The number of skeletons in output data.', {}, True, None, False, ''),
        ('outputs:occlusionTypes', 'token[]', 0, None, 'The semantic name of the object occluding the joint.', {}, True, None, False, ''),
        ('outputs:occlusionTypesSizes', 'int[]', 0, None, 'The size of each skeleton occlusionTypes array.', {}, True, None, False, ''),
        ('outputs:restGlobalTranslations', 'float3[]', 0, None, 'The rest skeleton joint translations in global space.', {}, True, None, False, ''),
        ('outputs:restGlobalTranslationsSizes', 'int[]', 0, None, 'The size of each skeleton restGlobalTranslations array.', {}, True, None, False, ''),
        ('outputs:restLocalRotations', 'float4[]', 0, None, 'The rest skeleton joint rotations in local space.', {}, True, None, False, ''),
        ('outputs:restLocalRotationsSizes', 'int[]', 0, None, 'The size of each skeleton restLocalRotations array.', {}, True, None, False, ''),
        ('outputs:restLocalTranslations', 'float3[]', 0, None, 'The rest skeleton joint translations in local space.', {}, True, None, False, ''),
        ('outputs:restLocalTranslationsSizes', 'int[]', 0, None, 'The size of each skeleton restLocalTranslations array.', {}, True, None, False, ''),
        ('outputs:skelName', 'token[]', 0, None, 'The skeleton name.', {}, True, None, False, ''),
        ('outputs:skelPath', 'token[]', 0, None, 'The USD stage path to the skeleton.', {}, True, None, False, ''),
        ('outputs:skeletonData', 'string', 0, None, 'Skeleton Data', {ogn.MetadataKeys.DEFAULT: '"{}"'}, True, "{}", True, 'Use separate node outputs instead.'),
        ('outputs:skeletonJoints', 'token[]', 0, None, 'The paths of all the skeleton joints.', {}, True, None, False, ''),
        ('outputs:skeletonParents', 'int[]', 0, None, 'The ID of all the skeleton joints.', {}, True, None, False, ''),
        ('outputs:skeletonParentsSizes', 'int[]', 0, None, 'The size of each skeleton skeletonParents array.', {}, True, None, False, ''),
        ('outputs:translations2d', 'float2[]', 0, None, 'The 2D projected skeleton joint positions.', {}, True, None, False, ''),
        ('outputs:translations2dSizes', 'int[]', 0, None, 'The size of each skeleton translations2d array.', {}, True, None, False, ''),
    ])

    @classmethod
    def _populate_role_data(cls):
        """Populate a role structure with the non-default roles on this node type"""
        role_data = super()._populate_role_data()
        role_data.inputs.cameraProjection = og.AttributeRole.MATRIX
        role_data.inputs.cameraViewTransform = og.AttributeRole.MATRIX
        role_data.inputs.exec = og.AttributeRole.EXECUTION
        role_data.outputs.exec = og.AttributeRole.EXECUTION
        role_data.outputs.skeletonData = og.AttributeRole.TEXT
        return role_data

    class ValuesForInputs(og.DynamicAttributeAccess):
        LOCAL_PROPERTY_NAMES = {"cameraAperture", "cameraFisheyeMaxFOV", "cameraFisheyeNominalHeight", "cameraFisheyeNominalWidth", "cameraFisheyeOpticalCentre", "cameraFocalLength", "cameraModel", "cameraNearFar", "cameraProjection", "cameraViewTransform", "exec", "instanceSegmentationCudaDeviceIndex", "instanceSegmentationHeight", "instanceSegmentationPtr", "instanceSegmentationStrides", "instanceSegmentationWidth", "renderProductPath", "useSkelJoints", "_setting_locked", "_batchedReadAttributes", "_batchedReadValues"}
        """Helper class that creates natural hierarchical access to input attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self._batchedReadAttributes = [self._attributes.cameraAperture, self._attributes.cameraFisheyeMaxFOV, self._attributes.cameraFisheyeNominalHeight, self._attributes.cameraFisheyeNominalWidth, self._attributes.cameraFisheyeOpticalCentre, self._attributes.cameraFocalLength, self._attributes.cameraModel, self._attributes.cameraNearFar, self._attributes.cameraProjection, self._attributes.cameraViewTransform, self._attributes.exec, self._attributes.instanceSegmentationCudaDeviceIndex, self._attributes.instanceSegmentationHeight, self._attributes.instanceSegmentationPtr, self._attributes.instanceSegmentationStrides, self._attributes.instanceSegmentationWidth, self._attributes.renderProductPath, self._attributes.useSkelJoints]
            self._batchedReadValues = [[0.0, 0.0], 0.0, 0, 0, [0.0, 0.0], 0.0, "", [0.0, 0.0], [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], None, -1, 0, 0, [0, 0], 0, "", False]

        @property
        def cameraFisheyePolynomial(self):
            data_view = og.AttributeValueHelper(self._attributes.cameraFisheyePolynomial)
            return data_view.get()

        @cameraFisheyePolynomial.setter
        def cameraFisheyePolynomial(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.cameraFisheyePolynomial)
            data_view = og.AttributeValueHelper(self._attributes.cameraFisheyePolynomial)
            data_view.set(value)
            self.cameraFisheyePolynomial_size = data_view.get_array_size()

        @property
        def fabricJoints(self):
            data_view = og.AttributeValueHelper(self._attributes.fabricJoints)
            return data_view.get()

        @fabricJoints.setter
        def fabricJoints(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.fabricJoints)
            data_view = og.AttributeValueHelper(self._attributes.fabricJoints)
            data_view.set(value)
            self.fabricJoints_size = data_view.get_array_size()

        @property
        def fabricPrims(self):
            data_view = og.AttributeValueHelper(self._attributes.fabricPrims)
            return data_view.get()

        @fabricPrims.setter
        def fabricPrims(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.fabricPrims)
            data_view = og.AttributeValueHelper(self._attributes.fabricPrims)
            data_view.set(value)
            self.fabricPrims_size = data_view.get_array_size()

        @property
        def instanceSegmentationIds(self):
            data_view = og.AttributeValueHelper(self._attributes.instanceSegmentationIds)
            return data_view.get()

        @instanceSegmentationIds.setter
        def instanceSegmentationIds(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.instanceSegmentationIds)
            data_view = og.AttributeValueHelper(self._attributes.instanceSegmentationIds)
            data_view.set(value)
            self.instanceSegmentationIds_size = data_view.get_array_size()

        @property
        def instanceSegmentationLabels(self):
            data_view = og.AttributeValueHelper(self._attributes.instanceSegmentationLabels)
            return data_view.get()

        @instanceSegmentationLabels.setter
        def instanceSegmentationLabels(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.instanceSegmentationLabels)
            data_view = og.AttributeValueHelper(self._attributes.instanceSegmentationLabels)
            data_view.set(value)
            self.instanceSegmentationLabels_size = data_view.get_array_size()

        @property
        def instanceSegmentationSemantics(self):
            data_view = og.AttributeValueHelper(self._attributes.instanceSegmentationSemantics)
            return data_view.get()

        @instanceSegmentationSemantics.setter
        def instanceSegmentationSemantics(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.instanceSegmentationSemantics)
            data_view = og.AttributeValueHelper(self._attributes.instanceSegmentationSemantics)
            data_view.set(value)
            self.instanceSegmentationSemantics_size = data_view.get_array_size()

        @property
        def jointWorldOrientations(self):
            data_view = og.AttributeValueHelper(self._attributes.jointWorldOrientations)
            return data_view.get()

        @jointWorldOrientations.setter
        def jointWorldOrientations(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.jointWorldOrientations)
            data_view = og.AttributeValueHelper(self._attributes.jointWorldOrientations)
            data_view.set(value)
            self.jointWorldOrientations_size = data_view.get_array_size()

        @property
        def jointWorldPositions(self):
            data_view = og.AttributeValueHelper(self._attributes.jointWorldPositions)
            return data_view.get()

        @jointWorldPositions.setter
        def jointWorldPositions(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.jointWorldPositions)
            data_view = og.AttributeValueHelper(self._attributes.jointWorldPositions)
            data_view.set(value)
            self.jointWorldPositions_size = data_view.get_array_size()

        @property
        def jointWorldScales(self):
            data_view = og.AttributeValueHelper(self._attributes.jointWorldScales)
            return data_view.get()

        @jointWorldScales.setter
        def jointWorldScales(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.jointWorldScales)
            data_view = og.AttributeValueHelper(self._attributes.jointWorldScales)
            data_view.set(value)
            self.jointWorldScales_size = data_view.get_array_size()

        @property
        def primWorldOrientations(self):
            data_view = og.AttributeValueHelper(self._attributes.primWorldOrientations)
            return data_view.get()

        @primWorldOrientations.setter
        def primWorldOrientations(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.primWorldOrientations)
            data_view = og.AttributeValueHelper(self._attributes.primWorldOrientations)
            data_view.set(value)
            self.primWorldOrientations_size = data_view.get_array_size()

        @property
        def primWorldPositions(self):
            data_view = og.AttributeValueHelper(self._attributes.primWorldPositions)
            return data_view.get()

        @primWorldPositions.setter
        def primWorldPositions(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.primWorldPositions)
            data_view = og.AttributeValueHelper(self._attributes.primWorldPositions)
            data_view.set(value)
            self.primWorldPositions_size = data_view.get_array_size()

        @property
        def primWorldScales(self):
            data_view = og.AttributeValueHelper(self._attributes.primWorldScales)
            return data_view.get()

        @primWorldScales.setter
        def primWorldScales(self, value):
            if self._setting_locked:
                raise og.ReadOnlyError(self._attributes.primWorldScales)
            data_view = og.AttributeValueHelper(self._attributes.primWorldScales)
            data_view.set(value)
            self.primWorldScales_size = data_view.get_array_size()

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
        def cameraAperture(self):
            return self._batchedReadValues[0]

        @cameraAperture.setter
        def cameraAperture(self, value):
            self._batchedReadValues[0] = value

        @property
        def cameraFisheyeMaxFOV(self):
            return self._batchedReadValues[1]

        @cameraFisheyeMaxFOV.setter
        def cameraFisheyeMaxFOV(self, value):
            self._batchedReadValues[1] = value

        @property
        def cameraFisheyeNominalHeight(self):
            return self._batchedReadValues[2]

        @cameraFisheyeNominalHeight.setter
        def cameraFisheyeNominalHeight(self, value):
            self._batchedReadValues[2] = value

        @property
        def cameraFisheyeNominalWidth(self):
            return self._batchedReadValues[3]

        @cameraFisheyeNominalWidth.setter
        def cameraFisheyeNominalWidth(self, value):
            self._batchedReadValues[3] = value

        @property
        def cameraFisheyeOpticalCentre(self):
            return self._batchedReadValues[4]

        @cameraFisheyeOpticalCentre.setter
        def cameraFisheyeOpticalCentre(self, value):
            self._batchedReadValues[4] = value

        @property
        def cameraFocalLength(self):
            return self._batchedReadValues[5]

        @cameraFocalLength.setter
        def cameraFocalLength(self, value):
            self._batchedReadValues[5] = value

        @property
        def cameraModel(self):
            return self._batchedReadValues[6]

        @cameraModel.setter
        def cameraModel(self, value):
            self._batchedReadValues[6] = value

        @property
        def cameraNearFar(self):
            return self._batchedReadValues[7]

        @cameraNearFar.setter
        def cameraNearFar(self, value):
            self._batchedReadValues[7] = value

        @property
        def cameraProjection(self):
            return self._batchedReadValues[8]

        @cameraProjection.setter
        def cameraProjection(self, value):
            self._batchedReadValues[8] = value

        @property
        def cameraViewTransform(self):
            return self._batchedReadValues[9]

        @cameraViewTransform.setter
        def cameraViewTransform(self, value):
            self._batchedReadValues[9] = value

        @property
        def exec(self):
            return self._batchedReadValues[10]

        @exec.setter
        def exec(self, value):
            self._batchedReadValues[10] = value

        @property
        def instanceSegmentationCudaDeviceIndex(self):
            return self._batchedReadValues[11]

        @instanceSegmentationCudaDeviceIndex.setter
        def instanceSegmentationCudaDeviceIndex(self, value):
            self._batchedReadValues[11] = value

        @property
        def instanceSegmentationHeight(self):
            return self._batchedReadValues[12]

        @instanceSegmentationHeight.setter
        def instanceSegmentationHeight(self, value):
            self._batchedReadValues[12] = value

        @property
        def instanceSegmentationPtr(self):
            return self._batchedReadValues[13]

        @instanceSegmentationPtr.setter
        def instanceSegmentationPtr(self, value):
            self._batchedReadValues[13] = value

        @property
        def instanceSegmentationStrides(self):
            return self._batchedReadValues[14]

        @instanceSegmentationStrides.setter
        def instanceSegmentationStrides(self, value):
            self._batchedReadValues[14] = value

        @property
        def instanceSegmentationWidth(self):
            return self._batchedReadValues[15]

        @instanceSegmentationWidth.setter
        def instanceSegmentationWidth(self, value):
            self._batchedReadValues[15] = value

        @property
        def renderProductPath(self):
            return self._batchedReadValues[16]

        @renderProductPath.setter
        def renderProductPath(self, value):
            self._batchedReadValues[16] = value

        @property
        def useSkelJoints(self):
            return self._batchedReadValues[17]

        @useSkelJoints.setter
        def useSkelJoints(self, value):
            self._batchedReadValues[17] = value

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
        LOCAL_PROPERTY_NAMES = {"exec", "numSkeletons", "skeletonData", "_batchedWriteValues"}
        """Helper class that creates natural hierarchical access to output attributes"""
        def __init__(self, node: og.Node, attributes, dynamic_attributes: og.DynamicAttributeInterface):
            """Initialize simplified access for the attribute data"""
            context = node.get_graph().get_default_graph_context()
            super().__init__(context, node, attributes, dynamic_attributes)
            self.animationVariant_size = None
            self.assetPath_size = None
            self.globalTranslations_size = None
            self.globalTranslationsSizes_size = None
            self.inView_size = None
            self.jointOcclusions_size = None
            self.jointOcclusionsSizes_size = None
            self.localRotations_size = None
            self.localRotationsSizes_size = None
            self.occlusionTypes_size = None
            self.occlusionTypesSizes_size = None
            self.restGlobalTranslations_size = None
            self.restGlobalTranslationsSizes_size = None
            self.restLocalRotations_size = None
            self.restLocalRotationsSizes_size = None
            self.restLocalTranslations_size = None
            self.restLocalTranslationsSizes_size = None
            self.skelName_size = None
            self.skelPath_size = None
            self.skeletonData_size = 2
            self.skeletonJoints_size = None
            self.skeletonParents_size = None
            self.skeletonParentsSizes_size = None
            self.translations2d_size = None
            self.translations2dSizes_size = None
            self._batchedWriteValues = { }

        @property
        def animationVariant(self):
            data_view = og.AttributeValueHelper(self._attributes.animationVariant)
            return data_view.get(reserved_element_count=self.animationVariant_size)

        @animationVariant.setter
        def animationVariant(self, value):
            data_view = og.AttributeValueHelper(self._attributes.animationVariant)
            data_view.set(value)
            self.animationVariant_size = data_view.get_array_size()

        @property
        def assetPath(self):
            data_view = og.AttributeValueHelper(self._attributes.assetPath)
            return data_view.get(reserved_element_count=self.assetPath_size)

        @assetPath.setter
        def assetPath(self, value):
            data_view = og.AttributeValueHelper(self._attributes.assetPath)
            data_view.set(value)
            self.assetPath_size = data_view.get_array_size()

        @property
        def globalTranslations(self):
            data_view = og.AttributeValueHelper(self._attributes.globalTranslations)
            return data_view.get(reserved_element_count=self.globalTranslations_size)

        @globalTranslations.setter
        def globalTranslations(self, value):
            data_view = og.AttributeValueHelper(self._attributes.globalTranslations)
            data_view.set(value)
            self.globalTranslations_size = data_view.get_array_size()

        @property
        def globalTranslationsSizes(self):
            data_view = og.AttributeValueHelper(self._attributes.globalTranslationsSizes)
            return data_view.get(reserved_element_count=self.globalTranslationsSizes_size)

        @globalTranslationsSizes.setter
        def globalTranslationsSizes(self, value):
            data_view = og.AttributeValueHelper(self._attributes.globalTranslationsSizes)
            data_view.set(value)
            self.globalTranslationsSizes_size = data_view.get_array_size()

        @property
        def inView(self):
            data_view = og.AttributeValueHelper(self._attributes.inView)
            return data_view.get(reserved_element_count=self.inView_size)

        @inView.setter
        def inView(self, value):
            data_view = og.AttributeValueHelper(self._attributes.inView)
            data_view.set(value)
            self.inView_size = data_view.get_array_size()

        @property
        def jointOcclusions(self):
            data_view = og.AttributeValueHelper(self._attributes.jointOcclusions)
            return data_view.get(reserved_element_count=self.jointOcclusions_size)

        @jointOcclusions.setter
        def jointOcclusions(self, value):
            data_view = og.AttributeValueHelper(self._attributes.jointOcclusions)
            data_view.set(value)
            self.jointOcclusions_size = data_view.get_array_size()

        @property
        def jointOcclusionsSizes(self):
            data_view = og.AttributeValueHelper(self._attributes.jointOcclusionsSizes)
            return data_view.get(reserved_element_count=self.jointOcclusionsSizes_size)

        @jointOcclusionsSizes.setter
        def jointOcclusionsSizes(self, value):
            data_view = og.AttributeValueHelper(self._attributes.jointOcclusionsSizes)
            data_view.set(value)
            self.jointOcclusionsSizes_size = data_view.get_array_size()

        @property
        def localRotations(self):
            data_view = og.AttributeValueHelper(self._attributes.localRotations)
            return data_view.get(reserved_element_count=self.localRotations_size)

        @localRotations.setter
        def localRotations(self, value):
            data_view = og.AttributeValueHelper(self._attributes.localRotations)
            data_view.set(value)
            self.localRotations_size = data_view.get_array_size()

        @property
        def localRotationsSizes(self):
            data_view = og.AttributeValueHelper(self._attributes.localRotationsSizes)
            return data_view.get(reserved_element_count=self.localRotationsSizes_size)

        @localRotationsSizes.setter
        def localRotationsSizes(self, value):
            data_view = og.AttributeValueHelper(self._attributes.localRotationsSizes)
            data_view.set(value)
            self.localRotationsSizes_size = data_view.get_array_size()

        @property
        def occlusionTypes(self):
            data_view = og.AttributeValueHelper(self._attributes.occlusionTypes)
            return data_view.get(reserved_element_count=self.occlusionTypes_size)

        @occlusionTypes.setter
        def occlusionTypes(self, value):
            data_view = og.AttributeValueHelper(self._attributes.occlusionTypes)
            data_view.set(value)
            self.occlusionTypes_size = data_view.get_array_size()

        @property
        def occlusionTypesSizes(self):
            data_view = og.AttributeValueHelper(self._attributes.occlusionTypesSizes)
            return data_view.get(reserved_element_count=self.occlusionTypesSizes_size)

        @occlusionTypesSizes.setter
        def occlusionTypesSizes(self, value):
            data_view = og.AttributeValueHelper(self._attributes.occlusionTypesSizes)
            data_view.set(value)
            self.occlusionTypesSizes_size = data_view.get_array_size()

        @property
        def restGlobalTranslations(self):
            data_view = og.AttributeValueHelper(self._attributes.restGlobalTranslations)
            return data_view.get(reserved_element_count=self.restGlobalTranslations_size)

        @restGlobalTranslations.setter
        def restGlobalTranslations(self, value):
            data_view = og.AttributeValueHelper(self._attributes.restGlobalTranslations)
            data_view.set(value)
            self.restGlobalTranslations_size = data_view.get_array_size()

        @property
        def restGlobalTranslationsSizes(self):
            data_view = og.AttributeValueHelper(self._attributes.restGlobalTranslationsSizes)
            return data_view.get(reserved_element_count=self.restGlobalTranslationsSizes_size)

        @restGlobalTranslationsSizes.setter
        def restGlobalTranslationsSizes(self, value):
            data_view = og.AttributeValueHelper(self._attributes.restGlobalTranslationsSizes)
            data_view.set(value)
            self.restGlobalTranslationsSizes_size = data_view.get_array_size()

        @property
        def restLocalRotations(self):
            data_view = og.AttributeValueHelper(self._attributes.restLocalRotations)
            return data_view.get(reserved_element_count=self.restLocalRotations_size)

        @restLocalRotations.setter
        def restLocalRotations(self, value):
            data_view = og.AttributeValueHelper(self._attributes.restLocalRotations)
            data_view.set(value)
            self.restLocalRotations_size = data_view.get_array_size()

        @property
        def restLocalRotationsSizes(self):
            data_view = og.AttributeValueHelper(self._attributes.restLocalRotationsSizes)
            return data_view.get(reserved_element_count=self.restLocalRotationsSizes_size)

        @restLocalRotationsSizes.setter
        def restLocalRotationsSizes(self, value):
            data_view = og.AttributeValueHelper(self._attributes.restLocalRotationsSizes)
            data_view.set(value)
            self.restLocalRotationsSizes_size = data_view.get_array_size()

        @property
        def restLocalTranslations(self):
            data_view = og.AttributeValueHelper(self._attributes.restLocalTranslations)
            return data_view.get(reserved_element_count=self.restLocalTranslations_size)

        @restLocalTranslations.setter
        def restLocalTranslations(self, value):
            data_view = og.AttributeValueHelper(self._attributes.restLocalTranslations)
            data_view.set(value)
            self.restLocalTranslations_size = data_view.get_array_size()

        @property
        def restLocalTranslationsSizes(self):
            data_view = og.AttributeValueHelper(self._attributes.restLocalTranslationsSizes)
            return data_view.get(reserved_element_count=self.restLocalTranslationsSizes_size)

        @restLocalTranslationsSizes.setter
        def restLocalTranslationsSizes(self, value):
            data_view = og.AttributeValueHelper(self._attributes.restLocalTranslationsSizes)
            data_view.set(value)
            self.restLocalTranslationsSizes_size = data_view.get_array_size()

        @property
        def skelName(self):
            data_view = og.AttributeValueHelper(self._attributes.skelName)
            return data_view.get(reserved_element_count=self.skelName_size)

        @skelName.setter
        def skelName(self, value):
            data_view = og.AttributeValueHelper(self._attributes.skelName)
            data_view.set(value)
            self.skelName_size = data_view.get_array_size()

        @property
        def skelPath(self):
            data_view = og.AttributeValueHelper(self._attributes.skelPath)
            return data_view.get(reserved_element_count=self.skelPath_size)

        @skelPath.setter
        def skelPath(self, value):
            data_view = og.AttributeValueHelper(self._attributes.skelPath)
            data_view.set(value)
            self.skelPath_size = data_view.get_array_size()

        @property
        def skeletonJoints(self):
            data_view = og.AttributeValueHelper(self._attributes.skeletonJoints)
            return data_view.get(reserved_element_count=self.skeletonJoints_size)

        @skeletonJoints.setter
        def skeletonJoints(self, value):
            data_view = og.AttributeValueHelper(self._attributes.skeletonJoints)
            data_view.set(value)
            self.skeletonJoints_size = data_view.get_array_size()

        @property
        def skeletonParents(self):
            data_view = og.AttributeValueHelper(self._attributes.skeletonParents)
            return data_view.get(reserved_element_count=self.skeletonParents_size)

        @skeletonParents.setter
        def skeletonParents(self, value):
            data_view = og.AttributeValueHelper(self._attributes.skeletonParents)
            data_view.set(value)
            self.skeletonParents_size = data_view.get_array_size()

        @property
        def skeletonParentsSizes(self):
            data_view = og.AttributeValueHelper(self._attributes.skeletonParentsSizes)
            return data_view.get(reserved_element_count=self.skeletonParentsSizes_size)

        @skeletonParentsSizes.setter
        def skeletonParentsSizes(self, value):
            data_view = og.AttributeValueHelper(self._attributes.skeletonParentsSizes)
            data_view.set(value)
            self.skeletonParentsSizes_size = data_view.get_array_size()

        @property
        def translations2d(self):
            data_view = og.AttributeValueHelper(self._attributes.translations2d)
            return data_view.get(reserved_element_count=self.translations2d_size)

        @translations2d.setter
        def translations2d(self, value):
            data_view = og.AttributeValueHelper(self._attributes.translations2d)
            data_view.set(value)
            self.translations2d_size = data_view.get_array_size()

        @property
        def translations2dSizes(self):
            data_view = og.AttributeValueHelper(self._attributes.translations2dSizes)
            return data_view.get(reserved_element_count=self.translations2dSizes_size)

        @translations2dSizes.setter
        def translations2dSizes(self, value):
            data_view = og.AttributeValueHelper(self._attributes.translations2dSizes)
            data_view.set(value)
            self.translations2dSizes_size = data_view.get_array_size()

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

        @property
        def numSkeletons(self):
            value = self._batchedWriteValues.get(self._attributes.numSkeletons)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.numSkeletons)
                return data_view.get()

        @numSkeletons.setter
        def numSkeletons(self, value):
            self._batchedWriteValues[self._attributes.numSkeletons] = value

        @property
        def skeletonData(self):
            value = self._batchedWriteValues.get(self._attributes.skeletonData)
            if value:
                return value
            else:
                data_view = og.AttributeValueHelper(self._attributes.skeletonData)
                return data_view.get()

        @skeletonData.setter
        def skeletonData(self, value):
            self._batchedWriteValues[self._attributes.skeletonData] = value

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
        self.inputs = OgnGetSkeletonDataDatabase.ValuesForInputs(node, self.attributes.inputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
        self.outputs = OgnGetSkeletonDataDatabase.ValuesForOutputs(node, self.attributes.outputs, dynamic_attributes)
        dynamic_attributes = self.dynamic_attribute_data(node, og.AttributePortType.ATTRIBUTE_PORT_TYPE_STATE)
        self.state = OgnGetSkeletonDataDatabase.ValuesForState(node, self.attributes.state, dynamic_attributes)

    class abi:
        """Class defining the ABI interface for the node type"""

        @staticmethod
        def get_node_type():
            get_node_type_function = getattr(OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS, 'get_node_type', None)
            if callable(get_node_type_function):  # pragma: no cover
                return get_node_type_function()
            return 'omni.replicator.core.OgnGetSkeletonData'

        @staticmethod
        def compute(context, node):
            def database_valid():
                return True
            try:
                per_node_data = OgnGetSkeletonDataDatabase.PER_NODE_DATA[node.node_id()]
                db = per_node_data.get('_db')
                if db is None:
                    db = OgnGetSkeletonDataDatabase(node)
                    per_node_data['_db'] = db
                if not database_valid():
                    per_node_data['_db'] = None
                    return False
            except:
                db = OgnGetSkeletonDataDatabase(node)

            try:
                compute_function = getattr(OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS, 'compute', None)
                if callable(compute_function) and compute_function.__code__.co_argcount > 1:  # pragma: no cover
                    return compute_function(context, node)

                db.inputs._prefetch()
                db.inputs._setting_locked = True
                with og.in_compute():
                    return OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS.compute(db)
            except Exception as error:  # pragma: no cover
                stack_trace = "".join(traceback.format_tb(sys.exc_info()[2].tb_next))
                db.log_error(f'Assertion raised in compute - {error}\n{stack_trace}', add_context=False)
            finally:
                db.inputs._setting_locked = False
                db.outputs._commit()
            return False

        @staticmethod
        def initialize(context, node):
            OgnGetSkeletonDataDatabase._initialize_per_node_data(node)
            initialize_function = getattr(OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS, 'initialize', None)
            if callable(initialize_function):  # pragma: no cover
                initialize_function(context, node)

            per_node_data = OgnGetSkeletonDataDatabase.PER_NODE_DATA[node.node_id()]

            def on_connection_or_disconnection(*args):
                per_node_data['_db'] = None

            node.register_on_connected_callback(on_connection_or_disconnection)
            node.register_on_disconnected_callback(on_connection_or_disconnection)

        @staticmethod
        def initialize_nodes(context, nodes):
            for n in nodes:
                OgnGetSkeletonDataDatabase.abi.initialize(context, n)

        @staticmethod
        def release(node):
            release_function = getattr(OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS, 'release', None)
            if callable(release_function):  # pragma: no cover
                release_function(node)
            OgnGetSkeletonDataDatabase._release_per_node_data(node)

        @staticmethod
        def init_instance(node, graph_instance_id):
            init_instance_function = getattr(OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS, 'init_instance', None)
            if callable(init_instance_function):  # pragma: no cover
                init_instance_function(node, graph_instance_id)

        @staticmethod
        def release_instance(node, graph_instance_id):
            release_instance_function = getattr(OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS, 'release_instance', None)
            if callable(release_instance_function):  # pragma: no cover
                release_instance_function(node, graph_instance_id)
            OgnGetSkeletonDataDatabase._release_per_node_instance_data(node, graph_instance_id)

        @staticmethod
        def update_node_version(context, node, old_version, new_version):
            update_node_version_function = getattr(OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS, 'update_node_version', None)
            if callable(update_node_version_function):  # pragma: no cover
                return update_node_version_function(context, node, old_version, new_version)
            return False

        @staticmethod
        def initialize_type(node_type):
            initialize_type_function = getattr(OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS, 'initialize_type', None)
            needs_initializing = True
            if callable(initialize_type_function):  # pragma: no cover
                needs_initializing = initialize_type_function(node_type)
            if needs_initializing:
                node_type.set_metadata(ogn.MetadataKeys.EXTENSION, "omni.replicator.core")
                node_type.set_metadata(ogn.MetadataKeys.UI_NAME, "Get Skeleton Data")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORIES, "Replicator:Annotators")
                node_type.set_metadata(ogn.MetadataKeys.CATEGORY_DESCRIPTIONS, "Replicator:Annotators,Replicator annotator nodes.")
                node_type.set_metadata(ogn.MetadataKeys.DESCRIPTION, "This node retrieves skeleton data given skeleton prims and camera paramters")
                node_type.set_metadata(ogn.MetadataKeys.LANGUAGE, "Python")
                __hints = node_type.get_scheduling_hints()
                if __hints is not None:
                    __hints.compute_rule = og.eComputeRule.E_ON_REQUEST
                OgnGetSkeletonDataDatabase.INTERFACE.add_to_node_type(node_type)

        @staticmethod
        def on_connection_type_resolve(node):
            on_connection_type_resolve_function = getattr(OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS, 'on_connection_type_resolve', None)
            if callable(on_connection_type_resolve_function):  # pragma: no cover
                on_connection_type_resolve_function(node)

    NODE_TYPE_CLASS = None

    @staticmethod
    def register(node_type_class):
        OgnGetSkeletonDataDatabase.NODE_TYPE_CLASS = node_type_class
        og.register_node_type(OgnGetSkeletonDataDatabase.abi, 2)

    @staticmethod
    def deregister():
        og.deregister_node_type("omni.replicator.core.OgnGetSkeletonData")
