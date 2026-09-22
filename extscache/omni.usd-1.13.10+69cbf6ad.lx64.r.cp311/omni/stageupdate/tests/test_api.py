# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.test
from multiprocessing import context
from pathlib import Path
import omni.stageupdate
from functools import partial
import carb.settings

class TestStageUpdate(omni.kit.test.AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setUp(self):
        self._callback_data = {}
        self._app = omni.kit.app.get_app()
        self._settings = carb.settings.get_settings()
        self._golden = {
            "attach": {"meters": 0.01},  # default stage meters per unit; ID is internal
            "prim_add" : {"path": "/Dummy"},
            "prim_remove" : {"path": "/Dummy"}
        }

    async def test_stage_update_api(self):
        self._stage_update = omni.stageupdate.get_stage_update_interface()
        usd_context_main = omni.usd.get_context()
        self.assertEqual(usd_context_main.get_name(), "")

        other_context_name = 'other usd context'
        usd_context_other = omni.usd.create_context(other_context_name)
        self.assertEqual(usd_context_other.get_name(), other_context_name)
        self._stage_update_other = omni.stageupdate.get_stage_update_interface(other_context_name)

        # test default stage update
        self._test_stage_update_node(self._stage_update)
        node_main = self._create_stage_update_node(self._stage_update, "main")
        self.assertEqual(len(self._stage_update.get_stage_update_nodes()), 1)
        self.assertEqual(len(self._stage_update_other.get_stage_update_nodes()), 0)
        await self._test_stage_update_node_callbacks(usd_context_main, self._stage_update, "main", node_main)

        # test other stage update
        self._test_stage_update_node(self._stage_update_other)
        node_other = self._create_stage_update_node(self._stage_update_other, other_context_name)
        self.assertEqual(len(self._stage_update.get_stage_update_nodes()), 1)
        self.assertEqual(len(self._stage_update_other.get_stage_update_nodes()), 1)
        await self._test_stage_update_node_callbacks(usd_context_other, self._stage_update_other, other_context_name, node_other)

        # run callback test again for defaut stage update
        #   to make sure it does not call the new one
        await self._test_stage_update_node_callbacks(usd_context_main, self._stage_update, "main", node_main)

    # we assume that this method is called before addding other nodes to a stage update
    def _test_stage_update_node(self, stage_update: omni.stageupdate.StageUpdate):
        # no nodes at start
        self.assertEqual(len(stage_update.get_stage_update_nodes()), 0)

        # create new
        node_name = "a node"
        node_0 = stage_update.create_stage_update_node(
            display_name=node_name
        )
        nodes = stage_update.get_stage_update_nodes()
        self.assertEqual(len(nodes), 1)
        self.assertEqual(node_name, nodes[0]["name"])

        node_name = "another node"
        node_1 = stage_update.create_stage_update_node(
            display_name=node_name
        )
        nodes = stage_update.get_stage_update_nodes()
        self.assertEqual(len(nodes), 2)
        self.assertEqual(node_name, nodes[1]["name"])

        # set enabled
        self.assertTrue(nodes[0]["enabled"])
        self.assertTrue(nodes[1]["enabled"])
        stage_update.set_stage_update_node_enabled(0, False)
        nodes = stage_update.get_stage_update_nodes()
        self.assertFalse(nodes[0]["enabled"])
        self.assertTrue(nodes[1]["enabled"])
        stage_update.set_stage_update_node_enabled(0, True)
        nodes = stage_update.get_stage_update_nodes()
        self.assertTrue(nodes[0]["enabled"])
        self.assertTrue(nodes[1]["enabled"])

        # set order
        orders = [n["order"] for n in nodes]
        stage_update.set_stage_update_node_order(0, 42)
        nodes = stage_update.get_stage_update_nodes()
        self.assertEqual(42, nodes[0]["order"])
        self.assertEqual(orders[1], nodes[1]["order"])

    def _create_stage_update_node(self, stage_update: omni.stageupdate.StageUpdate,
                                    stage_update_name: str) -> omni.stageupdate.StageUpdateNode:
        node = stage_update.create_stage_update_node(
            display_name='test_node',
            on_attach_fn=partial(self._on_attach, "attach_" + stage_update_name),
            on_detach_fn=partial(self._on_detach, "detach_" + stage_update_name),
            on_update_fn=partial(self._on_update, "update_" + stage_update_name),
            on_prim_add_fn=partial(self._on_prim_add, "prim_add_" + stage_update_name),
            on_prim_remove_fn=partial(self._on_prim_remove, "prim_remove_" + stage_update_name),
        )

        return node

    async def _test_stage_update_node_callbacks(self, usd_context, stage_update: omni.stageupdate.StageUpdate,
                                            stage_update_name : str, node: omni.stageupdate.StageUpdateNode):
        on_update_sub = stage_update.subscribe_to_stage_update_node_change_events(
            fn=partial(self._on_update_node_changed, "node_changed_" + stage_update_name)
        )

        # new_stage may populate the stage with objects which causes prim_add test to fail
        self._assert_prim_add = False
        self._ignore_prim_remove = True

        await usd_context.new_stage_async()
        for i in range(10):
            await self._app.next_update_async()
        self._verify_callbacks(["attach_" + stage_update_name, "update_" + stage_update_name])

        await self._app.next_update_async()
        self._verify_callback("update_" + stage_update_name)

        self._assert_prim_add = True
        stage = usd_context.get_stage()
        stage.DefinePrim(self._golden["prim_add"]["path"])
        for i in range(10):
            await self._app.next_update_async()
        self._verify_callbacks(["prim_add_" + stage_update_name, "update_" + stage_update_name])
        self._assert_prim_add = False

        stage_update.set_stage_update_node_order(0, 42)
        await self._app.next_update_async()
        self._verify_callbacks(["update_" + stage_update_name, "node_changed_" + stage_update_name])

        if self._settings.get("/app/useFabricSceneDelegate"):
            self._ignore_prim_remove = False
            stage.RemovePrim(self._golden["prim_remove"]["path"])
            self._verify_callback("prim_remove_" + stage_update_name)

        usd_context.close_stage()
        self._verify_callback("detach_" + stage_update_name)

    def _verify_callback(self, callback_name: str):
        self.assertEqual(len(self._callback_data), 1)  # no other callbacks
        self.assertTrue(callback_name in self._callback_data)
        self.assertTrue(self._callback_data[callback_name])
        self._callback_data = {}

    def _verify_callbacks(self, callback_names: list):
        self.assertEqual(len(self._callback_data), len(callback_names))
        for callback_name in callback_names:
            self.assertTrue(callback_name in self._callback_data)
            self.assertTrue(self._callback_data[callback_name])
        self._callback_data = {}

    def _on_attach(self, label: str, in_id: int, in_meters: float):
        self._callback_data[label] = True
        # self.assertEqual(in_meters, self._golden["attach"]["id"]) # this is set internally during stage open
        self.assertAlmostEqual(in_meters, self._golden["attach"]["meters"], places=5)

    def _on_detach(self, label: str):
        self._callback_data[label] = True

    def _on_update(self, label: str, in_time: float, in_dt: float):
        self._callback_data[label] = True

    def _on_prim_add(self, label: str, in_path: str):
        self._callback_data[label] = True
        if self._assert_prim_add:
            self.assertEqual(in_path, self._golden["prim_add"]["path"])

    def _on_prim_remove(self, label: str, in_path: str):
        if self._ignore_prim_remove:
            return
        self._callback_data[label] = True
        self.assertEqual(in_path, self._golden["prim_remove"]["path"])
            
    def _on_update_node_changed(self, label: str):
        self._callback_data[label] = True