"""Tests for the instance_bridge module (issue #1024).

Runtime role confirmed: instance_bridge is a standalone WebSocket relay
server (port 8090, localhost only).  It is NOT integrated into aurora_api.py
and has NO importers in the main Python codebase.  It serves cross-instance
messaging as an external tool.

These tests cover:
- ConnectionManager unit behaviour (connect, disconnect, broadcast, isolation)
- FastAPI app structure (route registration)
- bridge_client importability
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest


# ---------------------------------------------------------------------------
# ConnectionManager unit tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_connect_accepts_websocket_and_tracks_channel() -> None:
    """connect() must call accept() and register the socket in the channel."""
    from modules.instance_bridge.bridge_server import ConnectionManager

    manager = ConnectionManager()
    ws = AsyncMock()

    asyncio.run(manager.connect(ws, "alpha"))

    ws.accept.assert_awaited_once()
    assert "alpha" in manager.active_channels
    assert ws in manager.active_channels["alpha"]


@pytest.mark.unit
def test_connect_multiple_clients_same_channel() -> None:
    """Multiple clients in the same channel are all tracked."""
    from modules.instance_bridge.bridge_server import ConnectionManager

    manager = ConnectionManager()
    ws1, ws2, ws3 = AsyncMock(), AsyncMock(), AsyncMock()

    async def _setup() -> None:
        await manager.connect(ws1, "shared")
        await manager.connect(ws2, "shared")
        await manager.connect(ws3, "shared")

    asyncio.run(_setup())
    assert len(manager.active_channels["shared"]) == 3


@pytest.mark.unit
def test_disconnect_removes_websocket_from_channel() -> None:
    """disconnect() must remove the socket; channel key stays if others remain."""
    from modules.instance_bridge.bridge_server import ConnectionManager

    manager = ConnectionManager()
    ws1, ws2 = AsyncMock(), AsyncMock()

    async def _setup() -> None:
        await manager.connect(ws1, "beta")
        await manager.connect(ws2, "beta")

    asyncio.run(_setup())
    manager.disconnect(ws1, "beta")

    assert ws1 not in manager.active_channels["beta"]
    assert ws2 in manager.active_channels["beta"]


@pytest.mark.unit
def test_disconnect_cleans_up_empty_channel() -> None:
    """disconnect() removes the channel key when the last socket leaves."""
    from modules.instance_bridge.bridge_server import ConnectionManager

    manager = ConnectionManager()
    ws = AsyncMock()

    asyncio.run(manager.connect(ws, "gamma"))
    manager.disconnect(ws, "gamma")

    assert "gamma" not in manager.active_channels


@pytest.mark.unit
def test_disconnect_nonexistent_channel_is_safe() -> None:
    """disconnect() on an unknown channel must not raise."""
    from modules.instance_bridge.bridge_server import ConnectionManager

    manager = ConnectionManager()
    ws = AsyncMock()
    manager.disconnect(ws, "does_not_exist")  # must not raise


@pytest.mark.unit
def test_broadcast_sends_to_all_except_sender() -> None:
    """broadcast() must deliver the message to all non-sender sockets."""
    from modules.instance_bridge.bridge_server import ConnectionManager

    manager = ConnectionManager()
    sender = AsyncMock()
    receiver1, receiver2 = AsyncMock(), AsyncMock()

    async def _run() -> None:
        await manager.connect(sender, "ch")
        await manager.connect(receiver1, "ch")
        await manager.connect(receiver2, "ch")
        await manager.broadcast("ch", "hello", sender)

    asyncio.run(_run())

    receiver1.send_text.assert_awaited_once_with("hello")
    receiver2.send_text.assert_awaited_once_with("hello")
    sender.send_text.assert_not_awaited()


@pytest.mark.unit
def test_broadcast_empty_channel_does_not_raise() -> None:
    """broadcast() on an empty/missing channel must be a no-op."""
    from modules.instance_bridge.bridge_server import ConnectionManager

    manager = ConnectionManager()
    sender = AsyncMock()
    asyncio.run(manager.broadcast("empty", "msg", sender))
    sender.send_text.assert_not_awaited()


@pytest.mark.unit
def test_channels_are_isolated() -> None:
    """Messages in one channel must not reach sockets on other channels."""
    from modules.instance_bridge.bridge_server import ConnectionManager

    manager = ConnectionManager()
    ws_a, ws_b = AsyncMock(), AsyncMock()
    noise_sender = AsyncMock()

    async def _run() -> None:
        await manager.connect(ws_a, "channel_a")
        await manager.connect(ws_b, "channel_b")
        await manager.broadcast("channel_a", "only for A", noise_sender)

    asyncio.run(_run())

    ws_a.send_text.assert_awaited_once_with("only for A")
    ws_b.send_text.assert_not_awaited()


# ---------------------------------------------------------------------------
# App structure tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_bridge_server_importable() -> None:
    """bridge_server must be importable and expose the expected public names."""
    from modules.instance_bridge.bridge_server import app, ConnectionManager, manager

    assert app is not None
    assert ConnectionManager is not None
    assert manager is not None


@pytest.mark.unit
def test_bridge_app_registers_websocket_route() -> None:
    """The FastAPI app must register exactly one route at /ws/{channel}/{client_id}."""
    from modules.instance_bridge.bridge_server import app

    ws_paths = [
        getattr(r, "path", "") for r in app.routes
        if getattr(r, "path", "") == "/ws/{channel}/{client_id}"
    ]
    assert len(ws_paths) == 1, (
        f"Expected /ws/{{channel}}/{{client_id}} route, found: {[getattr(r,'path','') for r in app.routes]}"
    )


# ---------------------------------------------------------------------------
# bridge_client importability
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_bridge_client_importable() -> None:
    """bridge_client must be importable and expose relay() and main()."""
    try:
        from modules.instance_bridge.bridge_client import relay, main
    except ImportError as exc:
        pytest.skip(f"bridge_client optional dep missing: {exc}")

    assert callable(relay)
    assert callable(main)
