# Agentic TAED research revision: fair comparisons and evidence-aware sufficiency

**Date:** October 27, 2026. **Status:** implementation and offline validation completed; live experiments blocked. Original TAED and all earlier experiments/reports are preserved.

## Conclusion first

We still have **no evidence that trust-aware TAED improves real-agent security or utility**. There are zero live LLM trials in this revision. The available provider credentials and DistilBERT checkpoint are absent. No scripted-agent results are substituted for those missing experiments.

One additional, narrowly scoped observation is available: on ten previously used development emails, C-only, CF, CI, and CFI select **the same two records for withholding** after matching their empirical intervention rates. Measured instability varies, but it does not alter the selected records in this calibration. This is a detector/routing diagnostic, not an attack-success experiment or an estimate of population performance.

The revised implementation makes a meaningful future falsification possible: if CF/CFI do not improve paired secure completion over the confidence control and filtering-only at matched intervention cost, the trust-metric contribution should be rejected or narrowed. Adding more stages alone is not a contribution.

## 1. What changed, without changing old experiments

All new source lives in `agentic_taed/v2/`; all configurations, tests, results, and this report live under `research/agentic/v2/`. The original `src/`, model artifacts, previous `agentic_taed` modules, prior raw results, and previous reports remain byte-identical to the preceding branch state. This revision does not retroactively reinterpret the earlier scripted results as real-agent evidence.

The existing regex filter is frozen. No rule was added for reserved evaluation attacks. Real RF probabilities and real LIME explanations are reused through the existing adapter. The new extension measures instability using eight deterministic word-drop probes, instead of using the legacy constant as its routing input. The original core still executes unchanged.

## 2. Orthogonal ablation design

The main study is a complete 2×2×2 factorial, with the same operation order in every cell:

| Factor | Off | On |
|---|---|---|
| T: trust-based intervention | No trust withholding | Withhold whole email records whose calibrated risk exceeds the cutoff |
| F: selective filtering | Preserve retained text | Apply the frozen clause filter to retained subjects/bodies |
| S: evidence sufficiency | Let the agent continue | Check task-critical evidence; force clarification for missing or unresolved conflicting facts |

This yields all eight combinations. T0F1S0 is filtering-only; T0F1S1 measures sufficiency without TAED; T1F1S0 isolates trust withholding on top of filtering. Unlike v1, enabling S does not silently enable F or change its routing. Trust here is a record-withholding policy, not v1's classifier-triggered filtering policy. This makes its incremental role explicit but means results must not be described as a direct rerun of the old policy.

Four additional full-pipeline controls use CF, CI, C-only, and a deterministic placebo drawn from development CFI scores. The placebo is a negative control, not an exact within-test permutation. Two other conditions adapt AgentDojo's spotlighting/delimiting and repeat-user-prompt defenses with the same JSON formatter, base system message, model, temperature, tool budget, and tasks except for the intended defense changes. There are **14 treatments**, including the eight factorial cells.

These comparisons use natural-language attack payloads, not a scripted `EXECUTE_TOOL` interpreter. The optional Deep TAED checkpoint is not present; this revision evaluates an RF/LIME-derived trust extension when credentials become available, not the complete original paper model.

### Signal definitions and coverage calibration

C is RF prediction confidence. F is the fraction of three LIME-selected terms in the existing phishing dictionary; it is **dictionary alignment**, not established causal explanation fidelity. I is mean absolute change in phishing probability across eight deterministic word-drop probes. Word deletion may change semantics, so I is a sensitivity feature, not a validated maliciousness score.

CFI uses the preserved coefficient choices 0.30C + 0.40F − 0.25I, clipped to [0,1]. Controls omit the named terms while retaining the same scale. Risk combines phishing probability with inverse normalized trust. Cutoffs are selected separately on the same ten development emails to match a target withholding budget, without consulting evaluation outcomes. Fixed thresholds would otherwise confound the controls' score scales with intervention frequency.

The 30% target becomes 20% actual withholding because the conservative quantile rule and strict `>` cutoff exclude ties/boundaries. All five signal conditions achieve the same observed 20% development coverage. This is a small empirical match, not calibration of risk probabilities or a guarantee of equal evaluation coverage; realized test withholding must also be reported.

| Signal | Development cutoff | Actual coverage | Selected input indices |
|---|---:|---:|---|
| CFI | 0.770089 | 20% | 2, 3 |
| CF | 0.764286 | 20% | 2, 3 |
| CI | 0.790536 | 20% | 2, 3 |
| C-only | 0.777143 | 20% | 2, 3 |
| Development-draw placebo | 0.770089 | 20% | 2, 5 |

Indices are zero-based over the original five fixtures followed by the five earlier stress fixtures. These are development inputs already exposed in prior work. Measured I ranges from **0.01125 to 0.06625**. Raw probabilities, selected LIME terms, probe probabilities, thresholds, and timings are saved. The inherited metadata field `instability=0.05` describes the unmodified repository core; actual v2 routing uses each record's measured `I`, not that constant.

