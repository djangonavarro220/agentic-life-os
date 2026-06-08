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
        "category": "source-decisions",
        "owner_skill": "tasks-todo",
        "question": "Where should Life OS read and update tasks or follow-ups for this runtime?",
    },
    {
        "key": "memory_source",
        "category": "source-decisions",
        "owner_skill": "integrations-runtime",
        "question": "Where should Life OS read durable user context and preferences?",
    },
    {
        "key": "routine_schedule_policy",
        "category": "runtime-owned",
        "owner_skill": "integrations-runtime",
        "question": "Should Life OS stay manual, propose schedules only, or create/maintain runtime cron jobs after approval?",
    },
    {
        "key": "daily_pulse",
        "category": "routine",
        "owner_skill": "routines-pulse",
        "question": "Should a daily pulse exist, and if yes what cadence and delivery pointer should it use?",
    },
    {
        "key": "quiet_heartbeat",
        "category": "routine",
        "owner_skill": "routines-heartbeat",
        "question": "Should a quiet heartbeat exist, and what frequency/no-news policy should it use?",
    },
    {
        "key": "review_cadence",
        "category": "routine",
        "owner_skill": "routines-weekly-review",
        "question": "Which weekly, monthly, or quarterly review routines should be enabled?",
    },
    {
        "key": "delivery_policy",
        "category": "runtime-owned",
        "owner_skill": "integrations-runtime",
        "question": "Where should user-facing Life OS routine output be delivered, using runtime-owned aliases or pointers?",
    },
    {
        "key": "cron_record_source",
        "category": "source-decisions",
        "owner_skill": "integrations-runtime",
        "question": "Where should Life OS read routine run records and cron output history?",
    },
]
SEMANTIC_VERSION = 1

CRON_TEMPLATES: list[dict[str, Any]] = [
    {
        "name": "daily_pulse",
        "schedule": "0 9 * * *",
        "skills": ["life-os", "routines-pulse"],
        "delivery": "runtime-owned destination selected during setup",
        "create_by_default": False,
        "prompt": "Run the Life OS daily pulse. Read semantic_setup first. If setup is incomplete, report the next missing decision instead of pretending the routine is live. If there is no actionable change, stay silent according to the saved delivery policy.",
    },
    {
        "name": "quiet_heartbeat",
        "schedule": "every 3h",
        "skills": ["life-os", "routines-heartbeat"],
        "delivery": "runtime-owned destination selected during setup",
        "create_by_default": False,
        "prompt": "Run the Life OS quiet heartbeat. Read semantic_setup first, then check only the sources configured in the relevant skill data files. Return [SILENT] unless the saved policy says a change is actionable.",
    },
    {
        "name": "weekly_review",
        "schedule": "0 18 * * 0",
        "skills": ["life-os", "routines-weekly-review"],
        "delivery": "runtime-owned destination selected during setup",
        "create_by_default": False,
        "prompt": "Run the Life OS weekly review. Read semantic_setup and the relevant skill-owned source pointers. Summarize only decisions, risks, waiting items, and next actions.",
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
    """Remove empty legacy domain containers from global config.

    Non-empty values are preserved so the helper never silently migrates or
    deletes user data. Doctor reports them as warnings instead.
    """
    warnings: list[str] = []
    for key in ("sources", "internal_state", "caches"):
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
        "install_claim": "fully_configured" if health["complete"] else "mechanical_only",
        "safe_to_claim_fully_installed": bool(health["complete"]),
    }


def next_question(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    config = read_json(data_dir / "config.json", None)
    if isinstance(config, dict):
        now = utc_now()
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
    }


def plan(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    config = read_json(data_dir / "config.json", None)
    if isinstance(config, dict):
        now = utc_now()
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
    setup = ensure_semantic_setup(config, now)

    valid_keys = {item["key"] for item in SEMANTIC_QUESTIONS}
    if args.key not in valid_keys:
        raise ValueError(f"unknown semantic decision key: {args.key}")
    if not args.answer.strip():
        raise ValueError("answer must not be empty")

    question = next(item for item in SEMANTIC_QUESTIONS if item["key"] == args.key)
    owner_skill = question["owner_skill"]
    skill_data = ensure_skill_data(data_dir, owner_skill, now)
    setup_decisions = skill_data.setdefault("setup_decisions", {})
    setup_decisions[args.key] = {
        "answer": args.answer.strip(),
        "updated_at": now,
        "source": "user",
        "category": question["category"],
    }
    if question["category"] == "source-decisions":
        source_decisions = skill_data.setdefault("source_decisions", {})
        source_decisions[args.key] = {
            "answer": args.answer.strip(),
            "updated_at": now,
            "source": "user",
        }
    if args.note:
        setup_decisions[args.key]["note"] = args.note.strip()
    write_json(data_dir / owner_skill / "data.json", skill_data)

    decisions = setup.setdefault("decisions", {})
    decisions[args.key] = {
        "owner_skill": owner_skill,
        "stored_in": f"{owner_skill}/data.json",
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
        "stored_in": f"{owner_skill}/data.json",
        "semantic_health": health,
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
    p_answer.set_defaults(func=answer)

    p_config = sub.add_parser("config", help="Show Life OS private config/state")
    p_config.set_defaults(func=show_config)
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
