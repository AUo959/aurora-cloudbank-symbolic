/* global jest */
const { describe, test, expect, beforeEach } = require('@jest/globals');

let diagState;
const mockDiagnosticsModule = {
  loadDiagnostics: jest.fn(() => diagState),
  saveDiagnostics: jest.fn(updated => {
    diagState = { ...updated };
  }),
};

jest.mock('../src/core/diagnostics', () => mockDiagnosticsModule);

const { loadDiagnostics, saveDiagnostics } = require('../src/core/diagnostics');
const { runPASCycle } = require('../src/core/parasym_activation');

const createBaselineState = () => ({
  symbolicDrift: 0.5,
  lastAnchorSync: Date.now() - 11 * 60 * 1000,
  ethicsFlags: ['violation'],
  load: 10,
  commandCount: 0,
  glyphCount: 0,
  bundleCount: 0,
});

describe('runPASCycle', () => {
  beforeEach(() => {
    diagState = createBaselineState();
    loadDiagnostics.mockClear();
    saveDiagnostics.mockClear();
  });

  test('realigns drift, clears alerts, and throttles load', () => {
    loadDiagnostics.mockImplementation(() => diagState);

    runPASCycle();

    expect(loadDiagnostics).toHaveBeenCalled();
    expect(saveDiagnostics).toHaveBeenCalledWith(expect.objectContaining({}));
    expect(diagState.symbolicDrift).toBeLessThanOrEqual(0.5);
    expect(diagState.ethicsFlags).toHaveLength(0);
    expect(Date.now() - diagState.lastAnchorSync).toBeLessThan(2_000);
    expect(diagState.load).toBeLessThanOrEqual(9);
  });
});
