// modules/threadcore.js
// Payload-driven ThreadCore adapter for the command node runtime.

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const PAYLOAD_PATH = path.join(
  __dirname,
  '..',
  '..',
  '..',
  'modules',
  'reflective_autonomy',
  'threadcore_payloads',
  'threadcore_v3.5.1_macroready.json'
);
const DRIFTPULSE_PATH = path.join(
  __dirname,
  '..',
  '..',
  '..',
  'modules',
  'reflective_autonomy',
  'threadcore_payloads',
  'threadcore_v3.5.1_driftpulse.json'
);

const EMOJI_MAP = {
  memory: ['🧠', '🔮'],
  ethics: ['⚖️', '🛡️'],
  relay: ['🔄', '🌐'],
  planning: ['🗂️', '📝'],
  data: ['📊', '💾'],
  drift: ['🌊', '🌀'],
  simulation: ['🪐', '🛰️'],
  node: ['🧭', '🔗'],
  ai: ['🤖', '🧬'],
  archive: ['📦', '🗃️'],
  security: ['🔐', '🔒'],
  sovereignty: ['🔐', '🧬'],
  identity: ['🧬', '🧑‍💻'],
  default: ['🌐', '✨'],
};

function readJson(filePath, fallback) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    return fallback;
  }
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function sortForHash(value) {
  if (Array.isArray(value)) {
    return value.map(sortForHash);
  }
  if (value && typeof value === 'object') {
    return Object.keys(value)
      .sort()
      .reduce((acc, key) => {
        acc[key] = sortForHash(value[key]);
        return acc;
      }, {});
  }
  return value;
}

function stableStringify(value) {
  return JSON.stringify(sortForHash(value));
}

function nowIso() {
  return new Date().toISOString();
}

function capitalize(value) {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : '';
}

function capitalizeWords(value, maxWords = 4) {
  return (value || '')
    .split(/[\s-_]+/)
    .filter(Boolean)
    .slice(0, maxWords)
    .map(capitalize)
    .join(' ');
}

function normalizeMetadata(metadata = {}) {
  const normalized = { ...metadata };

  if (normalized.symbolic_tag && !normalized.topic) {
    normalized.topic = String(normalized.symbolic_tag)
      .split('::')
      .pop()
      .replace(/_/g, ' ');
  }
  if (normalized.anchor_code && !normalized.purpose) {
    normalized.purpose = String(normalized.anchor_code)
      .split('::')
      .pop()
      .replace(/_/g, ' ');
  }
  if (normalized.terminal_id && !normalized.node) {
    normalized.node = String(normalized.terminal_id).split('.')[0].toUpperCase();
  }
  if (normalized.threadcore_version && !normalized.version) {
    normalized.version = normalized.threadcore_version;
  }

  return normalized;
}

function shortHash(metadata = {}) {
  return crypto
    .createHash('sha256')
    .update(stableStringify(metadata))
    .digest('hex')
    .slice(0, 6);
}

function extractThemeEmojis(metadata = {}) {
  const bag = [
    metadata.topic || '',
    metadata.purpose || '',
    metadata.role || '',
    metadata.symbolic_statement || '',
    Array.isArray(metadata.glyph_agents) ? metadata.glyph_agents.join(' ') : metadata.glyph_agents || '',
  ]
    .join(' ')
    .toLowerCase();

  for (const [key, emojis] of Object.entries(EMOJI_MAP)) {
    if (bag.includes(key)) {
      return emojis;
    }
  }
  if (bag.includes('ethics')) {
    return EMOJI_MAP.ethics;
  }
  return EMOJI_MAP.default;
}

function extractShortTitle(metadata = {}) {
  if (metadata.topic) {
    return capitalizeWords(metadata.topic, 4);
  }
  if (metadata.purpose) {
    return capitalizeWords(metadata.purpose, 4);
  }
  if (metadata.symbolic_statement) {
    return capitalizeWords(metadata.symbolic_statement, 4);
  }
  if (metadata.node) {
    return `${capitalizeWords(metadata.node, 3)} Node`;
  }
  if (metadata.role) {
    return capitalizeWords(metadata.role, 4);
  }
  return 'Aurora Capsule';
}

