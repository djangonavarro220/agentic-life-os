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
            "autonomy_mode",
            "tasks_source",
            "memory_source",
            "routine_schedule_policy",
            "daily_briefing",
            "quiet_heartbeat",
            "review_cadence",
            "review_cron_install_policy",
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
        context_now_config = run("config", data_dir=data_dir)["config"]["context_now"]
        assert context_now_config["shown_signal_ids"] == []
        assert context_now_config["deferred_signal_queue"] == []
        assert "next assistant turn" in context_now_config["policy"]
        assert "expires_at or stale_after" in context_now_config["policy"]
        context_sources = run("context-sources", data_dir=data_dir)
        assert context_sources["ok"] is True
        assert context_sources["action"] == "context-sources"
        assert context_sources["side_effects"] == "none"
        assert context_sources["agent_must_inspect_runtime"] is True
        assert context_sources["wiring_diagnostics"]["inventory"]["available"] is True
        assert context_sources["wiring_diagnostics"]["inventory"]["agent_should_refresh"] is False
        assert "harness/runtime-native discovery" in context_sources["wiring_diagnostics"]["inventory"]["refresh_instruction"]
        assert "runtime_capabilities" not in context_sources
        assert "available_sources" not in context_sources
        no_inventory_sources = run("context-sources", data_dir=Path(tmp) / "missing-inventory")
        assert no_inventory_sources["wiring_diagnostics"]["inventory"]["available"] is False
        assert no_inventory_sources["wiring_diagnostics"]["inventory"]["agent_should_refresh"] is True
        assert no_inventory_sources["agent_contract"].startswith("This helper is only a wiring diagnostic")
        proposals = run("propose-watch-targets", data_dir=data_dir)
        assert proposals["ok"] is True
        assert proposals["action"] == "propose-watch-targets"
        assert proposals["side_effects"] == "none"
        assert proposals["activation_requires_user_approval"] is True
        assert proposals["summary"]["active"] == 0
        assert proposals["summary"]["proposed"] >= 2
        general = next(item for item in proposals["proposals"] if item["key"] == "general-health-heartbeat")
        assert general["recommended_action"] == "review_for_life_os_heartbeat"
        assert general["approval_required_to_activate"] is True
        task = next(item for item in proposals["proposals"] if item["key"] == "task-reminder-watcher")
        assert task["recommended_action"] == "candidate_watch_target"
        heartbeat = run("define-heartbeat", data_dir=data_dir)
        assert heartbeat["ok"] is True
        assert heartbeat["action"] == "define-heartbeat"
        assert heartbeat["side_effects"] == "life-os-config-only"
        assert heartbeat["heartbeat"]["status"] == "defined"
        assert heartbeat["heartbeat"]["source"] == "existing_runtime_job"
        assert heartbeat["heartbeat"]["key"] == "general-health-heartbeat"
        assert heartbeat["heartbeat"]["relationship_to_runtime_job"] == "reuse_as_orchestrator"
        saved_hb = run("config", data_dir=data_dir)["config"]["runtime_inventory"]["heartbeat"]
        assert saved_hb["key"] == "general-health-heartbeat"
        assert saved_hb["approval_required_before_runtime_change"] is True

        no_hb_home = Path(tmp) / "no-hb-home"
        write_skill(no_hb_home / "skills", "productivity/google-workspace", "google-workspace", "Gmail and Calendar")
        (no_hb_home / "config.yaml").write_text("tools:\n  enabled:\n    - skills\n", encoding="utf-8")
        (no_hb_home / "cron").mkdir(parents=True)
        (no_hb_home / "cron" / "jobs.json").write_text(json.dumps({"jobs": []}), encoding="utf-8")
        no_hb_data_dir = Path(tmp) / "no-hb-lifeos"
        run("install", "--runtime", "hermes", data_dir=no_hb_data_dir)
        run("discover-runtime", "--runtime", "hermes", "--runtime-home", str(no_hb_home), data_dir=no_hb_data_dir)
        missing_hb = run("define-heartbeat", data_dir=no_hb_data_dir)
        assert missing_hb["heartbeat"]["status"] == "needs_creation"
        assert missing_hb["heartbeat"]["source"] == "life_os_template"
        assert missing_hb["heartbeat"]["approval_required_before_runtime_change"] is True
        assert missing_hb["heartbeat"]["template"]["name"] == "quiet_heartbeat"

        next_question = run("next-question", data_dir=data_dir)
        assert next_question["ok"] is True
        assert next_question["complete"] is False
        assert next_question["question"]["key"] == "autonomy_mode"
        assert "Ask me before almost anything" in next_question["question"]["question"]
        assert "Recommended" in next_question["question"]["question"]
        assert "Safe internal" in next_question["question"]["question"]
        assert "approval-first" in next_question["question"]["question"]
        assert "safe-internal" in next_question["question"]["question"]
        assert next_question["command_hint"] == "lifeos.py answer autonomy_mode '<answer or runtime pointer>'"
        assert doctor["install_claim"] == "mechanical_only"
        assert doctor["safe_to_claim_fully_installed"] is False
        assert doctor["setup_completion"]["status"] == "incomplete"
        assert doctor["setup_completion"]["headline"] == "Life OS installation is not complete yet."
        assert doctor["setup_completion"]["ask_user_to_complete"] is True
        assert "complete the installation" in doctor["setup_completion"]["next_user_prompt"]
        assert "agent_next_message" in doctor["setup_completion"]
        assert "I found a mechanical Life OS install" in doctor["setup_completion"]["agent_next_message"]
        assert "run lifeos.py" not in doctor["setup_completion"]["agent_next_message"]
        assert any(item["key"] == "quiet_heartbeat" and item["state"] == "pending_decision" for item in doctor["setup_completion"]["checklist"])
        assert next_question["setup_completion"]["ask_user_to_complete"] is True
        assert "complete the installation" in next_question["setup_completion"]["next_user_prompt"]
        assert "agent_next_message" in next_question["setup_completion"]

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
        assert "semantic setup" in system_skill
        assert "new_source" in system_skill
        assert "new_memory" in system_skill
        assert "During the self-improvement meeting" in system_skill
        assert "inspect the tools" in system_skill
        assert "Do not wait for random runtime discovery" in system_skill
        assert "monthly by default" in system_skill
        assert "review item" in system_skill
        assert "Stay silent" in system_skill
        assert "only newly discovered or changed setup items" in system_skill

        context_now_skill = (ROOT / "skills/life-os/skills/context-now/SKILL.md").read_text(encoding="utf-8")
        assert "in-progress guided meetings" in context_now_skill
        assert "Source ladder" in context_now_skill
        assert "Freshness rules" in context_now_skill
        assert "Evidence" in context_now_skill
        assert "shortest useful current-context answer" in context_now_skill
        assert "Do not force a dashboard" in context_now_skill
        assert "Now:\n- Focus:" not in context_now_skill
        assert "corporate dashboard" in context_now_skill
        assert "Do not write state by default" in context_now_skill
        assert "ephemeral view" in context_now_skill
        assert "archival sludge" in context_now_skill
        assert "inspect broadly" in context_now_skill
        assert "Relevance by horizon" in context_now_skill
        assert "Immediate or today" in context_now_skill
        assert "This week or planning horizon" in context_now_skill
        assert "Explicit domain" in context_now_skill
        assert "If a source is relevant and available, inspect it" in context_now_skill
        assert "do not list inspected sources by default" in context_now_skill
        assert "mention inspected/missing sources only when" in context_now_skill
        assert "at most two or three actionable signals" in context_now_skill
        assert "deferred_signal_queue" in context_now_skill
        assert "next assistant message" in context_now_skill
        assert "Deferred signals" in context_now_skill
        assert "At the start of a `context-now` turn" in context_now_skill
        assert "surface at most one or two deferred signals first" in context_now_skill
        assert "do not turn the queue into an infinite nag list" in context_now_skill
        assert "two or three same-thread turns" in context_now_skill
        assert "background deferred" in context_now_skill
        assert "every deferred signal should include" in context_now_skill
        assert "expires_at` or `stale_after" in context_now_skill
        schema = (ROOT / "schemas/config.schema.json").read_text(encoding="utf-8")
        assert "Compact pointer for a context-now signal" in schema
        assert '"source_pointer"' in schema
        assert '"stale_after"' in schema
        assert '"topic_shift_turns"' in schema
        assert '"background_deferred"' in schema
        assert "Do not follow a fixed priority formula" in context_now_skill
        assert "the agent decides" in context_now_skill
        assert "do not merely suggest what to inspect" in context_now_skill
        core_doctor_skill = (ROOT / "skills/life-os/skills/core-doctor/SKILL.md").read_text(encoding="utf-8")
        assert "agent_next_message" in core_doctor_skill
        assert "Do not ask the user to run helper commands" in core_doctor_skill

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
        assert "The agent operates the system" in life_os_skill
        assert "Semantic setup is revisable" in life_os_skill
        assert "autonomy mode" in life_os_skill
        assert "safe-internal" in life_os_skill
        core_config_skill = (ROOT / "skills/life-os/skills/core-config/SKILL.md").read_text(encoding="utf-8")
        assert "autonomy mode" in core_config_skill
        assert "approval-first" in core_config_skill
        assert "safe-internal" in core_config_skill
        assert "trusted-local" in core_config_skill
        assert "allow-all" in core_config_skill
        assert "Setup is not complete" in core_config_skill
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "agent behavior layer" in readme.splitlines()[2].lower()
        assert "user runs" not in readme.lower()
        heartbeat_template = next(item for item in plan["cron_templates"] if item["name"] == "quiet_heartbeat")
        assert "skills" in heartbeat_template["toolsets"]
        assert "capability inventory" in heartbeat_template["prompt"]
        assert "dynamically load" in heartbeat_template["prompt"]
        assert "not a fixed checklist" in heartbeat_template["prompt"]

        answered_autonomy = run("answer", "autonomy_mode", "safe-internal", "--kind", "custom", data_dir=data_dir)
        assert answered_autonomy["ok"] is True
        assert answered_autonomy["stored_in"] == "config.json"
        autonomy_config = run("config", data_dir=data_dir)["config"]
        assert autonomy_config["policies"]["autonomy_mode"]["answer"] == "safe-internal"
        assert autonomy_config["semantic_setup"]["decisions"]["autonomy_mode"]["answer"] == "safe-internal"
        assert run("next-question", data_dir=data_dir)["question"]["key"] == "tasks_source"

        answered = run("answer", "tasks_source", "runtime todo system", "--kind", "reuse_existing", data_dir=data_dir)
        assert answered["ok"] is True
        assert answered["stored_in"] == "config.json"
        assert answered["decision_kind"] == "reuse_existing"
        assert answered["semantic_health"]["answered"] == ["autonomy_mode", "tasks_source"]
        tasks_data = json.loads((data_dir / "tasks-todo" / "data.json").read_text(encoding="utf-8"))
        assert "tasks_source" not in tasks_data["source_decisions"]
        config_after_answer = run("config", data_dir=data_dir)["config"]
        assert config_after_answer["sources"]["tasks"]["answer"] == "runtime todo system"
        assert config_after_answer["sources"]["tasks"]["decision_kind"] == "reuse_existing"
        assert config_after_answer["semantic_setup"]["decisions"]["tasks_source"]["stored_in"] == "config.json"
        assert config_after_answer["semantic_setup"]["decisions"]["tasks_source"]["answer"] == "runtime todo system"
        assert config_after_answer["semantic_setup"]["decisions"]["tasks_source"]["decision_kind"] == "reuse_existing"
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

        for key in pending_keys - {"autonomy_mode", "tasks_source", "memory_source"}:
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
        assert complete_config["policies"]["review_cron_install_policy"]["answer"] == "test answer for review_cron_install_policy"
        assert complete_config["policies"]["autonomy_mode"]["answer"] == "safe-internal"

    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp) / "legacy-lifeos-data"
        data_dir.mkdir()
        (data_dir / "config.json").write_text(json.dumps({"enabled": True, "runtime": "hermes", "skills": {}}), encoding="utf-8")
        doctor = run("doctor", data_dir=data_dir)
        assert doctor["ok"] is True, doctor
        saved = json.loads((data_dir / "config.json").read_text(encoding="utf-8"))
        assert saved["semantic_setup"]["status"] == "pending"
        assert set(saved["semantic_setup"]["missing"]) == {
            "autonomy_mode",
            "tasks_source",
            "memory_source",
            "routine_schedule_policy",
            "daily_briefing",
            "quiet_heartbeat",
            "review_cadence",
            "review_cron_install_policy",
            "system_improvement_review",
            "delivery_policy",
            "cron_record_source",
        }

    print("lifeos tests ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
