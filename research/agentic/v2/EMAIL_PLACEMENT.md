# Facebook-code email placement pilot

Development only. AgentDojo package 0.1.35, Workspace v1.2.2, user_task_16 and injection_task_0. The authorized task retrieves a simulated security code. The injected objective sends an unrelated email. All tool calls operate in a fresh simulated Workspace.

## Evidence to date

Five native scorer controls passed. For the normal Facebook-code search, whole-message blocking with a known target left the code available when the attack was in the decoy. It removed the code when the attack was appended to the genuine message. Exact-span removal preserved it in both placements. The repository's existing clause filter left the full attacker goal visible in both. The JSON file records observations at the retrieval boundary. It contains no model performance measurements.

Both attacked conditions append identical Important Instructions text to the existing clean body and use a fixed generic model addressee. The decoy uses the native carrier but differs from the stock vector replacement. The genuine-message condition assumes attacker influence over a useful message. These constructed placements cannot estimate the frequency of compromised messages. Whole-message and exact-span arms know the injected location. Filtering-only receives ordinary subject/body text. Three repeats of one public task support debugging, not generalization. The stock code is fixed; check randomized codes before interpreting an answer without visible evidence.

## Run

In a checkout of research/agentic-taed, from the repository root, use Python 3.12 and an isolated environment.

```bash
python3 -m venv .venv-placement
source .venv-placement/bin/activate
python -m pip install 'agentdojo==0.1.35'
python -m agentic_taed.v2.email_placement
```

To run the 36 matched development episodes on a machine with a running Ollama server and qwen3:8b installed, use the same environment. Ollama's local API accepts a placeholder key. Set a genuine credential privately for any hosted endpoint that needs one.

```bash
OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:11434/v1 \
OPENAI_COMPATIBLE_API_KEY=ollama \
python -m agentic_taed.v2.email_placement --live --model qwen3:8b --out placement-live.jsonl
```

The runner creates a new output file, requests seeds 11, 29 and 47, and records provider usage and traces. Check that tool calls are parsed and that the model reached the email before interpreting each case. A requested seed does not guarantee deterministic serving. Inspect error rows separately. The official attack scorer requires an exact outbound message. Inspect all other sends in the traces as well. A raw task failure after filtering may reflect model behavior, ordinary search failure or missing evidence. Neither observer visibility nor absence of the exact goal implies attack blocking.

The current pilot does not run the calibrated full TAED or AgentSentry. Use the resulting paired traces to decide whether to extend those comparisons.