function coalesceHash(metadata = {}) {
  const seed =
    metadata.anchor_hash ||
    metadata.thread_hash ||
    metadata.hash ||
    (metadata.capsule_id ? String(metadata.capsule_id).replace(/[^\da-z]/gi, '') : '');

  if (seed && seed.length >= 5) {
    return seed.slice(0, 6);
  }
  return shortHash(metadata);
}

function enforceMaxLength(value, maxLength = 60) {
  if (!maxLength || value.length <= maxLength) {
    return value;
  }

  let trimmed = value;
  for (const marker of [' – ', ' — ', ' · ']) {
    const index = trimmed.lastIndexOf(marker);
    if (index > -1 && index >= maxLength - 12) {
      trimmed = trimmed.slice(0, index);
      break;
    }
  }

  if (trimmed.length > maxLength) {
    trimmed = `${trimmed.slice(0, maxLength - 1)}…`;
  }
  return trimmed;
}

function composeAlias({ emoji, title, node, hash, version, maxLength }) {
  const nodeText = node ? ` (${capitalize(node)})` : '';
  const suffix = ` — #${hash} · ${version}`;
  let alias = `${emoji} ${title}${nodeText}${suffix}`;

  if (alias.length <= maxLength) {
    return alias;
  }

  const minimumTitle = 'Aurora';
  const fixedWithoutTitle = `${emoji} ${nodeText}${suffix}`;
  const availableForTitle = maxLength - fixedWithoutTitle.length;

  if (availableForTitle > minimumTitle.length) {
    alias = `${emoji} ${enforceMaxLength(title, availableForTitle)}${nodeText}${suffix}`;
  }

  if (alias.length <= maxLength) {
    return alias;
  }

  if (nodeText) {
    alias = `${emoji} ${enforceMaxLength(title, maxLength - `${emoji} ${suffix}`.length)}${suffix}`;
  }

  return enforceMaxLength(alias, maxLength);
}

function resolveThreadId(metadata = {}, prefix = 'thread') {
  if (metadata.thread_id) {
    return String(metadata.thread_id);
  }
  if (metadata.capsule_id) {
    return String(metadata.capsule_id);
  }

  const identity = {
    node: metadata.node || '',
    topic: metadata.topic || '',
    role: metadata.role || '',
    anchor_hash: metadata.anchor_hash || '',
    prefix,
  };
  return `${prefix}_${shortHash(identity)}`;
}

function buildRuntimeState() {
  const config = readJson(PAYLOAD_PATH, {
    augmentation: 'THREADCORE',
    version: 'v3.5.1_macroready',
    role: 'Symbolic Constellation Loom + Reflection Module',
    anchor_seed: 'EOS_SEED_ORION',
    ethics_protocol: 'Picard_Delta_3',
    symbolic_drift_max: 0.2,
    sidebar_alias_template: '🧭 [Functional Cortex Node] (v3.5.1 – Constellation Alignment)',
    threadreflect: {
      snapshot_fields: {
        context_summary: true,
        last_active_command: true,
        unutilized_logic: true,
        symbolic_drift: true,
        anchor_hash: true,
        glyph_sync_status: true,
        timestamp: true,
      },
      driftlog: {
        active: true,
        auto_return_suggestion: true,
        message: '⚠️ DRIFT detected: Please return-to-anchor before further capsule expansion.',
      },
    },
    beacon_contact: {
      activate: true,
      targets: ['ZIPWIZ', 'PATCHWEAVER', 'CONSTELLATION_CORE'],
    },
    glyph_agents: [],
  });
  const driftpulse = readJson(DRIFTPULSE_PATH, {
    capsule_id: 'THREADCORE_DRIFTPULSE_V3_5_1',
    beacon_contact: { channel: 'ZIPWIZ', status: 'synchronized' },
  });

  return {
    config,
    driftpulse,
    initialized: false,
    initializedAt: null,
    seed: config.anchor_seed,
    ethics: config.ethics_protocol,
    glyphAgents: clone(config.glyph_agents || []),
    driftDelta: 0.0,
    lastCommand: null,
    threads: new Map(),
    aliasByThread: new Map(),
    usedAliases: new Set(),
  };
}

let runtime = buildRuntimeState();

