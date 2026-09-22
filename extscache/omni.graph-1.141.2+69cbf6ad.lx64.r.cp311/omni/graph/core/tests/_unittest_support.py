"""Support for creating unittest style test cases that use OmniGraph components.

Note the leading underscore in the file name, indicating that it should not be imported directly. Instead use this:

.. code-block:: python

    import omni.graph.core.tests as ogts

There are three primary workflows for setting up unit test case classes that manage OmniGraph state.

If your test case uses OmniGraph and just wants a standard configuration while running then you can use the
predefined test case base class :py:class:`omni.graph.core.tests.OmniGraphTestCase`.

.. code-block:: python

    import omni.graph.core.tests as ogts
    class TestMyStuff(ogts.OmniGraphTestCase):
        async def test_my_stuff(self):
            pass  # My stuff always works

If instead you wish to make use of only a subset of the various OmniGraph configuration values or use your own test
base class then you can use :py:class:`omni.graph.core.tests.OmniGraphTestConfiguration` to build up a set of temporary
conditions in force while the test runs, such as using an empty scene, defining settings, etc.

.. code-block:: python

    import omni.graph.core.tests as ogts
    class TestMyStuff(omni.kit.test.AsyncTestCase):

        async def test_my_stuff(self):
            with ogts.OmniGraphTestConfiguration(clear_on_start=False):
                pass  # My stuff always works

You can also use the test case class constructor to define your own base class that can be used in multiple locations:

.. code-block:: python

    import omni.graph.core.tests as ogts
    MyDebugTestClass = ogts.test_case_class(clear_on_finish=False, clear_on_start=False)

    class TestMyStuff(MyDebugTestClass):
        async def test_my_stuff(self):
            pass  # My stuff always works
"""

from __future__ import annotations

import asyncio
import inspect
from contextlib import AsyncExitStack, ExitStack, asynccontextmanager, contextmanager

import omni.graph.core as og
import omni.graph.tools as ogt
import omni.kit
import omni.usd


# ==============================================================================================================
class OmniGraphTestConfiguration:
    """Class to manage testing configuration parameters as a context manager that brackets a test run.
    You can either use it around a single test to modify configuration for just that test:

    .. code-block:: python

        import omni.graph.core.tests as ogts
        class TestRun(ogts.OmniGraphTestCase):
            '''By default the tests in this class will clear the scene on start and finish of the test'''
            async def test_without_clearing(self):
                async with ogts.OmniGraphTestConfiguration(clear_on_start=False):
                    run_my_test()
                # Before this particular test the scene will not be cleared before starting

    See :py:func:`construct_test_class` for a way of applying it to every test in the test case.

    .. code-block:: python

        class TestRun(ogts.construct_test_class(clear_on_start=True)):
            async def test_without_clearing(self):
                run_my_test()

    If you can't change your base class you can still use it by adding it to the test case setUp/tearDown

    .. code-block:: python

        class TestRun(omni.kit.test.AsyncTestCase):
            async def setUp(self):
                self.configuration = ogts.OmniGraphTestConfiguration(clear_on_start=True)
                await self.configuration.__enter__()
            async def tearDown(self):
                await self.configuration.__exit__()
            async def test_without_clearing(self):
                run_my_test()

    It also has the ability to include user-defined contexts as part of the test configuration, which will be
    unwound in the order added using the standard *contextlib.{A}ExitStack()* functionality.

    .. code-block:: python

        @contextmanager
        def my_context():
            resource = acquire_my_resource()
            try:
                yield 1
            finally:
                release_my_resource(resource)

        @asynccontextmanager
        async def my_async_context():
            resource = await acquire_my_async_resource()
            try:
                yield 1
            finally:
                await release_my_async_resource(resource)

        my_configuration = OmniGraphTestConfiguration(contexts=[my_context], async_contexts=[my_async_context])
        MyCustomClass = ogts.construct_test_class(configuration=my_configuration)
        class TestRun(MyCustomClass):
            async def test_without_clearing(self):
                run_my_test()
    """

    def __init__(self, **kwargs):
        """Construct the stack objects that will hold the test contexts
        Args:
            clear_on_start (bool=False): Clear the scene before the test starts
            clear_on_finish (bool=False): Clear the scene after the test ends
            settings (dict=None): Dictionary of settingName:value to set while the test runs and restore after
            contexts (list=None): List of contextmanager functions or decorated classes to wrap the test runs
            async_contexts (list=None): List of asynccontextmanager functions or decorated classes to wrap the test runs
            extensions_enabled (list=None): List of the names of extensions to temporarily enable for the test
            extensions_disabled (list=None): List of the names of extensions to temporarily disable for the test

        Note:
            Be careful when using the extensions_{en,dis}abled options to ensure that you do not inadvertently force a
            hot reload of the extension containing the test.
        """
        self.stack = ExitStack()
        self.async_stack = AsyncExitStack()
        self.__kwargs = dict(kwargs)

    # --------------------------------------------------------------------------------------------------------------
    def __set_up_stack(self):
        """Define the parts of the ExitStack requested by the current keyword args"""

        @contextmanager
        def __enable_extensions(extensions: list[str]):
            manager = omni.kit.app.get_app().get_extension_manager()
            try:
                for name in extensions:
                    manager.set_extension_enabled_immediate(name, True)
                yield True
            finally:
                pass

        @contextmanager
        def __disable_extensions(extensions: list[str]):
            manager = omni.kit.app.get_app().get_extension_manager()
            try:
                for name in extensions:
                    manager.set_extension_enabled_immediate(name, False)
                yield True
            finally:
                pass

        for key, value in self.__kwargs.items():
            if key == "settings":
                for setting, temporary_value in value.items():
                    self.stack.enter_context(og.Settings.temporary(setting, temporary_value))
            elif key == "extensions_enabled":
                self.stack.enter_context(__enable_extensions(value))
            elif key == "extensions_disabled":
                self.stack.enter_context(__disable_extensions(value))
            elif key == "contexts":
                if not isinstance(value, list):
                    value = [value]
                for context in value:
                    self.stack.enter_context(context())

    # --------------------------------------------------------------------------------------------------------------
    async def __set_up_async_stack(self):
        """Define the parts of the AsyncExitStack requested by the current keyword args"""

        @asynccontextmanager
        async def __clear_scene_on_enter():
            try:
                yield await omni.usd.get_context().new_stage_async()
            finally:
                pass

        @asynccontextmanager
        async def __clear_scene_on_exit():
            try:
                yield None
            finally:
                await omni.usd.get_context().new_stage_async()

        for key, value in self.__kwargs.items():
            if key == "clear_on_start" and value:
                await self.async_stack.enter_async_context(__clear_scene_on_enter())
            if key == "clear_on_finish" and value:
                await self.async_stack.enter_async_context(__clear_scene_on_exit())
            if key == "async_contexts":
                if not isinstance(value, list):
                    value = [value]
                for context in value:
                    await self.async_stack.enter_async_context(context())

    # --------------------------------------------------------------------------------------------------------------
    def __enter__(self):
        """When used as a context manager this class calls this at the start of a 'with' clause"""
        self.__set_up_stack()
        asyncio.ensure_future(self.__set_up_async_stack())
        self.stack.__enter__()
        asyncio.ensure_future(self.async_stack.__aenter__())

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        """When used as a context manager this class calls this at the end of a 'with' clause"""
        self.stack.__exit__(exc_type, exc_value, exc_tb)
        asyncio.ensure_future(self.async_stack.__aexit__(exc_type, exc_value, exc_tb))

    # --------------------------------------------------------------------------------------------------------------
    async def __aenter__(self):
        """When used as an async context manager this class calls this at the start of a 'with' clause"""
        self.__set_up_stack()
        await self.__set_up_async_stack()
        self.stack.__enter__()
        await self.async_stack.__aenter__()

    async def __aexit__(self, exc_type=None, exc_value=None, exc_tb=None):
        """When used as an async context manager this class calls this at the end of a 'with' clause"""
        self.stack.__exit__(exc_type, exc_value, exc_tb)
        await self.async_stack.__aexit__(exc_type, exc_value, exc_tb)


