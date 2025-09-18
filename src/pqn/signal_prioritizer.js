function baseScore(item) {
  return item.title ? item.title.length : 0;
}

function rank(items, quantumFlag = false) {
  return items
    .map(item => {
      let score = baseScore(item);
      if (quantumFlag) {
        const n = item.tags ? item.tags.length : 0;
        let entropy = 0;
        if (n > 0) {
          // Count occurrences of each tag
          const tagCounts = {};
          for (const tag of item.tags) {
            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
          }
          // Calculate probabilities and entropy
          for (const tag in tagCounts) {
            const p = tagCounts[tag] / n;
            entropy -= p * Math.log2(p);
          }
        }
        score *= (1 + entropy);
      }
      return { ...item, priority: score };
    })
    .sort((a, b) => b.priority - a.priority);
}

module.exports = { rank };
