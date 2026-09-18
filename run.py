import os
import sys
import subprocess

if __name__ == "__main__":
    og_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "og")
    if os.path.isdir(og_dir) and os.path.exists(os.path.join(og_dir, "run.py")):
        # Forward arguments directly to og/run.py
        cmd = [sys.executable, "run.py"] + sys.argv[1:]
        sys.exit(subprocess.call(cmd, cwd=og_dir))
    else:
        print("Error: 'og' directory not found.")
        sys.exit(1)