# ==============================================================================================================
def construct_test_class(**kwargs):
    """Construct a new test case base class that configures the test in a predictable way.
    You can use the same parameters as :py:class:`OmniGraphTestConfiguration` to configure your test class,
    or you can construct one and pass it in as an argument
    Args:
        configuration (OmniGraphTestConfiguration): Full configuration definition
        deprecated (str | tuple[str, DeprecationLevel]): Used when this instantiation of the class has been deprecated
        base_class (object): Alternative base class for the test case, defaults to omni.kit.test.AsyncTestCase
    Other arguments can be seen in the parameters to :py:func:`OmniGraphTestConfiguration.setUp`

    Raises:
        TypeError if a base class was specified that is also a constructed class
    """
    # Check to see if an alternative base class was passed in
    base_class = kwargs.get("base_class", omni.kit.test.AsyncTestCase)

    # Issue the deprecation message if specified, but continue on
    deprecation = kwargs.get("deprecated", None)

    try:
        configuration = kwargs["configuration"]
        if not isinstance(configuration, OmniGraphTestConfiguration):
            raise TypeError(f"configuration only accepts type OmniGraphTestConfiguration, not {type(configuration)}")
    except KeyError:
        configuration = OmniGraphTestConfiguration(**kwargs)

    # --------------------------------------------------------------------------------------------------------------
    # Construct the customized test case base class object using the temporary setting and base class information
    class OmniGraphCustomTestCase(base_class):
        """A custom constructed test case base class that performs the prescribed setUp and tearDown actions."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__configuration = configuration
            self.__deprecation = deprecation

        async def setUp(self):
            """Set up the test by saving and then setting up all of the action contexts"""
            # Start with no test failures registered
            og.set_test_failure(False)

            if inspect.iscoroutinefunction(super().setUp):
                await super().setUp()
            else:
                super().setUp()

            if self.__deprecation is not None:
                if isinstance(self.__deprecation, tuple):
                    if len(self.__deprecation) != 2:
                        raise ValueError(
                            "deprecation argument can only be a message or (message, level) pair"
                            f" - saw {self.__deprecation}"
                        )
                    ogt.DeprecateMessage.deprecated(self.__deprecation[0], self.__deprecation[1])
                else:
                    ogt.DeprecateMessage.deprecated(self.__deprecation)

            await self.__configuration.__aenter__()  # noqa PLC2801

        async def tearDown(self):
            """Complete the test by tearing down all of the action contexts"""
            await self.__configuration.__aexit__()
            if inspect.iscoroutinefunction(super().setUp):
                await super().tearDown()
            else:
                super().tearDown()

    # Recursive class definition is more complicated and can be done other ways
    if base_class.__name__ == "OmniGraphCustomTestCase":
        raise TypeError(
            "Recursive class definition is not supported (construct_test_class(base_class=construct_test_class(...)))"
        )

    # Return the constructed class definition
    return OmniGraphCustomTestCase
