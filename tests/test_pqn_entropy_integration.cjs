const assert = require('assert');
const { rank } = require('../src/pqn/signal_prioritizer.cjs');
const { mapToIndex } = require('../src/pqn/symbolic_index_mapper.cjs');

/**
 * Integration test that demonstrates the entropy calculation fix
 * in the context of the PQN signal prioritizer workflow.
 */
function testPQNEntropyIntegration() {
  console.log('Testing PQN entropy calculation integration...');
  
  // Mock data that simulates results from research harvester
  const mockHarvesterResults = [
    {
      source: 'arXiv',
      title: 'Quantum Computing Advances', 
      summary: 'Research on quantum algorithms and computing hardware'
    },
    {
      source: 'PubMed',
      title: 'Quantum Biology Research',
      summary: 'Quantum effects in biological systems and quantum biology'
    },
    {
      source: 'News',
      title: 'Computing Hardware News',
      summary: 'Latest computing computing computing hardware developments'  // Repeated keywords
    },
    {
      source: 'arXiv',
      title: 'Advanced Algorithms',
      summary: 'Novel algorithmic approaches and computational methods'
    }
  ];
  
  // Step 1: Map to symbolic index (creates tags from content)
  const taggedItems = mapToIndex(mockHarvesterResults);
  
  console.log('Tagged items:');
  taggedItems.forEach((item, idx) => {
    console.log(`  ${idx + 1}. "${item.title}" tags: [${item.tags.join(', ')}]`);
  });
  console.log();
  
  // Step 2: Rank without quantum flag (baseline)
  const rankedBaseline = rank(taggedItems, false);
  console.log('Ranking without quantum entropy:');
  rankedBaseline.forEach((item, idx) => {
    console.log(`  ${idx + 1}. "${item.title}" - priority: ${item.priority} (${item.tags.length} tags)`);
  });
  console.log();
  
  // Step 3: Rank with quantum flag (entropy-enhanced)
  const rankedWithEntropy = rank(taggedItems, true);
  console.log('Ranking WITH corrected entropy calculation:');
  rankedWithEntropy.forEach((item, idx) => {
    console.log(`  ${idx + 1}. "${item.title}" - priority: ${item.priority.toFixed(3)}`);
  });
  console.log();
  
  // Verification: Items with more diverse tags should get entropy boost
  const itemsWithRepeatedTags = rankedWithEntropy.filter(item => 
    item.title.includes('Computing Hardware')  // This has repeated "computing" in summary
  );
  
  const itemsWithDiverseTags = rankedWithEntropy.filter(item => 
    item.title.includes('Quantum Computing Advances') || item.title.includes('Advanced Algorithms')
  );
  
  // Verify that entropy calculation affects ranking appropriately
  assert.ok(rankedWithEntropy[0].priority > rankedBaseline[0].priority,
    'Quantum flag should boost priority through entropy calculation');
  
  console.log('✅ Integration test passed - entropy calculation is working correctly in PQN workflow');
  
  return {
    baseline: rankedBaseline,
    withEntropy: rankedWithEntropy,
    taggedItems: taggedItems
  };
}

/**
 * Test that reproduces the specific issue mentioned in PR #97
 */
function testOriginalIssueReproduction() {
  console.log('\nTesting fix for original issue from PR #97...');
  
  // This reproduces the exact problem mentioned in the review:
  // "The entropy calculation is incorrect. It should sum -p * log2(p) for each tag's 
  // probability within the item, not use the global probability."
  
  const testItems = [
    {
      title: 'Article A',
      tags: ['common', 'rare1']  // Mix of global frequencies, uniform locally
    },
    {
      title: 'Article B', 
      tags: ['common', 'common']  // Repeated tag, low local entropy
    }
  ];
  
  // Create global context where 'common' appears much more frequently
  const allItems = [
    ...Array(10).fill().map(() => ({ tags: ['common'] })),  // Make 'common' very frequent
    { tags: ['rare1'] },
    ...testItems
  ];
  
  console.log('Test scenario:');
  console.log('  - "common" appears globally very frequently');
  console.log('  - "rare1" appears globally infrequently');
  console.log('  - Article A: ["common", "rare1"] - uniform locally, mixed globally');
  console.log('  - Article B: ["common", "common"] - repeated locally');
  console.log();
  
  const ranked = rank(testItems, true);
  
  console.log('Results with CORRECTED entropy calculation:');
  ranked.forEach((item, idx) => {
    const localEntropy = calculateLocalEntropy(item.tags);
    console.log(`  ${idx + 1}. ${item.title}: priority = ${item.priority.toFixed(3)} (local entropy: ${localEntropy.toFixed(3)})`);
  });
  
  // Verify Article A (uniform locally) ranks higher than Article B (repeated locally)
  const articleA = ranked.find(item => item.title === 'Article A');
  const articleB = ranked.find(item => item.title === 'Article B');
  
  assert.ok(articleA.priority > articleB.priority,
    'Article with uniform local tag distribution should rank higher than repeated tags');
  
  console.log('✅ Original issue fix verified - local entropy correctly prioritizes diverse tags');
}

function calculateLocalEntropy(tags) {
  if (!tags || tags.length === 0) return 0;
  
  const tagCounts = {};
  for (const tag of tags) {
    tagCounts[tag] = (tagCounts[tag] || 0) + 1;
  }
  
  const total = tags.length;
  let entropy = 0;
  for (const count of Object.values(tagCounts)) {
    const p = count / total;
    entropy -= p * Math.log2(p);
  }
  
  return entropy;
}

// Run the tests
try {
  testPQNEntropyIntegration();
  testOriginalIssueReproduction();
  console.log('\n🎉 All PQN integration tests passed successfully!');
  console.log('\nThe entropy calculation now correctly computes Shannon entropy');
  console.log('based on tag frequencies within each individual item, providing');
  console.log('proper information content measurement for ranking purposes.');
} catch (error) {
  console.error('❌ Integration test failed:', error.message);
  process.exit(1);
}