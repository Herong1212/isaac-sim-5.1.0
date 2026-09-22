import omni.kit.test
import omni.kit.pipapi


class TestPipApi(omni.kit.test.AsyncTestCase):
    async def test_pipapi_install(self):
        # Install simple package and import it.
        omni.kit.pipapi.install(
            "toml", version="0.10.1", ignore_import_check=True, ignore_cache=True
        )  # SWIPAT filed under: http://nvbugs/3060676
        import toml

        self.assertIsNotNone(toml)


    async def test_pipapi_install_non_existing(self):
        res = omni.kit.pipapi.install("weird_package_name_2312515")
        self.assertFalse(res)
