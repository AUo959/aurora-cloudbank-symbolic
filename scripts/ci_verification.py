#!/usr/bin/env python3
"""Reuse canonical CI only with a successful receipt for the exact checkout.

Uses the runner's gh CLI and read-only Actions token; never dispatches workflows.
PR run head_sha identifies the branch, whereas GITHUB_SHA identifies the tested
merge commit. Both must match. Receipts are data, never extracted or executed.
"""
import argparse
import io
import json
import os
from pathlib import Path
import re
import subprocess  # nosec B404 — fixed runner CLIs; no shell or eval.
import time
import zipfile

WORKFLOW = 'aurora-ci-minimal.yml'
RECEIPT = 'ci-verification.json'
MAX_BYTES = 16384


def gh_api(endpoint, binary=False):
    """Only fixed gh argv is executed; endpoints are constructed from validated IDs."""
    result = subprocess.run(  # nosec B603 B607
        ['gh', 'api', endpoint], check=True, capture_output=True, timeout=45,
    )
    return result.stdout if binary else json.loads(result.stdout)


def context(environ):
    """Validate runner context before constructing any API endpoint."""
    repo = environ['GITHUB_REPOSITORY']
    event = environ['GITHUB_EVENT_NAME']
    sha = environ['GITHUB_SHA']
    head = environ.get('CI_HEAD_SHA') or sha
    ref = environ['GITHUB_REF']
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*', repo):
        raise ValueError('Invalid repository')
    if event not in ('push', 'pull_request', 'workflow_dispatch'):
        raise ValueError('Unsupported CI event')
    if not all(re.fullmatch(r'[0-9a-f]{40}', value) for value in (sha, head)):
        raise ValueError('Invalid checkout/head SHA')
    if event == 'pull_request' and not re.fullmatch(r'refs/pull/[1-9][0-9]*/merge', ref):
        raise ValueError('Invalid PR ref')
    return {'repository': repo, 'event': event, 'ref': ref, 'checkout_sha': sha, 'head_sha': head}


def record(environ):
    proof = context(environ)
    checkout = subprocess.run(  # nosec B603 B607
        ['git', 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True,
    ).stdout.strip()
    if checkout != proof['checkout_sha']:
        raise ValueError('Checkout does not match GITHUB_SHA')
    proof.update(run_id=int(environ['GITHUB_RUN_ID']), run_attempt=int(environ['GITHUB_RUN_ATTEMPT']),
                 result=environ['CI_RESULT'])
    Path(RECEIPT).write_text(json.dumps(proof, sort_keys=True) + '\n')


def same_ref(run, expected):
    if expected['event'] == 'pull_request':
        number = int(expected['ref'].split('/')[2])
        return any(pr['number'] == number for pr in run.get('pull_requests', []))
    return run.get('head_branch') == expected['ref'].removeprefix('refs/heads/').removeprefix('refs/tags/')


def latest_run(runs, expected):
    candidates = [run for run in runs if run['head_sha'] == expected['head_sha']
                  and run['event'] == expected['event'] and same_ref(run, expected)]
    return max(candidates, key=lambda run: run['id'], default=None)


def read_receipt(payload):
    if len(payload) > MAX_BYTES:
        raise ValueError('Oversized CI receipt archive')
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if archive.namelist() != [RECEIPT]:
            raise ValueError('Unexpected CI receipt archive members')
        if archive.getinfo(RECEIPT).file_size > MAX_BYTES:
            raise ValueError('Oversized CI receipt')
        return json.loads(archive.read(RECEIPT))


def matching_receipt(proof, expected, run):
    fields = dict(expected, run_id=run['id'], run_attempt=run['run_attempt'], result='success')
    return all(proof.get(key) == value for key, value in fields.items())


def valid_artifact(matches):
    if len(matches) != 1 or matches[0]['expired'] or matches[0]['size_in_bytes'] > MAX_BYTES:
        raise ValueError('Invalid CI receipt artifact')
    return matches[0]


def verify_run(run, expected, api):
    """Return false while pending; failures and invalid artifacts fail closed."""
    if run['status'] != 'completed':
        return False
    if run['conclusion'] != 'success':
        raise ValueError('Canonical CI did not succeed')
    base = f"repos/{expected['repository']}/actions"
    artifacts = api(f"{base}/runs/{run['id']}/artifacts?per_page=100")['artifacts']
    name = f"ci-verification-{run['run_attempt']}"
    matches = [artifact for artifact in artifacts if artifact['name'] == name]
    if not matches:
        return False  # Old runs cannot prove the current checkout; wait for a fresh run.
    artifact = valid_artifact(matches)
    payload = api(f"{base}/artifacts/{int(artifact['id'])}/zip", binary=True)
    return matching_receipt(read_receipt(payload), expected, run)


def wait(environ, timeout=900, interval=15, api=gh_api, clock=time.monotonic, sleep=time.sleep):
    expected = context(environ)
    base = f"repos/{expected['repository']}/actions/workflows/{WORKFLOW}/runs"
    endpoint = f"{base}?head_sha={expected['head_sha']}&event={expected['event']}&per_page=100"
    deadline = clock() + timeout
    while clock() < deadline:
        run = latest_run(api(endpoint)['workflow_runs'], expected)
        if run and verify_run(run, expected, api):
            # Reruns/new runs must not be masked by a previously successful attempt.
            current = latest_run(api(endpoint)['workflow_runs'], expected)
            if current and (current['id'], current['run_attempt'], current['status']) == (
                    run['id'], run['run_attempt'], 'completed') and current['conclusion'] == 'success':
                print(f"Canonical CI verified checkout {expected['checkout_sha']} (run {run['id']}).")
                return
        sleep(interval)
    raise TimeoutError('No successful canonical CI receipt for this exact checkout before timeout')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('record', 'wait'))
    args = parser.parse_args()
    if args.command == 'record':
        record(os.environ)
    else:
        wait(os.environ)


if __name__ == '__main__':
    main()
