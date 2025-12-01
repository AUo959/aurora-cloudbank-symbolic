"""Tests for AIF hub token bootstrap and broadcast logging."""

import importlib
import logging
import sys

import asyncio

import pytest
from fastapi import WebSocketDisconnect


class _FailureWebSocket:
    def __init__(self, name: str, exc: Exception):
        self.name = name
        self.exc = exc
        self.client = (name, 0)

    async def send_text(self, message: str):  # pragma: no cover - exercised via broadcast
        raise self.exc


def test_token_bootstrap_uses_logger(monkeypatch, caplog, capsys):
    monkeypatch.setenv("AIF_TOKEN", "change-me")
    sys.modules.pop("services.aif_hub", None)

    with caplog.at_level(logging.INFO):
        module = importlib.import_module("services.aif_hub")

    output = capsys.readouterr()
    assert output.out == ""
    assert any("AIF_TOKEN" in record.getMessage() for record in caplog.records)
    assert module.AIF_TOKEN


def test_broadcast_logs_and_disconnects_on_failure(caplog):
    sys.modules.pop("services.aif_hub", None)
    module = importlib.import_module("services.aif_hub")

    failure_connection = _FailureWebSocket("failure", RuntimeError("send-failed"))
    disconnect_connection = _FailureWebSocket("disconnect", WebSocketDisconnect())

    manager = module.ConnectionManager()
    manager.active_connections = [failure_connection, disconnect_connection]

    async def _run_broadcast():
        with caplog.at_level(logging.INFO):
            await manager.broadcast("payload")

    asyncio.run(_run_broadcast())

    assert failure_connection not in manager.active_connections
    assert disconnect_connection not in manager.active_connections

    warning_records = [record for record in caplog.records if record.levelno >= logging.WARNING]
    info_records = [record for record in caplog.records if record.levelno == logging.INFO]

    assert any(getattr(record, "event", "") == "broadcast_failure" for record in warning_records)
    assert any(getattr(record, "event", "") == "broadcast_disconnect" for record in info_records)
