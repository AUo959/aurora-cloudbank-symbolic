"""Real stdio/SSE sessions against a controlled loopback API, never live Aurora."""
import asyncio
from contextlib import asynccontextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from threading import Thread

from mcp import Client, ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
import pytest
import uvicorn

from connector.server import build_server, build_sse_app

ROOT = Path(__file__).resolve().parents[2]
TOKEN = 'mcp-loopback-fixture-token'


@pytest.fixture
def api_stub():
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append((self.path, self.headers.get('Authorization'), self.headers.get('X-Source-Client')))
            if self.path != '/health' or self.headers.get('Authorization') != f'Bearer {TOKEN}':
                self.send_error(403)
                return
            body = json.dumps({'status': 'healthy', 'components': {'insight_ledger': True}}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


async def exercise_protocol(client, requests):
    tools = await client.list_tools()
    assert len(tools.tools) == 5
    result = await client.call_tool('aurora_get_state', {'include_echochain': False})
    assert not result.is_error
    data = json.loads(result.content[0].text)
    assert data['active_modules'] == ['INSIGHT_LEDGER']
    assert data['layer_state']['recovery_threaded'] is True
    assert requests == [('/health', f'Bearer {TOKEN}', 'aurora-mcp-connector')]
    invalid = await client.call_tool('aurora_get_ethics_log', {'limit': -1})
    assert invalid.is_error
    assert 'TOOL_VALIDATION_ERROR:' in invalid.content[0].text
    unknown = await client.call_tool('__missing__', {})
    assert unknown.is_error
    assert 'Unknown tool' in unknown.content[0].text
    assert len(requests) == 1  # Rejected calls never reach the backend.


@pytest.mark.asyncio
@pytest.mark.parametrize('mode', ['auto', 'legacy'])
async def test_stdio_handshake_discovery_call_and_validation(api_stub, mode):
    url, requests = api_stub
    parameters = StdioServerParameters(command=sys.executable, args=['-m', 'connector.server'], cwd=str(ROOT),
                                       env={'AURORA_CONNECTOR_TOKEN': TOKEN, 'AURORA_API_BASE_URL': url})
    async with Client(parameters, mode=mode, read_timeout_seconds=10) as client:
        await exercise_protocol(client, requests)


@asynccontextmanager
async def running_sse_server():
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    port = listener.getsockname()[1]
    config = uvicorn.Config(build_sse_app(build_server()), host='127.0.0.1', log_level='warning', lifespan='off')
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve(sockets=[listener]))
    try:
        async with asyncio.timeout(10):
            while not server.started:
                if task.done():
                    await task
                    pytest.fail('SSE server exited before startup')
                await asyncio.sleep(0.01)
        yield f'http://127.0.0.1:{port}/sse'
    finally:
        server.should_exit = True
        try:
            await asyncio.wait_for(task, timeout=10)
        finally:
            listener.close()


@pytest.mark.asyncio
async def test_sse_handshake_discovery_call_and_validation(api_stub, monkeypatch):
    url, requests = api_stub
    monkeypatch.setenv('AURORA_CONNECTOR_TOKEN', TOKEN)
    monkeypatch.setenv('AURORA_API_BASE_URL', url)
    async with running_sse_server() as endpoint:
        async with sse_client(endpoint, sse_read_timeout=10) as streams:
            async with ClientSession(*streams) as client:
                await client.initialize()
                await exercise_protocol(client, requests)


def test_cli_without_credentials_fails_before_protocol_start():
    environ = dict(os.environ)
    environ.pop('AURORA_CONNECTOR_TOKEN', None)
    environ.pop('AURORA_API_BASE_URL', None)
    result = subprocess.run([sys.executable, '-m', 'connector.server'], cwd=ROOT, env=environ,
                            capture_output=True, text=True, timeout=10, check=False)
    assert result.returncode != 0
    assert not result.stdout
    assert 'AURORA_CONNECTOR_TOKEN' in result.stderr


@pytest.mark.parametrize('host', [None, '192.0.2.10'])
def test_sse_cli_defaults_to_loopback_and_allows_explicit_host(monkeypatch, host):
    from unittest.mock import AsyncMock
    from connector import server as module
    sentinel = object()
    serve = AsyncMock()
    monkeypatch.setattr(module, 'validate_environment', lambda: None)
    monkeypatch.setattr(module, 'build_server', lambda: sentinel)
    monkeypatch.setattr(module, 'run_sse', serve)
    args = ['aurora-mcp', '--transport', 'sse', '--port', '9000']
    if host is not None:
        args.extend(['--host', host])
    monkeypatch.setattr(sys, 'argv', args)
    module.main()
    serve.assert_awaited_once_with(sentinel, 9000, host or '127.0.0.1', (), ())
