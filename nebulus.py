#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the project root to sys.path so we can import from src
# This file is expected to be at the project root: /home/jlwestsr/projects/west_ai_labs/nebulus/nebulus.py
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))

from src.cli import cli, status  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Show status if no command provided
        # We need to manually invoke the callback if we want the same behavior as cli.py's main block
        try:
            status.callback()
        except Exception:
            # Fallback if status callback fails or isn't set up as expected
            cli()
    else:
        cli()
