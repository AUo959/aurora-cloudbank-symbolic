"""Tests for CONSTELLINK Multi-Thread Relay Beacon"""

import pytest
import json
from pathlib import Path
import sys

# Add src to path  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent.parent))

from symbolic.constellink import (  # noqa: E402
    ConstellinkRelay,
    MeshRequest,
    ThreadDescriptor,
    DlpPolicy,
    mesh_request_from_dict,
    load_constellink_spec,
    DEFAULT_ANCHOR_SEED,
    DEFAULT_ETHICS_PROTOCOL,
    AnchorAlignment,
    DriftFlag
)


@pytest.mark.unit
@pytest.mark.aurora
@pytest.mark.critical
def test_happy_path_bind_with_compatible_threads():
    """Test happy-path bind with two threads sharing the same anchor and compatible DLP tags"""
    relay = ConstellinkRelay()

    # Create two threads with same anchor and compatible tags
    threads = [
        ThreadDescriptor(
            thread_id="thread_alpha",
            anchor_seed="EOS_SEED_ORION",
            dlp_tags=["cross-thread", "public"],
            entropy_score=0.2,
            metadata={"source": "gpt4"}
        ),
        ThreadDescriptor(
            thread_id="thread_beta",
            anchor_seed="EOS_SEED_ORION",
            dlp_tags=["cross-thread"],
            entropy_score=0.15,
            metadata={"source": "claude"}
        )
    ]

    request = MeshRequest(
        request_id="test_req_001",
        threads=threads,
        dlp_policy=DlpPolicy(
            allow_cross_thread_content=True,
            allowed_dlp_tags=["cross-thread", "public"]
        )
    )

    # Bind threads
    mesh = relay.bind(request)

    # Verify mesh structure
    assert mesh.mesh_id.startswith("mesh_test_req_001_")
    assert mesh.anchor_seed == "EOS_SEED_ORION"
    assert mesh.ethics_protocol == DEFAULT_ETHICS_PROTOCOL
    assert len(mesh.threads) == 2

    # Verify threads are aligned
    for thread_view in mesh.threads:
        assert thread_view.anchor_alignment == AnchorAlignment.ALIGNED.value

    # Verify DLP policy - no rejections
    assert mesh.dlp_effective_policy.rejected_thread_count == 0
    assert mesh.dlp_effective_policy.cross_thread_content_allowed is True

    # Verify entropy summary
    assert mesh.entropy_summary.min_entropy == 0.15
    assert mesh.entropy_summary.max_entropy == 0.2
    assert abs(mesh.entropy_summary.mean_entropy - 0.175) < 0.001
    assert mesh.entropy_summary.drift_flag == DriftFlag.STABLE.value

    # Verify no divergent truths
    assert len(mesh.divergent_truths) == 0

    # Verify manifest
    assert mesh.mesh_manifest.version == "1.0.0"
    assert mesh.mesh_manifest.anchor_seed == "EOS_SEED_ORION"
    assert mesh.mesh_manifest.ethics_protocol == DEFAULT_ETHICS_PROTOCOL
    assert mesh.mesh_manifest.state_hash.startswith("sha256::")

    # Verify glyphcard generation
    glyphcard = mesh.glyphcard()
    assert "CONSTELLINK MESH GLYPHCARD" in glyphcard
    assert mesh.mesh_id in glyphcard
    assert "stable" in glyphcard


@pytest.mark.unit
@pytest.mark.aurora
@pytest.mark.critical
def test_dlp_rejection_with_incompatible_tags():
    """Test DLP rejection when a thread has incompatible dlp_tags"""
    relay = ConstellinkRelay()

    # Create threads with incompatible tags
    threads = [
        ThreadDescriptor(
            thread_id="thread_alpha",
            anchor_seed="EOS_SEED_ORION",
            dlp_tags=["cross-thread", "public"],
            entropy_score=0.2
        ),
        ThreadDescriptor(
            thread_id="thread_beta",
            anchor_seed="EOS_SEED_ORION",
            dlp_tags=["cross-thread", "private"],  # "private" not in allowed list
            entropy_score=0.3
        )
    ]

    request = MeshRequest(
        request_id="test_req_dlp",
        threads=threads,
        dlp_policy=DlpPolicy(
            allow_cross_thread_content=True,
            allowed_dlp_tags=["cross-thread", "public"]  # Only these tags allowed
        )
    )

    # Bind threads
    mesh = relay.bind(request)

    # Verify one thread was rejected
    assert mesh.dlp_effective_policy.rejected_thread_count == 1
    assert len(mesh.threads) == 1  # Only one thread accepted

    # Verify accepted thread
    assert mesh.threads[0].thread_id == "thread_alpha"

    # Verify divergent truths contain DLP rejection
    assert len(mesh.divergent_truths) >= 1

    dlp_rejection = next(
        (t for t in mesh.divergent_truths if t["type"] == "dlp_rejection"),
        None
    )
    assert dlp_rejection is not None
    assert dlp_rejection["thread_id"] == "thread_beta"
    assert "private" in dlp_rejection["rejected_tags"]

    # Verify glyphcard shows rejection
    glyphcard = mesh.glyphcard()
    assert "DLP Rejections: 1" in glyphcard
    assert "dlp_rejection" in glyphcard


