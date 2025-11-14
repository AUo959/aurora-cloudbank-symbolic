// Drift-Aware Symbolic Agent
// Monitors and adapts to symbolic state drift in real time.

export class DriftAwareAgent {
  constructor(id, memoryModule, driftThreshold = 0.02) {
    this.id = id;
    this.memory = memoryModule;
    this.driftThreshold = driftThreshold;
    this.state = 'stable';
  }

  assessDrift(currentSymbolicHash) {
    const anchorHash = this.memory.anchorHash();
    const drift = this.calculateDrift(anchorHash, currentSymbolicHash);
    this.state = drift > this.driftThreshold ? 'drifting' : 'stable';
    return drift;
  }

  calculateDrift(anchor, current) {
    if (typeof anchor !== 'string' || typeof current !== 'string') return 1;
    let mismatch = 0;
    for (let i = 0; i < Math.min(anchor.length, current.length); i++) {
      if (anchor[i] !== current[i]) mismatch++;
    }
    return mismatch / anchor.length;
  }

  respondToDrift(actionMap) {
    if (this.state === 'drifting' && actionMap.onDrift) {
      return actionMap.onDrift(this.id);
    } else if (this.state === 'stable' && actionMap.onStable) {
      return actionMap.onStable(this.id);
    }
    return null;
  }

  status() {
    return {
      id: this.id,
      state: this.state,
      anchor: this.memory.anchorHash(),
    };
  }
}

// Example:
// agent.assessDrift(system.symbolicHash());
// agent.respondToDrift({ onDrift: id => console.warn(`Agent ${id} drifting`) });