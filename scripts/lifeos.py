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
import platform
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

DEFAULT_SCHEDULES = {
    "heartbeat": "every few hours",
    "pulse": "daily",
    "daily_review": "daily",
    "weekly_review": "weekly",
    "monthly_review": "monthly",
    "quarterly_review": "quarterly",
}

ROUTINE_TO_SKILL = {
    "heartbeat": "routines-heartbeat",
    "pulse": "routines-pulse",
    "daily-review": "routines-daily-review",
    "weekly-review": "routines-weekly-review",
    "monthly-review": "routines-monthly-review",
    "quarterly-review": "routines-quarterly-review",
    "now": "context-now",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_data_dir() -> Path:
    override = os.environ.get("LIFEOS_DATA_DIR")
    if override:
        return Path(override).expanduser()

    system = platform.system().lower()
    home = Path.home()
    if system == "darwin":
        return home / "Library" / "Application Support" / "agentic-life-os"
    if system == "windows":
        local = os.environ.get("LOCALAPPDATA")
        return Path(local) / "agentic-life-os" if local else home / "AppData" / "Local" / "agentic-life-os"
    xdg = os.environ.get("XDG_DATA_HOME")
    return (Path(xdg).expanduser() if xdg else home / ".local" / "share") / "agentic-life-os"


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


@dataclass(frozen=True)
class Subskill:
    name: str
    path: str
    category: str
    optional_global_registration: bool = False


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
            optional_global_registration=bool(meta.get("optional_global_registration", False)),
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
        skill_data_path = data_dir / name / "data.json"
        if not skill_data_path.exists():
            write_json(skill_data_path, {"skill": name, "created_at": now, "runs": []})

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
    config.setdefault("schedules", DEFAULT_SCHEDULES)
    config.setdefault("skills", {name: {"enabled": True} for name in sorted(subskills)})
    config.setdefault("optional_global_skills", {"tasks-todo": bool(args.global_tasks_todo)})
    config.setdefault("created_at", now)
    config["updated_at"] = now

    write_json(data_dir / "runtime.json", runtime)
    write_json(data_dir / "installed.json", installed)
    write_json(data_dir / "config.json", config)

    return {
        "ok": True,
        "action": "install",
        "data_dir": str(data_dir),
        "runtime": args.runtime,
        "subskills": len(subskills),
        "global_tasks_todo_requested": bool(args.global_tasks_todo),
        "note": "Runtime cron creation and delivery routing remain runtime-owned and are not modified by this helper.",
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
    }


def run_routine(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else default_data_dir()
    routine = args.routine
    skill = ROUTINE_TO_SKILL.get(routine, routine)
    subskills = parse_skill_index()
    if skill not in subskills:
        raise SystemExit(f"unknown routine or skill: {routine}")

    now = utc_now()
    skill_data_path = data_dir / skill / "data.json"
    data = read_json(skill_data_path, {"skill": skill, "created_at": now, "runs": []})
    runs = data.setdefault("runs", [])
    run = {
        "routine": routine,
        "skill": skill,
        "ran_at": now,
        "status": "recorded",
        "summary": args.summary or f"{routine} routine recorded. Agent should execute the playbook and update actionable state.",
    }
    runs.append(run)
    data["last_run_at"] = now
    data["last_run"] = run
    write_json(skill_data_path, data)

    return {
        "ok": True,
        "action": "run",
        "routine": routine,
        "skill": skill,
        "data_file": str(skill_data_path),
        "run": run,
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
    p_install.add_argument("--global-tasks-todo", action="store_true", help="Record that tasks-todo should be globally registered by the runtime")
    p_install.set_defaults(func=install)

    p_doctor = sub.add_parser("doctor", help="Validate repo and private Life OS state")
    p_doctor.set_defaults(func=doctor)

    p_run = sub.add_parser("run", help="Record a routine/subskill run in private state")
    p_run.add_argument("routine", choices=sorted(set(ROUTINE_TO_SKILL) | set(ROUTINE_TO_SKILL.values())))
    p_run.add_argument("--summary", help="Short run summary to store")
    p_run.set_defaults(func=run_routine)

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
