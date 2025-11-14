function extractKeywords(text) {
  return Array.from(new Set(text.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean)));
}

function mapToIndex(items) {
  return items.map(item => {
    const text = [item.title, item.summary].filter(Boolean).join(' ');
    const tags = extractKeywords(text);
    return { ...item, tags };
  });
}

module.exports = { mapToIndex };