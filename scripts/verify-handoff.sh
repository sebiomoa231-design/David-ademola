#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

printf '%s\n' '== Backend syntax and tests =='
cd "$ROOT_DIR"
python3 -m compileall -q app piper_tts.py voice_engine.py
pytest -q

printf '%s\n' '== Frontend typecheck, tests, and production build =='
cd "$ROOT_DIR/frontend"
npm run typecheck
npm test
npm run build

printf '%s\n' 'Handoff verification passed.'