## 3. Evidence-aware sufficiency

The new checker records each extracted fact's field, value, email ID, exact body offsets, sender, timestamp, topic relevance, and provenance assurance. It checks codes, URLs, dates, times, locations, durations, and attendees when required by the supported task contract. Calendar requests can supply duration through the trusted user query; email content cannot overwrite that query. Unsupported tasks explicitly ask for clarification.

Conflicting values are retained as conflicts rather than resolved by their order or how often they appear. Topic relevance gates whether a record supports the request, but a higher keyword count does not overrule contradictory facts. A real, out-of-band authenticated sender registry can give evidence priority; an `authenticated` claim inside a returned email cannot. URL-host policies use exact parsed hostnames, not substring matching.

Native AgentDojo does **not** supply that authenticated registry, and the runner does not invent one. Sender and timestamp fields remain unverified metadata. If equally assured records disagree, the checker requests clarification. A unique, consistent poisoned fact can still pass with an explicit provenance warning. Authenticated origin would also not establish factual truth. The checker remains a typed extraction and consistency baseline, not semantic entailment, general identity resolution, or an action-argument authorization proof.

Missing/conflicting evidence stops the next LLM action and produces a clarification response. This is enforced in the pipeline instead of merely telling the LLM to abstain. It does not implement safe retrieval/recovery or prove that clarification is optimal. Numeric or date normalization and context-sensitive contradictions still need broader validation. The calendar contracts check a minimum set of facts, not all task semantics.

## 4. Prospective data separation and expanded native scenarios

| Split | Native workspace tasks | Email-topic groups | Attack templates |
|---|---|---|---|
| Development | 16, 22 | Facebook code; password reset | Instruction override; authority spoofing |
| Reserved evaluation | 14, 15, 17, 18 | Family reunion; hiking | Claimed prerequisite/dependency; base64-encoded instruction |

Task pairs that share email evidence stay in the same split. Injection placeholder sets and template families are disjoint across splits. Native injection objectives 1, 2, and 3 cover file deletion, unauthorized event creation, and information exfiltration. Every selected task/vector was checked for visibility using native oracle tool paths in an isolated environment. That is **API/fixture compatibility validation**, not a defense evaluation: no trust/filter/sufficiency model was run on reserved content, and no oracle answers were passed to an evaluated agent.

The attack surface is an email-body placeholder; sender, subject, and timestamp tampering are not included. These are four tasks but only **two independent evaluation topic groups**. The benchmark is public and task sources were inspected previously. “Held out” therefore means prospectively excluded from this revision's calibration and tuning, not pristine unseen data for the developer or pretrained models. No evaluation effectiveness result has been obtained.

The full reserved matrix is 84 matched task/condition/goal/seed blocks × 14 treatments = **1,176 planned cases**. Three seeds (11, 29, 47), temperature 0.2, and eight tool-loop iterations are fixed. Default live CLI execution limits to two complete blocks for an initial API check; this is not the full study. Order is shuffled within blocks. The same attack payload, legitimate task, model, and seed are used for every treatment in a block.

## 5. Live providers, metrics, costs, and failures

The new runner has no scripted-agent mode. It supports OpenAI and OpenAI-compatible Chat Completions endpoints through AgentDojo's OpenAILLM. No other provider is represented as implemented. Missing credentials and an unspecified model stop before any call. Unsupported provider seed/temperature options fail visibly; an explicit unseeded option records replicate labels without falsely claiming the seed reached the provider.

For real runs, raw records include native utility, native attacker-goal success, joint secure completion, full message/tool traces, intervention/evidence audits, end-to-end time, and every attempted provider call. Native `security=True` is correctly interpreted as **attacker success**. Error cases are not scored as secure; paired contrasts exclude incomplete pairs and retain missing/error counts.

False blocking is the explicit clarification rate among clean cases the matched undefended agent solved. A separate clean utility-loss metric covers other failures, including model refusals not caused by the gate. This distinction prevents confusing a failed baseline with a defense-induced block. Reserved task-critical fact retention lacks independently validated gold annotations and is not reported as a new metric; extracted candidate counts would not be a valid substitute.

Provider-reported input/output/cache token counts and model fingerprints are recorded when present. Optional externally supplied, model-specific pricing produces a token-based cost estimate, not a billed invoice. If usage or rates are absent, cost is null. Failed/partial calls remain visible, and retry calls are metered separately. There are zero live calls, zero measured live costs, and no live latency distribution in this revision.

The analysis produces within-block T, F, and S contrasts and comparisons of full CFI against CF, CI, C-only, and placebo. More independent task groups are needed before reliable clustered inference. Seeds are repeated measurements, not new independent tasks. No population confidence interval or significance claim is emitted from the tiny planned set.