@pytest.mark.unit
@pytest.mark.aurora
@pytest.mark.critical
def test_divergent_anchor_detection():
    """Test detection of divergent anchors and surfacing in divergent_truths"""
    relay = ConstellinkRelay()

    # Create threads with different anchor seeds
    threads = [
        ThreadDescriptor(
            thread_id="thread_alpha",
            anchor_seed="EOS_SEED_ORION",
            dlp_tags=["cross-thread"],
            entropy_score=0.4
        ),
        ThreadDescriptor(
            thread_id="thread_beta",
            anchor_seed="CUSTOM_ANCHOR_SEED",  # Different anchor
            dlp_tags=["cross-thread"],
            entropy_score=0.5
        ),
        ThreadDescriptor(
            thread_id="thread_gamma",
            anchor_seed="EOS_SEED_ORION",
            dlp_tags=["cross-thread"],
            entropy_score=0.45
        )
    ]

    request = MeshRequest(
        request_id="test_req_divergent",
        threads=threads
    )

    # Bind threads
    mesh = relay.bind(request)

    # Verify mesh uses default anchor due to divergence
    assert mesh.anchor_seed == DEFAULT_ANCHOR_SEED

    # Verify divergent truths contain anchor divergence
    anchor_divergence = next(
        (t for t in mesh.divergent_truths if t["type"] == "anchor_divergence"),
        None
    )
    assert anchor_divergence is not None
    assert "EOS_SEED_ORION" in anchor_divergence["anchors"]
    assert "CUSTOM_ANCHOR_SEED" in anchor_divergence["anchors"]
    assert DEFAULT_ANCHOR_SEED in anchor_divergence["resolution"]

    # Verify threads show correct alignment
    alpha_view = next(t for t in mesh.threads if t.thread_id == "thread_alpha")
    beta_view = next(t for t in mesh.threads if t.thread_id == "thread_beta")
    gamma_view = next(t for t in mesh.threads if t.thread_id == "thread_gamma")

    assert alpha_view.anchor_alignment == AnchorAlignment.ALIGNED.value
    assert beta_view.anchor_alignment == AnchorAlignment.DIVERGENT.value
    assert gamma_view.anchor_alignment == AnchorAlignment.ALIGNED.value

    # Verify drift flag is not stable due to moderate entropy and divergent anchor
    assert mesh.entropy_summary.drift_flag != DriftFlag.STABLE.value

    # Verify glyphcard shows divergent truths
    glyphcard = mesh.glyphcard()
    assert "Divergent Truths" in glyphcard


@pytest.mark.unit
@pytest.mark.aurora
def test_empty_threads_raises_error():
    """Test that binding with no threads raises ValueError"""
    relay = ConstellinkRelay()

    request = MeshRequest(
        request_id="test_req_empty",
        threads=[]
    )

    with pytest.raises(ValueError, match="At least one thread is required"):
        relay.bind(request)


@pytest.mark.unit
@pytest.mark.aurora
def test_mesh_request_from_dict():
    """Test mesh_request_from_dict helper function"""
    payload = {
        "request_id": "test_req_dict",
        "threads": [
            {
                "thread_id": "alpha",
                "anchor_seed": "EOS_SEED_ORION",
                "dlp_tags": ["cross-thread"],
                "entropy_score": 0.3,
                "metadata": {"key": "value"}
            }
        ],
        "target_anchor_seed": "CUSTOM_SEED",
        "dlp_policy": {
            "allow_cross_thread_content": False,
            "allowed_dlp_tags": ["cross-thread"]
        },
        "caller_context": {"user": "test"}
    }

    request = mesh_request_from_dict(payload)

    assert request.request_id == "test_req_dict"
    assert len(request.threads) == 1
    assert request.threads[0].thread_id == "alpha"
    assert request.threads[0].anchor_seed == "EOS_SEED_ORION"
    assert request.threads[0].entropy_score == 0.3
    assert request.target_anchor_seed == "CUSTOM_SEED"
    assert request.dlp_policy.allow_cross_thread_content is False
    assert request.dlp_policy.allowed_dlp_tags == ["cross-thread"]
    assert request.caller_context == {"user": "test"}


