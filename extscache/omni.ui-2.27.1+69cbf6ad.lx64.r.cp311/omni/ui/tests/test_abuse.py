# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ui as ui
import omni.kit.app
from .test_base import OmniUiTest


# *************** WARNING ***************
#
# NONE OF THE API USAGE OR PATTERNS IN THIS FILE SHOULD BE CONSIDERED GOOD
# THESE ARE TESTS ONLY THAT THAT APPLICATION WILL NOT CRASH WHEN APIS MISUSED
#

class SimpleIntModel(ui.SimpleIntModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_value(self, *args, **kwargs):
        super().set_value(*args, **kwargs)
        super()._value_changed()


class SimpleItem(ui.AbstractItem):
    def __init__(self, value: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name_model = ui.SimpleStringModel(value)


class SimpleItemModel(ui.AbstractItemModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__items = []

    def destroy(self):
        self.__items = []

    def get_item_children(self, item: SimpleItem):
        if item is None:
            return self.__items
        return []

    def add_item(self, item: SimpleItem):
        self.__items.append(item)
        super()._item_changed(None)

    def get_item_value_model_count(self, item: SimpleItem):
        return 1

    def get_item_value_model(self, item: SimpleItem, column_id: int):
        return item.name_model if item else None


class TestAbuse(OmniUiTest):
    """Testing omni.ui callbacks do not crash"""

    async def __cleanup_window(self, window: omni.ui.Window):
        window.visible = False
        window.destroy()
        await self.finalize_test_no_image()
        return None

    async def test_empty_models_1(self):
        """Test that setting an empty model on ui objects does not crash"""
        window = await self.create_test_window(block_devices=False)
        app = omni.kit.app.get_app()

        with window.frame:
            with ui.VStack():
                items = [
                    ui.CheckBox(),
                    ui.ComboBox(),
                    ui.FloatField(),
                    ui.FloatSlider(),
                    ui.IntField(),
                    ui.IntSlider(),
                    ui.ProgressBar(),
                    ui.StringField(),
                    ui.ToolButton(),
                ]

        for _ in range(5):
            await app.next_update_async()

        for item in items:
            item.model = None

        for _ in range(5):
            await app.next_update_async()

        window = await self.__cleanup_window(window)

    async def test_empty_models_2(self):
        """Test that setting an empty model on ui objects does not crash"""
        window = await self.create_test_window()
        app = omni.kit.app.get_app()
        model = ui.SimpleBoolModel()
        with window.frame:
            with ui.VStack():
                items = [
                    ui.ToolButton(model=model),
                    ui.CheckBox(model=model),
                    ui.ComboBox(model=model),
                    ui.FloatField(model=model),
                    ui.FloatSlider(model=model),
                    ui.IntField(model=model),
                    ui.IntSlider(model=model),
                    ui.ProgressBar(model=model),
                    ui.StringField(model=model),
                ]

        model.set_value(True)

        for _ in range(5):
            await app.next_update_async()

        def check_changed(*args):
            # This slice is important to keep another crash from occuring by keeping at least on subscriber alive
            for i in range(1, len(items)):
                items[i].model = None

        items[0].set_checked_changed_fn(check_changed)
        model.set_value(False)

        for _ in range(5):
            await app.next_update_async()

        window = await self.__cleanup_window(window)

    async def test_workspace_window_visibility_changed(self):
        """Test that subscribe and unsubscribe to window visiblity will not crash"""
        await self.create_test_area()
        sub_1, sub_2 = None, None

        def window_visibility_callback_2(*args, **kwargs):
            nonlocal sub_1, sub_2
            ui.Workspace.remove_window_visibility_changed_callback(sub_1)
            ui.Workspace.remove_window_visibility_changed_callback(sub_2)

        def window_visibility_callback_1(*args, **kwargs):
            nonlocal sub_2
            if sub_2 is None:
                sub_2 = ui.Workspace.set_window_visibility_changed_callback(window_visibility_callback_2)

        sub_1 = ui.Workspace.set_window_visibility_changed_callback(window_visibility_callback_1)

        self.assertIsNotNone(sub_1)

        window_1 = ui.Window("window_1", width=100, height=100)
        self.assertIsNotNone(window_1)
        self.assertIsNotNone(sub_2)

        window_1.visible = False

        # Test against unsubscibing multiple times
        for _ in range(10):
            ui.Workspace.remove_window_visibility_changed_callback(sub_1)
            ui.Workspace.remove_window_visibility_changed_callback(sub_2)

        for idx in range(64):
            ui.Workspace.remove_window_visibility_changed_callback(idx)

        window_1 = await self.__cleanup_window(window_1)

    async def test_value_model_changed_subscriptions(self):
        """Test that subscribe and unsubscribe to ui.AbstractValueModel will not crash"""

        def null_callback(*args, **kwargs):
            pass
        model_a = SimpleIntModel()

        model_a.remove_value_changed_fn(64)
        sub_id = model_a.add_value_changed_fn(null_callback)
        for _ in range(4):
            model_a.remove_value_changed_fn(sub_id)

        model_a.remove_begin_edit_fn(64)
        sub_id = model_a.add_begin_edit_fn(null_callback)
        for _ in range(4):
            model_a.remove_begin_edit_fn(sub_id)

        model_a.remove_end_edit_fn(64)
        sub_id = model_a.add_end_edit_fn(null_callback)
        for _ in range(4):
            model_a.remove_end_edit_fn(sub_id)

    async def test_item_model_changed_subscriptions(self):
        """Test that subscribe and unsubscribe to ui.AbstractItemModel will not crash"""

        def null_callback(*args, **kwargs):
            pass
        model_a = SimpleItemModel()

        model_a.remove_item_changed_fn(64)
        sub_id = model_a.add_item_changed_fn(null_callback)
        for _ in range(4):
            model_a.remove_item_changed_fn(sub_id)

        model_a.remove_begin_edit_fn(64)
        sub_id = model_a.add_begin_edit_fn(null_callback)
        for _ in range(4):
            model_a.remove_begin_edit_fn(sub_id)

        model_a.remove_end_edit_fn(64)
        sub_id = model_a.add_end_edit_fn(null_callback)
        for _ in range(4):
            model_a.remove_end_edit_fn(sub_id)
