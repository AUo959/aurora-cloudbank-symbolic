const THREADCORE = require('../services/command_node/modules/threadcore');

describe('THREADCORE command-node adapter', () => {
  beforeEach(() => {
    THREADCORE.__private.resetRuntime();
  });

  test('initializes from canonical payload defaults', () => {
    const summary = THREADCORE.init({});

    expect(summary.anchor_seed).toBe('EOS_SEED_ORION');
    expect(summary.ethics_protocol).toBe('Picard_Delta_3');
    expect(summary.threadcore_version).toBe('v3.5.1_macroready');
    expect(summary.initialized).toBe(true);
  });

  test('seeds a thread with deterministic alias generation', () => {
    THREADCORE.init({});

    const seeded = THREADCORE.seed({
      capsule_id: 'THREAD_ALPHA',
      topic: 'memory drift harmonization',
      node: 'ARCHY',
      anchor_hash: 'a9f4bdc20e',
    });

    expect(seeded.thread_id).toBe('THREAD_ALPHA');
    expect(seeded.sidebar_alias).toContain('Memory Drift');
    expect(seeded.sidebar_alias).toContain('#a9f4bd');
    expect(seeded.sidebar_alias.length).toBeLessThanOrEqual(60);
    expect(seeded.reflect_snapshot.anchor_seed).toBe('EOS_SEED_ORION');
  });

  test('updates drift state and exposes escalation targets when threshold is exceeded', () => {
    THREADCORE.init({});
    THREADCORE.seed({ capsule_id: 'THREAD_BETA', topic: 'relay sync' });

    const updated = THREADCORE.update({
      thread_id: 'THREAD_BETA',
      symbolic_drift: 0.25,
      context_summary: 'Drift event detected',
    });

    expect(updated.drift_state.exceeds_threshold).toBe(true);
    expect(updated.drift_state.escalation_targets).toContain('ZIPWIZ');
    expect(updated.reflect_snapshot.context_summary).toBe('Drift event detected');
  });

  test('upconverts legacy metadata into aliasable fields', () => {
    THREADCORE.init({});

    const seeded = THREADCORE.seed({
      capsule_id: 'THREAD_GAMMA',
      symbolic_tag: 'THREADCORE::macro_drift_bridge',
      terminal_id: 'riverthread.808',
      threadcore_version: 'v3.6_macrodrift',
    });

    expect(seeded.metadata.topic).toBe('macro drift bridge');
    expect(seeded.metadata.node).toBe('RIVERTHREAD');
    expect(seeded.sidebar_alias).toContain('Macro Drift');
    expect(seeded.sidebar_alias).toContain('v3.6_macrodrift');
    expect(seeded.sidebar_alias.length).toBeLessThanOrEqual(60);
  });
});
