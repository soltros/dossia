/**
 * Persistent Audio Player & Podcast 2.0 Chapter Engine
 */
class DossiaAudioPlayer {
  constructor() {
    this.audioEl = document.getElementById('global-audio-element');
    this.playPauseBtn = document.getElementById('audio-play-pause-btn');
    this.scrubSlider = document.getElementById('audio-scrub-slider');
    this.currentTimeEl = document.getElementById('audio-current-time');
    this.durationTimeEl = document.getElementById('audio-duration-time');
    this.titleEl = document.getElementById('audio-player-title');
    this.chapterEl = document.getElementById('audio-player-chapter');
    this.chapterSelect = document.getElementById('audio-chapter-select');
    this.speedBtn = document.getElementById('audio-speed-btn');
    this.prevBtn = document.getElementById('audio-prev-chapter-btn');
    this.nextBtn = document.getElementById('audio-next-chapter-btn');

    this.currentChapters = [];
    this.currentSpeed = 1.0;
    this.speeds = [1.0, 1.25, 1.5, 2.0];
    this.isSpeechSynthesis = false;
    this.speechUtterance = null;

    this.initEvents();
  }

  initEvents() {
    this.playPauseBtn.addEventListener('click', () => this.togglePlay());
    this.speedBtn.addEventListener('click', () => this.cycleSpeed());
    this.chapterSelect.addEventListener('change', (e) => this.seekToTime(parseFloat(e.target.value)));
    
    this.prevBtn.addEventListener('click', () => this.skipChapter(-1));
    this.nextBtn.addEventListener('click', () => this.skipChapter(1));

    this.scrubSlider.addEventListener('input', (e) => {
      if (this.audioEl.duration) {
        const targetTime = (e.target.value / 100) * this.audioEl.duration;
        this.seekToTime(targetTime);
      }
    });

    this.audioEl.addEventListener('timeupdate', () => this.onTimeUpdate());
    this.audioEl.addEventListener('loadedmetadata', () => {
      this.durationTimeEl.textContent = this.formatTime(this.audioEl.duration);
    });
    this.audioEl.addEventListener('ended', () => {
      this.playPauseBtn.textContent = '▶';
    });
  }

  loadEpisode(title, audioUrl, chapters = [], durationSeconds = 0) {
    this.stopSpeech();
    this.isSpeechSynthesis = false;
    this.titleEl.textContent = title;
    this.currentChapters = chapters;
    this.updateChapterSelect(chapters);
    
    if (audioUrl) {
      this.audioEl.src = audioUrl;
      this.audioEl.playbackRate = this.currentSpeed;
      this.audioEl.play().then(() => {
        this.playPauseBtn.textContent = '⏸';
      }).catch(() => {
        this.playPauseBtn.textContent = '▶';
      });
    }

    if (durationSeconds) {
      this.durationTimeEl.textContent = this.formatTime(durationSeconds);
    }
  }

  sanitizeSpeechText(text) {
    if (!text) return '';
    let t = text;
    // 1. Unwrap markdown links: [Label](url) -> Label
    t = t.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1');

    // 2. Strip all remaining URLs, domains, and protocols
    t = t.replace(/https?:\/\/\S+/gi, '');
    t = t.replace(/www\.\S+/gi, '');
    t = t.replace(/mailto:\S+/gi, '');
    t = t.replace(/\S+@\S+\.\S+/g, '');
    
    // 3. Strip isolated URL paths & file extensions
    t = t.replace(/\(\/[^\)]+\)/g, '');
    t = t.replace(/\/[A-Za-z0-9_\-\.\/]{2,}/g, '');
    t = t.replace(/\.(php|html|htm|xml|json|rss|atom|asp|aspx|jsp)/gi, '');
    
