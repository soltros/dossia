# Dossia

A news intelligence dashboard and Podcasting 2.0 aggregator. Dossia ingests curated technical feeds and community discussions, extracts full-text content into a local SQLite repository, synthesizes daily editorial dossiers using an LLM backend (Hermes), and exposes a Podcasting 2.0 RSS feed with structured chapter markers and transcripts.

## Features

- **Editorial Synthesis**: Clusters incoming articles by topic and generates structured executive briefings with source citations.
- **Podcasting 2.0 Distribution**: Generates an RSS 2.0 feed (`/podcast.xml`) containing `<podcast:chapters>` and `<podcast:transcript>` metadata compatible with podcast clients such as Fountain, Pocket Casts, and AntennaPod.
- **Full-Text Ingestion**: HTML sanitization and readability extraction that strips navigation, advertisements, and trackers into clean Markdown.
- **In-App Reader**: Slide-over reader view with full-text display, summary callouts, and contextual question answering.
- **Search and Retrieval**: SQLite FTS5 full-text search indexing across all ingested article bodies, titles, and tags.

## Architecture

```
[ Ingestion Layer ]
  - RSS / Atom feeds (Engineering blogs, journals, community hubs)
  - Full-text HTML sanitization and Markdown extraction
        |
        v
[ Database Layer ]
  - SQLite with WAL mode
  - FTS5 virtual table for keyword search
  - Tables: articles, sources, dossiers, story_clusters, podcast_episodes
        |
        v
[ Editorial Engine (Hermes) ]
  - OpenAI-compatible API endpoint
  - Thematic clustering, executive summary generation, and podcast scripting
        |
        v
[ Delivery Layer ]
  - FastAPI web service
  - Static editorial frontend with responsive reader drawer and audio controls
  - Podcasting 2.0 RSS XML generator
```

## Project Layout

```
dossia/
├── backend/
│   ├── config.py           # Application settings and environment variables
│   ├── database.py         # SQLite schema initialization and connection helpers
│   ├── main.py             # FastAPI entry point and router registration
│   ├── ingest/
│   │   ├── cleaner.py      # HTML parsing and Markdown normalization
│   │   └── rss.py          # Feed fetcher and article storage
│   ├── hermes/
│   │   ├── client.py       # OpenAI-compatible API client with fallback handler
│   │   └── synthesizer.py  # Daily dossier clustering and synthesis
│   ├── podcast/
│   │   ├── rss_builder.py  # Podcasting 2.0 XML generator
│   │   ├── script_writer.py# Podcast script and chapter timestamp generator
│   │   └── tts_engine.py   # Text-to-speech audio synthesis interface
│   └── routes/             # REST and XML endpoint handlers
├── static/                 # Frontend assets (HTML, CSS, JavaScript)
├── docs/                   # Architecture notes and whitepaper
├── requirements.txt        # Python package dependencies
└── run.sh                  # Application launcher script
```

## Getting Started

### Prerequisites

- Python 3.10+
- SQLite 3 (with FTS5 support)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/soltros/dossia.git
   cd dossia
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   ./run.sh
   ```

   The dashboard will be available at `http://127.0.0.1:8000`.

### Configuration

Configuration can be set with environment variables or in a local `.env` file. The `.env` file and persisted local settings are excluded from Git. By default, Dossia listens only on `127.0.0.1`; set `DOSSIA_HOST=0.0.0.0` only when you intentionally want other devices on your network to reach it.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `HERMES_BASE_URL` | `http://localhost:11434/v1` | Base URL of the OpenAI-compatible Hermes LLM endpoint |
| `HERMES_API_KEY` | `""` | Optional Bearer token for LLM API authentication |
| `HERMES_MODEL` | `hermes-3-llama-3.1-8b` | Model identifier passed to the LLM backend |
| `TTS_API_URL` | `""` | Optional remote TTS endpoint (`/audio/speech`) |

### Use GPT with your ChatGPT plan

In Settings, select **ChatGPT Plan** and choose **Continue with ChatGPT**. Sign in in the browser and approve Dossia’s request to use eligible ChatGPT plan allowance. This open-source, locally run app uses OpenAI’s documented Sign in with ChatGPT OAuth/PKCE flow and the Responses API. Dossia stores OAuth credentials in a local, owner-only file under `data/`; credentials are not sent to the browser or committed to Git. You can disconnect the account from Dossia Settings, and review or limit usage in ChatGPT Settings → Usage.

The ChatGPT plan flow is separate from **OpenAI API Key** mode. For API billing instead, enter an API key in Settings or set `OPENAI_API_KEY` in `.env`; when that key is present and `LLM_PROVIDER` is unset, API mode is selected by default. The default API model is `gpt-4o-mini`; set `OPENAI_MODEL` to change it.

ChatGPT plan usage is subject to the eligibility, usage limits, and preview limitations for your account. OAuth authentication alone does not guarantee the plan-use permission; Dossia verifies that OpenAI granted the required scope before sending inference requests. The app sends these requests with response storage disabled and streaming enabled, as required by OpenAI’s local open-source flow.

Other useful local settings: `DOSSIA_HOST` (default `127.0.0.1`), `DOSSIA_PORT` (default `8000`), and `DOSSIA_CORS_ORIGINS` (comma-separated browser origins allowed to call the API). Use `http://127.0.0.1:8000` for the local dashboard; Sign in with ChatGPT requires a loopback callback on `127.0.0.1`.

## API Endpoints

- `GET /` - Web dashboard
- `GET /podcast.xml` - Podcasting 2.0 RSS feed
- `GET /api/dossiers/latest` - Latest synthesized editorial dossier
- `POST /api/dossiers/generate` - Trigger new dossier synthesis
- `GET /api/articles` - Query ingested articles with optional `q` (FTS) and `category` filters
- `POST /api/articles/ingest` - Trigger feed polling across all registered sources
- `GET /api/episodes` - List generated podcast episodes with chapter metadata
- `POST /api/hermes/ask` - Contextual question answering for article text

## License

MIT
