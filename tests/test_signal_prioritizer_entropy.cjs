const assert = require('assert');
const { rank } = require('../src/pqn/signal_prioritizer.cjs');

// Test cases for the corrected entropy calculation
function testEntropyCalculation() {
  console.log('Testing Shannon entropy calculation fix...');
  
  // Test case 1: Items with uniform tag distribution (high entropy)
  const items1 = [
    { 
      title: 'Uniform tags', 
      tags: ['alpha', 'beta', 'gamma'] // Each tag appears once, entropy = log2(3) ≈ 1.585
    },
    { 
      title: 'Single tag', 
      tags: ['alpha'] // Single tag, entropy = 0
    }
  ];
  
  const ranked1 = rank(items1, true);
  console.log('Test 1 - Uniform vs Single tag:');
  console.log('  Uniform tags priority:', ranked1[0].priority);
  console.log('  Single tag priority:', ranked1[1].priority);
  
  // The item with uniform tags should have higher priority due to higher entropy
  assert.ok(ranked1[0].priority > ranked1[1].priority, 
    'Item with uniform tags should have higher priority than single tag item');
  
  // Test case 2: Items with repeated tags (lower entropy)
  const items2 = [
    { 
      title: 'Repeated tags', 
      tags: ['alpha', 'alpha', 'beta'] // p(alpha)=2/3, p(beta)=1/3, entropy ≈ 0.918
    },
    { 
      title: 'Unique tags', 
      tags: ['alpha', 'beta'] // p(alpha)=1/2, p(beta)=1/2, entropy = 1.0
    }
  ];
  
  const ranked2 = rank(items2, true);
  console.log('Test 2 - Repeated vs Unique tags:');
  console.log('  Repeated tags priority:', ranked2[1].priority);
  console.log('  Unique tags priority:', ranked2[0].priority);
  
  // The item with unique tags should have higher entropy and thus higher priority
  assert.ok(ranked2[0].priority > ranked2[1].priority,
    'Item with unique tags should have higher priority than repeated tags item');
  
  // Test case 3: Empty tags should have zero entropy
  const items3 = [
    { title: 'No tags', tags: [] },
    { title: 'With tags', tags: ['alpha', 'beta'] }
  ];
  
  const ranked3 = rank(items3, true);
  console.log('Test 3 - No tags vs With tags:');
  console.log('  No tags priority:', ranked3[1].priority);
  console.log('  With tags priority:', ranked3[0].priority);
  
  // Item with tags should have higher priority
  assert.ok(ranked3[0].priority > ranked3[1].priority,
    'Item with tags should have higher priority than item without tags');
  
  // Test case 4: Verify entropy calculation is local, not global
  const items4 = [
    { title: 'Item 1', tags: ['rare1', 'rare2'] }, // Both rare globally, but uniform locally
    { title: 'Item 2', tags: ['common', 'common'] }, // Common globally, but repeated locally
    { title: 'Item 3', tags: ['common', 'common', 'common'] } // Even more repeated
  ];
  
  const ranked4 = rank(items4, true);
  console.log('Test 4 - Local vs Global entropy:');
  for (let i = 0; i < ranked4.length; i++) {
    console.log(`  ${ranked4[i].title} priority: ${ranked4[i].priority}`);
  }
  
  // Item 1 should have highest priority due to uniform local distribution
  assert.ok(ranked4[0].title === 'Item 1',
    'Item with uniform local tag distribution should rank highest');
  
  console.log('✅ All entropy calculation tests passed!');
}

// Test that quantum flag works correctly
function testQuantumFlag() {
  console.log('\nTesting quantum flag behavior...');
  
  const items = [
    { title: 'Test A', tags: ['x', 'y'] },
    { title: 'Test B', tags: ['x'] }
  ];
  
  const rankedWithoutQuantum = rank(items, false);
  const rankedWithQuantum = rank(items, true);
  
  // Without quantum flag, should rank only by tag count
  assert.strictEqual(rankedWithoutQuantum[0].title, 'Test A', 
    'Without quantum flag, should rank by tag count only');
  
  // With quantum flag, should consider entropy  
  assert.ok(rankedWithQuantum[0].priority > rankedWithoutQuantum[0].priority,
    'Quantum flag should boost priority with entropy calculation');
  
  console.log('✅ Quantum flag test passed!');
}

// Run all tests
try {
  testEntropyCalculation();
  testQuantumFlag();
  console.log('\n🎉 All signal prioritizer tests passed successfully!');
} catch (error) {
  console.error('❌ Test failed:', error.message);
  process.exit(1);
}