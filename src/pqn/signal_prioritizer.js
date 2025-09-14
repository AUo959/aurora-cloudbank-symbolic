function baseScore(item) {
  return item.title ? item.title.length : 0;
}

function rank(items, quantumFlag = false) {
  return items
    .map(item => {
      let score = baseScore(item);
      if (quantumFlag) {
        const n = item.tags ? item.tags.length : 0;
        const entropy = n > 0 ? Math.log2(n) : 0;
        score *= (1 + entropy);
      }
      return { ...item, priority: score };
    })
    .sort((a, b) => b.priority - a.priority);
}

module.exports = { rank };
