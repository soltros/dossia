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
    // View 1: The Daily Dossier
    // --------------------------------------------------------------------------
    initDossierView() {
      document.getElementById('synth-new-dossier-btn').addEventListener('click', async () => {
        const btn = document.getElementById('synth-new-dossier-btn');
        btn.innerHTML = '<span>⏳</span> Synthesizing...';
        btn.disabled = true;
        try {
          await API.generateDossier('morning');
          await this.loadDossier();
        } catch (e) {
          alert(`Synthesis error: ${e.message}`);
        } finally {
          btn.innerHTML = '<span>✨</span> Re-Synthesize with Hermes';
          btn.disabled = false;
        }
      });

      document.getElementById('listen-dossier-btn').addEventListener('click', () => {
        if (!this.currentDossier) return;
        const textToRead = `${this.currentDossier.title}. Executive summary: ${this.currentDossier.executive_tldr.join('. ')}.`;
        window.dossiaAudio.playSpokenText(this.currentDossier.title, textToRead);
      });
    },

    async loadDossier() {
      const container = document.getElementById('story-clusters-container');
      const bulletsList = document.getElementById('dossier-bullets-list');

      try {
        const dossier = await API.getLatestDossier();
        this.currentDossier = dossier;

        document.getElementById('dossier-title-text').textContent = dossier.title || 'The Daily Intelligence Dossier';
        document.getElementById('dossier-edition-label').textContent = `${dossier.edition_type || 'Morning'} Edition • ${dossier.edition_date || 'Today'}`;

        // Render executive bullets
        bulletsList.innerHTML = '';
        (dossier.executive_tldr || []).forEach(bullet => {
          const li = document.createElement('li');
          li.textContent = bullet;
          bulletsList.appendChild(li);
        });

        // Render story clusters
        container.innerHTML = '';
        (dossier.story_clusters || []).forEach(cluster => {
          const card = document.createElement('article');
          card.className = 'story-capsule';

          const sourcesHtml = (cluster.sources || []).map(s => `
            <button class="source-pill" data-article-id="${s.id}">
              <span>📄</span> ${s.publisher || 'Source'}: ${s.title.substring(0, 32)}...
            </button>
          `).join('');

          const takeawaysHtml = (cluster.key_takeaways || []).map(t => `<li>${t}</li>`).join('');

          card.innerHTML = `
            <div class="capsule-top">
              <span class="capsule-category">${cluster.category || 'General'}</span>
              <span class="signal-badge">${cluster.signal_badge || 'High Signal'}</span>
            </div>
            <h2 class="capsule-headline serif-heading">${cluster.headline}</h2>
            <p class="capsule-narrative">${cluster.narrative_summary}</p>
            
            <div class="capsule-takeaways">
              <div class="takeaways-title">Key Developments & Technical Implications</div>
              <ul class="takeaways-list">
                ${takeawaysHtml}
              </ul>
            </div>

            <div class="capsule-footer">
              <div class="capsule-sources">
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
            window.dossiaAudio.playSpokenText(cluster.headline, `${cluster.headline}. ${cluster.narrative_summary}`);
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
        bulletsList.innerHTML = `<li>Could not load dossier: ${e.message}</li>`;
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
      document.querySelectorAll('#category-filters-container .filter-pill').forEach(pill => {
        pill.addEventListener('click', () => {
          document.querySelectorAll('#category-filters-container .filter-pill').forEach(p => p.classList.remove('active'));
          pill.classList.add('active');
          this.loadReservoirArticles(pill.getAttribute('data-cat'));
        });
      });

      document.getElementById('reservoir-sync-btn').addEventListener('click', async () => {
        const btn = document.getElementById('reservoir-sync-btn');
        btn.textContent = 'Ingesting...';
        await API.triggerIngest();
        btn.textContent = '⚡ Ingest All Sources';
        this.loadReservoirArticles();
      });
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
    // View 4: Settings & Feed Sources
    // --------------------------------------------------------------------------
    initSettingsView() {
      document.getElementById('settings-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
          hermes_base_url: document.getElementById('setting-hermes-url').value,
          hermes_model: document.getElementById('setting-hermes-model').value,
          hermes_api_key: document.getElementById('setting-hermes-key').value
        };
        await API.saveSettings(payload);
        alert('Settings saved successfully!');
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

    async loadSettings() {
      try {
        const data = await API.getSettings();
        document.getElementById('setting-hermes-url').value = data.hermes_base_url || '';
        document.getElementById('setting-hermes-model').value = data.hermes_model || '';
        
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
        console.error('Settings load error:', e);
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
