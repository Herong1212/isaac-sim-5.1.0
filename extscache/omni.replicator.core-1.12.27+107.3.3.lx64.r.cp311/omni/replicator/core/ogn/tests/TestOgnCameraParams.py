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
        test_file_name = "OgnCameraParamsTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_CameraParams")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:cameraApertureOffset"))
        attribute = test_node.get_attribute("inputs:cameraApertureOffset")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraApertureSize"))
        attribute = test_node.get_attribute("inputs:cameraApertureSize")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraFStop"))
        attribute = test_node.get_attribute("inputs:cameraFStop")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraFisheyeParams"))
        attribute = test_node.get_attribute("inputs:cameraFisheyeParams")
        self.assertTrue(attribute.is_valid())
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraFocalLength"))
        attribute = test_node.get_attribute("inputs:cameraFocalLength")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraFocusDistance"))
        attribute = test_node.get_attribute("inputs:cameraFocusDistance")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraModel"))
        attribute = test_node.get_attribute("inputs:cameraModel")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraNearFar"))
        attribute = test_node.get_attribute("inputs:cameraNearFar")
        self.assertTrue(attribute.is_valid())
        expected_value = [0.0, 0.0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraOpenCVFx"))
        attribute = test_node.get_attribute("inputs:cameraOpenCVFx")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraOpenCVFy"))
        attribute = test_node.get_attribute("inputs:cameraOpenCVFy")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraProjection"))
        attribute = test_node.get_attribute("inputs:cameraProjection")
        self.assertTrue(attribute.is_valid())
        expected_value = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:cameraViewTransform"))
        attribute = test_node.get_attribute("inputs:cameraViewTransform")
        self.assertTrue(attribute.is_valid())
        expected_value = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:exec"))
        attribute = test_node.get_attribute("inputs:exec")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:isPinholeOpenCV"))
        attribute = test_node.get_attribute("inputs:isPinholeOpenCV")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:metersPerSceneUnit"))
        attribute = test_node.get_attribute("inputs:metersPerSceneUnit")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:renderProductResolution"))
        attribute = test_node.get_attribute("inputs:renderProductResolution")
        self.assertTrue(attribute.is_valid())
        expected_value = [0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraAperture"))
        attribute = test_node.get_attribute("outputs:cameraAperture")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraApertureOffset"))
        attribute = test_node.get_attribute("outputs:cameraApertureOffset")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraFStop"))
        attribute = test_node.get_attribute("outputs:cameraFStop")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraFisheyeLensP"))
        attribute = test_node.get_attribute("outputs:cameraFisheyeLensP")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraFisheyeLensS"))
        attribute = test_node.get_attribute("outputs:cameraFisheyeLensS")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraFisheyeMaxFOV"))
        attribute = test_node.get_attribute("outputs:cameraFisheyeMaxFOV")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraFisheyeNominalHeight"))
        attribute = test_node.get_attribute("outputs:cameraFisheyeNominalHeight")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraFisheyeNominalWidth"))
        attribute = test_node.get_attribute("outputs:cameraFisheyeNominalWidth")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraFisheyeOpticalCentre"))
        attribute = test_node.get_attribute("outputs:cameraFisheyeOpticalCentre")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraFisheyePolynomial"))
        attribute = test_node.get_attribute("outputs:cameraFisheyePolynomial")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraFocalLength"))
        attribute = test_node.get_attribute("outputs:cameraFocalLength")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraFocusDistance"))
        attribute = test_node.get_attribute("outputs:cameraFocusDistance")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraModel"))
        attribute = test_node.get_attribute("outputs:cameraModel")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraNearFar"))
        attribute = test_node.get_attribute("outputs:cameraNearFar")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraOpenCVFx"))
        attribute = test_node.get_attribute("outputs:cameraOpenCVFx")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraOpenCVFy"))
        attribute = test_node.get_attribute("outputs:cameraOpenCVFy")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraProjection"))
        attribute = test_node.get_attribute("outputs:cameraProjection")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:cameraViewTransform"))
        attribute = test_node.get_attribute("outputs:cameraViewTransform")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:exec"))
        attribute = test_node.get_attribute("outputs:exec")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:metersPerSceneUnit"))
        attribute = test_node.get_attribute("outputs:metersPerSceneUnit")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:renderProductResolution"))
        attribute = test_node.get_attribute("outputs:renderProductResolution")
        self.assertTrue(attribute.is_valid())
