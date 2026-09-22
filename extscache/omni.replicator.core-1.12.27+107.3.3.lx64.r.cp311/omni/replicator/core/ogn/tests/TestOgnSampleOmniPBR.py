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
        from omni.replicator.core.ogn.OgnSampleOmniPBRDatabase import OgnSampleOmniPBRDatabase
        test_file_name = "OgnSampleOmniPBRTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_OgnSampleOmniPBR")
        database = OgnSampleOmniPBRDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:diffuse"))
        attribute = test_node.get_attribute("inputs:diffuse")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.diffuse
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:diffuseTexture"))
        attribute = test_node.get_attribute("inputs:diffuseTexture")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.diffuseTexture
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:execIn"))
        attribute = test_node.get_attribute("inputs:execIn")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.execIn
        database.inputs.execIn = db_value

        self.assertTrue(test_node.get_attribute_exists("inputs:metallic"))
        attribute = test_node.get_attribute("inputs:metallic")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.metallic
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:metallicTexture"))
        attribute = test_node.get_attribute("inputs:metallicTexture")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.metallicTexture
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:mode"))
        attribute = test_node.get_attribute("inputs:mode")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.mode
        database.inputs.mode = db_value
        expected_value = "prims"
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:prims"))
        attribute = test_node.get_attribute("inputs:prims")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.prims

        self.assertTrue(test_node.get_attribute_exists("inputs:projectUVW"))
        attribute = test_node.get_attribute("inputs:projectUVW")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.projectUVW
        database.inputs.projectUVW = db_value
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:roughness"))
        attribute = test_node.get_attribute("inputs:roughness")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.roughness
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:roughnessTexture"))
        attribute = test_node.get_attribute("inputs:roughnessTexture")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.roughnessTexture
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:textureRotate"))
        attribute = test_node.get_attribute("inputs:textureRotate")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.textureRotate
        expected_value = []
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:textureScale"))
        attribute = test_node.get_attribute("inputs:textureScale")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.textureScale
        expected_value = []
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
