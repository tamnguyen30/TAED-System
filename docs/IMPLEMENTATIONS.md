# Implementation map

The names `final`, `production`, and `paper` in historical filenames are not version guarantees.

| Entry point | Actual behavior in this checkout | Relationship to revised manuscript |
| --- | --- | --- |
| `src/backend.py` -> `src/hybrid_defense.py` | Flask UI; prefers a DistilBERT model if available, otherwise loads or trains an RF/gradient-boosting ensemble; heuristic explanation score | Historical demo, not RF-first selective DistilBERT routing |
| `src/evaluate_hybrid_system.py` | RF, LIME, DistilBERT, and rules; weights `(0.3,0.4,0.25)`, threshold `0.35`, three explanation features | Older cascade configuration, not the revised settings |
| `src/evaluate_hybrid_v3.py` | RF plus keyword/domain heuristics and keyword-based escalation resolution; no DistilBERT invocation | Separate heuristic evaluator; confidence handling differs for legitimate predictions |
| `templates/web-app/server/routes.ts` -> `taed_robust_final.py` | React/Express UI invokes RF/XGBoost, LIME, domain heuristics and randomized probes | Separate demonstration configuration |
| `templates/web-app/taed_paper_implementation.py` | Ten LIME features, prediction-dependent alignment heuristic, fixed `I=0.05`, weights `(0.3,0.4,0.3)` | Historical prototype despite filename |
| `src/generate_figures.py` | Embedded numeric arrays, currently malformed color strings | Historical plotting code, not a fresh evaluation |

## Before selecting a reference implementation

Associate the exact implementation commit with the model checkpoint, dictionary, probe definitions, feature count, score weights, threshold, and rule order used in an experiment. Do not combine results from these variants under one undifferentiated TAED label.

The manuscript uses the positive-class probability for instability and the predicted-class probability for confidence. Existing variants need reconciliation against the completed experiment before changing either code or reported numbers.

## Web bridge cleanup

The review branch replaces shell-interpolated email text with a subprocess argument array and adds a regression test for literal shell metacharacters. It also resolves the selected bridge's model directory from the repository root. This fixes invocation and path handling; it does not validate the model or its detector logic.
