"""Capture exact implementation identity, including uncommitted source hashes."""
import hashlib
import platform
import subprocess
from pathlib import Path


def source_identity():
    root=Path(__file__).resolve().parents[1]
    return {'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
            'python':platform.python_version(),
            'source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted((root/'agentic_taed').glob('*.py'))},
            'original_core_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted((root/'src/taed').glob('*.py'))}}
