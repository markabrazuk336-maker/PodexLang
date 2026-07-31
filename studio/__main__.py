"""Launch Podex Studio."""

import runpy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
runpy.run_module("app", run_name="__main__")
