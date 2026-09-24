#!/usr/bin/env python3
"""Offline inventory: no third-party imports, model execution, or downloads."""
import argparse
import ast
import json
from pathlib import Path

REQUIRED = (
    "models/random_forest_pipeline.joblib",
    "models/distilbert_phishing_v2",
    "data/splits/X_train.csv", "data/splits/y_train.csv",
    "data/splits/X_test.csv", "data/splits/y_test.csv",
    "data/adversarial/adversarial_benchmark_dataset_ccs_clean.csv",
)
SKIP = {".git", ".venv", "venv", "taed_env", "node_modules", "__pycache__"}

def inspect(root):
    errors = []
    count = 0
    for path in sorted(root.rglob("*.py")):
        if SKIP.intersection(path.relative_to(root).parts):
            continue
        count += 1
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            errors.append({"path": str(path.relative_to(root)),
                           "line": getattr(exc, "lineno", None),
                           "error": getattr(exc, "msg", str(exc))})
    missing = [p for p in REQUIRED if not (root / p).exists()]
    return {"scope": "historical entry-point prerequisites and Python syntax",
            "python_files_checked": count, "syntax_errors": errors,
            "missing_assets": missing, "ready": not errors and not missing,
            "performance_validated": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("--root must be an existing directory")
    result = inspect(args.root.resolve())
    print(json.dumps(result, indent=2))
    return 0 if result["ready"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
