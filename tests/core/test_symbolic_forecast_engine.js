// Test Suite: Symbolic Forecast Engine
// Validates predictive symbolic state modeling and quantum-symbolic bridge integration

import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { SymbolicForecastEngine } from '../../core/symbolic-forecast-engine.js';

describe('SymbolicForecastEngine - Predictive State Modeling', () => {
  let engine;
  let anchorFn;
  let deltaFn;

  beforeEach(() => {
    anchorFn = (state) => `ANCHOR_${state.entropy || 0}`;
    deltaFn = (state) => ({
      entropy: (state.entropy || 0) + 0.1,
      step: (state.step || 0) + 1,
    });
    engine = new SymbolicForecastEngine(anchorFn, deltaFn);
  });

  it('should initialize with anchor and delta functions', () => {
    assert.equal(typeof engine.anchorFn, 'function');
    assert.equal(typeof engine.deltaFn, 'function');
    assert.deepEqual(engine.history, []);
  });

  it('should forecast future states with default horizon', () => {
    const currentState = { entropy: 0.5, step: 0 };
    const forecast = engine.forecast(currentState);
    assert.equal(forecast.length, 3); // default horizon
    assert.equal(forecast[0].step, 1);
    assert.equal(forecast[1].step, 2);
    assert.equal(forecast[2].step, 3);
  });

  it('should forecast with custom horizon', () => {
    const currentState = { entropy: 0.2 };
    const forecast = engine.forecast(currentState, 5);
    assert.equal(forecast.length, 5);
  });

  it('should apply delta function to evolve state', () => {
    const currentState = { entropy: 0.1, step: 0 };
    const forecast = engine.forecast(currentState, 3);
    // Each step should increase entropy by 0.1
    assert.ok(Math.abs(forecast[0].state.entropy - 0.2) < 0.01);
    assert.ok(Math.abs(forecast[1].state.entropy - 0.3) < 0.01);
    assert.ok(Math.abs(forecast[2].state.entropy - 0.4) < 0.01);
  });

  it('should generate anchor for each forecast step', () => {
    const currentState = { entropy: 0.5 };
    const forecast = engine.forecast(currentState, 2);
    assert.equal(forecast[0].anchor, 'ANCHOR_0.6');
    assert.ok(forecast[1].anchor.startsWith('ANCHOR_0.7')); // Float precision tolerance
  });

  it('should not mutate original state', () => {
    const originalState = { entropy: 1.0, immutable: true };
    const originalEntropy = originalState.entropy;
    engine.forecast(originalState, 3);
    assert.equal(originalState.entropy, originalEntropy);
    assert.ok(originalState.immutable);
  });

  it('should apply delta correctly with applyDelta method', () => {
    const state = { a: 1, b: 2 };
    const delta = { b: 20, c: 3 };
    const newState = engine.applyDelta(state, delta);
    assert.equal(newState.a, 1); // unchanged
    assert.equal(newState.b, 20); // updated
    assert.equal(newState.c, 3); // added
  });

  it('should preserve existing keys not in delta', () => {
    const state = { x: 10, y: 20, z: 30 };
    const delta = { y: 200 };
    const newState = engine.applyDelta(state, delta);
    assert.equal(newState.x, 10);
    assert.equal(newState.y, 200);
    assert.equal(newState.z, 30);
  });

  it('should record state in history', () => {
    const state = { test: 'data' };
    engine.record(state);
    assert.equal(engine.history.length, 1);
    assert.equal(engine.history[0].state, state);
    assert.ok(engine.history[0].time > 0);
  });

  it('should maintain history of multiple recordings', () => {
    engine.record({ step: 1 });
    engine.record({ step: 2 });
    engine.record({ step: 3 });
    assert.equal(engine.history.length, 3);
  });

  it('should return last forecast from history', () => {
    engine.record({ test: 'first' });
    engine.record({ test: 'last' });
    const last = engine.lastForecast();
    assert.equal(last.state.test, 'last');
  });

  it('should return undefined when history is empty', () => {
    const last = engine.lastForecast();
    assert.equal(last, undefined);
  });

  it('should handle complex delta functions', () => {
    const complexDelta = (state) => ({
      entropy: state.entropy * 1.1,
      confidence: (state.confidence || 1.0) * 0.9,
      iteration: (state.iteration || 0) + 1,
    });
    const complexEngine = new SymbolicForecastEngine(anchorFn, complexDelta);
    const forecast = complexEngine.forecast({ entropy: 1.0 }, 2);
    assert.ok(forecast[0].state.entropy > 1.0);
    assert.ok(forecast[0].state.confidence < 1.0);
  });

  it('should handle complex anchor functions', () => {
    const complexAnchor = (state) => {
      const hash = Math.floor(state.entropy * 1000);
      return `SYMBOLIC_ANCHOR_${hash}_T6`;
    };
    const complexEngine = new SymbolicForecastEngine(complexAnchor, deltaFn);
    const forecast = complexEngine.forecast({ entropy: 0.123 }, 1);
    assert.ok(forecast[0].anchor.includes('SYMBOLIC_ANCHOR'));
    assert.ok(forecast[0].anchor.includes('_T6'));
  });

  it('should project quantum-symbolic state evolution', () => {
    // Simulate quantum-symbolic bridge integration
    const quantumAnchor = (state) => {
      const phase = state.quantumPhase || 0;
      return `QUANTUM_ANCHOR_PHASE_${Math.floor(phase * 100)}`;
    };
    const quantumDelta = (state) => ({
      quantumPhase: (state.quantumPhase || 0) + 0.157, // quantum phase shift
      symbolicDrift: (state.symbolicDrift || 0) + 0.02,
      entanglement: (state.entanglement || 0.5) * 0.95,
    });
    const quantumEngine = new SymbolicForecastEngine(quantumAnchor, quantumDelta);
    const forecast = quantumEngine.forecast({ quantumPhase: 0.0 }, 3);
    
    assert.equal(forecast.length, 3);
    assert.ok(forecast[0].state.quantumPhase > 0);
    assert.ok(forecast[0].anchor.includes('QUANTUM_ANCHOR'));
  });

  it('should support multi-horizon symbolic prediction', () => {
    const initialState = { entropy: 0.1, drift: 0.0 };
    const shortHorizon = engine.forecast(initialState, 2);
    const longHorizon = engine.forecast(initialState, 10);
    
    assert.equal(shortHorizon.length, 2);
    assert.equal(longHorizon.length, 10);
    // Long horizon should have higher entropy
    assert.ok(longHorizon[9].state.entropy > shortHorizon[1].state.entropy);
  });

  it('should integrate with NEXUS enhancement modules', () => {
    // Simulate NEXUS integration pattern
    const nexusAnchor = (state) => `NEXUS_T6_ENTROPY_${state.entropy.toFixed(2)}`;
    const nexusDelta = (state) => ({
      entropy: state.entropy + 0.05,
      module: state.module || 'HARMION',
      layer: 'ENHANCEMENT',
    });
    const nexusEngine = new SymbolicForecastEngine(nexusAnchor, nexusDelta);
    const forecast = nexusEngine.forecast({ entropy: 0.15 }, 4);
    
    assert.equal(forecast.length, 4);
    assert.ok(forecast[0].anchor.includes('NEXUS_T6'));
    assert.equal(forecast[0].state.module, 'HARMION');
  });
});
