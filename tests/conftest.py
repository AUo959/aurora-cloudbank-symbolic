"""Shared pytest configuration for deterministic repository fixtures."""

from collections.abc import Iterator
import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def deterministic_git_default_branch() -> Iterator[None]:
    """Make temporary ``git init`` repositories use Aurora's ``main`` branch.

    Git's platform/user default can be either ``master`` or ``main``. Tests that
    exercise repository synchronization explicitly target ``main``, so append a
    process-local Git configuration entry for child processes launched during
    pytest. The caller's environment is restored when the session completes.
    """
    count_key = "GIT_CONFIG_COUNT"
    previous_count = os.environ.get(count_key)

    try:
        config_index = int(previous_count or "0")
    except ValueError:
        config_index = 0

    key_name = f"GIT_CONFIG_KEY_{config_index}"
    value_name = f"GIT_CONFIG_VALUE_{config_index}"
    previous_key = os.environ.get(key_name)
    previous_value = os.environ.get(value_name)

    os.environ[count_key] = str(config_index + 1)
    os.environ[key_name] = "init.defaultBranch"
    os.environ[value_name] = "main"

    try:
        yield
    finally:
        for name, previous in (
            (count_key, previous_count),
            (key_name, previous_key),
            (value_name, previous_value),
        ):
            if previous is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = previous