@pytest.mark.unit
@pytest.mark.aurora
def test_mesh_to_dict():
    """Test ConstellinkMesh.to_dict() for JSON export"""
    relay = ConstellinkRelay()

    threads = [
        ThreadDescriptor(
            thread_id="alpha",
            anchor_seed="EOS_SEED_ORION",
            entropy_score=0.2
        )
    ]

    request = MeshRequest(
        request_id="test_dict",
        threads=threads
    )

    mesh = relay.bind(request)
    mesh_dict = mesh.to_dict()

    # Verify dict structure
    assert isinstance(mesh_dict, dict)
    assert mesh_dict["mesh_id"] == mesh.mesh_id
    assert mesh_dict["anchor_seed"] == mesh.anchor_seed
    assert "threads" in mesh_dict
    assert "entropy_summary" in mesh_dict
    assert "mesh_manifest" in mesh_dict

    # Verify can serialize to JSON
    json_str = json.dumps(mesh_dict)
    assert len(json_str) > 0

    # Verify can deserialize
    parsed = json.loads(json_str)
    assert parsed["mesh_id"] == mesh.mesh_id


@pytest.mark.unit
@pytest.mark.aurora
def test_target_anchor_seed_override():
    """Test that target_anchor_seed in request overrides thread anchors"""
    relay = ConstellinkRelay()

    threads = [
        ThreadDescriptor(
            thread_id="alpha",
            anchor_seed="EOS_SEED_ORION"
        )
    ]

    request = MeshRequest(
        request_id="test_override",
        threads=threads,
        target_anchor_seed="CUSTOM_OVERRIDE_SEED"
    )

    mesh = relay.bind(request)

    # Verify mesh uses overridden anchor
    assert mesh.anchor_seed == "CUSTOM_OVERRIDE_SEED"


@pytest.mark.unit
@pytest.mark.aurora
def test_high_entropy_drift_flag():
    """Test that high entropy scores result in divergent drift flag"""
    relay = ConstellinkRelay()

    threads = [
        ThreadDescriptor(
            thread_id="alpha",
            anchor_seed="EOS_SEED_ORION",
            entropy_score=0.8
        ),
        ThreadDescriptor(
            thread_id="beta",
            anchor_seed="EOS_SEED_ORION",
            entropy_score=0.9
        )
    ]

    request = MeshRequest(
        request_id="test_high_entropy",
        threads=threads
    )

    mesh = relay.bind(request)

    # Verify divergent drift flag due to high entropy
    assert mesh.entropy_summary.drift_flag == DriftFlag.DIVERGENT.value
    assert mesh.entropy_summary.mean_entropy > 0.6


@pytest.mark.unit
@pytest.mark.aurora
def test_unknown_anchor_alignment():
    """Test threads with no anchor_seed get unknown alignment"""
    relay = ConstellinkRelay()

    threads = [
        ThreadDescriptor(
            thread_id="alpha",
            # No anchor_seed provided
            entropy_score=0.1
        )
    ]

    request = MeshRequest(
        request_id="test_unknown",
        threads=threads
    )

    mesh = relay.bind(request)

    # Verify unknown alignment
    assert mesh.threads[0].anchor_alignment == AnchorAlignment.UNKNOWN.value


@pytest.mark.integration
@pytest.mark.aurora
def test_load_constellink_spec():
    """Test loading the CONSTELLINK JSON spec"""
    spec = load_constellink_spec()

    assert "modules" in spec
    assert len(spec["modules"]) >= 1

    constellink_module = next(
        (m for m in spec["modules"] if m["module_name"] == "CONSTELLINK"),
        None
    )

    assert constellink_module is not None
    assert constellink_module["version"] == "v1.1.0"
    assert constellink_module["type"] == "Multi-Thread Relay Beacon"
    assert constellink_module["metadata"]["anchor_seed"] == "EOS_SEED_ORION"
    assert constellink_module["metadata"]["ethics_protocol"] == "Picard_Delta_3"


@pytest.mark.unit
@pytest.mark.aurora
def test_all_threads_rejected_edge_case():
    """Test edge case where all threads are rejected by DLP policy"""
    relay = ConstellinkRelay()

    threads = [
        ThreadDescriptor(
            thread_id="alpha",
            dlp_tags=["private"]
        ),
        ThreadDescriptor(
            thread_id="beta",
            dlp_tags=["secret"]
        )
    ]

    request = MeshRequest(
        request_id="test_all_rejected",
        threads=threads,
        dlp_policy=DlpPolicy(
            allowed_dlp_tags=["public"]  # None of the threads have "public"
        )
    )

    mesh = relay.bind(request)

    # Verify all threads rejected
    assert mesh.dlp_effective_policy.rejected_thread_count == 2
    assert len(mesh.threads) == 0

    # Verify divergent truth about all rejections
    all_rejected = next(
        (t for t in mesh.divergent_truths if t["type"] == "all_threads_rejected"),
        None
    )
    assert all_rejected is not None
    assert all_rejected["original_thread_count"] == 2
