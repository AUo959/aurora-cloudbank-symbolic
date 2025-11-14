// Resonance Token System
// Encapsulates symbolic memory threads into transmissible state bundles
// for integrity-checked inter-agent or inter-layer handoffs.

export class ResonanceToken {
  constructor(data, signature = null) {
    this.payload = data;
    this.signature = signature || this.generateSignature();
    this.timestamp = Date.now();
  }

  generateSignature() {
    const raw = JSON.stringify(this.payload) + this.timestamp;
    return btoa(unescape(encodeURIComponent(raw))).slice(0, 32); // naive hash-like
  }

  verify(incoming) {
    return incoming && incoming.signature === this.generateSignature();
  }

  relay(targetAgent) {
    if (!targetAgent || typeof targetAgent.receiveToken !== 'function') return false;
    return targetAgent.receiveToken(this);
  }

  toMeta() {
    return {
      tokenType: 'resonance',
      issuedAt: this.timestamp,
      summary: Object.keys(this.payload),
    };
  }
}

// Usage: const token = new ResonanceToken(memoryData).relay(agent);