from threading import Timer
from unittest.mock import patch, Mock
import carb
import omni.kit.test
import omni.usd
import omni.client
import unittest
import omni.kit.app
from omni.kit.usd.layers._omni_kit_usd_layers import IWorkflowLiveSyncing

from pxr import Sdf, Usd, UsdUtils

from omni.kit.usd.layers import get_layers, get_layer_event_payload, LayerEventType, LayerUtils, LayerErrorType, LayerEditMode
from .test_base import enable_server_tests
from omni.kit.usd.layers.tests.mock_utils import is_in_live_session_mocking, MockLiveSyncingApi, join_new_simulated_user, quit_simulated_user


class TestLiveSyncing(omni.kit.test.AsyncTestCase):  # pragma: no cover

    def __find_or_open_layer(self, identifier):
        layer = Sdf.Layer.FindOrOpen(identifier)
        if not layer:
            layer = Sdf.Layer.CreateNew(identifier)
        else:
            layer.Clear()
            layer.Save()

        return layer

    # Before running each test
    async def setUp(self):
        self.__external_stage = None
        self.previous_retry_values = omni.client.set_retries(0, 0, 0)
        self.app = omni.kit.app.get_app()
        self.usd_context = omni.usd.get_context()
        self.layers = get_layers(self.usd_context)
        self.live_syncing = self.layers.get_live_syncing()
        await omni.usd.get_context().new_stage_async()

        if enable_server_tests():
            self.test_folder = "omniverse://localhost/Projects/omni.kit.usd.layers/test_live_syncing/"
            await omni.client.delete_async(self.test_folder)
            self.stage_url = self.test_folder + "test.usd"
            self.sublayer = self.test_folder + "test2.usd"
            self.sublayer2 = self.test_folder + "test3.usd"
            stage = Usd.Stage.CreateNew(self.stage_url)
            layer = self.__find_or_open_layer(self.sublayer)
            stage.GetRootLayer().subLayerPaths.append(self.sublayer)

            self.reference = self.test_folder + "reference.usd"
            self.reference_layer = self.__find_or_open_layer(self.reference)
            prim_spec = Sdf.CreatePrimInLayer(self.reference_layer, "/World")
            prim_spec.specifier = Sdf.SpecifierDef
            self.reference_layer.defaultPrim = "World"
            self.reference_layer.Save()
            self.payload = self.test_folder + "payload.usd"
            self.payload_layer = self.__find_or_open_layer(self.payload)
            prim_spec = Sdf.CreatePrimInLayer(self.payload_layer, "/World")
            prim_spec.specifier = Sdf.SpecifierDef
            self.payload_layer.defaultPrim = "World"
            self.payload_layer.Save()

            self.reference_prim_path = "/test/Reference"
            self.payload_prim_path = "/test/Payload"

            self.stage = await self.__attach_stage_to_usd_context(self.usd_context, stage)
        else:
            self.test_folder = ""
            self.stage_url = ""
            self.stage = None

    async def tearDown(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        if stage:
            await usd_context.close_stage_async()

        self.stage = None
        external_stage, self.__external_stage = self.__external_stage, None
        if external_stage:
            UsdUtils.StageCache.Get().Erase(external_stage)

        if enable_server_tests():
            await omni.client.delete_async(self.test_folder)

        omni.client.set_retries(*self.previous_retry_values)

    async def wait(self, frames=10):
        for i in range(frames):
            await self.app.next_update_async()

    def __create_in_memory_layer(self, url):
        format = Sdf.FileFormat.FindByExtension(".usd")
        layer = Sdf.Layer.New(format, url)
        return layer

    async def __attach_stage_to_usd_context(self, usd_context, stage):
        await usd_context.attach_stage_async(stage)
        self.__external_stage = stage
        return stage

    async def __create_fake_stage(self, name = "test.usd", usd_context = None):
        stage_url = f"omniverse://__faked_omniverse_server__/test/{name}"
        layer = self.__create_in_memory_layer(stage_url)
        stage = Usd.Stage.Open(layer)
        if usd_context is None:
            usd_context = omni.usd.get_context()

        await self.__attach_stage_to_usd_context(usd_context, stage)

        self.stage_url = layer.identifier
        return stage, layer

    @MockLiveSyncingApi
    async def test_mock_utils(self):
        stage, layer = await self.__create_fake_stage("live_session.usd")

        session = self.live_syncing.create_live_session("test", layer.identifier)
        self.assertTrue(session)
        self.assertEqual(session.base_layer_identifier, layer.identifier)
        self.assertEqual(session.name, "test")

        channel_url = omni.client.combine_urls(layer.identifier, ".live/live_session.live/test.live/__session__.channel")
        session_url = omni.client.combine_urls(layer.identifier, ".live/live_session.live/test.live")
        self.assertEqual(session.channel_url, channel_url)
        self.assertEqual(session.url, session_url)

        session2 = self.live_syncing.create_live_session("test2", layer.identifier)
        self.assertEqual(len(self.live_syncing.get_all_live_sessions()), 2)
        live_session = self.live_syncing.find_live_session_by_name(layer.identifier, "test2")
        self.assertTrue(session2)
        self.assertEqual(session2.base_layer_identifier, layer.identifier)
        self.assertEqual(session2.name, "test2")

        live_session = self.live_syncing.find_live_session_by_name(layer.identifier, "test")
        self.assertTrue(live_session)
        self.assertFalse(self.live_syncing.is_stage_in_live_session())
        self.assertFalse(self.live_syncing.is_in_live_session())
        self.assertFalse(self.live_syncing.is_layer_in_live_session(layer.identifier))
        success = self.live_syncing.join_live_session(live_session)
        self.assertTrue(success)
        current_live_session = self.live_syncing.get_current_live_session()
        self.assertTrue(current_live_session)
        live_layer = Sdf.Find(current_live_session.root)
        self.assertTrue(live_layer)
        self.assertTrue(stage.HasLocalLayer(live_layer))
        self.assertTrue(self.live_syncing.is_stage_in_live_session())
        self.assertTrue(self.live_syncing.is_in_live_session())
        self.assertTrue(self.live_syncing.is_layer_in_live_session(layer.identifier))

        # Wait for connecting channel
        await self.wait()

        for i in range(10):
            join_new_simulated_user(f"test{i}", f"test{i}")
            await self.wait(2)
            self.assertEqual(len(current_live_session.peer_users), i+1)

        for i in range(10):
            quit_simulated_user(f"test{i}")
            await self.wait(2)
            self.assertEqual(len(current_live_session.peer_users), 9 - i)

        self.live_syncing.stop_live_session(layer.identifier)
        self.assertFalse(self.live_syncing.is_stage_in_live_session())
        self.assertFalse(self.live_syncing.is_in_live_session())
        self.assertFalse(self.live_syncing.is_layer_in_live_session(layer.identifier))

    @MockLiveSyncingApi
    async def test_join_session_with_url_mock(self):
        stage, layer = await self.__create_fake_stage("test.usd")

        session_url = omni.client.combine_urls(self.stage_url, ".live/test.live/customized_session.live")
        self.assertFalse(self.live_syncing.join_live_session_by_url(self.stage_url, session_url, False))
        self.assertTrue(self.live_syncing.join_live_session_by_url(self.stage_url, session_url, True))
        await self.wait(2)
        current_live_session = self.live_syncing.get_current_live_session()
        self.assertTrue(current_live_session)
        self.assertTrue(self.live_syncing.is_stage_in_live_session())
        self.assertTrue(self.live_syncing.is_in_live_session())
        self.assertTrue(self.live_syncing.is_layer_in_live_session(self.stage_url))
        self.assertEqual(current_live_session.name, "customized_session")
        self.assertEqual(current_live_session.url, session_url)
        self.assertTrue(self.live_syncing.get_live_session_by_url(session_url))
        self.live_syncing.stop_all_live_sessions()
        await self.wait(2)

    @MockLiveSyncingApi
    async def test_open_stage_with_live_session_mock(self):
        stage, layer = await self.__create_fake_stage("test.usd")
        # OMPE-50278: Fix crash when dereferencing nullptr for stage, crash stack is similar to:
        # https://omnicrashes.nvidia.com/minidump?uuid=9976bd9e-575d-405b-a0a7-85bf0c83fe8c
        # 
        # LiveSyncing.open_stage_with_live_session_async opens the stage in a worker thread, while
        # LayersImpl::update and LayersState::update runs in the main thread when we create a new stage
        # and attachStage. In between the null check of LayersImpl::update and when stageHandle is
        # actually used in LayersState::update, the stageHandle can be released in the worker thread.
        #
        # This crash callstack only happens in this test, we need to wait for one frame to avoid the
        # race condition that's causing the crash. 
        await self.wait(1)

        live_session = self.live_syncing.create_live_session("test", layer_identifier=self.stage_url)
        self.assertTrue(live_session)

        (success, _) = await self.live_syncing.open_stage_with_live_session_async(self.stage_url, "test")
        self.assertTrue(success)

        current_live_session = self.live_syncing.get_current_live_session()
        self.assertTrue(current_live_session is not None)
        self.assertEqual(current_live_session.name, "test")
        self.assertEqual(current_live_session.base_layer_identifier, self.stage_url)
        self.live_syncing.stop_all_live_sessions()
        await self.wait(2)

        # Test with query string
        url = omni.client.break_url(self.stage_url)
        query = "live_session_name=test"
        stage_url = omni.client.make_url(scheme=url.scheme, path=url.path, host=url.host, query=query)
        (success, _) = await self.live_syncing.open_stage_with_live_session_async(stage_url)
        self.assertTrue(success)

        current_live_session = self.live_syncing.get_current_live_session()
        self.assertTrue(current_live_session is not None)
        self.assertEqual(current_live_session.name, "test")
        self.assertEqual(current_live_session.base_layer_identifier, self.stage_url)
        self.live_syncing.stop_all_live_sessions()
        await self.wait(2)

    @MockLiveSyncingApi
    async def test_live_session_for_reference_prim_mock(self):
        self.stage, layer = await self.__create_fake_stage("live_session_ref.usd", self.live_syncing.usd_context)

        self.reference = omni.client.combine_urls(self.stage_url, "reference.usd")
        self.reference_layer = self.__create_in_memory_layer(self.reference)
        prim_spec = Sdf.CreatePrimInLayer(self.reference_layer, "/World")
        prim_spec.specifier = Sdf.SpecifierDef
        self.reference_layer.defaultPrim = "World"
        self.reference_prim_path = "/test/Reference"
        reference_prim = self.stage.DefinePrim(self.reference_prim_path)
        reference_prim.GetReferences().AddReference(self.reference)

        await self.__test_live_session_for_prim(self.reference_prim_path, True)
        self.live_syncing.stop_all_live_sessions()

    @MockLiveSyncingApi
    async def test_live_session_for_payload_prim_mock(self):
        self.stage, layer = await self.__create_fake_stage("live_session_payload.usd", self.live_syncing.usd_context)

        self.payload = omni.client.combine_urls(self.stage_url, "payload.usd")
        self.payload_layer = self.__create_in_memory_layer(self.payload)
        prim_spec = Sdf.CreatePrimInLayer(self.payload_layer, "/World")
        prim_spec.specifier = Sdf.SpecifierDef
        self.payload_layer.defaultPrim = "World"
        self.payload_prim_path = "/test/Payload"
        payload_prim = self.stage.DefinePrim(self.payload_prim_path)
        payload_prim.GetPayloads().AddPayload(self.payload)

        payload_prim = self.stage.DefinePrim(self.payload_prim_path)
        payload_prim.GetPayloads().AddPayload(self.payload)
        await self.__test_live_session_for_prim(self.payload_prim_path, False)

    @MockLiveSyncingApi
    async def test_live_session_for_multiple_references_mock(self):
        self.stage, layer = await self.__create_fake_stage("live_session_multiple.usd", self.live_syncing.usd_context)

        self.reference = omni.client.combine_urls(self.stage_url, "reference.usd")
        self.reference_layer = self.__create_in_memory_layer(self.reference)
        prim_spec = Sdf.CreatePrimInLayer(self.reference_layer, "/World")
        prim_spec.specifier = Sdf.SpecifierDef
        self.reference_layer.defaultPrim = "World"
        self.reference_prim_path = "/test/Reference"
        reference_prim = self.stage.DefinePrim(self.reference_prim_path)
        reference_prim.GetReferences().AddReference(self.reference)

        self.payload = omni.client.combine_urls(self.stage_url, "payload.usd")
        self.payload_layer = self.__create_in_memory_layer(self.payload)
        prim_spec = Sdf.CreatePrimInLayer(self.payload_layer, "/World")
        prim_spec.specifier = Sdf.SpecifierDef
        self.payload_layer.defaultPrim = "World"
        self.payload_prim_path = "/test/Payload"
        payload_prim = self.stage.DefinePrim(self.payload_prim_path)
        payload_prim.GetPayloads().AddPayload(self.payload)

        all_references = await self.__create_and_verify_10_live_prims()
        self.assertTrue(self.live_syncing.is_layer_in_live_session(self.reference))
        self.assertTrue(self.live_syncing.is_layer_in_live_session(self.reference, live_prim_only=True))
        for i in range(10):
            prim_path = all_references[i]
            prim_spec = self.stage.GetSessionLayer().GetPrimAtPath(prim_path)
            self.assertTrue(prim_spec)
            self.assertTrue(self.live_syncing.is_prim_in_live_session(prim_path))

        # Stop all live sessions about this layer.
        self.live_syncing.stop_live_session(self.reference)
        await self.wait(200)
        self.assertFalse(self.live_syncing.is_layer_in_live_session(self.reference))
        self.assertFalse(self.live_syncing.is_stage_in_live_session())
        for i in range(10):
            prim_path = all_references[i]
            self.assertFalse(self.live_syncing.is_prim_in_live_session(prim_path))
        self.assertFalse(self.live_syncing.is_layer_in_live_session(self.reference, live_prim_only=True))

    @MockLiveSyncingApi
    async def test_error_connection(self):
        def __mock_join_channel_with_callback_error(url, callback):
            def delayed_function():
                callback(omni.client.Result.ERROR_CONNECTION, omni.client.ChannelEvent.ERROR, None, None)
            callback(omni.client.Result.OK, omni.client.ChannelEvent.JOIN, None, None)
            Timer(0.001, delayed_function).start()
            return Mock(is_finished=lambda: False, id=1000)

        # join session
        stage, layer = await self.__create_fake_stage("test.usd")
        session_url = omni.client.combine_urls(self.stage_url, ".live/test.live/customized_session.live")
        with patch("omni.client.join_channel_with_callback") as mocked_callback:
            mocked_callback.side_effect = __mock_join_channel_with_callback_error
            self.assertTrue(self.live_syncing.join_live_session_by_url(self.stage_url, session_url, True))
            current_live_session = self.live_syncing.get_current_live_session()
            self.assertTrue(current_live_session)
            self.assertTrue(self.live_syncing.is_stage_in_live_session())
            self.assertTrue(self.live_syncing.is_in_live_session())
            self.assertTrue(self.live_syncing.is_layer_in_live_session(self.stage_url))
            self.assertEqual(current_live_session.name, "customized_session")
            self.assertEqual(current_live_session.url, session_url)
            self.assertTrue(self.live_syncing.get_live_session_by_url(session_url))
            old_user_name = current_live_session.logged_user_name
            old_user_id = current_live_session.logged_user_id
            await self.wait(2)

        # Mock user ID
        get_user_id_func_name = "get_logged_in_user_id_for_layer"
        native_get_id_func = getattr(IWorkflowLiveSyncing, get_user_id_func_name)
        self.assertTrue(native_get_id_func)
        mocked_get_id_func = Mock(return_value=old_user_id+'_updated')
        setattr(IWorkflowLiveSyncing, get_user_id_func_name, mocked_get_id_func)

        # Join the session again and check if user ID is updated
        self.assertTrue(self.live_syncing.join_live_session_by_url(self.stage_url, session_url, True))
        await self.wait(1)
        current_live_session = self.live_syncing.get_current_live_session()
        self.assertTrue(current_live_session)
        self.assertNotEqual(current_live_session.logged_user_id, old_user_id)

        # Restore the function
        setattr(IWorkflowLiveSyncing, get_user_id_func_name, native_get_id_func)

    async def test_other_interfaces(self):
        self.live_syncing.mute_live_session_merge_notice("omniverse://fake-test-server/a.usd")
        self.live_syncing.mute_live_session_merge_notice("omniverse://fake-test-server/b.usd")
        self.assertTrue(self.live_syncing.is_live_session_merge_notice_muted("omniverse://fake-test-server/a.usd"))
        self.assertTrue(self.live_syncing.is_live_session_merge_notice_muted("omniverse://fake-test-server/b.usd"))
        self.live_syncing.unmute_live_session_merge_notice("omniverse://fake-test-server/a.usd")
        self.assertFalse(self.live_syncing.is_live_session_merge_notice_muted("omniverse://fake-test-server/a.usd"))
        self.assertTrue(self.live_syncing.is_live_session_merge_notice_muted("omniverse://fake-test-server/b.usd"))

        # OMFP-2410: ensure it's not crashed with invalid session handle.
        interface = self.live_syncing._live_syncing_interface
        layers_instance = self.live_syncing._layers_instance
        self.assertFalse(interface.is_valid_live_session(layers_instance, None))

    async def test_create_session_for_non_omniverse_layer(self):
        await omni.usd.get_context().new_stage_async()
        live_session = self.live_syncing.create_live_session("test")
        self.assertFalse(live_session)

        error_type = self.layers.get_last_error_type()
        self.assertEqual(error_type, LayerErrorType.LIVE_SESSION_NOT_SUPPORTED)

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_join_session_with_url(self):
        session_url = omni.client.combine_urls(self.stage_url, ".live/test.live/customized_session.live")
        self.assertFalse(self.live_syncing.join_live_session_by_url(self.stage_url, session_url, False))
        self.assertTrue(self.live_syncing.join_live_session_by_url(self.stage_url, session_url, True))
        current_live_session = self.live_syncing.get_current_live_session()
        self.assertTrue(current_live_session)
        self.assertTrue(self.live_syncing.is_stage_in_live_session())
        self.assertTrue(self.live_syncing.is_in_live_session())
        self.assertTrue(self.live_syncing.is_layer_in_live_session(self.stage_url))
        self.assertEqual(current_live_session.name, "customized_session")
        self.assertEqual(current_live_session.url, session_url)
        self.assertTrue(self.live_syncing.get_live_session_by_url(session_url))
        self.live_syncing.stop_all_live_sessions()

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_live_session_for_reference_prim(self):
        reference_prim = self.stage.DefinePrim(self.reference_prim_path)
        reference_prim.GetReferences().AddReference(self.reference)
        await self.__test_live_session_for_prim(self.reference_prim_path, True)

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_live_session_for_payload_prim(self):
        payload_prim = self.stage.DefinePrim(self.payload_prim_path)
        payload_prim.GetPayloads().AddPayload(self.payload)
        await self.__test_live_session_for_prim(self.payload_prim_path, False)

    async def __create_and_verify_10_live_prims(self):
        all_references = []
        for i in range(10):
            reference_prim = self.stage.DefinePrim(self.reference_prim_path + str(i))
            reference_prim.GetReferences().AddReference(self.reference)
            await self.__test_live_session_for_prim(reference_prim.GetPath(), True, False)
            all_references.append(reference_prim.GetPath())

        return all_references

    async def __stop_live_session_for_reference(self, all_references, index):
        self.live_syncing.stop_live_session(self.reference, prim_path=all_references[index])
        await self.wait(2)
        for i in range(10):
            prim_path = all_references[i]
            if i == index:
                self.assertFalse(self.live_syncing.is_prim_in_live_session(prim_path))
            else:
                self.assertTrue(self.live_syncing.is_prim_in_live_session(prim_path))

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_live_session_for_multiple_references(self):
        all_references = await self.__create_and_verify_10_live_prims()
        self.assertTrue(self.live_syncing.is_layer_in_live_session(self.reference))
        self.assertTrue(self.live_syncing.is_layer_in_live_session(self.reference, live_prim_only=True))
        reference_prim = self.stage.DefinePrim("/AnotherReference")
        reference_prim.GetReferences().AddReference("", all_references[5])
        reference_path = reference_prim.GetPath()
        self.assertTrue(self.live_syncing.is_prim_in_live_session(reference_path))
        self.assertTrue(self.live_syncing.is_prim_in_live_session(reference_path, self.reference))
        self.assertTrue(self.live_syncing.is_prim_in_live_session(reference_path, self.reference, True))
        await self.__stop_live_session_for_reference(all_references, 5)
        self.assertFalse(self.live_syncing.is_prim_in_live_session(reference_path))
        self.assertFalse(self.live_syncing.is_prim_in_live_session(reference_path, self.reference))
        self.assertFalse(self.live_syncing.is_prim_in_live_session(reference_path, self.reference, True))

        stage = self.live_syncing.usd_context.get_stage()
        session_layer = stage.GetSessionLayer()
        current_session = self.live_syncing.get_current_live_session(self.reference)
        self.assertTrue(current_session)
        for i in range(10):
            # Index 5 is stoppped.
            if i == 5:
                continue

            prim_path = all_references[i]
            prim_spec = session_layer.GetPrimAtPath(prim_path)
            self.assertTrue(prim_spec)
            self.assertTrue(self.live_syncing.is_prim_in_live_session(prim_path))
            self.assertTrue(self._has_reference_or_payload(prim_spec, current_session.root, True))

        stage.RemovePrim(all_references[0])
        await self.wait(3)
        self.assertFalse(self.live_syncing.is_prim_in_live_session(all_references[0]))

        for i in range(10):
            if i == 5 or i == 0:
                continue

            prim_path = all_references[i]
            prim_spec = session_layer.GetPrimAtPath(prim_path)
            self.assertTrue(prim_spec)
            self.assertTrue(self.live_syncing.is_prim_in_live_session(prim_path))
            self.assertTrue(self._has_reference_or_payload(prim_spec, current_session.root, True))

        # Stop all live sessions about this layer.
        self.live_syncing.stop_live_session(self.reference)
        await self.wait(200)
        self.assertFalse(self.live_syncing.is_layer_in_live_session(self.reference))
        self.assertFalse(self.live_syncing.is_stage_in_live_session())
        for i in range(10):
            prim_path = all_references[i]
            self.assertFalse(self.live_syncing.is_prim_in_live_session(prim_path))
        self.assertFalse(self.live_syncing.is_layer_in_live_session(self.reference, live_prim_only=True))

    def _has_reference_or_payload(self, prim_spec, reference_path, reference):
        if reference:
            if not prim_spec or not prim_spec.HasInfo(Sdf.PrimSpec.ReferencesKey):
                return False

            op = prim_spec.GetInfo(Sdf.PrimSpec.ReferencesKey)
        else:
            if not prim_spec or not prim_spec.HasInfo(Sdf.PrimSpec.PayloadKey):
                return False

            op = prim_spec.GetInfo(Sdf.PrimSpec.PayloadKey)

        items = []
        items = op.ApplyOperations(items)

        for item in items:
            if item.assetPath == reference_path:
                return True

        return False

    async def __test_live_session_for_prim(self, prim_path, reference=True, unique_live_session=True):
        if reference:
            layer_identifier = self.reference
        else:
            layer_identifier = self.payload

        if unique_live_session:
            self.assertEqual(len(self.live_syncing.get_all_live_sessions(layer_identifier)), 0)

        live_session = self.live_syncing.find_live_session_by_name(layer_identifier, "test")
        if not live_session:
            live_session = self.live_syncing.create_live_session("test", layer_identifier=layer_identifier)
        self.assertTrue(live_session)

        self.assertTrue(self.live_syncing.join_live_session(live_session, prim_path))
        current_session = self.live_syncing.get_current_live_session(layer_identifier)
        self.assertTrue(current_session)
        self.assertTrue(current_session.name, live_session.name)
        all_live_sessions = self.live_syncing.get_all_current_live_sessions(prim_path=prim_path)
        self.assertEqual(len(all_live_sessions), 1)
        self.assertEqual(all_live_sessions[0].base_layer_identifier, layer_identifier)

        # Mock does not support re-parenting live prim for now.
        if not is_in_live_session_mocking():
            # Re-parent will keep the live session.
            move_to_path = Sdf.Path("/move_to_test_path")
            omni.kit.commands.execute(
                "MovePrim", path_from=prim_path, path_to=move_to_path, destructive=False,
                stage_or_context=self.stage
            )

            self.assertTrue(self.live_syncing.is_prim_in_live_session(move_to_path))
            all_live_sessions = self.live_syncing.get_all_current_live_sessions(prim_path=move_to_path)
            self.assertEqual(len(all_live_sessions), 1)
            self.assertEqual(all_live_sessions[0].base_layer_identifier, layer_identifier)

        # Undo will recover the prim and its live session.
        omni.kit.undo.undo()
        self.assertTrue(self.live_syncing.is_prim_in_live_session(prim_path))
        all_live_sessions = self.live_syncing.get_all_current_live_sessions(prim_path=prim_path)
        self.assertEqual(len(all_live_sessions), 1)
        self.assertEqual(all_live_sessions[0].base_layer_identifier, layer_identifier)

        result, server_info = await omni.client.get_server_info_async(layer_identifier)
        self.assertTrue(result == omni.client.Result.OK)
        self.assertEqual(server_info.username, current_session.logged_user_name)
        self.assertEqual(server_info.connection_id, current_session.logged_user_id)

        root_layer = self.stage.GetRootLayer()
        session_layer = self.stage.GetSessionLayer()

        prim_spec = root_layer.GetPrimAtPath(prim_path)
        self.assertFalse(self._has_reference_or_payload(prim_spec, current_session.root, reference))
        prim_spec = session_layer.GetPrimAtPath(prim_path)
        self.assertTrue(self._has_reference_or_payload(prim_spec, current_session.root, reference))

        self.assertTrue(self.live_syncing.is_layer_in_live_session(layer_identifier))
        if unique_live_session:
            self.live_syncing.stop_live_session(layer_identifier)
            self.assertFalse(self.live_syncing.is_layer_in_live_session(layer_identifier))

            prim_spec = root_layer.GetPrimAtPath(prim_path)
            self.assertFalse(self._has_reference_or_payload(prim_spec, current_session.root, reference))
            prim_spec = session_layer.GetPrimAtPath(prim_path)
            self.assertFalse(self._has_reference_or_payload(prim_spec, current_session.root, reference))

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_open_stage_with_live_session(self):
        live_session = self.live_syncing.create_live_session("test", layer_identifier=self.stage_url)
        self.assertTrue(live_session)

        (success, _) = await self.live_syncing.open_stage_with_live_session_async(self.stage_url, "test")
        self.assertTrue(success)

        current_live_session = self.live_syncing.get_current_live_session()
        self.assertTrue(current_live_session is not None)
        self.assertEqual(current_live_session.name, "test")
        self.assertEqual(current_live_session.base_layer_identifier, self.stage_url)

        # Test with query string
        url = omni.client.break_url(self.stage_url)
        query = "live_session_name=test"
        stage_url = omni.client.make_url(scheme=url.scheme, path=url.path, host=url.host, query=query)
        (success, _) = await self.live_syncing.open_stage_with_live_session_async(stage_url)
        self.assertTrue(success)

        current_live_session = self.live_syncing.get_current_live_session()
        self.assertTrue(current_live_session is not None)
        self.assertEqual(current_live_session.name, "test")
        self.assertEqual(current_live_session.base_layer_identifier, self.stage_url)

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_edit_mode_change(self):
        event_stream = self.layers.get_event_stream()

        cancelled_live_session = None
        def _on_layer_event(event: carb.events.IEvent):
            nonlocal cancelled_live_session

            payload = get_layer_event_payload(event)
            if payload.event_type == LayerEventType.LIVE_SESSION_JOINING:
                identifier = payload.identifiers_or_spec_paths[0]
                cancelled_live_session = self.live_syncing.try_cancelling_live_session_join(identifier)

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        live_session = self.live_syncing.find_live_session_by_name(self.stage_url, "test")
        if not live_session:
            live_session = self.live_syncing.create_live_session("test", layer_identifier=self.stage_url)

        # Cancel session join will not influence edit mode.
        self.layers.set_edit_mode(LayerEditMode.AUTO_AUTHORING)
        self.assertFalse(self.live_syncing.join_live_session(live_session))
        await self.wait(3)
        self.assertEqual(self.layers.get_edit_mode(), LayerEditMode.AUTO_AUTHORING)

        # Join live session will exit auto authoring
        subscription = None
        self.assertTrue(self.live_syncing.join_live_session(live_session))
        await self.wait(3)
        self.assertEqual(self.layers.get_edit_mode(), LayerEditMode.NORMAL)

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_session_management(self):
        for layer_identifier in [self.sublayer, self.stage_url]:
            await self.__test_session_management_internal(layer_identifier, False)

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_session_management_merge_to_new_layer(self):
        await self.__test_session_management_internal(self.sublayer, True)

    @unittest.skipIf(not enable_server_tests(), "")
    async def test_try_cancelling_live_session_join(self):
        event_stream = self.layers.get_event_stream()

        cancelled_live_session = None
        def _on_layer_event(event: carb.events.IEvent):
            nonlocal cancelled_live_session

            payload = get_layer_event_payload(event)
            if payload.event_type == LayerEventType.LIVE_SESSION_JOINING:
                identifier = payload.identifiers_or_spec_paths[0]
                cancelled_live_session = self.live_syncing.try_cancelling_live_session_join(identifier)

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        live_session = self.live_syncing.find_live_session_by_name(self.stage_url, "test")
        if not live_session:
            live_session = self.live_syncing.create_live_session("test", layer_identifier=self.stage_url)

        self.assertFalse(self.live_syncing.join_live_session(live_session))
        self.assertTrue(cancelled_live_session is not None)
        self.assertEqual(cancelled_live_session.base_layer_identifier, self.stage_url)
        self.assertFalse(self.live_syncing.is_layer_in_live_session(self.stage_url))
        self.assertFalse(self.live_syncing.get_current_live_session(self.stage_url))

    async def __test_session_management_internal(self, layer_identifier, merge_to_new_layer=False, prim_path=None):
        is_root_layer = layer_identifier == self.usd_context.get_stage_url()

        event_stream = self.layers.get_event_stream()

        joining_payload = None
        payload = None
        merge_started = None
        merge_ended = None

        def _on_layer_event(event: carb.events.IEvent):
            nonlocal joining_payload
            nonlocal payload
            nonlocal merge_started
            nonlocal merge_ended
            temp = get_layer_event_payload(event)
            if (
                temp.event_type == LayerEventType.LIVE_SESSION_LIST_CHANGED or
                temp.event_type == LayerEventType.LIVE_SESSION_STATE_CHANGED or
                temp.event_type == LayerEventType.LIVE_SESSION_JOINING
            ):
                if temp.event_type == LayerEventType.LIVE_SESSION_JOINING:
                    joining_payload = temp
                payload = temp
            elif temp.event_type == LayerEventType.LIVE_SESSION_MERGE_STARTED:
                merge_started = temp
            elif temp.event_type == LayerEventType.LIVE_SESSION_MERGE_ENDED:
                merge_ended = temp

        subscription = event_stream.create_subscription_to_pop(_on_layer_event, name="layer events")

        self.assertEqual(len(self.live_syncing.get_all_live_sessions(layer_identifier)), 0)

        live_session = self.live_syncing.create_live_session("test", layer_identifier=layer_identifier)
        self.assertTrue(live_session)
        self.assertEqual(live_session.name, "test")
        self.assertTrue(live_session.merge_permission)
        self.assertTrue(live_session.channel_url)
        self.assertTrue(live_session.url)
        self.assertTrue(live_session.root)
        self.assertTrue(live_session.owner)

        live_session_ref = self.live_syncing.find_live_session_by_name(layer_identifier, "test")
        self.assertEqual(live_session, live_session_ref)

        live_session_ref = self.live_syncing.get_live_session_by_url(live_session.url)
        self.assertEqual(live_session, live_session_ref)

        sessions = self.live_syncing.get_all_live_sessions(layer_identifier)
        self.assertEqual(len(sessions), 1)
        session = sessions[0]
        self.assertEqual(live_session.name, session.name)
        self.assertEqual(live_session.owner, session.owner)
        self.assertEqual(live_session.url, session.url)
        self.assertEqual(live_session.root, session.root)
        self.assertEqual(live_session.channel_url, session.channel_url)
        self.assertEqual(live_session.merge_permission, session.merge_permission)

        await self.wait()
        self.assertTrue(payload)
        self.assertEqual(payload.event_type, LayerEventType.LIVE_SESSION_LIST_CHANGED)

        live_session = self.live_syncing.create_live_session("test", layer_identifier=layer_identifier)
        # Create session with the same name will fail.
        self.assertFalse(live_session)
        self.assertEqual(self.layers.get_last_error_type(), LayerErrorType.ALREADY_EXISTS)

        # Create session with empty name will fail.
        live_session = self.live_syncing.create_live_session("", layer_identifier=layer_identifier)
        self.assertFalse(live_session)
        self.assertEqual(self.layers.get_last_error_type(), LayerErrorType.INVALID_PARAM)

        live_session = self.live_syncing.create_live_session("test2", layer_identifier=layer_identifier)
        sessions = self.live_syncing.get_all_live_sessions(layer_identifier)
        self.assertEqual(len(sessions), 2)
        self.live_syncing.stop_live_session(layer_identifier)
        await self.wait()

        payload = None
        self.assertTrue(self.live_syncing.join_live_session(live_session))
        current_session = self.live_syncing.get_current_live_session(layer_identifier)
        self.assertTrue(current_session)
        self.assertTrue(current_session.name, live_session.name)
        result, server_info = await omni.client.get_server_info_async(layer_identifier)
        self.assertTrue(result == omni.client.Result.OK)
        self.assertEqual(server_info.username, current_session.logged_user_name)
        self.assertEqual(server_info.connection_id, current_session.logged_user_id)

        self.assertTrue(self.live_syncing.is_layer_in_live_session(layer_identifier))
        if is_root_layer:
            self.assertTrue(self.usd_context.is_stage_live())
            self.assertEqual(self.usd_context.get_stage_live_mode(), omni.usd.StageLiveModeType.ALWAYS_ON)
        await self.wait()
        self.assertTrue(joining_payload)
        self.assertEqual(joining_payload.event_type, LayerEventType.LIVE_SESSION_JOINING)
        self.assertEqual(joining_payload.identifiers_or_spec_paths, [layer_identifier])
        self.assertEqual(joining_payload.layer_identifier, layer_identifier)
        self.assertTrue(payload)
        self.assertEqual(payload.event_type, LayerEventType.LIVE_SESSION_STATE_CHANGED)
        self.assertEqual(payload.identifiers_or_spec_paths, [layer_identifier])
        self.assertEqual(payload.layer_identifier, layer_identifier)
        self.assertTrue(payload.is_layer_influenced(layer_identifier))
        self.assertFalse(payload.is_layer_influenced(self.usd_context.get_stage().GetSessionLayer()))

        all_sublayers = set(LayerUtils.get_all_sublayers(self.stage, is_root_layer, True, False))
        all_sublayers.discard(self.stage_url)
        all_sublayers.discard(self.sublayer)
        all_sublayers.discard(self.sublayer2)
        for sublayer in all_sublayers:
            self.assertTrue(self.live_syncing.is_live_session_layer(sublayer))

        all_sublayers = set(self.live_syncing.get_current_live_session_layers(layer_identifier))
        all_sublayers.discard(self.sublayer2)
        self.assertEqual(len(all_sublayers), 1)
        self.assertTrue(self.live_syncing.is_live_session_layer(all_sublayers.pop()))

        # Makes some edits
        root_live_layer = Sdf.Find(current_session.root)
        self.assertTrue(root_live_layer)

        layer_content = """\
            #usda 1.0
            (
                subLayers = [
                    @omniverse://test-ov-fake-server/fake/path/sublayers/level2/sublayer2.usd@
                ]
            )

            over "root"
            {
                over "test_prim" (
                    prepend payload = @../invalid/payload2.usd@
                    prepend references = @../invalid/reference2.usd@
                )
                {
                    asset[] AssetArray = [@OmniPBR.mdl@]
                    bool[] BoolArray = [0, 1]
                    float[] FloatArray = [1, 2, 3]
                    int[] IntArray = [1, 2, 3]
                    string[] StringArray = ["string1", "string2", "string3"]
                    int test = 3
                    asset test2 = @../../invalid/path.usd@
                    asset test3 = @OmniPBR.mdl@
                    token[] TokenArray = ["token1", "token2", "token3"]
                }
            }
        """

        if is_root_layer:
            expected_string = """
#usda 1.0
(
    customLayerData = {
        dictionary omni_layer = {
            dictionary locked = {
                bool "./test2.usd" = 0
            }
        }
    }
    endTimeCode = 0
    startTimeCode = -1
    subLayers = [
        @omniverse://localhost/Projects/omni.kit.usd.layers/test_live_syncing/test2.usd@
    ]
)

over "root"
{
    over "test_prim" (
        prepend payload = @./.live/test.live/invalid/payload2.usd@
        prepend references = @./.live/test.live/invalid/reference2.usd@
    )
    {
        asset[] AssetArray = [@OmniPBR.mdl@]
        bool[] BoolArray = [0, 1]
        float[] FloatArray = [1, 2, 3]
        int[] IntArray = [1, 2, 3]
        string[] StringArray = ["string1", "string2", "string3"]
        int test = 3
        asset test2 = @./.live/invalid/path.usd@
        asset test3 = @OmniPBR.mdl@
        token[] TokenArray = ["token1", "token2", "token3"]
    }
}
            """
        else:
            expected_string = """
#usda 1.0

over "root"
{
    over "test_prim" (
        prepend payload = @./.live/test2.live/invalid/payload2.usd@
        prepend references = @./.live/test2.live/invalid/reference2.usd@
    )
    {
        asset[] AssetArray = [@OmniPBR.mdl@]
        bool[] BoolArray = [0, 1]
        float[] FloatArray = [1, 2, 3]
        int[] IntArray = [1, 2, 3]
        string[] StringArray = ["string1", "string2", "string3"]
        int test = 3
        asset test2 = @./.live/invalid/path.usd@
        asset test3 = @OmniPBR.mdl@
        token[] TokenArray = ["token1", "token2", "token3"]
    }
}
            """

        root_live_layer.ImportFromString(layer_content)
        payload = None
        merge_started = None
        merge_ended = None
        if merge_to_new_layer:
            new_sublayer = Sdf.Layer.CreateNew(self.sublayer2)
            self.live_syncing.merge_live_session_changes_to_specific_layer(layer_identifier, self.sublayer2, True, True)
            all_sublayers = set(LayerUtils.get_all_sublayers(self.stage, False, True, False))
            self.assertIn(self.sublayer2, all_sublayers)
            layer_identifier = layer_identifier
        elif is_root_layer:
            self.live_syncing.merge_changes_to_base_layers(True)
            layer_identifier = self.stage.GetRootLayer().identifier
        else:
            self.live_syncing.merge_live_session_changes(layer_identifier, True)
            layer_identifier = layer_identifier

        self.assertTrue(merge_started)
        self.assertTrue(merge_ended)
        self.assertTrue(merge_started.layer_identifier == layer_identifier)
        self.assertTrue(merge_ended.layer_identifier == layer_identifier)
        self.assertTrue(merge_ended.success)

        current_session = self.live_syncing.get_current_live_session(layer_identifier)
        self.assertFalse(current_session)
        if is_root_layer:
            self.assertFalse(self.live_syncing.is_in_live_session())
        else:
            self.assertFalse(self.live_syncing.is_layer_in_live_session(layer_identifier))
        await self.wait()
        self.assertTrue(payload)
        self.assertEqual(payload.event_type, LayerEventType.LIVE_SESSION_STATE_CHANGED)
        if merge_to_new_layer:
            layer = Sdf.Find(self.sublayer2)
        elif is_root_layer:
            layer = self.stage.GetRootLayer()
        else:
            layer = Sdf.Find(self.sublayer)

        string = layer.ExportToString()
        self.assertEqual(string.strip(), expected_string.strip())

        if merge_to_new_layer:
            LayerUtils.remove_sublayer(self.stage.GetRootLayer(), 0)
