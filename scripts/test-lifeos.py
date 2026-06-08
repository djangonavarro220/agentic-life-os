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
        assert install["semantic_health"]["complete"] is False
        assert install["install_claim"] == "mechanical_only"
        assert (data_dir / "installed.json").exists()
        assert (data_dir / "runtime.json").exists()
        assert (data_dir / "config.json").exists()
        assert (data_dir / "tasks-todo" / "data.json").exists()

        doctor = run("doctor", data_dir=data_dir)
        assert doctor["ok"] is True, doctor
        assert doctor["warnings"] == [], doctor
        assert doctor["semantic_health"]["complete"] is False, doctor
        pending_keys = {q["key"] for q in doctor["semantic_health"]["pending_questions"]}
        assert {
            "tasks_source",
            "memory_source",
            "routine_schedule_policy",
            "daily_pulse",
            "quiet_heartbeat",
            "review_cadence",
            "delivery_policy",
            "cron_record_source",
        } <= pending_keys

        config = run("config", data_dir=data_dir)
        assert config["ok"] is True
        assert config["config"]["runtime"] == "hermes"
        assert isinstance(config["config"]["sources"], dict)
        assert isinstance(config["config"]["internal_state"], dict)
        assert isinstance(config["config"]["caches"], dict)
        assert config["config"]["semantic_setup"]["status"] == "pending"
        assert "optional_global_skills" not in config["config"]
        assert "schedules" not in config["config"]

        next_question = run("next-question", data_dir=data_dir)
        assert next_question["ok"] is True
        assert next_question["complete"] is False
        assert next_question["question"]["key"] == "tasks_source"
        assert next_question["command_hint"] == "lifeos.py answer tasks_source '<answer or runtime pointer>'"
        assert doctor["install_claim"] == "mechanical_only"
        assert doctor["safe_to_claim_fully_installed"] is False

        plan = run("plan", data_dir=data_dir)
        assert plan["ok"] is True
        assert plan["semantic_health"]["complete"] is False
        assert "answer all pending semantic setup questions" in plan["steps"][0]
        assert {item["name"] for item in plan["cron_templates"]} == {"daily_pulse", "quiet_heartbeat", "weekly_review"}
        assert all(item["create_by_default"] is False for item in plan["cron_templates"])

        answered = run("answer", "tasks_source", "runtime todo system", data_dir=data_dir)
        assert answered["ok"] is True
        assert answered["semantic_health"]["answered"] == ["tasks_source"]
        doctor_after_one_answer = run("doctor", data_dir=data_dir)
        assert doctor_after_one_answer["semantic_health"]["complete"] is False
        assert "tasks_source" not in {q["key"] for q in doctor_after_one_answer["semantic_health"]["pending_questions"]}
        assert run("next-question", data_dir=data_dir)["question"]["key"] == "memory_source"

        for key in pending_keys - {"tasks_source"}:
            run("answer", key, f"test answer for {key}", data_dir=data_dir)
        complete_doctor = run("doctor", data_dir=data_dir)
        assert complete_doctor["semantic_health"]["complete"] is True, complete_doctor
        assert complete_doctor["semantic_health"]["pending_questions"] == []
        assert complete_doctor["install_claim"] == "fully_configured"
        assert complete_doctor["safe_to_claim_fully_installed"] is True
        assert run("next-question", data_dir=data_dir)["complete"] is True
        complete_config = run("config", data_dir=data_dir)["config"]
        assert complete_config["semantic_setup"]["status"] == "complete"
        assert complete_config["semantic_setup"]["decisions"]["tasks_source"]["answer"] == "runtime todo system"

    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp) / "legacy-lifeos-data"
        data_dir.mkdir()
        (data_dir / "config.json").write_text(json.dumps({"enabled": True, "runtime": "hermes", "skills": {}}), encoding="utf-8")
        doctor = run("doctor", data_dir=data_dir)
        assert doctor["ok"] is True, doctor
        saved = json.loads((data_dir / "config.json").read_text(encoding="utf-8"))
        assert saved["semantic_setup"]["status"] == "pending"
        assert set(saved["semantic_setup"]["missing"]) == {
            "tasks_source",
            "memory_source",
            "routine_schedule_policy",
            "daily_pulse",
            "quiet_heartbeat",
            "review_cadence",
            "delivery_policy",
            "cron_record_source",
        }

    print("lifeos tests ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
