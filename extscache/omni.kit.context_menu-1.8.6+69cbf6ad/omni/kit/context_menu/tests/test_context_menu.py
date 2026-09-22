## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import pathlib
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.ui as ui
import omni.usd
from omni.ui.tests.test_base import OmniUiTest
from omni.kit import ui_test
from pxr import Kind, Sdf, Gf, Usd


class TestContextMenu(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()

        from omni.kit.context_menu.scripts.context_menu import TEST_DATA_PATH
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        self._usd_path = TEST_DATA_PATH.absolute().joinpath("usd").absolute()

        self._usd_context = omni.usd.get_context()
        await self._usd_context.new_stage_async()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def test_conversion_between_payloads_and_references(self):
        from omni.kit import ui_test

        stage = self._usd_context.get_stage()
        prim = stage.DefinePrim("/root/prim", "Xform")
        reference_layer = Sdf.Layer.CreateAnonymous()
        reference_layer2 = Sdf.Layer.CreateAnonymous()

        reference_stage = Usd.Stage.Open(reference_layer)
        reference_prim = reference_stage.DefinePrim("/root/reference", "Xform")
        payload_prim = reference_stage.DefinePrim("/root/payload", "Xform")
        default_prim = reference_stage.GetPrimAtPath("/root")
        reference_stage.SetDefaultPrim(default_prim)
        reference_prim.GetReferences().AddReference(reference_layer2.identifier)
        payload_prim.GetPayloads().AddPayload(reference_layer2.identifier)

        prim.GetReferences().AddReference(reference_layer.identifier)
        await ui_test.wait_n_updates(2)

        self._usd_context.get_selection().set_selected_prim_paths(["/root/prim/reference"], True)
        await ui_test.wait_n_updates(2)
        self._usd_context.get_selection().set_selected_prim_paths([], True)

        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertTrue(len(ref_and_layers) == 1)

        reference_prim = stage.GetPrimAtPath("/root/prim/reference")
        ref_and_layers = omni.usd.get_composed_references_from_prim(reference_prim)
        self.assertTrue(len(ref_and_layers) == 1)

        payload_prim = stage.GetPrimAtPath("/root/prim/payload")
        payload_and_layers = omni.usd.get_composed_payloads_from_prim(payload_prim)
        self.assertTrue(len(payload_and_layers) == 1)

        await ui_test.find("Stage").focus()

        stage_widget = ui_test.find("Stage//Frame/**/ScrollingFrame/TreeView[*].visible==True")
        prim_widget = stage_widget.find("**/Label[*].text=='prim'")
        self.assertTrue(prim_widget)

        await prim_widget.right_click()
        await ui_test.select_context_menu("Convert References to Payloads")
        await ui_test.wait_n_updates(5)

        reference_prim = stage.GetPrimAtPath("/root/prim")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertTrue(len(ref_and_layers) == 0)

        payload_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        self.assertTrue(len(payload_and_layers) == 1)

        prim_widget = stage_widget.find("**/Label[*].text=='prim'")
        await prim_widget.right_click()
        await ui_test.select_context_menu("Convert Payloads to References")
        await ui_test.wait_n_updates(5)

        payload_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        self.assertTrue(len(payload_and_layers) == 0)

        reference_prim = stage.GetPrimAtPath("/root/prim")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertTrue(len(ref_and_layers) == 1)

        reference_prim_widget = stage_widget.find("**/Label[*].text=='reference'")
        self.assertTrue(reference_prim_widget)
        await reference_prim_widget.right_click()
        with self.assertRaises(Exception):
            await ui_test.select_context_menu("Convert Payloads to References")
        await ui_test.select_context_menu("Convert References to Payloads")
        prim = stage.GetPrimAtPath("/root/prim/reference")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertTrue(len(ref_and_layers) == 0)

        prim = stage.GetPrimAtPath("/root/prim/reference")
        payload_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        self.assertTrue(len(payload_and_layers) == 1)

        payload_prim_widget = stage_widget.find("**/Label[*].text=='payload'")
        self.assertTrue(payload_prim_widget)
        await payload_prim_widget.right_click()
        with self.assertRaises(Exception):
            await ui_test.select_context_menu("Convert References to Payloads")
        await ui_test.select_context_menu("Convert Payloads to References")
        prim = stage.GetPrimAtPath("/root/prim/payload")
        payload_and_layers = omni.usd.get_composed_payloads_from_prim(prim)
        self.assertTrue(len(payload_and_layers) == 0)

        reference_prim = stage.GetPrimAtPath("/root/prim/payload")
        ref_and_layers = omni.usd.get_composed_references_from_prim(prim)
        self.assertTrue(len(ref_and_layers) == 1)
