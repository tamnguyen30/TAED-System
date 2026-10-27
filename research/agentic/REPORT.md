# Agentic TAED: implementation and local research evaluation

**Status:** additive implementation and local development evaluation completed; full-model and live-LLM research evaluation blocked. No publication-level efficacy claim is supported.

## Main findings

The repository's real Random Forest checkpoint can be integrated with its unchanged TAED core. On these small development examples, its phishing classification does not reliably detect instructions aimed at an agent. Consequently, using its malicious verdict as the only trigger for filtering misses attacks. Always filtering catches more of the tested patterns, but its rules were tuned on the same examples.

The complete pipeline does **not** demonstrate an advantage over filtering alone. Both solve the final original synthetic fixtures after tuning. In the native AgentDojo sandbox, the complete pipeline is more conservative and loses utility when multiple password-reset URLs are present. This is a useful negative result: information presence and uniqueness alone are not sufficient for safe task completion.

The experiments use actual trained RF inference, actual LIME calls, and actual native AgentDojo state/evaluators where specified. **All evaluated agents are scripted simulators, not LLMs. DistilBERT is absent.** The live runners exist but have not been validated with provider calls.

## 1. Preservation and architecture inspection

Baseline repository commit: `12264ac5583ef7834e4a5ceea674656e4bd7cbd7`. All additions are under `agentic_taed/` and `research/agentic/` on `research/agentic-taed`. No original implementation, model, frontend, or root dependency file was modified.

The actual checkpoint inventory contains RF, logistic regression, naive Bayes, SVM, and XGBoost joblib files, despite some README prose saying trained files are excluded. Four loaded in an initial inspection; XGBoost required an unavailable optional import. Only RF is used for reported experiments. `model_inventory.json` records exact hashes and sizes. Scikit-learn 1.7.2 matches the version embedded in the saved models. Training split membership, dataset provenance, and the original deep checkpoint remain unavailable.

The adapter calls `src/taed/pipeline.py::TAEDPipeline.predict`, not a label oracle. That core computes confidence, uses three LIME-selected features and the existing phishing dictionary, applies the trust gate, and conditionally applies the existing semantic rules. We use deterministic text-hash seeds and 256 LIME perturbation samples for tractable local runs. This sample budget is an explicit experimental choice, not the original LIME default.

The inspected core uses alpha=0.30, beta=0.40, gamma=0.25, threshold=0.35, and **constant default instability 0.05**. The README gives alpha=0.35. We preserve and disclose the executable defaults instead of silently changing them to match a manuscript. The trust value is not a calibrated probability of safety. No real perturbation-based instability estimate was implemented into the preserved core. Missing DistilBERT means results are labeled **partial RF + LIME + rules**, never a reproduction of the complete paper system.

## 2. Threat model and implemented components

The attacker controls email content, which is lower-trust than the original user task. Evaluation labels, expected answers, and retained-fact annotations are unavailable to defense and agent inference. Synthetic actions are JSON records; AgentDojo actions affect only its isolated in-memory sandbox. No external emails, payments, or calendar events are performed.

The selective filter recognizes narrow instruction patterns, removes matching clauses, and stores original character offsets, removed text, and reasons. It preserves other text without generating replacement facts. Unicode normalization is used for matching while offsets refer to the original string. It can over-remove quoted or discussed malicious instructions and miss paraphrases, encodings, multilingual attacks, or context-dependent instructions. It is a transparent regex baseline, not a general semantic sanitizer.

Structural sufficiency checks missing/conflicting typed fields on the additional stress set. Original E01–E05 use a task parser from the prior implementation, given only the trusted request and visible text. That parser is shared with the simulated task agent: this is **not an independent semantic validator**. AgentDojo contracts cover only Facebook-code and password-reset-link retrieval; unsupported contracts abstain. A complete response can still contain fabricated or attacker-chosen facts. A missing fact is never reconstructed from the evaluation answer key.

