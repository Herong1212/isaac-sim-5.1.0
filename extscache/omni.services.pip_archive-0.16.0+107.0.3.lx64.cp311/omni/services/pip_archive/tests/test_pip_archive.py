import omni.kit.test
import omni.kit.pipapi


class TestPipArchive(omni.kit.test.AsyncTestCase):
    async def test_pip_archive(self):
        # Take one of packages from deps/pip.toml, it should be prebundled and available without need for going into online index
        omni.kit.pipapi.install("prometheus_client", version="0.12.0", use_online_index=False)
        import prometheus_client

        self.assertIsNotNone(prometheus_client)
