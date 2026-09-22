import omni.kit.test

from omni.services.core import main
from omni.services.client import AsyncClient

from omni.services.facilities.monitoring.metrics.middleware import MetricsMiddleware, metrics


class TestMetricsMiddleware(omni.kit.test.AsyncTestCase):

    async def setUp(self):
        main.register_endpoint("get", "/metrics", metrics, tags=["metrics"])
        main.get_app().add_middleware(MetricsMiddleware)

        async def ping():
            return "pong"

        main.register_endpoint("get", "/ping", ping)
        self._client = AsyncClient("local://")

    async def tearDown(self):
        main.deregister_endpoint("get", "/ping")
        main.deregister_endpoint("get", "/metrics")
        main.get_app().user_middleware.pop(0)

    async def test_metrics_middleware(self):
        for _ in range(10):
            await self._client.ping()

        metrics = await self._client.metrics()
        self.assertTrue(b"TYPE kit_services_requests_total counter" in metrics)
        self.assertTrue(b"TYPE kit_services_requests_active gauge" in metrics)
