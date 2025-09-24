// Use the number of tags as the base score, as items with more tags may be more relevant or connected.
function baseScore(item) {
  return item.tags && Array.isArray(item.tags) ? item.tags.length : 0;
}

function rank(items, quantumFlag = false) {
  return items
    .map(item => {
      let score = baseScore(item);
      if (quantumFlag) {
        const tags = item.tags || [];
        let entropy = 0;
        if (tags.length > 0) {
          // Calculate Shannon entropy from tag frequencies within THIS item
          // Count occurrences of each tag within this specific item
          const tagCounts = {};
          for (const tag of tags) {
            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
          }
          
          // Calculate probabilities based on tag frequencies within this item
          const totalTags = tags.length;
          for (const tag in tagCounts) {
            const p = tagCounts[tag] / totalTags;
            if (p > 0) {
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