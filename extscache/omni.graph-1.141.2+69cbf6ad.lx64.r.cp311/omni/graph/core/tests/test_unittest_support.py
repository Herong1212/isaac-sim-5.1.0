"""Tests that exercise the capabilities provided for OmniGraph unit testing"""

from contextlib import asynccontextmanager, contextmanager

import carb
import omni.graph.core.tests as ogts
import omni.graph.tools as ogt
import omni.kit.test
import omni.usd

# Name of a fake setting that will be used for testing
TEST_SETTING = "/not/a/setting"


# ==============================================================================================================
class TestOmniGraphTestFeatures(omni.kit.test.AsyncTestCase):
    """Run targeted tests on the test helper functions and classes directly, not as part of the test definition"""

    async def test_configuration_class(self):
        """Tests the functionality of customized OmniGraphTestConfiguration objects"""
        settings = carb.settings.get_settings()
        with ogts.OmniGraphTestConfiguration(settings={TEST_SETTING: True}):
            self.assertEqual(settings.get(TEST_SETTING), True)
        self.assertEqual(settings.get(TEST_SETTING), None)

    # --------------------------------------------------------------------------------------------------------------
    CONTEXT_FLAG = 0

    async def test_custom_contexts(self):
        """Tests the functionality of providing my own custom contexts via the contextmanager decorator"""

        @contextmanager
        def context_add_1():
            TestOmniGraphTestFeatures.CONTEXT_FLAG = TestOmniGraphTestFeatures.CONTEXT_FLAG + 1
            try:
                yield True
            finally:
                TestOmniGraphTestFeatures.CONTEXT_FLAG = TestOmniGraphTestFeatures.CONTEXT_FLAG - 1

        @asynccontextmanager
        async def async_context_add_10():
            TestOmniGraphTestFeatures.CONTEXT_FLAG = TestOmniGraphTestFeatures.CONTEXT_FLAG + 10
            try:
                yield True
            finally:
                TestOmniGraphTestFeatures.CONTEXT_FLAG = TestOmniGraphTestFeatures.CONTEXT_FLAG - 10

        my_configuration = ogts.OmniGraphTestConfiguration(
            contexts=[context_add_1], async_contexts=[async_context_add_10]
        )

        self.assertEqual(TestOmniGraphTestFeatures.CONTEXT_FLAG, 0)
        with my_configuration:
            self.assertEqual(TestOmniGraphTestFeatures.CONTEXT_FLAG, 1)
        self.assertEqual(TestOmniGraphTestFeatures.CONTEXT_FLAG, 0)

        async with my_configuration:
            self.assertEqual(TestOmniGraphTestFeatures.CONTEXT_FLAG, 11)
        self.assertEqual(TestOmniGraphTestFeatures.CONTEXT_FLAG, 0)

    # --------------------------------------------------------------------------------------------------------------
    async def test_construct_test_class(self):
        """Tests the ability to create a base class using the construct_test_class() function"""
        # Test the deprecated keyword
        message = "I am deprecated"
        deprecated_class = ogts.construct_test_class(deprecated=message)
        self.assertTrue(omni.kit.test.AsyncTestCase in deprecated_class.__bases__)
        with ogt.DeprecateMessage.NoLogging():
            instance = deprecated_class()
            await instance.setUp()
            messages_logged = ogt.DeprecateMessage.messages_logged()
            self.assertTrue(message in messages_logged, f"'{message}' not in {messages_logged}")

        # Test the base_class keyword
        class BaseTestClass(omni.kit.test.AsyncTestCase):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.i_exist = True

        derived_class = ogts.construct_test_class(base_class=BaseTestClass)
        instance = derived_class()
        self.assertTrue(hasattr(instance, "i_exist") and instance.i_exist, f"No 'i_exist' in {dir(instance)}")
        self.assertTrue(isinstance(instance, BaseTestClass))

        # Test the configure keyword
        configuration = ogts.OmniGraphTestConfiguration(settings={TEST_SETTING: True})
        configured_class = ogts.construct_test_class(configuration=configuration)
        instance = configured_class()
        self.assertEqual(type(configuration), type(instance._OmniGraphCustomTestCase__configuration))  # noqa PLW0212

        with self.assertRaises(TypeError):
            _ = ogts.construct_test_class(configuration=3)

        # Test the extensions_enabled keyword
        test_extension = "omni.graph.image.nodes"
        manager = omni.kit.app.get_app().get_extension_manager()
        was_enabled = manager.is_extension_enabled(test_extension)
        manager.set_extension_enabled_immediate(test_extension, False)
        configuration = ogts.OmniGraphTestConfiguration(extensions_enabled=[test_extension])
        with configuration:
            self.assertTrue(manager.is_extension_enabled(test_extension))
        manager.set_extension_enabled_immediate(test_extension, was_enabled)

        # Test the extensions_disabled keyword
        manager.set_extension_enabled_immediate(test_extension, True)
        configuration = ogts.OmniGraphTestConfiguration(extensions_disabled=[test_extension])
        with configuration:
            self.assertFalse(manager.is_extension_enabled(test_extension))
        manager.set_extension_enabled_immediate(test_extension, was_enabled)


# ==============================================================================================================
class TestStandardConfiguration(ogts.OmniGraphTestCase):
    """Run tests using the standard OmniGraph test configuration"""

    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    async def test_settings(self):
        """Test that the standard settings are applied by the test case"""


# ==============================================================================================================
class TestCustomSetUp(omni.kit.test.AsyncTestCase):
    """Run tests using an OmniGraphTestConfiguration customization using the Kit base class"""

    async def test_configuration(self):
        with ogts.OmniGraphTestConfiguration(settings={TEST_SETTING: True}):
            self.assertTrue(carb.settings.get_settings().get(TEST_SETTING))


# ==============================================================================================================
MyTestClass = ogts.construct_test_class(settings={TEST_SETTING: True})


class TestManualConfiguration(MyTestClass):
    """Run tests using a custom created base test class"""

    async def test_constructed_base_class(self):
        self.assertTrue(carb.settings.get_settings().get(TEST_SETTING))


# ==============================================================================================================
class TestCustomBaseClass(MyTestClass):
    """Run tests using a custom created base test class derived from another custom base class"""

    async def test_constructed_derived_class(self):
        with self.assertRaises(TypeError):
            MyDerivedTestClass = ogts.construct_test_class(base_class=MyTestClass)  # noqa F841


# ==============================================================================================================
class TestOverrideSetUp(ogts.OmniGraphTestCase):
    """Run tests using a customization that is based on the standard configuration"""

    async def test_configuration(self):
        with ogts.OmniGraphTestConfiguration(settings={TEST_SETTING: True}):
            self.assertTrue(carb.settings.get_settings().get(TEST_SETTING))
