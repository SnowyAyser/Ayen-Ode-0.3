import sys
from pathlib import Path
import time

log_path = Path(__file__).parent.parent / "boot.log"

with open(log_path, "a", encoding="utf-8") as f:
    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] test_streams.py starting\n")
    f.write(f"  sys.stdout is: {sys.stdout!r}\n")
    f.write(f"  sys.stderr is: {sys.stderr!r}\n")
    f.write(f"  sys.stdin is: {sys.stdin!r}\n")
