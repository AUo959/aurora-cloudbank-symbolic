"""Dependency-light slowapi stubs for focused router tests."""

import importlib.util
import sys
import types
from typing import Any, Callable


def install_slowapi_stub() -> None:
    """Install minimal slowapi modules when the optional package is unavailable."""
    if "slowapi" not in sys.modules and importlib.util.find_spec("slowapi") is None:
        slowapi_module = types.ModuleType("slowapi")
        slowapi_util_module = types.ModuleType("slowapi.util")

        class _Limiter:
            def __init__(self, *args: Any, **kwargs: Any):
                self.key_func = kwargs.get("key_func")

            def limit(
                self,
                *args: Any,
                **kwargs: Any,
            ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
                def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                    return func

                return decorator

        def _get_remote_address(request: Any) -> str:
            return "test-client"

        slowapi_module.Limiter = _Limiter
        slowapi_util_module.get_remote_address = _get_remote_address
        sys.modules["slowapi"] = slowapi_module
        sys.modules["slowapi.util"] = slowapi_util_module

    if "slowapi" in sys.modules and "slowapi.errors" not in sys.modules:
        slowapi_errors_module = types.ModuleType("slowapi.errors")
        slowapi_middleware_module = types.ModuleType("slowapi.middleware")

        class _RateLimitExceeded(Exception):
            """Test stub for slowapi.errors.RateLimitExceeded."""

        class _SlowAPIMiddleware:
            def __init__(self, app: Callable[..., Any], *args: Any, **kwargs: Any):
                self.app = app

            async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
                await self.app(scope, receive, send)

        slowapi_errors_module.RateLimitExceeded = _RateLimitExceeded
        slowapi_middleware_module.SlowAPIMiddleware = _SlowAPIMiddleware
        sys.modules["slowapi.errors"] = slowapi_errors_module
        sys.modules["slowapi.middleware"] = slowapi_middleware_module
