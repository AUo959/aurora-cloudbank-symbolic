/**
 * Aurora Constellation — Shared Type Definitions (TypeScript)
 *
 * Interfaces and Zod schemas matching all constellation contract JSON schemas.
 * Ref: Aurora Constellation Architecture Proposal v1.0.0
 */

import { z } from "zod";

// ---------------------------------------------------------------------------
// Enums / Literals
// ---------------------------------------------------------------------------

export const ConstellationNodeValues = [
  "CONSTELLATION-PRIME",
  "AURORA-RUNTIME",
  "QUANTUM-VAULT",
  "QGIA-CORPUS",
  "QGIA-SPINE",
  "ZIPWIZ-ENGINE",
] as const;
export type ConstellationNode = (typeof ConstellationNodeValues)[number];

export const EventTypeValues = [
  "qgia.forecast.completed",
  "qgia.forecast.requested",
  "zipwiz.archive.processed",
  "aurora.drift.detected",
  "qgia.knowledge.updated",
  "constellation.health.check",
  "constellation.health.response",
  "constellation.manifest.drift",
] as const;
export type EventType = (typeof EventTypeValues)[number];

export const NodeStatusValues = [
  "operational",
  "degraded",
  "offline",
  "unknown",
] as const;
export type NodeStatus = (typeof NodeStatusValues)[number];

export const DomainValues = [
  "nuclear",
  "cyber",
  "economic",
  "military",
  "political",
  "environmental",
  "social",
  "technological",
  "hybrid",
] as const;
export type Domain = (typeof DomainValues)[number];

export const PriorityValues = [
  "critical",
  "high",
  "standard",
  "low",
] as const;
export type Priority = (typeof PriorityValues)[number];

export const ForecastTierLevelValues = ["I", "II", "III"] as const;
export type ForecastTierLevel = (typeof ForecastTierLevelValues)[number];

// ---------------------------------------------------------------------------
// Interfaces — Provenance
// ---------------------------------------------------------------------------

export interface Provenance {
  caelion_anchor?: string;
  charter: string;
  l3_compliance: boolean;
}

// ---------------------------------------------------------------------------
// Interfaces — Forecast
// ---------------------------------------------------------------------------

export interface Requestor {
  node?: string;
  agent?: string;
}

export interface ForecastParameters {
  confidence_threshold?: number;
  max_analysts?: number;
  challenge_enabled?: boolean;
  echo_chamber_detection?: boolean;
}

export interface ForecastRequest {
  scenario_id: string;
  scenario_title: string;
  description: string;
  domain: Domain;
  time_horizon_days: number;
  priority?: Priority;
  requestor?: Requestor;
  parameters?: ForecastParameters;
  knowledge_refs?: string[];
  symbolic_tag?: string;
}

export interface EvidenceFragment {
  source?: string;
  weight?: number;
  knowledge_ref?: string;
}

export interface ForecastTier {
  tier: ForecastTierLevel;
  outcome: string;
  probability: number;
  confidence: number;
  evidence_fragments?: EvidenceFragment[];
}

export interface ForecastMetadata {
  analysts_activated?: number;
  echo_chambers_detected?: number;
  challenge_rounds?: number;
  processing_time_ms?: number;
  timestamp?: string;
  symbolic_tag?: string;
}

export interface ForecastResult {
  forecast_id: string;
  scenario_id: string;
  tiers: ForecastTier[];
  metadata: ForecastMetadata;
  provenance?: Provenance;
}

// ---------------------------------------------------------------------------
// Interfaces — Constellation Event
// ---------------------------------------------------------------------------

export interface ConstellationEvent {
  event_type: EventType;
  source_node: ConstellationNode;
  timestamp: string;
  payload: Record<string, unknown>;
  correlation_id?: string;
  provenance?: Provenance;
}

// ---------------------------------------------------------------------------
// Interfaces — Knowledge Index
// ---------------------------------------------------------------------------

export interface KnowledgeDocument {
  id: string;
  title: string;
  domain: string;
  path: string;
  checksum: string;
  word_count?: number;
  last_modified?: string;
  tags?: string[];
  summary?: string;
}

export interface KnowledgeIndex {
  version: string;
  source_repo: string;
  generated_at: string;
  documents: KnowledgeDocument[];
}

