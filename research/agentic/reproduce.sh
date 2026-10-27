#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
# Reuse an existing isolated environment, or install the pinned research dependencies.
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -r research/agentic/requirements.txt
fi
PY=.venv/bin/python
OUT="${1:-research/agentic/results/reproduction-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$OUT"
"$PY" -m pytest research/agentic/tests -q | tee "$OUT/tests.txt"
"$PY" -m agentic_taed.run_original_poc --out "$OUT/original"
"$PY" -m agentic_taed.run_original_poc --out "$OUT/paired" --clean-pairs
"$PY" -m agentic_taed.evaluate --out "$OUT/stress" --repeats 3
"$PY" -m agentic_taed.run_agentdojo --out "$OUT/agentdojo"
"$PY" -m agentic_taed.visualize "$OUT/agentdojo"
