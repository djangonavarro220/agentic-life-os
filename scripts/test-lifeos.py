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


def write_skill(root: Path, relative: str, name: str, description: str = "") -> None:
    skill_dir = root / relative
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_dir.joinpath("SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description or name}\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp) / "lifeos-data"

        install = run("install", "--runtime", "hermes", data_dir=data_dir)
        assert install["ok"] is True
        assert install["subskills"] == 31
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
            "daily_briefing",
            "quiet_heartbeat",
            "review_cadence",
            "system_improvement_review",
            "delivery_policy",
            "cron_record_source",
        } <= pending_keys

        config = run("config", data_dir=data_dir)
        assert config["ok"] is True
        assert config["config"]["runtime"] == "hermes"
        assert isinstance(config["config"].get("sources", {}), dict)
        assert isinstance(config["config"].get("runtime_inventory", {}).get("skill_sources", []), list)
        assert isinstance(config["config"].get("runtime_inventory", {}).get("capabilities", {}), dict)
        assert isinstance(config["config"].get("runtime_inventory", {}).get("watch_targets", {}), dict)
        assert "dynamic" in config["config"]["runtime_inventory"]["policy"]
        assert "internal_state" not in config["config"]
        assert "caches" not in config["config"]
        assert config["config"]["semantic_setup"]["status"] == "pending"
        tasks_data = json.loads((data_dir / "tasks-todo" / "data.json").read_text(encoding="utf-8"))
        assert isinstance(tasks_data["source_decisions"], dict)
        assert isinstance(tasks_data["internal_state"], dict)
        assert isinstance(tasks_data["caches"], dict)
        assert "optional_global_skills" not in config["config"]
        assert "schedules" not in config["config"]

        hermes_home = Path(tmp) / "hermes-home"
        write_skill(hermes_home / "skills", "productivity/google-workspace", "google-workspace", "Gmail and Calendar")
        write_skill(hermes_home / "skills", "productivity/global-todo-management", "global-todo-management", "Tasks")
        write_skill(hermes_home / "skills", "productivity/cron-governance", "cron-governance", "Cron jobs")
        write_skill(hermes_home / "skills", "autonomous-ai-agents/hermes-agent", "hermes-agent", "Hermes runtime")
        (hermes_home / "config.yaml").write_text(
            "tools:\n  enabled:\n    - skills\n    - terminal\n    - file\n    - cronjob\n    - session_search\n",
            encoding="utf-8",
        )
        (hermes_home / "cron").mkdir(parents=True)
        (hermes_home / "cron" / "jobs.json").write_text(
            json.dumps(
                {
                    "jobs": [
                        {
                            "id": "heartbeat1",
                            "name": "general health heartbeat",
                            "enabled": True,
                            "schedule": "*/30 * * * *",
                            "skills": ["cron-governance", "google-workspace"],
                            "enabled_toolsets": ["terminal", "file", "skills"],
                            "deliver": "origin",
                        },
                        {
                            "id": "tasks1",
                            "name": "task reminder watcher",
                            "enabled": True,
                            "schedule": "0 9 * * *",
                            "skills": ["global-todo-management"],
                            "enabled_toolsets": ["file", "skills"],
                            "deliver": "origin",
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        discovery = run("discover-runtime", "--runtime", "hermes", "--runtime-home", str(hermes_home), data_dir=data_dir)
        assert discovery["ok"] is True, discovery
        assert discovery["runtime"] == "hermes"
        assert discovery["side_effects"] == "life-os-config-only"
        assert discovery["summary"]["skills_discovered"] >= 4
        assert discovery["summary"]["cron_jobs_seen"] == 2
        assert discovery["summary"]["candidate_watch_targets"] >= 2
        inventory = discovery["runtime_inventory"]
        assert inventory["runtime"] == "hermes"
        assert inventory["skill_sources"][0]["count"] >= 4
        assert inventory["capabilities"]["mail"]["status"] == "available"
        assert "google-workspace" in inventory["capabilities"]["mail"]["adapter_skills"]
        assert inventory["capabilities"]["calendar"]["status"] == "available"
        assert inventory["capabilities"]["tasks"]["status"] == "available"
        assert inventory["capabilities"]["crons"]["status"] == "available"
        assert "skills" in inventory["tool_sources"][0]["toolsets"]
        assert "active" in inventory["watch_targets"]
        assert inventory["watch_targets"]["active"] == {}
        assert "general-health-heartbeat" in inventory["watch_targets"]["candidates"]
        assert inventory["watch_targets"]["candidates"]["general-health-heartbeat"]["status"] == "candidate"
        saved_inventory = run("config", data_dir=data_dir)["config"]["runtime_inventory"]
        assert saved_inventory["capabilities"]["mail"]["status"] == "available"
        assert saved_inventory["watch_targets"]["candidates"]["task-reminder-watcher"]["status"] == "candidate"

        next_question = run("next-question", data_dir=data_dir)
        assert next_question["ok"] is True
        assert next_question["complete"] is False
        assert next_question["question"]["key"] == "tasks_source"
        assert next_question["command_hint"] == "lifeos.py answer tasks_source '<answer or runtime pointer>'"
        assert doctor["install_claim"] == "mechanical_only"
        assert doctor["safe_to_claim_fully_installed"] is False
        assert doctor["setup_completion"]["status"] == "incomplete"
        assert doctor["setup_completion"]["headline"] == "Life OS installation is not complete yet."
        assert doctor["setup_completion"]["ask_user_to_complete"] is True
        assert "complete the installation" in doctor["setup_completion"]["next_user_prompt"]
        assert any(item["key"] == "quiet_heartbeat" and item["state"] == "pending_decision" for item in doctor["setup_completion"]["checklist"])
        assert next_question["setup_completion"]["ask_user_to_complete"] is True
        assert "complete the installation" in next_question["setup_completion"]["next_user_prompt"]

        plan = run("plan", data_dir=data_dir)
        assert plan["ok"] is True
        assert plan["semantic_health"]["complete"] is False
        assert "answer all pending semantic setup questions" in plan["steps"][0]
        template_names = {item["name"] for item in plan["cron_templates"]}
        assert {"daily_briefing", "quiet_heartbeat", "weekly_review", "monthly_reset", "quarterly_reset"} <= template_names
        assert all(item["create_by_default"] is False for item in plan["cron_templates"])
        weekly_prompt = next(item["prompt"] for item in plan["cron_templates"] if item["name"] == "weekly_review")
        assert "guided meeting" in weekly_prompt
        assert "due review items" in weekly_prompt

        weekly_skill = (ROOT / "skills/life-os/skills/routines-weekly-review/SKILL.md").read_text(encoding="utf-8")
        assert "guided meeting" in weekly_skill
        assert "review item" in weekly_skill
        assert "paused" in weekly_skill
        assert "context-now" in weekly_skill

        system_skill = (ROOT / "skills/life-os/skills/system-improvement/SKILL.md").read_text(encoding="utf-8")
        assert "heartbeat candidates" in system_skill
        assert "review-item cadence" in system_skill

        context_now_skill = (ROOT / "skills/life-os/skills/context-now/SKILL.md").read_text(encoding="utf-8")
        assert "in-progress guided meetings" in context_now_skill

        heartbeat_skill = (ROOT / "skills/life-os/skills/routines-heartbeat/SKILL.md").read_text(encoding="utf-8")
        assert "candidate watch targets" in heartbeat_skill
        assert "active watch targets" in heartbeat_skill
        assert "capability inventory" in heartbeat_skill
        assert "dynamic skill loading" in heartbeat_skill
        assert "not a fixed checklist" in heartbeat_skill
        assert "do not hard-code a universal list of checks" in heartbeat_skill
        life_os_skill = (ROOT / "skills/life-os/SKILL.md").read_text(encoding="utf-8")
        assert "capability inventory" in life_os_skill
        assert "dynamic heartbeat" in life_os_skill
        assert "runtime adapters execute access" in life_os_skill
        heartbeat_template = next(item for item in plan["cron_templates"] if item["name"] == "quiet_heartbeat")
        assert "skills" in heartbeat_template["toolsets"]
        assert "capability inventory" in heartbeat_template["prompt"]
        assert "dynamically load" in heartbeat_template["prompt"]
        assert "not a fixed checklist" in heartbeat_template["prompt"]

        answered = run("answer", "tasks_source", "runtime todo system", data_dir=data_dir)
        assert answered["ok"] is True
        assert answered["stored_in"] == "config.json"
        assert answered["semantic_health"]["answered"] == ["tasks_source"]
        tasks_data = json.loads((data_dir / "tasks-todo" / "data.json").read_text(encoding="utf-8"))
        assert "tasks_source" not in tasks_data["source_decisions"]
        config_after_answer = run("config", data_dir=data_dir)["config"]
        assert config_after_answer["sources"]["tasks"]["answer"] == "runtime todo system"
        assert config_after_answer["semantic_setup"]["decisions"]["tasks_source"]["stored_in"] == "config.json"
        assert config_after_answer["semantic_setup"]["decisions"]["tasks_source"]["answer"] == "runtime todo system"
        doctor_after_one_answer = run("doctor", data_dir=data_dir)
        assert doctor_after_one_answer["semantic_health"]["complete"] is False
        assert "tasks_source" not in {q["key"] for q in doctor_after_one_answer["semantic_health"]["pending_questions"]}
        assert run("next-question", data_dir=data_dir)["question"]["key"] == "memory_source"

        answered_memory = run("answer", "memory_source", "runtime memory pointer", "--usage", "read current runtime memory instructions first; use pointers only", data_dir=data_dir)
        assert answered_memory["ok"] is True
        config_after_memory = run("config", data_dir=data_dir)["config"]
        assert config_after_memory["sources"]["memory"]["answer"] == "runtime memory pointer"
        assert config_after_memory["sources"]["memory"]["usage"] == "read current runtime memory instructions first; use pointers only"
        assert config_after_memory["semantic_setup"]["decisions"]["memory_source"]["usage"] == "read current runtime memory instructions first; use pointers only"

        for key in pending_keys - {"tasks_source", "memory_source"}:
            run("answer", key, f"test answer for {key}", data_dir=data_dir)
        complete_doctor = run("doctor", data_dir=data_dir)
        assert complete_doctor["semantic_health"]["complete"] is True, complete_doctor
        assert complete_doctor["semantic_health"]["pending_questions"] == []
        assert complete_doctor["install_claim"] == "fully_configured"
        assert complete_doctor["safe_to_claim_fully_installed"] is True
        assert run("next-question", data_dir=data_dir)["complete"] is True
        complete_config = run("config", data_dir=data_dir)["config"]
        assert complete_config["semantic_setup"]["status"] == "complete"
        assert complete_config["semantic_setup"]["decisions"]["tasks_source"]["stored_in"] == "config.json"
        assert complete_config["semantic_setup"]["decisions"]["tasks_source"]["answer"] == "runtime todo system"
        assert complete_config["sources"]["memory"]["answer"] == "runtime memory pointer"
        assert complete_config["policies"]["delivery_policy"]["answer"] == "test answer for delivery_policy"

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
            "daily_briefing",
            "quiet_heartbeat",
            "review_cadence",
            "system_improvement_review",
            "delivery_policy",
            "cron_record_source",
        }

    print("lifeos tests ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
