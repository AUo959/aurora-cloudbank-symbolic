const { describe, test, expect, beforeEach } = require('@jest/globals');

jest.mock('../src/utils/aurora_logger.js', () => ({
  systemLogger: { info: jest.fn(), error: jest.fn() },
  bridgeLogger: { bridge: jest.fn(), error: jest.fn(), critical: jest.fn(), warn: jest.fn() },
  ethicsLogger: { info: jest.fn(), error: jest.fn(), warn: jest.fn() }
}));

const { EnhancedApiBridge } = require('../src/bridge/enhanced_api_bridge.js');

describe('EnhancedApiBridge relay constellation status', () => {
  let bridge;

  beforeEach(() => {
    bridge = new EnhancedApiBridge();
  });

  test('exposes relay tier naming and capsule roster', () => {
    const payloadHolder = {};

    bridge.getConstellationStatus({}, {
      json(payload) {
        payloadHolder.payload = payload;
      }
    });

    const { payload } = payloadHolder;
    expect(payload).toBeDefined();
    expect(payload.relay_tier.constellation).toBe('RELAY_TIER_CAPSULES');
    expect(payload.relay_tier.total_capsules).toBe(5);
    expect(Array.isArray(payload.relay_tier.capsules)).toBe(true);
    expect(payload.relay_tier.capsules).toHaveLength(5);
    const capsuleIds = payload.relay_tier.capsules.map(capsule => capsule.agentId);
    expect(capsuleIds).toEqual([
      'ARCHY',
      'OPPY',
      'LIORA',
      'STARLING_AU',
      'RIVERTHREAD_808'
    ]);
  });
});
