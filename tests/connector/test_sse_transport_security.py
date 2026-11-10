"""Host/Origin (DNS-rebinding) protection at the real SSE transport boundary.

Every case sends real HTTP to a uvicorn-served ``build_sse_app`` and checks both
endpoints, ``GET /sse`` and ``POST /messages/``. Nothing here calls a standalone
validator or reaches Aurora.
"""
import asyncio
from contextlib import asynccontextmanager
import json
import socket
import subprocess
import sys
from pathlib import Path

import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client
import pytest
import uvicorn

from connector.server import build_server, build_sse_app, build_transport_security

ROOT = Path(__file__).resolve().parents[2]
UNSPECIFIED_V4 = '.'.join(['0'] * 4)  # wildcard bind address, built so no test binds all interfaces
INITIALIZE = {
    'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
    'params': {'protocolVersion': '2025-03-26', 'capabilities': {},
               'clientInfo': {'name': 'sse-guard-test', 'version': '0'}},
}


def _ipv6_loopback_available() -> bool:
    try:
        with socket.socket(socket.AF_INET6) as probe:
            probe.bind(('::1', 0))
        return True
    except OSError:
        return False


@asynccontextmanager
async def serving(bind='127.0.0.1', allowed_hosts=(), allowed_origins=(), exact_port=True, profile_host=None):
    family = socket.AF_INET6 if ':' in bind else socket.AF_INET
    listener = socket.socket(family)
    listener.bind((bind, 0))
    port = listener.getsockname()[1]
    settings = build_transport_security(profile_host or bind, port if exact_port else None, allowed_hosts, allowed_origins)
    config = uvicorn.Config(build_sse_app(build_server(), settings), host=bind, log_level='warning', lifespan='off')
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve(sockets=[listener]))
    try:
        async with asyncio.timeout(10):
            while not server.started:
                if task.done():
                    await task
                    pytest.fail('SSE server exited before startup')
                await asyncio.sleep(0.01)
        yield port
    finally:
        server.should_exit = True
        try:
            await asyncio.wait_for(task, timeout=10)
        finally:
            listener.close()


@asynccontextmanager
async def sse_session(port, headers=None, base=None):
    """Yield (status, message_path_or_None) and keep the SSE stream open for the block's duration."""
    url = f'{base or f"http://127.0.0.1:{port}"}/sse'
    async with httpx.AsyncClient(timeout=10) as client:
        async with client.stream('GET', url, headers=headers or {}) as response:
            if response.status_code != 200:
                yield response.status_code, None
                return
            lines = response.aiter_lines()  # keep a reference: dropping it would close the stream
            try:
                async with asyncio.timeout(10):
                    async for line in lines:
                        if line.startswith('data: '):
                            break
                yield 200, line[6:]
            finally:
                await lines.aclose()


async def open_sse(port, headers=None, base=None):
    """Status and endpoint of a one-shot connection (the session ends when this returns)."""
    async with sse_session(port, headers, base) as result:
        return result


async def post_message(port, path, headers):
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(f'http://127.0.0.1:{port}{path}', headers={'content-type': 'application/json', **headers},
                                     content=json.dumps(INITIALIZE))
        return response.status_code


# ------------------------------------------------------------------ accepted
@pytest.mark.asyncio
@pytest.mark.parametrize('host_header', ['127.0.0.1:{p}', 'localhost:{p}', '[::1]:{p}'])
async def test_loopback_host_forms_without_origin_open_sse_and_accept_posts(host_header):
    async with serving() as port:
        headers = {'Host': host_header.format(p=port)}  # no Origin header: a non-browser client
        async with sse_session(port, headers) as (status, endpoint):
            assert status == 200
            assert endpoint.startswith('/messages/?session_id=')
            assert await post_message(port, endpoint, headers) == 202


@pytest.mark.asyncio
@pytest.mark.skipif(not _ipv6_loopback_available(), reason='IPv6 loopback unavailable')
async def test_real_ipv6_loopback_listener_serves_a_legitimate_client():
    async with serving('::1') as port:
        status, endpoint = await open_sse(port, base=f'http://[::1]:{port}')
        assert status == 200
        assert endpoint.startswith('/messages/?session_id=')


