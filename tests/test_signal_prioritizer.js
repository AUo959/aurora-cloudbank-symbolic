const assert = require('assert');
const { rank } = require('../src/pqn/signal_prioritizer');

const items = [
  { title: 'A', tags: ['x'] },
  { title: 'BB', tags: ['x', 'y'] }
];

const ranked = rank(items, true);
assert.ok(ranked[0].priority >= ranked[1].priority, 'ranking should sort by priority');
console.log('signal prioritizer test passed');
