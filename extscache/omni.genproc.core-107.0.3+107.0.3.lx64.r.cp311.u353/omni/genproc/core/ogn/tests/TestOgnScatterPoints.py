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
        test_file_name = "OgnScatterPointsTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_genproc_core_ScatterPoints")
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

        self.assertTrue(test_node.get_attribute_exists("inputs:binormals"))
        attribute = test_node.get_attribute("inputs:binormals")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:curveTessellation"))
        attribute = test_node.get_attribute("inputs:curveTessellation")
        self.assertTrue(attribute.is_valid())
        expected_value = 10
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:debugDraw"))
        attribute = test_node.get_attribute("inputs:debugDraw")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:debugDrawCurveTriangulation"))
        attribute = test_node.get_attribute("inputs:debugDrawCurveTriangulation")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:exclusive"))
        attribute = test_node.get_attribute("inputs:exclusive")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:filterUsingCamera"))
        attribute = test_node.get_attribute("inputs:filterUsingCamera")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:normals"))
        attribute = test_node.get_attribute("inputs:normals")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:numDesiredPoints"))
        attribute = test_node.get_attribute("inputs:numDesiredPoints")
        self.assertTrue(attribute.is_valid())
        expected_value = 100
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:objectIndex"))
        attribute = test_node.get_attribute("inputs:objectIndex")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:objectIndexRandom"))
        attribute = test_node.get_attribute("inputs:objectIndexRandom")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:objectIndices"))
        attribute = test_node.get_attribute("inputs:objectIndices")
        self.assertTrue(attribute.is_valid())
        expected_value = True
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

        self.assertTrue(test_node.get_attribute_exists("inputs:prim"))
        attribute = test_node.get_attribute("inputs:prim")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:randomSeed"))
        attribute = test_node.get_attribute("inputs:randomSeed")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:rotation"))
        attribute = test_node.get_attribute("inputs:rotation")
        self.assertTrue(attribute.is_valid())
        expected_value = [0, 0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:rotationRandom"))
        attribute = test_node.get_attribute("inputs:rotationRandom")
        self.assertTrue(attribute.is_valid())
        expected_value = [0, 0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:rotations"))
        attribute = test_node.get_attribute("inputs:rotations")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:scale"))
        attribute = test_node.get_attribute("inputs:scale")
        self.assertTrue(attribute.is_valid())
        expected_value = [5, 5, 5]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:scaleRandom"))
        attribute = test_node.get_attribute("inputs:scaleRandom")
        self.assertTrue(attribute.is_valid())
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:scales"))
        attribute = test_node.get_attribute("inputs:scales")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:scatterAcrossPoints"))
        attribute = test_node.get_attribute("inputs:scatterAcrossPoints")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:scatterInsideVolume"))
        attribute = test_node.get_attribute("inputs:scatterInsideVolume")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:scatterOnSurface"))
        attribute = test_node.get_attribute("inputs:scatterOnSurface")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:tangents"))
        attribute = test_node.get_attribute("inputs:tangents")
        self.assertTrue(attribute.is_valid())
        expected_value = True
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

        self.assertTrue(test_node.get_attribute_exists("inputs:useScatterGeometryAsOcclusionGeometry"))
        attribute = test_node.get_attribute("inputs:useScatterGeometryAsOcclusionGeometry")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("outputs_bundle"))
        attribute = test_node.get_attribute("outputs_bundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("outputs:projectedPoints"))
        attribute = test_node.get_attribute("outputs:projectedPoints")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state_cachedBundle"))
        attribute = test_node.get_attribute("state_cachedBundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevActive"))
        attribute = test_node.get_attribute("state:prevActive")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevBinormals"))
        attribute = test_node.get_attribute("state:prevBinormals")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevCurveTessellation"))
        attribute = test_node.get_attribute("state:prevCurveTessellation")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevExclusive"))
        attribute = test_node.get_attribute("state:prevExclusive")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevFilterUsingCamera"))
        attribute = test_node.get_attribute("state:prevFilterUsingCamera")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevNormals"))
        attribute = test_node.get_attribute("state:prevNormals")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevNumDesiredPoints"))
        attribute = test_node.get_attribute("state:prevNumDesiredPoints")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevObjectIndex"))
        attribute = test_node.get_attribute("state:prevObjectIndex")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevObjectIndexRandom"))
        attribute = test_node.get_attribute("state:prevObjectIndexRandom")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevObjectIndices"))
        attribute = test_node.get_attribute("state:prevObjectIndices")
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

        self.assertTrue(test_node.get_attribute_exists("state:prevRotation"))
        attribute = test_node.get_attribute("state:prevRotation")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevRotationRandom"))
        attribute = test_node.get_attribute("state:prevRotationRandom")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevRotations"))
        attribute = test_node.get_attribute("state:prevRotations")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevScale"))
        attribute = test_node.get_attribute("state:prevScale")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevScaleRandom"))
        attribute = test_node.get_attribute("state:prevScaleRandom")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevScales"))
        attribute = test_node.get_attribute("state:prevScales")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevScatterAcrossPoints"))
        attribute = test_node.get_attribute("state:prevScatterAcrossPoints")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevScatterInsideVolume"))
        attribute = test_node.get_attribute("state:prevScatterInsideVolume")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevScatterOnSurface"))
        attribute = test_node.get_attribute("state:prevScatterOnSurface")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevTangents"))
        attribute = test_node.get_attribute("state:prevTangents")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevTime"))
        attribute = test_node.get_attribute("state:prevTime")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevUsdTimecode"))
        attribute = test_node.get_attribute("state:prevUsdTimecode")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevUseScatterGeometryAsOcclusionGeometry"))
        attribute = test_node.get_attribute("state:prevUseScatterGeometryAsOcclusionGeometry")
        self.assertTrue(attribute.is_valid())
