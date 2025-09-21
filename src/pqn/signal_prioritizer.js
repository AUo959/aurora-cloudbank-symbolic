function baseScore(item) {
  return item.title ? item.title.length : 0;
}

function rank(items, quantumFlag = false) {
  // Compute global tag counts and probabilities
  const globalTagCounts = {};
  let totalTagCount = 0;
  for (const item of items) {
    if (item.tags && Array.isArray(item.tags)) {
      for (const tag of item.tags) {
        globalTagCounts[tag] = (globalTagCounts[tag] || 0) + 1;
        totalTagCount += 1;
      }
    }
  }
  const globalTagProbs = {};
  for (const tag in globalTagCounts) {
    globalTagProbs[tag] = globalTagCounts[tag] / totalTagCount;
  }

  return items
    .map(item => {
      let score = baseScore(item);
      if (quantumFlag) {
        const tags = item.tags || [];
        let entropy = 0;
        if (tags.length > 0) {
          // Calculate entropy of item's tags using global tag probabilities
          // Only consider unique tags in the item
          const uniqueTags = Array.from(new Set(tags));
          for (const tag of uniqueTags) {
            const p = globalTagProbs[tag];
            if (p) {
              entropy -= p * Math.log2(p);
            }
          }
        }
        score *= (1 + entropy);
      }
      return { ...item, priority: score };
    })
    .sort((a, b) => b.priority - a.priority);
}

module.exports = { rank };