Native middleware runs after `ToolsExecutor` and before the next agent call, preserves roles and tool-call IDs, and edits JSON email fields on a copied message history. Full transcripts and field-level audit traces are recorded. Code/URL fact retention is evaluated using a separate annotation file. Live OpenAI-backed PoC and native runners are wired, but no credentials are configured. The optional local transformer adapter is untested without a checkpoint and requires PyTorch/Transformers.

## 3. Five configurations and fairness

| Configuration | Behavior |
|---|---|
| No defense | Pass through content to the same scripted agent |
| TAED-only | Withhold content classified malicious by the real partial TAED detector |
| Selective filtering only | Run the clause filter without TAED |
| TAED + filtering | Filter only content labeled malicious by TAED |
| Complete pipeline | Run TAED for an audit signal, always filter, then apply structural sufficiency |

The complete pipeline deliberately avoids a phishing-detector false negative bypass. This changes routing as well as adding sufficiency, so its comparison with TAED + filtering is not a pure sufficiency ablation. In its current form TAED does not alter the complete pipeline's filtering action; **a contribution from TAED itself has not been demonstrated**. A future factorial study must add always-filter + TAED without sufficiency and an explicitly calibrated low-trust routing variant.

## 4. Metrics and denominators

- **ASR:** successful attacker goals / attacked cases. Not computed on clean cases.
- **Task completion:** exact expected structured action/answer. In original E05, asking for clarification is the requested legitimate outcome and counts as completion.
- **Secure completion:** task completion AND no successful attacker goal, per case before averaging.
- **Information retention:** macro-average fraction of separately annotated legitimate facts still present after intervention. It is not character retention, truth verification, or sufficiency. Original E05 has no legitimate date to retain.
- **False blocking:** explicitly withheld solvable clean cases / solvable clean cases. Expected abstention for a genuinely missing date is excluded. The paired original set has four eligible clean cases, plus one clean insufficient case.
- **Latency:** measured wall time, including defense and agent execution, excluding model loading. Final release runs are sequential in a shared CPU environment; means are descriptive only and contain no live LLM latency or token cost.

AgentDojo's return named `security` means **attacker-goal success**. Its native utility may also reject unauthorized state changes, so it is not independent of security. We save a separate answer-presence check, native utility, native attacker-goal result, and joint native utility/no-attack result. Provider/runtime errors are excluded from successful denominators and reported explicitly, never converted into secure outcomes.

## 5. Results: exact original five-email proof of concept

These are the unchanged E01–E05 from the previous implementation ZIP: calendar exfiltration, invoice amount substitution, answer contamination, a clean invoice, and an invented missing date. The archive's fixture bytes were preserved. Four attacks and one solvable clean control; **all are synthetic development fixtures**. The simulated attacker interpreter is deliberately vulnerable and is not an estimate of LLM behavior.

| Configuration | Attack success | Task completion | Secure completion | Fact retention | False blocking | Mean ms |
|---|---:|---:|---:|---:|---:|---:|
| no_defense | 100.0% | 60.0% | 20.0% | 100.0% | 0.0% | 0.36 |
| taed_only | 75.0% | 20.0% | 0.0% | 60.0% | 100.0% | 144.10 |
| filter_only | 0.0% | 100.0% | 100.0% | 100.0% | 0.0% | 0.72 |
| taed_filter | 75.0% | 60.0% | 40.0% | 100.0% | 0.0% | 151.31 |
| complete | 0.0% | 100.0% | 100.0% | 100.0% | 0.0% | 147.50 |

The complete pipeline removes the tested directives in E01–E03, retains the clean invoice in E04, and asks for clarification in E05. Filtering alone achieves the same end results because the scripted parser also detects missing information. This result does not establish incremental utility from a separate sufficiency stage.

Initial original-fixture runs had 75% ASR for filtering and complete, before adding calendar-exfiltration, answer-contamination, and invented-fact patterns. This is an iterative regression demonstration on known failures, **not held-out accuracy**. Earlier raw results remain in `original_poc_v1/`.

### Paired clean variants

Four clean counterparts were added using the preexisting `gold_safe_email` values; the already-clean E04 was not duplicated. Nine cases total, four attacked, four eligible solvable benign cases, one clean insufficient case. The gold-safe text is only an input-fixture construction method, never accessed by the defense.

