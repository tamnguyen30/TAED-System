name: Qwen held-out email placement

on:
  workflow_dispatch:
  push:
    branches:
      - research/agentic-taed
    paths:
      - .github/workflows/heldout-placement.yml

jobs:
  evaluation:
    runs-on: ubuntu-24.04
    timeout-minutes: 330
    strategy:
      fail-fast: false
      matrix:
        task:
          - user_task_14
          - user_task_17
        attack:
          - important_instructions
          - tool_knowledge
          - injecagent
        seed:
          - 11
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install "agentdojo==0.1.35" "openai==1.46.0"

      - name: Start Ollama and pull qwen3:8b
        run: |
          docker run -d --name ollama -p 127.0.0.1:11434:11434 -e OLLAMA_CONTEXT_LENGTH=16384 ollama/ollama:latest
          for i in $(seq 1 30); do
            curl -sf http://127.0.0.1:11434/api/version && break
            sleep 2
          done
          docker exec ollama ollama pull qwen3:8b
          mkdir -p results-pilot
          curl -sf http://127.0.0.1:11434/api/version > results-pilot/ollama_version.json
          curl -sf http://127.0.0.1:11434/api/tags > results-pilot/models.json

      - name: Run held-out placement evaluation
        env:
          OPENAI_BASE_URL: http://127.0.0.1:11434/v1
          OPENAI_API_KEY: ollama
        run: |
          python -m agentic_taed.v2.heldout_placement \
            --phase evaluation \
            --task "${{ matrix.task }}" \
            --attack "${{ matrix.attack }}" \
            --seed "${{ matrix.seed }}" \
            --out "results-pilot/episodes-${{ matrix.task }}-${{ matrix.attack }}-seed-${{ matrix.seed }}.jsonl"

      - name: Upload episode logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: evaluation-${{ matrix.task }}-${{ matrix.attack }}-seed-${{ matrix.seed }}
          path: results-pilot/
