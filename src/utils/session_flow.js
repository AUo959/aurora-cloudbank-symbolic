import { createHash, randomUUID } from 'node:crypto';

export const defaultRedaction = {
  enabled: true,
  strategy: 'mask',
  mask: '***',
  fields: ['email', 'phone', 'full_name', 'account_number'],
  anchor_seed: 'T1-SESSION-FLOW-START'
};

const piiFields = new Set(defaultRedaction.fields);

function maskState(state, redaction = defaultRedaction) {
  if (!redaction.enabled) {
    return { ...state, pii_redaction: redaction };
  }

  const masked = {};
  for (const [key, value] of Object.entries(state)) {
    if (piiFields.has(key)) {
      masked[key] = redaction.mask;
    } else {
      masked[key] = value;
    }
  }
  masked.pii_redaction = { ...defaultRedaction, ...redaction };
  return masked;
}

export function createSession(state = {}) {
  const sessionId = randomUUID();
  const timestamp = new Date().toISOString();
  const metadataAnchor = {
    anchor_seed: state.anchor_seed || defaultRedaction.anchor_seed,
    context_tag: 'session_flow_bridge'
  };

  const sessionState = {
    ...maskState(state),
    metadata_anchor: metadataAnchor
  };

  return {
    sessionId,
    state: sessionState,
    createdAt: timestamp,
    lastAccessed: timestamp,
    metadata_anchor: metadataAnchor
  };
}

export function runFlow(session, steps = []) {
  const executionTrace = steps.map(step => ({
    ...step,
    anchor_seed: session.metadata_anchor.anchor_seed,
    status: 'completed'
  }));

  return {
    sessionId: session.sessionId,
    anchor_seed: session.metadata_anchor.anchor_seed,
    pii_redaction: session.state.pii_redaction,
    steps: executionTrace,
    continuity_seal: createHash('sha256')
      .update(`${session.sessionId}:${session.metadata_anchor.anchor_seed}`)
      .digest('hex')
      .slice(0, 16)
  };
}

export function shareSession(session) {
  const shareToken = createHash('sha256')
    .update(`${session.sessionId}:${session.metadata_anchor.anchor_seed}`)
    .digest('hex')
    .slice(0, 16);

  return {
    sessionId: session.sessionId,
    shareToken,
    state: maskState(session.state),
    metadata_anchor: session.metadata_anchor
  };
}

export function forkSession(session, shareToken) {
  if (!shareToken) {
    throw new Error('shareToken is required to fork a session');
  }

  const forked = createSession({
    ...session.state,
    forked_from: session.sessionId,
    share_token: shareToken,
    anchor_seed: session.metadata_anchor.anchor_seed
  });

  return {
    ...forked,
    forked_from: session.sessionId,
    share_token: shareToken
  };
}
