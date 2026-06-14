#!/usr/bin/env python3
"""Agentic Life OS deterministic helper.

This helper gives the public skill pack real install, doctor, config, and routine
state behavior without owning runtime credentials, delivery routing, or private
memory. Agents still decide what a routine means; this script owns the boring
state mechanics.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LIFE_OS_ROOT = PROJECT_ROOT / "skills" / "life-os"
SKILL_INDEX = LIFE_OS_ROOT / "skill-index.yaml"
INSTALL_YAML = LIFE_OS_ROOT / "install.yaml"
CONFIG_SCHEMA = PROJECT_ROOT / "schemas" / "config.schema.json"

SEMANTIC_QUESTIONS: list[dict[str, str]] = [
    {
        "key": "tasks_source",
        "category": "core-source",
        "owner_skill": "core-config",
        "question": "Where should Life OS read and update tasks or follow-ups for this runtime?",
    },
    {
        "key": "memory_source",
        "category": "core-source",
        "owner_skill": "core-config",
        "question": "Where should Life OS read durable user context and preferences, and what runtime-specific memory instructions should agents follow when using it?",
    },
    {
        "key": "routine_schedule_policy",
        "category": "core-policy",
        "owner_skill": "core-config",
        "question": "Should Life OS stay manual, propose schedules only, or create/maintain runtime cron jobs after approval?",
    },
    {
        "key": "daily_briefing",
        "category": "routine",
        "owner_skill": "routines-pulse",
        "question": "What existing daily briefing or pulse routines already exist in the active runtime, and should Life OS reuse, ignore, or propose changes to them?",
    },
    {
        "key": "quiet_heartbeat",
        "category": "routine",
        "owner_skill": "routines-heartbeat",
        "question": "What existing heartbeat/watch routines already exist in the active runtime, and should Life OS reuse, ignore, or propose changes to them? Include frequency, delivery, and no-news policy.",
    },
    {
        "key": "review_cadence",
        "category": "core-policy",
        "owner_skill": "core-config",
        "question": "What existing review routines or cadence signals already exist in the active runtime, and which should Life OS reuse, ignore, or propose changing?",
    },
    {
        "key": "system_improvement_review",
        "category": "routine",
        "owner_skill": "system-improvement",
        "question": "What existing system-improvement, skill-maintenance, or improvement-backlog routines already exist, and should Life OS reuse, ignore, or propose changes to them?",
    },
    {
        "key": "delivery_policy",
        "category": "core-policy",
        "owner_skill": "core-config",
        "question": "What runtime-owned delivery routes already exist for similar routine output, and which pointer or policy should Life OS reuse?",
    },
    {
        "key": "cron_record_source",
        "category": "core-source",
        "owner_skill": "core-config",
        "question": "Where does the active runtime already store routine run records and cron output history, and how should Life OS read it without duplicating it?",
    },
]
SEMANTIC_VERSION = 1

HORIZONTAL_CORE_DECISION_KEYS = {
    "tasks_source",
    "memory_source",
    "cron_record_source",
    "routine_schedule_policy",
    "review_cadence",
    "delivery_policy",
}

CORE_SOURCE_KEY_MAP = {
    "tasks_source": "tasks",
    "memory_source": "memory",
    "cron_record_source": "cron_records",
}

CORE_POLICY_KEYS = {
    "routine_schedule_policy",
    "review_cadence",
    "delivery_policy",
}

CRON_TEMPLATES: list[dict[str, Any]] = [
    {
        "name": "daily_briefing",
        "schedule": "0 9 * * *",
        "skills": ["life-os", "routines-pulse"],
        "delivery": "runtime-owned destination selected during setup",
        "create_by_default": False,
        "prompt": "Run the Life OS daily briefing. Read semantic_setup first. If setup is incomplete, report the next missing decision instead of pretending the routine is live. Keep it short: today focus, waiting items, risks, and next action. If there is no actionable change, stay silent according to the saved delivery policy.",
    },
    {
        "name": "quiet_heartbeat",
        "schedule": "every 3h",
        "skills": ["life-os", "routines-heartbeat"],
        "toolsets": ["skills"],
        "delivery": "runtime-owned destination selected during setup",
        "create_by_default": False,
        "prompt": "Run the Life OS dynamic heartbeat. Read semantic_setup and the capability inventory first. This is not a fixed checklist: discover active watch targets, select only the relevant runtime adapters, dynamically load the needed skills, and return [SILENT] unless the saved policy says a change is actionable. Candidate watch targets must be approved before becoming active. If a needed capability or skill is missing, report the gap and propose a config/cron update instead of improvising.",
    },
    {
        "name": "weekly_review",
        "schedule": "0 18 * * 0",
        "skills": ["life-os", "routines-weekly-review", "system-improvement"],
        "delivery": "runtime-owned destination selected during setup",
        "create_by_default": False,
        "prompt": "Run the Life OS weekly review as a guided meeting. Read semantic_setup and the relevant skill-owned source pointers, gather due review items, ask one focused question at a time, and record paused/in-progress meeting state so context-now can resurface it. Summarize decisions, risks, waiting items, next actions, and a small system-improvement section with skill candidates or routine tuning only when useful.",
    },
    {
        "name": "monthly_reset",
        "schedule": "0 18 1 * *",
        "skills": ["life-os", "routines-monthly-review", "system-improvement"],
        "delivery": "runtime-owned destination selected during setup",
        "create_by_default": False,
        "prompt": "Run the Life OS monthly reset as a guided meeting. Gather due monthly review items, review slow-moving domains and stale routines, ask one focused question at a time, and record paused/in-progress meeting state instead of sending a dashboard dump.",
    },
    {
        "name": "quarterly_reset",
        "schedule": "0 18 1 */3 *",
        "skills": ["life-os", "routines-quarterly-review", "system-improvement"],
        "delivery": "runtime-owned destination selected during setup",
        "create_by_default": False,
        "prompt": "Run the Life OS quarterly reset as a guided meeting. Gather due quarterly review items, review strategic direction and stale system assumptions, ask one focused question at a time, and record paused/in-progress meeting state instead of sending a dashboard dump.",
    },
]

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_data_dir() -> Path:
    override = os.environ.get("LIFEOS_DATA_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".life-os"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    tmp.replace(path)


def default_skill_data(name: str, now: str) -> dict[str, Any]:
    return {
        "skill": name,
        "created_at": now,
        "runs": [],
        "source_decisions": {},
        "setup_decisions": {},
        "internal_state": {},
        "caches": {},
        "preferences": {},
    }


def ensure_skill_data(data_dir: Path, name: str, now: str) -> dict[str, Any]:
    path = data_dir / name / "data.json"
    data = read_json(path, default_skill_data(name, now))
    if not isinstance(data, dict):
        data = default_skill_data(name, now)
    data.setdefault("skill", name)
    data.setdefault("created_at", now)
    data.setdefault("runs", [])
    data.setdefault("source_decisions", {})
    data.setdefault("setup_decisions", {})
    data.setdefault("internal_state", {})
    data.setdefault("caches", {})
    data.setdefault("preferences", {})
    write_json(path, data)
    return data


def prune_empty_legacy_root_domain_keys(config: dict[str, Any]) -> list[str]:
    """Remove empty legacy domain-state containers from global config.

    `sources` is allowed in global config for horizontal core pointers such as
    tasks, memory, and cron records. Domain-specific operational state still
    belongs in the owning skill data file.
    """
    warnings: list[str] = []
    for key in ("internal_state", "caches"):
        value = config.get(key)
        if value == {}:
            config.pop(key, None)
        elif value is not None:
            warnings.append(
                f"legacy global config key '{key}' is non-empty; move domain entries to the owning skill data file after user approval"
            )
    return warnings


def semantic_decision_answer(data_dir: Path | None, setup: dict[str, Any], key: str) -> str | None:
    decision = setup.get("decisions", {}).get(key)
    if not isinstance(decision, dict):
        return None
    direct_answer = decision.get("answer")
    if isinstance(direct_answer, str) and direct_answer.strip():
        return direct_answer
    if data_dir is None:
        return None
    owner_skill = decision.get("owner_skill")
    if not isinstance(owner_skill, str) or not owner_skill:
        return None
    skill_data = read_json(data_dir / owner_skill / "data.json", {})
    if not isinstance(skill_data, dict):
        return None
    setup_decisions = skill_data.get("setup_decisions", {})
    if not isinstance(setup_decisions, dict):
        return None
    stored = setup_decisions.get(key)
    if not isinstance(stored, dict):
        return None
    answer = stored.get("answer")
    return answer if isinstance(answer, str) and answer.strip() else None


def ensure_runtime_inventory(config: dict[str, Any], now: str) -> dict[str, Any]:
    """Ensure config has the containers for runtime capability discovery."""
    inventory = config.setdefault("runtime_inventory", {})
    inventory.setdefault(
        "policy",
        "Use dynamic runtime discovery: keep an inventory of skills, tools, adapters, sources, and watch targets; load only the needed capability at runtime instead of hard-coding a universal checklist.",
    )
    inventory.setdefault("skill_sources", [])
    inventory.setdefault("tool_sources", [])
    inventory.setdefault("capabilities", {})
    inventory.setdefault("watch_targets", {})
    inventory.setdefault("updated_at", now)
    return inventory


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unnamed"


def parse_skill_name(skill_file: Path) -> str:
    text = skill_file.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines()[:30]:
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"\'')
    return skill_file.parent.name


def discover_skill_names(skills_dir: Path) -> list[str]:
    if not skills_dir.exists():
        return []
    names: list[str] = []
    for skill_file in sorted(skills_dir.rglob("SKILL.md")):
        try:
            names.append(parse_skill_name(skill_file))
        except OSError:
            continue
    return sorted(set(name for name in names if name))


def parse_enabled_toolsets(config_file: Path) -> list[str]:
    if not config_file.exists():
        return []
    toolsets: list[str] = []
    in_enabled = False
    for raw in config_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = raw.strip()
        if stripped.startswith("enabled:"):
            in_enabled = True
            continue
        if in_enabled:
            if stripped.startswith("-"):
                value = stripped[1:].strip().strip('"\'')
                if value:
                    toolsets.append(value)
                continue
            if stripped and not raw.startswith(" "):
                in_enabled = False
    return sorted(set(toolsets))


def load_runtime_jobs(runtime_home: Path) -> list[dict[str, Any]]:
    data = read_json(runtime_home / "cron" / "jobs.json", {})
    jobs = data.get("jobs", []) if isinstance(data, dict) else data if isinstance(data, list) else []
    return [job for job in jobs if isinstance(job, dict)]


def capability(status: str, adapter_skills: list[str], toolsets: list[str], evidence: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "adapter_skills": sorted(set(adapter_skills)),
        "toolsets": sorted(set(toolsets)),
        "evidence": sorted(set(evidence or [])),
    }


def build_capabilities(skill_names: list[str], toolsets: list[str], jobs: list[dict[str, Any]]) -> dict[str, Any]:
    job_skills = {skill for job in jobs for skill in (job.get("skills") or []) if isinstance(skill, str)}
    all_skills = set(skill_names) | job_skills

    def matching(*needles: str) -> list[str]:
        return [name for name in all_skills if any(needle in name for needle in needles)]

    mail = matching("google-workspace", "gmail", "mail", "integrations-mail")
    calendar = matching("google-workspace", "calendar", "integrations-calendar")
    tasks = matching("global-todo", "tasks-todo", "todo", "task")
    crons = matching("cron", "hermes-agent", "human-cron-reports")
    memory = matching("memory", "canonical", "life-os", "hermes-agent")
    browser = matching("browser", "web")

    return {
        "mail": capability("available" if mail else "missing", mail, ["skills"] if mail else []),
        "calendar": capability("available" if calendar else "missing", calendar, ["skills"] if calendar else []),
        "tasks": capability("available" if tasks else "missing", tasks, ["skills", "file"] if tasks else []),
        "crons": capability("available" if crons or jobs else "missing", crons, ["cronjob", "terminal", "skills"] if crons or jobs else [], ["cron/jobs.json"] if jobs else []),
        "memory": capability("available" if memory else "unknown", memory, ["skills", "file"] if memory else []),
        "browser_web": capability("available" if browser or "browser" in toolsets or "web" in toolsets else "missing", browser, [t for t in ("browser", "web", "skills") if t in toolsets or t == "skills"]),
    }


def build_candidate_watch_targets(jobs: list[dict[str, Any]]) -> dict[str, Any]:
    candidates: dict[str, Any] = {}
    watch_words = ("watch", "heartbeat", "latido", "reminder", "recordatorio", "check", "seguimiento", "briefing", "pulse")
    for job in jobs:
        name = str(job.get("name") or job.get("id") or "job")
        prompt = str(job.get("prompt_preview") or job.get("prompt") or "")
        if not any(word in f"{name} {prompt}".lower() for word in watch_words):
            continue
        candidates[slugify(name)] = {
            "status": "candidate",
            "runtime_job_id": str(job.get("id") or job.get("job_id") or ""),
            "runtime_job_name": name,
            "schedule": str(job.get("schedule") or ""),
            "enabled": bool(job.get("enabled", False)),
            "adapter_skills": [skill for skill in (job.get("skills") or []) if isinstance(skill, str)],
            "toolsets": [tool for tool in (job.get("enabled_toolsets") or []) if isinstance(tool, str)],
            "approval_required_to_activate": True,
        }
    return candidates


def default_runtime_home(runtime: str, override: str | None) -> Path:
    if override:
        return Path(override).expanduser()
    if runtime == "openclaw":
        return Path.home() / ".openclaw"
    return Path.home() / ".hermes"


def ensure_semantic_setup(config: dict[str, Any], now: str) -> dict[str, Any]:
    """Ensure the config contains the semantic install checklist."""
    setup = config.setdefault("semantic_setup", {})
    setup.setdefault("version", SEMANTIC_VERSION)
    setup.setdefault("created_at", now)
    setup.setdefault("decisions", {})
    setup.setdefault(
        "policy",
        "Ask and save every required setup decision before claiming Life OS is fully installed.",
    )

    questions = setup.setdefault("questions", {})
    for item in SEMANTIC_QUESTIONS:
        questions.setdefault(
            item["key"],
            {
                "key": item["key"],
                "category": item["category"],
                "question": item["question"],
                "owner_skill": item["owner_skill"],
                "required": True,
            },
        )
    setup["updated_at"] = now
    refresh_semantic_status(config, now)
    return setup


def semantic_health(config: dict[str, Any] | None, data_dir: Path | None = None) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {
            "complete": False,
            "answered": [],
            "missing": [item["key"] for item in SEMANTIC_QUESTIONS],
            "pending_questions": SEMANTIC_QUESTIONS,
        }
    raw_setup = config.get("semantic_setup")
    setup = raw_setup if isinstance(raw_setup, dict) else {}
    answered: list[str] = []
    pending: list[dict[str, str]] = []
    for item in SEMANTIC_QUESTIONS:
        answer = semantic_decision_answer(data_dir, setup, item["key"])
        if isinstance(answer, str) and answer.strip():
            answered.append(item["key"])
        else:
            pending.append(item)
    return {
        "complete": not pending,
        "answered": answered,
        "missing": [item["key"] for item in pending],
        "pending_questions": pending,
    }


def setup_completion_summary(health: dict[str, Any]) -> dict[str, Any]:
    """Return a user-facing semantic setup checklist."""
    answered = set(health.get("answered", []))
    pending_questions = health.get("pending_questions", [])
    pending_by_key = {
        item.get("key"): item
        for item in pending_questions
        if isinstance(item, dict) and isinstance(item.get("key"), str)
    }
    checklist: list[dict[str, Any]] = []
    for item in SEMANTIC_QUESTIONS:
        key = item["key"]
        pending = pending_by_key.get(key)
        checklist.append(
            {
                "key": key,
                "owner_skill": item["owner_skill"],
                "category": item["category"],
                "state": "answered" if key in answered else "pending_decision",
                "question": (pending or item)["question"],
            }
        )
    complete = bool(health.get("complete"))
    if complete:
        headline = "Life OS installation is complete."
        next_user_prompt = "No semantic setup decisions are pending. Do not create or change runtime crons unless the user explicitly approves a runtime change."
    else:
        missing = health.get("missing", [])
        missing_text = ", ".join(str(key) for key in missing)
        headline = "Life OS installation is not complete yet."
        next_user_prompt = (
            "To complete the installation, inspect the active runtime for the pending items, "
            "summarize what already exists, then ask the user whether to reuse it, ignore it, "
            "or approve adding the missing pieces. Pending: " + missing_text
        )
    return {
        "status": "complete" if complete else "incomplete",
        "headline": headline,
        "ask_user_to_complete": not complete,
        "checklist": checklist,
        "next_user_prompt": next_user_prompt,
    }


def refresh_semantic_status(config: dict[str, Any], now: str, data_dir: Path | None = None) -> dict[str, Any]:
    setup = config.setdefault("semantic_setup", {})
    health = semantic_health(config, data_dir)
    setup["status"] = "complete" if health["complete"] else "pending"
    setup["missing"] = health["missing"]
    setup["updated_at"] = now
    return health


@dataclass(frozen=True)
class Subskill:
    name: str
    path: str
    category: str


def parse_skill_index(path: Path = SKILL_INDEX) -> dict[str, Subskill]:
    """Parse the tiny repo-owned skill-index.yaml without external deps."""
    if not path.exists():
        raise FileNotFoundError(path)

    subskills: dict[str, dict[str, Any]] = {}
    current: str | None = None
    in_subskills = False

    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if raw == "subskills:":
            in_subskills = True
            continue
        if not in_subskills:
            continue
        if not raw.startswith("  "):
            in_subskills = False
            current = None
            continue
        if raw.startswith("  ") and not raw.startswith("    ") and raw.strip().endswith(":"):
            current = raw.strip()[:-1]
            subskills[current] = {}
            continue
        if current and raw.startswith("    ") and ":" in raw:
            key, value = raw.strip().split(":", 1)
            value = value.strip()
            if value.lower() == "true":
                parsed: Any = True
            elif value.lower() == "false":
                parsed = False
            else:
                parsed = value.strip('"')
            subskills[current][key] = parsed

    return {
        name: Subskill(
            name=name,
            path=str(meta.get("path", "")),
            category=str(meta.get("category", "uncategorized")),
        )
        for name, meta in subskills.items()
    }


def validate_repo() -> list[str]:
    errors: list[str] = []
    if not LIFE_OS_ROOT.exists():
        errors.append("skills/life-os is missing")
    if not SKILL_INDEX.exists():
        errors.append("skills/life-os/skill-index.yaml is missing")
    if not INSTALL_YAML.exists():
        errors.append("skills/life-os/install.yaml is missing")
    if not CONFIG_SCHEMA.exists():
        errors.append("schemas/config.schema.json is missing")

    try:
        subskills = parse_skill_index()
    except Exception as exc:
        return errors + [f"failed to parse skill-index.yaml: {exc}"]

    if not subskills:
        errors.append("skill-index.yaml has no subskills")

    for name, subskill in subskills.items():
        skill_file = LIFE_OS_ROOT / subskill.path
        schema_file = skill_file.parent / "schemas" / "data.schema.json"
        if not skill_file.exists():
            errors.append(f"{name}: missing {skill_file.relative_to(PROJECT_ROOT)}")
        if not schema_file.exists():
            errors.append(f"{name}: missing {schema_file.relative_to(PROJECT_ROOT)}")
        else:
            try:
                json.loads(schema_file.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"{name}: invalid schema JSON: {exc}")

    try:
        json.loads(CONFIG_SCHEMA.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"schemas/config.schema.json invalid JSON: {exc}")

    return errors


def install(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    subskills = parse_skill_index()
    now = utc_now()

    data_dir.mkdir(parents=True, exist_ok=True)
    for name in subskills:
        ensure_skill_data(data_dir, name, now)

    runtime = {
        "runtime": args.runtime,
        "repo": str(PROJECT_ROOT),
        "life_os_skill_dir": str(LIFE_OS_ROOT),
        "detected_at": now,
        "runtime_owned": {
            "credentials": True,
            "delivery_routing": True,
            "cron_jobs": True,
            "memory": True,
        },
    }
    installed = {
        "installed": True,
        "installed_at": now,
        "version": "0.0.0",
        "data_dir": str(data_dir),
        "subskills": sorted(subskills),
    }
    config = read_json(data_dir / "config.json", {})
    config.setdefault("enabled", True)
    config.setdefault("runtime", args.runtime)
    config.setdefault("skills", {name: {"enabled": True} for name in sorted(subskills)})
    config.setdefault("created_at", now)
    legacy_warnings = prune_empty_legacy_root_domain_keys(config)
    ensure_runtime_inventory(config, now)
    ensure_semantic_setup(config, now)
    refresh_semantic_status(config, now, data_dir)
    config["updated_at"] = now

    write_json(data_dir / "runtime.json", runtime)
    write_json(data_dir / "installed.json", installed)
    write_json(data_dir / "config.json", config)
    health = semantic_health(config, data_dir)

    return {
        "ok": True,
        "action": "install",
        "data_dir": str(data_dir),
        "runtime": args.runtime,
        "subskills": len(subskills),
        "semantic_health": health,
        "setup_completion": setup_completion_summary(health),
        "install_claim": "fully_configured" if health["complete"] else "mechanical_only",
        "safe_to_claim_fully_installed": bool(health["complete"]),
        "warnings": legacy_warnings,
        "note": "Runtime cron creation, delivery routing, task source changes, credentials, and memory remain runtime-owned and are not modified by this helper.",
    }


def doctor(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    errors = validate_repo()
    warnings: list[str] = []

    installed = read_json(data_dir / "installed.json", None)
    runtime = read_json(data_dir / "runtime.json", None)
    config = read_json(data_dir / "config.json", None)
    subskills = parse_skill_index() if not errors else {}

    if not data_dir.exists():
        warnings.append(f"data dir does not exist yet: {data_dir}")
    if installed is None:
        warnings.append("installed.json missing; run install")
    if runtime is None:
        warnings.append("runtime.json missing; run install")
    if config is None:
        warnings.append("config.json missing; run install")
    if config is not None and not isinstance(config.get("skills", {}), dict):
        errors.append("config.json skills must be an object")
    if isinstance(config, dict):
        now = utc_now()
        warnings.extend(prune_empty_legacy_root_domain_keys(config))
        ensure_runtime_inventory(config, now)
        ensure_semantic_setup(config, now)
        refresh_semantic_status(config, now, data_dir)
        write_json(data_dir / "config.json", config)
    health = semantic_health(config, data_dir)

    missing_data = []
    for name in subskills:
        if not (data_dir / name / "data.json").exists():
            missing_data.append(name)
    if missing_data:
        warnings.append(f"missing per-skill data files: {', '.join(missing_data)}")

    return {
        "ok": not errors,
        "action": "doctor",
        "data_dir": str(data_dir),
        "repo": str(PROJECT_ROOT),
        "subskills": len(subskills),
        "errors": errors,
        "warnings": warnings,
        "semantic_health": health,
        "setup_completion": setup_completion_summary(health),
        "install_claim": "fully_configured" if health["complete"] else "mechanical_only",
        "safe_to_claim_fully_installed": bool(health["complete"]),
    }


def next_question(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    config = read_json(data_dir / "config.json", None)
    if isinstance(config, dict):
        now = utc_now()
        ensure_runtime_inventory(config, now)
        ensure_semantic_setup(config, now)
        refresh_semantic_status(config, now, data_dir)
        write_json(data_dir / "config.json", config)
    health = semantic_health(config, data_dir)
    if health["complete"]:
        return {
            "ok": True,
            "action": "next-question",
            "data_dir": str(data_dir),
            "complete": True,
            "question": None,
            "command_hint": None,
            "semantic_health": health,
            "setup_completion": setup_completion_summary(health),
        }
    question = health["pending_questions"][0]
    return {
        "ok": True,
        "action": "next-question",
        "data_dir": str(data_dir),
        "complete": False,
        "question": question,
        "command_hint": f"lifeos.py answer {question['key']} '<answer or runtime pointer>'",
        "semantic_health": health,
        "setup_completion": setup_completion_summary(health),
    }


def plan(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    config = read_json(data_dir / "config.json", None)
    if isinstance(config, dict):
        now = utc_now()
        ensure_runtime_inventory(config, now)
        ensure_semantic_setup(config, now)
        refresh_semantic_status(config, now, data_dir)
        write_json(data_dir / "config.json", config)
    health = semantic_health(config, data_dir)
    steps = [
        "answer all pending semantic setup questions and save them with lifeos.py answer",
        "run lifeos.py doctor until semantic_health.complete is true",
        "only after approval, create runtime-owned cron jobs from the templates",
        "run runtime-native visibility and cron status checks after any runtime change",
    ]
    return {
        "ok": True,
        "action": "plan",
        "data_dir": str(data_dir),
        "semantic_health": health,
        "setup_completion": setup_completion_summary(health),
        "steps": steps,
        "cron_templates": CRON_TEMPLATES,
        "side_effects": "none; this command does not create runtime crons or delivery routes",
    }


def answer(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    now = utc_now()
    config = read_json(data_dir / "config.json", {})
    if not isinstance(config, dict):
        config = {}
    config.setdefault("enabled", True)
    config.setdefault("runtime", args.runtime)
    config.setdefault("created_at", now)
    prune_empty_legacy_root_domain_keys(config)
    ensure_runtime_inventory(config, now)
    setup = ensure_semantic_setup(config, now)

    valid_keys = {item["key"] for item in SEMANTIC_QUESTIONS}
    if args.key not in valid_keys:
        raise ValueError(f"unknown semantic decision key: {args.key}")
    if not args.answer.strip():
        raise ValueError("answer must not be empty")

    question = next(item for item in SEMANTIC_QUESTIONS if item["key"] == args.key)
    owner_skill = question["owner_skill"]
    answer_text = args.answer.strip()
    note_text = args.note.strip() if args.note else None
    usage_text = args.usage.strip() if args.usage else None

    decisions = setup.setdefault("decisions", {})
    if args.key in HORIZONTAL_CORE_DECISION_KEYS:
        decision_record = {
            "answer": answer_text,
            "updated_at": now,
            "source": "user",
            "category": question["category"],
            "stored_in": "config.json",
        }
        if note_text:
            decision_record["note"] = note_text
        if usage_text:
            decision_record["usage"] = usage_text
        decisions[args.key] = decision_record

        if args.key in CORE_SOURCE_KEY_MAP:
            sources = config.setdefault("sources", {})
            sources[CORE_SOURCE_KEY_MAP[args.key]] = {
                "answer": answer_text,
                "updated_at": now,
                "source": "user",
                "semantic_key": args.key,
            }
            if note_text:
                sources[CORE_SOURCE_KEY_MAP[args.key]]["note"] = note_text
            if usage_text:
                sources[CORE_SOURCE_KEY_MAP[args.key]]["usage"] = usage_text
        elif args.key in CORE_POLICY_KEYS:
            policies = config.setdefault("policies", {})
            policies[args.key] = {
                "answer": answer_text,
                "updated_at": now,
                "source": "user",
            }
            if note_text:
                policies[args.key]["note"] = note_text
            if usage_text:
                policies[args.key]["usage"] = usage_text
    else:
        skill_data = ensure_skill_data(data_dir, owner_skill, now)
        setup_decisions = skill_data.setdefault("setup_decisions", {})
        setup_decisions[args.key] = {
            "answer": answer_text,
            "updated_at": now,
            "source": "user",
            "category": question["category"],
        }
        if question["category"] == "source-decisions":
            source_decisions = skill_data.setdefault("source_decisions", {})
            source_decisions[args.key] = {
                "answer": answer_text,
                "updated_at": now,
                "source": "user",
            }
        if note_text:
            setup_decisions[args.key]["note"] = note_text
        if usage_text:
            setup_decisions[args.key]["usage"] = usage_text
        write_json(data_dir / owner_skill / "data.json", skill_data)

        decisions[args.key] = {
            "owner_skill": owner_skill,
            "stored_in": "config.json" if args.key in HORIZONTAL_CORE_DECISION_KEYS else f"{owner_skill}/data.json",
            "updated_at": now,
            "source": "user",
        }
    health = refresh_semantic_status(config, now, data_dir)
    config["updated_at"] = now
    write_json(data_dir / "config.json", config)
    return {
        "ok": True,
        "action": "answer",
        "data_dir": str(data_dir),
        "key": args.key,
        "stored_in": "config.json" if args.key in HORIZONTAL_CORE_DECISION_KEYS else f"{owner_skill}/data.json",
        "semantic_health": health,
    }


def discover_runtime(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    now = utc_now()
    runtime_home = default_runtime_home(args.runtime, args.runtime_home)
    config = read_json(data_dir / "config.json", {})
    if not isinstance(config, dict):
        config = {}
    config.setdefault("enabled", True)
    config.setdefault("runtime", args.runtime)
    config.setdefault("created_at", now)
    ensure_semantic_setup(config, now)

    skills_dir = runtime_home / "skills"
    skill_names = discover_skill_names(skills_dir)
    toolsets = parse_enabled_toolsets(runtime_home / "config.yaml")
    jobs = load_runtime_jobs(runtime_home)
    candidates = build_candidate_watch_targets(jobs)

    inventory = ensure_runtime_inventory(config, now)
    inventory.update(
        {
            "runtime": args.runtime,
            "discovered_at": now,
            "discovery_mode": "read-only-runtime; writes-life-os-config-only",
            "skill_sources": [
                {
                    "runtime": args.runtime,
                    "kind": "runtime_skills_dir",
                    "path": str(skills_dir),
                    "available": skills_dir.exists(),
                    "count": len(skill_names),
                    "skills": skill_names,
                }
            ],
            "tool_sources": [
                {
                    "runtime": args.runtime,
                    "kind": "runtime_config_toolsets",
                    "path": str(runtime_home / "config.yaml"),
                    "available": (runtime_home / "config.yaml").exists(),
                    "toolsets": toolsets,
                }
            ],
            "capabilities": build_capabilities(skill_names, toolsets, jobs),
            "watch_targets": {
                "active": inventory.get("watch_targets", {}).get("active", {}) if isinstance(inventory.get("watch_targets"), dict) else {},
                "candidates": candidates,
            },
        }
    )
    config["updated_at"] = now
    write_json(data_dir / "config.json", config)
    return {
        "ok": True,
        "action": "discover-runtime",
        "runtime": args.runtime,
        "data_dir": str(data_dir),
        "runtime_inventory": inventory,
        "summary": {
            "skills_discovered": len(skill_names),
            "toolsets_discovered": len(toolsets),
            "cron_jobs_seen": len(jobs),
            "candidate_watch_targets": len(candidates),
        },
        "side_effects": "life-os-config-only",
    }


def select_heartbeat_candidate(candidates: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for key, candidate in candidates.items():
        if not isinstance(candidate, dict):
            continue
        name = str(candidate.get("runtime_job_name") or key).lower()
        score = 0
        if "heartbeat" in name or "latido" in name:
            score += 100
        if "health" in name or "general" in name:
            score += 20
        if candidate.get("enabled", False):
            score += 10
        if "life" in name or "os" in name:
            score += 5
        if score:
            scored.append((score, key, candidate))
    if not scored:
        return None
    scored.sort(key=lambda item: (-item[0], item[1]))
    _, key, candidate = scored[0]
    return key, candidate


def quiet_heartbeat_template() -> dict[str, Any]:
    return next(item for item in CRON_TEMPLATES if item["name"] == "quiet_heartbeat")


def define_heartbeat(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    now = utc_now()
    config = read_json(data_dir / "config.json", {})
    if not isinstance(config, dict):
        config = {}
    inventory = ensure_runtime_inventory(config, now)
    watch_targets = inventory.get("watch_targets", {}) if isinstance(inventory.get("watch_targets"), dict) else {}
    candidates = watch_targets.get("candidates", {}) if isinstance(watch_targets.get("candidates"), dict) else {}
    selected = select_heartbeat_candidate(candidates)
    if selected:
        key, candidate = selected
        heartbeat = {
            "status": "defined",
            "source": "existing_runtime_job",
            "key": key,
            "runtime_job_id": candidate.get("runtime_job_id", ""),
            "runtime_job_name": candidate.get("runtime_job_name", key),
            "schedule": candidate.get("schedule", ""),
            "adapter_skills": candidate.get("adapter_skills", []),
            "toolsets": candidate.get("toolsets", []),
            "relationship_to_runtime_job": "reuse_as_orchestrator",
            "approval_required_before_runtime_change": True,
            "updated_at": now,
        }
    else:
        heartbeat = {
            "status": "needs_creation",
            "source": "life_os_template",
            "key": "quiet_heartbeat",
            "relationship_to_runtime_job": "create_runtime_job_after_approval",
            "approval_required_before_runtime_change": True,
            "template": quiet_heartbeat_template(),
            "updated_at": now,
        }
    inventory["heartbeat"] = heartbeat
    config["updated_at"] = now
    write_json(data_dir / "config.json", config)
    return {
        "ok": True,
        "action": "define-heartbeat",
        "data_dir": str(data_dir),
        "heartbeat": heartbeat,
        "side_effects": "life-os-config-only",
        "next_step": "Ask the user before creating or changing any runtime cron.",
    }


def classify_watch_target(candidate: dict[str, Any]) -> str:
    name = str(candidate.get("runtime_job_name") or "").lower()
    schedule = candidate.get("schedule")
    schedule_text = json.dumps(schedule, sort_keys=True) if isinstance(schedule, (dict, list)) else str(schedule or "")
    if "heartbeat" in name or "latido" in name:
        return "review_for_life_os_heartbeat"
    if not candidate.get("enabled", False):
        return "ignore_or_archive_disabled_candidate"
    if "once" in schedule_text or "run_at" in schedule_text:
        return "one_shot_reminder_candidate"
    return "candidate_watch_target"


def propose_watch_targets(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    config = read_json(data_dir / "config.json", {})
    if not isinstance(config, dict):
        config = {}
    inventory = config.get("runtime_inventory", {}) if isinstance(config.get("runtime_inventory"), dict) else {}
    watch_targets = inventory.get("watch_targets", {}) if isinstance(inventory.get("watch_targets"), dict) else {}
    active = watch_targets.get("active", {}) if isinstance(watch_targets.get("active"), dict) else {}
    candidates = watch_targets.get("candidates", {}) if isinstance(watch_targets.get("candidates"), dict) else {}
    proposals: list[dict[str, Any]] = []
    for key, candidate in sorted(candidates.items()):
        if not isinstance(candidate, dict) or key in active:
            continue
        proposals.append(
            {
                "key": key,
                "runtime_job_id": candidate.get("runtime_job_id", ""),
                "runtime_job_name": candidate.get("runtime_job_name", key),
                "enabled": candidate.get("enabled", False),
                "schedule": candidate.get("schedule", ""),
                "adapter_skills": candidate.get("adapter_skills", []),
                "toolsets": candidate.get("toolsets", []),
                "recommended_action": classify_watch_target(candidate),
                "approval_required_to_activate": True,
            }
        )
    return {
        "ok": True,
        "action": "propose-watch-targets",
        "data_dir": str(data_dir),
        "summary": {
            "active": len(active),
            "candidates": len(candidates),
            "proposed": len(proposals),
        },
        "proposals": proposals,
        "activation_requires_user_approval": True,
        "side_effects": "none",
        "next_step": "Ask the user which proposals should become active watch targets; do not activate or edit runtime crons without approval.",
    }


def show_config(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    return {
        "ok": True,
        "data_dir": str(data_dir),
        "runtime": read_json(data_dir / "runtime.json", None),
        "installed": read_json(data_dir / "installed.json", None),
        "config": read_json(data_dir / "config.json", None),
    }


def print_result(result: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print(json.dumps(result, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agentic Life OS helper")
    parser.add_argument("--data-dir", help="Override private data directory")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install", help="Create private Life OS state files")
    p_install.add_argument("--runtime", default="hermes", choices=["hermes", "openclaw", "unknown"])
    p_install.set_defaults(func=install)

    p_doctor = sub.add_parser("doctor", help="Validate repo and private Life OS state")
    p_doctor.set_defaults(func=doctor)

    p_next = sub.add_parser("next-question", help="Show the next required semantic setup question")
    p_next.set_defaults(func=next_question)

    p_plan = sub.add_parser("plan", help="Show semantic setup and cron-template plan without side effects")
    p_plan.set_defaults(func=plan)

    p_answer = sub.add_parser("answer", help="Save one semantic setup decision")
    p_answer.add_argument("--runtime", default="hermes", choices=["hermes", "openclaw", "unknown"])
    p_answer.add_argument("key", help="Semantic decision key to save")
    p_answer.add_argument("answer", help="User-approved answer or runtime pointer")
    p_answer.add_argument("--note", help="Optional safe note about this decision")
    p_answer.add_argument("--usage", help="Optional agent-facing instructions for how to use the saved source or policy")
    p_answer.set_defaults(func=answer)

    p_config = sub.add_parser("config", help="Show Life OS private config/state")
    p_config.set_defaults(func=show_config)

    p_discover = sub.add_parser("discover-runtime", help="Read runtime capabilities into Life OS inventory without external side effects")
    p_discover.add_argument("--runtime", default="hermes", choices=["hermes", "openclaw", "unknown"])
    p_discover.add_argument("--runtime-home", help="Override runtime home for discovery/tests")
    p_discover.set_defaults(func=discover_runtime)

    p_propose = sub.add_parser("propose-watch-targets", help="Propose active watch targets from discovered runtime candidates without side effects")
    p_propose.set_defaults(func=propose_watch_targets)

    p_define_hb = sub.add_parser("define-heartbeat", help="Define the single Life OS heartbeat from an existing runtime job or a creation template")
    p_define_hb.set_defaults(func=define_heartbeat)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True), file=sys.stderr)
        return 1
    print_result(result, args.json)
    return 0 if result.get("ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
