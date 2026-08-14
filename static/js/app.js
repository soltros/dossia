/**
 * Dossia Main Application Orchestrator & View Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const App = {
    currentTab: 'dossier-view',
    currentDossier: null,

    init() {
      this.initTheme();
      this.initNavigation();
      this.initSearchModal();
      this.initDossierView();
      this.initDiscoverView();
      this.initReservoirView();
      this.initPodcastView();
      this.initSettingsView();
      this.loadInitialData();
    },

    // --------------------------------------------------------------------------
    // Theme Management
    // --------------------------------------------------------------------------
    initTheme() {
      const savedTheme = localStorage.getItem('dossia-theme') || 'paper';
      document.documentElement.setAttribute('data-theme', savedTheme);
      this.updateThemeIcon(savedTheme);

      document.getElementById('theme-toggle-btn').addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'paper' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('dossia-theme', next);
        this.updateThemeIcon(next);
      });
    },

    updateThemeIcon(theme) {
      document.getElementById('theme-icon').textContent = theme === 'dark' ? '☀️' : '🌗';
    },

    // --------------------------------------------------------------------------
    // Navigation & Tabs
    // --------------------------------------------------------------------------
    initNavigation() {
      document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
          const target = tab.getAttribute('data-tab');
          this.switchTab(target);
        });
      });

      document.getElementById('brand-home-btn').addEventListener('click', (e) => {
        e.preventDefault();
        this.switchTab('dossier-view');
      });

      document.getElementById('trigger-sync-btn').addEventListener('click', async () => {
        const btn = document.getElementById('trigger-sync-btn');
        btn.textContent = '⏳';
        try {
          const res = await API.triggerIngest();
          alert(`Ingestion complete! Fetched ${res.total_new_articles} new articles across ${res.sources_processed} channels.`);
          this.loadInitialData();
        } catch (e) {
          alert(`Sync error: ${e.message}`);
        } finally {
          btn.textContent = '⚡';
        }
      });
    },

    switchTab(tabId) {
      this.currentTab = tabId;
      document.querySelectorAll('.nav-tab').forEach(t => {
        t.classList.toggle('active', t.getAttribute('data-tab') === tabId);
      });
      document.querySelectorAll('.tab-view').forEach(v => {
        v.classList.toggle('active', v.id === tabId);
      });

      if (tabId === 'discover-view') this.loadDiscoverCatalog();
      if (tabId === 'reservoir-view') this.loadReservoirArticles();
      if (tabId === 'podcast-view') this.loadPodcastEpisodes();
      if (tabId === 'settings-view') this.loadSettings();
    },

    // --------------------------------------------------------------------------
    // Initial Data Loader
    // --------------------------------------------------------------------------
    async loadInitialData() {
      await this.loadDossier();
    },

    // --------------------------------------------------------------------------
    // View 1: The Daily Dossier & Category Briefings
    // --------------------------------------------------------------------------
    selectedDossierCategory: 'all',
    selectedReservoirCategory: 'all',

    initDossierView() {
      document.getElementById('synth-new-dossier-btn').addEventListener('click', async () => {
        const btn = document.getElementById('synth-new-dossier-btn');
        btn.innerHTML = '<span>⏳</span> Synthesizing Briefing...';
        btn.disabled = true;
        try {
          await API.generateDossier('morning', this.selectedDossierCategory);
          await this.loadDossier(this.selectedDossierCategory);
        } catch (e) {
          alert(`Synthesis error: ${e.message}`);
        } finally {
          btn.innerHTML = '<span>✨</span> Re-Synthesize Briefing';
          btn.disabled = false;
        }
      });

      document.getElementById('listen-dossier-btn').addEventListener('click', () => {
        if (!this.currentDossier) return;
        const textToRead = this.buildFullBriefingAudioScript(this.currentDossier);
        window.dossiaAudio.playSpokenText(this.currentDossier.title, textToRead);
      });

      // Load category pills for Dossier view
      this.loadDossierCategories();
    },

    buildFullBriefingAudioScript(dossier) {
      const parts = [];
      const title = dossier.title || 'Daily Intelligence Briefing';
      const edition = dossier.edition_date || 'Today';
      
      parts.push(`Welcome to the Dossia ${title} for ${edition}. I am your autonomous editorial host.`);
      
      // Executive Overview
      parts.push("Here is your Executive 60-Second Overview covering the top technical signals.");
      (dossier.executive_tldr || []).forEach((b, i) => {
        const cleanB = b.replace(/\*\*/g, '').replace(/\[.*?\]/g, '').replace(/#+\s*/g, '');
        parts.push(cleanB);
      });
      
      // Story Capsules
      const clusters = dossier.story_clusters || [];
      if (clusters.length > 0) {
        parts.push(`Now, moving into our ${clusters.length} deep-dive story capsules.`);
        clusters.forEach((c, idx) => {
          parts.push(`Story number ${idx + 1}: ${c.headline}.`);
          if (c.narrative_summary) {
            const cleanNarrative = c.narrative_summary.replace(/\*\*/g, '').replace(/\[.*?\]/g, '').replace(/#+\s*/g, '');
            parts.push(cleanNarrative);
          }
          if (c.key_takeaways && c.key_takeaways.length > 0) {
            parts.push("Key technical takeaways for this story:");
            c.key_takeaways.forEach(t => {
              const cleanT = t.replace(/\*\*/g, '').replace(/\[.*?\]/g, '').replace(/#+\s*/g, '');
              parts.push(cleanT);
            });
          }
        });
      }

      parts.push("This concludes today's Dossia intelligence brief. You can inspect full-text citations and run in-margin Q&A directly on your dashboard. Thank you for listening.");
      return parts.join("\n\n");
    },

    formatMarkdown(text) {
      if (!text) return '';
      // Strip all raw URLs and markdown link wrappers
      let clean = text
        .replace(/!\[.*?\]\(.*?\)/g, '')
        .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
        .replace(/https?:\/\/\S+/gi, '')
        .replace(/www\.\S+/gi, '')
        .replace(/\(\/[^\)]+\)/g, '')
        .replace(/\[[A-Za-z0-9\.\-_ /]{1,30}\]/g, '')
        .replace(/\[\s*\]/g, '')
        .replace(/^[#*+\->\s|]+/gm, '')
        .trim();

      // Escape HTML
      let html = clean
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
      
      // Convert **bold** to <strong>
      html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // Convert "Publisher Name: Text" at start to "<strong>Publisher Name:</strong> Text" if not already bolded
      if (!html.startsWith('<strong>') && html.includes(':')) {
        const colonIdx = html.indexOf(':');
        if (colonIdx > 0 && colonIdx < 45) {
          const prefix = html.substring(0, colonIdx);
          const rest = html.substring(colonIdx + 1);
          html = `<strong>${prefix}:</strong>${rest}`;
        }
      }

      // Inline code
      html = html.replace(/`([^`]+)`/g, '<code style="background: var(--bg-surface-elevated); padding: 2px 5px; border-radius: 4px; font-size: 0.88em; font-family: var(--font-mono);">$1</code>');
      
      // Paragraph breaks
      const paras = html.split(/\n\s*\n/);
      if (paras.length > 1) {
        return paras.map(p => `<p style="margin-bottom: 12px; line-height: 1.65;">${p.trim()}</p>`).join('');
      }
      return html;
    },

    async loadDossierCategories() {
      const pillsContainer = document.getElementById('dossier-category-pills');
      if (!pillsContainer) return;

      try {
        const catRes = await API.getDossierCategories();
        const categories = catRes.categories || [];

        pillsContainer.innerHTML = '';
        
        // "All Intelligence" master pill
        const allBtn = document.createElement('button');
        allBtn.className = `filter-pill ${this.selectedDossierCategory === 'all' ? 'active' : ''}`;
        allBtn.textContent = 'All Intelligence';
        allBtn.addEventListener('click', () => {
          this.selectedDossierCategory = 'all';
          this.highlightPill(pillsContainer, allBtn);
          this.loadDossier('all');
        });
        pillsContainer.appendChild(allBtn);

        // Domain-specific category pills
        categories.forEach(item => {
          const pill = document.createElement('button');
          pill.className = `filter-pill ${this.selectedDossierCategory === item.category ? 'active' : ''}`;
          pill.textContent = item.category;
          pill.title = `${item.article_count || 0} articles from ${item.source_count || 0} sources`;
          pill.addEventListener('click', () => {
            this.selectedDossierCategory = item.category;
            this.highlightPill(pillsContainer, pill);
            this.loadDossier(item.category);
          });
          pillsContainer.appendChild(pill);
        });
      } catch (e) {
        console.error('Failed to load dossier categories:', e);
      }
    },

    highlightPill(container, activePill) {
      container.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
      activePill.classList.add('active');
    },

    async loadDossier(category = 'all') {
      const container = document.getElementById('story-clusters-container');
      const bulletsList = document.getElementById('dossier-bullets-list');

      container.innerHTML = '<div style="padding: 20px; color: var(--text-muted);">Synthesizing deep domain briefing...</div>';
      bulletsList.innerHTML = '<li>Loading domain briefing highlights...</li>';

      try {
        const dossier = await API.getLatestDossier(category);
        this.currentDossier = dossier;

        document.getElementById('dossier-title-text').textContent = dossier.title || `${category} Intelligence Briefing`;
        document.getElementById('dossier-edition-label').textContent = `${dossier.edition_type ? dossier.edition_type.toUpperCase() : 'DAILY'} BRIEFING • ${dossier.edition_date || 'Today'}`;

        // Render executive bullets
        bulletsList.innerHTML = '';
        (dossier.executive_tldr || []).forEach(bullet => {
          const li = document.createElement('li');
          li.innerHTML = this.formatMarkdown(bullet);
          bulletsList.appendChild(li);
        });

        // Render story clusters
        container.innerHTML = '';
        if (!dossier.story_clusters || dossier.story_clusters.length === 0) {
          container.innerHTML = `<div style="padding: 30px; text-align: center; color: var(--text-muted); grid-column: 1 / -1;">No story clusters yet for ${category}. Click "Re-Synthesize Briefing" to generate one.</div>`;
          return;
        }

        (dossier.story_clusters || []).forEach(cluster => {
          const card = document.createElement('article');
          card.className = 'story-capsule';

          const sourcesHtml = (cluster.sources || []).map(s => `
            <button class="source-pill" data-article-id="${s.id}">
              <span>📄</span> ${s.publisher || 'Source'}: ${s.title.substring(0, 36)}...
            </button>
          `).join('');

          const takeawaysHtml = (cluster.key_takeaways || []).map(t => `
            <li style="margin-bottom: 8px; line-height: 1.5;">${this.formatMarkdown(t)}</li>
          `).join('');

          card.innerHTML = `
            <div class="capsule-top">
              <span class="capsule-category">${cluster.category || category}</span>
              <span class="signal-badge">${cluster.signal_badge || 'High Signal'}</span>
            </div>
            <h2 class="capsule-headline serif-heading">${cluster.headline}</h2>
            <div class="capsule-narrative" style="color: var(--text-secondary); margin-bottom: 20px;">
              ${this.formatMarkdown(cluster.narrative_summary)}
            </div>
            
            <div class="capsule-takeaways">
              <div class="takeaways-title">Key Developments & Technical Implications</div>
              <ul class="takeaways-list" style="margin-top: 10px; padding-left: 18px;">
                ${takeawaysHtml}
              </ul>
            </div>

            <div class="capsule-footer">
              <div class="capsule-sources" style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">
                <span style="font-size: 0.76rem; font-family: var(--font-mono); color: var(--text-muted);">Sources:</span>
                ${sourcesHtml || '<span style="font-size: 0.8rem; color: var(--text-muted);">Curated synthesis</span>'}
              </div>
              <div class="capsule-actions">
                <button class="btn-secondary listen-cluster-btn" title="Listen to this section">
                  <span>🎧</span> Listen
                </button>
              </div>
            </div>
          `;

          // Event listeners
          card.querySelector('.listen-cluster-btn').addEventListener('click', () => {
            const clusterSpeech = `${cluster.headline}. ${cluster.narrative_summary}. Key takeaways: ${(cluster.key_takeaways || []).join('. ')}`;
            window.dossiaAudio.playSpokenText(cluster.headline, clusterSpeech);
          });

          card.querySelectorAll('.source-pill').forEach(pill => {
            pill.addEventListener('click', () => {
              const artId = pill.getAttribute('data-article-id');
              window.dossiaReader.open(artId);
            });
          });

          container.appendChild(card);
        });

      } catch (e) {
        bulletsList.innerHTML = `<li>Could not load briefing: ${e.message}</li>`;
      }
    },

    // --------------------------------------------------------------------------
    // View 2: Discover & Source Directory
    // --------------------------------------------------------------------------
    initDiscoverView() {
      document.getElementById('discover-sync-btn').addEventListener('click', async () => {
        const btn = document.getElementById('discover-sync-btn');
        btn.innerHTML = '<span>⏳</span> Ingesting...';
        try {
          const res = await API.triggerIngest();
          alert(`Ingestion complete! Fetched ${res.total_new_articles} new articles.`);
          this.loadDiscoverCatalog();
        } catch (e) {
          alert(`Ingestion error: ${e.message}`);
        } finally {
          btn.innerHTML = '<span>⚡</span> Ingest Followed Feeds';
        }
      });

      document.getElementById('discover-enable-all-btn').addEventListener('click', async () => {
        const btn = document.getElementById('discover-enable-all-btn');
        const isFollowAll = btn.textContent.includes('Follow All');
        await API.batchToggleDiscover(isFollowAll);
        btn.innerHTML = isFollowAll ? '<span>✕</span> Unfollow All' : '<span>✓</span> Follow All';
        this.loadDiscoverCatalog();
      });
    },

    async loadDiscoverCatalog(selectedCategory = 'all') {
      const container = document.getElementById('discover-catalog-container');
      const pillsContainer = document.getElementById('discover-category-pills');
      const statsLabel = document.getElementById('discover-stats-label');

      container.innerHTML = '<div style="padding: 20px; color: var(--text-muted);">Loading curated catalog...</div>';

      try {
        const catalog = await API.getDiscover();
        statsLabel.textContent = `${catalog.followed_count} of ${catalog.total} Channels Followed`;

        // Render Category Pills
        pillsContainer.innerHTML = '';
        const allPill = document.createElement('button');
        allPill.className = `filter-pill ${selectedCategory === 'all' ? 'active' : ''}`;
        allPill.textContent = 'All Categories';
        allPill.addEventListener('click', () => this.loadDiscoverCatalog('all'));
        pillsContainer.appendChild(allPill);

        (catalog.categories || []).forEach(cat => {
          const pill = document.createElement('button');
          pill.className = `filter-pill ${selectedCategory === cat ? 'active' : ''}`;
          pill.textContent = cat;
          pill.addEventListener('click', () => this.loadDiscoverCatalog(cat));
          pillsContainer.appendChild(pill);
        });

        // Filter sources
        const filtered = (catalog.sources || []).filter(s => {
          return selectedCategory === 'all' || s.category === selectedCategory;
        });

        container.innerHTML = '';
        filtered.forEach(src => {
          const card = document.createElement('div');
          card.className = 'story-capsule';
          card.style.cssText = 'padding: 24px; display: flex; flex-direction: column; justify-content: space-between; gap: 14px;';

          const isFollowed = src.enabled === 1;

          card.innerHTML = `
            <div>
              <div class="capsule-top" style="margin-bottom: 8px;">
                <span class="capsule-category">${src.category}</span>
                <span class="signal-badge" style="background: ${isFollowed ? 'var(--accent-surface)' : 'var(--badge-bg)'}; color: ${isFollowed ? 'var(--accent-primary)' : 'var(--text-muted)'};">
                  ${isFollowed ? '🟢 Followed' : 'Inactive'}
                </span>
              </div>
              <h3 class="serif-heading" style="font-size: 1.35rem; margin-bottom: 6px;">
                <a href="${src.site_url || '#'}" target="_blank" title="Visit website" style="display: inline-flex; align-items: center; gap: 6px;">
                  ${src.name} <span style="font-size: 0.8rem; color: var(--accent-primary);">↗</span>
                </a>
              </h3>
              <p style="font-size: 0.86rem; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.5;">
                ${src.why_read || src.best_for || ''}
              </p>
            </div>

            <div style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid var(--border-subtle); padding-top: 12px;">
              <span style="font-size: 0.74rem; font-family: var(--font-mono); color: var(--text-muted);">
                ${src.best_for ? '🎯 ' + src.best_for.substring(0, 36) + '...' : 'Curated feed'}
              </span>
              <button class="btn-${isFollowed ? 'secondary' : 'primary'} toggle-follow-btn" style="padding: 6px 14px; font-size: 0.8rem;">
                ${isFollowed ? 'Unfollow' : 'Follow +'}
              </button>
            </div>
          `;

          card.querySelector('.toggle-follow-btn').addEventListener('click', async () => {
            const nextState = src.enabled !== 1;
            await API.toggleDiscover(src.id, nextState);
            this.loadDiscoverCatalog(selectedCategory);
          });

          container.appendChild(card);
        });

      } catch (e) {
        container.innerHTML = `<div style="padding: 20px; color: red;">Failed to load catalog: ${e.message}</div>`;
      }
    },

    // --------------------------------------------------------------------------
    // View 3: Curated Knowledge Reservoir
    // --------------------------------------------------------------------------
    initReservoirView() {
      document.getElementById('reservoir-sync-btn').addEventListener('click', async () => {
        const btn = document.getElementById('reservoir-sync-btn');
        btn.textContent = 'Ingesting...';
        await API.triggerIngest();
        btn.textContent = '⚡ Ingest All Sources';
        this.loadReservoirCategories();
        this.loadReservoirArticles(this.selectedReservoirCategory);
      });

      this.loadReservoirCategories();
    },

    async loadReservoirCategories() {
      const pillsContainer = document.getElementById('category-filters-container');
      if (!pillsContainer) return;

      try {
        const catRes = await API.getDossierCategories();
        const categories = catRes.categories || [];

        pillsContainer.innerHTML = '';
        
        // "All Channels" pill
        const allBtn = document.createElement('button');
        allBtn.className = `filter-pill ${this.selectedReservoirCategory === 'all' ? 'active' : ''}`;
        allBtn.textContent = 'All Channels';
        allBtn.addEventListener('click', () => {
          this.selectedReservoirCategory = 'all';
          this.highlightPill(pillsContainer, allBtn);
          this.loadReservoirArticles('all');
        });
        pillsContainer.appendChild(allBtn);

        categories.forEach(item => {
          const pill = document.createElement('button');
          pill.className = `filter-pill ${this.selectedReservoirCategory === item.category ? 'active' : ''}`;
          pill.textContent = `${item.category} (${item.article_count || 0})`;
          pill.addEventListener('click', () => {
            this.selectedReservoirCategory = item.category;
            this.highlightPill(pillsContainer, pill);
            this.loadReservoirArticles(item.category);
          });
          pillsContainer.appendChild(pill);
        });
      } catch (e) {
        console.error('Failed to load reservoir categories:', e);
      }
    },

    async loadReservoirArticles(category = 'all') {
      const container = document.getElementById('articles-stream-container');
      container.innerHTML = '<div style="padding: 20px; color: var(--text-muted);">Loading articles...</div>';

      try {
        const res = await API.getArticles(category);
        container.innerHTML = '';

        if (!res.articles || res.articles.length === 0) {
          container.innerHTML = '<div style="padding: 30px; text-align: center; color: var(--text-muted);">No articles found. Click "Ingest All Sources" to fetch.</div>';
          return;
        }

        res.articles.forEach(art => {
          const row = document.createElement('div');
          row.className = 'article-row-card';
          row.innerHTML = `
            <div class="article-row-main">
              <div class="article-row-meta">
                <span>${art.publisher || 'FEED'}</span>
                <span>•</span>
                <span>${art.reading_time_minutes || 3} min read</span>
                <span>•</span>
                <span>${art.published_at ? art.published_at.substring(0, 10) : ''}</span>
              </div>
              <h3 class="article-row-title">${art.title}</h3>
              <p class="article-row-snippet">${art.summary || ''}</p>
            </div>
            <div class="article-row-side">
              <span class="signal-badge">${art.signal_score ? art.signal_score.toFixed(1) : '8.0'} Signal</span>
              <button class="btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;">Read</button>
            </div>
          `;

          row.addEventListener('click', () => {
            window.dossiaReader.open(art.id);
          });

          container.appendChild(row);
        });
      } catch (e) {
        container.innerHTML = `<div style="padding: 20px; color: red;">Error: ${e.message}</div>`;
      }
    },

    // --------------------------------------------------------------------------
    // View 3: Podcast Studio & Fountain Hub
    // --------------------------------------------------------------------------
    initPodcastView() {
      const urlInput = document.getElementById('podcast-feed-url-input');
      urlInput.value = `${window.location.origin}/podcast.xml`;

      document.getElementById('copy-feed-url-btn').addEventListener('click', () => {
        navigator.clipboard.writeText(urlInput.value);
        const feedback = document.getElementById('copy-feedback-msg');
        feedback.textContent = '✓ Copied RSS URL to clipboard! Paste into Fountain or Pocket Casts.';
        setTimeout(() => { feedback.textContent = ''; }, 4000);
      });

      document.getElementById('generate-episode-btn').addEventListener('click', async () => {
        const btn = document.getElementById('generate-episode-btn');
        btn.textContent = 'Synthesizing Episode...';
        btn.disabled = true;
        try {
          const res = await API.generateEpisode();
          alert(`New episode synthesized! #${res.episode_number}: ${res.title}`);
          this.loadPodcastEpisodes();
        } catch (e) {
          alert(`Podcast generation error: ${e.message}`);
        } finally {
          btn.textContent = '🎙️ Synthesize New Episode';
          btn.disabled = false;
        }
      });
    },

    async loadPodcastEpisodes() {
      const container = document.getElementById('episodes-archive-container');
      container.innerHTML = '<div style="padding: 20px; color: var(--text-muted);">Loading episodes...</div>';

      try {
        const episodes = await API.getEpisodes();
        container.innerHTML = '';

        if (!episodes || episodes.length === 0) {
          container.innerHTML = '<div style="padding: 30px; text-align: center; color: var(--text-muted);">No podcast episodes generated yet. Click "Synthesize New Episode".</div>';
          return;
        }

        episodes.forEach(ep => {
          const card = document.createElement('div');
          card.className = 'episode-card';
          
          const chaptersCount = (ep.chapters || []).length;
          
          card.innerHTML = `
            <div>
              <div style="font-family: var(--font-mono); font-size: 0.76rem; color: var(--accent-primary); margin-bottom: 4px;">
                EPISODE #${ep.episode_number} • ${Math.round(ep.duration_seconds / 60)} MINS • ${chaptersCount} CHAPTERS
              </div>
              <h3 class="serif-heading" style="font-size: 1.25rem; margin-bottom: 6px;">${ep.title}</h3>
              <p style="font-size: 0.88rem; color: var(--text-secondary);">${ep.description}</p>
            </div>
            <div style="display: flex; gap: 8px;">
              <button class="btn-primary play-ep-btn">
                <span>▶</span> Play
              </button>
            </div>
          `;

          card.querySelector('.play-ep-btn').addEventListener('click', () => {
            window.dossiaAudio.loadEpisode(
              ep.title,
              ep.audio_url,
              ep.chapters,
              ep.duration_seconds
            );
          });

          container.appendChild(card);
        });
      } catch (e) {
        container.innerHTML = `<div style="padding: 20px; color: red;">Error: ${e.message}</div>`;
      }
    },

    // --------------------------------------------------------------------------
    // --------------------------------------------------------------------------
    // View 4: Settings & Multi-LLM Provider Engine
    // --------------------------------------------------------------------------
    currentSettings: {},

    initSettingsView() {
      const providerSelect = document.getElementById('setting-llm-provider');
      providerSelect.addEventListener('change', () => {
        this.renderProviderFields(providerSelect.value);
      });

      document.getElementById('test-llm-btn').addEventListener('click', async () => {
        const testBtn = document.getElementById('test-llm-btn');
        const statusBox = document.getElementById('llm-test-status');
        const provider = providerSelect.value;

        testBtn.disabled = true;
        testBtn.innerHTML = '<span>⏳</span> Testing...';
        statusBox.textContent = 'Probing LLM endpoint...';
        statusBox.style.color = 'var(--text-muted)';

        try {
          // First save current form fields so test uses the latest inputs
          await this.saveCurrentSettingsForm(false);

          const res = await fetch('/api/settings/test-llm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider })
          });
          const result = await res.json();

          if (result.status === 'connected') {
            statusBox.innerHTML = `🟢 <strong>Connected</strong> to ${result.provider} (${result.latency_ms}ms) — Response: "${result.response}"`;
            statusBox.style.color = 'var(--accent-primary)';
          } else {
            statusBox.innerHTML = `🟡 <strong>Fallback Active</strong>: ${result.message} (${result.latency_ms}ms)`;
            statusBox.style.color = '#e6a23c';
          }
        } catch (e) {
          statusBox.innerHTML = `🔴 <strong>Error</strong>: ${e.message}`;
          statusBox.style.color = 'red';
        } finally {
          testBtn.disabled = false;
          testBtn.innerHTML = '<span>🧪</span> Test Connection';
        }
      });

      document.getElementById('settings-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.saveCurrentSettingsForm(true);
      });

      document.getElementById('add-source-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('new-source-name').value;
        const feed_url = document.getElementById('new-source-url').value;
        const category = document.getElementById('new-source-cat').value;
        await API.addSource({ name, feed_url, category });
        document.getElementById('new-source-name').value = '';
        document.getElementById('new-source-url').value = '';
        this.loadSettings();
      });
    },

    renderProviderFields(provider) {
      const container = document.getElementById('provider-fields-container');
      const s = this.currentSettings || {};

      if (provider === 'openai') {
        container.innerHTML = `
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">OpenAI API Key</label>
            <input type="password" id="setting-openai-key" class="qa-input" style="width: 100%;" placeholder="${s.openai_api_key_masked || 'sk-...'}">
          </div>
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">Model Identifier</label>
            <input type="text" id="setting-openai-model" class="qa-input" style="width: 100%;" value="${s.openai_model || 'gpt-4o-mini'}" placeholder="gpt-4o, gpt-4o-mini, o3-mini">
          </div>
        `;
      } else if (provider === 'anthropic') {
        container.innerHTML = `
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">Anthropic Claude API Key</label>
            <input type="password" id="setting-anthropic-key" class="qa-input" style="width: 100%;" placeholder="${s.anthropic_api_key_masked || 'sk-ant-...'}">
          </div>
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">Model Identifier</label>
            <input type="text" id="setting-anthropic-model" class="qa-input" style="width: 100%;" value="${s.anthropic_model || 'claude-3-5-sonnet-20241022'}" placeholder="claude-3-7-sonnet-20250219, claude-3-5-haiku-20241022">
          </div>
        `;
      } else if (provider === 'openrouter') {
        container.innerHTML = `
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">OpenRouter API Key</label>
            <input type="password" id="setting-openrouter-key" class="qa-input" style="width: 100%;" placeholder="${s.openrouter_api_key_masked || 'sk-or-...'}">
          </div>
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">Model Identifier</label>
            <input type="text" id="setting-openrouter-model" class="qa-input" style="width: 100%;" value="${s.openrouter_model || 'deepseek/deepseek-r1'}" placeholder="deepseek/deepseek-r1, meta-llama/llama-3.3-70b-instruct">
          </div>
        `;
      } else if (provider === 'custom') {
        container.innerHTML = `
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">Custom API Base URL</label>
            <input type="text" id="setting-custom-url" class="qa-input" style="width: 100%;" value="${s.custom_base_url || 'http://localhost:8080/v1'}" placeholder="http://localhost:8080/v1">
          </div>
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">Model Identifier</label>
            <input type="text" id="setting-custom-model" class="qa-input" style="width: 100%;" value="${s.custom_model || 'default'}" placeholder="model name">
          </div>
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">API Key (Optional)</label>
            <input type="password" id="setting-custom-key" class="qa-input" style="width: 100%;" placeholder="${s.custom_api_key_masked || 'Bearer token'}">
          </div>
        `;
      } else {
        // Default: hermes
        container.innerHTML = `
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">Hermes / VPS API Base URL</label>
            <input type="text" id="setting-hermes-url" class="qa-input" style="width: 100%;" value="${s.hermes_base_url || 'http://localhost:11434/v1'}" placeholder="http://your-vps-ip:11434/v1">
          </div>
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">Hermes Model Identifier</label>
            <input type="text" id="setting-hermes-model" class="qa-input" style="width: 100%;" value="${s.hermes_model || 'hermes-3-llama-3.1-8b'}" placeholder="hermes-3-llama-3.1-8b">
          </div>
          <div>
            <label style="font-size: 0.82rem; font-weight: 600; display: block; margin-bottom: 6px;">API Key (Optional)</label>
            <input type="password" id="setting-hermes-key" class="qa-input" style="width: 100%;" placeholder="${s.hermes_api_key_masked || 'Bearer token'}">
          </div>
        `;
      }
    },

    async saveCurrentSettingsForm(showAlert = true) {
      const provider = document.getElementById('setting-llm-provider').value;
      const payload = { llm_provider: provider };

      if (provider === 'openai') {
        const key = document.getElementById('setting-openai-key')?.value;
        const model = document.getElementById('setting-openai-model')?.value;
        if (key) payload.openai_api_key = key;
        if (model) payload.openai_model = model;
      } else if (provider === 'anthropic') {
        const key = document.getElementById('setting-anthropic-key')?.value;
        const model = document.getElementById('setting-anthropic-model')?.value;
        if (key) payload.anthropic_api_key = key;
        if (model) payload.anthropic_model = model;
      } else if (provider === 'openrouter') {
        const key = document.getElementById('setting-openrouter-key')?.value;
        const model = document.getElementById('setting-openrouter-model')?.value;
        if (key) payload.openrouter_api_key = key;
        if (model) payload.openrouter_model = model;
      } else if (provider === 'custom') {
        const url = document.getElementById('setting-custom-url')?.value;
        const model = document.getElementById('setting-custom-model')?.value;
        const key = document.getElementById('setting-custom-key')?.value;
        if (url) payload.custom_base_url = url;
        if (model) payload.custom_model = model;
        if (key) payload.custom_api_key = key;
      } else {
        const url = document.getElementById('setting-hermes-url')?.value;
        const model = document.getElementById('setting-hermes-model')?.value;
        const key = document.getElementById('setting-hermes-key')?.value;
        if (url) payload.hermes_base_url = url;
        if (model) payload.hermes_model = model;
        if (key) payload.hermes_api_key = key;
      }

      await API.saveSettings(payload);
      if (showAlert) alert('Settings saved successfully!');
      await this.loadSettings();
    },

    async loadSettings() {
      try {
        const data = await API.getSettings();
        this.currentSettings = data;

        const providerSelect = document.getElementById('setting-llm-provider');
        if (data.llm_provider) {
          providerSelect.value = data.llm_provider;
        }
        this.renderProviderFields(providerSelect.value);

        const list = document.getElementById('sources-list-container');
        list.innerHTML = '';
        (data.sources || []).forEach(src => {
          const item = document.createElement('div');
          item.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: var(--bg-surface-elevated); border-radius: var(--radius-md); font-size: 0.85rem;';
          item.innerHTML = `
            <div>
              <strong>${src.name}</strong> <span style="color: var(--text-muted);">(${src.category})</span>
              <div style="font-size: 0.74rem; font-family: var(--font-mono); color: var(--text-muted);">${src.feed_url}</div>
            </div>
            <button class="icon-btn delete-src-btn" style="width: 24px; height: 24px;" title="Delete">✕</button>
          `;
          item.querySelector('.delete-src-btn').addEventListener('click', async () => {
            if (confirm(`Remove source ${src.name}?`)) {
              await API.deleteSource(src.id);
              this.loadSettings();
            }
          });
          list.appendChild(item);
        });
      } catch (e) {
        console.error('Failed to load settings:', e);
      }
    },

    // --------------------------------------------------------------------------
    // Cmd+K Universal Search Modal
    // --------------------------------------------------------------------------
    initSearchModal() {
      const overlay = document.getElementById('search-modal-overlay');
      const input = document.getElementById('search-modal-input');
      const openBtn = document.getElementById('open-search-btn');
      const resultsContainer = document.getElementById('search-results-container');

      const openSearch = () => {
        overlay.classList.add('active');
        input.focus();
        input.select();
      };

      const closeSearch = () => {
        overlay.classList.remove('active');
      };

      openBtn.addEventListener('click', openSearch);
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeSearch();
      });

      document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
          e.preventDefault();
          if (overlay.classList.contains('active')) closeSearch();
          else openSearch();
        }
        if (e.key === 'Escape' && overlay.classList.contains('active')) {
          closeSearch();
        }
      });

      let debounceTimeout = null;
      input.addEventListener('input', () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(async () => {
          const q = input.value.trim();
          if (!q) {
            resultsContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted);">Type keywords to search across articles.</div>';
            return;
          }

          resultsContainer.innerHTML = '<div style="padding: 16px; color: var(--text-muted);">Searching full-text database...</div>';
          try {
            const res = await API.getArticles('all', q, 15);
            if (!res.articles || res.articles.length === 0) {
              resultsContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-muted);">No results matching "${q}".</div>`;
              return;
            }

            resultsContainer.innerHTML = '';
            res.articles.forEach(art => {
              const item = document.createElement('div');
              item.className = 'search-result-item';
              item.innerHTML = `
                <div style="font-size: 0.72rem; font-family: var(--font-mono); color: var(--accent-primary);">${art.publisher || 'FEED'}</div>
                <div style="font-size: 0.95rem; font-weight: 600;">${art.title}</div>
                <div style="font-size: 0.8rem; color: var(--text-muted);">${art.summary ? art.summary.substring(0, 100) + '...' : ''}</div>
              `;
              item.addEventListener('click', () => {
                closeSearch();
                window.dossiaReader.open(art.id);
              });
              resultsContainer.appendChild(item);
            });
          } catch (e) {
            resultsContainer.innerHTML = `<div style="padding: 16px; color: red;">Search error: ${e.message}</div>`;
          }
        }, 200);
      });
    }
  };

  App.init();
});
