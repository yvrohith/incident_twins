"""Individual original-study entry point; delegates all release policy and presentation."""
from pathlib import Path
import runpy
import sys
sys.argv[1:1] = ['original']
runpy.run_path(str(Path(__file__).resolve().with_name('replay.py')), run_name='__main__')
