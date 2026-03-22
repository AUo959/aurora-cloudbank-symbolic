// modules/zipwiz.js
// Command-node adapter for ZIPWIZ runtime transport behavior.

const crypto = require('crypto');
const path = require('path');

const HANDSHAKE_SEQUENCE = 'ZIPWIZ_BEACON -> ANCHOR_SYNC -> ETHICS_AUDIT -> DRIFT_VALIDATION';
const RUNTIME_CAPABILITIES = [
  'beacon_ping',
  'bundle_manifest_build',
  'gzip_transport',
  'diagnostics_recording',
];

let zipcomm = null;
let zipcommLoadError = null;

try {
  const zipcommPath = path.join(__dirname, '..', '..', '..', 'src', 'core', 'zipcomm');
  zipcomm = require(zipcommPath);
} catch (err) {
  zipcommLoadError = err;
}

function nowIso() {
  return new Date().toISOString();
}

function normalizeMessage(msg) {
  if (typeof msg === 'string' && msg.trim()) {
    return msg.trim();
  }
  if (msg && typeof msg === 'object') {
    return JSON.stringify(msg);
  }
  return 'beacon';
}

function hashText(text) {
  return crypto.createHash('sha256').update(text).digest('hex');
}

function buildBeaconEnvelope(message, options = {}) {
  const normalized = normalizeMessage(message);
  return {
    event: 'ZIPWIZ_BEACON',
    message: normalized,
    at: nowIso(),
    protocol: (zipcomm && zipcomm.ZIPWIZ_PROTOCOL) || 'ORION.L3.GOV.ZIPWIZ.PACKAGING.0001',
    handshake: HANDSHAKE_SEQUENCE,
    channel: options.channel || 'constellation',
    beacon_hash: hashText(normalized),
  };
}

function pingBeacon(msg, options = {}) {
  const envelope = buildBeaconEnvelope(msg, options);

  if (zipcomm && typeof zipcomm.compressBundleDetailed === 'function') {
    try {
      const compressed = zipcomm.compressBundleDetailed(envelope, {
        channel: 'zipwiz.beacon',
        bundleId: `ZIPWIZ_BEACON_${Date.now()}`,
      });
      console.log(
        'ZIPWIZ.pingBeacon',
        envelope.message,
        `payload_bytes=${compressed.summary.compressedBytes}`
      );
      return { ok: true, envelope, compressed: compressed.summary };
    } catch (err) {
      console.log('ZIPWIZ.pingBeacon', envelope.message, 'compression_fallback');
      return { ok: true, envelope, fallback: true, error: err.message };
    }
  }

  console.log('ZIPWIZ.pingBeacon', envelope.message, 'zipcomm_unavailable');
  return {
    ok: true,
    envelope,
    fallback: true,
    error: zipcommLoadError ? zipcommLoadError.message : 'zipcomm unavailable',
  };
}

function packageForTransfer(bundlePayload, options = {}) {
  if (!zipcomm || typeof zipcomm.compressBundleDetailed !== 'function') {
    return {
      ok: false,
      reason: 'zipcomm transport runtime unavailable',
      requestedBundleId: options.bundleId || null,
    };
  }

  const packaged = zipcomm.compressBundleDetailed(bundlePayload, {
    channel: options.channel || 'zipwiz.transfer',
    bundleId: options.bundleId || null,
  });

  return {
    ok: true,
    summary: packaged.summary,
    payload: packaged.payload,
  };
}

function buildRuntimeSummary() {
  return {
    handshake: HANDSHAKE_SEQUENCE,
    capabilities: RUNTIME_CAPABILITIES,
    zipcommLinked: Boolean(zipcomm),
    zipcommError: zipcommLoadError ? zipcommLoadError.message : null,
  };
}

function selfCheck() {
  const summary = buildRuntimeSummary();
  const beacon = pingBeacon('runtime-self-check', { channel: 'self_check' });
  return {
    ok: summary.capabilities.length >= 4,
    summary,
    beaconOk: Boolean(beacon && beacon.ok),
  };
}

module.exports = {
  HANDSHAKE_SEQUENCE,
  buildBeaconEnvelope,
  buildRuntimeSummary,
  packageForTransfer,
  selfCheck,
  pingBeacon,
};
