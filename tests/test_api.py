"""Tests of the read-only API contract without a Home Assistant installation."""
import importlib.util
import pathlib
import unittest
from unittest.mock import AsyncMock

spec = importlib.util.spec_from_file_location("headscale_api", pathlib.Path(__file__).parents[1] / "custom_components/headscale_monitor/api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class Response:
    def __init__(self, status, payload):
        self.status, self.payload = status, payload
    async def __aenter__(self):
        return self
    async def __aexit__(self, *_):
        return False
    async def json(self):
        return self.payload


class ClientTests(unittest.IsolatedAsyncioTestCase):
    def test_urls(self):
        self.assertEqual(api.normalize_url("https://EXAMPLE.org/"), "https://example.org")
        for value in ("http://example.org", "https://user:pass@example.org", "https://example.org/path", "https://example.org?token=x"):
            with self.assertRaises(ValueError):
                api.normalize_url(value)

    async def test_nodes_read_only_and_no_redirect(self):
        class Session:
            def get(self, url, **kwargs):
                self.url, self.kwargs = url, kwargs
                return Response(200, {"nodes": [{"id": "4", "online": True}]})
        session = Session()
        result = await api.HeadscaleClient(session, "https://example.org", "secret").nodes()
        self.assertTrue(result["4"]["online"])
        self.assertEqual(session.url, "https://example.org/api/v1/node")
        self.assertFalse(session.kwargs["allow_redirects"])
        self.assertEqual(session.kwargs["headers"]["Authorization"], "Bearer secret")

    async def test_failure_and_empty(self):
        class Session:
            def __init__(self, status, data): self.status, self.data = status, data
            def get(self, *args, **kwargs): return Response(self.status, self.data)
        for status in (401, 403):
            with self.assertRaises(api.HeadscaleAuthError):
                await api.HeadscaleClient(Session(status, {}), "https://example.org", "secret").nodes()
        with self.assertRaises(api.HeadscaleError):
            await api.HeadscaleClient(Session(200, {"nodes": [{"id": "1"}, {"id": "1"}]}), "https://example.org", "secret").nodes()
        self.assertEqual(await api.HeadscaleClient(Session(200, {}), "https://example.org", "secret").nodes(), {})
