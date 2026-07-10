"""Test setup for the execution backends.

`multiplex/execute/maven.py` (like the other pipeline modules) uses flat imports
—`from checks...`, `from util...`—because at runtime the tool is executed as a
directory with `multiplex/` on `sys.path`. Leaf modules under `multiplex/`
import cleanly as `multiplex.<x>` in tests, but `execute.maven` cannot, so its
tests import it the runtime way. Add `multiplex/` to `sys.path` here.
"""

import sys
from pathlib import Path

MULTIPLEX_DIR = Path(__file__).resolve().parents[2] / "multiplex"
if str(MULTIPLEX_DIR) not in sys.path:
    sys.path.insert(0, str(MULTIPLEX_DIR))
