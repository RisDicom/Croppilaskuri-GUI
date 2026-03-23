#!/usr/bin/env python3
"""Build a standalone .exe using PyInstaller.

Usage:
    python scripts/build_exe.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    entry_point = project_root / "src" / "croppilaskuri" / "__main__.py"

    if not entry_point.exists():
        print(f"Entry point not found: {entry_point}", file=sys.stderr)
        sys.exit(1)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "Croppilaskuri_GUI",
        "--distpath", str(project_root / "dist"),
        "--workpath", str(project_root / "build"),
        "--specpath", str(project_root / "build"),
        str(entry_point),
    ]

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"\nBuild complete! Executable in: {project_root / 'dist'}")


if __name__ == "__main__":
    main()