function releaseAlias(threadId) {
  const previousAlias = runtime.aliasByThread.get(threadId);
  if (previousAlias) {
    runtime.usedAliases.delete(previousAlias);
    runtime.aliasByThread.delete(threadId);
  }
}

function rememberAlias(threadId, alias) {
  runtime.usedAliases.add(alias);
  runtime.aliasByThread.set(threadId, alias);
}

function ensureUniqueAlias(alias) {
  let candidate = alias;
  let suffix = 2;
  while (runtime.usedAliases.has(candidate)) {
    candidate = `${alias} #${suffix}`;
    suffix += 1;
  }
  return candidate;
}

function generateSidebarAlias(metadata = {}, options = {}) {
  const normalized = normalizeMetadata(metadata);
  const [emoji] = extractThemeEmojis(normalized);
  const title = extractShortTitle(normalized);
  const node = normalized.node || '';
  const version = normalized.version || runtime.config.version || 'v3.5.1';
  const hash = coalesceHash(normalized);
  let alias = composeAlias({
    emoji,
    title,
    node,
    hash,
    version,
    maxLength: runtime.config.alias_generation?.max_length || 60,
  });
  if (!title || alias.length < 8) {
    alias = runtime.config.sidebar_alias_template || '🧭 [Functional Cortex Node] (v3.5.1 – Constellation Alignment)';
  }

  if (options.threadId) {
    releaseAlias(options.threadId);
  }
  alias = ensureUniqueAlias(alias);
  if (options.threadId) {
    rememberAlias(options.threadId, alias);
  }

  return alias;
}

function applyDrift(perturbation = 0.0) {
  const perturb = Number(perturbation) || 0.0;
  runtime.driftDelta = Math.max(0.0, (runtime.driftDelta + perturb) * 0.95);
  const exceedsThreshold = runtime.driftDelta > Number(runtime.config.symbolic_drift_max || 0.2);

  return {
    drift_delta: runtime.driftDelta,
    exceeds_threshold: exceedsThreshold,
    drift_alert: exceedsThreshold ? runtime.config.threadreflect?.driftlog?.message || null : null,
    escalation_targets: exceedsThreshold
      ? runtime.config.beacon_contact?.targets || [runtime.driftpulse?.beacon_contact?.channel].filter(Boolean)
      : [],
  };
}

function buildReflectSnapshot(metadata = {}, options = {}) {
  const fields = runtime.config.threadreflect?.snapshot_fields || {};
  const normalized = normalizeMetadata(metadata);
  const snapshot = {
    thread_id: options.threadId || resolveThreadId(normalized),
    sidebar_alias: options.alias || null,
    capsule_id: normalized.capsule_id || null,
    anchor_seed: runtime.seed,
    ethics_protocol: runtime.ethics,
    glyph_agents: clone(runtime.glyphAgents),
  };

  if (fields.context_summary) {
    snapshot.context_summary =
      normalized.context_summary ||
      normalized.summary ||
      normalized.topic ||
      normalized.purpose ||
      normalized.role ||
      'ThreadCore reflect snapshot';
  }
  if (fields.last_active_command) {
    snapshot.last_active_command = runtime.lastCommand;
  }
  if (fields.unutilized_logic) {
    snapshot.unutilized_logic = normalized.unutilized_logic || [];
  }
  if (fields.symbolic_drift) {
    snapshot.symbolic_drift = runtime.driftDelta;
  }
  if (fields.anchor_hash) {
    snapshot.anchor_hash = normalized.anchor_hash || coalesceHash(normalized);
  }
  if (fields.glyph_sync_status) {
    snapshot.glyph_sync_status =
      runtime.driftDelta > Number(runtime.config.symbolic_drift_max || 0.2) ? 'drift-alert' : 'aligned';
  }
  if (fields.timestamp) {
    snapshot.timestamp = nowIso();
  }

  return snapshot;
}

function buildRuntimeSummary() {
  return {
    initialized: runtime.initialized,
    initialized_at: runtime.initializedAt,
    anchor_seed: runtime.seed,
    ethics_protocol: runtime.ethics,
    threadcore_version: runtime.config.version,
    drift_delta: runtime.driftDelta,
    tracked_threads: runtime.threads.size,
    beacon_targets: runtime.config.beacon_contact?.targets || [],
  };
}

