# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from pathlib import Path

import omni.kit.app
import omni.ui as ui
from omni.kit import ui_test
from omni.ui.tests.test_base import OmniUiTest


class TestPropertyWindow(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        self._golden_img_dir = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests/golden_img"
        )
        self._usd_path = Path(
            f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/tests"
        )

        import omni.kit.window.property as p

        self._w = p.get_window()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # test scheme
    async def test_property_window_scheme(self):
        from omni.kit.window.property.property_scheme_delegate import PropertySchemeDelegate
        from omni.kit.window.property.templates import LABEL_HEIGHT, SimplePropertyWidget

        class SchemeTestWidget(SimplePropertyWidget):
            def __init__(self, name: str):
                super().__init__(title="SchemeTestWidget", collapsable=False)
                self._name = name
                nonlocal init_called
                init_called = True

            def on_new_payload(self, payload):
                nonlocal new_payload_called
                new_payload_called = True
                return True

            def build_items(self):
                nonlocal build_items_called
                build_items_called = True

                ui.Separator()
                with ui.HStack(height=0):
                    ui.Spacer(width=8)
                    ui.Button(self._name, width=52, height=LABEL_HEIGHT, name="add")
                    ui.Spacer(width=88 - 52)
                    widget = ui.StringField(name="scheme_name", height=LABEL_HEIGHT, enabled=False)
                    widget.model.set_value(f"{self._name}-" * 100)
                ui.Separator()

        class TestPropertySchemeDelegate(PropertySchemeDelegate):
            def get_widgets(self, payload):
                widgets_to_build = []
                if len(payload):
                    # should still only appear once
                    widgets_to_build.append("test_property_window_scheme_test")
                    widgets_to_build.append("test_property_window_scheme_test")
                return widgets_to_build

        # enable custom widget/scheme
        w = self._w

        init_called = False
        w.register_widget("test_scheme_1", "test_property_window_scheme_test", SchemeTestWidget("TEST1"))
        self.assertTrue(init_called)
        init_called = False
        w.register_widget("test_scheme_2", "test_property_window_scheme_test", SchemeTestWidget("TEST2"))
        self.assertTrue(init_called)
        init_called = False
        w.register_widget("test_scheme_3", "test_property_window_scheme_test", SchemeTestWidget("TEST3"))
        self.assertTrue(init_called)
        init_called = False
        w.register_widget("test_scheme_4", "test_property_window_scheme_test", SchemeTestWidget("TEST4"))
        self.assertTrue(init_called)

        w.register_scheme_delegate(
            "test_scheme_delegate", "test_property_window_scheme_test_scheme", TestPropertySchemeDelegate()
        )
        w.set_scheme_delegate_layout("test_scheme_delegate", ["test_property_window_scheme_test_scheme"])

        self.assertEqual(w.get_scheme(), "")

        # draw (should draw SchemeTestWidget item "TEST1")
        for scheme in ["test_scheme_1", "test_scheme_2", "test_scheme_3", "test_scheme_4"]:
            new_payload_called = False
            build_items_called = False

            await self.docked_test_window(
                window=self._w._window,
                width=450,
                height=200,
                restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
                restore_position=ui.DockPosition.BOTTOM,
            )

            w.notify(scheme, {"payload": ["Items..."]})
            await ui_test.human_delay(10)

            self.assertTrue(w.get_scheme() == scheme)
            self.assertTrue(new_payload_called)
            self.assertTrue(build_items_called)

            await self.finalize_test(
                golden_img_dir=self._golden_img_dir, golden_img_name=f"property_window_{scheme}.png"
            )

        # disable custom widget/scheme

        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=200,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        w.reset_scheme_delegate_layout("test_scheme_delegate")

        w.unregister_widget("test_scheme_4", "test_property_window_scheme_test")
        w.unregister_widget("test_scheme_3", "test_property_window_scheme_test")
        w.unregister_widget("test_scheme_2", "test_property_window_scheme_test")
        w.unregister_widget("test_scheme_1", "test_property_window_scheme_test")
        w.unregister_scheme_delegate("test_scheme_delegate", "test_property_window_scheme_test_scheme")

        # draw (should draw nothing)
        for scheme in ["test_scheme_1", "test_scheme_2", "test_scheme_3", "test_scheme_4"]:
            new_payload_called = False
            build_items_called = False

            await self.docked_test_window(
                window=self._w._window,
                width=450,
                height=200,
                restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
                restore_position=ui.DockPosition.BOTTOM,
            )

            w.notify(scheme, {"payload": ["Items..."]})
            await ui_test.human_delay(10)

            self.assertTrue(w.get_scheme() == scheme)
            self.assertFalse(new_payload_called)
            self.assertFalse(build_items_called)

            await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="property_window_empty.png")
        await ui_test.human_delay(10)

    async def test_pause_resume_property_window(self):
        from omni.kit.window.property.templates import LABEL_HEIGHT, SimplePropertyWidget

        class SchemeTestWidget(SimplePropertyWidget):
            def __init__(self, name: str):
                super().__init__(title="SchemeTestWidget", collapsable=False)
                self._name = name

            def on_new_payload(self, payload):
                if not super().on_new_payload(payload):
                    return False

                return self._payload == self._name

            def build_items(self):
                ui.Separator()
                with ui.HStack(height=0):
                    ui.Spacer(width=8)
                    ui.Button(self._name, width=52, height=LABEL_HEIGHT, name="add")
                    ui.Spacer(width=88 - 52)
                    widget = ui.StringField(name="scheme_name", height=LABEL_HEIGHT, enabled=False)
                    widget.model.set_value(f"{self._name}-" * 100)
                ui.Separator()

        # enable custom widget/scheme
        w = self._w

        w.register_widget("test_scheme_1", "test_property_window_scheme_test", SchemeTestWidget("TEST1"))
        w.register_widget("test_scheme_1", "test_property_window_scheme_test2", SchemeTestWidget("TEST2"))
        w.register_widget("test_scheme_2", "test_property_window_scheme_test3", SchemeTestWidget("TEST3"))

        # Not paused, refresh normally, show TEST1
        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=200,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )
        w.notify("test_scheme_1", "TEST1")
        await ui_test.human_delay(10)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="property_window_paused.png")

        # Pause property window
        w.paused = True

        # Paused, property window stops updating, show TEST1
        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=200,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )
        w.notify("test_scheme_1", "TEST2")
        await ui_test.human_delay(10)
        w.notify("test_scheme_2", "TEST3")
        await ui_test.human_delay(10)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="property_window_paused.png")

        # Resume property window, refresh to last scheme/payload, show TEST3
        w.paused = False
        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=200,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )
        await ui_test.human_delay(10)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="property_window_resumed.png")

        # Not paused, refresh normally, show TEST2
        await self.docked_test_window(
            window=self._w._window,
            width=450,
            height=200,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )
        w.notify("test_scheme_1", "TEST2")
        await ui_test.human_delay(10)
        await self.finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name="property_window_resumed2.png")

        w.unregister_widget("test_scheme_2", "test_property_window_scheme_test3")
        w.unregister_widget("test_scheme_1", "test_property_window_scheme_test2")
        w.unregister_widget("test_scheme_1", "test_property_window_scheme_test")

        # clear the schema - notify("", "") is ignored
        w.notify("", "payload")
        await ui_test.human_delay(10)
