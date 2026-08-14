/**
 * Dossia Backend API Client
 */
const API = {
  async getLatestDossier(category = 'all') {
    let url = '/api/dossiers/latest';
    if (category && category !== 'all') url += `?category=${encodeURIComponent(category)}`;
    const res = await fetch(url);
    return res.json();
  },

  async getDossierCategories() {
    const res = await fetch('/api/dossiers/categories');
    return res.json();
  },

  async generateDossier(editionType = 'morning', category = 'all') {
    let url = `/api/dossiers/generate?edition_type=${editionType}`;
    if (category && category !== 'all') url += `&category=${encodeURIComponent(category)}`;
    const res = await fetch(url, { method: 'POST' });
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

  async getDiscover() {
    const res = await fetch('/api/discover');
    return res.json();
  },

  async toggleDiscover(sourceId, enabled) {
    const res = await fetch(`/api/discover/${sourceId}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    return res.json();
  },

  async batchToggleDiscover(enabled, category = 'all') {
    let url = `/api/discover/batch?enabled=${enabled}`;
    if (category && category !== 'all') url += `&category=${encodeURIComponent(category)}`;
    const res = await fetch(url, { method: 'POST' });
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
