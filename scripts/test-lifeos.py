#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "lifeos.py"


def run(*args: str, data_dir: Path) -> dict:
    cmd = [sys.executable, str(CLI), "--data-dir", str(data_dir), "--json", *args]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    return json.loads(proc.stdout)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp) / "lifeos-data"

        install = run("install", "--runtime", "hermes", data_dir=data_dir)
        assert install["ok"] is True
        assert install["subskills"] == 20
        assert (data_dir / "installed.json").exists()
        assert (data_dir / "runtime.json").exists()
        assert (data_dir / "config.json").exists()
        assert (data_dir / "tasks-todo" / "data.json").exists()

        doctor = run("doctor", data_dir=data_dir)
        assert doctor["ok"] is True, doctor
        assert doctor["warnings"] == [], doctor

        config = run("config", data_dir=data_dir)
        assert config["ok"] is True
        assert config["config"]["runtime"] == "hermes"
        assert isinstance(config["config"]["sources"], dict)
        assert isinstance(config["config"]["internal_state"], dict)
        assert isinstance(config["config"]["caches"], dict)
        assert "optional_global_skills" not in config["config"]
        assert "schedules" not in config["config"]

    print("lifeos tests ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