    // 4. Clean brackets like [1], [2], [$], [#], but keep words
    t = t.replace(/\[\s*[\d\$#\*\-]+\s*\]/g, '');
    t = t.replace(/\[\s*\]/g, '');
    
    // 5. Clean version numbers and CVEs for natural reading
    t = t.replace(/\bCVE-(\d{4})-(\d+)\b/gi, 'C V E $1 $2');
    t = t.replace(/\bversion\s+v(\d+)/gi, 'version $1');
    t = t.replace(/\bv(\d+)\.(\d+)\.(\d+)\b/gi, 'version $1 point $2 point $3');
    t = t.replace(/\bv(\d+)\.(\d+)\b/gi, 'version $1 point $2');
    
    // 6. Strip markdown symbols, currencies, hashes, backticks, slashes, pipes
    t = t.replace(/[`*~_#|<>\/\\\^=+%\$]/g, ' ');
    t = t.replace(/[{}\[\]\(\)]/g, ' ');
    t = t.replace(/—|–|--+/g, ' — ');
    
    return t.replace(/\s+/g, ' ').trim();
  }

  async playSpokenText(title, text) {
    this.audioEl.pause();
    this.stopSpeech();
    this.isSpeechSynthesis = false;
    
    const cleanSpokenText = this.sanitizeSpeechText(text);
    const cleanTitle = this.sanitizeSpeechText(title);

    this.titleEl.textContent = `🎙️ ${cleanTitle}`;
    this.chapterEl.textContent = 'Synthesizing Neural Speech...';
    this.playPauseBtn.textContent = '⏳';
    this.currentChapters = [];
    this.chapterSelect.innerHTML = '<option>Full Audio</option>';

    try {
      // Use server-side neural voice synthesis with clean text
      const res = await API.speakText(cleanTitle, cleanSpokenText);
      if (res && res.audio_url) {
        this.chapterEl.textContent = 'Neural Broadcast Voice';
        this.audioEl.src = res.audio_url;
        this.audioEl.playbackRate = this.currentSpeed;
        await this.audioEl.play();
        this.playPauseBtn.textContent = '⏸';
        return;
      }
    } catch (err) {
      console.warn('Server TTS failed, attempting browser speech:', err);
    }

    // Fallback to browser SpeechSynthesis if server TTS is unreachable
    if ('speechSynthesis' in window) {
      this.isSpeechSynthesis = true;
      this.chapterEl.textContent = 'Browser Speech Engine';
      this.speechUtterance = new SpeechSynthesisUtterance(cleanSpokenText);
      this.speechUtterance.rate = this.currentSpeed;
      this.speechUtterance.onend = () => {
        this.playPauseBtn.textContent = '▶';
      };
      this.speechUtterance.onerror = (e) => {
        console.warn('Browser speech synthesis error:', e);
        this.playPauseBtn.textContent = '▶';
        this.chapterEl.textContent = 'Speech engine unavailable';
      };
      window.speechSynthesis.speak(this.speechUtterance);
      this.playPauseBtn.textContent = '⏸';
    } else {
      this.chapterEl.textContent = 'Speech synthesis unavailable';
      this.playPauseBtn.textContent = '▶';
    }
  }

  stopSpeech() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }

  togglePlay() {
    if (this.isSpeechSynthesis) {
      if (window.speechSynthesis.speaking) {
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume();
          this.playPauseBtn.textContent = '⏸';
        } else {
          window.speechSynthesis.pause();
          this.playPauseBtn.textContent = '▶';
        }
      }
      return;
    }

    if (this.audioEl.paused) {
      this.audioEl.play();
      this.playPauseBtn.textContent = '⏸';
    } else {
      this.audioEl.pause();
      this.playPauseBtn.textContent = '▶';
    }
  }

  cycleSpeed() {
    const nextIdx = (this.speeds.indexOf(this.currentSpeed) + 1) % this.speeds.length;
    this.currentSpeed = this.speeds[nextIdx];
    this.speedBtn.textContent = `${this.currentSpeed}x`;
    this.audioEl.playbackRate = this.currentSpeed;
    if (this.isSpeechSynthesis && this.speechUtterance) {
      this.speechUtterance.rate = this.currentSpeed;
    }
  }

  seekToTime(seconds) {
    this.audioEl.currentTime = seconds;
    this.onTimeUpdate();
  }

  skipChapter(direction) {
    if (!this.currentChapters.length) return;
    const curTime = this.audioEl.currentTime;
    let targetIdx = 0;

    for (let i = 0; i < this.currentChapters.length; i++) {
      if (this.currentChapters[i].start_seconds > curTime) {
        targetIdx = direction > 0 ? i : Math.max(0, i - 2);
        break;
      }
      if (i === this.currentChapters.length - 1 && direction < 0) {
        targetIdx = Math.max(0, i - 1);
      }
    }

    if (this.currentChapters[targetIdx]) {
      this.seekToTime(this.currentChapters[targetIdx].start_seconds);
    }
  }

  onTimeUpdate() {
    const cur = this.audioEl.currentTime;
    const dur = this.audioEl.duration || 1;
    this.currentTimeEl.textContent = this.formatTime(cur);
    this.scrubSlider.value = (cur / dur) * 100;

    // Determine current chapter
    if (this.currentChapters.length) {
      let currentCh = this.currentChapters[0].title;
      for (const ch of this.currentChapters) {
        if (cur >= ch.start_seconds) {
          currentCh = ch.title;
        }
      }
      this.chapterEl.textContent = currentCh;
    }
  }

  updateChapterSelect(chapters) {
    this.chapterSelect.innerHTML = '';
    if (!chapters || !chapters.length) {
      this.chapterSelect.innerHTML = '<option value="0">Chapters</option>';
      return;
    }
    chapters.forEach(ch => {
      const opt = document.createElement('option');
      opt.value = ch.start_seconds;
      opt.textContent = `${this.formatTime(ch.start_seconds)} - ${ch.title}`;
      this.chapterSelect.appendChild(opt);
    });
  }

  formatTime(secs) {
    if (isNaN(secs)) return '0:00';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  }
}

window.dossiaAudio = new DossiaAudioPlayer();