// ---------------------------------------------------------------------------
// Interfaces — Health
// ---------------------------------------------------------------------------

export interface HealthChecks {
  api_reachable?: boolean;
  manifest_valid?: boolean;
  contract_compatible?: boolean;
  last_sync_age_hours?: number;
}

export interface NodeHealth {
  node: string;
  status: NodeStatus;
  timestamp: string;
  manifest_version: string;
  constellation_version?: string;
  last_event?: string;
  checks?: HealthChecks;
}

// ---------------------------------------------------------------------------
// Zod Schemas — runtime validation
// ---------------------------------------------------------------------------

export const ProvenanceSchema = z.object({
  caelion_anchor: z.string().optional(),
  charter: z.string(),
  l3_compliance: z.boolean(),
});

export const RequestorSchema = z.object({
  node: z.string().optional(),
  agent: z.string().optional(),
});

export const ForecastParametersSchema = z.object({
  confidence_threshold: z.number().min(0).max(1).optional(),
  max_analysts: z.number().int().min(10).max(551).optional(),
  challenge_enabled: z.boolean().optional(),
  echo_chamber_detection: z.boolean().optional(),
});

export const ForecastRequestSchema = z.object({
  scenario_id: z.string().regex(/^SCN-[A-Z0-9-]+$/),
  scenario_title: z.string().max(200),
  description: z.string(),
  domain: z.enum(DomainValues),
  time_horizon_days: z.number().int().min(1).max(3650),
  priority: z.enum(PriorityValues).optional(),
  requestor: RequestorSchema.optional(),
  parameters: ForecastParametersSchema.optional(),
  knowledge_refs: z.array(z.string()).optional(),
  symbolic_tag: z.string().regex(/^s\.tag::.+/).optional(),
});

export const EvidenceFragmentSchema = z.object({
  source: z.string().optional(),
  weight: z.number().optional(),
  knowledge_ref: z.string().optional(),
});

export const ForecastTierSchema = z.object({
  tier: z.enum(ForecastTierLevelValues),
  outcome: z.string(),
  probability: z.number().min(0).max(1),
  confidence: z.number().min(0).max(1),
  evidence_fragments: z.array(EvidenceFragmentSchema).optional(),
});

export const ForecastMetadataSchema = z.object({
  analysts_activated: z.number().int().optional(),
  echo_chambers_detected: z.number().int().optional(),
  challenge_rounds: z.number().int().optional(),
  processing_time_ms: z.number().optional(),
  timestamp: z.string().datetime().optional(),
  symbolic_tag: z.string().optional(),
});

export const ForecastResultSchema = z.object({
  forecast_id: z.string().regex(/^FCST-[A-Z0-9-]+$/),
  scenario_id: z.string(),
  tiers: z.array(ForecastTierSchema),
  metadata: ForecastMetadataSchema,
  provenance: ProvenanceSchema.optional(),
});

export const ConstellationEventSchema = z.object({
  event_type: z.enum(EventTypeValues),
  source_node: z.enum(ConstellationNodeValues),
  timestamp: z.string().datetime(),
  payload: z.record(z.unknown()),
  correlation_id: z.string().uuid().optional(),
  provenance: ProvenanceSchema.optional(),
});

export const KnowledgeDocumentSchema = z.object({
  id: z.string(),
  title: z.string(),
  domain: z.string(),
  path: z.string(),
  checksum: z.string(),
  word_count: z.number().int().optional(),
  last_modified: z.string().datetime().optional(),
  tags: z.array(z.string()).optional(),
  summary: z.string().optional(),
});

export const KnowledgeIndexSchema = z.object({
  version: z.string(),
  source_repo: z.string(),
  generated_at: z.string().datetime(),
  documents: z.array(KnowledgeDocumentSchema),
});

export const HealthChecksSchema = z.object({
  api_reachable: z.boolean().optional(),
  manifest_valid: z.boolean().optional(),
  contract_compatible: z.boolean().optional(),
  last_sync_age_hours: z.number().optional(),
});

export const NodeHealthSchema = z.object({
  node: z.string(),
  status: z.enum(NodeStatusValues),
  timestamp: z.string().datetime(),
  manifest_version: z.string(),
  constellation_version: z.string().optional(),
  last_event: z.string().datetime().optional(),
  checks: HealthChecksSchema.optional(),
});
