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
        from isaacsim.robot.wheeled_robots.ogn.OgnAckermannControllerDatabase import OgnAckermannControllerDatabase
        test_file_name = "OgnAckermannControllerTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_isaacsim_robot_wheeled_robots_AckermannController")
        database = OgnAckermannControllerDatabase(test_node)
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 2)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:acceleration"))
        attribute = test_node.get_attribute("inputs:acceleration")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.acceleration
        database.inputs.acceleration = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:backWheelRadius"))
        attribute = test_node.get_attribute("inputs:backWheelRadius")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.backWheelRadius
        database.inputs.backWheelRadius = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:dt"))
        attribute = test_node.get_attribute("inputs:dt")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.dt
        database.inputs.dt = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:execIn"))
        attribute = test_node.get_attribute("inputs:execIn")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.execIn
        database.inputs.execIn = db_value

        self.assertTrue(test_node.get_attribute_exists("inputs:frontWheelRadius"))
        attribute = test_node.get_attribute("inputs:frontWheelRadius")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.frontWheelRadius
        database.inputs.frontWheelRadius = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:invertSteering"))
        attribute = test_node.get_attribute("inputs:invertSteering")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.invertSteering
        database.inputs.invertSteering = db_value
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:maxAcceleration"))
        attribute = test_node.get_attribute("inputs:maxAcceleration")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.maxAcceleration
        database.inputs.maxAcceleration = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:maxSteeringAngleVelocity"))
        attribute = test_node.get_attribute("inputs:maxSteeringAngleVelocity")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.maxSteeringAngleVelocity
        database.inputs.maxSteeringAngleVelocity = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:maxWheelRotation"))
        attribute = test_node.get_attribute("inputs:maxWheelRotation")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.maxWheelRotation
        database.inputs.maxWheelRotation = db_value
        expected_value = 6.28
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:maxWheelVelocity"))
        attribute = test_node.get_attribute("inputs:maxWheelVelocity")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.maxWheelVelocity
        database.inputs.maxWheelVelocity = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:speed"))
        attribute = test_node.get_attribute("inputs:speed")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.speed
        database.inputs.speed = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:steeringAngle"))
        attribute = test_node.get_attribute("inputs:steeringAngle")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.steeringAngle
        database.inputs.steeringAngle = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:steeringAngleVelocity"))
        attribute = test_node.get_attribute("inputs:steeringAngleVelocity")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.steeringAngleVelocity
        database.inputs.steeringAngleVelocity = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:trackWidth"))
        attribute = test_node.get_attribute("inputs:trackWidth")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.trackWidth
        database.inputs.trackWidth = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("inputs:wheelBase"))
        attribute = test_node.get_attribute("inputs:wheelBase")
        self.assertTrue(attribute.is_valid())
        db_value = database.inputs.wheelBase
        database.inputs.wheelBase = db_value
        expected_value = 0.0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))
        ogts.verify_values(expected_value, db_value, _attr_error(attribute, False))

        self.assertTrue(test_node.get_attribute_exists("outputs:execOut"))
        attribute = test_node.get_attribute("outputs:execOut")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.execOut
        database.outputs.execOut = db_value

        self.assertTrue(test_node.get_attribute_exists("outputs:wheelAngles"))
        attribute = test_node.get_attribute("outputs:wheelAngles")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.wheelAngles

        self.assertTrue(test_node.get_attribute_exists("outputs:wheelRotationVelocity"))
        attribute = test_node.get_attribute("outputs:wheelRotationVelocity")
        self.assertTrue(attribute.is_valid())
        db_value = database.outputs.wheelRotationVelocity
        temp_setting = database.inputs._setting_locked
        database.inputs._testing_sample_value = True
        database.outputs._testing_sample_value = True
        database.inputs._setting_locked = temp_setting
        self.assertTrue(database.inputs._testing_sample_value)
        self.assertTrue(database.outputs._testing_sample_value)
