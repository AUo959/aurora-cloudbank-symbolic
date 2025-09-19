const { verifyEthics } = require('../core/ethics_layer');
const harvester = require('./research_harvester');
const mapper = require('./symbolic_index_mapper');
const prioritizer = require('./signal_prioritizer');

async function parseKeywords(query) {
  return query.split(/\s+/);
}

async function handleQuery(query, opts = {}) {
  await verifyEthics();
  const keywords = await parseKeywords(query);
  const [papers, news, aiResponses] = await Promise.all([
    harvester.fetchArxiv(keywords.join(' ')),
    harvester.fetchNews(keywords.join(' ')),
    harvester.fetchPerplexity(query)
  ]);
  const tagged = mapper.mapToIndex([...papers, ...news, ...aiResponses]);
  const results = prioritizer.rank(tagged, opts.quantum_heuristic_flag);
  const summary = {
    query,
    timestamp: new Date().toISOString(),
    anchor: 'EOS_SEED_ORION',
    results
  };
  return summary;
}

module.exports = { handleQuery };
