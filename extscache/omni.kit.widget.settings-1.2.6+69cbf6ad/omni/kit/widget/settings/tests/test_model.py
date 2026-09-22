import collections

import omni.kit.test
import carb.settings
from ..settings_model import VectorFloatSettingsModel, RadioButtonSettingModel, SettingsComboItemModel


class TestModel(omni.kit.test.AsyncTestCase):
    async def test_vector_model(self):

        setting_name = "/rtx/pathtracing/maxBlah"
        settings = carb.settings.get_settings()

        initial_vals = (0.6, 0.7, 0.8)
        settings.set(setting_name, initial_vals)

        vector_model = VectorFloatSettingsModel(setting_name, 3, True)

        # Lets simulate a bit of what the color widget would do when getting values
        sub_items = vector_model.get_item_children(None)
        for cnt, sub_item in enumerate(sub_items):
            sub_model = vector_model.get_item_value_model(sub_item)
            val = sub_model.get_value_as_float()
            self.assertTrue(val == initial_vals[cnt])

        # Lets check if things work when we change the value
        new_vals = (0.5, 0.4, 0.3)
        settings.set(setting_name, new_vals)
        for cnt, sub_item in enumerate(sub_items):
            sub_model = vector_model.get_item_value_model(sub_item)
            val = sub_model.get_value_as_float()
            self.assertTrue(val == new_vals[cnt])

        # Let's set the value through the item model
        new_vals = [0.1, 0.15, 0.2]
        for cnt, sub_item in enumerate(sub_items):
            sub_model = vector_model.get_item_value_model(sub_item)
            val = sub_model.set_value(new_vals[cnt])
        settings_val = settings.get(setting_name)
        self.assertTrue(settings_val == new_vals)

        # Let's set the value directly through the Vector model
        new_vals = [0.2, 0.8, 0.9]
        vector_model.set_value(new_vals)
        settings_val = settings.get(setting_name)
        self.assertTrue(settings_val == new_vals)

        # TODO test begin_edit/end_edit
        # TODO test other sizes (2, 4 components
        # TODO test immediate mode on/off

    async def test_radio_button_setting_model(self):
        setting_value_path = "/ext/ui/settings/radiobutton/value"
        setting_items_path = "/ext/ui/settings/radiobutton/items"
        settings = carb.settings.get_settings()

        initial_val = "option1"
        items = ("option0", "option1", "option2", "option3")

        settings.set(setting_value_path, initial_val)
        settings.set(setting_items_path, items)

        radio_button_model = RadioButtonSettingModel(setting_value_path)

        # Lets check the initial_val and items
        self.assertEqual(radio_button_model.items, items)
        self.assertEqual(radio_button_model.get_value(), initial_val)
        self.assertEqual(radio_button_model.get_value_as_int(), 1)

        # Lets check if things work when we change the value
        # Set as int
        new_val = "option0"
        radio_button_model.set_value(0)
        self.assertEqual(radio_button_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path), new_val)
        self.assertEqual(radio_button_model.get_value_as_int(), 0)

        # Set as str
        new_val = "option2"
        radio_button_model.set_value(new_val)
        self.assertEqual(radio_button_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path), new_val)
        self.assertEqual(radio_button_model.get_value_as_int(), 2)

        # Let's set the value through settings
        new_val = "option3"
        settings.set(setting_value_path, new_val)
        self.assertEqual(radio_button_model.get_value(), new_val)
        self.assertEqual(radio_button_model.get_value_as_int(), 3)

    async def test_combobox_setting_model(self):
        setting_value_path = "/ext/ui/settings/combobox/value"
        settings = carb.settings.get_settings()

        initial_val = "option1"
        items = {"Option0": "option0", "Option1": "option1", "Option2": "option2", "Option3": "option3"}

        settings.set(setting_value_path, initial_val)

        combobox_model = SettingsComboItemModel(setting_value_path, items, setting_is_index=False)

        # Lets check the initial_val and items
        self.assertEqual(combobox_model.get_value(), initial_val)
        self.assertEqual(combobox_model.get_value_as_string(), "Option1")  # Label

        # Lets check if things work when we change the value
        # Set as value
        new_val = "option0"
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path), new_val)  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "Option0")  # Label

        # Set as label
        new_val = "Option2"
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), "option2")
        self.assertEqual(settings.get(setting_value_path), "option2")  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "Option2")  # Label

        # Let's set the value through settings
        new_val = "option3"
        settings.set(setting_value_path, new_val)
        self.assertEqual(combobox_model.get_value(), new_val)  # Check if value of model got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "Option3")  # Label

        # Test list case; setting_is_index=True (ordered dict)
        setting_value_path_int = "/ext/ui/settings/combobox_int/value"
        items = ("option0", "option1", "option2", "option3")
        items = collections.OrderedDict(zip(items, range(0, len(items))))
        initial_val = 1
        settings.set(setting_value_path_int, initial_val)

        combobox_model = SettingsComboItemModel(setting_value_path_int, items, setting_is_index=True)

        # Lets check the initial_val and items
        self.assertEqual(combobox_model.get_value(), initial_val)
        self.assertEqual(combobox_model.get_value_as_string(), "option1")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 1)  # index

        # Lets check if things work when we change the value
        # Set as value
        new_val = 0
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path_int), new_val)  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "option0")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 0)  # index

        # Set as label
        new_val = "option2"
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), 2)
        self.assertEqual(settings.get(setting_value_path_int), 2)  # Check if the carb setting got updated, too; as index
        self.assertEqual(combobox_model.get_value_as_string(), "option2")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 2)  # index

        # Let's set the value through settings
        new_val = 3
        settings.set(setting_value_path_int, new_val)
        self.assertEqual(combobox_model.get_value(), new_val)  # Check if value of model got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "option3")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 3)  # index

        # Test list case; setting_is_index=False (ordered dict) and value is int
        setting_value_path_int = "/ext/ui/settings/combobox_int/value"
        items = ("option0", "option1", "option2", "option3")
        items = collections.OrderedDict(zip(items, range(0, len(items))))
        initial_val = 1
        settings.set(setting_value_path_int, initial_val)

        combobox_model = SettingsComboItemModel(setting_value_path_int, items, setting_is_index=False)

        # Lets check the initial_val and items
        self.assertEqual(combobox_model.get_value(), initial_val)
        self.assertEqual(combobox_model.get_value_as_string(), "option1")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 1)  # index

        # Lets check if things work when we change the value
        # Set as value
        new_val = 0
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path_int), new_val)  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "option0")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 0)  # index

        # Set as label
        new_val = "option2"
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), 2)
        self.assertEqual(settings.get(setting_value_path_int), 2)  # Check if the carb setting got updated, too; as index
        self.assertEqual(combobox_model.get_value_as_string(), "option2")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 2)  # index

        # Let's set the value through settings
        new_val = 3
        settings.set(setting_value_path_int, new_val)
        self.assertEqual(combobox_model.get_value(), new_val)  # Check if value of model got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "option3")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 3)  # index

        # Test list case; setting_is_index=False (Regular dict)
        items = ("option0", "option1", "option2", "option3")
        items = dict(zip(items, items))
        initial_val = "option1"
        settings.set(setting_value_path, initial_val)

        combobox_model = SettingsComboItemModel(setting_value_path, items, setting_is_index=False)

        # Lets check the initial_val and items
        self.assertEqual(combobox_model.get_value(), initial_val)
        self.assertEqual(combobox_model.get_value_as_string(), "option1")  # Label

        # Lets check if things work when we change the value
        # Set as value
        new_val = "option0"
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path), new_val)  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "option0")  # Label

        # Set as label
        new_val = "option2"
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path), new_val)  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "option2")  # Label

        # Let's set the value through settings
        new_val = "option3"
        settings.set(setting_value_path, new_val)
        self.assertEqual(combobox_model.get_value(), new_val)  # Check if value of model got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "option3")  # Label

        # Test list case; setting_is_index=False (ordered dict) and value is bool
        setting_value_path_bool = "/ext/ui/settings/combobox_bool/value"
        items = {True: True, False: False}
        initial_val = False
        settings.set(setting_value_path_bool, initial_val)

        combobox_model = SettingsComboItemModel(setting_value_path_bool, items, setting_is_index=False)

        # Lets check the initial_val and items
        self.assertEqual(combobox_model.get_value(), initial_val)
        self.assertEqual(combobox_model.get_value_as_string(), "False")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 1)  # index

        # Lets check if things work when we change the value
        # Set as value
        new_val = True
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path_bool), new_val)  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "True")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 0)  # index

        # Let's set the value through settings
        new_val = False
        settings.set(setting_value_path_bool, new_val)
        self.assertEqual(combobox_model.get_value(), new_val)  # Check if value of model got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "False")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 1)  # index

        # Test list case; setting_is_index=True (ordered dict) and value is int
        setting_value_path_int = "/ext/ui/settings/combobox_int/value"
        items = (True, False)
        items = collections.OrderedDict(zip(items, range(0, len(items))))
        initial_val = 1
        settings.set(setting_value_path_int, initial_val)

        combobox_model = SettingsComboItemModel(setting_value_path_int, items, setting_is_index=False)

        # Lets check the initial_val and items
        self.assertEqual(combobox_model.get_value(), initial_val)
        self.assertEqual(combobox_model.get_value_as_string(), "False")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 1)  # index

        # Lets check if things work when we change the value
        # Set as value
        new_val = 0
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path_int), new_val)  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "True")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 0)  # index

        # Let's set the value through settings
        new_val = 1
        settings.set(setting_value_path_int, new_val)
        self.assertEqual(combobox_model.get_value(), new_val)  # Check if value of model got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "False")  # Label
        self.assertEqual(combobox_model.get_value_as_int(), 1)  # index

        # Iterate all items and set them
        # Test list case; setting_is_index=False (Regular dict)
        items = ("option0", "option1", "option2", "option3")
        items = dict(zip(items, items))
        initial_val = "option1"
        settings.set(setting_value_path, initial_val)

        combobox_model = SettingsComboItemModel(setting_value_path, items, setting_is_index=False)
        index_model = combobox_model.get_item_value_model(None, 0)
        item_list = combobox_model.get_item_children(None)
        for _, item in enumerate(item_list):
            index_model.set_value(item.model.value)
            self.assertEqual(settings.get(setting_value_path), item.model.value)

        # Iterate all items and set them
        # Test list case; setting_is_index=True (Regular dict)
        items = ("option0", "option1", "option2", "option3")
        items = collections.OrderedDict(zip(items, range(0, len(items))))
        initial_val = 1
        settings.set(setting_value_path_int, initial_val)

        combobox_model = SettingsComboItemModel(setting_value_path_int, items, setting_is_index=False)
        index_model = combobox_model.get_item_value_model(None, 0)
        item_list = combobox_model.get_item_children(None)
        for _, item in enumerate(item_list):
            index_model.set_value(item.model.value)
            self.assertEqual(settings.get(setting_value_path_int), item.model.value)

    async def test_combobox_setting_model_reset(self):
        setting_value_path = "/ext/ui/settings/combobox/value"
        settings = carb.settings.get_settings()

        initial_val = "option1"
        items = {"Option0": "option0", "Option1": "option1", "Option2": "option2", "Option3": "option3"}

        settings.set(setting_value_path, initial_val)

        combobox_model = SettingsComboItemModel(setting_value_path, items, setting_is_index=False)

        # Lets check the initial_val and items
        self.assertEqual(combobox_model.get_value(), initial_val)
        self.assertEqual(combobox_model.get_value_as_string(), "Option1")  # Label

        # Lets check if things work when we change the value
        # Set as value
        new_val = "option3"
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path), new_val)  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "Option3")  # Label

        # reset value
        settings.set(setting_value_path, initial_val)
        self.assertEqual(combobox_model.get_value(), initial_val)
        self.assertEqual(settings.get(setting_value_path), initial_val)  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "Option1")  # Label

        # change again
        # Lets check if things work when we change the value
        # Set as value
        new_val = "option2"
        combobox_model.set_value(new_val)
        self.assertEqual(combobox_model.get_value(), new_val)
        self.assertEqual(settings.get(setting_value_path), new_val)  # Check if the carb setting got updated, too
        self.assertEqual(combobox_model.get_value_as_string(), "Option2")  # Label
