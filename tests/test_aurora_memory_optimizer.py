from src.aurora_fusion import AuroraMemoryOptimizer, MemoryStatus, MemoryTier
from src.core.native_symbolic_anchor import NativeSymbolicCPUAnchor


def build_optimizer(symbolic_dim: int = 256) -> AuroraMemoryOptimizer:
    anchor = NativeSymbolicCPUAnchor(num_qubits=4, symbolic_dim=symbolic_dim)
    return AuroraMemoryOptimizer(anchor=anchor, symbolic_dim=symbolic_dim)


def test_memory_optimizer_retrieves_anchor_relevant_context():
    optimizer = build_optimizer()
    optimizer.remember(
        owner="ops",
        content="L2 treaty negotiation stabilized the EOS_SEED_ORION corridor for Orion diplomacy.",
        importance=9.0,
        layer="L2",
        source="sim.turn",
        tags=["diplomacy", "treaty", "corridor"],
        anchor_ids=["EOS_SEED_ORION", "ORION_STATION"],
    )
    optimizer.remember(
        owner="ops",
        content="Ritual archive maintenance completed for off-site glyph storage.",
        importance=4.0,
        layer="L3",
        source="ops.note",
        tags=["archive", "glyph"],
        anchor_ids=["RITUAL_ARC"],
    )

    hits = optimizer.retrieve_context("ops", "Orion treaty corridor negotiation", top_k=2)

    assert hits
    assert hits[0].record_id
    assert "treaty negotiation" in hits[0].content.lower()
    assert hits[0].score > hits[-1].score
    assert "EOS_SEED_ORION" in hits[0].anchor_ids


def test_memory_optimizer_marks_conflicting_records_as_disputed():
    optimizer = build_optimizer()
    optimizer.remember(
        owner="ops",
        content="EOS_SEED_ORION remained stable after THREADSYNC verification.",
        importance=8.0,
        layer="L3",
        source="threadsync.ok",
        tags=["stable", "verification"],
        anchor_ids=["EOS_SEED_ORION", "THREADSYNC"],
    )
    disputed = optimizer.remember(
        owner="ops",
        content="EOS_SEED_ORION drift caused THREADSYNC failure during verification.",
        importance=8.0,
        layer="L3",
        source="threadsync.fail",
        tags=["drift", "failure", "verification"],
        anchor_ids=["EOS_SEED_ORION", "THREADSYNC"],
    )

    assert disputed.status == MemoryStatus.DISPUTED
    assert disputed.related_records
    first_record = optimizer.export_owner_state("ops")["records"][0]
    assert first_record["status"] == MemoryStatus.DISPUTED.value


def test_memory_optimizer_maintenance_compresses_overflow_into_summary():
    optimizer = build_optimizer()
    for index in range(18):
        optimizer.remember(
            owner="ops",
            content=(
                f"L2 convoy memory {index} preserved on EOS_SEED_ORION trade lane with Orion station "
                "stability verification."
            ),
            importance=3.0 + (index % 4),
            layer="L2",
            source="sim.turn",
            tags=["trade", "convoy", "stability"],
            anchor_ids=["EOS_SEED_ORION", "ORION_STATION"],
        )

    report = optimizer.run_maintenance("ops")
    exported = optimizer.export_owner_state("ops")

    assert report["summaries_created"] >= 1
    assert any("compressed memory" in record["content"].lower() for record in exported["records"])
    assert any(record["tier"] == MemoryTier.ARCHIVED.value for record in exported["records"])


def test_memory_optimizer_builds_sealed_continuity_snapshot():
    optimizer = build_optimizer()
    optimizer.remember(
        owner="ops",
        content="QUEUEANCHOR registered THREADCORE_RECOVERY for continuity stabilization.",
        importance=7.0,
        layer="L3",
        source="QUEUEANCHOR",
        tags=["queueanchor", "continuity"],
        anchor_ids=["THREADCORE_RECOVERY", "EOS_SEED_ORION"],
    )

    snapshot = optimizer.build_continuity_snapshot("ops")

    assert snapshot["owner"] == "ops"
    assert snapshot["anchor_seed"] == "EOS_SEED_ORION"
    assert snapshot["memory_doctrine"] == "Thermax Precedent"
    assert snapshot["integrity_verified"] is True
