/**
 * Dossia Backend API Client
 */
const API = {
  async request(url, options = {}) {
    const res = await fetch(url, options);
    const contentType = res.headers.get('content-type') || '';
    const body = contentType.includes('application/json') ? await res.json() : await res.text();
    if (!res.ok) {
      const detail = body && typeof body === 'object' ? body.detail : body;
      throw new Error(detail || `Request failed (${res.status})`);
    }
    return body;
  },

  async getLatestDossier(category = 'all') {
    let url = '/api/dossiers/latest';
    if (category && category !== 'all') url += `?category=${encodeURIComponent(category)}`;
    return this.request(url);
  },

  async getDossierCategories() {
    return this.request('/api/dossiers/categories');
  },

  async generateDossier(editionType = 'morning', category = 'all') {
    let url = `/api/dossiers/generate?edition_type=${editionType}`;
    if (category && category !== 'all') url += `&category=${encodeURIComponent(category)}`;
    return this.request(url, { method: 'POST' });
  },

  async getArticles(category = 'all', q = '', limit = 50) {
    let url = `/api/articles?limit=${limit}`;
    if (category && category !== 'all') url += `&category=${encodeURIComponent(category)}`;
    if (q) url += `&q=${encodeURIComponent(q)}`;
    return this.request(url);
  },

  async getArticle(id) {
    return this.request(`/api/articles/${encodeURIComponent(id)}`);
  },

  async triggerIngest() {
    return this.request('/api/articles/ingest', { method: 'POST' });
  },

  async getEpisodes() {
    return this.request('/api/episodes');
  },

  async generateEpisode() {
    return this.request('/api/episodes/generate', { method: 'POST' });
  },

  async askHermes(context, question) {
    return this.request('/api/hermes/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context, question })
    });
  },

  async getSettings() {
    return this.request('/api/settings');
  },

  async getChatGPTStatus() {
    return this.request('/api/chatgpt-auth/status');
  },

  async getChatGPTModels() {
    return this.request('/api/chatgpt-auth/models');
  },

  async disconnectChatGPT() {
    return this.request('/api/chatgpt-auth/disconnect', { method: 'POST' });
  },

  async testLLM(provider) {
    return this.request('/api/settings/test-llm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider })
    });
  },

  async saveSettings(data) {
    return this.request('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  },

  async addSource(source) {
    return this.request('/api/settings/sources', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(source)
    });
  },

  async deleteSource(sourceId) {
    return this.request(`/api/settings/sources/${encodeURIComponent(sourceId)}`, { method: 'DELETE' });
  },

  async getDiscover() {
    return this.request('/api/discover');
  },

  async toggleDiscover(sourceId, enabled) {
    return this.request(`/api/discover/${encodeURIComponent(sourceId)}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
  },

  async batchToggleDiscover(enabled, category = 'all') {
    let url = `/api/discover/batch?enabled=${enabled}`;
    if (category && category !== 'all') url += `&category=${encodeURIComponent(category)}`;
    return this.request(url, { method: 'POST' });
  },

  async speakText(title, text) {
    return this.request('/api/tts/speak', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, text })
    });
  }
};
