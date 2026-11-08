"""Trust-boundary tests for canonical CI reuse (no network or runner required)."""
import io
import json
from pathlib import Path
from unittest.mock import patch
import zipfile

import pytest

from scripts import ci_verification as ci

SHA = 'a' * 40
HEAD = 'b' * 40
ENV = {'GITHUB_REPOSITORY': 'owner/repo', 'GITHUB_EVENT_NAME': 'pull_request',
       'GITHUB_SHA': SHA, 'CI_HEAD_SHA': HEAD, 'GITHUB_REF': 'refs/pull/9/merge'}
EXPECTED = ci.context(ENV)
RUN = {'id': 123, 'run_attempt': 2, 'status': 'completed', 'conclusion': 'success',
       'event': 'pull_request', 'head_sha': HEAD, 'pull_requests': [{'number': 9}]}
PROOF = dict(EXPECTED, run_id=123, run_attempt=2, result='success')
ARTIFACT = {'id': 456, 'name': 'ci-verification-2', 'expired': False, 'size_in_bytes': 500}


def archive(proof=PROOF, member=ci.RECEIPT):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as zipped:
        zipped.writestr(member, json.dumps(proof))
    return output.getvalue()


def api(endpoint, binary=False):
    if binary:
        assert endpoint == 'repos/owner/repo/actions/artifacts/456/zip'
        return archive()
    if '/artifacts?' in endpoint:
        return {'artifacts': [ARTIFACT]}
    assert 'actions/workflows/aurora-ci-minimal.yml/runs?' in endpoint
    assert f'head_sha={HEAD}&event=pull_request' in endpoint
    return {'workflow_runs': [RUN]}


def test_exact_success_can_be_reused():
    ci.wait(ENV, api=api)


@pytest.mark.parametrize('field,value', [
    ('repository', 'other/repo'), ('event', 'push'), ('ref', 'refs/pull/10/merge'), ('checkout_sha', HEAD),
    ('head_sha', SHA), ('run_id', 122), ('run_attempt', 1), ('result', 'failure'),
])
def test_unrelated_or_stale_receipts_cannot_satisfy_gate(field, value):
    assert not ci.matching_receipt(dict(PROOF, **{field: value}), EXPECTED, RUN)


@pytest.mark.parametrize('status', ['failure', 'cancelled', 'timed_out', 'skipped', 'neutral'])
def test_failed_run_is_never_reused(status):
    with pytest.raises(ValueError, match='did not succeed'):
        ci.verify_run(dict(RUN, conclusion=status), EXPECTED, api)


def test_latest_pending_attempt_is_not_hidden_by_old_success():
    pending = dict(RUN, id=124, status='in_progress', conclusion=None)
    assert ci.latest_run([RUN, pending], EXPECTED) == pending
    assert not ci.verify_run(pending, EXPECTED, api)


def test_other_event_or_head_is_ignored():
    assert ci.latest_run([dict(RUN, event='push'), dict(RUN, head_sha=SHA)], EXPECTED) is None


@pytest.mark.parametrize('change', [{'expired': True}, {'size_in_bytes': ci.MAX_BYTES + 1}])
def test_invalid_artifact_is_rejected_before_download(change):
    def invalid_api(endpoint, binary=False):
        assert not binary
        return {'artifacts': [dict(ARTIFACT, **change)]}
    with pytest.raises(ValueError, match='artifact'):
        ci.verify_run(RUN, EXPECTED, invalid_api)


def test_old_attempt_artifact_is_not_used():
    assert not ci.verify_run(RUN, EXPECTED, lambda _: {
        'artifacts': [dict(ARTIFACT, name='ci-verification-1')]})


@pytest.mark.parametrize('payload', [b'not a zip', archive(member='../ci-verification.json'),
                                    b'x' * (ci.MAX_BYTES + 1), archive({'x': 'y' * ci.MAX_BYTES})])
def test_invalid_archives_are_rejected(payload):
    with pytest.raises((ValueError, zipfile.BadZipFile)):
        ci.read_receipt(payload)


def test_missing_or_stale_proof_times_out_closed():
    for response in ({'workflow_runs': []}, {'workflow_runs': [dict(RUN, status='queued')]}):
        ticks = iter([0, 0, 2])
        with pytest.raises(TimeoutError):
            ci.wait(ENV, timeout=1, api=lambda _: response, clock=lambda: next(ticks), sleep=lambda _: None)