## 6. What actually ran

| Activity | Observed status |
|---|---|
| Previous 17 tests + 20 new tests | **37 passed** |
| RF/LIME and measured instability on ten development inputs | Executed; raw signals saved |
| Development coverage matching | Executed; 20% for all five signals |
| Native task/vector compatibility | All six selected vectors visible on oracle paths |
| Provenance/conflict and factor-isolation checks | Executed as unit/integration tests |
| Real LLM development trials | **Blocked; 0 cases** |
| Real LLM reserved-evaluation trials | **Blocked; 0 cases** |
| Full original DistilBERT cascade | **Checkpoint unavailable** |

New checks include self-asserted authentication rejection, source-offset validity, order/frequency-invariant conflict handling, authenticated-source conflict resolution, exact hostname checks, trusted-query facts, factor independence, enforced clarification without an LLM call, metering/error behavior, missing-result handling, and matched-contrast pairing. Passing these checks demonstrates implementation properties, not general prompt-injection robustness.

Observed remaining failures/risks include consistent poisoned facts passing; authentic-but-wrong sources; unrecognized natural-language facts; conservative conflict abstention; semantics-changing perturbations; lexical-filter false positives/bypasses; and fixed template attacks that are weaker than adaptive adversaries. These should be measured on new data rather than patched using reserved evaluation examples.

## 7. Novelty assessment and a defensible decision rule

The broad proposed contribution overlaps with existing work:

- **Task Shield** already checks whether instructions and tool calls contribute to the user's task [1]. Task alignment alone is not new.
- **ARGUS** audits whether actions have supporting benign causal evidence, with provenance graphs and grounded arguments [2]. Provenance-backed action justification is a substantial existing comparator, not an unclaimed space.
- **SecFid** explicitly measures how suppressing untrusted content can harm information fidelity [3]. Reporting both security and preservation is necessary, but not itself a novel contribution.
- A critical defense-evaluation study emphasizes both adaptive attack effectiveness and general utility [4]. Fixed-template success cannot establish robustness.

These are primary-source mechanism comparisons, not implementations or matched numerical reproductions. The current runner includes only the two simpler AgentDojo defense mechanisms. Task Shield, ARGUS, SecFid, trained injection detectors, CaMeL, and Fides are **not** claimed as experimentally reproduced competitors.

A narrower candidate contribution is: **Do inexpensive explanation-alignment and perturbation-sensitivity signals predict when selective removal or clarification improves secure completion, beyond RF confidence, at matched intervention budgets?** If supported, this could justify a calibrated routing policy rather than a new generic provenance architecture.

Before making that claim, obtain real multi-model, multi-seed traces; tune only on development; expand beyond two independent evaluation groups; add adaptive and context-dependent attacks and preservation-critical benign tasks; obtain independent evidence annotations; compare appropriate task/provenance defenses; and analyze secure utility and cost jointly. At present, even the calibration routing decisions do not distinguish CFI from C-only. The honest outcome may be a negative study showing that these TAED signals do not transfer to agent prompt-injection defense.

A positive result requires a reproducible held-out gain over filtering-only and the calibrated C-only/control conditions, without explaining the gain merely by increased withholding. A null/negative result requires reporting that outcome and revisiting the architecture. No acceptance threshold or power claim should be invented after seeing evaluation results.

## 8. Artifacts and next execution step

- `configs/protocol.json`: split, seeds, threat model, attack objectives, and planned endpoint.
- `configs/treatments.json`: the 14 exact treatment definitions.
- `results/calibration_final/`: real development signals and calibrated thresholds.
- `results/offline_release/`: reproducible validation, calibration, compatibility, and blocked preflight.
- `results/live_development/` and `results/live_evaluation/`: explicit zero-case blocker manifests; no efficacy table.
- `README.md` and `reproduce_offline.sh`: offline and live commands with limits.
- `environment.freeze.txt`: observed dependency versions.

The next dependent step is a small matched live development run with an explicitly selected tool-capable model and environment-configured credentials. Provider compatibility and actual cost must be established there before running the reserved split. No credentials should be committed or pasted into chat. The original deep checkpoint is separately required for claims about the complete TAED cascade.

## Primary sources checked October 27, 2026

[1] The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents. https://arxiv.org/abs/2412.16682

[2] ARGUS: Defending LLM Agents Against Context-Aware Prompt Injection. https://arxiv.org/abs/2605.03378 (v2, July 8, 2026).

[3] Security--Fidelity Tradeoffs: The Hidden Cost of Prompt Injection Defense. https://arxiv.org/abs/2606.30783

[4] A Critical Evaluation of Defenses against Prompt Injection Attacks. https://arxiv.org/abs/2505.18333

Pinned AgentDojo implementation: https://github.com/ethz-spylab/agentdojo/tree/089ed468cf3ed0322acc66b0211f26d9d90dbf60
