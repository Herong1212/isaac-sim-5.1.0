# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-overridden-method
import sys

import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.usd
from omni.kit.test_suite.helpers import (
    arrange_windows,
    get_test_data_path,
    open_stage,
    select_prims,
    wait_stage_loading,
)

# FIXME - do same tests for payloads too


class TestPayRefPrimPath(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._context = omni.usd.get_context()
        await arrange_windows("Stage", 150)
        await open_stage(get_test_data_path(__name__, "usd/reference_prim.usda"))
        await wait_stage_loading()

    async def tearDown(self):
        await wait_stage_loading()

    def get_reference(self, prim):
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        (ref, _) = ref_and_layers[0]
        return ref.primPath.pathString

    def get_payload(self, prim):
        ref_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        (ref, _) = ref_and_layers[0]
        return ref.primPath.pathString

    async def wait(self, frames=3):
        for _ in range(frames):
            await omni.kit.app.get_app().next_update_async()

    async def test_internal_reference_prim_path(self):
        await self._context.new_stage_async()
        stage = self._context.get_stage()
        prim = stage.DefinePrim("/World", "Xform")
        prim = stage.DefinePrim("/World/reference", "Xform")
        prim.GetReferences().AddReference(get_test_data_path(__name__, "usd/reference_prim.usda"))
        await self.wait()

        await select_prims(["/World/reference/Internal/Reference"])
        await wait_stage_loading()

        reference_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='References'")
        widget = reference_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        # Internal reference is not enabled for modifying
        self.assertFalse(widget.widget.enabled)
        self.assertEqual(widget.widget.model.get_value_as_string(), "/World/Internal/Prim")

    async def test_reference_prim_path(self):
        from omni.kit.property.usd.usd_style import Styles

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        anchor_prim = stage.GetPrimAtPath("/World/XformReference")
        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        await select_prims(["/World/XformReference"])
        await wait_stage_loading()

        # verify original prim_path
        await self.assertEqualWithRetry(lambda: self.get_reference(anchor_prim), "")

        reference_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='References'")
        widget = reference_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        await widget.input("bad_prim_path", clear_before_input=True)

        # verify new prim_path
        await self.assertEqualWithRetry(lambda: self.get_reference(anchor_prim), "/bad_prim_path")
        widget = reference_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        self.assertEqual(widget.widget.style["color"], Styles.REFERENCE_ERROR)

        reference_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='References'")
        widget = reference_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        await widget.input("/bad_path", clear_before_input=True)
        # verify new prim_path
        await self.assertEqualWithRetry(lambda: self.get_reference(anchor_prim), "/bad_path")
        widget = reference_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        self.assertEqual(widget.widget.style["color"], Styles.REFERENCE_ERROR)

        reference_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='References'")
        widget = reference_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        await widget.input("/Xform/Cube", clear_before_input=True)
        # verify new prim_path
        await self.assertEqualWithRetry(lambda: self.get_reference(anchor_prim), "/Xform/Cube")
        widget = reference_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        self.assertEqual(widget.widget.style, None)

    async def test_payload_prim_path(self):
        from omni.kit.property.usd.usd_style import Styles

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        anchor_prim = stage.GetPrimAtPath("/World/XformPayload")
        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        await select_prims(["/World/XformPayload"])
        await wait_stage_loading()

        # verify original prim_path
        await self.assertEqualWithRetry(lambda: self.get_payload(anchor_prim), "")

        payload_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Payloads'")
        widget = payload_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        await widget.input("bad_prim_path", clear_before_input=True)
        # verify new prim_path
        await self.assertEqualWithRetry(lambda: self.get_payload(anchor_prim), "/bad_prim_path")

        widget = payload_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        self.assertEqual(widget.widget.style["color"], Styles.REFERENCE_ERROR)

        payload_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Payloads'")
        widget = payload_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        await widget.input("/bad_path", clear_before_input=True)
        # verify new prim_path
        await self.assertEqualWithRetry(lambda: self.get_payload(anchor_prim), "/bad_path")

        widget = payload_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        self.assertEqual(widget.widget.style["color"], Styles.REFERENCE_ERROR)

        payload_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Payloads'")
        widget = payload_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        await widget.input("/Xform/Cube", clear_before_input=True)
        # verify new prim_path
        await self.assertEqualWithRetry(lambda: self.get_payload(anchor_prim), "/Xform/Cube")

        widget = payload_frame.find("**/StringField[*].identifier=='payref_prim_path'")
        self.assertEqual(widget.widget.style, None)

    async def test_reference_buttons(self):
        from omni.kit.window.content_browser import get_content_window

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        anchor_prim = stage.GetPrimAtPath("/World/XformPayload")
        stage_window = ui_test.find("Stage")
        await stage_window.focus()

        await select_prims(["/World/XformPayload"])
        await wait_stage_loading()

        # test locate_button
        content_browser = get_content_window()
        content_browser.set_current_directory(sys.path[1])
        root_dir = content_browser.get_current_directory()
        payload_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Payloads'")
        await payload_frame.find("**/Button[*].identifier=='locate_button'").click()
        await ui_test.human_delay(50)
        # verify file was located
        self.assertNotEqual(content_browser.get_current_directory(), root_dir)

        # test reload_button
        content_browser = get_content_window()
        root_dir = content_browser.get_current_directory()
        payload_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Payloads'")
        await payload_frame.find("**/Image[*].identifier=='reload_button'").click()
        await ui_test.human_delay(10)

        # test remove_button
        payload_frame = ui_test.find("Property//Frame/**/CollapsableFrame[*].title=='Payloads'")
        await payload_frame.find("**/Button[*].identifier=='remove_button'").click()
        await ui_test.human_delay(10)
        # verify file was removed
        ref_and_layers = omni.usd.get_composed_references_from_prim(anchor_prim)
        self.assertEqual(ref_and_layers, [])
