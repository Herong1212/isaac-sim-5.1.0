omni.kit.test
###########################

Python asyncio-centric testing system.

To create a test derive from :class:`omni.kit.test.AsyncTestCase` and add a method that starts with ``test_``, like in :mod:`unittest`. Method can be either async or regular one.

.. code:: python

    import omni.kit.test

    class MyTest(omni.kit.test.AsyncTestCase):
        async def setUp(self):
            pass

        async def tearDown(self):
            pass

        # Actual test, notice it is "async" function, so "await" can be used if needed
        async def test_hello(self):
            self.assertEqual(10, 10)

Test class must be defined in "tests" submodule of your public extension module. For example if your ``extension.toml`` defines:

.. code:: toml

    [[python.module]]
    name = "omni.foo"

``omni.foo.tests.MyTest`` should be a path to your test. Test system will automatically discover and import ``omni.foo.tests`` module. Using ``tests`` submodule of your extension module is a recommended way to organize tests. That keeps tests together with extension, but not too coupled with the actual module they test, so that they can import module with absolute path (e.g. ``import omni.foo``) and test it the way user will see them.

Refer to ``omni.example.hello`` extension as a simplest example of extension with a python test.


Settings
**********

For the settings refer to ``extension.toml`` file:

.. literalinclude:: ../config/extension.toml
  :language: toml

They can be used to filter, automatically run tests and quit.


API Reference
***************

.. automodule:: omni.kit.test
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :imported-members:
    :exclude-members: contextlib, suppress
