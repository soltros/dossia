# Dossia 🗞️🎙️

> **Autonomous News Intelligence, Editorial Dossiers & Podcasting 2.0 Engine**

Dossia transforms how you consume technical, scientific, and industry news. Instead of overwhelming you with an endless RSS firehose or truncated stubs, Dossia maintains a curated knowledge reservoir, uses **Hermes AI** as an autonomous Editor-in-Chief to synthesize the highest-signal stories into rich daily dossiers, and publishes an automated **Podcasting 2.0 RSS feed** for listening on the go (compatible with Fountain, Pocket Casts, and Apple Podcasts).

---

## ✨ Core Pillars

- **📰 The Daily Intelligence Dossier**: Editorial executive briefings that synthesize stories across multiple sources rather than dumping disjointed links.
- **🎧 Podcasting 2.0 RSS Publishing**: Automatically generates spoken morning briefings with synchronized `<podcast:chapters>` and `<podcast:transcript>` tags for apps like Fountain.
- **📖 Zero-Distraction In-App Reader**: Auto-extracts full-text articles with zero ads, cookie banners, or paywall clutter.
- **💬 Hermes In-Margin Q&A**: Highlight any paragraph in a report to ask Hermes questions, request technical deep dives, or verify claims.
- **📚 Curated Reservoir Explorer**: Search across thousands of ingested full-text technical articles and papers with low-latency search.

---

## 🏛️ System Architecture

```
[ Curated Knowledge Reservoir (Database) ]
   ├── High-signal engineering blogs, Hacker News top links, arXiv, releases
   └── Background readability engine (extracts clean full-text markdown)
                   │
                   ▼
[ Hermes Editorial Engine ]
   ├── Clusters stories & writes the "Daily Intelligence Dossier" (Rich Report)
   └── Drafts a lively conversational podcast script with chapter timestamps
                   │
                   ▼
[ Voice Synthesizer & Podcast 2.0 Publisher ]
   ├── Synthesizes audio MP3 (via Kokoro TTS / Piper / OpenAI TTS)
   ├── Emits standard `/podcast.xml` (with <podcast:chapters> & <podcast:transcript>)
   └── Subscribable directly in Fountain, Pocket Casts, or Apple Podcasts
                   │
                   ▼
[ Modern Editorial Web Dashboard ]
   ├── 📰 The Editorial Dossier (High-craft typography, source pills, executive summaries)
   ├── 🎧 In-Dashboard Audio Player (Synchronized transcript, speed controls, chapter jumps)
   ├── 📖 In-App Full-Text Reader (Clean, distraction-free longform reading)
   ├── 💬 Hermes Margin Chat (Highlight text to ask Hermes questions)
   └── 📱 Podcast RSS Feed Link & QR Code (One-click subscription into Fountain)
```

---

## 📁 Repository Structure

```
dossia/
├── backend/            # Ingestion worker, SQLite database & Hermes pipeline
├── frontend/           # Modern editorial web dashboard
├── podcast/            # Podcasting 2.0 XML generator & audio manager
└── docs/               # Architecture whitepaper & API specifications
```

---

## 📄 License
MIT
