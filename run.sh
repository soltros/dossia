#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

echo "🗞️ Starting Dossia Server on http://127.0.0.1:${DOSSIA_PORT:-8000} ..."
echo "🎙️ Podcasting 2.0 RSS Feed live at http://127.0.0.1:${DOSSIA_PORT:-8000}/podcast.xml"
exec .venv/bin/python -m uvicorn backend.main:app --host "${DOSSIA_HOST:-127.0.0.1}" --port "${DOSSIA_PORT:-8000}" --reload
