const fetch = globalThis.fetch || ((...args) => import('node-fetch').then(({ default: f }) => f(...args)));

async function fetchArxiv(query) {
  if (process.env.PQN_OFFLINE_TEST) {
    return [{ source: 'arXiv', title: `Arxiv result for ${query}`, summary: 'offline stub' }];
  }
  const url = `https://export.arxiv.org/api/query?search_query=all:${encodeURIComponent(query)}&start=0&max_results=5`;
  try {
    const res = await fetch(url);
    const text = await res.text();
    return [{ source: 'arXiv', title: query, summary: text.slice(0,100) }];
  } catch (e) {
    return [];
  }
}

async function fetchPubMed(query) {
  if (process.env.PQN_OFFLINE_TEST) {
    return [{ source: 'PubMed', title: `PubMed result for ${query}`, summary: 'offline stub' }];
  }
  const apiKey = process.env.NCBI_API_KEY || '';
  let url = `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=${encodeURIComponent(query)}`;
  if (apiKey) {
    url += `&api_key=${encodeURIComponent(apiKey)}`;
  }
  try {
    const res = await fetch(url);
    const text = await res.text();
    return [{ source: 'PubMed', title: query, summary: text.slice(0,100) }];
  } catch (e) {
    return [];
  }
}

async function fetchNews(query) {
  if (process.env.PQN_OFFLINE_TEST) {
    return [{ source: 'News', title: `News result for ${query}`, summary: 'offline stub' }];
  }
  const apiKey = process.env.NEWS_API_KEY || '';
  const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}`;
  try {
    const res = await fetch(url, {
      headers: { 'X-Api-Key': apiKey }
    });
    const json = await res.json();
    return (json.articles || []).map(a => ({ source: 'News', title: a.title, summary: a.description }));
  } catch (e) {
    return [];
  }
}

async function fetchPerplexity(question) {
  if (process.env.PQN_OFFLINE_TEST) {
    return [{ source: 'Perplexity', title: question, summary: 'offline stub' }];
  }
  const apiKey = process.env.PERPLEXITY_API_KEY || '';
  try {
    const res = await fetch('https://api.perplexity.ai/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'sonar-pro', messages: [{ role: 'user', content: question }] })
    });
    const json = await res.json();
    return [{ source: 'Perplexity', title: question, summary: json.choices?.[0]?.message?.content || '' }];
  } catch (e) {
    return [];
  }
}

module.exports = { fetchArxiv, fetchPubMed, fetchNews, fetchPerplexity };
