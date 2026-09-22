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
        test_file_name = "OgnScatterPointsGroupTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_genproc_core_ScatterPointsGroup")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:active"))
        attribute = test_node.get_attribute("inputs:active")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:curveStepsPerSegment"))
        attribute = test_node.get_attribute("inputs:curveStepsPerSegment")
        self.assertTrue(attribute.is_valid())
        expected_value = 10
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:filterUsingCamera"))
        attribute = test_node.get_attribute("inputs:filterUsingCamera")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:frustumOffset"))
        attribute = test_node.get_attribute("inputs:frustumOffset")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:groups"))
        attribute = test_node.get_attribute("inputs:groups")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:objectIndicesRampInterpolations"))
        attribute = test_node.get_attribute("inputs:objectIndicesRampInterpolations")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:objectIndicesRampPositions"))
        attribute = test_node.get_attribute("inputs:objectIndicesRampPositions")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:objectIndicesRampTags"))
        attribute = test_node.get_attribute("inputs:objectIndicesRampTags")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:objectIndicesRampValues"))
        attribute = test_node.get_attribute("inputs:objectIndicesRampValues")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:playbackEvaluation"))
        attribute = test_node.get_attribute("inputs:playbackEvaluation")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:playbackStartFrame"))
        attribute = test_node.get_attribute("inputs:playbackStartFrame")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:prototypes"))
        attribute = test_node.get_attribute("inputs:prototypes")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:randomSeed"))
        attribute = test_node.get_attribute("inputs:randomSeed")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:time"))
        attribute = test_node.get_attribute("inputs:time")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:usdTimecode"))
        attribute = test_node.get_attribute("inputs:usdTimecode")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:weightsRampInterpolations"))
        attribute = test_node.get_attribute("inputs:weightsRampInterpolations")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:weightsRampPositions"))
        attribute = test_node.get_attribute("inputs:weightsRampPositions")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:weightsRampValues"))
        attribute = test_node.get_attribute("inputs:weightsRampValues")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs_bundle"))
        attribute = test_node.get_attribute("outputs_bundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state_cachedBaseMeshes"))
        attribute = test_node.get_attribute("state_cachedBaseMeshes")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state_cachedCurveSources"))
        attribute = test_node.get_attribute("state_cachedCurveSources")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state_cachedVolumeSources"))
        attribute = test_node.get_attribute("state_cachedVolumeSources")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevActive"))
        attribute = test_node.get_attribute("state:prevActive")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevCurveStepsPerSegment"))
        attribute = test_node.get_attribute("state:prevCurveStepsPerSegment")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevFilterUsingCamera"))
        attribute = test_node.get_attribute("state:prevFilterUsingCamera")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevFrustumOffset"))
        attribute = test_node.get_attribute("state:prevFrustumOffset")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevObjectIndicesRampInterpolations"))
        attribute = test_node.get_attribute("state:prevObjectIndicesRampInterpolations")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevObjectIndicesRampPositions"))
        attribute = test_node.get_attribute("state:prevObjectIndicesRampPositions")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevObjectIndicesRampValues"))
        attribute = test_node.get_attribute("state:prevObjectIndicesRampValues")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevPlaybackEvaluation"))
        attribute = test_node.get_attribute("state:prevPlaybackEvaluation")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevPlaybackStartFrame"))
        attribute = test_node.get_attribute("state:prevPlaybackStartFrame")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevRandomSeed"))
        attribute = test_node.get_attribute("state:prevRandomSeed")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevTime"))
        attribute = test_node.get_attribute("state:prevTime")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevUsdTimecode"))
        attribute = test_node.get_attribute("state:prevUsdTimecode")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevWeightsRampInterpolations"))
        attribute = test_node.get_attribute("state:prevWeightsRampInterpolations")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevWeightsRampPositions"))
        attribute = test_node.get_attribute("state:prevWeightsRampPositions")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevWeightsRampValues"))
        attribute = test_node.get_attribute("state:prevWeightsRampValues")
        self.assertTrue(attribute.is_valid())
