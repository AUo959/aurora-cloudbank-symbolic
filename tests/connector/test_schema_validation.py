"""Validate through the actual dispatcher; invalid arguments never reach tools."""
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import AsyncMock, patch

import pytest

from connector.tools import TOOL_REGISTRY


@pytest.mark.unit
async def test_valid_args_pass_validation(mcp_client):
    async with mcp_client as client:
        arguments = {'limit': 5, 'severity_filter': 'info'}
        with patch.object(
            TOOL_REGISTRY['aurora_get_ethics_log'], 'run', new=AsyncMock(return_value='{"ok":true}')) as run:
            result = await client.call_tool('aurora_get_ethics_log', arguments)
        assert not result.is_error
        run.assert_awaited_once_with(arguments)


@pytest.mark.unit
@pytest.mark.parametrize('arguments', [{'limit': -1}, {'limit': 200}, {'limit': 'five'}, {'limit': False}])
async def test_invalid_args_return_validation_error(mcp_client, arguments):
    async with mcp_client as client:
        with patch.object(TOOL_REGISTRY['aurora_get_ethics_log'], 'run', new=AsyncMock()) as run:
            result = await client.call_tool('aurora_get_ethics_log', arguments)
        assert result.is_error
        assert 'TOOL_VALIDATION_ERROR:' in result.content[0].text
        assert '(path: limit)' in result.content[0].text
        run.assert_not_called()


@pytest.mark.unit
def test_missing_required_validator_fails_before_startup():
    # Simulate an incomplete install in a separate process, never in the
    # already-imported SDK used by the rest of the suite.
    result = subprocess.run(
        [sys.executable, '-c', "import sys; sys.modules['jsonschema'] = None; import connector.server"],
        cwd=Path(__file__).resolve().parents[2], env=dict(os.environ),
        capture_output=True, text=True, timeout=10, check=False,
    )
    assert result.returncode != 0
    assert not result.stdout
    assert 'MCP SDK dependencies not installed' in result.stderr
