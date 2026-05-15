"""Regression tests for authentication on sensitive mounted routers."""

import unittest
import importlib.util
import sys
import types
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


if "slowapi" not in sys.modules and importlib.util.find_spec("slowapi") is None:
    slowapi_module = types.ModuleType("slowapi")
    slowapi_util_module = types.ModuleType("slowapi.util")

    class _Limiter:
        def __init__(self, *args, **kwargs):
            pass

        def limit(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    slowapi_module.Limiter = _Limiter
    slowapi_util_module.get_remote_address = lambda request: "test-client"
    sys.modules["slowapi"] = slowapi_module
    sys.modules["slowapi.util"] = slowapi_util_module

if "slowapi" in sys.modules and "slowapi.errors" not in sys.modules:
    slowapi_errors_module = types.ModuleType("slowapi.errors")
    slowapi_middleware_module = types.ModuleType("slowapi.middleware")

    class _RateLimitExceeded(Exception):
        pass

    class _SlowAPIMiddleware:
        def __init__(self, app, *args, **kwargs):
            self.app = app

        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)

    slowapi_errors_module.RateLimitExceeded = _RateLimitExceeded
    slowapi_middleware_module.SlowAPIMiddleware = _SlowAPIMiddleware
    sys.modules["slowapi.errors"] = slowapi_errors_module
    sys.modules["slowapi.middleware"] = slowapi_middleware_module

from api import r2_telemetry_routes
from src.aurora.relays import api_routes as relay_api_routes
from src.middleware.fastapi_security import generate_csrf_token
from src.monitoring import dashboard_api


def _auth_header() -> dict[str, str]:
    token = generate_csrf_token("test-session")
    return {"Authorization": f"Bearer {token}"}


class SensitiveRouterAuthTests(unittest.TestCase):
    """Sensitive telemetry, monitoring, and relay routes require CSRF bearer auth."""

    def test_r2_telemetry_routes_reject_missing_token(self) -> None:
        app = FastAPI()
        app.include_router(r2_telemetry_routes.router)
        client = TestClient(app)

        response = client.get("/r2-telemetry/metrics")

        self.assertIn(response.status_code, (401, 403))

    def test_r2_telemetry_routes_accept_valid_token(self) -> None:
        class _Telemetry:
            enabled = True
            service_name = "test-r2"

            def export_prometheus_metrics(self) -> str:
                return "aurora_r2_test 1\n"

        app = FastAPI()
        app.include_router(r2_telemetry_routes.router)
        client = TestClient(app)

        with patch.object(
            r2_telemetry_routes,
            "get_r2_telemetry",
            return_value=_Telemetry(),
        ):
            response = client.get(
                "/r2-telemetry/metrics",
                headers=_auth_header(),
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("aurora_r2_test 1", response.text)

    def test_monitoring_routes_reject_missing_token(self) -> None:
        monitoring = SimpleNamespace(
            audit_logger=SimpleNamespace(verify_chain=lambda: True),
        )

        with patch.object(
            dashboard_api,
            "get_monitoring_system",
            return_value=monitoring,
        ):
            router = dashboard_api.create_monitoring_router()

        app = FastAPI()
        self.assertIsNotNone(router)
        app.include_router(router)
        client = TestClient(app)

        response = client.get("/monitoring/audit")

        self.assertIn(response.status_code, (401, 403))

    def test_monitoring_routes_accept_valid_token(self) -> None:
        monitoring = SimpleNamespace(
            audit_logger=SimpleNamespace(verify_chain=lambda: True),
        )

        with patch.object(
            dashboard_api,
            "get_monitoring_system",
            return_value=monitoring,
        ):
            router = dashboard_api.create_monitoring_router()

        app = FastAPI()
        self.assertIsNotNone(router)
        app.include_router(router)
        client = TestClient(app)

        response = client.get(
            "/monitoring/health",
            headers=_auth_header(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["audit_chain_valid"])

    def test_relay_routes_reject_missing_token(self) -> None:
        app = FastAPI()
        app.include_router(relay_api_routes.router)
        client = TestClient(app)

        response = client.post(
            "/relay/send",
            json={
                "source_layer": "L1",
                "target_layer": "L2",
                "payload": {"message": "blocked"},
            },
        )

        self.assertIn(response.status_code, (401, 403))

    def test_relay_routes_accept_valid_token(self) -> None:
        relay = SimpleNamespace(
            messages_processed=2,
            messages_blocked=0,
            ethics_gate=object(),
        )

        app = FastAPI()
        app.include_router(relay_api_routes.router)
        client = TestClient(app)

        with patch.object(
            relay_api_routes,
            "get_relay_manager",
            return_value=relay,
        ):
            response = client.get(
                "/relay/status",
                headers=_auth_header(),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["messages_processed"], 2)


if __name__ == "__main__":
    unittest.main()