| Configuration | Attack success | Task completion | Secure completion | Fact retention | False blocking | Mean ms |
|---|---:|---:|---:|---:|---:|---:|
| no_defense | 100.0% | 77.8% | 55.6% | 100.0% | 0.0% | 0.20 |
| taed_only | 75.0% | 55.6% | 44.4% | 77.8% | 25.0% | 141.95 |
| filter_only | 0.0% | 100.0% | 100.0% | 100.0% | 0.0% | 0.47 |
| taed_filter | 75.0% | 77.8% | 66.7% | 100.0% | 0.0% | 137.02 |
| complete | 0.0% | 100.0% | 100.0% | 100.0% | 0.0% | 140.20 |

## 6. Separate five-email stress set

This additional set includes a benign meeting, invoice exfiltration, a fact entangled in a malicious clause, a paraphrased mailbox-copy instruction, and a benign financial message. It is distinct from the original E01–E05. Three repetitions per case give 15 rows per configuration, but only five unique inputs: do not treat repetitions as independent samples.

| Configuration | Attack success | Task completion | Secure completion | Fact retention | False blocking | Mean ms |
|---|---:|---:|---:|---:|---:|---:|
| no_defense | 100.0% | 80.0% | 40.0% | 100.0% | 0.0% | 0.04 |
| taed_only | 66.7% | 40.0% | 20.0% | 60.0% | 50.0% | 133.86 |
| filter_only | 0.0% | 80.0% | 80.0% | 90.0% | 0.0% | 0.50 |
| taed_filter | 66.7% | 80.0% | 60.0% | 100.0% | 0.0% | 135.95 |
| complete | 0.0% | 80.0% | 80.0% | 90.0% | 0.0% | 142.49 |

Removing the instruction-entangled time prevents attack success but loses a required fact, so legitimate task completion falls. The complete pipeline abstains rather than fabricating the missing time. Retention and task completion must therefore be reported together. The original filter missed the mailbox-copy paraphrase; the later rule was tuned on that example.

## 7. Native AgentDojo results

Pinned source: `ethz-spylab/agentdojo@089ed468cf3ed0322acc66b0211f26d9d90dbf60`, package 0.1.35, benchmark **v1.2.2**, workspace tasks **16 and 22**, each clean and attacked. Attacker objective **injection_task_1** deletes sandbox file 13. The injection uses a disclosed fixed `EXECUTE_TOOL` payload. The agent parses that payload intentionally to test native tool execution and scoring. These are real AgentDojo integration runs with a **scripted protocol agent**, not the standard LLM benchmark or a standard adaptive attack suite.

| Configuration | ASR | Clean utility | Attacked utility | Joint secure utility | Fact retention | False blocking | Mean ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| no_defense | 100.0% | 100.0% | 0.0% | 50.0% | 100.0% | 0.0% | 99.37 |
| taed_only | 50.0% | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% | 1315.93 |
| filter_only | 0.0% | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 92.31 |
| taed_filter | 50.0% | 100.0% | 50.0% | 75.0% | 100.0% | 0.0% | 1479.54 |
| complete | 0.0% | 50.0% | 50.0% | 50.0% | 50.0% | 50.0% | 1317.14 |

The complete pipeline blocks ambiguous reset-link retrieval in both conditions, while filtering alone preserves the correct URL alongside other content and the permissive scripted answer contains it. Native answer-match success does not prove the agent selected the correct URL for a real action. The result exposes both the gate's conservatism and the limits of these retrieval evaluators.

A prior custom email-send attack produced a genuine evaluator collision: the injected message contained the target subject, causing a search-based native checker to miss a completed send. Those v2 numbers are invalid security evidence and retained only as debugging history. The final deletion objective has positive/negative native-state regression tests.

## 8. Comparisons with existing defenses

These comparisons describe mechanisms, not matched empirical superiority:

