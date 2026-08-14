---
name: dossia-editorial-synthesis
description: >-
  Autonomous editorial intelligence synthesizer, category briefing generator, and testing copilot for Dossia.
  Use to synthesize high-signal daily dossiers and category-specific intelligence briefings (Linux & Kernel,
  Local AI, Self-Hosting, Digital Privacy, Game Dev, Gaming, Labor & Politics, Culture, Hardware & Electronics,
  Independent Music, Food Science & Fermentation), run ingestion and feed testing, evaluate LLM provider hooks,
  and directly query or inject briefing records into the Dossia SQLite database.
---

# Dossia Editorial Synthesis & Testing Skill

This skill equips the Antigravity agent to act as **Hermes / Editor-in-Chief** and **QA Test Copilot** for the Dossia intelligence platform.

---

## 1. Editorial Voice and Synthesis Standards

When synthesizing dossiers or category briefings, strictly adhere to these standards:
- **Tone**: Dense, technical, precise, and voice-driven. Skip corporate press-release hype, marketing fluff, and generic AI filler.
- **Signal**: Prioritize concrete architecture decisions, metrics (latency, bandwidth, memory overhead), diffs, breaking changes, and structural implications.
- **Formatting**:
  - **Executive 60-Second Briefing**: 3 high-impact bullet points summarizing the most critical signals.
  - **Story Clusters**: Group related articles by thematic development, provide a 2-paragraph narrative synthesis, and 3 specific bullet-point takeaways.
  - **Badges**: Use signal indicators (`High Signal`, `Breakthrough`, `Security Alert`, `Architecture`, `Ecosystem`).

---

## 2. Supported Domain Categories (11 Total)

1. `Linux & Kernel`: Hardware benchmarks, Vulkan/Mesa drivers, kernel architecture, distro releases, and sysadmin tooling.
2. `Local AI & Machine Learning`: Local LLMs, GGUF/AWQ quantization, PyTorch, LoRA fine-tuning, KV-cache scaling, and open weights.
3. `Self-Hosting & HomeLab`: Proxmox VE, container architecture, high-availability storage, reverse proxies, and ActivityPub.
4. `Privacy & Cryptography`: Applied crypto, threat modeling, binary exploitation, zero-knowledge proofs, and packet inspection.
5. `Game Dev & Engine Tech`: Shader math, raymarching, game loops, procedural generation, rendering passes, and memory patterns.
6. `Gaming & Reviews`: PC/indie deep-dives, hardware performance breakdowns, studio economics, and labor trends.
7. `Labor & Politics`: Democratic socialist theory, union organizing, shop-floor contract fights, and investigative reporting on corporate lobbying.
8. `Culture & Criticism`: Media literacy, television/film deconstructions, PR manipulation analysis, and working-crew perspectives.
9. `Hardware & Electronics`: Circuit design, ESP32/RP2040 microcontrollers, single-board computers, bare-metal C, and reverse engineering.
10. `Independent Music`: Underground metal, DIY punk, avant-garde rock, and scene reports without commercial PR bias.
11. `Food Science & Fermentation`: Sourdough rheology, wild yeast kinetics, protein denaturing, and Maillard reaction physics.

---

## 3. How to Synthesize a Briefing for the User

When the user asks you to synthesize a briefing for any category:

### Method A: Direct CLI Execution
Run the Dossia CLI to generate and persist the briefing in SQLite:
```bash
cd /home/derrik/Projects/dossia
.venv/bin/python -m backend.cli synthesize --category "<Category Name>"
```

### Method B: Programmatic Python Generation & Injection
Execute Python code to query the latest database articles, synthesize domain intelligence, and commit to `dossiers` and `story_clusters`:
```python
import asyncio
from backend.hermes.synthesizer import generate_daily_dossier

dossier = asyncio.run(generate_daily_dossier(edition_type="morning", category="<Category Name>"))
print(f"Generated Briefing: {dossier['title']}")
```

---

## 4. Testing & Verification Runbook

Use these procedures when performing joint testing with the user:

### Ingestion Testing
Test RSS feed ingestion across all 110 publications:
```bash
cd /home/derrik/Projects/dossia
.venv/bin/python -m backend.cli ingest
```

### Database Verification
Inspect article counts and category breakdowns in SQLite:
```bash
cd /home/derrik/Projects/dossia
.venv/bin/python -c "
from backend.database import get_db_connection
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT s.category, COUNT(a.id) FROM sources s LEFT JOIN articles a ON s.id = a.source_id GROUP BY s.category;')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} articles')
conn.close()
"
```

### Multi-LLM Provider Testing
Probe LLM connectivity across configured providers (OpenAI, Anthropic Claude, OpenRouter, Hermes):
```bash
cd /home/derrik/Projects/dossia
.venv/bin/python -c "
import asyncio
from backend.hermes.client import LLMClient
client = LLMClient(provider='openai') # or 'anthropic', 'openrouter', 'hermes'
resp = asyncio.run(client.generate_chat_completion([{'role': 'user', 'content': 'Respond with: OK'}]))
print('Provider response:', resp)
"
```

### Server & Audio Testing
Test neural speech synthesis (`edge-tts`) and Podcasting 2.0 XML:
```bash
cd /home/derrik/Projects/dossia
.venv/bin/python -c "
import asyncio
from backend.podcast.tts_engine import TTSEngine
tts = TTSEngine()
mp3_path = asyncio.run(tts.synthesize_speech('Testing Dossia neural speech pipeline.', 'test_skill.mp3'))
print('Synthesized test audio:', mp3_path)
"
```