@pytest.mark.asyncio
@pytest.mark.parametrize('origin', ['http://localhost:3000', 'http://127.0.0.1:5173', 'http://[::1]:8080'])
async def test_loopback_web_origins_are_accepted_on_both_endpoints(origin):
    async with serving() as port:
        headers = {'Origin': origin}
        async with sse_session(port, headers) as (status, endpoint):
            assert status == 200
            assert await post_message(port, endpoint, headers) == 202


@pytest.mark.asyncio
async def test_sdk_client_still_completes_a_session_through_exact_port_settings():
    async with serving() as port:
        async with sse_client(f'http://127.0.0.1:{port}/sse', sse_read_timeout=10) as streams:
            async with ClientSession(*streams) as client:
                await client.initialize()
                assert len((await client.list_tools()).tools) == 5


# ------------------------------------------------------------------ rejected
HOSTILE_HOSTS = [
    'evil.example.com', 'evil.example.com:{p}', '127.0.0.1.evil.example.com:{p}', 'localhost.evil.example.com:{p}',
    '127.0.0.1:1', 'localhost:1', '0.0.0.0:{p}', '192.0.2.10:{p}',
]
HOSTILE_ORIGINS = [
    'http://evil.example.com', 'https://evil.example.com:443', 'null', 'http://localhost.evil.example.com:3000',
    'http://127.0.0.1.evil.example.com', 'https://localhost:3000', 'file://',
]


@pytest.mark.asyncio
@pytest.mark.parametrize('host_header', HOSTILE_HOSTS)
async def test_hostile_host_is_refused_on_sse_and_on_message_post(host_header):
    async with serving() as port:
        hostile = {'Host': host_header.format(p=port)}
        assert (await open_sse(port, hostile))[0] == 421
        # A real, open session, then a rebinding-style POST naming that session.
        async with sse_session(port, {}) as (_, endpoint):
            assert await post_message(port, endpoint, hostile) == 421
            assert await post_message(port, '/messages/', hostile) == 421  # refused before session lookup


@pytest.mark.asyncio
@pytest.mark.parametrize('origin', HOSTILE_ORIGINS)
async def test_hostile_origin_is_refused_even_with_a_loopback_host(origin):
    async with serving() as port:
        hostile = {'Origin': origin}
        assert (await open_sse(port, hostile))[0] == 403
        async with sse_session(port, {}) as (_, endpoint):
            assert await post_message(port, endpoint, hostile) == 403


@pytest.mark.asyncio
async def test_missing_host_header_is_refused_at_the_socket():
    async with serving() as port:
        reader, writer = await asyncio.open_connection('127.0.0.1', port)
        try:
            writer.write(b'GET /sse HTTP/1.0\r\n\r\n')  # HTTP/1.0 may legitimately omit Host
            await writer.drain()
            status_line = (await asyncio.wait_for(reader.readline(), timeout=5)).decode()
        finally:
            writer.close()
        assert ' 421 ' in status_line


@pytest.mark.asyncio
async def test_refused_post_does_not_deliver_the_message():
    """A refused POST must not reach the session: the later good POST is the first accepted one."""
    async with serving() as port:
        async with sse_session(port, {}) as (_, endpoint):
            assert await post_message(port, endpoint, {'Host': 'evil.example.com'}) == 421
            assert await post_message(port, endpoint, {}) == 202


# ------------------------------------------------------------ explicit remote
@pytest.mark.asyncio
async def test_wildcard_bind_trusts_only_loopback_until_hosts_are_explicit():
    # The listener stays on loopback; the guard profile is the one a wildcard bind would get.
    async with serving(profile_host=UNSPECIFIED_V4) as port:
        assert (await open_sse(port, {'Host': f'mcp.example.com:{port}'}))[0] == 421
        assert (await open_sse(port, {}))[0] == 200
    async with serving(profile_host=UNSPECIFIED_V4, allowed_hosts=['mcp.example.com:*'], allowed_origins=['https://app.example.com']) as port:
        assert (await open_sse(port, {'Host': f'mcp.example.com:{port}'}))[0] == 200
        assert (await open_sse(port, {'Host': f'mcp.example.com:{port}', 'Origin': 'https://app.example.com'}))[0] == 200
        assert (await open_sse(port, {'Host': f'mcp.example.com:{port}', 'Origin': 'https://other.example.com'}))[0] == 403
        assert (await open_sse(port, {'Host': f'attacker.example.com:{port}'}))[0] == 421


