// zipcomm.js
// ZIPWIZ runtime transport helpers with diagnostics integration.

const crypto = require('crypto');
const zlib = require('zlib');
const { loadDiagnostics, saveDiagnostics } = require('./diagnostics');

const ZIPWIZ_PROTOCOL = 'ORION.L3.GOV.ZIPWIZ.PACKAGING.0001';
const HANDSHAKE_SEQUENCE = 'ZIPWIZ_BEACON -> ANCHOR_SYNC -> ETHICS_AUDIT -> DRIFT_VALIDATION';

function nowIso() {
  return new Date().toISOString();
}

function canonicalizeBundle(bundle) {
  if (Buffer.isBuffer(bundle)) {
    return bundle;
  }
  if (typeof bundle === 'string') {
    return Buffer.from(bundle, 'utf8');
  }
  if (bundle && typeof bundle === 'object') {
    return Buffer.from(JSON.stringify(bundle), 'utf8');
  }
  return Buffer.from(String(bundle ?? ''), 'utf8');
}

function sha256Hex(input) {
  return crypto.createHash('sha256').update(input).digest('hex');
}

function updateBundleDiagnostics(summary) {
  const diag = loadDiagnostics();
  diag.bundleCount = (diag.bundleCount || 0) + 1;
  diag.lastZipwizBundleAt = Date.now();
  diag.lastZipwizBundleSummary = summary;
  saveDiagnostics(diag);
}

function validateBundlePayload(payload) {
  if (payload === null || payload === undefined) {
    return { ok: false, reason: 'Bundle payload is null or undefined.' };
  }
  if (Buffer.isBuffer(payload)) {
    return { ok: true, reason: 'Buffer payload accepted.' };
  }
  if (typeof payload === 'string' && payload.trim()) {
    return { ok: true, reason: 'String payload accepted.' };
  }
  if (typeof payload === 'object') {
    return { ok: true, reason: 'Object payload accepted.' };
  }
  return { ok: false, reason: 'Unsupported bundle payload type.' };
}

function compressBundleDetailed(bundle, options = {}) {
  const validity = validateBundlePayload(bundle);
  if (!validity.ok) {
    throw new Error(validity.reason);
  }

  const input = canonicalizeBundle(bundle);
  const compressed = zlib.gzipSync(input);

  const summary = {
    protocol: ZIPWIZ_PROTOCOL,
    handshake: HANDSHAKE_SEQUENCE,
    createdAt: nowIso(),
    inputBytes: input.length,
    compressedBytes: compressed.length,
    ratio: input.length > 0 ? Number((compressed.length / input.length).toFixed(4)) : 1,
    inputSha256: sha256Hex(input),
    compressedSha256: sha256Hex(compressed),
    bundleId: options.bundleId || null,
    channel: options.channel || 'local',
  };

  updateBundleDiagnostics(summary);

  return {
    summary,
    payload: compressed.toString('base64'),
  };
}

function decompressBundle(base64Payload) {
  const encoded = String(base64Payload || '');
  if (!encoded.trim()) {
    throw new Error('Cannot decompress empty payload.');
  }
  const binary = Buffer.from(encoded, 'base64');
  return zlib.gunzipSync(binary).toString('utf8');
}

function buildBundleManifest(entries, options = {}) {
  const files = Array.isArray(entries) ? entries : [];
  const createdAt = nowIso();
  const bundleId = options.bundleId || `ZIPWIZ_${createdAt.replace(/[:.]/g, '')}`;

  return {
    bundle_id: bundleId,
    created_at: createdAt,
    protocol_ref: ZIPWIZ_PROTOCOL,
    ethics_protocol: 'Picard_Delta_3',
    anchor_seed: 'EOS_SEED_ORION',
    files,
  };
}

function compressBundle(bundle) {
  const details = compressBundleDetailed(bundle, { channel: 'command_node' });
  console.log(
    `ZIPWIZ.compressBundle protocol=${details.summary.protocol} bytes=${details.summary.inputBytes}->${details.summary.compressedBytes}`
  );
  return `Bundle ${typeof bundle === 'string' ? bundle : 'payload'} compressed.`;
}

module.exports = {
  ZIPWIZ_PROTOCOL,
  HANDSHAKE_SEQUENCE,
  validateBundlePayload,
  buildBundleManifest,
  compressBundleDetailed,
  decompressBundle,
  compressBundle,
};
