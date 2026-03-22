"""Aurora/ORION/GUMAS-native memory optimization runtime."""

from __future__ import annotations

import hashlib
import math
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from modules.reflective_autonomy.symbolic_tagging_engine import classify_thread_content
from modules.reflective_autonomy.threadcore_tagging import tag_thread_context
from src.core.native_symbolic_anchor import NativeSymbolicCPUAnchor
from src.core.native_vsa import NativeSymbolicVector

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")
ANCHOR_PATTERN = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
LAYER_PATTERN = re.compile(r"\bL[123]\b", re.IGNORECASE)
DEFAULT_OWNER = "AuroraFusionEngine"


class MemoryTier(str, Enum):
    """Aurora three-tier memory stratification."""

    ACTIVE = "active"
    COMPRESSED = "compressed"
    ARCHIVED = "archived"


class MemoryStatus(str, Enum):
    """Thermax-aware memory status labels."""

    CANONICAL = "canonical"
    DISPUTED = "disputed"
    LOCKED = "locked"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class AuroraMemoryDoctrine:
    """Canonical doctrine for Aurora/ORION memory operations."""

    anchor_seed: str = "EOS_SEED_ORION"
    continuity_seal: str = "Aurora_Continuity_Seal_v2.2.5"
    ethics_protocol: str = "Picard_Delta_3"
    memory_doctrine: str = "Thermax Precedent"
    drift_lock: float = 0.000
    active_capacity: int = 12
    compressed_capacity: int = 40
    archive_capacity: int = 160
    active_window_hours: float = 72.0
    compression_batch_size: int = 4
    conflict_pairs: Tuple[Tuple[str, str], ...] = (
        ("success", "failure"),
        ("stable", "drift"),
        ("secure", "compromised"),
        ("ally", "hostile"),
        ("approved", "blocked"),
        ("present", "missing"),
        ("gain", "loss"),
        ("verified", "disputed"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe doctrine manifest."""
        return {
            "anchor_seed": self.anchor_seed,
            "continuity_seal": self.continuity_seal,
            "ethics_protocol": self.ethics_protocol,
            "memory_doctrine": self.memory_doctrine,
            "drift_lock": self.drift_lock,
            "active_capacity": self.active_capacity,
            "compressed_capacity": self.compressed_capacity,
            "archive_capacity": self.archive_capacity,
            "active_window_hours": self.active_window_hours,
            "compression_batch_size": self.compression_batch_size,
            "conflict_pairs": [list(pair) for pair in self.conflict_pairs],
        }


@dataclass
class AuroraMemoryRecord:
    """Single memory object with symbolic, narrative, and continuity metadata."""

    record_id: str
    owner: str
    content: str
    source: str
    layer: str
    timestamp: float
    last_access: float
    last_decay_at: float
    importance: float
    truth_confidence: float
    strength: float
    tier: MemoryTier
    status: MemoryStatus
    tags: List[str] = field(default_factory=list)
    anchor_ids: List[str] = field(default_factory=list)
    summary_of: List[str] = field(default_factory=list)
    related_records: List[str] = field(default_factory=list)
    classification: Dict[str, Any] = field(default_factory=dict)
    threadcore: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tokens: List[str] = field(default_factory=list)
    contention_score: float = 0.0
    access_count: int = 0
    vector: Optional[NativeSymbolicVector] = field(default=None, repr=False)

    def age_seconds(self, now: Optional[float] = None) -> float:
        current_time = now or time.time()
        return max(0.0, current_time - self.timestamp)

    def quiet_seconds(self, now: Optional[float] = None) -> float:
        current_time = now or time.time()
        return max(0.0, current_time - self.last_access)

    def decay(self, now: Optional[float] = None) -> None:
        """Apply importance-weighted decay without overwriting access timestamps."""
        if self.status == MemoryStatus.LOCKED:
            return

        current_time = now or time.time()
        elapsed = max(0.0, current_time - self.last_decay_at)
        if elapsed == 0:
            return

        tier_bias = {
            MemoryTier.ACTIVE: 1.0,
            MemoryTier.COMPRESSED: 1.75,
            MemoryTier.ARCHIVED: 2.5,
        }[self.tier]
        half_life = max(
            3600.0,
            43200.0 * tier_bias * (1.0 + (self.importance / 10.0)) * (0.75 + self.truth_confidence),
        )
        decay_constant = math.log(2.0) / half_life
        self.strength *= math.exp(-decay_constant * elapsed)
        self.last_decay_at = current_time

    def reinforce(self, now: Optional[float] = None, factor: float = 0.18) -> None:
        """Reinforce a record when it is retrieved or revisited."""
        current_time = now or time.time()
        self.last_access = current_time
        self.last_decay_at = current_time
        self.access_count += 1
        if self.status != MemoryStatus.LOCKED:
            self.strength = min(2.0, self.strength + factor * (0.5 + (self.importance / 10.0)))

    def to_dict(self) -> Dict[str, Any]:
        """Compact record export for artifacts and tests."""
        return {
            "record_id": self.record_id,
            "owner": self.owner,
            "content": self.content,
            "source": self.source,
            "layer": self.layer,
            "importance": round(self.importance, 3),
            "truth_confidence": round(self.truth_confidence, 3),
            "strength": round(self.strength, 4),
            "tier": self.tier.value,
            "status": self.status.value,
            "tags": list(self.tags),
            "anchor_ids": list(self.anchor_ids),
            "summary_of": list(self.summary_of),
            "related_records": list(self.related_records),
            "classification": dict(self.classification),
            "threadcore": dict(self.threadcore),
            "contention_score": round(self.contention_score, 4),
            "access_count": self.access_count,
            "vector_symbol": self.vector.symbol if self.vector else None,
        }


@dataclass(frozen=True)
class AuroraMemoryHit:
    """Ranked retrieval result with explainable scoring."""

    record_id: str
    owner: str
    content: str
    layer: str
    tier: str
    status: str
    source: str
    score: float
    anchor_ids: Tuple[str, ...]
    tags: Tuple[str, ...]
    score_breakdown: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        """Return a stable retrieval payload."""
        return {
            "record_id": self.record_id,
            "owner": self.owner,
            "content": self.content,
            "layer": self.layer,
            "tier": self.tier,
            "status": self.status,
            "source": self.source,
            "score": round(self.score, 4),
            "anchor_ids": list(self.anchor_ids),
            "tags": list(self.tags),
            "score_breakdown": {key: round(value, 4) for key, value in self.score_breakdown.items()},
        }


class AuroraMemoryOptimizer:
    """Advanced Aurora/ORION/GUMAS memory optimizer with symbolic retrieval."""

    def __init__(
        self,
        anchor: Optional[NativeSymbolicCPUAnchor] = None,
        doctrine: Optional[AuroraMemoryDoctrine] = None,
        symbolic_dim: int = 512,
    ):
        self.doctrine = doctrine or AuroraMemoryDoctrine()
        self.symbolic_dim = symbolic_dim
        self.anchor = anchor or NativeSymbolicCPUAnchor(symbolic_dim=symbolic_dim)
        self._owners: Dict[str, List[AuroraMemoryRecord]] = defaultdict(list)
        self._record_index: Dict[str, AuroraMemoryRecord] = {}

    def remember(
        self,
        owner: str,
        content: str,
        *,
        importance: float = 5.0,
        layer: str = "L2",
        source: str = "simulation",
        tags: Optional[Sequence[str]] = None,
        anchor_ids: Optional[Sequence[str]] = None,
        truth_confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None,
        summary_of: Optional[Sequence[str]] = None,
        status: MemoryStatus = MemoryStatus.CANONICAL,
        scan_conflicts: bool = True,
    ) -> AuroraMemoryRecord:
        """Create and register a new memory record."""
        record = self._build_record(
            owner=owner,
            content=content,
            importance=importance,
            layer=layer,
            source=source,
            tags=tags,
            anchor_ids=anchor_ids,
            truth_confidence=truth_confidence,
            metadata=metadata,
            summary_of=summary_of,
            status=status,
        )
        self._owners[owner].append(record)
        self._record_index[record.record_id] = record
        if scan_conflicts:
            self._reconcile_conflicts(owner, record)
        return record

    def retrieve_context(
        self,
        owner: Optional[str],
        query: str,
        *,
        top_k: int = 5,
        include_archived: bool = False,
    ) -> List[AuroraMemoryHit]:
        """Retrieve the highest-value context for a query."""
        records = self._select_records(owner)
        if not include_archived:
            records = [record for record in records if record.tier != MemoryTier.ARCHIVED]

        if not records:
            return []

        query_vector, query_tokens, query_tags, query_anchors = self._build_query_signature(query)
        ranked: List[Tuple[float, Dict[str, float], AuroraMemoryRecord]] = []
        now = time.time()

        for record in records:
            record.decay(now)
            breakdown = self._score_record(
                record,
                query_vector=query_vector,
                query_tokens=query_tokens,
                query_tags=query_tags,
                query_anchors=query_anchors,
                now=now,
            )
            total_score = sum(breakdown.values())
            ranked.append((total_score, breakdown, record))

        ranked.sort(key=lambda item: item[0], reverse=True)
        hits: List[AuroraMemoryHit] = []
        for score, breakdown, record in ranked[:top_k]:
            record.reinforce(now)
            hits.append(
                AuroraMemoryHit(
                    record_id=record.record_id,
                    owner=record.owner,
                    content=record.content,
                    layer=record.layer,
                    tier=record.tier.value,
                    status=record.status.value,
                    source=record.source,
                    score=score,
                    anchor_ids=tuple(record.anchor_ids),
                    tags=tuple(record.tags),
                    score_breakdown=breakdown,
                )
            )
        return hits

    def run_maintenance(self, owner: Optional[str] = None) -> Dict[str, Any]:
        """Decay, tier, compress, and prune memory stores."""
        owners = [owner] if owner else sorted(self._owners.keys())
        now = time.time()
        report = {
            "owners": {},
            "compressed_records": 0,
            "archived_records": 0,
            "summaries_created": 0,
        }

        for owner_key in owners:
            records = self._owners.get(owner_key, [])
            if not records:
                continue

            for record in records:
                record.decay(now)
                self._retier_record(record, now)

            summaries = self._compress_owner(owner_key, now)
            report["compressed_records"] += summaries["compressed_records"]
            report["archived_records"] += summaries["archived_records"]
            report["summaries_created"] += summaries["summaries_created"]
            report["owners"][owner_key] = summaries
            self._prune_archive(owner_key)

        return report

    def lock_memory(self, owner: str, anchor_id: Optional[str] = None, locked: bool = True) -> int:
        """Apply LOCKMEM semantics to a store or specific anchor lineage."""
        target_status = MemoryStatus.LOCKED if locked else MemoryStatus.CANONICAL
        updated = 0
        for record in self._owners.get(owner, []):
            if anchor_id and anchor_id not in record.anchor_ids:
                continue
            if locked:
                record.status = MemoryStatus.LOCKED
            elif record.status == MemoryStatus.LOCKED:
                record.status = MemoryStatus.CANONICAL
            record.tier = MemoryTier.ACTIVE if locked else record.tier
            updated += 1
        return updated

    def queue_anchor(self, owner: str, anchor_id: str, reason: str, *, importance: float = 8.0) -> AuroraMemoryRecord:
        """Register a re-callable symbolic anchor."""
        content = f"QUEUEANCHOR registered {anchor_id}: {reason}"
        return self.remember(
            owner=owner,
            content=content,
            importance=importance,
            layer="L3",
            source="QUEUEANCHOR",
            tags=["queueanchor", "anchor", "continuity"],
            anchor_ids=[anchor_id, self.doctrine.anchor_seed],
            metadata={"command": "QUEUEANCHOR"},
        )

    def build_continuity_snapshot(self, owner: Optional[str] = None) -> Dict[str, Any]:
        """Produce a sealed continuity report for a store or the full runtime."""
        records = self._select_records(owner)
        tier_counts = Counter(record.tier.value for record in records)
        status_counts = Counter(record.status.value for record in records)
        layer_counts = Counter(record.layer for record in records)
        anchor_counts = Counter(anchor for record in records for anchor in record.anchor_ids)
        disputed = [record.record_id for record in records if record.status == MemoryStatus.DISPUTED]
        drift_delta = round(
            sum(record.contention_score for record in records) / max(1, len(records)),
            6,
        )
        snapshot = {
            "owner": owner or "GLOBAL",
            "records": len(records),
            "anchor_seed": self.doctrine.anchor_seed,
            "continuity_seal": self.doctrine.continuity_seal,
            "ethics_protocol": self.doctrine.ethics_protocol,
            "memory_doctrine": self.doctrine.memory_doctrine,
            "drift_lock_target": self.doctrine.drift_lock,
            "drift_delta": drift_delta,
            "anchor_alignment": round(max(0.0, 1.0 - drift_delta), 6),
            "tier_counts": dict(tier_counts),
            "status_counts": dict(status_counts),
            "layer_counts": dict(layer_counts),
            "top_anchors": anchor_counts.most_common(5),
            "disputed_records": disputed,
        }
        snapshot_id = self._make_id("snapshot", owner or "global", snapshot["records"])
        integrity_hash = self.anchor.memory_sealer.seal_state(snapshot_id, dict(snapshot))
        snapshot["snapshot_id"] = snapshot_id
        snapshot["integrity_hash"] = integrity_hash
        snapshot["integrity_verified"] = self.anchor.memory_sealer.verify_integrity(snapshot_id)
        return snapshot

    def export_owner_state(self, owner: str) -> Dict[str, Any]:
        """Export records and continuity state for debugging or persistence."""
        return {
            "owner": owner,
            "doctrine": self.doctrine.to_dict(),
            "records": [record.to_dict() for record in self._owners.get(owner, [])],
            "continuity_snapshot": self.build_continuity_snapshot(owner),
        }

    def _select_records(self, owner: Optional[str]) -> List[AuroraMemoryRecord]:
        if owner is None:
            return [record for records in self._owners.values() for record in records]
        return list(self._owners.get(owner, []))

    def _build_record(
        self,
        *,
        owner: str,
        content: str,
        importance: float,
        layer: str,
        source: str,
        tags: Optional[Sequence[str]],
        anchor_ids: Optional[Sequence[str]],
        truth_confidence: float,
        metadata: Optional[Dict[str, Any]],
        summary_of: Optional[Sequence[str]],
        status: MemoryStatus,
    ) -> AuroraMemoryRecord:
        current_time = time.time()
        record_tags = self._normalize_terms(tags or [])
        tokens = self._tokenize(content)
        classification = classify_thread_content(content)
        threadcore = tag_thread_context(content)
        inferred_layer = self._infer_layer(content, default_layer=layer)
        inferred_anchors = self._infer_anchor_ids(content, anchor_ids)

        record_tags.extend(
            [
                classification.get("primary_folder", "Unsorted"),
                threadcore.get("primary_folder", "Unsorted"),
                f"source:{source}",
                inferred_layer,
            ]
        )
        record_tags = self._normalize_terms(record_tags)

        vector = self._compose_vector(tokens, record_tags, inferred_anchors)
        record_id = self._make_id(owner, source, content, current_time)
        return AuroraMemoryRecord(
            record_id=record_id,
            owner=owner,
            content=content.strip(),
            source=source,
            layer=inferred_layer,
            timestamp=current_time,
            last_access=current_time,
            last_decay_at=current_time,
            importance=max(1.0, min(10.0, importance)),
            truth_confidence=max(0.0, min(1.0, truth_confidence)),
            strength=1.0 + (max(1.0, min(10.0, importance)) / 20.0),
            tier=MemoryTier.ACTIVE,
            status=status,
            tags=record_tags,
            anchor_ids=inferred_anchors,
            summary_of=list(summary_of or []),
            classification=classification,
            threadcore=threadcore,
            metadata=dict(metadata or {}),
            tokens=tokens,
            vector=vector,
        )

    def _build_query_signature(
        self, query: str
    ) -> Tuple[NativeSymbolicVector, List[str], List[str], List[str]]:
        tokens = self._tokenize(query)
        classification = classify_thread_content(query)
        threadcore = tag_thread_context(query)
        tags = self._normalize_terms(
            [
                classification.get("primary_folder", "Unsorted"),
                threadcore.get("primary_folder", "Unsorted"),
                threadcore.get("priority", "low"),
            ]
        )
        anchors = self._infer_anchor_ids(query, [])
        return self._compose_vector(tokens, tags, anchors), tokens, tags, anchors

    def _score_record(
        self,
        record: AuroraMemoryRecord,
        *,
        query_vector: NativeSymbolicVector,
        query_tokens: Sequence[str],
        query_tags: Sequence[str],
        query_anchors: Sequence[str],
        now: float,
    ) -> Dict[str, float]:
        record_vector = record.vector or self._compose_vector(record.tokens, record.tags, record.anchor_ids)
        symbolic_similarity = max(0.0, (query_vector.similarity(record_vector) + 1.0) / 2.0)
        lexical_overlap = self._overlap_score(query_tokens, record.tokens)
        tag_overlap = self._overlap_score(query_tags, record.tags)
        anchor_overlap = self._overlap_score(query_anchors, record.anchor_ids)
        importance_score = record.importance / 10.0
        recency_score = math.exp(-record.quiet_seconds(now) / (24.0 * 3600.0 * 5.0))
        continuity_bonus = 1.0 if self.doctrine.anchor_seed in record.anchor_ids else 0.0
        tier_bonus = {
            MemoryTier.ACTIVE: 0.08,
            MemoryTier.COMPRESSED: 0.03,
            MemoryTier.ARCHIVED: -0.05,
        }[record.tier]
        dispute_penalty = -0.18 * record.contention_score
        locked_bonus = 0.06 if record.status == MemoryStatus.LOCKED else 0.0
        return {
            "symbolic": symbolic_similarity * 0.42,
            "lexical": lexical_overlap * 0.18,
            "tag": tag_overlap * 0.08,
            "anchor": anchor_overlap * 0.12,
            "importance": importance_score * 0.10,
            "recency": recency_score * 0.10,
            "continuity": continuity_bonus * 0.05,
            "tier": tier_bonus,
            "locked": locked_bonus,
            "contention": dispute_penalty,
        }

    def _retier_record(self, record: AuroraMemoryRecord, now: float) -> None:
        if record.status == MemoryStatus.LOCKED:
            record.tier = MemoryTier.ACTIVE
            return

        vitality = (
            (record.strength * 0.4)
            + ((record.importance / 10.0) * 0.25)
            + (min(record.access_count, 5) / 5.0 * 0.15)
            + (record.truth_confidence * 0.20)
        )
        quiet_hours = record.quiet_seconds(now) / 3600.0
        if vitality >= 0.95 and quiet_hours <= self.doctrine.active_window_hours:
            record.tier = MemoryTier.ACTIVE
            record.status = MemoryStatus.DISPUTED if record.contention_score >= 0.35 else record.status
            return
        if vitality >= 0.45 or record.importance >= 7.5:
            record.tier = MemoryTier.COMPRESSED
            record.status = MemoryStatus.DISPUTED if record.contention_score >= 0.35 else record.status
            return
        record.tier = MemoryTier.ARCHIVED
        if record.status != MemoryStatus.DISPUTED:
            record.status = MemoryStatus.ARCHIVED

    def _compress_owner(self, owner: str, now: float) -> Dict[str, Any]:
        records = self._owners.get(owner, [])
        active_records = [record for record in records if record.tier == MemoryTier.ACTIVE and record.status != MemoryStatus.LOCKED]
        compressed_records = [
            record for record in records if record.tier == MemoryTier.COMPRESSED and record.status != MemoryStatus.LOCKED
        ]
        hot_records = [
            record
            for record in records
            if record.tier in {MemoryTier.ACTIVE, MemoryTier.COMPRESSED}
            and record.status != MemoryStatus.LOCKED
            and not record.metadata.get("summary_record")
        ]
        summaries_created = 0
        archived_records = 0

        overflow = max(0, len(hot_records) - self.doctrine.active_capacity)
        if overflow:
            candidates = sorted(hot_records, key=self._compression_priority)[: max(overflow, self.doctrine.compression_batch_size)]
            summary = self._synthesize_summary(owner, candidates, now)
            if summary is not None:
                self._owners[owner].append(summary)
                self._record_index[summary.record_id] = summary
                summaries_created += 1
                for record in candidates:
                    record.tier = MemoryTier.ARCHIVED
                    if record.status != MemoryStatus.DISPUTED:
                        record.status = MemoryStatus.ARCHIVED
                    archived_records += 1

        overflow_compressed = max(0, len(compressed_records) - self.doctrine.compressed_capacity)
        if overflow_compressed:
            to_archive = sorted(compressed_records, key=self._compression_priority)[:overflow_compressed]
            for record in to_archive:
                record.tier = MemoryTier.ARCHIVED
                if record.status != MemoryStatus.DISPUTED:
                    record.status = MemoryStatus.ARCHIVED
                archived_records += 1

        return {
            "owner": owner,
            "compressed_records": overflow,
            "archived_records": archived_records,
            "summaries_created": summaries_created,
        }

    def _compression_priority(self, record: AuroraMemoryRecord) -> Tuple[float, float, float]:
        return (
            record.strength,
            record.importance,
            -record.access_count,
        )

    def _synthesize_summary(
        self, owner: str, records: Sequence[AuroraMemoryRecord], now: float
    ) -> Optional[AuroraMemoryRecord]:
        if not records:
            return None

        anchors = Counter(anchor for record in records for anchor in record.anchor_ids)
        tags = Counter(tag for record in records for tag in record.tags if not tag.startswith("source:"))
        layers = Counter(record.layer for record in records)
        sources = Counter(record.source for record in records)
        latest = max(records, key=lambda record: record.timestamp)
        status = MemoryStatus.DISPUTED if any(record.status == MemoryStatus.DISPUTED for record in records) else MemoryStatus.CANONICAL
        dominant_anchor = anchors.most_common(1)[0][0] if anchors else self.doctrine.anchor_seed
        dominant_tags = [tag for tag, _ in tags.most_common(4)] or ["continuity"]
        dominant_layers = ", ".join(f"{layer}={count}" for layer, count in sorted(layers.items()))
        sources_line = ", ".join(f"{source}={count}" for source, count in sorted(sources.items()))
        summary_content = (
            f"Aurora compressed memory for {owner}: consolidated {len(records)} records under {dominant_anchor}. "
            f"Layers [{dominant_layers}] sourced from [{sources_line}]. "
            f"Dominant tags: {', '.join(dominant_tags)}. "
            f"Latest retained event: {latest.content[:160]}. "
            f"{'Truth arbitration retained due to disputed inputs.' if status == MemoryStatus.DISPUTED else 'Continuity stable after compression.'}"
        )
        return self._build_record(
            owner=owner,
            content=summary_content,
            importance=min(10.0, max(record.importance for record in records) + 0.5),
            layer=latest.layer,
            source="compression.summary",
            tags=dominant_tags + ["compressed", "summary", "symbolic_compression"],
            anchor_ids=list(dict.fromkeys([dominant_anchor, self.doctrine.anchor_seed])),
            truth_confidence=sum(record.truth_confidence for record in records) / len(records),
            metadata={
                "summary_record": True,
                "created_at": now,
                "source_record_count": len(records),
            },
            summary_of=[record.record_id for record in records],
            status=status,
        )

    def _prune_archive(self, owner: str) -> None:
        records = self._owners.get(owner, [])
        archived = [record for record in records if record.tier == MemoryTier.ARCHIVED and record.status != MemoryStatus.LOCKED]
        if len(archived) <= self.doctrine.archive_capacity:
            return

        archived.sort(key=self._compression_priority)
        overflow = archived[: len(archived) - self.doctrine.archive_capacity]
        overflow_ids = {record.record_id for record in overflow}
        self._owners[owner] = [record for record in records if record.record_id not in overflow_ids]
        for record_id in overflow_ids:
            self._record_index.pop(record_id, None)

    def _reconcile_conflicts(self, owner: str, new_record: AuroraMemoryRecord) -> None:
        shared_candidates = [
            record
            for record in self._owners.get(owner, [])
            if record.record_id != new_record.record_id
            and (set(record.anchor_ids) & set(new_record.anchor_ids) or set(record.tags) & set(new_record.tags))
        ]
        new_tokens = set(new_record.tokens)
        for existing in shared_candidates:
            existing_tokens = set(existing.tokens)
            conflict_score = self._conflict_score(new_tokens, existing_tokens)
            if conflict_score < 0.35:
                continue

            new_record.status = MemoryStatus.DISPUTED
            existing.status = MemoryStatus.DISPUTED
            new_record.contention_score = max(new_record.contention_score, conflict_score)
            existing.contention_score = max(existing.contention_score, conflict_score)
            if existing.record_id not in new_record.related_records:
                new_record.related_records.append(existing.record_id)
            if new_record.record_id not in existing.related_records:
                existing.related_records.append(new_record.record_id)

    def _conflict_score(self, left_tokens: Iterable[str], right_tokens: Iterable[str]) -> float:
        left = set(left_tokens)
        right = set(right_tokens)
        shared = len(left & right)
        if shared < 2:
            return 0.0

        contradictions = 0
        for positive, negative in self.doctrine.conflict_pairs:
            if (positive in left and negative in right) or (negative in left and positive in right):
                contradictions += 1
        if contradictions == 0:
            return 0.0
        return min(1.0, (contradictions * 0.25) + (shared * 0.04))

    def _compose_vector(
        self,
        tokens: Sequence[str],
        tags: Sequence[str],
        anchor_ids: Sequence[str],
    ) -> NativeSymbolicVector:
        symbols = list(dict.fromkeys(list(anchor_ids) + list(tags) + list(tokens)))[:12]
        if not symbols:
            symbols = [self.doctrine.anchor_seed]

        vector = NativeSymbolicVector.from_symbol(symbols[0], self.symbolic_dim)
        for symbol in symbols[1:]:
            vector = vector.superpose(NativeSymbolicVector.from_symbol(symbol, self.symbolic_dim))
        return vector

    def _tokenize(self, text: str) -> List[str]:
        return [token.lower() for token in TOKEN_PATTERN.findall(text) if len(token) > 2]

    def _normalize_terms(self, values: Iterable[str]) -> List[str]:
        cleaned: List[str] = []
        for value in values:
            if not value:
                continue
            normalized = value.strip().lower().replace(" ", "_")
            if normalized and normalized not in cleaned:
                cleaned.append(normalized)
        return cleaned

    def _infer_layer(self, content: str, default_layer: str) -> str:
        match = LAYER_PATTERN.search(content)
        if match:
            return match.group(0).upper()
        normalized = default_layer.strip().upper()
        return normalized if normalized in {"L1", "L2", "L3"} else "L2"

    def _infer_anchor_ids(self, content: str, anchor_ids: Optional[Sequence[str]]) -> List[str]:
        discovered = list(anchor_ids or [])
        discovered.extend(ANCHOR_PATTERN.findall(content))
        discovered.append(self.doctrine.anchor_seed)
        unique: List[str] = []
        for anchor in discovered:
            normalized = anchor.strip().upper()
            if normalized and normalized not in unique:
                unique.append(normalized)
        return unique

    def _overlap_score(self, left: Sequence[str], right: Sequence[str]) -> float:
        left_set = set(left)
        right_set = set(right)
        if not left_set or not right_set:
            return 0.0
        return len(left_set & right_set) / len(left_set | right_set)

    def _make_id(self, *parts: Any) -> str:
        digest = hashlib.sha256("|".join(str(part) for part in parts).encode()).hexdigest()
        return f"AUMEM_{digest[:12].upper()}"
