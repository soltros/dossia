/**
 * Slide-Over Full-Text Reader & Hermes Margin Assistant
 */
class DossiaReaderDrawer {
  constructor() {
    this.overlay = document.getElementById('reader-overlay');
    this.drawer = document.getElementById('reader-drawer');
    this.closeBtn = document.getElementById('reader-close-btn');
    this.listenBtn = document.getElementById('reader-listen-btn');
    this.sourceLink = document.getElementById('reader-source-link');
    
    this.publisherLabel = document.getElementById('reader-publisher-label');
    this.titleEl = document.getElementById('reader-title-text');
    this.bylineEl = document.getElementById('reader-byline-text');
    this.tldrContent = document.getElementById('reader-tldr-content');
    this.markdownBody = document.getElementById('reader-markdown-body');
    
    this.qaInput = document.getElementById('reader-qa-input');
    this.qaSendBtn = document.getElementById('reader-qa-send-btn');
    this.qaResponseBox = document.getElementById('reader-qa-response-box');

    this.currentArticle = null;
    this.initEvents();
  }

  initEvents() {
    this.closeBtn.addEventListener('click', () => this.close());
    this.overlay.addEventListener('click', () => this.close());
    
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.drawer.classList.contains('active')) {
        this.close();
      }
    });

    this.listenBtn.addEventListener('click', () => {
      if (this.currentArticle) {
        window.dossiaAudio.playSpokenText(this.currentArticle.title, this.currentArticle.clean_content || this.currentArticle.summary);
      }
    });

    this.qaSendBtn.addEventListener('click', () => this.submitQA());
    this.qaInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.submitQA();
    });
  }

  async open(articleId) {
    this.overlay.classList.add('active');
    this.drawer.classList.add('active');
    document.body.style.overflow = 'hidden';

    this.titleEl.textContent = 'Loading article...';
    this.publisherLabel.textContent = 'HERMES PARSER';
    this.bylineEl.textContent = '';
    this.tldrContent.textContent = 'Synthesizing 3-bullet executive summary...';
    this.markdownBody.innerHTML = '<p>Extracting full readability text...</p>';
    this.qaResponseBox.style.display = 'none';
    this.qaInput.value = '';

    try {
      const article = await API.getArticle(articleId);
      this.currentArticle = article;
      this.renderArticle(article);
    } catch (e) {
      this.titleEl.textContent = 'Failed to load article';
      this.markdownBody.innerHTML = `<p style="color: var(--accent-primary);">Could not retrieve article content: ${e.message}</p>`;
    }
  }

  renderArticle(article) {
    this.publisherLabel.textContent = article.publisher || 'EDITORIAL FEED';
    this.titleEl.textContent = article.title;
    this.bylineEl.textContent = `By ${article.author || 'Staff'} • ${article.reading_time_minutes || 3} min read • Published ${article.published_at ? article.published_at.substring(0, 10) : ''}`;
    this.sourceLink.href = article.url;

    // TL;DR summary
    if (article.summary) {
      this.tldrContent.innerHTML = `<p>${this.escapeHtml(article.summary)}</p>`;
    } else {
      this.tldrContent.innerHTML = '<p>Full analytical piece available below.</p>';
    }

    // Render markdown content
    this.markdownBody.innerHTML = this.simpleMarkdownToHtml(article.clean_content || article.summary);
  }

  close() {
    this.overlay.classList.remove('active');
    this.drawer.classList.remove('active');
    document.body.style.overflow = '';
  }

  async submitQA() {
    const question = this.qaInput.value.trim();
    if (!question || !this.currentArticle) return;

    this.qaSendBtn.disabled = true;
    this.qaSendBtn.textContent = 'Thinking...';
    this.qaResponseBox.style.display = 'block';
    this.qaResponseBox.innerHTML = '<span style="color: var(--text-muted);">Hermes is analyzing context...</span>';

    try {
      const res = await API.askHermes(this.currentArticle.clean_content || this.currentArticle.summary, question);
      this.qaResponseBox.innerHTML = `
        <div style="background: var(--bg-surface-elevated); border-left: 3px solid var(--accent-primary); padding: 12px 16px; border-radius: var(--radius-md);">
          <strong>Hermes:</strong> ${this.simpleMarkdownToHtml(res.answer)}
        </div>
      `;
    } catch (e) {
      this.qaResponseBox.innerHTML = `<span style="color: red;">Error: ${e.message}</span>`;
    } finally {
      this.qaSendBtn.disabled = false;
      this.qaSendBtn.textContent = 'Ask';
    }
  }

  simpleMarkdownToHtml(md) {
    if (!md) return '';
    let html = this.escapeHtml(md);

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3 class="serif-heading" style="font-size: 1.3rem; margin: 1.2em 0 0.4em;">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="serif-heading" style="font-size: 1.6rem; margin: 1.4em 0 0.5em;">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 class="serif-heading" style="font-size: 1.9rem; margin: 1.5em 0 0.6em;">$1</h1>');

    // Code blocks
    html = html.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>');
    html = html.replace(/`([^`]+)`/gim, '<code>$1</code>');

    // Bold & Italics
    html = html.replace(/\*\*([^*]+)\*\*/gim, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/gim, '<em>$1</em>');

    // Paragraphs
    html = html.replace(/\n\n+/g, '</p><p>');
    return `<p>${html}</p>`;
  }

  escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

window.dossiaReader = new DossiaReaderDrawer();
