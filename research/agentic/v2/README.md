# Agentic TAED v2: prospective matched research

This revision adds `agentic_taed/v2` and this directory only. The original TAED,
previous extension, experiments, and reports remain intact. **No live LLM experiment
has run in this revision.** Read [REPORT.md](REPORT.md) for evidence and remaining gaps.

## Offline reproduction

Use Python 3.12 in a fresh environment; the previous requirements pin AgentDojo's source:

```bash
python3 -m venv /tmp/taed-v2-env
/tmp/taed-v2-env/bin/python -m pip install -r research/agentic/requirements.txt
TAED_PYTHON=/tmp/taed-v2-env/bin/python bash research/agentic/v2/reproduce_offline.sh research/agentic/v2/results/new-offline
```

`environment.freeze.txt` records the actual transitive package versions used here.
The script refuses an existing output directory. It runs unit/regression checks,
measures real RF/LIME/perturbation signals on development inputs, checks native
API/vector compatibility, and records a deliberately credential-free preflight.
It does **not** run an LLM or score a scripted agent.

## Real LLM evaluation

The implemented providers are OpenAI and OpenAI-compatible Chat Completions endpoints,
using AgentDojo's OpenAILLM. Configure credentials in the execution environment, never
in this repository or a chat message. Select an accessible tool-capable model with
`TAED_MODEL`. Provider capability must be validated in development before evaluation.
Other providers such as Anthropic are not wired in this runner.

```bash
python -m agentic_taed.v2.run \
  --split development --provider openai --model "$TAED_MODEL" \
  --calibration research/agentic/v2/results/calibration_final/calibration.json \
  --out research/agentic/v2/results/live-dev-new --max-blocks 2
python -m agentic_taed.v2.analyze research/agentic/v2/results/live-dev-new
```

Each block runs all 14 treatments on the SAME task, attack, goal, and seed, in a
deterministically shuffled order. The default two blocks are a small API smoke run,
not a full study. `--max-blocks 0` selects the entire preregistered split. Evaluation
is four tasks in two email-topic groups, 84 blocks / 1,176 cases including clean
controls. Three replicate seeds are requested (11, 29, 47), temperature 0.2, and a
common eight-tool-iteration budget applies. Unsupported seed/temperature requests
fail visibly; `--no-provider-seed` explicitly labels runs as unseeded replicates.
Provider seeds never guarantee bitwise reproducibility.

For an OpenAI-compatible service set `OPENAI_COMPATIBLE_API_KEY` and
`OPENAI_COMPATIBLE_BASE_URL`, then choose `--provider openai-compatible`.
No local endpoint is probed automatically.

Only after development and protocol freezing, use `--split evaluation` and a fresh
output directory. Never retune thresholds or filtering on those outputs. The split
is prospective; these public tasks are not guaranteed unknown to a pretrained LLM
or to developers who inspected the benchmark previously.

## Cost recording

Every attempted API call records duration, requested seed/model, returned model and
fingerprint, response ID, returned token usage, and sanitized error type. Optional
`--pricing PATH` accepts a JSON object with `model`, `input_per_million`,
`output_per_million`, and optionally `cached_input_per_million`; include source URL
and effective date for audit. Rates are not guessed. Missing rates or usage give
null costs, not zero. Token-based estimates are not provider billing statements.
Failed/partial runs preserve call records. The adapter caps calls at 32 per case;
AgentDojo may retry some provider errors, and these are separately metered.

## Treatments and endpoints

Eight T/F/S combinations independently switch record withholding by trust risk,
selective clause filtering, and evidence sufficiency. Filter-only is T0F1S0. T0F1S1
isolates the gate without TAED. Additional full-pipeline controls use CF, CI, C-only,
and a development-draw placebo instead of CFI. Two additional conditions implement
AgentDojo's spotlighting and repeat-user-prompt mechanisms with matched JSON formatting,
system/task prompt except for the intended defense change, model, seeds, and loop limit.
These are matched adaptations, not a claim of byte-identical upstream pipeline execution.

The existing lexical filter is frozen: v2 does not add patterns for held-out templates.
The trust operator is **whole-record withholding**, not the old classifier-triggered
filtering route; that deliberate change makes it independent of filtering. C is RF
confidence, F is LIME/dictionary alignment (not causal fidelity), and I is measured
probability sensitivity to deterministic word deletion (not an established attack score).

Primary endpoint: native utility AND no native attacker-goal success on attacked cases.
Native `security=True` means attacker success. Report ASR, clean/attacked utility,
paired clean utility loss, explicit false blocking conditional on baseline clean success,
latency, and cost. Missing/error cases and unmatched contrasts are counted separately.
The analysis does not invent confidence intervals with only two topic clusters.

## Evidence boundary

Facts carry record ID, offsets, source sender/timestamp, topic relevance, and assurance.
Out-of-band authentication may resolve a conflict; a sender field or a claim inside
an email is NOT authentication. Native runs supply no authenticated registry. Verified
provenance still does not guarantee factual truth. Consistent poisoned facts can pass.
Missing/conflicting facts trigger an enforced clarification before another LLM action.
This is a typed extraction baseline, not semantic entailment, identity resolution,
action-argument authorization, or an autonomous recovery system.

Compatibility validation runs benchmark oracle tool paths solely to verify selected
injection vectors are reachable. No defense or trained detector processes reserved
content during that validation, and no oracle answers are supplied to the actual agent.
