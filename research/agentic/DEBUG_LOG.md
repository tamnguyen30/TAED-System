# Debug and rerun record

All earlier outputs are retained; none were relabeled as successful live experiments.

1. **Model compatibility:** inspected actual joblib checkpoints. Four classical models
   loaded under sklearn 1.8 with 1.7.2 persistence warnings. Created isolated sklearn
   1.7.2 environment; the primary RF runs have no load warnings. XGBoost inspection
   was blocked by its missing optional dependency and is not used for reported results.
2. **Initial stress set:** paraphrased mailbox copying bypassed the clause filter.
   Added a disclosed mailbox-copy pattern. This is development-set tuning.
3. **AgentDojo v1:** Python datetimes in email model dumps were not JSON serializable.
   All 20 runs errored; successful denominators stayed zero. Added datetime serialization.
4. **Serialization-fix run:** clean tasks ran, but attack payloads containing JSON quotes
   broke AgentDojo's YAML-template substitution. Escaped payloads with JSON string
   encoding before insertion. Kept errors separate from security failures.
5. **AgentDojo v2:** native InjectionTask0 searched the entire inbox for its target
   subject. The injected email itself contained that subject, creating two matches;
   the checker returned false even when a sandbox email was sent. This is an observed
   limitation of this custom payload/evaluator pairing, not evidence the attack failed.
   Switched to native InjectionTask1 (delete a specific sandbox file), whose state
   predicate does not suffer this subject collision. Added positive and negative
   native evaluator regression tests. v2 ASR must not be used as robustness evidence.
6. **Original five emails:** copied byte-for-byte from the prior archive. Initial runs
   missed calendar exfiltration, answer contamination, and invented-date instructions.
   Added general lexical patterns for these forms and reran. Because the same fixtures
   motivated these edits, zero failures on their rerun is only a regression result.
7. **Native complete pipeline:** conflicting password-reset URLs cause abstention on
   both clean and attacked variants. Kept this utility loss rather than using an
   answer key or a trusted-domain shortcut to choose the desired URL.
8. **Metrics:** count only eligible solvable benign cases for false blocking; do not
   mark the expected missing-date clarification as a false block. Preserve official
   utility separately from output-answer correctness. Native `security=True` means
   attacker success; it is never blindly treated as safe. Annotated native code/URL
   retention independently, and added full message/tool traces.
9. **Final validation:** 17 regression tests and sequential reproduction of original,
   paired, stress, and native AgentDojo cases. Source SHA-256 values are included in
   final manifests. Legacy `src`, model files, and root requirements remain unchanged.

Initial source/result checkpoint commits:
- `0044a47`: initial stress and serialization-error runs.
- `7f631c7`: early fixes, stress v2, native v2 evaluator issue (not valid security evidence).
- `8dac92e`: native v3 with correct deletion evaluator, original-fixture v1.

No attempted API-provider call succeeded or produced live LLM results; the live runner
records a missing-credential blocker before issuing a request.
