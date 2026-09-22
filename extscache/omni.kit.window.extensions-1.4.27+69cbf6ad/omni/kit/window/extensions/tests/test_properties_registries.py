import carb.settings
import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.kit.window.extensions

from .utils import SyncEventHandler, open_window_and_sync

# pylint: disable=protected-access


class TestRegistries(omni.kit.test.AsyncTestCase):
    async def tearDown(self):
        instance = omni.kit.window.extensions.get_instance()()
        instance.show_window(False)

    async def test_add_remove_registry(self):  # noqa
        manager = omni.kit.app.get_app().get_extension_manager()
        settings = carb.settings.get_settings()

        def get_providers():
            return {p["name"] for p in manager.get_registry_providers()}

        await open_window_and_sync(True)
        instance = omni.kit.window.extensions.get_instance()()

        def get_model():
            widget = instance._window._exts_properties._registries_widget
            return widget._model

        model = get_model()
        model.set_default(model._children[0], True)

        providers_before = get_providers()
        # this can happen on TC & test will fail
        if not providers_before:
            print("no providers found, skipping test")
            return

        if carb.settings.get_settings().get("/exts/omni.kit.window.extensions/sync_registry"):  # pragma: no cover

            def get_default():
                return settings.get("/app/extensions/registryPublishDefault")

            default_before = get_default()
            self.assertEqual(model._children[0].name_model.as_string, default_before)

            # Add new registry using model
            model.add_empty()
            last = model._children[-1]
            last.url_model.as_string = "omniverse://kit-extensions.ov.nvidia.com/exts/kit/debug"
            # name is set automatically
            model.save()
            model = None

            # sync event from save
            sync = SyncEventHandler()
            await sync.wait_for_sync_event()
            sync.destroy()

            # Wait to propagate and check
            await ui_test.human_delay(10)
            self.assertEqual(get_providers() - providers_before, {"kit/debug"})

            # Make it default now
            get_model().set_default(get_model()._children[-1], True)
            await ui_test.human_delay()
            self.assertEqual(get_default(), "kit/debug")

            # Remove!
            get_model().remove_item(get_model()._children[-1])
            await ui_test.human_delay(10)
            self.assertEqual(get_providers(), providers_before)

            # sync event from remove
            sync = SyncEventHandler()
            await sync.wait_for_sync_event()
            sync.destroy()

            # get back default:
            get_model()._children[0].default_model.as_bool = True
            await ui_test.human_delay()
            self.assertEqual(get_default(), default_before)
