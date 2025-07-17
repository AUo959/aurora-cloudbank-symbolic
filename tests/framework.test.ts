/**
 * Test suite for Aurora/GUMAS Symbolic Simulation Framework
 * Operator: AUo959
 */

import { SymbolicSimulation } from '../src/core/SymbolicSimulation';
import { MemorySealer } from '../src/sealing/MemorySealer';
import { DLPTagger } from '../src/dlp/DLPTagger';
import { ReliquaryIndexer } from '../src/reliquary/ReliquaryIndexer';
import { SimulationSnapshotter } from '../src/snapshots/SimulationSnapshotter';
import { ExportHelper } from '../src/exports/ExportHelper';

describe('Aurora/GUMAS Symbolic Simulation Framework', () => {
  
  describe('SymbolicSimulation', () => {
    let simulation: SymbolicSimulation;
    
    beforeEach(() => {
      simulation = new SymbolicSimulation();
    });
    
    test('should create T1 anchor', () => {
      const anchor = simulation.createAnchor('T1', { test: true });
      expect(anchor.type).toBe('T1');
      expect(anchor.state).toBe('stable');
      expect(anchor.metadata.operator).toBe('AUo959');
    });
    
    test('should transition anchor states', () => {
      const anchor = simulation.createAnchor('SRB');
      const success = simulation.transitionAnchorState(anchor.id, 'evolving');
      expect(success).toBe(true);
      
      const updatedAnchor = simulation.exportState().anchors.get(anchor.id);
      expect(updatedAnchor?.state).toBe('evolving');
    });
    
    test('should create thread lineage', () => {
      const anchor = simulation.createAnchor('EOS_SEED');
      const thread = simulation.createThread(anchor.id);
      expect(thread.createdBy).toBe('AUo959');
      expect(thread.anchor.id).toBe(anchor.id);
    });
    
    test('should add cross-references', () => {
      const anchor1 = simulation.createAnchor('T1');
      const anchor2 = simulation.createAnchor('SRB');
      
      simulation.addCrossReference(anchor1.id, anchor2.id, 'supersedes');
      const relationships = simulation.getAnchorRelationships(anchor1.id);
      
      expect(relationships).toHaveLength(1);
      expect(relationships[0].relationship).toBe('supersedes');
    });
  });
  
  describe('MemorySealer', () => {
    let sealer: MemorySealer;
    
    beforeEach(() => {
      sealer = new MemorySealer();
    });
    
    test('should seal and rehydrate memory', async () => {
      const testData = { message: 'Aurora test data', operator: 'AUo959' };
      const sealed = await sealer.sealMemory(testData);
      
      expect(sealed.operatorId).toBe('AUo959');
      expect(sealed.data).toBeTruthy();
      
      const restored = await sealer.rehydrateMemory(sealed);
      expect(restored).toEqual(testData);
    });
    
    test('should create and validate entropy pools', async () => {
      const pool = sealer.createEntropyPool('test_pool');
      expect(pool.operatorId).toBe('AUo959');
      
      await sealer.addToEntropyPool('test_pool', 'test data');
      const isValid = sealer.validateEntropyPool('test_pool');
      expect(isValid).toBe(true);
    });
  });
  
  describe('DLPTagger', () => {
    let tagger: DLPTagger;
    
    beforeEach(() => {
      tagger = new DLPTagger();
    });
    
    test('should create DLP tags', () => {
      const tag = tagger.createTag('item1', 'confidential', 9);
      expect(tag.classification).toBe('confidential');
      expect(tag.sensitivity).toBe(9);
      expect(tag.operatorId).toBe('AUo959');
    });
    
    test('should check access permissions', () => {
      tagger.createTag('item1', 'internal', 5);
      const hasAccess = tagger.checkAccess('item1', 'internal', 'read');
      expect(hasAccess).toBe(true);
      
      const noAccess = tagger.checkAccess('item1', 'public', 'write');
      expect(noAccess).toBe(false);
    });
    
    test('should generate compliance reports', () => {
      tagger.createTag('item1', 'public', 3);
      tagger.createTag('item2', 'restricted', 7);
      
      const report = tagger.generateComplianceReport(
        new Date(Date.now() - 24 * 60 * 60 * 1000),
        new Date()
      );
      
      expect(report.operatorId).toBe('AUo959');
      expect(report.summary.totalItems).toBe(2);
      expect(report.auroraGumasCompliance).toBe(true);
    });
  });
  
  describe('ReliquaryIndexer', () => {
    let indexer: ReliquaryIndexer;
    
    beforeEach(() => {
      indexer = new ReliquaryIndexer();
    });
    
    test('should create reliquary', () => {
      const reliquary = indexer.createReliquary('test', 'Test reliquary');
      expect(reliquary.name).toBe('test');
      expect(reliquary.operatorId).toBe('AUo959');
    });
    
    test('should archive and restore threads', () => {
      const reliquary = indexer.createReliquary('test', 'Test reliquary');
      const testState = { data: 'sealed thread state' };
      
      const success = indexer.archiveThread(
        reliquary.id,
        'thread1',
        testState,
        { classification: 'internal' },
        ['aurora', 'test']
      );
      
      expect(success).toBe(true);
      
      const restored = indexer.restoreThread(reliquary.id, 'thread1');
      expect(restored?.sealedState).toEqual(testState);
    });
    
    test('should search across reliquaries', () => {
      const reliquary = indexer.createReliquary('test', 'Test reliquary');
      indexer.archiveThread(reliquary.id, 'thread1', {}, {}, ['aurora', 'simulation']);
      
      const results = indexer.search({
        tags: ['aurora'],
        maxResults: 10
      });
      
      expect(results).toHaveLength(1);
      expect(results[0].threadId).toBe('thread1');
    });
  });
  
  describe('SimulationSnapshotter', () => {
    let snapshotter: SimulationSnapshotter;
    
    beforeEach(() => {
      snapshotter = new SimulationSnapshotter();
    });
    
    test('should create full snapshots', () => {
      const testState = { simulation: 'state', step: 1 };
      const snapshot = snapshotter.createSnapshot(testState, 'Test snapshot');
      
      expect(snapshot.metadata.operatorId).toBe('AUo959');
      expect(snapshot.isDelta).toBe(false);
      expect(snapshot.state).toEqual(testState);
    });
    
    test('should create differential snapshots', () => {
      const baseState = { simulation: 'state', step: 1 };
      const currentState = { simulation: 'state', step: 2, newField: 'added' };
      
      const baseSnapshot = snapshotter.createSnapshot(baseState, 'Base');
      const deltaSnapshot = snapshotter.createDifferentialSnapshot(
        currentState,
        baseSnapshot.metadata.id,
        'Delta'
      );
      
      expect(deltaSnapshot.isDelta).toBe(true);
      expect(deltaSnapshot.metadata.parentSnapshot).toBe(baseSnapshot.metadata.id);
    });
    
    test('should validate snapshots', () => {
      const testState = { data: 'test' };
      const snapshot = snapshotter.createSnapshot(testState, 'Validation test');
      
      const isValid = snapshotter.validateSnapshot(snapshot.metadata.id);
      expect(isValid).toBe(true);
    });
  });
  
  describe('ExportHelper', () => {
    let exporter: ExportHelper;
    
    beforeEach(() => {
      exporter = new ExportHelper();
    });
    
    test('should export data in JSON format', async () => {
      const testData = { aurora: 'test', operator: 'AUo959' };
      const result = await exporter.exportData(testData, {
        format: 'json',
        outputDirectory: '/tmp/test_exports'
      });
      
      expect(result.success).toBe(true);
      expect(result.manifest.operatorId).toBe('AUo959');
      expect(result.manifest.format).toBe('json');
    });
    
    test('should list exports', async () => {
      const exports = await exporter.listExports('/tmp/test_exports');
      expect(Array.isArray(exports)).toBe(true);
    });
  });
  
  describe('Integration Tests', () => {
    test('should integrate simulation with sealing and archiving', async () => {
      const simulation = new SymbolicSimulation();
      const sealer = new MemorySealer();
      const indexer = new ReliquaryIndexer();
      
      // Create simulation state
      const anchor = simulation.createAnchor('T1', { integration: 'test' });
      const thread = simulation.createThread(anchor.id);
      const state = simulation.exportState();
      
      // Seal the state
      const sealed = await sealer.sealMemory(state);
      
      // Archive in reliquary
      const reliquary = indexer.createReliquary('integration', 'Integration test');
      const archived = indexer.archiveThread(
        reliquary.id,
        thread.threadId,
        sealed,
        { test: 'integration' }
      );
      
      expect(archived).toBe(true);
      
      // Verify restoration
      const restored = indexer.restoreThread(reliquary.id, thread.threadId);
      expect(restored).toBeTruthy();
      expect(restored?.metadata.operatorId).toBe('AUo959');
    });
  });
});

// Mock functions for testing
beforeAll(() => {
  // Mock file system operations for ExportHelper tests
  jest.mock('fs', () => ({
    promises: {
      writeFile: jest.fn().mockResolvedValue(undefined),
      readFile: jest.fn().mockResolvedValue('{"test": "data"}'),
      readdir: jest.fn().mockResolvedValue(['manifest_test.json']),
      access: jest.fn().mockResolvedValue(undefined),
      mkdir: jest.fn().mockResolvedValue(undefined)
    }
  }));
});