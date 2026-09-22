import os
import omni.kit.test
import omni.graph.core as og
import omni.graph.core.tests as ogts
from omni.graph.core.tests.omnigraph_test_utils import _TestGraphAndNode
from omni.graph.core.tests.omnigraph_test_utils import _test_clear_scene
from omni.graph.core.tests.omnigraph_test_utils import _test_setup_scene
from omni.graph.core.tests.omnigraph_test_utils import _test_verify_scene


class TestOgn(ogts.OmniGraphTestCase):

    async def test_data_access(self):
        from omni.replicator.core.ogn.OgnGetSkeletonDataDatabase import OgnGetSkeletonDataDatabase
        test_file_name = "OgnGetSkeletonDataTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_OgnGetSkeletonData")
        database = OgnGetSkeletonDataDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 2)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:cameraAperture"))
        attribute = test_node.get_attribute("inputs:cameraAperture")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraAperture
        database.inputs.cameraAperture = db_value
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraFisheyeMaxFOV"))
        attribute = test_node.get_attribute("inputs:cameraFisheyeMaxFOV")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraFisheyeMaxFOV
        database.inputs.cameraFisheyeMaxFOV = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraFisheyeNominalHeight"))
        attribute = test_node.get_attribute("inputs:cameraFisheyeNominalHeight")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraFisheyeNominalHeight
        database.inputs.cameraFisheyeNominalHeight = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraFisheyeNominalWidth"))
        attribute = test_node.get_attribute("inputs:cameraFisheyeNominalWidth")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraFisheyeNominalWidth
        database.inputs.cameraFisheyeNominalWidth = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraFisheyeOpticalCentre"))
        attribute = test_node.get_attribute("inputs:cameraFisheyeOpticalCentre")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraFisheyeOpticalCentre
        database.inputs.cameraFisheyeOpticalCentre = db_value
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraFisheyePolynomial"))
        attribute = test_node.get_attribute("inputs:cameraFisheyePolynomial")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraFisheyePolynomial
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraFocalLength"))
        attribute = test_node.get_attribute("inputs:cameraFocalLength")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraFocalLength
        database.inputs.cameraFocalLength = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraModel"))
        attribute = test_node.get_attribute("inputs:cameraModel")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraModel
        database.inputs.cameraModel = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraNearFar"))
        attribute = test_node.get_attribute("inputs:cameraNearFar")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraNearFar
        database.inputs.cameraNearFar = db_value
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraProjection"))
        attribute = test_node.get_attribute("inputs:cameraProjection")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraProjection
        database.inputs.cameraProjection = db_value
        expected_value = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraViewTransform"))
        attribute = test_node.get_attribute("inputs:cameraViewTransform")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.cameraViewTransform
        database.inputs.cameraViewTransform = db_value
        expected_value = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:exec"))
        attribute = test_node.get_attribute("inputs:exec")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.exec
        database.inputs.exec = db_value

        self.assertTrue(test_node.get_attribute_exists("inputs:fabricJoints"))
        attribute = test_node.get_attribute("inputs:fabricJoints")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.fabricJoints
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:fabricPrims"))
        attribute = test_node.get_attribute("inputs:fabricPrims")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.fabricPrims
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationCudaDeviceIndex"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationCudaDeviceIndex")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationCudaDeviceIndex
        database.inputs.instanceSegmentationCudaDeviceIndex = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationHeight"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationHeight")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationHeight
        database.inputs.instanceSegmentationHeight = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationIds"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationIds")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationIds
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationLabels"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationLabels")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationLabels
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationPtr"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationPtr")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationPtr
        database.inputs.instanceSegmentationPtr = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationSemantics"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationSemantics")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationSemantics
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationStrides"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationStrides")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationStrides
        database.inputs.instanceSegmentationStrides = db_value
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:instanceSegmentationWidth"))
        attribute = test_node.get_attribute("inputs:instanceSegmentationWidth")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.instanceSegmentationWidth
        database.inputs.instanceSegmentationWidth = db_value
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:jointWorldOrientations"))
        attribute = test_node.get_attribute("inputs:jointWorldOrientations")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.jointWorldOrientations
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:jointWorldPositions"))
        attribute = test_node.get_attribute("inputs:jointWorldPositions")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.jointWorldPositions
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:jointWorldScales"))
        attribute = test_node.get_attribute("inputs:jointWorldScales")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.jointWorldScales
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:primWorldOrientations"))
        attribute = test_node.get_attribute("inputs:primWorldOrientations")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.primWorldOrientations
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:primWorldPositions"))
        attribute = test_node.get_attribute("inputs:primWorldPositions")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.primWorldPositions
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:primWorldScales"))
        attribute = test_node.get_attribute("inputs:primWorldScales")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.primWorldScales
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:prims"))
        attribute = test_node.get_attribute("inputs:prims")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.prims
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:renderProductPath"))
        attribute = test_node.get_attribute("inputs:renderProductPath")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.renderProductPath
        database.inputs.renderProductPath = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:useSkelJoints"))
        attribute = test_node.get_attribute("inputs:useSkelJoints")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.useSkelJoints
        database.inputs.useSkelJoints = db_value
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("outputs:animationVariant"))
        attribute = test_node.get_attribute("outputs:animationVariant")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.animationVariant

        self.assertTrue(test_node.get_attribute_exists("outputs:assetPath"))
        attribute = test_node.get_attribute("outputs:assetPath")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.assetPath

        self.assertTrue(test_node.get_attribute_exists("outputs:exec"))
        attribute = test_node.get_attribute("outputs:exec")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.exec
        database.outputs.exec = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:globalTranslations"))
        attribute = test_node.get_attribute("outputs:globalTranslations")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.globalTranslations

        self.assertTrue(test_node.get_attribute_exists("outputs:globalTranslationsSizes"))
        attribute = test_node.get_attribute("outputs:globalTranslationsSizes")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.globalTranslationsSizes

        self.assertTrue(test_node.get_attribute_exists("outputs:inView"))
        attribute = test_node.get_attribute("outputs:inView")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.inView

        self.assertTrue(test_node.get_attribute_exists("outputs:jointOcclusions"))
        attribute = test_node.get_attribute("outputs:jointOcclusions")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.jointOcclusions

        self.assertTrue(test_node.get_attribute_exists("outputs:jointOcclusionsSizes"))
        attribute = test_node.get_attribute("outputs:jointOcclusionsSizes")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.jointOcclusionsSizes

        self.assertTrue(test_node.get_attribute_exists("outputs:localRotations"))
        attribute = test_node.get_attribute("outputs:localRotations")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.localRotations

        self.assertTrue(test_node.get_attribute_exists("outputs:localRotationsSizes"))
        attribute = test_node.get_attribute("outputs:localRotationsSizes")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.localRotationsSizes

        self.assertTrue(test_node.get_attribute_exists("outputs:numSkeletons"))
        attribute = test_node.get_attribute("outputs:numSkeletons")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.numSkeletons
        database.outputs.numSkeletons = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:occlusionTypes"))
        attribute = test_node.get_attribute("outputs:occlusionTypes")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.occlusionTypes

        self.assertTrue(test_node.get_attribute_exists("outputs:occlusionTypesSizes"))
        attribute = test_node.get_attribute("outputs:occlusionTypesSizes")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.occlusionTypesSizes

        self.assertTrue(test_node.get_attribute_exists("outputs:restGlobalTranslations"))
        attribute = test_node.get_attribute("outputs:restGlobalTranslations")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.restGlobalTranslations

        self.assertTrue(test_node.get_attribute_exists("outputs:restGlobalTranslationsSizes"))
        attribute = test_node.get_attribute("outputs:restGlobalTranslationsSizes")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.restGlobalTranslationsSizes

        self.assertTrue(test_node.get_attribute_exists("outputs:restLocalRotations"))
        attribute = test_node.get_attribute("outputs:restLocalRotations")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.restLocalRotations

        self.assertTrue(test_node.get_attribute_exists("outputs:restLocalRotationsSizes"))
        attribute = test_node.get_attribute("outputs:restLocalRotationsSizes")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.restLocalRotationsSizes

        self.assertTrue(test_node.get_attribute_exists("outputs:restLocalTranslations"))
        attribute = test_node.get_attribute("outputs:restLocalTranslations")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.restLocalTranslations

        self.assertTrue(test_node.get_attribute_exists("outputs:restLocalTranslationsSizes"))
        attribute = test_node.get_attribute("outputs:restLocalTranslationsSizes")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.restLocalTranslationsSizes

        self.assertTrue(test_node.get_attribute_exists("outputs:skelName"))
        attribute = test_node.get_attribute("outputs:skelName")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.skelName

        self.assertTrue(test_node.get_attribute_exists("outputs:skelPath"))
        attribute = test_node.get_attribute("outputs:skelPath")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.skelPath

        self.assertTrue(test_node.get_attribute_exists("outputs:skeletonData"))
        attribute = test_node.get_attribute("outputs:skeletonData")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.skeletonData
        database.outputs.skeletonData = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:skeletonJoints"))
        attribute = test_node.get_attribute("outputs:skeletonJoints")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.skeletonJoints

        self.assertTrue(test_node.get_attribute_exists("outputs:skeletonParents"))
        attribute = test_node.get_attribute("outputs:skeletonParents")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.skeletonParents

        self.assertTrue(test_node.get_attribute_exists("outputs:skeletonParentsSizes"))
        attribute = test_node.get_attribute("outputs:skeletonParentsSizes")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.skeletonParentsSizes

        self.assertTrue(test_node.get_attribute_exists("outputs:translations2d"))
        attribute = test_node.get_attribute("outputs:translations2d")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.translations2d

        self.assertTrue(test_node.get_attribute_exists("outputs:translations2dSizes"))
        attribute = test_node.get_attribute("outputs:translations2dSizes")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.translations2dSizes
        temp_setting = database.inputs._setting_locked
        database.inputs._testing_sample_value = True
        database.outputs._testing_sample_value = True
        database.inputs._setting_locked = temp_setting
        self.assertTrue(database.inputs._testing_sample_value)
        self.assertTrue(database.outputs._testing_sample_value)
