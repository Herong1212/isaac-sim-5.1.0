## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

__all__ = ['TestRegistry']


import omni.kit.test
from omni.kit.test import AsyncTestCase
from .. import RegisterScene, RegisterViewportLayer

def _make_factory(id_str_in: str):
    class _EmptyFactoy():
        def __init__(self, id_str: str = id_str_in):
            self.factory_id = id_str
    return _EmptyFactoy


class TestRegistry(AsyncTestCase):
    def setUp(self):
        self.__scenes = {}
        self.__layers = {}
        super().setUp()

    # After running each test
    def tearDown(self):
        self.__scenes = {}
        self.__layers = {}
        super().tearDown()

    def ___scene_type_notification(self, factory, loading):
        if loading:
            self.__scenes[factory().factory_id] = None
        else:
            del self.__scenes[factory().factory_id]

    def ___layer_type_notification(self, factory, loading):
        if loading:
            self.__layers[factory().factory_id] = None
        else:
            del self.__layers[factory().factory_id]

    def __build_unique_ids(self, base_id: str, n: int = 10):
        for i in range(n):
            yield f'omni.kit.viewport.registry.{base_id}.factory_{i}'

    async def test_add_remove_notifier(self):
        RegisterScene.add_notifier(self.___scene_type_notification)
        RegisterViewportLayer.add_notifier(self.___layer_type_notification)
        RegisterScene.remove_notifier(self.___scene_type_notification)
        RegisterViewportLayer.remove_notifier(self.___layer_type_notification)

    async def test_factory_auto_destruct_scope(self):
        RegisterScene.add_notifier(self.___scene_type_notification)
        RegisterViewportLayer.add_notifier(self.___layer_type_notification)

        # Register a bunch of factories
        for sid in self.__build_unique_ids('scene'):
            RegisterScene(_make_factory(sid), sid)
        # Those factories are already out of scope, so they should have been de-regsitered
        self.assertEqual(self.__scenes, {})
        self.assertEqual(self.__layers, {})

        # Register a bunch of factories
        for lid in self.__build_unique_ids('layer'):
            RegisterViewportLayer(_make_factory(lid), lid)
        # Those factories are already out of scope, so they should have been de-regsitered
        self.assertEqual(self.__scenes, {})
        self.assertEqual(self.__layers, {})

        RegisterScene.remove_notifier(self.___scene_type_notification)
        RegisterViewportLayer.remove_notifier(self.___layer_type_notification)

    async def test_factory_registration(self):
        RegisterScene.add_notifier(self.___scene_type_notification)
        RegisterViewportLayer.add_notifier(self.___layer_type_notification)

        # Register a bunch of scene-factories, saving the returned subscription
        scene_subs = {}
        for sid in self.__build_unique_ids('scene'):
            scene_subs[sid] = RegisterScene(_make_factory(sid), sid)
        # Scenes should have been registered
        self.assertEqual([sid for sid in self.__build_unique_ids('scene')], [sid for sid, fact in self.__scenes.items()])
        # Layers should be empty
        self.assertEqual([], [lid for lid, fact in self.__layers.items()])

        # Register a bunch of layer-factories, saving the returned subscription
        layer_subs = {}
        for lid in self.__build_unique_ids('layer'):
            layer_subs[lid] = RegisterViewportLayer(_make_factory(lid), lid)

        # Layers should now have been registered
        self.assertEqual([lid for lid in self.__build_unique_ids('layer')], [lid for lid, fact in self.__layers.items()])
        # Scenes should have stayed the same
        self.assertEqual([sid for sid in self.__build_unique_ids('scene')], [sid for sid, fact in self.__scenes.items()])

        layer_subs = {}
        # Layers should now have been all deregistered
        self.assertEqual([], [lid for lid, fact in self.__layers.items()])
        scene_subs = {}
        # Scenes should now have been all deregistered
        self.assertEqual([], [sid for sid, fact in self.__scenes.items()])

        RegisterScene.remove_notifier(self.___scene_type_notification)
        RegisterViewportLayer.remove_notifier(self.___layer_type_notification)

    async def test_factory_ordering(self):
        RegisterScene.add_notifier(self.___scene_type_notification)

        # Register a bunch of scene-factories, saving the returned subscription
        scene_subs = {}
        for sid in self.__build_unique_ids('scene'):
            scene_subs[sid] = RegisterScene(_make_factory(sid), sid)
        # Scenes should have been registered
        self.assertEqual([sid for sid in self.__build_unique_ids('scene')], [sid for sid, fact in self.__scenes.items()])
        # Layers should be empty
        self.assertEqual([], [lid for lid, fact in self.__layers.items()])

        scene_ids = [sid for sid in self.__build_unique_ids('scene', 10)]
        scene_ids_a = scene_ids[:5]
        scene_ids_b = scene_ids[5:]

        # Get ordered_factories, not including those not requested appened to end: [0-4]
        self.assertEqual([sid for sid, fact in RegisterScene.ordered_factories(scene_ids_a, append_unkown=False)], scene_ids_a)
        # Get ordered_factories, not including those not requested appened to end: [5-9]
        self.assertEqual([sid for sid, fact in RegisterScene.ordered_factories(scene_ids_b, append_unkown=False)], scene_ids_b)

        # Get ordered_factories, including those not requested appened to end: [0-4] + [5-9]
        self.assertEqual([sid for sid, fact in RegisterScene.ordered_factories(scene_ids_a)], scene_ids_a + scene_ids_b)
        # Get ordered_factories, including those not requested appened to end: [5-9] + [0-4]
        self.assertEqual([sid for sid, fact in RegisterScene.ordered_factories(scene_ids_b)], scene_ids_b + scene_ids_a)

        # Get ordered_factories, including those not requested appened to end, ignoring 9: [0-4] + [5-8]
        self.assertEqual([sid for sid, fact in RegisterScene.ordered_factories(scene_ids_a, ignore_unknown=['omni.kit.viewport.registry.scene.factory_9'])], scene_ids_a + scene_ids_b[:-1])
        # Get ordered_factories, including those not requested appened to end, ignoring 0: [5-9] + [1-4]
        self.assertEqual([sid for sid, fact in RegisterScene.ordered_factories(scene_ids_b, ignore_unknown=['omni.kit.viewport.registry.scene.factory_0'])], scene_ids_b + scene_ids_a[1:])

        RegisterScene.remove_notifier(self.___scene_type_notification)
