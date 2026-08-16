"""
Single switch that controls the entire ml_pipeline package.

Every stage module (preprocess.py, transcribe.py, diarize.py, extract.py)
checks this flag and dispatches to either its mock implementation or its
real implementation. To go live with the real ML pipeline, the teammate
does NOT need to touch this file — just set USE_MOCK_ML=false in backend/.env
(see .env.example). This constant just reads that env var once at import time.
"""

import os

USE_MOCK = os.getenv("USE_MOCK_ML", "true").strip().lower() != "false"