def test_rerun_started_during_download_is_not_accepted():
    calls = []
    def racing_api(endpoint, binary=False):
        if '/runs?' in endpoint:
            calls.append(endpoint)
            if len(calls) > 1:
                return {'workflow_runs': [dict(RUN, run_attempt=3, status='queued', conclusion=None)]}
        return api(endpoint, binary)
    ticks = iter([0, 0, 2])
    with pytest.raises(TimeoutError):
        ci.wait(ENV, timeout=1, api=racing_api, clock=lambda: next(ticks), sleep=lambda _: None)


def test_record_binds_actual_checkout(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    environ = dict(ENV, GITHUB_RUN_ID='123', GITHUB_RUN_ATTEMPT='2', CI_RESULT='success')
    with patch.object(ci.subprocess, 'run') as run:
        run.return_value.stdout = SHA + '\n'
        ci.record(environ)
        assert json.loads(Path(ci.RECEIPT).read_text()) == PROOF
        run.return_value.stdout = HEAD
        with pytest.raises(ValueError, match='Checkout'):
            ci.record(environ)


@pytest.mark.parametrize('field,value', [('GITHUB_REPOSITORY', '../repo'), ('GITHUB_SHA', 'main'),
                                       ('CI_HEAD_SHA', '--help'), ('GITHUB_EVENT_NAME', 'workflow_run')])
def test_invalid_context_never_reaches_api(field, value):
    with pytest.raises(ValueError):
        ci.context(dict(ENV, **{field: value}))


def workflows():
    import yaml
    # BaseLoader preserves GitHub's literal `on` key (YAML 1.1 treats it as True).
    root = Path(__file__).resolve().parents[1] / '.github/workflows'
    return {name: yaml.load((root / name).read_text(), Loader=yaml.BaseLoader) for name in (
        'aurora-ci-minimal.yml', 'code-quality.yml', 'k8s-deploy.yml')}


def test_check_names_and_build_dependency_are_preserved():
    files = workflows()
    assert files['aurora-ci-minimal.yml']['jobs']['ci']['name'] == 'CI Check'
    assert 'code_quality' in files['code-quality.yml']['jobs']
    k8s = files['k8s-deploy.yml']['jobs']
    assert k8s['test']['name'] == 'Run Tests'
    assert k8s['build']['needs'] == ['test']
    assert k8s['test']['permissions'] == {'contents': 'read', 'actions': 'read'}


def test_manual_tests_and_automatic_verification_are_separate():
    steps = workflows()['k8s-deploy.yml']['jobs']['test']['steps']
    tests = next(step for step in steps if step['name'] == 'Run unit tests (blocking)')
    gate = next(step for step in steps if ' wait' in step.get('run', ''))
    assert tests['if'] == "github.event_name == 'workflow_dispatch'"
    assert gate['if'] == "github.event_name != 'workflow_dispatch'"
    assert 'GH_TOKEN' in gate['env']


def test_docs_only_push_cannot_leave_quality_waiting_for_absent_ci():
    files = workflows()
    assert files['code-quality.yml']['on']['push']['paths-ignore'] == (
        files['aurora-ci-minimal.yml']['on']['push']['paths-ignore'])
    assert 'paths-ignore' not in files['code-quality.yml']['on']['pull_request']


def test_canonical_receipt_is_attempt_specific_and_always_recorded():
    steps = workflows()['aurora-ci-minimal.yml']['jobs']['ci']['steps']
    record = next(step for step in steps if step.get('run') == 'python scripts/ci_verification.py record')
    upload = next(step for step in steps if step.get('with', {}).get('path') == ci.RECEIPT)
    assert record['if'] == upload['if'] == 'always()'
    assert record['env']['CI_RESULT'] == '${{ job.status }}'
    assert upload['with']['name'] == 'ci-verification-${{ github.run_attempt }}'
    assert upload['with']['if-no-files-found'] == 'error'


def test_other_pr_cannot_mask_the_correct_run_even_with_the_same_head():
    unrelated = dict(RUN, id=124, pull_requests=[{'number': 10}], conclusion='failure')
    assert ci.latest_run([RUN, unrelated], EXPECTED) == RUN
    assert ci.latest_run([dict(RUN, pull_requests=[])], EXPECTED) is None


def test_push_runs_are_scoped_to_the_branch():
    expected = ci.context(dict(ENV, GITHUB_EVENT_NAME='push', GITHUB_REF='refs/heads/main'))
    main = dict(RUN, event='push', head_branch='main')
    develop = dict(main, id=124, head_branch='develop')
    assert ci.latest_run([main, develop], expected) == main


def test_kubernetes_markdown_push_cannot_wait_for_absent_canonical_run():
    triggers = workflows()['k8s-deploy.yml']['on']
    assert triggers['push']['paths'][-1] == '!**.md'
    assert 'k8s/**' in triggers['push']['paths'][:-1]
    assert '!**.md' not in triggers['pull_request']['paths']


def test_fork_run_without_api_pr_association_uses_bound_receipt():
    fork = dict(RUN, pull_requests=[])
    def fork_api(endpoint, binary=False):
        if '/runs?' in endpoint:
            return {'workflow_runs': [fork]}
        return api(endpoint, binary)
    ci.wait(ENV, api=fork_api)


def test_unrelated_fork_receipt_cannot_mask_this_pr():
    unrelated = dict(RUN, id=124, pull_requests=[])
    def fork_api(endpoint, binary=False):
        if binary:
            return archive(dict(PROOF, run_id=124, ref='refs/pull/10/merge'))
        return api(endpoint, binary)
    assert ci.latest_run([RUN, unrelated], EXPECTED, fork_api) == RUN


def test_unresolved_newer_fork_run_blocks_old_success():
    for changes in ({'status': 'in_progress'}, {}):
        unknown = dict(RUN, id=124, pull_requests=[], **changes)
        assert ci.latest_run([RUN, unknown], EXPECTED, lambda _: {'artifacts': []}) is None


def test_failed_fork_attempt_is_not_hidden_by_old_success():
    failed = dict(RUN, id=124, pull_requests=[], conclusion='failure')
    def fork_api(endpoint, binary=False):
        if binary:
            return archive(dict(PROOF, run_id=124, result='failure'))
        return api(endpoint, binary)
    latest = ci.latest_run([RUN, failed], EXPECTED, fork_api)
    assert latest == failed
    with pytest.raises(ValueError, match='did not succeed'):
        ci.verify_run(latest, EXPECTED, fork_api)


def test_fork_checkout_mismatch_cannot_expose_old_success():
    newer = dict(RUN, id=124, pull_requests=[])
    def fork_api(endpoint, binary=False):
        if binary:
            return archive(dict(PROOF, run_id=124, checkout_sha=HEAD))
        return api(endpoint, binary)
    latest = ci.latest_run([RUN, newer], EXPECTED, fork_api)
    assert latest == newer
    assert not ci.verify_run(latest, EXPECTED, fork_api)


def test_fork_identity_must_belong_to_current_attempt():
    with pytest.raises(ValueError, match='identify'):
        ci.latest_run([dict(RUN, id=124, pull_requests=[])], EXPECTED, api)


def test_unknown_fork_receipt_ref_cannot_expose_old_success():
    def invalid_api(endpoint, binary=False):
        if binary:
            proof = dict(PROOF, run_id=124)
            del proof['ref']
            return archive(proof)
        return api(endpoint, binary)
    with pytest.raises(ValueError, match='identify a PR'):
        ci.latest_run([RUN, dict(RUN, id=124, pull_requests=[])], EXPECTED, invalid_api)


def test_kubernetes_exercises_changes_to_shared_verification_contract():
    triggers = workflows()['k8s-deploy.yml']['on']
    for event in ('push', 'pull_request'):
        assert 'scripts/ci_verification.py' in triggers[event]['paths']
        assert 'tests/test_ci_verification.py' in triggers[event]['paths']
        assert '.github/workflows/aurora-ci-minimal.yml' in triggers[event]['paths']


def test_fork_final_status_check_never_downloads_identity_after_status_snapshot():
    reads = []
    def fork_api(endpoint, binary=False):
        if '/runs?' in endpoint:
            reads.append('metadata')
            return {'workflow_runs': [dict(RUN, pull_requests=[])]}
        # A download after the final snapshot would permit a rerun during I/O
        # to be accepted against the pre-download successful status.
        assert reads.count('metadata') == 1, 'Receipt I/O after final status snapshot'
        return api(endpoint, binary)
    ci.wait(ENV, api=fork_api)
    assert reads == ['metadata', 'metadata']


def test_new_unresolved_fork_attempt_at_final_check_blocks_old_success():
    reads = []
    def fork_api(endpoint, binary=False):
        if '/runs?' in endpoint:
            reads.append('metadata')
            attempt = 2 if len(reads) == 1 else 3
            return {'workflow_runs': [dict(RUN, pull_requests=[], run_attempt=attempt)]}
        assert len(reads) == 1, 'Final check must not resolve new identities via I/O'
        return api(endpoint, binary)
    ticks = iter([0, 0, 2])
    with pytest.raises(TimeoutError):
        ci.wait(ENV, timeout=1, api=fork_api, clock=lambda: next(ticks), sleep=lambda _: None)
