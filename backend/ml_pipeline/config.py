"""
Single switch that controls the entire ml_pipeline package.

Every stage module (preprocess.py, transcribe.py, diarize.py, extract.py)
checks this flag and dispatches to either its mock implementation or its
real implementation. To go live with the real ML pipeline, the teammate
does NOT need to touch this file — just set USE_MOCK_ML=false in backend/.env
(see .env.example). This constant just reads that env var once at import time.
"""

import os
import sys
from pathlib import Path

# Puts the repo root on sys.path so _real_* implementations can
# `from src.diarize import diarize_audio` etc. — src/ has no __init__.py,
# but that's fine: it's a valid implicit namespace package as long as the
# repo root is importable. See ML_INTEGRATION.md.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

USE_MOCK = os.getenv("USE_MOCK_ML", "true").strip().lower() != "false"
