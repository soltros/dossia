/**
 * Dossia Backend API Client
 */
const API = {
  async getLatestDossier() {
    const res = await fetch('/api/dossiers/latest');
    return res.json();
  },

  async generateDossier(editionType = 'morning') {
    const res = await fetch(`/api/dossiers/generate?edition_type=${editionType}`, { method: 'POST' });
    return res.json();
  },

  async getArticles(category = 'all', q = '', limit = 50) {
    let url = `/api/articles?limit=${limit}`;
    if (category && category !== 'all') url += `&category=${encodeURIComponent(category)}`;
    if (q) url += `&q=${encodeURIComponent(q)}`;
    const res = await fetch(url);
    return res.json();
  },

  async getArticle(id) {
    const res = await fetch(`/api/articles/${id}`);
    return res.json();
  },

  async triggerIngest() {
    const res = await fetch('/api/articles/ingest', { method: 'POST' });
    return res.json();
  },

  async getEpisodes() {
    const res = await fetch('/api/episodes');
    return res.json();
  },

  async generateEpisode() {
    const res = await fetch('/api/episodes/generate', { method: 'POST' });
    return res.json();
  },

  async askHermes(context, question) {
    const res = await fetch('/api/hermes/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context, question })
    });
    return res.json();
  },

  async getSettings() {
    const res = await fetch('/api/settings');
    return res.json();
  },

  async saveSettings(data) {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async addSource(source) {
    const res = await fetch('/api/settings/sources', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(source)
    });
    return res.json();
  },

  async deleteSource(sourceId) {
    const res = await fetch(`/api/settings/sources/${sourceId}`, { method: 'DELETE' });
    return res.json();
  },

  async speakText(title, text) {
    const res = await fetch('/api/tts/speak', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, text })
    });
    return res.json();
  }
};
