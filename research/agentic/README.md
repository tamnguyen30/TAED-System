# Agentic TAED research extension

An additive extension to `src/taed/TAEDPipeline`; the original source, trained artifacts,
frontend, and dependency file are unchanged. Read [REPORT.md](REPORT.md) before citing results.

## Reproduce locally

From the repository root, with Python 3.12 and network access for installation:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r research/agentic/requirements.txt
bash research/agentic/reproduce.sh research/agentic/results/my-run
```

The output path must be new. Dependencies are pinned directly in `requirements.txt`;
`environment.freeze.txt` records the complete execution environment (including inherited
analysis libraries). AgentDojo is pinned to a Git commit. No credentials are required
for the scripted tests. The checkout already includes the RF checkpoint. No datasets
or new model training are required for these tiny development experiments.

## Individual entry points

```bash
# Exact original five synthetic emails, actual trained RF, scripted task actions
.venv/bin/python -m agentic_taed.run_original_poc --out research/agentic/results/original-new
# Add clean counterparts (nine total cases; clean E04 is not duplicated)
.venv/bin/python -m agentic_taed.run_original_poc --clean-pairs --out research/agentic/results/paired-new
# Separate five-email extraction stress set; repeats are NOT independent samples
.venv/bin/python -m agentic_taed.evaluate --repeats 3 --out research/agentic/results/stress-new
# Actual AgentDojo sandbox with a scripted protocol test agent
.venv/bin/python -m agentic_taed.run_agentdojo --out research/agentic/results/dojo-new
```

## Live LLM experiments (not executed in this release)

Set `OPENAI_API_KEY` in the shell and choose a tool-capable model that your provider
account supports. Never put secrets in repository files. Then run:

```bash
.venv/bin/python -m agentic_taed.run_agentdojo --agent openai --model "$AGENT_MODEL" --out research/agentic/results/live-new
.venv/bin/python -m agentic_taed.evaluate --agent openai --model "$AGENT_MODEL" --out research/agentic/results/live-poc-new
```

The native AgentDojo runner uses real sandbox tool execution. The extraction PoC
LLM runner logs structured action intentions only. Neither sends real mail or changes
real calendars. Provider compatibility and live performance remain unvalidated.
The fixed attack is a protocol test, not a comprehensive adaptive benchmark.

## Full original TAED model

`RepositoryTAED(transformer_path=..., require_deep=True)` accepts a local Hugging Face
sequence-classification checkpoint and tokenizer, with class 0=safe and 1=phishing.
Install compatible PyTorch and Transformers before using that optional path.
The extraction CLI exposes `--transformer PATH --require-deep`.
The native AgentDojo and original-fixture runners currently use the partial RF/LIME/rules
configuration; to evaluate the full checkpoint there, instantiate the same adapter
with the verified checkpoint in their detector construction. This path was not tested
because no checkpoint is present. Do not label the partial detector full TAED.

## Layout

- `agentic_taed/models.py`: actual repository pipeline adapter, LIME seed, model fingerprint.
- `agentic_taed/core.py`: selective span removal, audit offsets, structural sufficiency, five ablations.
- `agentic_taed/agentdojo_adapter.py`: JSON tool-result middleware and scripted protocol agent.
- `agentic_taed/run_agentdojo.py`: native tasks, attacker-goal evaluation, answer checks, traces.
- `agentic_taed/run_original_poc.py`: exact prior E01–E05, clean pairs, evaluation-only labels.
- `agentic_taed/evaluate.py`: separate stress fixture runner, metrics, plots.
- `results/release/`: final sequential reproduction used in the report.
- Earlier result directories: debugging history; **not additional independent experiments**.

## Configuration semantics

| Configuration | Detector | Intervention |
|---|---|---|
| no_defense | none | unchanged email content |
| taed_only | real RF + original core | withhold content classified malicious |
| filter_only | none | always run clause filter |
| taed_filter | real RF + original core | run clause filter only on malicious verdicts |
| complete | real RF + original core | always filter, then check structural sufficiency and abstain if needed |

The complete configuration changes routing as well as adding sufficiency; its difference
from `taed_filter` is not a pure sufficiency ablation. Add TAED+always-filter without a
gate in a larger study. The current detector contributes a recorded signal but does not
change `complete`'s filtering decision. A gain over `filter_only` has not been established.

## Scope boundaries

The filter is a tuned regex baseline, not an instruction-understanding model. The
sufficiency check is structural and task-specific; it cannot verify truthful facts.
Unknown native task contracts abstain. The native runner covers only workspace
`user_task_16` and `user_task_22`; extending it requires task contracts and independent
fact annotations. Annotation files and native task answers are only used by scoring,
never passed into defense or agent inference.

## Local experiment history

`local-history.bundle` preserves the local experiment commits referenced in historical
manifests. Publication through the connected GitHub API uses a separate commit with
the same final source. After cloning this repository, recover the historical commits:

```bash
git fetch research/agentic/local-history.bundle HEAD:refs/heads/research/agentic-local-history
```

The bundle requires the original baseline commit, already in repository history.
Final release manifests additionally fingerprint every extension source file, so
source identity is verifiable independently of commit timestamps or publication method.
