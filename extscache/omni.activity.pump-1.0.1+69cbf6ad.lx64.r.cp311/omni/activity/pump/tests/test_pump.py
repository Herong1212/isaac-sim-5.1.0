## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.activity.core as act
import omni.kit.app
import omni.kit.test


class TestPump(omni.kit.test.AsyncTestCase):
    async def test_general(self):
        called = []

        def callback(node: act.INode):
            self.assertEqual(node.name, "Test")
            self.assertEqual(node.child_count, 1)

            child = node.get_child(0)

            self.assertEqual(child.name, "SubTest")
            self.assertEqual(child.event_count, 2)

            began = child.get_event(0)
            ended = child.get_event(1)

            self.assertEqual(began.event_type, act.EventType.BEGAN)
            self.assertEqual(ended.event_type, act.EventType.ENDED)
            self.assertEqual(began.payload["progress"], 0.0)
            self.assertEqual(ended.payload["progress"], 1.0)

            called.append(True)

        id = act.get_instance().create_callback_to_pop(callback)

        act.enable()
        act.began("Test|SubTest", progress=0.0)
        act.ended("Test|SubTest", progress=1.0)
        act.disable()

        for _ in range(50):
            await omni.kit.app.get_app().next_update_async()

        act.get_instance().remove_callback(id)

        self.assertEqual(len(called), 1)