@pytest.mark.parametrize('value', ['*', '*.example.com', 'a*b', 'host:*:*', '', ' ', 'bad host', 'http://x', 'x/y'])
def test_unsafe_allowed_host_entries_are_rejected(value):
    with pytest.raises(ValueError):
        build_transport_security('127.0.0.1', 8765, allowed_hosts=[value])


@pytest.mark.parametrize('value', ['*', 'null', 'example.com', 'https://*.example.com', 'https://a.example.com/path', ''])
def test_unsafe_allowed_origin_entries_are_rejected(value):
    with pytest.raises(ValueError):
        build_transport_security('127.0.0.1', 8765, allowed_origins=[value])


def test_default_http_port_accepts_portless_host_and_origin_spellings():
    settings = build_transport_security('127.0.0.1', 80)
    assert {'127.0.0.1', 'localhost', '[::1]', '127.0.0.1:80', 'localhost:80'} <= set(settings.allowed_hosts)
    assert 'localhost' not in build_transport_security('127.0.0.1', 8765).allowed_hosts
    assert {'http://localhost', 'http://127.0.0.1', 'http://[::1]'} <= set(settings.allowed_origins)


def test_settings_profile_for_default_concrete_and_wildcard_binds():
    default = build_transport_security()
    assert default.enable_dns_rebinding_protection
    assert default.allowed_hosts == ['127.0.0.1:*', 'localhost:*', '[::1]:*']
    assert 'http://localhost' in default.allowed_origins
    assert build_transport_security('127.0.0.1', 8765).allowed_hosts == ['127.0.0.1:8765', 'localhost:8765', '[::1]:8765']
    assert '192.0.2.10:9000' in build_transport_security('192.0.2.10', 9000).allowed_hosts
    assert '[2001:db8::1]:9000' in build_transport_security('2001:db8::1', 9000).allowed_hosts
    for unspecified in (UNSPECIFIED_V4, '::', '[::]', '', '0:0:0:0:0:0:0:0'):
        wildcard = build_transport_security(unspecified, 9000)
        assert wildcard.allowed_hosts == ['127.0.0.1:9000', 'localhost:9000', '[::1]:9000'], unspecified


# ------------------------------------------------------------------------ CLI
def _cli(*args):
    return subprocess.run([sys.executable, '-m', 'connector.server', *args], cwd=ROOT, capture_output=True, text=True,
                          timeout=15, check=False, env={'AURORA_CONNECTOR_TOKEN': 't', 'AURORA_API_BASE_URL': 'http://127.0.0.1:9',
                                                         'PATH': ''})


def test_cli_rejects_allowlists_on_stdio_and_wildcards_before_startup():
    stdio = _cli('--allowed-host', 'mcp.example.com')
    assert stdio.returncode == 2
    assert 'only to --transport sse' in stdio.stderr
    wildcard = _cli('--transport', 'sse', '--allowed-host', '*')
    assert wildcard.returncode == 2
    assert 'wildcards are not accepted' in wildcard.stderr
    assert not wildcard.stdout


def test_cli_passes_explicit_allowlists_to_run_sse(monkeypatch):
    from unittest.mock import AsyncMock
    from connector import server as module
    serve = AsyncMock()
    monkeypatch.setattr(module, 'validate_environment', lambda: None)
    monkeypatch.setattr(module, 'build_server', lambda: object())
    monkeypatch.setattr(module, 'run_sse', serve)
    monkeypatch.setattr(sys, 'argv', ['aurora-mcp', '--transport', 'sse', '--host', UNSPECIFIED_V4, '--allowed-host',
                                      'mcp.example.com:443', '--allowed-origin', 'https://app.example.com'])
    module.main()
    serve.assert_awaited_once()
    assert serve.await_args.args[2:] == (UNSPECIFIED_V4, ('mcp.example.com:443',), ('https://app.example.com',))