function init(options = {}) {
  runtime.initialized = true;
  runtime.initializedAt = nowIso();
  runtime.seed = options.seed || runtime.config.anchor_seed;
  runtime.ethics = options.ethics || runtime.config.ethics_protocol;
  runtime.glyphAgents = clone(options.glyphAgents || runtime.config.glyph_agents || []);
  runtime.lastCommand = 'init';

  const summary = buildRuntimeSummary();
  console.log('THREADCORE.init', summary);
  return summary;
}

function seed(payload = {}) {
  const metadata = normalizeMetadata(payload.metadata || payload);
  const threadId = resolveThreadId(metadata, 'seed');
  const alias = generateSidebarAlias(metadata, { threadId });
  const entry = {
    thread_id: threadId,
    capsule_id: metadata.capsule_id || null,
    sidebar_alias: alias,
    metadata,
    created_at: nowIso(),
    updated_at: nowIso(),
    anchor_seed: runtime.seed,
    ethics_protocol: runtime.ethics,
    reflect_snapshot: buildReflectSnapshot(metadata, { threadId, alias }),
  };

  runtime.lastCommand = 'seed';
  runtime.threads.set(threadId, entry);
  console.log('THREADCORE.seed', { thread_id: threadId, sidebar_alias: alias });
  return clone(entry);
}

function update(payload = {}) {
  const metadata = normalizeMetadata(payload.metadata || payload);
  const threadId = payload.thread_id || resolveThreadId(metadata, 'update');
  const current = runtime.threads.get(threadId) || {
    thread_id: threadId,
    created_at: nowIso(),
    metadata: {},
  };
  const mergedMetadata = { ...current.metadata, ...metadata };
  const alias = generateSidebarAlias(mergedMetadata, { threadId });
  const drift = applyDrift(
    payload.perturb ?? payload.symbolic_drift ?? payload.drift_delta ?? mergedMetadata.symbolic_drift ?? 0.0
  );

  const entry = {
    ...current,
    capsule_id: mergedMetadata.capsule_id || current.capsule_id || null,
    sidebar_alias: alias,
    metadata: mergedMetadata,
    updated_at: nowIso(),
    anchor_seed: runtime.seed,
    ethics_protocol: runtime.ethics,
    drift_state: drift,
    reflect_snapshot: buildReflectSnapshot(mergedMetadata, { threadId, alias }),
  };

  runtime.lastCommand = 'update';
  runtime.threads.set(threadId, entry);
  console.log('THREADCORE.update', {
    thread_id: threadId,
    sidebar_alias: alias,
    drift_delta: drift.drift_delta,
  });
  return clone(entry);
}

function reflect(payload = {}) {
  const requestedId = typeof payload === 'string' ? payload : payload.thread_id;
  runtime.lastCommand = 'reflect';

  if (requestedId) {
    const entry = runtime.threads.get(requestedId);
    const metadata = entry ? entry.metadata : payload.metadata || {};
    const alias = entry ? entry.sidebar_alias : null;
    const snapshot = buildReflectSnapshot(metadata, { threadId: requestedId, alias });
    console.log('THREADCORE.reflect', { thread_id: requestedId });
    return {
      ...snapshot,
      runtime: buildRuntimeSummary(),
    };
  }

  const snapshots = Array.from(runtime.threads.values()).map((entry) =>
    buildReflectSnapshot(entry.metadata, { threadId: entry.thread_id, alias: entry.sidebar_alias })
  );

  const response = {
    runtime: buildRuntimeSummary(),
    driftpulse_profile: runtime.driftpulse.capsule_id || null,
    active_threads: snapshots,
  };
  console.log('THREADCORE.reflect', { tracked_threads: snapshots.length });
  return response;
}

function resetRuntime() {
  runtime = buildRuntimeState();
  return buildRuntimeSummary();
}

module.exports = {
  init,
  seed,
  update,
  reflect,
  __private: {
    buildReflectSnapshot,
    buildRuntimeSummary,
    generateSidebarAlias,
    normalizeMetadata,
    resetRuntime,
    getRuntimeState: () => runtime,
  },
};
