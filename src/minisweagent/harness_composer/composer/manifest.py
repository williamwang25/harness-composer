from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from minisweagent.harness_composer.library.policy_loader import list_policy_names
from minisweagent.harness_composer.library.schemas.policy_schema import HarnessPolicy
from minisweagent.harness_composer.profiler.schema import RepoTaskProfile
from minisweagent.harness_composer.router.policy_router import RoutingDecision


def build_manifest(
    *,
    task_id: str,
    profile: RepoTaskProfile,
    policy: HarnessPolicy,
    routing: RoutingDecision,
    config_path: str | None = None,
) -> dict:
    all_modules = {
        "search_code",
        "view_file",
        "safe_edit",
        "run_test",
        "summarize_obs",
        "state",
        "context_policy",
        "test_policy",
        "compression_policy",
        "control_policy",
        "memory_policy",
    }
    enabled_modules = set(policy.enabled_modules)
    return {
        "task_id": task_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profile": profile.compact_dict(),
        "selected_policy": policy.policy_name,
        "available_policies": list_policy_names(),
        "enabled_modules": sorted(enabled_modules),
        "disabled_modules": sorted(all_modules - enabled_modules),
        "router_reason": routing.reason,
        "considered_rules": routing.considered_rules,
        "expected_benefit": policy.expected_benefit,
        "risk": policy.risk,
        "config_path": config_path,
    }


def save_manifest(manifest: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
