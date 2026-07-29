"""Test setup for the mutant-generation approaches.

Approach modules (like the execution backends) use flat imports — `from util.io
import ...`, `from approach.basic.code_generator import ...` — because at runtime
the tool runs as a directory with `multiplex/` on `sys.path`. They cannot be
imported as `multiplex.approach.<x>`, so their tests import them the runtime way.
Add `multiplex/` to `sys.path` here. (Mirrors tests/execute/conftest.py.)
"""

import sys
from pathlib import Path

MULTIPLEX_DIR = Path(__file__).resolve().parents[2] / "multiplex"
if str(MULTIPLEX_DIR) not in sys.path:
    sys.path.insert(0, str(MULTIPLEX_DIR))
