import carb
import omni.kit.test
import omni.usd
import omni.client
import unittest
import omni.kit.app
import carb.settings
import omni.kit.collaboration.presence_layer as pl
import omni.kit.collaboration.presence_layer.utils as pl_utils
import omni.kit.usd.layers as layers

from omni.kit.usd.layers.tests.mock_utils import MockLiveSyncingApi
from pxr import Usd, Sdf
from typing import List


class TestPresenceLayer(omni.kit.test.AsyncTestCase):

    # Before running each test
    async def setUp(self):
        self.app = omni.kit.app.get_app()
        self.usd_context = omni.usd.get_context()
        self.layers = layers.get_layers(self.usd_context)
        self.live_syncing = layers.get_live_syncing(self.usd_context)
        self.local_builtin_cameras = [
            "/OmniverseKit_Persp", "/OmniverseKit_Front", "/OmniverseKit_Top", "/OmniverseKit_Right"
        ]

        await omni.usd.get_context().new_stage_async()

        self.simulated_user_name = "test"
        self.simulated_user_id = "abcde"
        self.simulated_user_name2 = "test2"
        self.simulated_user_id2 = "abcdef"

    async def tearDown(self):
        pass

    async def wait(self, frames=10):
        for i in range(frames):
            await self.app.next_update_async()

    async def __create_session_and_simulate_users(self):
        session = self.live_syncing.find_live_session_by_name(self.stage_url, "test")
        if not session:
            session = self.live_syncing.create_live_session("test", self.stage_url)

        self.assertTrue(session, "Failed to create live session.")

        self.assertTrue(self.live_syncing.join_live_session(session))
        await self.wait()

        # Access private variable to simulate user login.
        user = layers.LiveSessionUser(self.simulated_user_name, self.simulated_user_id, "Create")
        user2 = layers.LiveSessionUser(self.simulated_user_name2, self.simulated_user_id2, "Create")
        current_session = self.live_syncing.get_current_live_session()
        session_channel = current_session._session_channel()
        session_channel._peer_users[self.simulated_user_id] = user
        session_channel._peer_users[self.simulated_user_id2] = user2
        session_channel._send_layer_event(
            layers.LayerEventType.LIVE_SESSION_USER_JOINED,
            {"user_name": self.simulated_user_name, "user_id": self.simulated_user_id}
        )
        session_channel._send_layer_event(
            layers.LayerEventType.LIVE_SESSION_USER_JOINED,
            {"user_name": self.simulated_user_name2, "user_id": self.simulated_user_id2}
        )

        await self.wait()

    def __get_shared_stage(self, current_session: layers.LiveSession):
        shared_data_stage_url = current_session.url + "/shared_data/users.live"
        layer = Sdf.Layer.FindOrOpen(shared_data_stage_url)
        if not layer:
            layer = Sdf.Layer.CreateNew(shared_data_stage_url)

        return Usd.Stage.Open(layer)

    async def __bound_camera(self, shared_stage: Usd.Stage, user_id: str, camera_path: Sdf.Path):
        if not camera_path:
            camera_path = Sdf.Path.emptyPath

        camera_path = Sdf.Path(camera_path)
        bound_camera_property_path = pl_utils.get_bound_camera_property_path(user_id)
        property_spec = pl_utils.get_or_create_property_spec(
            shared_stage.GetRootLayer(), bound_camera_property_path,
            Sdf.ValueTypeNames.String
        )

        builtin_camera_name = pl_utils.is_local_builtin_camera(camera_path)
        if not builtin_camera_name:
            property_spec.default = str(camera_path)
        else:
            property_spec.default = builtin_camera_name

        if builtin_camera_name:
            persp_camera = pl_utils.get_user_shared_root_path(user_id).AppendChild(builtin_camera_name)
            camera_prim = shared_stage.DefinePrim(persp_camera, "Camera")

        await self.wait()

    async def __select_prims(self, shared_stage: Usd.Stage, user_id: str, selections: List[str]):
        selection_property_path = pl_utils.get_selection_property_path(user_id)
        property_spec = pl_utils.get_or_create_property_spec(
            shared_stage.GetRootLayer(), selection_property_path,
            Sdf.ValueTypeNames.StringArray
        )
        property_spec.default = selections

        await self.wait()

    async def __follow_user(
        self, shared_stage: Usd.Stage, user_id: str, following_user_id: str
    ):
        following_user_property_path = pl_utils.get_following_user_property_path(user_id)
        property_spec = pl_utils.get_or_create_property_spec(
            shared_stage.GetRootLayer(), following_user_property_path,
            Sdf.ValueTypeNames.String
        )
        property_spec.default = following_user_id

        await self.wait()

    @MockLiveSyncingApi
    async def test_api(self):
        self.stage_url = "omniverse://__faked_omniverse_server__/test/test.usd"
        format = Sdf.FileFormat.FindByExtension(".usd")
        layer = Sdf.Layer.New(format, self.stage_url)
        stage = Usd.Stage.Open(layer)
        await self.usd_context.attach_stage_async(stage)

        self.all_camera_paths = []
        for i in range(10):
            camera_path = Sdf.Path(f"/Camera{i}")
            stage.DefinePrim(camera_path, "Camera")
            self.all_camera_paths.append(camera_path)

        # Simulated builtin cameras
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            for camera_path in self.local_builtin_cameras:
                stage.DefinePrim(camera_path, "Camera")
                self.all_camera_paths.append(camera_path)

        def _on_layers_event(event):
            nonlocal payload
            p = pl.get_presence_layer_event_payload(event)
            if p.event_type:
                payload = p

        subscription = self.layers.get_event_stream().create_subscription_to_pop(
            _on_layers_event, name="omni.kit.collaboration.presence_layer.tests"
        )

        await self.__create_session_and_simulate_users()

        current_live_session = self.live_syncing.get_current_live_session()
        shared_stage = self.__get_shared_stage(current_live_session)
        self.assertTrue(shared_stage)

        presence_layer = pl.get_presence_layer_interface(self.usd_context)
        # Simulated user has empty camera bound at start.
        self.assertFalse(presence_layer.is_bound_to_builtin_camera(self.simulated_user_id))
        self.assertFalse(presence_layer.get_bound_camera_prim(self.simulated_user_id))
        self.assertFalse(presence_layer.get_following_user_id(self.simulated_user_id))
        self.assertFalse(presence_layer.get_selections(self.simulated_user_id))

        # Bound to invalid camera
        for camera_path in ["/nonexisted", ""]:
            await self.__bound_camera(shared_stage, self.simulated_user_id, camera_path)
            self.assertTrue(payload)
            self.assertEqual(payload.event_type, pl.PresenceLayerEventType.BOUND_CAMERA_CHANGED)
            self.assertFalse(presence_layer.is_bound_to_builtin_camera(self.simulated_user_id))
            self.assertFalse(presence_layer.get_bound_camera_prim(self.simulated_user_id))

        payload = None

        # Bound to valid camera
        for camera_path in self.all_camera_paths:
            camera_path = Sdf.Path(camera_path)
            is_builtin_camera = pl_utils.is_local_builtin_camera(camera_path) is not None
            await self.__bound_camera(shared_stage, self.simulated_user_id, camera_path)
            self.assertTrue(payload)
            self.assertEqual(payload.event_type, pl.PresenceLayerEventType.BOUND_CAMERA_CHANGED, camera_path)
            self.assertEqual(presence_layer.is_bound_to_builtin_camera(self.simulated_user_id), is_builtin_camera, camera_path)
            self.assertTrue(presence_layer.get_bound_camera_prim(self.simulated_user_id), camera_path)

        # Selections
        for selections in [["/test", "/test2"], [], ["/test", "/test2", "test3"]]:
            payload = None
            await self.__select_prims(shared_stage, self.simulated_user_id, selections)
            self.assertTrue(payload)
            self.assertEqual(payload.event_type, pl.PresenceLayerEventType.SELECTIONS_CHANGED)
            self.assertEqual(presence_layer.get_selections(self.simulated_user_id), selections, selections)

        # Following user
        # Setups default camera
        logged_user_id = current_live_session.logged_user_id
        presence_layer.broadcast_local_bound_camera("/OmniverseKit_Persp")
        await self.__bound_camera(shared_stage, self.simulated_user_id2, self.all_camera_paths[0])

        for user_id in [logged_user_id, self.simulated_user_id2]:
            payload = None
            await self.__follow_user(shared_stage, self.simulated_user_id, user_id)
            self.assertTrue(payload)
            self.assertEqual(payload.event_type, pl.PresenceLayerEventType.BOUND_CAMERA_CHANGED)
            self.assertEqual(presence_layer.get_following_user_id(self.simulated_user_id), user_id)
            self.assertTrue(presence_layer.is_user_followed_by(user_id, self.simulated_user_id))
            self.assertTrue(presence_layer.get_bound_camera_prim(self.simulated_user_id))

        user_id = "invalid_user_id"
        payload = None
        await self.__follow_user(shared_stage, self.simulated_user_id, user_id)
        self.assertTrue(payload)
        self.assertEqual(payload.event_type, pl.PresenceLayerEventType.BOUND_CAMERA_CHANGED)
        self.assertFalse(presence_layer.get_bound_camera_prim(self.simulated_user_id))
        self.assertFalse(presence_layer.is_in_following_mode(self.simulated_user_id), user_id)
        self.assertFalse(presence_layer.is_user_followed_by(user_id, self.simulated_user_id))
        await self.__follow_user(shared_stage, self.simulated_user_id, "")

        payload = None
        self.assertFalse(presence_layer.enter_follow_mode(logged_user_id))
        self.assertTrue(presence_layer.enter_follow_mode(self.simulated_user_id))
        await self.wait()
        self.assertTrue(payload)
        self.assertEqual(payload.event_type, pl.PresenceLayerEventType.LOCAL_FOLLOW_MODE_CHANGED)
        self.assertEqual(presence_layer.get_following_user_id(), self.simulated_user_id)
        self.assertTrue(presence_layer.is_in_following_mode(logged_user_id))
        self.assertTrue(presence_layer.is_user_followed_by(self.simulated_user_id, logged_user_id))

        payload = None
        presence_layer.quit_follow_mode()
        await self.wait()
        self.assertTrue(payload)
        self.assertEqual(payload.event_type, pl.PresenceLayerEventType.LOCAL_FOLLOW_MODE_CHANGED)
        self.assertFalse(presence_layer.get_following_user_id())
        self.assertFalse(presence_layer.is_in_following_mode(logged_user_id))
        self.assertFalse(presence_layer.is_user_followed_by(self.simulated_user_id, logged_user_id))
