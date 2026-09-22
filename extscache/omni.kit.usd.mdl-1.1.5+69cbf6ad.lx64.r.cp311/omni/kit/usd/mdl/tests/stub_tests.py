import importlib
from omni.kit.test.async_unittest import AsyncTestCase

class PythonStub(AsyncTestCase):
    def _assert_module_imports(self, module_name: str):
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            self.fail(f"Module '{module_name}' not found")
        except ImportError as e:
            self.fail(f"Module '{module_name}' found but failed to import: {e}")

        self.assertIsNotNone(module)

    async def test_usd_mdl(self):
        self._assert_module_imports("usd.mdl")

    async def test_UsdMdl(self):
        self._assert_module_imports("UsdMdl")