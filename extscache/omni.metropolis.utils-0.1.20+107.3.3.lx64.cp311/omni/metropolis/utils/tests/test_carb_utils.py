import omni.kit
import omni.kit.test
import omni.usd
import carb
from omni.metropolis.utils.carb_util import CarbSettingUtil, CarbSettingProperty, CarbSettingMeta


class TestCartbUtils(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_carb_setting_helper(self):
        """
        Test customized properties and metaclass definition
        """

        # Initialize a template setting group
        class TestSetting(metaclass=CarbSettingMeta):
            """template class to test customized carb settings"""

            # test the persistent variables
            cat_name = CarbSettingProperty(default_value="poor cat without name.")
            # test the normal variables
            cat_sound = CarbSettingProperty(
                default_value="meow", is_persistent=True
            )  # by default it is not a persistant variable

        my_cat_name = TestSetting.cat_name
        self.assertEqual(my_cat_name, "poor cat without name.")
        generated_setting_path = TestSetting.get_setting_path(
            "cat_name"
        )  # fetch the carb setting path matched with the value
        # help developer to check and debug
        carb.log_warn(f"This is the carb setting path generated from carb setting properties{generated_setting_path}")
        # test whether the setting path is in snake style
        expected_setting_path = "/exts/omni.metropolis.utils.tests/test_setting/cat_name"
        self.assertEqual(expected_setting_path, generated_setting_path)
        # change the value from the carb setting util functions
        CarbSettingUtil.set_value_by_key(key=generated_setting_path, new_value="Leo")  # assign new value
        my_cat_name = TestSetting.cat_name
        self.assertEqual(my_cat_name, "Leo")  # check whether the updated name can be fetch successfully
        # test the oppsite way
        TestSetting.cat_name = "leo"  # lowercase
        my_cat_name = CarbSettingUtil.get_value_by_key(key=generated_setting_path, fallback_value="Tom")
        self.assertEqual(my_cat_name, "leo")
        # test remove the value
        TestSetting.remove_setting_property(property_name="cat_name")
        is_cat_avaialble = hasattr(TestSetting, "cat_name")
        self.assertFalse(is_cat_avaialble)
        # test whether the related carb setting path is removed successfully
        is_cat_avaialble = CarbSettingUtil.has_key(key=generated_setting_path)
        self.assertFalse(is_cat_avaialble)

        # check the path of the persistant value
        generated_setting_path = TestSetting.get_setting_path(
            "cat_sound"
        )  # fetch the carb setting path matched with the value
        expected_setting_path = "/persistent/exts/omni.metropolis.utils.tests/test_setting/cat_sound"
        self.assertEqual(generated_setting_path, expected_setting_path)
        # clean the setting values
        TestSetting.remove_setting_property(property_name="cat_sound")
