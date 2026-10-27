#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
TAED_PYTHON="${TAED_PYTHON:-python3}"
OUT="${1:?Usage: reproduce_offline.sh NEW_OUTPUT_DIRECTORY}"
mkdir "$OUT"
"$TAED_PYTHON" -m pytest research/agentic/tests research/agentic/v2/tests -q | tee "$OUT/tests.txt"
"$TAED_PYTHON" -m agentic_taed.v2.calibrate --out "$OUT/calibration"
"$TAED_PYTHON" -m agentic_taed.v2.diagnostics "$OUT/calibration"
"$TAED_PYTHON" -m agentic_taed.v2.validate_native --out "$OUT/native_compatibility.json"
# Explicitly offline: no provider calls even if the invoking shell has credentials.
env -u OPENAI_API_KEY -u TAED_MODEL "$TAED_PYTHON" -m agentic_taed.v2.run --out "$OUT/preflight" --calibration "$OUT/calibration/calibration.json"
"$TAED_PYTHON" -m agentic_taed.v2.analyze "$OUT/preflight"
