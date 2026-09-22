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
        from omni.replicator.core.ogn.OgnMeshDecalDatabase import OgnMeshDecalDatabase
        test_file_name = "OgnMeshDecalTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_replicator_core_OgnMeshDecal")
        database = OgnMeshDecalDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:decalPrim"))
        attribute = test_node.get_attribute("inputs:decalPrim")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.decalPrim

        self.assertTrue(test_node.get_attribute_exists("inputs:diffuse"))
        attribute = test_node.get_attribute("inputs:diffuse")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.diffuse
        database.inputs.diffuse = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:execIn"))
        attribute = test_node.get_attribute("inputs:execIn")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.execIn
        database.inputs.execIn = db_value

        self.assertTrue(test_node.get_attribute_exists("inputs:materialPrim"))
        attribute = test_node.get_attribute("inputs:materialPrim")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.materialPrim

        self.assertTrue(test_node.get_attribute_exists("inputs:metallic"))
        attribute = test_node.get_attribute("inputs:metallic")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.metallic
        database.inputs.metallic = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:normal"))
        attribute = test_node.get_attribute("inputs:normal")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.normal
        database.inputs.normal = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:offsetDepth"))
        attribute = test_node.get_attribute("inputs:offsetDepth")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.offsetDepth
        database.inputs.offsetDepth = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:offsetNormal"))
        attribute = test_node.get_attribute("inputs:offsetNormal")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.offsetNormal
        database.inputs.offsetNormal = db_value
        expected_value = 0.1
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:opacity"))
        attribute = test_node.get_attribute("inputs:opacity")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.opacity
        database.inputs.opacity = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:position"))
        attribute = test_node.get_attribute("inputs:position")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.position
        database.inputs.position = db_value
        expected_value = [0, 0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:prims"))
        attribute = test_node.get_attribute("inputs:prims")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.prims

        self.assertTrue(test_node.get_attribute_exists("inputs:rotation"))
        attribute = test_node.get_attribute("inputs:rotation")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.rotation
        database.inputs.rotation = db_value
        expected_value = [0, 0, 0]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:roughness"))
        attribute = test_node.get_attribute("inputs:roughness")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.roughness
        database.inputs.roughness = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:scale"))
        attribute = test_node.get_attribute("inputs:scale")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.scale
        database.inputs.scale = db_value
        expected_value = [1, 1, 1]
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:semantics"))
        attribute = test_node.get_attribute("inputs:semantics")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.semantics
        database.inputs.semantics = db_value
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:textureGroup"))
        attribute = test_node.get_attribute("inputs:textureGroup")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.textureGroup
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