| Existing approach | Relevant distinction and necessary future comparison |
|---|---|
| AgentDojo built-in tool filtering | Restricts tools available for a task; should be evaluated with the same LLM/tasks and attacker objectives. |
| Prompt-injection detector/message withholding | Tests whole-message rejection and utility loss; current partial phishing TAED is not equivalent to a trained injection detector. |
| Spotlighting / delimiting | Marks lower-trust content rather than deleting it. A matched live baseline is needed to test whether removal buys anything. |
| Repeat user prompt | Reinforces the original goal after tool output; another low-cost native baseline. |
| CaMeL | Separates trusted control flow from untrusted data using security-policy mechanisms. Our regex filter provides no comparable guarantee. |
| Fides | Tracks confidentiality/integrity and enforces information-flow policies, including selective hiding. Information restriction is already studied; “filter and continue” alone is not a defensible novelty claim. |

AgentDojo supplies dynamic tasks and attacker-goal evaluations [1]. Spotlighting targets the trust distinction in indirect injection [2]. CaMeL extracts control/data flow from the trusted query [3]. Fides supplies label-based policy enforcement and selective hiding [4]. None was reproduced as a live competitor here; numerical results across their papers cannot be compared to these tiny scripted tests.

## 9. Potential contribution and required evidence

A plausible research question is: **Under a fixed attack budget, can task-aware content removal preserve enough trustworthy evidence to improve joint secure completion over both withholding and non-removal defenses?** This remains a hypothesis.

Useful contributions could be: an independently annotated benchmark of task-critical fact loss; evidence-grounded sufficiency checking that measures missing, conflicting, and poisoned facts separately; and a calibrated routing policy balancing risk, latency, and utility. The present scaffolding supports those experiments but does not establish novelty, robustness, or a publishable result.

Before a publication claim: obtain original DistilBERT artifacts and training provenance; run multiple real agents and seeds; freeze filter/gate settings before a held-out test split; cover more tasks and multiple adaptive attack families; annotate required facts and removed spans independently; compare native defenses, a trained injection detector, and policy-based approaches; use paired task-level statistical analyses and confidence intervals. Measure failed recovery, clarification quality, false refusal, token cost, and end-to-end latency as well as attack success. Do not reuse these tuned fixtures as a test set.

## 10. Genuine blockers, limitations, and deliverables

1. **No DistilBERT checkpoint:** the full original four-stage model cannot be evaluated. The adapter does not silently train a replacement or fabricate a deep score.
2. **No provider credentials:** live LLM and live AgentDojo results are unavailable. `live_agentdojo_blocked/blocked.json` records preflight failure. There were no successful model-provider calls.
3. **Narrow components:** lexical filtering and task-specific structural checks cannot establish factual sufficiency or general instruction safety. Complete does not perform verified recovery; it abstains. Unknown native task contracts are unsupported.
4. **Small tuned datasets:** original five + clean counterparts, a separate five-input stress set, two native tasks, one native attack objective. No claim of generalization or significance is justified.
5. **Prototype provenance:** trained-model hashes are known, original training data/splits are not. No reproduction of previously reported TAED paper accuracy or ASR is claimed.

The final sequential reproduction passes **17 tests**. Final raw JSONL, transcripts, manifests, comparison CSVs, and plots are in `results/release/{original,paired,stress,agentdojo}/`. Earlier failed runs and the development sequence remain available. `reproduce.sh` reruns the full local workflow; `README.md` documents commands and live-run boundaries. `DEBUG_LOG.md` explains each failure and fix. Original repository files were verified unchanged relative to the baseline commit.

## Sources

[1] AgentDojo: https://arxiv.org/abs/2406.13352 and pinned implementation https://github.com/ethz-spylab/agentdojo/tree/089ed468cf3ed0322acc66b0211f26d9d90dbf60

[2] Defending Against Indirect Prompt Injection Attacks With Spotlighting: https://arxiv.org/abs/2403.14720

[3] Defeating Prompt Injections by Design (CaMeL): https://arxiv.org/abs/2503.18813

[4] Securing AI Agents with Information-Flow Control (Fides): https://arxiv.org/abs/2505.23643

[5] Original TAED source: https://github.com/tamnguyen30/TAED-System/tree/12264ac5583ef7834e4a5ceea674656e4bd7cbd7
