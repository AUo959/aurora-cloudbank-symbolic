#!/usr/bin/env node
/**
 * Demonstration of the entropy calculation fix for issue #144
 * 
 * This script shows the difference between the incorrect global entropy calculation
 * and the correct local entropy calculation within individual items.
 */

const { rank } = require('./src/pqn/signal_prioritizer.cjs');

console.log('🔬 Entropy Calculation Fix Demonstration');
console.log('=' .repeat(50));
console.log();

// Example that clearly shows the problem and solution
const demonstrationItems = [
  {
    title: 'Article with Uniform Local Tags',
    tags: ['artificial', 'intelligence', 'machine', 'learning']  // All different
  },
  {
    title: 'Article with Repeated Local Tags', 
    tags: ['machine', 'machine', 'machine', 'learning']  // Mostly repeated
  },
  {
    title: 'Mixed Distribution Article',
    tags: ['artificial', 'artificial', 'intelligence']  // Some repetition
  }
];

console.log('📊 Test Data:');
demonstrationItems.forEach((item, idx) => {
  console.log(`  ${idx + 1}. "${item.title}"`);
  console.log(`     Tags: [${item.tags.join(', ')}]`);
  console.log(`     Tag counts: ${JSON.stringify(item.tags.reduce((acc, tag) => {
    acc[tag] = (acc[tag] || 0) + 1; 
    return acc;
  }, {}))}`);
});
console.log();

// Calculate and display entropy values
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
    if (p > 0) {
      entropy -= p * Math.log2(p);
    }
  }
  return entropy;
}

console.log('🧮 Entropy Analysis:');
demonstrationItems.forEach((item, idx) => {
  const entropy = calculateLocalEntropy(item.tags);
  console.log(`  ${idx + 1}. "${item.title}"`);
  console.log(`     Local Shannon entropy: ${entropy.toFixed(6)}`);
  console.log(`     Information content: ${entropy > 1.5 ? 'High' : entropy > 0.5 ? 'Medium' : 'Low'}`);
});
console.log();

// Show ranking with and without entropy
console.log('🏆 Ranking Comparison:');
console.log();

const rankedBaseline = rank(demonstrationItems, false);
console.log('Without entropy (baseline - tag count only):');
rankedBaseline.forEach((item, idx) => {
  console.log(`  ${idx + 1}. "${item.title}" - priority: ${item.priority}`);
});
console.log();

const rankedWithEntropy = rank(demonstrationItems, true);
console.log('With CORRECTED entropy calculation:');
rankedWithEntropy.forEach((item, idx) => {
  const entropy = calculateLocalEntropy(item.tags);
  console.log(`  ${idx + 1}. "${item.title}" - priority: ${item.priority.toFixed(3)} (entropy boost: ${(item.priority / item.tags.length - 1).toFixed(3)})`);
});
console.log();

console.log('✅ Key Insights:');
console.log('  • Items with diverse tags get higher entropy scores');
console.log('  • Items with repeated tags get lower entropy scores');
console.log('  • Entropy is calculated LOCALLY within each item, not globally');
console.log('  • This provides proper information content measurement');
console.log();

console.log('🎯 The Fix:');
console.log('  Before: entropy -= globalTagProbs[tag] * Math.log2(globalTagProbs[tag])');
console.log('  After:  entropy -= (localCount/totalTags) * Math.log2(localCount/totalTags)');
console.log();

console.log('📚 This fix ensures Shannon entropy is calculated correctly for ranking');
console.log('   items based on their internal tag diversity, not global tag frequencies.');