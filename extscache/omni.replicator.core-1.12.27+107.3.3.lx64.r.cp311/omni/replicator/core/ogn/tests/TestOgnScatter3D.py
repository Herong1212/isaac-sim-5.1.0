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
        from omni.replicator.core.ogn.OgnScatter3DDatabase import OgnScatter3DDatabase
        test_file_name = "OgnScatter3DTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_OgnScatter3D")
        database = OgnScatter3DDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:checkForCollisions"))
        attribute = test_node.get_attribute("inputs:checkForCollisions")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.checkForCollisions
        database.inputs.checkForCollisions = db_value
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:execIn"))
        attribute = test_node.get_attribute("inputs:execIn")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.execIn
        database.inputs.execIn = db_value

        self.assertTrue(test_node.get_attribute_exists("inputs:maxSamp"))
        attribute = test_node.get_attribute("inputs:maxSamp")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.maxSamp
        database.inputs.maxSamp = db_value
        expected_value = [3.4028235e+38, 3.4028235e+38, 3.4028235e+38]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:minSamp"))
        attribute = test_node.get_attribute("inputs:minSamp")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.minSamp
        database.inputs.minSamp = db_value
        expected_value = [-3.4028235e+38, -3.4028235e+38, -3.4028235e+38]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:noCollPrims"))
        attribute = test_node.get_attribute("inputs:noCollPrims")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.noCollPrims

        self.assertTrue(test_node.get_attribute_exists("inputs:preventVolOverlap"))
        attribute = test_node.get_attribute("inputs:preventVolOverlap")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.preventVolOverlap
        database.inputs.preventVolOverlap = db_value
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:prims"))
        attribute = test_node.get_attribute("inputs:prims")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.prims

        self.assertTrue(test_node.get_attribute_exists("inputs:resolutionScaling"))
        attribute = test_node.get_attribute("inputs:resolutionScaling")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.resolutionScaling
        database.inputs.resolutionScaling = db_value
        expected_value = 1.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:seed"))
        attribute = test_node.get_attribute("inputs:seed")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.seed
        database.inputs.seed = db_value
        expected_value = -1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:vizSampledVoxels"))
        attribute = test_node.get_attribute("inputs:vizSampledVoxels")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.vizSampledVoxels
        database.inputs.vizSampledVoxels = db_value
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:volumeExclPrims"))
        attribute = test_node.get_attribute("inputs:volumeExclPrims")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.volumeExclPrims

        self.assertTrue(test_node.get_attribute_exists("inputs:volumePrims"))
        attribute = test_node.get_attribute("inputs:volumePrims")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.volumePrims

        self.assertTrue(test_node.get_attribute_exists("inputs:voxelSize"))
        attribute = test_node.get_attribute("inputs:voxelSize")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.voxelSize
        database.inputs.voxelSize = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("outputs:execOut"))
        attribute = test_node.get_attribute("outputs:execOut")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.execOut
        database.outputs.execOut = db_value
        temp_setting = database.inputs._setting_locked
        database.inputs._testing_sample_value = True
        database.outputs._testing_sample_value = True
        database.inputs._setting_locked = temp_setting
        self.assertTrue(database.inputs._testing_sample_value)
        self.assertTrue(database.outputs._testing_sample_value)
